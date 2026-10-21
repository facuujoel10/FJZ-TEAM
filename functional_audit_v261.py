import pathlib
import re
import json
import os

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
    "realtime_channels":count(r"\.channel\s*\("),
    "timeouts":count(r"setTimeout\s*\("),
    "rafs":count(r"requestAnimationFrame\s*\("),
    "listeners":count(r"addEventListener\s*\("),
    "mutation_observers":count(r"new\s+MutationObserver"),
    "performance_observers":count(r"new\s+PerformanceObserver"),
    "submit_checkin_authorities":count(r"window\.submitWeeklyCheckin\s*=\s*async\s+function"),
    "save_exercise_authorities":count(r"(?:window\.)?saveExercise\s*=\s*(?:async\s+)?function"),
    "coach_dashboard_defs":count(r"function\s+renderCoachDashboardV80\s*\("),
    "calendar_render_defs":count(r"function\s+renderCoachCalendarV259\s*\("),
    "four_week_render_defs":count(r"function\s+renderCoachFourWeekV260\s*\("),
}

required={
    "confirmed_session_save":"cloudConfirmationBeforeSuccess:true",
    "pending_session_recovery":"pendingMarkerPreservedWhenLocalMissing:true",
    "confirmed_checkin_success":"confirmedCheckinSuccess:true",
    "professional_checkin_review":"professionalCheckinReview:true",
    "atomic_reorder":"modalReorderUsesAtomicRpc:true",
    "mobile_stability":'meta name="fjz-mobile-stability" content="20.55"',
    "consolidation_gate":'meta name="fjz-consolidation-gate" content="20.56"',
    "weekly_focus":'meta name="fjz-checkin-weekly-focus" content="20.57"',
    "student_current_plan":'meta name="fjz-student-current-plan" content="20.58"',
    "coach_calendar":'meta name="fjz-coach-action-calendar" content="20.59"',
    "coach_four_week":'meta name="fjz-coach-four-week-snapshot" content="20.60"',
    "premium_polish":'meta name="fjz-premium-polish" content="20.62"',
    "coach_cockpit_music_removed":'meta name="fjz-coach-cockpit-music-removal" content="20.68"',
    "calendar_review_cadence":"coachReviewCadenceDaysV240",
    "calendar_agenda_source":"athlete_reminders",
    "calendar_checkin_source":"checkin_schedules",
    "calendar_checkin_next_due":"next_due",
    "calendar_checkin_cache":"coachCalendarCheckinsV259",
    "calendar_action_router":"coachPriorityActionV259",
    "four_week_snapshot":"coachFourWeekStateV260",
    "agenda_realtime_delegated":"__fjzV81RealtimeDelegatedV218",
    "single_realtime_authority":"singleRealtimeAuthority:true",
}

missing=[name for name,marker in required.items() if marker not in html]

env=os.environ.get("TEAM_FJZ_ENV","production").strip().lower()

expected_exact={
    "styles":1,
    # V20.68 intentionally removes two obsolete Music render wrappers.
    "render_assignments":18,
    "start_workout_assignments":12,
    "finish_workout_assignments":5,
    "realtime_channels":2,
    "rafs":24,
    "mutation_observers":3,
    "performance_observers":0,
    "submit_checkin_authorities":1,
    "save_exercise_authorities":1,
    "coach_dashboard_defs":1,
    "calendar_render_defs":1,
    "four_week_render_defs":1,
}
if env=="staging-local":
    # Full staging artifact includes the local safety guard + final release runtime.
    expected_exact["timeouts"]=57
    expected_exact["listeners"]=52

mismatches={
    key:{"expected":value,"actual":metrics.get(key)}
    for key,value in expected_exact.items()
    if metrics.get(key)!=value
}

legacy={
    "legacy_agenda_channel":"fjz-v81-agenda" in html,
    "obsolete_student_next_step_call":"injectStudentNextStepV243();" in html,
}

print("TEAM FJZ V20.61 FUNCTIONAL AUDIT")
print(json.dumps({
    "metrics":metrics,
    "missing":missing,
    "mismatches":mismatches,
    "legacy":legacy,
},indent=2,ensure_ascii=False))

if missing:
    raise SystemExit("Missing functional markers: "+", ".join(missing))
if mismatches:
    raise SystemExit("Authority/topology mismatch: "+json.dumps(mismatches,ensure_ascii=False))

# Outside staging-local, guard final runtime growth with ceilings rather than
# comparing against the pre-release V20.56 intermediate checkpoint.
if env!="staging-local":
    if metrics["timeouts"]>57:
        raise SystemExit("Timeout regression: "+str(metrics["timeouts"]))
    if metrics["listeners"]>52:
        raise SystemExit("Listener regression: "+str(metrics["listeners"]))

if any(legacy.values()):
    raise SystemExit("Legacy regression detected: "+json.dumps(legacy,ensure_ascii=False))

print("TEAM FJZ V20.61 FUNCTIONAL AUDIT OK")
