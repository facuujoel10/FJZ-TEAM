(function(root,factory){
  const api=factory(root||{});
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.TeamFJZAthlete360=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(root){
  'use strict';
  const VERSION='22.3B';
  const TZ='America/Argentina/Buenos_Aires';
  const ui={
    studentId:'',athleteId:'',sectionOverride:null,loading:false,error:null,
    comments:[],agenda:[],tracking:null,nutrition:null,loadedAt:0,loadedAthleteId:'',
    token:0
  };
  let agendaRepo=null,commentRepo=null;

  function text(v){return String(v??'').trim()}
  function esc(v){return text(v).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))}
  function clone(v){try{return JSON.parse(JSON.stringify(v))}catch(_e){return v}}
  function context(){try{return root.__fjzAthlete360ContextV22?.()||{}}catch(_e){return{}}}
  function currentIdentity(){
    const c=context(),s=c.student||null,a=c.athlete||null;
    return {studentId:text(s?.id||c.selectedStudentId),athleteId:text(a?.id),student:s,athlete:a,coachTab:text(c.coachTab),coachStudentTab:text(c.coachStudentTab),profile:c.profile||null,supabase:c.supabase||root.supabaseClient||null};
  }
  function isCoachStudent(){const x=currentIdentity();return x.profile?.role==='coach'&&x.coachTab==='student'&&!!x.studentId}
  function sectionForTab(tab){
    const t=text(tab);
    if(t==='nutrition')return'nutrition';if(t==='tracking')return'checkins';if(t==='agenda')return'agenda';
    if(t==='progress')return'progress';if(t==='routine'||t==='history')return'training';return'summary';
  }
  function activeSection(){return ui.sectionOverride||sectionForTab(currentIdentity().coachStudentTab)}
  function verifiedSession(engine,session){return !!(engine&&typeof engine.sessionConfirmed==='function'&&engine.sessionConfirmed(session))}
  function confirmedSessions(rows,engine=root.TeamFJZIntelligentTraining){
    return (Array.isArray(rows)?rows:[]).filter(x=>verifiedSession(engine,x)).slice().sort((a,b)=>(Date.parse(b?.date||b?.completedAt||0)||0)-(Date.parse(a?.date||a?.completedAt||0)||0));
  }
  function latestConfirmedSession(rows,engine=root.TeamFJZIntelligentTraining){return confirmedSessions(rows,engine)[0]||null}
  function parseDateOnly(v){const s=text(v).slice(0,10);return /^\d{4}-\d{2}-\d{2}$/.test(s)?s:null}
  function utcNoon(dateOnly){const [y,m,d]=dateOnly.split('-').map(Number);return new Date(Date.UTC(y,m-1,d,12))}
  function addDate(dateOnly,days){const d=utcNoon(dateOnly);d.setUTCDate(d.getUTCDate()+days);return d.toISOString().slice(0,10)}
  function mondayWeekday(dateOnly){return (utcNoon(dateOnly).getUTCDay()+6)%7}
  function calendarToday(now=new Date()){
    try{return root.TeamFJZDate?.calendarDate?.(now,TZ)||new Intl.DateTimeFormat('en-CA',{timeZone:TZ,year:'numeric',month:'2-digit',day:'2-digit'}).format(now)}
    catch(_e){return new Date(now).toISOString().slice(0,10)}
  }
  function nextWeeklyDate(weekday,today=calendarToday()){
    const wd=Number(weekday);if(!Number.isInteger(wd)||wd<0||wd>6)return null;
    const delta=(wd-mondayWeekday(today)+7)%7;
    return addDate(today,delta);
  }
  function nextAgendaItems(data,{today=calendarToday()}={}){
    const out=[];
    for(const r of data?.reminders||[]){
      if(r?.active===false)continue;
      const type=text(r?.schedule_type).toLowerCase();let date=null;
      if(type==='once')date=parseDateOnly(r?.reminder_date);
      else if(Number.isInteger(Number(r?.weekday)))date=nextWeeklyDate(Number(r.weekday),today);
      if(!date||date<today)continue;
      out.push({id:text(r.id),kind:'reminder',date,time:text(r.remind_time).slice(0,5),title:text(r.title||r.body||'Seguimiento'),body:text(r.body),source:r});
    }
    for(const r of data?.schedule||[]){
      if(r?.active===false)continue;
      const date=nextWeeklyDate(Number(r?.weekday),today);if(!date||date<today)continue;
      out.push({id:text(r.id),kind:'schedule',date,time:text(r.start_time).slice(0,5),title:text(r.workout_day_name||'Entrenamiento programado'),body:text(r.notes),source:r});
    }
    return out.sort((a,b)=>a.date.localeCompare(b.date)||a.time.localeCompare(b.time)||a.id.localeCompare(b.id));
  }
  function reviewState(checkin){if(!checkin)return'none';return checkin.reviewed_at?'reviewed':'pending'}
  function latestByDate(rows,keys){
    return (Array.isArray(rows)?rows:[]).slice().sort((a,b)=>{
      const av=keys.map(k=>a?.[k]).find(Boolean)||0,bv=keys.map(k=>b?.[k]).find(Boolean)||0;
      return (Date.parse(bv)||Date.parse(String(bv)+'T12:00:00Z')||0)-(Date.parse(av)||Date.parse(String(av)+'T12:00:00Z')||0);
    })[0]||null;
  }
  function latestMeasurement(rows){return latestByDate(rows,['measured_on','created_at'])}
  function latestCheckin(rows){return latestByDate(rows,['submitted_at','week_start','created_at'])}
  function neutralWeightChange(rows){
    const sorted=(Array.isArray(rows)?rows:[]).filter(x=>Number.isFinite(Number(x?.weight_kg))).slice().sort((a,b)=>text(b?.measured_on||b?.created_at).localeCompare(text(a?.measured_on||a?.created_at)));
    if(sorted.length<2)return null;return Number(sorted[0].weight_kg)-Number(sorted[1].weight_kg);
  }
  function activityCandidates({sessions=[],checkins=[],measurements=[]}={}){
    const out=[];const s=latestConfirmedSession(sessions);
    if(s)out.push({kind:'training',date:s.date||s.completedAt,label:s.dayName||s.workoutDayName||'Entrenamiento confirmado'});
    const c=latestCheckin(checkins);if(c)out.push({kind:'checkin',date:c.submitted_at||c.week_start,label:'Check-in'});
    const m=latestMeasurement(measurements);if(m)out.push({kind:'progress',date:m.measured_on||m.created_at,label:'Medición corporal'});
    return out.filter(x=>x.date).sort((a,b)=>(Date.parse(b.date)||Date.parse(String(b.date)+'T12:00:00Z')||0)-(Date.parse(a.date)||Date.parse(String(a.date)+'T12:00:00Z')||0));
  }
  function nextAction({comments=[],checkin=null,agenda=[]}={}){
    const pending=(comments||[]).filter(x=>text(x?.status||'pending')==='pending');
    const discomfort=pending.find(x=>text(x.feedback_type)==='discomfort');
    const comment=discomfort||pending[0];
    if(comment)return {kind:'comment',title:comment.feedback_type==='discomfort'?'Revisar molestia del alumno':'Revisar comentario de entrenamiento',detail:text(comment.exercise_name||'Ejercicio'),commentId:text(comment.id)};
    if(checkin&&reviewState(checkin)==='pending')return {kind:'checkin',title:'Revisar último check-in',detail:text(checkin.week_start||'Seguimiento pendiente')};
    if(agenda?.length)return {kind:'agenda',title:'Próximo seguimiento',detail:[agenda[0].title,agenda[0].date].filter(Boolean).join(' · ')};
    return {kind:'none',title:'Sin acción pendiente detectada',detail:'No hay pendientes confirmados con los datos disponibles.'};
  }
  function deriveSummary({student,tracking,comments,agenda,engine=root.TeamFJZIntelligentTraining}={}){
    const sessions=student?.sessions||[],confirmed=confirmedSessions(sessions,engine),lastSession=confirmed[0]||null;
    const checkins=tracking?.checkins||[],measurements=tracking?.measurements||[];
    const checkin=latestCheckin(checkins),measurement=latestMeasurement(measurements);
    const action=nextAction({comments,checkin,agenda});
    return {confirmed,lastSession,checkin,measurement,weightChange:neutralWeightChange(measurements),activity:activityCandidates({sessions,checkins,measurements})[0]||null,action,pendingComments:(comments||[]).filter(x=>text(x?.status||'pending')==='pending')};
  }
  function formatDate(v,withTime=false){
    if(!v)return'Sin registro';
    try{
      const raw=parseDateOnly(v)?String(v).slice(0,10)+'T12:00:00-03:00':v;
      return new Intl.DateTimeFormat('es-AR',{timeZone:TZ,day:'2-digit',month:'short',year:'numeric',...(withTime?{hour:'2-digit',minute:'2-digit'}:{})}).format(new Date(raw));
    }catch(_e){return text(v)}
  }
  function repositories(){
    const supabase=currentIdentity().supabase;if(!supabase)return{};
    if(!agendaRepo&&root.TeamFJZAgendaRepository?.createAgendaRepository)agendaRepo=root.TeamFJZAgendaRepository.createAgendaRepository({supabase,ttlMs:15000});
    if(!commentRepo&&root.TeamFJZCommentRepository?.createCommentRepository)commentRepo=root.TeamFJZCommentRepository.createCommentRepository({supabase});
    return {agendaRepo,commentRepo};
  }
  function resetForIdentity(identity){
    if(ui.studentId===identity.studentId&&ui.athleteId===identity.athleteId)return;
    ui.studentId=identity.studentId;ui.athleteId=identity.athleteId;ui.sectionOverride=null;ui.loading=false;ui.error=null;
    ui.comments=[];ui.agenda=[];ui.tracking=null;ui.nutrition=null;ui.loadedAt=0;ui.loadedAthleteId='';ui.token++;
  }
  function sectionLabel(section){return({summary:'Resumen',training:'Entrenamiento',nutrition:'Nutrición',progress:'Progreso',checkins:'Check-ins',agenda:'Agenda',info:'Información'})[section]||'Resumen'}
  function navHtml(){
    const active=activeSection();
    return '<nav class="fjz3b-nav" aria-label="Secciones del perfil 360">'+
      [['summary','Resumen','◉'],['training','Entreno','▤'],['nutrition','Nutrición','◇'],['progress','Progreso','↗'],['checkins','Check-ins','✓'],['agenda','Agenda','□'],['info','Info','ⓘ']].map(([k,l,i])=>'<button type="button" data-3b-action="section" data-section="'+k+'" class="'+(active===k?'active':'')+'" aria-current="'+(active===k?'page':'false')+'"><i>'+i+'</i><span>'+l+'</span></button>').join('')+
      '</nav>';
  }
  function trainingSubnav(){
    if(activeSection()!=='training')return'';
    const tab=currentIdentity().coachStudentTab;
    return '<div class="fjz3b-subnav" aria-label="Entrenamiento"><button type="button" data-3b-action="legacy-tab" data-tab="routine" class="'+(tab!=='history'?'active':'')+'">Rutina</button><button type="button" data-3b-action="legacy-tab" data-tab="history" class="'+(tab==='history'?'active':'')+'">Historial y rendimiento</button></div>';
  }
  function headerShell(hero,identity){
    const s=identity.student||{},goal=text(s.goal);
    const header=document.createElement('section');header.className='fjz3b-header';
    header.innerHTML='<div class="fjz3b-header-top"><button type="button" class="fjz3b-back" data-3b-action="back" aria-label="Volver al Command Center">‹ <span>Command Center</span></button><div class="fjz3b-product">ATHLETE WORKSPACE · TEAM FJZ</div><button type="button" class="fjz3b-info-shortcut" data-3b-action="section" data-section="info">Información</button></div>';
    const identityBox=document.createElement('div');identityBox.className='fjz3b-identity';
    if(hero){
      hero.classList.add('fjz3b-legacy-hero');
      const info=hero.querySelector('.v175-coach-profile-info');
      if(info&&goal){
        const p=info.querySelector('p');if(p)p.textContent=goal;
      }
      if(info&&!goal){
        const p=info.querySelector('p');if(p)p.textContent='Objetivo no cargado';
      }
      const actions=hero.querySelector('.v175-coach-profile-actions,.pill-row');
      if(actions){actions.classList.add('fjz3b-legacy-actions');actions.hidden=true}
      identityBox.appendChild(hero);
    }
    const contextBox=document.createElement('div');contextBox.id='fjz3bHeaderContext';contextBox.className='fjz3b-header-context';
    contextBox.innerHTML='<div><span>Última actividad</span><strong>Consultando…</strong></div><div><span>Próxima acción</span><strong>Consultando…</strong></div>';
    identityBox.appendChild(contextBox);header.appendChild(identityBox);return header;
  }
  function summarySkeleton(){
    return '<div class="fjz3b-summary" id="fjz3bSummary"><section class="fjz3b-action-card"><div class="fjz3b-kicker">PRÓXIMA DECISIÓN</div><h2>Preparando seguimiento…</h2><p>Consultando información confirmada del alumno.</p></section><div class="fjz3b-summary-grid"><section class="fjz3b-panel"><div class="fjz3b-panel-head"><div><span>ENTRENAMIENTO</span><h3>Actividad confirmada</h3></div></div><div class="fjz3b-loading-line"></div></section><section class="fjz3b-panel"><div class="fjz3b-panel-head"><div><span>CHECK-IN</span><h3>Seguimiento reciente</h3></div></div><div class="fjz3b-loading-line"></div></section><section class="fjz3b-panel"><div class="fjz3b-panel-head"><div><span>PROGRESO FÍSICO</span><h3>Último registro</h3></div></div><div class="fjz3b-loading-line"></div></section><section class="fjz3b-panel"><div class="fjz3b-panel-head"><div><span>AGENDA</span><h3>Próxima fecha</h3></div></div><div class="fjz3b-loading-line"></div></section></div><section class="fjz3b-panel fjz3b-comments"><div class="fjz3b-panel-head"><div><span>COMENTARIOS Y MOLESTIAS</span><h3>Contexto técnico pendiente</h3></div></div><div class="fjz3b-loading-line"></div></section></div>';
  }
  function infoHtml(identity,actions){
    const s=identity.student||{},a=identity.athlete||{};
    const rows=[['Objetivo',text(s.goal)],['Altura',a.height_cm!=null?text(a.height_cm)+' cm':''],['Sexo',text(a.sex)],['Ocupación',text(a.occupation||s.occupation)]].filter(x=>x[1]);
    return '<div class="fjz3b-info"><section class="fjz3b-panel"><div class="fjz3b-panel-head"><div><span>INFORMACIÓN</span><h3>Datos del alumno</h3></div></div><div class="fjz3b-info-grid">'+(rows.length?rows.map(([l,v])=>'<div><span>'+esc(l)+'</span><strong>'+esc(v)+'</strong></div>').join(''):'<div class="fjz3b-empty"><strong>Sin datos adicionales</strong><span>No se inventan campos ausentes.</span></div>')+'</div></section><section class="fjz3b-panel"><div class="fjz3b-panel-head"><div><span>ADMINISTRACIÓN EXISTENTE</span><h3>Acciones de la ficha</h3></div></div><div id="fjz3bAdminActions" class="fjz3b-admin-actions"></div></section></div>';
  }
  function shapeLegacySection(body){
    const section=activeSection();
    if(section==='checkins'){
      body.querySelector('.grid.kpi')?.remove();
      const latest=[...body.querySelectorAll('.card')].find(card=>/Último check-in completo/i.test(card.textContent||''));
      const two=[...body.children].find(x=>x.classList?.contains('grid')&&x.classList?.contains('two'));
      if(two&&two.children[1])two.children[1].remove();
      const photo=body.querySelector('#coachPhotoGrid')?.closest('.card');if(photo)photo.remove();
      return;
    }
    if(section!=='progress')return;
    const photo=body.querySelector('#coachPhotoGrid')?.closest('.card')||null;
    const two=[...body.children].find(x=>x.classList?.contains('grid')&&x.classList?.contains('two'));
    const measurementEditor=two?.querySelector('aside.card')||null;
    const ms=(ui.tracking?.measurements||[]).slice().sort((a,b)=>text(b?.measured_on||b?.created_at).localeCompare(text(a?.measured_on||a?.created_at)));
    body.innerHTML='<div class="fjz3b-physical-progress"><section class="fjz3b-panel"><div class="fjz3b-panel-head"><div><span>HISTORIAL CORPORAL</span><h3>Mediciones registradas</h3></div></div><div class="fjz3b-measure-list">'+(ms.length?ms.map((m,i)=>'<article><div><strong>'+esc(formatDate(m.measured_on||m.created_at))+'</strong><span>'+(m.weight_kg!=null?esc(m.weight_kg)+' kg':'Peso sin registro')+'</span></div><div class="fjz3b-measure-values">'+[['Cintura',m.waist_cm],['Abdomen',m.abdomen_cm],['Cadera',m.hip_cm],['Pecho',m.chest_cm],['Brazo izq.',m.arm_left_cm],['Brazo der.',m.arm_right_cm],['Muslo izq.',m.thigh_left_cm],['Muslo der.',m.thigh_right_cm]].filter(x=>x[1]!=null).map(x=>'<span>'+esc(x[0])+' <b>'+esc(x[1])+' cm</b></span>').join('')+'</div>'+(m.notes?'<p>'+esc(m.notes)+'</p>':'')+'</article>').join(''):'<div class="fjz3b-empty"><strong>Sin mediciones</strong><span>No hay datos corporales registrados.</span></div>')+'</div></section></div>';
    if(measurementEditor){const wrap=document.createElement('section');wrap.className='fjz3b-panel fjz3b-measure-editor';wrap.appendChild(measurementEditor);body.appendChild(wrap)}
    if(photo)body.appendChild(photo);
  }
  function mount(){
    const identity=currentIdentity();if(!isCoachStudent())return false;resetForIdentity(identity);
    const view=root.document?.getElementById('view');if(!view)return false;
    view.classList.add('fjz3b-mounted');
    const legacyNav=root.document?.getElementById('bottomNav');if(legacyNav)legacyNav.classList.add('fjz3b-hide-legacy-nav');
    const hero=view.querySelector('.v175-coach-profile-hero,.hero');
    const actions=hero?.querySelector('.v175-coach-profile-actions,.pill-row')||null;
    const header=headerShell(hero,identity);
    view.prepend(header);
    const oldTabs=root.document?.getElementById('coachStudentTabs')||view.querySelector('.tabs');
    if(oldTabs)oldTabs.classList.add('fjz3b-legacy-tabs');
    const oldWorkspace=root.document?.getElementById('v266CoachWorkspace');if(oldWorkspace)oldWorkspace.classList.add('fjz3b-legacy-workspace');
    const body=root.document?.getElementById('coachStudentBody');
    if(!body)return false;
    const layout=document.createElement('div');layout.className='fjz3b-layout';
    const nav=document.createElement('div');nav.className='fjz3b-nav-wrap';nav.innerHTML=navHtml();
    const main=document.createElement('main');main.className='fjz3b-main';
    const title=document.createElement('div');title.className='fjz3b-section-title';title.innerHTML='<div><span>PERFIL 360</span><h2>'+esc(sectionLabel(activeSection()))+'</h2></div>'+trainingSubnav();
    main.appendChild(title);main.appendChild(body);layout.appendChild(nav);layout.appendChild(main);view.appendChild(layout);
    if(activeSection()==='summary')body.innerHTML=summarySkeleton();
    else if(activeSection()==='info'){
      body.innerHTML=infoHtml(identity,actions);
      const host=root.document.getElementById('fjz3bAdminActions');if(host&&actions){actions.hidden=false;host.appendChild(actions)}
    }else{
      shapeLegacySection(body);
      const ctx=document.createElement('div');ctx.id='fjz3bSectionContext';ctx.className='fjz3b-section-context';ctx.innerHTML='<div class="fjz3b-loading-line"></div>';body.prepend(ctx);
    }
    bind(view);return true;
  }
  function bind(view){
    view.onclick=async e=>{
      const b=e.target.closest('[data-3b-action]');if(!b)return;
      const action=b.dataset['3bAction'];
      if(action==='back'){leave();ui.sectionOverride=null;root.__fjzAthlete360ReturnV22?.();return}
      if(action==='section'){navigateSection(b.dataset.section);return}
      if(action==='legacy-tab'){navigateLegacy(b.dataset.tab);return}
      if(action==='open-comment'){await openComment(b.dataset.comment);return}
      if(action==='ok-comment'){await resolveComment(b.dataset.comment,b);return}
      if(action==='retry'){await hydrate(true);return}
    };
  }
  function navigateLegacy(tab){ui.sectionOverride=null;root.__fjzAthlete360NavigateV22?.(tab);return true}
  function navigateSection(section){
    const s=text(section);if(!['summary','training','nutrition','progress','checkins','agenda','info'].includes(s))return false;
    if(s==='info'||s==='progress')ui.sectionOverride=s;else ui.sectionOverride=null;
    const tab={summary:'summary',training:'routine',nutrition:'nutrition',progress:'tracking',checkins:'tracking',agenda:'agenda',info:'summary'}[s];
    root.__fjzAthlete360NavigateV22?.(tab);return true;
  }
  function leave(){const nav=root.document?.getElementById('bottomNav');if(nav)nav.classList.remove('fjz3b-hide-legacy-nav')}
  function commentRow(id){return ui.comments.find(x=>text(x.id)===text(id))||null}
  async function openComment(id){
    const x=commentRow(id);if(!x)return false;
    if(!x.session_id){root.toast?.('Este comentario histórico no tiene una sesión exacta vinculada.');navigateLegacy('history');return false}
    ui.sectionOverride=null;
    root.__fjzFocusTrainingCommentV328={studentId:ui.studentId,sessionId:text(x.session_id),exerciseUid:text(x.exercise_uid),feedbackId:text(x.id),date:x.created_at||null};
    try{return !!(await root.__fjzOpenTrainingCommentV325?.(ui.studentId,text(x.session_id)))}catch(_e){return false}
  }
  async function resolveComment(id,button){
    const x=commentRow(id);if(!x)return false;const old=button?.textContent||'OK';
    if(button){button.disabled=true;button.textContent='Guardando…'}
    try{
      const ok=await root.__fjzAckTrainingCommentV329?.(ui.studentId,text(x.session_id),'exercise',text(x.id),text(x.exercise_uid));
      if(ok===false||ok==null)throw new Error('El servidor no confirmó el OK.');
      await hydrate(true);return true;
    }catch(err){root.toast?.(text(err?.message||'No se pudo guardar el OK.'));if(button){button.disabled=false;button.textContent=old}return false}
  }
  function renderHeader(summary){
    const host=root.document?.getElementById('fjz3bHeaderContext');if(!host)return;
    const activity=summary.activity;
    host.innerHTML='<div><span>Última actividad confirmada</span><strong>'+esc(activity?activity.label+' · '+formatDate(activity.date):'Sin actividad confirmada')+'</strong></div><div><span>Próxima acción</span><strong>'+esc(summary.action.title)+'</strong><small>'+esc(summary.action.detail||'')+'</small></div>';
  }
  function commentHtml(c){
    const type=text(c.feedback_type)==='discomfort'?'Molestia':'Comentario';
    return '<article class="fjz3b-comment '+(type==='Molestia'?'warn':'')+'"><div><div class="fjz3b-comment-meta"><span>'+type+'</span><span>'+esc(c.exercise_name||'Ejercicio')+'</span><time>'+esc(formatDate(c.created_at,true))+'</time></div><p>'+esc(c.message||'Sin texto')+'</p></div><div class="fjz3b-comment-actions">'+(c.session_id?'<button class="btn small" type="button" data-3b-action="open-comment" data-comment="'+esc(c.id)+'">Abrir ejercicio</button>':'<button class="btn small" type="button" data-3b-action="legacy-tab" data-tab="history">Ver historial</button>')+'<button class="btn small primary" type="button" data-3b-action="ok-comment" data-comment="'+esc(c.id)+'">OK</button></div></article>';
  }
  function renderSummary(summary){
    const host=root.document?.getElementById('fjz3bSummary');if(!host)return;
    const s=summary.lastSession,check=summary.checkin,m=summary.measurement,next=ui.agenda[0]||null;
    let workout=null;
    try{if(s)workout=root.TeamFJZIntelligentTraining?.workoutSummary?.({sessions:currentIdentity().student?.sessions||[],currentSession:s,confirmedSessionId:s.id,feedbackRows:ui.comments})||null}catch(_e){}
    const actionButton=summary.action.kind==='comment'&&summary.action.commentId?'<button class="btn primary" data-3b-action="open-comment" data-comment="'+esc(summary.action.commentId)+'">Abrir comentario exacto</button>':summary.action.kind==='checkin'?'<button class="btn primary" data-3b-action="section" data-section="checkins">Revisar check-in</button>':summary.action.kind==='agenda'?'<button class="btn primary" data-3b-action="section" data-section="agenda">Abrir agenda</button>':'';
    const delta=summary.weightChange;
    host.innerHTML='<section class="fjz3b-action-card"><div><div class="fjz3b-kicker">PRÓXIMA DECISIÓN</div><h2>'+esc(summary.action.title)+'</h2><p>'+esc(summary.action.detail||'')+'</p></div>'+actionButton+'</section>'+
      '<div class="fjz3b-summary-grid">'+
      '<section class="fjz3b-panel"><div class="fjz3b-panel-head"><div><span>ENTRENAMIENTO</span><h3>Actividad confirmada</h3></div><button class="fjz3b-link" data-3b-action="section" data-section="training">Abrir</button></div>'+(s?'<div class="fjz3b-keyline"><strong>'+esc(s.dayName||s.workoutDayName||'Entrenamiento')+'</strong><span>'+esc(formatDate(s.date||s.completedAt,true))+'</span></div><div class="fjz3b-facts"><div><strong>'+esc(workout?.exercises?.length??(s.exerciseResults||[]).length)+'</strong><span>ejercicios</span></div><div><strong>'+esc(workout?.totalSets??'—')+'</strong><span>series válidas</span></div><div><strong>'+esc(workout?.recordCount??0)+'</strong><span>PR válidos</span></div></div>':'<div class="fjz3b-empty"><strong>Sin sesión confirmada</strong><span>No se muestran récords ni comparaciones sin confirmación.</span></div>')+'</section>'+
      '<section class="fjz3b-panel"><div class="fjz3b-panel-head"><div><span>CHECK-IN</span><h3>Seguimiento reciente</h3></div><button class="fjz3b-link" data-3b-action="section" data-section="checkins">Abrir</button></div>'+(check?'<div class="fjz3b-keyline"><strong>'+esc(formatDate(check.submitted_at||check.week_start))+'</strong><span class="fjz3b-state '+reviewState(check)+'">'+(reviewState(check)==='reviewed'?'Revisado':'Pendiente')+'</span></div><div class="fjz3b-mini-metrics">'+[['Sueño',check.sleep_quality],['Hambre',check.hunger_level],['Estrés',check.stress_level],['Motivación',check.motivation_level],['Recuperación',check.recovery_level]].filter(x=>x[1]!=null).map(x=>'<span>'+esc(x[0])+' <b>'+esc(x[1])+'/10</b></span>').join('')+'</div>'+(check.notes?'<p class="fjz3b-note">'+esc(check.notes)+'</p>':''):'<div class="fjz3b-empty"><strong>Sin check-in</strong><span>No hay un registro reciente disponible.</span></div>')+'</section>'+
      '<section class="fjz3b-panel"><div class="fjz3b-panel-head"><div><span>PROGRESO FÍSICO</span><h3>Último registro</h3></div><button class="fjz3b-link" data-3b-action="section" data-section="progress">Abrir</button></div>'+(m?'<div class="fjz3b-keyline"><strong>'+(m.weight_kg!=null?esc(m.weight_kg)+' kg':'Medición')+'</strong><span>'+esc(formatDate(m.measured_on||m.created_at))+'</span></div>'+(delta!=null?'<p class="fjz3b-neutral-change">Cambio desde el registro anterior: <b>'+esc((delta>0?'+':'')+Math.round(delta*10)/10)+' kg</b>. Sin interpretación automática.</p>':''):'<div class="fjz3b-empty"><strong>Sin mediciones</strong><span>No se reemplaza la ausencia de datos por cero.</span></div>')+'</section>'+
      '<section class="fjz3b-panel"><div class="fjz3b-panel-head"><div><span>AGENDA</span><h3>Próxima fecha</h3></div><button class="fjz3b-link" data-3b-action="section" data-section="agenda">Abrir</button></div>'+(next?'<div class="fjz3b-keyline"><strong>'+esc(next.title)+'</strong><span>'+esc(formatDate(next.date))+(next.time?' · '+esc(next.time):'')+'</span></div>'+(next.body?'<p class="fjz3b-note">'+esc(next.body)+'</p>':''):'<div class="fjz3b-empty"><strong>Sin próximas fechas</strong><span>No hay eventos futuros confirmados.</span></div>')+'</section></div>'+
      '<section class="fjz3b-panel fjz3b-comments"><div class="fjz3b-panel-head"><div><span>COMENTARIOS Y MOLESTIAS</span><h3>Contexto técnico pendiente</h3></div></div>'+(summary.pendingComments.length?summary.pendingComments.map(commentHtml).join(''):'<div class="fjz3b-empty"><strong>Sin comentarios pendientes</strong><span>Los revisados no vuelven a pendientes si el servidor confirmó el OK.</span></div>')+'</section>';
  }
  function restoreSectionShell(){
    const section=activeSection(),body=root.document?.getElementById('coachStudentBody');
    if(!body||section==='summary'||section==='info')return;
    shapeLegacySection(body);
    let ctx=root.document?.getElementById('fjz3bSectionContext');
    if(!ctx){ctx=root.document.createElement('div');ctx.id='fjz3bSectionContext';ctx.className='fjz3b-section-context';body.prepend(ctx)}
  }
  function renderSectionContext(summary){
    const host=root.document?.getElementById('fjz3bSectionContext');if(!host)return;
    const section=activeSection(),check=summary.checkin,m=summary.measurement,next=ui.agenda[0],s=summary.lastSession;
    if(section==='training')host.innerHTML=s?'<div class="fjz3b-context-card"><span>ÚLTIMA SESIÓN CONFIRMADA</span><strong>'+esc(s.dayName||s.workoutDayName||'Entrenamiento')+'</strong><small>'+esc(formatDate(s.date||s.completedAt,true))+' · las comparaciones y PR se delegan a TeamFJZIntelligentTraining.</small></div>':'<div class="fjz3b-context-card empty"><strong>Sin sesión confirmada</strong><small>La rutina sigue disponible; no se fabrican referencias de rendimiento.</small></div>';
    else if(section==='nutrition')host.innerHTML='<div class="fjz3b-context-card"><span>PLAN NUTRICIONAL</span><strong>'+(ui.nutrition?.plan?esc(ui.nutrition.plan.title||'Plan asignado'):'Sin plan activo')+'</strong><small>Las cantidades y macros mostrados debajo provienen del plan existente; 3B no modifica cálculos ni registra comidas nuevas.</small></div>';
    else if(section==='progress')host.innerHTML=m?'<div class="fjz3b-context-card"><span>ÚLTIMA MEDICIÓN</span><strong>'+(m.weight_kg!=null?esc(m.weight_kg)+' kg · ':'')+esc(formatDate(m.measured_on||m.created_at))+'</strong><small>Las variaciones se presentan como registros corporales, sin interpretación clínica ni de grasa corporal.</small></div>':'<div class="fjz3b-context-card empty"><strong>Sin mediciones disponibles</strong><small>Podés seguir usando las funciones existentes de progreso y fotografías.</small></div>';
    else if(section==='checkins')host.innerHTML=check?'<div class="fjz3b-context-card"><span>ÚLTIMO CHECK-IN</span><strong>'+esc(formatDate(check.submitted_at||check.week_start))+' · '+(reviewState(check)==='reviewed'?'Revisado':'Pendiente de revisión')+'</strong><small>'+esc(check.coach_feedback||check.notes||'Sin comentario adicional.')+'</small></div>':'<div class="fjz3b-context-card empty"><strong>Sin check-ins disponibles</strong><small>No hay una revisión reciente para mostrar.</small></div>';
    else if(section==='agenda')host.innerHTML=next?'<div class="fjz3b-context-card"><span>PRÓXIMA FECHA VÁLIDA</span><strong>'+esc(next.title)+'</strong><small>'+esc(formatDate(next.date))+(next.time?' · '+esc(next.time):'')+'. Las fechas vencidas no se presentan como próximas.</small></div>':'<div class="fjz3b-context-card empty"><strong>Sin próximas fechas</strong><small>La agenda completa permanece disponible debajo.</small></div>';
  }
  function renderError(message){
    const summary=root.document?.getElementById('fjz3bSummary'),ctx=root.document?.getElementById('fjz3bSectionContext');
    const html='<div class="fjz3b-error"><strong>No pudimos cargar el contexto 360</strong><span>'+esc(message||'Error de lectura')+'</span><button class="btn small" data-3b-action="retry">Reintentar</button></div>';
    if(summary)summary.innerHTML=html;if(ctx)ctx.innerHTML=html;
  }
  async function hydrate(force=false){
    if(!isCoachStudent())return false;const identity=currentIdentity();resetForIdentity(identity);
    if(!force&&ui.loadedAthleteId===identity.athleteId&&Date.now()-ui.loadedAt<15000){const summary=deriveSummary({student:identity.student,tracking:ui.tracking,comments:ui.comments,agenda:ui.agenda});restoreSectionShell();renderHeader(summary);if(activeSection()==='summary')renderSummary(summary);else renderSectionContext(summary);return true}
    const token=++ui.token;ui.loading=true;ui.error=null;
    try{
      const {agendaRepo,commentRepo}=repositories();
      const legacyPromise=root.__fjzAthlete360LoadLegacyDataV22?.(identity.studentId)||Promise.resolve({tracking:null,nutrition:null});
      const [legacyRes,commentRes,agendaRes]=await Promise.allSettled([
        legacyPromise,
        commentRepo&&identity.athleteId?commentRepo.listForAthlete(identity.athleteId,{status:'pending',limit:100}):Promise.resolve({rows:[]}),
        agendaRepo&&identity.athleteId?agendaRepo.listForAthlete(identity.athleteId,{force}):Promise.resolve({schedule:[],reminders:[]})
      ]);
      const now=currentIdentity();
      if(token!==ui.token||now.studentId!==identity.studentId||now.athleteId!==identity.athleteId)return false;
      if(legacyRes.status==='rejected')throw legacyRes.reason;
      if(commentRes.status==='rejected')throw commentRes.reason;
      if(agendaRes.status==='rejected')throw agendaRes.reason;
      if(legacyRes.value?.cancelled)return false;
      ui.tracking=clone(legacyRes.value?.tracking)||{checkins:[],measurements:[],photos:[]};
      ui.nutrition=clone(legacyRes.value?.nutrition)||null;
      ui.comments=clone(commentRes.value?.rows)||[];
      ui.agenda=nextAgendaItems(agendaRes.value||{});
      ui.loadedAt=Date.now();ui.loadedAthleteId=identity.athleteId;ui.loading=false;ui.error=null;
      const summary=deriveSummary({student:currentIdentity().student,tracking:ui.tracking,comments:ui.comments,agenda:ui.agenda});
      restoreSectionShell();renderHeader(summary);if(activeSection()==='summary')renderSummary(summary);else renderSectionContext(summary);return true;
    }catch(err){
      if(token!==ui.token)return false;ui.loading=false;ui.error=text(err?.publicMessage||err?.message||'No pudimos completar la consulta.');restoreSectionShell();renderError(ui.error);return false;
    }
  }
  function render(){
    if(!isCoachStudent())return false;
    const identity=currentIdentity();resetForIdentity(identity);
    const rendered=root.__fjzRenderLegacyCoachStudentV22?.();
    mount();queueMicrotask(()=>hydrate(false));return rendered===undefined?true:rendered;
  }
  function install(){root.__fjzRenderAthlete360V22=render;root.__fjzHydrateAthlete360V22=hydrate;root.__fjzAthlete360StateV22=ui;return true}
  return Object.freeze({VERSION,TZ,sectionForTab,confirmedSessions,latestConfirmedSession,nextWeeklyDate,nextAgendaItems,reviewState,neutralWeightChange,activityCandidates,nextAction,deriveSummary,render,hydrate,openComment,resolveComment,navigateSection,install,state:ui});
});
