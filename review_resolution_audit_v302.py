import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def body(script_id):
    m=re.search(r'<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>(.*?)</script>',html,re.S|re.I)
    return m.group(1) if m else ""

v302=body("v302ReviewResolutionAuthorityRuntime")
checks={
  "release_2102_or_newer":tuple(map(int,release.split("."))) >= (21,2),
  "meta":'meta name="fjz-review-resolution-authority" content="21.02"' in html,
  "runtime":bool(v302),
  "resolved_set":"const resolved=new Set()" in v302,
  "seen_not_resolved":"window.__fjzReviewItemSeenV301=key=>!!key&&resolved.has(String(key))" in v302,
  "verified_upsert":".upsert(rows,{onConflict:'coach_id,event_key'})" in v302 and ".select('event_key,read_at,dismissed_at')" in v302,
  "ok_requires_dismissed":"mode!=='ok'||got.get(k)?.dismissed_at" in v302,
  "center_filters_resolved":"if(isResolved(s,d))return null" in v302,
  "focus_uses_filtered_rows":"students().map(rowFor).filter(Boolean)" in v302,
  "stable_state_key":"review-state-v302:" in v302 and "stateFingerprint(s)" in v302,
  "event_key_review":"review-v302:" in v302 and "sourceType='event'" in v302,
  "open_only_seen":"persist([d.reviewKey],'seen')" in v302,
  "ok_persists_state":"const keys=[lock,d.stateKey||stateKey(s),...(d.eventKeys||[])]" in v302,
  "optimistic_remove":"removeCards(lock)" in v302 and "if(!ok){resolving.delete(lock);refreshSurfaces();return false}" in v302,
  "guided_ok":"window.__fjzResolveGuidedReviewV301=async function(key)" in v302,
  "alert_ok_sync":"window.dismissCoachAlertV96=async function(key)" in v302,
  "context_ok":"__fjzResolveContextReviewV302" in v302,
  "no_timer":"setInterval(" not in v302 and "setTimeout(" not in v302,
  "no_listener":"addEventListener(" not in v302,
  "no_observer":"MutationObserver" not in v302 and "PerformanceObserver" not in v302,
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
print("TEAM FJZ V21.02 REVIEW RESOLUTION AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.02 REVIEW RESOLUTION AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.02 stylesheet regression")
if metrics["renders"]>18: raise SystemExit("V21.02 render regression")
if metrics["channels"]>2: raise SystemExit("V21.02 realtime regression")
if metrics["intervals"]!=0: raise SystemExit("V21.02 interval regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.02 observer regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.02 performance observer regression")
print("TEAM FJZ V21.02 REVIEW RESOLUTION AUDIT OK")
