import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":doc.count(".channel("),
        "timeouts":doc.count("setTimeout("),
        "intervals":doc.count("setInterval("),
        "listeners":doc.count("addEventListener("),
        "mutation_observers":doc.count("new MutationObserver"),
        "performance_observers":doc.count("new PerformanceObserver"),
    }

def edit_script(doc,sid,fn):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(sid)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m: raise RuntimeError("V21.19 missing script "+sid)
    body=fn(m.group(2))
    return doc[:m.start(2)]+body+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-review-event-archive-authority" content="21.18"',
    'id="v302ReviewResolutionAuthorityRuntime"',
    'id="v312ReviewAgendaAuthorityRuntime"',
    'id="v280OperationalRecoveryRuntime"',
    'id="v175ProfileAgendaCoachCenterRuntime"',
    "review-profile-v311:",
    "profileReviewedV311",
]:
    if marker not in html:
        raise RuntimeError("V21.19 prerequisite missing "+marker)

def patch_v302(body):
    old="""  const resolved=new Set(),read=new Set(),registry=new Map(),center=new Map(),resolving=new Set(),legacyResolvedAthletes=new Set(),promotionInflight=new Set(),profileReviewedAthletesV311=new Set();
  let loaded=false,loadPromise=null;"""
    new="""  const resolved=new Set(),read=new Set(),registry=new Map(),center=new Map(),resolving=new Set(),legacyResolvedAthletes=new Set(),promotionInflight=new Set(),profileReviewedAthletesV311=new Set(),profileReviewedClientsV319=new Set(),athleteByClientV319=new Map(),clientByAthleteV319=new Map();
  let loaded=false,loadPromise=null;"""
    if body.count(old)!=1:
        raise RuntimeError("V21.19 constants anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""  function athleteKeyV308(s){
    const a=athlete(s);
    return String(a?.id||s?.id||'unknown');
  }"""
    new="""  function athleteKeyV308(s){
    const a=athlete(s),clientId=String(s?.id||'');
    return String(a?.id||athleteByClientV319.get(clientId)||clientId||'unknown');
  }"""
    if body.count(old)!=1:
        raise RuntimeError("V21.19 athlete key anchor mismatch")
    body=body.replace(old,new,1)

    old="""  function profileReviewedV311(s){
    const id=athleteKeyV308(s);
    return !!id&&id!=='unknown'&&(profileReviewedAthletesV311.has(id)||resolved.has(PROFILE_PREFIX+id));
  }
  window.__fjzProfileReviewedAthleteV311=function(id){"""
    new="""  function profileReviewedV311(s){
    const id=athleteKeyV308(s),clientId=String(s?.id||'');
    return !!id&&id!=='unknown'&&(profileReviewedAthletesV311.has(id)||resolved.has(PROFILE_PREFIX+id)||profileReviewedClientsV319.has(clientId));
  }
  window.__fjzProfileReviewedStudentV319=function(clientId){return profileReviewedClientsV319.has(String(clientId||''))};
  window.__fjzFirstReviewAuthorityLoadedV319=function(){return !!loaded};
  window.__fjzProfileReviewedAthleteV311=function(id){"""
    if body.count(old)!=1:
        raise RuntimeError("V21.19 profile reviewed anchor mismatch")
    body=body.replace(old,new,1)

    old="""  function baselineCurrentV308(s){return resolved.has(baselineKeyV308(s))}
  function legacyReviewedV308(s){return legacyResolvedAthletes.has(athleteKeyV308(s))}
  function ensureLegacyBaselineV308(s){
    const id=athleteKeyV308(s);
    if(!id||id==='unknown'||!legacyResolvedAthletes.has(id)||hasAnyBaselineV308(s))return false;"""
    new="""  function baselineCurrentV308(s){return profileReviewedV311(s)||resolved.has(baselineKeyV308(s))}
  function legacyReviewedV308(s){return legacyResolvedAthletes.has(athleteKeyV308(s))}
  function ensureLegacyBaselineV308(s){
    const id=athleteKeyV308(s);
    if(profileReviewedV311(s))return false;
    if(!id||id==='unknown'||!legacyResolvedAthletes.has(id)||hasAnyBaselineV308(s))return false;"""
    if body.count(old)!=1:
        raise RuntimeError("V21.19 baseline authority anchor mismatch")
    body=body.replace(old,new,1)

    old="""      if(dismissedEventsErrorV318)throw dismissedEventsErrorV318;
      read.clear();resolved.clear();legacyResolvedAthletes.clear();profileReviewedAthletesV311.clear();
      (dismissedEventsV318||[]).forEach(x=>{"""
    new="""      if(dismissedEventsErrorV318)throw dismissedEventsErrorV318;
      const {data:athleteLinksV319,error:athleteLinksErrorV319}=await supabaseClient
        .from('athletes')
        .select('id,client_id')
        .eq('coach_id',currentUser.id);
      if(athleteLinksErrorV319)throw athleteLinksErrorV319;
      read.clear();resolved.clear();legacyResolvedAthletes.clear();profileReviewedAthletesV311.clear();profileReviewedClientsV319.clear();athleteByClientV319.clear();clientByAthleteV319.clear();
      (athleteLinksV319||[]).forEach(a=>{
        const id=String(a?.id||''),clientId=String(a?.client_id||'');
        if(id&&clientId){athleteByClientV319.set(clientId,id);clientByAthleteV319.set(id,clientId)}
      });
      (dismissedEventsV318||[]).forEach(x=>{"""
    if body.count(old)!=1:
        raise RuntimeError("V21.19 cloud map load anchor mismatch")
    body=body.replace(old,new,1)

    old="""          if(k.startsWith(STATE_PREFIX)){
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
          }"""
    new="""          if(k.startsWith(STATE_PREFIX)){
            const id=k.slice(STATE_PREFIX.length).split(':')[0];
            if(id){
              legacyResolvedAthletes.add(id);profileReviewedAthletesV311.add(id);promoteProfilesV311.add(PROFILE_PREFIX+id);
              const clientId=clientByAthleteV319.get(id);if(clientId)profileReviewedClientsV319.add(clientId);
            }
          }
          if(k.startsWith(BASE_PREFIX)){
            const id=k.slice(BASE_PREFIX.length).split(':')[0];
            if(id){
              profileReviewedAthletesV311.add(id);promoteProfilesV311.add(PROFILE_PREFIX+id);
              const clientId=clientByAthleteV319.get(id);if(clientId)profileReviewedClientsV319.add(clientId);
            }
          }
          if(k.startsWith(PROFILE_PREFIX)){
            const id=k.slice(PROFILE_PREFIX.length);
            if(id){
              profileReviewedAthletesV311.add(id);
              const clientId=clientByAthleteV319.get(id);if(clientId)profileReviewedClientsV319.add(clientId);
            }
          }"""
    if body.count(old)!=1:
        raise RuntimeError("V21.19 reviewed client hydration anchor mismatch")
    body=body.replace(old,new,1)

    old="""        if(ok)missingProfiles.forEach(k=>{
          resolved.add(k);
          const id=k.slice(PROFILE_PREFIX.length);if(id)profileReviewedAthletesV311.add(id);
        });"""
    new="""        if(ok)missingProfiles.forEach(k=>{
          resolved.add(k);
          const id=k.slice(PROFILE_PREFIX.length);
          if(id){
            profileReviewedAthletesV311.add(id);
            const clientId=clientByAthleteV319.get(id);if(clientId)profileReviewedClientsV319.add(clientId);
          }
        });"""
    if body.count(old)!=1:
        raise RuntimeError("V21.19 migration client anchor mismatch")
    body=body.replace(old,new,1)

    old="""    underlyingEventResolutionAuthorityV318:true,
    dismissedUnderlyingEventSuppressesDerivedReview:true,
    resolvedEventsFilteredBeforeRanking:true,"""
    new="""    underlyingEventResolutionAuthorityV318:true,
    dismissedUnderlyingEventSuppressesDerivedReview:true,
    resolvedEventsFilteredBeforeRanking:true,
    stableClientReviewAuthorityV319:true,
    firstReviewReadsCloudProfileKeyOnly:true,
    reviewedProfileCannotRegenerateDynamicBaseline:true,"""
    if body.count(old)!=1:
        raise RuntimeError("V21.19 flags anchor mismatch")
    body=body.replace(old,new,1)
    return body

html=edit_script(html,"v302ReviewResolutionAuthorityRuntime",patch_v302)

def patch_v312(body):
    old="""  function athleteIdForReviewV312(s){
    try{return String(coachAthleteV235?.(s)?.id||'')}catch(_e){return ''}
  }
  function permanentReviewedV312(s){
    const id=athleteIdForReviewV312(s);
    return !!id&&!!window.__fjzProfileReviewedAthleteV311?.(id);
  }

  const baseReviewLoopV312=window.coachReviewLoopStateV238||coachReviewLoopStateV238;
  window.coachReviewLoopStateV238=function(s){
    const out=baseReviewLoopV312?.(s)||{};
    if(permanentReviewedV312(s)&&!s?.coachReviewV237){
      return {
        ...out,
        hasBaseline:true,
        changed:false,
        reviewDue:false,
        reviewDueLabel:'Perfil 360 revisado',
        reason:'Perfil 360 revisado',
        newSessions:0,
        adherenceDelta:0
      };
    }
    return out;
  };"""
    new="""  function athleteIdForReviewV312(s){
    try{return String(cloudAthletes?.get?.(s?.id)?.id||coachAthleteV235?.(s)?.id||'')}catch(_e){return ''}
  }
  function permanentReviewedV312(s){
    if(window.__fjzProfileReviewedStudentV319?.(s?.id))return true;
    const id=athleteIdForReviewV312(s);
    return !!id&&!!window.__fjzProfileReviewedAthleteV311?.(id);
  }

  const baseReviewLoopV312=window.coachReviewLoopStateV238||coachReviewLoopStateV238;
  window.coachReviewLoopStateV238=function(s){
    const out=baseReviewLoopV312?.(s)||{};
    if(permanentReviewedV312(s)){
      const localReviewed=!!s?.coachReviewV237?.reviewedAt;
      return {
        ...out,
        hasBaseline:true,
        changed:localReviewed?!!out.changed:false,
        reviewDue:localReviewed?!!out.reviewDue:false,
        reviewDueLabel:localReviewed?(out.reviewDueLabel||'Seguimiento programado'):'Perfil 360 revisado',
        reason:localReviewed?(out.reason||'Seguimiento del alumno'):'Perfil 360 revisado',
        newSessions:localReviewed?Number(out.newSessions||0):0,
        adherenceDelta:localReviewed?(out.adherenceDelta??0):0
      };
    }
    return out;
  };"""
    if body.count(old)!=1:
        raise RuntimeError("V21.19 legacy loop authority anchor mismatch")
    body=body.replace(old,new,1)

    old="""    noDuplicateFirstReviewAfterReload:true,
    oldReviewHubCloudAware:true,"""
    new="""    noDuplicateFirstReviewAfterReload:true,
    oldReviewHubCloudAware:true,
    stableClientReviewAuthorityV319:true,
    legacySnapshotCannotOverrideCloudReviewedState:true,"""
    if body.count(old)!=1:
        raise RuntimeError("V21.19 V312 flags anchor mismatch")
    body=body.replace(old,new,1)
    return body

html=edit_script(html,"v312ReviewAgendaAuthorityRuntime",patch_v312)

def patch_v175(body):
    old="""  function renderReviewHubV237(cur){
    const host=el('v237ReviewHub');if(!host)return;
    const s=student(),prev=s?.coachReviewV237||null;
    const changes=reviewChangeItemsV237(cur,prev);"""
    new="""  function renderReviewHubV237(cur){
    const host=el('v237ReviewHub');if(!host)return;
    const s=student(),prev=s?.coachReviewV237||null;
    const cloudReviewReady=!!window.__fjzFirstReviewAuthorityLoadedV319?.();
    const cloudReviewed=!!window.__fjzProfileReviewedStudentV319?.(s?.id);
    if(cloudEnabled&&supabaseClient&&!window.__fjzStagingLocal?.enabled&&!cloudReviewReady){
      host.innerHTML='<div class="v237-review-head"><div><div class="v225-section-kicker">REVISIÓN DEL COACH</div><h4>Sincronizando revisión…</h4><p>Comprobando el estado confirmado de este alumno.</p></div></div>';
      return;
    }
    if(cloudReviewed&&!prev){
      host.innerHTML='<div class="v237-review-head"><div><div class="v225-section-kicker">REVISIÓN DEL COACH</div><h4>Perfil 360 revisado</h4>'+
        '<p>La primera revisión ya fue confirmada en la nube. Solo aparecerán nuevas revisiones por actividad nueva o una fecha real de seguimiento.</p></div>'+
        '<div class="v237-review-meta"><span>Estado</span><strong>Revisado en nube</strong></div></div>'+
        '<div class="v237-review-grid"><div class="v237-review-col"><div class="v237-review-label">ESTADO</div>'+
        '<div class="v237-review-item good"><div><strong>Sin primera revisión pendiente</strong><p>Este perfil ya tiene una revisión permanente confirmada.</p></div></div></div></div>';
      return;
    }
    const changes=reviewChangeItemsV237(cur,prev);"""
    if body.count(old)!=1:
        raise RuntimeError("V21.19 V237 hub anchor mismatch")
    body=body.replace(old,new,1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

def patch_v280(body):
    old="""  function cloudProfileReviewedV313(s){
    try{
      const a=athleteFor(s),id=String(a?.id||'');
      return !!id&&!!window.__fjzProfileReviewedAthleteV311?.(id);
    }catch(_e){return false}
  }
  function reviewStateReadyV313(){
    try{return !!window.__fjzProfileReviewStateLoadedV311?.()}catch(_e){return false}
  }"""
    new="""  function cloudProfileReviewedV313(s){
    try{
      if(window.__fjzProfileReviewedStudentV319?.(s?.id))return true;
      const a=athleteFor(s),id=String(a?.id||'');
      return !!id&&!!window.__fjzProfileReviewedAthleteV311?.(id);
    }catch(_e){return false}
  }
  function reviewStateReadyV313(){
    try{return !!window.__fjzFirstReviewAuthorityLoadedV319?.()||!!window.__fjzProfileReviewStateLoadedV311?.()}catch(_e){return false}
  }"""
    if body.count(old)!=1:
        raise RuntimeError("V21.19 calendar cloud authority anchor mismatch")
    body=body.replace(old,new,1)
    return body

html=edit_script(html,"v280OperationalRecoveryRuntime",patch_v280)

html=html.replace("</head>",'<meta name="fjz-first-review-authority" content="21.19">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V21.19 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-first-review-authority" content="21.19"',
    "profileReviewedClientsV319",
    "athleteByClientV319",
    ".select('id,client_id')",
    "__fjzProfileReviewedStudentV319",
    "firstReviewReadsCloudProfileKeyOnly:true",
    "reviewedProfileCannotRegenerateDynamicBaseline:true",
    "if(profileReviewedV311(s))return false",
    "legacySnapshotCannotOverrideCloudReviewedState:true",
    "Sin primera revisión pendiente",
    "window.__fjzProfileReviewedStudentV319?.(s?.id)",
]:
    if marker not in html:
        raise RuntimeError("V21.19 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.19 stable first-review authority")
print("V21.19 BEFORE:",before)
print("V21.19 AFTER:",after)
