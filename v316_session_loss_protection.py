import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "intervals":len(re.findall(r"setInterval\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

before=metrics(html)

for marker in [
    'id="v207ConfirmedSessionCommitRuntime"',
    'id="v304GlobalSaveIntegrityRuntime"',
    'id="v148SessionDeleteRuntime"',
    "__fjzQueueSessionSyncV201",
    "deleteSessionV148",
    'meta name="fjz-decimal-workout-weights" content="21.15"',
]:
    if marker not in html:
        raise RuntimeError("V21.16 prerequisite missing "+marker)

# --------------------------------------------------------------------
# 1) Explicit session deletion uses the dedicated DB authority.
#    Generic snapshot writes can no longer be used to mean "delete".
# --------------------------------------------------------------------
old_delete=r"""      if(supabaseClient&&currentUser&&athleteId){
        const payload=cloneV148(updated);
        const {data,error}=await supabaseClient
          .from('athlete_snapshots')
          .update({data:payload,updated_at:new Date().toISOString()})
          .eq('athlete_id',athleteId)
          .select('athlete_id')
          .maybeSingle();
        if(error)throw error;
        if(!data)throw new Error('No se pudo confirmar el borrado en la nube.');
      }"""
new_delete=r"""      if(supabaseClient&&currentUser&&athleteId){
        const payload=cloneV148(updated);
        const {data,error}=await supabaseClient.rpc('delete_workout_session_v214',{
          p_athlete_id:athleteId,
          p_session_id:String(session.id),
          p_data:payload
        });
        if(error)throw error;
        if(!data)throw new Error('No se pudo confirmar el borrado en la nube.');

        const {data:verify,error:verifyErr}=await supabaseClient
          .from('athlete_snapshots')
          .select('data,updated_at')
          .eq('athlete_id',athleteId)
          .single();
        if(verifyErr)throw verifyErr;
        const stillThere=(verify?.data?.sessions||[]).some(x=>String(x?.id)===String(session.id));
        if(stillThere)throw new Error('La sesión sigue presente en la nube.');
      }"""
if html.count(old_delete)!=1:
    raise RuntimeError("V21.16 session delete authority mismatch: "+str(html.count(old_delete)))
html=html.replace(old_delete,new_delete,1)

runtime=r"""
<script id="v316SessionLossProtectionRuntime">
(function(){
  const VERSION='21.16';
  const BACKUP_PREFIX='fjz_session_backup_v316:';
  const DONE_PREFIX='fjz_session_recovered_v316:';
  const MAX_RECOVERY_AGE=72*60*60*1000;
  let recoveryRunning=false;

  function cloneV316(x){
    try{return JSON.parse(JSON.stringify(x))}catch(_e){return x}
  }
  function athleteForStudentV316(s){
    try{
      const vals=[...((cloudAthletes&&cloudAthletes.values)?cloudAthletes.values():[])];
      return cloudAthletes?.get?.(s?.id)
        || vals.find(a=>String(a?.client_id||'')===String(s?.id||''))
        || vals.find(a=>currentProfile?.role==='student'&&String(a?.user_id||'')===String(currentUser?.id||''))
        || vals.find(a=>linkedAthleteId&&String(a?.id||'')===String(linkedAthleteId))
        || null;
    }catch(_e){return null}
  }
  function currentCtxV316(dayId){
    const s=student?.(),a=athleteForStudentV316(s);
    const d=(s?.days||[]).find(x=>String(x?.id)===String(dayId))||null;
    return {s,a,d};
  }
  function backupKeyV316(sessionId){return BACKUP_PREFIX+String(sessionId||'')}
  function saveBackupV316(session,dayId){
    try{
      const {s,a,d}=currentCtxV316(dayId);
      if(!session?.id||!s||!d)return null;
      const pack={
        version:VERSION,
        at:new Date().toISOString(),
        userId:currentUser?.id||null,
        studentId:s.id,
        athleteId:a?.id||null,
        athleteUserId:a?.user_id||null,
        dayId:d.id,
        day:cloneV316(d),
        session:cloneV316(session),
        confirmed:false
      };
      localStorage.setItem(backupKeyV316(session.id),JSON.stringify(pack));
      return pack;
    }catch(_e){return null}
  }
  function markBackupConfirmedV316(sessionId){
    try{
      const key=backupKeyV316(sessionId),raw=localStorage.getItem(key);
      if(!raw)return;
      const x=JSON.parse(raw);x.confirmed=true;x.confirmedAt=new Date().toISOString();
      localStorage.setItem(key,JSON.stringify(x));
    }catch(_e){}
  }
  function pruneBackupsV316(){
    try{
      const now=Date.now();
      Object.keys(localStorage).filter(k=>k.startsWith(BACKUP_PREFIX)).forEach(k=>{
        try{
          const x=JSON.parse(localStorage.getItem(k)||'null');
          const t=Date.parse(x?.at||0)||0;
          if(!t||now-t>7*24*60*60*1000)localStorage.removeItem(k);
        }catch(_e){localStorage.removeItem(k)}
      });
    }catch(_e){}
  }

  async function resolveAthleteV316(pack){
    if(pack?.athleteId){
      const {data,error}=await supabaseClient.from('athletes')
        .select('id,user_id,client_id,name').eq('id',pack.athleteId).maybeSingle();
      if(error)throw error;
      if(data?.id)return data;
    }
    const sid=String(pack?.studentId||'');
    if(sid){
      const {data,error}=await supabaseClient.from('athletes')
        .select('id,user_id,client_id,name').eq('client_id',sid).maybeSingle();
      if(error)throw error;
      if(data?.id)return data;
    }
    return null;
  }

  async function verifyCloudSessionV316(session,athlete){
    if(!session?.id||!athlete?.id||!athlete?.user_id)return false;
    const {data:snap,error:snapErr}=await supabaseClient.from('athlete_snapshots')
      .select('data,updated_at').eq('athlete_id',athlete.id).single();
    if(snapErr)throw snapErr;
    const inSnapshot=(snap?.data?.sessions||[]).some(x=>String(x?.id)===String(session.id));
    if(!inSnapshot)return false;

    const {data:row,error:rowErr}=await supabaseClient.from('workout_sessions')
      .select('id,student_id,source_session_id,status,completed_at')
      .eq('student_id',athlete.user_id)
      .eq('source_session_id',String(session.id))
      .maybeSingle();
    if(rowErr)throw rowErr;
    return !!row?.id;
  }

  const baseQueueV316=window.__fjzQueueSessionSyncV201;
  if(typeof baseQueueV316==='function'){
    window.__fjzQueueSessionSyncV201=async function(session,dayId){
      const backup=saveBackupV316(session,dayId);
      const ok=await baseQueueV316.apply(this,arguments);
      if(!ok)return false;

      const athlete=await resolveAthleteV316(backup||{
        athleteId:athleteForStudentV316(student?.())?.id,
        studentId:student?.()?.id
      });
      if(!athlete?.id||!athlete?.user_id){
        throw new Error('No pudimos resolver la ficha del alumno para confirmar la sesión.');
      }

      const verified=await verifyCloudSessionV316(session,athlete);
      if(!verified){
        throw new Error('La sesión todavía no existe completa en la nube. El borrador de recuperación se conserva.');
      }

      markBackupConfirmedV316(session.id);
      try{
        window.__fjzRecordConfirmedSaveV303?.('workout','Sesión guardada',{
          sessionId:session.id,athleteId:athlete.id,doubleVerified:true,version:VERSION
        });
      }catch(_e){}
      return true;
    };
  }

  function rawLocalStateV316(){
    try{
      const x=JSON.parse(localStorage.getItem('fjz_v4_state')||'null');
      return x?.students?x:(x?.state?.students?x.state:null);
    }catch(_e){return null}
  }
  function legacySessionPackV316(marker){
    const st=rawLocalStateV316();
    const students=st?.students||[];
    const s=students.find(x=>String(x?.id)===String(marker?.studentId||''));
    if(!s)return null;
    const session=(s.sessions||[]).find(x=>String(x?.id)===String(marker?.sessionId||''));
    const day=(s.days||[]).find(x=>String(x?.id)===String(marker?.dayId||session?.dayId||''));
    if(!session||!day)return null;
    return {
      version:'legacy',
      at:marker?.at||session?.date||null,
      studentId:s.id,
      athleteId:marker?.athleteId||null,
      dayId:day.id,
      day:cloneV316(day),
      session:cloneV316(session)
    };
  }
  function recoveryCandidatesV316(){
    const out=[],seen=new Set(),now=Date.now();
    try{
      Object.keys(localStorage).forEach(k=>{
        if(k.startsWith(BACKUP_PREFIX)){
          try{
            const x=JSON.parse(localStorage.getItem(k)||'null');
            const t=Date.parse(x?.at||x?.session?.date||0)||0;
            if(x?.session?.id&&t&&now-t<=MAX_RECOVERY_AGE&&!seen.has(x.session.id)){
              out.push(x);seen.add(x.session.id);
            }
          }catch(_e){}
        }
      });

      Object.keys(localStorage).filter(k=>k.startsWith('fjz_v205_closed:')).forEach(k=>{
        try{
          const marker=JSON.parse(localStorage.getItem(k)||'null');
          const t=Date.parse(marker?.at||0)||0;
          if(!marker?.sessionId||!t||now-t>MAX_RECOVERY_AGE||seen.has(marker.sessionId))return;
          const pack=legacySessionPackV316(marker);
          if(pack){out.push(pack);seen.add(marker.sessionId)}
        }catch(_e){}
      });

      const pending=JSON.parse(localStorage.getItem('fjz_v201_pending_session')||'null');
      if(pending?.sessionId&&!seen.has(pending.sessionId)){
        const t=Date.parse(pending?.at||0)||0;
        if(t&&now-t<=MAX_RECOVERY_AGE){
          const pack=legacySessionPackV316(pending);
          if(pack){out.push(pack);seen.add(pending.sessionId)}
        }
      }
    }catch(_e){}
    return out;
  }

  async function recoverPackV316(pack){
    const sid=String(pack?.session?.id||'');
    if(!sid||localStorage.getItem(DONE_PREFIX+sid))return false;
    const athlete=await resolveAthleteV316(pack);
    if(!athlete?.id||!athlete?.user_id||!pack?.day?.id)return false;

    if(await verifyCloudSessionV316(pack.session,athlete)){
      localStorage.setItem(DONE_PREFIX+sid,new Date().toISOString());
      return false;
    }

    const {error}=await supabaseClient.rpc('commit_workout_session_v202',{
      p_athlete_id:athlete.id,
      p_day_id:String(pack.day.id),
      p_day:cloneV316(pack.day),
      p_session:cloneV316(pack.session)
    });
    if(error)throw error;

    if(!await verifyCloudSessionV316(pack.session,athlete)){
      throw new Error('La recuperación no quedó confirmada en ambas rutas.');
    }

    localStorage.setItem(DONE_PREFIX+sid,new Date().toISOString());
    markBackupConfirmedV316(sid);
    return {athlete,session:pack.session};
  }

  async function recoverRecentV316(){
    if(recoveryRunning||!supabaseClient||!currentUser||!cloudEnabled)return;
    const ready=currentProfile?.role==='coach'
      ? Number(cloudAthletes?.size||0)>0
      : !!linkedAthleteId;
    if(!ready)return;

    recoveryRunning=true;
    let recovered=0;
    try{
      const candidates=recoveryCandidatesV316();
      for(const pack of candidates){
        try{
          const r=await recoverPackV316(pack);
          if(r)recovered++;
        }catch(e){
          console.warn('TEAM FJZ V21.16 local session recovery',e);
        }
      }
      if(recovered){
        try{
          if(currentProfile?.role==='coach')await loadCoachCloud?.();
          else await loadStudentCloud?.();
        }catch(_e){}
        try{toast('✓ Recuperamos '+recovered+' sesión'+(recovered===1?'':'es')+' que faltaba'+(recovered===1?'':'n')+' en la nube')}catch(_e){}
      }
    }finally{
      recoveryRunning=false;
    }
  }

  const basePostRenderV316=window.__fjzPostRenderV176;
  window.__fjzPostRenderV176=function(){
    const out=typeof basePostRenderV316==='function'
      ? basePostRenderV316.apply(this,arguments)
      : undefined;
    Promise.resolve().then(()=>recoverRecentV316());
    return out;
  };

  pruneBackupsV316();
  Promise.resolve().then(()=>recoverRecentV316());

  window.__fjzV316={
    version:VERSION,
    staleSnapshotCannotDeleteSessions:true,
    explicitDeleteRpc:true,
    snapshotAndProjectionConfirmation:true,
    localRecoveryBackup:true,
    legacyLocalRecovery:true,
    sessionSuccessRequiresDoubleVerification:true,
    noExtraTimers:true,
    noExtraListeners:true,
    noExtraObservers:true
  };
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-session-loss-protection" content="21.16">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V21.16 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-session-loss-protection" content="21.16"',
    'id="v316SessionLossProtectionRuntime"',
    "delete_workout_session_v214",
    "snapshotAndProjectionConfirmation:true",
    "localRecoveryBackup:true",
    "legacyLocalRecovery:true",
    "sessionSuccessRequiresDoubleVerification:true",
    "workout_sessions",
    "source_session_id",
    "fjz_v205_closed:",
    "fjz_v201_pending_session",
]:
    if marker not in html:
        raise RuntimeError("V21.16 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.16 session loss protection")
print("V21.16 BEFORE:",before)
print("V21.16 AFTER:",after)
