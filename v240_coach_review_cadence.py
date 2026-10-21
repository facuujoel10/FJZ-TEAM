import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.40 COACH REVIEW CADENCE
# =========================================================
# Per-student review cadence (7/14/30 days), persisted inside student JSON.
# Dashboard surfaces overdue reviews and uses them in work-queue priority.
# No schema/backend/realtime/listener/timer changes.

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

before=metrics(html)

for marker in [
    'meta name="fjz-coach-decision-log" content="20.39"',
    "coachReviewLoopStateV238","coachFocusScoreV235",
    "coachFilteredStudentsV235","renderReviewHubV237",
    "coachReviewV237"
]:
    if marker not in html:
        raise RuntimeError("V20.40 missing prerequisite: "+marker)

# ---------- Cadence helpers ----------
anchor="function coachReviewLoopStateV238(s){"
if html.count(anchor)!=1:
    raise RuntimeError("V20.40 review loop anchor mismatch")

helpers=r"""
function coachReviewCadenceDaysV240(s){
  const n=Number(s?.coachReviewSettingsV240?.cadenceDays||7);
  return [7,14,30].includes(n)?n:7;
}

function coachReviewDueV240(s){
  const days=coachReviewCadenceDaysV240(s);
  const reviewed=s?.coachReviewV237?.reviewedAt||null;
  if(!reviewed){
    return {due:true,days,cadenceDays:days,ageDays:999,remaining:0,label:'Sin revisión previa'};
  }
  const age=coachDaysSinceV235(reviewed);
  const remaining=Math.max(0,days-age);
  return {
    due:age>=days,
    days,
    cadenceDays:days,
    ageDays:age,
    remaining,
    label:age>=days
      ?'Revisión vencida · '+age+' días'
      :'Próxima revisión en '+remaining+' días'
  };
}

function coachReviewCadenceLabelV240(days){
  return Number(days)===30?'Mensual':Number(days)===14?'Quincenal':'Semanal';
}

window.setCoachReviewCadenceV240=function(days){
  const s=student();
  if(!s)return;
  const n=Number(days);
  s.coachReviewSettingsV240={
    ...(s.coachReviewSettingsV240||{}),
    cadenceDays:[7,14,30].includes(n)?n:7
  };
  saveState();
  if(typeof renderReviewHubV237==='function'&&reviewCurrentV237){
    renderReviewHubV237(reviewCurrentV237);
  }
  toast?.('Frecuencia de revisión actualizada');
};
"""
html=html.replace(anchor,helpers+"\n"+anchor,1)

# ---------- Add due state into review loop result ----------
old_no_prev="""    return {
      hasBaseline:false,
      changed:true,
      reason:'Sin revisión previa',
      newSessions:sessionsCount,
      adherenceDelta:null,
      pending
    };"""
new_no_prev="""    const due=coachReviewDueV240(s);
    return {
      hasBaseline:false,
      changed:true,
      reviewDue:true,
      reviewDueLabel:due.label,
      reason:'Sin revisión previa',
      newSessions:sessionsCount,
      adherenceDelta:null,
      pending
    };"""
if html.count(old_no_prev)!=1:
    raise RuntimeError("V20.40 no-baseline state mismatch")
html=html.replace(old_no_prev,new_no_prev,1)

old_return="""  return {
    hasBaseline:true,
    changed,
    reason:bits.slice(0,2).join(' · ')||(changed?'Cambios nuevos':'Al día'),
    newSessions,
    adherenceDelta,
    pending
  };"""
new_return="""  const due=coachReviewDueV240(s);
  return {
    hasBaseline:true,
    changed,
    reviewDue:due.due,
    reviewDueLabel:due.label,
    reason:bits.slice(0,2).join(' · ')||(changed?'Cambios nuevos':'Al día'),
    newSessions,
    adherenceDelta,
    pending
  };"""
if html.count(old_return)!=1:
    raise RuntimeError("V20.40 review state return mismatch")
html=html.replace(old_return,new_return,1)

# ---------- Add overdue-review weight to focus score ----------
old_score_tail="""    (r.changed?4:0)+
    (!r.hasBaseline?2:0);
}"""
new_score_tail="""    (r.changed?4:0)+
    (r.reviewDue?3:0)+
    (!r.hasBaseline?2:0);
}"""
if html.count(old_score_tail)!=1:
    raise RuntimeError("V20.40 focus score tail mismatch")
