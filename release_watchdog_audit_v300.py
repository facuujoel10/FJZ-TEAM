import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
sw=(root/"public"/"sw.js").read_text(encoding="utf-8")
version=json.loads((root/"public"/"version.json").read_text(encoding="utf-8"))
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

m=re.search(r'<script id="fjzReleaseRuntime">(.*?)</script>',html,re.S)
runtime=m.group(1) if m else ""

checks={
  "release_2100_or_newer":tuple(map(int,release.split("."))) >= (21,0),
  "version_json_matches":str(version.get("release"))==release,
  "cache_matches_release":("team-fjz-v"+release.replace(".","-")) in sw,
  "runtime_present":bool(runtime),
  "periodic_watchdog":"__fjzReleaseWatchdogV300" in runtime,
  "watchdog_30s":"cadenceMs:30000" in runtime and "scheduleReleaseWatch(30000)" in runtime,
  "first_check_7s":"scheduleReleaseWatch(7000)" in runtime,
  "manual_force_check":"__fjzForceReleaseCheckV300" in runtime,
  "version_fetch_no_store":"version.json?ts=" in runtime and "cache:'no-store'" in runtime,
  "sw_update_no_cache":"updateViaCache:'none'" in runtime,
  "network_first_navigation":"fetch(req,{cache:'no-store'})" in sw,
  "version_json_bypasses_cache":"url.pathname.endsWith('/version.json')" in sw and "cache:'no-store'" in sw,
  "no_interval":"setInterval(" not in runtime,
  "one_release_timeout":runtime.count("setTimeout(")==1,
  "single_navigation_lock":"releaseNavigationInProgress" in runtime,
  "bounded_release_navigation":"previousRetries>=2" in runtime and "previousRetries+1" in runtime and "__fjzReleaseMismatchBlockedV318" in runtime,
  "no_forced_controller_reload":"location.reload();" not in runtime,
  "v299_still_present":'meta name="fjz-alert-review-system" content="20.99"' in html,
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

failed=[k for k,v in checks.items() if not v]
print("TEAM FJZ V21.00 RELEASE WATCHDOG AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed:
    raise SystemExit("V21.00 RELEASE WATCHDOG AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.00 stylesheet regression")
if metrics["renders"]>18: raise SystemExit("V21.00 render regression")
if metrics["channels"]>2: raise SystemExit("V21.00 realtime regression")
if metrics["timeouts"]>57: raise SystemExit("V21.00 timeout source regression")
if metrics["intervals"]!=0: raise SystemExit("V21.00 interval regression")
if metrics["listeners"]>52: raise SystemExit("V21.00 listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.00 MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.00 PerformanceObserver regression")
print("TEAM FJZ V21.00 RELEASE WATCHDOG AUDIT OK")
