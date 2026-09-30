import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

before_metrics={
    "bytes":len(html),
    "scripts":len(re.findall(r"<script\b",html)),
    "styles":len(re.findall(r"<style\b",html)),
    "render_assignments":len(re.findall(r"(?:window\.)?render\s*=\s*function",html)),
    "mutation_observers":len(re.findall(r"new\s+MutationObserver",html)),
    "timeouts":len(re.findall(r"setTimeout\s*\(",html)),
}

removed=[]
def remove_tag(tag, ident):
    global html
    pat=rf'<{tag}\s+id="{re.escape(ident)}"[^>]*>.*?</{tag}>\s*'
    html,n=re.subn(pat,'',html,count=1,flags=re.S)
    if n: removed.append(ident)
    return n

for ident in [
    "v123AlertCenterCleanupStyles","v123AlertCenterCleanupRuntime",
    "v154CheckinScoreStyles","v154CheckinScoreRuntime",
    "v157CompactCheckinStyles","v157CompactCheckinRuntime",
    "v159MobileLayoutCheckinRenderStyles","v159MobileLayoutCheckinRenderRuntime",
    "v160SimpleCheckinInputStyles","v160SimpleCheckinInputRuntime",
    "v161UnifiedCoachSummaryStyles","v161UnifiedCoachSummaryRuntime",
    "v162CoachPanelDedupGuidanceStyles","v162CoachPanelDedupGuidanceRuntime",
    "v163SummaryIdentityCleanupStyles","v163SummaryIdentityCleanupRuntime",
    "v164AgendaReliabilityStyles","v164AgendaReliabilityRuntime",
    "v167CheckinCleanupFullCoachStyles","v167CheckinCleanupFullCoachRuntime",
]:
    remove_tag("style" if "Styles" in ident else "script",ident)

# Retire V12.4's separate Administration card; the same actions live in the V17 hero.
html=html.replace("    setTimeout(injectCoachAdminCardV124,60);\n","",1)

# V9.6 used three delayed reinjections after every render. Keep one scheduled pass.
old_v96="""  const oldRenderV96=window.render;
  window.render=function(){
    oldRenderV96();
    setTimeout(injectAlertsV96,80);
    setTimeout(injectAlertsV96,500);
    setTimeout(injectAlertsV96,1100);
  };"""
new_v96="""  const oldRenderV96=window.render;
  window.render=function(){
    oldRenderV96();
    if(typeof window.fjzPostRenderV125==='function'){
      window.fjzPostRenderV125('v170-alert-inject',injectAlertsV96);
    }else{
      setTimeout(injectAlertsV96,80);
    }
  };"""
if old_v96 in html:
    html=html.replace(old_v96,new_v96,1)

# V123's style was already merged by the V14 style consolidator, so 19 runtime/style
# blocks physically remain at this stage. All required obsolete runtimes are checked below.
if len(removed)!=19:
    raise RuntimeError("V17.0 expected 19 obsolete blocks removed, got "+str(len(removed)))

