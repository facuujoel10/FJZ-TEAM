import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")
html=html.replace("TEAM FJZ V9.4","TEAM FJZ V9.5")

css=r"""
<style id="v94TrainingPro">
.v94-day-tools{display:grid;gap:9px;margin-top:12px;padding-top:12px;border-top:1px solid var(--border)}
.v94-guide-box{border:1px solid var(--border);border-radius:12px;background:#0d0d10;padding:10px}
.v94-guide-head{display:flex;justify-content:space-between;align-items:center;gap:8px}
.v94-guide-head strong{font-size:12px}
.v94-guide-list{display:grid;gap:6px;margin-top:8px}
.v94-guide-item{display:flex;justify-content:space-between;gap:8px;align-items:flex-start;padding:7px 8px;border-radius:9px;background:rgba(255,255,255,.025)}
.v94-guide-item .muted{font-size:10px}
.v94-workout-guide{margin:12px 0}
.v94-workout-guide h3{margin:0 0 8px;font-size:14px}
.v94-cardio-kpis{display:flex;gap:7px;flex-wrap:wrap;margin-top:7px}
.v94-cardio-pill{font-size:10px;border:1px solid var(--border);border-radius:999px;padding:5px 8px;background:#0d0d10}
.v94-phase-badge{font-size:9px;text-transform:uppercase;letter-spacing:.5px;color:var(--muted)}
</style>
"""

