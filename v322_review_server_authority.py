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
    if mid<0: raise RuntimeError("V21.22 missing script "+sid)
    open_end=doc.find(">",mid); close=doc.find("</script>",open_end)
    if open_end<0 or close<0: raise RuntimeError("V21.22 malformed script "+sid)
    body=doc[open_end+1:close]
    body=fn(body)
    return doc[:open_end+1]+body+doc[close:]

before=metrics(html)

for marker in [
    'meta name="fjz-first-review-geometry-authority" content="21.21"',
    'id="v301ReviewWorkflowProRuntime"',
    'id="v302ReviewResolutionAuthorityRuntime"',
    "stableClientReviewAuthorityV319:true",
    "legacyFirstReviewSuppressedEverywhereV321:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.22 prerequisite missing "+marker)

# 1) The canonical coach feed is asynchronous. Review surfaces must fail closed
# until the server has answered, then immediately repaint from that answer.
feed_anchor="const feed=await loadCoachFeed(true);coachFeedV235=Array.isArray(feed)?feed:[];"
feed_repl="""window.__fjzCoachFeedReadyV322=false;
    const feed=await loadCoachFeed(true);
    coachFeedV235=Array.isArray(feed)?feed:[];
    window.__fjzCoachFeedReadyV322=true;
    window.__fjzCoachFeedLoadedAtV322=Date.now();
    try{window.renderCoachPriorityCenterV252?.()}catch(_e){}
    try{window.renderCoachFocusV235?.()}catch(_e){}"""
if html.count(feed_anchor)!=1:
    raise RuntimeError("V21.22 coach feed hydration anchor mismatch: "+str(html.count(feed_anchor)))
html=html.replace(feed_anchor,feed_repl,1)

# 2) Legacy V301 defense-in-depth: low adherence/inactivity/statusFor are
# priorities, not review cards. A review card needs a real server event,
# pending exercise/session feedback, a genuine review-loop change/due state,
# or a truly never-reviewed profile.
def patch_v301(body):
    old="""  function active(s){
    try{
      const p=coachPriorityStateV252?.(s)||{};
      if(!(p.bucket==='urgent'||p.bucket==='today'))return null;
      if(window.__fjzProfileReviewedStudentV319?.(s?.id)){
        const r=coachReviewLoopStateV238?.(s)||{};
        const hasFeed=(feed(s)||[]).length>0;
        let feedback=0;try{feedback=Number(pendingSessionFeedbackCountV243?.(s)||0)}catch(_e){}
        if(!hasFeed&&!feedback&&!r.changed&&!r.reviewDue)return null;
      }
      return p;
    }catch(_e){return null}
  }"""
    new="""  function active(s){
    try{
      const cloudRuntime=!!(cloudEnabled&&supabaseClient&&!window.__fjzStagingLocal?.enabled);
      if(cloudRuntime&&!window.__fjzFirstReviewAuthorityLoadedV319?.())return null;
      if(cloudRuntime&&window.__fjzCoachFeedReadyV322!==true)return null;
      const r=coachReviewLoopStateV238?.(s)||{};
      const hasFeed=(feed(s)||[]).length>0;
      let feedback=0;try{feedback=Number(pendingSessionFeedbackCountV243?.(s)||0)}catch(_e){}
      const reviewed=!!window.__fjzProfileReviewedStudentV319?.(s?.id);
      const genuine=hasFeed||feedback>0||!!r.changed||!!r.reviewDue||(!reviewed&&!r.hasBaseline);
      if(!genuine)return null;
      const p=coachPriorityStateV252?.(s)||{};
      return p.bucket==='urgent'||p.bucket==='today'?p:{...p,bucket:'today',score:Number(p.score||50)};
    }catch(_e){return null}
  }"""
    if body.count(old)!=1:
        raise RuntimeError("V21.22 V301 active anchor mismatch: "+str(body.count(old)))
    return body.replace(old,new,1)

html=edit_script(html,"v301ReviewWorkflowProRuntime",patch_v301)

# 3) V302 is the final Review Center authority. Enforce the same rule here,
# because this runtime owns the visible center after all legacy layers.
def patch_v302(body):
    old="""  function active(s){try{const p=coachPriorityStateV252?.(s)||{};return p.bucket==='urgent'||p.bucket==='today'?p:null}catch(_e){return null}}"""
    new="""  function realReviewSignalV322(s){
    const cloudRuntime=!!(cloudEnabled&&supabaseClient&&!window.__fjzStagingLocal?.enabled);
    if(cloudRuntime&&!window.__fjzFirstReviewAuthorityLoadedV319?.())return false;
    if(cloudRuntime&&window.__fjzCoachFeedReadyV322!==true)return false;
    const hasFeed=(feed(s)||[]).length>0;
    let feedback=0;try{feedback=Number(pendingSessionFeedbackCountV243?.(s)||0)}catch(_e){}
    const r=coachReviewLoopStateV238?.(s)||{};
    const reviewed=!!window.__fjzProfileReviewedStudentV319?.(s?.id);
    return hasFeed||feedback>0||!!r.changed||!!r.reviewDue||(!reviewed&&!r.hasBaseline);
  }
  function active(s){
    try{
      if(!realReviewSignalV322(s))return null;
      const p=coachPriorityStateV252?.(s)||{};
      return p.bucket==='urgent'||p.bucket==='today'?p:{...p,bucket:'today',score:Number(p.score||50)};
    }catch(_e){return null}
  }"""
    if body.count(old)!=1:
        raise RuntimeError("V21.22 V302 active anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""      loaded=true;
      return true;"""
    new="""      loaded=true;
      try{refreshSurfaces()}catch(_e){}
      return true;"""
    if body.count(old)!=1:
        raise RuntimeError("V21.22 cloud authority repaint anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    missingSnapshotBaselineCannotReopenReviewV321:true,"""
    new="""    missingSnapshotBaselineCannotReopenReviewV321:true,
    serverFeedRequiredForReviewCardsV322:true,
    reviewCardsFailClosedUntilCloudReadyV322:true,
    syntheticPriorityCannotBecomeReviewV322:true,
    cloudAuthorityRepaintsReviewCenterV322:true,"""
    if body.count(old)!=1:
        raise RuntimeError("V21.22 V302 flags anchor mismatch")
    body=body.replace(old,new,1)
    return body

html=edit_script(html,"v302ReviewResolutionAuthorityRuntime",patch_v302)

html=html.replace("</head>",'<meta name="fjz-review-server-authority" content="21.22">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V21.22 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-review-server-authority" content="21.22"',
    "__fjzCoachFeedReadyV322=false",
    "__fjzCoachFeedReadyV322=true",
    "realReviewSignalV322",
    "serverFeedRequiredForReviewCardsV322:true",
    "reviewCardsFailClosedUntilCloudReadyV322:true",
    "syntheticPriorityCannotBecomeReviewV322:true",
    "cloudAuthorityRepaintsReviewCenterV322:true",
    "if(!genuine)return null",
    "try{refreshSurfaces()}catch(_e){}",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.22 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.22 server review authority")
print("V21.22 BEFORE:",before)
print("V21.22 AFTER:",after)
