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
    'meta name="fjz-coach-integrity-recovery" content="20.81"',
    'id="v280OperationalRecoveryRuntime"',
    "coachIntegrityRecovery:true",
    "priorityCalendarRecovery:true",
]:
    if marker not in html:
        raise RuntimeError("V20.82 prerequisite missing "+marker)

css=r"""
/* TEAM FJZ · V20.82 CALENDAR ROUTE HARDENING */
.v282-agenda-status{display:flex;align-items:center;justify-content:space-between;gap:8px;margin:0 0 10px;padding:8px 10px;border:1px solid #2c3038;border-radius:10px;background:#0d0f13;color:#9aa0aa;font-size:8px}
.v282-agenda-status strong{color:#eef0f3;font-size:9px}
.v282-week-grid{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:6px}
.v282-week-day{min-width:0;border:1px solid #2a2e36;border-radius:10px;background:#0d0f13;overflow:hidden}
.v282-week-day.today{box-shadow:inset 0 0 0 1px rgba(255,70,88,.65)}
.v282-week-head{padding:8px;border-bottom:1px solid #252931}
.v282-week-head strong{display:block;color:#eff1f3;font-size:9px}.v282-week-head span{display:block;margin-top:2px;color:#858c96;font-size:7px}
.v282-week-items{display:grid;gap:5px;padding:7px}
.v282-week-item{min-width:0;padding:6px 7px;border:1px solid #292d35;border-radius:7px;background:#12151a}
.v282-week-item strong{display:block;color:#e9ebee;font-size:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.v282-week-item span{display:block;margin-top:2px;color:#858c96;font-size:7px;line-height:1.35}
.v282-empty-day{padding:7px;color:#666d77;font-size:7px;text-align:center}
.v282-fallback-calendar{margin:0 0 14px}
.v282-fallback-days{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));border:1px solid #2c3038;border-radius:10px;overflow:hidden;background:#0d0f13}
.v282-fallback-day{min-height:52px;padding:5px;border-right:1px solid #242831;border-bottom:1px solid #242831;color:#8c939d;font-size:7px}
.v282-fallback-day:nth-child(7n){border-right:0}.v282-fallback-day.today{box-shadow:inset 0 0 0 1px rgba(255,70,88,.65);color:#f2f3f5}
.v282-fallback-dot{display:block;width:5px;height:5px;margin-top:5px;border-radius:999px;background:#ff4658}
@media(max-width:760px){.v282-week-grid{grid-template-columns:1fr 1fr}.v282-week-day:last-child{grid-column:1/-1}}
@media(max-width:430px){.v282-week-grid{grid-template-columns:1fr}.v282-week-day:last-child{grid-column:auto}.v282-agenda-status{align-items:flex-start;display:grid}.v282-fallback-day{min-height:44px;padding:4px;font-size:6.5px}}
"""
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.82 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

