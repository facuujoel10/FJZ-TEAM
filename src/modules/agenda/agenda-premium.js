(function(root,factory){
  const api=factory(root||{});
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.TeamFJZAgendaPremium=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(root){
  'use strict';
  const VERSION='22.4C',TZ='America/Argentina/Buenos_Aires',DAY=86400000;
  const ui={studentMonth:null,coachMonth:null,selectedStudentDate:'',selectedCoachEvent:'',studentData:null,coachData:[],studentNotice:'',coachNotice:''};
  const text=v=>String(v??'').trim();
  const esc=v=>text(v).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const pad=n=>String(n).padStart(2,'0');
  const localKey=d=>d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate());
  const dateOnly=v=>/^\d{4}-\d{2}-\d{2}$/.test(text(v).slice(0,10))?text(v).slice(0,10):'';
  const parseDate=v=>{const m=dateOnly(v).match(/^(\d{4})-(\d{2})-(\d{2})$/);if(!m)return null;const d=new Date(+m[1],+m[2]-1,+m[3],12);return Number.isNaN(d.getTime())?null:d};
  const startDay=d=>new Date(d.getFullYear(),d.getMonth(),d.getDate());
  const addDays=(d,n)=>{const x=new Date(d);x.setDate(x.getDate()+Number(n||0));return x};
  const weekdayMon=d=>(d.getDay()+6)%7;
  const nextWeekday=(weekday,from)=>{const x=startDay(from),delta=(Number(weekday)-weekdayMon(x)+7)%7;x.setDate(x.getDate()+delta);return x};
  const fmtDate=(v,opts={})=>{const d=v instanceof Date?v:parseDate(v)||new Date(v);if(!d||Number.isNaN(d.getTime()))return'Sin fecha';return new Intl.DateTimeFormat('es-AR',{timeZone:TZ,weekday:opts.weekday?'long':undefined,day:'2-digit',month:'short',year:opts.year===false?undefined:'numeric'}).format(d)};
  const fmtTime=v=>text(v)?text(v).slice(0,5):'';
  const actions=()=>root.__fjzAgendaPremiumActionsV22||{};
  const context=()=>{try{return root.__fjzAgendaPremiumContextV22?.()||{}}catch(_e){return{}}};
  function monthStart(d=new Date()){return new Date(d.getFullYear(),d.getMonth(),1)}
  function monthTitle(d){const s=new Intl.DateTimeFormat('es-AR',{timeZone:TZ,month:'long',year:'numeric'}).format(d);return s.charAt(0).toUpperCase()+s.slice(1)}
  function stableEventKey(e){return[e.kind,e.id,e.date,e.time||''].join('|')}
  function eventFromReminder(r,date,athlete=null){
    return {id:text(r.id),kind:'reminder',date:localKey(date),time:fmtTime(r.remind_time),title:text(r.title)||'Recordatorio',body:text(r.body),category:text(r.category),athleteId:text(r.athlete_id),athleteName:text(athlete?.name),status:'scheduled',source:r};
  }
  function eventFromSchedule(s,date,athlete=null){
    return {id:text(s.id),kind:'schedule',date:localKey(date),time:fmtTime(s.start_time),title:text(s.workout_day_name)||'Entrenamiento',body:text(s.notes),athleteId:text(s.athlete_id),athleteName:text(athlete?.name),status:'scheduled',source:s};
  }
  function expandAgenda(data,{from=new Date(),days=75,athlete=null}={}){
    const start=startDay(from),limit=addDays(start,days),out=[],seen=new Set();
    const push=e=>{const k=stableEventKey(e);if(seen.has(k))return;seen.add(k);out.push(e)};
    (data?.reminders||[]).forEach(r=>{
      if(r?.active===false)return;
      if(r.schedule_type==='once'){
        const d=parseDate(r.reminder_date);if(d&&d>=start&&d<=limit)push(eventFromReminder(r,d,athlete));
      }else if(Number.isInteger(Number(r.weekday))){
        let d=nextWeekday(Number(r.weekday),start);
        while(d<=limit){push(eventFromReminder(r,d,athlete));d=addDays(d,7)}
      }
    });
    (data?.schedule||[]).forEach(s=>{
      if(s?.active===false||!Number.isInteger(Number(s.weekday)))return;
      let d=nextWeekday(Number(s.weekday),start);
      while(d<=limit){push(eventFromSchedule(s,d,athlete));d=addDays(d,7)}
    });
    return out.sort((a,b)=>a.date.localeCompare(b.date)||String(a.time||'99:99').localeCompare(String(b.time||'99:99'))||a.title.localeCompare(b.title));
  }
  function deriveEvents(data,{athlete=null,now=new Date(),days=75}={}){
    const today=localKey(now);
    return expandAgenda(data,{from:now,days,athlete}).map(e=>({...e,isPast:e.date<today,isToday:e.date===today,isFuture:e.date>=today}));
  }
  function calendarDays(month,events){
    const y=month.getFullYear(),m=month.getMonth(),first=new Date(y,m,1),offset=weekdayMon(first),last=new Date(y,m+1,0).getDate(),cells=[];
    for(let i=0;i<offset;i++)cells.push({muted:true,key:'pre-'+i});
    for(let day=1;day<=last;day++){const d=new Date(y,m,day),key=localKey(d);cells.push({key,day,events:events.filter(e=>e.date===key),today:key===localKey(new Date())})}
    while(cells.length%7)cells.push({muted:true,key:'post-'+cells.length});
    return cells;
  }
  function eventLabel(e){
    const type=e.kind==='schedule'?'Entrenamiento':'Recordatorio';
    return type+(e.time?' · '+e.time:'');
  }
  function eventCard(e,{coach=false,selected=false}={}){
    return '<button type="button" class="fjz4c-event '+(selected?'selected ':'')+(e.isToday?'today ':'')+'" data-4c-event="'+esc(stableEventKey(e))+'">'+
      '<span class="fjz4c-event-date"><b>'+esc(fmtDate(e.date,{weekday:true,year:false}))+'</b><small>'+esc(e.time||'Sin horario')+'</small></span>'+
      '<span class="fjz4c-event-copy"><strong>'+esc(e.title)+'</strong><small>'+esc(e.body||eventLabel(e))+'</small>'+(coach&&e.athleteName?'<em>'+esc(e.athleteName)+'</em>':'')+'</span><span class="fjz4c-arrow">›</span></button>';
  }
  function detailHtml(e,{coach=false}={}){
    if(!e)return '<div class="fjz4c-empty"><strong>Seleccioná un evento</strong><span>El detalle aparece acá sin salir de Agenda.</span></div>';
    return '<article class="fjz4c-detail" data-event-id="'+esc(e.id)+'"><div class="fjz4c-kicker">DETALLE DEL EVENTO</div><h3>'+esc(e.title)+'</h3>'+
      '<div class="fjz4c-detail-facts"><span><small>Fecha</small><b>'+esc(fmtDate(e.date,{weekday:true}))+'</b></span><span><small>Hora</small><b>'+esc(e.time||'Sin horario')+'</b></span><span><small>Tipo</small><b>'+esc(e.kind==='schedule'?'Entrenamiento programado':'Recordatorio')+'</b></span>'+(coach&&e.athleteName?'<span><small>Alumno</small><b>'+esc(e.athleteName)+'</b></span>':'')+'</div>'+
      (e.body?'<p>'+esc(e.body)+'</p>':'')+
      (coach?'<div class="fjz4c-detail-actions"><button type="button" class="btn" data-4c-action="open-athlete" data-athlete="'+esc(e.athleteId)+'">Abrir alumno</button>'+(e.kind==='reminder'?'<button type="button" class="btn ghost" data-4c-action="delete-reminder" data-id="'+esc(e.id)+'" data-athlete="'+esc(e.athleteId)+'">Eliminar</button>':'')+'</div>':'')+
      '</article>';
  }
  function calendarHtml(month,events,selectedDate){
    const cells=calendarDays(month,events);
    return '<div class="fjz4c-calendar"><div class="fjz4c-weekdays">'+['Lun','Mar','Mié','Jue','Vie','Sáb','Dom'].map(x=>'<span>'+x+'</span>').join('')+'</div><div class="fjz4c-days">'+cells.map(c=>c.muted?'<span class="fjz4c-day muted"></span>':'<button type="button" class="fjz4c-day '+(c.today?'today ':'')+(selectedDate===c.key?'selected ':'')+(c.events.length?'has-events':'')+'" data-4c-date="'+c.key+'"><b>'+c.day+'</b>'+(c.events.length?'<i>'+Math.min(c.events.length,9)+'</i>':'')+'</button>').join('')+'</div></div>';
  }
  function studentView(data){
    const c=context(),events=deriveEvents(data,{athlete:c.athlete,days:100}),next=events.find(e=>!e.isPast)||null;
    if(!ui.studentMonth)ui.studentMonth=monthStart(next?parseDate(next.date):new Date());
    if(!ui.selectedStudentDate)ui.selectedStudentDate=next?.date||localKey(new Date());
    const dayEvents=events.filter(e=>e.date===ui.selectedStudentDate),selected=dayEvents[0]||next;
    return '<div class="fjz4c-shell fjz4c-student">'+
      '<header class="fjz4c-hero"><div><span>AGENDA PREMIUM</span><h2>Lo próximo, claro y a tiempo</h2><p>Seguimientos, entrenamientos y recordatorios confirmados en tu agenda.</p></div>'+
      (next?'<button class="fjz4c-next" type="button" data-4c-date="'+esc(next.date)+'"><small>PRÓXIMO EVENTO</small><strong>'+esc(next.title)+'</strong><span>'+esc(fmtDate(next.date,{weekday:true}))+(next.time?' · '+esc(next.time):'')+'</span></button>':'<div class="fjz4c-next empty"><small>PRÓXIMO EVENTO</small><strong>Sin fechas próximas</strong><span>No hay eventos futuros confirmados.</span></div>')+'</header>'+
      '<div class="fjz4c-toolbar"><button class="btn small" data-4c-action="shift-month" data-delta="-1">‹</button><strong>'+esc(monthTitle(ui.studentMonth))+'</strong><button class="btn small" data-4c-action="shift-month" data-delta="1">›</button></div>'+
      '<section class="fjz4c-layout"><div class="fjz4c-calendar-panel">'+calendarHtml(ui.studentMonth,events,ui.selectedStudentDate)+'</div><aside class="fjz4c-side"><div class="fjz4c-side-head"><span>FECHA SELECCIONADA</span><strong>'+esc(fmtDate(ui.selectedStudentDate,{weekday:true}))+'</strong></div><div class="fjz4c-event-list">'+(dayEvents.length?dayEvents.map(e=>eventCard(e)).join(''):'<div class="fjz4c-empty"><strong>Sin eventos este día</strong><span>Elegí otra fecha marcada en el calendario.</span></div>')+'</div>'+detailHtml(selected)+'</aside></section>'+
      '<section class="fjz4c-upcoming"><div class="fjz4c-panel-head"><div><span>SIGUIENTES</span><h3>Próximos eventos</h3></div><small>'+events.filter(e=>!e.isPast).length+' confirmados</small></div><div class="fjz4c-event-list">'+(events.filter(e=>!e.isPast).slice(0,8).map(e=>eventCard(e)).join('')||'<div class="fjz4c-empty"><strong>Agenda despejada</strong><span>No hay eventos próximos.</span></div>')+'</div></section></div>';
  }
  function coachView(items){
    const events=items.flatMap(x=>deriveEvents(x.data,{athlete:x.athlete,days:100})).sort((a,b)=>a.date.localeCompare(b.date)||String(a.time||'99:99').localeCompare(String(b.time||'99:99')));
    const next=events.find(e=>!e.isPast)||null;
    if(!ui.coachMonth)ui.coachMonth=monthStart(next?parseDate(next.date):new Date());
    const monthEvents=events.filter(e=>{const d=parseDate(e.date);return d&&d.getFullYear()===ui.coachMonth.getFullYear()&&d.getMonth()===ui.coachMonth.getMonth()});
    const selected=events.find(e=>stableEventKey(e)===ui.selectedCoachEvent)||next||null;
    return '<div class="fjz4c-shell fjz4c-coach"><header class="fjz4c-hero"><div><span>AGENDA DEL COACH</span><h2>Seguimientos en una sola vista</h2><p>Fechas reales por alumno, sin mezclar revisiones pendientes con eventos programados.</p></div><div class="fjz4c-hero-actions"><button class="btn" data-4c-action="back-dashboard">← Command Center</button></div></header>'+
      '<div class="fjz4c-coach-stats"><div><strong>'+events.filter(e=>e.isToday).length+'</strong><span>Hoy</span></div><div><strong>'+events.filter(e=>!e.isPast).length+'</strong><span>Próximos</span></div><div><strong>'+items.length+'</strong><span>Alumnos con acceso</span></div></div>'+
      '<div class="fjz4c-toolbar"><button class="btn small" data-4c-action="shift-coach-month" data-delta="-1">‹</button><strong>'+esc(monthTitle(ui.coachMonth))+'</strong><button class="btn small" data-4c-action="shift-coach-month" data-delta="1">›</button></div>'+
      '<section class="fjz4c-coach-grid"><div class="fjz4c-calendar-panel">'+calendarHtml(ui.coachMonth,monthEvents,'')+'</div><aside class="fjz4c-side"><div class="fjz4c-panel-head"><div><span>PRÓXIMO</span><h3>Seguimientos</h3></div></div><div class="fjz4c-event-list">'+(events.filter(e=>!e.isPast).slice(0,10).map(e=>eventCard(e,{coach:true,selected:selected&&stableEventKey(e)===stableEventKey(selected)})).join('')||'<div class="fjz4c-empty"><strong>Sin eventos próximos</strong><span>No hay seguimientos programados.</span></div>')+'</div>'+detailHtml(selected,{coach:true})+'</aside></section></div>';
  }
  function bind(host,coach=false){
    if(!host)return;
    host.onclick=async e=>{
      const dateBtn=e.target.closest('[data-4c-date]');if(dateBtn){if(coach)return;ui.selectedStudentDate=dateBtn.dataset['4cDate'];renderStudent();return}
      const eventBtn=e.target.closest('[data-4c-event]');if(eventBtn){if(coach){ui.selectedCoachEvent=eventBtn.dataset['4cEvent'];renderCoach()}return}
      const b=e.target.closest('[data-4c-action]');if(!b)return;
      const a=b.dataset['4cAction'];
      if(a==='shift-month'){ui.studentMonth=new Date(ui.studentMonth.getFullYear(),ui.studentMonth.getMonth()+Number(b.dataset.delta||0),1);renderStudent()}
      else if(a==='shift-coach-month'){ui.coachMonth=new Date(ui.coachMonth.getFullYear(),ui.coachMonth.getMonth()+Number(b.dataset.delta||0),1);renderCoach()}
      else if(a==='back-dashboard')actions().backDashboard?.();
      else if(a==='open-athlete')actions().openAthlete?.(b.dataset.athlete,'agenda');
      else if(a==='delete-reminder'){b.disabled=true;try{await actions().deleteReminder?.(b.dataset.id,b.dataset.athlete);ui.coachNotice='<div class="fjz4c-success">✓ Guardado correctamente.</div>';await renderCoach(true)}catch(err){b.disabled=false;actions().showError?.(err)}}
    };
  }
  async function renderStudent(force=false){
    const host=root.document?.getElementById('studentSubBody');if(!host)return false;
    host.innerHTML='<div class="fjz4c-loading">Cargando tu agenda…</div>';
    try{ui.studentData=await actions().loadStudent?.(force);host.innerHTML=studentView(ui.studentData);bind(host,false);return true}catch(err){host.innerHTML='<div class="fjz4c-error"><strong>No pudimos cargar Agenda</strong><span>'+esc(err?.message||'Error de lectura')+'</span><button class="btn small" data-4c-action="retry-student">Reintentar</button></div>';return false}
  }
  async function renderCoach(force=false){
    const host=root.document?.getElementById('view');if(!host)return false;
    host.innerHTML='<div class="fjz4c-loading">Cargando agenda del Coach…</div>';
    try{ui.coachData=await actions().loadCoach?.(force)||[];host.innerHTML=coachView(ui.coachData);bind(host,true);return true}catch(err){host.innerHTML='<div class="fjz4c-error"><strong>No pudimos cargar Agenda</strong><span>'+esc(err?.message||'Error de lectura')+'</span></div>';return false}
  }
  async function renderCoachAthlete(force=false){
    const host=root.document?.getElementById('coachStudentBody');if(!host)return false;
    const c=context();host.innerHTML='<div class="fjz4c-loading">Cargando agenda del alumno…</div>';
    try{const data=await actions().loadAthlete?.(c.athlete?.id,force);host.innerHTML=studentView(data).replace('fjz4c-student','fjz4c-student fjz4c-coach-athlete');bind(host,false);const create=root.document.createElement('div');create.className='fjz4c-coach-create';create.innerHTML='<button type="button" class="btn primary" id="fjz4cAddReminder">+ Nuevo recordatorio</button><button type="button" class="btn" id="fjz4cEditWeekly">Editar programación semanal</button>';host.prepend(create);root.document.getElementById('fjz4cAddReminder').onclick=()=>actions().openAddReminder?.();root.document.getElementById('fjz4cEditWeekly').onclick=()=>actions().openLegacySchedule?.();return true}catch(err){host.innerHTML='<div class="fjz4c-error"><strong>No pudimos cargar Agenda</strong><span>'+esc(err?.message||'Error de lectura')+'</span></div>';return false}
  }
  function homeCard(event){
    if(!event)return'';
    return '<section class="fjz4c-home-next" id="fjz4cHomeNext"><div><span>PRÓXIMO SEGUIMIENTO</span><strong>'+esc(event.title)+'</strong><small>'+esc(fmtDate(event.date,{weekday:true}))+(event.time?' · '+esc(event.time):'')+'</small></div><button class="btn small" type="button" onclick="studentTab=\'agenda\';render()">Ver agenda</button></section>';
  }
  function install(){root.__fjzAgendaPremiumV22=api;return true}
  const api={VERSION,parseDate,localKey,nextWeekday,expandAgenda,deriveEvents,calendarDays,studentView,coachView,homeCard,renderStudent,renderCoach,renderCoachAthlete,install};
  return Object.freeze(api);
});