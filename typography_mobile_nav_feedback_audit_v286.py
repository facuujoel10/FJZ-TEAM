import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def vt(v):
    try:return tuple(int(x) for x in v.split("."))
    except Exception:return (0,)

required=[
 'meta name="fjz-typography-mobile-nav-feedback" content="20.86"',
 "@media(min-width:1000px)",
 "#v266CoachWorkspace .v266-quick-actions",
 "grid-template-columns:repeat(4,minmax(0,1fr))!important",
 "grid-template-columns:repeat(3,minmax(0,1fr))!important",
 ".v241-difficulty-grid label>input[type=\"checkbox\"]",
 "position:absolute!important",
 "text-align:center!important",
 "word-break:normal!important",
 'meta name="fjz-final-release-candidate" content="20.85"',
 "finalMonthlyCalendarAuthorityV284:true",
 "duplicateAsyncSaveGuard:true",
]
missing=[x for x in required if x not in html]

logic={
 "desktop_type_larger":"font-size:11px!important" in html and "font-size:9.5px!important" in html,
 "mobile_duplicate_nav_hidden":bool(re.search(r'@media\(max-width:760px\).*?#v266CoachWorkspace \.v266-quick-actions\s*\{\s*display:none!important;',html,re.S)),
 "mobile_tabs_single_surface":bool(re.search(r'#coachStudentTabs,\s*\.v266-coach-tabs\s*\{.*?display:grid!important;.*?overflow:visible!important;',html,re.S)),
 "mobile_tabs_touch_height":"min-height:42px!important" in html,
 "feedback_checkbox_left":"left:12px!important" in html or "left:10px!important" in html,
 "feedback_text_centered":bool(re.search(r'\.v241-difficulty-grid label>span\s*\{.*?text-align:center!important;.*?word-break:normal!important;',html,re.S)),
 "feedback_two_col_mobile":bool(re.search(r'@media\(max-width:560px\).*?\.v241-difficulty-grid\s*\{.*?grid-template-columns:repeat\(2,minmax\(0,1fr\)\)!important;',html,re.S)),
 "feedback_one_col_360":bool(re.search(r'@media\(max-width:360px\).*?\.v241-difficulty-grid\s*\{.*?grid-template-columns:1fr!important;',html,re.S)),
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

print("TEAM FJZ V20.86 TYPOGRAPHY/NAV/FEEDBACK AUDIT")
print(json.dumps({"release":release,"missing":missing,"logic":logic,"metrics":metrics},indent=2,ensure_ascii=False))

if vt(release)<vt("20.86"): raise SystemExit("Release older than V20.86: "+release)
if missing: raise SystemExit("Missing V20.86 markers: "+repr(missing))
if not all(logic.values()): raise SystemExit("V20.86 logic audit failed: "+repr(logic))
if metrics["styles"]!=1: raise SystemExit("Stylesheet regression")
if metrics["renders"]>18: raise SystemExit("Render assignment regression")
if metrics["intervals"]!=0: raise SystemExit("Interval regression")
if metrics["listeners"]>52: raise SystemExit("Listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("PerformanceObserver regression")
if metrics["smooth_scroll"]!=0: raise SystemExit("Smooth-scroll regression")
if metrics["transition_all"]!=0: raise SystemExit("transition:all regression")
print("TEAM FJZ V20.86 TYPOGRAPHY/NAV/FEEDBACK AUDIT OK")
