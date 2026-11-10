(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.TeamFJZSessionHistory=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const VERSION='22.2B';
  let active=null;

  function text(v){return String(v??'').trim()}
  function clone(x){try{return JSON.parse(JSON.stringify(x))}catch(_e){return x}}
  function randomId(){
    let token='';
    try{token=globalThis.crypto?.randomUUID?.()||''}catch(_e){}
    if(!token)token=Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,14);
    return 'ss_'+token;
  }
  function validSessionId(v){
    const s=text(v);
    return s.length>=3&&s.length<=160&&!/\s/.test(s);
  }
  function ensureSessionId({studentId,dayId,priorSessionId,startedAt}={}){
    const sid=text(studentId),did=text(dayId),prior=text(priorSessionId);
    if(prior&&validSessionId(prior)){
      active={studentId:sid,dayId:did,sessionId:prior,startedAt:startedAt||active?.startedAt||null,confirmed:false};
      return prior;
    }
    if(active&&active.studentId===sid&&active.dayId===did&&validSessionId(active.sessionId))return active.sessionId;
    const id=randomId();
    active={studentId:sid,dayId:did,sessionId:id,startedAt:startedAt||new Date().toISOString(),confirmed:false};
    return id;
  }
  function activate({studentId,dayId,sessionId,startedAt,confirmed=false}={}){
    const id=validSessionId(sessionId)?text(sessionId):ensureSessionId({studentId,dayId,startedAt});
    active={studentId:text(studentId),dayId:text(dayId),sessionId:id,startedAt:startedAt||null,confirmed:!!confirmed};
    return clone(active);
  }
  function activeSessionId(){return active?.sessionId||null}
  function current(){return active?Object.freeze(clone(active)):null}
  function markConfirmed(sessionId){
    const id=text(sessionId);
    if(active&&id&&active.sessionId===id){active={...active,confirmed:true};return true}
    return false;
  }
  function clear(sessionId=null){
    if(sessionId&&active&&text(sessionId)!==active.sessionId)return false;
    active=null;return true;
  }
  function feedbackForSession(rows,session,exerciseUid){
    const sid=text(session?.id),uid=text(exerciseUid),all=Array.isArray(rows)?rows:[];
    const exact=all.filter(x=>text(x?.session_id)===sid&&text(x?.exercise_uid)===uid);
    if(exact.length)return exact.map(x=>({...x,linkMode:'exact'}));
    const sessionTime=Date.parse(session?.date||0)||0,maxDelta=18*60*60*1000;
    return all.filter(x=>{
      if(text(x?.session_id))return false;
      if(text(x?.exercise_uid)!==uid)return false;
      if(session?.dayId&&x?.workout_day_id&&text(x.workout_day_id)!==text(session.dayId))return false;
      const t=Date.parse(x?.created_at||0)||0;
      return !!sessionTime&&!!t&&Math.abs(sessionTime-t)<=maxDelta;
    }).map(x=>({...x,linkMode:'historical-compatible'}));
  }
  function bestSet(result){
    const sets=Array.isArray(result?.sets)?result.sets:[];
    let best=null;
    sets.forEach((set,i)=>{
      const load=Number(set?.[0]),reps=Number(set?.[1]),rir=Number(set?.[2]);
      if(!Number.isFinite(load)||!Number.isFinite(reps))return;
      const row={load,reps,rir:Number.isFinite(rir)?rir:null,setIndex:Number(result?.setIndexes?.[i]??i)};
      if(!best||row.load>best.load||(row.load===best.load&&row.reps>best.reps))best=row;
    });
    return best;
  }
  function compareExercise(sessions,currentSessionId,exerciseUid){
    const rows=(Array.isArray(sessions)?sessions:[]).slice().sort((a,b)=>(Date.parse(a?.date||0)||0)-(Date.parse(b?.date||0)||0));
    const idx=rows.findIndex(x=>text(x?.id)===text(currentSessionId));
    if(idx<0)return null;
    const currentResult=(rows[idx]?.exerciseResults||[]).find(x=>text(x?.exerciseUid)===text(exerciseUid));
    const currentBest=bestSet(currentResult);if(!currentBest)return null;
    let previousSession=null,previousResult=null;
    for(let i=idx-1;i>=0;i--){
      const hit=(rows[i]?.exerciseResults||[]).find(x=>text(x?.exerciseUid)===text(exerciseUid));
      if(hit){previousSession=rows[i];previousResult=hit;break}
    }
    const previousBest=bestSet(previousResult);
    if(!previousBest)return {current:currentBest,previous:null,previousSessionId:null};
    return {
      current:currentBest,previous:previousBest,previousSessionId:previousSession?.id||null,
      loadDelta:currentBest.load-previousBest.load,repsDelta:currentBest.reps-previousBest.reps
    };
  }
  function linkLabel(mode){
    if(mode==='exact')return 'Vinculado a esta sesión';
    if(mode==='snapshot')return 'Guardado con la sesión';
    return 'Histórico compatible';
  }
  return Object.freeze({VERSION,validSessionId,ensureSessionId,activate,activeSessionId,current,markConfirmed,clear,feedbackForSession,compareExercise,linkLabel});
});