html=html.replace(old_score_tail,new_score_tail,1)

# ---------- Add dashboard filter ----------
old_filter_tail="""    if(coachStudentFilterV235==='unreviewed')return !coachReviewLoopStateV238(s).hasBaseline;
    return true;"""
new_filter_tail="""    if(coachStudentFilterV235==='unreviewed')return !coachReviewLoopStateV238(s).hasBaseline;
    if(coachStudentFilterV235==='due')return coachReviewLoopStateV238(s).reviewDue;
    return true;"""
if html.count(old_filter_tail)!=1:
    raise RuntimeError("V20.40 filter tail mismatch")
html=html.replace(old_filter_tail,new_filter_tail,1)

# ---------- Count overdue reviews ----------
old_counts="""    current:students.filter(s=>{
      const r=coachReviewLoopStateV238(s);
      return r.hasBaseline&&!r.changed;
    }).length
  };"""
new_counts="""    current:students.filter(s=>{
      const r=coachReviewLoopStateV238(s);
      return r.hasBaseline&&!r.changed&&!r.reviewDue;
    }).length,
    due:students.filter(s=>coachReviewLoopStateV238(s).reviewDue).length
  };"""
if html.count(old_counts)!=1:
    raise RuntimeError("V20.40 review counts mismatch")
html=html.replace(old_counts,new_counts,1)

# ---------- Student row badge reflects overdue state ----------
old_badges="""    if(!r.hasBaseline){
      main.insertAdjacentHTML('beforeend','<span class="v238-review-badge unreviewed">Sin revisión</span>');
    }else if(r.changed){
      main.insertAdjacentHTML('beforeend','<span class="v238-review-badge changed">Nuevo desde revisión</span>');
    }else{
      main.insertAdjacentHTML('beforeend','<span class="v238-review-badge current">Revisado</span>');
    }"""
new_badges="""    if(!r.hasBaseline){
      main.insertAdjacentHTML('beforeend','<span class="v238-review-badge unreviewed">Sin revisión</span>');
    }else if(r.reviewDue){
      main.insertAdjacentHTML('beforeend','<span class="v238-review-badge due">Revisión vencida</span>');
    }else if(r.changed){
      main.insertAdjacentHTML('beforeend','<span class="v238-review-badge changed">Nuevo desde revisión</span>');
    }else{
      main.insertAdjacentHTML('beforeend','<span class="v238-review-badge current">Revisado</span>');
    }"""
if html.count(old_badges)!=1:
    raise RuntimeError("V20.40 review badge block mismatch")
html=html.replace(old_badges,new_badges,1)

# ---------- Add filter button ----------
filter_anchor="""  <button class="btn small" data-v235-filter="unreviewed" onclick="setCoachStudentFilterV235('unreviewed')">Sin revisión · <span id="v238UnreviewedCount">0</span></button>
  <span class="badge blue" id="v235StudentCount">"""
filter_repl="""  <button class="btn small" data-v235-filter="unreviewed" onclick="setCoachStudentFilterV235('unreviewed')">Sin revisión · <span id="v238UnreviewedCount">0</span></button>
  <button class="btn small" data-v235-filter="due" onclick="setCoachStudentFilterV235('due')">Revisión vencida · <span id="v240DueCount">0</span></button>
  <span class="badge blue" id="v235StudentCount">"""
if html.count(filter_anchor)!=1:
    raise RuntimeError("V20.40 filter bar anchor mismatch")
html=html.replace(filter_anchor,filter_repl,1)

# ---------- Update due count after decorating ----------
count_anchor="""  if(el('v238CurrentCount'))el('v238CurrentCount').textContent=String(c.current);
}"""
count_repl="""  if(el('v238CurrentCount'))el('v238CurrentCount').textContent=String(c.current);
  if(el('v240DueCount'))el('v240DueCount').textContent=String(c.due||0);
}"""
if html.count(count_anchor)!=1:
    raise RuntimeError("V20.40 dashboard count anchor mismatch")
html=html.replace(count_anchor,count_repl,1)

# ---------- Focus reasons include overdue cadence ----------
reason_anchor="""    const rv=coachReviewLoopStateV238(s);
    if(rv.changed)bits.unshift(rv.reason);"""
