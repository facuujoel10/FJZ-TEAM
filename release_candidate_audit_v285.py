import pathlib,re,json,collections

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def vt(v):
    try:return tuple(int(x) for x in v.split("."))
    except Exception:return (0,)

# Runtime / rendering inventory.
metrics={
 "bytes":len(html.encode("utf-8")),
 "scripts":len(re.findall(r"<script\b",html,re.I)),
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

# Static duplicate DOM ids are a frequent source of mobile/render bugs.
ids=re.findall(r'\bid=["\']([^"\']+)["\']',html,re.I)
id_counts=collections.Counter(ids)
duplicate_ids={k:v for k,v in id_counts.items() if v>1}

# Retired surfaces must not remain actionable.
retired={
 "music_buttons":len(re.findall(r'<button[^>]+(?:coachTab|studentTab)[^>]+music[^>]*>',html,re.I)),
 "music_tab_arrays":len(re.findall(r"\['music','Música'\]",html)),
 "payments_buttons":len(re.findall(r'<button[^>]+coachTab[^>]+payments[^>]*>',html,re.I)),
}

# Save-success consistency. Pending/local-only messages are intentionally excluded.
toast_pat=re.compile(r"toast(?:\?\.)?\(\s*(['\"])(?P<msg>[^'\"]+)\1\s*\)")
success_rx=re.compile(r"(guardad[oa]s?|finalizad[oa]s?|enviad[oa]s?|registrad[oa]s?|cread[oa]s?|actualizad[oa]s?|confirmad[oa]s?)",re.I)
skip_rx=re.compile(r"(guardá el plan|guardado en curso|localmente|sincronización pendiente|pendiente|sin guardar|revisá|copiados? al plan)",re.I)
success_toasts=[m.group("msg") for m in toast_pat.finditer(html) if success_rx.search(m.group("msg")) and not skip_rx.search(m.group("msg"))]

# Inline onclick first-call symbol check. Ignore language/built-in/browser helpers
# and member calls; only bare application symbols are treated as candidates.
handlers=re.findall(r'\bonclick=["\']([^"\']+)["\']',html,re.I)
called=set()
for h in handlers:
    for m in re.finditer(r'(?<![.\w$])([A-Za-z_$][\w$]*)\s*\(',h):
        called.add(m.group(1))
defined=set(re.findall(r'(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(',html))
defined.update(re.findall(r'window\.([A-Za-z_$][\w$]*)\s*=',html))
defined.update(re.findall(r'(?<![.\w$])([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:function\s*\(|\([^)]*\)\s*=>)',html))
ignore={"if","for","while","switch","return","confirm","alert","prompt","Number","String","Date","Math","parseInt","parseFloat","setTimeout","clearTimeout","requestAnimationFrame","console","open","close","focus","blur"}
missing_onclick=sorted(x for x in called if x not in defined and x not in ignore)

# Final authorities and UX invariants.
required=[
 "__fjzConfirmSavedV264","__fjzQuickSavedV264",
 "duplicateAsyncSaveGuard:true","buttonBusyState:true",
 "workoutFinishUsesConfirmedState:true","checkinUsesConfirmedState:true","nutritionSaveCloudConfirmed:true",
 "specificProgressAlerts:true","smartAlertDedupByEventKey:true",
 "finalMonthlyCalendarAuthorityV284:true","synchronousDashboardCalendarV284:true","calendarDelegatedToV284:true",
 "agendaFinalRouteAuthority:true","calendarHostIndependentFromPriority:true",
 "coachIntegrityRecovery:true","filtersRestored:true","studentNavigationRestored:true",
 "overflow-x:clip","@media(max-width:430px)","@media(max-width:360px)",
 'input[type="date"]','input[type="time"]',"overscroll-behavior-x:contain",
 "productionNetworkBlocked:true","syntheticDataOnly:true","cloudDisabled:true",
]
missing_markers=[x for x in required if x not in html]

# Save guards for deliberate async actions expected to be protected.
guarded_expected=[
 "saveNutritionPlan","submitMeasurement","saveCheckinFeedback",
 "saveStudentScheduleV81","saveReminderV81","saveRecipeV70",
 "saveNutritionTemplateV63","submitExerciseFeedbackV73","submitWeeklyCheckin"
]
guarded_missing=[x for x in guarded_expected if x not in html or ("wrapSaveV277('"+x+"')" not in html and 'wrapSaveV277("'+x+'")' not in html)]

# CSS / geometry danger inventory.
geometry={
 "raw_100vw":len(re.findall(r'(?<!d)100vw',html)),
 "raw_min_width_px":len(re.findall(r'min-width\s*:\s*(?:[4-9]\d\d|\d{4,})px',html,re.I)),
 "position_fixed":len(re.findall(r'position\s*:\s*fixed',html,re.I)),
 "overflow_x_auto":len(re.findall(r'overflow-x\s*:\s*auto',html,re.I)),
}

report={
 "release":release,
 "metrics":metrics,
 "duplicate_ids":duplicate_ids,
 "retired":retired,
 "success_toasts":success_toasts,
 "missing_onclick_symbols":missing_onclick,
 "missing_markers":missing_markers,
 "guarded_missing":guarded_missing,
 "geometry_inventory":geometry,
}
print("TEAM FJZ V20.85 RELEASE CANDIDATE AUDIT")
print(json.dumps(report,indent=2,ensure_ascii=False))

if vt(release)<vt("20.84"): raise SystemExit("Release older than V20.84 baseline: "+release)
if duplicate_ids: raise SystemExit("Duplicate static DOM ids: "+repr(duplicate_ids))
if retired["music_buttons"] or retired["music_tab_arrays"]: raise SystemExit("Retired Music action survived: "+repr(retired))
if success_toasts: raise SystemExit("Unstandardized success toasts: "+repr(success_toasts))
if missing_onclick: raise SystemExit("Inline handlers reference undefined symbols: "+repr(missing_onclick))
if missing_markers: raise SystemExit("Missing final authority markers: "+repr(missing_markers))
if guarded_missing: raise SystemExit("Missing async save guards: "+repr(guarded_missing))
if metrics["styles"]!=1: raise SystemExit("Stylesheet regression")
if metrics["renders"]>18: raise SystemExit("Render assignment regression")
if metrics["intervals"]!=0: raise SystemExit("Interval regression")
if metrics["listeners"]>52: raise SystemExit("Listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("PerformanceObserver regression")
if metrics["smooth_scroll"]!=0: raise SystemExit("Smooth-scroll regression")
if metrics["transition_all"]!=0: raise SystemExit("transition:all regression")

print("TEAM FJZ V20.85 RELEASE CANDIDATE AUDIT OK")
