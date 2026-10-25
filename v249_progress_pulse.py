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
    if not m: raise RuntimeError("V20.49 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body: raise RuntimeError("V20.49 no script change")
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-checkin-reply-loop" content="20.48"',
    "function postRenderV175()",
    "trackingCache","loadTracking"
]:
    if marker not in html:
        raise RuntimeError("V20.49 missing prerequisite: "+marker)

def patch_v175(body):
    anchor="  function postRenderV175(){"
    if body.count(anchor)!=1:
        raise RuntimeError("V20.49 postRender anchor mismatch")

    helpers=r"""
  /* ---------- Progress Pulse V20.49 ---------- */
  function progressPeriodV249(offsetDays){
    const end=Date.now()-offsetDays*86400000;
    return {start:end-28*86400000,end};
  }

  function inPeriodV249(value,p){
    const t=Date.parse(value||0);
    return Number.isFinite(t)&&t>=p.start&&t<p.end;
  }

  function avgV249(rows,key){
    const vals=(rows||[]).map(x=>Number(x?.[key])).filter(Number.isFinite);
    return vals.length?vals.reduce((a,b)=>a+b,0)/vals.length:null;
  }

  function periodSnapshotV249(s,p){
    const sessions=(s?.sessions||[]).filter(x=>inPeriodV249(x?.date,p));
    const checks=(trackingCache?.checkins||[]).filter(x=>inPeriodV249(x?.week_start,p));
    return {
      sessions:sessions.length,
      sets:sessions.reduce((a,x)=>a+(Number(x?.summary?.totalSets)||0),0),
      progressed:sessions.reduce((a,x)=>a+(Number(x?.summary?.up)||0),0),
      adherence:avgV249(checks,'adherence_level'),
      energy:avgV249(checks,'energy_level'),
      recovery:avgV249(checks,'recovery_level'),
      checkins:checks.length
    };
  }

  function progressDeltaV249(now,prev,key){
    const a=Number(now?.[key]),b=Number(prev?.[key]);
    if(!Number.isFinite(a)||!Number.isFinite(b))return null;
    return a-b;
  }

  function progressDeltaTextV249(d,suffix=''){
    if(d==null||!Number.isFinite(d))return 'Sin comparación';
    if(Math.abs(d)<0.05)return 'Sin cambio';
    return (d>0?'+':'')+(Math.abs(d)<10?round1(d):Math.round(d))+suffix;
  }

  function progressPulseSummaryV249(now,prev){
    const sessionDelta=now.sessions-prev.sessions;
    const energyDelta=progressDeltaV249(now,prev,'energy');
    const recoveryDelta=progressDeltaV249(now,prev,'recovery');
    const adherenceDelta=progressDeltaV249(now,prev,'adherence');

    if(sessionDelta>0&&(!Number.isFinite(recoveryDelta)||recoveryDelta>=-1)){
      return {
        tone:'good',
        title:'Más constancia en las últimas 4 semanas',
        copy:'Registraste más sesiones que en el período anterior sin una caída marcada de recuperación.'
      };
    }
    if((Number.isFinite(energyDelta)&&energyDelta<=-2)||(Number.isFinite(recoveryDelta)&&recoveryDelta<=-2)){
      return {
        tone:'warn',
        title:'Conviene mirar recuperación',
        copy:'Energía o recuperación bajaron frente a las 4 semanas anteriores. Usá el check-in para dar contexto antes de ajustar el plan.'
      };
    }
    if(Number.isFinite(adherenceDelta)&&adherenceDelta>=1){
      return {
        tone:'good',
        title:'Adherencia en mejora',
        copy:'La adherencia media del check-in subió frente al período anterior.'
      };
    }
    if(sessionDelta<0){
      return {
        tone:'info',
        title:'Menos sesiones registradas',
        copy:'Hubo menos entrenamientos registrados que en las 4 semanas anteriores. Revisá contexto y disponibilidad antes de sacar conclusiones.'
      };
    }
    return {
      tone:'info',
      title:'Ritmo estable',
      copy:'La actividad reciente se mantiene relativamente estable frente al período anterior.'
    };
  }

  function progressMetricV249(label,value,delta,unit=''){
    return '<div class="v249-pulse-metric"><span>'+esc(label)+'</span>'+
      '<strong>'+esc(value)+'</strong>'+
      '<small>'+esc(progressDeltaTextV249(delta,unit))+' vs. 4 sem. previas</small></div>';
  }

  function injectProgressPulseV249(){
    const coachView=mode==='coach'&&coachTab==='student'&&coachStudentTab==='progress';
    const studentView=mode==='student'&&studentTab==='progress';
    if(!coachView&&!studentView)return;

    const host=el(coachView?'coachStudentBody':'studentSubBody');
    if(!host)return;
    el('v249ProgressPulse')?.remove();

    const s=student?.();if(!s)return;
    const current=periodSnapshotV249(s,progressPeriodV249(0));
    const previous=periodSnapshotV249(s,progressPeriodV249(28));
    const summary=progressPulseSummaryV249(current,previous);

    const card=document.createElement('section');
    card.id='v249ProgressPulse';
    card.className='card v249-progress-pulse '+summary.tone;
    card.innerHTML=
      '<div class="section-title v249-pulse-head"><div><div class="v225-section-kicker">PULSO 4 SEMANAS</div>'+
      '<h3>'+esc(summary.title)+'</h3><div class="muted tiny">'+esc(summary.copy)+'</div></div>'+
      '<span class="badge blue">28 días</span></div>'+
      '<div class="v249-pulse-grid">'+
        progressMetricV249('Entrenamientos',String(current.sessions),current.sessions-previous.sessions)+
        progressMetricV249('Series registradas',String(current.sets),current.sets-previous.sets)+
        progressMetricV249('Ejercicios progresados',String(current.progressed),current.progressed-previous.progressed)+
        progressMetricV249('Adherencia check-in',current.adherence==null?'—':round1(current.adherence)+'/10',progressDeltaV249(current,previous,'adherence'))+
        progressMetricV249('Energía',current.energy==null?'—':round1(current.energy)+'/10',progressDeltaV249(current,previous,'energy'))+
        progressMetricV249('Recuperación',current.recovery==null?'—':round1(current.recovery)+'/10',progressDeltaV249(current,previous,'recovery'))+
      '</div>'+
      '<div class="v249-pulse-foot">El resumen compara constancia, entrenamiento y bienestar. Peso y medidas siguen disponibles por separado en Progreso.</div>';

    host.prepend(card);
  }

  function hydrateProgressPulseV249(){
    const coachView=mode==='coach'&&coachTab==='student'&&coachStudentTab==='progress';
    const studentView=mode==='student'&&studentTab==='progress';
    if(!coachView&&!studentView)return;

    injectProgressPulseV249();

    if(!cloudEnabled||!supabaseClient)return;
    const athleteId=trackingAthleteId?.();
    if(athleteId&&trackingLoadedFor===athleteId){
      injectProgressPulseV249();
      return;
    }
    loadTracking(false).then(()=>{
      const stillCoach=mode==='coach'&&coachTab==='student'&&coachStudentTab==='progress';
      const stillStudent=mode==='student'&&studentTab==='progress';
      if(stillCoach||stillStudent)injectProgressPulseV249();
    }).catch(()=>{});
  }

"""
    body=body.replace(anchor,helpers+anchor,1)
    body=body.replace(anchor,anchor+"\n    hydrateProgressPulseV249();",1)

    marker_old="""    checkinReplyAcknowledgement:true
  };"""
    marker_new="""    checkinReplyAcknowledgement:true,
    progressPulseFourWeeks:true,
    progressPulseAvoidsBodyJudgement:true
  };"""
    if body.count(marker_old)!=1:
        raise RuntimeError("V20.49 V175 marker mismatch")
    body=body.replace(marker_old,marker_new,1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

css=r"""
/* TEAM FJZ · V20.49 PROGRESS PULSE */
.v249-progress-pulse{
  border-color:#30343c;
  margin-bottom:14px;
}
.v249-progress-pulse.good{border-left:3px solid #3bd58a}
.v249-progress-pulse.warn{border-left:3px solid #f2bd55}
.v249-progress-pulse.info{border-left:3px solid #67adff}
.v249-pulse-head{align-items:flex-start}
.v249-pulse-grid{
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:8px;
}
.v249-pulse-metric{
  padding:11px;
  border:1px solid #2c3038;
  border-radius:11px;
  background:#0d0e12;
}
.v249-pulse-metric>span{
  display:block;color:#8d929c;font-size:8px;font-weight:800;text-transform:uppercase;letter-spacing:.05em
}
.v249-pulse-metric>strong{
  display:block;margin-top:5px;color:#f5f6f8;font-size:18px;font-weight:920
}
.v249-pulse-metric>small{
  display:block;margin-top:6px;color:#999da7;font-size:8px;line-height:1.35
}
.v249-pulse-foot{
  margin-top:9px;color:#858a95;font-size:8px;line-height:1.45
}
@media(max-width:650px){
  .v249-pulse-grid{grid-template-columns:1fr 1fr}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V20.49 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-progress-pulse" content="20.49">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.49 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-progress-pulse" content="20.49"',
    "injectProgressPulseV249","hydrateProgressPulseV249",
    "PULSO 4 SEMANAS","Más constancia","Conviene mirar recuperación",
    "progressPulseFourWeeks:true","progressPulseAvoidsBodyJudgement:true"
]:
    if marker not in html:
        raise RuntimeError("V20.49 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.49 progress pulse")
print("V20.49 BEFORE:",before)
print("V20.49 AFTER:",after)
print("V20.49 four-week training/wellness comparison added without body judgement")
