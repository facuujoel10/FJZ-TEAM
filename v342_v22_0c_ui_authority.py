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
    'meta name="fjz-mobile-workout-stability" content="21.41"',
    'meta name="fjz-coach-dashboard" content="20.25"',
    "function renderCoachDashboardV80()",
    "trainingCommentsGlobalRendererV325:true",
    "trainingCommentsAfterHydrationV325:true",
    "reviewCenterRepaintsTrainingCommentsV339:true",
]:
    if marker not in html:
        raise RuntimeError("V22 0C final UI prerequisite missing "+marker)

start=html.find("function renderCoachDashboardV80()")
end=html.find("const _renderCoachV80Base",start)
if start<0 or end<0 or end<=start:
    raise RuntimeError("V22 0C dashboard function bounds missing")
block=html[start:end]

hero=re.compile(r'(<div class="v225-hero-actions">)(.*?)(</div>)',re.S)
m=hero.search(block)
if not m:
    raise RuntimeError("V22 0C dashboard hero actions missing")
actions=m.group(2)

# Final dashboard authority: exactly one visible Agenda route and no retired Music route.
actions=re.sub(r"""\s*<button[^>]*onclick="coachTab='agenda';render\(\)"[^>]*>\s*Agenda\s*</button>""","",actions)
actions=re.sub(r"""\s*<button[^>]*onclick="coachTab='music';render\(\)"[^>]*>\s*Música\s*</button>""","",actions)
agenda="""\n      <button class="btn v342-coach-agenda" onclick="coachTab='agenda';render()">Agenda</button>"""
status='<button class="btn ghost" onclick="showSystemStatusV80()">Estado</button>'
if status in actions:
    actions=actions.replace(status,status+agenda,1)
else:
    actions=agenda+actions
new_hero=m.group(1)+actions+m.group(3)
block=block[:m.start()]+new_hero+block[m.end():]
html=html[:start]+block+html[end:]

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V22 0C expected one stylesheet")
css=r"""
/* TEAM FJZ V22 · ETAPA 0C FINAL DESKTOP AGENDA AUTHORITY */
@media(min-width:901px){
  .v225-coach-hero .v225-hero-actions{
    display:flex!important;
    visibility:visible!important;
    opacity:1!important;
  }
  .v225-coach-hero .v225-hero-actions .v342-coach-agenda{
    display:inline-flex!important;
    visibility:visible!important;
    opacity:1!important;
    pointer-events:auto!important;
  }
}
"""
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]
html=html.replace("</head>",'<meta name="fjz-v22-0c-final-ui-authority" content="0C.10">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V22 0C runtime topology changed "+key+": "+repr({"before":before,"after":after}))

final_start=html.find("function renderCoachDashboardV80()")
final_end=html.find("const _renderCoachV80Base",final_start)
final_block=html[final_start:final_end]
if final_block.count("v342-coach-agenda")!=1:
    raise RuntimeError("V22 0C Agenda authority count mismatch: "+str(final_block.count("v342-coach-agenda")))
if "coachTab='music';render()" in final_block or ">Música</button>" in final_block:
    raise RuntimeError("V22 0C retired dashboard Music route survived")
for marker in [
    'meta name="fjz-v22-0c-final-ui-authority" content="0C.10"',
    'class="btn v342-coach-agenda"',
    "reviewCenterRepaintsTrainingCommentsV339:true",
    "trainingCommentsAfterHydrationV325:true",
]:
    if marker not in html:
        raise RuntimeError("V22 0C final UI marker missing "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V22 ETAPA 0C final UI authority")
print("V22 0C BEFORE:",before)
print("V22 0C AFTER:",after)
print("V22 0C desktop Agenda + training comments repaint: OK")
