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
    if mid<0: raise RuntimeError("V21.27 missing script "+sid)
    a=doc.find(">",mid); b=doc.find("</script>",a)
    if a<0 or b<0: raise RuntimeError("V21.27 malformed script "+sid)
    body=doc[a+1:b]
    body=fn(body)
    return doc[:a+1]+body+doc[b:]

before=metrics(html)

for marker in [
    'meta name="fjz-first-review-final-authority" content="21.26"',
    'id="v175ProfileAgendaCoachCenterRuntime"',
    'id="v301ReviewWorkflowProRuntime"',
    'id="v302ReviewResolutionAuthorityRuntime"',
    "serverFeedRequiredForReviewCardsV322:true",
    "automaticDynamicBaselinePromotionRetiredV326:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.27 prerequisite missing "+marker)

# ------------------------------------------------------------
# 1) Legacy V301 visible center: missing baseline is never a review signal.
# ------------------------------------------------------------
def patch_v301(body):
    old="""      const reviewed=!!window.__fjzProfileReviewedStudentV319?.(s?.id);
      const genuine=hasFeed||feedback>0||!!r.changed||!!r.reviewDue||(!reviewed&&!r.hasBaseline);
      if(!genuine)return null;"""
    new="""      const genuine=hasFeed||feedback>0||((!!r.hasBaseline)&&!!r.changed)||((!!r.hasBaseline)&&!!r.reviewDue);
      if(!genuine)return null;"""
    if body.count(old)!=1:
        raise RuntimeError("V21.27 V301 genuine signal anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    else if(!reviewedV321&&(r?.reviewDue||!r?.hasBaseline)){title=!r?.hasBaseline?'Primera revisión del alumno':'Revisión de seguimiento vencida';why=r?.reviewDueLabel||'No hay revisión de referencia.';look='Revisá el 360 completo: adherencia, últimas sesiones, check-in y progreso.'}"""
    new="""    else if(r?.hasBaseline&&r?.reviewDue){title='Revisión de seguimiento vencida';why=r?.reviewDueLabel||'Hay un seguimiento programado pendiente.';look='Revisá el 360 completo: adherencia, últimas sesiones, check-in y progreso.'}"""
    if body.count(old)!=1:
        raise RuntimeError("V21.27 V301 first-review detail anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    else if(r?.changed){title='Cambios desde la última revisión';"""
    new="""    else if(r?.hasBaseline&&r?.changed){title='Cambios desde la última revisión';"""
    if body.count(old)!=1:
        raise RuntimeError("V21.27 V301 changed baseline anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)
    return body

html=edit_script(html,"v301ReviewWorkflowProRuntime",patch_v301)

# ------------------------------------------------------------
# 2) V302 final Review Center authority: only real changes/events/feedback.
# ------------------------------------------------------------
def patch_v302(body):
    old="""    const reviewed=!!window.__fjzProfileReviewedStudentV319?.(s?.id);
    return hasFeed||feedback>0||!!r.changed||!!r.reviewDue||(!reviewed&&!r.hasBaseline);"""
    new="""    return hasFeed||feedback>0||((!!r.hasBaseline)&&!!r.changed)||((!!r.hasBaseline)&&!!r.reviewDue);"""
    if body.count(old)!=1:
        raise RuntimeError("V21.27 V302 real signal anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    }else if(r?.reviewDue||(!effectiveHasBaseline&&firstReviewAuthorityV326(s).canShowFirst)){
      title=!effectiveHasBaseline?'Primera revisión del alumno':'Revisión de seguimiento vencida';
      why=r?.reviewDueLabel||(!effectiveHasBaseline?'No hay revisión de referencia.':'La revisión programada requiere atención.');
      look='Revisá el 360 completo: adherencia, últimas sesiones, check-in y progreso.';
      source=!effectiveHasBaseline?'first_review:'+athleteKeyV308(s):'review_due:'+stateFingerprint(s);"""
    new="""    }else if(effectiveHasBaseline&&r?.reviewDue){
      title='Revisión de seguimiento vencida';
      why=r?.reviewDueLabel||'La revisión programada requiere atención.';
      look='Revisá el 360 completo: adherencia, últimas sesiones, check-in y progreso.';
      source='review_due:'+stateFingerprint(s);"""
    if body.count(old)!=1:
        raise RuntimeError("V21.27 V302 first-review branch mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    }else if(effectiveChanged){
      title='Cambios desde la última revisión';"""
    new="""    }else if(effectiveHasBaseline&&effectiveChanged){
      title='Cambios desde la última revisión';"""
    if body.count(old)!=1:
        raise RuntimeError("V21.27 V302 changed baseline anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    flag="""    reviewedProfileCanNeverBecomeFirstReviewV326:true,"""
    if body.count(flag)!=1:
        raise RuntimeError("V21.27 V302 flags anchor mismatch")
    body=body.replace(flag,flag+"""
    firstReviewCardsDisabledV327:true,
    missingBaselineNeverCreatesReviewV327:true,
    reviewCenterRequiresRealSignalV327:true,
    newStudentsNeedRealActivityForReviewCardV327:true,""",1)
    return body

html=edit_script(html,"v302ReviewResolutionAuthorityRuntime",patch_v302)

# ------------------------------------------------------------
# 3) Oldest 360 review hub: remove "Primera revisión" wording entirely.
# ------------------------------------------------------------
def patch_v175(body):
    body=body.replace(
      "{tone:'good',title:'Revisión al día',body:'La primera revisión ya está confirmada en la nube. Solo se muestran cambios nuevos reales.'}",
      "{tone:'good',title:'Revisión al día',body:'El perfil ya está revisado. Solo se muestran cambios nuevos reales.'}"
    )
    body=body.replace(
      "{tone:'info',title:'Primera revisión',body:'Todavía no hay una revisión permanente confirmada para este perfil.'}",
      "{tone:'good',title:'Sin cambios pendientes',body:'Este espacio se activará cuando exista una señal nueva real para revisar.'}"
    )
    body=body.replace(
      "La primera revisión ya fue confirmada en la nube. Solo aparecerán nuevas revisiones por actividad nueva o una fecha real de seguimiento.",
      "El perfil ya fue revisado. Solo aparecerán nuevas revisiones por actividad nueva o una fecha real de seguimiento."
    )
    body=body.replace(
      "<strong>Sin primera revisión pendiente</strong>",
      "<strong>Sin revisiones pendientes</strong>"
    )
    if "title:'Primera revisión'" in body or "Primera revisión del alumno" in body:
        raise RuntimeError("V21.27 V175 still contains first-review UI text")
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

# ------------------------------------------------------------
# 4) Missing baseline must not increase priority/focus anywhere.
# ------------------------------------------------------------
old="""    (r.reviewDue?3:0)+
    (!r.hasBaseline?2:0);"""
new="""    ((r.hasBaseline&&r.reviewDue)?3:0);"""
if html.count(old)!=1:
    raise RuntimeError("V21.27 focus-score missing-baseline anchor mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

old="""  if(review.reviewDue||o.review||o.low||o.inactive||feed>0){"""
new="""  if((review.hasBaseline&&review.reviewDue)||o.review||o.low||o.inactive||feed>0){"""
if html.count(old)!=1:
    raise RuntimeError("V21.27 priority due anchor mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

old="""    if(review.reviewDue)reasons.push('revisión vencida');"""
new="""    if(review.hasBaseline&&review.reviewDue)reasons.push('revisión vencida');"""
if html.count(old)!=1:
    raise RuntimeError("V21.27 priority reason anchor mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

html=html.replace("</head>",'<meta name="fjz-no-first-review-alerts" content="21.27">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V21.27 topology changed "+key+": "+repr({"before":before,"after":after}))

# Final runtime invariants. Historical source files may still contain old text,
# but no active review surface is allowed to expose it.
def body_of(sid):
    for marker in ('id="'+sid+'"',"id='"+sid+"'"):
        mid=html.find(marker)
        if mid>=0:
            a=html.find(">",mid); b=html.find("</script>",a)
            return html[a+1:b]
    return ""

for sid in ["v175ProfileAgendaCoachCenterRuntime","v301ReviewWorkflowProRuntime","v302ReviewResolutionAuthorityRuntime"]:
    b=body_of(sid)
    if "Primera revisión" in b or "Primera revisión del alumno" in b:
        raise RuntimeError("V21.27 active runtime still exposes first-review text: "+sid)

for marker in [
    'meta name="fjz-no-first-review-alerts" content="21.27"',
    "firstReviewCardsDisabledV327:true",
    "missingBaselineNeverCreatesReviewV327:true",
    "reviewCenterRequiresRealSignalV327:true",
    "newStudentsNeedRealActivityForReviewCardV327:true",
    "return hasFeed||feedback>0||((!!r.hasBaseline)&&!!r.changed)||((!!r.hasBaseline)&&!!r.reviewDue)",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.27 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.27 no first-review alerts")
print("V21.27 BEFORE:",before)
print("V21.27 AFTER:",after)
