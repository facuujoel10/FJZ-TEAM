import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

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

def edit_script(doc,script_id,transform):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.58 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.58 no script change "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-checkin-weekly-focus" content="20.57"',
    'meta name="fjz-student-week-flow" content="20.53"',
    "latestReviewedCheckinV248",
    "injectStudentWeekFlowV253",
    "checkinReplyAckV248"
]:
    if marker not in html:
        raise RuntimeError("V20.58 missing prerequisite: "+marker)

def patch_v175(body):
    anchor="  /* ---------- Student action hub V20.45 ---------- */"
    if body.count(anchor)!=1:
        raise RuntimeError("V20.58 action hub anchor mismatch")

    helpers=r"""
  /* ---------- Persistent current plan V20.58 ---------- */
  function currentCoachPlanV258(){
    const row=latestReviewedCheckinV248();
    if(!row)return null;
    const parsed=parseCheckinFeedbackV248(row.coach_feedback||'');
    if(!parsed.nextStep&&!parsed.weeklyFocus)return null;
    return {row,parsed};
  }

  function injectStudentCurrentPlanV258(){
    if(!(mode==='student'&&studentTab==='home'))return;
    const view=el('view');if(!view)return;
    el('v258StudentCurrentPlan')?.remove();

    const plan=currentCoachPlanV258();
    if(!plan)return;

    const s=student?.();
    const seen=!!s?.checkinReplyAckV248?.[plan.row.id];
    const card=document.createElement('section');
    card.id='v258StudentCurrentPlan';
    card.className='card v258-current-plan';
    card.innerHTML=
      '<div class="section-title v258-plan-head">'+
        '<div><div class="v225-section-kicker">PLAN ACTUAL</div><h3>'+esc(checkinDecisionLabelV248(plan.parsed.decision))+'</h3>'+
        '<div class="muted tiny">Última revisión · semana '+esc(plan.row.week_start||'')+'</div></div>'+
        '<span class="badge '+(seen?'green':'amber')+'">'+(seen?'Visto':'Nuevo')+'</span>'+
      '</div>'+
      (plan.parsed.weeklyFocus
        ?'<div class="v258-focus"><span>PRIORIDAD DE LA SEMANA</span><strong>'+esc(plan.parsed.weeklyFocus)+'</strong></div>'
        :'')+
      (plan.parsed.nextStep
        ?'<div class="v258-next"><span>CÓMO SEGUIMOS</span><p>'+esc(plan.parsed.nextStep)+'</p></div>'
        :'')+
      '<div class="v258-actions">'+
        '<button class="btn" onclick="studentTab=\\'tracking\\';render()">Ver seguimiento</button>'+
        (!seen?'<button class="btn primary" onclick="acknowledgeCheckinReplyV248(\\''+esc(plan.row.id)+'\\')">Entendido</button>':'')+
      '</div>';

    const week=el('v253StudentWeekFlow');
    const hub=el('v245StudentActionHub');
    const profile=el('v115StudentProfileCard')||el('v175StudentProfilePlaceholder');
    if(week)week.insertAdjacentElement('afterend',card);
    else if(hub)hub.insertAdjacentElement('afterend',card);
    else if(profile)profile.insertAdjacentElement('afterend',card);
    else view.prepend(card);
  }

"""
    body=body.replace(anchor,helpers+anchor,1)

    week_anchor="""    if(anchor)anchor.insertAdjacentElement('afterend',card);
    else view.prepend(card);
  }

"""
    week_repl="""    if(anchor)anchor.insertAdjacentElement('afterend',card);
    else view.prepend(card);
    injectStudentCurrentPlanV258();
  }

"""
    if body.count(week_anchor)!=1:
        raise RuntimeError("V20.58 week-flow refresh anchor mismatch: "+str(body.count(week_anchor)))
    body=body.replace(week_anchor,week_repl,1)

    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

css=r"""
/* TEAM FJZ · V20.58 PERSISTENT CURRENT PLAN */
.v258-current-plan{
  border-color:#30343c;
  background:
    linear-gradient(145deg,rgba(103,173,255,.05),transparent 45%),
    var(--card);
}
.v258-plan-head{
  align-items:flex-start;
}
.v258-plan-head h3{
  margin:4px 0 0;
  color:#f3f5f8;
  font-size:16px;
  font-weight:920;
  letter-spacing:-.02em;
}
.v258-focus{
  display:grid;
  gap:5px;
  margin-top:10px;
  padding:10px 11px;
  border-left:3px solid #67adff;
  border-radius:0 10px 10px 0;
  background:#10151d;
}
.v258-focus span,
.v258-next span{
  color:#818895;
  font-size:7px;
  font-weight:900;
  letter-spacing:.08em;
}
.v258-focus strong{
  color:#edf2f8;
  font-size:11px;
  line-height:1.45;
}
.v258-next{
  margin-top:9px;
  padding:10px 11px;
  border:1px solid #2b3039;
  border-radius:10px;
  background:#0d0f13;
}
.v258-next p{
  margin:5px 0 0;
  color:#c8cdd5;
  font-size:9px;
  line-height:1.5;
  white-space:pre-wrap;
}
.v258-actions{
  display:flex;
  justify-content:flex-end;
  gap:7px;
  margin-top:10px;
}
@media(max-width:520px){
  .v258-actions{
    display:grid;
    grid-template-columns:1fr 1fr;
  }
  .v258-actions .btn:only-child{
    grid-column:1/-1;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.58 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-student-current-plan" content="20.58">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.58 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-student-current-plan" content="20.58"',
    "currentCoachPlanV258",
    "injectStudentCurrentPlanV258",
    "v258StudentCurrentPlan",
    "PLAN ACTUAL",
    "PRIORIDAD DE LA SEMANA",
    "CÓMO SEGUIMOS"
]:
    if marker not in html:
        raise RuntimeError("V20.58 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.58 persistent student current plan")
print("V20.58 BEFORE:",before)
print("V20.58 AFTER:",after)
print("V20.58 latest reviewed coach plan remains visible on Student Home after acknowledgement")
