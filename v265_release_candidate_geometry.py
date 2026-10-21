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
        "scroll_into_view":len(re.findall(r"scrollIntoView\s*\(",doc)),
    }

before=metrics(html)

for marker in [
    'meta name="fjz-confirmed-save-feedback" content="20.64"',
    'meta name="fjz-mobile-stability" content="20.55"',
    'meta name="fjz-premium-polish" content="20.62"',
    "routeScrollAuthority:true",
    "widthOnlyTrackingResize:true"
]:
    if marker not in html:
        raise RuntimeError("V20.65 missing prerequisite: "+marker)

css=r"""
/* =========================================================
   TEAM FJZ · V20.65 RELEASE CANDIDATE GEOMETRY / STABILITY
   ========================================================= */

/* One geometry model for every important surface. */
*,
*::before,
*::after{
  box-sizing:border-box;
}

.shell,
#view,
#coachStudentBody,
#studentSubBody,
.card,
.hero,
.modal,
.student-row,
.day-card,
.exercise-row,
.workout-card,
.session-card,
.track-row,
.history-item,
.v252-column,
.v253-flow-item,
.v254-exercise-card,
.v259-calendar-card,
.v259-month,
.v259-upcoming,
.v260-four-week,
.v258-current-plan,
.v249-progress-pulse,
.v250-weekly-brief{
  min-width:0!important;
  max-width:100%;
}

/* Titles/copy never push a box wider than its container. */
.section-title,
.modal-head,
.v259-calendar-head,
.v252-priority-head,
.v253-flow-head,
.v260-head,
.v258-plan-head,
.v250-action,
.v260-current{
  min-width:0;
}
.section-title>div,
.modal-head>div,
.v259-calendar-head>div,
.v252-priority-head>div,
.v253-flow-head>div,
.v260-head>div,
.v258-plan-head>div,
.v250-action>div,
.v260-current>div{
  min-width:0;
}
.card h2,.card h3,.card h4,
.hero h2,.hero h3,
.section-title h2,.section-title h3,
.modal-head h2,.modal-head h3,
.card p,.hero p,.muted,.tiny,.micro{
  overflow-wrap:anywhere;
}

/* Uniform control geometry. */
.input,
input:not([type="checkbox"]):not([type="radio"]),
select,
textarea{
  width:100%;
  min-width:0;
  max-width:100%;
  box-sizing:border-box;
}
input:not([type="checkbox"]):not([type="radio"]),
select,
.input:not(textarea){
  min-height:42px;
}
textarea.input,
textarea{
  min-height:78px;
  resize:vertical;
}
.form-grid>label,
.v186-field-pair>label{
  min-width:0;
  align-self:start;
}
.form-grid>label>.input,
.form-grid>label>input,
.form-grid>label>select,
.form-grid>label>textarea{
  margin-top:5px;
}

/* Metrics use stable-width numerals so values changing do not nudge boxes. */
.v259-calendar-stats strong,
.v260-grid strong,
.v249-pulse-metric strong,
.v250-grid strong,
.metric-grid strong,
.kpi strong{
  font-variant-numeric:tabular-nums;
}

/* Grid children stretch consistently and do not acquire accidental widths. */
.v259-calendar-stats,
.v260-grid,
.v249-pulse-grid,
.v250-grid,
.v252-columns,
.v253-flow-grid,
.v254-exercise-grid{
  align-items:stretch;
}
.v259-calendar-stats>div,
.v260-grid>div,
.v249-pulse-metric,
.v250-grid>div,
.v252-column,
.v253-flow-item,
.v254-exercise-card{
  height:100%;
}

/* Calendar cells and event rows must remain inside their grid tracks. */
.v259-days,
.v259-weekdays{
  min-width:0;
}
.v259-day,
.v259-day-events,
.v259-event,
.v259-upcoming-row,
.v259-up-copy{
  min-width:0;
  max-width:100%;
  overflow:hidden;
}
.v259-upcoming-row{
  padding-left:9px!important;
  transition:background-color .14s ease,border-color .14s ease!important;
}
.v259-upcoming-row:hover{
  padding-left:9px!important;
}
.v259-event{
  transform:none!important;
  transition:filter .14s ease,background-color .14s ease!important;
}
.v259-event:hover{
  transform:none!important;
}

/* Buttons may change color but never physically jump a layout on tap. */
.btn{
  transform:none;
}
.btn:active:not(:disabled){
  transform:none!important;
}

/* New save confirmations are dimensionally stable. */
.v207-save-state,
.v264-confirmed-save{
  width:min(100%,520px);
  margin-inline:auto;
}
.v207-save-actions{
  width:100%;
}
.v207-save-actions>.btn{
  min-height:40px;
}

/* Mobile: remove old compositing layers that can create visual shimmer. */
@media(max-width:900px){
  .session-card,
  .photo-month,
  .v205-chart,
  .track-row,
  .card,
  .hero,
  .student-row,
  .exercise-row,
  .day-card,
  .history-item{
    transform:none!important;
    backface-visibility:visible!important;
    will-change:auto!important;
  }

  /* Structural surfaces do not animate size/position during async refreshes. */
  .card,
  .hero,
  .student-row,
  .day-card,
  .exercise-row,
  .workout-card,
  .session-card,
  .track-row,
  .history-item,
  .v252-column,
  .v253-flow-item,
  .v254-exercise-card,
  .v259-calendar-card,
  .v259-month,
  .v259-upcoming,
  .v260-four-week,
  .v258-current-plan{
    transition-property:background-color,border-color,color,opacity!important;
  }
}

@media(max-width:680px){
  .section-title,
  .v259-calendar-head,
  .v252-priority-head,
  .v253-flow-head,
  .v260-head,
  .v258-plan-head{
    align-items:flex-start;
  }

  .form-grid{
    align-items:start;
  }

  .v259-calendar-stats>div,
  .v260-grid>div{
    padding:9px;
  }

  .v259-calendar-stats strong,
  .v260-grid strong{
    line-height:1.15;
  }
}

@media(max-width:420px){
  .card,
  .hero,
  .student-row,
  .day-card,
  .exercise-row,
  .workout-card,
  .session-card{
    border-radius:13px!important;
  }

  .v259-calendar-stats,
  .v260-grid{
    grid-template-columns:1fr 1fr!important;
  }

  .v259-calendar-stats span,
  .v260-grid span{
    font-size:7px;
  }
}

@media(prefers-reduced-motion:reduce){
  .v264-quick-save.show{
    animation:none!important;
    opacity:1;
    transform:translate(-50%,0)!important;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.65 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-release-candidate-geometry" content="20.65">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners","mutation_observers","performance_observers","scroll_into_view"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.65 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-release-candidate-geometry" content="20.65"',
    "TEAM FJZ · V20.65 RELEASE CANDIDATE GEOMETRY / STABILITY",
    ".v259-upcoming-row:hover",
    "padding-left:9px!important",
    "backface-visibility:visible!important",
    "transition-property:background-color,border-color,color,opacity!important",
    "font-variant-numeric:tabular-nums"
]:
    if marker not in html:
        raise RuntimeError("V20.65 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.65 release-candidate geometry/stability")
print("V20.65 BEFORE:",before)
print("V20.65 AFTER:",after)
print("V20.65 geometry transitions removed; controls/cards normalized; no runtime topology growth")
