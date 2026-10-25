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
    'meta name="fjz-student-current-plan" content="20.58"',
    'meta name="fjz-coach-priority-center" content="20.52"',
    'meta name="fjz-coach-review-cadence" content="20.40"',
    "coachPriorityStateV252",
    "coachReviewCadenceDaysV240",
    "coachReviewDueV240",
    "openCoachStudentTabV235"
]:
    if marker not in html:
        raise RuntimeError("V20.59 missing prerequisite: "+marker)

anchor="function renderCoachFocusV235(){"
if html.count(anchor)!=1:
    raise RuntimeError("V20.59 helper anchor mismatch")

helpers=r"""
/* ---------- Coach Action Center 2.0 + Calendar V20.59 ---------- */
let coachCalendarMonthV259=new Date(new Date().getFullYear(),new Date().getMonth(),1);
let coachCalendarRemindersV259=[];
let coachCalendarCheckinsV259=[];
let coachCalendarLoadedAtV259=0;
let coachCalendarInflightV259=null;

function pad2V259(v){return String(v).padStart(2,'0')}
function dateKeyV259(d){
  return d.getFullYear()+'-'+pad2V259(d.getMonth()+1)+'-'+pad2V259(d.getDate());
}
function startOfDayV259(d){
  return new Date(d.getFullYear(),d.getMonth(),d.getDate());
}
function addDaysV259(d,n){
  const out=new Date(d.getTime());out.setDate(out.getDate()+Number(n||0));return out;
}
function parseDateKeyV259(v){
  const m=String(v||'').match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if(!m)return null;
  const d=new Date(Number(m[1]),Number(m[2])-1,Number(m[3]));
  return Number.isNaN(d.getTime())?null:d;
}
function monthTitleV259(d){
  const t=new Intl.DateTimeFormat('es-AR',{month:'long',year:'numeric'}).format(d);
  return t.charAt(0).toUpperCase()+t.slice(1);
}
function coachStudentByAthleteIdV259(id){
  return (state.students||[]).find(s=>{
    const a=coachAthleteV235(s);
    return a&&String(a.id)===String(id);
  })||null;
}

function coachPriorityActionV259(s){
  const review=coachReviewLoopStateV238(s);
  const sessionFeedback=pendingSessionFeedbackCountV243(s);
  if(sessionFeedback>0)return {tab:'summary',label:'Responder feedback',status:'Pendiente'};
  const a=coachAthleteV235(s);
  const feed=a?(coachFeedV235||[]).filter(x=>x?.athlete_id===a.id):[];
  const critical=feed.find(x=>x?.severity==='critical')||feed[0]||null;
  if(critical?.kind==='checkin'||critical?.kind==='wellness')return {tab:'tracking',label:'Revisar check-in',status:'Pendiente'};
  if(critical?.kind==='nutrition')return {tab:'nutrition',label:'Revisar nutrición',status:'Pendiente'};
  if(critical?.kind==='exercise_feedback'||critical?.kind==='training')return {tab:'routine',label:'Revisar entrenamiento',status:'Pendiente'};
  if(review.reviewDue)return {tab:'summary',label:'Hacer chequeo',status:'Vencido'};
  if(review.changed)return {tab:'summary',label:'Revisar cambios',status:'Revisar'};
  const o=coachStateV235(s);
  if(o.low||o.inactive||o.review)return {tab:'summary',label:'Abrir seguimiento',status:'Seguimiento'};
  return {tab:'progress',label:'Ver evolución',status:'Al día'};
}
window.coachPriorityActionV259=coachPriorityActionV259;

function reviewEventV259(s){
  const days=coachReviewCadenceDaysV240(s);
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

function reminderEventsForMonthV259(month){
  const y=month.getFullYear(),m=month.getMonth();
  const last=new Date(y,m+1,0).getDate();
  const out=[];
  (coachCalendarRemindersV259||[]).forEach(r=>{
    if(r?.active===false)return;
    const s=coachStudentByAthleteIdV259(r?.athlete_id);
    if(!s)return;
    const title=String(r?.title||'Recordatorio');
    const category=String(r?.category||'').toLowerCase();
    const isCheck=/check[\s-]?in|chequeo/i.test(title)||category==='checkin';
    const push=d=>out.push({
      date:dateKeyV259(d),rawDate:startOfDayV259(d),student:s,
      kind:isCheck?'checkin':'reminder',
      title,time:r?.remind_time?String(r.remind_time).slice(0,5):'',
      overdue:false,tab:isCheck?'tracking':'agenda'
    });

    if(r?.schedule_type==='weekly'){
      const wd=Number(r.weekday);
      if(!Number.isInteger(wd)||wd<0||wd>6)return;
      for(let day=1;day<=last;day++){
        const d=new Date(y,m,day);
        if(d.getDay()===wd)push(d);
      }
    }else{
      const d=parseDateKeyV259(r?.reminder_date);
      if(d&&d.getFullYear()===y&&d.getMonth()===m)push(d);
    }
  });
  return out;
}

function checkinScheduleEventsV259(month){
  const y=month.getFullYear(),m=month.getMonth();
  const today=startOfDayV259(new Date());
  return (coachCalendarCheckinsV259||[]).map(row=>{
    const s=coachStudentByAthleteIdV259(row?.athlete_id);
    const due=parseDateKeyV259(row?.next_due);
    if(!s||!due||due.getFullYear()!==y||due.getMonth()!==m||row?.active===false)return null;
    const cadenceMap={once:'Único',weekly:'Semanal',biweekly:'Quincenal',monthly:'Mensual'};
    return {
      date:dateKeyV259(due),
      rawDate:startOfDayV259(due),
      student:s,
      kind:'checkin',
      title:'Check-in programado · '+(cadenceMap[row?.cadence]||'Programado'),
      time:row?.remind_time?String(row.remind_time).slice(0,5):'',
      overdue:startOfDayV259(due)<today,
      tab:'tracking'
    };
  }).filter(Boolean);
}

function calendarEventsV259(month=coachCalendarMonthV259){
  const reviews=(state.students||[]).map(reviewEventV259);
  const reminders=reminderEventsForMonthV259(month);
  const checkins=checkinScheduleEventsV259(month);
  return [...reviews,...checkins,...reminders];
}

function eventToneV259(e){
  if(e.overdue)return 'overdue';
  if(e.kind==='checkin')return 'checkin';
  if(e.kind==='reminder')return 'reminder';
  return 'review';
}

function openCoachCalendarEventV259(studentId,tab){
  openCoachStudentTabV235(studentId,tab||'summary');
}
window.openCoachCalendarEventV259=openCoachCalendarEventV259;

function calendarCellEventsV259(events,key){
  return events.filter(x=>x.date===key).sort((a,b)=>{
    if(a.overdue!==b.overdue)return a.overdue?-1:1;
    return String(a.time||'').localeCompare(String(b.time||''));
  });
}

function calendarUpcomingV259(events){
  const today=startOfDayV259(new Date()),limit=addDaysV259(today,14);
  return events
    .filter(e=>{
      const d=e.rawDate;
      return e.kind==='review'?(d<=limit):(d>=today&&d<=limit);
    })
    .sort((a,b)=>{
      if(a.overdue!==b.overdue)return a.overdue?-1:1;
      return a.rawDate-b.rawDate||String(a.student?.name||'').localeCompare(String(b.student?.name||''));
    })
    .slice(0,8);
}

function calendarEventChipV259(e){
  return '<button class="v259-event '+eventToneV259(e)+'" type="button" title="'+esc(e.title+' · '+(e.student?.name||'Alumno'))+'" '+
    'onclick="openCoachCalendarEventV259(\''+esc(e.student.id)+'\',\''+esc(e.tab)+'\')">'+
    '<span>'+esc((e.student?.name||'A').split(' ')[0])+'</span>'+
  '</button>';
}

function renderCoachCalendarV259(){
  const host=el('v259CoachCalendar');if(!host)return;
  const month=coachCalendarMonthV259;
  const y=month.getFullYear(),m=month.getMonth();
  const first=new Date(y,m,1);
  const lastDay=new Date(y,m+1,0).getDate();
  const mondayOffset=(first.getDay()+6)%7;
  const events=calendarEventsV259(month);
  const todayKey=dateKeyV259(new Date());
  const cells=[];

  for(let i=0;i<mondayOffset;i++)cells.push('<div class="v259-day muted-day"></div>');
  for(let day=1;day<=lastDay;day++){
    const d=new Date(y,m,day),key=dateKeyV259(d);
    const rows=calendarCellEventsV259(events,key);
    cells.push(
      '<div class="v259-day '+(key===todayKey?'today':'')+'">'+
        '<div class="v259-day-num">'+day+'</div>'+
        '<div class="v259-day-events">'+rows.slice(0,3).map(calendarEventChipV259).join('')+
          (rows.length>3?'<span class="v259-more">+'+(rows.length-3)+'</span>':'')+
        '</div>'+
      '</div>'
    );
  }

  const reviewEvents=(state.students||[]).map(reviewEventV259);
  const today=startOfDayV259(new Date()),weekEnd=addDaysV259(today,7);
  const currentMonth=new Date(today.getFullYear(),today.getMonth(),1);
  const nextMonth=new Date(today.getFullYear(),today.getMonth()+1,1);
  const checkinCurrent=checkinScheduleEventsV259(currentMonth);
  const checkinNext=checkinScheduleEventsV259(nextMonth);
  const reminderCurrent=reminderEventsForMonthV259(currentMonth);
  const reminderNext=reminderEventsForMonthV259(nextMonth);
  const dueEvents=[...reviewEvents,...checkinCurrent,...checkinNext];
  const overdue=dueEvents.filter(x=>x.overdue).length;
  const week=dueEvents.filter(x=>!x.overdue&&x.rawDate>=today&&x.rawDate<=weekEnd).length;
  const upcoming=calendarUpcomingV259([...dueEvents,...reminderCurrent,...reminderNext]);
  const days=['Lun','Mar','Mié','Jue','Vie','Sáb','Dom'];

  host.innerHTML=
    '<div class="v259-calendar-head">'+
      '<div><div class="v225-section-kicker">CALENDARIO DEL COACH</div><h3>Chequeos y seguimiento</h3>'+
      '<p>Revisiones por frecuencia + recordatorios sincronizados de Agenda.</p></div>'+
      '<div class="v259-calendar-nav">'+
        '<button class="btn small" type="button" onclick="shiftCoachCalendarV259(-1)">‹</button>'+
        '<button class="btn small" type="button" onclick="goTodayCoachCalendarV259()">'+esc(monthTitleV259(month))+'</button>'+
        '<button class="btn small" type="button" onclick="shiftCoachCalendarV259(1)">›</button>'+
      '</div>'+
    '</div>'+
    '<div class="v259-calendar-stats">'+
      '<div class="'+(overdue?'warn':'')+'"><strong>'+overdue+'</strong><span>Vencidos</span></div>'+
      '<div><strong>'+week+'</strong><span>Próx. 7 días</span></div>'+
      '<div><strong>'+(coachCalendarCheckinsV259||[]).length+'</strong><span>Check-ins</span></div>'+
      '<div><strong>'+(coachCalendarRemindersV259||[]).length+'</strong><span>Recordatorios</span></div>'+
    '</div>'+
    '<div class="v259-calendar-layout">'+
      '<div class="v259-month">'+
        '<div class="v259-weekdays">'+days.map(x=>'<span>'+x+'</span>').join('')+'</div>'+
        '<div class="v259-days">'+cells.join('')+'</div>'+
        '<div class="v259-legend"><span><i class="review"></i>Chequeo</span><span><i class="checkin"></i>Check-in</span><span><i class="reminder"></i>Agenda</span><span><i class="overdue"></i>Vencido</span></div>'+
      '</div>'+
      '<aside class="v259-upcoming">'+
        '<div class="v259-upcoming-head"><strong>Próximo</strong><span>14 días</span></div>'+
        (upcoming.length?upcoming.map(e=>
          '<button type="button" class="v259-upcoming-row '+eventToneV259(e)+'" onclick="openCoachCalendarEventV259(\''+esc(e.student.id)+'\',\''+esc(e.tab)+'\')">'+
            '<span class="v259-up-date">'+(e.overdue?'Vencido':new Intl.DateTimeFormat('es-AR',{day:'2-digit',month:'short'}).format(e.rawDate))+'</span>'+
            '<span class="v259-up-copy"><strong>'+esc(e.student.name||'Alumno')+'</strong><small>'+esc(e.title+(e.time?' · '+e.time:''))+'</small></span>'+
            '<span>›</span>'+
          '</button>'
        ).join(''):'<div class="v259-empty">Sin chequeos próximos.</div>')+
      '</aside>'+
    '</div>';
}

window.shiftCoachCalendarV259=function(delta){
  coachCalendarMonthV259=new Date(
    coachCalendarMonthV259.getFullYear(),
    coachCalendarMonthV259.getMonth()+Number(delta||0),
    1
  );
  renderCoachCalendarV259();
};
window.goTodayCoachCalendarV259=function(){
  const d=new Date();
  coachCalendarMonthV259=new Date(d.getFullYear(),d.getMonth(),1);
  renderCoachCalendarV259();
};

async function loadCoachCalendarV259(force=false){
  if(!cloudEnabled||!supabaseClient||window.__fjzStagingLocal?.enabled){
    coachCalendarRemindersV259=Array.isArray(agendaRemindersV81)?agendaRemindersV81.slice():[];
    coachCalendarCheckinsV259=[];
    renderCoachCalendarV259();
    return {reminders:coachCalendarRemindersV259,checkins:coachCalendarCheckinsV259};
  }
  const fresh=coachCalendarLoadedAtV259&&Date.now()-coachCalendarLoadedAtV259<30000;
  if(!force&&fresh)return coachCalendarRemindersV259;
  if(coachCalendarInflightV259)return coachCalendarInflightV259;

  coachCalendarInflightV259=(async()=>{
    const [reminderRes,checkinRes]=await Promise.all([
      supabaseClient.from('athlete_reminders')
        .select('id,athlete_id,coach_id,title,body,category,schedule_type,reminder_date,weekday,remind_time,active,created_at')
        .eq('coach_id',currentUser.id)
        .eq('active',true),
      supabaseClient.from('checkin_schedules')
        .select('id,athlete_id,coach_id,cadence,next_due,remind_time,active,notes,last_completed_at,updated_at')
        .eq('coach_id',currentUser.id)
        .eq('active',true)
    ]);
    if(reminderRes.error)throw reminderRes.error;
    if(checkinRes.error)throw checkinRes.error;
    coachCalendarRemindersV259=Array.isArray(reminderRes.data)?reminderRes.data:[];
    coachCalendarCheckinsV259=Array.isArray(checkinRes.data)?checkinRes.data:[];
    coachCalendarLoadedAtV259=Date.now();
    renderCoachCalendarV259();
    return {reminders:coachCalendarRemindersV259,checkins:coachCalendarCheckinsV259};
  })().catch(()=>{
    coachCalendarRemindersV259=Array.isArray(agendaRemindersV81)?agendaRemindersV81.slice():coachCalendarRemindersV259;
    renderCoachCalendarV259();
    return {reminders:coachCalendarRemindersV259,checkins:coachCalendarCheckinsV259};
  }).finally(()=>{coachCalendarInflightV259=null});

  return coachCalendarInflightV259;
}
window.loadCoachCalendarV259=loadCoachCalendarV259;

function hydrateCoachCalendarV259(){
  const host=el('v259CoachCalendar');if(!host)return;
  const force=(typeof agendaLoadedV81!=='undefined'&&agendaLoadedV81===false)||
    (typeof followupLoadedV122!=='undefined'&&followupLoadedV122===false);
  loadCoachCalendarV259(force);
}
window.hydrateCoachCalendarV259=hydrateCoachCalendarV259;
"""
html=html.replace(anchor,helpers+"\n"+anchor,1)

