import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

required=[
  'meta name="fjz-final-stability-polish" content="20.79"',
  'meta name="fjz-smart-alerts-progress" content="20.78"',
  'meta name="fjz-final-save-geometry" content="20.77"',
  "feedRequestCoalescing:true",
  "dashboardHydrateCoalescing:true",
  "filterUsesCachedFeed:true",
  "manualRefreshStillForces:true",
  "progressAvoidsRedundantSecondRender:true",
  "athleteSummaryAvoidsRedundantSecondRender:true",
  "svgAspectPreserved:true",
  "mobileOverflowClip:true",
  "mobileAlertActionsNormalized:true",
  "confirmedSaveAuthorityPreserved:true",
  "duplicateAsyncSaveGuard:true",
  "buttonBusyState:true",
  "workoutFinishUsesConfirmedState:true",
  "checkinUsesConfirmedState:true",
  "nutritionSaveCloudConfirmed:true",
  "specificProgressAlerts:true",
  "smartAlertDedupByEventKey:true",
  "forceCoachAlertsV279",
  'preserveAspectRatio="xMidYMid meet"',
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

# Final focused logic checks.
v80_start=html.find("async function hydrateCoachDashboardV80(){")
v80_end=html.find("\nfunction renderCoachDashboardV80(){",v80_start)
v80=html[v80_start:v80_end] if v80_start>=0 and v80_end>v80_start else ""
logic={
  "dashboard_feed_not_force_on_filter":"loadCoachFeed(false)" in v80 and "loadCoachFeed(true)" not in v80,
  "explicit_force_refresh":'onclick="forceCoachAlertsV279()">Actualizar</button>' in html,
  "progress_stale_gate":"needsSmartCloud" in html and "needsTracking" in html,
  "athlete_intel_jobs_bounded":"if(!jobs.length)return;" in html and "athleteIntelInflightV279" in html,
  "feed_coalescer":"feedInflightV279&&!force" in html,
  "hydrate_coalescer":"attentionInflightV279" in html,
  "save_lock_retained":"const active=new Map();" in html and "v277-saving" in html,
  "mobile_360_rule":"@media(max-width:360px)" in html,
  "mobile_430_rule":"@media(max-width:430px)" in html,
}

report={"release":release,"missing":missing,"logic":logic,"metrics":metrics}
print("TEAM FJZ V20.79 FINAL STABILITY AUDIT")
print(json.dumps(report,indent=2,ensure_ascii=False))

def version_tuple(v):
  try:
    return tuple(int(x) for x in v.split("."))
  except Exception:
    return (0,)

if version_tuple(release)<version_tuple("20.79"):
  raise SystemExit("Release older than V20.79 final-stability baseline: "+release)
if missing:
  raise SystemExit("Missing V20.79 markers: "+repr(missing))
if not all(logic.values()):
  raise SystemExit("V20.79 logic audit failed: "+repr(logic))
if metrics["styles"]!=1:
  raise SystemExit("Stylesheet regression")
if metrics["renders"]>18:
  raise SystemExit("Render assignment regression")
if metrics["intervals"]!=0:
  raise SystemExit("Interval regression")
if metrics["listeners"]>52:
  raise SystemExit("Listener regression")
if metrics["mutation_observers"]>3:
  raise SystemExit("MutationObserver regression")
if metrics["performance_observers"]!=0:
  raise SystemExit("PerformanceObserver regression")
if metrics["smooth_scroll"]!=0:
  raise SystemExit("Smooth scroll regression")
if metrics["transition_all"]!=0:
  raise SystemExit("Geometry transition regression")

print("TEAM FJZ V20.79 FINAL STABILITY AUDIT OK")
