import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V18.0 MOBILE VISUAL STABILITY + CANONICAL SCROLL
# =========================================================

# 1) V15.8: keep its cache-first logic/statistics, but disable the visual
# height reservation and long settle loop on mobile.
old_release=r"""  function releaseRenderV158(seq,attempt=0){
    if(seq!==renderSeq)return;
    if(visibleLoadingV158()&&attempt<12){
      clearTimeout(settleTimer);
      settleTimer=setTimeout(()=>releaseRenderV158(seq,attempt+1),80);
      return;
    }
    window.__fjzRenderSettleV158=false;
    document.body?.classList.remove('v158-rendering');
    const v=el('view');
    if(v){
      v.style.removeProperty('--v158-stable-height');
    }
  }"""
new_release=r"""  function releaseRenderV158(seq,attempt=0){
    if(seq!==renderSeq)return;
    const mobile=window.matchMedia?.('(max-width:900px)')?.matches??window.innerWidth<=900;
    if(!mobile&&visibleLoadingV158()&&attempt<12){
      clearTimeout(settleTimer);
      settleTimer=setTimeout(()=>releaseRenderV158(seq,attempt+1),80);
      return;
    }
    window.__fjzRenderSettleV158=false;
    document.body?.classList.remove('v158-rendering');
    const v=el('view');
    if(v)v.style.removeProperty('--v158-stable-height');
  }"""
if html.count(old_release)!=1:
    raise RuntimeError("V18.0 could not locate V15.8 release loop")
html=html.replace(old_release,new_release,1)

old_visual=r"""    const viewportH=Math.max(320,window.visualViewport?.height||window.innerHeight||720);
    const oldH=v?.getBoundingClientRect?.().height||0;
    const stableH=Math.max(
      Math.min(oldH,viewportH*1.12),
      viewportH*(window.innerWidth<=900?.58:.62)
    );

    if(v&&Number.isFinite(stableH)&&stableH>0){
      v.style.setProperty('--v158-stable-height',Math.round(stableH)+'px');
    }
    document.body?.classList.add('v158-rendering');
    window.__fjzRenderSettleV158=true;"""
new_visual=r"""    const mobile=window.matchMedia?.('(max-width:900px)')?.matches??window.innerWidth<=900;
    if(!mobile){
      const viewportH=Math.max(320,window.innerHeight||720);
      const oldH=v?.getBoundingClientRect?.().height||0;
      const stableH=Math.max(
        Math.min(oldH,viewportH*1.12),
        viewportH*.62
      );
      if(v&&Number.isFinite(stableH)&&stableH>0){
        v.style.setProperty('--v158-stable-height',Math.round(stableH)+'px');
      }
      document.body?.classList.add('v158-rendering');
    }else{
      document.body?.classList.remove('v158-rendering');
      v?.style?.removeProperty('--v158-stable-height');
    }
    window.__fjzRenderSettleV158=true;"""
if html.count(old_visual)!=1:
    raise RuntimeError("V18.0 could not locate V15.8 viewport stabilizer")
html=html.replace(old_visual,new_visual,1)

# 2) V17.6: remove delayed routine re-scrolls. Global route scroll below
# becomes the single authority for navigation position.
old_routine=r"""  function scheduleRoutineTopV176(){
    const token=++routineScrollTokenV176;
    const entryAt=performance.now();
    requestAnimationFrame(()=>resetRoutineScrollV176(token,entryAt));
    [260,850].forEach(ms=>setTimeout(()=>{
      if(lastUserInteractionV176>entryAt)return;
      resetRoutineScrollV176(token,entryAt);
    },ms));
  }"""
new_routine=r"""  function scheduleRoutineTopV176(){
    routineScrollTokenV176++;
  }"""
if html.count(old_routine)!=1:
    raise RuntimeError("V18.0 could not locate V17.6 delayed routine scroll")
html=html.replace(old_routine,new_routine,1)

