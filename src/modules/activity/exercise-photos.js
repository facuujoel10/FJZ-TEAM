// The catalog is supplied by the staging build. Custom exercises match only an exact name.
const guideNameKey = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
const guideIdsByName = new Map(Object.entries(exerciseGuides).filter(([,g])=>!g.archived).map(([id,g])=>[guideNameKey(g.name),id]));
function exerciseGuideId(id,assigned){
 if(Object.hasOwn(exerciseGuides,assigned?.techniqueGuideId))return assigned.techniqueGuideId;
 if(Object.hasOwn(exerciseGuides,id))return id;
 if(assigned?.name==='Press QA' && assigned.muscle==='Pecho' && assigned.equipment==='Máquina')return 'chest_press';
 return guideIdsByName.get(guideNameKey(assigned?.name)) || (guideNameKey(assigned?.name)==='facepull'?'face_pull':undefined);
}

function exercisePhotoHtml(id,assigned){
 const key=exerciseGuideId(id,assigned),guide=exerciseGuides[key];
 if(!guide)return '';
 const base=guide.src==='fjz'?'':'./exercise-media/';
 const labels=guide.files.length===1?['Posición']:['Inicio','Posición de trabajo'];
 const figures=labels.map((label,i)=>{
   const visual='<img loading="lazy" decoding="async" width="256" height="216" src="'+base+guide.files[i]+'" alt="'+esc(guide.name+' · '+label)+'">';
   return '<figure>'+visual+'<figcaption>'+label+'</figcaption></figure>';
 }).join('');
 return '<details class="exercise-demo fjz-tech-guide" '+(assigned?'open':'')+'><summary>Guía de técnica</summary>'+(guide.attachment?'<p>'+esc(guide.attachment)+'</p>':'')+'<div class="fjz-tech-frames">'+figures+'</div>'+
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
   if(!guide.archived||exercise?.techniqueGuideId===id)select.add(new Option(guide.name,id));
 }
 select.value=exerciseGuideId(exercise?.libId,exercise)||'';
 select.onchange=()=>{preview.innerHTML=exercisePhotoHtml(id,{...exercise,techniqueGuideId:select.value})};
 label.append(select);field.after(label);
}
