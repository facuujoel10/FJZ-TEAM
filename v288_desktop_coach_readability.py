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
  'meta name="fjz-session-exercise-comments" content="20.87"',
  "v225-student-list","v80-attention-item","student-main"
]:
    if marker not in html: raise RuntimeError("V20.88 prerequisite missing "+marker)

css=r"""
/* TEAM FJZ · V20.88 DESKTOP COACH READABILITY */
@media(min-width:1000px){
  /* Student list: primary identity */
  .v225-student-list .student-row{
    min-height:82px!important;
    padding:16px!important;
    gap:16px!important;
  }
  .v225-student-list .student-main{
    gap:13px!important;
  }
  .v225-student-list .student-main .avatar{
    width:48px!important;
    height:48px!important;
    font-size:14px!important;
  }
  .v225-student-list .student-main>div>strong{
    display:block!important;
    font-size:15px!important;
    line-height:1.25!important;
    font-weight:900!important;
    color:#f4f5f7!important;
  }
  .v225-student-list .student-main>div>.muted.tiny{
    margin-top:4px!important;
    font-size:12.5px!important;
    line-height:1.35!important;
    color:#a8adb6!important;
  }

  /* Secondary student metrics */
  .v225-student-list .student-row>div:not(.student-main)>strong{
    font-size:14px!important;
    line-height:1.2!important;
  }
  .v225-student-list .student-row>div:not(.student-main)>.muted.tiny{
    margin-top:4px!important;
    font-size:11.5px!important;
    line-height:1.3!important;
  }
  .v225-student-list .badge{
    font-size:11.5px!important;
    padding:7px 10px!important;
  }
  .v225-student-list .btn.small{
    min-height:35px!important;
    font-size:11px!important;
  }

  /* Activity / attention center */
  .v225-attention-card .section-title h3{
    font-size:19px!important;
  }
  .v225-attention-card .section-title .muted.tiny{
    font-size:12.5px!important;
    line-height:1.45!important;
  }
  .v225-filter-row .btn{
    min-height:36px!important;
    padding:8px 12px!important;
    font-size:11px!important;
  }
  .v80-attention{
    gap:11px!important;
  }
  .v80-attention-item{
    padding:14px!important;
  }
  .v80-attention-item h4{
    font-size:14px!important;
    line-height:1.35!important;
  }
  .v80-attention-item p,
  .v80-attention-item .muted.tiny{
    margin-top:6px!important;
    font-size:12px!important;
    line-height:1.5!important;
    color:#aeb3bc!important;
  }
  .v80-attention-item .badge{
    font-size:11px!important;
  }
  .v80-attention-actions .btn.small{
    min-height:34px!important;
    font-size:10.5px!important;
  }

  /* General coach dashboard helper copy */
  .v225-students-head .muted.tiny,
  .v225-today-card .muted.tiny,
  .v225-flow-card .muted.tiny,
  #v252PriorityCenter .muted.tiny,
  #v259CoachCalendar .muted.tiny{
    font-size:12px!important;
    line-height:1.45!important;
  }
  .v225-flow-step strong{
    font-size:14px!important;
  }
  .v225-flow-step p{
    font-size:12px!important;
  }
  .v225-signal span{
    font-size:12px!important;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V20.88 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-desktop-coach-readability" content="20.88">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V20.88 topology changed "+k)

for marker in [
  'meta name="fjz-desktop-coach-readability" content="20.88"',
  ".v225-student-list .student-main>div>strong",
  "font-size:15px!important",
  ".v80-attention-item h4",
  "font-size:14px!important",
  ".v80-attention-item .muted.tiny",
  "font-size:12px!important",
]:
    if marker not in html: raise RuntimeError("V20.88 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.88 desktop coach readability")
print("V20.88 BEFORE:",before)
print("V20.88 AFTER:",after)
