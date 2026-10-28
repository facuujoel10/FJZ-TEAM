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
v301=body("v301ReviewWorkflowProRuntime")
v302=body("v302ReviewResolutionAuthorityRuntime")
v304=body("v304GlobalSaveIntegrityRuntime")
v316=body("v316SessionLossProtectionRuntime")

checks={
 "release":tuple(map(int,release.split("."))) >= (21,27),
 "meta":'meta name="fjz-no-first-review-alerts" content="21.27"' in html,
 "v175_no_first_text":"Primera revisión" not in v175 and "Primera revisión del alumno" not in v175,
 "v301_no_first_text":"Primera revisión" not in v301 and "Primera revisión del alumno" not in v301,
 "v302_no_first_text":"Primera revisión" not in v302 and "Primera revisión del alumno" not in v302,
 "real_signal_only":"return hasFeed||feedback>0||((!!r.hasBaseline)&&!!r.changed)||((!!r.hasBaseline)&&!!r.reviewDue)" in v302,
 "missing_baseline_disabled":"missingBaselineNeverCreatesReviewV327:true" in v302,
 "first_cards_disabled":"firstReviewCardsDisabledV327:true" in v302,
 "new_students_need_activity":"newStudentsNeedRealActivityForReviewCardV327:true" in v302,
 "review_due_needs_baseline":"else if(effectiveHasBaseline&&r?.reviewDue)" in v302,
 "changed_needs_baseline":"else if(effectiveHasBaseline&&effectiveChanged)" in v302,
 "legacy_center_real_only":"const genuine=hasFeed||feedback>0||((!!r.hasBaseline)&&!!r.changed)||((!!r.hasBaseline)&&!!r.reviewDue)" in v301,
 "v326_writer_still_retired":"automaticDynamicBaselinePromotionRetiredV326:true" in v302,
 "server_feed_gate_preserved":"serverFeedRequiredForReviewCardsV322:true" in v302,
 "global_save_intact":"globalSaveIntegrity:true" in v304 and "successDeferredUntilVerified:true" in v304,
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
print("TEAM FJZ V21.27 NO FIRST REVIEW ALERTS AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.27 NO FIRST REVIEW ALERTS AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.27 stylesheet topology regression")
if metrics["renders"]>18: raise SystemExit("V21.27 render regression")
if metrics["channels"]>2: raise SystemExit("V21.27 channel regression")
if metrics["intervals"]!=0: raise SystemExit("V21.27 interval regression")
if metrics["listeners"]>52: raise SystemExit("V21.27 listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.27 MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.27 PerformanceObserver regression")
print("TEAM FJZ V21.27 NO FIRST REVIEW ALERTS AUDIT OK")