css=r"""
<style id="v170ConsolidatedRuntimeStyles">
#view{overflow-anchor:none!important}
.v170-coach-hero{align-items:center!important;margin-bottom:14px!important}
.v170-coach-hero h2{font-size:27px}
.v170-coach-actions{display:flex;gap:7px;flex-wrap:wrap;justify-content:flex-end}
.v170-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px;margin-bottom:14px}
.v170-kpi{min-width:0;border:1px solid var(--border);border-radius:14px;padding:13px;background:linear-gradient(180deg,rgba(255,255,255,.025),transparent),#0d0d10}
.v170-kpi strong{display:block;font-size:24px;line-height:1}
.v170-kpi span{display:block;margin-top:6px;font-size:10px;color:var(--muted);line-height:1.25}
.v170-dashboard{display:grid;gap:14px}
.v170-section-head{display:flex;align-items:flex-start;justify-content:space-between;gap:10px;margin-bottom:10px}
.v170-section-head h3{margin:0;font-size:16px}
.v170-section-head p{margin:4px 0 0;color:var(--muted);font-size:11px;line-height:1.4}
.v170-alert-card{border-color:#32323a!important;background:linear-gradient(180deg,rgba(255,255,255,.018),transparent),#0d0d10!important}
#v96CoachAlerts .v96-alert-summary{grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:7px!important;margin:10px 0!important}
#v96CoachAlerts .v96-alert-kpi{padding:10px!important;background:#0b0b0e!important}
#v96CoachAlerts .v96-alert-kpi strong{font-size:19px!important}
#v96CoachAlerts .v96-alert-tools{position:static!important;background:transparent!important;padding:0!important;margin:10px 0!important;gap:6px!important}
#v96CoachAlerts .v96-alert-list{gap:7px!important}
#v96CoachAlerts .v96-alert-card{border-radius:12px!important;padding:10px!important;grid-template-columns:30px minmax(0,1fr) auto!important;box-shadow:none!important}
#v96CoachAlerts .v96-alert-icon{width:30px!important;height:30px!important;border-radius:9px!important}
#v96CoachAlerts .v96-alert-body{line-height:1.35!important}
.v170-students-card .section-title{margin-top:0!important}
.student-row{min-width:0!important;content-visibility:auto;contain-intrinsic-size:70px}
.student-main,.student-main>div{min-width:0!important}
.student-main strong,.student-main .muted{overflow-wrap:anywhere}
.v170-overview{display:grid;gap:12px}
.v170-summary-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.v170-summary-metric{min-width:0;padding:10px;border:1px solid var(--border);border-radius:12px;background:rgba(255,255,255,.02)}
.v170-summary-metric strong{display:block;font-size:17px;line-height:1.15;overflow-wrap:anywhere}
.v170-summary-metric span{display:block;margin-top:4px;font-size:9px;line-height:1.3;color:var(--muted)}
.v170-summary-section{padding-top:11px;border-top:1px solid var(--border)}
.v170-summary-signals{display:flex;flex-wrap:wrap;gap:6px}
.v170-signal{display:inline-flex;align-items:center;min-height:27px;padding:5px 8px;border:1px solid var(--border);border-radius:999px;font-size:9px;color:var(--muted);background:rgba(255,255,255,.02)}
.v170-signal.warn{color:#ffc6ca;border-color:rgba(255,82,97,.28);background:rgba(255,82,97,.055)}
.v170-guide-list{display:grid;gap:7px}
.v170-guide{padding:9px 10px;border:1px solid var(--border);border-radius:11px;background:rgba(255,255,255,.02)}
.v170-guide.warn{border-color:rgba(255,82,97,.24);background:rgba(255,82,97,.045)}
.v170-guide.good{border-color:rgba(53,208,127,.20);background:rgba(53,208,127,.035)}
.v170-guide-top{display:flex;justify-content:space-between;gap:8px;align-items:flex-start}
.v170-guide h4{margin:0;font-size:11px;line-height:1.3}
.v170-guide p{margin:5px 0 0;font-size:10px;line-height:1.4;color:var(--muted)}
.v170-overview-actions{display:flex;flex-wrap:wrap;gap:7px}
.v170-checkin-scores{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.v170-score-row{display:grid;grid-template-columns:minmax(0,1fr) 78px;gap:10px;align-items:center;padding:10px 12px;border:1px solid var(--border);border-radius:12px;background:var(--card);min-width:0}
.v170-score-row strong{display:block;font-size:12px}
.v170-score-row small{display:block;margin-top:2px;font-size:9px;color:var(--muted)}
.v170-score-box{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:5px;align-items:center;min-width:0}
.v170-score-input{width:100%!important;height:40px!important;padding:6px 8px!important;text-align:center!important;font-size:17px!important;font-weight:900!important;pointer-events:auto!important;touch-action:manipulation!important}
.v170-score-box span{font-size:10px;color:var(--muted);font-weight:800}
.v170-checkin-sent{padding:10px 12px;border:1px solid rgba(53,208,127,.25);border-radius:12px;background:rgba(53,208,127,.045);margin-bottom:10px}
.v170-checkin-sent-head{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
.v170-checkin-metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px;margin-top:9px}
.v170-checkin-metric{min-width:0;padding:8px 9px;border:1px solid var(--border);border-radius:10px;background:rgba(255,255,255,.02)}
.v170-checkin-metric span{display:block;font-size:9px;color:var(--muted)}
.v170-checkin-metric strong{display:block;margin-top:3px;font-size:14px}
.v170-track-row{content-visibility:auto;contain-intrinsic-size:220px}
body.v158-rendering #view{min-height:calc(100dvh - 145px)!important}
@media(max-width:900px){
  .v170-coach-hero{align-items:flex-start!important}
  .v170-coach-actions{justify-content:flex-start}
  .v170-kpis{grid-template-columns:repeat(2,minmax(0,1fr))}
  .v170-summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
  #v96CoachAlerts .v96-alert-card{grid-template-columns:30px minmax(0,1fr)!important}
  #v96CoachAlerts .v96-alert-actions{grid-column:1/-1!important;padding-left:38px!important;justify-content:flex-start!important}
  .student-row{grid-template-columns:minmax(0,1fr) 64px!important;gap:9px!important;padding:11px!important;align-items:center!important}
  .student-row>div:nth-child(2),.student-row>div:nth-child(3),.student-row>div:nth-child(4){display:none!important}
  .student-row>.btn:last-child{width:64px!important;min-width:64px!important;padding:8px 6px!important}
  .student-main{display:grid!important;grid-template-columns:44px minmax(0,1fr)!important;column-gap:10px!important;row-gap:4px!important}
  .student-main>.v70-student-avatar-slot,.student-main>.avatar{grid-column:1!important;grid-row:1 / span 2!important;width:44px!important;min-width:44px!important}
  .student-main>div:nth-child(2){grid-column:2!important;min-width:0!important}
  .student-main>.v80-student-alert-count{grid-column:2!important;justify-self:start!important;margin:0!important}
  .topbar,.bottom-nav{-webkit-backdrop-filter:none!important;backdrop-filter:none!important}
}
@media(max-width:700px){
  .v170-checkin-scores{grid-template-columns:1fr}
  .v170-checkin-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}
  #v96CoachAlerts .v96-alert-summary{grid-template-columns:repeat(2,minmax(0,1fr))!important}
}
@media(max-width:520px){
  .shell{padding-left:10px!important;padding-right:10px!important}
  .card{padding:13px!important}
  .v170-coach-hero h2{font-size:23px}
  .v170-coach-actions{display:grid;grid-template-columns:1fr 1fr;width:100%}
  .v170-coach-actions .btn{width:100%}
}
</style>
"""

