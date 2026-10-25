import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()
is_staging_local='id="fjzStagingLocalRuntime"' in html
v294_source=(root/"v294_session_resilience.py").read_text(encoding="utf-8")

runtime_match=re.search(r'<script id="fjzReleaseRuntime">.*?</script>',html,re.S)
release_runtime=runtime_match.group(0) if runtime_match else ""

checks={
  "stable_auth_storage_key":
    ("storageKey:'sb-cujipwacwwpejhqjhnkr-auth-token'" in html if not is_staging_local
     else "storageKey:'sb-cujipwacwwpejhqjhnkr-auth-token'" in v294_source),
  "stale_refresh_detected":
    "function isStaleAuthErrorV298" in html and
    "refresh_token_not_found" in html and
    "invalid refresh token" in html,
  "stale_local_token_only_cleared":
    "localStorage.removeItem(FJZ_AUTH_STORAGE_KEY_V298)" in html,
  "stale_session_routes_to_login":
    "showFreshLoginAfterStaleSessionV298" in html and
    "Tus datos siguen guardados." in html,
  "boot_no_retry_trap_for_stale_token":
    "if(isStaleAuthErrorV298(e)){showFreshLoginAfterStaleSessionV298();return}" in html,
  "unexpected_signout_stale_handled":
    "if(isStaleAuthErrorV298(authError)){showFreshLoginAfterStaleSessionV298();return}" in html,
  "release_single_navigation_lock":
    "releaseNavigationInProgress" in release_runtime,
  "controllerchange_no_forced_reload":
    "controllerchange" in release_runtime and "location.reload();" not in release_runtime,
  "release_navigation_still_active":
    "location.replace(" in release_runtime and "version.json?ts=" in release_runtime,
  "local_logout_only":
    "signOut({scope:'local'})" in html,
  "session_persistence_still_enabled":
    "persistSession:true" in html and "autoRefreshToken:true" in html,
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

fail=[k for k,v in checks.items() if not v]

print("TEAM FJZ AUTH REENTRY / UPDATE SAFETY AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":fail,"metrics":metrics},indent=2,ensure_ascii=False))

if fail:
    raise SystemExit("AUTH REENTRY / UPDATE SAFETY AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("Stylesheet regression")
if metrics["renders"]>18: raise SystemExit("Render regression")
if metrics["intervals"]!=0: raise SystemExit("Interval regression")
if metrics["listeners"]>52: raise SystemExit("Listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("PerformanceObserver regression")

print("TEAM FJZ AUTH REENTRY / UPDATE SAFETY AUDIT OK")
