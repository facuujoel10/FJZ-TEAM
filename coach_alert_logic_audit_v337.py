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

v278=script_body("v278SmartAlertsProgressRuntime")
v331=script_body("v331ProfessionalAlertGroupingRuntime")
compare_start=v278.find("function compareExerciseV278")
compare_end=v278.find("function exerciseAlertsV278",compare_start)
v278_compare=v278[compare_start:compare_end] if compare_start>=0 and compare_end>compare_start else ""

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
  "release":tuple(map(int,release.split("."))) >= (21,37),
  "meta":'meta name="fjz-coach-alert-logic" content="21.37"' in html,
  "kg_rep_not_coach_facing":"kg·rep" not in v278_compare and "ambiguousVolumeAlertsSuppressedV337:true" in v331,
  "volume_titles_removed":"row.name+' · volumen" not in v278 and "'volume','success'" not in v278 and "'volume-down','warning'" not in v278,
  "reps_drop_alert":"'reps-down','warning'" in v278 and "Con una carga máxima y un RIR comparables" in v278,
  "reps_drop_uses_real_values":"reps totales" in v278 and "kg ×" in v278,
  "trend_uses_reps":"repsTrendUsesComparableContextV337:true" in v278 and "reps/sesión" in v278,
  "trend_requires_same_sets_and_load":"setsStable" in v278 and "loadStable" in v278 and "blockContext" in v278,
  "same_day_duplicate_suppressed":"exactSameDayExerciseDuplicateSuppressedV337:true" in v278 and "const duplicate=series.some" in v278,
  "volume_internal_only":"volumeKeptInternalOnlyV337:true" in v278,
  "panel_blocks_legacy_volume":"ambiguousVolumeAlertsSuppressedV337:true" in v331 and "metric.includes('volume')" in v331 and "kg\\s*[·x*]\\s*rep" in v331,
  "panel_labels_reps":"metric==='reps-down'" in v331 and "metric==='reps-trend'" in v331,
  "review_ok_preserved":"groupedAlertCloudReadbackV336:true" in html and "groupedAlertOkBusyLockV336:true" in html,
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

print("TEAM FJZ V21.37 COACH ALERT LOGIC AUDIT")
print(json.dumps({
  "release":release,
  "checks":checks,
  "metrics":metrics,
  "hard_limits":hard_limits,
  "failed_checks":failed_checks,
  "failed_limits":failed_limits,
},indent=2,ensure_ascii=False))

if failed_checks or failed_limits:
  raise SystemExit("V21.37 COACH ALERT LOGIC AUDIT FAILED")
print("TEAM FJZ V21.37 COACH ALERT LOGIC AUDIT OK")
