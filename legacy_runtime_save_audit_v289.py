import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def vt(v):
    try:return tuple(int(x) for x in v.split("."))
    except:return (0,)

required=[
 'meta name="fjz-legacy-runtime-cleanup" content="20.89"',
 'meta name="fjz-desktop-readability-scale" content="20.89"',
 "paymentsDeferredV289:true",
 "checkinScheduleV122GuardedV289:true",
 "payments:false",
 "saveCheckinScheduleV122",
 "duplicateAsyncSaveGuard:true",
 "greenCheckOnConfirmedSaves:true",
 "finalMonthlyCalendarAuthorityV284:true",
 "exerciseCommentsVisiblePerSessionV287:true",
 "font-size:17px!important",
 ".v278-dashboard-alert-top strong",
 "font-size:14px!important",
]
missing=[x for x in required if x not in html]

legacy={
 "coach_payments_refs":html.count("coach_payments"),
 "payment_route_assignments":len(re.findall(r"coachTab\s*=\s*\\?(['\"])payments\\?\1",html)),
 "music_route_assignments":len(re.findall(r"(?:coachTab|studentTab|coachStudentTab)\s*=\s*\\?(['\"])music\\?\1",html)),
 "music_channel_refs":html.count("fjz-v69-global-music"),
 "payment_realtime_refs":len(re.findall(r"table:'coach_payments'",html)),
}

v277=re.search(r'<script[^>]*id=["\']v277SaveGeometryRuntime["\'][^>]*>(.*?)</script>',html,re.S|re.I)
v277_body=v277.group(1) if v277 else ""
guard_match=re.search(r"const guarded=\[(.*?)\];",v277_body,re.S)
guarded=set(re.findall(r"['\"]([^'\"]+)['\"]",guard_match.group(1))) if guard_match else set()

logic={
 "checkin_save_guarded":"saveCheckinScheduleV122" in guarded,
 "payment_io_removed":legacy["coach_payments_refs"]==0,
 "retired_routes_zero":legacy["payment_route_assignments"]==0 and legacy["music_route_assignments"]==0,
 "retired_music_channel_zero":legacy["music_channel_refs"]==0,
 "payment_realtime_zero":legacy["payment_realtime_refs"]==0,
 "desktop_name_17":"font-size:17px!important" in html,
 "desktop_goal_14":"font-size:14px!important" in html,
 "smart_alert_readable":".v278-dashboard-alert p" in html and "font-size:12.5px!important" in html,
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

print("TEAM FJZ V20.89 LEGACY/RUNTIME/SAVE AUDIT")
print(json.dumps({"release":release,"missing":missing,"legacy":legacy,"logic":logic,"metrics":metrics},indent=2,ensure_ascii=False))

if vt(release)<vt("20.89"): raise SystemExit("Release older than V20.89")
if missing: raise SystemExit("Missing V20.89 markers: "+repr(missing))
if not all(logic.values()): raise SystemExit("V20.89 logic audit failed: "+repr(logic))
if any(legacy.values()): raise SystemExit("Retired runtime references survived: "+repr(legacy))
if metrics["styles"]!=1: raise SystemExit("Stylesheet regression")
if metrics["renders"]>18: raise SystemExit("Render assignment regression")
if metrics["intervals"]!=0: raise SystemExit("Interval regression")
if metrics["listeners"]>52: raise SystemExit("Listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("PerformanceObserver regression")
if metrics["smooth_scroll"]!=0: raise SystemExit("Smooth-scroll regression")
if metrics["transition_all"]!=0: raise SystemExit("transition:all regression")

print("TEAM FJZ V20.89 LEGACY/RUNTIME/SAVE AUDIT OK")
