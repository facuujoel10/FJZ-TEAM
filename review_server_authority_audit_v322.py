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

v301=body("v301ReviewWorkflowProRuntime")
v302=body("v302ReviewResolutionAuthorityRuntime")
v304=body("v304GlobalSaveIntegrityRuntime")
v316=body("v316SessionLossProtectionRuntime")

checks={
 "release":tuple(map(int,release.split("."))) >= (21,22),
 "meta":'meta name="fjz-review-server-authority" content="21.22"' in html,
 "feed_readiness":"__fjzCoachFeedReadyV322=false" in html and "__fjzCoachFeedReadyV322=true" in html,
 "feed_repaint":"window.renderCoachPriorityCenterV252?.()" in html,
 "v301_fail_closed":"__fjzCoachFeedReadyV322!==true" in v301 and "if(!genuine)return null" in v301,
 "v302_final_authority":"realReviewSignalV322" in v302 and "serverFeedRequiredForReviewCardsV322:true" in v302,
 "cloud_fail_closed":"reviewCardsFailClosedUntilCloudReadyV322:true" in v302,
 "no_synthetic_priority":"syntheticPriorityCannotBecomeReviewV322:true" in v302,
 "authority_repaint":"cloudAuthorityRepaintsReviewCenterV322:true" in v302 and "try{refreshSurfaces()}catch(_e){}" in v302,
 "v319_preserved":"stableClientReviewAuthorityV319:true" in v302,
 "v321_preserved":"legacyFirstReviewSuppressedEverywhereV321:true" in v302,
 "geometry_preserved":'meta name="fjz-first-review-geometry-authority" content="21.21"' in html and ".set-grid>label>.v150-load-static" in html,
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
print("TEAM FJZ V21.22 SERVER REVIEW AUTHORITY AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.22 SERVER REVIEW AUTHORITY AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.22 stylesheet topology regression")
if metrics["renders"]>18: raise SystemExit("V21.22 render authority regression")
if metrics["channels"]>2: raise SystemExit("V21.22 realtime channel regression")
if metrics["intervals"]!=0: raise SystemExit("V21.22 interval regression")
if metrics["listeners"]>52: raise SystemExit("V21.22 listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.22 MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.22 PerformanceObserver regression")
print("TEAM FJZ V21.22 SERVER REVIEW AUTHORITY AUDIT OK")
