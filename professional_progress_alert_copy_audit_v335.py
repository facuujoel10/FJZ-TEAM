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
  "release":tuple(map(int,release.split("."))) >= (21,35),
  "meta":'meta name="fjz-professional-progress-alert-copy" content="21.35"' in html,
  "source_runtime":'id="v278SmartAlertsProgressRuntime"' in html,
  "panel_runtime":'id="v331ProfessionalAlertGroupingRuntime"' in html,
  "concrete_copy":"concreteProgressCopyV335:true" in html,
  "percentage_only_generic_suppressed":"percentageOnlyProgressSuppressedV335:true" in html and "percentageOnlyProgress=" in html,
  "load_uses_kg":"loadAlertsUseKgDeltaV335:true" in html and "Progreso de carga consistente" in html,
  "volume_absolute":"volumeAlertsUseAbsoluteWorkV335:true" in html and "blockDiff" in html and "kg·rep" in html,
  "adherence_counts":"adherenceNutritionUseCountsV335:true" in html and "Frecuencia cumplida" in html,
  "nutrition_counts":"Semana completa" in html and "días con registro" in html,
  "coach_reading":"coachReadingLabelV335:true" in html and "Lectura coach" in html,
  "structured_facts":"progressFactsStructuredV335:true" in html and "v335-progress-facts" in html and "Anterior" in html and "Actual" in html and "Cambio" in html,
  "percent_hidden_in_panel":"progressPercentHiddenFromCoachV335:true" in html and "rawDelta" in html,
  "old_fatigue_percent_removed":"+'% volumen'" not in html,
  "old_volume_title_percent_removed":"row.name+' · volumen +'+fmtV278(blockPct,0)+'%'" not in html,
  "old_adherence_percent_removed":"Math.round(done/planned*100)+'%'" not in html,
  "old_nutrition_percent_removed":"Math.round(days/7*100)+'%'" not in html,
  "first_review_disabled":"firstReviewCardsDisabledV327:true" in html and "missingBaselineNeverCreatesReviewV327:true" in html,
  "review_center_v334":"reviewCenterAthleteFirstV334:true" in html and "allAthleteAlertsExpandedV334:true" in html,
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

print("TEAM FJZ V21.35 PROFESSIONAL PROGRESS ALERT COPY AUDIT")
print(json.dumps({
  "release":release,
  "checks":checks,
  "metrics":metrics,
  "hard_limits":hard_limits,
  "failed_checks":failed_checks,
  "failed_limits":failed_limits,
},indent=2,ensure_ascii=False))

if failed_checks or failed_limits:
  raise SystemExit("V21.35 PROFESSIONAL PROGRESS ALERT COPY AUDIT FAILED")
print("TEAM FJZ V21.35 PROFESSIONAL PROGRESS ALERT COPY AUDIT OK")
