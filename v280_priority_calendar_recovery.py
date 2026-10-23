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
    'id="v175ProfileAgendaCoachCenterRuntime"',
]:
    if marker not in html:
        raise RuntimeError("V20.80 prerequisite missing "+marker)

# Remove stale calls to the V20.59 calendar authority if they survived inside
# the historical priority renderer.
html=html.replace("  renderCoachCalendarV259();\n  hydrateCoachCalendarV259();\n}","}",1)
html=html.replace("  renderCoachCalendarV259();\n}","}",1)

# Canonical post-render hook; V20.80 owns both operational surfaces.
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
/* =========================================================
   TEAM FJZ · V20.80 PRIORITY + CALENDAR RECOVERY
   ========================================================= */
.v280-priority-head,.v280-calendar-head{
  display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:10px
}
.v280-priority-head h3,.v280-calendar-head h3{margin:4px 0 0;font-size:16px;color:#f5f6f8}
.v280-priority-head p,.v280-calendar-head p{margin:5px 0 0;color:#959aa4;font-size:9px;line-height:1.45}
.v280-priority-columns{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.v280-priority-column{min-width:0;border:1px solid #2c3038;border-top:3px solid #67adff;border-radius:0 11px 11px 11px;background:#0d0e12;overflow:hidden}
.v280-priority-column.urgent{border-top-color:#ff5262}.v280-priority-column.today{border-top-color:#f2bd55}
.v280-priority-column-head{display:flex;justify-content:space-between;align-items:center;padding:8px 9px;border-bottom:1px solid #252931}
.v280-priority-column-head strong{font-size:9px;color:#eef0f3}.v280-priority-column-head span{font-size:7px;color:#8c939d}
.v280-priority-row{appearance:none;width:100%;min-width:0;display:grid;grid-template-columns:30px minmax(0,1fr) auto;gap:8px;align-items:center;padding:8px 9px;border:0;border-bottom:1px solid #23262d;background:transparent;color:inherit;text-align:left}
.v280-priority-row:last-child{border-bottom:0}.v280-priority-avatar{width:30px;height:30px;display:grid;place-items:center;border:1px solid #343842;border-radius:8px;background:#15171c;color:#f1f3f5;font-size:8px;font-weight:900}
.v280-priority-copy{min-width:0}.v280-priority-copy strong{display:block;color:#eef0f3;font-size:9px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.v280-priority-copy small{display:block;margin-top:3px;color:#858c96;font-size:7px;line-height:1.35;overflow-wrap:anywhere}.v280-priority-arrow{color:#717884;font-size:15px}
.v280-empty{padding:13px;color:#747b86;font-size:8px;text-align:center}
.v280-calendar-card{margin:0 0 14px;min-width:0;max-width:100%;overflow:hidden;border-color:#30343c;background:linear-gradient(145deg,rgba(103,173,255,.035),transparent 46%),var(--card)}
.v280-calendar-nav{display:flex;align-items:center;gap:6px}
.v280-calendar-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:7px;margin-bottom:9px}
.v280-calendar-stats>div{min-width:0;padding:9px 10px;border:1px solid #2b2f37;border-radius:10px;background:#0d0e12}
.v280-calendar-stats strong{display:block;color:#f5f6f8;font-size:17px}.v280-calendar-stats span{display:block;margin-top:3px;color:#858c96;font-size:7px}
.v280-calendar-layout{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(190px,.65fr);gap:9px;min-width:0}
.v280-month,.v280-upcoming{min-width:0;overflow:hidden;border:1px solid #2c3038;border-radius:11px;background:#0d0e12}
.v280-weekdays,.v280-days{display:grid;grid-template-columns:repeat(7,minmax(0,1fr))}
.v280-weekdays{border-bottom:1px solid #252931;background:#101218}.v280-weekdays span{padding:7px 3px;color:#7f8791;font-size:6.5px;font-weight:900;text-align:center}
.v280-day{min-width:0;min-height:67px;padding:6px;border-right:1px solid #23262d;border-bottom:1px solid #23262d}.v280-day:nth-child(7n){border-right:0}.v280-day.muted{opacity:.22}.v280-day.today{box-shadow:inset 0 0 0 1px rgba(103,173,255,.55)}
.v280-day-num{color:#858c96;font-size:7px;font-weight:900}.v280-events{display:grid;gap:3px;margin-top:5px}
.v280-event{appearance:none;width:100%;min-width:0;padding:4px 5px;border:0;border-left:2px solid #67adff;border-radius:5px;background:#13161c;color:#dfe3e8;font-size:6.5px;text-align:left;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.v280-event.overdue{border-left-color:#ff5262}.v280-event.reminder{border-left-color:#f2bd55}
.v280-upcoming-head{display:flex;justify-content:space-between;gap:8px;padding:9px 10px;border-bottom:1px solid #252931}.v280-upcoming-head strong{font-size:9px;color:#eef0f3}.v280-upcoming-head span{font-size:7px;color:#818893}
.v280-upcoming-list{display:grid}.v280-upcoming-row{appearance:none;width:100%;min-width:0;display:grid;grid-template-columns:52px minmax(0,1fr) auto;gap:7px;align-items:center;padding:8px 9px;border:0;border-bottom:1px solid #23262d;background:transparent;color:inherit;text-align:left}.v280-upcoming-row:last-child{border-bottom:0}.v280-upcoming-row>span:first-child{font-size:6.5px;color:#8d949e}.v280-upcoming-row strong{display:block;font-size:8px;color:#eceef1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.v280-upcoming-row small{display:block;margin-top:2px;font-size:6.5px;color:#818893;overflow-wrap:anywhere}
@media(max-width:760px){.v280-priority-columns,.v280-calendar-layout{grid-template-columns:1fr}}
@media(max-width:430px){.v280-priority-head,.v280-calendar-head{display:grid}.v280-calendar-nav{width:100%;display:grid;grid-template-columns:auto minmax(0,1fr) auto}.v280-calendar-nav .btn{min-width:0}.v280-calendar-stats{grid-template-columns:1fr 1fr}.v280-calendar-stats>div:last-child{grid-column:1/-1}.v280-day{min-height:55px;padding:4px}.v280-weekdays span{font-size:6px;padding:6px 1px}.v280-event{font-size:6px;padding:3px}}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.80 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

runtime=r"""
<script id="v280OperationalRecoveryRuntime">
(function(){
  let monthV280=new Date(new Date().getFullYear(),new Date().getMonth(),1);
  let remindersV280=[],checkinsV280=[],loadedAtV280=0,inflightV280=null,hydratingV280=false;
  const DAY=86400000,pad=n=>String(n).padStart(2,'0');
  const key=d=>d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate());
  const startDay=d=>new Date(d.getFullYear(),d.getMonth(),d.getDate());
  const addDays=(d,n)=>{const x=new Date(d);x.setDate(x.getDate()+Number(n||0));return x};
  const parse=v=>{const m=String(v||'').match(/^(\d{4})-(\d{2})-(\d{2})$/);if(!m)return null;const d=new Date(+m[1],+m[2]-1,+m[3]);return Number.isNaN(d.getTime())?null:d};
  const monthTitle=d=>{const s=new Intl.DateTimeFormat('es-AR',{month:'long',year:'numeric'}).format(d);return s.charAt(0).toUpperCase()+s.slice(1)};
  const students=()=>Array.isArray(state?.students)?state.students:[];
  const daysSince=v=>{const t=Date.parse(v||0);return t?Math.max(0,Math.floor((Date.now()-t)/DAY)):999};

  function athleteFor(s){try{return cloudAthletes?.get?.(s?.id)||null}catch(_e){return null}}
  function feedFor(s){
    try{const a=athleteFor(s),f=Array.isArray(coachFeedV235)?coachFeedV235:[];return a?f.filter(x=>x?.athlete_id===a.id):[]}catch(_e){return []}
  }
  function priorityState(s){
    const feed=feedFor(s);
    const critical=feed.filter(x=>x?.severity==='critical').length;
    let pendingFeedback=0;
    try{if(typeof pendingSessionFeedbackCountV243==='function')pendingFeedback=Number(pendingSessionFeedbackCountV243(s)||0)}catch(_e){}
    let reviewDue=false,changed=false;
    try{if(typeof coachReviewLoopStateV238==='function'){const r=coachReviewLoopStateV238(s)||{};reviewDue=!!r.reviewDue;changed=!!r.changed}}catch(_e){}
    const adh=Number(typeof adherence==='function'?adherence(s):0)||0;
    const inactive=daysSince(s?.lastWorkout);
    const needsReview=(()=>{try{return typeof statusFor==='function'&&statusFor(s)==='Revisar'}catch(_e){return false}})();
    if(critical>0||pendingFeedback>0)return {bucket:'urgent',score:100+critical*20+pendingFeedback*12,label:pendingFeedback?pendingFeedback+' feedback pendiente':critical+' señal crítica'};
    if(reviewDue||changed||needsReview||adh<70||inactive>=7||feed.length>0){
      const bits=[];if(reviewDue)bits.push('revisión vencida');if(changed)bits.push('cambios nuevos');if(adh<70)bits.push('adherencia '+adh+'%');if(inactive>=7&&inactive<999)bits.push(inactive+' días sin entrenar');if(feed.length)bits.push(feed.length+' alertas');
      return {bucket:'today',score:50+feed.length*3+(reviewDue?8:0)+(adh<70?4:0),label:bits.slice(0,2).join(' · ')||'Revisar seguimiento'};
    }
    return {bucket:'watch',score:0,label:'Seguimiento al día'};
  }
  function priorityTab(s){
    const f=feedFor(s),x=f.find(v=>v?.severity==='critical')||f[0];
    if(x?.kind==='nutrition')return 'nutrition';
    if(x?.kind==='checkin'||x?.kind==='wellness')return 'tracking';
    if(x?.kind==='exercise_feedback'||x?.kind==='training')return 'routine';
    if(x?.kind==='progression')return 'progress';
    return 'summary';
  }
  function priorityRows(bucket){
    return students().map(s=>{try{return {s,...priorityState(s)}}catch(e){console.warn('TEAM FJZ V20.80 priority row',s?.id,e);return {s,bucket:'watch',score:0,label:'Seguimiento disponible'}}})
      .filter(x=>x.bucket===bucket).sort((a,b)=>b.score-a.score||String(a.s?.name||'').localeCompare(String(b.s?.name||'')));
  }
  function openStudent(id,tab){if(typeof openCoachStudentTabV235==='function')return openCoachStudentTabV235(id,tab||'summary');state.selectedStudentId=id;coachTab='student';coachStudentTab=tab||'summary';saveState?.();render?.()}
  function renderPriority(){
    const host=el('v252PriorityCenter');if(!host)return;
    const urgent=priorityRows('urgent'),today=priorityRows('today'),watch=priorityRows('watch');
    const row=x=>'<button class="v280-priority-row" onclick="window.__fjzOpenPriorityV280(\''+esc(x.s.id)+'\',\''+esc(priorityTab(x.s))+'\')"><span class="v280-priority-avatar">'+esc((x.s.name||'A').slice(0,2).toUpperCase())+'</span><span class="v280-priority-copy"><strong>'+esc(x.s.name||'Alumno')+'</strong><small>'+esc(x.label||'Seguimiento')+'</small></span><span class="v280-priority-arrow">›</span></button>';
    const col=(title,cls,rows,empty)=>'<div class="v280-priority-column '+cls+'"><div class="v280-priority-column-head"><strong>'+title+'</strong><span>'+rows.length+'</span></div>'+(rows.length?rows.slice(0,5).map(row).join(''):'<div class="v280-empty">'+empty+'</div>')+'</div>';
    host.innerHTML='<div class="v280-priority-head"><div><div class="v225-section-kicker">CENTRO DE PRIORIDADES</div><h3>Qué necesita atención ahora</h3><p>Señales operativas calculadas sin depender de helpers históricos.</p></div></div><div class="v280-priority-columns">'+col('Urgente','urgent',urgent,'Sin urgencias ahora')+col('Hoy','today',today,'Nada pendiente para hoy')+col('Seguimiento','watch',watch,'Sin alumnos en seguimiento')+'</div>';
  }

  function cadenceDays(s){try{if(typeof coachReviewCadenceDaysV240==='function'){const n=Number(coachReviewCadenceDaysV240(s));if(Number.isFinite(n)&&n>0)return n}}catch(_e){}return 14}
  function reviewEvent(s){const today=startDay(new Date()),reviewed=s?.coachReviewV237?.reviewedAt||null;let due=today;if(reviewed){const d=new Date(reviewed);if(!Number.isNaN(d.getTime()))due=startDay(addDays(d,cadenceDays(s)))}return {date:key(due),raw:due,student:s,kind:'review',title:reviewed?'Chequeo / revisión':'Primer chequeo',overdue:due<today,tab:'summary'}}
  function studentByAthlete(aid){try{for(const s of students()){const a=athleteFor(s);if(a&&String(a.id)===String(aid))return s}}catch(_e){}return null}
  function remoteEvents(month){const y=month.getFullYear(),m=month.getMonth(),out=[];remindersV280.forEach(r=>{if(r?.active===false)return;const s=studentByAthlete(r?.athlete_id);if(!s)return;const push=d=>out.push({date:key(d),raw:startDay(d),student:s,kind:'reminder',title:String(r?.title||'Recordatorio'),overdue:false,tab:'agenda'});if(r?.schedule_type==='weekly'){const wd=Number(r.weekday);if(!Number.isInteger(wd))return;const last=new Date(y,m+1,0).getDate();for(let day=1;day<=last;day++){const d=new Date(y,m,day);if(d.getDay()===wd)push(d)}}else{const d=parse(r?.reminder_date);if(d&&d.getFullYear()===y&&d.getMonth()===m)push(d)}});checkinsV280.forEach(r=>{if(r?.active===false)return;const s=studentByAthlete(r?.athlete_id),d=parse(r?.next_due);if(!s||!d||d.getFullYear()!==y||d.getMonth()!==m)return;out.push({date:key(d),raw:startDay(d),student:s,kind:'checkin',title:'Check-in programado',overdue:startDay(d)<startDay(new Date()),tab:'tracking'})});return out}
  const events=(month=monthV280)=>[...students().map(reviewEvent),...remoteEvents(month)];
  function ensureCalendarHost(){let host=el('v259CoachCalendar');if(host)return host;const priority=el('v252PriorityCenter');if(!priority?.parentNode)return null;host=document.createElement('section');host.id='v259CoachCalendar';host.className='card v280-calendar-card';priority.insertAdjacentElement('afterend',host);return host}
  function renderCalendar(){
    const host=ensureCalendarHost();if(!host)return;host.classList.add('v280-calendar-card');
    const y=monthV280.getFullYear(),m=monthV280.getMonth(),first=new Date(y,m,1),last=new Date(y,m+1,0).getDate(),offset=(first.getDay()+6)%7,rows=events(monthV280),todayKey=key(new Date()),cells=[];
    for(let i=0;i<offset;i++)cells.push('<div class="v280-day muted"></div>');
    for(let day=1;day<=last;day++){const d=new Date(y,m,day),k=key(d),es=rows.filter(x=>x.date===k).slice(0,3);cells.push('<div class="v280-day '+(k===todayKey?'today':'')+'"><div class="v280-day-num">'+day+'</div><div class="v280-events">'+es.map(e=>'<button class="v280-event '+(e.overdue?'overdue ':e.kind==='reminder'?'reminder ':'')+'" onclick="window.__fjzOpenPriorityV280(\''+esc(e.student.id)+'\',\''+esc(e.tab||'summary')+'\')">'+esc((e.student.name||'Alumno').split(' ')[0])+'</button>').join('')+'</div></div>')}
    const today=startDay(new Date()),limit=addDays(today,14),all=[...students().map(reviewEvent),...remoteEvents(new Date(today.getFullYear(),today.getMonth(),1)),...remoteEvents(new Date(today.getFullYear(),today.getMonth()+1,1))],upcoming=all.filter(e=>e.kind==='review'?e.raw<=limit:(e.raw>=today&&e.raw<=limit)).sort((a,b)=>(a.overdue===b.overdue?0:a.overdue?-1:1)||a.raw-b.raw).slice(0,8),overdue=students().map(reviewEvent).filter(e=>e.overdue).length,week=students().map(reviewEvent).filter(e=>!e.overdue&&e.raw>=today&&e.raw<=addDays(today,7)).length;
    host.innerHTML='<div class="v280-calendar-head"><div><div class="v225-section-kicker">CALENDARIO DEL COACH</div><h3>Chequeos y seguimiento</h3><p>Revisiones, check-ins y recordatorios en una sola vista.</p></div><div class="v280-calendar-nav"><button class="btn small" onclick="shiftCoachCalendarV280(-1)">‹</button><button class="btn small" onclick="goTodayCoachCalendarV280()">'+esc(monthTitle(monthV280))+'</button><button class="btn small" onclick="shiftCoachCalendarV280(1)">›</button></div></div><div class="v280-calendar-stats"><div><strong>'+overdue+'</strong><span>Vencidos</span></div><div><strong>'+week+'</strong><span>Próx. 7 días</span></div><div><strong>'+students().length+'</strong><span>Alumnos con seguimiento</span></div></div><div class="v280-calendar-layout"><div class="v280-month"><div class="v280-weekdays">'+['Lun','Mar','Mié','Jue','Vie','Sáb','Dom'].map(x=>'<span>'+x+'</span>').join('')+'</div><div class="v280-days">'+cells.join('')+'</div></div><aside class="v280-upcoming"><div class="v280-upcoming-head"><strong>Próximo</strong><span>14 días</span></div><div class="v280-upcoming-list">'+(upcoming.length?upcoming.map(e=>'<button class="v280-upcoming-row" onclick="window.__fjzOpenPriorityV280(\''+esc(e.student.id)+'\',\''+esc(e.tab||'summary')+'\')"><span>'+(e.overdue?'Vencido':new Intl.DateTimeFormat('es-AR',{day:'2-digit',month:'short'}).format(e.raw))+'</span><span><strong>'+esc(e.student.name||'Alumno')+'</strong><small>'+esc(e.title)+'</small></span><span>›</span></button>').join(''):'<div class="v280-empty">Sin chequeos próximos.</div>')+'</div></aside></div>';
  }
  async function loadCalendar(force=false){
    if(!cloudEnabled||!supabaseClient||window.__fjzStagingLocal?.enabled){remindersV280=(typeof agendaRemindersV81!=='undefined'&&Array.isArray(agendaRemindersV81))?agendaRemindersV81.slice():[];checkinsV280=[];loadedAtV280=Date.now();renderCalendar();return}
    if(!force&&loadedAtV280&&Date.now()-loadedAtV280<30000){renderCalendar();return}
    if(inflightV280)return inflightV280;
    inflightV280=(async()=>{const [rr,cr]=await Promise.all([supabaseClient.from('athlete_reminders').select('athlete_id,title,schedule_type,reminder_date,weekday,active').eq('coach_id',currentUser.id).eq('active',true),supabaseClient.from('checkin_schedules').select('athlete_id,next_due,active').eq('coach_id',currentUser.id).eq('active',true)]);if(!rr.error)remindersV280=rr.data||[];if(!cr.error)checkinsV280=cr.data||[];loadedAtV280=Date.now();renderCalendar()})().catch(e=>{console.warn('TEAM FJZ V20.80 calendar load',e);renderCalendar()}).finally(()=>{inflightV280=null});return inflightV280;
  }

  window.__fjzOpenPriorityV280=(id,tab)=>openStudent(id,tab);
  window.shiftCoachCalendarV280=function(delta){monthV280=new Date(monthV280.getFullYear(),monthV280.getMonth()+Number(delta||0),1);renderCalendar()};
  window.goTodayCoachCalendarV280=function(){const d=new Date();monthV280=new Date(d.getFullYear(),d.getMonth(),1);renderCalendar()};
  window.renderCoachPriorityCenterV252=renderPriority;try{renderCoachPriorityCenterV252=renderPriority}catch(_e){}

  window.__fjzOperationalDashboardV280=function(){
    if(hydratingV280||!(mode==='coach'&&coachTab==='dashboard'))return;
    hydratingV280=true;
    try{renderPriority();renderCalendar();loadCalendar(false)}finally{hydratingV280=false}
  };
  window.refreshCoachOperationalV280=function(){renderPriority();loadedAtV280=0;return loadCalendar(true)};

  window.__fjzV280={version:'20.80',priorityCalendarRecovery:true,restoredPriorityAuthorityAfterMusicRemoval:true,restoredCalendarAuthorityAfterMusicRemoval:true,staleCalendarCallsRemoved:true,priorityPerStudentIsolation:true,calendarIndependentFromPriority:true,stagingCalendarFallbackSafe:true,explicitDashboardOperationalHydration:true,productionUntouched:true,noExtraTimers:true,noExtraListeners:true,noExtraObservers:true};
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-priority-calendar-recovery" content="20.80">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.80 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in ['meta name="fjz-priority-calendar-recovery" content="20.80"',"priorityCalendarRecovery:true","restoredPriorityAuthorityAfterMusicRemoval:true","restoredCalendarAuthorityAfterMusicRemoval:true","staleCalendarCallsRemoved:true","priorityPerStudentIsolation:true","calendarIndependentFromPriority:true","stagingCalendarFallbackSafe:true","explicitDashboardOperationalHydration:true","__fjzOperationalDashboardV280","shiftCoachCalendarV280","goTodayCoachCalendarV280"]:
    if marker not in html: raise RuntimeError("V20.80 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.80 priority/calendar recovery")
print("V20.80 BEFORE:",before)
print("V20.80 AFTER:",after)
print("V20.80 restored both priority and calendar authorities after V20.68 cleanup")
