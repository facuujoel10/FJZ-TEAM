// The catalog is supplied by the staging build. Custom exercises match only an exact name.
const guideNameKey = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
const guideIdsByName = new Map(Object.entries(exerciseGuides).map(([id,g])=>[guideNameKey(g.name),id]));
function exerciseGuideId(id,assigned){
 if(Object.hasOwn(exerciseGuides,assigned?.techniqueGuideId))return assigned.techniqueGuideId;
 if(Object.hasOwn(exerciseGuides,id))return id;
 if(assigned?.name==='Press QA' && assigned.muscle==='Pecho' && assigned.equipment==='Máquina')return 'chest_press';
 return guideIdsByName.get(guideNameKey(assigned?.name));
}

// Movement diagrams show the moving segment in red against the fixed supports.
const techniqueDiagrams={
 machine_pullover:{frame:'M38 34v51h45m-45-2v16',body:'M46 39l4 39 28 1 3 19',limbs:['M46 43l3-24 18-8','M46 43l12 24 15-8'],head:[44,28]},
 pendulum:{frame:'M24 97h75m-8-70L65 45',poses:['M66 36l-2 29 4 17-13 14','M63 45l-13 26 22 6-17 19'],heads:[[68,26],[66,35]]},
 machine_glute:{frame:'M27 46h34m-14 0v49',body:'M45 42l23 19-3 32m-20-49-13 8',limbs:['M68 61l8 16-13 10','M68 61l21 4 12-6'],head:[39,32]},
 upright_rope:{frame:'M55 97h33m-8-3L58 65',body:'M52 35v31l-7 29m7-29 8 29',limbs:['M52 38l4 16 3 13','M52 38l20 1-13 11'],head:[52,23]},
 meadows_row:{frame:'M10 95l55-13m-5-7 3 14',body:'M46 45l28 15-9 16 7 17',limbs:['M48 47l6 17 8 16','M48 47l21 4-5 12'],head:[35,40]},
 bayesian_curl:{frame:'M15 28v61l32-22',body:'M57 36l1 31-6 28m6-28 11 27',limbs:['M56 39l-9 15-5 18','M56 39l-9 15 14-12'],head:[57,24]},
 belt_squat:{frame:'M22 96h77m-40-2v-18',poses:['M55 31l3 32 4 16-8 15','M51 46l-4 26 22 5-15 17'],heads:[[55,20],[53,35]]},
 cable_abduction:{frame:'M18 24v66l39-4',body:'M55 34v32l-6 29m6-58-23 8',limbs:['M56 66l6 28','M56 66l27 22'],head:[55,22]},
 tibialis_raise:{frame:'M36 18v78h62',body:'M42 37l3 29 22 26',limbs:['M66 92l18 1','M66 92l14-10'],head:[42,25]}
};
function techniqueDiagram(id,index){
 const d=techniqueDiagrams[id],head=d.head||d.heads[index];
 return '<svg viewBox="0 0 112 106" aria-hidden="true" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="#738096" stroke-width="3" d="'+d.frame+'"/><circle cx="'+head[0]+'" cy="'+head[1]+'" r="7" fill="#424d62"/>'+
 (d.body?'<path stroke="#424d62" stroke-width="7" d="'+d.body+'"/>':'')+'<path stroke="#bf254b" stroke-width="6" d="'+(d.limbs||d.poses)[index]+'"/></svg>';
}
function exercisePhotoHtml(id,assigned){
 const key=exerciseGuideId(id,assigned),guide=exerciseGuides[key];
 if(!guide)return '';
 const base='./exercise-media/';
 const labels=guide.src==='diagram'?['Preparación','Movimiento']:guide.files.length===1?['Posición']:['Inicio','Posición de trabajo'];
 const figures=labels.map((label,i)=>{
   const visual=guide.src==='diagram'?techniqueDiagram(key,i):'<img loading="lazy" decoding="async" width="256" height="216" src="'+base+guide.files[i]+'" alt="'+esc(guide.name+' · '+label)+'">';
   return '<figure>'+visual+'<figcaption>'+label+'</figcaption></figure>';
 }).join('');
 return '<details class="exercise-demo fjz-tech-guide" '+(assigned?'open':'')+'><summary>Guía de técnica</summary><div class="fjz-tech-frames">'+figures+'</div>'+
 '<details class="fjz-tech-instructions"><summary>Cómo hacerlo</summary><ol>'+guide.steps.map(step=>'<li>'+esc(step)+'</li>').join('')+'</ol><p><strong>Clave técnica</strong> '+esc(guide.cue)+'</p></details></details>';
}

function installExerciseGuidePicker(modal,exercise){
 if(!modal)return;
 const cue=modal.querySelector('#fCue');if(!cue)return;
 const field=cue.closest('label')||cue;
 const preview=document.createElement('div');preview.className='span2 fjz-coach-guide';
 field.after(preview);
 const id=exercise?.libId||exercise?.id;
 preview.innerHTML=exercisePhotoHtml(id,exercise);
 if(Object.hasOwn(exerciseGuides,id))return;
 const label=document.createElement('label');label.textContent='Demostración del ejercicio';
 const select=document.createElement('select');select.id='fjzGuidePicker';select.className='input';
 select.add(new Option('Elegir una guía de la biblioteca',''));
 for(const [id,guide] of Object.entries(exerciseGuides).sort((a,b)=>a[1].name.localeCompare(b[1].name,'es'))){
   select.add(new Option(guide.name,id));
 }
 select.value=exerciseGuideId(exercise?.libId,exercise)||'';
 select.onchange=()=>{preview.innerHTML=exercisePhotoHtml(id,{...exercise,techniqueGuideId:select.value})};
 label.append(select);field.after(label);
}
