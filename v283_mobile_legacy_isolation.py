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

def edit_script(doc,script_id,transform):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.83 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.83 no changes in "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-calendar-route-hardening" content="20.82"',
    'meta name="fjz-coach-integrity-recovery" content="20.81"',
    'id="v275MobileHudProgressRuntime"',
    'id="v276CoachHudNutritionRuntime"',
    'id="v282CalendarRouteHardeningRuntime"',
]:
    if marker not in html:
        raise RuntimeError("V20.83 prerequisite missing "+marker)

# ---------------------------------------------------------------
# 1) Student route recovery: old local state must not resurrect
# removed Music or invalid workout/day routes.
# ---------------------------------------------------------------
def patch_v275(body):
    old="""  window.renderStudent=function(){
    if(studentTab==='training')return window.renderTrainingHubV275();
    return baseRenderStudentV275.apply(this,arguments);
  };"""
    new="""  window.renderStudent=function(){
    const allowed=new Set(['home','agenda','tracking','nutrition','progress','history','workout','training']);
    if(!allowed.has(studentTab))studentTab='home';
    if(studentTab==='workout'){
      const s=typeof student==='function'?student():null;
      const valid=!!(s&&Array.isArray(s.days)&&Number.isInteger(Number(currentDay))&&s.days[Number(currentDay)]);
      if(!valid)studentTab='training';
    }
    if(studentTab==='training')return window.renderTrainingHubV275();
    return baseRenderStudentV275.apply(this,arguments);
  };"""
    if old not in body:
        raise RuntimeError("V20.83 student route anchor missing")
    return body.replace(old,new,1)

html=edit_script(html,"v275MobileHudProgressRuntime",patch_v275)

# ---------------------------------------------------------------
# 2) Coach route recovery: retired tabs and deleted/stale selected
# students fall back safely before any old renderer can execute.
# ---------------------------------------------------------------
def patch_v282(body):
    old="""  window.renderCoach=function(){
    if(coachTab==='agenda')return renderCoachAgendaV282();
    return typeof baseRenderCoachV282==='function'?baseRenderCoachV282.apply(this,arguments):undefined;
  };"""
    new="""  window.renderCoach=function(){
    const allowedCoach=new Set(['dashboard','agenda','student']);
    if(!allowedCoach.has(coachTab))coachTab='dashboard';

    if(coachTab==='student'){
      const allowedStudentTabs=new Set(['summary','routine','progress','history','tracking','nutrition','agenda']);
      if(!allowedStudentTabs.has(coachStudentTab))coachStudentTab='summary';
      let selected=null;
      try{selected=typeof student==='function'?student():null}catch(_e){}
      if(!selected){
        coachTab='dashboard';
        coachStudentTab='summary';
      }
    }

    if(coachTab==='agenda')return renderCoachAgendaV282();
    return typeof baseRenderCoachV282==='function'?baseRenderCoachV282.apply(this,arguments):undefined;
  };"""
    if old not in body:
        raise RuntimeError("V20.83 coach route anchor missing")
    return body.replace(old,new,1)

html=edit_script(html,"v282CalendarRouteHardeningRuntime",patch_v282)

# ---------------------------------------------------------------
# 3) Final HUD authority: clean classes on every mode switch so an
# old Coach/Student HUD cannot remain visually attached after render.
# ---------------------------------------------------------------
def patch_v276(body):
    old="""  window.renderBottomNav=function(){
    const nav=el('bottomNav');
    if(mode==='coach'&&nav){
      coachHudV276(nav);
      return;
    }
    nav?.classList.remove('v276-coach-hud');
    return baseBottomNavV276.apply(this,arguments);
  };"""
    new="""  window.renderBottomNav=function(){
    const nav=el('bottomNav');
    if(!nav)return;
    if(mode==='coach'){
      nav.classList.remove('v275-student-hud');
      coachHudV276(nav);
      return;
    }
    nav.classList.remove('v276-coach-hud');
    if(mode!=='student')nav.classList.remove('v275-student-hud');
    return baseBottomNavV276.apply(this,arguments);
  };"""
    if old not in body:
        raise RuntimeError("V20.83 bottom nav anchor missing")
    return body.replace(old,new,1)

html=edit_script(html,"v276CoachHudNutritionRuntime",patch_v276)

# Remove old Music entry from legacy tab arrays if it survived historical
# wrappers. This is intentionally narrow and only targets the retired tab.
html=html.replace("['music','Música'],","")
html=html.replace(",['music','Música']","")

