import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.23 PROFESSIONAL UI FOUNDATION
# =========================================================
# Visual-only foundation on top of the V20.22 stability checkpoint.
# No render wrappers, listeners, timers, RAFs, channels or observers.
# Keep the existing single consolidated stylesheet and append overrides there.

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

if before["styles"]!=1:
    raise RuntimeError("V20.23 expected one consolidated stylesheet: "+repr(before))
if before["render_assignments"]!=20:
    raise RuntimeError("V20.23 expected V20.22 render baseline: "+repr(before))
if before["channels"]!=2:
    raise RuntimeError("V20.23 expected two realtime channel definitions: "+repr(before))

css=r"""
/* =========================================================
   TEAM FJZ · V20.23 PROFESSIONAL UI FOUNDATION
   Visual hierarchy only — no layout animation / no JS.
   ========================================================= */

:root{
  --bg:#070708;
  --panel:#0d0e11;
  --card:#121318;
  --card2:#181a20;
  --surface-raised:#1d1f26;
  --surface-soft:#101116;
  --border:#292c34;
  --border-soft:#20232a;
  --border-strong:#3a3e49;
  --text:#f6f7f9;
  --muted:#9b9faa;
  --muted-strong:#b8bbc4;
  --red:#ff2639;
  --red2:#c61022;
  --red-soft:rgba(255,38,57,.10);
  --red-border:rgba(255,38,57,.34);
  --green:#3bd58a;
  --amber:#f2bd55;
  --blue:#67adff;
  --shadow:0 20px 55px rgba(0,0,0,.38);
  --shadow-card:0 12px 34px rgba(0,0,0,.20);
  --shadow-float:0 28px 80px rgba(0,0,0,.56);
  --focus-ring:0 0 0 3px rgba(255,38,57,.15);
  --radius-xs:8px;
  --radius-sm:11px;
  --radius-md:14px;
  --radius-lg:18px;
  --radius-xl:22px;
}

html{
  background:var(--bg);
  color-scheme:dark;
}

body{
  background:
    radial-gradient(circle at 82% -12%,rgba(255,38,57,.12),transparent 31%),
    radial-gradient(circle at 8% 22%,rgba(255,255,255,.018),transparent 24%),
    linear-gradient(180deg,#09090b 0%,#070708 54%,#060607 100%);
  color:var(--text);
  -webkit-font-smoothing:antialiased;
  text-rendering:optimizeLegibility;
}

/* ---------- App chrome ---------- */
.topbar{
  background:rgba(8,8,10,.91);
  border-bottom-color:rgba(255,255,255,.07);
  box-shadow:0 8px 30px rgba(0,0,0,.18);
  backdrop-filter:blur(18px) saturate(125%);
  -webkit-backdrop-filter:blur(18px) saturate(125%);
}

.brand{
  gap:12px;
}

.brand img{
  filter:drop-shadow(0 8px 18px rgba(0,0,0,.30));
}

.brand h1{
  color:#fff;
  font-weight:900;
  letter-spacing:-.02em;
}

.brand small{
  color:#8f929d;
  font-weight:750;
}

.mode-switch,
.segmented{
  background:rgba(14,15,19,.92);
  border-color:var(--border);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.025);
}

.mode-switch button,
.segmented button{
  color:var(--muted);
}

.mode-switch .active,
.segmented button.active{
  background:linear-gradient(180deg,#24262d,#1a1c22);
  color:#fff;
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.035);
}

.mode-switch .active{
  background:linear-gradient(180deg,var(--red),var(--red2));
  box-shadow:0 5px 16px rgba(198,16,34,.20);
}

.shell{
  width:100%;
}

/* ---------- Typography / hierarchy ---------- */
.hero{
  margin-bottom:22px;
}

.hero h2{
  color:#fff;
  font-weight:920;
  letter-spacing:-.035em;
  line-height:1.08;
}

.hero p{
  color:var(--muted);
  line-height:1.55;
}

.section-title{
  margin-top:10px;
}

.section-title h3{
  color:#f8f8fa;
  font-weight:880;
  letter-spacing:-.018em;
}

.muted{
  color:var(--muted);
}

.tiny,.micro{
  line-height:1.4;
}

/* ---------- Surface system ---------- */
.card,
.metric,
.track-row,
.track-score,
.history-item,
.library-item,
.student-row,
.coach-note,
.alert{
  background:
    linear-gradient(180deg,rgba(255,255,255,.018),rgba(255,255,255,0) 38%),
    var(--card);
  border-color:var(--border);
  box-shadow:var(--shadow-card);
}

.card{
  border-radius:var(--radius-lg);
  padding:17px;
}

.grid.kpi .card{
  position:relative;
  overflow:hidden;
  min-width:0;
  border-color:#2d3038;
}

.grid.kpi .card strong{
  color:#fff;
  font-weight:920;
  letter-spacing:-.035em;
  line-height:1.05;
}

.grid.kpi .card span{
  color:var(--muted);
  font-weight:650;
}

.metric,
.track-score{
  border-radius:var(--radius-md);
}

.metric strong{
  color:#fff;
  font-weight:900;
  letter-spacing:-.025em;
}

.student-row{
  border-radius:var(--radius-md);
  background:
    linear-gradient(90deg,rgba(255,38,57,.022),transparent 30%),
    var(--card);
}

.student-main strong{
  color:#f8f8fa;
  letter-spacing:-.01em;
}

.avatar,
.v70-avatar{
  border-color:#3b3e48;
  background:linear-gradient(145deg,#25272e,#15161b);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.035);
}

.day-card,
.session-card{
  border-color:var(--border);
}

.exercise-row{
  border-top-color:var(--border-soft);
}

.exercise-row h4,
.library-item h4{
  color:#f3f4f6;
  font-weight:850;
}

.library-item{
  border-radius:var(--radius-md);
}

.history-item,
.track-row{
  border-radius:var(--radius-md);
}

.chart-wrap{
  background:#0a0b0e;
  border-color:var(--border);
  border-radius:var(--radius-md);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.018);
}

/* ---------- Buttons ---------- */
.btn{
  min-height:38px;
  border-radius:var(--radius-sm);
  border-color:var(--border-strong);
  background:linear-gradient(180deg,#202229,#181a20);
  color:#f6f7f9;
  font-weight:820;
  letter-spacing:-.005em;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.035);
  filter:none!important;
  transition:
    background-color .14s ease,
    border-color .14s ease,
    color .14s ease,
    opacity .14s ease,
    box-shadow .14s ease;
}

.btn.primary{
  background:linear-gradient(180deg,#ff3043,var(--red2));
  border-color:rgba(255,68,82,.42);
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.16),
    0 8px 22px rgba(198,16,34,.20);
}

.btn.ghost{
  background:rgba(255,255,255,.012);
  border-color:var(--border);
}

.btn.small{
  min-height:32px;
}

.btn:disabled,
button:disabled{
  opacity:.48;
  cursor:not-allowed;
}

.btn:focus-visible,
button:focus-visible,
.tab:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible{
  outline:none;
  box-shadow:var(--focus-ring);
}

/* ---------- Tabs / navigation ---------- */
.tabs{
  gap:7px;
  scrollbar-width:none;
}

.tabs::-webkit-scrollbar{
  display:none;
}

.tab{
  border-color:var(--border);
  background:#111217;
  color:var(--muted);
  border-radius:999px;
  font-weight:780;
  transition:
    background-color .14s ease,
    border-color .14s ease,
    color .14s ease,
    box-shadow .14s ease;
}

.tab.active{
  color:#fff;
  background:var(--red-soft);
  border-color:var(--red-border);
  box-shadow:inset 0 0 0 1px rgba(255,38,57,.04);
}

/* ---------- Forms ---------- */
.input,
input,
select,
textarea{
  border-color:#30333c;
  background:#0c0d10;
  color:#f5f6f8;
}

.input,
select,
textarea{
  border-radius:var(--radius-sm);
}

.input::placeholder,
input::placeholder,
textarea::placeholder{
  color:#696d78;
}

.input:focus,
input:focus,
select:focus,
textarea:focus{
  border-color:rgba(255,38,57,.62);
  outline:none;
  box-shadow:var(--focus-ring);
}

label{
  color:var(--muted-strong);
}

/* ---------- Workout ---------- */
.session-card{
  background:
    linear-gradient(180deg,rgba(255,38,57,.022),transparent 34%),
    var(--panel);
}

.set-grid{
  gap:9px;
}

.set-n{
  color:#d9dbe1;
  background:#0f1014;
  border:1px solid var(--border-soft);
  border-radius:9px;
}

.session-progress,
.progress-bar{
  background:#24262d;
}

.session-progress span,
.progress-bar span{
  background:linear-gradient(90deg,var(--red2),var(--red));
}

.recommend{
  border-left-width:3px;
  border-left-color:var(--red);
  background:rgba(255,38,57,.07);
  border-radius:0 var(--radius-sm) var(--radius-sm) 0;
}

.recommend.coach{
  border-left-color:var(--blue);
  background:rgba(103,173,255,.07);
}

/* ---------- Status / alerts ---------- */
.badge{
  border:1px solid transparent;
  font-weight:820;
}

.badge.green{
  border-color:rgba(59,213,138,.16);
}

.badge.amber{
  border-color:rgba(242,189,85,.16);
}

.badge.red{
  border-color:rgba(255,38,57,.18);
}

.badge.blue{
  border-color:rgba(103,173,255,.16);
}

.alert{
  border-radius:var(--radius-md);
}

.inline-note{
  border-color:var(--red-border);
  background:rgba(255,38,57,.055);
}

/* ---------- Modal ---------- */
.modal-wrap{
  background:rgba(0,0,0,.76);
  backdrop-filter:blur(6px);
  -webkit-backdrop-filter:blur(6px);
}

.modal{
  background:
    linear-gradient(180deg,rgba(255,255,255,.025),transparent 22%),
    #101116;
  border-color:#353842;
  border-radius:var(--radius-xl);
  box-shadow:var(--shadow-float);
}

.modal-head{
  padding-bottom:12px;
  border-bottom:1px solid var(--border-soft);
}

.modal-head h3{
  color:#fff;
  font-weight:900;
  letter-spacing:-.02em;
}

/* ---------- Toast ---------- */
.toast{
  background:#16181e;
  border-color:#383b45;
  border-radius:var(--radius-md);
  box-shadow:var(--shadow-float);
}

/* ---------- Mobile nav ---------- */
.bottom-nav{
  background:rgba(9,9,11,.94);
  border-top-color:rgba(255,255,255,.075);
  box-shadow:0 -12px 30px rgba(0,0,0,.22);
  backdrop-filter:blur(16px) saturate(120%);
  -webkit-backdrop-filter:blur(16px) saturate(120%);
}

/* ---------- Safe hover: never transform geometry ---------- */
@media (hover:hover) and (pointer:fine){
  .btn:hover{
    filter:none!important;
    border-color:#4a4e5a;
    background:linear-gradient(180deg,#262932,#1b1d24);
  }

  .btn.primary:hover{
    background:linear-gradient(180deg,#ff3b4d,#d41427);
    border-color:rgba(255,91,103,.54);
  }

  .tab:hover:not(.active){
    color:#d4d6dc;
    border-color:#3b3e48;
    background:#15161b;
  }

  .student-row:hover,
  .library-item:hover,
  .history-item:hover,
  .track-row:hover{
    border-color:#3a3e48;
    background-color:#15171c;
  }
}

/* ---------- Geometry safety ---------- */
.card,
.student-row,
.library-item,
.history-item,
.track-row,
.track-score,
.metric,
.modal,
.btn,
.tab,
.input,
input,
select,
textarea{
  transform:none;
}

.card,
.student-row,
.library-item,
.history-item,
.track-row,
.track-score,
.metric{
  transition:
    background-color .14s ease,
    border-color .14s ease,
    box-shadow .14s ease;
}

@media(max-width:900px){
  .topbar{
    background:rgba(8,8,10,.95);
  }

  .shell{
    padding-left:14px;
    padding-right:14px;
  }

  .card{
    border-radius:16px;
    padding:15px;
  }

  .hero{
    margin-bottom:17px;
  }

  .hero h2{
    font-size:25px;
  }

  .student-row{
    border-radius:13px;
  }

  .modal{
    border-radius:18px;
    padding:16px;
  }

  .bottom-nav{
    padding-bottom:max(0px,env(safe-area-inset-bottom));
  }
}

@media(max-width:520px){
  .grid.kpi{
    gap:10px;
  }

  .grid.kpi .card{
    padding:14px;
  }

  .grid.kpi .card strong{
    font-size:25px;
  }

  .btn{
    min-height:40px;
  }

  .btn.small{
    min-height:34px;
  }
}

@media(prefers-reduced-motion:reduce){
  .btn,
  .tab,
  .card,
  .student-row,
  .library-item,
  .history-item,
  .track-row,
  .track-score,
  .metric{
    transition:none!important;
    animation:none!important;
  }
}
"""

