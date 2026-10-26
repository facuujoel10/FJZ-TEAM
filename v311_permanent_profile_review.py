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
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

def edit_script(doc,sid,fn):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(sid)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m: raise RuntimeError("V21.11 missing script "+sid)
    body=fn(m.group(2))
    return doc[:m.start(2)]+body+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-review-recurrence-fix" content="21.08"',
    'id="v302ReviewResolutionAuthorityRuntime"',
    "review-baseline-v308:",
    "noRepeatedFirstReview:true",
]:
    if marker not in html:
        raise RuntimeError("V21.11 prerequisite missing "+marker)

def patch_v302(body):
    old="""  const BASE_PREFIX='review-baseline-v308:';
  const resolved=new Set(),read=new Set(),registry=new Map(),center=new Map(),resolving=new Set(),legacyResolvedAthletes=new Set(),promotionInflight=new Set();
  let loaded=false,loadPromise=null;"""
    new="""  const BASE_PREFIX='review-baseline-v308:';
  const PROFILE_PREFIX='review-profile-v311:';
  const resolved=new Set(),read=new Set(),registry=new Map(),center=new Map(),resolving=new Set(),legacyResolvedAthletes=new Set(),promotionInflight=new Set(),profileReviewedAthletesV311=new Set();
  let loaded=false,loadPromise=null;"""
    if body.count(old)!=1:
        raise RuntimeError("V21.11 constants anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""  function baselinePrefixV308(s){return BASE_PREFIX+athleteKeyV308(s)+':'}
  function baselineKeyV308(s){return baselinePrefixV308(s)+hash(baselineSignalV308(s))}
  function hasAnyBaselineV308(s){"""
    new="""  function baselinePrefixV308(s){return BASE_PREFIX+athleteKeyV308(s)+':'}
  function baselineKeyV308(s){return baselinePrefixV308(s)+hash(baselineSignalV308(s))}
  function profileKeyV311(s){return PROFILE_PREFIX+athleteKeyV308(s)}
  function profileReviewedV311(s){
    const id=athleteKeyV308(s);
    return !!id&&id!=='unknown'&&(profileReviewedAthletesV311.has(id)||resolved.has(PROFILE_PREFIX+id));
  }
  function hasAnyBaselineV308(s){"""
    if body.count(old)!=1:
        raise RuntimeError("V21.11 profile helper anchor mismatch")
    body=body.replace(old,new,1)

    old="""    const cloudBaseline=hasAnyBaselineV308(s),cloudBaselineCurrent=baselineCurrentV308(s);
    const effectiveHasBaseline=!!r?.hasBaseline||cloudBaseline;
    const effectiveChanged=!!r?.hasBaseline?!!r?.changed:(cloudBaseline&&!cloudBaselineCurrent);"""
    new="""    const cloudBaseline=hasAnyBaselineV308(s),cloudBaselineCurrent=baselineCurrentV308(s),profileReviewed=profileReviewedV311(s);
    const effectiveHasBaseline=!!r?.hasBaseline||cloudBaseline||profileReviewed;
    // A permanent 360-review acknowledgement must not turn into a new generic
    // review merely because the old dynamic baseline hash changed.
    const effectiveChanged=!!r?.hasBaseline?!!r?.changed:(profileReviewed?false:(cloudBaseline&&!cloudBaselineCurrent));"""
    if body.count(old)!=1:
        raise RuntimeError("V21.11 effective baseline anchor mismatch")
    body=body.replace(old,new,1)

    old="""  function isResolved(s,d){
    if(!d)return false;
    if(d.sourceType==='event'||d.sourceType==='feedback')return resolved.has(d.reviewKey);
    if(baselineCurrentV308(s))return true;
    if(resolved.has(d.stateKey)||resolved.has(d.reviewKey))return true;
    try{return !!window.__fjzIsReviewAckedV299?.(s)}catch(_e){return false}
  }"""
    new="""  function isResolved(s,d){
    if(!d)return false;
    if(d.sourceType==='event'||d.sourceType==='feedback')return resolved.has(d.reviewKey);
    if(String(d.source||'').startsWith('first_review:')&&profileReviewedV311(s))return true;
    if(baselineCurrentV308(s))return true;
    if(resolved.has(d.stateKey)||resolved.has(d.reviewKey))return true;
    try{return !!window.__fjzIsReviewAckedV299?.(s)}catch(_e){return false}
  }"""
    if body.count(old)!=1:
        raise RuntimeError("V21.11 isResolved anchor mismatch")
    body=body.replace(old,new,1)

    old="""      const prefixes=[ITEM_PREFIX+'%',REVIEW_PREFIX+'%',STATE_PREFIX+'%',BASE_PREFIX+'%','review-ack-v299:%'];"""
    new="""      const prefixes=[ITEM_PREFIX+'%',REVIEW_PREFIX+'%',STATE_PREFIX+'%',BASE_PREFIX+'%',PROFILE_PREFIX+'%','review-ack-v299:%'];"""
    if body.count(old)!=1:
        raise RuntimeError("V21.11 load prefix anchor mismatch")
    body=body.replace(old,new,1)

    old="""      read.clear();resolved.clear();legacyResolvedAthletes.clear();
      batches.flat().forEach(x=>{
        const k=String(x?.event_key||'');if(!k)return;
        if(x.read_at)read.add(k);
        if(x.dismissed_at){
          resolved.add(k);
          if(k.startsWith(STATE_PREFIX)){
            const id=k.slice(STATE_PREFIX.length).split(':')[0];
            if(id)legacyResolvedAthletes.add(id);
          }
        }
      });
      loaded=true;
      return true;"""
    new="""      read.clear();resolved.clear();legacyResolvedAthletes.clear();profileReviewedAthletesV311.clear();
      const promoteProfilesV311=new Set();
      batches.flat().forEach(x=>{
        const k=String(x?.event_key||'');if(!k)return;
        if(x.read_at)read.add(k);
        if(x.dismissed_at){
          resolved.add(k);
          if(k.startsWith(STATE_PREFIX)){
            const id=k.slice(STATE_PREFIX.length).split(':')[0];
            if(id){legacyResolvedAthletes.add(id);profileReviewedAthletesV311.add(id);promoteProfilesV311.add(PROFILE_PREFIX+id)}
          }
          if(k.startsWith(BASE_PREFIX)){
            const id=k.slice(BASE_PREFIX.length).split(':')[0];
            if(id){profileReviewedAthletesV311.add(id);promoteProfilesV311.add(PROFILE_PREFIX+id)}
          }
          if(k.startsWith(PROFILE_PREFIX)){
            const id=k.slice(PROFILE_PREFIX.length);
            if(id)profileReviewedAthletesV311.add(id);
          }
        }
      });
      // Migrate already-reviewed profiles once to a stable per-athlete key.
      const missingProfiles=[...promoteProfilesV311].filter(k=>!resolved.has(k));
      if(missingProfiles.length){
        const ok=await persist(missingProfiles,'ok');
        if(ok)missingProfiles.forEach(k=>{
          resolved.add(k);
          const id=k.slice(PROFILE_PREFIX.length);if(id)profileReviewedAthletesV311.add(id);
        });
      }
      loaded=true;
      return true;"""
    if body.count(old)!=1:
        raise RuntimeError("V21.11 state migration anchor mismatch")
    body=body.replace(old,new,1)

    old="""    const keys=[lock,d.stateKey||stateKey(s),...(d.eventKeys||[])].filter(Boolean);
    if(d.sourceType==='state')keys.push(baselineKeyV308(s));
    const ok=await persist(keys,'ok');"""
    new="""    const keys=[lock,d.stateKey||stateKey(s),...(d.eventKeys||[])].filter(Boolean);
    if(d.sourceType==='state'){
      keys.push(baselineKeyV308(s));
      keys.push(profileKeyV311(s));
    }
    const ok=await persist(keys,'ok');"""
    if body.count(old)!=1:
        raise RuntimeError("V21.11 resolve profile key anchor mismatch")
    body=body.replace(old,new,1)

    old="""    resolved.add(lock);resolved.add(d.stateKey||stateKey(s));if(d.sourceType==='state')resolved.add(baselineKeyV308(s));"""
    new="""    resolved.add(lock);resolved.add(d.stateKey||stateKey(s));if(d.sourceType==='state'){resolved.add(baselineKeyV308(s));resolved.add(profileKeyV311(s));profileReviewedAthletesV311.add(athleteKeyV308(s));}"""
    if body.count(old)!=1:
        raise RuntimeError("V21.11 resolved profile cache anchor mismatch")
    body=body.replace(old,new,1)


    old="""  function renderCenter(){
    const host=el('v252PriorityCenter');if(!host)return;center.clear();"""
    new="""  function renderCenter(){
    const host=el('v252PriorityCenter');if(!host)return;
    if(!loaded&&cloudEnabled&&supabaseClient&&!window.__fjzStagingLocal?.enabled){
      host.innerHTML='<div class="v301-empty"><strong>Sincronizando revisiones…</strong><span>Comprobando qué revisiones ya fueron cerradas.</span></div>';
      loadStates(false).finally(()=>{if(currentProfile?.role==='coach'&&coachTab==='dashboard')renderCenter()});
      return;
    }
    center.clear();"""
    if body.count(old)!=1:
        raise RuntimeError("V21.11 center hydration guard anchor mismatch")
    body=body.replace(old,new,1)

    old="""  function renderFocus(){
    const host=el('v235CoachFocus');if(!host)return;"""
    new="""  function renderFocus(){
    const host=el('v235CoachFocus');if(!host)return;
    if(!loaded&&cloudEnabled&&supabaseClient&&!window.__fjzStagingLocal?.enabled){
      host.innerHTML='<div class="v301-empty"><strong>Sincronizando revisiones…</strong><span>Esperando el estado confirmado de cada alumno.</span></div>';
      return;
    }"""
    if body.count(old)!=1:
        raise RuntimeError("V21.11 focus hydration guard anchor mismatch")
    body=body.replace(old,new,1)

    old="""    version:'21.08',
    resolvedStateAuthoritative:true,
    stableBaselineAuthority:true,
    legacyResolvedMigration:true,
    noRepeatedFirstReview:true,"""
    new="""    version:'21.11',
    resolvedStateAuthoritative:true,
    stableBaselineAuthority:true,
    legacyResolvedMigration:true,
    noRepeatedFirstReview:true,
    permanentProfileReviewAuthority:true,
    dynamicHashCannotReopenFirstReview:true,
    existingBaselinesPromotedToProfileReview:true,"""
    if body.count(old)!=1:
        raise RuntimeError("V21.11 flags anchor mismatch")
    body=body.replace(old,new,1)

    return body

html=edit_script(html,"v302ReviewResolutionAuthorityRuntime",patch_v302)
html=html.replace("</head>",'<meta name="fjz-permanent-profile-review" content="21.11">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V21.11 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-permanent-profile-review" content="21.11"',
    "review-profile-v311:",
    "profileReviewedV311",
    "dynamicHashCannotReopenFirstReview:true",
    "existingBaselinesPromotedToProfileReview:true",
    "String(d.source||'').startsWith('first_review:')&&profileReviewedV311(s)",
    "keys.push(profileKeyV311(s))",
    "PROFILE_PREFIX+'%'",
]:
    if marker not in html:
        raise RuntimeError("V21.11 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.11 permanent profile review authority")
print("V21.11 BEFORE:",before)
print("V21.11 AFTER:",after)
