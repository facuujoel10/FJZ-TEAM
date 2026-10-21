import pathlib,re,json,os

ROOT=pathlib.Path(__file__).resolve().parent
HTML=ROOT/"public"/"index.html"
if not HTML.exists():
    raise SystemExit("public/index.html missing")
html=HTML.read_text(encoding="utf-8")

def count(pattern,flags=0):
    return len(re.findall(pattern,html,flags))

metrics={
    "styles":count(r"<style\b",re.I),
    "render_assignments":count(r"(?:window\.)?render\s*="),
    "start_workout_assignments":count(r"(?:window\.)?startWorkout\s*="),
    "finish_workout_assignments":count(r"(?:window\.)?finishWorkout\s*="),
    "submit_checkin_authorities":count(r"window\.submitWeeklyCheckin\s*=\s*async\s+function"),
    "save_exercise_authorities":count(r"(?:window\.)?saveExercise\s*=\s*(?:async\s+)?function"),
    "realtime_channels":count(r"\.channel\s*\("),
    "mutation_observers":count(r"new\s+MutationObserver"),
    "performance_observers":count(r"new\s+PerformanceObserver"),
    "scroll_into_view":count(r"scrollIntoView\s*\("),
    "smooth_scroll_into_view":count(r'scrollIntoView\s*\([^)]*behavior\s*:\s*[\'"]smooth[\'"]',re.I|re.S),
}

required={
    "session_cloud_confirmation":"cloudConfirmationBeforeSuccess:true",
    "session_success_after_cloud":"successModalAfterConfirmedSave:true",
    "duplicate_save_blocked":"duplicateSaveByDesignBlocked:true",
    "retry_same_session":"retryUsesSameSessionId:true",
    "save_button_lock":"saveButtonLockedWhileSaving:true",
    "pending_marker_preserved":"pendingMarkerPreservedWhenLocalMissing:true",
    "pending_blocks_new_workout":"blocksNewWorkoutUntilReconciled:true",
    "partial_session_supported":"confirmPartialSessionV106",
    "checkin_cloud_confirmation":"checkinSuccessOnlyAfterCloudConfirmation:true",
    "checkin_single_authority":'meta name="fjz-consolidation-gate" content="20.56"',
    "professional_checkin_review":"professionalCheckinReview:true",
    "student_current_plan":'meta name="fjz-student-current-plan" content="20.58"',
    "calendar_real_checkin_source":"checkin_schedules",
    "calendar_next_due":"next_due",
    "calendar_realtime_source":"followupLoadedV122",
    "mobile_stability":'meta name="fjz-mobile-stability" content="20.55"',
    "reduced_motion":"prefers-reduced-motion",
    "auth_local_cleanup":"signOut({scope:'local'})",
    "auth_cloud_gate":"cloudTasksRequireFreshAuth:true",
    "auth_loop_guard":"invalidRefreshLoopGuard:true",
    "premium_polish":'meta name="fjz-premium-polish" content="20.62"',
    "preproduction_hardening":'meta name="fjz-preproduction-hardening" content="20.63"',
    "confirmed_save_feedback":'meta name="fjz-confirmed-save-feedback" content="20.64"',
    "release_candidate_geometry":'meta name="fjz-release-candidate-geometry" content="20.65"',
    "coach_athlete_workspace":'meta name="fjz-coach-athlete-workspace" content="20.66"',
    "coach_cockpit_music_removed":'meta name="fjz-coach-cockpit-music-removal" content="20.68"',
    "save_feedback_green":"greenConfirmedSaveFeedback:true",
    "routine_success_after_cloud":"routineSuccessAfterCloudSync:true",
    "no_false_green_pending":"noFalseGreenOnPendingSync:true",
}

missing=[k for k,v in required.items() if v not in html]

success_toasts=sorted(set(
    m.group(2) for m in re.finditer(
        r"toast(?:\?\.)?\(\s*(['\"])([^'\"]*(?:guardad|actualizad|cread|enviad|registrad|agregad|eliminad|marcad)[^'\"]*)\1\s*\)",
        html,re.I
    )
))

unexpected_success_toasts=[
    x for x in success_toasts
    if "pendiente" not in x.lower()
]

env=os.environ.get("TEAM_FJZ_ENV","production").strip().lower()
expected={
    "styles":1,
    # V20.68 removes two obsolete Music render wrappers.
    "render_assignments":18,
    "start_workout_assignments":12,
    "finish_workout_assignments":5,
    "submit_checkin_authorities":1,
    "save_exercise_authorities":1,
    "realtime_channels":2,
    "mutation_observers":3,
    "performance_observers":0,
}
mismatches={k:{"expected":v,"actual":metrics[k]} for k,v in expected.items() if metrics[k]!=v}

legacy={
    "legacy_agenda_channel":"fjz-v81-agenda" in html,
    "obsolete_student_next_step_call":"injectStudentNextStepV243();" in html,
    "global_invalid_refresh_cleanup":"invalid_refresh_token" in html and "signOut()" in html and "signOut({scope:'local'})" not in html,
}

print("TEAM FJZ V20.63 PREPRODUCTION AUDIT")
print(json.dumps({
    "env":env,
    "metrics":metrics,
    "missing":missing,
    "mismatches":mismatches,
    "legacy":legacy,
    "remaining_literal_success_toasts":success_toasts,
    "unexpected_literal_success_toasts":unexpected_success_toasts,
},indent=2,ensure_ascii=False))

if missing:
    raise SystemExit("Missing preproduction markers: "+", ".join(missing))
if mismatches:
    raise SystemExit("Authority/topology mismatch: "+json.dumps(mismatches,ensure_ascii=False))
if any(legacy.values()):
    raise SystemExit("Legacy/security regression: "+json.dumps(legacy,ensure_ascii=False))
if unexpected_success_toasts:
    raise SystemExit("Unstyled success toast regression: "+json.dumps(unexpected_success_toasts,ensure_ascii=False))
if metrics["smooth_scroll_into_view"]>0:
    raise SystemExit("Smooth scrollIntoView regression: "+str(metrics["smooth_scroll_into_view"]))

print("TEAM FJZ V20.63 PREPRODUCTION AUDIT OK")
