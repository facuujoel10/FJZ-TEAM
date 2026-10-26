import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def script_body(sid):
    marker='id="'+sid+'"'
    mid=html.find(marker)
    if mid<0:return ""
    start=html.find(">",mid);end=html.find("</script>",start)
    return html[start+1:end] if start>=0 and end>=0 else ""

v312=script_body("v312ReviewAgendaAuthorityRuntime")
v314=script_body("v314OperationalIntegrityUxRuntime")
v316=script_body("v316SessionLossProtectionRuntime")
save=script_body("v304GlobalSaveIntegrityRuntime")
review=script_body("v302ReviewResolutionAuthorityRuntime")
updater=script_body("fjzReleaseRuntime")

checks={
 "release":tuple(map(int,release.split("."))) >= (21,20),
 "meta":'meta name="fjz-runtime-flow-cleanup" content="21.20"' in html,
 "appointment_render_uses_cache":"injectNextAppointmentV312(false)" in v312 and "injectAgendaDatesV313(false)" in v312,
 "no_forced_appointment_render":"injectNextAppointmentV312(true)" not in v312,
 "agenda_owned_once":"agendaAlwaysVisibleOwnedByV312:true" in v312 and "No tenés fechas puntuales agendadas" in v312,
 "old_coach_summary_wrapper_removed":"legacyCoachSummaryWrapperRemovedV320:true" in v312 and "baseCoachSummaryV312" not in v312,
 "duplicate_student_wrapper_removed":"studentAgendaRenderWrapperRemovedV320:true" in v314 and "baseRenderStudentV314" not in v314,
 "obsolete_empty_helper_removed":"ensureStudentAgendaEmptyStateV314" not in v314,
 "recovery_throttled":"RECOVERY_SWEEP_COOLDOWN_V320=15000" in v316 and "recoverRecentV316(false)" in v316,
 "recovery_startup_immediate":"recoverRecentV316(true)" in v316,
 "global_save_intact":"globalSaveIntegrity:true" in save and "duplicateCriticalWriteLocks:true" in save and "successDeferredUntilVerified:true" in save,
 "workout_double_verify_intact":"sessionSuccessRequiresDoubleVerification:true" in v316 and "snapshotAndProjectionConfirmation:true" in v316,
 "stale_snapshot_guard_intact":"staleSnapshotCannotDeleteSessions:true" in v316,
 "first_review_authority_intact":"stableClientReviewAuthorityV319:true" in review and "firstReviewReadsCloudProfileKeyOnly:true" in review,
 "release_loop_guard_intact":"previousRetries>=2" in updater and "__fjzReleaseMismatchBlockedV318" in updater,
}
failed=[k for k,v in checks.items() if not v]
metrics={
 "styles":len(re.findall(r"<style\b",html,re.I)),
 "renders":len(re.findall(r"(?:window\.)?render\s*=",html)),
 "channels":html.count(".channel("),
 "timeouts":html.count("setTimeout("),
 "intervals":html.count("setInterval("),
 "listeners":html.count("addEventListener("),
 "mutation_observers":html.count("new MutationObserver"),
 "performance_observers":html.count("new PerformanceObserver"),
}
print("TEAM FJZ V21.20 RUNTIME FLOW CLEANUP AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.20 RUNTIME FLOW CLEANUP AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.20 stylesheet topology regression")
if metrics["renders"]>18: raise SystemExit("V21.20 render authority regression")
if metrics["channels"]>2: raise SystemExit("V21.20 realtime channel regression")
if metrics["intervals"]!=0: raise SystemExit("V21.20 interval regression")
if metrics["listeners"]>48: raise SystemExit("V21.20 listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.20 MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.20 PerformanceObserver regression")
print("TEAM FJZ V21.20 RUNTIME FLOW CLEANUP AUDIT OK")
