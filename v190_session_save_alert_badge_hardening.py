import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V19.0 SESSION SAVE CONFIRMATION + BADGE GEOMETRY
# =========================================================

# 1) Session save must be async and must not show final success until cloud
#    synchronization has been verified.
needle="  function saveSessionV106(pack){"
if html.count(needle)!=1:
    raise RuntimeError(f"V19.0 expected one saveSessionV106, got {html.count(needle)}")
html=html.replace(needle,"  async function saveSessionV106(pack){",1)

save_anchor="""    s.sessions=s.sessions||[];
    s.sessions.push(session);
    s.lastWorkout=session.date;
    saveState();

    const skippedText="""
save_repl="""    s.sessions=s.sessions||[];
    s.sessions.push(session);
    s.lastWorkout=session.date;
    saveState();

    const cloudConfirmed=await window.__fjzConfirmSessionSavedV190?.(session,d.id);
    if(cloudConfirmed===false){
      showModal(
        '<div class="modal-head"><div><h3>Sesión pendiente de sincronización</h3><div class="muted tiny">Tus datos quedaron guardados en este dispositivo, pero todavía no pude confirmarlos en la nube.</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
        '<div class="card"><strong>No vuelvas a guardar la sesión</strong><div class="muted tiny" style="margin-top:6px">TEAM FJZ va a reintentar la sincronización. Podés usar “Reintentar ahora” sin duplicar el entrenamiento.</div></div>'+
        '<button class="btn primary" style="width:100%;margin-top:12px" onclick="window.__fjzRetrySessionSyncV190?.()">Reintentar ahora</button>'
      );
      return;
    }

    const skippedText="""
if html.count(save_anchor)!=1:
    raise RuntimeError(f"V19.0 save confirmation anchor mismatch: {html.count(save_anchor)}")
html=html.replace(save_anchor,save_repl,1)

# 2) Do not destroy the autosave draft until the saved session is actually
#    present in the cloud snapshot. This prevents a realtime/cloud race from
#    erasing the only recoverable copy.
old_clear="""  function clearIfSessionSavedV145(dayId,beforeCount){
    const s=student();
    if((s.sessions||[]).length>beforeCount){
      clearDraftV145(dayId,true);
      workoutDraft={};
      window.__fjzMethodDraftV110={};
      return true;
    }
    return false;
  }"""
new_clear="""  function clearIfSessionSavedV145(dayId,beforeCount){
    const s=student();
    if((s.sessions||[]).length>beforeCount){
      const saved=(s.sessions||[])[(s.sessions||[]).length-1]||null;
      window.__fjzPendingDraftClearV190=saved?.id?{sessionId:saved.id,dayId}:null;
      if(saved?.id&&window.__fjzSessionCloudConfirmedId===saved.id){
        clearDraftV145(dayId,true);
        workoutDraft={};
        window.__fjzMethodDraftV110={};
        window.__fjzPendingDraftClearV190=null;
      }
      return true;
    }
    return false;
  }

  window.__fjzFinalizeSessionDraftV190=function(sessionId){
    const p=window.__fjzPendingDraftClearV190;
    if(!p||!sessionId||p.sessionId!==sessionId)return false;
    clearDraftV145(p.dayId,true);
    workoutDraft={};
    window.__fjzMethodDraftV110={};
    window.__fjzPendingDraftClearV190=null;
    return true;
  };"""
if html.count(old_clear)!=1:
    raise RuntimeError(f"V19.0 expected one V145 draft clear, got {html.count(old_clear)}")
html=html.replace(old_clear,new_clear,1)

css=r"""
<style id="v190SaveBadgeHardeningStyles">
/* Red alert/status pills must always contain the full label. */
.badge.red,
.v175-agenda-row-badge,
.v175-agenda-tab-badge,
.v73-alert-badge,
.v80-student-alert-count{
  display:inline-flex!important;
  align-items:center!important;
  justify-content:center!important;
  width:auto!important;
  min-width:max-content!important;
  max-width:100%!important;
  min-height:24px!important;
  height:auto!important;
  padding:5px 9px!important;
  box-sizing:border-box!important;
  border-radius:999px!important;
  line-height:1.1!important;
  white-space:nowrap!important;
  word-break:keep-all!important;
  overflow:visible!important;
  text-overflow:clip!important;
  flex-shrink:0!important;
}

/* Buttons should visibly communicate the cloud-save transaction. */
body.v190-session-saving button[onclick*="finishWorkout"],
body.v190-session-saving button[onclick*="confirmPartialSessionV106"]{
  pointer-events:none!important;
  opacity:.72!important;
}

.v190-save-state{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  min-height:24px;
  padding:5px 9px;
  border:1px solid var(--border);
  border-radius:999px;
  font-size:9px;
  line-height:1.1;
  white-space:nowrap;
}
</style>
"""

