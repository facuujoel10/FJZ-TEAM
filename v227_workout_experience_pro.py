import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# V20.27 WORKOUT EXPERIENCE PRO — visual only
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
if before["styles"]!=1: raise RuntimeError("V20.27 expected one stylesheet: "+repr(before))

required=[
    "session-card","set-grid","set-n","session-progress","recommend","finishWorkout",
    "cloudConfirmationBeforeSuccess:true","duplicateSaveByDesignBlocked:true",
    "savedWorkoutCannotReopen:true","__fjzV226"
]
# V20.26 is CSS-only and has no JS marker; use meta fallback.
if "__fjzV226" in required and "__fjzV226" not in html:
    required.remove("__fjzV226")
    required.append('meta name="fjz-profile-360" content="20.26"')
missing=[x for x in required if x not in html]
if missing: raise RuntimeError("V20.27 workout authority missing: "+repr(missing))

css=r"""
/* TEAM FJZ · V20.27 WORKOUT EXPERIENCE PRO */

.session-progress{
  height:9px;
  border:1px solid #282b32;
  background:#0d0e12;
  box-shadow:inset 0 1px 3px rgba(0,0,0,.32);
}
.session-progress span{
  background:linear-gradient(90deg,var(--red2),var(--red));
  box-shadow:0 0 14px rgba(255,38,57,.20);
}

.session-card{
  position:relative;
  margin-bottom:14px;
  padding:17px;
  border-color:#2e3139;
  border-radius:18px;
  background:
    linear-gradient(180deg,rgba(255,255,255,.018),transparent 26%),
    linear-gradient(145deg,rgba(255,38,57,.025),transparent 48%),
    #101116;
  box-shadow:var(--shadow-card);
  overflow:hidden;
}

.session-card::before{
  content:"";
  position:absolute;
  left:0;
  top:0;
  bottom:0;
  width:3px;
  background:linear-gradient(180deg,var(--red),rgba(198,16,34,.18));
  border-radius:18px 0 0 18px;
}

.session-card .day-head{
  margin-bottom:10px;
  align-items:flex-start;
}

.session-card .day-head strong{
  color:#fff;
  font-size:16px;
  line-height:1.25;
  font-weight:900;
  letter-spacing:-.018em;
}

.session-card .day-head .tiny{
  margin-top:4px;
  color:#9da1ab;
  line-height:1.45;
}

.session-card .badge.amber{
  flex:0 0 auto;
  background:rgba(242,189,85,.08);
  border-color:rgba(242,189,85,.22);
  color:#f2c66c;
}

.session-card .coach-note{
  margin-top:10px;
  border-color:#2d3038;
  border-radius:12px;
  background:#0c0d10;
  color:#a8abb4;
  line-height:1.5;
}

.session-card .coach-note strong{
  color:#dfe1e6;
}

.v72-tech-layout{
  gap:10px;
}

.set-grid{
  grid-template-columns:40px repeat(3,minmax(0,1fr));
  gap:9px;
  padding:7px;
  border:1px solid #24272e;
  border-radius:13px;
  background:#0c0d10;
  align-items:end;
}

.set-grid+.set-grid{
  margin-top:8px;
}

.set-grid label{
  font-size:9px!important;
  font-weight:800;
  letter-spacing:.055em;
  text-transform:uppercase;
  color:#8f939e!important;
}

.set-grid .input{
  margin-top:5px;
  min-height:42px;
  padding:9px 9px;
  background:#121318;
  border-color:#30343d;
  border-radius:10px;
  color:#fff;
  font-size:15px;
  font-weight:800;
  text-align:center;
}

.set-grid .input:focus{
  background:#15161b;
  border-color:rgba(255,38,57,.64);
  box-shadow:var(--focus-ring);
}

.set-n{
  width:40px;
  height:42px;
  border:1px solid #30343d;
  border-radius:10px;
  background:linear-gradient(180deg,#17191f,#101116);
  color:#ff6c79;
  font-size:12px;
  font-weight:920;
}

.recommend{
  margin-top:12px;
  padding:12px 13px;
  border-left-width:3px;
  border-radius:0 12px 12px 0;
  background:rgba(255,38,57,.055);
  color:#dfe1e6;
  line-height:1.5;
}

.recommend strong,
.recommend b{
  color:#fff;
}

.recommend.coach{
  background:rgba(103,173,255,.055);
  border-left-color:var(--blue);
}

.session-card [id^="rec_"]{
  min-width:0;
}

/* Method / intensity panels inherit a clear nested surface. */
.session-card [class*="method"],
.session-card [class*="drop"],
.session-card [class*="superset"],
.session-card [class*="biserie"]{
  max-width:100%;
}

/* Workout hero: keep controls prominent without changing DOM. */
body:has(.session-card) #view>.hero{
  padding-bottom:14px;
  margin-bottom:10px;
  border-bottom:1px solid var(--border-soft);
}

body:has(.session-card) #view>.hero h2{
  font-size:27px;
}

body:has(.session-card) #view>.hero>.btn.primary,
body:has(.session-card) #view>.hero .btn.primary{
  min-height:42px;
  padding-left:16px;
  padding-right:16px;
}

/* Save state from V20.7 remains visible and calm. */
body.v207-session-saving .session-card{
  pointer-events:none;
}

body.v207-session-saving #view>.hero .btn.primary{
  opacity:.58;
}

/* Numeric fields: avoid spinner geometry shifts on WebKit. */
.session-card input[type="number"]{
  min-width:0;
  font-variant-numeric:tabular-nums;
}

@media(max-width:760px){
  .session-card{
    padding:14px;
    border-radius:16px;
  }

  .session-card .day-head{
    display:flex;
    gap:9px;
  }

  .session-card .day-head strong{
    font-size:15px;
  }

  .set-grid{
    grid-template-columns:36px repeat(3,minmax(0,1fr));
    gap:6px;
    padding:6px;
  }

  .set-n{
    width:36px;
    height:43px;
  }

  .set-grid .input{
    min-height:43px;
    padding:8px 5px;
    font-size:14px;
  }

  body:has(.session-card) #view>.hero{
    align-items:flex-start;
  }

  body:has(.session-card) #view>.hero>.btn.primary{
    width:100%;
  }
}

@media(max-width:420px){
  .session-card{
    padding:12px;
  }

  .set-grid{
    grid-template-columns:32px repeat(3,minmax(0,1fr));
    gap:5px;
    padding:5px;
  }

  .set-n{
    width:32px;
  }

  .set-grid label{
    font-size:8px!important;
  }

  .set-grid .input{
    padding-left:3px;
    padding-right:3px;
    font-size:13px;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V20.27 stylesheet surface changed: "+str(len(styles)))
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

marker='<meta name="fjz-workout-ui" content="20.27">'
if re.search(r'<meta\s+name=["\']fjz-workout-ui["\']',html,re.I):
    html=re.sub(r'<meta\s+name=["\']fjz-workout-ui["\']\s+content=["\'][^"\']*["\']\s*/?>',marker,html,count=1,flags=re.I)
else:
    html=html.replace("</head>",marker+"\n</head>",1)

after=metrics(html)
for key in ("styles","render_assignments","channels","mutation_observers","performance_observers","timeouts","rafs","listeners"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.27 runtime topology changed for "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-workout-ui" content="20.27"',"TEAM FJZ · V20.27 WORKOUT EXPERIENCE PRO",
    ".session-card",".set-grid",".set-n",".session-progress",".recommend",
    "cloudConfirmationBeforeSuccess:true","duplicateSaveByDesignBlocked:true",
    "savedWorkoutCannotReopen:true",'meta name="fjz-profile-360" content="20.26"'
]
missing=[x for x in critical if x not in html]
if missing: raise RuntimeError("V20.27 missing workout/stability marker: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.27 workout experience pro")
print("V20.27 BEFORE:",before)
print("V20.27 AFTER:",after)
print("V20.27 workout visual hierarchy polished; save/session runtime unchanged")
