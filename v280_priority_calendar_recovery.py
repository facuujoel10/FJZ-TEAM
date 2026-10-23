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
    'meta name="fjz-final-stability-polish" content="20.79"',
    'meta name="fjz-coach-priority-center" content="20.52"',
    'meta name="fjz-coach-action-calendar" content="20.59"',
    "renderCoachPriorityCenterV252",
    "renderCoachCalendarV259",
    "hydrateCoachCalendarV259",
    "coachPriorityRowsV252",
    "reviewEventV259",
]:
    if marker not in html:
        raise RuntimeError("V20.80 prerequisite missing "+marker)

# 1) A malformed student must never break the entire priority center.
start=html.find("function coachPriorityRowsV252(bucket){")
end=html.find("\nfunction priorityPersonV252",start)
if start<0 or end<0:
    raise RuntimeError("V20.80 priority rows bounds missing")
priority_rows=r"""function coachPriorityRowsV252(bucket){
  return (state.students||[])
    .map(s=>{
      try{return {s,...coachPriorityStateV252(s)}}
      catch(e){
        console.warn('TEAM FJZ V20.80 priority row fallback',s?.id,e);
        return {s,bucket:'watch',score:0,label:'Seguimiento disponible'};
      }
    })
    .filter(x=>x.bucket===bucket)
    .sort((a,b)=>b.score-a.score||String(a.s?.name||'').localeCompare(String(b.s?.name||'')));
}
"""
html=html[:start]+priority_rows+html[end:]

# 2) Calendar review events use a safe cadence fallback.
start=html.find("function reviewEventV259(s){")
end=html.find("\nfunction reminderEventsForMonthV259",start)
if start<0 or end<0:
    raise RuntimeError("V20.80 review event bounds missing")
review_fn=r"""function reviewEventV259(s){
  let days=14;
  try{
    const raw=Number(coachReviewCadenceDaysV240(s));
    if(Number.isFinite(raw)&&raw>0)days=raw;
  }catch(e){
    console.warn('TEAM FJZ V20.80 review cadence fallback',s?.id,e);
  }
  const reviewed=s?.coachReviewV237?.reviewedAt||null;
  const today=startOfDayV259(new Date());
  let due=today;
  if(reviewed){
    const base=new Date(reviewed);
    if(!Number.isNaN(base.getTime()))due=startOfDayV259(addDaysV259(base,days));
  }
  return {
    date:dateKeyV259(due),
    rawDate:due,
    student:s,
    kind:'review',
    title:reviewed?'Chequeo / revisión':'Primer chequeo',
    time:'',
    overdue:due<today,
    tab:'summary'
  };
}
"""
html=html[:start]+review_fn+html[end:]

# 3) Staging/local calendar data fallback must never throw.
old_local="""  if(!cloudEnabled||!supabaseClient||window.__fjzStagingLocal?.enabled){
    coachCalendarRemindersV259=Array.isArray(agendaRemindersV81)?agendaRemindersV81.slice():[];
    coachCalendarCheckinsV259=[];
    renderCoachCalendarV259();
    return {reminders:coachCalendarRemindersV259,checkins:coachCalendarCheckinsV259};
  }"""
new_local="""  if(!cloudEnabled||!supabaseClient||window.__fjzStagingLocal?.enabled){
    const localReminders=(typeof agendaRemindersV81!=='undefined'&&Array.isArray(agendaRemindersV81))
      ?agendaRemindersV81.slice():[];
    coachCalendarRemindersV259=localReminders;
    coachCalendarCheckinsV259=[];
    coachCalendarLoadedAtV259=Date.now();
    try{renderCoachCalendarV259()}catch(e){console.warn('TEAM FJZ V20.80 local calendar render',e)}
    return {reminders:coachCalendarRemindersV259,checkins:coachCalendarCheckinsV259};
  }"""
if old_local not in html:
    raise RuntimeError("V20.80 staging calendar fallback anchor missing")
html=html.replace(old_local,new_local,1)

# 4) Remove calendar hydration from inside the priority renderer. They become
# independent authorities so one can never block the other.
nested="""  renderCoachCalendarV259();
  hydrateCoachCalendarV259();
}"""
if nested not in html:
    raise RuntimeError("V20.80 nested calendar anchor missing")
html=html.replace(nested,"}",1)

