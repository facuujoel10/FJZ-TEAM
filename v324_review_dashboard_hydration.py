import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":doc.lower().count("<style"),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":doc.count(".channel("),
        "timeouts":doc.count("setTimeout("),
        "intervals":doc.count("setInterval("),
        "listeners":doc.count("addEventListener("),
        "mutation_observers":doc.count("new MutationObserver"),
        "performance_observers":doc.count("new PerformanceObserver"),
    }

def edit_script(doc,sid,fn):
    mid=-1
    for marker in ('id="'+sid+'"',"id='"+sid+"'"):
        mid=doc.find(marker)
        if mid>=0: break
    if mid<0: raise RuntimeError("V21.24 missing script "+sid)
    a=doc.find(">",mid); b=doc.find("</script>",a)
    if a<0 or b<0: raise RuntimeError("V21.24 malformed script "+sid)
    body=doc[a+1:b]
    body=fn(body)
    return doc[:a+1]+body+doc[b:]

before=metrics(html)

for marker in [
    'meta name="fjz-review-alert-identity" content="21.23"',
    'id="v302ReviewResolutionAuthorityRuntime"',
    "reviewFeedUsesAthleteKeyV308:true",
    "serverFeedRequiredForReviewCardsV322:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.24 prerequisite missing "+marker)

def patch_v302(body):
    old="""    if(cloudRuntime&&window.__fjzCoachFeedReadyV322!==true)return false;"""
    new="""    if(cloudRuntime&&window.__fjzCanonicalCoachFeedReadyV324!==true)return false;"""
    if body.count(old)!=1:
        raise RuntimeError("V21.24 V302 legacy readiness anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    reviewKeysUseStableAthleteIdV323:true,"""
    new="""    reviewKeysUseStableAthleteIdV323:true,
    dashboardHydrationOwnsReviewReadinessV324:true,
    v96ReadinessNoLongerBlocksReviewCenterV324:true,"""
    if body.count(old)!=1:
        raise RuntimeError("V21.24 V302 flags anchor mismatch")
    body=body.replace(old,new,1)
    return body

html=edit_script(html,"v302ReviewResolutionAuthorityRuntime",patch_v302)

runtime=r"""
<script id="v324ReviewDashboardHydrationRuntime">
(function(){
  window.__fjzCanonicalCoachFeedReadyV324=false;

  function feedAlreadyHydratedV324(){
    try{
      if(Number(coachFeedLoadedAt||0)>0)return true;
    }catch(_e){}
    try{
      if(Array.isArray(coachFeedV235)&&coachFeedV235.length>0)return true;
    }catch(_e){}
    return false;
  }

  function repaintReviewsV324(){
    try{window.renderCoachPriorityCenterV252?.()}catch(_e){}
    try{window.renderCoachFocusV235?.()}catch(_e){}
  }

  const base=window.hydrateCoachDashboardV80||
    (typeof hydrateCoachDashboardV80==='function'?hydrateCoachDashboardV80:null);

  if(typeof base==='function'){
    const wrapped=async function(){
      window.__fjzCanonicalCoachFeedReadyV324=false;
      try{
        const out=await base.apply(this,arguments);
        window.__fjzCanonicalCoachFeedReadyV324=true;
        repaintReviewsV324();
        return out;
      }catch(e){
        window.__fjzCanonicalCoachFeedReadyV324=false;
        throw e;
      }
    };
    window.hydrateCoachDashboardV80=wrapped;
    try{hydrateCoachDashboardV80=wrapped}catch(_e){}
  }

  if(feedAlreadyHydratedV324()){
    window.__fjzCanonicalCoachFeedReadyV324=true;
    repaintReviewsV324();
  }

  window.__fjzV324={
    version:'21.24',
    dashboardHydrationOwnsReviewReadiness:true,
    existingCanonicalFeedCanUnlockImmediately:true,
    repaintAfterDashboardHydration:true,
    noExtraTimers:true,
    noExtraListeners:true,
    noExtraObservers:true
  };
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-review-dashboard-hydration" content="21.24">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V21.24 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-review-dashboard-hydration" content="21.24"',
    'id="v324ReviewDashboardHydrationRuntime"',
    "__fjzCanonicalCoachFeedReadyV324",
    "dashboardHydrationOwnsReviewReadinessV324:true",
    "v96ReadinessNoLongerBlocksReviewCenterV324:true",
    "window.hydrateCoachDashboardV80=wrapped",
    "repaintReviewsV324();",
    "reviewFeedUsesAthleteKeyV308:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.24 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.24 review dashboard hydration authority")
print("V21.24 BEFORE:",before)
print("V21.24 AFTER:",after)
