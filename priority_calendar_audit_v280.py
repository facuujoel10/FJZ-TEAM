import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()
required=['meta name="fjz-release" content="20.80"','meta name="fjz-priority-calendar-recovery" content="20.80"',"priorityCalendarRecovery:true","restoredPriorityAuthorityAfterMusicRemoval:true","restoredCalendarAuthorityAfterMusicRemoval:true","staleCalendarCallsRemoved:true","priorityPerStudentIsolation:true","calendarIndependentFromPriority:true","stagingCalendarFallbackSafe:true","explicitDashboardOperationalHydration:true","__fjzOperationalDashboardV280","shiftCoachCalendarV280","goTodayCoachCalendarV280","productionNetworkBlocked:true","syntheticDataOnly:true","cloudDisabled:true"]
missing=[x for x in required if x not in html]
metrics={"styles":len(re.findall(r"<style\b",html,re.I)),"renders":len(re.findall(r"(?:window\.)?render\s*=",html)),"channels":len(re.findall(r"\.channel\s*\(",html)),"timeouts":len(re.findall(r"setTimeout\s*\(",html)),"intervals":len(re.findall(r"setInterval\s*\(",html)),"rafs":len(re.findall(r"requestAnimationFrame\s*\(",html)),"listeners":len(re.findall(r"addEventListener\s*\(",html)),"mutation_observers":len(re.findall(r"new\s+MutationObserver",html)),"performance_observers":len(re.findall(r"new\s+PerformanceObserver",html))}
logic={"priority_authority":"function renderPriority(){" in html and "CENTRO DE PRIORIDADES" in html,"calendar_authority":"function renderCalendar(){" in html and "CALENDARIO DEL COACH" in html,"stale_nested_call_removed":"renderCoachCalendarV259();\n  hydrateCoachCalendarV259();" not in html,"post_render_hook":"window.__fjzOperationalDashboardV280?.();" in html,"staging_safe":"typeof agendaRemindersV81!=='undefined'" in html}
print("TEAM FJZ V20.80 PRIORITY/CALENDAR AUDIT")
print(json.dumps({"release":release,"missing":missing,"logic":logic,"metrics":metrics},indent=2,ensure_ascii=False))
def version_tuple(v):
  try:return tuple(int(x) for x in v.split("."))
  except Exception:return (0,)
if version_tuple(release)<version_tuple("20.80"): raise SystemExit("Release older than V20.80 baseline: "+release)
if missing: raise SystemExit("Missing V20.80 markers: "+repr(missing))
if not all(logic.values()): raise SystemExit("V20.80 logic audit failed: "+repr(logic))
if metrics["styles"]!=1: raise SystemExit("Stylesheet regression")
if metrics["renders"]>18: raise SystemExit("Render assignment regression")
if metrics["intervals"]!=0: raise SystemExit("Interval regression")
if metrics["listeners"]>52: raise SystemExit("Listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("PerformanceObserver regression")
print("TEAM FJZ V20.80 PRIORITY/CALENDAR AUDIT OK")
