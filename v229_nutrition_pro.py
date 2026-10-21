import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# V20.29 NUTRITION PRO — visual only
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
if before["styles"]!=1: raise RuntimeError("V20.29 expected one stylesheet: "+repr(before))

required=[
    "nutrition-targets","macro-card","macro-chip","meal-plan","meal-block","option-card",
    "meal-option-student","macro-preview","nutrition-log-row","nutrition-datebar",
    "nutrition-builder-actions","renderNutritionMealStudent","updateMacroPreview",
    'meta name="fjz-tracking-progress-ui" content="20.28"'
]
missing=[x for x in required if x not in html]
if missing: raise RuntimeError("V20.29 nutrition authority missing: "+repr(missing))

css=r"""
/* TEAM FJZ · V20.29 NUTRITION PRO */

.nutrition-targets{
  gap:9px;
}

.macro-card{
  min-width:0;
  min-height:94px;
  display:flex;
  flex-direction:column;
  justify-content:center;
  padding:13px;
  border-color:#2c3038;
  border-radius:14px;
  background:
    linear-gradient(155deg,rgba(255,38,57,.03),transparent 52%),
    #111217;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.018);
}

.macro-card strong{
  color:#fff;
  font-size:22px;
  line-height:1.05;
  font-weight:920;
  letter-spacing:-.035em;
  font-variant-numeric:tabular-nums;
}

.macro-card .muted,
.macro-card span{
  margin-top:5px;
}

.macro-row{
  gap:6px;
}

.macro-chip{
  min-height:26px;
  padding:5px 8px;
  border-color:#2e3139;
  background:#0d0e12;
  color:#a3a7b1;
  font-size:10px;
  font-weight:760;
  font-variant-numeric:tabular-nums;
}

.meal-plan{
  gap:14px;
}

.meal-block{
  padding:15px;
  border-color:#2d3038;
  border-radius:17px;
  background:
    linear-gradient(180deg,rgba(255,255,255,.016),transparent 24%),
    #101116;
  box-shadow:var(--shadow-card);
}

.meal-head{
  padding-bottom:10px;
  border-bottom:1px solid var(--border-soft);
}

.meal-head strong{
  color:#fff;
  font-size:15px;
  font-weight:900;
  letter-spacing:-.018em;
}

.meal-head .tiny{
  margin-top:4px;
  line-height:1.45;
}

.option-grid{
  gap:9px;
  margin-top:11px;
}

.option-card,
.meal-option-student{
  padding:12px 13px;
  border-color:#2c3038;
  border-radius:13px;
  background:#0d0e12;
}

.option-card:hover,
.meal-option-student:hover{
  border-color:#363a43;
}

.option-head{
  gap:9px;
}

.option-head strong{
  color:#f4f5f7;
  font-size:13px;
  font-weight:860;
}

.meal-items-text{
  margin-top:9px;
  gap:5px;
  padding-top:8px;
  border-top:1px solid #24272e;
}

.meal-items-text .tiny{
  color:#a1a5af;
  line-height:1.45;
}

.food-item,
.food-item-v61{
  border-top-color:#25282f;
}

.food-item strong,
.food-item-v61 strong{
  color:#f1f2f5;
}

.food-choice{
  border-color:#2c3038;
  border-radius:13px;
  background:#101116;
}

.food-choice:hover{
  border-color:#3a3e48;
  background:#14161b;
}

.measure-editor,
.macro-measure-grid{
  gap:8px;
}

.measure-pill{
  border-color:#2e3139;
  background:#0d0e12;
  color:#a6aab4;
}

/* Macro calculator */
.macro-preview{
  gap:8px;
}

.macro-preview>div{
  min-width:0;
  min-height:76px;
  display:flex;
  flex-direction:column;
  justify-content:center;
  padding:10px;
  border-color:#2c3038;
  border-radius:12px;
  background:#101116;
}

.macro-preview strong{
  margin-top:5px;
  color:#fff;
  font-size:18px;
  font-weight:920;
  font-variant-numeric:tabular-nums;
}

.nutrition-builder-actions{
  gap:8px;
}

.nutrition-builder-actions .btn{
  min-height:38px;
}

/* Daily log */
.nutrition-datebar{
  gap:9px;
  padding:10px;
  border:1px solid #282b32;
  border-radius:13px;
  background:#0d0e12;
}

.nutrition-datebar label{
  min-width:180px;
  margin:0;
}

.nutrition-log{
  gap:8px;
}

.nutrition-log-row{
  padding:11px 12px;
  border-color:#2c3038;
  border-radius:13px;
  background:#101116;
  box-shadow:none;
}

.nutrition-log-row strong{
  color:#f3f4f6;
}

.nutrition-note{
  border-color:rgba(103,173,255,.22);
  border-left:3px solid var(--blue);
  border-radius:0 12px 12px 0;
  background:rgba(103,173,255,.055);
  color:#c7d6e9;
}

/* Templates / adherence / revisions */
.v63-adherence{
  gap:9px;
}

.v63-history,
.v63-template-grid{
  gap:8px;
}

.v63-history-row,
.v63-template-row{
  border-color:#2c3038;
  border-radius:13px;
  background:#101116;
}

.plan-visible-note{
  border-color:rgba(59,213,138,.22);
  background:rgba(59,213,138,.055);
  color:#c6efd7;
}

.unit-config{
  border-color:#2c3038;
  background:#0d0e12;
}

.nutrition-section-gap{
  height:16px;
}

/* Student nutrition navigation stays compact and scroll-safe. */
#studentMainTabs{
  gap:7px;
}

@media(max-width:900px){
  .nutrition-targets,
  .macro-preview{
    grid-template-columns:repeat(2,minmax(0,1fr));
  }

  .meal-block{
    padding:13px;
  }
}

@media(max-width:650px){
  .nutrition-targets{
    grid-template-columns:repeat(2,minmax(0,1fr));
  }

  .macro-card{
    min-height:84px;
    padding:11px;
  }

  .macro-card strong{
    font-size:20px;
  }

  .meal-block{
    border-radius:15px;
  }

  .option-head{
    display:grid;
    grid-template-columns:minmax(0,1fr) auto;
    align-items:start;
  }

  .option-head .btn{
    min-width:82px;
  }

  .macro-preview{
    grid-template-columns:repeat(2,minmax(0,1fr));
  }

  .nutrition-datebar{
    align-items:stretch;
  }

  .nutrition-datebar label{
    min-width:0;
    flex:1 1 100%;
  }

  .nutrition-datebar .btn{
    width:100%;
  }
}

@media(max-width:380px){
  .nutrition-targets{
    gap:7px;
  }

  .macro-card{
    padding:10px;
  }

  .macro-chip{
    font-size:9px;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V20.29 stylesheet surface changed: "+str(len(styles)))
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

marker='<meta name="fjz-nutrition-ui" content="20.29">'
if re.search(r'<meta\s+name=["\']fjz-nutrition-ui["\']',html,re.I):
    html=re.sub(r'<meta\s+name=["\']fjz-nutrition-ui["\']\s+content=["\'][^"\']*["\']\s*/?>',marker,html,count=1,flags=re.I)
else:
    html=html.replace("</head>",marker+"\n</head>",1)

after=metrics(html)
for key in ("styles","render_assignments","channels","mutation_observers","performance_observers","timeouts","rafs","listeners"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.29 runtime topology changed for "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-nutrition-ui" content="20.29"',"TEAM FJZ · V20.29 NUTRITION PRO",
    ".nutrition-targets",".macro-card",".meal-block",".meal-option-student",
    ".macro-preview",".nutrition-log-row",".nutrition-datebar",
    "renderNutritionMealStudent","updateMacroPreview",
    'meta name="fjz-tracking-progress-ui" content="20.28"'
]
missing=[x for x in critical if x not in html]
if missing: raise RuntimeError("V20.29 missing nutrition/stability marker: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.29 nutrition pro")
print("V20.29 BEFORE:",before)
print("V20.29 AFTER:",after)
print("V20.29 nutrition visual hierarchy polished; macros/logging runtime unchanged")
