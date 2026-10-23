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
    'meta name="fjz-final-release-candidate" content="20.85"',
    'meta name="fjz-coach-athlete-workspace" content="20.66"',
    'meta name="fjz-session-feedback" content="20.41"',
    "v266-quick-actions",
    "v241-difficulty-grid",
    "#coachStudentTabs"
]:
    if marker not in html:
        raise RuntimeError("V20.86 prerequisite missing "+marker)

css=r"""
/* =========================================================
   TEAM FJZ · V20.86 TYPOGRAPHY / SINGLE MOBILE PROFILE NAV /
   POST-SESSION FEEDBACK SYMMETRY
   ========================================================= */

/* Desktop: preserve the compact premium hierarchy, but stop using 7–8px
   helper text on a full-size monitor. */
@media(min-width:1000px){
  .v225-eyebrow,
  .v225-section-kicker,
  .v266-profile-kicker,
  .v266-command-kicker,
  .v266-section-kicker,
  .v278-kicker,
  .v280-section-kicker,
  .v225-kpi-label{
    font-size:11px!important;
    line-height:1.25!important;
  }

  #v266CoachWorkspace .v266-context-metric>span{
    font-size:9.5px!important;
    line-height:1.25!important;
  }
  #v266CoachWorkspace .v266-context-metric>strong{
    font-size:15px!important;
  }
  #v266CoachWorkspace .v266-context-metric>small{
    font-size:9.5px!important;
    line-height:1.35!important;
  }
  #v266CoachWorkspace .v266-quick-actions .btn{
    min-height:34px!important;
    font-size:10.5px!important;
  }

  #coachStudentTabs .tab,
  .v266-coach-tabs .tab{
    min-height:38px!important;
    font-size:11px!important;
  }

  :where(.v225-coach-hero,.v225-dashboard-grid,#v175Coach360,#v266CoachWorkspace,
         #v252PriorityCenter,#v259CoachCalendar,.v278-dashboard-card,.v280-calendar-card)
  :where(.tiny,.muted.tiny){
    font-size:11px!important;
    line-height:1.45!important;
  }

  :where(.v225-coach-hero,.v225-dashboard-grid,#v175Coach360,#v266CoachWorkspace,
         #v252PriorityCenter,#v259CoachCalendar,.v278-dashboard-card,.v280-calendar-card)
  :where(.micro,.muted.micro){
    font-size:9.5px!important;
    line-height:1.4!important;
  }

  .v225-signal span,
  .v225-flow-step p{
    font-size:12px!important;
    line-height:1.45!important;
  }
}

/* Coach athlete profile on phone: one navigation only.
   The persistent context metrics stay, but their duplicate quick-action
   buttons disappear; the canonical tabs become the sole navigation. */
@media(max-width:760px){
  #v266CoachWorkspace .v266-quick-actions{
    display:none!important;
  }

  #v266CoachWorkspace{
    grid-template-columns:1fr!important;
    margin-bottom:9px!important;
  }

  #coachStudentTabs,
  .v266-coach-tabs{
    position:sticky!important;
    top:max(6px,env(safe-area-inset-top))!important;
    z-index:35!important;
    display:grid!important;
    grid-template-columns:repeat(4,minmax(0,1fr))!important;
    gap:6px!important;
    width:100%!important;
    max-width:100%!important;
    padding:6px!important;
    margin:0 0 12px!important;
    overflow:visible!important;
    white-space:normal!important;
    border-radius:14px!important;
    background:rgba(12,13,16,.96)!important;
    backdrop-filter:blur(14px);
    -webkit-backdrop-filter:blur(14px);
  }

  #coachStudentTabs .tab,
  .v266-coach-tabs .tab{
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
    min-width:0!important;
    width:100%!important;
    min-height:42px!important;
    padding:8px 5px!important;
    border-radius:10px!important;
    font-size:10px!important;
    line-height:1.15!important;
    text-align:center!important;
    white-space:normal!important;
    overflow-wrap:normal!important;
    word-break:normal!important;
  }
}

@media(max-width:420px){
  #coachStudentTabs,
  .v266-coach-tabs{
    grid-template-columns:repeat(3,minmax(0,1fr))!important;
  }
  #coachStudentTabs .tab,
  .v266-coach-tabs .tab{
    min-height:41px!important;
    font-size:10px!important;
  }
}

/* Post-session difficulty selector: keep checkbox anchored to the left and
   center the option label inside every card. This overrides later generic
   label/input rules that were pushing text to the far right on mobile. */
.v241-difficulty-grid{
  align-items:stretch!important;
}
.v241-difficulty-grid label{
  position:relative!important;
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
  min-width:0!important;
  min-height:46px!important;
  padding:9px 38px!important;
  text-align:center!important;
  overflow:hidden!important;
}
.v241-difficulty-grid label>input[type="checkbox"]{
  position:absolute!important;
  left:12px!important;
  top:50%!important;
  transform:translateY(-50%)!important;
  width:18px!important;
  min-width:18px!important;
  max-width:18px!important;
  height:18px!important;
  margin:0!important;
}
.v241-difficulty-grid label>span{
  display:block!important;
  width:100%!important;
  min-width:0!important;
  margin:0!important;
  color:#c8cbd2!important;
  font-size:10.5px!important;
  line-height:1.25!important;
  text-align:center!important;
  white-space:normal!important;
  overflow-wrap:normal!important;
  word-break:normal!important;
  hyphens:none!important;
}

@media(max-width:560px){
  .v241-difficulty-grid{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:8px!important;
  }
  .v241-difficulty-grid label{
    min-height:50px!important;
    padding:9px 31px!important;
  }
  .v241-difficulty-grid label>input[type="checkbox"]{
    left:10px!important;
  }
}

@media(max-width:360px){
  .v241-difficulty-grid{
    grid-template-columns:1fr!important;
  }
  .v241-difficulty-grid label{
    min-height:46px!important;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.86 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-typography-mobile-nav-feedback" content="20.86">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.86 topology changed "+key+": "+repr({"before":before,"after":after}))

required=[
    'meta name="fjz-typography-mobile-nav-feedback" content="20.86"',
    "@media(min-width:1000px)",
    "#v266CoachWorkspace .v266-quick-actions{",
    "display:none!important;",
    "grid-template-columns:repeat(4,minmax(0,1fr))!important;",
    "grid-template-columns:repeat(3,minmax(0,1fr))!important;",
    ".v241-difficulty-grid label>input[type=\"checkbox\"]",
    "position:absolute!important;",
    "text-align:center!important;",
    "word-break:normal!important;",
]
for marker in required:
    if marker not in html:
        raise RuntimeError("V20.86 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.86 typography + single mobile profile nav + feedback symmetry")
print("V20.86 BEFORE:",before)
print("V20.86 AFTER:",after)
