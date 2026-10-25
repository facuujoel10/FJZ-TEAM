import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "intervals":len(re.findall(r"setInterval\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

before=metrics(html)

for marker in [
    'meta name="fjz-coach-athlete-workspace" content="20.66"',
    'meta name="fjz-typography-mobile-nav-feedback" content="20.86"',
    'meta name="fjz-new-feature-hardening" content="20.91"',
    "v266-quick-actions",
    "#coachStudentTabs"
]:
    if marker not in html:
        raise RuntimeError("V20.92 prerequisite missing "+marker)

css=r"""
/* TEAM FJZ · V20.92 SINGLE COACH ATHLETE NAVIGATION
   Keep one canonical navigation (coachStudentTabs) on every viewport.
   Context metrics remain; duplicate quick-action shortcuts are hidden. */
#v266CoachWorkspace{
  grid-template-columns:minmax(0,1fr)!important;
}
#v266CoachWorkspace .v266-quick-actions{
  display:none!important;
}
#v266CoachWorkspace .v266-context-main{
  width:100%!important;
}
@media(min-width:1000px){
  #v266CoachWorkspace .v266-context-main{
    grid-template-columns:repeat(4,minmax(0,1fr))!important;
  }
  #coachStudentTabs,
  .v266-coach-tabs{
    margin-top:0!important;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.92 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-single-coach-athlete-nav" content="20.92">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V20.92 topology changed "+key+": "+repr({"before":before,"after":after}))

required=[
    'meta name="fjz-single-coach-athlete-nav" content="20.92"',
    "#v266CoachWorkspace .v266-quick-actions{",
    "display:none!important;",
    "grid-template-columns:minmax(0,1fr)!important;",
    "#coachStudentTabs",
]
for marker in required:
    if marker not in html:
        raise RuntimeError("V20.92 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.92 single coach athlete navigation")
print("V20.92 BEFORE:",before)
print("V20.92 AFTER:",after)
