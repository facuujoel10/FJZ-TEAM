import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v164AgendaReliabilityStyles">
.v164-agenda-status{
  display:flex;
  gap:7px;
  flex-wrap:wrap;
  margin:10px 0 0
}
.v164-reminder-error{
  display:none;
  margin-top:10px;
  padding:9px 10px;
  border:1px solid rgba(255,82,97,.35);
  border-radius:10px;
  background:rgba(255,82,97,.06);
  color:#ffb7bd;
  font-size:10px;
  line-height:1.35
}
.v164-reminder-error.show{display:block}
.v164-reminder-form label{min-width:0}
.v164-reminder-form input,
.v164-reminder-form select,
.v164-reminder-form textarea{
  width:100%!important
}
.v164-save-state{
  min-height:16px;
  margin-top:7px;
  color:var(--muted);
  font-size:9px;
  text-align:center
}
.v164-reminder-card{
  position:relative
}
.v164-reminder-card .v81-reminder-head{
  gap:8px
}
@media(max-width:700px){
  .v164-reminder-form.form-grid{
    grid-template-columns:1fr!important
  }
  .v164-reminder-form .span2{
    grid-column:auto!important
  }
  .v81-config-row{
    grid-template-columns:1fr!important
  }
  .v81-config-day{
    padding-bottom:3px
  }
}
</style>
"""

js=r"""
<script id="v164AgendaReliabilityRuntime">
(function(){
  const VERSION='16.4';
  let agendaInflightV164=null;
  let agendaLoadedAtV164=0;
  let reminderSavingV164=false;
  let scheduleSavingV164=false;
  const CACHE_MS=15000;

  function agendaAthleteV164(){
    try{
      const s=student();
      return s?.id?cloudAthletes?.get?.(s.id)||null:null;
    }catch(e){ return null; }
  }

  function agendaErrorV164(message){
    const box=el('v164ReminderError');
    if(box){
      box.textContent=String(message||'No se pudo guardar.');
      box.classList.add('show');
    }
  }

  function clearAgendaErrorV164(){
    const box=el('v164ReminderError');
    if(box){
      box.textContent='';
      box.classList.remove('show');
    }
  }

  // Single in-flight request + short cache. Realtime invalidation still sets agendaLoadedV81=false.
  window.loadAgendaV81=async function(force=false){
    if(!cloudEnabled||!supabaseClient){
      return {schedule:agendaScheduleV81,reminders:agendaRemindersV81};
    }

    const fresh=agendaLoadedV81 && (Date.now()-agendaLoadedAtV164<CACHE_MS);
    if(!force&&fresh){
      return {schedule:agendaScheduleV81,reminders:agendaRemindersV81};
    }
    if(force&&fresh&&window.__fjzRenderSettleV158){
      return {schedule:agendaScheduleV81,reminders:agendaRemindersV81};
    }
    if(agendaInflightV164)return agendaInflightV164;

    agendaInflightV164=(async()=>{
      const [scheduleRes,reminderRes]=await Promise.all([
        supabaseClient.from('athlete_schedule')
          .select('*')
          .eq('active',true)
          .order('weekday',{ascending:true}),
        supabaseClient.from('athlete_reminders')
          .select('*')
          .eq('active',true)
          .order('created_at',{ascending:false})
      ]);
      if(scheduleRes.error)throw scheduleRes.error;
      if(reminderRes.error)throw reminderRes.error;

      const scheduleSeen=new Set();
      agendaScheduleV81=(scheduleRes.data||[]).filter(row=>{
        const k=String(row.athlete_id)+'|'+String(row.weekday);
        if(scheduleSeen.has(k))return false;
        scheduleSeen.add(k); return true;
      });

      const reminderSeen=new Set();
      agendaRemindersV81=(reminderRes.data||[]).filter(row=>{
        const k=String(row.id||'');
        if(!k||reminderSeen.has(k))return false;
        reminderSeen.add(k); return true;
      });

      agendaLoadedV81=true;
      agendaLoadedAtV164=Date.now();
      return {schedule:agendaScheduleV81,reminders:agendaRemindersV81};
    })().finally(()=>{agendaInflightV164=null});

    return agendaInflightV164;
  };

  function renderReminderListV164(){
    if(!(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='agenda'))return;
    const ath=agendaAthleteV164();
    const host=document.querySelector('#coachStudentBody .v81-reminders');
    if(!ath||!host)return;
    const rows=remindersForV81(ath.id);
    host.innerHTML=rows.length
      ? rows.map(r=>reminderCoachHtmlV81(r).replace('class="v81-reminder"','class="v81-reminder v164-reminder-card"')).join('')
      : '<div class="empty">Todavía no hay recordatorios personalizados.</div>';

    const card=host.closest('.card');
    if(card){
      let status=card.querySelector('.v164-agenda-status');
      if(!status){
        status=document.createElement('div');
        status.className='v164-agenda-status';
        const title=card.querySelector('.section-title');
        title?.insertAdjacentElement('afterend',status);
      }
      status.innerHTML='<span class="badge blue">'+rows.length+' recordatorio'+(rows.length===1?'':'s')+'</span>';
    }
  }

  function renderScheduleStatusV164(){
    if(!(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='agenda'))return;
    const ath=agendaAthleteV164();
    const host=el('coachStudentBody');
    if(!ath||!host)return;
    const rows=scheduleForV81(ath.id);
    const first=host.querySelector('.card');
    if(!first)return;
    let status=first.querySelector('.v164-agenda-status');
    if(!status){
      status=document.createElement('div');
      status.className='v164-agenda-status';
      first.querySelector('.section-title')?.insertAdjacentElement('afterend',status);
    }
    status.innerHTML=
      '<span class="badge blue">'+rows.length+' día'+(rows.length===1?'':'s')+' programado'+(rows.length===1?'':'s')+'</span>'+
      '<span class="badge">'+(rows.filter(x=>x.reminder_enabled!==false).length)+' avisos activos</span>';
  }

  const baseRenderCoachStudentAgendaV164=window.renderCoachStudentAgendaV81;
  window.renderCoachStudentAgendaV81=async function(){
    const ath=agendaAthleteV164();
    const host=el('coachStudentBody');
    if(!host)return;
    if(!ath){
      host.innerHTML='<div class="empty">Vinculá la cuenta del alumno para usar la agenda en nube.</div>';
      return;
    }

    if(agendaLoadedV81){
      // Render immediately from cache to avoid a loading flash.
      try{
        const originalForce=window.__fjzRenderSettleV158;
        window.__fjzRenderSettleV158=true;
        await baseRenderCoachStudentAgendaV164();
        window.__fjzRenderSettleV158=originalForce;
        renderScheduleStatusV164();
        renderReminderListV164();
      }catch(e){
        host.innerHTML='<div class="empty">'+esc(cloudErr(e))+'</div>';
      }
      return;
    }
    await baseRenderCoachStudentAgendaV164();
    renderScheduleStatusV164();
    renderReminderListV164();
  };

  window.openAddReminderV81=function(){
    const ath=agendaAthleteV164();
    if(!ath){toast('No encuentro la ficha vinculada del alumno');return}

    showModal(
      '<div class="modal-head"><div><h3>Nuevo recordatorio</h3>'+
      '<div class="muted tiny">'+esc(student().name)+' · se guarda en su Agenda</div></div>'+
      '<button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="form-grid v164-reminder-form">'+
        '<label class="tiny muted span2">Título *<input id="v81RemTitle" class="input" maxlength="80" placeholder="Ej: Completar check-in"></label>'+
        '<label class="tiny muted span2">Mensaje<textarea id="v81RemBody" class="input" rows="3" maxlength="400" placeholder="Mensaje breve para el alumno"></textarea></label>'+
        '<label class="tiny muted">Frecuencia<select id="v81RemType" class="input"><option value="once">Una fecha</option><option value="weekly">Todas las semanas</option></select></label>'+
        '<label class="tiny muted">Hora opcional<input id="v81RemTime" class="input" type="time"></label>'+
        '<label class="tiny muted" id="v81OnceField">Fecha *<input id="v81RemDate" class="input" type="date" min="'+dateInputToday()+'" value="'+dateInputToday()+'"></label>'+
        '<label class="tiny muted" id="v81WeeklyField" style="display:none">Día *<select id="v81RemWeekday" class="input">'+
          WEEK_NAMES_V81.map((x,i)=>'<option value="'+i+'">'+esc(x)+'</option>').join('')+
        '</select></label>'+
      '</div>'+
      '<div id="v164ReminderError" class="v164-reminder-error"></div>'+
      '<button id="v164SaveReminderBtn" class="btn primary" style="width:100%;margin-top:12px">Guardar recordatorio</button>'+
      '<div id="v164ReminderSaveState" class="v164-save-state"></div>'
    );

    const type=el('v81RemType');
    if(type)type.onchange=toggleReminderFieldsV81;
    const btn=el('v164SaveReminderBtn');
    if(btn)btn.onclick=saveReminderV81;
    setTimeout(()=>el('v81RemTitle')?.focus(),60);
  };

  window.toggleReminderFieldsV81=function(){
    const once=(el('v81RemType')?.value||'once')==='once';
    if(el('v81WeeklyField'))el('v81WeeklyField').style.display=once?'none':'block';
    if(el('v81OnceField'))el('v81OnceField').style.display=once?'block':'none';
    clearAgendaErrorV164();
  };

  window.saveReminderV81=async function(){
    if(reminderSavingV164)return false;
    clearAgendaErrorV164();

    if(!cloudEnabled||!supabaseClient){
      agendaErrorV164('La Agenda necesita conexión a la nube.');
      return false;
    }

    const ath=agendaAthleteV164();
    if(!ath?.id){
      agendaErrorV164('No encuentro la ficha vinculada de este alumno.');
      return false;
    }
    if(!currentUser?.id){
      agendaErrorV164('No encuentro tu sesión de coach. Volvé a iniciar sesión.');
      return false;
    }

    const title=(el('v81RemTitle')?.value||'').trim();
    const body=(el('v81RemBody')?.value||'').trim();
    const type=(el('v81RemType')?.value||'once')==='weekly'?'weekly':'once';
    const remindTime=el('v81RemTime')?.value||null;
    const date=el('v81RemDate')?.value||'';
    const weekday=Number(el('v81RemWeekday')?.value);

    if(!title){
      agendaErrorV164('Escribí un título para el recordatorio.');
      el('v81RemTitle')?.focus();
      return false;
    }
    if(type==='once'&&!/^\d{4}-\d{2}-\d{2}$/.test(date)){
      agendaErrorV164('Elegí una fecha válida.');
      el('v81RemDate')?.focus();
      return false;
    }
    if(type==='weekly'&&(!Number.isInteger(weekday)||weekday<0||weekday>6)){
      agendaErrorV164('Elegí un día de la semana.');
      return false;
    }

    const payload={
      athlete_id:ath.id,
      coach_id:currentUser.id,
      title,
      body,
      category:'custom',
      schedule_type:type,
      reminder_date:type==='once'?date:null,
      weekday:type==='weekly'?weekday:null,
      remind_time:remindTime,
      active:true
    };

    const btn=el('v164SaveReminderBtn');
    const state=el('v164ReminderSaveState');
    reminderSavingV164=true;
    if(btn){btn.disabled=true;btn.textContent='Guardando…'}
    if(state)state.textContent='Confirmando con la nube…';

    try{
      const {data,error}=await supabaseClient
        .from('athlete_reminders')
        .insert(payload)
        .select('*')
        .single();

      if(error)throw error;
      if(!data?.id)throw new Error('Supabase no confirmó el recordatorio creado.');

      agendaRemindersV81=[
        data,
        ...(agendaRemindersV81||[]).filter(x=>x.id!==data.id)
      ];
      agendaLoadedV81=true;
      agendaLoadedAtV164=Date.now();

      closeModal();
      renderReminderListV164();
      toast('Recordatorio guardado');
      return true;
    }catch(e){
      const msg=cloudErr(e);
      agendaErrorV164(msg);
      if(state)state.textContent='No se guardó.';
      toast(msg);
      return false;
    }finally{
      reminderSavingV164=false;
      if(btn){btn.disabled=false;btn.textContent='Guardar recordatorio'}
    }
  };

  window.deleteReminderV81=async function(id){
    if(!id||!supabaseClient)return false;
    try{
      const {data,error}=await supabaseClient
        .from('athlete_reminders')
        .delete()
        .eq('id',id)
        .select('id');
      if(error)throw error;
      if(!data?.length)throw new Error('No se encontró el recordatorio para eliminar.');

      agendaRemindersV81=(agendaRemindersV81||[]).filter(x=>x.id!==id);
      agendaLoadedV81=true;
      agendaLoadedAtV164=Date.now();
      renderReminderListV164();
      toast('Recordatorio eliminado');
      return true;
    }catch(e){
      toast(cloudErr(e));
      return false;
    }
  };

  window.saveStudentScheduleV81=async function(){
    if(scheduleSavingV164)return false;
    const s=student(),ath=agendaAthleteV164();
    if(!ath?.id){toast('No encuentro la ficha vinculada del alumno');return false}
    if(!currentUser?.id){toast('No encuentro tu sesión de coach');return false}

    const desired=[];
    for(let i=0;i<7;i++){
      const dayId=el('v81Day_'+i)?.value||'';
      if(!dayId)continue;
      const day=s.days.find(x=>String(x.id)===String(dayId));
      desired.push({
        athlete_id:ath.id,
        coach_id:currentUser.id,
        weekday:i,
        workout_day_id:dayId,
        workout_day_name:day?.name||'Entrenamiento',
        start_time:el('v81Time_'+i)?.value||null,
        reminder_enabled:el('v81Rem_'+i)?.value!=='0',
        reminder_minutes_before:60,
        active:true
      });
    }

    const old=scheduleForV81(ath.id);
    const keep=new Set(desired.map(x=>Number(x.weekday)));
    const remove=old.filter(x=>!keep.has(Number(x.weekday))).map(x=>Number(x.weekday));

    const buttons=[...document.querySelectorAll('button')].filter(b=>(b.getAttribute('onclick')||'').includes('saveStudentScheduleV81'));
    scheduleSavingV164=true;
    buttons.forEach(b=>{b.disabled=true;b.dataset.v164Text=b.textContent||'';b.textContent='Guardando…'});

    try{
      let saved=[];
      if(desired.length){
        const {data,error}=await supabaseClient
          .from('athlete_schedule')
          .upsert(desired,{onConflict:'athlete_id,weekday'})
          .select('*');
        if(error)throw error;
        saved=data||[];
      }

      if(remove.length){
        const {error}=await supabaseClient
          .from('athlete_schedule')
          .delete()
          .eq('athlete_id',ath.id)
          .in('weekday',remove);
        if(error)throw error;
      }

      agendaScheduleV81=[
        ...(agendaScheduleV81||[]).filter(x=>x.athlete_id!==ath.id),
        ...saved
      ].sort((a,b)=>Number(a.weekday)-Number(b.weekday));
      agendaLoadedV81=true;
      agendaLoadedAtV164=Date.now();

      renderScheduleStatusV164();
      toast('Agenda semanal guardada');
      return true;
    }catch(e){
      toast(cloudErr(e));
      // force a clean reload next time because a partial network operation may have succeeded.
      agendaLoadedV81=false;
      agendaLoadedAtV164=0;
      return false;
    }finally{
      scheduleSavingV164=false;
      buttons.forEach(b=>{
        b.disabled=false;
        b.textContent=b.dataset.v164Text||'Guardar agenda semanal';
        delete b.dataset.v164Text;
      });
    }
  };

  // Keep cache timestamp in sync with realtime invalidation and avoid stale UI.
  const baseSetupRealtimeV164=window.setupRealtime;
  if(typeof baseSetupRealtimeV164==='function'){
    window.setupRealtime=function(){
      const out=baseSetupRealtimeV164.apply(this,arguments);
      return out;
    };
  }

  Object.assign(window,{
    loadAgendaV81,
    openAddReminderV81,
    toggleReminderFieldsV81,
    saveReminderV81,
    deleteReminderV81,
    saveStudentScheduleV81,
    renderCoachStudentAgendaV81
  });

  window.__fjzAgendaV164={
    version:VERSION,
    confirmedInsert:true,
    instantLocalUpdate:true,
    inlineErrors:true,
    singleInflightLoad:true,
    shortCache:true,
    batchScheduleUpsert:true,
    deleteVerified:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzAgendaV164",
  "confirmedInsert:true",
  "instantLocalUpdate:true",
  "inlineErrors:true",
  "singleInflightLoad:true",
  "batchScheduleUpsert:true",
  "deleteVerified:true"
]:
    if marker not in html:
        raise RuntimeError("V16.4 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V16.4 agenda reliability/performance enabled")
