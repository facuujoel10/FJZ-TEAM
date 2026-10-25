import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# V20.28 TRACKING & PROGRESS PRO — visual only
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
if before["styles"]!=1: raise RuntimeError("V20.28 expected one stylesheet: "+repr(before))

required=[
    "tracking-grid","track-score","tracking-form","track-row","metric-grid",
    "v205-chart","v205-chart-kpi","renderTrackingStudent","renderProgress",
    "measurementEditRepair:true",'meta name="fjz-workout-ui" content="20.27"'
]
missing=[x for x in required if x not in html]
if missing: raise RuntimeError("V20.28 tracking/progress authority missing: "+repr(missing))

css=r"""
/* TEAM FJZ · V20.28 TRACKING & PROGRESS PRO */

.tracking-form{
  gap:14px;
}

.tracking-form>.form-grid{
  gap:9px;
  padding:12px;
  border:1px solid #292c34;
  border-radius:14px;
  background:#0d0e12;
}

.tracking-grid{
  gap:9px;
}

.track-score{
  min-width:0;
  padding:12px;
  border-color:#2c3038;
  border-radius:14px;
  background:
    linear-gradient(155deg,rgba(255,38,57,.03),transparent 55%),
    #111217;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.018);
}

.track-score label{
  margin-bottom:8px;
  color:#a5a9b3;
  font-size:9px;
  line-height:1.3;
  font-weight:850;
  letter-spacing:.055em;
  text-transform:uppercase;
}

.track-score input{
  min-height:44px;
  background:#0b0c0f;
  border-color:#30343d;
  border-radius:10px;
  color:#fff;
  font-size:19px;
  font-weight:920;
  text-align:center;
  font-variant-numeric:tabular-nums;
}

.track-score input:focus{
  background:#111217;
  border-color:rgba(255,38,57,.62);
  box-shadow:var(--focus-ring);
}

.tracking-form textarea{
  line-height:1.55;
  resize:vertical;
}

.tracking-form>.btn.primary{
  min-height:44px;
  font-size:13px;
}

/* Tracking/history cards */
.track-list{
  gap:9px;
}

.track-row{
  padding:13px 14px;
  border-color:#2c3038;
  border-radius:14px;
  background:#101116;
  box-shadow:none;
}

.track-row-head{
  gap:10px;
}

.track-row-head strong{
  color:#f4f5f7;
  font-size:13px;
  font-weight:860;
}

.track-row-head .tiny{
  margin-top:4px;
  line-height:1.45;
}

/* Student tracking page cards: visually separate the 3 workflows. */
#studentSubBody>.card{
  border-color:#2d3038;
  border-radius:18px;
  box-shadow:var(--shadow-card);
}

#studentSubBody>.card>.section-title{
  margin-top:0;
}

#studentSubBody>.card>.section-title h3{
  color:#f7f8fa;
  font-weight:900;
  letter-spacing:-.018em;
}

#trackingStudentHistory{
  margin-top:16px!important;
}

/* Measurement/date fields remain geometry-safe. */
#mDate,#mWeight,#mWaist,#mAbd,#mHip,#mChest,
#progressPhotoDate,#progressPhotoPose,#progressPhotoFile,
#ciWeight,#ciWeek,#ciHunger{
  min-width:0!important;
  max-width:100%!important;
}

/* Metric summaries */
.metric-grid{
  gap:9px;
}

.metric-grid .metric{
  min-width:0;
  min-height:88px;
  display:flex;
  flex-direction:column;
  justify-content:center;
  padding:12px!important;
  border-color:#2c3038!important;
  border-radius:14px!important;
  background:
    linear-gradient(150deg,rgba(255,38,57,.025),transparent 52%),
    #111217!important;
}

.metric-grid .metric strong{
  color:#fff;
  font-size:22px;
  line-height:1.05;
  font-weight:920;
  letter-spacing:-.035em;
  font-variant-numeric:tabular-nums;
}

.metric-grid .metric span,
.metric-grid .metric .muted{
  margin-top:6px;
  color:#9a9ea9;
  font-size:9px;
  font-weight:760;
  line-height:1.35;
}

/* V20.5 professional charts, aligned with new design system. */
.v205-chart{
  border-color:#2d3038;
  border-radius:17px;
  background:
    linear-gradient(180deg,rgba(255,255,255,.018),transparent 32%),
    #0c0d10;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.014);
}

.v205-chart-title{
  color:#f6f7f9;
  font-size:13px;
  font-weight:900;
  letter-spacing:-.015em;
}

.v205-chart-sub{
  margin-top:4px;
  color:#969aa5;
  font-size:9px;
  line-height:1.4;
}

.v205-chart-kpis{
  gap:7px;
}

.v205-chart-kpi{
  min-width:82px;
  padding:7px 9px;
  border-color:#2c3038;
  border-radius:10px;
  background:#111217;
}

.v205-chart-kpi span{
  color:#8f939e;
  font-size:7px;
  font-weight:800;
}

.v205-chart-kpi strong{
  color:#f5f6f8;
  font-size:11px;
  font-weight:900;
}

.v205-grid-line{
  stroke:rgba(255,255,255,.055);
}

.v205-line{
  stroke:#ff3043;
}

.v205-point{
  fill:#0d0e12;
  stroke:#ff3043;
}

.v205-point-last{
  fill:#ff3043;
  stroke:#fff;
}

.history-item{
  border-color:#2b2e36;
}

.delta-up{color:#55db98}
.delta-down{color:#ff6d79}
.delta-flat{color:#efbf62}

/* Private progress photo inputs */
input[type="file"].input{
  padding:8px;
}

@media(max-width:900px){
  .tracking-grid{
    grid-template-columns:repeat(3,minmax(0,1fr));
  }

  .tracking-form>.form-grid{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
  }
}

@media(max-width:620px){
  .tracking-grid{
    grid-template-columns:repeat(2,minmax(0,1fr));
  }

  .track-score{
    padding:10px;
  }

  .track-score input{
    min-height:42px;
    font-size:18px;
  }

  .tracking-form>.form-grid{
    grid-template-columns:1fr!important;
    padding:10px;
  }

  .metric-grid{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
  }

  .v205-chart{
    padding:11px;
  }
}

@media(max-width:380px){
  .tracking-grid{
    gap:7px;
  }

  .track-score{
    padding:9px;
  }

  .metric-grid .metric{
    min-height:80px;
    padding:10px!important;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V20.28 stylesheet surface changed: "+str(len(styles)))
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

marker='<meta name="fjz-tracking-progress-ui" content="20.28">'
if re.search(r'<meta\s+name=["\']fjz-tracking-progress-ui["\']',html,re.I):
    html=re.sub(r'<meta\s+name=["\']fjz-tracking-progress-ui["\']\s+content=["\'][^"\']*["\']\s*/?>',marker,html,count=1,flags=re.I)
else:
    html=html.replace("</head>",marker+"\n</head>",1)

after=metrics(html)
for key in ("styles","render_assignments","channels","mutation_observers","performance_observers","timeouts","rafs","listeners"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.28 runtime topology changed for "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-tracking-progress-ui" content="20.28"',
    "TEAM FJZ · V20.28 TRACKING & PROGRESS PRO",
    ".tracking-form",".tracking-grid",".track-score",".track-row",".metric-grid",
    ".v205-chart",".v205-chart-kpi","measurementEditRepair:true",
    'meta name="fjz-workout-ui" content="20.27"'
]
missing=[x for x in critical if x not in html]
if missing: raise RuntimeError("V20.28 missing tracking/stability marker: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.28 tracking progress pro")
print("V20.28 BEFORE:",before)
print("V20.28 AFTER:",after)
print("V20.28 tracking/progress visual hierarchy polished; data/runtime unchanged")
