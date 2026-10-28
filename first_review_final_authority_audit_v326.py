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

s=v302.find("function ensureLegacyBaselineV308(s){")
e=v302.find("\n\n  function detail(s){",s)
baseline_fn=v302[s:e] if s>=0 and e>=0 else ""

checks={
 "release":tuple(map(int,release.split("."))) >= (21,26),
 "meta":'meta name="fjz-first-review-final-authority" content="21.26"' in html,
 "final_authority":"finalFirstReviewAuthorityV326:true" in v302,
 "cloud_ready_required":"firstReviewRequiresLoadedCloudAuthorityV326:true" in v302 and "canShowFirst" in v302,
 "reviewed_never_first":"reviewedProfileCanNeverBecomeFirstReviewV326:true" in v302,
 "auto_baseline_retired":"automaticDynamicBaselinePromotionRetiredV326:true" in v302 and "persist(" not in baseline_fn,
 "profile_guard_preserved":"if(profileReviewedV311(s))return false" in baseline_fn,
 "rowfor_no_preload_writer":"function rowFor(s){\n    const p=active(s);if(!p)return null;" in v302,
 "hub_fail_closed":"reviewHubFailsClosedUntilCloudReady:true" in v175 and "Sincronizando revisión…" in v175,
 "cadence_cloud_aware":"cadenceUsesCloudProfileReview:true" in v175 and "Perfil 360 revisado" in v175,
 "new_profiles_still_supported":"authorityReadyV326&&!reviewedInCloudV321" in v175 and "title:'Primera revisión'" in v175,
 "v319_preserved":"stableClientReviewAuthorityV319:true" in v302 and "__fjzProfileReviewedStudentV319" in v302,
 "v321_preserved":"legacyFirstReviewSuppressedEverywhereV321:true" in v302,
 "v322_preserved":"serverFeedRequiredForReviewCardsV322:true" in v302,
 "comments_preserved":"trainingCommentsCenterV325:true" in v302,
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
print("TEAM FJZ V21.26 FINAL FIRST REVIEW AUTHORITY AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.26 FINAL FIRST REVIEW AUTHORITY AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.26 stylesheet topology regression")
if metrics["renders"]>18: raise SystemExit("V21.26 render authority regression")
if metrics["channels"]>2: raise SystemExit("V21.26 realtime channel regression")
if metrics["intervals"]!=0: raise SystemExit("V21.26 interval regression")
if metrics["listeners"]>52: raise SystemExit("V21.26 listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.26 MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.26 PerformanceObserver regression")
print("TEAM FJZ V21.26 FINAL FIRST REVIEW AUTHORITY AUDIT OK")
