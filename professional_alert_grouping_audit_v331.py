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
  "release":tuple(map(int,release.split("."))) >= (21,31),
  "meta":'meta name="fjz-professional-grouped-alerts" content="21.31"' in html,
  "runtime":'id="v331ProfessionalAlertGroupingRuntime"' in html,
  "grouped_by_athlete":"alertsGroupedByAthlete:true" in html and "function groupRows(rows)" in html,
  "dashboard_grouped":"dashboardSmartGrouped:true" in html and "Resumen por alumno" in html,
  "attention_grouped":"attentionCenterGrouped:true" in html and "renderAttentionItemsV80=groupedAttention" in html,
  "weight_current_kg":"weightAlertShowsCurrentKg:true" in html and "if(isWeight(x))return sm.current||'';" in html,
  "weight_prev_to_current":"weightAlertShowsPreviousToCurrent:true" in html and "prev+' → '+current" in html,
  "weight_no_percent_primary":"weightAlertAvoidsPercentAsPrimaryMetric:true" in html,
  "adherence_completed_vs_planned":"adherenceShowsCompletedVsPlanned:true" in html and "'Plan: '+prev" in html and "'Realizado: '+current" in html,
  "nutrition_days_primary":"nutritionShowsDaysNotPercentPrimary:true" in html,
  "exercise_metric_concrete":"exerciseAlertShowsConcreteMetric:true" in html,
  "group_priority":"groupSeverityPrioritized:true" in html,
  "first_review_still_disabled":"firstReviewCardsDisabledV327:true" in html and "missingBaselineNeverCreatesReviewV327:true" in html,
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

print("TEAM FJZ V21.31 PROFESSIONAL ALERT GROUPING AUDIT")
print(json.dumps({
  "release":release,
  "checks":checks,
  "metrics":metrics,
  "hard_limits":hard_limits,
  "failed_checks":failed_checks,
  "failed_limits":failed_limits,
},indent=2,ensure_ascii=False))

if failed_checks or failed_limits:
  raise SystemExit("V21.31 PROFESSIONAL ALERT GROUPING AUDIT FAILED")
print("TEAM FJZ V21.31 PROFESSIONAL ALERT GROUPING AUDIT OK")
