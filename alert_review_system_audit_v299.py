import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def script_body(script_id):
    m=re.search(r'<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>(.*?)</script>',html,re.S|re.I)
    return m.group(1) if m else ""

v96=script_body("v96AlertCenterRuntime")
v175=script_body("v175ProfileAgendaCoachCenterRuntime")
v280=script_body("v280OperationalRecoveryRuntime")

checks={
  "release_2099":release=="20.99",
  "meta":'meta name="fjz-alert-review-system" content="20.99"' in html,

  # One canonical alert lifecycle
  "v96_student_archive_authority":"__fjzArchiveCoachStudentV299" in v96,
  "seen_persists_read_at":"read_at:now" in v96 and "mode==='ok'?now:null" in v96,
  "ok_persists_dismissed_at":"dismissed_at:mode==='ok'?now:null" in v96,
  "active_copies_sync":
    "coachAlertsV96=coachAlertsV96.filter" in v96 and
    "coachFeedCache=(coachFeedCache||[]).filter" in v96 and
    "coachFeedV235=(coachFeedV235||[]).filter" in v96,
  "open_archives_before_route":
    "window.openCoachAlertV96=async function" in v96 and
    "await persistCoachKeysV299([key],'seen')" in v96,
  "ok_resolves":
    "window.dismissCoachAlertV96=async function" in v96 and
    "persistCoachKeysV299([key],'ok')" in v96,
  "read_all_clears_active":
    "Alertas vistas · panel limpio" in v96,
  "coach_uses_new_lifecycle_buttons":
    "coachAlertCardV96" in v96 and
    "coachActionLabelV299" in v96 and
    "onclick=\"dismissCoachAlertV96" in v96 and
    "✓ OK" in v96,

  # Review acknowledgement is fresh + cross-device
  "review_ack_fingerprint":"review-ack-v299" in v175 and "__fjzReviewFingerprintV299" in v175,
  "review_ack_cloud_load":
    ".from('coach_feed_state')" in v175 and
    ".like('event_key','review-ack-v299:%')" in v175,
  "review_ack_current_snapshot":
    "freshReviewSnapshotV299" in v175 and
    "s.coachReviewV237=clone(snap)" in v175,
  "review_ok_archives_student_alerts":
    "__fjzMarkCoachReviewOkV298=async function" in v175 and
    "__fjzArchiveCoachStudentV299?.(a.id,'ok')" in v175,
  "review_seen_archives_student_alerts":
    "__fjzMarkCoachReviewSeenV299=async function" in v175 and
    "__fjzArchiveCoachStudentV299?.(a.id,'seen')" in v175,
  "ok_success_copy":"✓ Revisado / OK · salió de pendientes" in v175,

  # Priority center only contains unresolved items and explains exactly why
  "priority_specific_signals":
    "Adherencia: " in v280 and
    "días sin registrar entrenamiento" in v280 and
    "Feedback: " in v280 and
    "Cambios desde la última revisión:" in v280,
  "priority_ack_suppresses_same_snapshot":
    "__fjzIsReviewAckedV299?.(s)" in v280 and
    "if(acked)return {bucket:'watch'" in v280,
  "new_feed_beats_old_ack":
    "if(feed.length||critical||warning)" in v280,
  "opening_priority_marks_seen_first":
    "window.__fjzOpenPriorityV280=async function" in v280 and
    "await window.__fjzMarkCoachReviewSeenV299?.(id)" in v280,
  "active_columns_only":
    "col('Urgente','urgent'" in v280 and
    "col('Revisar','today'" in v280 and
    "col('Seguimiento','watch'" not in v280[v280.find("renderPriority=function()"):],
  "lifecycle_explained":"Al entrar se archiva como visto" in v280,
  "dashboard_role_guard":"currentProfile?.role==='coach'&&coachTab==='dashboard'" in v280,

  # Legacy Coach focus respects the same acknowledged snapshot.
  "legacy_focus_ack_aware":
    "const acked=!!window.__fjzIsReviewAckedV299?.(s)" in html and
    "if(acked&&!feed&&!sf&&!critical)return 0" in html and
    "if(filterV281==='review')return !acked" in html and
    "if(acked)return {bucket:'watch',score:0,label:'Revisado'}" in html,

  # More specific alert UX
  "alert_metric_detail":
    "Anterior" in v96 and "Actual" in v96 and "Cambio" in v96 and "Qué revisar" in v96,
  "alert_lifecycle_copy":"Abrir una alerta la marca como vista" in v96,
  "alert_ok_button":"✓ OK" in v96,
}

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

failed=[k for k,v in checks.items() if not v]
print("TEAM FJZ V20.99 ALERT / REVIEW SYSTEM AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed:
    raise SystemExit("V20.99 ALERT / REVIEW SYSTEM AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V20.99 stylesheet regression")
if metrics["renders"]>18: raise SystemExit("V20.99 render regression")
if metrics["channels"]>2: raise SystemExit("V20.99 realtime regression")
if metrics["timeouts"]>57: raise SystemExit("V20.99 timeout regression")
if metrics["intervals"]!=0: raise SystemExit("V20.99 interval regression")
if metrics["listeners"]>52: raise SystemExit("V20.99 listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("V20.99 MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("V20.99 PerformanceObserver regression")
print("TEAM FJZ V20.99 ALERT / REVIEW SYSTEM AUDIT OK")
