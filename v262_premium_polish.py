import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

before=metrics(html)

for marker in [
    'meta name="fjz-coach-action-calendar" content="20.59"',
    'meta name="fjz-coach-four-week-snapshot" content="20.60"',
    'meta name="fjz-student-current-plan" content="20.58"',
    "renderCoachCalendarV259",
    "renderCoachFourWeekV260"
]:
    if marker not in html:
        raise RuntimeError("V20.62 missing prerequisite: "+marker)

css=r"""
/* =========================================================
   TEAM FJZ · V20.62 PREMIUM POLISH
   Visual-only refinement. No runtime topology changes.
   ========================================================= */

:root{
  --v262-edge:#30343d;
  --v262-edge-soft:#282c34;
  --v262-panel:#101116;
  --v262-panel-deep:#0c0e12;
  --v262-red:#ff3348;
  --v262-red-soft:rgba(255,51,72,.08);
  --v262-blue-soft:rgba(103,173,255,.07);
}

.card{
  border-color:var(--v262-edge-soft);
  box-shadow:0 10px 28px rgba(0,0,0,.14);
}

.btn,
.input,
button,
select,
textarea,
input{
  -webkit-tap-highlight-color:transparent;
}

.btn{
  transition:border-color .16s ease,background .16s ease,transform .16s ease,box-shadow .16s ease;
}
.btn:hover:not(:disabled){
  border-color:#444a55;
}
.btn.primary:hover:not(:disabled){
  box-shadow:0 6px 18px rgba(255,38,57,.14);
}
.btn:active:not(:disabled){
  transform:translateY(1px);
}

button:focus-visible,
.btn:focus-visible,
.input:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible,
[tabindex]:focus-visible{
  outline:2px solid rgba(255,65,82,.78);
  outline-offset:2px;
}

.input,
input,
select,
textarea{
  transition:border-color .16s ease,background .16s ease,box-shadow .16s ease;
}
.input:focus,
input:focus,
select:focus,
textarea:focus{
  border-color:#555b66;
  box-shadow:0 0 0 3px rgba(255,51,72,.055);
}

.v225-section-kicker{
  letter-spacing:.13em;
}

.v252-priority-card,
.v259-calendar-card,
.v260-four-week,
.v258-current-plan,
.v253-week-flow,
.v249-progress-pulse,
.v254-exercise-progress{
  position:relative;
  overflow:hidden;
}
.v252-priority-card::before,
.v259-calendar-card::before,
.v260-four-week::before,
.v258-current-plan::before,
.v253-week-flow::before{
  content:"";
  position:absolute;
  inset:0 auto 0 0;
  width:2px;
  pointer-events:none;
  background:linear-gradient(180deg,rgba(255,51,72,.82),rgba(255,51,72,0));
  opacity:.5;
}

.v252-column,
.v259-month,
.v259-upcoming,
.v260-grid>div,
.v258-next,
.v258-focus,
.v253-flow-item,
.v249-pulse-metric,
.v254-exercise-card{
  box-shadow:inset 0 1px 0 rgba(255,255,255,.012);
}

.v259-calendar-head,
.v252-priority-head,
.v253-flow-head,
.v260-head,
.v258-plan-head{
  position:relative;
  z-index:1;
}

.v259-calendar-nav .btn:nth-child(2){
  min-width:132px;
  font-weight:850;
}

.v259-day{
  transition:background .14s ease,box-shadow .14s ease;
}
.v259-day:hover:not(.muted-day){
  background:#11141a;
}
.v259-day.today{
  box-shadow:inset 0 0 0 1px rgba(103,173,255,.52),inset 0 0 22px rgba(103,173,255,.025);
}
.v259-event{
  transition:filter .14s ease,transform .14s ease;
}
.v259-event:hover{
  filter:brightness(1.13);
  transform:translateX(1px);
}
.v259-upcoming-row{
  transition:background .14s ease,padding-left .14s ease;
}
.v259-upcoming-row:hover{
  padding-left:11px;
}

.v259-calendar-stats>div,
.v260-grid>div{
  position:relative;
  overflow:hidden;
}
.v259-calendar-stats>div::after,
.v260-grid>div::after{
  content:"";
  position:absolute;
  left:0;right:0;bottom:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.08),transparent);
}

.v259-action-status{
  letter-spacing:.025em;
}

.v259-priority-row{
  transition:background .14s ease;
}
.v259-priority-row:hover{
  background:#111318;
}

.v260-current,
.v250-action,
.v258-focus{
  box-shadow:0 8px 22px rgba(0,0,0,.10);
}

.v258-current-plan .badge,
.v259-calendar-card .badge,
.v260-four-week .badge{
  box-shadow:inset 0 1px 0 rgba(255,255,255,.035);
}

.v258-next p,
.v260-current p,
.v250-action p,
.v252-copy small,
.v259-up-copy small{
  text-wrap:pretty;
}

.empty{
  min-height:44px;
  display:grid;
  place-items:center;
  padding:14px;
  border-radius:10px;
}

.v207-save-icon.success{
  box-shadow:0 0 0 6px rgba(59,213,138,.055);
}

@media(max-width:680px){
  .card{
    box-shadow:0 7px 20px rgba(0,0,0,.11);
  }
  .v259-calendar-card,
  .v252-priority-card,
  .v260-four-week,
  .v258-current-plan{
    border-radius:13px;
  }
  .v259-calendar-head,
  .v252-priority-head{
    gap:9px;
  }
  .v259-calendar-stats{
    gap:5px;
  }
  .v259-calendar-stats>div{
    min-width:0;
  }
  .v259-calendar-stats span{
    white-space:normal;
    line-height:1.25;
  }
}

@media(max-width:480px){
  .v259-calendar-nav .btn:nth-child(2){
    min-width:0;
  }
  .v259-day-num{
    font-size:7px;
  }
  .v259-legend{
    gap:7px;
  }
}

@media(prefers-reduced-motion:reduce){
  *,
  *::before,
  *::after{
    scroll-behavior:auto!important;
    animation-duration:.001ms!important;
    animation-iteration-count:1!important;
    transition-duration:.001ms!important;
  }
  .btn:active:not(:disabled),
  .v259-event:hover,
  .v259-upcoming-row:hover{
    transform:none;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.62 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-premium-polish" content="20.62">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.62 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-premium-polish" content="20.62"',
    "TEAM FJZ · V20.62 PREMIUM POLISH",
    "prefers-reduced-motion",
    "button:focus-visible",
    ".v259-calendar-card",
    ".v260-four-week",
    ".v258-current-plan"
]:
    if marker not in html:
        raise RuntimeError("V20.62 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.62 premium polish")
print("V20.62 BEFORE:",before)
print("V20.62 AFTER:",after)
print("V20.62 visual hierarchy/accessibility/mobile polish applied with zero runtime topology growth")
