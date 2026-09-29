import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v154CheckinScoreStyles">
.v701-checkin-scores{
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:10px!important
}
.v154-score-card{
  padding:11px!important
}
.v154-score-head{
  display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:8px
}
.v154-score-head label{margin:0!important;min-height:auto!important}
.v154-score-value{
  min-width:54px;text-align:center;padding:4px 7px;border:1px solid var(--border);
  border-radius:999px;font-size:9px;color:var(--muted);background:#0d0d10
}
.v154-score-value.selected{
  color:#fff;border-color:rgba(255,31,47,.42);background:rgba(255,31,47,.10)
}
.v154-score-grid{
  display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:5px
}
.v154-score-btn{
  appearance:none;-webkit-appearance:none;border:1px solid var(--border);
  background:#101014;color:var(--muted);border-radius:9px;
  min-height:38px;font-size:12px;font-weight:900;cursor:pointer;
  touch-action:manipulation
}
.v154-score-btn:active{transform:scale(.97)}
.v154-score-btn.active{
  color:#fff;border-color:rgba(255,31,47,.55);
  background:linear-gradient(180deg,rgba(255,31,47,.20),rgba(255,31,47,.10));
  box-shadow:0 0 0 1px rgba(255,31,47,.08) inset
}
.v154-required-note{
  margin:10px 0 0;padding:9px 11px;border:1px solid rgba(90,167,255,.22);
  border-radius:11px;background:rgba(90,167,255,.04);font-size:10px;color:var(--muted)
}
@media(max-width:700px){
  .v701-checkin-scores{grid-template-columns:1fr!important}
  .v701-checkin-scores .track-score:last-child{grid-column:auto!important}
  .v154-score-btn{min-height:42px;font-size:13px}
}
</style>
"""

js=r"""
<script id="v154CheckinScoreRuntime">
(function(){
  const VERSION='15.4';
  let submittingV154=false;

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

  function scoreCardV154(label,id){
    const buttons=Array.from({length:10},(_,i)=>{
      const v=i+1;
      return '<button type="button" class="v154-score-btn" data-score="'+v+'" aria-pressed="false" onclick="setCheckinScoreV154(\''+id+'\','+v+')">'+v+'</button>';
    }).join('');
    return '<div class="track-score v154-score-card" data-score-id="'+id+'">'+
      '<div class="v154-score-head"><label>'+esc(label)+'</label><span class="v154-score-value" id="'+id+'ValueV154">Sin elegir</span></div>'+
      '<input id="'+id+'" type="hidden" value="">'+
      '<div class="v154-score-grid">'+buttons+'</div>'+
      '</div>';
  }

  window.setCheckinScoreV154=function(id,value){
    const v=Math.max(1,Math.min(10,Number(value)||0));
    const input=el(id);
    const card=document.querySelector('[data-score-id="'+id+'"]');
    if(!input||!card||!v)return;
    input.value=String(v);
    card.querySelectorAll('.v154-score-btn').forEach(btn=>{
      const active=Number(btn.dataset.score)===v;
      btn.classList.toggle('active',active);
      btn.setAttribute('aria-pressed',active?'true':'false');
    });
    const badge=el(id+'ValueV154');
    if(badge){
      badge.textContent=v+'/10';
      badge.classList.add('selected');
    }
  };

  function clearCheckinScoresV154(){
    SPECS.forEach(([,id])=>{
      const input=el(id);
      if(input)input.value='';
      const card=document.querySelector('[data-score-id="'+id+'"]');
      card?.querySelectorAll('.v154-score-btn').forEach(btn=>{
        btn.classList.remove('active');
        btn.setAttribute('aria-pressed','false');
      });
      const badge=el(id+'ValueV154');
      if(badge){
        badge.textContent='Sin elegir';
        badge.classList.remove('selected');
      }
    });
  }

  function currentWeekCheckinV154(){
    const week=el('ciWeek')?.value||weekStartISO();
    return (trackingCache?.checkins||[]).find(x=>x.week_start===week)||null;
  }

  function prefillCurrentCheckinV154(){
    const row=currentWeekCheckinV154();
    if(!row)return;
    SPECS.forEach(([,id,key])=>{
      const v=Number(row[key]);
      if(Number.isFinite(v)&&v>=1&&v<=10)setCheckinScoreV154(id,v);
    });
    if(el('ciWeight')&&row.weight_kg!=null)el('ciWeight').value=row.weight_kg;
    if(el('ciNotes')&&row.notes!=null)el('ciNotes').value=row.notes||'';
  }

  function buildInteractiveScoresV154(){
    const host=el('studentSubBody');
    const grid=host?.querySelector('.v701-checkin-scores');
    if(!grid)return;
    grid.innerHTML=SPECS.map(([label,id])=>scoreCardV154(label,id)).join('');
    clearCheckinScoresV154();

    if(!host.querySelector('#v154RequiredNote')){
      const note=document.createElement('div');
      note.id='v154RequiredNote';
      note.className='v154-required-note';
      note.textContent='Elegí un valor del 1 al 10 en cada indicador. No hay números preseleccionados.';
      grid.insertAdjacentElement('afterend',note);
    }

    const week=el('ciWeek');
    if(week&&!week.dataset.v154Bound){
      week.dataset.v154Bound='1';
      week.addEventListener('change',()=>{
        clearCheckinScoresV154();
        const row=(trackingCache?.checkins||[]).find(x=>x.week_start===week.value);
        if(row)prefillCurrentCheckinV154();
      });
    }
  }

  const baseRenderTrackingStudentV154=renderTrackingStudent;
  renderTrackingStudent=function(){
    const out=baseRenderTrackingStudentV154.apply(this,arguments);
    buildInteractiveScoresV154();

    // Reuse the tracking request already started by the base renderer whenever possible.
    Promise.resolve().then(async()=>{
      try{
        await loadTracking(false);
        if(el('ciWeek'))prefillCurrentCheckinV154();
      }catch(e){
        console.warn('TEAM FJZ check-in prefill unavailable',e);
      }
    });
    return out;
  };

  function checkinValueV154(id){
    const n=Number(el(id)?.value);
    return Number.isFinite(n)&&n>=1&&n<=10?n:null;
  }

  window.submitWeeklyCheckin=async function(){
    if(submittingV154)return;
    if(!cloudEnabled||!supabaseClient){toast('El check-in requiere modo nube');return}

    const athleteId=trackingAthleteId();
    if(!athleteId){toast('No encuentro tu ficha');return}

    const missing=SPECS.filter(([,id])=>checkinValueV154(id)==null).map(([label])=>label);
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
      sleep_quality:checkinValueV154('ciSleep'),
      hunger_level:checkinValueV154('ciHunger'),
      stress_level:checkinValueV154('ciStress'),
      energy_level:checkinValueV154('ciEnergy'),
      adherence_level:checkinValueV154('ciAdh'),
      mood_level:checkinValueV154('ciMood'),
      motivation_level:checkinValueV154('ciMotivation'),
      recovery_level:checkinValueV154('ciRecovery'),
      notes:el('ciNotes')?.value.trim()||'',
      submitted_at:new Date().toISOString()
    };

    const btn=[...document.querySelectorAll('button')].find(b=>(b.getAttribute('onclick')||'').includes('submitWeeklyCheckin'));
    submittingV154=true;
    if(btn){
      btn.dataset.v154Text=btn.textContent||'Enviar check-in';
      btn.disabled=true;
      btn.textContent='Guardando…';
    }

    try{
      const {error}=await supabaseClient.from('weekly_checkins').upsert(payload,{onConflict:'athlete_id,week_start'});
      if(error){toast(cloudErr(error));return}

      student().checkin='Recibido';
      saveState();
      trackingLoadedFor=null;
      await loadTracking(true);
      renderStudentTrackingHistory();
      toast('Check-in enviado');
    }catch(e){
      toast(cloudErr(e));
    }finally{
      submittingV154=false;
      if(btn){
        btn.disabled=false;
        btn.textContent=btn.dataset.v154Text||'Enviar check-in';
        delete btn.dataset.v154Text;
      }
    }
  };

  window.__fjzCheckinScoresV154={
    version:VERSION,
    interactiveOneToTen:true,
    noPresetScores:true,
    motivationIncluded:true,
    weeklyPrefill:true,
    submitValidation:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzCheckinScoresV154",
  "interactiveOneToTen:true",
  "noPresetScores:true",
  "motivationIncluded:true",
  "weeklyPrefill:true",
  "submitValidation:true"
]:
    if marker not in html:
        raise RuntimeError("V15.4 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V15.4 interactive check-in scores enabled")
