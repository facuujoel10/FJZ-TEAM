
import pathlib

OUT = pathlib.Path("public")
p = OUT / "index.html"
html = p.read_text(encoding="utf-8")

html = html.replace("TEAM FJZ V8.7", "TEAM FJZ V8.8")

css = r"""
<style id="v88Fixes">
.v65-lib-shortcuts{display:none!important}
.v88-version{font-size:9px;color:var(--muted);opacity:.65;margin-top:3px}
</style>
"""

js = r"""
<script id="v88Runtime">
(function(){
  function ensureMotivationV88(){
    if(currentProfile?.role!=='student'||studentTab!=='tracking')return;
    if(document.getElementById('ciMotivation'))return;
    var grid=document.querySelector('.tracking-grid');
    if(!grid)return;
    var card=document.createElement('div');
    card.className='track-score';
    card.innerHTML='<label>Motivación</label><input id="ciMotivation" class="input" type="number" min="1" max="10" value="7">';
    var recovery=document.getElementById('ciRecovery')?.closest('.track-score');
    if(recovery)grid.insertBefore(card,recovery); else grid.appendChild(card);
  }

  function cleanupLibraryShortcutsV88(){
    document.querySelectorAll('.v65-lib-shortcuts').forEach(function(n){n.remove();});
  }

  var oldRenderV88=window.render;
  window.render=function(){
    oldRenderV88();
    setTimeout(function(){ensureMotivationV88();cleanupLibraryShortcutsV88();},20);
    setTimeout(function(){ensureMotivationV88();cleanupLibraryShortcutsV88();},250);
  };

  var oldTrackingV88=window.renderTrackingStudent;
  if(typeof oldTrackingV88==='function'){
    window.renderTrackingStudent=function(){
      oldTrackingV88();
      setTimeout(ensureMotivationV88,0);
    };
  }

  var oldOpenLibraryV88=window.openLibrary;
  if(typeof oldOpenLibraryV88==='function'){
    window.openLibrary=function(dayIndex){
      oldOpenLibraryV88(dayIndex);
      setTimeout(cleanupLibraryShortcutsV88,0);
    };
  }

  setTimeout(function(){
    var brand=document.querySelector('.brand');
    if(brand&&!document.getElementById('v88Version')){
      var v=document.createElement('div');v.id='v88Version';v.className='v88-version';v.textContent='V8.8';brand.appendChild(v);
    }
  },100);
})();
</script>
"""

html = html.replace("</head>", css + "\n</head>", 1)
html = html.replace("</body>", js + "\n</body>", 1)
p.write_text(html, encoding="utf-8")

swp = OUT / "sw.js"
sw = swp.read_text(encoding="utf-8")
for old in ("team-fjz-v8-4","team-fjz-v8-5","team-fjz-v8-6","team-fjz-v8-7"):
    sw = sw.replace(old, "team-fjz-v8-8")
sw = sw.replace(
    "fetch(req).then(res=>{",
    "fetch(new Request(req,{cache:'no-store'})).then(res=>{"
)
swp.write_text(sw, encoding="utf-8")

print("TEAM FJZ V8.8 fixes aplicado:", len(html), "bytes")


# V8.9 · objetivos múltiples + perfil 360 simplificado
import re
html = p.read_text(encoding="utf-8")
html = html.replace("TEAM FJZ V8.8","TEAM FJZ V8.9")

