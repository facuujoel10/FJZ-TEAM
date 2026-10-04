import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v193InteractionPersistenceStyles">
/* A modal/editing surface is an interaction boundary. */
#modalWrap.v193-interaction-open{
  overscroll-behavior:contain!important;
}
#modalWrap.v193-interaction-open #modal{
  pointer-events:auto!important;
}
</style>
"""

js=r"""
<script id="v193InteractionPersistenceRuntime">
(function(){
  const VERSION='19.3';
  let interactionLockUntilV193=0;
  let deferredTablesV193=new Set();
  let deferredTimerV193=0;

  function modalVisibleV193(){
    const wrap=document.getElementById('modalWrap');
    if(!wrap)return false;
    const cs=getComputedStyle(wrap);
    return cs.display!=='none'&&cs.visibility!=='hidden'&&cs.pointerEvents!=='none';
  }

  function editingSurfaceV193(){
    if(modalVisibleV193())return true;
    const a=document.activeElement;
    if(a?.matches?.('input,select,textarea,[contenteditable="true"]'))return true;
    if(document.body?.classList.contains('v190-session-saving'))return true;
    return Date.now()<interactionLockUntilV193;
  }

  function syncModalStateV193(){
    const wrap=document.getElementById('modalWrap');
    wrap?.classList.toggle('v193-interaction-open',modalVisibleV193());
  }

  // Internal modal clicks must never reach an overlay/document click handler.
  function bindModalBoundaryV193(){
    const modal=document.getElementById('modal');
    if(!modal||modal.__v193Bound)return;
    modal.__v193Bound=true;
    ['click','dblclick','contextmenu'].forEach(type=>{
      modal.addEventListener(type,e=>e.stopPropagation(),false);
    });
    ['pointerdown','pointerup'].forEach(type=>{
      modal.addEventListener(type,()=>{
        interactionLockUntilV193=Date.now()+700;
        clearTimeout(deferredTimerV193);
        deferredTimerV193=setTimeout(flushDeferredV193,720);
      },{passive:true});
    });
  }

  function queueDeferredV193(tables){
    (tables||[]).forEach(t=>deferredTablesV193.add(t));
    clearTimeout(deferredTimerV193);
    deferredTimerV193=setTimeout(flushDeferredV193,900);
  }

  function flushDeferredV193(){
    if(editingSurfaceV193()){
      clearTimeout(deferredTimerV193);
      deferredTimerV193=setTimeout(flushDeferredV193,900);
      return;
    }
    if(!deferredTablesV193.size)return;
    const tables=[...deferredTablesV193];
    deferredTablesV193.clear();

    // Invalidate relevant caches first, then do one coalesced render only
    // after the user is no longer editing.
    try{tables.forEach(t=>invalidateV132?.(t))}catch(_e){}
    try{window.fjzScheduleRenderV125?.()}catch(_e){}
  }

  const baseShouldRenderV193=window.__fjzShouldRenderRealtimeV146;
  window.__fjzShouldRenderRealtimeV146=function(tables){
    if(editingSurfaceV193()){
      queueDeferredV193(tables);
      return false;
    }
    return baseShouldRenderV193?.(tables)??true;
  };

  const baseShowModalV193=window.showModal;
  if(typeof baseShowModalV193==='function'){
    window.showModal=function(){
      const out=baseShowModalV193.apply(this,arguments);
      interactionLockUntilV193=Date.now()+700;
      queueMicrotask(()=>{
        bindModalBoundaryV193();
        syncModalStateV193();
      });
      return out;
    };
    try{showModal=window.showModal}catch(_e){}
  }

  const baseCloseModalV193=window.closeModal;
  if(typeof baseCloseModalV193==='function'){
    window.closeModal=function(){
      const out=baseCloseModalV193.apply(this,arguments);
      interactionLockUntilV193=Date.now()+250;
      syncModalStateV193();
      clearTimeout(deferredTimerV193);
      deferredTimerV193=setTimeout(flushDeferredV193,250);
      return out;
    };
    try{closeModal=window.closeModal}catch(_e){}
  }

  // Keep a short interaction lock around editor taps. This prevents a
  // realtime event landing in the exact same frame as a tap from replacing
  // the DOM the user is interacting with.
  document.addEventListener('pointerdown',e=>{
    const target=e.target?.closest?.('#modal,.modal,.routine-editor,.exercise-card,.session-card,input,select,textarea,button');
    if(!target)return;
    interactionLockUntilV193=Date.now()+650;
    clearTimeout(deferredTimerV193);
    deferredTimerV193=setTimeout(flushDeferredV193,670);
  },{capture:true,passive:true});

  bindModalBoundaryV193();
  syncModalStateV193();

  window.__fjzInteractionHealthV193=function(){
    return {
      modalVisible:modalVisibleV193(),
      editing:editingSurfaceV193(),
      interactionLockMs:Math.max(0,interactionLockUntilV193-Date.now()),
      deferredTables:[...deferredTablesV193]
    };
  };

  window.__fjzV193={
    version:VERSION,
    modalRealtimeLock:true,
    internalModalClickBoundary:true,
    shortTapRenderLock:true,
    deferredRealtimeFlush:true,
    interactionHealthProbe:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "modalRealtimeLock:true",
  "internalModalClickBoundary:true",
  "shortTapRenderLock:true",
  "deferredRealtimeFlush:true",
  "interactionHealthProbe:true"
]:
    if marker not in html:
        raise RuntimeError("V19.3 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V19.3 interaction persistence enabled")
