import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.7 CONFIRMED SESSION COMMIT STATE MACHINE
# =========================================================

# 1) V20.2 saveSessionV106 must only build/mutate the local pending session.
#    V20.7 owns cloud commit + draft clear + terminal UI after confirmation.
old_auto=r"""    setTimeout(()=>{
      window.__fjzCloudApplying=previousApplying;
      try{
        clearDraftV145?.(d.id,true);
        workoutDraft={};
      }catch(_e){}
      window.__fjzQueueSessionSyncV201?.(session,d.id);
    },0);

    return session;"""
new_auto=r"""    setTimeout(()=>{
      window.__fjzCloudApplying=previousApplying;
    },0);

    return session;"""
if html.count(old_auto)!=1:
    raise RuntimeError(f"V20.7 expected one V20.2 auto-queue block, got {html.count(old_auto)}")
html=html.replace(old_auto,new_auto,1)

# 2) While V20.7 is explicitly waiting for user-confirmed persistence,
#    disable the old automatic retry loop so UI and cloud state cannot diverge.
old_retry="""        clearTimeout(retryTimerV201);
        retryTimerV201=setTimeout(()=>retryPendingV201('timer'),5000);
        return false;"""
new_retry="""        if(!window.__fjzManualSessionCommitV207){
          clearTimeout(retryTimerV201);
          retryTimerV201=setTimeout(()=>retryPendingV201('timer'),5000);
        }
        return false;"""
if html.count(old_retry)!=1:
    raise RuntimeError(f"V20.7 expected one retry scheduler block, got {html.count(old_retry)}")
html=html.replace(old_retry,new_retry,1)

old_retry_guard="if(syncPromiseV201||navigator.onLine===false)return;"
new_retry_guard="if(window.__fjzManualSessionCommitV207||syncPromiseV201||navigator.onLine===false)return;"
if html.count(old_retry_guard)!=1:
    raise RuntimeError(f"V20.7 expected one retry guard, got {html.count(old_retry_guard)}")
html=html.replace(old_retry_guard,new_retry_guard,1)

css=r"""
<style id="v207ConfirmedSaveStyles">
body.v207-session-saving{
  overflow:hidden;
}
body.v207-session-saving button[onclick*="finishWorkout"],
body.v207-session-saving button[onclick*="confirmPartialSessionV106"]{
  pointer-events:none!important;
  opacity:.55!important;
}
.v207-save-state{
  display:grid;
  place-items:center;
  text-align:center;
  gap:10px;
  padding:18px 8px 8px;
}
.v207-save-icon{
  width:52px;
  height:52px;
  border-radius:50%;
  display:grid;
  place-items:center;
  font-size:23px;
  font-weight:950;
  border:1px solid rgba(255,255,255,.10);
  background:rgba(255,255,255,.035);
}
.v207-save-icon.saving{
  border-color:rgba(255,255,255,.12);
  animation:v207spin 1s linear infinite;
}
.v207-save-icon.success{
  border-color:rgba(74,222,128,.34);
  background:rgba(74,222,128,.08);
}
.v207-save-icon.error{
  border-color:rgba(255,68,85,.35);
  background:rgba(255,68,85,.08);
}
.v207-save-title{
  font-size:16px;
  font-weight:900;
  line-height:1.15;
}
.v207-save-copy{
  max-width:390px;
  color:var(--muted);
  font-size:10px;
  line-height:1.55;
}
.v207-save-actions{
  display:flex;
  justify-content:center;
  gap:8px;
  width:100%;
  margin-top:4px;
}
.v207-save-actions .btn{
  min-width:130px;
  min-height:44px;
}
@keyframes v207spin{
  from{transform:rotate(0deg)}
  to{transform:rotate(360deg)}
}
</style>
"""

