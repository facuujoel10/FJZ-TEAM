import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

required=[
 'meta name="fjz-final-calendar-authority" content="20.84"',
 "finalMonthlyCalendarAuthorityV284:true",
 "synchronousDashboardCalendarV284:true",
 "calendarDelegatedToV284:true",
 "window.__fjzRenderCoachCalendarV284=renderDashboardCalendarV284",
 "window.__fjzHydrateCoachCalendarV284=hydrateDashboardCalendarV284",
 "host.dataset.calendarAuthority='20.84'",
 "if(mode==='coach'&&coachTab==='dashboard'){",
 "renderDashboardCalendarV284();",
 "hydrateDashboardCalendarV284(false);",
 "window.__fjzRenderCoachCalendarV284?.();",
 "return window.__fjzHydrateCoachCalendarV284?.(true);",
 "calendarHostIndependentFromPriority:true",
 "agendaFinalRouteAuthority:true",
 "productionNetworkBlocked:true","syntheticDataOnly:true","cloudDisabled:true"
]
missing=[x for x in required if x not in html]

logic={
 "final_authority":"finalMonthlyCalendarAuthorityV284:true" in html,
 "sync_mount":"synchronousDashboardCalendarV284:true" in html and "hydrateDashboardCalendarV284(false);" in html,
 "v280_delegates":"calendarDelegatedToV284:true" in html,
 "priority_independent":"calendarHostIndependentFromPriority:true" in html,
 "agenda_source_reused":"localScheduleV282()" in html and "localRemindersV282()" in html,
 "staging_immediate":"window.__fjzStagingLocal?.enabled||!cloudEnabled||!supabaseClient" in html,
 "month_navigation":"shiftCoachCalendarV284" in html and "goTodayCoachCalendarV284" in html,
 "host_stamp":"calendarAuthority='20.84'" in html,
}

# The historical V280 private renderCalendar function may remain as inert
# compatibility code, but operational/public entry points must not call it.
v280=re.search(r'<script[^>]*id=["\']v280OperationalRecoveryRuntime["\'][^>]*>(.*?)</script>',html,re.S|re.I)
v280_body=v280.group(1) if v280 else ""
operational=re.search(r'window\.__fjzOperationalDashboardV280=function\(\)\{(.*?)\n\s*\};',v280_body,re.S)
refresh=re.search(r'window\.refreshCoachOperationalV280=function\(\)\{(.*?)\n\s*\};',v280_body,re.S)
legacy_calls={
 "operational_calls_old_render":bool(operational and re.search(r'\brenderCalendar\s*\(',operational.group(1))),
 "operational_calls_old_load":bool(operational and re.search(r'\bloadCalendar\s*\(',operational.group(1))),
 "refresh_calls_old_load":bool(refresh and re.search(r'\bloadCalendar\s*\(',refresh.group(1))),
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
 "smooth_scroll":len(re.findall(r"behavior\s*:\s*['\"]smooth['\"]",html)),
 "transition_all":len(re.findall(r"transition\s*:\s*all\b",html,re.I)),
}

def vt(v):
    try:return tuple(int(x) for x in v.split("."))
    except Exception:return (0,)

print("TEAM FJZ V20.84 FINAL CALENDAR AUDIT")
print(json.dumps({"release":release,"missing":missing,"logic":logic,"legacy_calls":legacy_calls,"metrics":metrics},indent=2,ensure_ascii=False))

if vt(release)<vt("20.84"): raise SystemExit("Release older than V20.84: "+release)
if missing: raise SystemExit("Missing V20.84 markers: "+repr(missing))
if not all(logic.values()): raise SystemExit("V20.84 logic audit failed: "+repr(logic))
if any(legacy_calls.values()): raise SystemExit("Legacy V20.80 calendar still owns an operational entry point: "+repr(legacy_calls))
if metrics["styles"]!=1: raise SystemExit("Stylesheet regression")
if metrics["renders"]>18: raise SystemExit("Render assignment regression")
if metrics["intervals"]!=0: raise SystemExit("Interval regression")
if metrics["listeners"]>52: raise SystemExit("Listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("PerformanceObserver regression")
if metrics["smooth_scroll"]!=0: raise SystemExit("Smooth-scroll regression")
if metrics["transition_all"]!=0: raise SystemExit("transition:all regression")

print("TEAM FJZ V20.84 FINAL CALENDAR AUDIT OK")
