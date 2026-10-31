import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

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
  "release":tuple(map(int,release.split("."))) >= (21,34),
  "meta":'meta name="fjz-review-center-athlete-accordion" content="21.34"' in html,
  "runtime":'id="v331ProfessionalAlertGroupingRuntime"' in html,
  "athlete_first":"reviewCenterAthleteFirstV334:true" in html and 'class="v334-student-main"' in html,
  "collapsed_accordion":"alertsCollapsedByDefaultV333:true" in html and "professionalAccordionV334:true" in html,
  "all_alerts_expand":"allAthleteAlertsExpandedV334:true" in html and "g.rows.map(x=>rowHtml(x,{dismiss}))" in html,
  "no_old_row_limit":"slice(0,limit)" not in html and "limit=5" not in html and "limit:6" not in html,
  "dedupe_event_key":"groupRowsDedupesEventKeyV334:true" in html and "seen=new Map()" in html and "dedupeKey=athlete+'::'+identity" in html,
  "category_summary":'class="v334-category-strip"' in html and 'class="v334-category-chip"' in html,
  "readable_typography":"reviewCenterReadableTypographyV334:true" in html and ".v331-alert-student>strong" in html,
  "first_review_disabled":"firstReviewCardsDisabledV327:true" in html and "missingBaselineNeverCreatesReviewV327:true" in html,
  "save_integrity":"globalSaveIntegrity:true" in html and "successDeferredUntilVerified:true" in html,
  "session_integrity":"sessionSuccessRequiresDoubleVerification:true" in html and "snapshotAndProjectionConfirmation:true" in html,
  "comments_inbox":"trainingCommentsInboxPendingOnlyV330:true" in html and "reviewedCommentsLeaveDashboardV330:true" in html,
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

print("TEAM FJZ V21.34 REVIEW CENTER ATHLETE ACCORDION AUDIT")
print(json.dumps({
  "release":release,
  "checks":checks,
  "metrics":metrics,
  "hard_limits":hard_limits,
  "failed_checks":failed_checks,
  "failed_limits":failed_limits,
},indent=2,ensure_ascii=False))

if failed_checks or failed_limits:
  raise SystemExit("V21.34 REVIEW CENTER ATHLETE ACCORDION AUDIT FAILED")
print("TEAM FJZ V21.34 REVIEW CENTER ATHLETE ACCORDION AUDIT OK")
