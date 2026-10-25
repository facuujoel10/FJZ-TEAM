import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def script_body(script_id):
    m=re.search(r'<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>(.*?)</script>',html,re.S|re.I)
    return m.group(1) if m else ""

v175=script_body("v175ProfileAgendaCoachCenterRuntime")
v280=script_body("v280OperationalRecoveryRuntime")

launcher=""
m=re.search(r'window\.__fjzRenderCoachCockpitV268=function\(\)\{.*?\n  \};',v175,re.S)
if m: launcher=m.group(0)

checks={
  "release_2098_or_newer":tuple(map(int,release.split("."))) >= (20,98),
  "meta":'meta name="fjz-review-ok-cockpit-fix" content="20.98"' in html,
  "stale_exact_placeholder_removed":"Preparando lectura operativa" not in html,
  "cockpit_final_fallback":"fallbackCoachCockpitV298" in v175,
  "launcher_present":"__fjzRenderCoachCockpitV268" in launcher,
  "launcher_not_blocked_by_mode":"mode==='coach'" not in launcher and 'mode==="coach"' not in launcher,
  "launcher_uses_real_coach_context":"currentProfile?.role==='coach'" in launcher and "coachTab==='student'" in launcher,
  "review_ok_authority":"__fjzMarkCoachReviewOkV298" in v175,
  "review_main_cta":"✓ Revisado / OK" in v175,
  "review_baseline_saved":"s.coachReviewV237=clone(snap)" in v175,
  "priority_ok":"v298-priority-ok" in v280 and "✓ OK" in v280,
  "current_review_suppresses_same_persistent_request":
    "reviewCurrent=hasBaseline&&!changed&&!reviewDue" in v280 and
    "const lowAdherence=!reviewCurrent&&adh<70" in v280 and
    "const inactivityReview=!reviewCurrent&&inactive>=7" in v280,
  "critical_still_urgent":"if(critical>0||pendingFeedback>0)return {bucket:'urgent'" in v280,
  "summary_final_pass":"window.__fjzRenderCoachCockpitV268?.()" in v175,
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
print("TEAM FJZ V20.98 REVIEW OK / COCKPIT AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed:
    raise SystemExit("V20.98 REVIEW OK / COCKPIT AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V20.98 stylesheet regression")
if metrics["renders"]>18: raise SystemExit("V20.98 render regression")
if metrics["channels"]>2: raise SystemExit("V20.98 realtime regression")
if metrics["timeouts"]>57: raise SystemExit("V20.98 timeout regression")
if metrics["intervals"]!=0: raise SystemExit("V20.98 interval regression")
if metrics["listeners"]>52: raise SystemExit("V20.98 listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("V20.98 MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("V20.98 PerformanceObserver regression")
print("TEAM FJZ V20.98 REVIEW OK / COCKPIT AUDIT OK")
