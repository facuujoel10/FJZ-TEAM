import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v174Single360AssistantStyles">
/* Absolute safety net: legacy standalone 360/help cards never render visibly. */
#v80Student360,#v80Student360Loading,
#v71CoachHelp,#v71CoachHelpLoading,
#v71CoachHelpTracking,#v71CoachHelpTrackingCard,
#v63UnifiedSummary{
  display:none!important
}
#v174Coach360{
  display:grid;
  gap:12px;
  contain:layout style
}
.v174-360-head{
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  gap:12px
}
.v174-360-head h3{margin:0;font-size:17px}
.v174-360-head p{margin:4px 0 0;font-size:10px;line-height:1.4;color:var(--muted)}
.v174-360-grid{
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:8px
}
.v174-metric{
  min-width:0;
  padding:11px;
  border:1px solid var(--border);
  border-radius:12px;
  background:rgba(255,255,255,.02)
}
.v174-metric strong{
  display:block;
  font-size:18px;
  line-height:1.1;
  overflow-wrap:anywhere
}
.v174-metric span{
  display:block;
  margin-top:5px;
  color:var(--muted);
  font-size:9px;
  line-height:1.3
}
.v174-status{
  display:flex;
  gap:6px;
  flex-wrap:wrap
}
.v174-chip{
  display:inline-flex;
  align-items:center;
  min-height:27px;
  padding:5px 8px;
  border:1px solid var(--border);
  border-radius:999px;
  background:rgba(255,255,255,.02);
  color:var(--muted);
  font-size:9px
}
.v174-chip.warn{
  border-color:rgba(255,82,97,.3);
  background:rgba(255,82,97,.055);
  color:#ffc4c9
}
.v174-section{
  padding-top:12px;
  border-top:1px solid var(--border)
}
.v174-section-head{
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  gap:10px;
  margin-bottom:9px
}
.v174-section-head h4{margin:0;font-size:12px}
.v174-section-head p{margin:3px 0 0;font-size:9px;color:var(--muted);line-height:1.35}
.v174-confidence{
  white-space:nowrap;
  font-size:9px;
  color:var(--muted)
}
.v174-assistant-list{display:grid;gap:8px}
.v174-advice{
  padding:10px 11px;
  border:1px solid var(--border);
  border-radius:12px;
  background:rgba(255,255,255,.02)
}
.v174-advice.review{
  border-color:rgba(255,82,97,.25);
  background:rgba(255,82,97,.045)
}
.v174-advice.good{
  border-color:rgba(62,202,126,.20);
  background:rgba(62,202,126,.035)
}
.v174-advice-top{
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  gap:8px
}
.v174-advice h5{
  margin:0;
  font-size:11px;
  line-height:1.3
}
.v174-advice-copy{
  margin-top:5px;
  color:var(--muted);
  font-size:10px;
  line-height:1.4
}
.v174-evidence{
  margin-top:7px;
  padding-top:7px;
  border-top:1px dashed rgba(255,255,255,.08);
  color:var(--muted);
  font-size:9px;
  line-height:1.35
}
.v174-advice-actions{
  display:flex;
  gap:6px;
  flex-wrap:wrap;
  margin-top:8px
}
.v174-message{
  padding:10px 11px;
  border:1px solid var(--border);
  border-radius:11px;
  background:rgba(255,255,255,.02);
  font-size:10px;
  line-height:1.4
}
@media(max-width:760px){
  .v174-360-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .v174-360-head,.v174-section-head{display:block}
  .v174-confidence{display:block;margin-top:5px}
}
</style>
"""

js=r"""
<script id="v174Single360AssistantRuntime">
(function(){
  const VERSION='17.4';
  let seqV174=0;

  function cleanupLegacyV174(){
    [
      'v80Student360','v80Student360Loading',
      'v71CoachHelp','v71CoachHelpLoading',
      'v71CoachHelpTracking','v71CoachHelpTrackingCard',
      'v63UnifiedSummary'
    ].forEach(id=>document.getElementById(id)?.remove());
  }

  // Preserve old names because historical render wrappers call them.
  // They now do nothing: no DOM insertion and, critically, no forced data loads.
  const noopAsyncV174=async function(){cleanupLegacyV174();return null};
  try{injectStudent360V80=noopAsyncV174}catch(e){}
  try{window.injectStudent360V80=noopAsyncV174}catch(e){}
  try{injectCoachHelpV71=noopAsyncV174}catch(e){}
  try{window.injectCoachHelpV71=noopAsyncV174}catch(e){}
  try{injectUnifiedStudentSummaryV63=noopAsyncV174}catch(e){}
  try{window.injectUnifiedStudentSummaryV63=noopAsyncV174}catch(e){}

  function metricV174(value,label){
    return '<div class="v174-metric"><strong>'+esc(String(value??'—'))+'</strong><span>'+esc(label)+'</span></div>';
  }
  function chipV174(text,warn=false){
    return '<span class="v174-chip '+(warn?'warn':'')+'">'+esc(text)+'</span>';
  }
  function recentSessionsV174(s,days){
    const cut=Date.now()-days*86400000;
    return (s?.sessions||[]).filter(x=>{
      const t=new Date(x.date||x.completedAt||0).getTime();
      return Number.isFinite(t)&&t>=cut
    });
  }
  function latestWeightV174(latest,measurement){
    const x=measurement?.weight_kg??latest?.weight_kg;
    return x!=null&&x!==''?Number(x):null;
  }
  function pendingV174(){
    try{return typeof pendingFeedbackV73==='function'?(pendingFeedbackV73()||[]):[]}catch(e){return []}
  }

  function nutritionInfoV174(){
    try{
      if(!nutritionCache?.plan)return {active:false,logging:false,expected:0,completed:0,pct:null};
      const logging=typeof nutritionLoggingEnabledV64==='function'?nutritionLoggingEnabledV64():true;
      if(!logging)return {active:true,logging:false,expected:0,completed:0,pct:null};
      if(typeof nutritionAdherenceV63==='function'){
        const a=nutritionAdherenceV63();
        return {active:true,logging:true,expected:Number(a.expected)||0,completed:Number(a.completed)||0,pct:Number.isFinite(Number(a.pct))?Number(a.pct):null}
      }
      return {active:true,logging:true,expected:0,completed:0,pct:null}
    }catch(e){
      return {active:!!nutritionCache?.plan,logging:false,expected:0,completed:0,pct:null}
    }
  }

  function dataConfidenceV174(s,latest,prev,nutrition,pending){
    let score=0,parts=[];
    if(latest){score+=2;parts.push('check-in')}
    if(prev){score+=1;parts.push('tendencia')}
    const sessions14=recentSessionsV174(s,14).length;
    if(sessions14>=2){score+=2;parts.push('entrenamiento')}
    else if(sessions14===1){score+=1;parts.push('1 sesión')}
    if(nutrition.active){score+=1;parts.push('nutrición')}
    if(Array.isArray(pending)){score+=1;parts.push('feedback')}
    return {
      label:score>=6?'Alta':score>=3?'Media':'Baja',
      detail:parts.length?parts.join(' · '):'pocos datos recientes'
    };
  }

  function buildAdviceV174(){
    const s=student();
    const checks=trackingCache?.checkins||[];
    const latest=checks[0]||null,prev=checks[1]||null;
    const pending=pendingV174();
    const nutrition=nutritionInfoV174();
    const s7=recentSessionsV174(s,7),s14=recentSessionsV174(s,14);
    const planned=Math.max(1,Number(s?.plannedPerWeek)||s?.days?.length||1);
    const list=[];
    const add=(type,priority,title,copy,evidence,tab)=>list.push({type,priority,title,copy,evidence,tab});

    if(pending.length){
      const names=[...new Set(pending.map(x=>x.exercise_name).filter(Boolean))].slice(0,3);
      add('review',100,'Resolver feedback de ejercicios primero',
        'Antes de progresar cargas o volumen, revisaría los comentarios técnicos o molestias pendientes.',
        pending.length+' pendiente'+(pending.length===1?'':'s')+(names.length?' · '+names.join(' · '):''),
        'routine');
    }

    if(!latest){
      add('info',96,'Falta contexto de recuperación',
        'No haría un ajuste importante solo con el entrenamiento. Pediría un check-in para sumar sueño, energía, estrés, recuperación y adherencia.',
        'No hay un check-in reciente disponible.',
        'tracking');
    }else{
      const flags=[];
      if(Number(latest.sleep_quality)<=4)flags.push('sueño '+latest.sleep_quality+'/10');
      if(Number(latest.energy_level)<=4)flags.push('energía '+latest.energy_level+'/10');
      if(Number(latest.recovery_level)<=4)flags.push('recuperación '+latest.recovery_level+'/10');
      if(Number(latest.stress_level)>=8)flags.push('estrés '+latest.stress_level+'/10');
      if(flags.length>=2){
        add('review',94,'Priorizar recuperación antes de exigir más',
          'Hay varias señales coincidentes. Revisaría descanso, estrés, adherencia y tolerancia de la rutina antes de sumar trabajo.',
          flags.join(' · '),
          'tracking');
      }

      if(Number(latest.adherence_level)<=5){
        add('review',88,'Buscar la barrera de adherencia',
          'Antes de agregar ejercicios o restricciones, identificaría qué parte del plan está costando sostener.',
          'Adherencia reportada '+latest.adherence_level+'/10.',
          'tracking');
      }

      if(prev){
        const changes=[];
        if(Number(latest.energy_level)-Number(prev.energy_level)<=-2)changes.push('energía bajó '+prev.energy_level+'→'+latest.energy_level);
        if(Number(latest.recovery_level)-Number(prev.recovery_level)<=-2)changes.push('recuperación bajó '+prev.recovery_level+'→'+latest.recovery_level);
        if(Number(latest.stress_level)-Number(prev.stress_level)>=2)changes.push('estrés subió '+prev.stress_level+'→'+latest.stress_level);
        if(changes.length>=2){
          add('review',86,'La tendencia semanal empeoró',
            'Más que mirar un valor aislado, acá hay un cambio simultáneo en varias señales. Revisaría qué cambió esta semana.',
            changes.join(' · '),
            'tracking');
        }
      }
    }

    const days=typeof daysSince==='function'?daysSince(s?.lastWorkout):null;
    if(Number.isFinite(days)&&days>=7){
      add('review',91,'Revisar continuidad de entrenamiento',
        'Hay una pausa suficientemente larga como para confirmar si entrenó, si faltó registrar sesiones o si hubo una dificultad real.',
        'Último entrenamiento registrado hace '+days+' días.',
        'history');
    }else if(s7.length<Math.ceil(planned*.6)){
      add('info',74,'Frecuencia por debajo de la planificación',
        'La semana tiene menos sesiones registradas que la estructura prevista. Confirmaría adherencia antes de modificar la rutina.',
        s7.length+' de '+planned+' sesiones previstas esta semana.',
        'routine');
    }

    const incomplete=s14.filter(x=>(Number(x.summary?.skippedExercises)||0)>0||(Number(x.summary?.partial)||0)>0);
    if(incomplete.length>=2){
      add('review',84,'La rutina puede estar costando completarse',
        'Se repiten sesiones parciales. Revisaría duración, orden de ejercicios y qué partes suelen quedar afuera.',
        incomplete.length+' sesiones incompletas en los últimos 14 días.',
        'history');
    }

    const results=s14.flatMap(x=>x.exerciseResults||[]);
    const review=results.filter(x=>['down','plateau','review'].includes(x.recommendation?.type));
    const progress=results.filter(x=>['up','rep','load'].includes(x.recommendation?.type));
    if(review.length>=2){
      const names=[...new Set(review.map(x=>x.name).filter(Boolean))].slice(0,3);
      add('info',80,'Revisar progresiones puntuales',
        'No cambiaría toda la rutina: hay ejercicios concretos que merecen revisión individual.',
        review.length+' señales'+(names.length?' · '+names.join(' · '):''),
        'progress');
    }

    if(nutrition.active&&nutrition.logging&&nutrition.expected>=4&&nutrition.pct!=null&&nutrition.pct<50){
      add('info',70,'Confirmar adherencia nutricional antes de ajustar',
        'El registro está bajo. Primero distinguiría si faltó cumplir el plan o solamente faltó registrarlo.',
        nutrition.completed+' de '+nutrition.expected+' registros · '+nutrition.pct+'%.',
        'nutrition');
    }

    if(latest&&progress.length>=2&&Number(latest.energy_level)>=6&&Number(latest.recovery_level)>=6&&Number(latest.stress_level)<=6){
      add('good',45,'Hay margen para progresión selectiva',
        'Rendimiento y recuperación acompañan. Progresaría solo en los ejercicios donde realmente se cumplió el objetivo.',
        progress.length+' señales de progresión reciente con recuperación favorable.',
        'progress');
    }

    if(!list.length){
      add('good',20,'Mantener la base y observar tendencia',
        'No aparece una bandera fuerte que justifique cambiar el plan ahora. Mantendría la estructura y seguiría evaluando ejecución y tendencia.',
        'Sin señales principales de atención con los datos actuales.',
        'progress');
    }

    return {
      items:list.sort((a,b)=>b.priority-a.priority).slice(0,3),
      confidence:dataConfidenceV174(s,latest,prev,nutrition,pending)
    };
  }

  function adviceHtmlV174(x,index){
    const badge=x.type==='review'
      ?'<span class="badge red">Prioridad '+(index+1)+'</span>'
      :x.type==='good'
        ?'<span class="badge green">Oportunidad</span>'
        :'<span class="badge blue">Revisar</span>';
    const tabLabel={routine:'Rutina',tracking:'Seguimiento',history:'Historial',progress:'Progreso',nutrition:'Nutrición'}[x.tab]||'Abrir';
    return '<div class="v174-advice '+esc(x.type)+'">'+
      '<div class="v174-advice-top"><h5>'+esc(x.title)+'</h5>'+badge+'</div>'+
      '<div class="v174-advice-copy">'+esc(x.copy)+'</div>'+
      '<div class="v174-evidence"><strong>Evidencia:</strong> '+esc(x.evidence)+'</div>'+
      '<div class="v174-advice-actions"><button class="btn small" onclick="coachStudentTab=\''+esc(x.tab)+'\';render()">Abrir '+esc(tabLabel)+'</button></div>'+
    '</div>';
  }

  function updatePanelV174(){
    const panel=el('v174Coach360');
    if(!panel)return;
    const s=student(),latest=trackingCache?.checkins?.[0]||null,measurement=trackingCache?.measurements?.[0]||null;
    const sessions30=recentSessionsV174(s,30).length;
    const weight=latestWeightV174(latest,measurement);
    const pending=pendingV174();
    const nutrition=nutritionInfoV174();

    const grid=el('v174Metrics');
    if(grid)grid.innerHTML=
      metricV174(sessions30,'Entrenos 30 días')+
      metricV174(weight!=null?round1(weight)+' kg':'—','Peso reciente')+
      metricV174(latest?.energy_level!=null?latest.energy_level+'/10':'—','Energía')+
      metricV174(latest?.recovery_level!=null?latest.recovery_level+'/10':'—','Recuperación');

    const status=[];
    status.push(latest?chipV174('Check-in '+fmtDate(latest.week_start)):chipV174('Sin check-in reciente',true));
    status.push(nutrition.active?chipV174('Plan nutricional activo'):chipV174('Sin plan nutricional',true));
    if(pending.length)status.push(chipV174(pending.length+' comentario'+(pending.length===1?'':'s')+' pendiente'+(pending.length===1?'':'s'),true));
    const days=typeof daysSince==='function'?daysSince(s?.lastWorkout):null;
    if(Number.isFinite(days)&&days>=7)status.push(chipV174(days+' días sin entrenar',true));
    if(el('v174Status'))el('v174Status').innerHTML=status.join('');

    const advice=buildAdviceV174();
    if(el('v174Confidence'))el('v174Confidence').textContent='Confianza '+advice.confidence.label+' · '+advice.confidence.detail;
    if(el('v174Assistant'))el('v174Assistant').innerHTML=advice.items.map(adviceHtmlV174).join('');
    if(el('v174LoadState'))el('v174LoadState').textContent='Actualizado';
  }

  async function hydrateV174(){
    const run=++seqV174;
    const jobs=[];
    const athleteId=typeof trackingAthleteId==='function'?trackingAthleteId():null;
    if(athleteId&&trackingLoadedFor!==athleteId&&typeof loadTracking==='function')jobs.push(loadTracking(false));

    const nAth=typeof nutritionAthleteId==='function'?nutritionAthleteId():null;
    const nutritionReady=nAth&&nutritionLoadedAthlete===nAth&&nutritionFoodsLoaded===true;
    if(nAth&&!nutritionReady&&typeof loadNutrition==='function'){
      jobs.push(loadNutrition(false,nutritionCache?.date||dateInputToday()));
    }

    try{
      if(typeof loadExerciseFeedbackV73==='function')jobs.push(loadExerciseFeedbackV73(false));
    }catch(e){}

    await Promise.allSettled(jobs);
    if(run!==seqV174)return;
    if(!(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'))return;
    cleanupLegacyV174();
    updatePanelV174();
  }

  window.renderCoachSummary=function(){
    cleanupLegacyV174();
    const b=el('coachStudentBody');
    if(!b)return;
    const s=student();

    b.innerHTML=
      '<div class="card" id="v174Coach360">'+
        '<div class="v174-360-head"><div><h3>Resumen 360</h3>'+
          '<p>Una sola lectura del alumno: rendimiento, seguimiento y prioridades para decidir qué revisar.</p></div>'+
          '<span id="v174LoadState" class="muted micro">Actualizando…</span></div>'+
        '<div id="v174Metrics" class="v174-360-grid">'+
          metricV174('—','Entrenos 30 días')+metricV174('—','Peso reciente')+metricV174('—','Energía')+metricV174('—','Recuperación')+
        '</div>'+
        '<div class="v174-section"><div class="v174-section-head"><div><h4>Estado del alumno</h4>'+
          '<p>Señales rápidas sin repetir toda la información de Seguimiento.</p></div></div>'+
          '<div id="v174Status" class="v174-status">'+chipV174('Cargando datos…')+'</div></div>'+
        '<div class="v174-section"><div class="v174-section-head"><div><h4>Asistente Coach</h4>'+
          '<p>Prioriza hasta 3 decisiones concretas cruzando entrenamiento, check-in, nutrición y feedback. No cambia el plan automáticamente.</p></div>'+
          '<span id="v174Confidence" class="v174-confidence">Evaluando datos…</span></div>'+
          '<div id="v174Assistant" class="v174-assistant-list"><div class="empty">Analizando información disponible…</div></div></div>'+
        '<div class="v174-section"><div class="v174-section-head"><div><h4>Mensaje para el alumno</h4>'+
          '<p>Tu mensaje general visible para este alumno.</p></div>'+
          '<button class="btn small" onclick="editCoachMessage()">Editar</button></div>'+
          '<div class="v174-message">'+esc(s?.coachMessage||'Sin mensaje cargado.')+'</div></div>'+
      '</div>';

    hydrateV174();
  };

  cleanupLegacyV174();

  window.__fjzSingle360V174={
    version:VERSION,
    oldPerfil360Disabled:true,
    oldCoachHelpDisabled:true,
    oldIntegralDisabled:true,
    forcedDuplicateLoadsRemoved:true,
    oneCanonical360:true,
    assistantIntegrated:true,
    assistantMaxPriorities:3,
    cacheFirst:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzSingle360V174",
  "oldPerfil360Disabled:true",
  "oldCoachHelpDisabled:true",
  "forcedDuplicateLoadsRemoved:true",
  "oneCanonical360:true",
  "assistantIntegrated:true",
  "assistantMaxPriorities:3",
  "cacheFirst:true"
]:
    if marker not in html:
        raise RuntimeError("V17.4 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V17.4 single canonical 360 + integrated coach assistant enabled")
