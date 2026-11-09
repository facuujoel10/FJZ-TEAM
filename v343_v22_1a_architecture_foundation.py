import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")
def topology(doc):
    return {
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "intervals":len(re.findall(r"setInterval\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
    }
before=topology(html)
for marker in [
    'meta name="fjz-v22-0c-final-ui-authority"',
    "sessionSuccessRequiresDoubleVerification:true",
    "function dateInputToday(){const d=new Date();",
]:
    if marker not in html:
        raise RuntimeError("V22 1A prerequisite missing "+marker)
core=pathlib.Path("src/core/date.js").read_text(encoding="utf-8").strip()
if "</script" in core.lower(): raise RuntimeError("V22 1A date core cannot contain closing script markup")
if "TeamFJZDate" not in core or "calendarDate" not in core: raise RuntimeError("V22 1A invalid date core")
script='<script id="v22CanonicalDateCore">\n'+core+'\n</script>\n'
if html.count("</head>")!=1: raise RuntimeError("V22 1A head anchor mismatch")
html=html.replace("</head>",script+'<meta name="fjz-v22-1a-architecture-foundation" content="date-pilot">\n</head>',1)
old="function dateInputToday(){const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')}"
new="function dateInputToday(){try{return globalThis.TeamFJZDate.calendarDate(new Date(),'America/Argentina/Buenos_Aires')}catch(_e){const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')}}"
if html.count(old)!=1: raise RuntimeError("V22 1A dateInputToday authority mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)
after=topology(html)
if after!=before: raise RuntimeError("V22 1A date pilot changed runtime topology: "+repr({"before":before,"after":after}))
for marker in ['id="v22CanonicalDateCore"','meta name="fjz-v22-1a-architecture-foundation" content="date-pilot"',"globalThis.TeamFJZDate.calendarDate"]:
    if marker not in html: raise RuntimeError("V22 1A missing marker "+marker)
p.write_text(html,encoding="utf-8")
print("TEAM FJZ V22 1A canonical date pilot")
print("V22 1A topology:",after)
