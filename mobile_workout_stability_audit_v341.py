import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def script_body(script_id):
    m=re.search(r'<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>(.*?)</script>',html,re.S|re.I)
    return m.group(1) if m else ""

v112=script_body("v112SyncHardeningRuntime")
v146=script_body("v146RenderStabilityRuntime")
v341=script_body("v341MobileWorkoutStabilityRuntime")

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

schedule_match=re.search(r"function scheduleCloudSync\(\)\{(.*?)\n\}",html,re.S)
schedule=schedule_match.group(1) if schedule_match else ""

checks={
  "release":tuple(map(int,release.split("."))) >= (21,41),
  "meta":'meta name="fjz-mobile-workout-stability" content="21.41"' in html,
  "runtime":'id="v341MobileWorkoutStabilityRuntime"' in html,

  "workout_cloud_coalesced":
    "workoutActiveV341?4200:650" in schedule and
    "clearTimeout(cloudSyncTimer)" in schedule,
  "normal_cloud_delay_preserved":"workoutActiveV341?4200:650" in schedule,
  "no_syncing_status_churn":
    "if(!workoutActiveV341)setCloudStatus('syncing','Sincronizando')" in schedule,

  "active_workout_branch":"function activeWorkoutSyncV341()" in v112 and "const activeV341=activeWorkoutSyncV341();" in v112,
  "remote_merge_preserved":"const merged=mergeForStudentV112(local,data.data);" in v112,
  "draft_preserved":"merged.workoutDrafts=cloneV112(local.workoutDrafts)" in v112,
  "active_write_direct":".upsert({" in v112 and "athlete_id:linkedAthleteId" in v112,
  "no_state_replace_active":
    "if(activeV341){" in v112 and
    "return true;" in v112 and
    v112.find("if(activeV341){") < v112.find("const idx=state.students.findIndex"),
  "no_localstorage_rewrite_active":
    v112.find("if(activeV341){") < v112.find("writeStateQuietV112();"),
  "unsafe_fallback_blocked":
    "if(activeV341)throw e;" in v112 and
    "activeWorkoutNoUnsafeFallback:true" in v341,

  "realtime_freeze_preserved":"activeWorkoutFreeze:true" in v146 and "viewScopedRealtime:true" in v146,
  "local_autosave_preserved":"localImmediate:true" in html and "restoresAfterClose:true" in html,
  "session_double_verify_preserved":"sessionSuccessRequiresDoubleVerification:true" in html and "snapshotAndProjectionConfirmation:true" in html,
  "retry_same_session_preserved":"retryUsesSameSessionId:true" in html,
  "global_save_integrity_preserved":"globalSaveIntegrity:true" in html,
  "v2141_markers":
    all(x in v341 for x in [
      "workoutCloudDebounceMs:4200",
      "activeWorkoutStateReplacementBlocked:true",
      "activeWorkoutLocalStorageRewriteBlocked:true",
      "remoteConfigMergePreserved:true",
      "localWorkoutDraftPreserved:true",
      "explicitFinalSaveUntouched:true",
      "activeWorkoutNoUnsafeFallback:true",
    ]),
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

print("TEAM FJZ V21.41 MOBILE WORKOUT STABILITY AUDIT")
print(json.dumps({
  "release":release,
  "checks":checks,
  "metrics":metrics,
  "hard_limits":hard_limits,
  "failed_checks":failed_checks,
  "failed_limits":failed_limits,
},indent=2,ensure_ascii=False))

if failed_checks or failed_limits:
    raise SystemExit("V21.41 MOBILE WORKOUT STABILITY AUDIT FAILED")

print("TEAM FJZ V21.41 MOBILE WORKOUT STABILITY AUDIT OK")
