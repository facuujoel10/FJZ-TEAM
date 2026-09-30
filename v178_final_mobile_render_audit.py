import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V17.8 FINAL MOBILE / RENDER AUDIT
# - one final post-render pass for V17.5/V17.6/V17.7
# - stable mobile viewport
# - symmetric form/card containment
# - no extra observer/timer loop
# =========================================================

# 1) Expose V17.5 final pass and remove its dedicated render wrapper.
old175=r"""  const baseRenderV175=window.render;
  window.render=function(){
    const out=baseRenderV175.apply(this,arguments);
    ensureCoachHeroFrameV175();
    ensureStudentProfilePlaceholderV175();
    if(typeof fjzPostRenderV125==='function')fjzPostRenderV125('v175-final-ui',postRenderV175);
    else requestAnimationFrame(postRenderV175);
    return out;
  };"""
new175=r"""  window.__fjzPostRenderV175=postRenderV175;"""
html,n175=html.replace(old175,new175),html.count(old175)
if n175!=1:
    raise RuntimeError(f"V17.8 expected one V17.5 render wrapper, got {n175}")

# 2) Expose V17.6 final pass/route logic and remove its dedicated render wrapper.
old176=r"""  const baseRenderV176=window.render;
  window.render=function(){
    const next=routeKeyV176();
    const enteringRoutine=routineActiveV176()&&next!==lastRouteV176;
    const out=baseRenderV176.apply(this,arguments);
    lastRouteV176=next;
    if(enteringRoutine)scheduleRoutineTopV176();
    if(typeof fjzPostRenderV125==='function')fjzPostRenderV125('v176-polish',postRenderV176);
    else requestAnimationFrame(postRenderV176);
    return out;
  };
  try{render=window.render}catch(e){}"""
new176=r"""  window.__fjzPostRenderV176=postRenderV176;
  window.__fjzRouteAfterRenderV176=function(){
    const next=routeKeyV176();
    const enteringRoutine=routineActiveV176()&&next!==lastRouteV176;
    lastRouteV176=next;
    if(enteringRoutine)scheduleRoutineTopV176();
  };"""
html,n176=html.replace(old176,new176),html.count(old176)
if n176!=1:
    raise RuntimeError(f"V17.8 expected one V17.6 render wrapper, got {n176}")

# 3) Replace V17.7 dedicated wrapper with one consolidated post-render transaction.
old177=r"""  // One post-render repair frame only. No MutationObserver and no repeating timer.
  if(typeof render==='function'){
    const baseRenderV177=render;
    render=function(){
      const out=baseRenderV177.apply(this,arguments);
      queueRepairV177();
      return out;
    };
  }"""
new177=r"""  // Final consolidated visual transaction: V17.5 + V17.6 + V17.7.
  // All DOM polish runs in one shared RAF batch instead of stacked render wrappers.
  if(typeof render==='function'){
    const baseRenderV178=render;
    render=function(){
      if(window.__fjzRenderBusyV178){
        window.__fjzRenderQueuedV178=true;
        return;
      }
      window.__fjzRenderBusyV178=true;
      let out;
      try{
        out=baseRenderV178.apply(this,arguments);
      }finally{
        window.__fjzRenderBusyV178=false;
      }
      const runFinalPass=()=>{
        try{window.__fjzPostRenderV175?.()}catch(e){console.warn('TEAM FJZ V17.5 final pass',e)}
        try{window.__fjzPostRenderV176?.()}catch(e){console.warn('TEAM FJZ V17.6 final pass',e)}
        try{window.__fjzRouteAfterRenderV176?.()}catch(e){console.warn('TEAM FJZ V17.6 route pass',e)}
        try{repairV177()}catch(e){console.warn('TEAM FJZ V17.7 repair',e)}
        if(window.__fjzRenderQueuedV178){
          window.__fjzRenderQueuedV178=false;
          window.fjzScheduleRenderV125?.();
        }
      };
      if(typeof fjzPostRenderV125==='function')fjzPostRenderV125('v178-final-pass',runFinalPass);
      else requestAnimationFrame(runFinalPass);
      return out;
    };
    try{window.render=render}catch(_e){}
  }"""
html,n177=html.replace(old177,new177),html.count(old177)
if n177!=1:
    raise RuntimeError(f"V17.8 expected one V17.7 render wrapper, got {n177}")

