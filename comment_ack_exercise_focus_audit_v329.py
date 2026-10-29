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
v244=body("v244UnifiedSessionHistoryRuntime")
v302=body("v302ReviewResolutionAuthorityRuntime")
v304=body("v304GlobalSaveIntegrityRuntime")
v316=body("v316SessionLossProtectionRuntime")

checks={
 "release":tuple(map(int,release.split("."))) >= (21,29),
 "meta":'meta name="fjz-comment-ok-exercise-focus" content="21.29"' in html,
 "dashboard_ok":"__fjzAckTrainingCommentV329" in v302 and ">OK</button>" in v302,
 "dashboard_passes_identity":"feedbackId" in v302 and "exerciseUid" in v302 and "trainingCommentCarriesExerciseIdentityV329:true" in v302,
 "cloud_ok_verified":".update({" in v302 and ".select('id,status')" in v302 and ".single()" in v302 and "trainingCommentOkCloudVerifiedV329:true" in v302,
 "snapshot_status_sync":"row.status='reviewed'" in v302 and "trainingCommentSnapshotStatusSyncedV329:true" in v302,
 "session_comment_ok":"fb.status='reviewed'" in v302,
 "busy_lock":"trainingCommentAckBusyV329" in v302,
 "athlete_360_ok":"trainingCommentOkIn360V329:true" in v175 and "__fjzAckTrainingCommentV329" in v175,
 "exact_exercise_match":"commentFocusMatchesV329" in v244 and "exerciseFocusMatchesV329" in v244,
 "exact_comment_highlight":"v329-comment-target" in v244 and "exactExerciseCommentHighlightV329:true" in v244,
 "exercise_highlight":"v329-comment-exercise-focus" in v244,
 "comment_stays_below_exercise":"exerciseCommentHtmlV287(comments,ss,r)" in v244,
 "auto_scroll":"scrollIntoView" in v244 and "exactExerciseCommentAutoScrollV329:true" in v244,
 "v328_preserved":"trainingCommentOpensExactSessionV328:true" in v302 and "linkedCommentSessionBannerV328:true" in v244,
 "v327_preserved":"firstReviewCardsDisabledV327:true" in v302 and "missingBaselineNeverCreatesReviewV327:true" in v302,
 "save_intact":"globalSaveIntegrity:true" in v304 and "successDeferredUntilVerified:true" in v304,
 "session_guard_intact":"sessionSuccessRequiresDoubleVerification:true" in v316 and "snapshotAndProjectionConfirmation:true" in v316,
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
print("TEAM FJZ V21.29 COMMENT OK + EXACT EXERCISE FOCUS AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.29 COMMENT OK + EXACT EXERCISE FOCUS AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.29 stylesheet topology regression")
if metrics["renders"]>18: raise SystemExit("V21.29 render regression")
if metrics["channels"]>2: raise SystemExit("V21.29 channel regression")
if metrics["intervals"]!=0: raise SystemExit("V21.29 interval regression")
if metrics["listeners"]>52: raise SystemExit("V21.29 listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.29 MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.29 PerformanceObserver regression")
print("TEAM FJZ V21.29 COMMENT OK + EXACT EXERCISE FOCUS AUDIT OK")
