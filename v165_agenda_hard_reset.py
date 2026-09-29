import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v165AgendaHardResetStyles">
.v165-agenda-shell{display:grid;gap:14px}
.v165-week-grid{display:grid;gap:8px}
.v165-week-row{
  display:grid;
  grid-template-columns:86px minmax(0,1fr) 110px 110px;
  gap:8px;
  align-items:end;
  padding:10px;
  border:1px solid var(--border);
  border-radius:12px;
  background:rgba(255,255,255,.02)
}
.v165-week-row .v165-day{
  font-weight:900;
  font-size:11px;
  align-self:center
}
.v165-rem-list{display:grid;gap:8px}
.v165-rem-card{
  padding:11px;
  border:1px solid var(--border);
  border-radius:12px;
  background:rgba(255,255,255,.02)
}
.v165-rem-top{
  display:flex;
  justify-content:space-between;
  gap:10px;
  align-items:flex-start
}
.v165-rem-top>div:first-child{min-width:0}
.v165-rem-top strong,.v165-rem-card p{overflow-wrap:anywhere}
.v165-rem-actions{margin-top:8px}
.v165-agenda-meta{
  display:flex;
  gap:6px;
  flex-wrap:wrap;
  margin-top:9px
}
.v165-form-error{
  display:none;
  margin-top:10px;
  padding:9px 10px;
  border:1px solid rgba(255,82,97,.35);
  border-radius:10px;
  background:rgba(255,82,97,.06);
  color:#ffb8bf;
  font-size:10px
}
.v165-form-error.show{display:block}
.v165-save-state{
  margin-top:7px;
  min-height:14px;
  text-align:center;
  color:var(--muted);
  font-size:9px
}
@media(max-width:760px){
  .v165-week-row{
    grid-template-columns:1fr;
    align-items:stretch
  }
  .v165-week-row .v165-day{
    padding-bottom:2px
  }
  .v165-rem-top{
    display:block
  }
  .v165-rem-top .badge{
    display:inline-flex;
    margin-top:6px
  }
}
</style>
"""

js=r"""
<script id="v165AgendaHardResetRuntime">
(function(){
  const VERSION='16.5';
  const cache=new Map();
  let reminderBusy=false;
  let scheduleBusy=false;
  let resolveBusy=null;

  function cacheRow(id){
    if(!cache.has(id))cache.set(id,{schedule:[],reminders:[],loadedAt:0,inflight:null});
    return cache.get(id);
  }

  async function resolveAthleteV165(){
    const s=student?.();
    if(!s?.id)throw new Error('No hay un alumno seleccionado.');

    let row=cloudAthletes?.get?.(s.id)||null;
    if(!row&&cloudAthletes?.values){
      row=[...cloudAthletes.values()].find(x=>String(x.client_id)===String(s.id))||null;
    }
    if(row?.id)return row;

    if(resolveBusy)return resolveBusy;
    resolveBusy=(async()=>{
      const {data,error}=await supabaseClient
        .from('athletes')
        .select('id,coach_id,user_id,client_id,name,goal')
        .eq('client_id',s.id)
        .eq('coach_id',currentUser.id)
        .maybeSingle();
      if(error)throw error;
      if(!data?.id)throw new Error('No encuentro la ficha vinculada de este alumno en la nube.');
      cloudAthletes?.set?.(data.client_id,data);
      return data;
    })().finally(()=>{resolveBusy=null});
    return resolveBusy;
  }

  async function fetchAgendaV165(athleteId,force=false){
    const box=cacheRow(athleteId);
    if(!force&&box.loadedAt&&Date.now()-box.loadedAt<15000)return box;
    if(box.inflight)return box.inflight;

    box.inflight=(async()=>{
      const [sRes,rRes]=await Promise.all([
        supabaseClient.from('athlete_schedule')
          .select('*')
          .eq('athlete_id',athleteId)
          .eq('active',true)
          .order('weekday',{ascending:true}),
        supabaseClient.from('athlete_reminders')
          .select('*')
          .eq('athlete_id',athleteId)
          .eq('active',true)
          .order('created_at',{ascending:false})
      ]);
      if(sRes.error)throw sRes.error;
      if(rRes.error)throw rRes.error;

      const seenS=new Set();
      box.schedule=(sRes.data||[]).filter(x=>{
        const k=String(x.weekday);
        if(seenS.has(k))return false;
        seenS.add(k); return true;
      });

      const seenR=new Set();
      box.reminders=(rRes.data||[]).filter(x=>{
        const k=String(x.id||'');
        if(!k||seenR.has(k))return false;
        seenR.add(k); return true;
      });

      box.loadedAt=Date.now();
      syncLegacyV165(athleteId,box);
      return box;
    })().finally(()=>{box.inflight=null});

    return box.inflight;
  }

  function syncLegacyV165(athleteId,box){
    agendaScheduleV81=[
      ...(agendaScheduleV81||[]).filter(x=>x.athlete_id!==athleteId),
      ...box.schedule
    ];
    agendaRemindersV81=[
      ...(agendaRemindersV81||[]).filter(x=>x.athlete_id!==athleteId),
      ...box.reminders
    ];
    agendaLoadedV81=true;
  }

  function whenTextV165(r){
    if(r.schedule_type==='weekly'){
      const day=WEEK_NAMES_V81[Number(r.weekday)]||'Semanal';
      return day+(r.remind_time?' · '+fmtTimeV81(r.remind_time):'');
    }
    return (r.reminder_date||'Sin fecha')+(r.remind_time?' · '+fmtTimeV81(r.remind_time):'');
  }

  function reminderHtmlV165(r){
    return '<div class="v165-rem-card" data-v165-reminder-id="'+esc(r.id)+'">'+
      '<div class="v165-rem-top"><div><strong>'+esc(r.title)+'</strong>'+
      '<div class="muted micro" style="margin-top:3px">'+esc(whenTextV165(r))+'</div></div>'+
      '<span class="badge blue">'+(r.schedule_type==='weekly'?'Semanal':'Una fecha')+'</span></div>'+
      (r.body?'<p class="muted tiny" style="margin:8px 0 0">'+esc(r.body)+'</p>':'')+
      '<div class="v165-rem-actions"><button class="btn ghost small" type="button" data-v165-action="delete-reminder" data-id="'+esc(r.id)+'">Eliminar</button></div>'+
    '</div>';
  }

  function renderEditorV165(athlete,box){
    const host=el('coachStudentBody');
    if(!host)return;
    const s=student();

    host.innerHTML='<div class="v165-agenda-shell">'+
      '<div class="card">'+
        '<div class="section-title"><div><h3>Programación semanal</h3>'+
        '<div class="muted tiny">Organizá los días de entrenamiento. No modifica la rutina.</div></div>'+
        '<span class="badge blue">Agenda</span></div>'+
        '<div class="v165-agenda-meta">'+
          '<span class="badge">'+box.schedule.length+' días programados</span>'+
          '<span class="badge">'+box.reminders.length+' recordatorios</span>'+
        '</div>'+
        '<div class="v165-week-grid" style="margin-top:10px">'+
          WEEK_NAMES_V81.map((name,i)=>{
            const row=box.schedule.find(x=>Number(x.weekday)===i);
            const options=(s.days||[]).map(d=>'<option value="'+esc(d.id)+'" '+(String(row?.workout_day_id||'')===String(d.id)?'selected':'')+'>'+esc(d.name)+'</option>').join('');
            return '<div class="v165-week-row">'+
              '<div class="v165-day">'+esc(name)+'</div>'+
              '<label class="tiny muted">Entrenamiento<select class="input" data-v165-day="'+i+'"><option value="">Descanso / sin programar</option>'+options+'</select></label>'+
              '<label class="tiny muted">Hora<input class="input" type="time" data-v165-time="'+i+'" value="'+(row?.start_time?esc(String(row.start_time).slice(0,5)):'')+'"></label>'+
              '<label class="tiny muted">Aviso<select class="input" data-v165-remind="'+i+'"><option value="1" '+(row?.reminder_enabled!==false?'selected':'')+'>Sí</option><option value="0" '+(row?.reminder_enabled===false?'selected':'')+'>No</option></select></label>'+
            '</div>';
          }).join('')+
        '</div>'+
        '<button class="btn primary" type="button" style="width:100%;margin-top:12px" data-v165-action="save-schedule">Guardar agenda semanal</button>'+
        '<div id="v165ScheduleState" class="v165-save-state"></div>'+
      '</div>'+
      '<div class="card">'+
        '<div class="section-title"><div><h3>Recordatorios</h3>'+
        '<div class="muted tiny">Aparecen en la Agenda del alumno según fecha o día semanal.</div></div>'+
        '<button class="btn primary small" type="button" data-v165-action="add-reminder">+ Recordatorio</button></div>'+
        '<div id="v165ReminderList" class="v165-rem-list" style="margin-top:10px">'+
          (box.reminders.length?box.reminders.map(reminderHtmlV165).join(''):'<div class="empty">Todavía no hay recordatorios.</div>')+
        '</div>'+
      '</div>'+
    '</div>';
  }

  async function renderCoachAgendaV165(){
    const host=el('coachStudentBody');
    if(!host)return;
    host.innerHTML='<div class="card"><div class="empty">Cargando agenda…</div></div>';

    try{
      const athlete=await resolveAthleteV165();
      const box=await fetchAgendaV165(athlete.id,false);
      if(!(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='agenda'))return;
      renderEditorV165(athlete,box);
    }catch(e){
      host.innerHTML='<div class="card"><div class="empty">'+esc(cloudErr(e))+'</div></div>';
    }
  }

  function openReminderModalV165(){
    showModal(
      '<div class="modal-head"><div><h3>Nuevo recordatorio</h3>'+
      '<div class="muted tiny">'+esc(student()?.name||'Alumno')+'</div></div>'+
      '<button class="btn small" type="button" onclick="closeModal()">✕</button></div>'+
      '<div class="form-grid">'+
        '<label class="tiny muted span2">Título *<input id="v165Title" class="input" maxlength="80" placeholder="Ej: Completar check-in"></label>'+
        '<label class="tiny muted span2">Mensaje<textarea id="v165Body" class="input" rows="3" maxlength="400" placeholder="Mensaje breve"></textarea></label>'+
        '<label class="tiny muted">Tipo<select id="v165Type" class="input"><option value="once">Una fecha</option><option value="weekly">Semanal</option></select></label>'+
        '<label class="tiny muted">Hora opcional<input id="v165Time" class="input" type="time"></label>'+
        '<label class="tiny muted" id="v165DateWrap">Fecha *<input id="v165Date" class="input" type="date" min="'+dateInputToday()+'" value="'+dateInputToday()+'"></label>'+
        '<label class="tiny muted" id="v165WeekWrap" style="display:none">Día *<select id="v165Weekday" class="input">'+
          WEEK_NAMES_V81.map((x,i)=>'<option value="'+i+'">'+esc(x)+'</option>').join('')+
        '</select></label>'+
      '</div>'+
      '<div id="v165Error" class="v165-form-error"></div>'+
      '<button class="btn primary" type="button" style="width:100%;margin-top:12px" data-v165-action="save-reminder">Guardar recordatorio</button>'+
      '<div id="v165ReminderState" class="v165-save-state"></div>'
    );

    const type=el('v165Type');
    if(type)type.addEventListener('change',()=>{
      const once=type.value==='once';
      if(el('v165DateWrap'))el('v165DateWrap').style.display=once?'block':'none';
      if(el('v165WeekWrap'))el('v165WeekWrap').style.display=once?'none':'block';
      hideErrorV165();
    });
    setTimeout(()=>el('v165Title')?.focus(),50);
  }

  function showErrorV165(msg){
    const box=el('v165Error');
    if(!box)return;
    box.textContent=String(msg||'No se pudo guardar.');
    box.classList.add('show');
  }
  function hideErrorV165(){
    const box=el('v165Error');
    if(box){box.textContent='';box.classList.remove('show')}
  }

  async function saveReminderV165(){
    if(reminderBusy)return;
    reminderBusy=true;
    hideErrorV165();

    const btn=document.querySelector('[data-v165-action="save-reminder"]');
    const state=el('v165ReminderState');
    if(btn){btn.disabled=true;btn.textContent='Guardando…'}
    if(state)state.textContent='Confirmando con Supabase…';

    try{
      const athlete=await resolveAthleteV165();
      const title=(el('v165Title')?.value||'').trim();
      const body=(el('v165Body')?.value||'').trim();
      const type=el('v165Type')?.value==='weekly'?'weekly':'once';
      const date=el('v165Date')?.value||'';
      const weekday=Number(el('v165Weekday')?.value);
      const time=el('v165Time')?.value||null;

      if(!title)throw new Error('Escribí un título.');
      if(type==='once'&&!/^\d{4}-\d{2}-\d{2}$/.test(date))throw new Error('Elegí una fecha válida.');
      if(type==='weekly'&&(!Number.isInteger(weekday)||weekday<0||weekday>6))throw new Error('Elegí un día válido.');

      const payload={
        athlete_id:athlete.id,
        coach_id:currentUser.id,
        title,
        body,
        category:'custom',
        schedule_type:type,
        reminder_date:type==='once'?date:null,
        weekday:type==='weekly'?weekday:null,
        remind_time:time,
        active:true
      };

      const {data,error}=await supabaseClient
        .from('athlete_reminders')
        .insert(payload)
        .select('*')
        .single();

      if(error)throw error;
      if(!data?.id)throw new Error('La nube no confirmó el recordatorio.');

      const box=cacheRow(athlete.id);
      box.reminders=[data,...box.reminders.filter(x=>x.id!==data.id)];
      box.loadedAt=Date.now();
      syncLegacyV165(athlete.id,box);

      closeModal();
      if(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='agenda'){
        renderEditorV165(athlete,box);
      }
      toast('Recordatorio guardado');
    }catch(e){
      showErrorV165(cloudErr(e));
      if(state)state.textContent='No se guardó.';
    }finally{
      reminderBusy=false;
      if(btn){btn.disabled=false;btn.textContent='Guardar recordatorio'}
    }
  }

  async function deleteReminderV165(id){
    if(!id)return;
    try{
      const athlete=await resolveAthleteV165();
      const {data,error}=await supabaseClient
        .from('athlete_reminders')
        .delete()
        .eq('id',id)
        .eq('athlete_id',athlete.id)
        .select('id');
      if(error)throw error;
      if(!data?.length)throw new Error('No se encontró el recordatorio.');

      const box=cacheRow(athlete.id);
      box.reminders=box.reminders.filter(x=>x.id!==id);
      box.loadedAt=Date.now();
      syncLegacyV165(athlete.id,box);
      renderEditorV165(athlete,box);
      toast('Recordatorio eliminado');
    }catch(e){
      toast(cloudErr(e));
    }
  }

  async function saveScheduleV165(){
    if(scheduleBusy)return;
    scheduleBusy=true;
    const btn=document.querySelector('[data-v165-action="save-schedule"]');
    const state=el('v165ScheduleState');
    if(btn){btn.disabled=true;btn.textContent='Guardando…'}
    if(state)state.textContent='Confirmando agenda…';

    try{
      const athlete=await resolveAthleteV165();
      const s=student();
      const desired=[];

      for(let i=0;i<7;i++){
        const dayId=document.querySelector('[data-v165-day="'+i+'"]')?.value||'';
        if(!dayId)continue;
        const day=(s.days||[]).find(x=>String(x.id)===String(dayId));
        desired.push({
          athlete_id:athlete.id,
          coach_id:currentUser.id,
          weekday:i,
          workout_day_id:dayId,
          workout_day_name:day?.name||'Entrenamiento',
          start_time:document.querySelector('[data-v165-time="'+i+'"]')?.value||null,
          reminder_enabled:document.querySelector('[data-v165-remind="'+i+'"]')?.value!=='0',
          reminder_minutes_before:60,
          active:true
        });
      }

      const box=cacheRow(athlete.id);
      const keep=new Set(desired.map(x=>Number(x.weekday)));
      const remove=box.schedule.filter(x=>!keep.has(Number(x.weekday))).map(x=>Number(x.weekday));

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
          .eq('athlete_id',athlete.id)
          .in('weekday',remove);
        if(error)throw error;
      }

      box.schedule=saved.sort((a,b)=>Number(a.weekday)-Number(b.weekday));
      box.loadedAt=Date.now();
      syncLegacyV165(athlete.id,box);
      renderEditorV165(athlete,box);
      toast('Agenda semanal guardada');
    }catch(e){
      if(state)state.textContent='No se guardó.';
      toast(cloudErr(e));
    }finally{
      scheduleBusy=false;
      if(btn){btn.disabled=false;btn.textContent='Guardar agenda semanal'}
    }
  }

  if(!window.__fjzAgendaV165Delegated){
    window.__fjzAgendaV165Delegated=true;
    document.addEventListener('click',e=>{
      const btn=e.target?.closest?.('[data-v165-action]');
      if(!btn)return;
      const action=btn.getAttribute('data-v165-action');
      if(action==='add-reminder'){e.preventDefault();openReminderModalV165();return}
      if(action==='save-reminder'){e.preventDefault();saveReminderV165();return}
      if(action==='delete-reminder'){e.preventDefault();deleteReminderV165(btn.getAttribute('data-id'));return}
      if(action==='save-schedule'){e.preventDefault();saveScheduleV165();return}
    },true);
  }

  const baseRenderCoachStudentV165=window.renderCoachStudent;
  window.renderCoachStudent=function(){
    if(coachStudentTab!=='agenda')return baseRenderCoachStudentV165.apply(this,arguments);
    const s=student(),v=el('view');
    v.innerHTML='<section class="hero"><div><button class="btn ghost small" onclick="coachTab=\'dashboard\';render()">← Alumnos</button>'+
      '<h2 style="margin-top:10px">'+esc(s.name)+'</h2><p>'+esc(s.goal)+' · agenda y recordatorios</p></div>'+
      '<div class="pill-row">'+badge(statusFor(s))+'</div></section>'+
      coachTabs()+'<div id="coachStudentBody"></div>';
    renderCoachAgendaV165();
  };

  // Keep legacy public names pointed at the new implementation too.
  window.openAddReminderV81=openReminderModalV165;
  window.saveReminderV81=saveReminderV165;
  window.deleteReminderV81=deleteReminderV165;
  window.saveStudentScheduleV81=saveScheduleV165;
  window.renderCoachStudentAgendaV81=renderCoachAgendaV165;

  window.__fjzAgendaV165={
    version:VERSION,
    hardReset:true,
    directAthleteLookup:true,
    scopedQueries:true,
    delegatedActions:true,
    confirmedInsert:true,
    legacyAgendaBypassed:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzAgendaV165",
  "hardReset:true",
  "directAthleteLookup:true",
  "scopedQueries:true",
  "delegatedActions:true",
  "confirmedInsert:true",
  "legacyAgendaBypassed:true"
]:
    if marker not in html:
        raise RuntimeError("V16.5 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V16.5 agenda hard reset enabled")