js=r"""
<script id="v170ConsolidatedRuntime">
(function(){
  const VERSION='17.0';
  let checkinBusy=false;
  let editingCheckinWeek='';
  let summarySeq=0;
  const CHECKIN=[
    ['Sueño','ciSleep','sleep_quality'],['Hambre','ciHunger','hunger_level'],
    ['Estrés','ciStress','stress_level'],['Energía','ciEnergy','energy_level'],
    ['Adherencia','ciAdh','adherence_level'],['Ánimo','ciMood','mood_level'],
    ['Motivación','ciMotivation','motivation_level'],['Recuperación','ciRecovery','recovery_level']
  ];

  const metricV170=(value,label)=>'<div class="v170-summary-metric"><strong>'+esc(String(value??'—'))+'</strong><span>'+esc(label)+'</span></div>';
  const signalV170=(text,warn=false)=>'<span class="v170-signal '+(warn?'warn':'')+'">'+esc(text)+'</span>';

  function dedupPhotosV170(){
    if(!trackingCache||!Array.isArray(trackingCache.photos))return;
    const seen=new Set();
    trackingCache.photos=trackingCache.photos.filter(x=>{
      const k=String(x?.storage_path||x?.id||'');
      if(!k||seen.has(k))return false;
      seen.add(k);return true;
    });
  }
  const basePhotoGridV170=window.renderPhotoGrid;
  if(typeof basePhotoGridV170==='function'){
    window.renderPhotoGrid=async function(targetId){
      dedupPhotosV170();
      const out=await basePhotoGridV170.apply(this,arguments);
      const root=el(targetId);
      if(root){
        const seen=new Set();
        root.querySelectorAll('img').forEach(img=>{
          const src=String(img.getAttribute('src')||'').split('?')[0];
          if(!src)return;
          if(seen.has(src))img.closest('.photo-slot,.photo-card')?.remove();
          else seen.add(src);
        });
      }
      return out;
    };
  }

  function decorateCoachFeedV170(feed){
    if(el('v170AlertTotal'))el('v170AlertTotal').textContent=String(feed?.length||0);
    const byAthlete=new Map();
    (feed||[]).forEach(x=>byAthlete.set(x.athlete_id,(byAthlete.get(x.athlete_id)||0)+1));
    document.querySelectorAll('.student-row[data-client-id]').forEach(row=>{
      row.querySelector('.v80-student-alert-count')?.remove();
      const ath=cloudAthletes?.get?.(row.getAttribute('data-client-id'));
      const n=ath?byAthlete.get(ath.id)||0:0;
      if(n){
        const main=row.querySelector('.student-main');
        if(main)main.insertAdjacentHTML('beforeend','<span class="v73-alert-badge v80-student-alert-count">'+n+'</span>');
      }
    });
  }

  function renderCoachDashboardV170(){
    const v=el('view'),total=state.students.length;
    const review=state.students.filter(s=>statusFor(s)==='Revisar').length;
    const avg=Math.round(state.students.reduce((a,s)=>a+adherence(s),0)/Math.max(1,total));
    v.innerHTML='<section class="hero v170-coach-hero"><div><h2>Panel Coach</h2><p>Alumnos, alertas y acciones importantes en una sola vista.</p></div>'+
      '<div class="v170-coach-actions"><button class="btn" onclick="showTemplates()">Plantillas</button>'+
      '<button class="btn" onclick="coachTab=\'payments\';render()">Pagos</button>'+
      '<button class="btn" onclick="openNoticePickerV124()">Enviar alerta</button>'+
      '<button class="btn primary" onclick="newStudent()">+ Nuevo alumno</button></div></section>'+
      '<div class="v170-kpis"><div class="v170-kpi"><strong>'+total+'</strong><span>Alumnos activos</span></div>'+
      '<div class="v170-kpi"><strong>'+review+'</strong><span>Requieren revisión</span></div>'+
      '<div class="v170-kpi"><strong>'+avg+'%</strong><span>Adherencia media · 7 días</span></div>'+
      '<div class="v170-kpi"><strong id="v170AlertTotal">—</strong><span>Alertas activas</span></div></div>'+
      '<div class="v170-dashboard"><div id="v96CoachAlerts" class="card v170-alert-card">'+
      '<div class="v170-section-head"><div><h3>Centro de seguimiento</h3><p>Prioriza check-ins, recuperación, comentarios, entrenamiento, nutrición y pagos.</p></div>'+
      '<button class="btn small" onclick="refreshCoachAlertsV96(true)">Actualizar</button></div>'+
      '<div id="v96CoachAlertBody"><div class="empty">Cargando alertas…</div></div></div>'+
      '<div class="card v170-students-card"><div class="section-title"><div><h3>Alumnos</h3><div class="muted tiny">Estado general y acceso directo a cada ficha.</div></div>'+
      '<input id="studentSearch" class="input" style="max-width:270px" placeholder="Buscar alumno..."></div>'+
      '<div class="student-list" id="studentList">'+studentRows(state.students)+'</div></div></div>';

    const search=el('studentSearch');
    if(search)search.oninput=e=>{
      const q=typeof normalizeTextV70==='function'?normalizeTextV70(e.target.value):String(e.target.value||'').toLowerCase();
      const list=state.students.filter(s=>{
        const n=typeof normalizeTextV70==='function'?normalizeTextV70(s.name):String(s.name||'').toLowerCase();
        const g=typeof normalizeTextV70==='function'?normalizeTextV70(s.goal||''):String(s.goal||'').toLowerCase();
        return n.includes(q)||g.includes(q);
      });
      el('studentList').innerHTML=studentRows(list);
      try{loadCoachAvatarsV70?.()}catch(e){}
      loadCoachFeed(false).then(decorateCoachFeedV170).catch(()=>{});
    };
    try{loadCoachAvatarsV70?.()}catch(e){}
    try{refreshCoachAlertsV96(false)}catch(e){}
    loadCoachFeed(false).then(decorateCoachFeedV170).catch(()=>{if(el('v170AlertTotal'))el('v170AlertTotal').textContent='—'});
  }

  const baseRenderCoachV170=window.renderCoach;
  window.renderCoach=function(){
    if(coachTab==='dashboard')return renderCoachDashboardV170();
    return baseRenderCoachV170.apply(this,arguments);
  };

  window.openCoachAlertV96=async function(athleteId,key,kind){
    if(key){try{await window.readCoachAlertV96(key)}catch(e){}}
    if(kind==='payment'){coachTab='payments';render();return}
    const row=[...cloudAthletes.values()].find(x=>x.id===athleteId);
    if(!row){toast('No encuentro esa ficha');return}
    state.selectedStudentId=row.client_id;saveState();coachTab='student';
    coachStudentTab={exercise_feedback:'routine',checkin:'tracking',wellness:'tracking',training:'summary',progression:'progress',nutrition:'nutrition'}[kind]||'summary';
    render();
  };

  function buildGuidanceV170(){
    const s=student(),latest=trackingCache?.checkins?.[0]||null;
    const pending=typeof pendingFeedbackV73==='function'?pendingFeedbackV73():[];
    const list=[],push=(type,priority,title,copy,tab)=>list.push({type,priority,title,copy,tab});
    if(!s?.days?.length)push('warn',100,'Falta una rutina activa','Sin una estructura semanal no hay una base clara para interpretar adherencia o progresión.','routine');
    if(pending?.length)push('warn',96,'Revisar comentarios de ejercicios',pending.length+' comentario'+(pending.length===1?'':'s')+' pendiente'+(pending.length===1?'':'s')+'.','routine');
    const d=typeof daysSince==='function'?daysSince(s?.lastWorkout):null;
    if(Number.isFinite(d)&&d>=7)push('warn',92,'Revisar continuidad','Hay '+d+' días desde el último entrenamiento registrado.','history');
    if(latest){
      const weak=[];
      if(Number(latest.sleep_quality)<=4)weak.push('sueño');
      if(Number(latest.energy_level)<=4)weak.push('energía');
      if(Number(latest.recovery_level)<=4)weak.push('recuperación');
      if(Number(latest.stress_level)>=8)weak.push('estrés');
      if(weak.length>=2)push('warn',90,'Revisar recuperación','Hay varias señales para revisar antes de aumentar exigencia: '+weak.join(', ')+'.','tracking');
      if(Number(latest.adherence_level)<=5)push('info',82,'Revisar adherencia','Conviene identificar qué parte del plan le cuesta sostener antes de sumar tareas.','tracking');
    }else push('info',78,'Falta un check-in reciente','Sin check-in hay menos contexto para interpretar rendimiento y recuperación.','tracking');
    try{
      if(nutritionCache?.plan&&typeof nutritionAdherenceV63==='function'){
        const a=nutritionAdherenceV63();
        if(a.expected>=4&&a.pct<50)push('info',68,'Confirmar registro nutricional','Hay pocos registros del plan; primero conviene confirmar si faltó cumplirlo o solo registrarlo.','nutrition');
      }
    }catch(e){}
    if(!list.length)push('good',20,'Mantener la base','No aparece una señal fuerte para modificar el plan ahora. Seguiría observando tendencia y ejecución.','progress');
    return list.sort((a,b)=>b.priority-a.priority).slice(0,3);
  }

  function renderGuidanceV170(){
    const box=el('v170Guidance');if(!box)return;
    box.innerHTML=buildGuidanceV170().map(x=>'<div class="v170-guide '+esc(x.type)+'"><div class="v170-guide-top"><h4>'+esc(x.title)+'</h4>'+
      '<span class="badge '+(x.type==='warn'?'red':x.type==='good'?'green':'blue')+'">'+(x.type==='warn'?'Revisar':x.type==='good'?'Bien':'Sugerencia')+'</span></div>'+
      '<p>'+esc(x.copy)+'</p><button class="btn small" style="margin-top:7px" onclick="coachStudentTab=\''+esc(x.tab)+'\';render()">Abrir</button></div>').join('');
  }

  function updateSummaryV170(){
    const card=el('v170CoachOverview');if(!card)return;
    const s=student(),latest=trackingCache?.checkins?.[0]||null,meas=trackingCache?.measurements?.[0]||null;
    const sessions30=typeof progressSessionsInDaysV72==='function'?progressSessionsInDaysV72(s,30).length:(s.sessions||[]).length;
    const weight=meas?.weight_kg??latest?.weight_kg??null;
    if(el('v170SummaryGrid'))el('v170SummaryGrid').innerHTML=
      metricV170(adherence(s)+'%','Adherencia 7 días')+metricV170(sessions30,'Entrenos 30 días')+
      metricV170(fmtDate(s.lastWorkout),'Último entreno')+metricV170(weight!=null?round1(weight)+' kg':'—','Peso reciente')+
      metricV170(latest?.energy_level!=null?latest.energy_level+'/10':'—','Energía')+
      metricV170(latest?.recovery_level!=null?latest.recovery_level+'/10':'—','Recuperación')+
      metricV170(latest?.sleep_quality!=null?latest.sleep_quality+'/10':'—','Sueño')+
      metricV170(latest?.stress_level!=null?latest.stress_level+'/10':'—','Estrés');
    const signals=[];
    if(latest?.week_start)signals.push(signalV170('Check-in '+fmtDate(latest.week_start))); else signals.push(signalV170('Sin check-in reciente',true));
    if(nutritionCache?.plan)signals.push(signalV170('Plan nutricional activo')); else signals.push(signalV170('Sin plan nutricional',true));
    const pending=typeof pendingFeedbackV73==='function'?pendingFeedbackV73().length:0;
    if(pending)signals.push(signalV170(pending+' comentario'+(pending===1?'':'s')+' pendiente'+(pending===1?'':'s'),true));
    if(!pending&&latest)signals.push(signalV170('Sin alertas críticas'));
    if(el('v170SummarySignals'))el('v170SummarySignals').innerHTML=signals.join('');
    renderGuidanceV170();if(el('v170SummaryState'))el('v170SummaryState').textContent='Datos actualizados';
  }

  async function hydrateSummaryV170(){
    const seq=++summarySeq,athleteId=trackingAthleteId?.(),jobs=[];
    if(athleteId&&trackingLoadedFor!==athleteId&&typeof loadTracking==='function')jobs.push(loadTracking(false));
    const nAth=nutritionAthleteId?.(),nutritionReady=nAth&&nutritionLoadedAthlete===nAth&&nutritionFoodsLoaded===true;
    if(nAth&&!nutritionReady&&typeof loadNutrition==='function')jobs.push(loadNutrition(false,nutritionCache?.date||dateInputToday()));
    try{if(typeof loadExerciseFeedbackV73==='function')jobs.push(loadExerciseFeedbackV73(false))}catch(e){}
    await Promise.allSettled(jobs);
    if(seq!==summarySeq||coachTab!=='student'||coachStudentTab!=='summary')return;
    updateSummaryV170();
  }

  window.renderCoachSummary=function(){
    const s=student(),b=el('coachStudentBody');if(!b)return;
    b.innerHTML='<div class="v170-overview"><div class="card" id="v170CoachOverview">'+
      '<div class="v170-section-head"><div><h3>Resumen 360</h3><p>Estado, seguimiento y señales útiles sin repetir la información del encabezado.</p></div>'+
      '<span id="v170SummaryState" class="muted micro">Actualizando…</span></div>'+
      '<div id="v170SummaryGrid" class="v170-summary-grid">'+metricV170(adherence(s)+'%','Adherencia 7 días')+metricV170('—','Entrenos 30 días')+
      metricV170(fmtDate(s.lastWorkout),'Último entreno')+metricV170('—','Peso reciente')+metricV170('—','Energía')+metricV170('—','Recuperación')+metricV170('—','Sueño')+metricV170('—','Estrés')+'</div>'+
      '<div class="v170-summary-section"><div class="v170-section-head"><div><h3>Estado conectado</h3><p>Check-in, nutrición y comentarios pendientes.</p></div></div><div id="v170SummarySignals" class="v170-summary-signals">'+signalV170('Cargando datos…')+'</div></div>'+
      '<div class="v170-summary-section"><div class="v170-section-head"><div><h3>Sugerencias del coach</h3><p>Máximo tres acciones concretas. No modifica ningún plan automáticamente.</p></div></div><div id="v170Guidance" class="v170-guide-list"></div></div>'+
      '<div class="v170-summary-section"><div class="section-title"><div><h3>Mensaje para el alumno</h3><div class="muted tiny">Mensaje general visible para el alumno.</div></div><button class="btn small" onclick="editCoachMessage()">Editar</button></div>'+
      '<div class="coach-note">'+esc(s.coachMessage||'Sin mensaje cargado.')+'</div></div>'+
      '<div class="v170-overview-actions"><button class="btn primary small" onclick="coachStudentTab=\'routine\';render()">Rutina</button><button class="btn small" onclick="coachStudentTab=\'progress\';render()">Progreso</button>'+
      '<button class="btn small" onclick="coachStudentTab=\'tracking\';render()">Seguimiento</button><button class="btn small" onclick="coachStudentTab=\'nutrition\';render()">Nutrición</button><button class="btn small" onclick="coachStudentTab=\'agenda\';render()">Agenda</button></div>'+
      '</div></div>';
    hydrateSummaryV170();
  };

  const scoreInputV170=(label,id)=>'<div class="v170-score-row"><div><strong>'+esc(label)+'</strong><small>Escribí del 1 al 10</small></div><div class="v170-score-box">'+
    '<input id="'+id+'" class="input v170-score-input" type="tel" inputmode="numeric" pattern="[0-9]*" maxlength="2" autocomplete="off" placeholder="—"><span>/10</span></div></div>';
  function normalizeScoreV170(input,finalize=false){
    if(!input)return;let raw=String(input.value||'').replace(/[^0-9]/g,'').slice(0,2);
    if(!raw){input.value='';return}let n=parseInt(raw,10);if(n>10)n=10;if(finalize&&n<1){input.value='';return}input.value=String(n);
  }
  function bindScoreInputsV170(){CHECKIN.forEach(([,id])=>{const x=el(id);if(x){x.oninput=()=>normalizeScoreV170(x,false);x.onblur=()=>normalizeScoreV170(x,true)}})}
  function currentCheckinV170(){const week=el('ciWeek')?.value||weekStartISO();return (trackingCache?.checkins||[]).find(x=>x.week_start===week)||null}
  function clearCheckinV170(){CHECKIN.forEach(([,id])=>{if(el(id))el(id).value=''});if(el('ciWeight'))el('ciWeight').value='';if(el('ciNotes'))el('ciNotes').value=''}
  function fillCheckinV170(row){if(!row)return;CHECKIN.forEach(([,id,key])=>{if(el(id))el(id).value=row[key]??''});if(el('ciWeight'))el('ciWeight').value=row.weight_kg??'';if(el('ciNotes'))el('ciNotes').value=row.notes||''}
  function renderSentStateV170(){
    const host=el('v170CheckinStatus');if(!host)return;const row=currentCheckinV170();
    if(!row){host.innerHTML='';editingCheckinWeek='';return}
    if(editingCheckinWeek===row.week_start){host.innerHTML='<div class="v170-checkin-sent"><div class="v170-checkin-sent-head"><div><strong>Editando check-in enviado</strong><div class="muted tiny">Al enviarlo se actualizará esta misma semana.</div></div><span class="badge blue">Edición</span></div></div>';return}
    clearCheckinV170();host.innerHTML='<div class="v170-checkin-sent"><div class="v170-checkin-sent-head"><div><strong>Check-in enviado</strong><div class="muted tiny">Semana '+esc(row.week_start)+' · formulario limpio.</div></div><button class="btn small" type="button" onclick="editCheckinV170()">Editar</button></div></div>';
  }
  window.editCheckinV170=function(){const row=currentCheckinV170();if(!row)return;editingCheckinWeek=row.week_start;fillCheckinV170(row);renderSentStateV170();el('ciSleep')?.focus()};

  window.renderTrackingStudent=function(){
    const b=el('studentSubBody');if(!b)return;
    b.innerHTML='<div class="card"><div class="section-title"><div><h3>Check-in semanal</h3><div class="muted tiny">Completá los 8 indicadores del 1 al 10.</div></div><span class="badge blue">1–10</span></div>'+
      '<div class="tracking-form"><div id="v170CheckinStatus"></div><div class="form-grid"><label class="tiny muted">Peso actual (kg)<input id="ciWeight" class="input" type="number" min="20" max="400" step="0.1" placeholder="Opcional"></label>'+
      '<label class="tiny muted">Semana<input id="ciWeek" class="input" type="date" value="'+weekStartISO()+'"></label></div><div class="v170-checkin-scores">'+CHECKIN.map(x=>scoreInputV170(x[0],x[1])).join('')+'</div>'+
      '<label class="tiny muted">Comentarios<textarea id="ciNotes" class="input" rows="4" placeholder="Cómo te sentiste, dificultades, molestias, cambios de horarios..."></textarea></label>'+
      '<button class="btn primary" style="width:100%" onclick="submitWeeklyCheckin()">Enviar check-in</button></div></div>'+
      '<div style="height:14px"></div><div class="card"><div class="section-title"><div><h3>Peso y medidas</h3><div class="muted tiny">Registrá tus medidas cuando corresponda.</div></div></div>'+
      '<div class="form-grid"><label class="tiny muted">Fecha<input id="mDate" class="input" type="date" value="'+dateInputToday()+'"></label><label class="tiny muted">Peso kg<input id="mWeight" class="input" type="number" step="0.1"></label>'+
      '<label class="tiny muted">Cintura cm<input id="mWaist" class="input" type="number" step="0.1"></label><label class="tiny muted">Abdomen cm<input id="mAbd" class="input" type="number" step="0.1"></label>'+
      '<label class="tiny muted">Cadera cm<input id="mHip" class="input" type="number" step="0.1"></label><label class="tiny muted">Pecho cm<input id="mChest" class="input" type="number" step="0.1"></label></div>'+
      '<button class="btn" style="width:100%;margin-top:12px" onclick="submitMeasurement()">Guardar medición</button></div>'+
      '<div style="height:14px"></div><div class="card"><div class="section-title"><div><h3>Fotos de progreso</h3><div class="muted tiny">Privadas: solo vos y tu coach pueden acceder.</div></div><span class="badge blue">Privado</span></div>'+
      '<div class="form-grid"><label class="tiny muted">Fecha<input id="progressPhotoDate" class="input" type="date" value="'+dateInputToday()+'"></label><label class="tiny muted">Vista<select id="progressPhotoPose"><option value="front">Frente</option><option value="side">Perfil</option><option value="back">Espalda</option><option value="other">Otra</option></select></label>'+
      '<label class="tiny muted span2">Foto<input id="progressPhotoFile" class="input" type="file" accept="image/*"></label></div><button class="btn" style="width:100%;margin-top:10px" onclick="uploadProgressPhoto()">Subir foto</button></div>'+
      '<div id="trackingStudentHistory" style="margin-top:14px"><div class="empty">Cargando historial…</div></div>';
    bindScoreInputsV170();const week=el('ciWeek');if(week)week.onchange=()=>{editingCheckinWeek='';clearCheckinV170();renderSentStateV170()};
    loadTracking(false).then(()=>{dedupPhotosV170();renderStudentTrackingHistory();renderSentStateV170()}).catch(e=>{const h=el('trackingStudentHistory');if(h)h.innerHTML='<div class="empty">'+esc(cloudErr(e))+'</div>'});
  };

  const checkinScoreV170=id=>{const n=Number(el(id)?.value);return Number.isFinite(n)&&n>=1&&n<=10?n:null};
  window.submitWeeklyCheckin=async function(){
    if(checkinBusy)return;if(!cloudEnabled||!supabaseClient){toast('El check-in requiere modo nube');return}
    const athleteId=trackingAthleteId();if(!athleteId){toast('No encuentro tu ficha');return}
    const missing=CHECKIN.filter(([,id])=>checkinScoreV170(id)==null).map(x=>x[0]);if(missing.length){toast('Falta completar: '+missing.join(', '));return}
    const weightRaw=el('ciWeight')?.value,weight=weightRaw?Number(weightRaw):null;if(weight!=null&&(!Number.isFinite(weight)||weight<20||weight>400)){toast('Revisá el peso ingresado');return}
    const payload={athlete_id:athleteId,student_id:currentUser.id,week_start:el('ciWeek')?.value||weekStartISO(),weight_kg:weight,
      sleep_quality:checkinScoreV170('ciSleep'),hunger_level:checkinScoreV170('ciHunger'),stress_level:checkinScoreV170('ciStress'),energy_level:checkinScoreV170('ciEnergy'),
      adherence_level:checkinScoreV170('ciAdh'),mood_level:checkinScoreV170('ciMood'),motivation_level:checkinScoreV170('ciMotivation'),recovery_level:checkinScoreV170('ciRecovery'),
      notes:(el('ciNotes')?.value||'').trim(),submitted_at:new Date().toISOString()};
    const btn=[...document.querySelectorAll('.tracking-form button')].find(x=>/Enviar check-in/.test(x.textContent||''));checkinBusy=true;if(btn){btn.disabled=true;btn.textContent='Guardando…'}
    try{
      const {data,error}=await supabaseClient.from('weekly_checkins').upsert(payload,{onConflict:'athlete_id,week_start'}).select('*').single();
      if(error)throw error;if(!data?.id)throw new Error('La nube no confirmó el check-in.');
      student().checkin='Recibido';saveState();trackingLoadedFor=null;await loadTracking(true);dedupPhotosV170();renderStudentTrackingHistory();
      editingCheckinWeek='';clearCheckinV170();renderSentStateV170();toast('Check-in enviado');
    }catch(e){toast(cloudErr(e))}finally{checkinBusy=false;if(btn){btn.disabled=false;btn.textContent='Enviar check-in'}}
  };

  const checkinMetricGridV170=c=>'<div class="v170-checkin-metrics">'+CHECKIN.map(([label,,key])=>'<div class="v170-checkin-metric"><span>'+esc(label)+'</span><strong>'+(c?.[key]!=null?esc(String(c[key]))+'/10':'—')+'</strong></div>').join('')+'</div>';

  window.renderTrackingCoach=function(){
    const b=el('coachStudentBody');if(!b)return;const row=cloudAthletes.get(student()?.id);
    if(!row){b.innerHTML='<div class="empty">Sincronizá la ficha para habilitar seguimiento.</div>';return}
    b.innerHTML='<div class="empty">Cargando seguimiento…</div>';
    loadTracking(false).then(()=>{dedupPhotosV170();renderTrackingCoachLoaded()}).catch(e=>{b.innerHTML='<div class="empty">'+esc(cloudErr(e))+'</div>'});
  };

  window.renderTrackingCoachLoaded=function(){
    const b=el('coachStudentBody');if(!b)return;const cs=trackingCache.checkins||[],ms=trackingCache.measurements||[],latest=cs[0],lastM=ms[0],prevM=ms[1];
    const delta=lastM?.weight_kg&&prevM?.weight_kg?lastM.weight_kg-prevM.weight_kg:null;
    b.innerHTML='<div class="grid kpi"><div class="card"><strong>'+(lastM?.weight_kg??latest?.weight_kg??'—')+((lastM?.weight_kg||latest?.weight_kg)?' kg':'')+'</strong><span>Peso reciente</span></div>'+
      '<div class="card"><strong>'+(delta==null?'—':(delta>0?'+':'')+delta.toFixed(1)+' kg')+'</strong><span>Cambio último registro</span></div>'+
      '<div class="card"><strong>'+(latest?.adherence_level??'—')+(latest?'/10':'')+'</strong><span>Adherencia</span></div>'+
      '<div class="card"><strong>'+(latest?.recovery_level??'—')+(latest?'/10':'')+'</strong><span>Recuperación</span></div></div>'+
      (latest?'<div class="card" style="margin-bottom:14px"><div class="section-title"><div><h3>Último check-in completo</h3><div class="muted tiny">Semana '+esc(latest.week_start)+(latest.weight_kg?' · '+esc(String(latest.weight_kg))+' kg':'')+'</div></div><span class="badge blue">8 indicadores</span></div>'+
      checkinMetricGridV170(latest)+(latest.notes?'<div class="coach-note" style="margin-top:10px"><b>Comentario del alumno:</b> '+esc(latest.notes)+'</div>':'')+'</div>':'')+
      '<div class="grid two"><div class="card"><div class="section-title"><div><h3>Check-ins semanales</h3><div class="muted tiny">Todos los indicadores y tu feedback.</div></div></div>'+
      (cs.length?cs.map(c=>'<div class="track-row v170-track-row"><div class="track-row-head"><div><strong>Semana '+esc(c.week_start)+'</strong><div class="muted tiny">'+(c.weight_kg?esc(String(c.weight_kg))+' kg · ':'')+'8 indicadores completos</div></div><span class="badge blue">Check-in</span></div>'+
      checkinMetricGridV170(c)+(c.notes?'<p class="muted tiny">'+esc(c.notes)+'</p>':'')+
      '<div class="form-grid" style="margin-top:10px"><textarea id="fb_'+esc(c.id)+'" class="input span2" rows="2" placeholder="Feedback para el alumno">'+esc(c.coach_feedback||'')+'</textarea><button class="btn small" onclick="saveCheckinFeedback(\''+esc(c.id)+'\')">Guardar feedback</button></div></div>').join(''):'<div class="empty">El alumno todavía no envió check-ins.</div>')+
      '</div><aside class="card"><div class="section-title"><h3>Agregar medición</h3></div><div class="form-grid"><label class="tiny muted">Fecha<input id="mDate" class="input" type="date" value="'+dateInputToday()+'"></label>'+
      '<label class="tiny muted">Peso kg<input id="mWeight" class="input" type="number" step="0.1"></label><label class="tiny muted">Cintura<input id="mWaist" class="input" type="number" step="0.1"></label>'+
      '<label class="tiny muted">Abdomen<input id="mAbd" class="input" type="number" step="0.1"></label><label class="tiny muted">Cadera<input id="mHip" class="input" type="number" step="0.1"></label><label class="tiny muted">Pecho<input id="mChest" class="input" type="number" step="0.1"></label></div>'+
      '<button class="btn primary" style="width:100%;margin-top:10px" onclick="submitMeasurement()">Guardar</button><div class="section-title" style="margin-top:18px"><h3>Tendencias</h3></div>'+simpleLineChart(ms,'weight_kg','Peso')+simpleLineChart(ms,'waist_cm','Cintura')+'</aside></div>'+
      '<div class="card" style="margin-top:14px"><div class="section-title"><div><h3>Fotos de progreso</h3><div class="muted tiny">Una sola galería, organizada por mes.</div></div></div><div id="coachPhotoGrid"><div class="empty">Cargando fotos…</div></div></div>';
    renderPhotoGrid('coachPhotoGrid');
  };

  window.saveCheckinFeedback=async function(id){
    const value=(el('fb_'+id)?.value||'').trim();
    const {data,error}=await supabaseClient.from('weekly_checkins').update({coach_feedback:value,reviewed_at:new Date().toISOString()}).eq('id',id).select('id,coach_feedback,reviewed_at').single();
    if(error){toast(cloudErr(error));return}
    const row=(trackingCache.checkins||[]).find(x=>x.id===id);if(row&&data)Object.assign(row,data);toast('Feedback guardado');
  };

  const baseProgressV170=window.renderProgress;
  if(typeof baseProgressV170==='function'){
    window.renderProgress=function(isCoach,targetId){
      const out=baseProgressV170.apply(this,arguments);
      if(isCoach&&currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='progress'){
        const go=()=>{if(coachStudentTab==='progress'&&!el('monthlyCompareCard')&&typeof injectMonthlyComparisonV53==='function')injectMonthlyComparisonV53()};
        const athleteId=trackingAthleteId?.();
        if(athleteId&&trackingLoadedFor===athleteId)go(); else loadTracking(false).then(()=>{dedupPhotosV170();go()}).catch(()=>{});
      }
      return out;
    };
  }

  window.__fjzRuntimeV170={version:VERSION,consolidated:true,obsoleteRuntimeBlocksRemoved:19,canonicalDashboard:true,canonicalSummary:true,canonicalCheckin:true,alertReinjectCoalesced:true,photoDedup:true};
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for ident in [
    "v154CheckinScoreRuntime","v157CompactCheckinRuntime","v159MobileLayoutCheckinRenderRuntime",
    "v160SimpleCheckinInputRuntime","v161UnifiedCoachSummaryRuntime","v162CoachPanelDedupGuidanceRuntime",
    "v163SummaryIdentityCleanupRuntime","v164AgendaReliabilityRuntime","v167CheckinCleanupFullCoachRuntime",
    "v123AlertCenterCleanupRuntime"
]:
    if ident in html:
        raise RuntimeError("V17.0 legacy runtime still present: "+ident)

for marker in ["__fjzRuntimeV170","canonicalDashboard:true","canonicalSummary:true","canonicalCheckin:true","alertReinjectCoalesced:true","photoDedup:true"]:
    if marker not in html:
        raise RuntimeError("V17.0 missing marker: "+marker)

after_metrics={
    "bytes":len(html),
    "scripts":len(re.findall(r"<script\b",html)),
    "styles":len(re.findall(r"<style\b",html)),
    "render_assignments":len(re.findall(r"(?:window\.)?render\s*=\s*function",html)),
    "mutation_observers":len(re.findall(r"new\s+MutationObserver",html)),
    "timeouts":len(re.findall(r"setTimeout\s*\(",html)),
}
print("TEAM FJZ V17.0 obsolete blocks removed:",removed)
print("TEAM FJZ V17.0 metrics before:",before_metrics)
print("TEAM FJZ V17.0 metrics after:",after_metrics)
p.write_text(html,encoding="utf-8")
print("TEAM FJZ V17.0 consolidated runtime/dashboard enabled")
