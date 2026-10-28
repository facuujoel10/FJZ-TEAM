import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def body(sid):
    for marker in ('id="'+sid+'"',"id='"+sid+"'"):
        mid=html.find(marker)
        if mid>=0:
            a=html.find(">",mid); b=html.find("</script>",a)
            if a>=0 and b>=0:return html[a+1:b]
    return ""

v175=body("v175ProfileAgendaCoachCenterRuntime")
v302=body("v302ReviewResolutionAuthorityRuntime")
v304=body("v304GlobalSaveIntegrityRuntime")
v316=body("v316SessionLossProtectionRuntime")

checks={
 "release":tuple(map(int,release.split("."))) >= (21,25),
 "meta":'meta name="fjz-training-comments-center" content="21.25"' in html,
 "dashboard_center":"v325TrainingCommentsCenter" in v302 and "trainingCommentsCenterV325:true" in v302,
 "dashboard_comment_text":"Lo que te dejaron tus alumnos" in v302 and "COMENTARIO DEL ENTRENAMIENTO" in v302,
 "student_summary":"v325StudentTrainingComments" in v175 and "dedicatedTrainingCommentsV325:true" in v175,
 "pending_first":"trainingCommentsPendingFirstV325:true" in v302 and "pendingCommentsFirstV325:true" in v175,
 "session_comments":"sessionFeedback" in v175 and "fb?.comment" in v175,
 "exercise_comments":"exerciseFeedback" in v175 and "exerciseFeedback" in v302,
 "coach_action":"Revisar y responder" in v175 and "openSessionFeedbackCoachV242" in v175,
 "review_authority_preserved":"serverFeedRequiredForReviewCardsV322:true" in v302 and "reviewFeedUsesAthleteKeyV308:true" in v302,
 "global_save_intact":"globalSaveIntegrity:true" in v304 and "successDeferredUntilVerified:true" in v304,
 "session_protection_intact":"sessionSuccessRequiresDoubleVerification:true" in v316 and "snapshotAndProjectionConfirmation:true" in v316,
}
failed=[k for k,v in checks.items() if not v]
metrics={
 "styles":html.lower().count("<style"),
 "renders":len(re.findall(r"(?:window\.)?render\s*=",html)),
 "channels":html.count(".channel("),
 "timeouts":html.count("setTimeout("),
 "intervals":html.count("setInterval("),
 "listeners":html.count("addEventListener("),
 "mutation_observers":html.count("new MutationObserver"),
 "performance_observers":html.count("new PerformanceObserver"),
}
print("TEAM FJZ V21.25 TRAINING COMMENTS CENTER AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.25 TRAINING COMMENTS CENTER AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.25 stylesheet topology regression")
if metrics["renders"]>18: raise SystemExit("V21.25 render authority regression")
if metrics["channels"]>2: raise SystemExit("V21.25 realtime channel regression")
if metrics["intervals"]!=0: raise SystemExit("V21.25 interval regression")
if metrics["listeners"]>52: raise SystemExit("V21.25 listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.25 MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.25 PerformanceObserver regression")
print("TEAM FJZ V21.25 TRAINING COMMENTS CENTER AUDIT OK")
