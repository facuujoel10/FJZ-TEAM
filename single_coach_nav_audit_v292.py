import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

required=[
 'meta name="fjz-single-coach-athlete-nav" content="20.92"',
 '#v266CoachWorkspace .v266-quick-actions{',
 'display:none!important;',
 '#coachStudentTabs',
 'grid-template-columns:minmax(0,1fr)!important;',
]
missing=[x for x in required if x not in html]

metrics={
 "styles":len(re.findall(r"<style\b",html,re.I)),
 "renders":len(re.findall(r"(?:window\.)?render\s*=",html)),
 "channels":len(re.findall(r"\.channel\s*\(",html)),
 "timeouts":len(re.findall(r"setTimeout\s*\(",html)),
 "intervals":len(re.findall(r"setInterval\s*\(",html)),
 "listeners":len(re.findall(r"addEventListener\s*\(",html)),
 "mutation_observers":len(re.findall(r"new\s+MutationObserver",html)),
}
checks={
 "quick_actions_hidden_globally":"#v266CoachWorkspace .v266-quick-actions{" in html and "display:none!important;" in html,
 "canonical_tabs_preserved":"#coachStudentTabs" in html and "coachStudentTab" in html,
 "desktop_metrics_four_columns":"@media(min-width:1000px)" in html and "repeat(4,minmax(0,1fr))!important;" in html,
}
print("TEAM FJZ V20.92 SINGLE COACH NAV AUDIT")
print(json.dumps({"release":release,"missing":missing,"metrics":metrics,"checks":checks},indent=2,ensure_ascii=False))
if tuple(map(int,release.split("."))) < (20,92): raise SystemExit("Release older than 20.92")
if missing: raise SystemExit("Missing V20.92 markers: "+repr(missing))
if not all(checks.values()): raise SystemExit("Single-nav check failed: "+repr(checks))
if metrics["styles"]!=1: raise SystemExit("Stylesheet regression")
if metrics["renders"]>18: raise SystemExit("Render regression")
if metrics["intervals"]!=0: raise SystemExit("Interval regression")
if metrics["listeners"]>52: raise SystemExit("Listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("Observer regression")
print("TEAM FJZ V20.92 SINGLE COACH NAV AUDIT OK")