html = re.sub(
    r"function newStudent\(\)\{.*?\}\nfunction createStudent\(\)\{.*?\}\n\nfunction renderStudent\(",
    """function newStudent(){const goals=['Ganar masa muscular','Bajar grasa','Recomposición corporal','Mejorar fuerza','Mejorar rendimiento','Mejorar hábitos','Volver a entrenar','Otro'];showModal(`<div class="modal-head"><div><h3>Nuevo alumno</h3><div class="muted tiny">Podés elegir uno o varios objetivos.</div></div><button class="btn small" onclick="closeModal()">✕</button></div><label class="tiny muted">Nombre<input id="nName" class="input"></label><div style="margin-top:12px"><div class="tiny muted">Objetivos</div><div class="v89-goals">${goals.map((g,i)=>`<label class="v89-goal"><input type="checkbox" class="v89-goal-check" value="${esc(g)}" ${g==='Otro'?'onchange="toggleOtherGoalV89(this.checked)"':''}><span>${esc(g)}</span></label>`).join('')}</div><div id="v89OtherWrap" style="display:none;margin-top:8px"><label class="tiny muted">Otro objetivo<input id="v89OtherText" class="input" placeholder="Escribí el objetivo personalizado"></label></div></div><label class="tiny muted" style="display:block;margin-top:12px">Entrenamientos por semana<input id="nFreq" class="input" type="number" min="1" max="7" value="4"></label><button class="btn primary" style="width:100%;margin-top:14px" onclick="createStudent()">Crear alumno</button>`)}
function toggleOtherGoalV89(on){const w=el('v89OtherWrap');if(w)w.style.display=on?'block':'none'}
function createStudent(){const name=el('nName').value.trim();if(!name){toast('Escribí el nombre del alumno');return}let goals=[...document.querySelectorAll('.v89-goal-check:checked')].map(x=>x.value).filter(x=>x!=='Otro');if(document.querySelector('.v89-goal-check[value="Otro"]')?.checked){const x=el('v89OtherText')?.value.trim();if(x)goals.push(x)}if(!goals.length){toast('Elegí al menos un objetivo');return}const s={id:uid('s'),name,goal:goals.join(' · '),coachMessage:'Respetá la técnica y el RIR indicado.',checkin:'Pendiente',plannedPerWeek:+el('nFreq').value||4,lastWorkout:null,days:[{id:uid('d'),name:'Día 1',muscles:'A definir',exercises:[]}],sessions:[],checkins:[]};state.students.push(s);state.selectedStudentId=s.id;saveState();closeModal();coachTab='student';coachStudentTab='routine';render();toast('Alumno creado')}

function renderStudent(""",
    html, count=1, flags=re.S
)

html = re.sub(
    r"async function buildStudent360V80\(\)\{.*?\n\}\nasync function injectStudent360V80",
    """async function buildStudent360V80(){const s=student();let latest=null,nutrition=null;try{await Promise.all([loadTracking(true),loadNutrition(true),loadExerciseFeedbackV73(true)]);latest=trackingCache.checkins?.[0]||null;nutrition=nutritionCache.plan||null}catch(e){}const pending=pendingFeedbackV73?.().length||0;const sessions30=progressSessionsInDaysV72?.(s,30)?.length||0;return `<div class="card v80-360" id="v80Student360"><div class="section-title"><div><h3>Resumen 360°</h3><div class="muted tiny">Datos clave del seguimiento.</div></div>${pending?`<span class="v73-alert-badge pulse">${pending} comentario${pending>1?'s':''}</span>`:''}</div><div class="v80-360-grid"><div class="v80-360-metric"><strong>${adherence(s)}%</strong><span>Adherencia 7 días</span></div><div class="v80-360-metric"><strong>${sessions30}</strong><span>Sesiones 30 días</span></div><div class="v80-360-metric"><strong>${latest?latest.energy_level+'/10':'—'}</strong><span>Energía</span></div><div class="v80-360-metric"><strong>${latest?(latest.motivation_level??'—')+'/10':'—'}</strong><span>Motivación</span></div><div class="v80-360-metric"><strong>${latest?latest.recovery_level+'/10':'—'}</strong><span>Recuperación</span></div><div class="v80-360-metric"><strong>${nutrition?'Activo':'—'}</strong><span>Nutrición</span></div></div></div>`}
async function injectStudent360V80""",
    html, count=1, flags=re.S
)

html = html.replace("</head>", "<style id=\"v89Styles\">.v89-goals{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:8px}.v89-goal{display:flex;gap:8px;align-items:flex-start;border:1px solid var(--border);background:var(--card);border-radius:11px;padding:10px}.v89-goal input{width:17px;height:17px;accent-color:var(--red)}@media(max-width:620px){.v89-goals{grid-template-columns:1fr}}</style>\n</head>",1)
p.write_text(html,encoding="utf-8")
sw=swp.read_text(encoding="utf-8").replace("team-fjz-v8-8","team-fjz-v8-9")
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V8.9 mejoras:",len(html),"bytes")


# V9.0 · motivación garantizada en Check-in
html = p.read_text(encoding="utf-8")
html = html.replace("TEAM FJZ V8.9","TEAM FJZ V9.0")

