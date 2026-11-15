import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")
required=[
 'meta name="fjz-nutrition-premium" content="22.4A"',
 'id="v22NutritionPremiumRuntime"',
 'meta name="fjz-athlete-360-workspace" content="22.3B"',
 'meta name="fjz-coach-ux-final-polish" content="22.3C-UX"'
]
for marker in required:
    if marker not in html: raise RuntimeError("V22 4A-UX prerequisite missing: "+marker)
before={
 "scripts":len(re.findall(r"<script\\b",html,re.I)),
 "channels":len(re.findall(r"\\.channel\\s*\\(",html)),
 "listeners":len(re.findall(r"addEventListener\\s*\\(",html)),
 "timers":len(re.findall(r"setTimeout\\s*\\(|setInterval\\s*\\(",html)),
 "observers":len(re.findall(r"new\\s+(?:Mutation|Performance)Observer",html))
}
css=pathlib.Path("src/ui/nutrition-ux-final-polish.css").read_text(encoding="utf-8")
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V22 4A-UX expected one consolidated stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]
html=html.replace("</head>",'<meta name="fjz-nutrition-ux-final-polish" content="22.4A-UX">\n</head>',1)
after={
 "scripts":len(re.findall(r"<script\\b",html,re.I)),
 "channels":len(re.findall(r"\\.channel\\s*\\(",html)),
 "listeners":len(re.findall(r"addEventListener\\s*\\(",html)),
 "timers":len(re.findall(r"setTimeout\\s*\\(|setInterval\\s*\\(",html)),
 "observers":len(re.findall(r"new\\s+(?:Mutation|Performance)Observer",html))
}
if before!=after: raise RuntimeError("V22 4A-UX changed runtime topology: "+repr({"before":before,"after":after}))
for marker in [
 'meta name="fjz-nutrition-ux-final-polish" content="22.4A-UX"',
 'TEAM FJZ V22 · 4A-UX Nutrition final polish',
 '#view:has(.fjz4a-student-shell)',
 '#view.fjz3b-mounted:has(.fjz4a-coach-shell)'
]:
    if marker not in html: raise RuntimeError("V22 4A-UX output marker missing: "+marker)
p.write_text(html,encoding="utf-8")
print("TEAM FJZ V22 4A-UX Nutrition final polish injected",len(html))
