import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

required=[
  'meta name="fjz-release" content="20.78"',
  'meta name="fjz-smart-alerts-progress" content="20.78"',
  "specificProgressAlerts:true",
  "genericProgressAlertSuppressedWhenSpecific:true",
  "smartAlertDedupByEventKey:true",
  "smartAlertReadDismissState:true",
  "weightTrendUsesMultipleRecords:true",
  "weightDirectionNeutral:true",
  "rirComparableExerciseLogic:true",
  "repeatedHighRirAlert:true",
  "repeatedLowRirFatigueSignal:true",
  "loadRepsVolumeAlerts:true",
  "clickableSmartAlerts:true",
  "professionalWeightChart:true",
  "targetWeightOnlyWhenExplicit:true",
  "exerciseMetricSelector:true",
  "loadRirCombinedChart:true",
  "fourWeekAdherenceChart:true",
  "athleteIntelligenceSummary:true",
  "noExtraTimers:true",
  "noExtraListeners:true",
  "noExtraObservers:true",
  "ALERTAS INTELIGENTES",
  "Carga × RIR",
  "RIR alto sostenido",
  "posible fatiga",
  "Peso estable",
  "v278SmartProgress",
  "v278AthleteIntel",
  "productionNetworkBlocked:true",
  "syntheticDataOnly:true",
  "cloudDisabled:true",
]
missing=[x for x in required if x not in html]

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
  "smooth_scroll":len(re.findall(r"behavior\s*:\s*['\"]smooth['\"]",html)),
  "transition_all":len(re.findall(r"transition\s*:\s*all\b",html,re.I)),
}

# Static threshold sanity: the runtime must require repeated evidence for the
# strongest RIR signals and multiple records for weight trend interpretation.
logic_checks={
  "high_rir_three_sessions":"last3.length===3" in html and "x.avgRir>=3.5" in html,
  "low_rir_repeated":"last2.length===2" in html and "x.avgRir<=.75" in html,
  "weight_multi_record":"recent.length<3" in html and "span<14" in html,
  "target_not_invented":"explicitTargetWeightV278" in html and "targetWeightOnlyWhenExplicit:true" in html,
  "generic_progress_filter":"progreso detectado" in html and "specificAthletes.has" in html,
  "dedup_event_key":"seen.has(x.event_key)" in html,
}

report={"release":release,"missing":missing,"logic_checks":logic_checks,"metrics":metrics}
print("TEAM FJZ V20.78 SMART ALERT/PROGRESS AUDIT")
print(json.dumps(report,indent=2,ensure_ascii=False))

if release!="20.78":
  raise SystemExit("Release mismatch: "+release)
if missing:
  raise SystemExit("Missing V20.78 markers: "+repr(missing))
if not all(logic_checks.values()):
  raise SystemExit("V20.78 logic sanity failed: "+repr(logic_checks))
if metrics["styles"]!=1:
  raise SystemExit("Stylesheet regression")
if metrics["intervals"]!=0:
  raise SystemExit("Unexpected interval loop")
if metrics["performance_observers"]!=0:
  raise SystemExit("PerformanceObserver regression")
if metrics["mutation_observers"]>3:
  raise SystemExit("MutationObserver regression")
if metrics["smooth_scroll"]!=0:
  raise SystemExit("Smooth-scroll regression")
if metrics["transition_all"]!=0:
  raise SystemExit("Geometry transition regression")

print("TEAM FJZ V20.78 SMART ALERT/PROGRESS AUDIT OK")
