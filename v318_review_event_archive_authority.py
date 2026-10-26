import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\\.)?render\\s*=",doc)),
        "channels":len(re.findall(r"\\.channel\\s*\\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\\s*\\(",doc)),
        "intervals":len(re.findall(r"setInterval\\s*\\(",doc)),
        "listeners":len(re.findall(r"addEventListener\\s*\\(",doc)),
        "mutation_observers":len(re.findall(r"new\\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\\s+PerformanceObserver",doc)),
    }

def edit_script(doc,sid,fn):
    pat=re.compile(r'(<script[^>]*\\bid=["\\']'+re.escape(sid)+r'["\\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m: raise RuntimeError("V21.18 missing script "+sid)
    body=fn(m.group(2))
    return doc[:m.start(2)]+body+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-review-calendar-authority" content="21.13"',
    'meta name="fjz-session-loss-protection" content="21.16"',
    'id="v302ReviewResolutionAuthorityRuntime"',
    'id="v304GlobalSaveIntegrityRuntime"',
    'id="v316SessionLossProtectionRuntime"',
    "review-profile-v311:",
    "PROFILE_PREFIX+'%'",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.18 prerequisite missing "+marker)

def patch_v302(body):
    old="""    const f=feed(s).slice().sort((a,b)=>({critical:4,warning:3,info:2,success:1}[b?.severity]||0)-({critical:4,warning:3,info:2,success:1}[a?.severity]||0));"""
    new="""    const f=feed(s)
      .filter(x=>{const k=String(x?.event_key||'');return !k||!resolved.has(k)})
      .slice()
      .sort((a,b)=>({critical:4,warning:3,info:2,success:1}[b?.severity]||0)-({critical:4,warning:3,info:2,success:1}[a?.severity]||0));"""
    if body.count(old)!=1:
        raise RuntimeError("V21.18 feed unresolved filter anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""  function isResolved(s,d){
    if(!d)return false;
    if(d.sourceType==='event'||d.sourceType==='feedback')return resolved.has(d.reviewKey);
    if(String(d.source||'').startsWith('first_review:')&&profileReviewedV311(s))return true;
    if(baselineCurrentV308(s))return true;
    if(resolved.has(d.stateKey)||resolved.has(d.reviewKey))return true;
    try{return !!window.__fjzIsReviewAckedV299?.(s)}catch(_e){return false}
  }"""
    new="""  function isResolved(s,d){
    if(!d)return false;
    if(d.sourceType==='event'){
      if(resolved.has(d.reviewKey))return true;
      if((d.eventKeys||[]).some(k=>resolved.has(String(k))))return true;
      return false;
    }
    if(d.sourceType==='feedback')return resolved.has(d.reviewKey);
    if(String(d.source||'').startsWith('first_review:')&&profileReviewedV311(s))return true;
    if(baselineCurrentV308(s))return true;
    if(resolved.has(d.stateKey)||resolved.has(d.reviewKey))return true;
    try{return !!window.__fjzIsReviewAckedV299?.(s)}catch(_e){return false}
  }"""
    if body.count(old)!=1:
        raise RuntimeError("V21.18 isResolved anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""      const prefixes=[ITEM_PREFIX+'%',REVIEW_PREFIX+'%',STATE_PREFIX+'%',BASE_PREFIX+'%',PROFILE_PREFIX+'%','review-ack-v299:%'];
      const batches=await Promise.all(prefixes.map(async pattern=>{
        const {data,error}=await supabaseClient.from('coach_feed_state')
          .select('event_key,read_at,dismissed_at')
          .eq('coach_id',currentUser.id)
          .like('event_key',pattern);
        if(error)throw error;
        return data||[];
      }));
      read.clear();resolved.clear();legacyResolvedAthletes.clear();profileReviewedAthletesV311.clear();
      const promoteProfilesV311=new Set();"""
    new="""      const prefixes=[ITEM_PREFIX+'%',REVIEW_PREFIX+'%',STATE_PREFIX+'%',BASE_PREFIX+'%',PROFILE_PREFIX+'%','review-ack-v299:%'];
      const batches=await Promise.all(prefixes.map(async pattern=>{
        const {data,error}=await supabaseClient.from('coach_feed_state')
          .select('event_key,read_at,dismissed_at')
          .eq('coach_id',currentUser.id)
          .like('event_key',pattern);
        if(error)throw error;
        return data||[];
      }));
      const {data:dismissedEventsV318,error:dismissedEventsErrorV318}=await supabaseClient
        .from('coach_feed_state')
        .select('event_key,dismissed_at')
        .eq('coach_id',currentUser.id)
        .not('dismissed_at','is',null);
      if(dismissedEventsErrorV318)throw dismissedEventsErrorV318;
      read.clear();resolved.clear();legacyResolvedAthletes.clear();profileReviewedAthletesV311.clear();
      (dismissedEventsV318||[]).forEach(x=>{
        const k=String(x?.event_key||'');
        if(k&&x?.dismissed_at)resolved.add(k);
      });
      const promoteProfilesV311=new Set();"""
    if body.count(old)!=1:
        raise RuntimeError("V21.18 load dismissed-event authority anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    version:'21.11',
    resolvedStateAuthoritative:true,
    stableBaselineAuthority:true,
    legacyResolvedMigration:true,
    noRepeatedFirstReview:true,
    permanentProfileReviewAuthority:true,
    dynamicHashCannotReopenFirstReview:true,
    existingBaselinesPromotedToProfileReview:true,"""
    new="""    version:'21.18',
    resolvedStateAuthoritative:true,
    stableBaselineAuthority:true,
    legacyResolvedMigration:true,
    noRepeatedFirstReview:true,
    permanentProfileReviewAuthority:true,
    dynamicHashCannotReopenFirstReview:true,
    existingBaselinesPromotedToProfileReview:true,
    underlyingEventResolutionAuthorityV318:true,
    dismissedUnderlyingEventSuppressesDerivedReview:true,
    resolvedEventsFilteredBeforeRanking:true,"""
    if body.count(old)!=1:
        raise RuntimeError("V21.18 V302 flags anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    return body

html=edit_script(html,"v302ReviewResolutionAuthorityRuntime",patch_v302)
html=html.replace("</head>",'<meta name="fjz-review-event-archive-authority" content="21.18">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V21.18 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-review-event-archive-authority" content="21.18"',
    "underlyingEventResolutionAuthorityV318:true",
    "dismissedUnderlyingEventSuppressesDerivedReview:true",
    "resolvedEventsFilteredBeforeRanking:true",
    ".not('dismissed_at','is',null)",
    "(d.eventKeys||[]).some(k=>resolved.has(String(k)))",
    ".filter(x=>{const k=String(x?.event_key||'');return !k||!resolved.has(k)})",
]:
    if marker not in html:
        raise RuntimeError("V21.18 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.18 review event archive authority")
print("V21.18 BEFORE:",before)
print("V21.18 AFTER:",after)
