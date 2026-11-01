import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def script_body(script_id):
    m=re.search(r'<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>(.*?)</script>',html,re.S|re.I)
    return m.group(1) if m else ""

v145=script_body("v145WorkoutAutosaveRuntime")
v207=script_body("v207ConfirmedSessionCommitRuntime")
v316=script_body("v316SessionLossProtectionRuntime")

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

begin=v207.find("function beginCommitV207(pack)")
validate_call=v207.find("const issue=validatePackV340(pack)",begin)
create_call=v207.find("createPendingV207(pack)",begin)

checks={
  "release":tuple(map(int,release.split("."))) >= (21,40),
  "meta":'meta name="fjz-session-input-recovery" content="21.40"' in html,

  "draft_started_at_saved":
    "let startedAtV340=null" in v145 and
    "startedAt:startedAtV340||new Date().toISOString()" in v145,
  "legacy_draft_time_fallback":
    "p?.startedAt||p?.updatedAt||null" in v145 and
    "72*60*60*1000" in v145,
  "draft_time_exported":"__fjzWorkoutStartedAtV340" in v145,

  "preflight_before_session_creation":
    begin>=0 and validate_call>begin and create_call>validate_call,
  "reps_matches_db_constraint":
    "Number.isInteger(reps)" in v207 and "reps<1||reps>200" in v207,
  "rir_matches_db_constraint":"rir<0||rir>10" in v207,
  "set_number_matches_db_constraint":"setNumber<1||setNumber>20" in v207,
  "invalid_never_reaches_cloud":
    "invalidSetNeverReachesCloudV340:true" in v207 and
    "modalInvalidPackV340(issue)" in v207,
  "specific_invalid_copy":
    "Revisá una serie antes de guardar" in v207 and
    "Parece que peso y repeticiones quedaron invertidos." in v207,
  "interactive_does_not_auto_swap":
    "swapEvidenceV340" in v207 and
    "set[0]=reps" not in v207,

  "recovery_reads_preserved_draft":
    "readLegacyDraftV340" in v316 and
    "fjz_workout_draft_v145:" in v316,
  "recovery_requires_strong_swap_evidence":
    "swapEvidenceRecoveryV340" in v316 and
    "priorLoad&&plausibleReps" in v316 and
    "strongSwapEvidenceRequiredV340:true" in v316,
  "no_blind_recovery":
    "noBlindAutoCorrectionV340:true" in v316 and
    "no hay evidencia suficiente" in v316,
  "recovery_updates_session_and_history":
    "set[0]=reps" in v316 and
    "set[1]=kg" in v316 and
    "repairHistorySetV340" in v316,
  "recovery_records_correction":
    "integrityCorrections" in v316 and
    "strong_load_reps_swap_evidence_v340" in v316,
  "recovery_uses_old_draft_time":
    "draft?.startedAt||draft?.updatedAt||null" in v316 and
    "session.date=recoveredDate" in v316,
  "recovery_cleans_stale_draft":
    "clearRecoveredDraftV340(pack)" in v316 and
    "fjz_v201_pending_session" in v316,

  "same_session_retry_preserved":"retryUsesSameSessionId:true" in v207,
  "duplicate_guard_preserved":"duplicateSaveByDesignBlocked:true" in v207,
  "double_verification_preserved":
    "snapshotAndProjectionConfirmation:true" in v316 and
    "sessionSuccessRequiresDoubleVerification:true" in v316,
  "global_save_integrity_preserved":"globalSaveIntegrity:true" in html,
  "review_center_preserved":
    'meta name="fjz-review-center-curtain" content="21.39"' in html and
    "reviewCenterCurtainV339:true" in html,
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

print("TEAM FJZ V21.40 SESSION INPUT + RECOVERY AUDIT")
print(json.dumps({
  "release":release,
  "checks":checks,
  "metrics":metrics,
  "hard_limits":hard_limits,
  "failed_checks":failed_checks,
  "failed_limits":failed_limits,
},indent=2,ensure_ascii=False))

if failed_checks or failed_limits:
    raise SystemExit("V21.40 SESSION INPUT + RECOVERY AUDIT FAILED")

print("TEAM FJZ V21.40 SESSION INPUT + RECOVERY AUDIT OK")
