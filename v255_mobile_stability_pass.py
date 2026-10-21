import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.55 MOBILE STABILITY PASS
# =========================================================
# Geometry/CSS hardening only. No JS/runtime topology changes.

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
        "scroll_smooth":len(re.findall(r"scroll-behavior\s*:\s*smooth",doc,re.I)),
    }

before=metrics(html)
if before["styles"]!=1:
    raise RuntimeError("V20.55 expected one stylesheet: "+repr(before))

for marker in [
    'meta name="fjz-exercise-performance-progress" content="20.54"',
    "v252-priority-card","v253-week-flow","v254-exercise-progress",
    "v241-feedback-form","v247-review-form","v239-decision-form"
]:
    if marker not in html:
        raise RuntimeError("V20.55 missing current UI marker: "+marker)

css=r"""
/* =========================================================
   TEAM FJZ · V20.55 MOBILE STABILITY PASS
   ========================================================= */

/* Universal geometry safety */
html,body{
  max-width:100%;
  overflow-x:hidden;
}
.shell,
#view,
.card,
.hero,
.modal,
.modal-wrap,
.day-card,
.exercise-row,
.student-row,
.track-row,
.history-item,
.library-item{
  min-width:0;
}
img,video,canvas,svg{
  max-width:100%;
}
.input,
input,
select,
textarea,
button{
  min-width:0;
  max-width:100%;
}
input[type="date"],
input[type="time"],
input[type="number"]{
  width:100%;
  box-sizing:border-box;
}
textarea{
  overflow-wrap:anywhere;
}
.grid,
.form-grid,
.pill-row,
.row{
  min-width:0;
}

/* Avoid content forcing columns wider than the viewport */
.v252-columns,
.v253-flow-grid,
.v254-exercise-grid,
.v249-pulse-grid,
.v250-grid,
.v247-source-kpis,
.v245-week,
.v239-decision-preview,
.v237-review-grid,
.v235-focus-actions{
  min-width:0;
}
.v252-column,
.v253-flow-item,
.v254-exercise-card,
.v249-pulse-metric,
.v250-grid>div,
.v247-source-kpis>span,
.v245-week>div,
.v239-decision-preview>*,
.v237-review-col{
  min-width:0;
  overflow-wrap:anywhere;
}

/* Modal viewport safety: no content hidden behind browser chrome / keyboard */
.modal-wrap{
  padding:
    max(12px,env(safe-area-inset-top))
    max(12px,env(safe-area-inset-right))
    max(12px,env(safe-area-inset-bottom))
    max(12px,env(safe-area-inset-left));
  overflow:auto;
  overscroll-behavior:contain;
}
.modal{
  width:min(720px,100%);
  max-height:min(88dvh,880px);
  overflow:auto;
  overscroll-behavior:contain;
}
.modal-head{
  min-width:0;
  gap:10px;
}
.modal-head>div{
  min-width:0;
}
.modal-head h3,
.modal-head .muted{
  overflow-wrap:anywhere;
}

/* Horizontal action rows can wrap instead of pushing the app */
.v225-hero-actions,
.v225-filter-row,
.v235-student-filters,
.v241-feedback-actions,
.v242-student-reply-actions,
.v243-next-actions,
.v245-action-buttons,
.v253-flow-actions,
.v239-review-actions,
.v207-save-actions{
  max-width:100%;
  flex-wrap:wrap;
}
.btn{
  white-space:normal;
  overflow-wrap:anywhere;
  text-align:center;
}

/* Workout fields must remain tappable and aligned */
.exercise-row .input,
.day-card .input,
.workout-card .input,
.set-row .input,
.series-row .input{
  width:100%;
  box-sizing:border-box;
}
.exercise-row,
.workout-card,
.set-row,
.series-row{
  min-width:0;
}

/* Tables/charts that genuinely need width stay inside their own scroller */
.table-wrap,
.chart-wrap,
[class*="table-scroll"]{
  max-width:100%;
  overflow-x:auto;
  overscroll-behavior-x:contain;
}

/* iOS/browser text scaling should not reshape inputs unexpectedly */
input,
select,
textarea{
  -webkit-text-size-adjust:100%;
  text-size-adjust:100%;
}

@media(max-width:760px){
  .shell{
    width:100%;
    padding-left:max(12px,env(safe-area-inset-left));
    padding-right:max(12px,env(safe-area-inset-right));
  }

  .card,
  .hero{
    max-width:100%;
  }

  .v252-columns,
  .v225-dashboard-grid,
  .v237-review-grid{
    grid-template-columns:1fr!important;
  }

  .v249-pulse-grid,
  .v250-grid,
  .v247-source-kpis,
  .v245-week,
  .v239-decision-preview{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
  }

  .v254-exercise-grid{
    grid-template-columns:1fr!important;
  }

  .v252-priority-head,
  .v237-review-head,
  .v242-session-head,
  .v245-action-top,
  .v250-action{
    min-width:0;
  }

  .v252-person{
    grid-template-columns:32px minmax(0,1fr) 18px;
  }

  .v254-exercise-main{
    align-items:flex-start;
  }

  .v254-exercise-main>span{
    max-width:48%;
  }

  .v247-checkin-review,
  .v242-student-reply,
  .v239-last-decision{
    min-width:0;
  }

  .bottom-nav{
    padding-bottom:max(7px,env(safe-area-inset-bottom));
  }
}

@media(max-width:520px){
  .modal-wrap{
    align-items:flex-start;
    padding-top:max(8px,env(safe-area-inset-top));
  }

  .modal{
    width:100%;
    max-width:100%;
    max-height:calc(100dvh - 16px - env(safe-area-inset-top) - env(safe-area-inset-bottom));
    border-radius:14px;
  }

  .modal-head{
    position:sticky;
    top:0;
    z-index:2;
    margin:-1px -1px 10px;
    padding:10px 1px 9px;
    background:linear-gradient(180deg,#111217 78%,rgba(17,18,23,0));
  }

  .v252-columns,
  .v253-flow-grid,
  .v249-pulse-grid,
  .v250-grid,
  .v247-source-kpis,
  .v245-week,
  .v239-decision-preview,
  .v241-difficulty-grid{
    grid-template-columns:1fr!important;
  }

  .v235-student-filters{
    grid-template-columns:1fr 1fr!important;
  }

  .v236-sort{
    grid-column:1/-1;
  }

  .v252-priority-head>.btn,
  .v236-focus-head>.btn,
  .v237-review-footer .btn,
  .v247-checkin-review .btn{
    width:100%;
  }

  .v254-exercise-main{
    display:grid;
    gap:5px;
  }

  .v254-exercise-main>span{
    max-width:none;
    text-align:left;
  }

  .v254-detail-row{
    grid-template-columns:1fr 1fr;
  }

  .v253-flow-actions,
  .v245-action-buttons,
  .v242-student-reply-actions{
    grid-template-columns:1fr 1fr!important;
  }

  .v253-flow-actions .btn:last-child{
    grid-column:1/-1;
  }

  /* Prevent native date/time controls from escaping cards on narrow screens */
  input[type="date"],
  input[type="time"]{
    min-height:42px;
    padding-left:9px;
    padding-right:7px;
  }
}

@media(max-width:380px){
  .v235-student-filters,
  .v253-flow-actions,
  .v245-action-buttons,
  .v242-student-reply-actions,
  .v235-focus-actions{
    grid-template-columns:1fr!important;
  }

  .v253-flow-actions .btn:last-child{
    grid-column:auto;
  }

  .v254-detail-row{
    grid-template-columns:1fr;
  }
  .v254-detail-row>div:last-child{
    text-align:left;
  }
}

/* Avoid geometry motion when the user/browser requests reduced motion. */
@media(prefers-reduced-motion:reduce){
  html{
    scroll-behavior:auto!important;
  }
  *,
  *::before,
  *::after{
    scroll-behavior:auto!important;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.55 stylesheet surface mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-mobile-stability" content="20.55">\n</head>',1)

after=metrics(html)
for key in (
    "styles","renders","channels","timeouts","rafs","listeners",
    "mutation_observers","performance_observers"
):
    if after[key]!=before[key]:
        raise RuntimeError("V20.55 runtime topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-mobile-stability" content="20.55"',
    "TEAM FJZ · V20.55 MOBILE STABILITY PASS",
    "overflow-x:hidden","overscroll-behavior:contain",
    "max-height:calc(100dvh","input[type=\"date\"]",
    ".v252-columns",".v254-exercise-grid"
]:
    if marker not in html:
        raise RuntimeError("V20.55 missing mobile marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.55 mobile stability pass")
print("V20.55 BEFORE:",before)
print("V20.55 AFTER:",after)
print("V20.55 geometry/input/modal hardening applied; runtime topology unchanged")