js=r"""
<script id="v207ConfirmedSessionCommitRuntime">
(function(){
  const VERSION='20.7';
  const V205_CLOSED_PREFIX='fjz_v205_closed:';
  let stateV207='idle'; // idle | saving | failed | success
  let pendingV207=null;

  function escV207(v){return esc(String(v??''))}
  function cloneV207(x){
    try{return JSON.parse(JSON.stringify(x))}catch(_e){return x}
  }

  function modalSavingV207(){
    showModal(
      '<div class="v207-save-state">'+
        '<div class="v207-save-icon saving">↻</div>'+
        '<div class="v207-save-title">Guardando sesión…</div>'+
        '<div class="v207-save-copy">Estamos confirmando el entrenamiento en la nube. No cierres esta pantalla.</div>'+
      '</div>'
    );
  }

  function modalSuccessV207(){
    showModal(
      '<div class="v207-save-state">'+
        '<div class="v207-save-icon success">✓</div>'+
        '<div class="v207-save-title">Sesión guardada con éxito</div>'+
        '<div class="v207-save-copy">El entrenamiento quedó registrado correctamente. Ya podés salir con tranquilidad.</div>'+
        '<div class="v207-save-actions"><button class="btn primary" onclick="finishConfirmedSessionV207()">Listo</button></div>'+
      '</div>'
    );
  }

  function modalErrorV207(message){
    showModal(
      '<div class="v207-save-state">'+
        '<div class="v207-save-icon error">!</div>'+
        '<div class="v207-save-title">No se pudo confirmar el guardado</div>'+
        '<div class="v207-save-copy">'+escV207(message||'Revisá tu conexión y volvé a intentar. La sesión pendiente se conserva y no se duplicará.')+'</div>'+
        '<div class="v207-save-actions"><button class="btn primary" onclick="retryConfirmedSessionV207()">Reintentar</button></div>'+
      '</div>'
    );
  }

  function methodLogV207(e){
    const x=window.__fjzMethodDraftV110?.[e?.uid];
    if(!x||!e?.method||e.method==='normal')return null;
    const sets={};
    Object.entries(x.sets||{}).forEach(([si,row])=>{
      const clean={};
      Object.entries(row||{}).forEach(([k,v])=>{
        const n=Number(v);
        if(Number.isFinite(n)&&n>=0)clean[k]=n;
      });
      if(Object.keys(clean).length)sets[si]=clean;
    });
    const note=String(x.note||'').trim();
    if(!Object.keys(sets).length&&!note)return null;
    return {type:e.method,methodNote:e.methodNote||'',sets,note};
  }

  function attachMethodHistoryV207(pack,session){
    if(!pack||!session)return;
    (session.exerciseResults||[]).forEach(r=>{
      const e=(pack.d?.exercises||[]).find(x=>x.uid===r.exerciseUid);
      if(!e)return;
      const log=methodLogV207(e);
      if(!log)return;
      r.methodLog=cloneV207(log);
      if(r.completed&&e.history?.length){
        e.history[e.history.length-1].methodLog=cloneV207(log);
      }
    });
  }

  function markClosedV207(pack,session){
    const s=pack?.s,d=pack?.d;
    if(!s||!d||!session)return;
    const marker={
      studentId:s.id,
      dayId:d.id,
      sessionId:session.id,
      at:new Date().toISOString()
    };
    try{
      localStorage.setItem(V205_CLOSED_PREFIX+s.id+':'+d.id,JSON.stringify(marker));
    }catch(_e){}
    window.__fjzClosedWorkoutV205=marker;
    window.__fjzWorkoutClosedV204=marker;
    window.__fjzClosedWorkoutV207=marker;
  }

  function removeLocalPendingSessionV207(pack,session){
    // Used only if local session creation succeeds but no cloud attempt can
    // even be made. Normally we retain the same session for safe retry.
    if(!pack?.s||!session?.id)return;
    const idx=(pack.s.sessions||[]).findIndex(x=>x?.id===session.id);
    if(idx>=0)pack.s.sessions.splice(idx,1);
  }

  function createPendingV207(pack){
    if(pendingV207&&pendingV207.pack?.d?.id===pack?.d?.id)return pendingV207;

    const session=window.__fjzSaveSessionV205?.(pack);
    if(!session)throw new Error('No se pudo preparar la sesión.');

    attachMethodHistoryV207(pack,session);
    try{saveState()}catch(_e){}

    pendingV207={pack,session};
    return pendingV207;
  }

  async function persistPendingV207(){
    if(stateV207==='saving'||stateV207==='success'||!pendingV207)return;
    stateV207='saving';
    window.__fjzManualSessionCommitV207=true;
    document.body?.classList.add('v207-session-saving');
    modalSavingV207();

    const {pack,session}=pendingV207;
    try{
      const ok=await window.__fjzQueueSessionSyncV201?.(session,pack.d.id);
      if(!ok)throw new Error('No recibimos confirmación de la nube.');

      // Cloud confirmation is the single source of truth for terminal success.
      markClosedV207(pack,session);

      try{
        window.__fjzClearWorkoutDraftV205?.(pack.d.id,false);
        workoutDraft={};
        window.__fjzMethodDraftV110={};
      }catch(_e){}

      window.__v106PendingSession=null;
      window.__fjzPendingSavedSessionV190=null;
      window.__fjzPendingDraftClearV190=null;
      window.__fjzSessionCloudConfirmedId=session.id;

      stateV207='success';
      studentTab='home';
      currentDay=-1;
      render();
      modalSuccessV207();
    }catch(e){
      console.warn('TEAM FJZ V20.7 confirmed save failed',e);
      stateV207='failed';
      // Keep pendingV207 and the same session id. Retry cannot append another.
      try{
        studentTab='workout';
        const idx=(pack.s?.days||[]).findIndex(x=>x?.id===pack.d?.id);
        if(idx>=0)currentDay=idx;
      }catch(_e){}
      modalErrorV207('No se pudo confirmar la sesión en la nube. Tocá Reintentar: vamos a usar exactamente la misma sesión, sin duplicarla.');
    }finally{
      window.__fjzManualSessionCommitV207=false;
      document.body?.classList.remove('v207-session-saving');
    }
  }

  function beginCommitV207(pack){
    if(stateV207==='saving'||stateV207==='success'||!pack)return;
    try{
      createPendingV207(pack);
      persistPendingV207();
    }catch(e){
      console.error('TEAM FJZ V20.7 prepare save failed',e);
      stateV207='failed';
      modalErrorV207('No pudimos preparar el guardado. Tus datos cargados siguen en el entrenamiento.');
    }
  }

  window.retryConfirmedSessionV207=function(){
    if(stateV207!=='failed'||!pendingV207)return;
    persistPendingV207();
  };

  window.finishConfirmedSessionV207=function(){
    if(stateV207!=='success')return;
    try{closeModal?.()}catch(_e){}
    studentTab='home';
    currentDay=-1;
    render();
  };

  // FINAL canonical finish handler. No historical wrapper is invoked.
  window.finishWorkout=function(){
    if(stateV207==='saving')return;
    if(stateV207==='success'){
      modalSuccessV207();
      return;
    }
    if(stateV207==='failed'&&pendingV207){
      modalErrorV207();
      return;
    }

    const pack=window.__fjzSessionDraftV205?.();
    if(!pack?.d)return;
    if(!pack.d.exercises?.length){
      studentTab='home';currentDay=-1;render();return;
    }
    if(!pack.registered?.length){
      toast('Cargá al menos una serie para guardar la sesión');
      return;
    }

    const partial=(pack.registered||[]).filter(x=>!x.complete);
    const missing=(pack.skipped||[]).length+partial.length;
    if(!missing){
      beginCommitV207(pack);
      return;
    }

    window.__v106PendingSession=pack;
    const parts=[];
    if(pack.skipped?.length)parts.push(pack.skipped.length+' ejercicio'+(pack.skipped.length===1?'':'s')+' sin cargar');
    if(partial.length)parts.push(partial.length+' ejercicio'+(partial.length===1?'':'s')+' incompleto'+(partial.length===1?'':'s'));

    showModal(
      '<div class="modal-head"><div><h3>Finalizar entrenamiento</h3><div class="muted tiny">Revisá antes de confirmar.</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="card"><strong>'+escV207(parts.join(' · '))+'</strong><div class="muted tiny" style="margin-top:6px">Se guardarán únicamente las series con datos válidos.</div></div>'+
      '<div class="pill-row" style="justify-content:flex-end;margin-top:12px"><button class="btn" onclick="closeModal()">Seguir entrenando</button><button class="btn primary" onclick="confirmPartialSessionV106()">Guardar y finalizar</button></div>'
    );
  };
  try{finishWorkout=window.finishWorkout}catch(_e){}

  window.confirmPartialSessionV106=function(){
    if(stateV207==='saving')return;
    if(stateV207==='success'){
      modalSuccessV207();
      return;
    }
    if(stateV207==='failed'&&pendingV207){
      modalErrorV207();
      return;
    }
    const pack=window.__v106PendingSession;
    window.__v106PendingSession=null;
    if(!pack){closeModal?.();return}
    beginCommitV207(pack);
  };
  try{confirmPartialSessionV106=window.confirmPartialSessionV106}catch(_e){}

  // A new explicit workout is the ONLY event that re-arms saving.
  const baseStartV207=window.startWorkout||globalThis.startWorkout;
  if(typeof baseStartV207==='function'){
    const wrapped=function(){
      stateV207='idle';
      pendingV207=null;
      window.__fjzManualSessionCommitV207=false;
      window.__v106PendingSession=null;
      document.body?.classList.remove('v207-session-saving');
      return baseStartV207.apply(this,arguments);
    };
    window.startWorkout=wrapped;
    try{startWorkout=wrapped}catch(_e){}
  }

  window.__fjzSessionSaveStateV207=function(){
    return {
      state:stateV207,
      sessionId:pendingV207?.session?.id||null,
      dayId:pendingV207?.pack?.d?.id||null,
      cloudConfirmed:!!(
        pendingV207?.session?.id&&
        window.__fjzSessionCloudConfirmedId===pendingV207.session.id
      )
    };
  };

  window.__fjzV207={
    version:VERSION,
    cloudConfirmationBeforeSuccess:true,
    successModalAfterConfirmedSave:true,
    retryUsesSameSessionId:true,
    duplicateSaveByDesignBlocked:true,
    saveButtonLockedWhileSaving:true,
    failedSaveRemainsRetryable:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

# Consolidate styles.
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
mergeable=[]
for m in styles:
    attrs=m.group("attrs") or ""
    if re.search(r"\b(media|nonce)\s*=",attrs,re.I):continue
    mergeable.append(m)
if len(mergeable)>1:
    chunks=[]
    for m in mergeable:
        ident=re.search(r'id=["\']([^"\']+)["\']',m.group("attrs") or "",re.I)
        name=ident.group(1) if ident else "anonymous"
        chunks.append("\n/* --- "+name+" --- */\n"+m.group("body").strip())
    for m in reversed(mergeable):
        html=html[:m.start()]+html[m.end():]
    html=html.replace("</head>",'<style id="fjzProductionStylesV207">'+''.join(chunks)+'\n</style>\n</head>',1)

critical=[
  "cloudConfirmationBeforeSuccess:true",
  "successModalAfterConfirmedSave:true",
  "retryUsesSameSessionId:true",
  "duplicateSaveByDesignBlocked:true",
  "failedSaveRemainsRetryable:true",
  "__fjzSessionSaveStateV207",
  "__fjzQueueSessionSyncV201"
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.7 missing critical markers: "+repr(missing))

if old_auto in html:
    raise RuntimeError("V20.7 old automatic session queue/clear remains")
if len(re.findall(r"<style\b",html,re.I))!=1:
    raise RuntimeError("V20.7 expected one final stylesheet")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.7 confirmed session commit state machine enabled")
print("TEAM FJZ V20.7 automatic premature session close removed")
