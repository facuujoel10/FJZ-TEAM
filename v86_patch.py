
import pathlib

OUT = pathlib.Path("public")
p = OUT / "index.html"
html = p.read_text(encoding="utf-8")

html = html.replace("TEAM FJZ V8.4", "TEAM FJZ V8.6")
html = html.replace("TEAM FJZ V8.5", "TEAM FJZ V8.6")
html = html.replace(
    "id,coach_id,user_id,client_id,name,goal,invite_code,spotify_url,spotify_title,created_at",
    "id,coach_id,user_id,client_id,name,goal,invite_code,spotify_url,spotify_title,sex,birth_date,occupation_study,created_at"
)
html = html.replace(
    "id,coach_id,user_id,client_id,name,goal,invite_code,spotify_url,spotify_title",
    "id,coach_id,user_id,client_id,name,goal,invite_code,spotify_url,spotify_title,sex,birth_date,occupation_study"
)

css = r"""
<style id="v86Styles">
.v86-method-badge{display:inline-flex;align-items:center;gap:6px;border:1px solid rgba(255,31,47,.34);background:rgba(255,31,47,.08);color:#ff8790;border-radius:999px;padding:5px 8px;font-size:10px;font-weight:900;margin-top:7px}
.v86-method-note{margin-top:6px;padding:8px 10px;border-left:2px solid rgba(255,31,47,.55);background:rgba(255,31,47,.035);border-radius:0 9px 9px 0;font-size:11px;color:var(--muted)}
.v86-video-slot{border:1px solid var(--border)!important;border-radius:11px!important;padding:8px!important;background:#0d0d10!important;display:flex!important;align-items:center;justify-content:space-between;gap:8px;min-height:0!important}
.v86-video-slot .btn{white-space:nowrap}
.v86-profile-card{margin-top:12px}
.v86-profile-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.v86-profile-field{border:1px solid var(--border);background:#0d0d10;border-radius:11px;padding:10px;min-width:0}
.v86-profile-field strong{display:block;font-size:13px;overflow-wrap:anywhere}
.v86-profile-field span{display:block;margin-top:3px;color:var(--muted);font-size:9px}
.v86-profile-modal-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.v86-profile-modal-grid .span2{grid-column:1/-1}
.v80-video-slot{min-height:0!important}
@media(max-width:700px){.v86-profile-grid{grid-template-columns:1fr 1fr}.v86-profile-modal-grid{grid-template-columns:1fr}.v86-profile-modal-grid .span2{grid-column:auto}}
</style>
"""

