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
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

def edit_script(doc,script_id,transform):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.79 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.79 no changes in "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-smart-alerts-progress" content="20.78"',
    'meta name="fjz-final-save-geometry" content="20.77"',
    'id="v278SmartAlertsProgressRuntime"',
    "duplicateAsyncSaveGuard:true",
    "specificProgressAlerts:true",
    "noExtraTimers:true",
    "noExtraListeners:true",
]:
    if marker not in html:
        raise RuntimeError("V20.79 prerequisite missing "+marker)

# Final render/lag pass inside the V20.78 authority. Avoid rebuilding a heavy
# progress card a second time when both tracking and smart cloud context are
# already fresh.
def patch_v278(body):
    old_progress=r"""  async function hydrateSmartProgressV278(){
    renderSmartProgressV278();
    const aid=typeof trackingAthleteId==='function'?trackingAthleteId():null;
    if(cloudEnabled&&supabaseClient&&aid&&trackingLoadedFor!==aid&&!smartTrackingPromiseV278){
      smartTrackingPromiseV278=Promise.resolve(loadTracking(false)).then(()=>{
        smartTrackingPromiseV278=null;
        return currentProfile?.role==='coach'?loadSmartCloudDataV278(false):null;
      }).then(()=>{
        const stillCoach=mode==='coach'&&coachTab==='student'&&coachStudentTab==='progress';
        const stillStudent=mode==='student'&&studentTab==='progress';
        if(stillCoach||stillStudent)renderSmartProgressV278();
      }).catch(()=>{smartTrackingPromiseV278=null});
    }else if(currentProfile?.role==='coach'&&cloudEnabled){
      loadSmartCloudDataV278(false).then(()=>renderSmartProgressV278()).catch(()=>{});
    }
  }"""
    new_progress=r"""  async function hydrateSmartProgressV278(){
    renderSmartProgressV278();
    const aid=typeof trackingAthleteId==='function'?trackingAthleteId():null;
    const needsTracking=!!(cloudEnabled&&supabaseClient&&aid&&trackingLoadedFor!==aid);
    const needsSmartCloud=!!(currentProfile?.role==='coach'&&cloudEnabled&&supabaseClient&&Date.now()-Number(smartCloudCacheV278.at||0)>=60000);
    if(!needsTracking&&!needsSmartCloud)return;
    if(smartTrackingPromiseV278)return smartTrackingPromiseV278;
    smartTrackingPromiseV278=(async()=>{
      if(needsTracking)await loadTracking(false);
      if(needsSmartCloud)await loadSmartCloudDataV278(false);
      const stillCoach=mode==='coach'&&coachTab==='student'&&coachStudentTab==='progress';
      const stillStudent=mode==='student'&&studentTab==='progress';
      if(stillCoach||stillStudent)renderSmartProgressV278();
    })().catch(e=>console.warn('TEAM FJZ V20.79 progress hydrate',e)).finally(()=>{
      smartTrackingPromiseV278=null;
    });
    return smartTrackingPromiseV278;
  }"""
    if old_progress not in body:
        raise RuntimeError("V20.79 progress hydrate anchor missing")
    body=body.replace(old_progress,new_progress,1)

    old_intel=r"""  async function hydrateAthleteIntelV278(){
    renderAthleteIntelV278();
    if(!cloudEnabled||!supabaseClient)return;
    const aid=typeof trackingAthleteId==='function'?trackingAthleteId():null;
    const jobs=[loadSmartCloudDataV278(false)];
    if(aid&&trackingLoadedFor!==aid)jobs.push(loadTracking(false));
    Promise.allSettled(jobs).then(()=>{
      if(mode==='coach'&&coachTab==='student'&&coachStudentTab==='summary')renderAthleteIntelV278();
    });
  }"""
    new_intel=r"""  let athleteIntelInflightV279=null;
  async function hydrateAthleteIntelV278(){
    renderAthleteIntelV278();
    if(!cloudEnabled||!supabaseClient)return;
    const aid=typeof trackingAthleteId==='function'?trackingAthleteId():null;
    const jobs=[];
    if(Date.now()-Number(smartCloudCacheV278.at||0)>=60000)jobs.push(loadSmartCloudDataV278(false));
    if(aid&&trackingLoadedFor!==aid)jobs.push(loadTracking(false));
    if(!jobs.length)return;
    if(athleteIntelInflightV279)return athleteIntelInflightV279;
    athleteIntelInflightV279=Promise.allSettled(jobs).then(()=>{
      if(mode==='coach'&&coachTab==='student'&&coachStudentTab==='summary')renderAthleteIntelV278();
    }).finally(()=>{athleteIntelInflightV279=null});
    return athleteIntelInflightV279;
  }"""
    if old_intel not in body:
        raise RuntimeError("V20.79 athlete intel hydrate anchor missing")
    body=body.replace(old_intel,new_intel,1)

    # Preserve SVG proportions so text/circles do not visually stretch on
    # narrow mobile cards.
    body=body.replace('preserveAspectRatio="none"','preserveAspectRatio="xMidYMid meet"')
    return body

