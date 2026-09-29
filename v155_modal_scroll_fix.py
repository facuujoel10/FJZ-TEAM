import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v155ModalScrollFixStyles">
/* General modal stability. The overlay can scroll when the viewport is short. */
.modal-wrap.v155-scroll-shell{
  overscroll-behavior:contain;
  -webkit-overflow-scrolling:touch;
}
.modal.v155-exercise-modal .v155-exercise-save{
  position:sticky;
  bottom:0;
  z-index:8;
  margin-top:14px!important;
  padding-top:12px!important;
  padding-bottom:12px!important;
  box-shadow:0 -12px 24px rgba(15,15,18,.92);
}

/* iPhone / Android / installed PWA: avoid nested-scroll traps and browser HUD clipping. */
@media(max-width:760px){
  .modal-wrap.v155-scroll-shell{
    align-items:flex-start!important;
    justify-content:center!important;
    overflow-y:auto!important;
    overflow-x:hidden!important;
    height:100dvh!important;
    max-height:100dvh!important;
    padding:
      max(10px,env(safe-area-inset-top))
      9px
      max(88px,calc(26px + env(safe-area-inset-bottom)))!important;
    box-sizing:border-box!important;
    touch-action:pan-y!important;
  }
  .modal-wrap.v155-scroll-shell>.modal{
    width:100%!important;
    max-height:none!important;
    min-height:0!important;
    overflow:visible!important;
    margin:0 auto!important;
    border-radius:16px!important;
    padding-bottom:max(20px,env(safe-area-inset-bottom))!important;
    box-sizing:border-box!important;
    touch-action:pan-y!important;
  }
  .modal.v155-exercise-modal .modal-head{
    position:sticky;
    top:0;
    z-index:9;
    margin:-1px -1px 12px!important;
    padding:8px 1px 10px!important;
    background:linear-gradient(180deg,#0f0f12 80%,rgba(15,15,18,.88));
  }
  .modal.v155-exercise-modal .v155-exercise-save{
    bottom:max(0px,env(safe-area-inset-bottom));
    background:#0f0f12;
  }
  .modal.v155-library-modal .library{
    max-height:none!important;
    overflow:visible!important;
  }
}

/* Short screens in landscape also need overlay scrolling. */
@media(max-height:650px){
  .modal-wrap.v155-scroll-shell{
    align-items:flex-start!important;
    overflow-y:auto!important;
    padding-top:8px!important;
    padding-bottom:32px!important;
  }
  .modal-wrap.v155-scroll-shell>.modal{
    max-height:none!important;
    overflow:visible!important;
  }
}
</style>
"""

js=r"""
<script id="v155ModalScrollFixRuntime">
(function(){
  const VERSION='15.5';

  function prepareModalScrollV155(kind){
    const wrap=el('modalWrap'),modal=el('modal');
    if(!wrap||!modal)return;
    wrap.classList.add('v155-scroll-shell');
    modal.classList.remove('v155-exercise-modal','v155-library-modal');
    if(kind==='exercise')modal.classList.add('v155-exercise-modal');
    if(kind==='library')modal.classList.add('v155-library-modal');

    // Always open a fresh modal at the top. iOS can otherwise preserve a stale nested scroll offset.
    requestAnimationFrame(()=>{
      try{wrap.scrollTop=0}catch(e){}
      try{modal.scrollTop=0}catch(e){}
    });
  }

  const baseShowModalV155=showModal;
  showModal=function(html){
    const out=baseShowModalV155.apply(this,arguments);
    prepareModalScrollV155('');
    return out;
  };

  const baseCloseModalV155=closeModal;
  closeModal=function(){
    const wrap=el('modalWrap'),modal=el('modal');
    const out=baseCloseModalV155.apply(this,arguments);
    wrap?.classList.remove('v155-scroll-shell');
    modal?.classList.remove('v155-exercise-modal','v155-library-modal');
    return out;
  };

  const baseOpenLibraryV155=openLibrary;
  openLibrary=function(){
    const out=baseOpenLibraryV155.apply(this,arguments);
    prepareModalScrollV155('library');
    return out;
  };

  const baseShowExerciseFormV155=showExerciseForm;
  showExerciseForm=function(){
    const out=baseShowExerciseFormV155.apply(this,arguments);
    prepareModalScrollV155('exercise');
    const modal=el('modal');
    const save=[...(modal?.querySelectorAll('button')||[])].find(btn=>{
      const oc=btn.getAttribute('onclick')||'';
      return oc.includes('saveExercise(')||(btn.textContent||'').trim()==='Guardar ejercicio';
    });
    if(save){
      save.classList.add('v155-exercise-save');
      save.setAttribute('data-v155-save','1');
    }
    return out;
  };

  // If the visual viewport changes because the iPhone HUD/keyboard opens,
  // keep the currently visible modal scrollable instead of freezing its height.
  if(window.visualViewport&&!window.__fjzV155ViewportBound){
    window.__fjzV155ViewportBound=true;
    let raf=0;
    const sync=()=>{
      cancelAnimationFrame(raf);
      raf=requestAnimationFrame(()=>{
        const wrap=el('modalWrap');
        if(!wrap||getComputedStyle(wrap).display==='none')return;
        wrap.style.setProperty('--v155-vh',Math.round(window.visualViewport.height)+'px');
      });
    };
    window.visualViewport.addEventListener('resize',sync,{passive:true});
    window.visualViewport.addEventListener('scroll',sync,{passive:true});
  }

  window.__fjzModalScrollV155={
    version:VERSION,
    mobileOverlayScroll:true,
    exerciseSaveSticky:true,
    libraryFullScroll:true,
    safeAreaAware:true,
    visualViewportAware:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzModalScrollV155",
  "mobileOverlayScroll:true",
  "exerciseSaveSticky:true",
  "libraryFullScroll:true",
  "safeAreaAware:true",
  "visualViewportAware:true",
  "v155-exercise-save"
]:
    if marker not in html:
        raise RuntimeError("V15.5 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V15.5 mobile modal / exercise scroll fix enabled")
