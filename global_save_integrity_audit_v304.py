import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def body(sid):
    m=re.search(r'<script[^>]*\bid=["\']'+re.escape(sid)+r'["\'][^>]*>(.*?)</script>',html,re.S|re.I)
    return m.group(1) if m else ""

v304=body("v304GlobalSaveIntegrityRuntime")
checks={
  "release_2104_or_newer":tuple(map(int,release.split("."))) >= (21,4),
  "meta":'meta name="fjz-global-save-integrity" content="21.04"' in html,
  "runtime":bool(v304),
  "v303_retained":'id="v303SaveIntegrityRuntime"' in html and "checkinWriteReadBack:true" in html,
  "v207_retained":'id="v207ConfirmedSessionCommitRuntime"' in html and "cloudConfirmationBeforeSuccess:true" in html,
  "workout_readback":"workoutReadBack:true" in v304 and "athlete_snapshots" in v304 and "La nube no confirmó completamente la sesión." in v304,
  "routine_readback":"routineReadBack:true" in v304 and "sameDeep(localDays" in v304,
  "reorder_readback":"reorderReadBack:true" in v304 and "actualOrderV304" in html and "expectedOrderV304" in html,
  "agenda_exact":"agendaExactReadBack:true" in v304 and "scheduleMatches" in v304 and "reconcileSchedule" in v304,
  "reminder_readback":"reminderReadBack:true" in v304 and "athlete_reminders" in v304,
  "measurement_readback":"measurementReadBack:true" in v304 and "measurementMatches" in v304,
  "photo_compensation":"photoTwoResourceCompensation:true" in v304 and "progress-photos" in v304 and ".remove([path])" in v304,
  "nutrition_plan":"nutritionPlanReadBack:true" in v304 and "planMatches" in v304,
  "nutrition_single":"nutritionSingleLogReadBack:true" in v304 and "nutritionIds" in v304,
  "nutrition_option":"nutritionOptionReadBack:true" in v304 and "basePlanOption" in v304,
  "nutrition_group":"nutritionMealGroupReadBack:true" in v304 and "meal_group_id" in v304,
  "nutrition_delete":"nutritionDeleteReadBack:true" in v304 and "baseDeleteLog" in v304 and "baseDeleteMeal" in v304,
  "feedback_readback":"exerciseFeedbackReadBack:true" in v304 and "baseReviewFeedback" in v304,
  "checkin_feedback":"checkinFeedbackReadBack:true" in v304 and "baseCheckinFeedback" in v304,
  "success_deferred":"successDeferredUntilVerified:true" in v304 and "verifyDepth" in v304,
  "fresh_auth":"freshAuthForCriticalWrites:true" in v304 and "__fjzEnsureFreshAuthV194" in v304,
  "locks":"duplicateCriticalWriteLocks:true" in v304 and "const locks=new Map()" in v304,
  "no_timer":"setTimeout(" not in v304 and "setInterval(" not in v304,
  "no_listener":"addEventListener(" not in v304,
  "no_observer":"MutationObserver" not in v304 and "PerformanceObserver" not in v304,
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
print("TEAM FJZ V21.04 GLOBAL SAVE INTEGRITY AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed,"metrics":metrics},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.04 GLOBAL SAVE INTEGRITY AUDIT FAILED")
if metrics["styles"]!=1: raise SystemExit("V21.04 stylesheet regression")
if metrics["renders"]>18: raise SystemExit("V21.04 render regression")
if metrics["channels"]>2: raise SystemExit("V21.04 realtime regression")
if metrics["intervals"]!=0: raise SystemExit("V21.04 interval regression")
if metrics["mutation_observers"]>3: raise SystemExit("V21.04 observer regression")
if metrics["performance_observers"]!=0: raise SystemExit("V21.04 performance observer regression")
print("TEAM FJZ V21.04 GLOBAL SAVE INTEGRITY AUDIT OK")
