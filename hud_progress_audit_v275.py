import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()
is_staging_local='id="fjzStagingLocalRuntime"' in html

required=[
  'meta name="fjz-final-runtime-stability" content="20.74"',
  'meta name="fjz-mobile-hud-progress" content="20.75"',
  "premiumMobileHud:true",
  "hudFourPrimaryActions:true",
  "dedicatedTrainingHub:true",
  "progressOverview:true",
  "weightTrendOverview:true",
  "weeklyTrainingProgress:true",
  "goalContextWithoutBodyJudgement:true",
  "noExtraTimers:true",
  "noExtraListeners:true",
  "preparationPersistenceIntegratedV274:true",
  "keyboardHeightResizeIgnored:true",
  "noSmoothPrimaryScroll:true",
  "v275-student-hud",
  "renderTrainingHubV275",
  "v275ProgressOverview",
]
if is_staging_local:
  required += ["productionNetworkBlocked:true","syntheticDataOnly:true","cloudDisabled:true"]
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

print("TEAM FJZ V20.75 HUD/PROGRESS AUDIT")
print(json.dumps({"release":release,"missing":missing,"metrics":metrics},indent=2,ensure_ascii=False))

def version_tuple(v):
  try:
    return tuple(int(x) for x in v.split("."))
  except Exception:
    return (0,)

if version_tuple(release)<version_tuple("20.75"):
  raise SystemExit("Release older than V20.75 HUD baseline: "+release)
if missing:
  raise SystemExit("Missing V20.75 markers: "+repr(missing))
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

print("TEAM FJZ V20.75 HUD/PROGRESS AUDIT OK")
