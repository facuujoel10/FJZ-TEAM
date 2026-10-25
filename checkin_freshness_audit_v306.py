import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()
def body(sid):
    m=re.search(r'<script[^>]*\bid=["\']'+re.escape(sid)+r'["\'][^>]*>(.*?)</script>',html,re.S|re.I)
    return m.group(1) if m else ""
v306=body("v306CheckinFreshnessPresentationRuntime")
checks={
 "release_2106_or_newer":tuple(map(int,release.split("."))) >= (21,6),
 "meta":'meta name="fjz-checkin-freshness" content="21.06"' in html,
 "runtime":bool(v306),
 "week_label":"Semana (inicio lunes)" in html,
 "range":"weekRangePresentation:true" in v306 and "__fjzWeekRangeLabelV306" in v306,
 "submitted":"submissionTimestampPresentation:true" in v306 and "Enviado hoy " in v306,
 "timezone":"America/Argentina/Buenos_Aires" in v306,
 "freshness_markers":"feedCurrentPendingOnly:true" in v306 and "reviewedWellnessHidden:true" in v306 and "staleCheckinFeedStateCleaned:true" in v306,
 "v305_retained":'id="v305CheckinResubmissionLifecycleRuntime"' in html,
 "no_timer":"setTimeout(" not in v306 and "setInterval(" not in v306,
 "no_listener":"addEventListener(" not in v306,
 "no_observer":"MutationObserver" not in v306 and "PerformanceObserver" not in v306,
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
print("TEAM FJZ V21.06 CHECK-IN FRESHNESS AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.06 CHECK-IN FRESHNESS AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.06 stylesheet regression")
if metrics["renders"]>18: raise SystemExit("V21.06 render regression")
if metrics["channels"]>2: raise SystemExit("V21.06 realtime regression")
if metrics["intervals"]!=0: raise SystemExit("V21.06 interval regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.06 observer regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.06 performance observer regression")
print("TEAM FJZ V21.06 CHECK-IN FRESHNESS AUDIT OK")
