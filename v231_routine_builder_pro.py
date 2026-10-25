import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# V20.31 ROUTINE BUILDER PRO — visual only
def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "render_assignments":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

before=metrics(html)
if before["styles"]!=1: raise RuntimeError("V20.31 expected one stylesheet: "+repr(before))

required=[
    "day-card","exercise-row","library-item","saveExercise",
    "modalReorderUsesAtomicRpc:true","routineBackdropCloseBlocked:true",
    "singleExerciseSave:true","preservesSessionHistory:true",
    'meta name="fjz-agenda-alerts-ui" content="20.30"'
]
missing=[x for x in required if x not in html]
if missing: raise RuntimeError("V20.31 routine authority missing: "+repr(missing))

css=r"""
/* TEAM FJZ · V20.31 ROUTINE BUILDER PRO */

.day-card{
  margin-bottom:14px;
  border-color:#2e3139;
  border-radius:18px;
  background:
    linear-gradient(180deg,rgba(255,255,255,.016),transparent 24%),
    #101116;
  box-shadow:var(--shadow-card);
  overflow:hidden;
}

.day-card>.section-title,
.day-card>.day-head{
  margin-top:0;
  padding-bottom:10px;
  border-bottom:1px solid var(--border-soft);
}

.day-card h3,
.day-card .day-name{
  color:#fff;
  font-weight:900;
  letter-spacing:-.018em;
}

.exercise-row{
  position:relative;
  min-width:0;
  padding:13px 0;
  border-top-color:#25282f;
  background:transparent;
}

.exercise-row:first-child{
  border-top:0;
}

.exercise-row h4{
  color:#f5f6f8;
  font-size:13px;
  line-height:1.35;
  font-weight:880;
  letter-spacing:-.012em;
}

.exercise-row .muted,
.exercise-row .tiny,
.exercise-row .micro{
  color:#9296a1;
  line-height:1.45;
}

.exercise-row .btn{
  min-height:31px;
}

.exercise-row .btn.primary{
  box-shadow:none;
}

/* Inputs inside routine editor */
.day-card .input,
.exercise-row .input,
.modal .exercise-row .input{
  min-height:40px;
  background:#0d0e12;
  border-color:#30343d;
  border-radius:10px;
}

.day-card .input:focus,
.exercise-row .input:focus{
  background:#111217;
  border-color:rgba(255,38,57,.62);
}

.day-card label,
.exercise-row label{
  color:#a0a4ae;
  font-size:9px;
  font-weight:780;
  line-height:1.35;
}

.library-item{
  padding:12px 13px;
  border-color:#2c3038;
  border-radius:13px;
  background:#0f1014;
  box-shadow:none;
}

.library-item h4{
  color:#f4f5f7;
  font-size:13px;
  font-weight:870;
  margin-bottom:4px;
}

.library-item .tiny,
.library-item .micro{
  color:#9599a4;
}

.library-item .btn{
  min-height:32px;
}

/* Exercise library / modal */
.modal .library-item{
  background:#0d0e12;
}

.modal .library-item:hover{
  border-color:#3b3f49;
}

.modal .tabs{
  margin-bottom:10px;
}

.modal .section-title{
  margin-top:6px;
}

/* Reorder/move modal: emphasize destination, not animation. */
[id*="MoveExercise"],
[id*="moveExercise"]{
  max-width:100%;
}

.modal select.input{
  min-height:42px;
}

/* Method/intensification boxes */
.exercise-row [class*="method"],
.exercise-row [class*="intens"],
.exercise-row [class*="drop"],
.exercise-row [class*="super"],
.exercise-row [class*="biserie"]{
  max-width:100%;
}

.exercise-row [class*="method"]{
  border-color:#2c3038;
}

/* Routine summary/actions */
.day-card .pill-row{
  gap:6px;
}

.day-card .badge{
  font-size:9px;
  font-weight:820;
}

.day-card .recommend{
  margin-top:10px;
}

/* Clear coach hierarchy on desktop */
@media(min-width:901px){
  .day-card{
    padding:17px;
  }

  .exercise-row{
    padding-top:14px;
    padding-bottom:14px;
  }
}

@media(max-width:760px){
  .day-card{
    border-radius:16px;
  }

  .day-card>.section-title,
  .day-card>.day-head{
    align-items:flex-start;
  }

  .exercise-row{
    padding:12px 0;
  }

  .exercise-row>.row,
  .exercise-row>.pill-row{
    gap:6px;
  }

  .library-item{
    padding:11px;
  }
}

@media(max-width:480px){
  .day-card{
    padding:12px!important;
  }

  .exercise-row h4{
    font-size:12px;
  }

  .exercise-row .btn.small,
  .library-item .btn.small{
    min-height:34px;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V20.31 stylesheet surface changed: "+str(len(styles)))
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

marker='<meta name="fjz-routine-builder-ui" content="20.31">'
if re.search(r'<meta\s+name=["\']fjz-routine-builder-ui["\']',html,re.I):
    html=re.sub(r'<meta\s+name=["\']fjz-routine-builder-ui["\']\s+content=["\'][^"\']*["\']\s*/?>',marker,html,count=1,flags=re.I)
else:
    html=html.replace("</head>",marker+"\n</head>",1)

after=metrics(html)
for key in ("styles","render_assignments","channels","mutation_observers","performance_observers","timeouts","rafs","listeners"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.31 runtime topology changed for "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-routine-builder-ui" content="20.31"',
    "TEAM FJZ · V20.31 ROUTINE BUILDER PRO",
    ".day-card",".exercise-row",".library-item",
    "modalReorderUsesAtomicRpc:true","routineBackdropCloseBlocked:true",
    "singleExerciseSave:true","preservesSessionHistory:true",
    'meta name="fjz-agenda-alerts-ui" content="20.30"'
]
missing=[x for x in critical if x not in html]
if missing: raise RuntimeError("V20.31 missing routine/stability marker: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.31 routine builder pro")
print("V20.31 BEFORE:",before)
print("V20.31 AFTER:",after)
print("V20.31 routine builder visual hierarchy polished; save/reorder runtime unchanged")
