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

review=script_body("v302ReviewResolutionAuthorityRuntime")
legacy=script_body("v312ReviewAgendaAuthorityRuntime")
hub=script_body("v175ProfileAgendaCoachCenterRuntime")
calendar=script_body("v280OperationalRecoveryRuntime")
save=script_body("v304GlobalSaveIntegrityRuntime")
sessions=script_body("v316SessionLossProtectionRuntime")

checks={
 "release":tuple(map(int,release.split("."))) >= (21,19),
 "meta":'meta name="fjz-first-review-authority" content="21.19"' in html,
 "single_review_runtime":html.count('id="v302ReviewResolutionAuthorityRuntime"')==1,
 "stable_client_map":"profileReviewedClientsV319" in review and "athleteByClientV319" in review,
 "athlete_link_load":".select('id,client_id')" in review and ".eq('coach_id',currentUser.id)" in review,
 "stable_client_exposed":"__fjzProfileReviewedStudentV319" in review,
 "dynamic_baseline_blocked":"if(profileReviewedV311(s))return false" in review,
 "profile_counts_as_current_baseline":"function baselineCurrentV308(s){return profileReviewedV311(s)||" in review,
 "legacy_uses_stable_client":"window.__fjzProfileReviewedStudentV319?.(s?.id)" in legacy,
 "legacy_no_snapshot_override":"legacySnapshotCannotOverrideCloudReviewedState:true" in legacy,
 "hub_waits_for_cloud":"Sincronizando revisión…" in hub and "__fjzFirstReviewAuthorityLoadedV319" in hub,
 "hub_no_false_first_review":"Sin primera revisión pendiente" in hub,
 "calendar_stable_client":"window.__fjzProfileReviewedStudentV319?.(s?.id)" in calendar,
 "event_archive_preserved":"underlyingEventResolutionAuthorityV318:true" in review,
 "global_save_preserved":"globalSaveIntegrity:true" in save and "duplicateCriticalWriteLocks:true" in save,
 "session_guard_preserved":"sessionSuccessRequiresDoubleVerification:true" in sessions and "staleSnapshotCannotDeleteSessions:true" in sessions,
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
print("TEAM FJZ V21.19 FIRST REVIEW AUTHORITY AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.19 FIRST REVIEW AUTHORITY AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.19 stylesheet topology regression")
if metrics["renders"]>18: raise SystemExit("V21.19 render authority regression")
if metrics["channels"]>2: raise SystemExit("V21.19 realtime channel regression")
if metrics["intervals"]!=0: raise SystemExit("V21.19 interval regression")
if metrics["listeners"]>52: raise SystemExit("V21.19 listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.19 MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.19 PerformanceObserver regression")
print("TEAM FJZ V21.19 FIRST REVIEW AUTHORITY AUDIT OK")
