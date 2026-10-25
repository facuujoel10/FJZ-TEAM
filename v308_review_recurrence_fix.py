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
    if not m: raise RuntimeError("V21.08 missing script "+sid)
    body=fn(m.group(2))
    return doc[:m.start(2)]+body+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-review-resolution-authority" content="21.02"',
    'id="v302ReviewResolutionAuthorityRuntime"',
    "review-state-v302:",
    "__fjzResolveCenterReviewV301",
    "cloudConfirmationRequired:true",
]:
    if marker not in html:
        raise RuntimeError("V21.08 prerequisite missing "+marker)

def patch_v302(body):
    old="""  const REVIEW_PREFIX='review-v302:';
  const STATE_PREFIX='review-state-v302:';
  const ITEM_PREFIX='review-item-v301:';
  const resolved=new Set(),read=new Set(),registry=new Map(),center=new Map(),resolving=new Set();
  let loaded=false,loadPromise=null;"""
    new="""  const REVIEW_PREFIX='review-v302:';
  const STATE_PREFIX='review-state-v302:';
  const ITEM_PREFIX='review-item-v301:';
  const BASE_PREFIX='review-baseline-v308:';
  const resolved=new Set(),read=new Set(),registry=new Map(),center=new Map(),resolving=new Set(),legacyResolvedAthletes=new Set(),promotionInflight=new Set();
  let loaded=false,loadPromise=null;"""
    if body.count(old)!=1:
        raise RuntimeError("V21.08 constants anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""  function stateKey(s){
    const a=athlete(s);
    return STATE_PREFIX+String(a?.id||s?.id||'unknown')+':'+hash(stateFingerprint(s));
  }

  function detail(s){"""
    new="""  function stateKey(s){
    const a=athlete(s);
    return STATE_PREFIX+String(a?.id||s?.id||'unknown')+':'+hash(stateFingerprint(s));
  }

  function athleteKeyV308(s){
    const a=athlete(s);
    return String(a?.id||s?.id||'unknown');
  }
  function baselineSignalV308(s){
    const pf=pendingFeedbackInfo(s);
    let status='';try{status=String(statusFor?.(s)||'')}catch(_e){}
    return [
      Array.isArray(s?.sessions)?s.sessions.length:0,
      Date.parse(s?.lastWorkout||0)||0,
      pf.count,
      status
    ].join(':');
  }
  function baselinePrefixV308(s){return BASE_PREFIX+athleteKeyV308(s)+':'}
  function baselineKeyV308(s){return baselinePrefixV308(s)+hash(baselineSignalV308(s))}
  function hasAnyBaselineV308(s){
    const prefix=baselinePrefixV308(s);
    for(const k of resolved)if(String(k).startsWith(prefix))return true;
    return false;
  }
  function baselineCurrentV308(s){return resolved.has(baselineKeyV308(s))}
  function legacyReviewedV308(s){return legacyResolvedAthletes.has(athleteKeyV308(s))}
  function ensureLegacyBaselineV308(s){
    const id=athleteKeyV308(s);
    if(!id||id==='unknown'||!legacyResolvedAthletes.has(id)||hasAnyBaselineV308(s))return false;
    const key=baselineKeyV308(s);
    resolved.add(key);read.add(key);legacyResolvedAthletes.delete(id);
    if(!promotionInflight.has(key)){
      promotionInflight.add(key);
      Promise.resolve(persist([key],'ok')).catch(e=>console.warn('TEAM FJZ V21.08 baseline promotion',e)).finally(()=>promotionInflight.delete(key));
    }
    return true;
  }

  function detail(s){"""
    if body.count(old)!=1:
        raise RuntimeError("V21.08 baseline helper anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    const f=feed(s).slice().sort((a,b)=>({critical:4,warning:3,info:2,success:1}[b?.severity]||0)-({critical:4,warning:3,info:2,success:1}[a?.severity]||0));
    const top=f[0]||null;
    const pf=pendingFeedbackInfo(s);
    const r=(()=>{try{return coachReviewLoopStateV238?.(s)||null}catch(_e){return null}})();
    const inactive=days(s?.lastWorkout),a=adh(s),kind=top?.kind||'';
    const tab=kind==='nutrition'?'nutrition':kind==='checkin'||kind==='wellness'?'tracking':kind==='progression'?'progress':kind==='exercise_feedback'||kind==='training'?'routine':pf.count?'routine':inactive>=7?'history':'summary';
    let title,why,look,sourceType='state',source='';"""
    new="""    const f=feed(s).slice().sort((a,b)=>({critical:4,warning:3,info:2,success:1}[b?.severity]||0)-({critical:4,warning:3,info:2,success:1}[a?.severity]||0));
    const top=f[0]||null;
    const pf=pendingFeedbackInfo(s);
    const r=(()=>{try{return coachReviewLoopStateV238?.(s)||null}catch(_e){return null}})();
    const cloudBaseline=hasAnyBaselineV308(s),cloudBaselineCurrent=baselineCurrentV308(s);
    const effectiveHasBaseline=!!r?.hasBaseline||cloudBaseline;
    const effectiveChanged=!!r?.hasBaseline?!!r?.changed:(cloudBaseline&&!cloudBaselineCurrent);
    const inactive=days(s?.lastWorkout),a=adh(s),kind=top?.kind||'';
    const tab=kind==='nutrition'?'nutrition':kind==='checkin'||kind==='wellness'?'tracking':kind==='progression'?'progress':kind==='exercise_feedback'||kind==='training'?'routine':pf.count?'routine':inactive>=7?'history':'summary';
    let title,why,look,sourceType='state',source='';"""
    if body.count(old)!=1:
        raise RuntimeError("V21.08 detail prelude anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    }else if(r?.reviewDue||!r?.hasBaseline){
      title=!r?.hasBaseline?'Primera revisión del alumno':'Revisión de seguimiento vencida';
      why=r?.reviewDueLabel||'No hay revisión de referencia.';
      look='Revisá el 360 completo: adherencia, últimas sesiones, check-in y progreso.';
      source='review_due:'+stateFingerprint(s);
    }else if(r?.changed){
      title='Cambios desde la última revisión';
      why=r.reason||'Hay actividad nueva.';
      look='Compará qué cambió desde el último chequeo y confirmá si requiere ajuste.';
      source='changed:'+stateFingerprint(s);"""
    new="""    }else if(r?.reviewDue||!effectiveHasBaseline){
      title=!effectiveHasBaseline?'Primera revisión del alumno':'Revisión de seguimiento vencida';
      why=r?.reviewDueLabel||(!effectiveHasBaseline?'No hay revisión de referencia.':'La revisión programada requiere atención.');
      look='Revisá el 360 completo: adherencia, últimas sesiones, check-in y progreso.';
      source=!effectiveHasBaseline?'first_review:'+athleteKeyV308(s):'review_due:'+stateFingerprint(s);
    }else if(effectiveChanged){
      title='Cambios desde la última revisión';
      why=(r?.hasBaseline&&r?.reason)?r.reason:'Hay cambios nuevos desde la última revisión confirmada.';
      look='Compará qué cambió desde el último chequeo y confirmá si requiere ajuste.';
      source='changed:'+stateFingerprint(s);"""
    if body.count(old)!=1:
        raise RuntimeError("V21.08 review branch anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""  function isResolved(s,d){
    if(!d)return false;
    if(d.sourceType==='event'||d.sourceType==='feedback')return resolved.has(d.reviewKey);
    if(resolved.has(d.stateKey)||resolved.has(d.reviewKey))return true;
    try{return !!window.__fjzIsReviewAckedV299?.(s)}catch(_e){return false}
  }"""
    new="""  function isResolved(s,d){
    if(!d)return false;
    if(d.sourceType==='event'||d.sourceType==='feedback')return resolved.has(d.reviewKey);
    if(baselineCurrentV308(s))return true;
    if(resolved.has(d.stateKey)||resolved.has(d.reviewKey))return true;
    try{return !!window.__fjzIsReviewAckedV299?.(s)}catch(_e){return false}
  }"""
    if body.count(old)!=1:
        raise RuntimeError("V21.08 isResolved anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""      const prefixes=[ITEM_PREFIX+'%',REVIEW_PREFIX+'%',STATE_PREFIX+'%','review-ack-v299:%'];
      const batches=await Promise.all(prefixes.map(async pattern=>{
        const {data,error}=await supabaseClient.from('coach_feed_state')
          .select('event_key,read_at,dismissed_at')
          .eq('coach_id',currentUser.id)
          .like('event_key',pattern);
        if(error)throw error;
        return data||[];
      }));
      read.clear();resolved.clear();
      batches.flat().forEach(x=>{
        const k=String(x?.event_key||'');if(!k)return;
        if(x.read_at)read.add(k);
        if(x.dismissed_at)resolved.add(k);
      });"""
    new="""      const prefixes=[ITEM_PREFIX+'%',REVIEW_PREFIX+'%',STATE_PREFIX+'%',BASE_PREFIX+'%','review-ack-v299:%'];
      const batches=await Promise.all(prefixes.map(async pattern=>{
        const {data,error}=await supabaseClient.from('coach_feed_state')
          .select('event_key,read_at,dismissed_at')
          .eq('coach_id',currentUser.id)
          .like('event_key',pattern);
        if(error)throw error;
        return data||[];
      }));
      read.clear();resolved.clear();legacyResolvedAthletes.clear();
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
      });"""
    if body.count(old)!=1:
        raise RuntimeError("V21.08 loadStates anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""  function rowFor(s){
    const p=active(s);if(!p)return null;
    const d=detail(s);if(isResolved(s,d))return null;
    center.set(String(s.id),d);return {s,p,d};
  }"""
    new="""  function rowFor(s){
    ensureLegacyBaselineV308(s);
    const p=active(s);if(!p)return null;
    const d=detail(s);if(isResolved(s,d))return null;
    center.set(String(s.id),d);return {s,p,d};
  }"""
    if body.count(old)!=1:
        raise RuntimeError("V21.08 rowFor anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    const keys=[lock,d.stateKey||stateKey(s),...(d.eventKeys||[])].filter(Boolean);
    const ok=await persist(keys,'ok');"""
    new="""    const keys=[lock,d.stateKey||stateKey(s),...(d.eventKeys||[])].filter(Boolean);
    if(d.sourceType==='state')keys.push(baselineKeyV308(s));
    const ok=await persist(keys,'ok');"""
    if body.count(old)!=1:
        raise RuntimeError("V21.08 resolve keys anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    resolved.add(lock);resolved.add(d.stateKey||stateKey(s));"""
    new="""    resolved.add(lock);resolved.add(d.stateKey||stateKey(s));if(d.sourceType==='state')resolved.add(baselineKeyV308(s));"""
    if body.count(old)!=1:
        raise RuntimeError("V21.08 resolved cache anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    version:'21.02',
    resolvedStateAuthoritative:true,"""
    new="""    version:'21.08',
    resolvedStateAuthoritative:true,
    stableBaselineAuthority:true,
    legacyResolvedMigration:true,
    noRepeatedFirstReview:true,"""
    if body.count(old)!=1:
        raise RuntimeError("V21.08 flags anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    return body

html=edit_script(html,"v302ReviewResolutionAuthorityRuntime",patch_v302)
html=html.replace("</head>",'<meta name="fjz-review-recurrence-fix" content="21.08">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V21.08 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-review-recurrence-fix" content="21.08"',
    "review-baseline-v308:",
    "stableBaselineAuthority:true",
    "legacyResolvedMigration:true",
    "noRepeatedFirstReview:true",
    "ensureLegacyBaselineV308",
    "baselineCurrentV308",
    "if(d.sourceType==='state')keys.push(baselineKeyV308(s))",
    "BASE_PREFIX+'%'",
    "first_review:'+athleteKeyV308(s)",
]:
    if marker not in html:
        raise RuntimeError("V21.08 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.08 review recurrence fix")
print("V21.08 BEFORE:",before)
print("V21.08 AFTER:",after)
