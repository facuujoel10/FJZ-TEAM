import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":doc.lower().count("<style"),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":doc.count(".channel("),
        "timeouts":doc.count("setTimeout("),
        "intervals":doc.count("setInterval("),
        "listeners":doc.count("addEventListener("),
        "mutation_observers":doc.count("new MutationObserver"),
        "performance_observers":doc.count("new PerformanceObserver"),
    }

before=metrics(html)

for marker in [
    'meta name="fjz-professional-grouped-alerts" content="21.31"',
    "nutrition-targets",
    "option-head",
    "macro-row",
    "macro-chip",
    "meal-option-student",
    "nutrition-builder-actions",
    "renderNutritionOptionCoach",
    "renderNutritionMealStudent",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.32 prerequisite missing "+marker)

css=r"""
/* TEAM FJZ · V21.32 MOBILE NUTRITION MACRO GEOMETRY */

/* Never let a macro pill collapse into one-character columns. */
.option-head .macro-row{
  min-width:0;
  width:100%;
}
.option-head .macro-chip{
  flex:0 0 auto!important;
  width:auto!important;
  max-width:100%;
  min-width:max-content;
  white-space:nowrap!important;
  word-break:normal!important;
  overflow-wrap:normal!important;
  line-height:1.2;
}
.option-head>div:first-child{
  min-width:0;
}
.option-head>div:first-child>strong{
  word-break:normal!important;
  overflow-wrap:break-word!important;
}

/* On phones the option identity/macros own a full row.
   Actions move below instead of crushing the left column. */
@media(max-width:700px){
  #coachStudentBody .option-head,
  #studentSubBody .option-head{
    display:grid!important;
    grid-template-columns:minmax(0,1fr)!important;
    gap:9px!important;
    align-items:start!important;
    justify-content:stretch!important;
  }

  #coachStudentBody .option-head>div:first-child,
  #studentSubBody .option-head>div:first-child{
    width:100%!important;
    min-width:0!important;
    max-width:100%!important;
  }

  #coachStudentBody .option-head .macro-row,
  #studentSubBody .option-head .macro-row{
    display:flex!important;
    flex-wrap:wrap!important;
    align-items:center!important;
    gap:6px!important;
    width:100%!important;
    min-width:0!important;
    max-width:100%!important;
  }

  #coachStudentBody .option-head>.nutrition-builder-actions,
  #studentSubBody .option-head>.nutrition-builder-actions{
    width:100%!important;
    min-width:0!important;
    max-width:100%!important;
    display:flex!important;
    flex-wrap:wrap!important;
    justify-content:flex-start!important;
    align-items:center!important;
    gap:7px!important;
  }

  #coachStudentBody .option-head>.nutrition-builder-actions .btn,
  #studentSubBody .option-head>.nutrition-builder-actions .btn,
  #studentSubBody .option-head>.btn{
    flex:0 1 auto;
    max-width:100%;
    white-space:normal;
  }

  #coachStudentBody .option-card,
  #studentSubBody .meal-option-student{
    min-width:0!important;
    max-width:100%!important;
  }
}

/* Extra protection for very narrow phones. */
@media(max-width:390px){
  #coachStudentBody .option-head>.nutrition-builder-actions .btn{
    flex:1 1 calc(50% - 7px);
    min-width:0;
  }
  #studentSubBody .option-head>.btn{
    width:100%;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V21.32 expected one stylesheet, got "+str(len(styles)))
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-nutrition-mobile-macro-geometry" content="21.32">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V21.32 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-nutrition-mobile-macro-geometry" content="21.32"',
    "MOBILE NUTRITION MACRO GEOMETRY",
    ".option-head .macro-chip",
    "white-space:nowrap!important",
    "word-break:normal!important",
    "#coachStudentBody .option-head",
    "grid-template-columns:minmax(0,1fr)!important",
    "#coachStudentBody .option-head>.nutrition-builder-actions",
    "flex-wrap:wrap!important",
    "#studentSubBody .option-head",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.32 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.32 nutrition mobile macro geometry")
print("V21.32 BEFORE:",before)
print("V21.32 AFTER:",after)