v90_js = r"""
<script id="v90MotivationFix">
(function(){
  function injectMotivationV90(){
    var grid=document.querySelector('#studentSubBody .tracking-grid, #studentSubBody .v701-checkin-scores');
    if(!grid)return false;
    if(document.getElementById('ciMotivation'))return true;
    var card=document.createElement('div');
    card.className='track-score';
    card.setAttribute('data-v90-motivation','1');
    card.innerHTML='<label>Motivación</label><input id="ciMotivation" class="input" type="number" min="1" max="10" value="7">';
    var recovery=document.getElementById('ciRecovery');
    var recoveryCard=recovery&&recovery.closest('.track-score');
    if(recoveryCard)grid.insertBefore(card,recoveryCard);else grid.appendChild(card);
    return true;
  }

  function watchCheckinV90(){
    injectMotivationV90();
    var host=document.getElementById('studentSubBody')||document.getElementById('view');
    if(!host)return;
    if(window.__v90CheckinObserver)window.__v90CheckinObserver.disconnect();
    window.__v90CheckinObserver=new MutationObserver(function(){injectMotivationV90();});
    window.__v90CheckinObserver.observe(host,{childList:true,subtree:true});
    setTimeout(injectMotivationV90,50);
    setTimeout(injectMotivationV90,250);
    setTimeout(injectMotivationV90,800);
  }

  var oldRenderV90=window.render;
  window.render=function(){
    oldRenderV90();
    setTimeout(watchCheckinV90,20);
  };

  var oldTrackingV90=window.renderTrackingStudent;
  if(typeof oldTrackingV90==='function'){
    window.renderTrackingStudent=function(){
      oldTrackingV90();
      setTimeout(watchCheckinV90,0);
    };
  }

  var oldSubmitV90=window.submitWeeklyCheckin;
  if(typeof oldSubmitV90==='function'){
    window.submitWeeklyCheckin=async function(){
      injectMotivationV90();
      return oldSubmitV90();
    };
  }

  setTimeout(watchCheckinV90,100);
})();
</script>
"""
html = html.replace("</body>", v90_js + "\n</body>", 1)
p.write_text(html,encoding="utf-8")

sw=swp.read_text(encoding="utf-8").replace("team-fjz-v8-9","team-fjz-v9-0")
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V9.0 motivacion garantizada:",len(html),"bytes")


# V9.1 · check-in simétrico + validación estricta 1-10
html = p.read_text(encoding="utf-8")
html = html.replace("TEAM FJZ V9.0","TEAM FJZ V9.1")

v91_css = r"""
<style id="v91CheckinPolish">
#studentSubBody .tracking-grid,
#studentSubBody .v701-checkin-scores{
  display:grid!important;
  grid-template-columns:repeat(4,minmax(0,1fr))!important;
  gap:10px!important;
  align-items:stretch!important;
}
#studentSubBody .tracking-grid .track-score,
#studentSubBody .v701-checkin-scores .track-score{
  display:flex!important;
  flex-direction:column!important;
  justify-content:space-between!important;
  min-height:96px!important;
  height:100%!important;
  padding:12px!important;
  border-radius:13px!important;
  box-sizing:border-box!important;
}
#studentSubBody .tracking-grid .track-score label,
#studentSubBody .v701-checkin-scores .track-score label{
  display:block!important;
  min-height:30px!important;
  margin:0 0 8px!important;
  line-height:1.2!important;
}
#studentSubBody .tracking-grid .track-score input,
#studentSubBody .v701-checkin-scores .track-score input{
  width:100%!important;
  min-height:40px!important;
  text-align:center!important;
  font-weight:800!important;
  box-sizing:border-box!important;
}
#studentSubBody .section-title .badge.blue{
  min-width:52px!important;
  text-align:center!important;
  justify-content:center!important;
  padding:6px 9px!important;
  border-radius:999px!important;
  font-size:10px!important;
  letter-spacing:.2px!important;
  white-space:nowrap!important;
}
@media(max-width:900px){
  #studentSubBody .tracking-grid,
  #studentSubBody .v701-checkin-scores{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
  }
}
@media(max-width:430px){
  #studentSubBody .tracking-grid,
  #studentSubBody .v701-checkin-scores{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:8px!important;
  }
  #studentSubBody .tracking-grid .track-score,
  #studentSubBody .v701-checkin-scores .track-score{
    min-height:92px!important;
    padding:10px!important;
  }
}
</style>
"""