css=r"""
/* =========================================================
   TEAM FJZ · V20.83 MOBILE LEGACY ISOLATION / GEOMETRY
   ========================================================= */
html,body,#app,#view,#coachStudentBody,#studentSubBody{
  max-width:100%;
  min-width:0;
}
body,#view,#coachStudentBody,#studentSubBody{
  overflow-x:clip;
}

@media(max-width:900px){
  :where(#view,#coachStudentBody,#studentSubBody,
    .card,.hero,.grid,.form-grid,.metric-grid,.tabs,
    .meal-block,.meal-option-student,.option-card,.exercise-row,.day-card,
    .v225-dashboard-grid,.v252-priority-card,.v280-calendar-card,
    .v278-dashboard-card,.v278-progress,.v282-week-grid,.v282-week-day){
    min-width:0!important;
    max-width:100%!important;
    box-sizing:border-box!important;
  }

  :where(input,select,textarea,.input,
    input[type="date"],input[type="time"],input[type="number"],input[type="text"],input[type="email"]){
    width:100%;
    min-width:0!important;
    max-width:100%!important;
    box-sizing:border-box!important;
  }

  :where(input,select,textarea,.input):focus{
    scroll-margin-top:max(82px,calc(env(safe-area-inset-top) + 62px));
    scroll-margin-bottom:calc(136px + env(safe-area-inset-bottom));
  }

  .tabs{
    width:100%;
    max-width:100%;
    overflow-x:auto!important;
    overflow-y:hidden!important;
    overscroll-behavior-x:contain;
    -webkit-overflow-scrolling:touch;
    scrollbar-width:none;
  }
  .tabs::-webkit-scrollbar{display:none}
  .tabs>.tab{flex:0 0 auto;min-width:max-content}

  #coachStudentTabs{
    top:max(6px,env(safe-area-inset-top))!important;
    max-width:100%!important;
    overflow-x:auto!important;
    overflow-y:hidden!important;
  }

  .modal-wrap{
    width:100dvw!important;
    max-width:100dvw!important;
    overflow-x:hidden!important;
    box-sizing:border-box!important;
  }
  .modal{
    width:min(100%,680px)!important;
    max-width:calc(100dvw - max(12px,env(safe-area-inset-left)) - max(12px,env(safe-area-inset-right)))!important;
    max-height:calc(100dvh - max(12px,env(safe-area-inset-top)) - max(12px,env(safe-area-inset-bottom)))!important;
    overflow-x:hidden!important;
    box-sizing:border-box!important;
  }

  :where(img,video,canvas,svg){
    max-width:100%;
  }

  :where(.section-title,.modal-head,.day-head,.meal-head,.v280-calendar-head,.v280-priority-head){
    min-width:0!important;
    max-width:100%!important;
  }
  :where(.section-title,.modal-head,.day-head,.meal-head,.v280-calendar-head,.v280-priority-head)>*{
    min-width:0!important;
  }

  :where(.btn,button){
    max-width:100%;
  }

  /* Legacy routes are retired on mobile even if an old renderer briefly
     reconstructs their buttons before the final HUD authority runs. */
  button[onclick*="Tab='music'"],
  button[onclick*='Tab="music"'],
  button[onclick*="coachTab='payments'"],
  button[onclick*='coachTab="payments"']{
    display:none!important;
  }

  .bottom-nav.v275-student-hud,
  .bottom-nav.v276-coach-hud{
    max-width:calc(100dvw - max(12px,env(safe-area-inset-left)) - max(12px,env(safe-area-inset-right)))!important;
  }
}

@media(max-width:430px){
  :where(.grid,.form-grid,.metric-grid){
    min-width:0!important;
  }
  :where(.section-title,.modal-head,.day-head,.meal-head){
    gap:7px!important;
  }
}

@media(max-width:360px){
  .modal{
    max-width:calc(100dvw - 8px)!important;
  }
  .bottom-nav.v275-student-hud,
  .bottom-nav.v276-coach-hud{
    width:calc(100dvw - 8px)!important;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.83 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-mobile-legacy-isolation" content="20.83">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.83 topology changed "+key+": "+repr({"before":before,"after":after}))

required=[
    'meta name="fjz-mobile-legacy-isolation" content="20.83"',
    "const allowed=new Set(['home','agenda','tracking','nutrition','progress','history','workout','training'])",
    "if(!allowed.has(studentTab))studentTab='home'",
    "if(!valid)studentTab='training'",
    "const allowedCoach=new Set(['dashboard','agenda','student'])",
    "if(!allowedCoach.has(coachTab))coachTab='dashboard'",
    "const allowedStudentTabs=new Set(['summary','routine','progress','history','tracking','nutrition','agenda'])",
    "if(!selected){",
    "nav.classList.remove('v275-student-hud')",
    "body,#view,#coachStudentBody,#studentSubBody",
    "button[onclick*=\"Tab='music'\"]",
    "input[type=\"date\"]",
    "input[type=\"time\"]",
    "scroll-margin-bottom:calc(136px + env(safe-area-inset-bottom))",
]
for marker in required:
    if marker not in html:
        raise RuntimeError("V20.83 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.83 mobile legacy isolation")
print("V20.83 BEFORE:",before)
print("V20.83 AFTER:",after)
print("V20.83 stale routes/workout state + HUD classes + mobile geometry hardened")