css=r"""
<style id="v178FinalMobileAuditStyles">
*,
*::before,
*::after{box-sizing:border-box}

html,body{
  width:100%!important;
  max-width:100%!important;
  overflow-x:clip!important;
}

#view,#coachStudentBody,#studentSubBody,
.shell,.card,.hero,.grid,.form-grid,.metric-grid,.modal,
.student-row,.exercise-row,.day-card,.history-item,.track-row,
.v165-agenda-shell,.v165-week-row,.nutrition-datebar,.tracking-form{
  min-width:0!important;
  max-width:100%;
  box-sizing:border-box!important;
}

.grid>*,
.form-grid>*,
.metric-grid>*,
.v165-week-row>*,
.nutrition-datebar>*,
.tracking-form>*,
.section-title>*{
  min-width:0!important;
  max-width:100%;
  box-sizing:border-box!important;
}

input,select,textarea,button,.input,.btn{
  box-sizing:border-box!important;
  max-width:100%;
}

input[type="date"],input[type="time"]{
  width:100%!important;
  max-width:100%!important;
  min-width:0!important;
  min-inline-size:0!important;
  overflow:hidden!important;
}

input[type="date"]::-webkit-date-and-time-value,
input[type="time"]::-webkit-date-and-time-value{
  width:100%!important;
  min-width:0!important;
  text-align:left!important;
}

.section-title{
  gap:10px!important;
  align-items:flex-start!important;
}
.section-title>div:first-child{
  flex:1 1 180px;
  min-width:0!important;
}

@media(max-width:900px){
  html,body{
    min-height:100svh!important;
    overscroll-behavior-x:none!important;
  }

  #view,
  body.v158-rendering #view{
    min-height:calc(100svh - 128px)!important;
  }

  #coachStudentBody,#studentSubBody{
    min-height:calc(100svh - 170px)!important;
  }

  body.v158-rendering #view{
    /* Ignore V15.8 dynamic viewport reserve on mobile. */
    --v158-stable-height:calc(100svh - 128px)!important;
  }

  .shell{
    width:100%!important;
    max-width:100%!important;
    padding-left:10px!important;
    padding-right:10px!important;
  }

  .card,.hero{
    width:100%!important;
    border-radius:14px!important;
  }

  .form-grid,.tracking-form .form-grid{
    grid-template-columns:1fr!important;
  }

  .form-grid .span2,
  .tracking-form .span2{
    grid-column:auto!important;
  }

  input,select,textarea,.input{
    width:100%!important;
    min-width:0!important;
  }

  input[type="date"],input[type="time"],
  #ciWeek,#mDate,#progressPhotoDate,#nutritionLogDate,
  #v165Time,#v165Date{
    width:100%!important;
    max-width:100%!important;
    min-width:0!important;
    font-size:16px!important;
  }

  .v165-week-row{
    grid-template-columns:1fr!important;
    gap:9px!important;
  }

  .v176-measure-row{
    grid-template-columns:1fr!important;
    align-items:stretch!important;
  }
  .v176-measure-values{
    grid-column:auto!important;
  }
  .v176-measure-row>.btn{
    width:100%!important;
  }

  .v159-score-card,.track-score{
    min-width:0!important;
  }

  .topbar,.bottom-nav{
    transform:translateZ(0);
    will-change:auto!important;
  }
}

@media(max-width:520px){
  .card{padding:13px!important}
  .hero{padding:13px!important}
  .section-title{flex-direction:column!important}
  .section-title>div,
  .section-title>.btn,
  .section-title>button,
  .section-title>input,
  .section-title>select{
    width:100%;
    max-width:100%!important;
  }
  .pill-row{
    max-width:100%!important;
    flex-wrap:wrap!important;
  }
}

/* During app-driven redraws, never animate layout geometry. */
body.v158-rendering #view,
body.v158-rendering #view *{
  transition-property:color,background-color,border-color,opacity!important;
}
</style>
"""

js=r"""
<script id="v178FinalMobileAuditRuntime">
(function(){
  const VERSION='17.8';

  function auditLayoutV178(){
    const root=document.getElementById('view');
    if(!root)return;
    const vw=document.documentElement.clientWidth||window.innerWidth||0;
    let offenders=0;
    root.querySelectorAll('*').forEach(node=>{
      const r=node.getBoundingClientRect?.();
      if(!r)return;
      if(r.right>vw+3||r.left<-3)offenders++;
    });
    window.__fjzUiAuditV178={
      version:VERSION,
      viewportWidth:vw,
      horizontalOverflowNodes:offenders,
      width:root.getBoundingClientRect?.().width||0,
      at:new Date().toISOString()
    };
  }

  let auditRaf=0;
  function scheduleAuditV178(){
    if(auditRaf)return;
    auditRaf=requestAnimationFrame(()=>{
      auditRaf=0;
      auditLayoutV178();
    });
  }

  window.addEventListener('resize',scheduleAuditV178,{passive:true});
  window.addEventListener('orientationchange',scheduleAuditV178,{passive:true});
  document.addEventListener('visibilitychange',()=>{
    if(document.visibilityState==='visible')scheduleAuditV178();
  });

  scheduleAuditV178();

  window.__fjzV178={
    version:VERSION,
    finalPostRenderConsolidated:true,
    stableMobileViewport:true,
    symmetricMobileForms:true,
    horizontalContainment:true,
    reentrantRenderGuard:true,
    diagnosticOverflowCounter:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

# Build-time audit assertions.
if html.count("v178FinalMobileAuditStyles")!=1:
    raise RuntimeError("V17.8 styles missing/duplicated")
if html.count("v178FinalMobileAuditRuntime")!=1:
    raise RuntimeError("V17.8 runtime missing/duplicated")
for marker in [
  "__fjzPostRenderV175",
  "__fjzPostRenderV176",
  "__fjzRouteAfterRenderV176",
  "v178-final-pass",
  "100svh",
  "__fjzUiAuditV178"
]:
    if marker not in html:
        raise RuntimeError("V17.8 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V17.8 final mobile/render audit:",{
  "v175_wrappers_consolidated":n175,
  "v176_wrappers_consolidated":n176,
  "v177_wrappers_consolidated":n177,
  "render_assignments":len(re.findall(r"(?:window\.)?render\s*=\s*function",html)),
  "mutation_observers":len(re.findall(r"new\s+MutationObserver",html)),
  "timeouts":len(re.findall(r"setTimeout\s*\(",html)),
})