reason_repl="""    const rv=coachReviewLoopStateV238(s);
    if(rv.reviewDue)bits.unshift(rv.reviewDueLabel);
    if(rv.changed)bits.unshift(rv.reason);"""
if html.count(reason_anchor)!=1:
    raise RuntimeError("V20.40 focus reason mismatch")
html=html.replace(reason_anchor,reason_repl,1)

# ---------- Add cadence control inside review hub ----------
stamp_anchor="""    const history=reviewHistoryV239(s);
    const lastDecision=history[0]||null;

    host.innerHTML="""
stamp_repl="""    const history=reviewHistoryV239(s);
    const lastDecision=history[0]||null;
    const cadenceDays=coachReviewCadenceDaysV240(s);
    const dueState=coachReviewDueV240(s);

    host.innerHTML="""
if html.count(stamp_anchor)!=1:
    raise RuntimeError("V20.40 review hub state anchor mismatch")
html=html.replace(stamp_anchor,stamp_repl,1)

meta_anchor="""        '<div class="v237-review-meta"><span>Última revisión</span><strong>'+esc(stamp)+'</strong></div>'+
      '</div>'+"""
meta_repl="""        '<div class="v237-review-meta"><span>Última revisión</span><strong>'+esc(stamp)+'</strong>'+
          '<div class="v240-review-due '+(dueState.due?'due':'ok')+'">'+esc(dueState.label)+'</div>'+
          '<label class="v240-cadence"><span>Frecuencia</span><select class="input" onchange="setCoachReviewCadenceV240(this.value)">'+
            '<option value="7" '+(cadenceDays===7?'selected':'')+'>Semanal</option>'+
            '<option value="14" '+(cadenceDays===14?'selected':'')+'>Quincenal</option>'+
            '<option value="30" '+(cadenceDays===30?'selected':'')+'>Mensual</option>'+
          '</select></label>'+
        '</div>'+
      '</div>'+"""
if html.count(meta_anchor)!=1:
    raise RuntimeError("V20.40 review meta anchor mismatch")
html=html.replace(meta_anchor,meta_repl,1)

# ---------- Extend marker object ----------
marker_old="""    coachDecisionLog:true,
    reviewHistoryLimit:12
  };"""
marker_new="""    coachDecisionLog:true,
    reviewHistoryLimit:12,
    coachReviewCadence:true,
    reviewCadenceOptions:[7,14,30]
  };"""
if html.count(marker_old)!=1:
    raise RuntimeError("V20.40 marker object mismatch")
html=html.replace(marker_old,marker_new,1)

css=r"""
/* TEAM FJZ · V20.40 COACH REVIEW CADENCE */
.v238-review-badge.due{
  color:#ffd09a;
  border-color:rgba(242,189,85,.30);
  background:rgba(242,189,85,.075);
}
.v240-review-due{
  margin-top:7px;
  padding-top:7px;
  border-top:1px solid #292c33;
  font-size:9px;
  line-height:1.35;
  font-weight:780;
}
.v240-review-due.due{color:#f2c66c}
.v240-review-due.ok{color:#8fdcaf}
.v240-cadence{
  display:grid;
  gap:5px;
  margin-top:8px;
}
.v240-cadence>span{
  color:#7f848f;
  font-size:8px;
  font-weight:800;
  text-transform:uppercase;
  letter-spacing:.06em;
}
.v240-cadence .input{
  min-height:31px;
  padding:5px 28px 5px 8px;
  font-size:10px;
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.40 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-coach-review-cadence" content="20.40">\n</head>',1)

after=metrics(html)
for key in (
    "styles","renders","channels","timeouts","rafs","listeners",
    "mutation_observers","performance_observers"
):
    if after[key]!=before[key]:
        raise RuntimeError("V20.40 topology changed "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-coach-review-cadence" content="20.40"',
    "coachReviewSettingsV240","coachReviewCadenceDaysV240",
    "coachReviewDueV240","setCoachReviewCadenceV240",
    "Revisión vencida","Quincenal","Mensual",
    "coachReviewCadence:true","reviewCadenceOptions:[7,14,30]",
    "openNextCoachPriorityV236","coachReviewHistoryV239",
    "v122FollowupPaymentsRuntime"
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.40 missing cadence marker: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.40 coach review cadence")
print("V20.40 BEFORE:",before)
print("V20.40 AFTER:",after)
print("V20.40 weekly/biweekly/monthly coach review cadence added; topology unchanged")
