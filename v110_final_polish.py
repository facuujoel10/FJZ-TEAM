import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")
for old in ["TEAM FJZ V10.6","TEAM FJZ V10.5","TEAM FJZ V10.4","TEAM FJZ V10.2","TEAM FJZ V10.0"]:
    html=html.replace(old,"TEAM FJZ V11.0")

css=r"""
<style id="v110FinalStyles">
.v110-method-log{margin:-7px 0 14px;padding:11px 12px;border:1px solid rgba(255,255,255,.10);border-top:0;border-radius:0 0 14px 14px;background:linear-gradient(180deg,rgba(255,255,255,.018),rgba(255,45,58,.035))}
.v110-method-head{display:flex;justify-content:space-between;gap:10px;align-items:flex-start;margin-bottom:9px}
.v110-method-head strong{font-size:11px}
.v110-method-grid{display:grid;gap:7px}
.v110-method-row{display:grid;grid-template-columns:54px repeat(3,minmax(0,1fr));gap:7px;align-items:end}
.v110-method-row.superset{grid-template-columns:54px minmax(0,1fr)}
.v110-method-row.single{grid-template-columns:54px minmax(0,1fr)}
.v110-method-row .input{min-width:0}
.v110-method-note{margin-top:8px}
.v110-method-prev{margin-top:8px;padding-top:8px;border-top:1px dashed var(--border);font-size:9px;color:var(--muted);line-height:1.45}
.v110-method-badge{display:inline-flex;padding:4px 7px;border-radius:999px;border:1px solid rgba(255,45,58,.28);background:rgba(255,45,58,.07);font-size:9px;font-weight:850}
.v110-insight-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
.v110-insight{border:1px solid var(--border);border-radius:13px;padding:12px;background:#0d0d10}
.v110-insight.review{border-left:3px solid #e9a23b}
.v110-insight.good{border-left:3px solid #45b36b}
.v110-insight.info{border-left:3px solid #5b8def}
.v110-insight h4{margin:0;font-size:12px;line-height:1.35}
.v110-insight-copy{margin-top:6px;font-size:10px;line-height:1.48;color:var(--muted)}
.v110-insight-why{margin-top:8px;padding-top:8px;border-top:1px solid var(--border);font-size:9px;line-height:1.45;color:var(--muted)}
.v110-insight-action{margin-top:8px;font-size:10px;line-height:1.45}
.v110-help-head{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
.v110-session-method{margin-top:8px;padding:8px 9px;border:1px solid rgba(90,167,255,.20);border-radius:9px;background:rgba(90,167,255,.04)}
.v110-session-method strong{font-size:10px}
.v110-session-method .muted{margin-top:4px}
.v110-partial-pill{display:inline-flex;margin-left:6px;padding:2px 6px;border-radius:999px;border:1px solid rgba(233,162,59,.28);font-size:8px;color:#f0b45c}
.v110-audit-note{font-size:9px;color:var(--muted)}
@media(max-width:760px){
  .v110-method-row{grid-template-columns:48px repeat(2,minmax(0,1fr))}
  .v110-method-row>label:last-child:nth-child(4){grid-column:2/-1}
  .v110-insight-grid{grid-template-columns:1fr}
}
@media(max-width:520px){
  .v110-method-row,.v110-method-row.superset,.v110-method-row.single{grid-template-columns:1fr 1fr}
  .v110-method-row>.set-n{grid-column:1/-1;text-align:left}
}
</style>
"""

