import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

metrics={
  "bytes":len(html.encode("utf-8")),
  "scripts":len(re.findall(r"<script\b",html,re.I)),
  "styles":len(re.findall(r"<style\b",html,re.I)),
  "render_assignments":len(re.findall(r"(?:window\.)?render\s*=",html)),
  "day_editor_assignments":len(re.findall(r"(?:window\.)?dayEditor\s*=",html)),
  "render_workout_assignments":len(re.findall(r"(?:window\.)?renderWorkout\s*=",html)),
  "channels":len(re.findall(r"\.channel\s*\(",html)),
  "timeouts":len(re.findall(r"setTimeout\s*\(",html)),
  "intervals":len(re.findall(r"setInterval\s*\(",html)),
  "rafs":len(re.findall(r"requestAnimationFrame\s*\(",html)),
  "listeners":len(re.findall(r"addEventListener\s*\(",html)),
  "mutation_observers":len(re.findall(r"new\s+MutationObserver",html)),
  "performance_observers":len(re.findall(r"new\s+PerformanceObserver",html)),
  "scroll_calls":len(re.findall(r"(?:scrollTo|scrollIntoView)\s*\(",html)),
  "smooth_scroll_refs":len(re.findall(r"behavior\s*:\s*['\"]smooth['\"]",html)),
  "transition_all_refs":len(re.findall(r"transition\s*:\s*all\b",html,re.I)),
}

required=[
  'meta name="fjz-release" content="20.74"',
  'meta name="fjz-final-runtime-stability" content="20.74"',
  "preparationPersistenceIntegratedV274:true",
  "preparationSaveCoalescedV274:true",
  "keyboardHeightResizeIgnored:true",
  "noSmoothPrimaryScroll:true",
  "routeScrollAuthority:true",
  "noSmoothPrimaryScroll:true",
  "modalRealtimeLock:true",
  "deferredRealtimeFlush:true",
  "productionNetworkBlocked:true",
  "syntheticDataOnly:true",
  "cloudDisabled:true",
]
missing=[x for x in required if x not in html]

forbidden=[
  'id="v273PreparationPersistenceRuntime"',
  "coachTab==='music'",
  "studentTab==='music'",
  "coachStudentTab==='music'",
  "new PerformanceObserver",
  "closest?.('.student-row,[data-client-id]')",
]

print("TEAM FJZ V20.74 FINAL STABILITY AUDIT")
print(json.dumps({
  "release":release,
  "missing":missing,
  "forbidden_present":[x for x in forbidden if x in html],
  "metrics":metrics,
},indent=2,ensure_ascii=False))

if release!="20.74":
  raise SystemExit("Release mismatch: "+release)
if missing:
  raise SystemExit("Missing V20.74 markers: "+repr(missing))
bad=[x for x in forbidden if x in html]
if bad:
  raise SystemExit("Forbidden stability regression: "+repr(bad))
if metrics["styles"]!=1:
  raise SystemExit("Stylesheet regression")
if metrics["performance_observers"]!=0:
  raise SystemExit("PerformanceObserver regression")
if metrics["mutation_observers"]>3:
  raise SystemExit("MutationObserver regression")
if metrics["render_assignments"]>30:
  raise SystemExit("Render authority regression")
if metrics["day_editor_assignments"]>9:
  raise SystemExit("Routine editor wrapper depth regression")
if metrics["intervals"]>0:
  raise SystemExit("Unexpected interval loop present")
if metrics["smooth_scroll_refs"]>0:
  raise SystemExit("Smooth-scroll regression")
if metrics["transition_all_refs"]>0:
  raise SystemExit("Geometry-wide transition regression")

print("TEAM FJZ V20.74 FINAL STABILITY AUDIT OK")
