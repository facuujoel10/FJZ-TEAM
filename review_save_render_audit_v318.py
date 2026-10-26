import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def script_body(sid):
    marker='id="'+sid+'"'
    mid=html.find(marker)
    if mid<0:return ""
    start=html.find(">",mid)
    end=html.find("</script>",start)
    return html[start+1:end] if start>=0 and end>=0 else ""

review=script_body("v302ReviewResolutionAuthorityRuntime")
save=script_body("v304GlobalSaveIntegrityRuntime")
sessions=script_body("v316SessionLossProtectionRuntime")
updater=script_body("fjzReleaseRuntime")

checks={
 "release":tuple(map(int,release.split("."))) >= (21,18),
 "review_meta":'meta name="fjz-review-event-archive-authority" content="21.18"' in html,
 "single_review_runtime":html.count('id="v302ReviewResolutionAuthorityRuntime"')==1,
 "single_global_save_runtime":html.count('id="v304GlobalSaveIntegrityRuntime"')==1,
 "single_session_guard_runtime":html.count('id="v316SessionLossProtectionRuntime"')==1,
 "resolved_underlying_event":"(d.eventKeys||[]).some(k=>resolved.has(String(k)))" in review,
 "dismissed_events_loaded":".not('dismissed_at','is',null)" in review and "dismissedEventsV318" in review,
 "resolved_feed_filtered":"resolvedEventsFilteredBeforeRanking:true" in review,
 "permanent_profile_review":"permanentProfileReviewAuthority:true" in review,
 "global_save_integrity":"globalSaveIntegrity:true" in save,
 "duplicate_write_locks":"duplicateCriticalWriteLocks:true" in save,
 "verified_workout_save":"workoutReadBack:true" in save,
 "verified_agenda_save":"agendaExactReadBack:true" in save,
 "verified_nutrition_save":"nutritionPlanReadBack:true" in save,
 "session_double_verify":"sessionSuccessRequiresDoubleVerification:true" in sessions,
 "session_local_recovery":"localRecoveryBackup:true" in sessions,
 "stale_snapshot_protection":"staleSnapshotCannotDeleteSessions:true" in sessions,
 "release_retry_bounded":"previousRetries>=2" in updater and "__fjzReleaseMismatchBlockedV318" in updater,
 "no_forced_reload":"location.reload();" not in updater,
 "review_no_new_timers":"setInterval(" not in review and "setTimeout(" not in review,
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
print("TEAM FJZ V21.18 REVIEW / SAVE / RENDER AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.18 REVIEW / SAVE / RENDER AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.18 stylesheet topology regression")
if metrics["renders"]>18: raise SystemExit("V21.18 render authority regression")
if metrics["channels"]>2: raise SystemExit("V21.18 realtime channel regression")
if metrics["intervals"]!=0: raise SystemExit("V21.18 interval regression")
if metrics["listeners"]>52: raise SystemExit("V21.18 listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.18 MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.18 PerformanceObserver regression")
print("TEAM FJZ V21.18 REVIEW / SAVE / RENDER AUDIT OK")
