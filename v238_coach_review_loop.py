import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.38 COACH REVIEW LOOP
# =========================================================
# Connects V20.37 review baselines back into the V20.35/20.36 dashboard.
# No backend/schema/realtime/listener/timer changes.

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
    'meta name="fjz-coach-review-hub" content="20.37"',
    "coachFocusScoreV235","coachFilteredStudentsV235",
    "renderCoachStudentsV235","coachReviewV237",
    "openNextCoachPriorityV236"
]:
    if marker not in html:
        raise RuntimeError("V20.38 missing prerequisite: "+marker)

# ---------- Review-state helpers ----------
anchor="function coachFocusScoreV235(s){"
if html.count(anchor)!=1:
    raise RuntimeError("V20.38 focus score anchor mismatch")

helpers=r"""
function coachReviewLoopStateV238(s){
  const prev=s?.coachReviewV237||null;
  const currentAdh=Number(adherence(s)||0);
  const sessionsCount=Array.isArray(s?.sessions)?s.sessions.length:0;
  const currentStatus=statusFor(s);
  const pending=coachPendingV235(s);

  if(!prev){
    return {
      hasBaseline:false,
      changed:true,
      reason:'Sin revisión previa',
      newSessions:sessionsCount,
      adherenceDelta:null,
      pending
    };
  }

  const newSessions=Math.max(0,sessionsCount-Number(prev.sessionsCount||0));
  const adherenceDelta=currentAdh-Number(prev.adherence||0);
  const statusChanged=currentStatus!==prev.status;
  const lastWorkoutChanged=!!(s?.lastWorkout&&s.lastWorkout!==prev.lastWorkout);
  const changed=(
    newSessions>0||
    pending>0||
    statusChanged||
    Math.abs(adherenceDelta)>=10||
    lastWorkoutChanged
  );

  const bits=[];
  if(newSessions)bits.push(newSessions+' entreno'+(newSessions===1?' nuevo':'s nuevos'));
  if(pending)bits.push(pending+' pendiente'+(pending===1?'':'s'));
  if(statusChanged)bits.push('estado '+currentStatus.toLowerCase());
  if(Math.abs(adherenceDelta)>=10)bits.push('adherencia '+(adherenceDelta>0?'+':'')+Math.round(adherenceDelta)+'%');
  if(lastWorkoutChanged&&!newSessions)bits.push('actividad nueva');

  return {
    hasBaseline:true,
    changed,
    reason:bits.slice(0,2).join(' · ')||(changed?'Cambios nuevos':'Al día'),
    newSessions,
    adherenceDelta,
    pending
  };
}

function coachReviewCountsV238(){
  const students=state.students||[];
  return {
    changed:students.filter(s=>coachReviewLoopStateV238(s).changed).length,
    unreviewed:students.filter(s=>!coachReviewLoopStateV238(s).hasBaseline).length,
    current:students.filter(s=>{
      const r=coachReviewLoopStateV238(s);
      return r.hasBaseline&&!r.changed;
    }).length
  };
}

function decorateCoachReviewStateV238(){
  document.querySelectorAll('.student-row[data-client-id]').forEach(row=>{
    row.querySelector('.v238-review-badge')?.remove();
    const s=(state.students||[]).find(x=>x.id===row.dataset.clientId);
    if(!s)return;
    const r=coachReviewLoopStateV238(s);
    const main=row.querySelector('.student-main');
    if(!main)return;

    if(!r.hasBaseline){
      main.insertAdjacentHTML('beforeend','<span class="v238-review-badge unreviewed">Sin revisión</span>');
    }else if(r.changed){
      main.insertAdjacentHTML('beforeend','<span class="v238-review-badge changed">Nuevo desde revisión</span>');
    }else{
      main.insertAdjacentHTML('beforeend','<span class="v238-review-badge current">Revisado</span>');
    }
  });

  const c=coachReviewCountsV238();
  if(el('v238ChangedCount'))el('v238ChangedCount').textContent=String(c.changed);
  if(el('v238UnreviewedCount'))el('v238UnreviewedCount').textContent=String(c.unreviewed);
  if(el('v238CurrentCount'))el('v238CurrentCount').textContent=String(c.current);
}
"""
html=html.replace(anchor,helpers+"\n"+anchor,1)

# ---------- Make review-state part of priority score ----------
old_score="""function coachFocusScoreV235(s){
  const o=coachStateV235(s);
  return coachCriticalV235(s)*8+coachPendingV235(s)*3+(o.review?5:0)+(o.low?3:0)+(o.inactive?2:0);
}"""
new_score="""function coachFocusScoreV235(s){
  const o=coachStateV235(s),r=coachReviewLoopStateV238(s);
  return coachCriticalV235(s)*8+
    coachPendingV235(s)*3+
    (o.review?5:0)+
    (o.low?3:0)+
    (o.inactive?2:0)+
    (r.changed?4:0)+
    (!r.hasBaseline?2:0);
}"""
if html.count(old_score)!=1:
    raise RuntimeError("V20.38 focus score function mismatch")
html=html.replace(old_score,new_score,1)

# ---------- Add review filters ----------
old_filter_tail="""    if(coachStudentFilterV235==='inactive')return o.inactive;
    return true;"""
new_filter_tail="""    if(coachStudentFilterV235==='inactive')return o.inactive;
    if(coachStudentFilterV235==='changes')return coachReviewLoopStateV238(s).changed;
    if(coachStudentFilterV235==='unreviewed')return !coachReviewLoopStateV238(s).hasBaseline;
    return true;"""
if html.count(old_filter_tail)!=1:
    raise RuntimeError("V20.38 student filter tail mismatch")
