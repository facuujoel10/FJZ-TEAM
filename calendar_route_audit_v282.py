import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()
is_staging_local='id="fjzStagingLocalRuntime"' in html

required=[
 'meta name="fjz-calendar-route-hardening" content="20.82"',
 "agendaFinalRouteAuthority:true","agendaImmediateFrame:true","agendaNoPermanentSpinner:true",
 "calendarHostIndependentFromPriority:true","dashboardCalendarFallback:true","hudAgendaRouteCovered:true",
 "if(coachTab==='agenda')return renderCoachAgendaV282()",
 "window.renderCoachAgendaV81=renderCoachAgendaV282",
 "window.__fjzMountCoachCalendarV282=mountDashboardCalendarV282",
 "v282CoachAgendaBody","v259CoachCalendar",
 "coachTab=\\'agenda\\';render()",]
if is_staging_local:
  required += ["productionNetworkBlocked:true","syntheticDataOnly:true","cloudDisabled:true"]
missing=[x for x in required if x not in html]
logic={
 "final_agenda_router":"if(coachTab==='agenda')return renderCoachAgendaV282()" in html,
 "immediate_agenda_frame":"renderAgendaBodyV282('Agenda cargada');" in html,
 "monthly_host_priority_optional":"if(priority?.parentNode)priority.insertAdjacentElement('afterend',host);" in html and "else{" in html,
 "fallback_month_render":"function renderMonthlyFallbackV282(host)" in html,
 "post_render_recovery":"fjzPostRenderV125('v282-calendar-route'" in html,
 "hud_points_to_agenda":"coachTab=\\'agenda\\';render()" in html,
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
def vt(v):
    try:return tuple(int(x) for x in v.split("."))
    except Exception:return (0,)
print("TEAM FJZ V20.82 CALENDAR ROUTE AUDIT")
print(json.dumps({"release":release,"missing":missing,"logic":logic,"metrics":metrics},indent=2,ensure_ascii=False))
if vt(release)<vt("20.82"): raise SystemExit("Release older than V20.82: "+release)
if missing: raise SystemExit("Missing V20.82 markers: "+repr(missing))
if not all(logic.values()): raise SystemExit("V20.82 route logic failed: "+repr(logic))
if metrics["styles"]!=1: raise SystemExit("Stylesheet regression")
if metrics["renders"]>18: raise SystemExit("Render assignment regression")
if metrics["intervals"]!=0: raise SystemExit("Interval regression")
if metrics["listeners"]>52: raise SystemExit("Listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("PerformanceObserver regression")
print("TEAM FJZ V20.82 CALENDAR ROUTE AUDIT OK")
