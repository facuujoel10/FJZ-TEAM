import pathlib,re,json,math

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

required=[
  'meta name="fjz-release" content="20.73"',
  'meta name="fjz-routine-library-preparation" content="20.69"',
  'meta name="fjz-mobile-edge-avatar-resilience" content="20.70"',
  'meta name="fjz-coach-student-preview-context" content="20.71"',
  'meta name="fjz-preparation-nutrition-calculator" content="20.72"',
  'meta name="fjz-preparation-nutrition-hardening" content="20.73"',
  "mainLibraryStrengthOnly:true",
  "preparationLibrarySeparated:true",
  "warmupBeforeWorkout:true",
  "stretchingAfterWorkout:true",
  "preparationMigrationPersisted:true",
  "mixedGoalDetectsRecomposition:true",
  "latestWeightCloudFallback:true",
  "calculatorStrictBounds:true",
  "currentPlanDelta:true",
  "unsafeAutoApplyBlocked:true",
  "macroEnergyReconciled:true",
  "under18AutoTargetsBlocked:true",
  "applyTargetsRequiresCoachReview:true",
  "Calculadora avanzada de macros",
  "Calculadora de alimentos y comidas",
  "productionNetworkBlocked:true",
  "syntheticDataOnly:true",
  "cloudDisabled:true",
]
forbidden=[
  "coachTab==='music'",
  "studentTab==='music'",
  "coachStudentTab==='music'",
  "renderGlobalMusicCoachV69",
  "saveGlobalSpotifyV69",
  "renderSpotifyStudentV69",
  "saveSpotifyV68",
  "coach_media_settings",
  "__fjzV69MediaChannel",
]
missing=[x for x in required if x not in html]
bad=[x for x in forbidden if x in html]

metrics={
  "styles":len(re.findall(r"<style\\b",html,re.I)),
  "render_assignments":len(re.findall(r"(?:window\\.)?render\\s*=",html)),
  "channels":len(re.findall(r"\\.channel\\s*\\(",html)),
  "timeouts":len(re.findall(r"setTimeout\\s*\\(",html)),
  "rafs":len(re.findall(r"requestAnimationFrame\\s*\\(",html)),
  "listeners":len(re.findall(r"addEventListener\\s*\\(",html)),
  "mutation_observers":len(re.findall(r"new\\s+MutationObserver",html)),
  "performance_observers":len(re.findall(r"new\\s+PerformanceObserver",html)),
}

# Formula sanity check mirrors the documented adult Mifflin + residual-carb model.
weight,height,age=80.0,180.0,30.0
bmr=10*weight+6.25*height-5*age+5
factor=1.332
tdee=bmr*factor
target=tdee*.95
protein=1.9*weight
fat=.8*weight
carbs=(target-protein*4-fat*9)/4
energy=protein*4+fat*9+carbs*4
formula_ok=(abs(bmr-1780.0)<1e-9 and carbs>0 and abs(energy-target)<1e-6)

report={
  "release":release,
  "missing":missing,
  "forbidden_music_refs":bad,
  "metrics":metrics,
  "formula_sanity":formula_ok,
}
print("TEAM FJZ V20.73 FINAL HARDENING AUDIT")
print(json.dumps(report,indent=2,ensure_ascii=False))

if release!="20.73":
  raise SystemExit("Release mismatch: "+release)
if missing:
  raise SystemExit("Missing V20.73 markers: "+repr(missing))
if bad:
  raise SystemExit("Music regression: "+repr(bad))
if not formula_ok:
  raise SystemExit("Macro formula sanity regression")
if metrics["styles"]!=1:
  raise SystemExit("Stylesheet regression")
if metrics["performance_observers"]!=0:
  raise SystemExit("PerformanceObserver regression")
if metrics["mutation_observers"]>3:
  raise SystemExit("MutationObserver regression")
if metrics["render_assignments"]>30:
  raise SystemExit("Render authority regression")

print("TEAM FJZ V20.73 FINAL HARDENING AUDIT OK")
