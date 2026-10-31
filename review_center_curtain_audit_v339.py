import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def script_body(script_id):
    for marker in ('id="'+script_id+'"',"id='"+script_id+"'"):
        mid=html.find(marker)
        if mid>=0:
            a=html.find(">",mid); b=html.find("</script>",a)
            if a>=0 and b>=0:return html[a+1:b]
    return ""

v280=script_body("v280OperationalRecoveryRuntime")
v331=script_body("v331ProfessionalAlertGroupingRuntime")

metrics={
  "styles":len(re.findall(r"<style\b",html,re.I)),
  "renders":len(re.findall(r"(?:window\.)?render\s*=",html)),
  "channels":len(re.findall(r"\.channel\s*\(",html)),
  "timeouts":len(re.findall(r"setTimeout\s*\(",html)),
  "intervals":len(re.findall(r"setInterval\s*\(",html)),
  "rafs":len(re.findall(r"requestAnimationFrame\s*\(",html)),
  "listeners":len(re.findall(r"addEventListener\s*\(",html)),
  "mutation_observers":len(re.findall(r"new\s+MutationObserver",html)),
  "performance_observers":len(re.findall(r"new\s+PerformanceObserver",html)),
}

checks={
  "release":tuple(map(int,release.split("."))) >= (21,39),
  "meta":'meta name="fjz-review-center-curtain" content="21.39"' in html,
  "canonical_center_targeted":"CENTRO DE REVISIONES" in v280 and "reviewCenterCurtainV339:true" in v280,
  "one_card_per_student":"v339-review-student" in v280 and "data-v339-student" in v280,
  "toggle_only":"__fjzToggleReviewCurtainV339" in v280 and "__fjzMarkCoachReviewSeenV299" not in v280[v280.find("window.__fjzOpenPriorityV280=function"):v280.find("window.shiftCoachCalendarV280")],
  "all_feed_rows":"reviewFeedRowsV339" in v280 and "feed.map(a=>reviewAlertHtmlV339" in v280,
  "no_feed_slice_in_curtain":"feed.map(a=>reviewAlertHtmlV339" in v280 and "feed.slice(" not in v280[v280.find("function reviewFeedRowsV339"):v280.find("window.__fjzResolveReviewSyntheticV339")],
  "individual_ok":"__fjzResolveReviewCenterAlertV339" in v280 and "✓ OK" in v280,
  "individual_ok_uses_verified_authority":"__fjzResolveGroupedAlertV336(key,button)" in v280,
  "open_does_not_archive":"reviewCenterOpenDoesNotArchiveV339:true" in v280 and "window.__fjzOpenReviewAlertV339" in v280,
  "curtain_stays_open":"reviewCurtainOpenV339" in v280 and "renderPriority();" in v280,
  "secondary_surface_individual_ok":"individualOkRestoredV339:true" in v331 and "data-v336-ok-key" in v331,
  "bulk_ui_removed":"bulkOkUiRemovedV339:true" in v331 and "v338-athlete-alert-footer" not in v331[v331.find("function groupHtml"):v331.find("window.__fjzOpenGroupedAlertV331")],
  "v336_persistence_preserved":"groupedAlertCloudReadbackV336:true" in v331,
  "v337_progress_copy_preserved":"coachNeverSeesKgRepAsLoadV337:true" in v331,
  "first_review_disabled":"firstReviewCardsDisabledV327:true" in html and "missingBaselineNeverCreatesReviewV327:true" in html,
  "save_integrity":"globalSaveIntegrity:true" in html and "successDeferredUntilVerified:true" in html,
  "session_integrity":"sessionSuccessRequiresDoubleVerification:true" in html and "snapshotAndProjectionConfirmation:true" in html,
}

hard_limits={
  "styles":metrics["styles"]==1,
  "renders":metrics["renders"]<=18,
  "channels":metrics["channels"]<=2,
  "intervals":metrics["intervals"]==0,
  "listeners":metrics["listeners"]<=52,
  "mutation_observers":metrics["mutation_observers"]<=3,
  "performance_observers":metrics["performance_observers"]==0,
}

failed_checks=[k for k,v in checks.items() if not v]
failed_limits=[k for k,v in hard_limits.items() if not v]

print("TEAM FJZ V21.39 REVIEW CENTER CURTAIN AUDIT")
print(json.dumps({
  "release":release,
  "checks":checks,
  "metrics":metrics,
  "hard_limits":hard_limits,
  "failed_checks":failed_checks,
  "failed_limits":failed_limits,
},indent=2,ensure_ascii=False))

if failed_checks or failed_limits:
  raise SystemExit("V21.39 REVIEW CENTER CURTAIN AUDIT FAILED")
print("TEAM FJZ V21.39 REVIEW CENTER CURTAIN AUDIT OK")
