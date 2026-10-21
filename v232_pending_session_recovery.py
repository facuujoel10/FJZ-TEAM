import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.32 PENDING SESSION RECOVERY HARDENING
# =========================================================
# Close the reload/crash gap left between V20.2 pending persistence and the
# V20.7 in-memory confirmation state.
#
# Invariants:
# - same pending session id is always reused
# - missing local state NEVER clears the pending marker
# - a new workout cannot start until the pending session is reconciled
# - V20.7 in-memory saving/failed/success flow keeps its authority
# - no new listeners, timers, channels, observers or wrapper assignments

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "render_assignments":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "start_assignments":len(re.findall(r"(?:window\.)?startWorkout\s*=",doc)),
        "finish_assignments":len(re.findall(r"(?:window\.)?finishWorkout\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

def edit_script(doc,script_id,transform):
    pat=re.compile(
        r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',
        re.S|re.I
    )
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.32 missing script: "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.32 no change in "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)
if before["styles"]!=1:
    raise RuntimeError("V20.32 expected one stylesheet: "+repr(before))
if before["render_assignments"]!=20 or before["channels"]!=2:
    raise RuntimeError("V20.32 unexpected V20.31 topology: "+repr(before))

# ---------------------------------------------------------
# 1) V20.2: never silently erase a pending marker when the
#    local session copy cannot be found after reload.
# ---------------------------------------------------------
def patch_v201(body):
    old_missing="""    if(!session){
      clearPendingV201(p.sessionId);
      return;
    }"""
    new_missing="""    if(!session){
      window.__fjzPendingSessionMissingLocalV232={
        ...p,
        noticedAt:new Date().toISOString(),
        reason:String(reason||'retry')
      };
      try{window.setCloudStatus?.('error','Sesión pendiente de recuperar')}catch(_e){}
      return false;
    }
    window.__fjzPendingSessionMissingLocalV232=null;"""
    if body.count(old_missing)!=1:
        raise RuntimeError("V20.32 V20.2 missing-local branch mismatch: "+str(body.count(old_missing)))
    body=body.replace(old_missing,new_missing,1)

    anchor="""  async function retryPendingV201(reason){"""
    if body.count(anchor)!=1:
        raise RuntimeError("V20.32 V20.2 retry anchor mismatch: "+str(body.count(anchor)))

    recovery=r"""
  function pendingForCurrentV232(){
    const p=pendingV201();
    const s=student?.();
    if(!p||!currentUser||p.userId!==currentUser.id||!s)return null;
    if(p.studentId&&p.studentId!==s.id)return null;
    return p;
  }

  function pendingSessionLocalV232(p){
    const s=student?.();
    if(!p||!s)return null;
    return (s.sessions||[]).find(x=>x?.id===p.sessionId)||null;
  }

  function pendingModalV232(kind){
    const missing=kind==='missing';
    const offline=kind==='offline';
    const title=missing?'Sesión pendiente por recuperar':
      offline?'Sin conexión para recuperar la sesión':
      'Hay una sesión pendiente de guardado';
    const copy=missing
      ?'La sesión pendiente sigue protegida, pero todavía no aparece en los datos locales. No vamos a borrarla ni iniciar otra sesión hasta reconciliarla.'
      :offline
        ?'La sesión pendiente sigue guardada en este dispositivo. Conectate a internet y reintentá antes de empezar otro entrenamiento.'
        :'Antes de empezar otro entrenamiento tenemos que confirmar la sesión anterior. Se va a reutilizar exactamente el mismo registro para evitar duplicados.';
    const action=missing
      ?'<button class="btn primary" onclick="recoverPendingSessionV232(true)">Actualizar y reintentar</button>'
      :'<button class="btn primary" onclick="recoverPendingSessionV232(false)">Reintentar guardado</button>';

    showModal(
      '<div class="modal-head"><div><h3>'+title+'</h3><div class="muted tiny">Protección anti-duplicados TEAM FJZ</div></div></div>'+
      '<div class="v207-save-state">'+
        '<div class="v207-save-icon '+(missing||offline?'error':'saving')+'">'+(missing||offline?'!':'↻')+'</div>'+
        '<div class="v207-save-copy">'+copy+'</div>'+
        '<div class="v207-save-actions">'+action+'<button class="btn" onclick="closeModal()">Volver</button></div>'+
      '</div>'
    );
  }

  window.__fjzHasBlockingPendingSessionV232=function(){
    return !!pendingForCurrentV232();
  };

  window.__fjzShowPendingRecoveryV232=function(){
    const p=pendingForCurrentV232();
    if(!p)return false;
    if(navigator.onLine===false){
      pendingModalV232('offline');
      return true;
    }
    pendingModalV232(pendingSessionLocalV232(p)?'pending':'missing');
    return true;
  };

  window.__fjzRequestPendingStartV232=function(i){
    const n=Number(i);
    window.__fjzPendingStartIndexV232=Number.isInteger(n)?n:null;
    return window.__fjzShowPendingRecoveryV232?.();
  };

  window.recoverPendingSessionV232=async function(refreshFirst){
    if(window.__fjzPendingRecoverBusyV232)return false;

    let p=pendingForCurrentV232();
    if(!p){
      try{closeModal?.()}catch(_e){}
      const idx=window.__fjzPendingStartIndexV232;
      window.__fjzPendingStartIndexV232=null;
      if(Number.isInteger(idx))window.startWorkout?.(idx);
      return true;
    }

    if(navigator.onLine===false){
      pendingModalV232('offline');
      return false;
    }

    window.__fjzPendingRecoverBusyV232=true;
    window.__fjzManualSessionCommitV207=true;
    try{
      if(refreshFirst){
        try{await window.refreshCloudFromRealtime?.()}catch(e){
          console.warn('TEAM FJZ V20.32 refresh before recovery',e);
        }
        p=pendingForCurrentV232()||p;
      }

      const session=pendingSessionLocalV232(p);
      if(!session){
        window.__fjzPendingSessionMissingLocalV232={
          ...p,
          noticedAt:new Date().toISOString(),
          reason:'manual-recovery'
        };
        pendingModalV232('missing');
        return false;
      }

      showModal(
        '<div class="v207-save-state">'+
          '<div class="v207-save-icon saving">↻</div>'+
          '<div class="v207-save-title">Recuperando sesión…</div>'+
          '<div class="v207-save-copy">Estamos confirmando el mismo entrenamiento pendiente en la nube. No se creará una sesión nueva.</div>'+
        '</div>'
      );

      const ok=await persistSelectedSnapshotV201(session,p.dayId);
      if(!ok)throw new Error('La nube todavía no confirmó la sesión.');

      window.__fjzPendingSessionMissingLocalV232=null;
      try{closeModal?.()}catch(_e){}
      toast?.('Sesión pendiente recuperada y guardada');

      const idx=window.__fjzPendingStartIndexV232;
      window.__fjzPendingStartIndexV232=null;
      if(Number.isInteger(idx))window.startWorkout?.(idx);
      return true;
    }catch(e){
      console.warn('TEAM FJZ V20.32 pending recovery',e);
      pendingModalV232('pending');
      return false;
    }finally{
      window.__fjzManualSessionCommitV207=false;
      window.__fjzPendingRecoverBusyV232=false;
    }
  };

  window.__fjzV232={
    version:'20.32',
    pendingMarkerPreservedWhenLocalMissing:true,
    sameSessionIdRecovery:true,
    blocksNewWorkoutUntilReconciled:true,
    noPendingDiscardPath:true,
    refreshThenRetrySupported:true
  };

"""
    body=body.replace(anchor,recovery+anchor,1)
    return body

html=edit_script(html,"v201WorkoutSaveRuntime",patch_v201)

# ---------------------------------------------------------
# 2) V20.5: this is the outer startWorkout authority.
#    Block BEFORE it clears closed-state / re-arms the day.
# ---------------------------------------------------------
def patch_v205(body):
    old="""    const wrapped=function(i){
      const s=student?.(),d=s?.days?.[i];"""
    new="""    const wrapped=function(i){
      if(window.__fjzHasBlockingPendingSessionV232?.()){
        window.__fjzRequestPendingStartV232?.(i);
        return;
      }
      const s=student?.(),d=s?.days?.[i];"""
    if body.count(old)!=1:
        raise RuntimeError("V20.32 V20.5 start authority mismatch: "+str(body.count(old)))
    return body.replace(old,new,1)

html=edit_script(html,"v205CanonicalWorkoutProgressRuntime",patch_v205)

# ---------------------------------------------------------
# 3) V20.7: after a reload its state machine resets to idle.
#    In that specific state, an old pending marker must win.
# ---------------------------------------------------------
def patch_v207(body):
    old_finish="""  window.finishWorkout=function(){
    if(stateV207==='saving')return;"""
    new_finish="""  window.finishWorkout=function(){
    if(stateV207==='idle'&&window.__fjzHasBlockingPendingSessionV232?.()){
      window.__fjzShowPendingRecoveryV232?.();
      return;
    }
    if(stateV207==='saving')return;"""
    if body.count(old_finish)!=1:
        raise RuntimeError("V20.32 V20.7 finish authority mismatch: "+str(body.count(old_finish)))
    body=body.replace(old_finish,new_finish,1)

    old_partial="""  window.confirmPartialSessionV106=function(){
    if(stateV207==='saving')return;"""
    new_partial="""  window.confirmPartialSessionV106=function(){
    if(stateV207==='idle'&&window.__fjzHasBlockingPendingSessionV232?.()){
      window.__fjzShowPendingRecoveryV232?.();
      return;
    }
    if(stateV207==='saving')return;"""
    if body.count(old_partial)!=1:
        raise RuntimeError("V20.32 V20.7 partial authority mismatch: "+str(body.count(old_partial)))
    return body.replace(old_partial,new_partial,1)

html=edit_script(html,"v207ConfirmedSessionCommitRuntime",patch_v207)

marker='<meta name="fjz-pending-session-recovery" content="20.32">'
if re.search(r'<meta\s+name=["\']fjz-pending-session-recovery["\']',html,re.I):
    html=re.sub(
        r'<meta\s+name=["\']fjz-pending-session-recovery["\']\s+content=["\'][^"\']*["\']\s*/?>',
        marker,html,count=1,flags=re.I
    )
else:
    html=html.replace("</head>",marker+"\n</head>",1)

after=metrics(html)

# No runtime topology growth: only behavior inside existing authorities.
for key in (
    "styles","render_assignments","start_assignments","finish_assignments",
    "channels","mutation_observers","performance_observers",
    "timeouts","rafs","listeners"
):
    if after[key]!=before[key]:
        raise RuntimeError("V20.32 runtime topology changed for "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-pending-session-recovery" content="20.32"',
    "pendingMarkerPreservedWhenLocalMissing:true",
    "sameSessionIdRecovery:true",
    "blocksNewWorkoutUntilReconciled:true",
    "noPendingDiscardPath:true",
    "refreshThenRetrySupported:true",
    "__fjzHasBlockingPendingSessionV232",
    "__fjzRequestPendingStartV232",
    "recoverPendingSessionV232",
    "__fjzQueueSessionSyncV201",
    "__fjzManualSessionCommitV207",
    "cloudConfirmationBeforeSuccess:true",
    "retryUsesSameSessionId:true",
    "savedWorkoutCannotReopen:true",
    "modalReorderUsesAtomicRpc:true",
    'meta name="fjz-routine-builder-ui" content="20.31"'
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.32 missing recovery/stability marker: "+repr(missing))

# Explicit regression checks.
if "clearPendingV201(p.sessionId);" in html:
    raise RuntimeError("V20.32 unsafe missing-local pending clear still present")
if "window.__fjzPendingStartIndexV232=null;" not in html:
    raise RuntimeError("V20.32 pending start intent cleanup missing")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.32 pending session recovery hardening")
print("V20.32 BEFORE:",before)
print("V20.32 AFTER:",after)
print("V20.32 pending session is preserved/reconciled before any new workout")
