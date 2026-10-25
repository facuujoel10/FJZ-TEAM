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
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

def edit_script(doc,sid,fn):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(sid)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m: raise RuntimeError("V21.07 missing script "+sid)
    body=fn(m.group(2))
    return doc[:m.start()]+m.group(1)+body+m.group(3)+doc[m.end():]

before=metrics(html)

# Remove loading-like first-frame language from the Coach student summary.
def patch_v175(body):
    old='<span id="v175SummaryState" class="muted micro">Actualizando…</span>'
    new='<span id="v175SummaryState" class="muted micro v307-profile-sync-state" aria-live="polite"></span>'
    if body.count(old)!=1:
        raise RuntimeError("V21.07 summary-state anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old_success="if(el('v175SummaryState'))el('v175SummaryState').textContent='Actualizado';"
    new_success="if(el('v175SummaryState'))el('v175SummaryState').textContent='';"
    if body.count(old_success)!=1:
        raise RuntimeError("V21.07 summary-success anchor mismatch: "+str(body.count(old_success)))
    body=body.replace(old_success,new_success,1)

    old_final=r"""    const summaryState=el('v175SummaryState');
    if(summaryState&&/Actualizando|Preparando|Cargando/i.test(summaryState.textContent||'')){
      summaryState.textContent=failed?'Actualizado · datos parciales':'Actualizado';
    }"""
    new_final=r"""    const summaryState=el('v175SummaryState');
    if(summaryState){
      summaryState.textContent=failed?'Actualizado · datos parciales · la ficha sigue disponible':'';
      summaryState.classList.toggle('v307-sync-warning',!!failed);
    }"""
    if body.count(old_final)!=1:
        raise RuntimeError("V21.07 final-state anchor mismatch: "+str(body.count(old_final)))
    body=body.replace(old_final,new_final,1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

css=r"""
/* TEAM FJZ · V21.07 COACH PROFILE SYNC UI */
.v307-profile-sync-state:empty{display:none!important}
.v307-profile-sync-state.v307-sync-warning{
  display:inline-flex!important;
  align-items:center;
  min-height:24px;
  padding:4px 8px;
  border:1px solid rgba(242,189,85,.30);
  border-radius:999px;
  background:rgba(242,189,85,.06);
  color:#f2c76c!important;
  font-weight:850;
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V21.07 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-coach-profile-sync-ui" content="21.07">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V21.07 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-coach-profile-sync-ui" content="21.07"',
    'v307-profile-sync-state',
    "Actualizado · datos parciales · la ficha sigue disponible",
    "summaryState.textContent=failed?",
]:
    if marker not in html:
        raise RuntimeError("V21.07 missing marker "+marker)

# No confusing transient copy should remain in the Coach 360 first frame.
v175=re.search(r'<script[^>]*id=["\']v175ProfileAgendaCoachCenterRuntime["\'][^>]*>(.*?)</script>',html,re.S|re.I)
if not v175: raise RuntimeError("V21.07 V175 missing after patch")
if "Actualizando…" in v175.group(1):
    raise RuntimeError("V21.07 stale Actualizando copy remains")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.07 coach profile sync UI")
print("V21.07 BEFORE:",before)
print("V21.07 AFTER:",after)