js=r"""
<script id="v110FinalRuntime">
(function(){
  window.__fjzMethodDraftV110=window.__fjzMethodDraftV110||{};

  function methodLabelV110(m){
    return ({dropset:'Dropset',superserie:'Superserie / biserie',rest_pause:'Rest-pause',myo_reps:'Myo-reps',cluster:'Cluster'})[m]||'Método';
  }
  function methodConfigV110(m){
    if(m==='dropset')return {cls:'',slots:[['d1','Descenso 1 kg'],['d2','Descenso 2 kg'],['d3','Descenso 3 kg']]};
    if(m==='superserie')return {cls:'superset',slots:[['b','Peso ejercicio B kg']]};
    if(m==='rest_pause')return {cls:'single',slots:[['rp','Peso rest-pause kg']]};
    if(m==='myo_reps')return {cls:'single',slots:[['myo','Peso minisets kg']]};
    if(m==='cluster')return {cls:'single',slots:[['cl','Peso bloques kg']]};
    return null;
  }
  function methodEntryV110(uidv,si){
    const root=window.__fjzMethodDraftV110;
    root[uidv]=root[uidv]||{sets:{},note:''};
    root[uidv].sets[si]=root[uidv].sets[si]||{};
    return root[uidv].sets[si];
  }
  window.setMethodLoadV110=function(uidv,si,key,val){
    const e=methodEntryV110(uidv,si);
    const raw=String(val??'').trim();
    if(raw==='')delete e[key];
    else{
      const n=Number(raw);
      if(Number.isFinite(n)&&n>=0)e[key]=n;
    }
  };
  window.setMethodNoteV110=function(uidv,val){
    const root=window.__fjzMethodDraftV110;
    root[uidv]=root[uidv]||{sets:{},note:''};
    root[uidv].note=String(val||'').slice(0,180);
  };
  function compactMethodLogV110(uidv,e){
    const x=window.__fjzMethodDraftV110?.[uidv];
    if(!x)return null;
    const sets={};
    Object.entries(x.sets||{}).forEach(([k,v])=>{
      const clean={};
      Object.entries(v||{}).forEach(([a,b])=>{if(Number.isFinite(Number(b)))clean[a]=Number(b)});
      if(Object.keys(clean).length)sets[k]=clean;
    });
    const note=String(x.note||'').trim();
    if(!Object.keys(sets).length&&!note)return null;
    return {type:e.method||'normal',methodNote:e.methodNote||'',sets,note};
  }
  function methodLogTextV110(log){
    if(!log)return '';
    const cfg=methodConfigV110(log.type);
    const labels=Object.fromEntries((cfg?.slots||[]).map(x=>x));
    const rows=Object.entries(log.sets||{}).map(([si,vals])=>{
      const parts=Object.entries(vals||{}).map(([k,v])=>(labels[k]||k)+': '+v+' kg');
      return parts.length?'S'+(Number(si)+1)+' · '+parts.join(' · '):'';
    }).filter(Boolean);
    if(log.note)rows.push('Nota: '+log.note);
    return rows.join(' | ');
  }
  function previousMethodLogV110(e){
    const h=latestHistory(e);
    return h?.methodLog||null;
  }
  function methodBlockV110(e){
    if(!e||!e.method||e.method==='normal')return '';
    const cfg=methodConfigV110(e.method);if(!cfg)return '';
    const current=window.__fjzMethodDraftV110[e.uid]||{sets:{},note:''};
    const prev=previousMethodLogV110(e);
    return '<div class="v110-method-log">'+
      '<div class="v110-method-head"><div><strong>Registrar '+esc(methodLabelV110(e.method))+'</strong><div class="muted micro">La carga principal sigue en cada serie. Acá guardás los pesos extra del método.</div></div><span class="v110-method-badge">'+esc(methodLabelV110(e.method))+'</span></div>'+
      '<div class="v110-method-grid">'+
      Array.from({length:e.sets},(_,si)=>{
        const vals=current.sets?.[si]||{};
        return '<div class="v110-method-row '+cfg.cls+'"><div class="set-n">S'+(si+1)+'</div>'+
          cfg.slots.map(([key,label])=>'<label class="tiny muted">'+esc(label)+'<input class="input" type="number" min="0" step="0.5" value="'+(vals[key]??'')+'" placeholder="Opcional" oninput="setMethodLoadV110(\''+e.uid+'\','+si+',\''+key+'\',this.value)"></label>').join('')+
          '</div>';
      }).join('')+
      '</div>'+
      '<label class="tiny muted v110-method-note">Nota de carga / método<input class="input" maxlength="180" value="'+esc(current.note||'')+'" placeholder="Opcional: Ej. ejercicio B con 12 kg" oninput="setMethodNoteV110(\''+e.uid+'\',this.value)"></label>'+
      (prev?'<div class="v110-method-prev"><strong>Último registro:</strong> '+esc(methodLogTextV110(prev))+'</div>':'')+
      '</div>';
  }

  const baseWorkoutV110=window.workoutExercise;
  window.workoutExercise=function(e,i){
    const out=baseWorkoutV110.apply(this,arguments);
    return out+methodBlockV110(e);
  };

  const baseStartV110=window.startWorkout;
  window.startWorkout=function(i){
    window.__fjzMethodDraftV110={};
    return baseStartV110.apply(this,arguments);
  };

  function attachMethodLogsV110(beforeCount){
    const s=student();
    if(!s?.sessions||s.sessions.length<=beforeCount)return false;
    const ss=s.sessions[s.sessions.length-1];
    if(!ss||ss.dayId!==s.days[currentDay]?.id)return false;
    let touched=false;
    (ss.exerciseResults||[]).forEach(r=>{
      const found=allExercises(s).find(x=>x.e.uid===r.exerciseUid);
      const e=found?.e;if(!e||!e.method||e.method==='normal')return;
      const log=compactMethodLogV110(e.uid,e);
      if(!log)return;
      r.methodLog=clone(log);touched=true;
      if(r.completed&&e.history?.length){
        const h=e.history[e.history.length-1];
        if(h)h.methodLog=clone(log);
      }
    });
    if(touched)saveState();
    return touched;
  }

  const baseFinishV110=window.finishWorkout;
  window.finishWorkout=function(){
    const before=student()?.sessions?.length||0;
    const out=baseFinishV110.apply(this,arguments);
    attachMethodLogsV110(before);
    return out;
  };
  const baseConfirmPartialV110=window.confirmPartialSessionV106;
  if(typeof baseConfirmPartialV110==='function'){
    window.confirmPartialSessionV106=function(){
      const before=student()?.sessions?.length||0;
      const out=baseConfirmPartialV110.apply(this,arguments);
      attachMethodLogsV110(before);
      return out;
    };
  }

  function fmtSetV110(x,i){
    const kg=Number(x?.[0]),reps=Number(x?.[1]),rir=Number(x?.[2]);
    const load=kg===0?'peso corporal':((Number.isFinite(kg)?kg:'—')+' kg');
    return 'S'+(i+1)+': '+load+' × '+(Number.isFinite(reps)?reps:'—')+' · RIR '+(Number.isFinite(rir)?rir:'—');
  }
  window.sessionDetails=function(id){
    const ss=student().sessions.find(x=>x.id===id);if(!ss)return;
    const sum=ss.summary||{};
    const skipped=Number(sum.skippedExercises)||0,partial=Number(sum.partial)||0;
    showModal('<div class="modal-head"><div><h3>'+esc(ss.dayName)+'</h3><div class="muted tiny">'+new Date(ss.date).toLocaleString('es-AR')+'</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="grid summary-grid">'+
        '<div class="card"><strong class="stat-good" style="font-size:26px">'+(sum.up||0)+'</strong><div class="muted tiny">Progresaron</div></div>'+
        '<div class="card"><strong class="stat-warn" style="font-size:26px">'+(sum.hold||0)+'</strong><div class="muted tiny">Estables</div></div>'+
        '<div class="card"><strong class="stat-bad" style="font-size:26px">'+(sum.review||0)+'</strong><div class="muted tiny">Revisar</div></div>'+
      '</div>'+
      ((skipped||partial)?'<div class="v106-partial-list"><strong>Sesión incompleta</strong><div class="muted tiny">'+skipped+' omitidos · '+partial+' parciales</div></div>':'')+
      (ss.exerciseResults?.length?ss.exerciseResults.map(r=>{
        const method=r.methodLog;
        return '<div class="card" style="margin-top:10px"><strong>'+esc(r.name)+(r.completed===false?'<span class="v110-partial-pill">PARCIAL</span>':'')+'</strong>'+
          '<div class="muted tiny" style="margin-top:4px">'+(r.sets||[]).map(fmtSetV110).join(' · ')+'</div>'+
          (method?'<div class="v110-session-method"><strong>'+esc(methodLabelV110(method.type))+'</strong><div class="muted tiny">'+esc(methodLogTextV110(method))+'</div></div>':'')+
          '<div class="recommend"><strong>'+esc(r.recommendation?.title||'Registro guardado')+'</strong><div class="muted tiny">'+esc(r.recommendation?.copy||'')+'</div></div></div>';
      }).join(''):'<p class="muted tiny">Esta sesión no contiene detalle por ejercicio.</p>')+
      (ss.skippedExerciseNames?.length?'<div class="v106-partial-list"><strong>No realizados / no cargados</strong><div class="muted tiny">'+esc(ss.skippedExerciseNames.join(' · '))+'</div></div>':'')
    );
  };

  // ---- Asistente del coach V11 ----
  function pushInsightV110(list,type,priority,title,copy,reason,action,tab){
    if(list.some(x=>x.title===title))return;
    list.push({type,priority,title,copy,reason,action,tab});
  }
  function recentSessionsV110(s,days){
    const cut=Date.now()-days*86400000;
    return (s.sessions||[]).filter(x=>{
      const t=new Date(x.date||0).getTime();
      return Number.isFinite(t)&&t>=cut;
    });
  }
  window.buildCoachHelpV71=async function(){
    const list=[],s=student();
    try{await loadTracking(true)}catch(e){}
    try{await loadNutrition(true)}catch(e){}
    const checks=trackingCache?.checkins||[],latest=checks[0]||null;
    const ss7=recentSessionsV110(s,7),ss14=recentSessionsV110(s,14);
    const planned=Math.max(1,Number(s.plannedPerWeek)||s.days?.length||1);
    const adh=Math.min(100,Math.round(ss7.length/planned*100));
    const last=(s.sessions||[]).slice().sort((a,b)=>new Date(b.date||0)-new Date(a.date||0))[0]||null;
    const incomplete=ss14.filter(x=>(Number(x.summary?.skippedExercises)||0)>0||(Number(x.summary?.partial)||0)>0);
    const results=ss14.flatMap(x=>x.exerciseResults||[]);
    const review=results.filter(x=>['down','plateau'].includes(x.recommendation?.type));
    const progress=results.filter(x=>['up','rep','load'].includes(x.recommendation?.type));
    const row=cloudAthletes?.get?.(s.id);
    const linked=!!row?.user_id;

    if(!s.days?.length){
      pushInsightV110(list,'review',100,'Falta una rutina activa','No hay días de entrenamiento cargados para este alumno.','Rutina: 0 días programados.','Cargar o asignar la rutina antes de empezar el seguimiento.','routine');
    }

    if(linked&&daysSince(s.lastWorkout)>=6){
      pushInsightV110(list,'review',92,'Revisar continuidad','Hace varios días que no aparece una sesión registrada. Antes de cambiar el programa, conviene confirmar si entrenó y no cargó, o si realmente perdió continuidad.','Último entrenamiento registrado: '+fmtDate(s.lastWorkout)+'.','Preguntar qué pasó y ajustar organización o agenda si hace falta.','history');
    }

    if(incomplete.length>=2){
      const omitted=incomplete.reduce((a,x)=>a+(Number(x.summary?.skippedExercises)||0),0);
      const partial=incomplete.reduce((a,x)=>a+(Number(x.summary?.partial)||0),0);
      pushInsightV110(list,'review',88,'Se repiten sesiones incompletas','Hay más de una sesión reciente con ejercicios omitidos o series parciales. Puede indicar falta de tiempo, orden poco práctico o que el final de la rutina cuesta sostener.','Últimos 14 días: '+incomplete.length+' sesiones incompletas · '+omitted+' ejercicios omitidos · '+partial+' parciales.','Revisar duración, orden de ejercicios y qué suele quedar sin hacer antes de sumar volumen.','history');
    }

    if(adh<60&&ss7.length>0){
      pushInsightV110(list,'review',82,'Adherencia de entrenamiento baja','La frecuencia real está bastante por debajo de lo programado. Conviene mejorar primero la ejecución semanal antes de hacer la rutina más compleja.','Últimos 7 días: '+ss7.length+' de '+planned+' sesiones · '+adh+'%.','Confirmar horarios y, si hace falta, simplificar la semana para que sea sostenible.','routine');
    }

    if(review.length>=2){
      const names=[...new Set(review.map(x=>x.name).filter(Boolean))].slice(0,4);
      pushInsightV110(list,'review',80,'Hay progresiones para revisar','Varios registros recientes marcaron que conviene revisar carga, repeticiones o tolerancia antes de seguir subiendo.','Detectados: '+review.length+(names.length?' · '+names.join(' · '):'')+'.','Entrar a Progreso y revisar primero estos ejercicios; no hace falta cambiar toda la rutina.','progress');
    }

    if(latest){
      const flags=[
        latest.sleep_quality<=5?'sueño '+latest.sleep_quality+'/10':null,
        latest.energy_level<=5?'energía '+latest.energy_level+'/10':null,
        latest.recovery_level<=5?'recuperación '+latest.recovery_level+'/10':null,
        latest.stress_level>=7?'estrés '+latest.stress_level+'/10':null
      ].filter(Boolean);
      if(flags.length>=2){
        pushInsightV110(list,'review',86,'Revisar recuperación antes de subir exigencia','Varias respuestas del último check-in sugieren que conviene mirar recuperación y contexto antes de aumentar volumen o intensidad.','Último check-in: '+flags.join(' · ')+'.','Hablar con el alumno sobre descanso, estrés y tolerancia a la semana; mantener o ajustar solo lo necesario.','tracking');
      }
      if(latest.adherence_level<=5){
        pushInsightV110(list,'review',78,'El plan está costando sostenerse','La adherencia reportada es baja. Cambiar muchas variables a la vez suele dificultar saber qué está fallando.','Adherencia del check-in: '+latest.adherence_level+'/10.','Identificar una o dos barreras concretas y resolverlas antes de hacer cambios grandes.','tracking');
      }
    }else{
      pushInsightV110(list,'info',55,'Falta el check-in semanal','Hay menos contexto para interpretar rendimiento, recuperación y adherencia.','No hay un check-in reciente disponible.','Pedir el check-in antes de tomar decisiones importantes sobre el plan.','tracking');
    }

    try{
      if(nutritionCache?.plan&&typeof nutritionAdherenceV63==='function'){
        const a=nutritionAdherenceV63();
        if(!a.disabled&&a.expected>=6&&a.pct<50){
          pushInsightV110(list,'info',62,'Revisar el registro nutricional','El registro del plan está bajo para interpretar con confianza la adherencia alimentaria.','Semana actual: '+a.completed+' de '+a.expected+' registros esperados · '+a.pct+'%.','Antes de modificar el plan, confirmar si faltó registrar o si realmente hubo dificultad para seguirlo.','nutrition');
        }
      }
    }catch(e){}

    if(progress.length>=2&&(!latest||(latest.energy_level>=6&&latest.recovery_level>=6&&latest.stress_level<=6))){
      const names=[...new Set(progress.map(x=>x.name).filter(Boolean))].slice(0,4);
      pushInsightV110(list,'good',45,'Hay progreso utilizable','Aparecen mejoras recientes sin una señal fuerte de recuperación baja. La progresión puede seguir siendo selectiva, ejercicio por ejercicio.','Mejoras detectadas: '+progress.length+(names.length?' · '+names.join(' · '):'')+'.','Mantener la estructura y progresar únicamente donde el objetivo de reps/RIR se cumplió.','progress');
    }

    if(!list.length){
      pushInsightV110(list,'good',30,'Sin cambios urgentes','Los datos disponibles no muestran una razón clara para modificar el plan ahora.','No se detectaron banderas principales en entrenamiento, seguimiento o registro.','Mantener la base y volver a evaluar con el próximo check-in y las próximas sesiones.','progress');
    }
    return list.sort((a,b)=>b.priority-a.priority).slice(0,6);
  };

  window.coachHelpHtmlV71=function(items){
    return '<div class="card v71-coach-help" id="v71CoachHelp">'+
      '<div class="v110-help-head"><div><h3 style="margin:0">Ayuda para el Coach</h3><div class="muted tiny">Prioriza qué mirar, explica por qué y propone una próxima acción. No cambia ningún plan automáticamente.</div></div><span class="badge blue">Asistente V11</span></div>'+
      '<div class="v110-insight-grid" style="margin-top:12px">'+items.map(x=>
        '<div class="v110-insight '+esc(x.type)+'"><div class="v71-help-top"><h4>'+esc(x.title)+'</h4>'+coachHelpBadgeV71(x.type)+'</div>'+
        '<div class="v110-insight-copy">'+esc(x.copy)+'</div>'+
        '<div class="v110-insight-why"><strong>Por qué:</strong> '+esc(x.reason)+'</div>'+
        '<div class="v110-insight-action"><strong>Próxima acción:</strong> '+esc(x.action)+'</div>'+
        (x.tab?'<button class="btn small" style="margin-top:9px" onclick="coachStudentTab=\''+esc(x.tab)+'\';render()">Abrir '+esc(x.tab==='tracking'?'seguimiento':x.tab==='routine'?'rutina':x.tab==='nutrition'?'nutrición':x.tab==='history'?'historial':'progreso')+'</button>':'')+
        '</div>'
      ).join('')+'</div>'+
      '<div class="v71-help-note">La lectura se basa en registros de la app. Si faltan datos o el alumno no registró una sesión, el sistema lo trata como incertidumbre y no como una conclusión.</div></div>';
  };

  // ---- Alertas del coach: limpieza y filtros extra ----
  function polishCoachAlertsV110(){
    if(currentProfile?.role!=='coach'||coachTab!=='dashboard')return;
    document.querySelectorAll('#view .alert-list').forEach(n=>{
      const card=n.closest('.card');
      if(card&&!card.closest('#v96CoachAlerts'))card.remove();
    });
    const tools=el('v96CoachAlertBody')?.querySelector('.v96-alert-tools');
    if(tools&&!el('v110WellnessFilter')){
      const btn=document.createElement('button');
      btn.id='v110WellnessFilter';btn.className='v96-chip';btn.textContent='Bienestar';
      btn.onclick=()=>setCoachAlertFilterV96('wellness');
      tools.insertBefore(btn,tools.lastElementChild||null);
      const pr=document.createElement('button');
      pr.id='v110ProgressFilter';pr.className='v96-chip';pr.textContent='Progresión';
      pr.onclick=()=>setCoachAlertFilterV96('progression');
      tools.insertBefore(pr,tools.lastElementChild||null);
    }
    const sub=el('v96CoachAlerts')?.querySelector('.section-title .muted');
    if(sub)sub.textContent='Prioriza molestias/comentarios, recuperación, check-ins, inactividad, sesiones incompletas, adherencia y progresión.';
  }

  const baseRefreshAlertsV110=window.refreshCoachAlertsV96;
  if(typeof baseRefreshAlertsV110==='function'){
    window.refreshCoachAlertsV96=async function(){
      const out=await baseRefreshAlertsV110.apply(this,arguments);
      polishCoachAlertsV110();
      return out;
    };
  }

  const baseRenderV110=window.render;
  window.render=function(){
    const out=baseRenderV110.apply(this,arguments);
    setTimeout(polishCoachAlertsV110,0);
    setTimeout(polishCoachAlertsV110,500);
    return out;
  };

  window.__fjzV110Audit={
    version:'11.0',
    partialSessions:true,
    exactReps:true,
    methodLoads:true,
    coachInsights:true,
    coachAlertsV2:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)
p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8")
import re
sw=re.sub(r"team-fjz-v\d+(?:-\d+)+","team-fjz-v11-0",sw)
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V11.0 final polish:",len(html),"bytes")