css=r"""
<style id="v180VisualStabilityStyles">
html{
  scroll-behavior:auto!important;
  overflow-anchor:none!important;
}
body,#view,#coachStudentBody,#studentSubBody{
  overflow-anchor:none!important;
}

@media(max-width:900px){
  /* No artificial render height on mobile. Content uses its natural height. */
  #view,
  body.v158-rendering #view,
  #coachStudentBody,
  #studentSubBody{
    min-height:0!important;
  }

  body.v158-rendering #view{
    --v158-stable-height:auto!important;
  }

  /* Expensive compositing effects are unnecessary on phone and can stutter
     during long pages / scrolling. */
  .topbar,.bottom-nav{
    backdrop-filter:none!important;
    -webkit-backdrop-filter:none!important;
  }

  .card,.hero,.student-row,.exercise-row,.day-card,.track-row,.history-item{
    will-change:auto!important;
    transform:none;
  }

  /* Never animate geometry during app navigation. */
  #view,
  #view *{
    scroll-margin-top:0;
  }

  body.v180-navigating #view *,
  body.v180-navigating #view{
    animation:none!important;
    transition-property:color,background-color,border-color,opacity!important;
  }
}
</style>
"""

js=r"""
<script id="v180VisualStabilityRuntime">
(function(){
  const VERSION='18.0';
  let lastRouteV180='';
  let navSeqV180=0;
  let scrollRafV180=0;

  try{
    if('scrollRestoration' in history)history.scrollRestoration='manual';
  }catch(_e){}

  function routeKeyV180(){
    return [
      currentProfile?.role||'',
      mode||'',
      coachTab||'',
      coachStudentTab||'',
      studentTab||'',
      state?.selectedStudentId||''
    ].join('|');
  }

  function hardTopV180(){
    const se=document.scrollingElement||document.documentElement;
    if(se)se.scrollTop=0;
    if(document.documentElement)document.documentElement.scrollTop=0;
    if(document.body)document.body.scrollTop=0;
    window.scrollTo(0,0);

    // Some app shells may become their own scroller at small breakpoints.
    ['view','coachStudentBody','studentSubBody'].forEach(id=>{
      const x=document.getElementById(id);
      if(x&&x.scrollTop>0)x.scrollTop=0;
    });
  }

  function scheduleRouteTopV180(seq){
    cancelAnimationFrame(scrollRafV180);
    scrollRafV180=requestAnimationFrame(()=>{
      if(seq!==navSeqV180)return;
      hardTopV180();
      requestAnimationFrame(()=>{
        if(seq!==navSeqV180)return;
        hardTopV180();
        document.body?.classList.remove('v180-navigating');
      });
    });
  }

  // Add only one final wrapper. It does not mutate page contents; it only
  // normalizes scroll when the logical route really changed.
  const baseRenderV180=window.render||render;
  if(typeof baseRenderV180==='function'){
    window.render=function(){
      const before=routeKeyV180();
      const changed=before!==lastRouteV180;
      if(changed){
        navSeqV180++;
        document.body?.classList.add('v180-navigating');
      }

      const out=baseRenderV180.apply(this,arguments);
      const after=routeKeyV180();

      if(after!==lastRouteV180){
        lastRouteV180=after;
        const seq=navSeqV180;
        scheduleRouteTopV180(seq);
      }else if(changed){
        document.body?.classList.remove('v180-navigating');
      }
      return out;
    };
    try{render=window.render}catch(_e){}
  }

  // Opening a student from a previously scrolled dashboard can preserve the
  // browser's old scroll before render runs. Catch student selection itself.
  document.addEventListener('click',e=>{
    const row=e.target?.closest?.('.student-row,[data-client-id]');
    if(!row)return;
    requestAnimationFrame(hardTopV180);
  },{capture:true,passive:true});

  window.__fjzV180={
    version:VERSION,
    mobileDynamicHeightDisabled:true,
    delayedRoutineScrollRemoved:true,
    routeScrollAuthority:true,
    scrollRestorationManual:true,
    doubleRafTopReset:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "v180VisualStabilityStyles",
  "__fjzV180",
  "mobileDynamicHeightDisabled:true",
  "delayedRoutineScrollRemoved:true",
  "routeScrollAuthority:true",
  "scrollRestoration='manual'"
]:
    if marker not in html:
        raise RuntimeError("V18.0 missing marker: "+marker)

# Assert the problematic delayed routine scroll no longer exists.
if "[260,850].forEach" in html:
    raise RuntimeError("V18.0 delayed routine scroll still present")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V18.0 visual stability/navigation enabled",{
  "v158_mobile_dynamic_height":"disabled",
  "v176_delayed_scroll":"removed",
  "route_scroll":"canonical_top",
})
