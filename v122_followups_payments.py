import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v122FollowupPaymentsStyles">
.v122-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px}
.v122-kpi{border:1px solid var(--border);border-radius:12px;padding:11px;background:var(--card)}
.v122-kpi strong{display:block;font-size:20px}.v122-kpi span{font-size:10px;color:var(--muted)}
.v122-row{display:grid;grid-template-columns:minmax(150px,1.5fr) 120px 120px 120px minmax(160px,1fr) auto;gap:8px;align-items:center;padding:10px 0;border-top:1px solid var(--border)}
.v122-row:first-child{border-top:0}.v122-money{font-weight:900}.v122-actions{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}
.v122-event{border:1px solid var(--border);border-radius:11px;padding:10px;margin-top:8px;background:rgba(255,255,255,.02)}
.v122-event.warning{border-color:rgba(233,162,59,.35)}.v122-event.success{border-color:rgba(69,179,107,.35)}
.v122-event-head{display:flex;justify-content:space-between;gap:8px;align-items:flex-start}
@media(max-width:900px){.v122-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.v122-row{grid-template-columns:1fr 1fr}.v122-actions{justify-content:flex-start}}
@media(max-width:520px){.v122-grid,.v122-row{grid-template-columns:1fr}}
</style>
"""

js=r"""
<script id="v122FollowupPaymentsRuntime">
(function(){
let followupCacheV122={checkins:[],payments:[]},followupLoadedV122=false;
const cadenceLabelV122={once:'Una vez',weekly:'Semanal',biweekly:'Cada 15 días',monthly:'Mensual'};
const methodLabelV122={cash:'Efectivo',transfer:'Transferencia',other:'Otro'};

function moneyV122(v){if(v===null||v===undefined||v==='')return '—';return '$'+Number(v).toLocaleString('es-AR',{maximumFractionDigits:2})}
function localDateV122(v){if(!v)return '—';const p=String(v).slice(0,10).split('-');return p.length===3?p[2]+'/'+p[1]+'/'+p[0]:v}
function todayISO122(){const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')}
function athleteNameV122(id){const row=[...cloudAthletes.values()].find(x=>x.id===id);return row?.name||state.students.find(s=>cloudAthletes.get(s.id)?.id===id)?.name||'Alumno'}
function athleteClientV122(id){return [...cloudAthletes.entries()].find(([,v])=>v.id===id)?.[0]||null}

async function loadFollowupsV122(force=false){
 if(followupLoadedV122&&!force)return followupCacheV122;
 const [c,p]=await Promise.all([
   supabaseClient.from('checkin_schedules').select('*').order('next_due'),
   supabaseClient.from('coach_payments').select('*').order('due_date',{ascending:false})
 ]);
 if(c.error)throw c.error;if(p.error)throw p.error;
 followupCacheV122={checkins:c.data||[],payments:p.data||[]};followupLoadedV122=true;return followupCacheV122;
}
function scheduleForAthleteV122(id){return followupCacheV122.checkins.find(x=>x.athlete_id===id)||null}
function paymentsForAthleteV122(id){return followupCacheV122.payments.filter(x=>x.athlete_id===id)}

window.saveCheckinScheduleV122=async function(){
 const ath=cloudAthletes.get(student().id);if(!ath)return;
 const cadence=el('v122Cadence')?.value||'weekly',date=el('v122NextDue')?.value,time=el('v122CheckTime')?.value||null;
 if(!date){toast('Elegí la próxima fecha');return}
 const payload={athlete_id:ath.id,coach_id:currentUser.id,cadence,next_due:date,remind_time:time,active:el('v122CheckActive')?.value!=='0',notes:(el('v122CheckNotes')?.value||'').trim(),updated_at:new Date().toISOString()};
 const {error}=await supabaseClient.from('checkin_schedules').upsert(payload,{onConflict:'athlete_id'});
 if(error){toast(cloudErr(error));return}
 followupLoadedV122=false;toast('Próximo check-in guardado');render();
};

async function injectStudentFollowupCoachV122(){
 if(currentProfile?.role!=='coach'||coachTab!=='student'||coachStudentTab!=='agenda')return;
 const host=el('coachStudentBody');if(!host||el('v122CheckinCard'))return;
 const ath=cloudAthletes.get(student().id);if(!ath)return;
 try{await loadFollowupsV122(true)}catch(e){return}
 const s=scheduleForAthleteV122(ath.id);
 const card=document.createElement('div');card.id='v122CheckinCard';card.className='card';card.style.marginBottom='14px';
 card.innerHTML='<div class="section-title"><div><h3>Próximo check-in</h3><div class="muted tiny">Elegí cuándo le corresponde. Al completarlo, la próxima fecha avanza sola según la frecuencia.</div></div><span class="badge blue">Dinámico</span></div>'+
 '<div class="form-grid">'+
 '<label class="tiny muted">Frecuencia<select id="v122Cadence" class="input"><option value="once">Una vez</option><option value="weekly">Semanal</option><option value="biweekly">Cada 15 días</option><option value="monthly">Mensual</option></select></label>'+
 '<label class="tiny muted">Próxima fecha<input id="v122NextDue" class="input" type="date" value="'+esc(s?.next_due||'')+'"></label>'+
 '<label class="tiny muted">Hora de alerta<input id="v122CheckTime" class="input" type="time" value="'+esc(s?.remind_time?String(s.remind_time).slice(0,5):'09:00')+'"></label>'+
 '<label class="tiny muted">Estado<select id="v122CheckActive" class="input"><option value="1">Activo</option><option value="0">Pausado</option></select></label>'+
 '<label class="tiny muted span2">Nota<input id="v122CheckNotes" class="input" value="'+esc(s?.notes||'')+'" placeholder="Ej: revisión quincenal"></label></div>'+
 '<button class="btn primary" style="width:100%;margin-top:12px" onclick="saveCheckinScheduleV122()">Guardar programación</button>';
 host.prepend(card);
 if(s){el('v122Cadence').value=s.cadence;el('v122CheckActive').value=s.active?'1':'0'}
}

window.openNewPaymentV122=function(clientId=''){
 if(clientId){state.selectedStudentId=clientId}
 const ath=cloudAthletes.get(student().id);if(!ath){toast('No encuentro la ficha');return}
 showModal('<div class="modal-head"><div><h3>Nueva cobranza</h3><div class="muted tiny">'+esc(student().name)+'</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
 '<div class="form-grid"><label class="tiny muted">Fecha de pago<input id="v122PayDue" class="input" type="date" value="'+todayISO122()+'"></label>'+
 '<label class="tiny muted">Importe opcional<input id="v122PayAmount" class="input" type="number" min="0" step="0.01" placeholder="Ej: 55000"></label>'+
 '<label class="tiny muted span2">Nota<input id="v122PayNote" class="input" placeholder="Ej: mensualidad octubre"></label></div>'+
 '<div class="muted tiny" style="margin-top:10px">La fecha aparecerá en la agenda del alumno y generará la alerta correspondiente.</div>'+
 '<button class="btn primary" style="width:100%;margin-top:14px" onclick="saveNewPaymentV122()">Guardar cobranza</button>');
};
window.saveNewPaymentV122=async function(){
 const ath=cloudAthletes.get(student().id);if(!ath)return;
 const due=el('v122PayDue')?.value;if(!due){toast('Elegí una fecha');return}
 const raw=el('v122PayAmount')?.value;
 const {error}=await supabaseClient.from('coach_payments').insert({athlete_id:ath.id,coach_id:currentUser.id,due_date:due,amount:raw?Number(raw):null,status:'pending',note:(el('v122PayNote')?.value||'').trim()});
 if(error){toast(cloudErr(error));return}followupLoadedV122=false;closeModal();toast('Cobranza agendada');render();
};
window.openMarkPaidV122=function(id){
 const p=followupCacheV122.payments.find(x=>x.id===id);if(!p)return;
 showModal('<div class="modal-head"><div><h3>Marcar abonado</h3><div class="muted tiny">'+esc(athleteNameV122(p.athlete_id))+'</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
 '<div class="form-grid"><label class="tiny muted">Fecha de pago<input id="v122PaidOn" class="input" type="date" value="'+todayISO122()+'"></label>'+
 '<label class="tiny muted">Forma<select id="v122Method" class="input"><option value="transfer">Transferencia</option><option value="cash">Efectivo</option><option value="other">Otro</option></select></label></div>'+
 '<button class="btn primary" style="width:100%;margin-top:14px" onclick="markPaidV122(\''+id+'\')">Confirmar pago</button>');
};
window.markPaidV122=async function(id){
 const {error}=await supabaseClient.from('coach_payments').update({status:'paid',paid_on:el('v122PaidOn')?.value||todayISO122(),payment_method:el('v122Method')?.value||'other',updated_at:new Date().toISOString()}).eq('id',id);
 if(error){toast(cloudErr(error));return}followupLoadedV122=false;closeModal();toast('Pago registrado');render();
};
window.deletePaymentV122=async function(id){
 if(!confirm('¿Eliminar este registro de cobranza?'))return;
 const {error}=await supabaseClient.from('coach_payments').delete().eq('id',id);
 if(error){toast(cloudErr(error));return}followupLoadedV122=false;toast('Cobranza eliminada');render();
};

window.renderCoachPaymentsV122=async function(){
 const v=el('view');v.innerHTML='<section class="hero"><div><h2>Pagos y cobranzas</h2><p>Control simple de vencimientos y pagos recibidos.</p></div><div class="pill-row"><button class="btn primary" onclick="openPaymentPickerV122()">+ Cobranza</button></div></section><div id="v122PaymentsBody"><div class="empty">Cargando…</div></div>';
 try{await loadFollowupsV122(true);const ps=followupCacheV122.payments,t=todayISO122(),month=t.slice(0,7);
 const pending=ps.filter(x=>x.status==='pending'),over=pending.filter(x=>x.due_date<t),paidMonth=ps.filter(x=>x.status==='paid'&&String(x.paid_on||'').startsWith(month));
 el('v122PaymentsBody').innerHTML='<div class="v122-grid"><div class="v122-kpi"><strong>'+pending.length+'</strong><span>Pendientes</span></div><div class="v122-kpi"><strong>'+over.length+'</strong><span>Vencidos</span></div><div class="v122-kpi"><strong>'+paidMonth.length+'</strong><span>Pagados este mes</span></div><div class="v122-kpi"><strong>'+moneyV122(paidMonth.reduce((a,x)=>a+(Number(x.amount)||0),0))+'</strong><span>Cobrado este mes</span></div></div><div class="card" style="margin-top:14px"><div class="section-title"><div><h3>Movimientos</h3><div class="muted tiny">Solo control administrativo. No procesa pagos.</div></div></div>'+
 (ps.length?ps.map(p=>'<div class="v122-row"><div><strong>'+esc(athleteNameV122(p.athlete_id))+'</strong><div class="muted micro">'+esc(p.note||'')+'</div></div><div><strong>'+localDateV122(p.due_date)+'</strong><div class="muted micro">Vencimiento</div></div><div class="v122-money">'+moneyV122(p.amount)+'</div><div><span class="badge '+(p.status==='paid'?'green':p.due_date<t?'red':'amber')+'">'+(p.status==='paid'?'Pagado':p.due_date<t?'Vencido':'Pendiente')+'</span></div><div class="muted tiny">'+(p.status==='paid'?(localDateV122(p.paid_on)+' · '+(methodLabelV122[p.payment_method]||'Otro')):'—')+'</div><div class="v122-actions">'+(p.status!=='paid'?'<button class="btn primary small" onclick="openMarkPaidV122(\''+p.id+'\')">Abonado</button>':'')+'<button class="btn ghost small" onclick="deletePaymentV122(\''+p.id+'\')">Eliminar</button></div></div>').join(''):'<div class="empty">Todavía no cargaste cobranzas.</div>')+'</div>';
 }catch(e){el('v122PaymentsBody').innerHTML='<div class="empty">'+esc(cloudErr(e))+'</div>'}
};
window.openPaymentPickerV122=function(){
 showModal('<div class="modal-head"><div><h3>Elegir alumno</h3></div><button class="btn small" onclick="closeModal()">✕</button></div><div class="v81-reminders">'+state.students.map(s=>'<button class="btn" style="width:100%;justify-content:flex-start" onclick="closeModal();openNewPaymentV122(\''+s.id+'\')">'+esc(s.name)+'</button>').join('')+'</div>');
};

async function upcomingEventsV122(athleteId=null,days=30){
 await loadFollowupsV122(true);const start=todayISO122(),end=new Date();end.setDate(end.getDate()+days);const endIso=end.toISOString().slice(0,10);
 const cs=followupCacheV122.checkins.filter(x=>x.active&&(athleteId?x.athlete_id===athleteId:true)&&x.next_due>=start&&x.next_due<=endIso);
 const ps=followupCacheV122.payments.filter(x=>x.status==='pending'&&(athleteId?x.athlete_id===athleteId:true)&&x.due_date>=start&&x.due_date<=endIso);
 return {cs,ps};
}
async function injectCoachAgendaFollowupsV122(){
 if(currentProfile?.role!=='coach'||coachTab!=='agenda')return;
 const b=el('v81CoachAgendaBody');if(!b||el('v122AgendaFollowups'))return;
 try{const e=await upcomingEventsV122(null,30);const box=document.createElement('div');box.id='v122AgendaFollowups';box.className='card';box.style.marginTop='14px';
 box.innerHTML='<div class="section-title"><div><h3>Próximos seguimientos y cobranzas</h3><div class="muted tiny">Próximos 30 días.</div></div></div>'+
 [...e.cs.map(x=>({date:x.next_due,type:'Check-in',name:athleteNameV122(x.athlete_id),extra:cadenceLabelV122[x.cadence]})),...e.ps.map(x=>({date:x.due_date,type:'Pago',name:athleteNameV122(x.athlete_id),extra:moneyV122(x.amount)}))].sort((a,b)=>a.date.localeCompare(b.date)).map(x=>'<div class="v122-event"><div class="v122-event-head"><div><strong>'+esc(x.name)+' · '+esc(x.type)+'</strong><div class="muted tiny">'+esc(x.extra||'')+'</div></div><span class="badge blue">'+localDateV122(x.date)+'</span></div></div>').join('')||'<div class="empty">No hay eventos próximos.</div>';
 b.appendChild(box)}catch(e){}
}
async function injectStudentAgendaFollowupsV122(){
 if(currentProfile?.role!=='student'||studentTab!=='agenda')return;
 const host=el('studentSubBody');if(!host||el('v122StudentEvents'))return;const ath=currentAthleteRowV73?.();if(!ath)return;
 try{const e=await upcomingEventsV122(ath.id,45);const box=document.createElement('div');box.id='v122StudentEvents';box.className='card';box.style.marginTop='14px';
 box.innerHTML='<div class="section-title"><div><h3>Próximas fechas</h3><div class="muted tiny">Check-ins y fechas de pago agendadas por tu coach.</div></div></div>'+
 e.cs.map(x=>'<div class="v122-event"><div class="v122-event-head"><div><strong>Check-in</strong><div class="muted tiny">'+esc(cadenceLabelV122[x.cadence]||'')+'</div></div><span class="badge blue">'+localDateV122(x.next_due)+'</span></div></div>').concat(
 e.ps.map(x=>'<div class="v122-event"><div class="v122-event-head"><div><strong>Fecha de pago</strong><div class="muted tiny">'+moneyV122(x.amount)+'</div></div><span class="badge blue">'+localDateV122(x.due_date)+'</span></div></div>')
 ).join('')||'<div class="empty">No tenés fechas próximas agendadas.</div>';
 host.appendChild(box)}catch(e){}
}

const baseRenderCoachStudentV122=window.renderCoachStudentAgendaV81;
window.renderCoachStudentAgendaV81=async function(){await baseRenderCoachStudentV122.apply(this,arguments);setTimeout(injectStudentFollowupCoachV122,40)};
const baseCoachAgendaV122=window.renderCoachAgendaV81;
window.renderCoachAgendaV81=async function(){await baseCoachAgendaV122.apply(this,arguments);setTimeout(injectCoachAgendaFollowupsV122,50)};
const baseStudentAgendaV122=window.renderStudentAgendaV81;
window.renderStudentAgendaV81=async function(){await baseStudentAgendaV122.apply(this,arguments);setTimeout(injectStudentAgendaFollowupsV122,50)};

const baseCoachRenderV122=window.renderCoach;
window.renderCoach=function(){if(coachTab==='payments')return renderCoachPaymentsV122();return baseCoachRenderV122.apply(this,arguments)};
const baseBottomV122=window.renderBottomNav;
window.renderBottomNav=function(){
 if(mode==='coach'){
  const nav=el('bottomNav');nav.innerHTML='<button class="'+(coachTab==='dashboard'?'active':'')+'" onclick="coachTab=\'dashboard\';render()">Alumnos</button><button class="'+(coachTab==='agenda'?'active':'')+'" onclick="coachTab=\'agenda\';render()">Agenda</button><button class="'+(coachTab==='payments'?'active':'')+'" onclick="coachTab=\'payments\';render()">Pagos</button><button onclick="showTemplates()">Plantillas</button><button class="'+(coachTab==='music'?'active':'')+'" onclick="coachTab=\'music\';render()">Música</button><button onclick="newStudent()">+ Alumno</button>';return;
 }
 return baseBottomV122.apply(this,arguments)
};

const baseSetupV122=window.setupRealtime;
window.setupRealtime=function(){
 const r=baseSetupV122.apply(this,arguments);if(!supabaseClient)return r;
 try{
  if(window.__fjzV122Channel)supabaseClient.removeChannel(window.__fjzV122Channel);
  window.__fjzV122Channel=supabaseClient.channel('fjz-v122-followups')
   .on('postgres_changes',{event:'*',schema:'public',table:'checkin_schedules'},()=>{followupLoadedV122=false;setTimeout(()=>render(),250)})
   .on('postgres_changes',{event:'*',schema:'public',table:'coach_payments'},()=>{followupLoadedV122=false;setTimeout(()=>render(),250)})
   .subscribe();
 }catch(e){console.warn('V12.2 realtime',e)}
 return r;
};

window.__fjzFollowupsV122={version:'12.2',checkins:true,payments:true};
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)
html=re.sub(r"TEAM FJZ V\d+(?:\.\d+)+","TEAM FJZ V12.2",html)
p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8")
sw=re.sub(r"team-fjz-v\d+(?:-\d+)+","team-fjz-v12-2",sw)
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V12.2 check-ins + cobranzas:",len(html),"bytes")
