import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def script_body(script_id):
    m=re.search(r'<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>(.*?)</script>',html,re.S|re.I)
    return m.group(1) if m else ""

v301=script_body("v301ReviewWorkflowProRuntime")
v175=script_body("v175ProfileAgendaCoachCenterRuntime")

checks={
  "release_2101_or_newer":tuple(map(int,release.split("."))) >= (21,1),
  "meta":'meta name="fjz-review-workflow-pro" content="21.01"' in html,
  "runtime":bool(v301),
  "guided_360":"__fjzOpenGuidedReviewV301" in v301 and "__fjzResolveGuidedReviewV301" in v301,
  "verified_persistence":"upsert(rows,{onConflict:'coach_id,event_key'}).select" in v301 and "dismissed_at:now" in v301,
  "item_state_load":"__fjzLoadReviewItemStatesV301" in v301 and "review-item-v301:" in v301,
  "center":"renderCenter" in v301 and "CENTRO DE REVISIONES" in v301,
  "focus":"renderFocus" in v301 and "Próximas acciones" in v301,
  "context":"v301GuidedReview" in v301 and "POR QUÉ APARECIÓ" in v301 and "QUÉ REVISAR" in v301,
  "v175_uses_guided":"__fjzRegisterReviewItemV301" in v175 and "__fjzOpenGuidedReviewV301" in v175 and "__fjzResolveGuidedReviewV301" in v175,
  "seen_filtered":"__fjzReviewItemSeenV301" in v175,
  "readability":".v301-center-card" in html and ".v301-focus-card" in html and "font-size:12.5px" in html,
  "no_interval":"setInterval(" not in v301,
  "no_listener":"addEventListener(" not in v301,
  "no_observer":"MutationObserver" not in v301,
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
print("TEAM FJZ V21.01 REVIEW WORKFLOW AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.01 REVIEW WORKFLOW AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.01 stylesheet regression")
if metrics["renders"]>18: raise SystemExit("V21.01 render regression")
if metrics["channels"]>2: raise SystemExit("V21.01 realtime regression")
if metrics["intervals"]!=0: raise SystemExit("V21.01 interval regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.01 MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.01 PerformanceObserver regression")
print("TEAM FJZ V21.01 REVIEW WORKFLOW AUDIT OK")
