import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")
html=html.replace("TEAM FJZ V9.5","TEAM FJZ V9.6")

css=r"""
<style id="v96AlertCenterStyles">
#cloudFeedWrap{display:none!important}
.v96-alert-panel{margin-bottom:14px}
.v96-alert-summary{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:12px 0}
.v96-alert-kpi{padding:11px;border:1px solid var(--border);border-radius:12px;background:#0d0d10}
.v96-alert-kpi strong{display:block;font-size:20px;line-height:1}
.v96-alert-kpi span{display:block;margin-top:5px;font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:.45px}
.v96-alert-tools{display:flex;gap:7px;align-items:center;flex-wrap:wrap;margin-bottom:10px}
.v96-chip{border:1px solid var(--border);background:#0c0c0f;color:var(--muted);border-radius:999px;padding:6px 9px;font-size:10px;font-weight:750;cursor:pointer}
.v96-chip.active{border-color:rgba(255,45,58,.55);color:#fff;background:rgba(255,45,58,.10)}
.v96-alert-list{display:grid;gap:8px}
.v96-alert-card{border:1px solid var(--border);border-radius:13px;padding:11px;background:#0d0d10;display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:10px;align-items:start}
.v96-alert-card.unread{border-color:rgba(255,255,255,.20);background:#101014}
.v96-alert-card.warning{border-left:3px solid #f0a000}
.v96-alert-card.critical{border-left:3px solid #e5484d}
.v96-alert-card.success{border-left:3px solid #46a758}
.v96-alert-card.info{border-left:3px solid #5b8def}
.v96-alert-icon{width:31px;height:31px;border:1px solid var(--border);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:14px;background:#09090b}
.v96-alert-title{font-size:12px;font-weight:850;line-height:1.25}
.v96-alert-meta{font-size:9px;color:var(--muted);margin-top:3px}
.v96-alert-body{font-size:10px;color:var(--muted);margin-top:5px;line-height:1.45}
.v96-alert-actions{display:flex;gap:5px;align-items:center;flex-wrap:wrap;justify-content:flex-end}
.v96-bell{position:relative}
.v96-bell-count{position:absolute;right:-5px;top:-7px;min-width:18px;height:18px;padding:0 4px;border-radius:999px;background:#e5484d;color:white;font-size:9px;font-weight:900;display:flex;align-items:center;justify-content:center;border:2px solid #0b0b0d}
.v96-student-preview{margin:0 0 14px}
.v96-preview-row{display:flex;gap:9px;align-items:flex-start;padding:9px 0;border-top:1px solid var(--border)}
.v96-preview-row:first-of-type{border-top:0}
.v96-preview-row strong{font-size:11px}
.v96-notice-card{margin-bottom:14px}
.v96-notice-list{display:grid;gap:7px;margin-top:10px}
.v96-notice-item{display:flex;justify-content:space-between;gap:10px;align-items:flex-start;padding:9px 10px;border:1px solid var(--border);border-radius:10px;background:#0d0d10}
.v96-notice-item strong{font-size:11px}
.v96-center-head{display:flex;justify-content:space-between;gap:10px;align-items:flex-start;margin-bottom:10px}
.v96-empty{text-align:center;padding:22px 10px;color:var(--muted);font-size:11px}
@media(max-width:760px){
 .v96-alert-summary{grid-template-columns:repeat(2,minmax(0,1fr))}
 .v96-alert-card{grid-template-columns:auto minmax(0,1fr)}
 .v96-alert-actions{grid-column:1/-1;justify-content:flex-start;padding-left:41px}
}
</style>
"""