v91_js = r"""
<script id="v91CheckinClamp">
(function(){
  function clampScoreV91(input){
    if(!input)return;
    let raw=String(input.value||'').replace(/[^0-9]/g,'');
    if(raw===''){input.value='';return}
    let n=parseInt(raw,10);
    if(!Number.isFinite(n))n=1;
    if(n<1)n=1;
    if(n>10)n=10;
    input.value=String(n);
  }

  function setupScoresV91(){
    const ids=['ciSleep','ciStress','ciEnergy','ciAdh','ciMood','ciMotivation','ciRecovery'];
    ids.forEach(function(id){
      const input=document.getElementById(id);
      if(!input)return;
      input.setAttribute('min','1');
      input.setAttribute('max','10');
      input.setAttribute('step','1');
      input.setAttribute('inputmode','numeric');
      input.setAttribute('pattern','[0-9]*');
      input.oninput=function(){clampScoreV91(input)};
      input.onchange=function(){clampScoreV91(input)};
      input.onblur=function(){
        clampScoreV91(input);
        if(input.value==='')input.value='1';
      };
    });
    const badge=document.querySelector('#studentSubBody .section-title .badge.blue');
    if(badge)badge.textContent='1–10';
  }

  const oldRenderV91=window.render;
  window.render=function(){
    oldRenderV91();
    setTimeout(setupScoresV91,40);
    setTimeout(setupScoresV91,300);
  };

  const oldTrackingV91=window.renderTrackingStudent;
  if(typeof oldTrackingV91==='function'){
    window.renderTrackingStudent=function(){
      oldTrackingV91();
      setTimeout(setupScoresV91,0);
    };
  }

  const oldSubmitV91=window.submitWeeklyCheckin;
  if(typeof oldSubmitV91==='function'){
    window.submitWeeklyCheckin=async function(){
      setupScoresV91();
      const ids=['ciSleep','ciStress','ciEnergy','ciAdh','ciMood','ciMotivation','ciRecovery'];
      for(const id of ids){
        const input=document.getElementById(id);
        if(!input)continue;
        clampScoreV91(input);
        const n=Number(input.value);
        if(!Number.isFinite(n)||n<1||n>10){
          toast('Todos los valores del check-in deben estar entre 1 y 10');
          input.focus();
          return;
        }
      }
      return oldSubmitV91();
    };
  }

  setTimeout(setupScoresV91,100);
})();
</script>
"""

html = html.replace("</head>", v91_css + "\n</head>", 1)
html = html.replace("</body>", v91_js + "\n</body>", 1)
p.write_text(html,encoding="utf-8")

sw=swp.read_text(encoding="utf-8").replace("team-fjz-v9-0","team-fjz-v9-1")
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V9.1 checkin polish:",len(html),"bytes")


# V9.2 · carga de fotos históricas desde Coach
html = p.read_text(encoding="utf-8")
html = html.replace("TEAM FJZ V9.1","TEAM FJZ V9.2")

v92_css = r"""
<style id="v92CoachPhotoUpload">
.v92-photo-card{margin-top:14px}
.v92-photo-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.v92-photo-slot{border:1px solid var(--border);background:#0d0d10;border-radius:12px;padding:10px}
.v92-photo-slot strong{display:block;font-size:12px;margin-bottom:6px}
.v92-photo-slot input{width:100%}
.v92-photo-status{margin-top:10px}
@media(max-width:760px){.v92-photo-grid{grid-template-columns:1fr}}
</style>
"""

