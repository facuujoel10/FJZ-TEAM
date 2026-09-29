import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v158FluidNavigationStyles">
html{scroll-behavior:auto!important}
#view{
  min-height:calc(100dvh - 150px);
  overflow-anchor:none!important
}
#coachStudentBody,#studentSubBody,#v81CoachAgendaBody{
  overflow-anchor:none!important
}
body.v158-rendering #view,
body.v158-rendering #view *{
  animation:none!important;
  transition:none!important
}
body.v158-rendering #view{
  min-height:var(--v158-stable-height,calc(100dvh - 150px))!important
}
#v80AttentionBody{min-height:92px}
#v80Student360Loading{min-height:172px}
@media(max-width:900px){
  .topbar,.bottom-nav{
    -webkit-backdrop-filter:none!important;
    backdrop-filter:none!important;
    background:rgba(8,8,9,.985)!important
  }
  .card,.hero,.metric,.student-row,.exercise-row,.day-card,.option-card{
    box-shadow:none!important
  }
  #view{min-height:calc(100dvh - 128px)}
  body.v158-rendering #view{
    min-height:var(--v158-stable-height,calc(100dvh - 128px))!important
  }
}
</style>
"""

js=r"""
<script id="v158FluidNavigationRuntime">
(function(){
  const VERSION='15.8';
  let renderSeq=0;
  let settleTimer=0;
  let lastRoute='';
  const stats={
    version:VERSION,
    renderCount:0,
    lastRenderMs:0,
    maxRenderMs:0,
    cacheHits:{tracking:0,nutrition:0,agenda:0,feed:0,feedback:0},
    layoutShift:0,
    lastRoute:null
  };

  function routeKeyV158(){
    return [
      String(mode||''),
      String(coachTab||''),
      String(coachStudentTab||''),
      String(studentTab||''),
      String(state?.selectedStudentId||'')
    ].join('|');
  }

  function visibleLoadingV158(){
    const root=el('view');
    if(!root)return false;
    return [...root.querySelectorAll('.empty')].some(x=>{
      const t=(x.textContent||'').trim();
      return /^(Cargando|Armando|Preparando|Comprobando)/i.test(t);
    });
  }

  function releaseRenderV158(seq,attempt=0){
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
  }

  // Cache-first navigation. Realtime already invalidates these caches whenever
  // the underlying table changes, so this avoids duplicate requests without
  // making the UI stale.
  if(typeof loadTracking==='function'){
    const baseLoadTrackingV158=loadTracking;
    loadTracking=async function(force=false){
      const athleteId=trackingAthleteId?.();
      const valid=!!athleteId&&trackingLoadedFor===athleteId;
      if(force&&valid&&window.__fjzRenderSettleV158){
        force=false;
        stats.cacheHits.tracking++;
      }
      return baseLoadTrackingV158.call(this,force);
    };
  }

  if(typeof loadNutrition==='function'){
    const baseLoadNutritionV158=loadNutrition;
    loadNutrition=async function(force=false,date=null){
      const athleteId=nutritionAthleteId?.();
      const wantedDate=date||nutritionCache?.date||dateInputToday();
      const valid=!!athleteId&&
        nutritionLoadedAthlete===athleteId&&
        nutritionFoodsLoaded===true&&
        nutritionCache?.date===wantedDate;
      if(force&&valid&&window.__fjzRenderSettleV158){
        force=false;
        stats.cacheHits.nutrition++;
      }
      return baseLoadNutritionV158.call(this,force,date);
    };
  }

  if(typeof loadAgendaV81==='function'){
    const baseLoadAgendaV158=loadAgendaV81;
    loadAgendaV81=async function(force=false){
      if(force&&agendaLoadedV81===true&&window.__fjzRenderSettleV158){
        force=false;
        stats.cacheHits.agenda++;
      }
      return baseLoadAgendaV158.call(this,force);
    };
  }

  if(typeof loadCoachFeed==='function'){
    const baseLoadCoachFeedV158=loadCoachFeed;
    loadCoachFeed=async function(force=false){
      const fresh=Date.now()-Number(coachFeedLoadedAt||0)<15000;
      if(force&&fresh&&window.__fjzRenderSettleV158){
        force=false;
        stats.cacheHits.feed++;
      }
      return baseLoadCoachFeedV158.call(this,force);
    };
  }

  if(typeof loadExerciseFeedbackV73==='function'){
    const baseLoadFeedbackV158=loadExerciseFeedbackV73;
    loadExerciseFeedbackV73=async function(force=false){
      try{
        const athleteId=currentAthleteIdV73?.();
        const key=athleteId?feedbackKeyV73(athleteId):'local';
        const valid=exerciseFeedbackCacheV73?.has?.(key);
        if(force&&valid&&window.__fjzRenderSettleV158){
          force=false;
          stats.cacheHits.feedback++;
        }
      }catch(e){}
      return baseLoadFeedbackV158.call(this,force);
    };
  }

  // One visual transaction per navigation. The previous viewport height is
  // briefly reserved while async sections settle, avoiding collapse/expand warp.
  const baseRenderV158=render;
  render=function(){
    const seq=++renderSeq;
    const started=performance.now();
    const v=el('view');
    const viewportH=Math.max(320,window.visualViewport?.height||window.innerHeight||720);
    const oldH=v?.getBoundingClientRect?.().height||0;
    const stableH=Math.max(
      Math.min(oldH,viewportH*1.12),
      viewportH*(window.innerWidth<=900?.58:.62)
    );

    if(v&&Number.isFinite(stableH)&&stableH>0){
      v.style.setProperty('--v158-stable-height',Math.round(stableH)+'px');
    }
    document.body?.classList.add('v158-rendering');
    window.__fjzRenderSettleV158=true;

    const route=routeKeyV158();
    const changed=route!==lastRoute;
    lastRoute=route;

    let out;
    try{
      out=baseRenderV158.apply(this,arguments);
    }finally{
      const ms=Math.round((performance.now()-started)*10)/10;
      stats.renderCount++;
      stats.lastRenderMs=ms;
      stats.maxRenderMs=Math.max(stats.maxRenderMs,ms);
      stats.lastRoute=route;
      stats.lastNavigationChanged=changed;
      requestAnimationFrame(()=>requestAnimationFrame(()=>releaseRenderV158(seq,0)));
    }
    return out;
  };

  // If a background scheduled render happens, still use the stabilized wrapper.
  // V15.6 already defers these while a field is being edited.
  if('PerformanceObserver' in window){
    try{
      const po=new PerformanceObserver(list=>{
        for(const e of list.getEntries()){
          if(e.entryType==='layout-shift'&&!e.hadRecentInput){
            stats.layoutShift=Math.round((stats.layoutShift+Number(e.value||0))*10000)/10000;
          }
        }
      });
      po.observe({type:'layout-shift',buffered:true});
    }catch(e){}
  }

  window.__fjzFluidityV158=stats;
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzFluidityV158",
  "cacheHits:{tracking:0,nutrition:0,agenda:0,feed:0,feedback:0}",
  "window.__fjzRenderSettleV158=true",
  "v158-rendering",
  "layout-shift"
]:
    if marker not in html:
        raise RuntimeError("V15.8 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V15.8 fluid navigation/render stability enabled")
