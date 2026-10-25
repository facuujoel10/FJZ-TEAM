import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def body(sid):
    m=re.search(r'<script[^>]*\bid=["\']'+re.escape(sid)+r'["\'][^>]*>(.*?)</script>',html,re.S|re.I)
    return m.group(1) if m else ""

v305=body("v305CheckinResubmissionLifecycleRuntime")
checks={
  "release_2105_or_newer":tuple(map(int,release.split("."))) >= (21,5),
  "meta":'meta name="fjz-checkin-resubmission-lifecycle" content="21.05"' in html,
  "runtime":bool(v305),
  "payload_resets_review":"reviewed_at:null" in html,
  "select_includes_review_state":"coach_feedback,reviewed_at,submitted_at" in html,
  "coach_status":"Pendiente de revisión" in v305 and "Revisado" in v305,
  "submitted_time":"Último envío " in v305,
  "tracking_reload":"trackingLoadedFor=null" in v305,
  "feed_refresh":"coachFeedLoadedAt=0" in v305,
  "stale_review_logic":"reviewed<submitted" in v305,
  "db_backstop_marker":"dbTriggerBackstop:true" in v305,
  "versioned_feed_marker":"versionedCheckinFeedKeys:true" in v305,
  "v304_retained":'id="v304GlobalSaveIntegrityRuntime"' in html,
  "v303_retained":'id="v303SaveIntegrityRuntime"' in html,
  "no_timer":"setTimeout(" not in v305 and "setInterval(" not in v305,
  "no_listener":"addEventListener(" not in v305,
  "no_observer":"MutationObserver" not in v305 and "PerformanceObserver" not in v305,
}
failed=[k for k,v in checks.items() if not v]
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
print("TEAM FJZ V21.05 CHECK-IN RESUBMISSION AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.05 CHECK-IN RESUBMISSION AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.05 stylesheet regression")
if metrics["renders"]>18: raise SystemExit("V21.05 render regression")
if metrics["channels"]>2: raise SystemExit("V21.05 realtime regression")
if metrics["intervals"]!=0: raise SystemExit("V21.05 interval regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.05 observer regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.05 performance observer regression")
print("TEAM FJZ V21.05 CHECK-IN RESUBMISSION AUDIT OK")