# 5) Reuse the canonical V17.5 post-render hook to hydrate both surfaces.
pat=re.compile(r'(<script[^>]*\bid=["\']v175ProfileAgendaCoachCenterRuntime["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
m=pat.search(html)
if not m:
    raise RuntimeError("V20.80 V175 runtime missing")
body=m.group(2)
anchor="  function postRenderV175(){"
if body.count(anchor)!=1:
    raise RuntimeError("V20.80 V175 postRender anchor mismatch")
body=body.replace(anchor,anchor+"\n    window.__fjzOperationalDashboardV280?.();",1)
html=html[:m.start(2)]+body+html[m.end(2):]

css=r"""
/* TEAM FJZ · V20.80 PRIORITY/CALENDAR RECOVERY */
.v280-operational-error{
  padding:12px;
  border:1px solid rgba(242,189,85,.22);
  border-radius:10px;
  background:rgba(242,189,85,.04);
  color:#aeb4bd;
  font-size:9px;
  line-height:1.45;
}
.v280-operational-error strong{
  display:block;
  margin-bottom:4px;
  color:#f1c86f;
  font-size:10px;
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.80 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

runtime=r"""
<script id="v280OperationalRecoveryRuntime">
(function(){
  let operationalHydrateV280=false;

  function priorityFallbackV280(e){
    const host=el('v252PriorityCenter');
    if(!host)return;
    host.innerHTML=
      '<div class="v280-operational-error"><strong>Prioridades disponibles con datos parciales</strong>'+
      'No se pudo calcular una señal puntual. El resto del panel sigue operativo.</div>';
    console.warn('TEAM FJZ V20.80 priority recovery',e);
  }

  function calendarFallbackV280(e){
    const host=el('v259CoachCalendar');
    if(!host)return;
    host.innerHTML=
      '<div class="v280-operational-error"><strong>Calendario disponible sin sincronización remota</strong>'+
      'Mostrando el panel local de staging. La nube de producción continúa bloqueada.</div>';
    console.warn('TEAM FJZ V20.80 calendar recovery',e);
  }

  window.__fjzOperationalDashboardV280=function(){
    if(operationalHydrateV280)return;
    if(!(mode==='coach'&&coachTab==='dashboard'))return;
    const pHost=el('v252PriorityCenter');
    const cHost=el('v259CoachCalendar');
    if(!pHost&&!cHost)return;

    operationalHydrateV280=true;
    try{
      if(pHost){
        try{renderCoachPriorityCenterV252()}catch(e){priorityFallbackV280(e)}
      }
      if(cHost){
        try{
          renderCoachCalendarV259();
          const out=hydrateCoachCalendarV259();
          if(out&&typeof out.catch==='function')out.catch(calendarFallbackV280);
        }catch(e){calendarFallbackV280(e)}
      }
    }finally{
      operationalHydrateV280=false;
    }
  };

  window.refreshCoachOperationalV280=function(){
    if(!(mode==='coach'&&coachTab==='dashboard'))return;
    try{renderCoachPriorityCenterV252()}catch(e){priorityFallbackV280(e)}
    try{
      coachCalendarLoadedAtV259=0;
      return Promise.resolve(loadCoachCalendarV259(true)).catch(calendarFallbackV280);
    }catch(e){
      calendarFallbackV280(e);
    }
  };

  window.__fjzV280={
    version:'20.80',
    priorityCalendarRecovery:true,
    priorityPerStudentIsolation:true,
    calendarIndependentFromPriority:true,
    stagingCalendarFallbackSafe:true,
    explicitDashboardOperationalHydration:true,
    reviewCadenceFallback:true,
    productionUntouched:true,
    noExtraTimers:true,
    noExtraListeners:true,
    noExtraObservers:true
  };
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-priority-calendar-recovery" content="20.80">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.80 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-priority-calendar-recovery" content="20.80"',
    "priorityCalendarRecovery:true",
    "priorityPerStudentIsolation:true",
    "calendarIndependentFromPriority:true",
    "stagingCalendarFallbackSafe:true",
    "explicitDashboardOperationalHydration:true",
    "reviewCadenceFallback:true",
    "__fjzOperationalDashboardV280",
    "typeof agendaRemindersV81!=='undefined'",
]:
    if marker not in html:
        raise RuntimeError("V20.80 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.80 priority/calendar recovery")
print("V20.80 BEFORE:",before)
print("V20.80 AFTER:",after)
print("V20.80 priorities and calendar decoupled + staging fallback hardened")
