import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v167CheckinCleanupFullCoachStyles">
.v167-checkin-sent{
  margin:10px 0 12px;
  padding:10px 12px;
  border:1px solid rgba(70,200,130,.26);
  border-radius:12px;
  background:rgba(70,200,130,.055)
}
.v167-checkin-sent-head{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:10px
}
.v167-checkin-sent strong{font-size:11px}
.v167-checkin-sent .muted{margin-top:3px}
.v167-checkin-metrics{
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:7px;
  margin-top:10px
}
.v167-checkin-metric{
  min-width:0;
  padding:8px 9px;
  border:1px solid var(--border);
  border-radius:10px;
  background:rgba(255,255,255,.025)
}
.v167-checkin-metric span{
  display:block;
  color:var(--muted);
  font-size:9px;
  line-height:1.2
}
.v167-checkin-metric strong{
  display:block;
  margin-top:3px;
  font-size:14px;
  line-height:1.15
}
.v167-latest-checkin{
  margin-top:10px
}
.v167-latest-checkin .section-title{
  margin-bottom:0
}
@media(max-width:760px){
  .v167-checkin-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}
  .v167-checkin-sent-head{align-items:flex-start}
}
</style>
"""

js=r"""
<script id="v167CheckinCleanupFullCoachRuntime">
(function(){
  const VERSION='16.7';
  let submittingV167=false;
  let editingWeekV167='';

  const SPECS=[
    ['Sueño','ciSleep','sleep_quality'],
    ['Hambre','ciHunger','hunger_level'],
    ['Estrés','ciStress','stress_level'],
    ['Energía','ciEnergy','energy_level'],
    ['Adherencia','ciAdh','adherence_level'],
    ['Ánimo','ciMood','mood_level'],
    ['Motivación','ciMotivation','motivation_level'],
    ['Recuperación','ciRecovery','recovery_level']
  ];

  function rowForWeekV167(){
    const week=el('ciWeek')?.value||weekStartISO();
    return (trackingCache?.checkins||[]).find(x=>x.week_start===week)||null;
  }

  function clearCheckinFormV167(){
    SPECS.forEach(([,id])=>{
      const node=el(id);
      if(node){
        node.value='';
        node.classList.remove('v159-invalid','v160-invalid','v167-invalid');
      }
    });
    if(el('ciWeight'))el('ciWeight').value='';
    if(el('ciNotes'))el('ciNotes').value='';
  }

  function fillCheckinFormV167(row){
    if(!row)return;
    SPECS.forEach(([,id,key])=>{
      const node=el(id);
      const n=Number(row[key]);
      if(node)node.value=Number.isFinite(n)&&n>=1&&n<=10?String(Math.round(n)):'';
    });
    if(el('ciWeight'))el('ciWeight').value=row.weight_kg??'';
    if(el('ciNotes'))el('ciNotes').value=row.notes||'';
  }

  function sentStatusV167(row){
    const form=el('ciWeek')?.closest('.tracking-form');
    if(!form)return;
    let box=el('v167CheckinSent');
    if(!row){
      box?.remove();
      return;
    }
    if(!box){
      box=document.createElement('div');
      box.id='v167CheckinSent';
      box.className='v167-checkin-sent';
      form.insertBefore(box,form.firstChild);
    }
    box.innerHTML=
      '<div class="v167-checkin-sent-head"><div><strong>Check-in enviado</strong>'+
      '<div class="muted tiny">Semana '+esc(row.week_start)+' · los campos quedan limpios después del envío.</div></div>'+
      '<button class="btn small" type="button" onclick="editCheckinV167()">Editar check-in</button></div>';
  }

  function applyCleanStateV167(){
    if(currentProfile?.role!=='student'||studentTab!=='tracking')return;
    const row=rowForWeekV167();
    if(!row){
      editingWeekV167='';
      sentStatusV167(null);
      return;
    }
    if(editingWeekV167===row.week_start){
      sentStatusV167(row);
      return;
    }
    clearCheckinFormV167();
    sentStatusV167(row);
  }

  window.editCheckinV167=function(){
    const row=rowForWeekV167();
    if(!row)return;
    editingWeekV167=row.week_start;
    fillCheckinFormV167(row);
    const box=el('v167CheckinSent');
    if(box){
      box.innerHTML='<div class="v167-checkin-sent-head"><div><strong>Editando check-in enviado</strong>'+
        '<div class="muted tiny">Al volver a enviarlo se actualizará esta misma semana.</div></div>'+
        '<span class="badge blue">Edición</span></div>';
    }
    el('ciSleep')?.focus();
  };

  const baseRenderTrackingStudentV167=window.renderTrackingStudent;
  window.renderTrackingStudent=function(){
    const out=baseRenderTrackingStudentV167.apply(this,arguments);

    const week=el('ciWeek');
    if(week&&!week.dataset.v167Bound){
      week.dataset.v167Bound='1';
      week.addEventListener('change',()=>{
        editingWeekV167='';
        requestAnimationFrame(()=>requestAnimationFrame(applyCleanStateV167));
      });
    }

    Promise.resolve().then(async()=>{
      try{
        await loadTracking(false);
        requestAnimationFrame(()=>requestAnimationFrame(applyCleanStateV167));
      }catch(e){}
    });
    return out;
  };

  function scoreV167(id){
    const n=Number(el(id)?.value);
    return Number.isFinite(n)&&n>=1&&n<=10?n:null;
  }

  window.submitWeeklyCheckin=async function(){
    if(submittingV167)return;
    if(!cloudEnabled||!supabaseClient){toast('El check-in requiere modo nube');return}

    const athleteId=trackingAthleteId();
    if(!athleteId){toast('No encuentro tu ficha');return}

    const missing=SPECS.filter(([,id])=>scoreV167(id)==null).map(([label])=>label);
    if(missing.length){
      toast('Falta completar: '+missing.join(', '));
      return;
    }

    const week=el('ciWeek')?.value||weekStartISO();
    const weightRaw=el('ciWeight')?.value;
    const weight=weightRaw===''||weightRaw==null?null:Number(weightRaw);
    if(weight!=null&&(!Number.isFinite(weight)||weight<20||weight>400)){
      toast('Revisá el peso ingresado');
      return;
    }

    const payload={
      athlete_id:athleteId,
      student_id:currentUser.id,
      week_start:week,
      weight_kg:weight,
      sleep_quality:scoreV167('ciSleep'),
      hunger_level:scoreV167('ciHunger'),
      stress_level:scoreV167('ciStress'),
      energy_level:scoreV167('ciEnergy'),
      adherence_level:scoreV167('ciAdh'),
      mood_level:scoreV167('ciMood'),
      motivation_level:scoreV167('ciMotivation'),
      recovery_level:scoreV167('ciRecovery'),
      notes:(el('ciNotes')?.value||'').trim(),
      submitted_at:new Date().toISOString()
    };

    const form=el('ciWeek')?.closest('.tracking-form');
    const btn=[...(form?.querySelectorAll('button')||[])].find(b=>(b.getAttribute('onclick')||'').includes('submitWeeklyCheckin'));

    submittingV167=true;
    if(btn){
      btn.dataset.v167Text=btn.textContent||'Enviar check-in';
      btn.disabled=true;
      btn.textContent='Guardando…';
    }

    try{
      const {data,error}=await supabaseClient
        .from('weekly_checkins')
        .upsert(payload,{onConflict:'athlete_id,week_start'})
        .select('*')
        .single();
      if(error)throw error;
      if(!data?.id)throw new Error('La nube no confirmó el check-in.');

      student().checkin='Recibido';
      saveState();

      trackingLoadedFor=null;
      await loadTracking(true);
      renderStudentTrackingHistory();

      editingWeekV167='';
      clearCheckinFormV167();
      sentStatusV167(data);
      toast('Check-in enviado');
    }catch(e){
      toast(cloudErr(e));
    }finally{
      submittingV167=false;
      if(btn){
        btn.disabled=false;
        btn.textContent=btn.dataset.v167Text||'Enviar check-in';
        delete btn.dataset.v167Text;
      }
    }
  };

  function metricHtmlV167(label,value){
    const n=Number(value);
    return '<div class="v167-checkin-metric"><span>'+esc(label)+'</span>'+
      '<strong>'+(Number.isFinite(n)?esc(String(n))+'/10':'—')+'</strong></div>';
  }

  function metricsGridV167(row){
    return '<div class="v167-checkin-metrics">'+SPECS.map(([label,,key])=>metricHtmlV167(label,row?.[key])).join('')+'</div>';
  }

  function enhanceCoachCheckinsV167(){
    if(!(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='tracking'))return;
    const host=el('coachStudentBody');
    if(!host)return;
    const cs=trackingCache?.checkins||[];

    const checkinCard=[...host.querySelectorAll('.card')].find(card=>
      /Check-ins semanales/i.test(card.querySelector('h3')?.textContent||'')
    );
    if(!checkinCard)return;

    const rows=[...checkinCard.querySelectorAll('.track-row')];
    rows.forEach((node,i)=>{
      const row=cs[i];
      if(!row)return;
      node.querySelector('.v167-checkin-metrics')?.remove();

      const head=node.querySelector('.track-row-head');
      const muted=head?.querySelector('.muted.tiny');
      if(muted){
        muted.textContent=(row.weight_kg?row.weight_kg+' kg · ':'')+'8 indicadores completos';
      }
      const badge=head?.querySelector('.badge');
      if(badge)badge.textContent='Check-in completo';

      head?.insertAdjacentHTML('afterend',metricsGridV167(row));
    });

    host.querySelector('.v167-latest-checkin')?.remove();
    const latest=cs[0];
    if(latest){
      const top=host.querySelector('.grid.kpi');
      if(top){
        const card=document.createElement('div');
        card.className='card v167-latest-checkin';
        card.innerHTML='<div class="section-title"><div><h3>Último check-in completo</h3>'+
          '<div class="muted tiny">Semana '+esc(latest.week_start)+(latest.weight_kg?' · '+esc(String(latest.weight_kg))+' kg':'')+'</div></div>'+
          '<span class="badge blue">8 indicadores</span></div>'+
          metricsGridV167(latest)+
          (latest.notes?'<div class="coach-note" style="margin-top:10px"><b>Comentario del alumno:</b> '+esc(latest.notes)+'</div>':'');
        top.insertAdjacentElement('afterend',card);
      }
    }
  }

  const baseRenderTrackingCoachLoadedV167=window.renderTrackingCoachLoaded;
  window.renderTrackingCoachLoaded=function(){
    const out=baseRenderTrackingCoachLoadedV167.apply(this,arguments);
    enhanceCoachCheckinsV167();
    return out;
  };

  window.__fjzCheckinV167={
    version:VERSION,
    clearAfterConfirmedSubmit:true,
    editSavedCheckin:true,
    coachShowsAllEight:true,
    weightAndNotesVisible:true,
    motivationVisible:true,
    recoveryVisible:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzCheckinV167",
  "clearAfterConfirmedSubmit:true",
  "editSavedCheckin:true",
  "coachShowsAllEight:true",
  "motivationVisible:true",
  "recoveryVisible:true"
]:
    if marker not in html:
        raise RuntimeError("V16.7 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V16.7 check-in cleanup/full coach view enabled")