js = r"""
<script id="v86Runtime">
(function(){
  var METHOD_LABELS_V86={normal:'Normal',dropset:'Dropset',rest_pause:'Rest-pause',myo_reps:'Myo-reps',cluster:'Cluster',superserie:'Superserie'};
  function methodLabelV86(v){return METHOD_LABELS_V86[v||'normal']||String(v||'Normal');}

  var showExerciseFormV86Base=window.showExerciseForm;
  window.showExerciseForm=function(dayIndex,exIndex,e){
    showExerciseFormV86Base(dayIndex,exIndex,e);
    var grid=document.querySelector('.modal .form-grid');
    if(!grid||document.getElementById('fMethod'))return;
    var box=document.createElement('div');
    box.className='span4';
    box.innerHTML='<div class="card" style="padding:11px;margin-top:2px"><div class="section-title" style="margin:0 0 8px"><div><strong>Método de intensificación</strong><div class="muted tiny">Opcional. Usalo para técnicas especiales del ejercicio.</div></div></div><div class="form-grid"><label class="span2 tiny muted">Método<select id="fMethod" class="input"><option value="normal">Normal</option><option value="dropset">Dropset</option><option value="rest_pause">Rest-pause</option><option value="myo_reps">Myo-reps</option><option value="cluster">Cluster</option><option value="superserie">Superserie</option></select></label><label class="span2 tiny muted">Detalle<input id="fMethodNote" class="input" placeholder="Ej: última serie, bajar 25% y continuar..."></label></div></div>';
    grid.appendChild(box);
    var sel=document.getElementById('fMethod');
    var note=document.getElementById('fMethodNote');
    if(sel)sel.value=(e&&e.method)||'normal';
    if(note)note.value=(e&&e.methodNote)||'';
  };

  window.saveExercise=function(di,ei,exUid,libId,muscle,equipment){
    var old=ei==null?null:student().days[di].exercises[ei];
    var data={
      uid:(old&&old.uid)||exUid||uid('e'),libId:libId,
      name:el('fName').value.trim()||'Ejercicio',muscle:muscle,equipment:equipment,
      sets:+el('fSets').value,min:+el('fMin').value,max:+el('fMax').value,
      rirMin:+el('fRMin').value,rirMax:+el('fRMax').value,rest:+el('fRest').value,
      cue:el('fCue').value.trim(),increment:+el('fInc').value,
      method:(el('fMethod')&&el('fMethod').value)||((old&&old.method)||'normal'),
      methodNote:(el('fMethodNote')&&el('fMethodNote').value.trim())||'',
      history:(old&&old.history)||[],override:(old&&old.override)||null
    };
    if(ei==null)student().days[di].exercises.push(data);else student().days[di].exercises[ei]=data;
    saveState();closeModal();render();toast('Rutina actualizada');
  };

  var dayEditorV86Base=window.dayEditor;
  window.dayEditor=function(d,i){
    var out=dayEditorV86Base(d,i);
    (d.exercises||[]).forEach(function(e){
      if(!e.method||e.method==='normal')return;
      var cue=esc(e.cue||'');
      var marker='<p>'+cue+'</p>';
      var method='<span class="v86-method-badge">'+esc(methodLabelV86(e.method))+'</span>';
      if(e.methodNote)method+='<div class="v86-method-note">'+esc(e.methodNote)+'</div>';
      if(out.indexOf(marker)>=0)out=out.replace(marker,marker+method);
    });
    return out;
  };

  var workoutExerciseV86Base=window.workoutExercise;
  window.workoutExercise=function(e,i){
    var out=workoutExerciseV86Base(e,i);
    if(e&&e.method&&e.method!=='normal'){
      var strip='<div style="margin:0 0 10px"><span class="v86-method-badge">'+esc(methodLabelV86(e.method))+'</span>';
      if(e.methodNote)strip+='<div class="v86-method-note">'+esc(e.methodNote)+'</div>';
      strip+='</div>';
      out=out.replace('<div class="card session-card">','<div class="card session-card">'+strip);
    }
    return out;
  };

  window.videoPlaceholderV72=function(e,coach){
    var key=exerciseMediaKeyV80(e);
    return '<div class="v80-video-slot v86-video-slot" data-v80-video-key="'+esc(key)+'" data-v80-video-title="'+esc((e&&e.name)||'Ejercicio')+'" data-v80-video-coach="'+(coach?'1':'0')+'"><div><strong>Video técnico</strong><div class="muted micro">Referencia visual opcional</div></div><button class="btn small" disabled>Cargando…</button></div>';
  };

  window.renderVideoSlotV80=async function(slot,media){
    var coach=slot.dataset.v80VideoCoach==='1';
    var key=slot.dataset.v80VideoKey;
    var title=slot.dataset.v80VideoTitle||'Ejercicio';
    slot.classList.add('v86-video-slot');
    if(media){
      slot.innerHTML='<div><strong>Video técnico</strong><div class="muted micro">'+esc(media.title||title)+'</div></div><button class="btn small" onclick="openExerciseVideoV86(\''+esc(key)+'\',\''+esc(title)+'\','+(coach?'true':'false')+')">▶ Ver video</button>';
    }else if(coach){
      slot.innerHTML='<div><strong>Video técnico</strong><div class="muted micro">Todavía no hay video asociado.</div></div><button class="btn small" onclick="openExerciseVideoV86(\''+esc(key)+'\',\''+esc(title)+'\',true)">+ Agregar</button>';
    }else{
      slot.innerHTML='<div><strong>Video técnico</strong><div class="muted micro">Sin video cargado por el coach.</div></div>';
    }
  };

  window.openExerciseVideoV86=async function(key,title,coach){
    try{
      await loadExerciseMediaV80();
      var media=exerciseMediaCacheV80.get(key)||null;
      var player='';
      if(media){
        var url=media.storage_path?await signedExerciseVideoV80(media.storage_path):(media.video_url||'');
        if(url)player='<video controls preload="metadata" playsinline src="'+esc(url)+'" style="width:100%;max-height:55vh;border-radius:12px;background:#000"></video>';
      }
      var controls='';
      if(coach){
        controls='<div class="pill-row" style="margin-top:12px"><button class="btn primary" onclick="el(\'v86VideoUpload\').click()">'+(media?'Reemplazar video':'Subir video')+'</button>';
        if(media)controls+='<button class="btn" onclick="removeExerciseVideoV80(\''+esc(key)+'\');closeModal()">Quitar video</button>';
        controls+='<input id="v86VideoUpload" class="v80-video-upload" type="file" accept="video/mp4,video/webm,video/quicktime" onchange="uploadExerciseVideoV80(\''+esc(key)+'\',\''+esc(title)+'\',this);closeModal()"></div>';
      }
      showModal('<div class="modal-head"><div><h3>'+esc(title)+'</h3><div class="muted tiny">Video técnico</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+(player||'<div class="empty">Todavía no hay un video cargado para este ejercicio.</div>')+controls);
    }catch(e){toast(cloudErr(e));}
  };

  function sexLabelV86(v){return ({hombre:'Hombre',mujer:'Mujer',otro:'Otro',prefiero_no_decir:'Prefiero no decir'})[v]||'Sin completar';}
  function ageV86(date){
    if(!date)return null;
    var d=new Date(date+'T12:00:00'),now=new Date(),a=now.getFullYear()-d.getFullYear(),m=now.getMonth()-d.getMonth();
    if(m<0||(m===0&&now.getDate()<d.getDate()))a--;
    return a>=0?a:null;
  }
  function currentAthleteV86(){
    if(currentProfile&&currentProfile.role==='student')return Array.from(cloudAthletes.values())[0]||null;
    return cloudAthletes.get(student()&&student().id)||null;
  }

  window.openStudentProfileV86=function(){
    var a=currentAthleteV86()||{},age=ageV86(a.birth_date);
    showModal('<div class="modal-head"><div><h3>Datos personales</h3><div class="muted tiny">Información básica para que tu coach conozca mejor tu contexto.</div></div><button class="btn small" onclick="closeModal()">✕</button></div><div class="v86-profile-modal-grid"><label class="tiny muted">Sexo<select id="v86Sex" class="input"><option value="">Sin completar</option><option value="hombre">Hombre</option><option value="mujer">Mujer</option><option value="otro">Otro</option><option value="prefiero_no_decir">Prefiero no decir</option></select></label><label class="tiny muted">Fecha de nacimiento<input id="v86Birth" class="input" type="date" value="'+esc(a.birth_date||'')+'"></label><label class="tiny muted">Edad<input class="input" value="'+(age!=null?age+' años':'Se calcula con tu fecha')+'" disabled></label><label class="tiny muted">Ocupación / estudio<input id="v86Occupation" class="input" maxlength="120" placeholder="Ej: estudiante, administrativo, reparto..." value="'+esc(a.occupation_study||'')+'"></label></div><button class="btn primary" style="width:100%;margin-top:14px" onclick="saveStudentProfileV86()">Guardar datos</button>');
    var s=el('v86Sex');if(s)s.value=a.sex||'';
  };

  window.saveStudentProfileV86=async function(){
    if(!currentProfile||currentProfile.role!=='student'){toast('Solo el alumno puede editar estos datos');return;}
    var sex=(el('v86Sex')&&el('v86Sex').value)||null;
    var birth=(el('v86Birth')&&el('v86Birth').value)||null;
    var occupation=(el('v86Occupation')&&el('v86Occupation').value.trim())||null;
    try{
      var res=await supabaseClient.rpc('update_my_athlete_profile',{p_sex:sex,p_birth_date:birth,p_occupation_study:occupation});
      if(res.error)throw res.error;
      var row=Array.isArray(res.data)?res.data[0]:res.data;
      if(row){
        linkedAthleteId=row.id||linkedAthleteId;
        var key=row.client_id||(student()&&student().id);
        if(key)cloudAthletes.set(key,row);
      }
      closeModal();toast('Datos personales actualizados');render();
    }catch(e){toast(cloudErr(e));}
  };

  async function injectStudentProfileV86(){
    if(!currentProfile||currentProfile.role!=='student'||mode!=='student'||studentTab!=='home')return;
    var a=currentAthleteV86();if(!a)return;
    var hero=el('view')&&el('view').querySelector('.hero');if(!hero)return;
    var actions=el('v70StudentProfile')&&el('v70StudentProfile').querySelector('.v70-profile-actions');
    if(actions&&!el('v86ProfileBtn')){
      var b=document.createElement('button');b.id='v86ProfileBtn';b.className='btn small';b.textContent='Datos personales';b.onclick=openStudentProfileV86;actions.appendChild(b);
    }
    if(el('v86StudentProfileCard'))return;
    var age=ageV86(a.birth_date),card=document.createElement('div');
    card.id='v86StudentProfileCard';card.className='card v86-profile-card';
    card.innerHTML='<div class="section-title"><div><h3>Mi perfil</h3><div class="muted tiny">Tus datos básicos para el seguimiento.</div></div><button class="btn small" onclick="openStudentProfileV86()">Editar</button></div><div class="v86-profile-grid"><div class="v86-profile-field"><strong>'+esc(sexLabelV86(a.sex))+'</strong><span>Sexo</span></div><div class="v86-profile-field"><strong>'+(age!=null?age+' años':'—')+'</strong><span>Edad</span></div><div class="v86-profile-field"><strong>'+(a.birth_date?formatTrackingDate(a.birth_date):'—')+'</strong><span>Fecha de nacimiento</span></div><div class="v86-profile-field"><strong>'+esc(a.occupation_study||'—')+'</strong><span>Ocupación / estudio</span></div></div>';
    hero.insertAdjacentElement('afterend',card);
  }

  async function injectCoachProfileV86(){
    if(!currentProfile||currentProfile.role!=='coach'||coachTab!=='student'||coachStudentTab!=='summary')return;
    var a=currentAthleteV86();if(!a)return;
    var box=el('v80Student360');if(!box||el('v86CoachProfile'))return;
    var age=ageV86(a.birth_date),n=document.createElement('div');n.id='v86CoachProfile';n.style.marginTop='12px';
    n.innerHTML='<div class="v86-profile-grid"><div class="v86-profile-field"><strong>'+esc(sexLabelV86(a.sex))+'</strong><span>Sexo</span></div><div class="v86-profile-field"><strong>'+(age!=null?age+' años':'—')+'</strong><span>Edad</span></div><div class="v86-profile-field"><strong>'+(a.birth_date?formatTrackingDate(a.birth_date):'—')+'</strong><span>Cumpleaños</span></div><div class="v86-profile-field"><strong>'+esc(a.occupation_study||'—')+'</strong><span>Ocupación / estudio</span></div></div>';
    box.appendChild(n);
  }

  window.studentRows=function(arr){
    return arr.map(function(s){
      return '<div class="student-row" data-client-id="'+esc(s.id)+'"><div class="student-main"><div class="v70-student-avatar-slot"><div class="v70-avatar">'+esc(s.name.slice(0,2).toUpperCase())+'</div></div><div><strong>'+esc(s.name)+'</strong><div class="muted tiny">'+esc(s.goal)+'</div></div></div><div><strong>'+adherence(s)+'%</strong><div class="muted tiny">Adherencia</div></div><div><strong>'+fmtDate(s.lastWorkout)+'</strong><div class="muted tiny">Último entreno</div></div><div>'+badge(statusFor(s))+'</div><div class="pill-row" style="justify-content:flex-end"><button class="btn small" onclick="openStudent(\''+s.id+'\')">Abrir</button><button class="btn small" style="border-color:rgba(255,31,47,.55);color:#ff7a84" onclick="deleteStudentCloud(\''+s.id+'\')">Eliminar</button></div></div>';
    }).join('');
  };

  var renderV86Base=window.render;
  window.render=function(){
    renderV86Base();
    setTimeout(function(){injectStudentProfileV86();injectCoachProfileV86();},140);
    setTimeout(function(){injectCoachProfileV86();},700);
  };

  Object.assign(window,{openExerciseVideoV86:openExerciseVideoV86,openStudentProfileV86:openStudentProfileV86,saveStudentProfileV86:saveStudentProfileV86});
})();
</script>
"""

html = html.replace("</head>", css + "\n</head>", 1)
html = html.replace("</body>", js + "\n</body>", 1)
p.write_text(html, encoding="utf-8")

swp = OUT / "sw.js"
sw = swp.read_text(encoding="utf-8")
sw = sw.replace("team-fjz-v8-4", "team-fjz-v8-6").replace("team-fjz-v8-5", "team-fjz-v8-6")
swp.write_text(sw, encoding="utf-8")

print("TEAM FJZ V8.6 patch aplicado:", len(html), "bytes")