v92_js = r"""
<script id="v92CoachPhotoUploadRuntime">
(function(){
  function coachAthleteV92(){
    if(currentProfile?.role!=='coach')return null;
    return cloudAthletes.get(student()?.id)||null;
  }

  function coachPhotoUploaderHtmlV92(){
    return '<div class="card v92-photo-card" id="v92CoachPhotoUploader">'+
      '<div class="section-title"><div><h3>Subir fotos de progreso</h3><div class="muted tiny">Podés cargar fotos actuales o históricas que el alumno te mande por WhatsApp.</div></div><span class="badge blue">Coach</span></div>'+
      '<div class="form-grid">'+
        '<label class="tiny muted">Fecha de las fotos<input id="v92PhotoDate" class="input" type="date" value="'+dateInputToday()+'"></label>'+
        '<label class="tiny muted span2">Nota opcional<input id="v92PhotoNotes" class="input" placeholder="Ej: chequeo mensual, fotos iniciales..."></label>'+
      '</div>'+
      '<div class="v92-photo-grid" style="margin-top:10px">'+
        '<label class="v92-photo-slot"><strong>Frente</strong><input id="v92PhotoFront" class="input" type="file" accept="image/jpeg,image/png,image/webp,image/heic,image/heif"></label>'+
        '<label class="v92-photo-slot"><strong>Perfil</strong><input id="v92PhotoSide" class="input" type="file" accept="image/jpeg,image/png,image/webp,image/heic,image/heif"></label>'+
        '<label class="v92-photo-slot"><strong>Espalda</strong><input id="v92PhotoBack" class="input" type="file" accept="image/jpeg,image/png,image/webp,image/heic,image/heif"></label>'+
      '</div>'+
      '<div id="v92PhotoStatus" class="muted tiny v92-photo-status"></div>'+
      '<button class="btn primary" style="width:100%;margin-top:10px" onclick="uploadCoachProgressPhotosV92()">Subir fotos seleccionadas</button>'+
    '</div>';
  }

  async function uploadOneCoachPhotoV92(athlete,file,date,pose,notes){
    if(!file)return false;
    if(file.size>8*1024*1024)throw new Error('Cada foto debe pesar menos de 8 MB');
    const allowed=['image/jpeg','image/png','image/webp','image/heic','image/heif'];
    if(file.type&& !allowed.includes(file.type))throw new Error('Formato de imagen no compatible');
    const ext=(file.name.split('.').pop()||'jpg').toLowerCase().replace(/[^a-z0-9]/g,'')||'jpg';
    const safePose=pose.replace(/[^a-z]/g,'');
    const path=athlete.id+'/'+date+'/'+safePose+'_'+Date.now()+'_'+Math.random().toString(36).slice(2,7)+'.'+ext;

    const up=await supabaseClient.storage.from('progress-photos').upload(path,file,{
      cacheControl:'3600',
      upsert:false,
      contentType:file.type||undefined
    });
    if(up.error)throw up.error;

    const row={
      athlete_id:athlete.id,
      student_id:athlete.user_id||null,
      taken_on:date,
      pose:pose,
      storage_path:path,
      notes:notes||''
    };
    const ins=await supabaseClient.from('progress_photos').insert(row);
    if(ins.error){
      await supabaseClient.storage.from('progress-photos').remove([path]);
      throw ins.error;
    }
    return true;
  }

  window.uploadCoachProgressPhotosV92=async function(){
    const athlete=coachAthleteV92();
    if(!athlete){toast('No encuentro la ficha del alumno');return}
    const date=el('v92PhotoDate')?.value;
    if(!date){toast('Elegí la fecha de las fotos');return}
    const notes=el('v92PhotoNotes')?.value.trim()||'';
    const jobs=[
      ['front',el('v92PhotoFront')?.files?.[0]||null],
      ['side',el('v92PhotoSide')?.files?.[0]||null],
      ['back',el('v92PhotoBack')?.files?.[0]||null]
    ].filter(x=>x[1]);

    if(!jobs.length){toast('Seleccioná al menos una foto');return}

    const status=el('v92PhotoStatus');
    if(status)status.textContent='Subiendo '+jobs.length+' foto'+(jobs.length>1?'s':'')+'…';

    try{
      let done=0;
      for(const [pose,file] of jobs){
        await uploadOneCoachPhotoV92(athlete,file,date,pose,notes);
        done++;
        if(status)status.textContent='Subidas '+done+' de '+jobs.length+'…';
      }

      trackingLoadedFor=null;
      await loadTracking(true);
      if(typeof renderTrackingCoachLoaded==='function')renderTrackingCoachLoaded();
      setTimeout(injectCoachPhotoUploaderV92,80);
      toast('Fotos guardadas en el perfil del alumno');
    }catch(e){
      console.error(e);
      if(status)status.textContent='';
      toast(cloudErr(e));
    }
  };

  function injectCoachPhotoUploaderV92(){
    if(currentProfile?.role!=='coach'||coachTab!=='student'||coachStudentTab!=='tracking')return;
    if(el('v92CoachPhotoUploader'))return;
    const host=el('coachStudentBody');
    if(!host)return;
    const wrap=document.createElement('div');
    wrap.innerHTML=coachPhotoUploaderHtmlV92();
    const node=wrap.firstElementChild;
    const photoSection=host.querySelector('#coachPhotoGrid')?.closest('.card');
    if(photoSection)photoSection.insertAdjacentElement('beforebegin',node);
    else host.appendChild(node);
  }

  const oldRenderV92=window.render;
  window.render=function(){
    oldRenderV92();
    setTimeout(injectCoachPhotoUploaderV92,120);
    setTimeout(injectCoachPhotoUploaderV92,700);
  };

  const oldCoachTrackingV92=window.renderTrackingCoachLoaded;
  if(typeof oldCoachTrackingV92==='function'){
    window.renderTrackingCoachLoaded=function(){
      oldCoachTrackingV92();
      setTimeout(injectCoachPhotoUploaderV92,0);
    };
  }

  Object.assign(window,{uploadCoachProgressPhotosV92});
})();
</script>
"""

