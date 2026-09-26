import pathlib
import re

p = pathlib.Path("public/index.html")
html = p.read_text(encoding="utf-8")

js = r"""
<script id="v112SyncHardeningRuntime">
(function(){
  const DIRTY_KEY='fjz_v112_pending_sync';
  let syncPromiseV112=null;
  let syncQueuedV112=false;
  let retryTimerV112=null;
  let retryAttemptV112=0;

  function pendingV112(){
    try{return JSON.parse(localStorage.getItem(DIRTY_KEY)||'null')}catch(e){return null}
  }
  function markPendingV112(){
    try{
      if(!currentUser||!currentProfile)return;
      localStorage.setItem(DIRTY_KEY,JSON.stringify({
        userId:currentUser.id,
        role:currentProfile.role,
        at:new Date().toISOString()
      }));
    }catch(e){}
  }
  function clearPendingV112(){
    try{localStorage.removeItem(DIRTY_KEY)}catch(e){}
    retryAttemptV112=0;
    clearTimeout(retryTimerV112);
    retryTimerV112=null;
  }
  function isPendingForCurrentV112(){
    const p=pendingV112();
    return !!(p&&currentUser&&p.userId===currentUser.id);
  }
  function cloneV112(x){return x==null?x:JSON.parse(JSON.stringify(x))}

  function latestIsoV112(a,b){
    const ta=a?new Date(a).getTime():0,tb=b?new Date(b).getTime():0;
    return ta>=tb?(a||b):(b||a);
  }
  function unionByV112(a,b,keyFn){
    const m=new Map();
    [...(a||[]),...(b||[])].forEach(x=>{
      if(!x)return;
      const k=keyFn(x);
      if(!m.has(k))m.set(k,cloneV112(x));
      else m.set(k,Object.assign({},m.get(k),cloneV112(x)));
    });
    return [...m.values()];
  }
  function sessionKeyV112(x){
    return x?.id||[x?.date||'',x?.dayId||'',x?.dayName||''].join('|');
  }
  function historyKeyV112(x){
    return [x?.date||'',x?.target||'',JSON.stringify(x?.sets||[])].join('|');
  }
  function mergeHistoriesV112(primary,secondary){
    return unionByV112(primary,secondary,historyKeyV112)
      .sort((a,b)=>new Date(a?.date||0)-new Date(b?.date||0));
  }
  function mergeCheckinsV112(a,b){
    return unionByV112(a,b,x=>x?.id||x?.week_start||x?.date||JSON.stringify(x||{}));
  }
  function attachProgressV112(configStudent,progressStudent){
    if(!configStudent||!progressStudent)return configStudent;
    const progressExercises=new Map();
    (progressStudent.days||[]).forEach(d=>(d.exercises||[]).forEach(e=>progressExercises.set(e.uid,e)));
    (configStudent.days||[]).forEach(d=>(d.exercises||[]).forEach(e=>{
      const pe=progressExercises.get(e.uid);
      if(pe)e.history=mergeHistoriesV112(e.history,pe.history);
    }));
    configStudent.sessions=unionByV112(configStudent.sessions,progressStudent.sessions,sessionKeyV112)
      .sort((a,b)=>new Date(a?.date||0)-new Date(b?.date||0));
    configStudent.lastWorkout=latestIsoV112(configStudent.lastWorkout,progressStudent.lastWorkout);
    configStudent.checkins=mergeCheckinsV112(configStudent.checkins,progressStudent.checkins);
    if(progressStudent.checkin==='Recibido')configStudent.checkin='Recibido';
    return configStudent;
  }
  function mergeForStudentV112(localStudent,remoteStudent){
    if(!remoteStudent)return cloneV112(localStudent);
    const merged=cloneV112(remoteStudent);
    return attachProgressV112(merged,localStudent);
  }
  function mergeForCoachV112(localStudent,remoteStudent){
    if(!localStudent)return cloneV112(remoteStudent);
    const merged=cloneV112(localStudent);
    return attachProgressV112(merged,remoteStudent);
  }
  function writeStateQuietV112(){
    try{
      window.__fjzCloudApplying=true;
      localStorage.setItem('fjz_v4_state',JSON.stringify(state));
    }finally{
      window.__fjzCloudApplying=false;
    }
  }

  const baseSaveStateV112=window.saveState;
  window.saveState=function(){
    const out=baseSaveStateV112.apply(this,arguments);
    if(window.__fjzCloudReady&&!window.__fjzCloudApplying&&currentUser&&currentProfile){
      markPendingV112();
    }
    return out;
  };

  const baseSyncStudentStateV112=window.syncStudentState;
  window.syncStudentState=async function(){
    const local=cloneV112(student());
    if(local&&linkedAthleteId&&supabaseClient){
      try{
        const {data,error}=await supabaseClient
          .from('athlete_snapshots')
          .select('data,updated_at')
          .eq('athlete_id',linkedAthleteId)
          .maybeSingle();
        if(error)throw error;
        if(data?.data){
          const merged=mergeForStudentV112(local,data.data);
          const idx=state.students.findIndex(x=>x.id===local.id);
          if(idx>=0)state.students[idx]=merged;
          writeStateQuietV112();
        }
      }catch(e){
        console.warn('V11.2 pre-sync alumno',e);
      }
    }
    return baseSyncStudentStateV112.apply(this,arguments);
  };

  const baseSyncCoachStateV112=window.syncCoachState;
  window.syncCoachState=async function(){
    if(supabaseClient&&cloudAthletes?.size){
      try{
        const ids=[...cloudAthletes.values()].map(x=>x.id).filter(Boolean);
        if(ids.length){
          const {data,error}=await supabaseClient
            .from('athlete_snapshots')
            .select('athlete_id,data,updated_at')
            .in('athlete_id',ids);
          if(error)throw error;
          const remoteByAthlete=new Map((data||[]).map(x=>[x.athlete_id,x.data]));
          state.students=state.students.map(local=>{
            const row=cloudAthletes.get(local.id);
            const remote=row?remoteByAthlete.get(row.id):null;
            return remote?mergeForCoachV112(local,remote):local;
          });
          writeStateQuietV112();
        }
      }catch(e){
        console.warn('V11.2 pre-sync coach',e);
      }
    }
    return baseSyncCoachStateV112.apply(this,arguments);
  };

  const baseSyncCloudNowV112=window.syncCloudNow;
  window.syncCloudNow=function(){
    if(syncPromiseV112){
      syncQueuedV112=true;
      return syncPromiseV112;
    }
    syncPromiseV112=(async()=>{
      try{
        const out=await baseSyncCloudNowV112.apply(this,arguments);
        clearPendingV112();
        return out;
      }catch(e){
        markPendingV112();
        retryAttemptV112=Math.min(retryAttemptV112+1,6);
        clearTimeout(retryTimerV112);
        const delay=Math.min(60000,Math.pow(2,retryAttemptV112-1)*4000);
        retryTimerV112=setTimeout(()=>{
          if(navigator.onLine!==false&&isPendingForCurrentV112()){
            window.syncCloudNow().catch(()=>{});
          }
        },delay);
        try{window.setCloudStatus?.('error','Pendiente')}catch(_e){}
        throw e;
      }finally{
        syncPromiseV112=null;
        if(syncQueuedV112){
          syncQueuedV112=false;
          setTimeout(()=>{
            if(isPendingForCurrentV112())window.syncCloudNow().catch(()=>{});
          },120);
        }
      }
    })();
    return syncPromiseV112;
  };

  function recoverPendingV112(reason){
    if(!currentUser||!currentProfile||!cloudEnabled||!supabaseClient)return;
    if(!isPendingForCurrentV112())return;
    if(navigator.onLine===false)return;
    setTimeout(()=>window.syncCloudNow().catch(e=>console.warn('V11.2 retry '+reason,e)),250);
  }

  window.addEventListener('online',()=>recoverPendingV112('online'));
  window.addEventListener('focus',()=>recoverPendingV112('focus'));
  document.addEventListener('visibilitychange',()=>{
    if(document.visibilityState==='visible')recoverPendingV112('visible');
    else if(isPendingForCurrentV112()&&navigator.onLine!==false){
      window.syncCloudNow().catch(()=>{});
    }
  });
  window.addEventListener('pagehide',()=>{
    if(isPendingForCurrentV112()&&navigator.onLine!==false){
      window.syncCloudNow().catch(()=>{});
    }
  });

  const baseHandleSessionV112=window.handleSession;
  window.handleSession=async function(session){
    const out=await baseHandleSessionV112.apply(this,arguments);
    recoverPendingV112('session');
    return out;
  };

  window.__fjzV112Sync={
    version:'11.2',
    serializedWrites:true,
    retry:true,
    reconnectRecovery:true,
    mergeBeforeWrite:true,
    pendingKey:DIRTY_KEY
  };
})();
</script>
"""

html = html.replace("</body>", js + "\n</body>", 1)
p.write_text(html, encoding="utf-8")

swp = pathlib.Path("public/sw.js")
sw = swp.read_text(encoding="utf-8")
sw = re.sub(r"team-fjz-v\d+(?:-\d+)+", "team-fjz-v11-2", sw)
swp.write_text(sw, encoding="utf-8")

print("TEAM FJZ V11.2 sync hardening:", len(html), "bytes")
