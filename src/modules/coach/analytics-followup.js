(function(root,factory){
  const api=factory(root||{});
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.TeamFJZCoachAnalytics=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(root){
  'use strict';
  const VERSION='22.3C';
  const TZ='America/Argentina/Buenos_Aires';
  const text=v=>String(v??'').trim();
  const esc=v=>text(v).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const num=v=>{const n=Number(String(v??'').replace(',','.'));return Number.isFinite(n)?n:null};
  const dateValue=v=>Date.parse(v||0)||Date.parse(String(v||'')+'T12:00:00Z')||0;
  const fmtDate=v=>{if(!v)return'Sin fecha';try{return new Intl.DateTimeFormat('es-AR',{timeZone:TZ,day:'2-digit',month:'short',year:'numeric'}).format(new Date(/^\d{4}-\d{2}-\d{2}$/.test(String(v))?String(v)+'T12:00:00-03:00':v))}catch(_e){return text(v)}};
  function context(){try{return root.__fjzAthlete360ContextV22?.()||{}}catch(_e){return{}}}
  function state(){return root.__fjzAthlete360StateV22||{}}
  function confirmedSessions(student,engine=root.TeamFJZIntelligentTraining){
    return (student?.sessions||[]).filter(s=>engine?.sessionConfirmed?.(s)).slice().sort((a,b)=>dateValue(a?.date||a?.completedAt)-dateValue(b?.date||b?.completedAt));
  }
  function exerciseSeries(student,engine=root.TeamFJZIntelligentTraining){
    const sessions=confirmedSessions(student,engine),map=new Map();
    for(const session of sessions){
      for(const result of session?.exerciseResults||[]){
        const uid=text(result?.exerciseUid||result?.uid||result?.exerciseName||result?.name);if(!uid)continue;
        const current=engine?.bestLoad?.(result)||null;
        if(!current)continue;
        const analysis=engine?.analyzeExercise?.({sessions:student?.sessions||[],currentSession:session,exerciseUid:result.exerciseUid||uid,confirmedSessionId:session.id})||null;
        const prs=engine?.personalRecords?.({sessions:student?.sessions||[],currentSession:session,exerciseUid:result.exerciseUid||uid,confirmedSessionId:session.id})||[];
        if(!map.has(uid))map.set(uid,{uid,name:text(result?.exerciseName||result?.name||uid),points:[]});
        map.get(uid).points.push({sessionId:text(session.id),date:session.date||session.completedAt||null,dayName:text(session.dayName||session.workoutDayName||'Entrenamiento'),load:current.load,reps:current.reps,rir:current.rir,mode:engine?.modeOf?.(result)||'external',analysis,prs});
      }
    }
    return [...map.values()].filter(x=>x.points.length).sort((a,b)=>dateValue(b.points.at(-1)?.date)-dateValue(a.points.at(-1)?.date));
  }
  function measurementTimeline(rows){
    const keys=[['weight_kg','Peso','kg'],['waist_cm','Cintura','cm'],['abdomen_cm','Abdomen','cm'],['hip_cm','Cadera','cm'],['chest_cm','Pecho','cm'],['arm_left_cm','Brazo izq.','cm'],['arm_right_cm','Brazo der.','cm'],['thigh_left_cm','Muslo izq.','cm'],['thigh_right_cm','Muslo der.','cm']];
    const sorted=(rows||[]).slice().sort((a,b)=>dateValue(a?.measured_on||a?.created_at)-dateValue(b?.measured_on||b?.created_at));
    return keys.map(([key,label,unit])=>{
      const points=sorted.map(r=>({id:text(r.id),date:r.measured_on||r.created_at||null,value:num(r[key]),source:r})).filter(p=>p.value!==null);
      const latest=points.at(-1)||null,previous=points.length>1?points.at(-2):null;
      return {key,label,unit,points,latest,previous,delta:latest&&previous?latest.value-previous.value:null};
    }).filter(x=>x.points.length);
  }
  function checkinTimeline(rows){
    const sorted=(rows||[]).slice().sort((a,b)=>dateValue(a?.submitted_at||a?.week_start||a?.created_at)-dateValue(b?.submitted_at||b?.week_start||b?.created_at));
    const fields=[['sleep_quality','Sueño'],['hunger_level','Hambre'],['stress_level','Estrés'],['motivation_level','Motivación'],['recovery_level','Recuperación'],['energy_level','Energía'],['mood_level','Ánimo'],['adherence_level','Adherencia registrada']];
    return fields.map(([key,label])=>{
      const points=sorted.map(r=>({id:text(r.id),date:r.submitted_at||r.week_start||r.created_at||null,value:num(r[key]),source:r})).filter(p=>p.value!==null);
      const latest=points.at(-1)||null,previous=points.length>1?points.at(-2):null;
      return {key,label,points,latest,previous,delta:latest&&previous?latest.value-previous.value:null};
    }).filter(x=>x.points.length);
  }
  function priorityReasons({comments=[],checkins=[],sessions=[],engine=root.TeamFJZIntelligentTraining}={}){
    const out=[];
    for(const c of comments||[]){
      if(text(c?.status||'pending')!=='pending')continue;
      out.push({kind:'comment',severity:text(c.feedback_type)==='discomfort'?0:1,title:text(c.feedback_type)==='discomfort'?'Molestia pendiente':'Comentario pendiente',detail:text(c.exercise_name||'Entrenamiento'),evidenceId:text(c.id),date:c.created_at||null});
    }
    for(const c of checkins||[]){
      const reviewed=c?.reviewed_at?dateValue(c.reviewed_at):0,submitted=dateValue(c?.submitted_at||c?.week_start||c?.created_at);
      if(!c?.reviewed_at||reviewed<submitted)out.push({kind:'checkin',severity:1,title:'Check-in pendiente de revisión',detail:fmtDate(c.submitted_at||c.week_start||c.created_at),evidenceId:text(c.id),date:c.submitted_at||c.week_start||c.created_at||null});
    }
    const confirmed=(sessions||[]).filter(s=>engine?.sessionConfirmed?.(s));
    const latest=confirmed.slice().sort((a,b)=>dateValue(b?.date)-dateValue(a?.date))[0];
    if(latest){
      const summary=engine?.workoutSummary?.({sessions,currentSession:latest,confirmedSessionId:latest.id})||null;
      if(summary?.commentCount)out.push({kind:'training',severity:2,title:'Sesión con contexto registrado',detail:text(latest.dayName||latest.workoutDayName||'Entrenamiento'),evidenceId:text(latest.id),date:latest.date||null});
    }
    return out.sort((a,b)=>a.severity-b.severity||dateValue(b.date)-dateValue(a.date));
  }
  function spark(points,{min=0,max=10}={}){
    if(!points||points.length<2)return'';
    const w=180,h=54,pad=5,vals=points.map(p=>p.value),lo=Math.min(min,...vals),hi=Math.max(max,...vals),span=(hi-lo)||1;
    const d=points.map((p,i)=>{const x=pad+(w-pad*2)*(i/Math.max(1,points.length-1)),y=h-pad-(h-pad*2)*((p.value-lo)/span);return (i?'L':'M')+x.toFixed(1)+' '+y.toFixed(1)}).join(' ');
    return '<svg class="fjz3c-spark" viewBox="0 0 '+w+' '+h+'" role="img" aria-label="Evolución observada"><path d="'+d+'" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  }
  function deltaText(delta,unit=''){
    if(delta===null||!Number.isFinite(delta))return'Falta un registro comparable';
    if(Math.abs(delta)<1e-9)return'Sin cambio vs. registro anterior';
    return (delta>0?'+':'')+Math.round(delta*10)/10+' '+unit+' vs. registro anterior';
  }
  function renderTraining(host,student){
    const series=exerciseSeries(student),recent=series.slice(0,6);
    host.innerHTML='<section class="fjz3c-panel"><div class="fjz3c-head"><div><span>RENDIMIENTO OBSERVADO</span><h3>Evolución por ejercicio</h3><p>Carga, repeticiones, RIR y PR sólo desde sesiones confirmadas. El veredicto de comparación pertenece a TeamFJZIntelligentTraining.</p></div><span class="fjz3c-count">'+recent.length+' ejercicios</span></div>'+
      (recent.length?'<div class="fjz3c-exercises">'+recent.map(x=>{const last=x.points.at(-1),prev=x.points.length>1?x.points.at(-2):null,a=last.analysis||{},trend=a.comparable?(a.trend==='improved'?'Mejora verificada':a.trend==='stable'?'Estable':a.trend==='lower'||a.trend==='higher-effort'?'Revisar cambio':'Cambio mixto'):'Sin referencia comparable';return '<article class="fjz3c-exercise"><div class="fjz3c-row"><div><strong>'+esc(x.name)+'</strong><span>'+esc(fmtDate(last.date))+' · '+x.points.length+' sesión'+(x.points.length===1?'':'es')+'</span></div><span class="fjz3c-trend '+esc(a.trend||'unknown')+'">'+esc(trend)+'</span></div><div class="fjz3c-observed"><b>'+esc(last.mode==='bodyweight'?last.reps+' reps':last.load+' kg × '+last.reps)+'</b><span>'+(last.rir==null?'RIR sin dato':'RIR '+esc(last.rir))+'</span>'+(last.prs?.length?'<em>PR · '+esc(last.prs[0].label)+'</em>':'')+'</div>'+(a.comparison?'<p>'+esc(a.comparison)+'</p>':prev?'<p>Existe registro previo, pero no es comparable según la autoridad de entrenamiento.</p>':'<p>Se necesita otra sesión comparable para evaluar tendencia.</p>')+'<button class="fjz3c-evidence" data-3c-action="session" data-session="'+esc(last.sessionId)+'">Ver sesión fuente →</button></article>'}).join('')+'</div>':'<div class="fjz3c-empty"><strong>Sin historial comparable</strong><span>Los gráficos y tendencias aparecen sólo cuando existen sesiones confirmadas válidas.</span></div>')+
    '</section>';
  }
  function renderMeasurements(host,tracking){
    const metrics=measurementTimeline(tracking?.measurements||[]),key=metrics.find(x=>x.key==='weight_kg')||metrics[0];
    host.innerHTML='<section class="fjz3c-panel"><div class="fjz3c-head"><div><span>SEGUIMIENTO CORPORAL</span><h3>Registros históricos</h3><p>Datos observados. Los cambios no se etiquetan automáticamente como positivos o negativos.</p></div></div>'+
      (key?'<div class="fjz3c-feature"><div><span>'+esc(key.label)+'</span><strong>'+esc(key.latest.value)+' '+key.unit+'</strong><small>'+esc(deltaText(key.delta,key.unit))+'</small></div>'+spark(key.points,{min:Math.min(...key.points.map(p=>p.value)),max:Math.max(...key.points.map(p=>p.value))})+'</div>':'')+
      '<div class="fjz3c-metric-grid">'+metrics.slice(0,8).map(m=>'<button data-3c-action="measurement" data-measurement="'+esc(m.latest.id)+'"><span>'+esc(m.label)+'</span><strong>'+esc(m.latest.value)+' '+m.unit+'</strong><small>'+esc(deltaText(m.delta,m.unit))+'</small></button>').join('')+'</div></section>';
  }
  function renderCheckins(host,tracking){
    const rows=checkinTimeline(tracking?.checkins||[]);
    host.innerHTML='<section class="fjz3c-panel"><div class="fjz3c-head"><div><span>RECUPERACIÓN Y CHECK-INS</span><h3>Comparación cronológica</h3><p>Cada escala mantiene su significado original. No se combinan en un score inventado.</p></div></div>'+
      (rows.length?'<div class="fjz3c-check-grid">'+rows.slice(0,8).map(m=>'<button data-3c-action="checkin" data-checkin="'+esc(m.latest.id)+'"><div><span>'+esc(m.label)+'</span><strong>'+esc(m.latest.value)+'/10</strong><small>'+esc(deltaText(m.delta,''))+'</small></div>'+spark(m.points,{min:1,max:10})+'</button>').join('')+'</div>':'<div class="fjz3c-empty"><strong>Sin check-ins suficientes</strong><span>No se muestra tendencia sin registros observados.</span></div>')+'</section>';
  }
  function renderPriorities(host,student,tracking,comments){
    const rows=priorityReasons({comments,checkins:tracking?.checkins||[],sessions:student?.sessions||[]});
    host.innerHTML='<section class="fjz3c-panel fjz3c-priority"><div class="fjz3c-head"><div><span>SEGUIMIENTO INTELIGENTE</span><h3>Qué revisar primero</h3><p>Prioridad basada únicamente en pendientes verificables y evidencia disponible.</p></div></div>'+(rows.length?'<div class="fjz3c-priority-list">'+rows.slice(0,5).map((x,i)=>'<button data-3c-action="'+esc(x.kind)+'" data-evidence="'+esc(x.evidenceId)+'"><i>'+(i+1)+'</i><div><strong>'+esc(x.title)+'</strong><span>'+esc(x.detail)+'</span></div><b>Ver evidencia</b></button>').join('')+'</div>':'<div class="fjz3c-empty"><strong>Sin revisiones verificables pendientes</strong><span>No se genera urgencia artificial.</span></div>')+'</section>';
  }
  function ensureHost(anchor,id,where='afterend'){
    let host=root.document?.getElementById(id);if(host)return host;
    if(!anchor)return null;host=root.document.createElement('div');host.id=id;host.className='fjz3c-host';anchor.insertAdjacentElement(where,host);return host;
  }
  function renderAthlete(){
    const c=context(),s=state();if(c.profile?.role!=='coach'||c.coachTab!=='student'||!c.student)return false;
    const summary=root.document?.getElementById('fjz3bSummary');
    if(summary){const h=ensureHost(summary.querySelector('.fjz3b-action-card')||summary,'fjz3cPriorityHost');if(h)renderPriorities(h,c.student,s.tracking,s.comments||[])}
    const section=root.document?.querySelector('.fjz3b-section-title h2')?.textContent||'';
    if(/Entrenamiento/i.test(section)){const anchor=root.document?.getElementById('fjz3bSectionContext');const h=ensureHost(anchor,'fjz3cTrainingHost');if(h)renderTraining(h,c.student)}
    if(/Progreso/i.test(section)){const anchor=root.document?.getElementById('fjz3bSectionContext');const h=ensureHost(anchor,'fjz3cMeasurementsHost');if(h)renderMeasurements(h,s.tracking)}
    if(/Check-ins/i.test(section)){const anchor=root.document?.getElementById('fjz3bSectionContext');const h=ensureHost(anchor,'fjz3cCheckinsHost');if(h)renderCheckins(h,s.tracking)}
    bind();return true;
  }
  function renderDashboard(){
    const c=root.__fjzCoachContextV22?.()||{};if(c.profile?.role!=='coach'||c.coachTab!=='dashboard')return false;
    const host=root.document?.querySelector('.fjz3a-command-center');if(!host)return false;
    let badge=host.querySelector('.fjz3c-dashboard-note');if(!badge){badge=root.document.createElement('div');badge.className='fjz3c-dashboard-note';badge.innerHTML='<strong>3C · Evidencia primero</strong><span>Las prioridades abren el registro que las justifica; no se usan scores opacos.</span>';host.querySelector('.fjz3a-main')?.prepend(badge)}return true;
  }
  function openSession(id){
    const c=context(),sid=text(id);if(!sid||!c.student?.id)return false;
    root.__fjzFocusTrainingCommentV328={studentId:c.student.id,sessionId:sid,exerciseUid:'',feedbackId:'',date:null};
    return !!root.__fjzOpenTrainingCommentV325?.(c.student.id,sid);
  }
  function openComment(id){
    const row=(state().comments||[]).find(x=>text(x.id)===text(id));if(!row)return false;
    return root.TeamFJZAthlete360?.openComment?.(row.id)||false;
  }
  function openSection(name,id){
    root.TeamFJZAthlete360?.navigateSection?.(name);
    queueMicrotask(()=>{try{const selector=name==='progress'?'[data-measurement="'+CSS.escape(text(id))+'"]':'[data-checkin="'+CSS.escape(text(id))+'"]';root.document?.querySelector(selector)?.scrollIntoView?.({block:'center'})}catch(_e){}});
    return true;
  }
  function handleAction(e){
    const b=e.target.closest?.('[data-3c-action]');if(!b)return;
    const a=b.dataset['3cAction'];
    if(a==='session'||a==='training'){openSession(b.dataset.session||b.dataset.evidence);return}
    if(a==='comment'){openComment(b.dataset.evidence);return}
    if(a==='checkin'){openSection('checkins',b.dataset.checkin||b.dataset.evidence);return}
    if(a==='measurement'||a==='progress'){openSection('progress',b.dataset.measurement||b.dataset.evidence);return}
  }
  function bind(){
    root.document?.querySelectorAll?.('.fjz3c-host').forEach(host=>{
      if(host.dataset.fjz3cBound==='true')return;
      host.dataset.fjz3cBound='true';host.onclick=handleAction;
    });
  }
  function install(){
    if(root.__fjzCoachAnalyticsInstalledV22)return true;
    root.__fjzCoachAnalyticsInstalledV22=true;
    const previousAfterHydrate=root.__fjzAfterAthlete360HydrateV22;
    root.__fjzAfterAthlete360HydrateV22=function(payload){
      try{previousAfterHydrate?.(payload)}catch(_e){}
      try{renderAthlete()}catch(_e){}
    };
    const previousAfterCommandRender=root.__fjzAfterCoachCommandCenterRenderV22;
    root.__fjzAfterCoachCommandCenterRenderV22=function(){
      try{previousAfterCommandRender?.()}catch(_e){}
      try{renderDashboard()}catch(_e){}
    };
    bind();
    queueMicrotask(()=>{try{renderDashboard()}catch(_e){}try{renderAthlete()}catch(_e){}});
    return true;
  }
  return Object.freeze({VERSION,confirmedSessions,exerciseSeries,measurementTimeline,checkinTimeline,priorityReasons,renderAthlete,renderDashboard,openSession,install});
});