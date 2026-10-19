import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.8 PENDING SESSION RELOAD GUARD
# =========================================================
# V20.7 already guarantees terminal success only after Supabase confirms.
# V20.8 closes the remaining reload/crash edge case: if a cloud-confirmation
# attempt was left pending in localStorage, a new finish/start action cannot
# create another local session before that pending session is reconciled.

required=[
    "__fjzV207",
    "__fjzQueueSessionSyncV201",
    "fjz_v201_pending_session",
    "__fjzClearWorkoutDraftV205"
]
missing=[x for x in required if x not in html]
if missing:
    raise RuntimeError("V20.8 missing prerequisite markers: "+repr(missing))

if 'id="v208PendingSessionReloadGuard"' in html:
    raise RuntimeError("V20.8 runtime already present")

js=r"""
<script id="v208PendingSessionReloadGuard">
(function(){
  const VERSION='20.8';
  const PENDING_KEY='fjz_v201_pending_session';
  const CLOSED_PREFIX='fjz_v205_closed:';
  let recoveryPromiseV208=null;

  function readPendingV208(){
    try{return JSON.parse(localStorage.getItem(PENDING_KEY)||'null')}
    catch(_e){return null}
  }

  function currentPendingV208(){
    const p=readPendingV208();
    const s=typeof student==='function'?student():null;
    if(!p||!s||!currentUser)return null;
    if(p.userId!==currentUser.id)return null;
    if(p.studentId!==s.id)return null;
    return p;
  }

  function pendingSessionV208(p){
    const s=typeof student==='function'?student():null;
    if(!s||!p?.sessionId)return null;
    return (s.sessions||[]).find(x=>x?.id===p.sessionId)||null;
  }

  function markRecoveredClosedV208(p,session){
    const s=typeof student==='function'?student():null;
    if(!s||!p?.dayId||!session?.id)return;
    const marker={
      studentId:s.id,
      dayId:p.dayId,
      sessionId:session.id,
      at:new Date().toISOString()
    };
    try{
      localStorage.setItem(CLOSED_PREFIX+s.id+':'+p.dayId,JSON.stringify(marker));
    }catch(_e){}
    window.__fjzClosedWorkoutV205=marker;
    window.__fjzWorkoutClosedV204=marker;
    window.__fjzClosedWorkoutV207=marker;
    window.__fjzClosedWorkoutV208=marker;
  }

  function pendingModalV208(copy){
    showModal(
      '<div class="v207-save-state">'+
        '<div class="v207-save-icon saving">↻</div>'+
        '<div class="v207-save-title">Confirmando sesión pendiente…</div>'+
        '<div class="v207-save-copy">'+esc(copy||'Hay una sesión anterior que todavía necesita confirmación en la nube. La recuperamos antes de continuar para evitar duplicados.')+'</div>'+
      '</div>'
    );
  }

  function pendingErrorV208(){
    showModal(
      '<div class="v207-save-state">'+
        '<div class="v207-save-icon error">!</div>'+
        '<div class="v207-save-title">La sesión sigue pendiente</div>'+
        '<div class="v207-save-copy">No vamos a crear otra sesión mientras esta siga sin confirmar. Tus datos locales se conservan.</div>'+
        '<div class="v207-save-actions"><button class="btn primary" onclick="retryPendingSessionV208()">Reintentar</button><button class="btn" onclick="closeModal()">Cerrar</button></div>'+
      '</div>'
    );
  }

  function recoveredModalV208(){
    showModal(
      '<div class="v207-save-state">'+
        '<div class="v207-save-icon success">✓</div>'+
        '<div class="v207-save-title">Sesión recuperada y guardada</div>'+
        '<div class="v207-save-copy">La sesión pendiente quedó confirmada correctamente. Ya podés continuar con normalidad.</div>'+
        '<div class="v207-save-actions"><button class="btn primary" onclick="finishRecoveredSessionV208()">Listo</button></div>'+
      '</div>'
    );
  }

  async function recoverPendingV208(showFeedback=true){
    if(recoveryPromiseV208)return recoveryPromiseV208;

    const p=currentPendingV208();
    if(!p)return true;

    const session=pendingSessionV208(p);
    if(!session){
      if(showFeedback)pendingErrorV208();
      return false;
    }

    if(showFeedback)pendingModalV208();
    window.__fjzRecoveringPendingV208=true;

    recoveryPromiseV208=(async()=>{
      try{
        const ok=await window.__fjzQueueSessionSyncV201?.(session,p.dayId);
        if(!ok)throw new Error('Cloud confirmation unavailable');

        markRecoveredClosedV208(p,session);
        window.__fjzSessionCloudConfirmedId=session.id;

        try{
          window.__fjzClearWorkoutDraftV205?.(p.dayId,false);
          workoutDraft={};
          window.__fjzMethodDraftV110={};
        }catch(_e){}

        try{
          const nowPending=readPendingV208();
          if(nowPending?.sessionId===session.id){
            localStorage.removeItem(PENDING_KEY);
          }
        }catch(_e){}

        if(showFeedback)recoveredModalV208();
        return true;
      }catch(e){
        console.warn('TEAM FJZ V20.8 pending recovery failed',e);
        if(showFeedback)pendingErrorV208();
        return false;
      }finally{
        window.__fjzRecoveringPendingV208=false;
        recoveryPromiseV208=null;
      }
    })();

    return recoveryPromiseV208;
  }

  function guardPendingV208(){
    const p=currentPendingV208();
    if(!p)return false;
    recoverPendingV208(true);
    return true;
  }

  window.retryPendingSessionV208=function(){
    recoverPendingV208(true);
  };

  window.finishRecoveredSessionV208=function(){
    try{closeModal?.()}catch(_e){}
    studentTab='home';
    currentDay=-1;
    render();
  };

  const baseStartV208=window.startWorkout||globalThis.startWorkout;
  if(typeof baseStartV208==='function'){
    const wrapped=function(){
      if(guardPendingV208())return;
      return baseStartV208.apply(this,arguments);
    };
    window.startWorkout=wrapped;
    try{startWorkout=wrapped}catch(_e){}
  }

  const baseFinishV208=window.finishWorkout||globalThis.finishWorkout;
  if(typeof baseFinishV208==='function'){
    const wrapped=function(){
      if(guardPendingV208())return;
      return baseFinishV208.apply(this,arguments);
    };
    window.finishWorkout=wrapped;
    try{finishWorkout=wrapped}catch(_e){}
  }

  const basePartialV208=window.confirmPartialSessionV106;
  if(typeof basePartialV208==='function'){
    const wrapped=function(){
      if(guardPendingV208())return;
      return basePartialV208.apply(this,arguments);
    };
    window.confirmPartialSessionV106=wrapped;
    try{confirmPartialSessionV106=wrapped}catch(_e){}
  }

  window.__fjzPendingSessionStateV208=function(){
    const p=currentPendingV208();
    return {
      version:VERSION,
      pending:!!p,
      sessionId:p?.sessionId||null,
      dayId:p?.dayId||null,
      recovering:!!recoveryPromiseV208
    };
  };

  window.__fjzV208={
    version:VERSION,
    reloadPendingGuard:true,
    startBlockedWhilePending:true,
    finishBlockedWhilePending:true,
    sameSessionRecovery:true,
    productionDbMigrationRequired:false
  };
})();
</script>
"""

html=html.replace("</body>",js+"\n</body>",1)

critical=[
    "__fjzPendingSessionStateV208",
    "reloadPendingGuard:true",
    "startBlockedWhilePending:true",
    "finishBlockedWhilePending:true",
    "sameSessionRecovery:true"
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.8 missing critical markers: "+repr(missing))

if len(re.findall(r'id="v208PendingSessionReloadGuard"',html))!=1:
    raise RuntimeError("V20.8 expected exactly one runtime guard")

# V20.8 adds no CSS authority and no extra background listeners/timers.
# This intentionally avoids increasing the V20.6 render/listener churn budget.
p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.8 pending-session reload guard enabled")
