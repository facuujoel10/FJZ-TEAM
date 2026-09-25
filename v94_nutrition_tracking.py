import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")
html=html.replace("TEAM FJZ V9.3","TEAM FJZ V9.4")

css=r"""
<style id="v94NutritionTracking">
.v94-statusbar{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:12px;padding:10px 12px;border:1px solid var(--border);border-radius:12px;background:#0d0d10}
.v94-supp-card{margin-top:14px}
.v94-supp-list{display:grid;gap:8px;margin-top:10px}
.v94-supp-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;padding:10px;border:1px solid var(--border);border-radius:11px;background:#0d0d10}
.v94-supp-row strong{font-size:12px}
.v94-supp-meta{font-size:10px;color:var(--muted);margin-top:3px}
.v94-source-note{margin-top:8px;padding:8px 10px;border:1px solid var(--border);border-radius:10px;background:#0d0d10;font-size:10px;color:var(--muted)}
.v94-chart{position:relative;border:1px solid var(--border);border-radius:14px;padding:12px;background:linear-gradient(180deg,rgba(255,255,255,.02),rgba(255,255,255,0))}
.v94-chart-head{display:flex;justify-content:space-between;align-items:flex-end;gap:10px;margin-bottom:8px}
.v94-chart-value{font-size:22px;font-weight:900;letter-spacing:-.6px}
.v94-chart-delta{font-size:10px;font-weight:800;padding:4px 7px;border-radius:999px;border:1px solid var(--border)}
.v94-chart svg{width:100%;height:190px;display:block;overflow:visible}
.v94-chart-grid{stroke:currentColor;opacity:.10;stroke-width:1}
.v94-chart-line{fill:none;stroke:currentColor;stroke-width:3;vector-effect:non-scaling-stroke}
.v94-chart-dot{fill:currentColor}
.v94-chart-axis{display:flex;justify-content:space-between;font-size:9px;color:var(--muted);margin-top:4px}
.v94-measure-standard{display:grid;grid-template-columns:1fr 1fr;gap:10px}
@media(max-width:620px){.v94-supp-row{grid-template-columns:1fr}.v94-measure-standard{grid-template-columns:1fr}}
</style>
"""

