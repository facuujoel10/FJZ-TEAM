import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

required=[
  'meta name="fjz-final-save-geometry" content="20.77"',
  "greenConfirmedSaveFeedback:true",
  "confirmedCheckinSuccess:true",
  "finalSaveConfirmationAudit:true",
  "greenCheckOnConfirmedSaves:true",
  "duplicateAsyncSaveGuard:true",
  "buttonBusyState:true",
  "workoutFinishUsesConfirmedState:true",
  "checkinUsesConfirmedState:true",
  "nutritionSaveCloudConfirmed:true",
  "symmetryGeometryPass:true",
  "mobile360GeometryPass:true",
  "__fjzConfirmSavedV264",
  "__fjzQuickSavedV264",
  "v277-saving",
  "saveNutritionPlan",
  "submitMeasurement",
  "submitWeeklyCheckin",
  "finishWorkout",
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

toast_pat=re.compile(r"toast(?:\?\.)?\(\s*(['\"])(?P<msg>[^'\"]+)\1\s*\)")
success_rx=re.compile(r"(guardad[oa]s?|finalizad[oa]s?|enviad[oa]s?|registrad[oa]s?|cread[oa]s?|actualizad[oa]s?|publicad[oa]s?|confirmad[oa]s?)",re.I)
skip_rx=re.compile(r"(guardá el plan|guardado en curso|localmente|sincronización pendiente|pendiente|sin guardar|revisá|copiados? al plan)",re.I)
remaining=[
  m.group("msg") for m in toast_pat.finditer(html)
  if success_rx.search(m.group("msg")) and not skip_rx.search(m.group("msg"))
]

report={"release":release,"missing":missing,"remaining_success_toasts":sorted(set(remaining)),"metrics":metrics}
print("TEAM FJZ V20.77 FINAL SAVE/GEOMETRY AUDIT")
print(json.dumps(report,indent=2,ensure_ascii=False))

def version_tuple(v):
  try:
    return tuple(int(x) for x in v.split("."))
  except Exception:
    return (0,)

if version_tuple(release)<version_tuple("20.77"):
  raise SystemExit("Release older than V20.77 save/geometry baseline: "+release)
if missing:
  raise SystemExit("Missing V20.77 markers: "+repr(missing))
if remaining:
  raise SystemExit("Unstandardized successful save toasts: "+repr(sorted(set(remaining))))
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

print("TEAM FJZ V20.77 FINAL SAVE/GEOMETRY AUDIT OK")
