import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()
m=re.search(r'<script[^>]*id=["\']v316SessionLossProtectionRuntime["\'][^>]*>(.*?)</script>',html,re.S|re.I)
body=m.group(1) if m else ""
checks={
 "release":tuple(map(int,release.split("."))) >= (21,16),
 "meta":'meta name="fjz-session-loss-protection" content="21.16"' in html,
 "runtime":bool(body),
 "explicit_delete_rpc":"delete_workout_session_v214" in html,
 "double_verify":"snapshotAndProjectionConfirmation:true" in body,
 "snapshot_read":".from('athlete_snapshots')" in body,
 "projection_read":".from('workout_sessions')" in body and "source_session_id" in body,
 "backup":"fjz_session_backup_v316:" in body,
 "legacy_closed_recovery":"fjz_v205_closed:" in body,
 "legacy_pending_recovery":"fjz_v201_pending_session" in body,
 "recovery_commit":"commit_workout_session_v202" in body,
 "success_gate":"sessionSuccessRequiresDoubleVerification:true" in body,
 "no_extra_timers":"noExtraTimers:true" in body,
 "no_extra_listeners":"noExtraListeners:true" in body,
 "no_extra_observers":"noExtraObservers:true" in body,
}
failed=[k for k,v in checks.items() if not v]
print("TEAM FJZ V21.16 SESSION LOSS PROTECTION AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.16 SESSION LOSS PROTECTION AUDIT FAILED")
print("TEAM FJZ V21.16 SESSION LOSS PROTECTION AUDIT OK")