html=html.replace(old_filter_tail,new_filter_tail,1)

# ---------- Ensure every student-list repaint adds review badges ----------
old_decorate="""  decorateCoachAlertsV235();
}"""
new_decorate="""  decorateCoachAlertsV235();
  decorateCoachReviewStateV238();
}"""
# Only patch first occurrence, the renderCoachStudentsV235 function.
if html.count(old_decorate)<1:
    raise RuntimeError("V20.38 student decorate anchor missing")
html=html.replace(old_decorate,new_decorate,1)

# ---------- Extend dashboard filter bar ----------
filter_anchor="""  <button class="btn small" data-v235-filter="inactive" onclick="setCoachStudentFilterV235('inactive')">7+ días sin entrenar</button>
  <span class="badge blue" id="v235StudentCount">"""
filter_repl="""  <button class="btn small" data-v235-filter="inactive" onclick="setCoachStudentFilterV235('inactive')">7+ días sin entrenar</button>
  <button class="btn small" data-v235-filter="changes" onclick="setCoachStudentFilterV235('changes')">Cambios nuevos · <span id="v238ChangedCount">0</span></button>
  <button class="btn small" data-v235-filter="unreviewed" onclick="setCoachStudentFilterV235('unreviewed')">Sin revisión · <span id="v238UnreviewedCount">0</span></button>
  <span class="badge blue" id="v235StudentCount">"""
if html.count(filter_anchor)!=1:
    raise RuntimeError("V20.38 filter bar anchor mismatch")
html=html.replace(filter_anchor,filter_repl,1)

# ---------- Surface review loop in focus-card header ----------
focus_anchor="""  <div id="v235CoachFocus"><div class="empty">Preparando prioridades…</div></div>
</section>"""
focus_repl="""  <div class="v238-review-summary">
    <span><strong id="v238ChangedCountTop">—</strong> con cambios nuevos</span>
    <span><strong id="v238CurrentCount">—</strong> al día</span>
  </div>
  <div id="v235CoachFocus"><div class="empty">Preparando prioridades…</div></div>
</section>"""
if html.count(focus_anchor)!=1:
    raise RuntimeError("V20.38 focus card anchor mismatch")
html=html.replace(focus_anchor,focus_repl,1)

# ---------- Hydration updates summary counts after feed arrives ----------
hydrate_anchor="""    renderCoachFocusV235();
    const byAthlete=new Map();"""
hydrate_repl="""    renderCoachFocusV235();
    decorateCoachReviewStateV238();
    const rc238=coachReviewCountsV238();
    if(el('v238ChangedCountTop'))el('v238ChangedCountTop').textContent=String(rc238.changed);
    const byAthlete=new Map();"""
if html.count(hydrate_anchor)!=1:
    raise RuntimeError("V20.38 hydrate review anchor mismatch")
html=html.replace(hydrate_anchor,hydrate_repl,1)

# ---------- Focus reasons include review changes ----------
reason_anchor="""    if(o.inactive&&o.days<999)bits.push(o.days+' días sin entrenar');"""
reason_repl="""    if(o.inactive&&o.days<999)bits.push(o.days+' días sin entrenar');
    const rv=coachReviewLoopStateV238(s);
    if(rv.changed)bits.unshift(rv.reason);"""
if html.count(reason_anchor)!=1:
    raise RuntimeError("V20.38 focus reason anchor mismatch")
html=html.replace(reason_anchor,reason_repl,1)

css=r"""
/* TEAM FJZ · V20.38 COACH REVIEW LOOP */
.v238-review-badge{
  display:inline-flex;
  align-items:center;
  min-height:22px;
  margin-left:7px;
  padding:3px 7px;
  border:1px solid #30343d;
  border-radius:999px;
  font-size:8px;
  line-height:1;
  font-weight:850;
  white-space:nowrap;
}
.v238-review-badge.changed{
  color:#ffb7bd;
  border-color:rgba(255,38,57,.26);
  background:rgba(255,38,57,.07);
}
.v238-review-badge.unreviewed{
  color:#f2c66c;
  border-color:rgba(242,189,85,.24);
  background:rgba(242,189,85,.06);
}
.v238-review-badge.current{
  color:#9ddfba;
  border-color:rgba(59,213,138,.20);
  background:rgba(59,213,138,.05);
}
.v238-review-summary{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:7px;
  margin:0 0 10px;
}
.v238-review-summary span{
  padding:8px 9px;
  border:1px solid #2b2e35;
  border-radius:10px;
  background:#0c0d10;
  color:#9397a2;
  font-size:9px;
  line-height:1.35;
}
.v238-review-summary strong{
  color:#f4f5f7;
  font-size:13px;
  font-weight:900;
  margin-right:3px;
}
@media(max-width:560px){
  .v238-review-badge{
    margin-left:0;
    margin-top:5px;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.38 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-coach-review-loop" content="20.38">\n</head>',1)

after=metrics(html)
for key in (
    "styles","renders","channels","timeouts","rafs","listeners",
    "mutation_observers","performance_observers"
):
    if after[key]!=before[key]:
        raise RuntimeError("V20.38 topology changed "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-coach-review-loop" content="20.38"',
    "coachReviewLoopStateV238","coachReviewCountsV238",
    "decorateCoachReviewStateV238","Nuevo desde revisión",
    "Cambios nuevos","Sin revisión","v238-review-summary",
    "openNextCoachPriorityV236","coachReviewV237",
    "v122FollowupPaymentsRuntime"
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.38 missing review-loop marker: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.38 coach review loop")
print("V20.38 BEFORE:",before)
print("V20.38 AFTER:",after)
print("V20.38 dashboard now reacts to new changes since last coach review")
