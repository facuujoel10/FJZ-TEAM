(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.TeamFJZIntelligentTraining=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const VERSION='22.2C';
  const REST_KEY='team_fjz_v22_rest_timer:';
  const confirmedIds=new Set();
  let timer=null;
  let tickHandle=null;

  function text(v){return String(v??'').trim()}
  function num(v){const n=Number(String(v??'').replace(',','.'));return Number.isFinite(n)?n:null}
  function clone(v){try{return JSON.parse(JSON.stringify(v))}catch(_e){return v}}
  function hasDOM(){return typeof document!=='undefined'&&!!document.querySelector}
  function now(){return Date.now()}
  function sessionKey(sessionId){return REST_KEY+text(sessionId)}
  function storage(){
    try{return typeof localStorage!=='undefined'?localStorage:null}catch(_e){return null}
  }
  function saveTimer(){
    const s=storage(); if(!s||!timer?.sessionId)return;
    try{s.setItem(sessionKey(timer.sessionId),JSON.stringify(timer))}catch(_e){}
  }
  function clearStored(sessionId){
    const s=storage(); if(!s)return;
    try{s.removeItem(sessionKey(sessionId))}catch(_e){}
  }
  function normalizeTimer(raw){
    if(!raw||!text(raw.sessionId)||!Number.isFinite(Number(raw.durationMs)))return null;
    const out={
      sessionId:text(raw.sessionId),exerciseUid:text(raw.exerciseUid),
      durationMs:Math.max(1000,Number(raw.durationMs)),
      state:['running','paused','finished'].includes(raw.state)?raw.state:'paused',
      targetAt:Number(raw.targetAt)||null,
      remainingMs:Math.max(0,Number(raw.remainingMs)||0),
      source:raw.source==='coach'?'coach':'personal',
      startedAt:Number(raw.startedAt)||null
    };
    if(out.state==='running'&&out.targetAt){
      out.remainingMs=Math.max(0,out.targetAt-now());
      if(out.remainingMs===0)out.state='finished';
    }
    return out;
  }
  function timerSnapshot(at=now()){
    if(!timer)return null;
    const out={...timer};
    if(out.state==='running'&&out.targetAt){
      out.remainingMs=Math.max(0,out.targetAt-at);
      if(out.remainingMs===0)out.state='finished';
    }
    return Object.freeze(out);
  }
  function restoreTimer(sessionId){
    if(timer?.sessionId===text(sessionId))return timerSnapshot();
    const s=storage(); if(!s)return null;
    try{
      const raw=JSON.parse(s.getItem(sessionKey(sessionId))||'null');
      timer=normalizeTimer(raw);
      if(timer?.state==='finished')saveTimer();
      syncTicker();
      return timerSnapshot();
    }catch(_e){return null}
  }
  function startRest({sessionId,exerciseUid,durationSeconds,source='personal'}={}){
    const sid=text(sessionId),uid=text(exerciseUid),seconds=Math.round(Number(durationSeconds));
    if(!sid||!uid||!Number.isFinite(seconds)||seconds<1)return null;
    timer={sessionId:sid,exerciseUid:uid,durationMs:seconds*1000,state:'running',targetAt:now()+seconds*1000,remainingMs:seconds*1000,source:source==='coach'?'coach':'personal',startedAt:now()};
    saveTimer();syncTicker();renderTimer();
    return timerSnapshot();
  }
  function pauseRest(){
    if(!timer||timer.state!=='running')return timerSnapshot();
    timer.remainingMs=Math.max(0,(timer.targetAt||now())-now());
    timer.targetAt=null;timer.state=timer.remainingMs?'paused':'finished';
    saveTimer();syncTicker();renderTimer();return timerSnapshot();
  }
  function resumeRest(){
    if(!timer||timer.state!=='paused'||timer.remainingMs<=0)return timerSnapshot();
    timer.state='running';timer.targetAt=now()+timer.remainingMs;
    saveTimer();syncTicker();renderTimer();return timerSnapshot();
  }
  function resetRest(){
    if(!timer)return null;
    timer.state='paused';timer.targetAt=null;timer.remainingMs=timer.durationMs;
    saveTimer();syncTicker();renderTimer();return timerSnapshot();
  }
  function skipRest(){
    if(!timer)return null;
    const sid=timer.sessionId;timer=null;clearStored(sid);syncTicker();renderTimer();return null;
  }
  function advance(at=now()){
    if(!timer||timer.state!=='running')return timerSnapshot(at);
    timer.remainingMs=Math.max(0,(timer.targetAt||at)-at);
    if(timer.remainingMs<=0){timer.remainingMs=0;timer.state='finished';timer.targetAt=null;saveTimer();syncTicker()}
    return timerSnapshot(at);
  }
  function syncTicker(){
    if(tickHandle){clearInterval(tickHandle);tickHandle=null}
    if(timer?.state==='running'&&typeof setInterval==='function'){
      tickHandle=setInterval(()=>{advance();renderTimer()},1000);
    }
  }
  function timerCount(){return tickHandle?1:0}

  function modeOf(result){
    const raw=text(result?.loadMode||result?.weightMode||result?.mode||result?.resistanceMode||result?.exerciseMode).toLowerCase();
    if(/assist/.test(raw)||result?.assisted===true||result?.isAssisted===true)return 'assisted';
    if(/body|corporal/.test(raw)||result?.bodyweight===true||result?.isBodyweight===true){
      if(/lastre|weighted|external/.test(raw)||result?.weightedBodyweight===true)return 'bodyweight-added';
      return 'bodyweight';
    }
    if(/lastre|weighted-body/.test(raw))return 'bodyweight-added';
    return 'external';
  }
  function comparableMode(a,b){return modeOf(a)===modeOf(b)}
  function validSet(set,index,result){
    if(!Array.isArray(set))return null;
    const load=num(set[0]),reps=num(set[1]),rir=num(set[2]);
    if(load===null||reps===null||reps<=0||load<0)return null;
    const kinds=result?.setKinds||result?.setTypes||[];
    const kind=text(kinds[index]||'work').toLowerCase();
    if(/warm|calent/.test(kind))return null;
    if(/drop|rest.?pause|intens/.test(kind))return null;
    return {load,reps,rir:rir===null?null:rir,index,kind};
  }
  function workSets(result){
    return (Array.isArray(result?.sets)?result.sets:[]).map((s,i)=>validSet(s,i,result)).filter(Boolean);
  }
  function bestLoad(result){
    return workSets(result).sort((a,b)=>b.load-a.load||b.reps-a.reps)[0]||null;
  }
  function bestRepsAtLoad(result,load){
    return workSets(result).filter(x=>x.load===load).sort((a,b)=>b.reps-a.reps)[0]||null;
  }
  function sessionConfirmed(session,confirmedSessionId=null){
    const id=text(session?.id);
    if(!id)return false;
    if(id===text(confirmedSessionId)||confirmedIds.has(id))return true;
    if(session?.cloudConfirmed===true||session?.confirmed===true)return true;
    if(text(session?.status).toLowerCase()==='completed')return true;
    return false;
  }
  function markSessionConfirmed(sessionId){if(text(sessionId))confirmedIds.add(text(sessionId));return text(sessionId)||null}
  function sessionResult(session,exerciseUid){
    return (Array.isArray(session?.exerciseResults)?session.exerciseResults:[]).find(r=>text(r?.exerciseUid)===text(exerciseUid))||null;
  }
  function previousComparable(sessions,currentSession,exerciseUid){
    const rows=(Array.isArray(sessions)?sessions:[]).filter(Boolean).slice().sort((a,b)=>(Date.parse(a?.date||0)||0)-(Date.parse(b?.date||0)||0));
    const currentTime=Date.parse(currentSession?.date||0)||Infinity;
    const current=sessionResult(currentSession,exerciseUid);
    if(!current)return null;
    for(let i=rows.length-1;i>=0;i--){
      const s=rows[i];if(text(s?.id)===text(currentSession?.id))continue;
      if((Date.parse(s?.date||0)||0)>currentTime)continue;
      const r=sessionResult(s,exerciseUid);if(!r||!comparableMode(current,r))continue;
      if(workSets(r).length)return {session:s,result:r};
    }
    return null;
  }
  function analyzeExercise({sessions,currentSession,exerciseUid,confirmedSessionId}={}){
    if(!currentSession||!sessionConfirmed(currentSession,confirmedSessionId))return {comparable:false,reason:'La sesión actual todavía no está confirmada.',records:[],improvements:[]};
    const current=sessionResult(currentSession,exerciseUid);
    if(!current||!workSets(current).length)return {comparable:false,reason:'No hay series de trabajo válidas para comparar.',records:[],improvements:[]};
    const previous=previousComparable(sessions,currentSession,exerciseUid);
    if(!previous)return {comparable:false,reason:'No existe una referencia comparable confirmada.',records:[],improvements:[]};
    const cb=bestLoad(current),pb=bestLoad(previous.result),records=[],improvements=[];
    if(cb&&pb&&cb.load>pb.load){
      records.push({type:'load',label:'Mayor carga',from:pb,to:cb,message:`${pb.load} kg × ${pb.reps} → ${cb.load} kg × ${cb.reps}`});
    }else if(cb&&pb&&cb.load===pb.load&&cb.reps>pb.reps){
      records.push({type:'reps_same_load',label:'Más repeticiones con la misma carga',from:pb,to:cb,message:`${pb.load} kg × ${pb.reps} → ${cb.load} kg × ${cb.reps}`});
    }
    if(cb&&pb){
      if(cb.load!==pb.load||cb.reps!==pb.reps||cb.rir!==pb.rir){
        improvements.push({type:'previous_comparison',from:pb,to:cb,message:`${pb.load} kg × ${pb.reps}${pb.rir===null?'':' · RIR '+pb.rir} → ${cb.load} kg × ${cb.reps}${cb.rir===null?'':' · RIR '+cb.rir}`});
      }
    }
    return {comparable:true,mode:modeOf(current),previousSessionId:previous.session.id,current:cb,previous:pb,records,improvements};
  }
  function allPriorResults(sessions,currentSession,exerciseUid,currentResult){
    const t=Date.parse(currentSession?.date||0)||Infinity;
    return (Array.isArray(sessions)?sessions:[]).filter(s=>text(s?.id)!==text(currentSession?.id)&&(Date.parse(s?.date||0)||0)<=t)
      .map(s=>({session:s,result:sessionResult(s,exerciseUid)})).filter(x=>x.result&&comparableMode(currentResult,x.result)&&workSets(x.result).length);
  }
  function personalRecords({sessions,currentSession,exerciseUid,confirmedSessionId}={}){
    if(!sessionConfirmed(currentSession,confirmedSessionId))return [];
    const current=sessionResult(currentSession,exerciseUid);if(!current)return[];
    const prior=allPriorResults(sessions,currentSession,exerciseUid,current);
    const sets=workSets(current),out=[];
    if(!sets.length||!prior.length)return out;
    const priorSets=prior.flatMap(x=>workSets(x.result));
    const priorMaxLoad=Math.max(...priorSets.map(x=>x.load));
    const cMax=bestLoad(current);
    if(cMax&&cMax.load>priorMaxLoad)out.push({type:'all_time_load',label:'Récord de carga',set:cMax});
    for(const set of sets){
      const previousAtLoad=priorSets.filter(x=>x.load===set.load).sort((a,b)=>b.reps-a.reps)[0];
      if(previousAtLoad&&set.reps>previousAtLoad.reps){
        out.push({type:'all_time_reps_same_load',label:'Récord de repeticiones',set,previous:previousAtLoad});break;
      }
    }
    return out;
  }
  function progressionSuggestion(analysis){
    if(!analysis?.comparable||!analysis.current||!analysis.previous)return null;
    const c=analysis.current,p=analysis.previous;
    if(c.rir===null)return {kind:'hold',label:'Sugerencia calculada',message:'Hay mejora verificable, pero falta RIR para justificar una subida de carga.'};
    if(c.load>p.load&&c.reps>=p.reps&&c.rir>=1)return {kind:'maintain',label:'Sugerencia calculada',message:'La carga ya progresó con margen registrado. Conviene confirmar esta tendencia antes de otra subida.'};
    if(c.load===p.load&&c.reps>p.reps&&c.rir>=2)return {kind:'consider',label:'Sugerencia calculada',message:'Más repeticiones con la misma carga y RIR ≥ 2. El Coach puede considerar progresar la carga.'};
    if(c.rir<1)return {kind:'hold',label:'Sugerencia calculada',message:'El esfuerzo fue muy alto. No se sugiere aumentar carga automáticamente.'};
    return {kind:'maintain',label:'Sugerencia calculada',message:'Mantener la prescripción y observar otra sesión comparable.'};
  }
  function workoutSummary({sessions,currentSession,confirmedSessionId,feedbackRows}={}){
    if(!currentSession||!sessionConfirmed(currentSession,confirmedSessionId))return null;
    const results=(currentSession.exerciseResults||[]).filter(r=>workSets(r).length);
    const exercises=results.map(r=>{
      const analysis=analyzeExercise({sessions,currentSession,exerciseUid:r.exerciseUid,confirmedSessionId});
      const prs=personalRecords({sessions,currentSession,exerciseUid:r.exerciseUid,confirmedSessionId});
      const comments=(feedbackRows||[]).filter(x=>text(x?.session_id)===text(currentSession.id)&&text(x?.exercise_uid)===text(r.exerciseUid));
      return {exerciseUid:r.exerciseUid,name:r.exerciseName||r.name||r.exerciseUid,sets:workSets(r).length,analysis,prs,comments};
    });
    return {
      sessionId:currentSession.id,date:currentSession.date||null,dayName:currentSession.dayName||currentSession.workoutDayName||'Entrenamiento',
      exercises,totalSets:exercises.reduce((a,x)=>a+x.sets,0),
      recordCount:exercises.reduce((a,x)=>a+x.prs.length,0),
      improvementCount:exercises.reduce((a,x)=>a+(x.analysis?.improvements?.length||0),0),
      commentCount:exercises.reduce((a,x)=>a+x.comments.length,0)
    };
  }
  function prescribedRestSeconds(card){
    const raw=text(card?.textContent);
    let m=raw.match(/descanso\s*[:·-]?\s*(\d{1,3})\s*(?:s|seg|segundos?)\b/i);
    if(m)return {seconds:Number(m[1]),source:'coach'};
    m=raw.match(/descanso\s*[:·-]?\s*(\d+(?:[.,]\d+)?)\s*(?:min|minutos?)\b/i);
    if(m)return {seconds:Math.round(Number(m[1].replace(',','.'))*60),source:'coach'};
    return null;
  }
  function fmt(ms){const sec=Math.ceil(Math.max(0,ms)/1000),m=Math.floor(sec/60),s=sec%60;return m+':'+String(s).padStart(2,'0')}
  function sessionId(){try{return globalThis.TeamFJZSessionHistory?.activeSessionId?.()||globalThis.__fjzWorkoutSessionIdV2B?.()||''}catch(_e){return''}}
  function exerciseUid(card){return text(card?.querySelector('[data-exercise-uid]')?.dataset.exerciseUid||card?.dataset.exerciseUid||card?.querySelector('.v22-comment-action')?.getAttribute('onclick')?.match(/['"]([^'"]+)['"]/)?.[1]||card?.querySelector('.v22v2-exercise-name')?.textContent)}
  function renderTimer(){
    if(!hasDOM())return;
    const snap=advance();
    document.querySelectorAll('.v22c-rest-control').forEach(node=>{
      const uid=node.dataset.exerciseUid;
      const active=snap&&uid===snap.exerciseUid;
      node.dataset.active=active?'true':'false';
      const time=node.querySelector('.v22c-rest-time');
      const state=node.querySelector('.v22c-rest-state');
      if(time)time.textContent=active?fmt(snap.remainingMs):node.dataset.defaultLabel||'Descanso';
      if(state)state.textContent=active?(snap.state==='running'?'En curso':snap.state==='paused'?'Pausado':'Finalizado'):(node.dataset.source==='coach'?'Indicado por el Coach':'Temporizador personal');
      node.querySelectorAll('[data-rest-action]').forEach(b=>{
        const a=b.dataset.restAction;
        b.hidden=active?false:(a!=='start');
        if(active&&a==='start')b.hidden=true;
      });
    });
  }
  function enhanceWorkout(view){
    if(!hasDOM())return false;view=view||document.getElementById('view');
    if(!view?.classList.contains('v22v2-workout-active'))return false;
    const sid=sessionId();if(sid)restoreTimer(sid);
    [...view.querySelectorAll('.v22v2-exercise')].forEach(card=>{
      if(card.querySelector('.v22c-rest-control'))return;
      const prescribed=prescribedRestSeconds(card);
      const uid=exerciseUid(card)||('exercise-'+(card.dataset.exerciseIndex||'0'));
      const seconds=prescribed?.seconds||90;
      const wrap=document.createElement('div');wrap.className='v22c-rest-control';wrap.dataset.exerciseUid=uid;wrap.dataset.source=prescribed?'coach':'personal';wrap.dataset.seconds=String(seconds);wrap.dataset.defaultLabel=prescribed?fmt(seconds*1000):'Descanso';
      wrap.innerHTML='<div class="v22c-rest-copy"><strong class="v22c-rest-time">'+(prescribed?fmt(seconds*1000):'Descanso')+'</strong><small class="v22c-rest-state">'+(prescribed?'Indicado por el Coach':'Temporizador personal')+'</small></div>'+
        (!prescribed?'<label class="v22c-rest-custom"><span>seg</span><input inputmode="numeric" min="15" max="600" step="15" value="90" aria-label="Duración personal del descanso en segundos"></label>':'')+
        '<div class="v22c-rest-actions"><button class="btn small" data-rest-action="start">Iniciar</button><button class="btn small" data-rest-action="pause" hidden>Pausar</button><button class="btn small" data-rest-action="resume" hidden>Reanudar</button><button class="btn small" data-rest-action="reset" hidden>Reiniciar</button><button class="btn small" data-rest-action="skip" hidden>Omitir</button></div>';
      const target=card.querySelector('.v22v2-series-block')||card.firstElementChild; target?.before(wrap);
      wrap.onclick=function(e){
        const b=e.target.closest('[data-rest-action]');if(!b)return;
        const action=b.dataset.restAction;
        const personal=num(wrap.querySelector('input')?.value);
        if(action==='start')startRest({sessionId:sid||sessionId(),exerciseUid:uid,durationSeconds:prescribed?.seconds||personal||90,source:prescribed?'coach':'personal'});
        if(action==='pause')pauseRest();if(action==='resume')resumeRest();if(action==='reset')resetRest();if(action==='skip')skipRest();
        renderTimer();
      };
    });
    renderTimer();return true;
  }
  function escapeHtml(v){return text(v).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))}
  function renderSummaryModal(summary){
    if(!hasDOM()||!summary)return false;
    const modal=document.getElementById('modal');if(!modal)return false;
    const content=modal.querySelector('.modal-content')||modal;
    const rows=summary.exercises.map(x=>{
      const pr=x.prs[0],imp=x.analysis?.improvements?.[0];
      return '<div class="v22c-summary-exercise"><div><strong>'+escapeHtml(x.name)+'</strong><small>'+x.sets+' series registradas</small></div>'+
        (pr?'<span class="v22c-pr">PR · '+escapeHtml(pr.label)+'</span>':imp?'<span class="v22c-improvement">'+escapeHtml(imp.message)+'</span>':'')+'</div>';
    }).join('');
    content.innerHTML='<div class="v22c-summary"><div class="modal-head"><div><span class="v22c-kicker">SESIÓN CONFIRMADA</span><h3>'+escapeHtml(summary.dayName)+'</h3><div class="muted tiny">'+escapeHtml(summary.date?new Date(summary.date).toLocaleString('es-AR'):'')+'</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="v22c-summary-stats"><div><strong>'+summary.totalSets+'</strong><span>series</span></div><div><strong>'+summary.exercises.length+'</strong><span>ejercicios</span></div><div><strong>'+summary.recordCount+'</strong><span>récords</span></div></div>'+
      '<div class="v22c-summary-list">'+rows+'</div>'+
      '<div class="v22c-summary-actions"><button class="btn" onclick="closeModal();studentTab=\'home\';currentDay=-1;render()">Volver al inicio</button><button class="btn primary" onclick="closeModal();studentTab=\'history\';currentDay=-1;render()">Ver historial</button></div></div>';
    return true;
  }
  function buildConfirmedSummary(session,feedbackRows){
    const sessions=globalThis.student?.()?.sessions||[];
    if(!session)return null;markSessionConfirmed(session.id);
    return workoutSummary({sessions,currentSession:session,confirmedSessionId:session.id,feedbackRows:feedbackRows||[]});
  }

  return Object.freeze({
    VERSION,startRest,pauseRest,resumeRest,resetRest,skipRest,advance,restoreTimer,timerSnapshot,timerCount,
    modeOf,comparableMode,workSets,bestLoad,bestRepsAtLoad,sessionConfirmed,markSessionConfirmed,
    analyzeExercise,personalRecords,progressionSuggestion,workoutSummary,prescribedRestSeconds,
    enhanceWorkout,renderTimer,renderSummaryModal,buildConfirmedSummary
  });
});
