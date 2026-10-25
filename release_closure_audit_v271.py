import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

required=[
  'meta name="fjz-release" content="20.71"',
  'meta name="fjz-routine-library-preparation" content="20.69"',
  'meta name="fjz-mobile-edge-avatar-resilience" content="20.70"',
  'meta name="fjz-coach-student-preview-context" content="20.71"',
  "mainLibraryStrengthOnly:true",
  "preparationLibrarySeparated:true",
  "warmupBeforeWorkout:true",
  "stretchingAfterWorkout:true",
  "stableExerciseModalHeader:true",
  "mobileLibraryGeometry:true",
  "avatarCachedPathFallbackV270:true",
  "avatarEmptyStateExplicitV270:true",
  "coachStudentPreviewContextV271:true",
  "coachStudentPreviewOneTapExitV271:true",
  "coachStudentPreviewSynchronousV271:true",
  "VISTA PREVIA DEL ALUMNO",
  "Volver al panel Coach",
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
  "styles":len(re.findall(r"<style\b",html,re.I)),
  "render_assignments":len(re.findall(r"(?:window\.)?render\s*=",html)),
  "channels":len(re.findall(r"\.channel\s*\(",html)),
  "timeouts":len(re.findall(r"setTimeout\s*\(",html)),
  "rafs":len(re.findall(r"requestAnimationFrame\s*\(",html)),
  "listeners":len(re.findall(r"addEventListener\s*\(",html)),
  "mutation_observers":len(re.findall(r"new\s+MutationObserver",html)),
  "performance_observers":len(re.findall(r"new\s+PerformanceObserver",html)),
}

report={
  "release":release,
  "missing":missing,
  "forbidden_music_refs":bad,
  "metrics":metrics,
  "mobile_breakpoints":{
    "430":"@media(max-width:430px)" in html,
    "390":"@media(max-width:390px)" in html,
    "360":"@media(max-width:360px)" in html,
  },
}
print("TEAM FJZ V20.71 RELEASE CLOSURE AUDIT")
print(json.dumps(report,indent=2,ensure_ascii=False))

if release!="20.71":
  raise SystemExit("Release mismatch: "+release)
if missing:
  raise SystemExit("Missing final markers: "+repr(missing))
if bad:
  raise SystemExit("Music regression: "+repr(bad))
if metrics["styles"]!=1:
  raise SystemExit("Stylesheet regression")
if metrics["performance_observers"]!=0:
  raise SystemExit("PerformanceObserver regression")
if metrics["mutation_observers"]>3:
  raise SystemExit("MutationObserver regression")
if metrics["render_assignments"]>30:
  raise SystemExit("Render authority regression")

print("TEAM FJZ V20.71 RELEASE CLOSURE AUDIT OK")