# Upgrade priority-row rendering with explicit status + action.
start=html.find("function priorityPersonV252(item){")
end=html.find("\nfunction renderCoachPriorityCenterV252(){",start)
if start<0 or end<0:
    raise RuntimeError("V20.59 priority row function scope missing")

priority_fn=r"""function priorityPersonV252(item){
  const s=item.s;
  const action=coachPriorityActionV259(s);
  const statusClass=action.status==='Vencido'||action.status==='Pendiente'?'warn':
    action.status==='Al día'?'ok':'watch';
  return '<div class="v259-priority-row">'+
    '<button class="v259-priority-person" type="button" onclick="openCoachStudentTabV235(\''+esc(s.id)+'\',\''+esc(action.tab)+'\')">'+
      '<span class="v252-avatar">'+esc((s.name||'A').slice(0,2).toUpperCase())+'</span>'+
      '<span class="v252-copy"><strong>'+esc(s.name||'Alumno')+'</strong><small>'+esc(item.label||'Seguimiento')+'</small></span>'+
    '</button>'+
    '<span class="v259-action-status '+statusClass+'">'+esc(action.status)+'</span>'+
    '<button class="btn small '+(statusClass==='warn'?'primary':'')+'" type="button" onclick="openCoachStudentTabV235(\''+esc(s.id)+'\',\''+esc(action.tab)+'\')">'+esc(action.label)+'</button>'+
  '</div>';
}
"""
html=html[:start]+priority_fn+html[end:]