js=r"""
<script id="v94TrainingProRuntime">
(function(){
  let exerciseLibraryCloudLoadedV95=false;
  let exerciseLibraryCloudLoadingV95=false;

  async function loadExerciseLibraryCloudV95(){
    if(exerciseLibraryCloudLoadedV95||exerciseLibraryCloudLoadingV95||!window.supabaseClient||!window.currentUser)return;
    exerciseLibraryCloudLoadingV95=true;
    try{
      const {data,error}=await supabaseClient.from('exercise_library').select('*').order('name');
      if(error)throw error;
      const norm=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
      const byName=new Map((exerciseLibrary||[]).map(x=>[norm(x.name),x]));
      for(const row of (data||[])){
        const key=norm(row.name);
        const mapped={
          id:row.id,
          name:row.name,
          muscle:row.primary_muscle||'General',
          equipment:row.equipment||'',
          pattern:row.movement_pattern||'',
          cue:row.technique_cue||row.execution_notes||'',
          variants:row.variants||[]
        };
        if(!byName.has(key)){
          exerciseLibrary.push(mapped);
          byName.set(key,mapped);
        }
      }
      exerciseLibraryCloudLoadedV95=true;
    }catch(e){
      console.warn('exercise library cloud sync',e);
    }finally{
      exerciseLibraryCloudLoadingV95=false;
    }
  }

  function ensureDayV94(d){
    d.warmup=d.warmup||[];
    d.stretching=d.stretching||[];
    d.cardio=d.cardio||{enabled:false,type:'',minutes:'',steps:'',intensity:'',timing:'Después del entrenamiento',notes:''};
    return d;
  }
  function phaseTitleV94(phase){return phase==='warmup'?'Calentamiento / activación':'Estiramiento / movilidad final'}
  function phaseFilterV94(phase){
    const wanted=phase==='warmup'?['Calentamiento','Movilidad']:['Estiramiento','Movilidad'];
    return (exerciseLibrary||[]).filter(x=>wanted.includes(x.muscle));
  }
  function guideItemsHtmlV94(arr,di,phase){
    if(!arr?.length)return '<div class="muted tiny" style="margin-top:7px">Sin ejercicios cargados.</div>';
    return '<div class="v94-guide-list">'+arr.map((x,i)=>'<div class="v94-guide-item"><div><strong>'+esc(x.name)+'</strong><div class="muted">'+esc([x.prescription||'',x.note||''].filter(Boolean).join(' · '))+'</div></div><div class="pill-row"><button class="btn ghost small" onclick="editPrepItemV94('+di+',\''+phase+'\','+i+')">Editar</button><button class="btn ghost small" onclick="removePrepItemV94('+di+',\''+phase+'\','+i+')">×</button></div></div>').join('')+'</div>';
  }
  function cardioHtmlV94(d,di){
    const c=d.cardio||{};
    const bits=[];
    if(c.type)bits.push(c.type);
    if(c.minutes)bits.push(c.minutes+' min');
    if(c.steps)bits.push(Number(c.steps).toLocaleString('es-AR')+' pasos');
    if(c.intensity)bits.push(c.intensity);
    return '<div class="v94-guide-box"><div class="v94-guide-head"><div><div class="v94-phase-badge">Cardio / actividad diaria</div><strong>'+(c.enabled&&bits.length?esc(bits.join(' · ')):'Sin indicación cargada')+'</strong></div><button class="btn small" onclick="editCardioV94('+di+')">'+(c.enabled?'Editar':'Configurar')+'</button></div>'+(c.enabled&&c.notes?'<div class="muted tiny" style="margin-top:7px">'+esc(c.notes)+'</div>':'')+'</div>';
  }
  function dayToolsHtmlV94(d,di){
    ensureDayV94(d);
    return '<div class="v94-day-tools" data-v94-day="'+di+'">'+
      '<div class="v94-guide-box"><div class="v94-guide-head"><div><div class="v94-phase-badge">Antes de entrenar</div><strong>Calentamiento / activación</strong></div><button class="btn small" onclick="openPrepPickerV94('+di+',\'warmup\')">+ Agregar</button></div>'+guideItemsHtmlV94(d.warmup,di,'warmup')+'</div>'+
      cardioHtmlV94(d,di)+
      '<div class="v94-guide-box"><div class="v94-guide-head"><div><div class="v94-phase-badge">Al finalizar</div><strong>Estiramiento / movilidad</strong></div><button class="btn small" onclick="openPrepPickerV94('+di+',\'stretching\')">+ Agregar</button></div>'+guideItemsHtmlV94(d.stretching,di,'stretching')+'</div>'+
    '</div>';
  }

  function enhanceRoutineEditorV94(){
    if(currentProfile?.role!=='coach'||coachStudentTab!=='routine')return;
    const days=student()?.days||[];
    const cards=[...document.querySelectorAll('#coachStudentBody .day-card')];
    cards.forEach(function(card,i){
      if(card.querySelector('.v94-day-tools'))return;
      const d=days[i];if(!d)return;
      const temp=document.createElement('div');temp.innerHTML=dayToolsHtmlV94(d,i);
      card.appendChild(temp.firstElementChild);
    });
  }

  window.openPrepPickerV94=function(di,phase){
    const arr=phaseFilterV94(phase);
    showModal('<div class="modal-head"><div><h3>'+phaseTitleV94(phase)+'</h3><div class="muted tiny">Elegí de la biblioteca de TEAM FJZ.</div></div><button class="btn small" onclick="closeModal()">✕</button></div><input id="v94PrepSearch" class="input" placeholder="Buscar..." oninput="filterPrepPickerV94('+di+',\''+phase+'\',this.value)"><div id="v94PrepList" class="library" style="margin-top:10px">'+prepChoicesV94(di,phase,arr)+'</div><button class="btn" style="width:100%;margin-top:10px" onclick="customPrepV94('+di+',\''+phase+'\')">+ Personalizado</button>');
  };
  function prepChoicesV94(di,phase,arr){
    return arr.map(x=>'<div class="library-item"><h4>'+esc(x.name)+'</h4><p>'+esc(x.muscle)+' · '+esc(x.equipment||'')+'</p><button class="btn primary small" onclick="configurePrepV94('+di+',\''+phase+'\',\''+x.id+'\')">Agregar</button></div>').join('')||'<div class="empty">No encontré ejercicios.</div>';
  }
  window.filterPrepPickerV94=function(di,phase,q){
    const norm=String(q||'').toLowerCase();
    const arr=phaseFilterV94(phase).filter(x=>(x.name+' '+x.muscle+' '+x.equipment).toLowerCase().includes(norm));
    const h=el('v94PrepList');if(h)h.innerHTML=prepChoicesV94(di,phase,arr);
  };
  window.configurePrepV94=function(di,phase,id){
    const x=(exerciseLibrary||[]).find(a=>a.id===id);if(!x)return;
    openPrepEditorV94(di,phase,null,{name:x.name,prescription:'',note:x.cue||''});
  };
  window.customPrepV94=function(di,phase){openPrepEditorV94(di,phase,null,{name:'',prescription:'',note:''})};
  window.editPrepItemV94=function(di,phase,idx){
    const d=ensureDayV94(student().days[di]),arr=phase==='warmup'?d.warmup:d.stretching;
    openPrepEditorV94(di,phase,idx,arr[idx]||{});
  };
  function openPrepEditorV94(di,phase,idx,item){
    showModal('<div class="modal-head"><h3>'+phaseTitleV94(phase)+'</h3><button class="btn small" onclick="closeModal()">✕</button></div><div class="form-grid"><label class="tiny muted span2">Ejercicio<input id="v94PrepName" class="input" value="'+esc(item.name||'')+'"></label><label class="tiny muted span2">Series / repeticiones / tiempo<input id="v94PrepPrescription" class="input" value="'+esc(item.prescription||'')+'" placeholder="Ej: 2 x 15 · 30 s · 5 min"></label><label class="tiny muted span2">Indicación<textarea id="v94PrepNote" class="input" rows="3">'+esc(item.note||'')+'</textarea></label></div><button class="btn primary" style="width:100%;margin-top:12px" onclick="savePrepV94('+di+',\''+phase+'\','+(idx==null?'null':idx)+')">Guardar</button>');
  }
  window.savePrepV94=function(di,phase,idx){
    const d=ensureDayV94(student().days[di]),arr=phase==='warmup'?d.warmup:d.stretching;
    const item={id:uid('prep'),name:el('v94PrepName')?.value.trim()||'Ejercicio',prescription:el('v94PrepPrescription')?.value.trim()||'',note:el('v94PrepNote')?.value.trim()||''};
    if(idx==null)arr.push(item);else item.id=arr[idx]?.id||item.id,arr[idx]=item;
    saveState();closeModal();render();toast('Indicaciones actualizadas');
  };
  window.removePrepItemV94=function(di,phase,idx){
    const d=ensureDayV94(student().days[di]),arr=phase==='warmup'?d.warmup:d.stretching;
    arr.splice(idx,1);saveState();render();
  };

  window.editCardioV94=function(di){
    const d=ensureDayV94(student().days[di]),c=d.cardio||{};
    const types=['Cinta','Bicicleta','Elíptico','Escaladora','Remo','Caminata','Pasos diarios','Otro'];
    const timings=['Antes del entrenamiento','Después del entrenamiento','En otro momento del día','Día de descanso'];
    showModal('<div class="modal-head"><div><h3>Cardio y actividad diaria</h3><div class="muted tiny">Podés indicar máquina, minutos, intensidad y objetivo de pasos.</div></div><button class="btn small" onclick="closeModal()">✕</button></div><div class="form-grid"><label class="tiny muted span2">Modalidad<select id="v94CardioType" class="input"><option value="">Sin cardio</option>'+types.map(x=>'<option '+(c.type===x?'selected':'')+'>'+x+'</option>').join('')+'</select></label><label class="tiny muted">Minutos<input id="v94CardioMinutes" class="input" type="number" min="0" max="300" step="1" value="'+esc(String(c.minutes??''))+'"></label><label class="tiny muted">Pasos del día<input id="v94CardioSteps" class="input" type="number" min="0" max="50000" step="500" value="'+esc(String(c.steps??''))+'"></label><label class="tiny muted">Intensidad<input id="v94CardioIntensity" class="input" value="'+esc(c.intensity||'')+'" placeholder="Ej: suave / moderada"></label><label class="tiny muted">Momento<select id="v94CardioTiming" class="input">'+timings.map(x=>'<option '+(c.timing===x?'selected':'')+'>'+x+'</option>').join('')+'</select></label><label class="tiny muted span2">Indicaciones<textarea id="v94CardioNotes" class="input" rows="3" placeholder="Ej: cinta con inclinación cómoda, ritmo sostenible...">'+esc(c.notes||'')+'</textarea></label></div><button class="btn primary" style="width:100%;margin-top:12px" onclick="saveCardioV94('+di+')">Guardar cardio / pasos</button>');
  };
  window.saveCardioV94=function(di){
    const d=ensureDayV94(student().days[di]);
    const type=el('v94CardioType')?.value||'';
    d.cardio={
      enabled:!!type,
      type,
      minutes:el('v94CardioMinutes')?.value?Number(el('v94CardioMinutes').value):'',
      steps:el('v94CardioSteps')?.value?Number(el('v94CardioSteps').value):'',
      intensity:el('v94CardioIntensity')?.value.trim()||'',
      timing:el('v94CardioTiming')?.value||'',
      notes:el('v94CardioNotes')?.value.trim()||''
    };
    saveState();closeModal();render();toast('Cardio y pasos actualizados');
  };

  function studentGuideCardV94(title,phase,arr){
    if(!arr?.length)return '';
    return '<div class="card v94-workout-guide"><div class="v94-phase-badge">'+phase+'</div><h3>'+title+'</h3><div class="v94-guide-list">'+arr.map(x=>'<div class="v94-guide-item"><div><strong>'+esc(x.name)+'</strong><div class="muted">'+esc([x.prescription||'',x.note||''].filter(Boolean).join(' · '))+'</div></div></div>').join('')+'</div></div>';
  }
  function cardioStudentHtmlV94(c){
    if(!c?.enabled)return '';
    const bits=[];
    if(c.type)bits.push(c.type);if(c.minutes)bits.push(c.minutes+' min');if(c.steps)bits.push(Number(c.steps).toLocaleString('es-AR')+' pasos');if(c.intensity)bits.push(c.intensity);
    return '<div class="card v94-workout-guide"><div class="v94-phase-badge">'+esc(c.timing||'Actividad')+'</div><h3>Cardio / pasos</h3><div class="v94-cardio-kpis">'+bits.map(x=>'<span class="v94-cardio-pill">'+esc(x)+'</span>').join('')+'</div>'+(c.notes?'<div class="muted tiny" style="margin-top:9px">'+esc(c.notes)+'</div>':'')+'</div>';
  }
  function injectWorkoutGuideV94(){
    if(currentProfile?.role!=='student'||studentTab!=='workout')return;
    if(el('v94WorkoutTop'))return;
    const d=ensureDayV94(student().days[currentDay]||{});
    const topHtml=studentGuideCardV94('Calentamiento / activación','Antes de entrenar',d.warmup)+cardioStudentHtmlV94(d.cardio);
    if(topHtml){
      const top=document.createElement('div');top.id='v94WorkoutTop';top.innerHTML=topHtml;
      const prog=document.querySelector('.session-progress');if(prog)prog.insertAdjacentElement('beforebegin',top);
    }
    const bottomHtml=studentGuideCardV94('Estiramiento / movilidad','Al finalizar',d.stretching);
    if(bottomHtml){
      const bottom=document.createElement('div');bottom.id='v94WorkoutBottom';bottom.innerHTML=bottomHtml;
      el('view')?.appendChild(bottom);
    }
  }

  const oldRenderTrainingV94=window.render;
  window.render=function(){
    oldRenderTrainingV94();
    setTimeout(function(){loadExerciseLibraryCloudV95();enhanceRoutineEditorV94();injectWorkoutGuideV94()},80);
    setTimeout(function(){loadExerciseLibraryCloudV95();enhanceRoutineEditorV94();injectWorkoutGuideV94()},500);
  };

  Object.assign(window,{openPrepPickerV94,filterPrepPickerV94,configurePrepV94,customPrepV94,editPrepItemV94,savePrepV94,removePrepItemV94,editCardioV94,saveCardioV94});
  setTimeout(function(){loadExerciseLibraryCloudV95();enhanceRoutineEditorV94();injectWorkoutGuideV94()},200);
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)
p.write_text(html,encoding="utf-8")
swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8").replace("team-fjz-v9-4","team-fjz-v9-5")
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V9.5 estabilidad entrenamiento:",len(html),"bytes")
