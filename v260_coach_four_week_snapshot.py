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
        raise RuntimeError("V20.60 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.60 no script change "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-coach-action-calendar" content="20.59"',
    'meta name="fjz-coach-weekly-brief" content="20.50"',
    "weeklyBriefV250","trackingCache","recentSessionsV175",
    "coachPriorityActionV259","coachPriorityStateV252"
]:
    if marker not in html:
        raise RuntimeError("V20.60 missing prerequisite: "+marker)

def patch_v175(body):
    anchor="  async function hydrateSummaryV175(){"
    if body.count(anchor)!=1:
        raise RuntimeError("V20.60 hydrate anchor mismatch")

    helpers=r"""
  /* ---------- Coach 4-week snapshot V20.60 ---------- */
  function periodBoundsV260(offsetDays){
    const end=Date.now()-Number(offsetDays||0)*86400000;
    return {start:end-28*86400000,end};
  }

  function inPeriodV260(value,p){
    const t=Date.parse(value||0);
    return Number.isFinite(t)&&t>=p.start&&t<p.end;
  }

  function avgFieldV260(rows,key){
    const vals=(rows||[]).map(x=>Number(x?.[key])).filter(Number.isFinite);
    return vals.length?vals.reduce((a,b)=>a+b,0)/vals.length:null;
  }

  function snapshotV260(s,p){
    const sessions=(s?.sessions||[]).filter(x=>inPeriodV260(x?.date,p));
    const checks=(trackingCache?.checkins||[]).filter(x=>inPeriodV260(x?.week_start||x?.created_at,p));
    return {
      sessions:sessions.length,
      sets:sessions.reduce((a,x)=>a+(Number(x?.summary?.totalSets)||0),0),
      progressed:sessions.reduce((a,x)=>a+(Number(x?.summary?.up)||0),0),
      checkins:checks.length,
      adherence:avgFieldV260(checks,'adherence_level'),
      energy:avgFieldV260(checks,'energy_level'),
      recovery:avgFieldV260(checks,'recovery_level')
    };
  }

  function deltaLabelV260(a,b,suffix=''){
    const x=Number(a),y=Number(b);
    if(!Number.isFinite(x)||!Number.isFinite(y))return 'Sin comparación';
    const d=x-y;
    if(Math.abs(d)<0.05)return 'Sin cambio';
    const v=Math.abs(d)<10?round1(d):Math.round(d);
    return (d>0?'+':'')+v+suffix+' vs. 4 sem. previas';
  }

  function coachFourWeekStateV260(s,latest){
    const now=snapshotV260(s,periodBoundsV260(0));
    const prev=snapshotV260(s,periodBoundsV260(28));
    const priority=coachPriorityStateV252(s);
    const action=typeof coachPriorityActionV259==='function'
      ?coachPriorityActionV259(s)
      :{tab:'summary',label:'Abrir seguimiento',status:'Seguimiento'};
    const lastDays=coachDaysSinceV235(s?.lastWorkout);

    let headline='Seguimiento estable';
    let tone='good';
    if(priority.bucket==='urgent'){headline='Necesita atención prioritaria';tone='warn'}
    else if(priority.bucket==='today'){headline='Hay una acción para revisar';tone='warn'}
    else if(now.sessions===0){headline='Sin entrenamientos en 4 semanas';tone='info'}
    else if(now.sessions>prev.sessions){headline='Más constancia que el período anterior';tone='good'}
    else if(now.sessions<prev.sessions){headline='Bajó la frecuencia de entrenamiento';tone='info'}

    return {now,prev,priority,action,lastDays,headline,tone,latest};
  }

  function renderCoachFourWeekV260(s,latest){
    const host=el('v260CoachFourWeek');if(!host)return;
    const x=coachFourWeekStateV260(s,latest);
    const adh=x.now.adherence==null?'—':round1(x.now.adherence)+'/10';
    const energy=x.now.energy==null?'—':round1(x.now.energy)+'/10';
    const recovery=x.now.recovery==null?'—':round1(x.now.recovery)+'/10';
    const last=x.lastDays>=999?'Sin registro':x.lastDays===0?'Hoy':x.lastDays+' d';

    host.innerHTML=
      '<div class="v175-360-section-head v260-head"><div><div class="v225-section-kicker">ESTADO 4 SEMANAS</div>'+
        '<h4>'+esc(x.headline)+'</h4><p>Entrenamiento, check-ins y señales de seguimiento en una vista rápida.</p></div>'+
        '<span class="badge '+(x.tone==='warn'?'amber':x.tone==='good'?'green':'blue')+'">28 días</span></div>'+
      '<div class="v260-grid">'+
        '<div><span>Entrenos</span><strong>'+x.now.sessions+'</strong><small>'+esc(deltaLabelV260(x.now.sessions,x.prev.sessions))+'</small></div>'+
        '<div><span>Check-ins</span><strong>'+x.now.checkins+'</strong><small>Adherencia '+esc(adh)+'</small></div>'+
        '<div><span>Energía / recuperación</span><strong>'+esc(energy)+' · '+esc(recovery)+'</strong><small>Promedio del período</small></div>'+
        '<div><span>Último entreno</span><strong>'+esc(last)+'</strong><small>'+esc(x.priority.label||'Seguimiento')+'</small></div>'+
      '</div>'+
      '<div class="v260-current '+esc(x.priority.bucket)+'">'+
        '<div><span>PRIORIDAD ACTUAL</span><strong>'+esc(x.action.status)+'</strong><p>'+esc(x.priority.label||'Seguimiento al día')+'</p></div>'+
        '<button class="btn small '+(x.priority.bucket==='urgent'||x.priority.bucket==='today'?'primary':'')+'" onclick="openCoachStudentTabV235(\''+esc(s.id)+'\',\''+esc(x.action.tab)+'\')">'+esc(x.action.label)+'</button>'+
      '</div>';
  }

"""
    body=body.replace(anchor,helpers+anchor,1)

    hydrate_anchor="""    renderReviewHubV237(reviewCurrentV237);
    renderSessionFeedbackCoachV242();
    renderCoachWeeklyBriefV250(s,latest,agenda,nutrition,pending);

    if(el('v175Metrics'))"""
    hydrate_repl="""    renderReviewHubV237(reviewCurrentV237);
    renderSessionFeedbackCoachV242();
    renderCoachFourWeekV260(s,latest);
    renderCoachWeeklyBriefV250(s,latest,agenda,nutrition,pending);

    if(el('v175Metrics'))"""
    if body.count(hydrate_anchor)!=1:
        raise RuntimeError("V20.60 hydrate insertion mismatch")
    body=body.replace(hydrate_anchor,hydrate_repl,1)

    brief_section="""      '<div class="v175-360-section v250-weekly-brief" id="v250CoachWeeklyBrief"><div class="empty">Preparando brief semanal…</div></div>'+
"""
    snapshot_section="""      '<div class="v175-360-section v260-four-week" id="v260CoachFourWeek"><div class="empty">Preparando estado de 4 semanas…</div></div>'+
"""
    if body.count(brief_section)!=1:
        raise RuntimeError("V20.60 summary insertion mismatch")
    body=body.replace(brief_section,snapshot_section+brief_section,1)

    marker_old="""    exerciseProgressReadOnly:true
  };"""
    marker_new="""    exerciseProgressReadOnly:true,
    coachFourWeekSnapshot:true,
    coachFourWeekUsesExistingTracking:true
  };"""
    if body.count(marker_old)!=1:
        raise RuntimeError("V20.60 marker mismatch")
    body=body.replace(marker_old,marker_new,1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

css=r"""
/* TEAM FJZ · V20.60 COACH 4-WEEK SNAPSHOT */
.v260-four-week{
  border-color:rgba(103,173,255,.18);
  background:linear-gradient(145deg,rgba(103,173,255,.035),transparent 52%),#101116;
}
.v260-head{align-items:flex-start}
.v260-head h4{margin:4px 0 0;color:#f4f6f8;font-size:15px;font-weight:920;letter-spacing:-.018em}
.v260-head p{margin:5px 0 0;color:#969ba5;font-size:9px;line-height:1.45}
.v260-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px}
.v260-grid>div{
  min-width:0;padding:10px;border:1px solid #2b2f37;border-radius:10px;background:#0d0e12
}
.v260-grid span{display:block;color:#858b96;font-size:7px;font-weight:850;text-transform:uppercase;letter-spacing:.05em}
.v260-grid strong{display:block;margin-top:5px;color:#f3f5f8;font-size:16px;font-weight:920;overflow-wrap:anywhere}
.v260-grid small{display:block;margin-top:5px;color:#8d939e;font-size:7px;line-height:1.35}
.v260-current{
  display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;align-items:center;
  margin-top:9px;padding:10px 11px;border:1px solid #2c3038;border-left:3px solid #67adff;border-radius:0 11px 11px 0;background:#0d0e12
}
.v260-current.urgent{border-left-color:#ff4657}.v260-current.today{border-left-color:#f2bd55}.v260-current.watch{border-left-color:#67adff}
.v260-current span{display:block;color:#858b96;font-size:7px;font-weight:900;letter-spacing:.09em}
.v260-current strong{display:block;margin-top:4px;color:#f2f4f6;font-size:11px;font-weight:900}
.v260-current p{margin:3px 0 0;color:#9298a2;font-size:8px;line-height:1.4}
@media(max-width:760px){
  .v260-grid{grid-template-columns:1fr 1fr}
}
@media(max-width:540px){
  .v260-current{grid-template-columns:1fr}
  .v260-current .btn{width:100%}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.60 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-coach-four-week-snapshot" content="20.60">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.60 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-coach-four-week-snapshot" content="20.60"',
    "coachFourWeekStateV260","renderCoachFourWeekV260",
    "ESTADO 4 SEMANAS","PRIORIDAD ACTUAL",
    "coachFourWeekSnapshot:true","coachFourWeekUsesExistingTracking:true"
]:
    if marker not in html:
        raise RuntimeError("V20.60 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.60 coach 4-week snapshot")
print("V20.60 BEFORE:",before)
print("V20.60 AFTER:",after)
print("V20.60 fast 28-day coach read added using existing session/check-in data")