# Priority render also refreshes calendar and its cache.
render_anchor="""    '<div class="v252-columns">'+
      column('Urgente','urgent',urgent,'Sin urgencias ahora')+
      column('Hoy','today',today,'Nada pendiente para hoy')+
      column('Seguimiento','watch',watch,'Sin alumnos en seguimiento')+
    '</div>';
}"""
render_repl="""    '<div class="v252-columns">'+
      column('Urgente','urgent',urgent,'Sin urgencias ahora')+
      column('Hoy','today',today,'Nada pendiente para hoy')+
      column('Seguimiento','watch',watch,'Sin alumnos en seguimiento')+
    '</div>';
  renderCoachCalendarV259();
  hydrateCoachCalendarV259();
}"""
if html.count(render_anchor)!=1:
    raise RuntimeError("V20.59 priority render refresh anchor mismatch")
html=html.replace(render_anchor,render_repl,1)

# Insert calendar between priorities and the main dashboard grid.
insert_anchor="""  <section class="card v252-priority-card" id="v252PriorityCenter">
    <div class="empty">Preparando prioridades…</div>
  </section>

  <div class="grid v225-dashboard-grid">"""
insert_repl="""  <section class="card v252-priority-card" id="v252PriorityCenter">
    <div class="empty">Preparando prioridades…</div>
  </section>

  <section class="card v259-calendar-card" id="v259CoachCalendar">
    <div class="empty">Preparando calendario de chequeos…</div>
  </section>

  <div class="grid v225-dashboard-grid">"""
