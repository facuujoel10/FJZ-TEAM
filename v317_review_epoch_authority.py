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
    pat=re.compile(r"(<script[^>]*\\bid=[\"']"+re.escape(sid)+r"[\"'][^>]*>)(.*?)(</script>)",re.S|re.I)
    m=pat.search(doc)
    if not m: raise RuntimeError("V21.17 missing script "+sid)
    body=fn(m.group(2))
    return doc[:m.start(2)]+body+doc[m.end(2):]

before=metrics(html)

for marker in [
    'id="v302ReviewResolutionAuthorityRuntime"',
    "review-profile-v311:",
    "profileReviewedV311",
    "eventKeys:top?.event_key",
    "window.__fjzLoadReviewStatesV302",
]:
    if marker not in html:
        raise RuntimeError("V21.17 prerequisite missing "+marker)

def patch_v302(body):
    old="""  const BASE_PREFIX='review-baseline-v308:';
  const PROFILE_PREFIX='review-profile-v311:';
  const resolved=new Set(),read=new Set(),registry=new Map(),center=new Map(),resolving=new Set(),legacyResolvedAthletes=new Set(),promotionInflight=new Set(),profileReviewedAthletesV311=new Set();
  let loaded=false,loadPromise=null;"""
    new="""  const BASE_PREFIX='review-baseline-v308:';
  const PROFILE_PREFIX='review-profile-v311:';
  const EPOCH_PREFIX='review-epoch-v317:';
  const resolved=new Set(),read=new Set(),registry=new Map(),center=new Map(),resolving=new Set(),legacyResolvedAthletes=new Set(),promotionInflight=new Set(),profileReviewedAthletesV311=new Set(),reviewEpochV317=new Map();
  let loaded=false,loadPromise=null;"""
    if body.count(old)!=1:
        raise RuntimeError("V21.17 constants anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""  function profileReviewedV311(s){
    const id=athleteKeyV308(s);
    return !!id&&id!=='unknown'&&(profileReviewedAthletesV311.has(id)||resolved.has(PROFILE_PREFIX+id));
  }
  window.__fjzProfileReviewedAthleteV311=function(id){"""
    new="""  function profileReviewedV311(s){
    const id=athleteKeyV308(s);
    return !!id&&id!=='unknown'&&(profileReviewedAthletesV311.has(id)||resolved.has(PROFILE_PREFIX+id));
  }
  function epochKeyV317(s){return EPOCH_PREFIX+athleteKeyV308(s)}
  function epochAtV317(s){return Number(reviewEpochV317.get(athleteKeyV308(s))||0)}
  function rememberEpochV317(id,value){
    id=String(id||'');const t=Date.parse(value||0)||Number(value)||0;if(!id||!t)return;
    if(t>Number(reviewEpochV317.get(id)||0))reviewEpochV317.set(id,t);
  }
  function eventOccurredAtV317(s,d){
    const keys=new Set((d?.eventKeys||[]).map(String));
    let row=null;
    try{
      const rows=feed(s);
      row=keys.size?rows.find(x=>keys.has(String(x?.event_key||'')))||null:rows[0]||null;
    }catch(_e){}
    return Date.parse(row?.occurred_at||row?.created_at||row?.updated_at||0)||0;
  }
  function eventCoveredByEpochV317(s,d){
    const epoch=epochAtV317(s);if(!epoch)return false;
    const at=eventOccurredAtV317(s,d);if(!at)return false;
    return at<=epoch;
  }
  window.__fjzProfileReviewedAthleteV311=function(id){"""
    if body.count(old)!=1:
        raise RuntimeError("V21.17 epoch helper anchor mismatch")
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
      if(eventCoveredByEpochV317(s,d))return true;
      return false;
    }
    if(d.sourceType==='feedback')return resolved.has(d.reviewKey);
    if(String(d.source||'').startsWith('first_review:')&&profileReviewedV311(s))return true;
    if(baselineCurrentV308(s))return true;
    if(resolved.has(d.stateKey)||resolved.has(d.reviewKey))return true;
    try{return !!window.__fjzIsReviewAckedV299?.(s)}catch(_e){return false}
  }"""
    if body.count(old)!=1:
        raise RuntimeError("V21.17 isResolved anchor mismatch")
    body=body.replace(old,new,1)

    old="""      const prefixes=[ITEM_PREFIX+'%',REVIEW_PREFIX+'%',STATE_PREFIX+'%',BASE_PREFIX+'%',PROFILE_PREFIX+'%','review-ack-v299:%'];"""
    new="""      const prefixes=[ITEM_PREFIX+'%',REVIEW_PREFIX+'%',STATE_PREFIX+'%',BASE_PREFIX+'%',PROFILE_PREFIX+'%',EPOCH_PREFIX+'%','review-ack-v299:%'];"""
    if body.count(old)!=1:
        raise RuntimeError("V21.17 prefixes anchor mismatch")
    body=body.replace(old,new,1)

    old="""      read.clear();resolved.clear();legacyResolvedAthletes.clear();profileReviewedAthletesV311.clear();
      const promoteProfilesV311=new Set();
      batches.flat().forEach(x=>{
        const k=String(x?.event_key||'');if(!k)return;
        if(x.read_at)read.add(k);
        if(x.dismissed_at){
          resolved.add(k);"""
    new="""      read.clear();resolved.clear();legacyResolvedAthletes.clear();profileReviewedAthletesV311.clear();reviewEpochV317.clear();
      const promoteProfilesV311=new Set();
      batches.flat().forEach(x=>{
        const k=String(x?.event_key||'');if(!k)return;
        if(x.read_at)read.add(k);
        if(x.dismissed_at){
          resolved.add(k);
          if(k.startsWith(EPOCH_PREFIX)){
            const id=k.slice(EPOCH_PREFIX.length);if(id)rememberEpochV317(id,x.dismissed_at);
          }"""
    if body.count(old)!=1:
        raise RuntimeError("V21.17 load reset anchor mismatch")
    body=body.replace(old,new,1)

    old="""          if(k.startsWith(PROFILE_PREFIX)){
            const id=k.slice(PROFILE_PREFIX.length);
            if(id)profileReviewedAthletesV311.add(id);
          }"""
    new="""          if(k.startsWith(PROFILE_PREFIX)){
            const id=k.slice(PROFILE_PREFIX.length);
            if(id){profileReviewedAthletesV311.add(id);rememberEpochV317(id,x.dismissed_at)}
          }"""
    if body.count(old)!=1:
        raise RuntimeError("V21.17 profile epoch migration anchor mismatch")
    body=body.replace(old,new,1)

    old="""    const keys=[lock,d.stateKey||stateKey(s),...(d.eventKeys||[])].filter(Boolean);
    if(d.sourceType==='state'){
      keys.push(baselineKeyV308(s));
      keys.push(profileKeyV311(s));
    }
    const ok=await persist(keys,'ok');"""
    new="""    const keys=[lock,d.stateKey||stateKey(s),...(d.eventKeys||[])].filter(Boolean);
    if(d.sourceType==='state'){
      keys.push(baselineKeyV308(s));
      keys.push(profileKeyV311(s));
    }
    keys.push(epochKeyV317(s));
    const ok=await persist(keys,'ok');"""
    if body.count(old)!=1:
        raise RuntimeError("V21.17 resolve epoch key anchor mismatch")
    body=body.replace(old,new,1)

    old="""    resolved.add(lock);resolved.add(d.stateKey||stateKey(s));if(d.sourceType==='state'){resolved.add(baselineKeyV308(s));resolved.add(profileKeyV311(s));profileReviewedAthletesV311.add(athleteKeyV308(s));}"""
    new="""    resolved.add(lock);resolved.add(d.stateKey||stateKey(s));resolved.add(epochKeyV317(s));rememberEpochV317(athleteKeyV308(s),Date.now());if(d.sourceType==='state'){resolved.add(baselineKeyV308(s));resolved.add(profileKeyV311(s));profileReviewedAthletesV311.add(athleteKeyV308(s));}"""
    if body.count(old)!=1:
        raise RuntimeError("V21.17 resolved epoch cache anchor mismatch")
    body=body.replace(old,new,1)

    old="""      const keys=[d.reviewKey,d.stateKey].filter(Boolean);
      const saved=await persist(keys,'ok');
      if(saved){resolved.add(d.reviewKey);resolved.add(d.stateKey)}"""
    new="""      const keys=[d.reviewKey,d.stateKey,epochKeyV317(s)].filter(Boolean);
      const saved=await persist(keys,'ok');
      if(saved){resolved.add(d.reviewKey);resolved.add(d.stateKey);resolved.add(epochKeyV317(s));rememberEpochV317(athleteKeyV308(s),Date.now())}"""
    if body.count(old)!=1:
        raise RuntimeError("V21.17 dismiss epoch anchor mismatch")
    body=body.replace(old,new,1)

    old="""    permanentProfileReviewAuthority:true,
    dynamicHashCannotReopenFirstReview:true,
    existingBaselinesPromotedToProfileReview:true,"""
    new="""    permanentProfileReviewAuthority:true,
    dynamicHashCannotReopenFirstReview:true,
    existingBaselinesPromotedToProfileReview:true,
    reviewEpochAuthorityV317:true,
    oldEventHashCannotReopenAfterOk:true,
    realEventsAfterLastReviewRemainVisible:true,"""
    if body.count(old)!=1:
        raise RuntimeError("V21.17 flags anchor mismatch")
    body=body.replace(old,new,1)

    end=body.rfind("})();")
    if end<0: raise RuntimeError("V21.17 runtime end missing")
    expose="""  window.__fjzReviewEpochV317=function(id){return Number(reviewEpochV317.get(String(id||''))||0)};
"""
    body=body[:end]+expose+body[end:]
    return body

html=edit_script(html,"v302ReviewResolutionAuthorityRuntime",patch_v302)
html=html.replace("</head>",'<meta name="fjz-review-epoch-authority" content="21.17">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V21.17 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-review-epoch-authority" content="21.17"',
    "review-epoch-v317:",
    "reviewEpochAuthorityV317:true",
    "oldEventHashCannotReopenAfterOk:true",
    "realEventsAfterLastReviewRemainVisible:true",
    "eventCoveredByEpochV317",
    "keys.push(epochKeyV317(s))",
    "rememberEpochV317(id,x.dismissed_at)",
]:
    if marker not in html:
        raise RuntimeError("V21.17 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.17 review epoch authority")
print("V21.17 BEFORE:",before)
print("V21.17 AFTER:",after)
