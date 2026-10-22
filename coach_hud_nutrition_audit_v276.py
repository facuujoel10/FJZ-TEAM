import pathlib,re,json,math

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

required=[
  'meta name="fjz-mobile-hud-progress" content="20.75"',
  'meta name="fjz-coach-hud-nutrition-detail" content="20.76"',
  "premiumCoachMobileHud:true",
  "coachHudFourPrimaryActions:true",
  "coachStudentTabsMobilePolished:true",
  "dailyNutritionStatus:true",
  "macroConsumedTargetRemaining:true",
  "perMealMacroTargets:true",
  "mealOptionMacroRanges:true",
  "expandedMealPresets:true",
  "calculatorMealsUpToEight:true",
  "calculatorEnergyCheckVisible:true",
  "visibleEnergyReconciliationV276:true",
  "mealCountUpToEightV276:true",
  "v276-coach-hud",
  "v276NutritionStatus",
  "openMealMacroTargetV276",
  "Media mañana",
  "Colación nocturna",
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

# Mifflin-St Jeor male sanity case: 80 kg, 180 cm, 30 years.
bmr_m=10*80+6.25*180-5*30+5
# Female equivalent.
bmr_f=10*80+6.25*180-5*30-161
# Katch-McArdle sanity case at 20% body fat.
lean=80*(1-.20)
bmr_k=370+21.6*lean
# Macro-energy reconciliation for a representative recomposition target.
tdee=bmr_m*1.45
target=tdee*.95
protein=80*1.9
fat=80*.8
carbs=(target-protein*4-fat*9)/4
macro_energy=protein*4+fat*9+carbs*4
formula_ok=(
  abs(bmr_m-1780.0)<1e-9
  and abs(bmr_f-1614.0)<1e-9
  and abs(bmr_k-1752.4)<1e-9
  and carbs>0
  and abs(macro_energy-target)<1e-6
)

report={"release":release,"missing":missing,"metrics":metrics,"calculator_formula_sanity":formula_ok}
print("TEAM FJZ V20.76 COACH HUD/NUTRITION AUDIT")
print(json.dumps(report,indent=2,ensure_ascii=False))

def version_tuple(v):
  try:
    return tuple(int(x) for x in v.split("."))
  except Exception:
    return (0,)

if version_tuple(release)<version_tuple("20.76"):
  raise SystemExit("Release older than V20.76 Coach/Nutrition baseline: "+release)
if missing:
  raise SystemExit("Missing V20.76 markers: "+repr(missing))
if not formula_ok:
  raise SystemExit("Macro calculator formula sanity failed")
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

print("TEAM FJZ V20.76 COACH HUD/NUTRITION AUDIT OK")
