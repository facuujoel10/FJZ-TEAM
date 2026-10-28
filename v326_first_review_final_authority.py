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
    if mid<0:
        raise RuntimeError("V21.26 missing script "+sid)
    a=doc.find(">",mid); b=doc.find("</script>",a)
    if a<0 or b<0:
        raise RuntimeError("V21.26 malformed script "+sid)
    body=doc[a+1:b]
    body=fn(body)
    return doc[:a+1]+body+doc[b:]

before=metrics(html)

for marker in [
    'meta name="fjz-training-comments-center" content="21.25"',
    'id="v175ProfileAgendaCoachCenterRuntime"',
    'id="v302ReviewResolutionAuthorityRuntime"',
    "stableClientReviewAuthorityV319:true",
    "legacyFirstReviewSuppressedEverywhereV321:true",
    "serverFeedRequiredForReviewCardsV322:true",
    "reviewFeedUsesAthleteKeyV308:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.26 prerequisite missing "+marker)

def patch_v302(body):
    # Final cloud authority helper. A first review may only exist once cloud
    # review state has loaded and explicitly says this profile is unreviewed.
    anchor="""  function baselineSignalV308(s){"""
    helper=r"""
  function firstReviewAuthorityV326(s){
    const cloudRuntime=!!(cloudEnabled&&supabaseClient&&!window.__fjzStagingLocal?.enabled);
    const ready=!cloudRuntime||!!window.__fjzFirstReviewAuthorityLoadedV319?.();
    const reviewed=ready&&!!window.__fjzProfileReviewedStudentV319?.(s?.id);
    return {cloudRuntime,ready,reviewed,canShowFirst:ready&&!reviewed};
  }
  window.__fjzFirstReviewStateV326=function(s){return firstReviewAuthorityV326(s)};

"""
    if body.count(anchor)!=1:
        raise RuntimeError("V21.26 authority helper anchor mismatch: "+str(body.count(anchor)))
    body=body.replace(anchor,helper+anchor,1)

    # Retire the automatic V308 baseline promotion entirely. This was the
    # remaining writer that could run before cloud authority finished loading.
    start=body.find("  function ensureLegacyBaselineV308(s){")
    end=body.find("\n\n  function detail(s){",start)
    if start<0 or end<0:
        raise RuntimeError("V21.26 V308 automatic baseline function not found")
    retired="""  function ensureLegacyBaselineV308(s){
    const id=athleteKeyV308(s);
    if(profileReviewedV311(s))return false;
    if(!id||id==='unknown'||!legacyResolvedAthletes.has(id)||hasAnyBaselineV308(s))return false;
    // V21.26: historical baseline promotion is retired. First-review state is
    // now derived only from the permanent review-profile-v311 authority.
    return false;
  }"""
    body=body[:start]+retired+body[end:]

    # Never call the retired migration before the readiness gate.
    old="""  function rowFor(s){
    ensureLegacyBaselineV308(s);
    const p=active(s);if(!p)return null;"""
    new="""  function rowFor(s){
    const p=active(s);if(!p)return null;"""
    if body.count(old)!=1:
        raise RuntimeError("V21.26 rowFor pre-readiness baseline anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    # Even inside V302 itself, first review requires explicit loaded/unreviewed
    # cloud authority. This is defense-in-depth behind the active() gate.
    old="""    }else if(r?.reviewDue||!effectiveHasBaseline){
      title=!effectiveHasBaseline?'Primera revisión del alumno':'Revisión de seguimiento vencida';"""
    new="""    }else if(r?.reviewDue||(!effectiveHasBaseline&&firstReviewAuthorityV326(s).canShowFirst)){
      title=!effectiveHasBaseline?'Primera revisión del alumno':'Revisión de seguimiento vencida';"""
    if body.count(old)!=1:
        raise RuntimeError("V21.26 V302 first-review branch mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    flag="""    trainingCommentsUsesSessionSnapshotV325:true,"""
    if body.count(flag)!=1:
        raise RuntimeError("V21.26 V302 flag anchor mismatch")
    body=body.replace(flag,flag+"""
    finalFirstReviewAuthorityV326:true,
    automaticDynamicBaselinePromotionRetiredV326:true,
    firstReviewRequiresLoadedCloudAuthorityV326:true,
    reviewedProfileCanNeverBecomeFirstReviewV326:true,""",1)
    return body

html=edit_script(html,"v302ReviewResolutionAuthorityRuntime",patch_v302)

def patch_v175(body):
    # Oldest Review Hub: fail closed while cloud authority is loading.
    old="""  function reviewChangeItemsV237(cur,prev){
    const reviewedInCloudV321=!!window.__fjzProfileReviewedStudentV319?.(student?.()?.id);
    if(!prev&&reviewedInCloudV321)return [
      {tone:'good',title:'Revisión al día',body:'La primera revisión ya está confirmada en la nube. Solo se muestran cambios nuevos reales.'}
    ];
    if(!prev)return [
      {tone:'info',title:'Primera revisión',body:'Todavía no hay una referencia anterior. Marcá esta revisión como completada para empezar a comparar cambios.'}
    ];"""
    new="""  function reviewChangeItemsV237(cur,prev){
    const sV326=student?.();
    const cloudRuntimeV326=!!(cloudEnabled&&supabaseClient&&!window.__fjzStagingLocal?.enabled);
    const authorityReadyV326=!cloudRuntimeV326||!!window.__fjzFirstReviewAuthorityLoadedV319?.();
    const reviewedInCloudV321=authorityReadyV326&&!!window.__fjzProfileReviewedStudentV319?.(sV326?.id);
    if(!prev&&!authorityReadyV326)return [
      {tone:'info',title:'Sincronizando revisión…',body:'Comprobando el estado confirmado de este alumno antes de mostrar una revisión.'}
    ];
    if(!prev&&reviewedInCloudV321)return [
      {tone:'good',title:'Revisión al día',body:'La primera revisión ya está confirmada en la nube. Solo se muestran cambios nuevos reales.'}
    ];
    if(!prev&&authorityReadyV326&&!reviewedInCloudV321)return [
      {tone:'info',title:'Primera revisión',body:'Todavía no hay una revisión permanente confirmada para este perfil.'}
    ];
    if(!prev)return [
      {tone:'info',title:'Sincronizando revisión…',body:'Comprobando el estado confirmado de este alumno.'}
    ];"""
    if body.count(old)!=1:
        raise RuntimeError("V21.26 V237 final first-review guard mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    # Cadence helper must also fail closed. Previously a missing legacy
    # coachReviewV237 snapshot immediately meant "Sin revisión previa".
    start=body.find("function coachReviewDueV240(s){")
    end=body.find("\n\nfunction coachReviewCadenceLabelV240",start)
    if start<0 or end<0:
        raise RuntimeError("V21.26 coachReviewDueV240 function not found")
    cadence=r"""function coachReviewDueV240(s){
  const days=coachReviewCadenceDaysV240(s);
  const cloudRuntimeV326=!!(cloudEnabled&&supabaseClient&&!window.__fjzStagingLocal?.enabled);
  const authorityReadyV326=!cloudRuntimeV326||!!window.__fjzFirstReviewAuthorityLoadedV319?.();
  const cloudReviewedV326=authorityReadyV326&&!!window.__fjzProfileReviewedStudentV319?.(s?.id);

  if(cloudRuntimeV326&&!authorityReadyV326){
    return {due:false,days,cadenceDays:days,ageDays:0,remaining:days,label:'Sincronizando revisión…'};
  }
  if(cloudReviewedV326){
    return {due:false,days,cadenceDays:days,ageDays:0,remaining:days,label:'Perfil 360 revisado'};
  }

  const reviewed=s?.coachReviewV237?.reviewedAt||null;
  if(!reviewed){
    return {due:true,days,cadenceDays:days,ageDays:999,remaining:0,label:'Sin revisión previa'};
  }
  const age=coachDaysSinceV235(reviewed);
  const remaining=Math.max(0,days-age);
  return {
    due:age>=days,
    days,
    cadenceDays:days,
    ageDays:age,
    remaining,
    label:age>=days
      ?'Revisión vencida · '+age+' días'
      :'Próxima revisión en '+remaining+' días'
  };
}"""
    body=body[:start]+cadence+body[end:]

    # Expose diagnostics without adding any timers/listeners.
    end_i=body.rfind("})();")
    if end_i<0:
        raise RuntimeError("V21.26 V175 runtime end missing")
    expose=r"""
  window.__fjzLegacyReviewAuthorityV326={
    finalFirstReviewAuthority:true,
    cadenceUsesCloudProfileReview:true,
    reviewHubFailsClosedUntilCloudReady:true,
    legacySnapshotCannotCreateFirstReview:true
  };
"""
    body=body[:end_i]+expose+body[end_i:]
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

html=html.replace("</head>",'<meta name="fjz-first-review-final-authority" content="21.26">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V21.26 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-first-review-final-authority" content="21.26"',
    "finalFirstReviewAuthorityV326:true",
    "automaticDynamicBaselinePromotionRetiredV326:true",
    "firstReviewRequiresLoadedCloudAuthorityV326:true",
    "reviewedProfileCanNeverBecomeFirstReviewV326:true",
    "__fjzFirstReviewStateV326",
    "if(profileReviewedV311(s))return false",
    "historical baseline promotion is retired",
    "reviewHubFailsClosedUntilCloudReady:true",
    "cadenceUsesCloudProfileReview:true",
    "Sincronizando revisión…",
    "Perfil 360 revisado",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.26 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.26 final first-review authority")
print("V21.26 BEFORE:",before)
print("V21.26 AFTER:",after)
