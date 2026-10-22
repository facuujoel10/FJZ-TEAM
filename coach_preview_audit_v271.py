import pathlib,json

html=pathlib.Path("public/index.html").read_text(encoding="utf-8")
required=[
  'meta name="fjz-coach-student-preview-context" content="20.71"',
  "coachPreviewSynchronousV271:true",
  "coachStudentPreviewContextV271:true",
  "coachStudentPreviewOneTapExitV271:true",
  "currentProfile?.role==='coach'&&mode==='student'",
  "__fjzEnsureCoachPreviewV271",
  "exitCoachStudentPreviewV271",
  "VISTA PREVIA DEL ALUMNO",
  "Volver al panel Coach",
  "TEAM FJZ · V20.71 COACH -> STUDENT PREVIEW CONTEXT",
  "@media(max-width:560px)",
  "@media(max-width:390px)",
]
missing=[x for x in required if x not in html]
report={
  "missing":missing,
  "v176_runtime_count":html.count('id="v176MobileTrackingMealsCleanupRuntime"'),
  "v268_runtime_count":html.count('id="v268CoachCockpitAvatarRuntime"'),
  "preview_marker_count":html.count("coachStudentPreviewContextV271:true"),
  "preview_is_coach_only":"currentProfile?.role==='coach'&&mode==='student'" in html,
}
print("TEAM FJZ V20.71 COACH PREVIEW AUDIT")
print(json.dumps(report,indent=2,ensure_ascii=False))
if missing:
  raise SystemExit("V20.71 missing: "+repr(missing))
if report["v176_runtime_count"]!=1 or report["v268_runtime_count"]!=1:
  raise SystemExit("V20.71 runtime authority regression")
if report["preview_marker_count"]!=1:
  raise SystemExit("V20.71 preview authority duplicated")
print("TEAM FJZ V20.71 COACH PREVIEW AUDIT OK")