html = html.replace("</head>", v92_css + "\n</head>", 1)
html = html.replace("</body>", v92_js + "\n</body>", 1)
p.write_text(html,encoding="utf-8")

sw=swp.read_text(encoding="utf-8").replace("team-fjz-v9-1","team-fjz-v9-2")
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V9.2 coach photo upload:",len(html),"bytes")


# V9.3 · cargador robusto PC/móvil + comparación de medidas
html = p.read_text(encoding="utf-8")
html = html.replace("TEAM FJZ V9.2","TEAM FJZ V9.3")

v93_css = r"""
<style id="v93ProgressTools">
#v92CoachPhotoUploader{display:none!important}
.v93-upload{margin-top:14px}
.v93-drop{
  border:1px dashed rgba(255,255,255,.22);
  background:#0d0d10;
  border-radius:14px;
  padding:16px;
  text-align:center;
  transition:.18s ease;
}
.v93-drop.drag{border-color:var(--red);background:rgba(255,31,47,.06)}
.v93-file-list{display:grid;gap:8px;margin-top:10px}
.v93-file-row{
  display:grid;
  grid-template-columns:minmax(0,1fr) 150px auto;
  align-items:center;
  gap:8px;
  border:1px solid var(--border);
  border-radius:11px;
  padding:9px;
  background:#0b0b0d
}
.v93-file-name{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:11px}
.v93-status{margin-top:9px;min-height:18px}
.v93-compare{margin-top:14px}
.v93-compare-head{display:flex;justify-content:space-between;gap:10px;align-items:flex-end;margin-bottom:10px;flex-wrap:wrap}
.v93-measure-table{display:grid;gap:7px}
.v93-measure-row{
  display:grid;
  grid-template-columns:minmax(110px,1.2fr) repeat(3,minmax(72px,.8fr));
  gap:8px;
  align-items:center;
  padding:9px 10px;
  border:1px solid var(--border);
  border-radius:10px;
  background:#0d0d10
}
.v93-measure-row.header{background:transparent;border:0;padding:0 10px 4px;color:var(--muted);font-size:9px}
.v93-measure-row strong{font-size:12px}
.v93-delta{font-weight:800}
@media(max-width:620px){
  .v93-file-row{grid-template-columns:1fr;gap:6px}
  .v93-measure-row{grid-template-columns:1.2fr repeat(3,.8fr);padding:8px 7px;gap:5px;font-size:10px}
  .v93-measure-row.header{padding:0 7px 4px}
}
</style>
"""