js=r"""
<script id="v94NutritionTrackingRuntime">
(function(){
  let suppCacheV94=null;
  let suppEditIndexV94=null;

  function cleanMeasureCompareV94(){
    const nodes=[...document.querySelectorAll('.v93-compare,#v93MeasureCompare')];
    nodes.slice(1).forEach(n=>n.remove());
    const card=nodes[0];
    if(card){
      card.querySelectorAll('.v93-measure-row').forEach(function(row){
        const label=row.querySelector('strong')?.textContent?.trim()||'';
        if(['Abdomen','Brazo der.','Muslo der.'].includes(label)){row.remove();return}
        if(label==='Brazo izq.')row.querySelector('strong').textContent='Brazo';
        if(label==='Muslo izq.')row.querySelector('strong').textContent='Muslo';
      });
    }
  }

  function normalizeMeasureFormV94(){
    document.querySelectorAll('#mAbd').forEach(function(input){input.closest('label')?.remove()});
    document.querySelectorAll('#mArmRight,#mThighRight').forEach(function(input){input.closest('label')?.remove()});
    document.querySelectorAll('#mArmLeft').forEach(function(input){input.id='mArm';const l=input.closest('label');if(l)l.childNodes[0].textContent='Brazo cm'});
    document.querySelectorAll('#mThighLeft').forEach(function(input){input.id='mThigh';const l=input.closest('label');if(l)l.childNodes[0].textContent='Muslo cm'});
    const weight=document.getElementById('mWeight');
    const grid=weight?.closest('.form-grid');
    if(grid&&!document.getElementById('mArm')){
      const l=document.createElement('label');
      l.className='tiny muted';
      l.innerHTML='Brazo cm<input id="mArm" class="input" type="number" step="0.1" min="10" max="100">';
      grid.appendChild(l);
    }
    if(grid&&!document.getElementById('mThigh')){
      const l=document.createElement('label');
      l.className='tiny muted';
      l.innerHTML='Muslo cm<input id="mThigh" class="input" type="number" step="0.1" min="15" max="150">';
      grid.appendChild(l);
    }
  }

  window.submitMeasurement=async function(){
    if(!cloudEnabled||!supabaseClient){toast('Las mediciones requieren modo nube');return}
    const athleteId=trackingAthleteId();if(!athleteId){toast('No encuentro la ficha');return}
    const n=id=>{const x=el(id)?.value;return x?+x:null};
    const payload={
      athlete_id:athleteId,
      student_id:trackingStudentUserId(),
      measured_on:el('mDate')?.value||dateInputToday(),
      weight_kg:n('mWeight'),
      waist_cm:n('mWaist'),
      abdomen_cm:null,
      hip_cm:n('mHip'),
      chest_cm:n('mChest'),
      arm_left_cm:n('mArm'),
      arm_right_cm:null,
      thigh_left_cm:n('mThigh'),
      thigh_right_cm:null
    };
    const {error}=await supabaseClient.from('body_measurements').upsert(payload,{onConflict:'athlete_id,measured_on'});
    if(error){toast(cloudErr(error));return}
    trackingLoadedFor=null;await loadTracking(true);
    if(currentProfile.role==='student')renderStudentTrackingHistory();else renderTrackingCoachLoaded();
    toast('Medición guardada');
  };

  window.simpleLineChart=function(rows,key,label){
    const pts=(rows||[]).filter(x=>x[key]!=null).slice().reverse();
    if(pts.length<2)return '<div class="empty">Necesitamos al menos 2 registros para mostrar la tendencia.</div>';
    const vals=pts.map(x=>+x[key]),first=vals[0],last=vals[vals.length-1],delta=last-first;
    let min=Math.min(...vals),max=Math.max(...vals);
    if(min===max){min-=1;max+=1}
    const extra=(max-min)*.12;min-=extra;max+=extra;
    const w=680,h=190,padX=22,padY=20;
    const xy=vals.map((v,i)=>[
      padX+(w-padX*2)*(i/Math.max(1,vals.length-1)),
      h-padY-(h-padY*2)*((v-min)/(max-min))
    ]);
    const grid=[.25,.5,.75].map(t=>'<line class="v94-chart-grid" x1="'+padX+'" x2="'+(w-padX)+'" y1="'+(padY+(h-padY*2)*t)+'" y2="'+(padY+(h-padY*2)*t)+'"/>').join('');
    const points=xy.map(p=>p[0]+','+p[1]).join(' ');
    const dots=xy.map((p,i)=>'<circle class="v94-chart-dot" cx="'+p[0]+'" cy="'+p[1]+'" r="'+(i===xy.length-1?5:3.5)+'"/>').join('');
    const d1=pts[0].measured_on||pts[0].week_start||'';
    const d2=pts[pts.length-1].measured_on||pts[pts.length-1].week_start||'';
    return '<div class="v94-chart"><div class="v94-chart-head"><div><div class="muted micro">'+esc(label)+'</div><div class="v94-chart-value">'+last.toLocaleString('es-AR',{maximumFractionDigits:1})+'</div></div><span class="v94-chart-delta">'+(delta>0?'+':'')+delta.toLocaleString('es-AR',{maximumFractionDigits:1})+'</span></div><svg viewBox="0 0 '+w+' '+h+'" preserveAspectRatio="none">'+grid+'<polyline class="v94-chart-line" points="'+points+'"/>'+dots+'</svg><div class="v94-chart-axis"><span>'+esc(String(d1))+'</span><span>'+esc(String(d2))+'</span></div></div>';
  };

  async function loadSupplementsV94(){
    if(suppCacheV94)return suppCacheV94;
    const {data,error}=await supabaseClient.from('supplement_library').select('*').order('category').order('name');
    if(error)throw error;
    suppCacheV94=data||[];
    return suppCacheV94;
  }
  function suppDataV94(){
    const pd=nutritionPlanData();
    pd.supplements=pd.supplements||[];
    return pd.supplements;
  }
  function suppRowsV94(studentView=false){
    const arr=suppDataV94();
    if(!arr.length)return '<div class="empty">Sin suplementos cargados.</div>';
    return '<div class="v94-supp-list">'+arr.map((s,i)=>'<div class="v94-supp-row"><div><strong>'+esc(s.name||'Suplemento')+'</strong><div class="v94-supp-meta">'+esc([s.amount&&s.unit?(s.amount+' '+s.unit):'',s.timing||'',s.notes||''].filter(Boolean).join(' · '))+'</div></div>'+(studentView?'':'<div class="pill-row"><button class="btn small" onclick="editSupplementV94('+i+')">Editar</button><button class="btn ghost small" onclick="removeSupplementV94('+i+')">Quitar</button></div>')+'</div>').join('')+'</div>';
  }
  function injectCoachNutritionV94(){
    if(currentProfile?.role!=='coach'||coachStudentTab!=='nutrition')return;
    const b=el('coachStudentBody'),p=nutritionCache.plan;if(!b||!p)return;
    if(!el('v94NutStatus')){
      const first=b.querySelector('.card');
      if(first){
        const bar=document.createElement('div');bar.id='v94NutStatus';bar.className='v94-statusbar';
        bar.innerHTML='<div><strong>'+(p.active===false?'Plan pausado':'Plan activo')+'</strong><div class="muted tiny">'+(p.active===false?'El alumno no ve el plan hasta que lo reactives.':'Visible para el alumno.')+'</div></div><button class="btn '+(p.active===false?'primary':'ghost')+' small" onclick="toggleNutritionActiveV94()">'+(p.active===false?'Reactivar plan':'Pausar / quitar plan')+'</button>';
        first.appendChild(bar);
      }
    }
    if(!el('v94SuppCoach')){
      const card=document.createElement('div');card.id='v94SuppCoach';card.className='card v94-supp-card';
      card.innerHTML='<div class="section-title"><div><h3>Suplementos</h3><div class="muted tiny">Opcional. Cargá solo lo que corresponda al plan; la app no asigna dosis automáticas.</div></div><button class="btn small" onclick="openSupplementPickerV94()">+ Suplemento</button></div>'+suppRowsV94(false)+'<div class="muted micro" style="margin-top:8px">Los cambios quedan incluidos cuando guardás el plan nutricional.</div>';
      const first=b.querySelector('.card');if(first)first.insertAdjacentElement('afterend',card);else b.appendChild(card);
    }
  }
  function injectStudentSuppV94(){
    if(currentProfile?.role!=='student'||studentTab!=='nutrition')return;
    const p=nutritionCache.plan;if(!p||p.active===false)return;
    const arr=nutritionPlanData()?.supplements||[];if(!arr.length||el('v94SuppStudent'))return;
    const b=el('studentSubBody');if(!b)return;
    const card=document.createElement('div');card.id='v94SuppStudent';card.className='card v94-supp-card';
    card.innerHTML='<div class="section-title"><div><h3>Suplementos del plan</h3><div class="muted tiny">Seguí las cantidades e indicaciones cargadas por tu coach/profesional.</div></div></div>'+suppRowsV94(true);
    const first=b.querySelector('.card');if(first)first.insertAdjacentElement('afterend',card);else b.prepend(card);
  }

  window.toggleNutritionActiveV94=async function(){
    const p=nutritionCache.plan;if(!p)return;
    const next=p.active===false;
    const {data,error}=await supabaseClient.from('nutrition_plans').update({active:next,updated_at:new Date().toISOString()}).eq('id',p.id).select('*').single();
    if(error){toast(cloudErr(error));return}
    nutritionCache.plan=data;renderNutritionCoachLoaded();toast(next?'Plan reactivado':'Plan pausado para el alumno');
  };

  window.openSupplementPickerV94=async function(){
    try{
      const arr=await loadSupplementsV94();
      showModal('<div class="modal-head"><div><h3>Agregar suplemento</h3><div class="muted tiny">Elegí uno de la biblioteca o cargá otro manualmente.</div></div><button class="btn small" onclick="closeModal()">✕</button></div><div class="library">'+arr.map(s=>'<button class="food-choice" onclick="chooseSupplementV94(\''+s.id+'\')"><strong>'+esc(s.name)+'</strong><small>'+esc(s.category)+'</small></button>').join('')+'</div><button class="btn" style="width:100%;margin-top:10px" onclick="chooseSupplementV94(\'custom\')">+ Otro suplemento</button>');
    }catch(e){toast(cloudErr(e))}
  };
  window.chooseSupplementV94=function(id){
    const s=(suppCacheV94||[]).find(x=>x.id===id);
    suppEditIndexV94=null;
    openSupplementEditorV94({name:s?.name||'',amount:'',unit:'g',timing:'',notes:s?.notes||''});
  };
  window.editSupplementV94=function(i){
    const s=suppDataV94()[i];if(!s)return;suppEditIndexV94=i;openSupplementEditorV94(s);
  };
  function openSupplementEditorV94(s){
    showModal('<div class="modal-head"><h3>Suplemento</h3><button class="btn small" onclick="closeModal()">✕</button></div><div class="form-grid"><label class="tiny muted span2">Nombre<input id="v94SuppName" class="input" value="'+esc(s.name||'')+'" placeholder="Nombre"></label><label class="tiny muted">Cantidad<input id="v94SuppAmount" class="input" type="number" min="0" step="0.1" value="'+esc(String(s.amount??''))+'"></label><label class="tiny muted">Unidad<select id="v94SuppUnit" class="input">'+['g','mg','ml','cápsula','tableta','scoop','unidad'].map(u=>'<option '+(s.unit===u?'selected':'')+'>'+u+'</option>').join('')+'</select></label><label class="tiny muted span2">Momento / frecuencia<input id="v94SuppTiming" class="input" value="'+esc(s.timing||'')+'" placeholder="Ej: con desayuno / según plan"></label><label class="tiny muted span2">Indicación<textarea id="v94SuppNotes" class="input" rows="3">'+esc(s.notes||'')+'</textarea></label></div><button class="btn primary" style="width:100%;margin-top:12px" onclick="saveSupplementV94()">Guardar suplemento</button>');
  }
  window.saveSupplementV94=function(){
    const name=el('v94SuppName')?.value.trim();if(!name){toast('Escribí el nombre');return}
    const amount=el('v94SuppAmount')?.value;
    const item={name,amount:amount===''?'':Number(amount),unit:el('v94SuppUnit')?.value||'',timing:el('v94SuppTiming')?.value.trim()||'',notes:el('v94SuppNotes')?.value.trim()||''};
    const arr=suppDataV94();if(suppEditIndexV94==null)arr.push(item);else arr[suppEditIndexV94]=item;
    closeModal();renderNutritionCoachLoaded();toast('Suplemento agregado al plan');
  };
  window.removeSupplementV94=function(i){suppDataV94().splice(i,1);renderNutritionCoachLoaded()};

  const oldCoachNutV94=window.renderNutritionCoachLoaded;
  if(typeof oldCoachNutV94==='function')window.renderNutritionCoachLoaded=function(){oldCoachNutV94();setTimeout(injectCoachNutritionV94,0)};

  const oldStudentNutV94=window.renderNutritionStudentLoaded;
  if(typeof oldStudentNutV94==='function')window.renderNutritionStudentLoaded=function(){
    const p=nutritionCache.plan;
    if(p?.active===false){
      nutritionCache.plan=null;oldStudentNutV94();nutritionCache.plan=p;
      const b=el('studentSubBody');if(b){
        const first=b.querySelector('.card');if(first){first.innerHTML='<div class="empty">No tenés un plan nutricional activo en este momento.</div>'}
      }
    }else oldStudentNutV94();
    setTimeout(injectStudentSuppV94,0);
  };

  const oldFoodPickerV94=window.openNutritionFoodPicker;
  if(typeof oldFoodPickerV94==='function')window.openNutritionFoodPicker=function(){
    oldFoodPickerV94.apply(this,arguments);
    const modal=document.querySelector('.modal-content,.modal-card,.modal')||document.body;
    if(modal&&!document.getElementById('v94FoodSource')){
      const note=document.createElement('div');note.id='v94FoodSource';note.className='v94-source-note';
      note.textContent='Macros de referencia: para alimentos genéricos se priorizan valores de USDA FoodData Central; en productos comerciales manda la etiqueta de la marca.';
      modal.appendChild(note);
    }
  };

  function polishAllV94(){normalizeMeasureFormV94();cleanMeasureCompareV94();injectCoachNutritionV94();injectStudentSuppV94()}
  const oldRenderV94=window.render;
  window.render=function(){oldRenderV94();setTimeout(polishAllV94,60);setTimeout(polishAllV94,500);setTimeout(polishAllV94,1100)};

  const obs=new MutationObserver(function(){cleanMeasureCompareV94();normalizeMeasureFormV94()});
  setTimeout(function(){const v=el('view');if(v)obs.observe(v,{childList:true,subtree:true});polishAllV94()},150);

  Object.assign(window,{toggleNutritionActiveV94,openSupplementPickerV94,chooseSupplementV94,editSupplementV94,saveSupplementV94,removeSupplementV94});
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)
p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8").replace("team-fjz-v9-3","team-fjz-v9-4")
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V9.4 nutricion/seguimiento:",len(html),"bytes")
