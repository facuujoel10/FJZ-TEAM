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

v302=body("v302ReviewResolutionAuthorityRuntime")
v324=body("v324ReviewDashboardHydrationRuntime")
v304=body("v304GlobalSaveIntegrityRuntime")
v316=body("v316SessionLossProtectionRuntime")

checks={
 "release":tuple(map(int,release.split("."))) >= (21,24),
 "meta":'meta name="fjz-review-dashboard-hydration" content="21.24"' in html,
 "v302_uses_dashboard_readiness":"__fjzCanonicalCoachFeedReadyV324!==true" in v302,
 "v302_no_v96_block":"__fjzCoachFeedReadyV322!==true" not in v302,
 "stable_identity_preserved":"reviewFeedUsesAthleteKeyV308:true" in v302,
 "server_signal_preserved":"realReviewSignalV322" in v302 and "serverFeedRequiredForReviewCardsV322:true" in v302,
 "hydrate_wrapped":"window.hydrateCoachDashboardV80=wrapped" in v324,
 "hydrate_unlocks":"__fjzCanonicalCoachFeedReadyV324=true" in v324,
 "hydrate_repaints":"repaintReviewsV324();" in v324 and "renderCoachPriorityCenterV252" in v324,
 "existing_feed_unlock":"feedAlreadyHydratedV324()" in v324,
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
print("TEAM FJZ V21.24 REVIEW DASHBOARD HYDRATION AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.24 REVIEW DASHBOARD HYDRATION AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.24 stylesheet topology regression")
if metrics["renders"]>18: raise SystemExit("V21.24 render authority regression")
if metrics["channels"]>2: raise SystemExit("V21.24 realtime channel regression")
if metrics["intervals"]!=0: raise SystemExit("V21.24 interval regression")
if metrics["listeners"]>52: raise SystemExit("V21.24 listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.24 MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.24 PerformanceObserver regression")
print("TEAM FJZ V21.24 REVIEW DASHBOARD HYDRATION AUDIT OK")