html=edit_script(html,"v278SmartAlertsProgressRuntime",patch_v278)

# Filter/search changes must reuse the feed cache. The explicit Actualizar
# action remains the only force-refresh path.
v80_start=html.find("async function hydrateCoachDashboardV80(){")
v80_end=html.find("\nfunction renderCoachDashboardV80(){",v80_start)
if v80_start<0 or v80_end<0:
    raise RuntimeError("V20.79 V80 hydrate bounds missing")
v80=html[v80_start:v80_end]
if "const feed=await loadCoachFeed(true);" not in v80:
    raise RuntimeError("V20.79 force-feed anchor missing")
v80=v80.replace("const feed=await loadCoachFeed(true);","const feed=await loadCoachFeed(false);",1)
html=html[:v80_start]+v80+html[v80_end:]

old_refresh='onclick="hydrateCoachDashboardV80()">Actualizar</button>'
if old_refresh not in html:
    raise RuntimeError("V20.79 dashboard refresh button anchor missing")
html=html.replace(old_refresh,'onclick="forceCoachAlertsV279()">Actualizar</button>',1)

css=r"""
/* =========================================================
   TEAM FJZ · V20.79 FINAL STABILITY / MOBILE POLISH
   ========================================================= */
:where(#view,#coachStudentBody,#studentSubBody,
       .v278-dashboard-card,.v278-dashboard-smart,.v278-dashboard-smart-list,
       .v278-progress,.v278-performance,.v278-adherence,
       .v278-chart-shell,.v278-controls,.v278-weight-kpis,.v278-perf-kpis,
       .v278-intel-grid,.v278-mini-alerts,
       .v80-attention,.v80-attention-item,.v252-priority-card,.v259-calendar-card){
  min-width:0;
  max-width:100%;
  box-sizing:border-box;
}
:where(#view,#coachStudentBody,#studentSubBody,
       .v278-dashboard-card,.v278-progress,.v278-chart-shell){
  overflow-x:clip;
}
.v278-chart-shell{
  contain:layout paint;
}
.v278-chart{
  width:100%;
  max-width:100%;
  min-width:0;
  min-height:0!important;
  height:auto!important;
  touch-action:pan-y;
}
.v278-controls :where(label,select,.input),
.v278-dashboard-alert,
.v278-mini-alert,
.v80-attention-item,
.v80-attention-actions,
.v96-alert-actions{
  min-width:0;
  max-width:100%;
  box-sizing:border-box;
}
.v278-dashboard-alert :where(strong,p,span),
.v278-mini-alert :where(strong,small),
.v80-attention-item :where(h4,p,strong,span),
.v278-alert-detail :where(strong,span){
  overflow-wrap:anywhere;
}
.v278-dashboard-alert-stats,
.v278-alert-delta{
  min-width:0;
}
.v278-dashboard-alert-stats>*,
.v278-alert-delta>*{
  min-width:0;
  overflow:hidden;
}
.v278-controls select{
  text-overflow:ellipsis;
}
.v278-chart-legend{
  max-width:100%;
  overflow-wrap:anywhere;
}
.v278-dashboard-card .section-title,
.v278-progress .section-title,
.v80-attention-head{
  min-width:0;
}
.v278-dashboard-card .section-title>*,
.v278-progress .section-title>*,
.v80-attention-head>*{
  min-width:0;
}
@media(max-width:430px){
  .v278-dashboard-alert-top,
  .v80-attention-head{
    display:grid!important;
    grid-template-columns:minmax(0,1fr);
    gap:6px!important;
  }
  .v278-dashboard-alert-top>span,
  .v80-attention-head>.badge{
    justify-self:start;
  }
  .v278-dashboard-alert-stats,
  .v278-alert-delta{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
  }
  .v278-dashboard-alert-stats>*:last-child,
  .v278-alert-delta>*:last-child{
    grid-column:1/-1;
  }
  .v278-chart-shell{
    padding:7px!important;
  }
  .v278-chart-legend{
    gap:6px 9px!important;
  }
  .v278-controls select{
    width:100%!important;
    max-width:100%!important;
  }
  .v80-attention-actions,
  .v96-alert-actions{
    display:grid!important;
    grid-template-columns:repeat(2,minmax(0,1fr));
    width:100%;
    gap:6px!important;
  }
  .v80-attention-actions>.btn,
  .v96-alert-actions>.btn{
    width:100%;
    min-width:0;
  }
}
@media(max-width:360px){
  .v278-dashboard-alert-stats,
  .v278-alert-delta,
  .v80-attention-actions,
  .v96-alert-actions{
    grid-template-columns:1fr!important;
  }
  .v278-dashboard-alert-stats>*:last-child,
  .v278-alert-delta>*:last-child{
    grid-column:auto;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.79 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

runtime=r"""
<script id="v279FinalStabilityRuntime">
(function(){
  const originalFeedV279=window.loadCoachFeed;
  let feedInflightV279=null;
  let attentionInflightV279=null;

  if(typeof originalFeedV279==='function'){
    window.loadCoachFeed=function(force=false){
      if(feedInflightV279&&!force)return feedInflightV279;
      const run=async()=>{
        if(feedInflightV279&&force){
          try{await feedInflightV279}catch(_e){}
        }
        return originalFeedV279.call(this,force);
      };
      const p=Promise.resolve(run()).finally(()=>{
        if(feedInflightV279===p)feedInflightV279=null;
      });
      feedInflightV279=p;
      return p;
    };
    try{loadCoachFeed=window.loadCoachFeed}catch(_e){}
  }

  const originalHydrateV279=window.hydrateCoachDashboardV80||
    (typeof hydrateCoachDashboardV80==='function'?hydrateCoachDashboardV80:null);
  if(typeof originalHydrateV279==='function'){
    window.hydrateCoachDashboardV80=function(){
      if(attentionInflightV279)return attentionInflightV279;
      const args=arguments,ctx=this;
      attentionInflightV279=Promise.resolve(originalHydrateV279.apply(ctx,args)).finally(()=>{
        attentionInflightV279=null;
      });
      return attentionInflightV279;
    };
    try{hydrateCoachDashboardV80=window.hydrateCoachDashboardV80}catch(_e){}
  }

  window.forceCoachAlertsV279=async function(){
    if(currentProfile?.role!=='coach'||coachTab!=='dashboard')return;
    try{
      coachFeedLoadedAt=0;
      await window.loadCoachFeed(true);
    }catch(e){
      console.warn('TEAM FJZ V20.79 force alerts refresh',e);
    }
    return window.hydrateCoachDashboardV80?.();
  };

  window.__fjzV279={
    version:'20.79',
    finalStabilityOnly:true,
    productionUntouched:true,
    feedRequestCoalescing:true,
    dashboardHydrateCoalescing:true,
    filterUsesCachedFeed:true,
    manualRefreshStillForces:true,
    progressAvoidsRedundantSecondRender:true,
    athleteSummaryAvoidsRedundantSecondRender:true,
    svgAspectPreserved:true,
    mobileOverflowClip:true,
    mobileAlertActionsNormalized:true,
    confirmedSaveAuthorityPreserved:true,
    noExtraTimers:true,
    noExtraListeners:true,
    noExtraObservers:true
  };
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-final-stability-polish" content="20.79">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.79 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-final-stability-polish" content="20.79"',
    "feedRequestCoalescing:true",
    "dashboardHydrateCoalescing:true",
    "filterUsesCachedFeed:true",
    "manualRefreshStillForces:true",
    "progressAvoidsRedundantSecondRender:true",
    "athleteSummaryAvoidsRedundantSecondRender:true",
    "svgAspectPreserved:true",
    "mobileOverflowClip:true",
    "mobileAlertActionsNormalized:true",
    "confirmedSaveAuthorityPreserved:true",
    "forceCoachAlertsV279",
    'preserveAspectRatio="xMidYMid meet"',
]:
    if marker not in html:
        raise RuntimeError("V20.79 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.79 final stability polish")
print("V20.79 BEFORE:",before)
print("V20.79 AFTER:",after)
print("V20.79 feed/render coalescing + chart/mobile overflow polish; save authority preserved")
