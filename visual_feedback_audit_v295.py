import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

required=[
 'meta name="fjz-visual-feedback-fix" content="20.95"',
 "singleCanonicalProfilePhoto:true",
 "reviewBadgeCentered:true",
 "workoutSetGeometryV295:true",
 "coachPreviewSessionFeedback:true",
 "feedbackSourceTagged:true",
 "submittedFromCoachPreview",
 "cleanupDuplicateProfilePhotosV295",
 "body:has(#v175CoachAvatarSlot) #v70CoachStudentAvatar",
 "body:has(#v268StudentAvatarPanel) #v70StudentProfile",
 "grid-template-columns:68px minmax(96px,1.25fr)",
 "justify-self:center!important",
 "mode==='student'&&(role==='student'||role==='coach'",
 "openSessionFeedbackV241(pack)",
 "¿Cómo salió la sesión?",
 "Molestia",
]
missing=[x for x in required if x not in html]

checks={
 "feedback_real_student_and_preview":"mode==='student'&&(role==='student'||role==='coach'" in html,
 "feedback_source_tagged":"submittedByRole:" in html and "submittedFromCoachPreview:" in html,
 "complete_finish_feedback":html.count("openSessionFeedbackV241(pack)")>=2,
 "feedback_before_commit":"sessionFeedbackAttachedBeforeCloudCommit:true" in html,
 "legacy_coach_photo_hidden":"body:has(#v175CoachAvatarSlot) #v70CoachStudentAvatar" in html,
 "legacy_student_photo_hidden":"body:has(#v268StudentAvatarPanel) #v70StudentProfile" in html,
 "workout_previous_aligned":".v205-prev-load" in html and "grid-row:2!important" in html,
 "workout_inputs_aligned":"grid-row:3!important" in html and "min-height:46px!important" in html,
 "meta_centered":".set-n>.v104-set-target" in html and "text-align:center!important" in html,
 "review_centered":".v238-review-badge" in html and "justify-self:center!important" in html,
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

print("TEAM FJZ V20.95 VISUAL/FEEDBACK AUDIT")
print(json.dumps({"release":release,"missing":missing,"checks":checks,"metrics":metrics},indent=2,ensure_ascii=False))

if tuple(map(int,release.split("."))) < (20,95): raise SystemExit("Release older than 20.95")
if missing: raise SystemExit("Missing V20.95 markers: "+repr(missing))
if not all(checks.values()): raise SystemExit("V20.95 behavior check failed: "+repr(checks))
if metrics["styles"]!=1: raise SystemExit("Stylesheet regression")
if metrics["renders"]>18: raise SystemExit("Render regression")
if metrics["intervals"]!=0: raise SystemExit("Interval regression")
if metrics["listeners"]>52: raise SystemExit("Listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("PerformanceObserver regression")

print("TEAM FJZ V20.95 VISUAL/FEEDBACK AUDIT OK")
