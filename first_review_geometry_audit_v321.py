import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def body(sid):
    for marker in ('id="'+sid+'"',"id='"+sid+"'"):
        mid=html.find(marker)
        if mid>=0:
            open_end=html.find(">",mid)
            close=html.find("</script>",open_end)
            if open_end>=0 and close>=0:
                return html[open_end+1:close]
    return ""

v175=body("v175ProfileAgendaCoachCenterRuntime")
v301=body("v301ReviewWorkflowProRuntime")
v302=body("v302ReviewResolutionAuthorityRuntime")
v304=body("v304GlobalSaveIntegrityRuntime")
v316=body("v316SessionLossProtectionRuntime")

checks={
  "release":tuple(map(int,release.split("."))) >= (21,21),
  "meta":'meta name="fjz-first-review-geometry-authority" content="21.21"' in html,
  "v237_cloud_guard":"reviewedInCloudV321" in v175 and "Revisión al día" in v175,
  "v301_first_review_guard":"reviewedV321" in v301 and "else if(!reviewedV321&&(r?.reviewDue||!r?.hasBaseline))" in v301,
  "v301_synthetic_priority_guard":"if(!hasFeed&&!feedback&&!r.changed&&!r.reviewDue)return null" in v301,
  "v302_final_suppression":"suppressLegacyFirstReviewV321" in v302 and "legacyFirstReviewSuppressedEverywhereV321:true" in v302,
  "v319_authority_preserved":"stableClientReviewAuthorityV319:true" in v302 and "firstReviewReadsCloudProfileKeyOnly:true" in v302 and "legacySnapshotCannotOverrideCloudReviewedState:true" in html,
  "bodyweight_geometry":".set-grid>label>.v150-load-static" in html and "grid-template-rows:15px 44px" in html,
  "set_number_geometry":".set-grid>.set-n" in html and "height:44px!important" in html,
  "mobile_geometry":"grid-template-columns:42px minmax(0,1.32fr) minmax(0,.84fr) minmax(0,.84fr)" in html,
  "global_save_intact":"globalSaveIntegrity:true" in v304 and "successDeferredUntilVerified:true" in v304,
  "session_protection_intact":"sessionSuccessRequiresDoubleVerification:true" in v316 and "snapshotAndProjectionConfirmation:true" in v316,
}
failed=[k for k,v in checks.items() if not v]

metrics={
 "styles":len(re.findall(r"<style\\b",html,re.I)),
 "renders":len(re.findall(r"(?:window\\.)?render\\s*=",html)),
 "channels":html.count(".channel("),
 "timeouts":html.count("setTimeout("),
 "intervals":html.count("setInterval("),
 "listeners":html.count("addEventListener("),
 "mutation_observers":html.count("new MutationObserver"),
 "performance_observers":html.count("new PerformanceObserver"),
}
print("TEAM FJZ V21.21 FIRST REVIEW + GEOMETRY AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.21 FIRST REVIEW + GEOMETRY AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.21 stylesheet topology regression")
if metrics["renders"]>18: raise SystemExit("V21.21 render authority regression")
if metrics["channels"]>2: raise SystemExit("V21.21 realtime channel regression")
if metrics["intervals"]!=0: raise SystemExit("V21.21 interval regression")
if metrics["listeners"]>52: raise SystemExit("V21.21 listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.21 MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.21 PerformanceObserver regression")
print("TEAM FJZ V21.21 FIRST REVIEW + GEOMETRY AUDIT OK")
