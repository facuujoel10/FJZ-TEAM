import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# Coalesce legacy realtime-triggered renders into the V12.5 frame scheduler.
html=re.sub(r"setTimeout\(\(\)=>render\(\),\s*(?:0|120|180|200|250|300|350|400|500)\)", "fjzScheduleRenderV125()", html)

css=r"""
<style id="v132CoachAssistantStyles">
.v132-assistant{margin-top:14px}
.v132-assistant-top{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;margin-top:12px}
.v132-assistant-kpi{border:1px solid var(--border);border-radius:12px;padding:11px;background:rgba(255,255,255,.025)}
.v132-assistant-kpi span{display:block;color:var(--muted);font-size:9px;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px}
.v132-assistant-kpi strong{display:block;font-size:13px;line-height:1.35}
.v132-plan{display:grid;gap:10px;margin-top:12px}
.v132-step{border:1px solid var(--border);border-radius:13px;padding:12px;background:var(--card)}
.v132-step.review{border-color:rgba(255,106,117,.34)}
.v132-step.good{border-color:rgba(69,179,107,.3)}
.v132-step.info{border-color:rgba(90,167,255,.3)}
.v132-step-head{display:flex;justify-content:space-between;gap:9px;align-items:flex-start}
.v132-step h4{margin:0;font-size:14px}
.v132-step-copy{margin-top:6px;font-size:12px;line-height:1.5}
.v132-step-row{margin-top:8px;padding-top:8px;border-top:1px solid var(--border);font-size:11px;line-height:1.5}
.v132-step-actions{display:flex;gap:7px;flex-wrap:wrap;margin-top:9px}
.v132-data-note{margin-top:11px;padding:10px 11px;border:1px dashed var(--border);border-radius:11px;color:var(--muted);font-size:10px;line-height:1.55}
@media(max-width:720px){.v132-assistant-top{grid-template-columns:1fr}}
</style>
"""

