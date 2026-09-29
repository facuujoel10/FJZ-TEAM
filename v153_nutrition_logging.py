import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v153NutritionLoggingStyles">
.v153-food-note{
  margin-top:10px;padding:10px 12px;border:1px solid rgba(90,167,255,.22);
  border-radius:12px;background:rgba(90,167,255,.045)
}
.v153-food-note strong{font-size:11px}
.v153-food-note .muted{margin-top:3px}
.v153-save-status{
  margin-top:8px;font-size:10px;color:var(--muted)
}
.v153-disabled{
  margin-top:10px;padding:10px 12px;border:1px solid var(--border);
  border-radius:12px;background:rgba(255,255,255,.025)
}
</style>
"""

js=r"""
<script id="v153NutritionLoggingRuntime">
(function(){
  const VERSION='15.3';
  let saveBusy=false;

  function canStudentLogV153(){
    const p=nutritionCache?.plan;
    return !!p && p.active!==false && p.student_logging_enabled!==false;
  }

  function numV153(v){
    const n=Number(v);
    return Number.isFinite(n)?n:0;
  }

  function setBusyV153(on){
    saveBusy=!!on;
    const selectors=[
      'button[onclick*="addCalculatorLog"]',
      'button[onclick*="confirmCustomMacroLog"]',
      'button[onclick*="logPlanOption"]'
    ].join(',');
    document.querySelectorAll(selectors).forEach(btn=>{
      if(on){
        if(!btn.dataset.v153Text)btn.dataset.v153Text=btn.textContent||'Guardar';
        btn.disabled=true;
        btn.textContent='Guardando…';
      }else{
        btn.disabled=false;
        if(btn.dataset.v153Text){
          btn.textContent=btn.dataset.v153Text;
          delete btn.dataset.v153Text;
        }
      }
    });
  }

  function validateNutritionLogV153(data){
    const name=String(data?.food_name||'').trim();
    const grams=Number(data?.grams);
    if(!name)return 'Falta el nombre del alimento';
    if(!Number.isFinite(grams)||grams<0.1||grams>5000)return 'Revisá la cantidad consumida';
    const vals=[
      ['calorías',Number(data?.kcal),20000],
      ['proteína',Number(data?.protein_g),2000],
      ['carbohidratos',Number(data?.carbs_g),3000],
      ['grasas',Number(data?.fat_g),1000]
    ];
    for(const [label,v,max] of vals){
      if(!Number.isFinite(v)||v<0||v>max)return 'Revisá '+label;
    }
    return '';
  }

  window.insertNutritionLog=async function(data){
    if(saveBusy)return false;
    if(currentProfile?.role==='student'&&!canStudentLogV153()){
      const p=nutritionCache?.plan;
      toast(!p||p.active===false
        ? 'Tu registro nutricional todavía no está habilitado'
        : 'Tu coach tiene desactivado el registro de comidas');
      return false;
    }

    const athleteId=nutritionAthleteId();
    if(!athleteId){toast('No encuentro tu ficha nutricional');return false}

    const payload={
      athlete_id:athleteId,
      student_id:currentProfile?.role==='student'?currentUser.id:trackingStudentUserId(),
      logged_on:nutritionCache.date||dateInputToday(),
      meal_label:String(data?.meal_label||'Comida'),
      food_id:data?.food_id||null,
      food_name:String(data?.food_name||'').trim(),
      grams:numV153(data?.grams),
      kcal:numV153(data?.kcal),
      protein_g:numV153(data?.protein_g),
      carbs_g:numV153(data?.carbs_g),
      fat_g:numV153(data?.fat_g),
      source:data?.source||'custom',
      note:String(data?.note||''),
      measure_type:data?.measure_type||'grams',
      quantity:data?.quantity??null,
      unit_name:data?.unit_name??null
    };

    const invalid=validateNutritionLogV153(payload);
    if(invalid){toast(invalid);return false}

    setBusyV153(true);
    try{
      const {error}=await supabaseClient.from('nutrition_logs').insert(payload);
      if(error){toast(cloudErr(error));return false}

      await loadNutrition(true,nutritionCache.date);
      if(currentProfile?.role==='student')renderNutritionStudentLoaded();
      else renderNutritionCoachLoaded();
      toast('Agregado al registro');
      return true;
    }catch(e){
      toast(cloudErr(e));
      return false;
    }finally{
      setBusyV153(false);
    }
  };

  window.addCalculatorLog=async function(){
    if(saveBusy)return;
    const f=nutritionCache.foods.find(x=>x.id===el('macroFood')?.value);
    if(!f){toast('Elegí un alimento');return}
    const grams=Math.max(.1,numV153(el('macroGrams')?.value||100));
    const m=macroCalcFrom100(f,grams);
    return insertNutritionLog({
      food_id:f.id,
      food_name:f.name,
      grams,
      ...m,
      meal_label:el('macroMeal')?.value||'Comida',
      source:'calculator'
    });
  };

  window.openCustomMacroLog=function(){
    if(currentProfile?.role==='student'&&!canStudentLogV153()){
      toast(nutritionCache?.plan?.student_logging_enabled===false
        ? 'Tu coach tiene desactivado el registro de comidas'
        : 'Tu registro nutricional todavía no está habilitado');
      return;
    }

    showModal(
      '<div class="modal-head"><div><h3>Registrar alimento personalizado</h3>'+
      '<div class="muted tiny">Para algo que comiste aunque no esté en tu dieta ni en la biblioteca.</div></div>'+
      '<button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="form-grid">'+
      '<label class="tiny muted span2">Nombre<input id="cmName" class="input" placeholder="Ej: alfajor, tarta, yogur de una marca..."></label>'+
      '<label class="tiny muted">Cantidad consumida (g/ml)<input id="cmGrams" class="input" type="number" min="0.1" step="0.1" value="100"></label>'+
      '<label class="tiny muted">Comida<select id="cmMeal"><option>Desayuno</option><option>Almuerzo</option><option>Merienda</option><option>Cena</option><option>Pre entreno</option><option>Post entreno</option><option>Colación</option><option>Otra</option></select></label>'+
      '<label class="tiny muted span2">Los valores que tenés son<select id="cmModeV153" class="input" onchange="updateCustomMacroModeV153()"><option value="portion">De la porción que comí</option><option value="per100">Por 100 g/ml</option></select></label>'+
      '<label class="tiny muted">Calorías<input id="cmKcal" class="input" type="number" min="0" step="0.1"></label>'+
      '<label class="tiny muted">Proteína (g)<input id="cmP" class="input" type="number" min="0" step="0.1"></label>'+
      '<label class="tiny muted">Carbohidratos (g)<input id="cmC" class="input" type="number" min="0" step="0.1"></label>'+
      '<label class="tiny muted">Grasas (g)<input id="cmF" class="input" type="number" min="0" step="0.1"></label>'+
      '</div>'+
      '<div id="cmModeHelpV153" class="v153-food-note"><strong>Macros de la porción consumida</strong><div class="muted tiny">Copiá los valores de la porción que realmente comiste. No hace falta convertirlos a 100 g.</div></div>'+
      '<button class="btn primary" style="width:100%;margin-top:12px" onclick="confirmCustomMacroLog()">Guardar en mi registro</button>'
    );
  };

  window.updateCustomMacroModeV153=function(){
    const help=el('cmModeHelpV153'),mode=el('cmModeV153')?.value||'portion';
    if(!help)return;
    help.innerHTML=mode==='per100'
      ? '<strong>Valores por 100 g/ml</strong><div class="muted tiny">La app los ajusta automáticamente a la cantidad que comiste.</div>'
      : '<strong>Macros de la porción consumida</strong><div class="muted tiny">Copiá los valores de la porción que realmente comiste. No hace falta convertirlos a 100 g.</div>';
  };

  window.confirmCustomMacroLog=async function(){
    if(saveBusy)return;
    const name=el('cmName')?.value.trim()||'';
    if(!name){toast('Poné el nombre del alimento');return false}

    const grams=Math.max(.1,numV153(el('cmGrams')?.value||0));
    if(!grams){toast('Poné la cantidad que consumiste');return false}

    const raw={
      kcal:numV153(el('cmKcal')?.value),
      protein_g:numV153(el('cmP')?.value),
      carbs_g:numV153(el('cmC')?.value),
      fat_g:numV153(el('cmF')?.value)
    };
    if(!(raw.kcal>0||raw.protein_g>0||raw.carbs_g>0||raw.fat_g>0)){
      toast('Cargá al menos un dato nutricional');
      return false;
    }

    const mode=el('cmModeV153')?.value||'portion';
    const macros=mode==='per100'
      ? macroCalcFrom100({
          kcal_100g:raw.kcal,
          protein_100g:raw.protein_g,
          carbs_100g:raw.carbs_g,
          fat_100g:raw.fat_g
        },grams)
      : raw;

    const ok=await insertNutritionLog({
      food_id:null,
      food_name:name,
      grams,
      ...macros,
      meal_label:el('cmMeal')?.value||'Comida',
      source:'custom'
    });
    if(ok)closeModal();
    return ok;
  };

  window.logPlanOption=async function(mealId,optId){
    if(saveBusy)return false;
    if(currentProfile?.role==='student'&&!canStudentLogV153()){
      toast('Tu coach tiene desactivado el registro de comidas');
      return false;
    }
    const m=findNutritionMeal(mealId),o=findNutritionOption(mealId,optId);
    if(!m||!o||!(o.items||[]).length){toast('Esta opción no tiene alimentos');return false}

    const rows=o.items.map(i=>({
      athlete_id:nutritionAthleteId(),
      student_id:currentUser.id,
      logged_on:nutritionCache.date||dateInputToday(),
      meal_label:m.name,
      food_id:i.food_id||null,
      food_name:i.name,
      grams:i.grams,
      kcal:i.kcal,
      protein_g:i.protein_g,
      carbs_g:i.carbs_g,
      fat_g:i.fat_g,
      source:'plan'
    }));

    setBusyV153(true);
    try{
      const {error}=await supabaseClient.from('nutrition_logs').insert(rows);
      if(error){toast(cloudErr(error));return false}
      await loadNutrition(true,nutritionCache.date);
      renderNutritionStudentLoaded();
      toast('Opción registrada');
      return true;
    }catch(e){
      toast(cloudErr(e));
      return false;
    }finally{
      setBusyV153(false);
    }
  };

  const baseStudentNutritionV153=renderNutritionStudentLoaded;
  renderNutritionStudentLoaded=function(){
    const out=baseStudentNutritionV153.apply(this,arguments);
    const host=el('studentSubBody');
    if(!host)return out;

    const canSave=canStudentLogV153();
    host.querySelectorAll('.card').forEach(card=>{
      const h=(card.querySelector('h3')?.textContent||'').trim();
      if(h==='Calculadora de macros'){
        const sub=card.querySelector('.section-title .muted.tiny');
        if(canSave){
          if(sub)sub.textContent='Calculá y registrá cualquier alimento, aunque no esté dentro de tu dieta.';
          if(!card.querySelector('#v153OffPlanNote')){
            const note=document.createElement('div');
            note.id='v153OffPlanNote';
            note.className='v153-food-note';
            note.innerHTML='<strong>¿Comiste algo fuera del plan?</strong><div class="muted tiny">Buscalo en la biblioteca o tocá “+ Personalizado”. Se guarda solo en tu registro del día; no modifica la dieta indicada por tu coach.</div>';
            const actions=card.querySelector('.nutrition-builder-actions');
            if(actions)actions.insertAdjacentElement('afterend',note);
          }
        }else{
          if(sub)sub.textContent='Podés usar la calculadora como referencia, pero el guardado diario no está habilitado.';
          card.querySelectorAll('.nutrition-builder-actions').forEach(x=>x.style.display='none');
          if(!card.querySelector('#v153DisabledLog')){
            const box=document.createElement('div');
            box.id='v153DisabledLog';
            box.className='v153-disabled';
            box.innerHTML='<strong>Guardado desactivado</strong><div class="muted tiny" style="margin-top:3px">Para guardar alimentos —incluidos los que no están en tu dieta— tu coach debe activar “Registro de comidas del alumno”.</div>';
            card.appendChild(box);
          }
        }
      }
      if(h==='Registro del día'&&!canSave)card.style.display='none';
    });
    return out;
  };

  const baseCoachNutritionV153=renderNutritionCoachLoaded;
  renderNutritionCoachLoaded=function(){
    const out=baseCoachNutritionV153.apply(this,arguments);
    const hint=el('v64LoggingHint');
    const enabled=nutritionCache?.plan?.student_logging_enabled!==false;
    if(hint){
      hint.textContent=enabled
        ? 'Activado: el alumno puede registrar su plan y también alimentos que haya comido fuera de la dieta.'
        : 'Desactivado: puede consultar el plan y calcular macros, pero no puede guardar lo que comió. Guardá el plan para aplicar el cambio.';
    }
    return out;
  };

  window.__fjzNutritionLoggingV153={
    version:VERSION,
    customOffPlanFood:true,
    portionOrPer100:true,
    duplicateSubmitGuard:true,
    closeAfterConfirmedSave:true,
    disabledLoggingExplained:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzNutritionLoggingV153",
  "customOffPlanFood:true",
  "portionOrPer100:true",
  "duplicateSubmitGuard:true",
  "closeAfterConfirmedSave:true",
  "disabledLoggingExplained:true"
]:
    if marker not in html:
        raise RuntimeError("V15.3 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V15.3 nutrition logging reliability enabled")
