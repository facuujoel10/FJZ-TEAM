import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

required=[
  'meta name="fjz-release" content="20.72"',
  'meta name="fjz-preparation-nutrition-calculator" content="20.72"',
  "singlePreparationAuthority:true",
  "legacyPrepExercisesMigrated:true",
  "warmupBeforeOnly:true",
  "stretchingAfterOnly:true",
  "coachMacroCalculator:true",
  "mifflinStJeor:true",
  "katchMcArdleOptional:true",
  "activityContext:true",
  "goalAdjustmentGuarded:true",
  "under18AutoTargetsBlocked:true",
  "applyTargetsRequiresCoachReview:true",
  "studentFoodCalculatorClarified:true",
  "Calculadora avanzada de macros",
  "Calculadora de alimentos y comidas",
  "Copiar al plan del alumno",
  "Para menores de 18 años",
  "productionNetworkBlocked:true",
  "syntheticDataOnly:true",
  "cloudDisabled:true",
]

missing=[x for x in required if x not in html]
metrics={
  "styles":len(re.findall(r"<style\b",html,re.I)),
  "render_assignments":len(re.findall(r"(?:window\.)?render\s*=",html)),
  "channels":len(re.findall(r"\.channel\s*\(",html)),
  "timeouts":len(re.findall(r"setTimeout\s*\(",html)),
  "rafs":len(re.findall(r"requestAnimationFrame\s*\(",html)),
  "listeners":len(re.findall(r"addEventListener\s*\(",html)),
  "mutation_observers":len(re.findall(r"new\s+MutationObserver",html)),
  "performance_observers":len(re.findall(r"new\s+PerformanceObserver",html)),
}
report={"release":release,"missing":missing,"metrics":metrics}
print("TEAM FJZ V20.72 PREPARATION/NUTRITION AUDIT")
print(json.dumps(report,indent=2,ensure_ascii=False))

if release!="20.72":
  raise SystemExit("Release mismatch: "+release)
if missing:
  raise SystemExit("Missing V20.72 markers: "+repr(missing))
if metrics["styles"]!=1:
  raise SystemExit("Stylesheet regression")
if metrics["performance_observers"]!=0:
  raise SystemExit("PerformanceObserver regression")
if metrics["mutation_observers"]>3:
  raise SystemExit("MutationObserver regression")
if metrics["render_assignments"]>30:
  raise SystemExit("Render authority regression")

print("TEAM FJZ V20.72 PREPARATION/NUTRITION AUDIT OK")
