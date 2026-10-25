import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def script_body(script_id):
    m=re.search(r'<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>(.*?)</script>',html,re.S|re.I)
    return m.group(1) if m else ""

v96=script_body("v96AlertCenterRuntime")
v197=script_body("v197AlertArchiveRuntime")
v175=script_body("v175ProfileAgendaCoachCenterRuntime")
v278=script_body("v278SmartAlertsProgressRuntime")

checks={
  "release_2097_or_newer": tuple(map(int,release.split("."))) >= (20,97),
  "patch_meta": 'meta name="fjz-coach-summary-alert-archive" content="20.97"' in html,
  "v96_owns_archive": "canonicalArchiveOwnedByV96:true" in v197,
  "broken_v197_private_mutation_removed":
    "coachAlertsV96=coachAlertsV96.filter" not in v197 and
    "studentAlertsV96=studentAlertsV96.filter" not in v197,
  "coach_read_immediate_removal":
    "coachAlertsV96=coachAlertsV96.filter(a=>a.event_key!==key)" in v96,
  "coach_read_all_clears_active":
    "coachAlertsV96=[];" in v96 and "Alertas revisadas y archivadas" in v96,
  "student_read_immediate_removal":
    "studentAlertsV96=studentAlertsV96.filter(a=>a.event_key!==key)" in v96,
  "student_read_all_clears_active":
    "studentAlertsV96=[];" in v96 and "Avisos revisados y archivados" in v96,
  "smart_read_is_archived":
    "if(st?.dismissed_at||st?.read_at)return" in v278 and
    "x.is_read=false" in v278,
  "smart_transient_archive_guard":
    "__fjzReviewedCoachKeysV297" in v278 and
    "if(x?.is_read)return false" in v278,
  "base_feed_actions_sync_archive":
    "async function markFeedRead(key)" in html and
    "async function dismissFeed(key)" in html and
    "__fjzReviewedCoachKeysV297?.add(String(key))" in html,
  "summary_core_wrapped":
    "hydrateSummaryCoreV297" in v175 and
    "async function hydrateSummaryV175()" in v175,
  "summary_failure_isolated":
    "coach summary hydration recovered" in v175 and
    "finally{" in v175 and
    "finalizeCoachSummaryV297(failed)" in v175,
  "weekly_brief_recovery":
    "renderCoachWeeklyBriefV250(s,latest,agenda,nutrition,pending)" in v175,
  "four_week_recovery":
    "renderCoachFourWeekV260(s,latest)" in v175,
  "loading_copy_cannot_stick":
    "Actualizado · datos parciales" in v175 and
    "Sin datos adicionales para mostrar en esta sección." in v175,
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
print("TEAM FJZ COACH SUMMARY / ALERT ARCHIVE AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":fail,"metrics":metrics},indent=2,ensure_ascii=False))

if fail:
    raise SystemExit("COACH SUMMARY / ALERT ARCHIVE AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("Stylesheet regression")
if metrics["renders"]>18: raise SystemExit("Render regression")
if metrics["channels"]>2: raise SystemExit("Realtime channel regression")
if metrics["timeouts"]>57: raise SystemExit("Timeout regression")
if metrics["intervals"]!=0: raise SystemExit("Interval regression")
if metrics["listeners"]>52: raise SystemExit("Listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("PerformanceObserver regression")

print("TEAM FJZ COACH SUMMARY / ALERT ARCHIVE AUDIT OK")
