import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

required=[
 'meta name="fjz-general-audit-hardening" content="20.96"',
 "coachPreviewFeedbackNotStudentPending:true",
 "coachPreviewFeedbackOriginVisible:true",
 "const fromCoachPreview=currentProfile?.role==='coach'&&mode==='student';",
 "status:fromCoachPreview?'reviewed':(needsCoach?'pending':'clear')",
 "submittedFromCoachPreview:fromCoachPreview",
 "cargado por Coach",
 "Coach · vista alumno",
 "sessionFeedbackAttachedBeforeCloudCommit:true",
 "cloudConfirmationBeforeSuccess:true",
 "duplicateSaveByDesignBlocked:true",
]
missing=[x for x in required if x not in html]

checks={
 "preview_does_not_create_pending_student_feedback":
   "const needsCoach=!fromCoachPreview&&!clear" in html and
   "status:fromCoachPreview?'reviewed':(needsCoach?'pending':'clear')" in html,
 "origin_visible_in_coach_review":
   "cargado por Coach" in html and "Coach · vista alumno" in html,
 "feedback_still_cloud_committed":
   "sessionFeedbackAttachedBeforeCloudCommit:true" in html and "__fjzQueueSessionSyncV201" in html,
 "save_guards_preserved":
   "retryUsesSameSessionId:true" in html and "duplicateSaveByDesignBlocked:true" in html,
}

metrics={
 "styles":len(re.findall(r"<style\b",html,re.I)),
 "renders":len(re.findall(r"(?:window\.)?render\s*=",html)),
 "channels":len(re.findall(r"\.channel\s*\(",html)),
 "timeouts":len(re.findall(r"setTimeout\s*\(",html)),
 "intervals":len(re.findall(r"setInterval\s*\(",html)),
 "listeners":len(re.findall(r"addEventListener\s*\(",html)),
 "mutation_observers":len(re.findall(r"new\s+MutationObserver",html)),
 "performance_observers":len(re.findall(r"new\s+PerformanceObserver",html)),
}

print("TEAM FJZ V20.96 GENERAL AUDIT HARDENING")
print(json.dumps({"release":release,"missing":missing,"checks":checks,"metrics":metrics},indent=2,ensure_ascii=False))

if tuple(map(int,release.split("."))) < (20,96): raise SystemExit("Release older than 20.96")
if missing: raise SystemExit("Missing V20.96 markers: "+repr(missing))
if not all(checks.values()): raise SystemExit("V20.96 behavior check failed: "+repr(checks))
if metrics["styles"]!=1: raise SystemExit("Stylesheet regression")
if metrics["renders"]>18: raise SystemExit("Render regression")
if metrics["intervals"]!=0: raise SystemExit("Interval regression")
if metrics["listeners"]>52: raise SystemExit("Listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("PerformanceObserver regression")

print("TEAM FJZ V20.96 GENERAL AUDIT HARDENING OK")
