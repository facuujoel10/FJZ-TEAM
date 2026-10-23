import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\\.)?render\\s*=",doc)),
        "channels":len(re.findall(r"\\.channel\\s*\\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\\s*\\(",doc)),
        "intervals":len(re.findall(r"setInterval\\s*\\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\\s*\\(",doc)),
        "listeners":len(re.findall(r"addEventListener\\s*\\(",doc)),
        "mutation_observers":len(re.findall(r"new\\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\\s+PerformanceObserver",doc)),
    }

def edit_script(doc,script_id,transform):
    pat=re.compile(r'(<script[^>]*\\bid=["\\']'+re.escape(script_id)+r'["\\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m: raise RuntimeError("V20.84 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body: raise RuntimeError("V20.84 no changes in "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-mobile-legacy-isolation" content="20.83"',
    'id="v280OperationalRecoveryRuntime"',
    'id="v282CalendarRouteHardeningRuntime"',
    "calendarHostIndependentFromPriority:true",
]:
    if marker not in html:
        raise RuntimeError("V20.84 prerequisite missing "+marker)

# ------------------------------------------------------------------
# Final calendar authority lives inside V282 so no new runtime/listener
# topology is added. It renders immediately from Agenda's canonical local
# data and hydrates remote Agenda data only when available.
# ------------------------------------------------------------------
def patch_v282(body):
    anchor="  window.__fjzV282={"
    if body.count(anchor)!=1:
        raise RuntimeError("V20.84 V282 authority anchor mismatch")

    final_calendar=r"""
  // V20.84: final monthly calendar authority. Independent from Priority
  // center and from V20.80's historical calendar renderer.
  let monthV284=new Date(new Date().getFullYear(),new Date().getMonth(),1);
  let calendarHydratingV284=false,calendarHydratedAtV284=0;

  function monthTitleV284(d){
    const s=new Intl.DateTimeFormat('es-AR',{month:'long',year:'numeric'}).format(d);
    return s.charAt(0).toUpperCase()+s.slice(1);
  }

  function calendarRowsForDateV284(d){
    const weekday=(d.getDay()+6)%7;
    const schedule=localScheduleV282()
      .filter(x=>Number(x?.weekday)===weekday)
      .sort((a,b)=>String(a?.start_time||'99').localeCompare(String(b?.start_time||'99')))
      .map(x=>({
        kind:'schedule',
        name:studentNameForAgendaV282(x),
        label:String(x?.start_time||'').slice(0,5)||'Entrenamiento',
        title:x?.workout_day_name||'Entrenamiento'
      }));

    const reminders=localRemindersV282()
      .filter(r=>reminderOnV282(r,d))
      .map(r=>({
        kind:'reminder',
        name:studentNameForAgendaV282(r),
        label:'Recordatorio',
        title:r?.title||'Recordatorio'
      }));

    return [...schedule,...reminders];
  }

  function ensureMonthlyHostV284(){
    if(!(mode==='coach'&&coachTab==='dashboard'))return null;
    const view=el('view');if(!view)return null;

    let host=el('v259CoachCalendar');
    if(host && !view.contains(host)){
      try{host.remove()}catch(_e){}
      host=null;
    }
    if(host)return host;

    host=document.createElement('section');
    host.id='v259CoachCalendar';
    host.className='card v280-calendar-card v282-fallback-calendar';

    const priority=el('v252PriorityCenter');
    if(priority&&view.contains(priority)&&priority.parentNode){
      priority.insertAdjacentElement('afterend',host);
      return host;
    }

    const grid=view.querySelector('.v225-dashboard-grid,.grid.two');
    if(grid?.parentNode){
      grid.insertAdjacentElement('beforebegin',host);
      return host;
    }

    const hero=view.querySelector('.hero');
    if(hero?.parentNode)hero.insertAdjacentElement('afterend',host);
    else view.prepend(host);
    return host;
  }

  function renderDashboardCalendarV284(){
    if(!(mode==='coach'&&coachTab==='dashboard'))return false;
    const host=ensureMonthlyHostV284();if(!host)return false;

    const y=monthV284.getFullYear(),m=monthV284.getMonth();
    const first=new Date(y,m,1),lastDay=new Date(y,m+1,0).getDate();
    const offset=(first.getDay()+6)%7;
    const todayIso=isoV282(new Date());
    const cells=[];
    let monthEvents=0;

    for(let i=0;i<offset;i++)cells.push('<div class="v280-day muted"></div>');

    for(let day=1;day<=lastDay;day++){
      const d=new Date(y,m,day),k=isoV282(d),rows=calendarRowsForDateV284(d);
      monthEvents+=rows.length;
      const previews=rows.slice(0,2).map(e=>
        '<div class="v280-event '+(e.kind==='reminder'?'reminder':'')+'" title="'+esc(e.name+' · '+e.title)+'">'+
          esc(e.name.split(' ')[0]||'Alumno')+
        '</div>'
      ).join('');
      const extra=rows.length>2?'<div class="v282-empty-day">+'+(rows.length-2)+' más</div>':'';
      cells.push(
        '<div class="v280-day '+(k===todayIso?'today':'')+'">'+
          '<div class="v280-day-num">'+day+'</div>'+
          '<div class="v280-events">'+previews+extra+'</div>'+
        '</div>'
      );
    }

    const today=new Date();today.setHours(0,0,0,0);
    const upcoming=[];
    for(let i=0;i<14;i++){
      const d=new Date(today);d.setDate(d.getDate()+i);
      calendarRowsForDateV284(d).forEach(e=>upcoming.push({d,e}));
    }

    const todayCount=calendarRowsForDateV284(today).length;
    const reminderMonth=(()=>{
      let n=0;
      for(let day=1;day<=lastDay;day++){
        const d=new Date(y,m,day);
        n+=localRemindersV282().filter(r=>reminderOnV282(r,d)).length;
      }
      return n;
    })();

    host.className='card v280-calendar-card';
    host.innerHTML=
      '<div class="v280-calendar-head">'+
        '<div><div class="v225-section-kicker">CALENDARIO DEL COACH</div><h3>Agenda mensual</h3><p>Entrenamientos programados y recordatorios. Esta vista no depende de Prioridades.</p></div>'+
        '<div class="v280-calendar-nav">'+
          '<button class="btn small" onclick="shiftCoachCalendarV284(-1)" aria-label="Mes anterior">‹</button>'+
          '<button class="btn small" onclick="goTodayCoachCalendarV284()">'+esc(monthTitleV284(monthV284))+'</button>'+
          '<button class="btn small" onclick="shiftCoachCalendarV284(1)" aria-label="Mes siguiente">›</button>'+
        '</div>'+
      '</div>'+
      '<div class="v280-calendar-stats">'+
        '<div><strong>'+todayCount+'</strong><span>Eventos hoy</span></div>'+
        '<div><strong>'+monthEvents+'</strong><span>Eventos del mes</span></div>'+
        '<div><strong>'+reminderMonth+'</strong><span>Recordatorios</span></div>'+
      '</div>'+
      '<div class="v280-calendar-layout">'+
        '<div class="v280-month">'+
          '<div class="v280-weekdays">'+weekNamesV282.map(x=>'<span>'+x+'</span>').join('')+'</div>'+
          '<div class="v280-days">'+cells.join('')+'</div>'+
        '</div>'+
        '<aside class="v280-upcoming">'+
          '<div class="v280-upcoming-head"><strong>Próximo</strong><span>14 días</span></div>'+
          '<div class="v280-upcoming-list">'+
            (upcoming.length?upcoming.slice(0,10).map(x=>
              '<div class="v280-upcoming-row">'+
                '<span>'+new Intl.DateTimeFormat('es-AR',{day:'2-digit',month:'short'}).format(x.d)+'</span>'+
                '<span><strong>'+esc(x.e.name)+'</strong><small>'+esc(x.e.label+' · '+x.e.title)+'</small></span>'+
                '<span>•</span>'+
              '</div>'
            ).join(''):'<div class="v280-empty">Sin eventos próximos.</div>')+
          '</div>'+
        '</aside>'+
      '</div>';

    host.dataset.calendarAuthority='20.84';
    return true;
  }

  async function hydrateDashboardCalendarV284(force=false){
    if(!(mode==='coach'&&coachTab==='dashboard'))return;
    renderDashboardCalendarV284();
    if(window.__fjzStagingLocal?.enabled||!cloudEnabled||!supabaseClient)return;
    if(calendarHydratingV284)return;
    if(!force&&calendarHydratedAtV284&&Date.now()-calendarHydratedAtV284<30000)return;

    calendarHydratingV284=true;
    try{
      if(typeof loadAgendaV81==='function')await loadAgendaV81(true);
      calendarHydratedAtV284=Date.now();
    }catch(e){
      console.warn('TEAM FJZ V20.84 calendar hydration',e);
    }finally{
      calendarHydratingV284=false;
      if(mode==='coach'&&coachTab==='dashboard')renderDashboardCalendarV284();
    }
  }

  window.shiftCoachCalendarV284=function(delta){
    monthV284=new Date(monthV284.getFullYear(),monthV284.getMonth()+Number(delta||0),1);
    renderDashboardCalendarV284();
  };
  window.goTodayCoachCalendarV284=function(){
    const d=new Date();
    monthV284=new Date(d.getFullYear(),d.getMonth(),1);
    renderDashboardCalendarV284();
  };
  window.__fjzRenderCoachCalendarV284=renderDashboardCalendarV284;
  window.__fjzHydrateCoachCalendarV284=hydrateDashboardCalendarV284;

  // Keep the legacy public V282 entry point but make it delegate only to the
  // final V20.84 authority.
  mountDashboardCalendarV282=function(){
    if(!(mode==='coach'&&coachTab==='dashboard'))return;
    renderDashboardCalendarV284();
    hydrateDashboardCalendarV284(false);
  };
  window.__fjzMountCoachCalendarV282=mountDashboardCalendarV282;

"""
    body=body.replace(anchor,final_calendar+anchor,1)

    # Synchronous final render: dashboard calendar is mounted in the same
    # renderCoach transaction, rather than relying only on historical hooks.
    old="""    if(coachTab==='agenda')return renderCoachAgendaV282();
    return typeof baseRenderCoachV282==='function'?baseRenderCoachV282.apply(this,arguments):undefined;
  };"""
    new="""    if(coachTab==='agenda')return renderCoachAgendaV282();
    const out=typeof baseRenderCoachV282==='function'?baseRenderCoachV282.apply(this,arguments):undefined;
    if(mode==='coach'&&coachTab==='dashboard'){
      renderDashboardCalendarV284();
      hydrateDashboardCalendarV284(false);
    }
    return out;
  };"""
    if body.count(old)!=1:
        raise RuntimeError("V20.84 final Coach render anchor mismatch")
    body=body.replace(old,new,1)

    body=body.replace(
        "    calendarHostIndependentFromPriority:true,",
        "    calendarHostIndependentFromPriority:true,\n    finalMonthlyCalendarAuthorityV284:true,\n    synchronousDashboardCalendarV284:true,"
    )
    return body

html=edit_script(html,"v282CalendarRouteHardeningRuntime",patch_v282)

# ------------------------------------------------------------------
# V20.80 may still be called by old post-render code. It remains the
# Priority authority but must never repaint the calendar after V20.84.
# ------------------------------------------------------------------
def patch_v280(body):
    old="""  window.__fjzOperationalDashboardV280=function(){
    if(hydratingV280||!(mode==='coach'&&coachTab==='dashboard'))return;
    hydratingV280=true;
    try{renderPriority();renderCalendar();loadCalendar(false)}finally{hydratingV280=false}
  };
  window.refreshCoachOperationalV280=function(){renderPriority();loadedAtV280=0;return loadCalendar(true)};"""
    new="""  window.__fjzOperationalDashboardV280=function(){
    if(hydratingV280||!(mode==='coach'&&coachTab==='dashboard'))return;
    hydratingV280=true;
    try{
      renderPriority();
      window.__fjzRenderCoachCalendarV284?.();
    }finally{hydratingV280=false}
  };
  window.refreshCoachOperationalV280=function(){
    renderPriority();
    return window.__fjzHydrateCoachCalendarV284?.(true);
  };"""
    if body.count(old)!=1:
        raise RuntimeError("V20.84 V280 operational anchor mismatch")
    body=body.replace(old,new,1)
    body=body.replace(
        "explicitDashboardOperationalHydration:true,",
        "explicitDashboardOperationalHydration:true,calendarDelegatedToV284:true,"
    )
    return body

html=edit_script(html,"v280OperationalRecoveryRuntime",patch_v280)

html=html.replace("</head>",'<meta name="fjz-final-calendar-authority" content="20.84">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.84 topology changed "+key+": "+repr({"before":before,"after":after}))

required=[
    'meta name="fjz-final-calendar-authority" content="20.84"',
    "finalMonthlyCalendarAuthorityV284:true",
    "synchronousDashboardCalendarV284:true",
    "calendarDelegatedToV284:true",
    "window.__fjzRenderCoachCalendarV284=renderDashboardCalendarV284",
    "window.__fjzHydrateCoachCalendarV284=hydrateDashboardCalendarV284",
    "host.dataset.calendarAuthority='20.84'",
    "renderDashboardCalendarV284();",
    "hydrateDashboardCalendarV284(false);",
    "window.__fjzRenderCoachCalendarV284?.();",
    "return window.__fjzHydrateCoachCalendarV284?.(true);",
]
for marker in required:
    if marker not in html:
        raise RuntimeError("V20.84 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.84 final calendar authority")
print("V20.84 BEFORE:",before)
print("V20.84 AFTER:",after)
print("V20.84 monthly calendar now renders synchronously and V20.80 delegates calendar ownership")
