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

v244=body("v244UnifiedSessionHistoryRuntime")
v302=body("v302ReviewResolutionAuthorityRuntime")
v304=body("v304GlobalSaveIntegrityRuntime")
v316=body("v316SessionLossProtectionRuntime")

checks={
 "release":tuple(map(int,release.split("."))) >= (21,28),
 "meta":'meta name="fjz-comment-session-deeplink" content="21.28"' in html,
 "dashboard_button":"Ver sesión del día" in v302,
 "deeplink_routes_history":"coachStudentTab='history'" in v302,
 "deeplink_opens_session":"await window.sessionDetails(sid)" in v302,
 "target_must_exist":"const target=(Array.isArray(s?.sessions)?s.sessions:[])" in v302,
 "safe_missing_target":"missingCommentSessionFallsBackSafelyV328:true" in v302,
 "session_banner":"Esta es la sesión exacta donde dejó el comentario." in v244,
 "session_feedback_visible":"feedbackVisibleInHistory:true" in v244,
 "exercise_feedback_visible":"exerciseCommentsVisiblePerSessionV287:true" in v244,
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
print("TEAM FJZ V21.28 COMMENT SESSION DEEPLINK AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.28 COMMENT SESSION DEEPLINK AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.28 stylesheet topology regression")
if metrics["renders"]>18: raise SystemExit("V21.28 render regression")
if metrics["channels"]>2: raise SystemExit("V21.28 channel regression")
if metrics["intervals"]!=0: raise SystemExit("V21.28 interval regression")
if metrics["listeners"]>52: raise SystemExit("V21.28 listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.28 MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.28 PerformanceObserver regression")
print("TEAM FJZ V21.28 COMMENT SESSION DEEPLINK AUDIT OK")