js=r"""
<script id="v96AlertCenterRuntime">
(function(){
  let coachAlertsV96=[];
  let coachFilterV96='all';
  let coachUnreadV96=false;
  let studentAlertsV96=[];
  let studentAlertsLoadedAtV96=0;

  const KIND_LABEL_V96={
    exercise_feedback:'Ejercicio',checkin:'Check-in',wellness:'Seguimiento',
    training:'Entrenamiento',progression:'Progresión',nutrition:'Nutrición',
    coach:'Coach',reminder:'Recordatorio'
  };
  const KIND_ICON_V96={
    exercise_feedback:'!',checkin:'✓',wellness:'◎',training:'↗',
    progression:'+',nutrition:'N',coach:'FJZ',reminder:'⏱'
  };

  function escAttrV96(s){return esc(String(s||'')).replace(/"/g,'&quot;')}
  function isoDowV96(){const d=new Date().getDay();return d===0?7:d}
  function relativeV96(v){
    if(!v)return '';
    const t=new Date(v).getTime(),diff=Date.now()-t;
    if(!Number.isFinite(t))return '';
    const mins=Math.max(0,Math.floor(diff/60000));
    if(mins<1)return 'Ahora';
    if(mins<60)return 'Hace '+mins+' min';
    const h=Math.floor(mins/60);if(h<24)return 'Hace '+h+' h';
    const days=Math.floor(h/24);if(days<7)return 'Hace '+days+' d';
    return new Date(v).toLocaleDateString('es-AR',{day:'2-digit',month:'short'});
  }
  function labelV96(kind){return KIND_LABEL_V96[kind]||'Aviso'}
  function iconV96(kind){return KIND_ICON_V96[kind]||'•'}

  function normalizeCoachV96(feed){
    let arr=[...(feed||[])];
    if(isoDowV96()<4)arr=arr.filter(x=>!String(x.event_key||'').startsWith('pending-checkin:'));
    return arr;
  }
  function coachCountsV96(){
    const arr=coachAlertsV96;
    return {
      priority:arr.filter(x=>x.severity==='critical').length,
      attention:arr.filter(x=>x.severity==='warning').length,
      unread:arr.filter(x=>!x.is_read).length,
      total:arr.length
    };
  }
  function coachFilteredV96(){
    return coachAlertsV96.filter(x=>{
      if(coachUnreadV96&&x.is_read)return false;
      if(coachFilterV96==='all')return true;
      if(coachFilterV96==='priority')return x.severity==='critical'||x.severity==='warning';
      return x.kind===coachFilterV96;
    });
  }
  function coachAlertCardV96(x){
    return '<div class="v96-alert-card '+esc(x.severity||'info')+' '+(x.is_read?'':'unread')+'">'+
      '<div class="v96-alert-icon">'+esc(iconV96(x.kind))+'</div>'+
      '<div><div class="v96-alert-title">'+(!x.is_read?'<span class="unread-dot"></span>':'')+esc(x.athlete_name||'Alumno')+' · '+esc(x.title||'Aviso')+'</div>'+
      '<div class="v96-alert-meta">'+esc(labelV96(x.kind))+' · '+esc(relativeV96(x.occurred_at))+'</div>'+
      '<div class="v96-alert-body">'+esc(x.body||'')+'</div></div>'+
      '<div class="v96-alert-actions"><button class="btn small" onclick="openCoachAlertV96(\''+x.athlete_id+'\',\''+escAttrV96(x.event_key)+'\',\''+escAttrV96(x.kind)+'\')">Abrir</button>'+
      (!x.is_read?'<button class="btn ghost small" onclick="readCoachAlertV96(\''+escAttrV96(x.event_key)+'\')">Leído</button>':'')+
      '<button class="btn ghost small" onclick="dismissCoachAlertV96(\''+escAttrV96(x.event_key)+'\')">Ocultar</button></div></div>';
  }
  function renderCoachAlertsV96(){
    const holder=el('v96CoachAlertBody');if(!holder)return;
    const c=coachCountsV96(),arr=coachFilteredV96();
    holder.innerHTML='<div class="v96-alert-summary">'+
      '<div class="v96-alert-kpi"><strong>'+c.priority+'</strong><span>Prioridad</span></div>'+
      '<div class="v96-alert-kpi"><strong>'+c.attention+'</strong><span>Atención</span></div>'+
      '<div class="v96-alert-kpi"><strong>'+c.unread+'</strong><span>Sin leer</span></div>'+
      '<div class="v96-alert-kpi"><strong>'+c.total+'</strong><span>Activas</span></div></div>'+
      '<div class="v96-alert-tools">'+
      [['all','Todas'],['priority','Prioridad'],['checkin','Check-ins'],['training','Entrenamiento'],['nutrition','Nutrición'],['exercise_feedback','Ejercicios']].map(x=>'<button class="v96-chip '+(coachFilterV96===x[0]?'active':'')+'" onclick="setCoachAlertFilterV96(\''+x[0]+'\')">'+x[1]+'</button>').join('')+
      '<button class="v96-chip '+(coachUnreadV96?'active':'')+'" onclick="toggleCoachUnreadV96()">Solo sin leer</button>'+
      (c.unread?'<button class="btn ghost small" onclick="readAllCoachAlertsV96()">Marcar todo leído</button>':'')+
      '</div><div class="v96-alert-list">'+(arr.length?arr.map(coachAlertCardV96).join(''):'<div class="v96-empty">No hay alertas en este filtro.</div>')+'</div>';
  }
  async function refreshCoachAlertsV96(force=true){
    const holder=el('v96CoachAlertBody');if(holder)holder.innerHTML='<div class="empty">Actualizando alertas…</div>';
    try{
      const feed=await loadCoachFeed(force);
      coachAlertsV96=normalizeCoachV96(feed);
      renderCoachAlertsV96();
      updateCoachBellV96();
    }catch(e){
      if(holder)holder.innerHTML='<div class="empty">'+esc(cloudErr(e))+'</div>';
    }
  }
  function injectCoachAlertPanelV96(){
    if(currentProfile?.role!=='coach'||coachTab!=='dashboard')return;
    document.querySelectorAll('#cloudFeedWrap').forEach(n=>n.remove());
    if(el('v96CoachAlerts'))return;
    const view=el('view'),hero=view?.querySelector('.hero');if(!hero)return;
    const panel=document.createElement('div');panel.id='v96CoachAlerts';panel.className='card v96-alert-panel';
    panel.innerHTML='<div class="section-title"><div><h3>Centro de alertas</h3><div class="muted tiny">Lo que requiere tu atención, ordenado por prioridad.</div></div><button class="btn small" onclick="refreshCoachAlertsV96(true)">Actualizar</button></div><div id="v96CoachAlertBody"><div class="empty">Cargando alertas…</div></div>';
    hero.insertAdjacentElement('afterend',panel);
    refreshCoachAlertsV96(false);
  }
  window.setCoachAlertFilterV96=function(v){coachFilterV96=v;renderCoachAlertsV96()};
  window.toggleCoachUnreadV96=function(){coachUnreadV96=!coachUnreadV96;renderCoachAlertsV96()};
  window.readCoachAlertV96=async function(key){
    const payload={coach_id:currentUser.id,event_key:key,read_at:new Date().toISOString(),dismissed_at:null};
    const {error}=await supabaseClient.from('coach_feed_state').upsert(payload,{onConflict:'coach_id,event_key'});
    if(error){toast(cloudErr(error));return}
    const x=coachAlertsV96.find(a=>a.event_key===key);if(x)x.is_read=true;
    coachFeedLoadedAt=0;renderCoachAlertsV96();updateCoachBellV96();
  };
  window.dismissCoachAlertV96=async function(key){
    const payload={coach_id:currentUser.id,event_key:key,dismissed_at:new Date().toISOString()};
    const {error}=await supabaseClient.from('coach_feed_state').upsert(payload,{onConflict:'coach_id,event_key'});
    if(error){toast(cloudErr(error));return}
    coachAlertsV96=coachAlertsV96.filter(x=>x.event_key!==key);coachFeedLoadedAt=0;renderCoachAlertsV96();updateCoachBellV96();
  };
  window.readAllCoachAlertsV96=async function(){
    const rows=coachAlertsV96.filter(x=>!x.is_read).map(x=>({coach_id:currentUser.id,event_key:x.event_key,read_at:new Date().toISOString(),dismissed_at:null}));
    if(!rows.length)return;
    const {error}=await supabaseClient.from('coach_feed_state').upsert(rows,{onConflict:'coach_id,event_key'});
    if(error){toast(cloudErr(error));return}
    coachAlertsV96.forEach(x=>x.is_read=true);coachFeedLoadedAt=0;renderCoachAlertsV96();updateCoachBellV96();toast('Alertas marcadas como leídas');
  };
  window.openCoachAlertV96=async function(athleteId,key,kind){
    await readCoachAlertV96(key);
    const row=[...cloudAthletes.values()].find(x=>x.id===athleteId);if(!row){toast('No encuentro esa ficha');return}
    state.selectedStudentId=row.client_id;saveState();coachTab='student';
    coachStudentTab=kind==='nutrition'?'nutrition':kind==='progression'?'progress':'tracking';
    render();
  };
  window.refreshCoachAlertsV96=refreshCoachAlertsV96;

  function updateCoachBellV96(){
    if(currentProfile?.role!=='coach')return;
    const n=coachAlertsV96.filter(x=>!x.is_read).length;
    let btn=el('v96CoachBell');
    const hero=el('view')?.querySelector('.hero');
    if(!hero)return;
    if(!btn){
      btn=document.createElement('button');btn.id='v96CoachBell';btn.className='btn ghost small v96-bell';btn.onclick=function(){coachTab='dashboard';render()};
      btn.innerHTML='Alertas<span id="v96CoachBellCount" class="v96-bell-count"></span>';
      const actions=hero.querySelector('.pill-row');if(actions)actions.prepend(btn);else hero.appendChild(btn);
    }
    const b=el('v96CoachBellCount');if(b){b.textContent=n>99?'99+':String(n);b.style.display=n?'flex':'none'}
  }

  async function loadStudentAlertsV96(force=false){
    if(currentProfile?.role!=='student'||!supabaseClient)return[];
    if(!force&&Date.now()-studentAlertsLoadedAtV96<15000)return studentAlertsV96;
    const {data,error}=await supabaseClient.rpc('get_student_alerts');
    if(error)throw error;
    studentAlertsV96=data||[];studentAlertsLoadedAtV96=Date.now();
    return studentAlertsV96;
  }
  function studentAlertCardV96(x,compact=false){
    return '<div class="'+(compact?'v96-preview-row':'v96-alert-card '+esc(x.severity||'info')+' '+(x.is_read?'':'unread'))+'">'+
      (compact?'':'<div class="v96-alert-icon">'+esc(iconV96(x.category))+'</div>')+
      '<div style="min-width:0"><strong>'+esc(x.title||'Aviso')+'</strong><div class="v96-alert-meta">'+esc(labelV96(x.category))+' · '+esc(relativeV96(x.occurred_at))+'</div>'+
      (x.body?'<div class="v96-alert-body">'+esc(x.body)+'</div>':'')+'</div>'+
      (compact?'':'<div class="v96-alert-actions"><button class="btn small" onclick="openStudentAlertActionV96(\''+escAttrV96(x.event_key)+'\',\''+escAttrV96(x.action_target||'home')+'\')">'+esc(x.action_label||'Abrir')+'</button>'+(!x.is_read?'<button class="btn ghost small" onclick="readStudentAlertV96(\''+escAttrV96(x.event_key)+'\')">Leído</button>':'')+'<button class="btn ghost small" onclick="dismissStudentAlertV96(\''+escAttrV96(x.event_key)+'\')">Ocultar</button></div>')+
      '</div>';
  }
  async function updateStudentAlertsV96(force=false){
    try{
      await loadStudentAlertsV96(force);
      const unread=studentAlertsV96.filter(x=>!x.is_read).length;
      const count=el('v96StudentBellCount');if(count){count.textContent=unread>99?'99+':String(unread);count.style.display=unread?'flex':'none'}
      if(studentTab==='home')injectStudentAlertPreviewV96();
    }catch(e){console.warn('student alerts',e)}
  }
  function injectStudentBellV96(){
    if(currentProfile?.role!=='student')return;
    const hero=el('view')?.querySelector('.hero');if(!hero||el('v96StudentBell'))return;
    const btn=document.createElement('button');btn.id='v96StudentBell';btn.className='btn ghost small v96-bell';
    btn.innerHTML='🔔 Avisos<span id="v96StudentBellCount" class="v96-bell-count"></span>';
    btn.onclick=openStudentAlertsV96;
    hero.appendChild(btn);
    updateStudentAlertsV96(false);
  }
  function injectStudentAlertPreviewV96(){
    if(currentProfile?.role!=='student'||studentTab!=='home')return;
    document.querySelectorAll('#v96StudentPreview').forEach(n=>n.remove());
    const unread=studentAlertsV96.filter(x=>!x.is_read);
    if(!unread.length)return;
    const hero=el('view')?.querySelector('.hero');if(!hero)return;
    const card=document.createElement('div');card.id='v96StudentPreview';card.className='card v96-student-preview';
    card.innerHTML='<div class="section-title"><div><h3>Avisos para vos</h3><div class="muted tiny">'+unread.length+' sin leer</div></div><button class="btn small" onclick="openStudentAlertsV96()">Ver todos</button></div>'+unread.slice(0,3).map(x=>studentAlertCardV96(x,true)).join('');
    hero.insertAdjacentElement('afterend',card);
  }
  window.openStudentAlertsV96=async function(){
    showModal('<div class="v96-center-head"><div><h3 style="margin:0">Centro de avisos</h3><div class="muted tiny">Entrenamientos, recordatorios y mensajes de tu coach.</div></div><button class="btn small" onclick="closeModal()">✕</button></div><div id="v96StudentAlertModal"><div class="empty">Cargando avisos…</div></div>');
    try{await loadStudentAlertsV96(true);renderStudentAlertModalV96()}catch(e){const h=el('v96StudentAlertModal');if(h)h.innerHTML='<div class="empty">'+esc(cloudErr(e))+'</div>'}
  };
  function renderStudentAlertModalV96(){
    const h=el('v96StudentAlertModal');if(!h)return;
    const unread=studentAlertsV96.filter(x=>!x.is_read).length;
    h.innerHTML='<div class="v96-alert-tools">'+(unread?'<button class="btn ghost small" onclick="readAllStudentAlertsV96()">Marcar todo leído</button>':'')+'<span class="muted tiny">'+unread+' sin leer · '+studentAlertsV96.length+' activas</span></div><div class="v96-alert-list">'+(studentAlertsV96.length?studentAlertsV96.map(x=>studentAlertCardV96(x,false)).join(''):'<div class="v96-empty">No tenés avisos pendientes.</div>')+'</div>';
  }
  window.readStudentAlertV96=async function(key){
    const payload={student_id:currentUser.id,event_key:key,read_at:new Date().toISOString(),dismissed_at:null};
    const {error}=await supabaseClient.from('student_alert_state').upsert(payload,{onConflict:'student_id,event_key'});
    if(error){toast(cloudErr(error));return}
    const x=studentAlertsV96.find(a=>a.event_key===key);if(x)x.is_read=true;
    studentAlertsLoadedAtV96=0;renderStudentAlertModalV96();updateStudentAlertsV96(false);
  };
  window.dismissStudentAlertV96=async function(key){
    const payload={student_id:currentUser.id,event_key:key,dismissed_at:new Date().toISOString()};
    const {error}=await supabaseClient.from('student_alert_state').upsert(payload,{onConflict:'student_id,event_key'});
    if(error){toast(cloudErr(error));return}
    studentAlertsV96=studentAlertsV96.filter(x=>x.event_key!==key);studentAlertsLoadedAtV96=0;renderStudentAlertModalV96();updateStudentAlertsV96(false);
  };
  window.readAllStudentAlertsV96=async function(){
    const rows=studentAlertsV96.filter(x=>!x.is_read).map(x=>({student_id:currentUser.id,event_key:x.event_key,read_at:new Date().toISOString(),dismissed_at:null}));
    if(rows.length){
      const {error}=await supabaseClient.from('student_alert_state').upsert(rows,{onConflict:'student_id,event_key'});
      if(error){toast(cloudErr(error));return}
    }
    studentAlertsV96.forEach(x=>x.is_read=true);studentAlertsLoadedAtV96=0;renderStudentAlertModalV96();updateStudentAlertsV96(false);toast('Avisos marcados como leídos');
  };
  window.openStudentAlertActionV96=async function(key,target){
    await readStudentAlertV96(key);closeModal();
    studentTab=target||'home';render();
  };

  async function loadCoachNoticesV96(){
    if(currentProfile?.role!=='coach'||coachTab!=='student')return;
    const ath=cloudAthletes.get(student()?.id),holder=el('v96NoticeList');if(!ath||!holder)return;
    const {data,error}=await supabaseClient.from('student_notices').select('*').eq('athlete_id',ath.id).eq('active',true).order('created_at',{ascending:false}).limit(8);
    if(error){holder.innerHTML='<div class="muted tiny">'+esc(cloudErr(error))+'</div>';return}
    holder.innerHTML=data?.length?data.map(n=>'<div class="v96-notice-item"><div><strong>'+esc(n.title)+'</strong><div class="muted tiny">'+esc(n.body||'')+'</div><div class="muted micro">'+(n.priority==='important'?'Importante':'Informativo')+' · '+esc(relativeV96(n.created_at))+'</div></div><button class="btn ghost small" onclick="disableStudentNoticeV96(\''+n.id+'\')">Quitar</button></div>').join(''):'<div class="muted tiny">No hay avisos manuales activos.</div>';
  }
  function injectCoachNoticeCardV96(){
    if(currentProfile?.role!=='coach'||coachTab!=='student'||coachStudentTab!=='summary')return;
    const host=el('coachStudentBody');if(!host||el('v96NoticeCoachCard'))return;
    const ath=cloudAthletes.get(student()?.id);if(!ath)return;
    const card=document.createElement('div');card.id='v96NoticeCoachCard';card.className='card v96-notice-card';
    card.innerHTML='<div class="section-title"><div><h3>Avisos al alumno</h3><div class="muted tiny">Mensajes importantes que aparecen en su centro de avisos.</div></div><button class="btn primary small" onclick="openSendStudentNoticeV96()">+ Enviar aviso</button></div><div id="v96NoticeList" class="v96-notice-list"><div class="muted tiny">Cargando…</div></div>';
    host.prepend(card);loadCoachNoticesV96();
  }
  window.openSendStudentNoticeV96=function(){
    const ath=cloudAthletes.get(student()?.id);if(!ath){toast('Vinculá primero la ficha');return}
    showModal('<div class="modal-head"><div><h3>Enviar aviso</h3><div class="muted tiny">'+esc(student().name)+'</div></div><button class="btn small" onclick="closeModal()">✕</button></div><div class="form-grid"><label class="tiny muted span2">Título<input id="v96NoticeTitle" class="input" placeholder="Ej: Actualicé tu rutina"></label><label class="tiny muted span2">Mensaje<textarea id="v96NoticeBody" class="input" rows="4" placeholder="Escribí un mensaje breve y claro"></textarea></label><label class="tiny muted">Prioridad<select id="v96NoticePriority" class="input"><option value="info">Informativo</option><option value="important">Importante</option></select></label><label class="tiny muted">Visible por<select id="v96NoticeDays" class="input"><option value="7">7 días</option><option value="14">14 días</option><option value="30">30 días</option><option value="0">Sin vencimiento</option></select></label></div><button class="btn primary" style="width:100%;margin-top:12px" onclick="sendStudentNoticeV96()">Enviar aviso</button>');
  };
  window.sendStudentNoticeV96=async function(){
    const ath=cloudAthletes.get(student()?.id);if(!ath)return;
    const title=el('v96NoticeTitle')?.value.trim(),body=el('v96NoticeBody')?.value.trim();
    if(!title||!body){toast('Completá título y mensaje');return}
    const days=Number(el('v96NoticeDays')?.value||0);
    const expires_at=days?new Date(Date.now()+days*86400000).toISOString():null;
    const payload={athlete_id:ath.id,coach_id:currentUser.id,title,body,priority:el('v96NoticePriority')?.value||'info',expires_at,active:true};
    const {error}=await supabaseClient.from('student_notices').insert(payload);
    if(error){toast(cloudErr(error));return}
    closeModal();loadCoachNoticesV96();toast('Aviso enviado al alumno');
  };
  window.disableStudentNoticeV96=async function(id){
    const {error}=await supabaseClient.from('student_notices').update({active:false,updated_at:new Date().toISOString()}).eq('id',id);
    if(error){toast(cloudErr(error));return}
    loadCoachNoticesV96();toast('Aviso quitado');
  };

  function injectAlertsV96(){
    document.querySelectorAll('#cloudFeedWrap').forEach(n=>n.remove());
    if(currentProfile?.role==='coach'){
      injectCoachAlertPanelV96();updateCoachBellV96();injectCoachNoticeCardV96();
    }else if(currentProfile?.role==='student'){
      injectStudentBellV96();updateStudentAlertsV96(false);
    }
  }

  const oldRenderV96=window.render;
  window.render=function(){
    oldRenderV96();
    setTimeout(injectAlertsV96,80);
    setTimeout(injectAlertsV96,500);
    setTimeout(injectAlertsV96,1100);
  };

  const oldSetupRealtimeV96=window.setupRealtime;
  if(typeof oldSetupRealtimeV96==='function'){
    window.setupRealtime=function(){
      const out=oldSetupRealtimeV96();
      if(!supabaseClient)return out;
      try{
        if(window.__fjzV96AlertChannel)supabaseClient.removeChannel(window.__fjzV96AlertChannel);
        const refresh=function(){
          coachFeedLoadedAt=0;studentAlertsLoadedAtV96=0;
          if(currentProfile?.role==='coach'){
            if(coachTab==='dashboard')setTimeout(()=>refreshCoachAlertsV96(true),250);
            if(coachTab==='student'&&coachStudentTab==='summary')setTimeout(loadCoachNoticesV96,250);
          }else if(currentProfile?.role==='student'){
            setTimeout(()=>updateStudentAlertsV96(true),250);
          }
        };
        window.__fjzV96AlertChannel=supabaseClient.channel('fjz-v96-alerts')
          .on('postgres_changes',{event:'*',schema:'public',table:'student_notices'},refresh)
          .on('postgres_changes',{event:'*',schema:'public',table:'weekly_checkins'},refresh)
          .on('postgres_changes',{event:'*',schema:'public',table:'athlete_reminders'},refresh)
          .on('postgres_changes',{event:'*',schema:'public',table:'athlete_schedule'},refresh)
          .on('postgres_changes',{event:'*',schema:'public',table:'nutrition_plans'},refresh)
          .on('postgres_changes',{event:'*',schema:'public',table:'exercise_feedback'},refresh)
          .subscribe();
      }catch(e){console.warn('alert realtime',e)}
      return out;
    };
  }

  Object.assign(window,{
    setCoachAlertFilterV96,toggleCoachUnreadV96,readCoachAlertV96,dismissCoachAlertV96,
    readAllCoachAlertsV96,openCoachAlertV96,refreshCoachAlertsV96,openStudentAlertsV96,
    readStudentAlertV96,dismissStudentAlertV96,readAllStudentAlertsV96,openStudentAlertActionV96,
    openSendStudentNoticeV96,sendStudentNoticeV96,disableStudentNoticeV96
  });

  setTimeout(injectAlertsV96,250);
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)
p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8").replace("team-fjz-v9-5","team-fjz-v9-6")
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V9.6 alertas pro:",len(html),"bytes")
