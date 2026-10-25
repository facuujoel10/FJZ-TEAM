import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def count(x): return html.count(x)

checks={
  # Workout finish -> feedback -> commit
  "feedback_function_present": count("function openSessionFeedbackV241(pack)") == 1,
  "feedback_modal_copy_present": all(x in html for x in [
      "¿Cómo salió la sesión?","¿Tuviste alguna dificultad?","Molestia",
      "Todo bien · finalizar","Enviar feedback y finalizar"
  ]),
  "complete_and_partial_finish_route_to_feedback": count("openSessionFeedbackV241(pack);") >= 2,
  "feedback_submit_commits": "window.submitSessionFeedbackV241=function(clear)" in html and "beginCommitV207(pack);" in html,
  "feedback_attached_before_cloud_commit":
      "session.sessionFeedback=cloneV207(pack.sessionFeedbackV241)" in html and
      "sessionFeedbackAttachedBeforeCloudCommit:true" in html,
  "coach_preview_can_open_feedback":
      "mode==='student'&&(role==='student'||role==='coach'" in html,
  "coach_preview_origin_tagged":
      "submittedFromCoachPreview:fromCoachPreview" in html and
      "status:fromCoachPreview?'reviewed':(needsCoach?'pending':'clear')" in html,
  "feedback_close_returns_without_commit":
      'onclick="cancelSessionFeedbackV241()"' in html,
  "confirmed_cloud_save_preserved":
      all(x in html for x in [
        "cloudConfirmationBeforeSuccess:true",
        "duplicateSaveByDesignBlocked:true",
        "retryUsesSameSessionId:true",
        "failedSaveRemainsRetryable:true",
        "Sesión guardada con éxito"
      ]),

  # Recent UI fixes
  "single_profile_photo_authority":
      "singleCanonicalProfilePhoto:true" in html and
      "cleanupDuplicateProfilePhotosV295" in html and
      "body:has(#v175CoachAvatarSlot) #v70CoachStudentAvatar" in html and
      "body:has(#v268StudentAvatarPanel) #v70StudentProfile" in html,
  "review_badge_centered":
      "reviewBadgeCentered:true" in html and "justify-self:center!important" in html,
  "workout_geometry_fixed":
      "workoutSetGeometryV295:true" in html and
      ".v205-prev-load" in html and ".set-n>.v104-set-target" in html,
  "single_coach_navigation":
      'meta name="fjz-single-coach-athlete-nav" content="20.92"' in html and
      "#v266CoachWorkspace .v266-quick-actions{" in html and
      "display:none!important;" in html,

  # Auth/password/session
  "password_recovery_hardened":
      all(x in html for x in [
        "resetPasswordForEmail","event==='PASSWORD_RECOVERY'",
        "window.__fjzRecoveryModeV293",'minlength="8"',
        "history.replaceState","El enlace de recuperación venció"
      ]),
  "session_resilience_active":
      all(x in html for x in [
        "@supabase/supabase-js@2.118.0/+esm",
        "signOut({scope:'local'})","recoverUnexpectedSignedOutV294",
        "showSessionRecoveryV294","handleSession=handleSessionV294",
        "No borramos tu sesión ni tus datos"
      ]),

  # Coach/student operational features
  "exercise_comments_in_session_review":
      all(x in html for x in [
        "exerciseCommentsVisiblePerSessionV287:true",
        "sessionExerciseFeedbackSnapshotV287",
        "exerciseCommentHtmlV287"
      ]),
  "checkin_success_present":
      "confirmedCheckinSuccess" in html or "checkinSuccess" in html or "Check-in guardado" in html,
  "pr_system_active":
      all(x in html for x in [
        "prBannerV291:true","robustPrDetectionV291:true",
        "prSessionDedupV291:true","prSafeStorageKeyV291:true",
        "NUEVO PESO · NUEVO PR"
      ]),
  "habit_history_date_aware":
      all(x in html for x in [
        "habitAssignmentDateAwareV291:true","habitEligibleOnV291"
      ]),
  "checkin_assistant_active":
      "ASISTENTE DE CHECK-IN" in html,
  "no_automatic_messages":
      not any(x in html for x in [
        "sendAutomaticMessageV290","sendAutomaticMessageV291",
        "scheduledMessageV291","automaticMessagingV291"
      ]),
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

limits={
 "styles":1,
 "renders":18,
 "channels":2,
 "intervals":0,
 "listeners":52,
 "mutation_observers":3,
 "performance_observers":0,
}

fail=[k for k,v in checks.items() if not v]
metric_fail=[]
for k,v in limits.items():
    cur=metrics[k]
    if k in ("renders","channels","listeners","mutation_observers"):
        if cur>v: metric_fail.append(f"{k}:{cur}>{v}")
    elif cur!=v:
        metric_fail.append(f"{k}:{cur}!={v}")

print("TEAM FJZ RECENT FEATURE REGRESSION AUDIT")
print(json.dumps({
  "release":release,
  "checks":checks,
  "metrics":metrics,
  "failed_checks":fail,
  "metric_failures":metric_fail
},indent=2,ensure_ascii=False))

if fail or metric_fail:
    raise SystemExit("RECENT FEATURE REGRESSION AUDIT FAILED")
print("TEAM FJZ RECENT FEATURE REGRESSION AUDIT OK")