runtime=r"""
<script id="v282CalendarRouteHardeningRuntime">
(function(){
  const DAY_V282=86400000;
  const weekNamesV282=['Lun','Mar','Mié','Jue','Vie','Sáb','Dom'];

  function startDayV282(d){const x=new Date(d);x.setHours(0,0,0,0);return x}
  function mondayV282(d=new Date()){const x=startDayV282(d),wd=(x.getDay()+6)%7;x.setDate(x.getDate()-wd);return x}
  function isoV282(d){return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')}
  function localScheduleV282(){
    try{return typeof agendaScheduleV81!=='undefined'&&Array.isArray(agendaScheduleV81)?agendaScheduleV81.filter(x=>x?.active!==false):[]}
    catch(_e){return []}
  }
  function localRemindersV282(){
    try{return typeof agendaRemindersV81!=='undefined'&&Array.isArray(agendaRemindersV81)?agendaRemindersV81.filter(x=>x?.active!==false):[]}
    catch(_e){return []}
  }
  function studentNameForAgendaV282(row){
    try{
      if(typeof athleteByIdV81==='function'){
        const a=athleteByIdV81(row?.athlete_id);
        if(a?.name)return a.name;
      }
    }catch(_e){}
    const students=Array.isArray(state?.students)?state.students:[];
    const direct=students.find(s=>String(s?.id)===String(row?.client_id||row?.athlete_id));
    return direct?.name||'Alumno';
  }
  function reminderOnV282(r,d){
    try{if(typeof reminderOccursV81==='function')return !!reminderOccursV81(r,d)}catch(_e){}
    if(r?.schedule_type==='once')return String(r?.reminder_date||'')===isoV282(d);
    return Number(r?.weekday)===(d.getDay()+6)%7;
  }
  function renderAgendaBodyV282(note='Agenda cargada'){
    if(!(mode==='coach'&&coachTab==='agenda'))return;
    const host=el('v282CoachAgendaBody');if(!host)return;
    const schedule=localScheduleV282(),reminders=localRemindersV282();
    const start=mondayV282(),dates=Array.from({length:7},(_,i)=>{const d=new Date(start);d.setDate(d.getDate()+i);return d});
    const todayIso=isoV282(new Date()),todayIdx=(new Date().getDay()+6)%7;
    const todayRows=schedule.filter(x=>Number(x?.weekday)===todayIdx);
    const reminderWeek=reminders.filter(r=>dates.some(d=>reminderOnV282(r,d))).length;
    const dayHtml=dates.map((d,i)=>{
      const rows=schedule.filter(x=>Number(x?.weekday)===i).sort((a,b)=>String(a?.start_time||'99').localeCompare(String(b?.start_time||'99')));
      const rem=reminders.filter(r=>reminderOnV282(r,d));
      const items=[
        ...rows.map(x=>'<div class="v282-week-item"><strong>'+esc(studentNameForAgendaV282(x))+'</strong><span>'+esc(String(x?.start_time||'Sin horario').slice(0,5))+' · '+esc(x?.workout_day_name||'Entrenamiento')+'</span></div>'),
        ...rem.slice(0,2).map(x=>'<div class="v282-week-item"><strong>'+esc(studentNameForAgendaV282(x))+'</strong><span>'+esc(x?.title||'Recordatorio')+'</span></div>')
      ];
      return '<div class="v282-week-day '+(isoV282(d)===todayIso?'today':'')+'"><div class="v282-week-head"><strong>'+weekNamesV282[i]+'</strong><span>'+new Intl.DateTimeFormat('es-AR',{day:'2-digit',month:'short'}).format(d)+'</span></div><div class="v282-week-items">'+(items.length?items.join(''):'<div class="v282-empty-day">Sin eventos</div>')+'</div></div>';
    }).join('');

    host.innerHTML=
      '<div class="v282-agenda-status"><div><strong>'+esc(note)+'</strong><div>La vista siempre se monta; los datos conectados se actualizan cuando están disponibles.</div></div><span class="badge '+(schedule.length||reminders.length?'blue':'gray')+'">'+(schedule.length||reminders.length?'Con datos':'Sin eventos')+'</span></div>'+
      '<div class="grid kpi"><div class="card"><strong>'+todayRows.length+'</strong><span>Programados hoy</span></div><div class="card"><strong>'+schedule.length+'</strong><span>Bloques semanales</span></div><div class="card"><strong>'+reminderWeek+'</strong><span>Recordatorios esta semana</span></div></div>'+
      '<div class="card"><div class="section-title"><div><h3>Semana actual</h3><div class="muted tiny">Calendario operativo del Coach.</div></div></div><div class="v282-week-grid">'+dayHtml+'</div></div>';
  }

  async function hydrateAgendaV282(){
    if(!(mode==='coach'&&coachTab==='agenda'))return;
    if(window.__fjzStagingLocal?.enabled||!cloudEnabled||!supabaseClient){renderAgendaBodyV282('Agenda cargada en staging');return}
    try{
      if(typeof loadAgendaV81==='function')await loadAgendaV81(true);
      renderAgendaBodyV282('Agenda actualizada');
    }catch(e){
      console.warn('TEAM FJZ V20.82 agenda hydration',e);
      renderAgendaBodyV282('Agenda disponible · no se pudieron actualizar datos conectados');
    }
  }

  function renderCoachAgendaV282(){
    const v=el('view');if(!v)return;
    v.innerHTML='<section class="hero"><div><h2>Calendario del Coach</h2><p>Agenda semanal, entrenamientos programados y recordatorios.</p></div><div class="pill-row"><button class="btn" onclick="coachTab=\'dashboard\';render()">← Panel</button></div></section><div id="v282CoachAgendaBody"></div>';
    renderAgendaBodyV282('Agenda cargada');
    hydrateAgendaV282();
  }

  function ensureMonthlyHostV282(){
    if(!(mode==='coach'&&coachTab==='dashboard'))return null;
    let host=el('v259CoachCalendar');if(host)return host;
    const view=el('view');if(!view)return null;
    host=document.createElement('section');
    host.id='v259CoachCalendar';
    host.className='card v280-calendar-card v282-fallback-calendar';
    const priority=el('v252PriorityCenter');
    if(priority?.parentNode)priority.insertAdjacentElement('afterend',host);
    else{
      const grid=view.querySelector('.v225-dashboard-grid,.grid.two');
      if(grid?.parentNode)grid.insertAdjacentElement('beforebegin',host);
      else{
        const hero=view.querySelector('.hero');
        if(hero)hero.insertAdjacentElement('afterend',host);
        else view.prepend(host);
      }
    }
    return host;
  }

  function renderMonthlyFallbackV282(host){
    if(!host)return;
    const now=new Date(),y=now.getFullYear(),m=now.getMonth(),first=new Date(y,m,1),last=new Date(y,m+1,0).getDate(),offset=(first.getDay()+6)%7;
    const dueDates=new Set();
    const students=Array.isArray(state?.students)?state.students:[];
    students.forEach(s=>{
      try{
        const due=typeof coachReviewDueV240==='function'?coachReviewDueV240(s):null;
        if(due?.due)dueDates.add(isoV282(now));
      }catch(_e){}
    });
    const cells=[];
    for(let i=0;i<offset;i++)cells.push('<div class="v282-fallback-day"></div>');
    for(let day=1;day<=last;day++){
      const d=new Date(y,m,day),k=isoV282(d);
      cells.push('<div class="v282-fallback-day '+(k===isoV282(now)?'today':'')+'">'+day+(dueDates.has(k)?'<span class="v282-fallback-dot"></span>':'')+'</div>');
    }
    host.innerHTML='<div class="v280-calendar-head"><div><div class="v225-section-kicker">CALENDARIO DEL COACH</div><h3>'+esc(new Intl.DateTimeFormat('es-AR',{month:'long',year:'numeric'}).format(now))+'</h3><p>Vista disponible mientras se hidratan chequeos y recordatorios.</p></div></div><div class="v282-fallback-days">'+cells.join('')+'</div>';
  }

  function mountDashboardCalendarV282(){
    if(!(mode==='coach'&&coachTab==='dashboard'))return;
    const host=ensureMonthlyHostV282();if(!host)return;
    if(!host.innerHTML.trim())renderMonthlyFallbackV282(host);
    try{
      if(typeof window.__fjzOperationalDashboardV280==='function')window.__fjzOperationalDashboardV280();
    }catch(e){
      console.warn('TEAM FJZ V20.82 monthly calendar recovery',e);
      renderMonthlyFallbackV282(host);
    }
  }

  const baseRenderCoachV282=window.renderCoach;
  window.renderCoachAgendaV282=renderCoachAgendaV282;
  window.renderCoachAgendaV81=renderCoachAgendaV282;
  window.renderCoach=function(){
    if(coachTab==='agenda')return renderCoachAgendaV282();
    return typeof baseRenderCoachV282==='function'?baseRenderCoachV282.apply(this,arguments):undefined;
  };
  try{renderCoach=window.renderCoach}catch(_e){}
  try{renderCoachAgendaV81=renderCoachAgendaV282}catch(_e){}

  window.__fjzMountCoachCalendarV282=mountDashboardCalendarV282;
  if(typeof fjzPostRenderV125==='function'){
    fjzPostRenderV125('v282-calendar-route',()=>{
      if(mode==='coach'&&coachTab==='dashboard')mountDashboardCalendarV282();
      if(mode==='coach'&&coachTab==='agenda'&&!el('v282CoachAgendaBody'))renderCoachAgendaV282();
    });
  }

  if(mode==='coach'&&coachTab==='dashboard')mountDashboardCalendarV282();

  window.__fjzV282={
    version:'20.82',
    agendaFinalRouteAuthority:true,
    agendaImmediateFrame:true,
    agendaNoPermanentSpinner:true,
    calendarHostIndependentFromPriority:true,
    dashboardCalendarFallback:true,
    hudAgendaRouteCovered:true,
    productionUntouched:true,
    noExtraTimers:true,
    noExtraListeners:true,
    noExtraObservers:true
  };
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-calendar-route-hardening" content="20.82">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.82 topology changed "+key+": "+repr({"before":before,"after":after}))

required=[
 'meta name="fjz-calendar-route-hardening" content="20.82"',
 "agendaFinalRouteAuthority:true","agendaImmediateFrame:true","agendaNoPermanentSpinner:true",
 "calendarHostIndependentFromPriority:true","dashboardCalendarFallback:true","hudAgendaRouteCovered:true",
 "if(coachTab==='agenda')return renderCoachAgendaV282()",
 "window.renderCoachAgendaV81=renderCoachAgendaV282",
 "window.__fjzMountCoachCalendarV282=mountDashboardCalendarV282",
 "v282CoachAgendaBody","v259CoachCalendar"
]
for marker in required:
    if marker not in html: raise RuntimeError("V20.82 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.82 calendar route hardening")
print("V20.82 BEFORE:",before)
print("V20.82 AFTER:",after)
print("V20.82 agenda route + dashboard calendar host hardened with immediate fallback")