# Append to the one existing stylesheet, keeping styles == 1.
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.23 stylesheet surface changed: "+str(len(styles)))

m=styles[0]
new_body=m.group("body").rstrip()+"\n"+css+"\n"
html=html[:m.start("body")]+new_body+html[m.end("body"):]

marker='<meta name="fjz-ui-foundation" content="20.23">'
if re.search(r'<meta\s+name=["\']fjz-ui-foundation["\']',html,re.I):
    html=re.sub(
        r'<meta\s+name=["\']fjz-ui-foundation["\']\s+content=["\'][^"\']*["\']\s*/?>',
        marker,html,count=1,flags=re.I
    )
else:
    html=html.replace("</head>",marker+"\n</head>",1)

after=metrics(html)

# Visual-only patch must leave runtime topology unchanged.
for key in (
    "styles","render_assignments","channels","mutation_observers",
    "performance_observers","timeouts","rafs","listeners"
):
    if after[key]!=before[key]:
        raise RuntimeError("V20.23 runtime topology changed for "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-ui-foundation" content="20.23"',
    "TEAM FJZ · V20.23 PROFESSIONAL UI FOUNDATION",
    "--surface-raised:#1d1f26",
    "--focus-ring:0 0 0 3px rgba(255,38,57,.15)",
    ".bottom-nav",
    ".session-card",
    ".student-row",
    ".modal",
    "prefers-reduced-motion:reduce",
    "__fjzV222",
    "__fjzV207",
    "modalReorderUsesAtomicRpc:true",
    "singleRealtimeAuthority:true",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.23 missing visual/stability marker: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.23 professional UI foundation")
print("V20.23 BEFORE:",before)
print("V20.23 AFTER:",after)
print("V20.23 visual-only foundation applied; runtime topology unchanged")