v93_js = r"""
<script id="v93ProgressToolsRuntime">
(function(){
  let filesV93=[];

  function athleteV93(){
    if(currentProfile?.role==='coach')return cloudAthletes.get(student()?.id)||null;
    return [...cloudAthletes.values()][0]||null;
  }

  function uploadCardV93(){
    return '<div class="card v93-upload" id="v93CoachPhotoUploader">'+
      '<div class="section-title"><div><h3>Fotos de progreso</h3><div class="muted tiny">Subí fotos desde PC o celular, incluso si te las mandaron por WhatsApp.</div></div><span class="badge blue">Hasta 15 MB</span></div>'+
      '<div class="form-grid"><label class="tiny muted">Fecha<input id="v93Date" class="input" type="date" value="'+dateInputToday()+'"></label>'+
      '<label class="tiny muted span2">Nota opcional<input id="v93Notes" class="input" placeholder="Ej: chequeo mensual, fotos iniciales..."></label></div>'+
      '<div id="v93Drop" class="v93-drop" style="margin-top:10px"><strong>Elegir fotos</strong><div class="muted tiny" style="margin:5px 0 10px">Podés seleccionar hasta 3 juntas o arrastrarlas desde la PC.</div>'+
      '<button type="button" class="btn" onclick="el(\'v93Input\').click()">Seleccionar archivos</button>'+
      '<input id="v93Input" type="file" accept="image/*,.heic,.heif" multiple style="display:none" onchange="selectPhotosV93(this.files)"></div>'+
      '<div id="v93Files" class="v93-file-list"></div><div id="v93Status" class="muted tiny v93-status"></div>'+
      '<button id="v93UploadBtn" type="button" class="btn primary" style="width:100%;margin-top:8px" onclick="uploadPhotosV93()">Subir fotos</button>'+
    '</div>';
  }

  window.selectPhotosV93=function(list){
    filesV93=[...list].slice(0,3);
    const host=el('v93Files');if(!host)return;
    const poses=['front','side','back'];
    const labels={front:'Frente',side:'Perfil',back:'Espalda',other:'Otra'};
    host.innerHTML=filesV93.map(function(file,i){
      return '<div class="v93-file-row"><div class="v93-file-name"><strong>'+esc(file.name)+'</strong><div class="muted micro">'+(file.size/1024/1024).toFixed(1)+' MB</div></div>'+
        '<select class="input v93Pose" data-i="'+i+'">'+Object.keys(labels).map(function(k){return '<option value="'+k+'" '+(poses[i]===k?'selected':'')+'>'+labels[k]+'</option>'}).join('')+'</select>'+
        '<button type="button" class="btn ghost small" onclick="removePhotoV93('+i+')">Quitar</button></div>';
    }).join('');
  };

  window.removePhotoV93=function(i){
    filesV93.splice(i,1);
    selectPhotosV93(filesV93);
  };

  async function sendOneV93(athlete,file,date,pose,notes){
    const fd=new FormData();
    fd.append('athlete_id',athlete.id);
    fd.append('taken_on',date);
    fd.append('pose',pose);
    fd.append('notes',notes||'');
    fd.append('file',file,file.name);
    const res=await supabaseClient.functions.invoke('team-fjz-photo-upload',{body:fd});
    if(res.error)throw res.error;
    if(res.data?.error)throw new Error(res.data.detail||res.data.error);
    return res.data;
  }

  window.uploadPhotosV93=async function(){
    const athlete=athleteV93();
    if(!athlete){toast('No encuentro la ficha del alumno');return}
    const date=el('v93Date')?.value;
    if(!date){toast('Elegí la fecha de las fotos');return}
    if(!filesV93.length){toast('Seleccioná al menos una foto');return}
    for(const f of filesV93){
      if(f.size>15*1024*1024){toast('Cada foto debe pesar menos de 15 MB');return}
    }
    const notes=el('v93Notes')?.value.trim()||'';
    const poses=[...document.querySelectorAll('.v93Pose')].map(x=>x.value);
    const btn=el('v93UploadBtn'),status=el('v93Status');
    if(btn)btn.disabled=true;
    try{
      for(let i=0;i<filesV93.length;i++){
        if(status)status.textContent='Subiendo '+(i+1)+' de '+filesV93.length+'…';
        await sendOneV93(athlete,filesV93[i],date,poses[i]||'other',notes);
      }
      filesV93=[];
      if(el('v93Input'))el('v93Input').value='';
      if(el('v93Files'))el('v93Files').innerHTML='';
      if(status)status.textContent='Fotos guardadas correctamente.';
      trackingLoadedFor=null;
      await loadTracking(true);
      if(currentProfile?.role==='coach'&&coachStudentTab==='tracking'&&typeof renderTrackingCoachLoaded==='function')renderTrackingCoachLoaded();
      toast('Fotos guardadas en el perfil');
    }catch(e){
      console.error(e);
      if(status)status.textContent='No se pudo completar la carga. '+(e?.message||'Probá nuevamente.');
      toast('No se pudo subir la foto');
    }finally{
      if(btn)btn.disabled=false;
      setTimeout(injectToolsV93,100);
    }
  };

  function setupDropV93(){
    const drop=el('v93Drop');if(!drop||drop.dataset.ready)return;
    drop.dataset.ready='1';
    ['dragenter','dragover'].forEach(ev=>drop.addEventListener(ev,function(e){e.preventDefault();drop.classList.add('drag')}));
    ['dragleave','drop'].forEach(ev=>drop.addEventListener(ev,function(e){e.preventDefault();drop.classList.remove('drag')}));
    drop.addEventListener('drop',function(e){if(e.dataTransfer?.files?.length)selectPhotosV93(e.dataTransfer.files)});
  }

  const fieldsV93=[
    ['weight_kg','Peso','kg'],['waist_cm','Cintura','cm'],['abdomen_cm','Abdomen','cm'],
    ['hip_cm','Cadera','cm'],['chest_cm','Pecho','cm'],['arm_left_cm','Brazo izq.','cm'],
    ['arm_right_cm','Brazo der.','cm'],['thigh_left_cm','Muslo izq.','cm'],['thigh_right_cm','Muslo der.','cm']
  ];
  function nV93(v){const n=Number(v);return Number.isFinite(n)?n:null}
  function fmtV93(v,u){const n=nV93(v);return n==null?'—':n.toLocaleString('es-AR',{maximumFractionDigits:1})+' '+u}

  function compareHtmlV93(){
    const arr=(trackingCache.measurements||[]).slice().filter(x=>x.measured_on).sort((a,b)=>String(a.measured_on).localeCompare(String(b.measured_on)));
    if(!arr.length)return '';
    const first=arr[0],last=arr[arr.length-1];
    const rows=fieldsV93.filter(([k])=>nV93(first[k])!=null||nV93(last[k])!=null).map(function(x){
      const [k,label,u]=x,a=nV93(first[k]),b=nV93(last[k]),d=(a!=null&&b!=null)?b-a:null;
      return '<div class="v93-measure-row"><strong>'+label+'</strong><span>'+fmtV93(a,u)+'</span><span>'+fmtV93(b,u)+'</span><span class="v93-delta">'+(d==null?'—':(d>0?'+':'')+d.toLocaleString('es-AR',{maximumFractionDigits:1})+' '+u)+'</span></div>';
    }).join('');
    if(!rows)return '';
    return '<div class="card v93-compare" id="v93MeasureCompare"><div class="v93-compare-head"><div><h3 style="margin:0">Evolución de medidas</h3><div class="muted tiny">Comparación entre el primer registro y el último chequeo.</div></div><div class="muted tiny">'+esc(first.measured_on)+' → '+esc(last.measured_on)+'</div></div>'+
      '<div class="v93-measure-table"><div class="v93-measure-row header"><span>Medida</span><span>Inicio</span><span>Actual</span><span>Cambio</span></div>'+rows+'</div></div>';
  }

  async function injectCompareV93(){
    const isCoach=currentProfile?.role==='coach'&&coachTab==='student'&&(coachStudentTab==='tracking'||coachStudentTab==='progress'||coachStudentTab==='summary');
    const isStudent=currentProfile?.role==='student'&&(studentTab==='tracking'||studentTab==='progress'||studentTab==='home');
    if(!isCoach&&!isStudent)return;
    if(el('v93MeasureCompare'))return;
    try{await loadTracking(false)}catch(e){return}
    const html=compareHtmlV93();if(!html)return;
    let host=null;
    if(isCoach)host=el('coachStudentBody')||el('view');
    else host=el('studentSubBody')||el('view');
    if(!host)return;
    const temp=document.createElement('div');temp.innerHTML=html;
    const node=temp.firstElementChild;
    if(isCoach&&el('v80Student360'))el('v80Student360').insertAdjacentElement('afterend',node);
    else host.insertBefore(node,host.firstChild);
  }

  function injectUploaderV93(){
    if(currentProfile?.role!=='coach'||coachTab!=='student'||(coachStudentTab!=='tracking'&&coachStudentTab!=='progress'))return;
    if(el('v93CoachPhotoUploader')){setupDropV93();return}
    const host=el('coachStudentBody');if(!host)return;
    const temp=document.createElement('div');temp.innerHTML=uploadCardV93();
    const node=temp.firstElementChild;
    host.appendChild(node);
    setupDropV93();
  }

  function injectToolsV93(){
    injectUploaderV93();
    injectCompareV93();
  }

  const oldRenderV93=window.render;
  window.render=function(){
    oldRenderV93();
    setTimeout(injectToolsV93,120);
    setTimeout(injectToolsV93,700);
  };

  const oldCoachLoadedV93=window.renderTrackingCoachLoaded;
  if(typeof oldCoachLoadedV93==='function'){
    window.renderTrackingCoachLoaded=function(){
      oldCoachLoadedV93();
      setTimeout(injectToolsV93,50);
    };
  }

  const oldStudentHistV93=window.renderStudentTrackingHistory;
  if(typeof oldStudentHistV93==='function'){
    window.renderStudentTrackingHistory=function(){
      oldStudentHistV93();
      setTimeout(injectCompareV93,50);
    };
  }

  Object.assign(window,{selectPhotosV93,removePhotoV93,uploadPhotosV93});
  setTimeout(injectToolsV93,150);
})();
</script>
"""

html = html.replace("</head>", v93_css + "\n</head>", 1)
html = html.replace("</body>", v93_js + "\n</body>", 1)
p.write_text(html,encoding="utf-8")

sw=swp.read_text(encoding="utf-8").replace("team-fjz-v9-2","team-fjz-v9-3")
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V9.3 fotos y comparacion:",len(html),"bytes")
