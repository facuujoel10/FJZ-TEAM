import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

critical=[
 "openCoachStudentTabV235","renderCoachStudentsV235","renderCoachFocusV235",
 "setCoachStudentFilterV235","setCoachStudentSortV236","openNextCoachPriorityV236",
 "coachReviewLoopStateV238","coachReviewCountsV238","decorateCoachReviewStateV238",
 "coachReviewCadenceDaysV240","coachReviewDueV240","setCoachReviewCadenceV240",
 "pendingSessionFeedbackCountV243","coachPriorityStateV252","coachPriorityActionV259",
 "renderCoachPriorityCenterV252","shiftCoachCalendarV280","goTodayCoachCalendarV280"
]

def has_authority(name):
    pats=[
      rf"function\s+{re.escape(name)}\s*\(",
      rf"window\.{re.escape(name)}\s*=",
      rf"\b{re.escape(name)}\s*=\s*(?:async\s*)?function\s*\(",
      rf"\b{re.escape(name)}\s*=\s*(?:async\s*)?\([^)]*\)\s*=>",
    ]
    return any(re.search(p,html) for p in pats)

missing=[x for x in critical if not has_authority(x)]
required=[

 'meta name="fjz-coach-integrity-recovery" content="20.81"',
 "coachIntegrityRecovery:true","filtersRestored:true","sortingRestored:true",
 "nextPriorityRestored:true","reviewCadenceRestored:true","reviewLoopRestored:true",
 "focusPanelRestored:true","studentNavigationRestored:true","legacyMusicCallNeutralized:true",
 "priorityCalendarRecovery:true","restoredPriorityAuthorityAfterMusicRemoval:true",
 "restoredCalendarAuthorityAfterMusicRemoval:true","productionNetworkBlocked:true",
 "syntheticDataOnly:true","cloudDisabled:true"
]
markers=[x for x in required if x not in html]
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
print("TEAM FJZ V20.81 COACH INTEGRITY AUDIT")
print(json.dumps({"release":release,"missing_critical_authorities":missing,"missing_markers":markers,"metrics":metrics},indent=2,ensure_ascii=False))
def version_tuple(v):
  try:return tuple(int(x) for x in v.split("."))
  except Exception:return (0,)
if version_tuple(release)<version_tuple("20.81"): raise SystemExit("Release older than V20.81 baseline: "+release)
if missing: raise SystemExit("Missing critical Coach authorities: "+repr(missing))
if markers: raise SystemExit("Missing V20.81 markers: "+repr(markers))
if metrics["styles"]!=1: raise SystemExit("Stylesheet regression")
if metrics["renders"]>18: raise SystemExit("Render assignment regression")
if metrics["intervals"]!=0: raise SystemExit("Interval regression")
if metrics["listeners"]>52: raise SystemExit("Listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("PerformanceObserver regression")
print("TEAM FJZ V20.81 COACH INTEGRITY AUDIT OK")