js=r"""
<script id="v132CoachAssistantRealtime">
(function(){
  const RELEASE='13.2';

  function nV132(v){const n=Number(v);return Number.isFinite(n)?n:null}
  function avgV132(rows,key,count=3){
    const vals=(rows||[]).slice(0,count).map(x=>nV132(x?.[key])).filter(v=>v!==null);
    return vals.length?vals.reduce((a,b)=>a+b,0)/vals.length:null
  }
  function deltaV132(a,b){a=nV132(a);b=nV132(b);return a===null||b===null?null:a-b}
  function absFmtV132(v,unit=''){return v===null?'—':(v>0?'+':'')+v.toFixed(1)+unit}
  function daysV132(v){if(!v)return 999;const t=new Date(v).getTime();return Number.isFinite(t)?Math.floor((Date.now()-t)/86400000):999}
  function recentSessionsV132(s,days){
    const cut=Date.now()-days*86400000;
    return (s?.sessions||[]).filter(x=>{const t=new Date(x.date||x.completedAt||0).getTime();return Number.isFinite(t)&&t>=cut})
  }
  function pushV132(list,type,priority,title,copy,reason,action,tab,when='Ahora',watch=''){
    if(list.some(x=>x.title===title))return;
    list.push({type,priority,title,copy,reason,action,tab,when,watch})
  }
  function tabLabelV132(tab){
    return ({tracking:'seguimiento',routine:'rutina',nutrition:'nutrición',history:'historial',progress:'progreso',summary:'resumen'})[tab]||tab
  }
  function confidenceV132(meta){
    let points=0;
    if(meta.checkins>=2)points+=2; else if(meta.checkins===1)points+=1;
    if(meta.sessions14>=2)points+=2; else if(meta.sessions14===1)points+=1;
    if(meta.measurements>=2)points+=1;
    if(meta.feedbackLoaded)points+=1;
    return points>=5?'Alta':points>=3?'Media':'Baja'
  }

  window.buildCoachHelpV71=async function(){
    const s=student(), list=[];
    const row=cloudAthletes?.get?.(s?.id)||null;
    const athleteId=row?.id||null;

    const jobs=[];
    if(typeof loadTracking==='function')jobs.push(loadTracking(true));
    if(typeof loadNutrition==='function')jobs.push(loadNutrition(true));
    await Promise.allSettled(jobs);

    let feedback=[],schedule=null,feedbackLoaded=false;
    if(supabaseClient&&athleteId){
      try{
        const {data,error}=await supabaseClient.from('exercise_feedback')
          .select('id,exercise_name,feedback_type,message,status,created_at')
          .eq('athlete_id',athleteId)
          .order('created_at',{ascending:false})
          .limit(20);
        if(error)throw error;
        feedback=(data||[]).filter(x=>!['reviewed','resolved','closed'].includes(String(x.status||'').toLowerCase()));
        feedbackLoaded=true;
      }catch(e){}
      try{
        const {data}=await supabaseClient.from('checkin_schedules')
          .select('cadence,next_due,active,last_completed_at')
          .eq('athlete_id',athleteId).maybeSingle();
        schedule=data||null;
      }catch(e){}
    }

    const checks=trackingCache?.checkins||[];
    const measurements=trackingCache?.measurements||[];
    const latest=checks[0]||null,prev=checks[1]||null;
    const ss7=recentSessionsV132(s,7),ss14=recentSessionsV132(s,14),ss28=recentSessionsV132(s,28);
    const planned=Math.max(1,Number(s?.plannedPerWeek)||s?.days?.length||1);
    const adherence7=Math.min(100,Math.round(ss7.length/planned*100));
    const adherence14=Math.min(100,Math.round(ss14.length/(planned*2)*100));
    const results14=ss14.flatMap(x=>x.exerciseResults||[]);
    const results28=ss28.flatMap(x=>x.exerciseResults||[]);
    const progress14=results14.filter(x=>['up','rep','load'].includes(x.recommendation?.type));
    const review14=results14.filter(x=>['down','plateau'].includes(x.recommendation?.type));
    const incomplete14=ss14.filter(x=>(Number(x.summary?.skippedExercises)||0)>0||(Number(x.summary?.partial)||0)>0);
    const lastSession=(s?.sessions||[]).slice().sort((a,b)=>new Date(b.date||0)-new Date(a.date||0))[0]||null;

    const meta={
      checkins:checks.length,
      sessions14:ss14.length,
      measurements:measurements.length,
      feedbackLoaded,
      adherence7,
      unresolvedFeedback:feedback.length
    };

    if(!s?.days?.length){
      pushV132(list,'review',100,'Cargar una rutina activa','No hay una estructura de entrenamiento disponible para analizar ni seguir.','Rutina: 0 días programados.','Definir la semana de entrenamiento antes de interpretar progresión o adherencia.','routine','Ahora');
    }

    if(feedback.length){
      const names=[...new Set(feedback.map(x=>x.exercise_name).filter(Boolean))].slice(0,3);
      pushV132(list,'review',98,'Revisar comentarios de ejercicios antes de progresar',
        'Hay comentarios del alumno todavía abiertos. Conviene resolverlos antes de aumentar carga o exigir más en esos movimientos.',
        feedback.length+' comentario(s) pendiente(s)'+(names.length?' · '+names.join(' · '):'')+'.',
        'Abrir la rutina, revisar técnica/contexto y responder. Si el alumno refiere dolor o síntomas, no forzar el movimiento y considerar derivación profesional según corresponda.',
        'routine','Ahora','Confirmar si el problema se repite en la próxima sesión.');
    }

    if(schedule?.active&&schedule.next_due){
      const dueDays=Math.floor((new Date().setHours(0,0,0,0)-new Date(schedule.next_due+'T00:00:00').getTime())/86400000);
      if(dueDays>0){
        pushV132(list,'info',94,'Check-in programado pendiente',
          'La fecha prevista del check-in ya pasó y falta contexto actualizado para decidir con precisión.',
          'Vencimiento: '+String(schedule.next_due)+'.',
          'Pedir el check-in y usarlo como referencia antes de hacer cambios grandes.','tracking','Ahora');
      }
    }

    if(latest){
      const flags=[
        nV132(latest.sleep_quality)!==null&&latest.sleep_quality<=5?'sueño '+latest.sleep_quality+'/10':null,
        nV132(latest.energy_level)!==null&&latest.energy_level<=5?'energía '+latest.energy_level+'/10':null,
        nV132(latest.recovery_level)!==null&&latest.recovery_level<=5?'recuperación '+latest.recovery_level+'/10':null,
        nV132(latest.stress_level)!==null&&latest.stress_level>=7?'estrés '+latest.stress_level+'/10':null
      ].filter(Boolean);
      if(flags.length>=2){
        pushV132(list,'review',92,'Priorizar recuperación antes de sumar exigencia',
          'Varias señales del último check-in están comprometidas. No conviene interpretar una sesión floja como falta de esfuerzo sin mirar el contexto.',
          flags.join(' · ')+'.',
          'Mantener o simplificar temporalmente lo necesario, revisar descanso/estrés y reevaluar con el próximo check-in y 1–2 sesiones.','tracking','Ahora','Energía, sueño, recuperación y rendimiento en las próximas sesiones.');
      }
      if(prev){
        const recNow=avgV132([latest],'recovery_level',1),recPrev=avgV132([prev],'recovery_level',1);
        const enNow=avgV132([latest],'energy_level',1),enPrev=avgV132([prev],'energy_level',1);
        const stNow=avgV132([latest],'stress_level',1),stPrev=avgV132([prev],'stress_level',1);
        if((recNow!==null&&recPrev!==null&&recNow<=recPrev-2)||(enNow!==null&&enPrev!==null&&enNow<=enPrev-2)||(stNow!==null&&stPrev!==null&&stNow>=stPrev+2)){
          pushV132(list,'info',82,'La recuperación cambió respecto al check-in anterior',
            'Hay un cambio claro entre los dos reportes más recientes. Conviene interpretar la tendencia, no solo el último número.',
            'Comparación entre los 2 check-ins más recientes.',
            'Preguntar qué cambió en horarios, estrés, sueño o rutina diaria y observar si el rendimiento acompaña esa tendencia.','tracking','Próximo contacto');
        }
      }
      if(nV132(latest.adherence_level)!==null&&latest.adherence_level<=5){
        pushV132(list,'review',84,'Resolver adherencia antes de complejizar el plan',
          'El alumno reporta dificultad para sostener el plan. Agregar más tareas puede empeorar el problema.',
          'Adherencia del último check-in: '+latest.adherence_level+'/10.',
          'Identificar 1–2 barreras concretas y simplificar lo necesario antes de sumar volumen, ejercicios o nuevas obligaciones.','tracking','Ahora','Ver si la adherencia mejora en el próximo check-in.');
      }
    }else{
      pushV132(list,'info',76,'Falta contexto de check-in',
        'Sin un check-in reciente hay menos información sobre sueño, energía, estrés, recuperación y adherencia.',
        'No hay check-ins disponibles.',
        'Programar/completar el próximo check-in antes de tomar decisiones importantes sobre el plan.','tracking','Próximo paso');
    }

    if(row?.user_id&&daysV132(s?.lastWorkout)>=7){
      pushV132(list,'review',90,'Revisar continuidad de entrenamiento',
        'Hace varios días que no aparece una sesión registrada. Puede ser falta de entrenamiento o simplemente falta de registro.',
        'Última sesión registrada: '+(s?.lastWorkout?fmtDate(s.lastWorkout):'sin registros')+'.',
        'Confirmar primero si entrenó. Si no entrenó, revisar horarios, duración y barreras antes de modificar el programa.','history','Ahora');
    }

    if(incomplete14.length>=2){
      const omitted=incomplete14.reduce((a,x)=>a+(Number(x.summary?.skippedExercises)||0),0);
      pushV132(list,'review',86,'La rutina puede estar costando completarse',
        'Se repiten sesiones con ejercicios omitidos o parciales. Eso puede señalar duración excesiva, orden poco práctico o prioridades poco claras.',
        incomplete14.length+' sesiones incompletas en 14 días · '+omitted+' ejercicios omitidos.',
        'Revisar qué queda afuera con mayor frecuencia y considerar reordenar o acortar antes de agregar trabajo.','history','Próximas 1–2 sesiones','Controlar duración real y qué ejercicios vuelve a omitir.');
    }

    if(ss7.length&&adherence7<60){
      pushV132(list,'review',83,'Frecuencia real por debajo de lo planificado',
        'La semana registrada está bastante por debajo de la frecuencia prevista.',
        ss7.length+' de '+planned+' sesiones en 7 días · '+adherence7+'%.',
        'Ajustar organización y expectativas semanales antes de aumentar complejidad.','routine','Esta semana');
    }

    if(review14.length>=2){
      const names=[...new Set(review14.map(x=>x.name).filter(Boolean))].slice(0,4);
      pushV132(list,'review',80,'Revisar progresiones puntuales',
        'Varios ejercicios recientes marcaron revisión de carga, repeticiones o tolerancia.',
        review14.length+' señales'+(names.length?' · '+names.join(' · '):'')+'.',
        'Revisar esos ejercicios uno por uno; no hace falta cambiar toda la rutina.','progress','Próximas sesiones');
    }

    if(progress14.length>=2&&latest&&latest.energy_level>=6&&latest.recovery_level>=6&&latest.stress_level<=6){
      const names=[...new Set(progress14.map(x=>x.name).filter(Boolean))].slice(0,4);
      pushV132(list,'good',54,'Hay margen para progresión selectiva',
        'Aparecen mejoras recientes y el check-in no muestra una señal fuerte de recuperación baja.',
        progress14.length+' mejoras detectadas'+(names.length?' · '+names.join(' · '):'')+'.',
        'Progresar solo donde cumplió rango de repeticiones/RIR y mantener el resto estable.','progress','Próximas 1–2 sesiones','Que la técnica y el RIR sigan dentro del objetivo.');
    }

    if(ss28.length>=Math.max(4,planned*2)&&results28.length>=6&&progress14.length===0&&review14.length===0){
      pushV132(list,'info',58,'Revisar si el estímulo sigue generando progreso',
        'Hay suficientes sesiones recientes pero pocas señales claras de progresión o revisión.',
        ss28.length+' sesiones en 28 días.',
        'Revisar objetivos de repeticiones/RIR, técnica y selección de ejercicios antes de cambiar muchas variables a la vez.','progress','Próxima revisión');
    }

    if(measurements.length>=2){
      const m0=measurements[0],m1=measurements[1];
      const wd=deltaV132(m0.weight_kg,m1.weight_kg),wa=deltaV132(m0.waist_cm,m1.waist_cm);
      if((wd!==null&&Math.abs(wd)>=0.5)||(wa!==null&&Math.abs(wa)>=1)){
        pushV132(list,'info',50,'Hay una tendencia corporal para contextualizar',
          'Las últimas mediciones cambiaron lo suficiente como para mirarlas junto con rendimiento, adherencia y objetivo del alumno, no de forma aislada.',
          'Peso: '+absFmtV132(wd,' kg')+' · Cintura: '+absFmtV132(wa,' cm')+'.',
          'Comparar con el objetivo actual y confirmar la tendencia con más de un registro antes de hacer cambios importantes.','tracking','Próximo check-in');
      }
    }

    try{
      if(nutritionCache?.plan&&typeof nutritionAdherenceV63==='function'){
        const a=nutritionAdherenceV63();
        if(!a.disabled&&a.expected>=6&&a.pct<50){
          pushV132(list,'info',66,'Distinguir baja adherencia de bajo registro nutricional',
            'Hay pocos registros para saber si el plan realmente se está siguiendo o simplemente no se está cargando.',
            a.completed+' de '+a.expected+' registros esperados · '+a.pct+'%.',
            'Preguntar primero si faltó registrar. No modificar el plan solo por ausencia de datos.','nutrition','Próximo contacto');
        }
      }
    }catch(e){}

    if(!list.length){
      pushV132(list,'good',30,'Mantener la base y seguir observando',
        'Los datos disponibles no muestran una razón clara para hacer cambios ahora.',
        'Sin banderas principales en entrenamiento, seguimiento o adherencia.',
        'Mantener la estructura y reevaluar con el próximo check-in y las próximas sesiones.','progress','Próxima revisión');
    }

    const confidence=confidenceV132(meta);
    const nextReview=!latest?'Después del próximo check-in':(ss14.length<2?'Después de 2–3 sesiones':'Próximo check-in / 7–14 días');
    list.sort((a,b)=>b.priority-a.priority);
    const result=list.slice(0,7);
    result.meta={...meta,confidence,nextReview,goal:row?.goal||s?.goal||'Sin objetivo cargado'};
    return result;
  };

  window.coachHelpHtmlV71=function(items){
    const meta=items?.meta||{};
    const first=items?.[0];
    return '<div class="card v71-coach-help v132-assistant" id="v71CoachHelp">'+
      '<div class="section-title"><div><h3>Asistente Coach 360</h3><div class="muted tiny">Cruza entrenamiento, check-ins, mediciones, comentarios y nutrición para proponerte próximos pasos. No modifica el plan automáticamente.</div></div><div class="pill-row"><span class="badge blue">V13.2</span><button class="btn small" onclick="refreshCoachAssistantV132()">Actualizar análisis</button></div></div>'+
      '<div class="v132-assistant-top">'+
        '<div class="v132-assistant-kpi"><span>Prioridad actual</span><strong>'+esc(first?.title||'Sin urgencias')+'</strong></div>'+
        '<div class="v132-assistant-kpi"><span>Calidad de datos</span><strong>'+esc(meta.confidence||'Baja')+' · '+(meta.sessions14||0)+' sesiones / '+(meta.checkins||0)+' check-ins</strong></div>'+
        '<div class="v132-assistant-kpi"><span>Reevaluar</span><strong>'+esc(meta.nextReview||'Con próximos registros')+'</strong></div>'+
      '</div>'+
      '<div class="v132-plan">'+items.map(x=>
        '<div class="v132-step '+esc(x.type)+'">'+
          '<div class="v132-step-head"><div><div class="muted micro">'+esc(x.when||'Ahora')+'</div><h4>'+esc(x.title)+'</h4></div>'+coachHelpBadgeV71(x.type)+'</div>'+
          '<div class="v132-step-copy">'+esc(x.copy)+'</div>'+
          '<div class="v132-step-row"><strong>Por qué:</strong> '+esc(x.reason)+'</div>'+
          '<div class="v132-step-row"><strong>Qué haría ahora:</strong> '+esc(x.action)+'</div>'+
          (x.watch?'<div class="v132-step-row"><strong>Qué vigilar:</strong> '+esc(x.watch)+'</div>':'')+
          (x.tab?'<div class="v132-step-actions"><button class="btn small" onclick="coachStudentTab=\''+esc(x.tab)+'\';render()">Abrir '+esc(tabLabelV132(x.tab))+'</button></div>':'')+
        '</div>'
      ).join('')+'</div>'+
      '<div class="v132-data-note">Objetivo cargado: '+esc(meta.goal||'Sin cargar')+'. El asistente prioriza tendencias y contexto; un único peso, check-in o sesión no se toma como conclusión por sí solo.</div>'+
    '</div>';
  };

  window.refreshCoachAssistantV132=function(){
    try{trackingLoadedFor=null}catch(e){}
    try{nutritionLoadedAthlete=null}catch(e){}
    try{coachFeedLoadedAt=0}catch(e){}
    fjzScheduleRenderV125();
  };

  // ---------- Realtime safety net ----------
  let rtTimerV132=null,rtTablesV132=new Set();
  window.__fjzRealtimeV132={status:'idle',lastTable:null,lastAt:null,pending:0};

  function invalidateV132(table){
    if(['weekly_checkins','body_measurements','progress_photos'].includes(table)){
      try{trackingLoadedFor=null}catch(e){}
    }
    if(['nutrition_logs','nutrition_plans','nutrition_habit_logs','nutrition_plan_revisions'].includes(table)){
      try{nutritionLoadedAthlete=null}catch(e){}
    }
    if(table==='exercise_feedback'){
      try{exerciseFeedbackCacheV73.clear()}catch(e){}
      try{exerciseFeedbackAllCoachV73=[]}catch(e){}
      try{coachFeedLoadedAt=0}catch(e){}
    }
    if(['checkin_schedules','coach_payments'].includes(table)){
      try{followupLoadedV122=false}catch(e){}
      try{coachFeedLoadedAt=0}catch(e){}
    }
    if(['athlete_schedule','athlete_reminders'].includes(table)){
      try{agendaLoadedV81=false}catch(e){}
    }
    if(table==='coach_media_settings'){
      try{coachMediaV69=null}catch(e){}
    }
    if(table==='exercise_media'){
      try{exerciseMediaCacheV80.clear()}catch(e){}
      try{exerciseMediaCoachV80=null}catch(e){}
      try{exerciseMediaSignedV80.clear()}catch(e){}
    }
  }

  async function flushRealtimeV132(){
    clearTimeout(rtTimerV132);rtTimerV132=null;
    const tables=[...rtTablesV132];rtTablesV132.clear();
    window.__fjzRealtimeV132.pending=0;
    if(!tables.length)return;
    tables.forEach(invalidateV132);

    const core=tables.some(t=>['athlete_snapshots','athletes'].includes(t));
    if(core&&typeof refreshCloudFromRealtime==='function'&&Date.now()-(Number(cloudLastWrite)||0)>700){
      try{await refreshCloudFromRealtime();return}catch(e){console.warn('V13.2 core realtime refresh',e)}
    }
    fjzScheduleRenderV125();
  }

  function queueRealtimeV132(table){
    window.__fjzRealtimeV132.lastTable=table;
    window.__fjzRealtimeV132.lastAt=new Date().toISOString();
    rtTablesV132.add(table);
    window.__fjzRealtimeV132.pending=rtTablesV132.size;
    clearTimeout(rtTimerV132);
    rtTimerV132=setTimeout(flushRealtimeV132,180);
  }

  function setupRealtimeV132(){
    if(!supabaseClient)return;
    try{
      if(window.__fjzUnifiedRealtimeV132)supabaseClient.removeChannel(window.__fjzUnifiedRealtimeV132);
      const tables=[
        'athlete_snapshots','athletes','weekly_checkins','body_measurements','progress_photos',
        'nutrition_logs','nutrition_plans','nutrition_habit_logs','nutrition_plan_revisions','nutrition_templates',
        'exercise_feedback','checkin_schedules','coach_payments','student_notices',
        'athlete_schedule','athlete_reminders','coach_media_settings','exercise_media',
        'workout_sessions','workout_sets','progression_recommendations'
      ];
      let ch=supabaseClient.channel('fjz-v132-unified');
      tables.forEach(table=>{
        ch=ch.on('postgres_changes',{event:'*',schema:'public',table},()=>queueRealtimeV132(table));
      });
      window.__fjzUnifiedRealtimeV132=ch.subscribe(status=>{
        window.__fjzRealtimeV132.status=status;
      });
    }catch(e){
      window.__fjzRealtimeV132.status='error';
      console.error('V13.2 realtime',e);
    }
  }

  const baseSetupRealtimeV132=setupRealtime;
  setupRealtime=function(){
    const out=baseSetupRealtimeV132.apply(this,arguments);
    setupRealtimeV132();
    return out;
  };

  // Diagnostic panel now reports actual sync/realtime state.
  const baseSystemStatusV132=window.showSystemStatusV80;
  window.showSystemStatusV80=async function(){
    showModal('<div class="modal-head"><div><h3>Estado del sistema</h3><div class="muted tiny">Sincronización, Realtime y cachés de TEAM FJZ.</div></div><button class="btn small" onclick="closeModal()">✕</button></div><div id="v80SystemBody"><div class="empty">Comprobando…</div></div>');
    try{
      let feed='—';
      if(currentProfile?.role==='coach'){try{feed=String((await loadCoachFeed(true)).length)}catch(e){feed='Error'}}
      const rt=window.__fjzRealtimeV132||{};
      const pending=localStorage.getItem('fjz_v112_pending_sync')?'Sí':'No';
      const channels=typeof supabaseClient?.getChannels==='function'?supabaseClient.getChannels().length:'—';
      const checks=[
        ['Versión','V'+(window.__FJZ_RELEASE__||RELEASE)],
        ['Sesión',currentUser?'OK':'Revisar'],
        ['Nube',cloudEnabled?'Conectada':'Local'],
        ['Realtime',rt.status||'—'],
        ['Canales activos',String(channels)],
        ['Sync pendiente',pending],
        ['Último evento',rt.lastTable||'—'],
        ['Alertas',feed]
      ];
      el('v80SystemBody').innerHTML='<div class="v80-system-grid">'+checks.map(([a,b])=>'<div class="v80-system-item"><strong>'+esc(b)+'</strong><span>'+esc(a)+'</span></div>').join('')+'</div><div class="v71-help-note">Los cambios Realtime se agrupan durante 180 ms para evitar renders repetidos. Si una escritura queda pendiente por conexión, V11.2 mantiene el sistema de reintento automático.</div>';
    }catch(e){
      el('v80SystemBody').innerHTML='<div class="empty">'+esc(cloudErr(e))+'</div>';
    }
  };

  window.addEventListener('online',()=>{if(window.__fjzRealtimeV132?.status!=='SUBSCRIBED')setupRealtimeV132()});
  document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible'&&window.__fjzRealtimeV132?.status!=='SUBSCRIBED')setupRealtimeV132()});

  window.__fjzV132={
    version:RELEASE,
    coachAssistant360:true,
    realtimeBatchMs:180,
    unifiedSafetyNet:true,
    coalescedLegacyRenders:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

# Build audit markers.
remaining_delayed=len(re.findall(r"setTimeout\(\(\)=>render\(\)",html))
if remaining_delayed>8:
    raise RuntimeError(f"Too many delayed render calls remain: {remaining_delayed}")
for marker in ["Asistente Coach 360","fjz-v132-unified","Perfil actualizado y guardado","Datos actualizados y guardados"]:
    if marker not in html:
        raise RuntimeError("V13.2 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V13.2 assistant + realtime:",len(html),"bytes")
print("TEAM FJZ V13.2 delayed direct renders remaining:",remaining_delayed)
