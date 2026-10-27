import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\\.)?render\\s*=",doc)),
        "channels":doc.count(".channel("),
        "timeouts":doc.count("setTimeout("),
        "intervals":doc.count("setInterval("),
        "listeners":doc.count("addEventListener("),
        "mutation_observers":doc.count("new MutationObserver"),
        "performance_observers":doc.count("new PerformanceObserver"),
    }

def edit_script(doc,sid,fn):
    pat=re.compile(r'(<script[^>]*\\bid=["\\']'+re.escape(sid)+r'["\\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V21.21 missing script "+sid)
    body=fn(m.group(2))
    return doc[:m.start(2)]+body+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-first-review-authority" content="21.19"',
    'meta name="fjz-runtime-flow-cleanup" content="21.20"',
    'id="v175ProfileAgendaCoachCenterRuntime"',
    'id="v301ReviewWorkflowProRuntime"',
    'id="v302ReviewResolutionAuthorityRuntime"',
    'id="v150LoadModeRuntime"',
    "stableClientReviewAuthorityV319:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.21 prerequisite missing "+marker)

# ------------------------------------------------------------------
# 1) Permanent first-review authority for the oldest 360 review hub.
# ------------------------------------------------------------------
def patch_v175(body):
    old="""  function reviewChangeItemsV237(cur,prev){
    if(!prev)return [
      {tone:'info',title:'Primera revisión',body:'Todavía no hay una referencia anterior. Marcá esta revisión como completada para empezar a comparar cambios.'}
    ];"""
    new="""  function reviewChangeItemsV237(cur,prev){
    const reviewedInCloudV321=!!window.__fjzProfileReviewedStudentV319?.(student?.()?.id);
    if(!prev&&reviewedInCloudV321)return [
      {tone:'good',title:'Revisión al día',body:'La primera revisión ya está confirmada en la nube. Solo se muestran cambios nuevos reales.'}
    ];
    if(!prev)return [
      {tone:'info',title:'Primera revisión',body:'Todavía no hay una referencia anterior. Marcá esta revisión como completada para empezar a comparar cambios.'}
    ];"""
    if body.count(old)!=1:
        raise RuntimeError("V21.21 V237 first-review anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    const s=student(),prev=s?.coachReviewV237||null;
    const cloudReviewReady=!!window.__fjzFirstReviewAuthorityLoadedV319?.();"""
    new="""    const s=student(),prev=s?.coachReviewV237||null;
    const legacySnapshotMissingV321=!prev;
    const cloudReviewReady=!!window.__fjzFirstReviewAuthorityLoadedV319?.();"""
    if body.count(old)!=1:
        raise RuntimeError("V21.21 V237 render hub anchor mismatch")
    body=body.replace(old,new,1)

    old="""    if(cloudReviewed&&!prev){
      host.innerHTML='<div class="v237-review-head"><div><div class="v225-section-kicker">REVISIÓN DEL COACH</div><h4>Perfil 360 revisado</h4>'+"""
    new="""    if(cloudReviewed&&legacySnapshotMissingV321){
      host.innerHTML='<div class="v237-review-head"><div><div class="v225-section-kicker">REVISIÓN DEL COACH</div><h4>Perfil 360 revisado</h4>'+"""
    if body.count(old)!=1:
        raise RuntimeError("V21.21 V237 permanent reviewed anchor mismatch")
    body=body.replace(old,new,1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

# ------------------------------------------------------------------
# 2) Old V20.40 cadence must not invent a first review after cloud OK.
# ------------------------------------------------------------------
old_due="""function coachReviewDueV240(s){
  const days=coachReviewCadenceDaysV240(s);
  const reviewed=s?.coachReviewV237?.reviewedAt||null;
  if(!reviewed){
    return {due:true,days,cadenceDays:days,ageDays:999,remaining:0,label:'Sin revisión previa'};
  }"""
new_due="""function coachReviewDueV240(s){
  const days=coachReviewCadenceDaysV240(s);
  const reviewed=s?.coachReviewV237?.reviewedAt||null;
  const reviewedInCloudV321=!!window.__fjzProfileReviewedStudentV319?.(s?.id);
  if(!reviewed&&reviewedInCloudV321){
    return {due:false,days,cadenceDays:days,ageDays:0,remaining:days,label:'Perfil 360 revisado'};
  }
  if(!reviewed){
    return {due:true,days,cadenceDays:days,ageDays:999,remaining:0,label:'Sin revisión previa'};
  }"""
if html.count(old_due)!=1:
    raise RuntimeError("V21.21 V240 cadence anchor mismatch: "+str(html.count(old_due)))
html=html.replace(old_due,new_due,1)

# ------------------------------------------------------------------
# 3) Legacy V301 center cannot label a cloud-reviewed profile as first.
# ------------------------------------------------------------------
def patch_v301(body):
    old="""    const r=(()=>{try{return coachReviewLoopStateV238?.(s)||null}catch(_e){return null}})();let feedback=0;try{feedback=Number(pendingSessionFeedbackCountV243?.(s)||0)}catch(_e){}"""
    new="""    const r=(()=>{try{return coachReviewLoopStateV238?.(s)||null}catch(_e){return null}})();
    const reviewedV321=!!window.__fjzProfileReviewedStudentV319?.(s?.id);
    let feedback=0;try{feedback=Number(pendingSessionFeedbackCountV243?.(s)||0)}catch(_e){}"""
    if body.count(old)!=1:
        raise RuntimeError("V21.21 V301 detail prelude mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    else if(r?.reviewDue||!r?.hasBaseline){title=!r?.hasBaseline?'Primera revisión del alumno':'Revisión de seguimiento vencida';why=r?.reviewDueLabel||'No hay revisión de referencia.';look='Revisá el 360 completo: adherencia, últimas sesiones, check-in y progreso.'}"""
    new="""    else if(!reviewedV321&&(r?.reviewDue||!r?.hasBaseline)){title=!r?.hasBaseline?'Primera revisión del alumno':'Revisión de seguimiento vencida';why=r?.reviewDueLabel||'No hay revisión de referencia.';look='Revisá el 360 completo: adherencia, últimas sesiones, check-in y progreso.'}"""
    if body.count(old)!=1:
        raise RuntimeError("V21.21 V301 first-review branch mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""  function active(s){try{const p=coachPriorityStateV252?.(s)||{};return p.bucket==='urgent'||p.bucket==='today'?p:null}catch(_e){return null}}"""
    new="""  function active(s){
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
    if body.count(old)!=1:
        raise RuntimeError("V21.21 V301 active anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)
    return body

html=edit_script(html,"v301ReviewWorkflowProRuntime",patch_v301)

# ------------------------------------------------------------------
# 4) Final V302 authority: suppress state-only first/review_due generated
#    solely because the obsolete snapshot baseline is absent.
# ------------------------------------------------------------------
def patch_v302(body):
    old="""  function rowFor(s){
    ensureLegacyBaselineV308(s);
    const p=active(s);if(!p)return null;
    const d=detail(s);if(isResolved(s,d))return null;
    center.set(String(s.id),d);return {s,p,d};
  }"""
    new="""  function rowFor(s){
    ensureLegacyBaselineV308(s);
    const p=active(s);if(!p)return null;
    const d=detail(s);
    const reviewedV321=!!window.__fjzProfileReviewedStudentV319?.(s?.id);
    const suppressLegacyFirstReviewV321=reviewedV321&&!s?.coachReviewV237&&d?.sourceType==='state'&&/^(first_review|review_due):/.test(String(d?.source||''));
    if(suppressLegacyFirstReviewV321)return null;
    if(isResolved(s,d))return null;
    center.set(String(s.id),d);return {s,p,d};
  }"""
    if body.count(old)!=1:
        raise RuntimeError("V21.21 V302 rowFor anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    stableClientReviewAuthorityV319:true,
    firstReviewReadsCloudProfileKeyOnly:true,
    reviewedProfileCannotRegenerateDynamicBaseline:true,"""
    new="""    stableClientReviewAuthorityV319:true,
    firstReviewReadsCloudProfileKeyOnly:true,
    reviewedProfileCannotRegenerateDynamicBaseline:true,
    legacyFirstReviewSuppressedEverywhereV321:true,
    missingSnapshotBaselineCannotReopenReviewV321:true,"""
    if body.count(old)!=1:
        raise RuntimeError("V21.21 V302 flags anchor mismatch")
    body=body.replace(old,new,1)
    return body

html=edit_script(html,"v302ReviewResolutionAuthorityRuntime",patch_v302)

# ------------------------------------------------------------------
# 5) Workout geometry: CARGA / REPS / RIR / set number share one grid.
#    The static bodyweight cell must have the exact same geometry as inputs.
# ------------------------------------------------------------------
css=r"""
/* TEAM FJZ · V21.21 WORKOUT SET GEOMETRY */
.set-grid{
  grid-template-columns:44px minmax(0,1.28fr) minmax(0,.86fr) minmax(0,.86fr);
  gap:8px;
  align-items:end;
}
.set-grid>label{
  min-width:0;
  height:auto!important;
  min-height:0!important;
  display:grid;
  grid-template-rows:15px 44px;
  gap:5px;
  align-items:end;
  margin:0!important;
  line-height:1;
  text-align:center;
}
.set-grid>label>.input,
.set-grid>label>.v150-load-static{
  width:100%;
  height:44px!important;
  min-height:44px!important;
  max-height:44px!important;
  box-sizing:border-box;
  margin:0!important;
  border-radius:10px;
}
.set-grid>label>.input{
  padding:0 10px;
  text-align:center;
}
.set-grid>label>.v150-load-static{
  display:flex;
  align-items:center;
  justify-content:center;
  padding:0 8px;
  text-align:center;
  white-space:nowrap;
  font-size:10px;
  line-height:1;
  letter-spacing:.025em;
}
.set-grid>.set-n{
  width:100%;
  height:44px!important;
  min-height:44px!important;
  max-height:44px!important;
  align-self:end!important;
  box-sizing:border-box;
  margin:0!important;
  border-radius:10px;
}
@media(max-width:520px){
  .set-grid{
    grid-template-columns:42px minmax(0,1.32fr) minmax(0,.84fr) minmax(0,.84fr);
    gap:7px;
  }
  .set-grid>label{
    grid-template-rows:14px 44px;
    gap:4px;
  }
  .set-grid>label>.input{
    padding:0 7px;
  }
  .set-grid>label>.v150-load-static{
    padding:0 5px;
    font-size:9.5px;
    letter-spacing:.015em;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V21.21 expected one consolidated style block")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-first-review-geometry-authority" content="21.21">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V21.21 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-first-review-geometry-authority" content="21.21"',
    "reviewedInCloudV321",
    "legacyFirstReviewSuppressedEverywhereV321:true",
    "missingSnapshotBaselineCannotReopenReviewV321:true",
    "suppressLegacyFirstReviewV321",
    "reviewedV321&&!s?.coachReviewV237",
    "grid-template-rows:15px 44px",
    ".set-grid>label>.v150-load-static",
    ".set-grid>.set-n",
    "height:44px!important",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.21 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.21 first-review + workout geometry authority")
print("V21.21 BEFORE:",before)
print("V21.21 AFTER:",after)