if html.count(insert_anchor)!=1:
    raise RuntimeError("V20.59 calendar insertion anchor mismatch")
html=html.replace(insert_anchor,insert_repl,1)

css=r"""
/* TEAM FJZ · V20.59 COACH ACTION CENTER 2.0 + CALENDAR */
.v259-priority-row{
  display:grid;
  grid-template-columns:minmax(0,1fr) auto auto;
  gap:7px;
  align-items:center;
  padding:7px 8px;
  border-bottom:1px solid #24272e;
}
.v259-priority-row:last-child{border-bottom:0}
.v259-priority-person{
  appearance:none;border:0;background:transparent;color:inherit;text-align:left;cursor:pointer;
  min-width:0;display:grid;grid-template-columns:32px minmax(0,1fr);gap:8px;align-items:center;padding:2px
}
.v259-action-status{
  padding:4px 6px;border:1px solid #343842;border-radius:999px;
  color:#a7acb5;font-size:7px;font-weight:900;white-space:nowrap
}
.v259-action-status.warn{color:#f5c775;border-color:rgba(242,189,85,.28);background:rgba(242,189,85,.06)}
.v259-action-status.ok{color:#8fdcaf;border-color:rgba(59,213,138,.25);background:rgba(59,213,138,.05)}
.v259-action-status.watch{color:#91c1fa;border-color:rgba(103,173,255,.25);background:rgba(103,173,255,.05)}

.v259-calendar-card{
  margin:0 0 14px;
  border-color:#30343c;
  background:linear-gradient(145deg,rgba(103,173,255,.035),transparent 46%),var(--card);
}
.v259-calendar-head{
  display:flex;justify-content:space-between;gap:14px;align-items:flex-start;margin-bottom:10px
}
.v259-calendar-head h3{margin:4px 0 0;color:#f5f6f8;font-size:16px;font-weight:920;letter-spacing:-.02em}
.v259-calendar-head p{margin:5px 0 0;color:#959aa4;font-size:9px;line-height:1.45}
.v259-calendar-nav{display:flex;gap:6px;align-items:center}
.v259-calendar-stats{
  display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px;margin-bottom:9px
}
.v259-calendar-stats>div{
  padding:9px 10px;border:1px solid #2b2f37;border-radius:10px;background:#0d0e12
}
.v259-calendar-stats strong{display:block;color:#f5f6f8;font-size:17px;font-weight:920}
.v259-calendar-stats span{display:block;margin-top:3px;color:#858b96;font-size:8px;font-weight:800;text-transform:uppercase;letter-spacing:.05em}
.v259-calendar-stats .warn{border-color:rgba(242,189,85,.26)}
.v259-calendar-stats .warn strong{color:#f2c66c}
.v259-calendar-layout{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(220px,.65fr);gap:10px}
.v259-month,.v259-upcoming{min-width:0;border:1px solid #2b2f37;border-radius:11px;background:#0d0e12;overflow:hidden}
.v259-weekdays{display:grid;grid-template-columns:repeat(7,1fr);border-bottom:1px solid #282c33;background:#111319}
.v259-weekdays span{padding:7px 3px;color:#808691;font-size:7px;font-weight:900;text-align:center;text-transform:uppercase}
.v259-days{display:grid;grid-template-columns:repeat(7,1fr)}
.v259-day{min-width:0;min-height:78px;padding:5px;border-right:1px solid #23262d;border-bottom:1px solid #23262d;background:#0d0e12}
.v259-day:nth-child(7n){border-right:0}
.v259-day.muted-day{background:#0a0b0e}
.v259-day.today{box-shadow:inset 0 0 0 1px rgba(103,173,255,.38);background:rgba(103,173,255,.025)}
.v259-day-num{color:#8d929c;font-size:8px;font-weight:900}
.v259-day.today .v259-day-num{color:#9ac7ff}
.v259-day-events{display:grid;gap:3px;margin-top:5px}
.v259-event{
  width:100%;min-width:0;padding:3px 4px;border:0;border-left:2px solid #67adff;border-radius:0 5px 5px 0;
  background:#151922;color:#bec7d3;font-size:7px;text-align:left;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:pointer
}
.v259-event.checkin{border-left-color:#3bd58a;background:rgba(59,213,138,.07);color:#a9e6c3}
.v259-event.reminder{border-left-color:#9b88ff;background:rgba(155,136,255,.07);color:#c9c0ff}
.v259-event.overdue{border-left-color:#f2bd55;background:rgba(242,189,85,.08);color:#f0cc86}
.v259-more{color:#747b86;font-size:7px;padding-left:3px}
.v259-legend{display:flex;gap:10px;flex-wrap:wrap;padding:7px 8px;border-top:1px solid #282c33}
.v259-legend span{display:flex;align-items:center;gap:4px;color:#7d838e;font-size:7px}
.v259-legend i{width:7px;height:7px;border-radius:2px;background:#67adff}
.v259-legend i.checkin{background:#3bd58a}.v259-legend i.reminder{background:#9b88ff}.v259-legend i.overdue{background:#f2bd55}
.v259-upcoming-head{display:flex;justify-content:space-between;padding:9px 10px;border-bottom:1px solid #282c33}
.v259-upcoming-head strong{color:#e8eaee;font-size:9px}.v259-upcoming-head span{color:#777e89;font-size:8px}
.v259-upcoming-row{
  width:100%;display:grid;grid-template-columns:54px minmax(0,1fr) auto;gap:8px;align-items:center;
  padding:8px 9px;border:0;border-bottom:1px solid #24272e;background:transparent;color:inherit;text-align:left;cursor:pointer
}
.v259-upcoming-row:last-child{border-bottom:0}.v259-upcoming-row:hover{background:#121419}
.v259-upcoming-row>span:last-child{color:#666d78;font-size:16px}
.v259-up-date{color:#8d949f;font-size:8px;font-weight:850}
.v259-upcoming-row.overdue .v259-up-date{color:#efc978}
.v259-up-copy{min-width:0}.v259-up-copy strong{display:block;color:#e8eaed;font-size:9px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.v259-up-copy small{display:block;margin-top:3px;color:#818793;font-size:7px;line-height:1.35;overflow-wrap:anywhere}
.v259-empty{padding:18px 10px;color:#737a85;font-size:8px;text-align:center}
@media(max-width:880px){
  .v259-calendar-layout{grid-template-columns:1fr}
}
@media(max-width:680px){
  .v259-priority-row{grid-template-columns:minmax(0,1fr) auto}
  .v259-priority-row>.btn{grid-column:1/-1;width:100%}
  .v259-calendar-head{display:grid}
  .v259-calendar-nav{justify-content:space-between}
  .v259-calendar-nav .btn:nth-child(2){flex:1}
  .v259-day{min-height:62px;padding:4px}
  .v259-event{font-size:0;height:8px;padding:0;border-left:0;border-radius:999px;background:#67adff}
  .v259-event.checkin{background:#3bd58a}.v259-event.reminder{background:#9b88ff}.v259-event.overdue{background:#f2bd55}
}
@media(max-width:480px){
  .v259-calendar-stats{grid-template-columns:1fr 1fr}
  .v259-calendar-stats>div{padding:7px}
  .v259-calendar-stats strong{font-size:14px}
  .v259-day{min-height:54px}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.59 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-coach-action-calendar" content="20.59">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.59 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-coach-action-calendar" content="20.59"',
    "coachPriorityActionV259","renderCoachCalendarV259","loadCoachCalendarV259",
    "CALENDARIO DEL COACH","Chequeos y seguimiento",
    "coachCalendarRemindersV259","coachCalendarCheckinsV259",
    "athlete_reminders","checkin_schedules","next_due",
    "Hacer chequeo","Responder feedback","Revisar check-in"
]:
    if marker not in html:
        raise RuntimeError("V20.59 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.59 coach action center 2.0 + calendar")
print("V20.59 BEFORE:",before)
print("V20.59 AFTER:",after)
print("V20.59 review cadence + agenda reminders rendered in one coach calendar without new timers/listeners/channels")
