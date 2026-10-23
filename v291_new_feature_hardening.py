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
    }

before=metrics(html)

for marker in [
    'meta name="fjz-final-product-layer" content="20.90"',
    "prBannerV291:true",
    "robustPrDetectionV291:true",
    "localizedWeightParsingV291:true",
    "normalizedExercisePrKeyV291:true",
    "successModalAfterConfirmedSave:true",
]:
    if marker not in html:
        raise RuntimeError("V20.91 prerequisite missing "+marker)

old="""'<div class="modal-head"><div><h3>Finalizar entrenamiento</h3><div class="muted tiny">Revisá antes de confirmar.</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+"""
new="""'<div class="modal-head v291-finish-head"><div><h3>Finalizar entrenamiento</h3><div class="muted tiny">Revisá antes de confirmar.</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+"""
if html.count(old)!=1:
    raise RuntimeError("V20.91 final workout modal anchor mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

old2="""'<div class="card"><strong>'+escV207(parts.join(' · '))+'</strong><div class="muted tiny" style="margin-top:6px">Se guardarán únicamente las series con datos válidos.</div></div>'+"""
new2="""'<div class="card v291-finish-summary"><strong>'+escV207(parts.join(' · '))+'</strong><div class="muted tiny" style="margin-top:6px">Se guardarán únicamente las series con datos válidos.</div></div>'+"""
if html.count(old2)!=1:
    raise RuntimeError("V20.91 finish summary anchor mismatch")
html=html.replace(old2,new2,1)

old3="""'<div class="pill-row" style="justify-content:flex-end;margin-top:12px"><button class="btn" onclick="closeModal()">Seguir entrenando</button><button class="btn primary" onclick="confirmPartialSessionV106()">Guardar y finalizar</button></div>'"""
new3="""'<div class="pill-row v291-finish-actions" style="justify-content:flex-end;margin-top:12px"><button class="btn" onclick="closeModal()">Seguir entrenando</button><button class="btn primary" onclick="confirmPartialSessionV106()">Guardar y finalizar</button></div>'"""
if html.count(old3)!=1:
    raise RuntimeError("V20.91 finish actions anchor mismatch")
html=html.replace(old3,new3,1)

css=r"""
/* TEAM FJZ · V20.91 NEW FEATURE + FINISH WORKOUT HARDENING */
.v291-finish-head{
  align-items:flex-start!important;
  gap:12px!important;
}
.v291-finish-head h3{
  margin:0!important;
  font-size:20px!important;
  line-height:1.15!important;
  letter-spacing:-.015em!important;
}
.v291-finish-head .muted.tiny{
  margin-top:5px!important;
  font-size:12px!important;
  line-height:1.4!important;
}
.v291-finish-summary{
  margin-top:12px!important;
  padding:14px!important;
}
.v291-finish-summary>strong{
  display:block!important;
  font-size:14px!important;
  line-height:1.4!important;
}
.v291-finish-summary .muted.tiny{
  font-size:12px!important;
  line-height:1.5!important;
}
.v291-finish-actions{
  gap:9px!important;
}
.v291-finish-actions>.btn{
  min-height:46px!important;
  padding:10px 14px!important;
  font-size:12.5px!important;
  line-height:1.2!important;
}
.v207-save-state .v207-save-title{
  font-size:19px!important;
  line-height:1.2!important;
}
.v207-save-state .v207-save-copy{
  font-size:12.5px!important;
  line-height:1.55!important;
}
.v207-save-state .v207-save-actions>.btn{
  min-height:46px!important;
  font-size:12.5px!important;
}
.v291-pr-banner{
  min-width:0!important;
  overflow:hidden!important;
}
.v291-pr-copy{
  min-width:0!important;
}
.v291-pr-copy strong,
.v291-pr-copy b,
.v291-pr-copy small{
  overflow-wrap:anywhere!important;
}
@media(max-width:430px){
  .v291-finish-head h3{font-size:19px!important}
  .v291-finish-head .muted.tiny,
  .v291-finish-summary .muted.tiny{font-size:12px!important}
  .v291-finish-summary>strong{font-size:13px!important}
  .v291-finish-actions{
    display:grid!important;
    grid-template-columns:1fr!important;
    width:100%!important;
  }
  .v291-finish-actions>.btn{
    width:100%!important;
    min-height:48px!important;
    font-size:13px!important;
  }
  .v207-save-state{
    padding:16px 4px 6px!important;
  }
  .v207-save-state .v207-save-title{font-size:18px!important}
  .v207-save-state .v207-save-copy{font-size:12.5px!important}
  .v291-pr-banner{
    grid-template-columns:44px minmax(0,1fr)!important;
    gap:10px!important;
    padding:13px 39px 13px 13px!important;
  }
  .v291-pr-icon{width:40px!important;height:40px!important;font-size:21px!important}
  .v291-pr-copy strong{font-size:15px!important}
  .v291-pr-copy b{font-size:18px!important}
  .v291-pr-copy small{font-size:10.5px!important;line-height:1.4!important}
}
"""
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V20.91 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-new-feature-hardening" content="20.91">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V20.91 topology changed "+key+": "+repr({"before":before,"after":after}))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.91 new feature + finish workout hardening")
print("V20.91 BEFORE:",before)
print("V20.91 AFTER:",after)
