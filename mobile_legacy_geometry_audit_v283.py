import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()
is_staging_local='id="fjzStagingLocalRuntime"' in html

required=[
 'meta name="fjz-mobile-legacy-isolation" content="20.83"',
 "if(!allowed.has(studentTab))studentTab='home'",
 "if(!valid)studentTab='training'",
 "if(!allowedCoach.has(coachTab))coachTab='dashboard'",
 "if(!selected){",
 "nav.classList.remove('v275-student-hud')",
 "agendaFinalRouteAuthority:true",
 "calendarHostIndependentFromPriority:true",
 "coachIntegrityRecovery:true",
 'input[type="date"]',
 'input[type="time"]',
 "overflow-x:clip",
 "scroll-margin-bottom:calc(136px + env(safe-area-inset-bottom))",]
if is_staging_local:
  required += ["productionNetworkBlocked:true","syntheticDataOnly:true","cloudDisabled:true"]
missing=[x for x in required if x not in html]

retired={
 "legacy_student_music_array":len(re.findall(r"\['music','Música'\]",html)),
 "legacy_coach_music_button":len(re.findall(r"<button[^>]+coachTab[^>]+music[^>]*>\s*Música\s*</button>",html,re.I)),
 "legacy_student_music_button":len(re.findall(r"<button[^>]+studentTab[^>]+music[^>]*>\s*Música\s*</button>",html,re.I)),
}

logic={
 "student_route_guard":"const allowed=new Set(['home','agenda','tracking','nutrition','progress','history','workout','training'])" in html,
 "stale_workout_guard":"if(!valid)studentTab='training'" in html,
 "coach_route_guard":"const allowedCoach=new Set(['dashboard','agenda','student'])" in html,
 "stale_student_guard":"if(!selected){" in html and "coachTab='dashboard'" in html,
 "coach_subtab_guard":"allowedStudentTabs" in html,
 "hud_class_isolation":"nav.classList.remove('v275-student-hud')" in html and "nav.classList.remove('v276-coach-hud')" in html,
 "mobile_inputs_hardened":'input[type="date"]' in html and 'input[type="time"]' in html,
 "modal_viewport_hardened":"100dvw" in html and "100dvh" in html,
 "tabs_local_scroll":"overscroll-behavior-x:contain" in html,
 "legacy_mobile_buttons_hidden":("coachTab='payments'" in html or 'meta name="fjz-payments-deferred" content="20.85"' in html) and "Tab='music'" in html,
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

print("TEAM FJZ V20.83 MOBILE LEGACY/GEOMETRY AUDIT")
print(json.dumps({"release":release,"missing":missing,"retired":retired,"logic":logic,"metrics":metrics},indent=2,ensure_ascii=False))

if vt(release)<vt("20.83"): raise SystemExit("Release older than V20.83: "+release)
if missing: raise SystemExit("Missing V20.83 markers: "+repr(missing))
if not all(logic.values()): raise SystemExit("V20.83 logic audit failed: "+repr(logic))
if retired["legacy_student_music_array"]!=0: raise SystemExit("Legacy student Music tab array survived")
if retired["legacy_coach_music_button"]!=0: raise SystemExit("Legacy Coach Music button survived")
if retired["legacy_student_music_button"]!=0: raise SystemExit("Legacy Student Music button survived")
if metrics["styles"]!=1: raise SystemExit("Stylesheet regression")
if metrics["renders"]>18: raise SystemExit("Render assignment regression")
if metrics["intervals"]!=0: raise SystemExit("Interval regression")
if metrics["listeners"]>52: raise SystemExit("Listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("PerformanceObserver regression")
if metrics["smooth_scroll"]!=0: raise SystemExit("Smooth-scroll regression")
if metrics["transition_all"]!=0: raise SystemExit("transition:all regression")

print("TEAM FJZ V20.83 MOBILE LEGACY/GEOMETRY AUDIT OK")
