import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

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
}

checks={
  "release":tuple(map(int,release.split("."))) >= (21,36),
  "meta":'meta name="fjz-review-comment-hardening" content="21.36"' in html,
  "review_grouped_by_athlete":"reviewCenterAthleteFirstV334:true" in html and "allAthleteAlertsExpandedV334:true" in html,
  "accordion_collapsed":"alertsCollapsedByDefaultV333:true" in html and "__fjzToggleAlertGroupV333" in html,
  "grouped_ok_visible":"✓ OK" in html and "v336-alert-ok" in html,
  "grouped_ok_uses_review_authority":"groupedAlertOkUsesReviewAuthorityV336:true" in html and "dismissCoachAlertV96(key)" in html,
  "grouped_ok_readback":"groupedAlertCloudReadbackV336:true" in html and ".select('event_key,read_at,dismissed_at')" in html,
  "grouped_ok_busy_lock":"groupedAlertOkBusyLockV336:true" in html and "groupedAlertAckBusyV336" in html,
  "old_grouped_ocultar_removed":">Ocultar</button>" not in html,
  "session_comment_durable":"sessionCommentAckSnapshotVerifiedV333:true" in html and "sessionCommentAckReadbackV333:true" in html,
  "exercise_comment_durable":"exerciseCommentAckSnapshotVerifiedV336:true" in html and "exerciseCommentAckReadbackV336:true" in html,
  "exercise_comment_snapshot_helper":"persistExerciseCommentAckSnapshotV336" in html and "await persistExerciseCommentAckSnapshotV336" in html,
  "comments_pending_only":"trainingCommentsInboxPendingOnlyV330:true" in html and "reviewedCommentsLeaveDashboardV330:true" in html,
  "comment_exact_session":"trainingCommentOpensExactSessionV328:true" in html,
  "comment_exact_exercise":"exactExerciseCommentHighlightV329:true" in html and "exactExerciseCommentAutoScrollV329:true" in html,
  "first_review_disabled":"firstReviewCardsDisabledV327:true" in html and "missingBaselineNeverCreatesReviewV327:true" in html,
  "save_integrity":"globalSaveIntegrity:true" in html and "successDeferredUntilVerified:true" in html,
  "session_integrity":"sessionSuccessRequiresDoubleVerification:true" in html and "snapshotAndProjectionConfirmation:true" in html,
}

hard_limits={
  "styles":metrics["styles"]==1,
  "renders":metrics["renders"]<=18,
  "channels":metrics["channels"]<=2,
  "intervals":metrics["intervals"]==0,
  "listeners":metrics["listeners"]<=52,
  "mutation_observers":metrics["mutation_observers"]<=3,
  "performance_observers":metrics["performance_observers"]==0,
}

failed_checks=[k for k,v in checks.items() if not v]
failed_limits=[k for k,v in hard_limits.items() if not v]

print("TEAM FJZ V21.36 REVIEW + COMMENT ACK HARDENING AUDIT")
print(json.dumps({
  "release":release,
  "checks":checks,
  "metrics":metrics,
  "hard_limits":hard_limits,
  "failed_checks":failed_checks,
  "failed_limits":failed_limits,
},indent=2,ensure_ascii=False))

if failed_checks or failed_limits:
  raise SystemExit("V21.36 REVIEW + COMMENT ACK HARDENING AUDIT FAILED")
print("TEAM FJZ V21.36 REVIEW + COMMENT ACK HARDENING AUDIT OK")
