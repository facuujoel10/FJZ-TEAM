import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def script_body(sid):
    m=re.search(r'<script[^>]*\bid=["\']'+re.escape(sid)+r'["\'][^>]*>(.*?)</script>',html,re.S|re.I)
    return m.group(1) if m else ""

v303=script_body("v303SaveIntegrityRuntime")
checks={
  "release_2103_or_newer":tuple(map(int,release.split("."))) >= (21,3),
  "runtime":bool(v303),
  "meta":'meta name="fjz-save-integrity" content="21.03"' in html,
  "write_returns_row":".upsert(payload,{onConflict:'athlete_id,week_start'})" in v303 and ".select(columns)" in v303 and ".single()" in v303,
  "readback_same_identity":".eq('athlete_id',aid)" in v303 and ".eq('week_start',payload.week_start)" in v303,
  "payload_compared":"verifyCheckinRow(written,payload)" in v303,
  "cache_reconciled":"reconcileTracking(verified,aid)" in v303,
  "receipt_persisted":"localStorage.setItem(RECEIPT_KEY" in v303,
  "receipt_rendered":"Check-in confirmado en la nube" in v303,
  "busy_guard":"if(checkinPromise)return checkinPromise" in v303,
  "auth_guard":"__fjzEnsureFreshAuthV194" in v303,
  "no_realtime_dependency":"noRealtimeDependencyForSaveConfirmation:true" in v303,
  "global_confirm_receipt":"const baseConfirm=window.__fjzConfirmSavedV264" in v303,
  "session_commit_existing":'id="v207ConfirmedSessionCommitRuntime"' in html and "__fjzManualSessionCommitV207" in html,
  "confirmed_save_layer_existing":"greenConfirmedSaveFeedback:true" in html and "duplicateAsyncSaveGuard:true" in html,
  "checkin_cloud_confirmation_existing":"checkinSuccessOnlyAfterCloudConfirmation:true" in html,
  "no_timer":"setInterval(" not in v303 and "setTimeout(" not in v303,
  "no_listener":"addEventListener(" not in v303,
  "no_observer":"MutationObserver" not in v303 and "PerformanceObserver" not in v303,
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
print("TEAM FJZ V21.03 SAVE INTEGRITY AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.03 SAVE INTEGRITY AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.03 stylesheet regression")
if metrics["renders"]>18: raise SystemExit("V21.03 render regression")
if metrics["channels"]>2: raise SystemExit("V21.03 realtime regression")
if metrics["intervals"]!=0: raise SystemExit("V21.03 interval regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.03 observer regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.03 performance observer regression")
print("TEAM FJZ V21.03 SAVE INTEGRITY AUDIT OK")