js=r"""
<script id="v190SessionSaveBadgeHardeningRuntime">
(function(){
  const VERSION='19.0';
  let pendingSessionV190=null;
  let syncPromiseV190=null;

  function athleteIdV190(){
    if(currentProfile?.role==='student')return linkedAthleteId||null;
    const s=student?.();
    return s?cloudAthletes?.get?.(s.id)?.id||null:null;
  }

  function localHasV190(sessionId){
    return !!(student?.()?.sessions||[]).some(x=>x?.id===sessionId);
  }

  async function remoteHasV190(athleteId,sessionId){
    if(!supabaseClient||!athleteId||!sessionId)return false;
    const {data,error}=await supabaseClient
      .from('athlete_snapshots')
      .select('data,updated_at')
      .eq('athlete_id',athleteId)
      .maybeSingle();
    if(error)throw error;
    return !!(data?.data?.sessions||[]).some(x=>x?.id===sessionId);
  }

  async function waitV190(ms){
    return new Promise(resolve=>setTimeout(resolve,ms));
  }

  async function confirmCloudV190(session,dayId){
    if(!session?.id)return false;
    pendingSessionV190={sessionId:session.id,dayId,session};
    window.__fjzPendingSavedSessionV190=pendingSessionV190;
    document.body?.classList.add('v190-session-saving');

    if(!localHasV190(session.id)){
      document.body?.classList.remove('v190-session-saving');
      return false;
    }

    const athleteId=athleteIdV190();
    if(!cloudEnabled||!supabaseClient||!athleteId){
      try{window.setCloudStatus?.('error','Sesión pendiente')}catch(_e){}
      document.body?.classList.remove('v190-session-saving');
      return false;
    }

    if(syncPromiseV190)return syncPromiseV190;

    syncPromiseV190=(async()=>{
      let lastError=null;
      for(let attempt=1;attempt<=3;attempt++){
        try{
          try{window.setCloudStatus?.('syncing','Guardando sesión…')}catch(_e){}
          await window.syncCloudNow?.();

          if(await remoteHasV190(athleteId,session.id)){
            window.__fjzSessionCloudConfirmedId=session.id;
            window.__fjzFinalizeSessionDraftV190?.(session.id);
            try{window.setCloudStatus?.('online','Sesión guardada')}catch(_e){}
            pendingSessionV190=null;
            window.__fjzPendingSavedSessionV190=null;
            return true;
          }
          lastError=new Error('La sesión todavía no aparece en el snapshot remoto');
        }catch(e){
          lastError=e;
          console.warn('TEAM FJZ V19.0 session sync attempt '+attempt,e);
        }
        if(attempt<3)await waitV190(450*attempt);
      }

      try{window.setCloudStatus?.('error','Sesión pendiente')}catch(_e){}
      console.warn('TEAM FJZ V19.0 session remains pending',lastError);
      return false;
    })().finally(()=>{
      syncPromiseV190=null;
      document.body?.classList.remove('v190-session-saving');
    });

    return syncPromiseV190;
  }

  window.__fjzConfirmSessionSavedV190=confirmCloudV190;

  window.__fjzRetrySessionSyncV190=async function(){
    const p=pendingSessionV190||window.__fjzPendingSavedSessionV190;
    if(!p?.session){
      toast('No hay una sesión pendiente para reintentar');
      return;
    }
    const ok=await confirmCloudV190(p.session,p.dayId);
    if(ok){
      closeModal();
      toast('Sesión sincronizada correctamente');
      studentTab='home';
      render();
    }else{
      toast('Sigue pendiente. TEAM FJZ va a continuar reintentando.');
    }
  };

  /* Guard against double-taps / duplicate sessions while a save transaction
     is already in progress. */
  const baseFinishV190=window.finishWorkout||globalThis.finishWorkout;
  if(typeof baseFinishV190==='function'){
    window.finishWorkout=function(){
      if(document.body?.classList.contains('v190-session-saving')){
        toast('La sesión ya se está guardando');
        return;
      }
      return baseFinishV190.apply(this,arguments);
    };
    try{finishWorkout=window.finishWorkout}catch(_e){}
  }

  const basePartialV190=window.confirmPartialSessionV106;
  if(typeof basePartialV190==='function'){
    window.confirmPartialSessionV106=function(){
      if(document.body?.classList.contains('v190-session-saving')){
        toast('La sesión ya se está guardando');
        return;
      }
      return basePartialV190.apply(this,arguments);
    };
  }

  window.__fjzV190={
    version:VERSION,
    cloudConfirmedSessionSave:true,
    draftClearAfterCloudConfirmation:true,
    duplicateSaveGuard:true,
    remoteSnapshotVerification:true,
    redBadgeGeometryFixed:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "cloudConfirmedSessionSave:true",
  "draftClearAfterCloudConfirmation:true",
  "duplicateSaveGuard:true",
  "remoteSnapshotVerification:true",
  "redBadgeGeometryFixed:true",
]:
    if marker not in html:
        raise RuntimeError("V19.0 missing marker: "+marker)

if "async function saveSessionV106(pack)" not in html:
    raise RuntimeError("V19.0 saveSessionV106 is not async")
if "__fjzFinalizeSessionDraftV190" not in html:
    raise RuntimeError("V19.0 draft finalizer missing")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V19.0 session save confirmation + badge hardening enabled")
