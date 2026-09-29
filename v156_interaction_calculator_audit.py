import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v156InteractionCalculatorAuditStyles">
/* Mobile form hardening across every tab. */
@media(max-width:760px){
  html{
    scroll-padding-bottom:calc(120px + env(safe-area-inset-bottom));
  }
  #view,#coachStudentBody,#studentSubBody{
    min-height:0;
    scroll-padding-bottom:calc(120px + env(safe-area-inset-bottom));
  }
  #view input,#view select,#view textarea,
  #coachStudentBody input,#coachStudentBody select,#coachStudentBody textarea,
  #studentSubBody input,#studentSubBody select,#studentSubBody textarea,
  .modal input,.modal select,.modal textarea{
    font-size:16px!important;
    touch-action:manipulation!important;
    pointer-events:auto!important;
  }
  input,select,textarea,button,.btn{
    scroll-margin-top:90px;
    scroll-margin-bottom:calc(120px + env(safe-area-inset-bottom));
  }
  .bottom-nav{
    padding-bottom:max(8px,env(safe-area-inset-bottom))!important;
  }
  .modal-wrap.v155-scroll-shell{
    height:var(--v156-visual-height,100dvh)!important;
    max-height:var(--v156-visual-height,100dvh)!important;
  }
  .modal.v155-exercise-modal{
    scroll-padding-bottom:110px;
  }
}
</style>
"""

js=r"""
<script id="v156InteractionCalculatorAuditRuntime">
(function(){
  const VERSION='15.6';
  let scheduledRenderPending=false;

  function activeEditableV156(){
    const a=document.activeElement;
    return !!(a&&a.matches?.('input:not([type="button"]):not([type="submit"]),textarea,select,[contenteditable="true"]'));
  }

  function syncVisualHeightV156(){
    const wrap=el('modalWrap');
    if(!wrap)return;
    const h=Math.round(window.visualViewport?.height||window.innerHeight||0);
    if(h>0)wrap.style.setProperty('--v156-visual-height',h+'px');
  }

  // Scheduled/background renders must never erase text while somebody is typing.
  const baseScheduledRenderV156=window.fjzScheduleRenderV125;
  if(typeof baseScheduledRenderV156==='function'){
    window.fjzScheduleRenderV125=function(){
      if(activeEditableV156()){
        scheduledRenderPending=true;
        window.__fjzUiAuditV156.deferredRenders++;
        return;
      }
      scheduledRenderPending=false;
      return baseScheduledRenderV156.apply(this,arguments);
    };
  }

  if(!window.__fjzV156FocusBound){
    window.__fjzV156FocusBound=true;
    document.addEventListener('focusout',()=>{
      if(!scheduledRenderPending)return;
      setTimeout(()=>{
        if(scheduledRenderPending&&!activeEditableV156()&&typeof baseScheduledRenderV156==='function'){
          scheduledRenderPending=false;
          baseScheduledRenderV156();
        }
      },80);
    },true);
  }

  // Keep all modals inside the real iPhone visual viewport (HUD / keyboard included).
  const baseShowModalV156=showModal;
  showModal=function(){
    const out=baseShowModalV156.apply(this,arguments);
    syncVisualHeightV156();
    return out;
  };
  if(window.visualViewport&&!window.__fjzV156VisualBound){
    window.__fjzV156VisualBound=true;
    window.visualViewport.addEventListener('resize',syncVisualHeightV156,{passive:true});
    window.visualViewport.addEventListener('scroll',syncVisualHeightV156,{passive:true});
  }

  function decimalV156(v){
    if(v===null||v===undefined||v==='')return 0;
    const n=Number(String(v).trim().replace(',','.'));
    return Number.isFinite(n)?n:0;
  }

  // V15.3 accidentally lost the unit-aware calculator state when saving.
  // Use the same state used by the preview, so what is shown is exactly what is saved.
  window.addCalculatorLog=async function(){
    const s=typeof macroInputState==='function'?macroInputState():null;
    const f=s?.food||nutritionCache?.foods?.find(x=>x.id===el('macroFood')?.value);
    if(!f){toast('Elegí un alimento');return false}
    const grams=Math.max(.1,decimalV156(s?.grams||el('macroGrams')?.value||100));
    const m=macroCalcFrom100(f,grams);
    return insertNutritionLog({
      food_id:f.id,
      food_name:f.name,
      grams,
      measure_type:s?.measure_type||'grams',
      quantity:s?.measure_type==='units'?s.quantity:null,
      unit_name:s?.measure_type==='units'?s.unit_name:null,
      ...m,
      meal_label:el('macroMeal')?.value||'Comida',
      source:'calculator'
    });
  };

  // Coach "Ver como alumno" must never try to save a plan log using the coach user id.
  window.logPlanOption=async function(mealId,optId){
    const m=findNutritionMeal(mealId),o=findNutritionOption(mealId,optId);
    if(!m||!o||!(o.items||[]).length){toast('Esta opción no tiene alimentos');return false}

    if(currentProfile?.role==='student'&&nutritionCache?.plan?.student_logging_enabled===false){
      toast('Tu coach tiene desactivado el registro de comidas');
      return false;
    }

    const athleteId=nutritionAthleteId();
    if(!athleteId){toast('No se encontró la ficha vinculada');return false}
    const studentId=currentProfile?.role==='student'?currentUser.id:trackingStudentUserId();
    if(!studentId){toast('No se encontró la cuenta del alumno');return false}

    const rows=o.items.map(i=>({
      athlete_id:athleteId,
      student_id:studentId,
      logged_on:nutritionCache.date||dateInputToday(),
      meal_label:m.name,
      food_id:i.food_id||null,
      food_name:i.name,
      grams:i.grams,
      kcal:i.kcal,
      protein_g:i.protein_g,
      carbs_g:i.carbs_g,
      fat_g:i.fat_g,
      source:'plan',
      measure_type:i.measure_type||'grams',
      quantity:(i.measure_type||'grams')==='units'?i.quantity:null,
      unit_name:(i.measure_type||'grams')==='units'?i.unit_name:null
    }));

    const buttons=[...document.querySelectorAll('button')].filter(b=>(b.getAttribute('onclick')||'').includes("logPlanOption("));
    buttons.forEach(b=>b.disabled=true);
    try{
      const {error}=await supabaseClient.from('nutrition_logs').insert(rows);
      if(error){toast(cloudErr(error));return false}
      await loadNutrition(true,nutritionCache.date);
      if(currentProfile?.role==='student')renderNutritionStudentLoaded();
      else renderNutritionCoachLoaded();
      toast('Opción registrada');
      return true;
    }catch(e){
      toast(cloudErr(e));
      return false;
    }finally{
      buttons.forEach(b=>b.disabled=false);
    }
  };

  // Make custom macro inputs reliable with Argentine decimal commas as well as dots.
  const baseOpenCustomMacroV156=window.openCustomMacroLog;
  if(typeof baseOpenCustomMacroV156==='function'){
    window.openCustomMacroLog=function(){
      const out=baseOpenCustomMacroV156.apply(this,arguments);
      ['cmGrams','cmKcal','cmP','cmC','cmF'].forEach(id=>{
        const x=el(id);
        if(!x)return;
        try{x.type='text'}catch(e){}
        x.inputMode='decimal';
        x.autocomplete='off';
      });
      return out;
    };
  }

  window.confirmCustomMacroLog=async function(){
    const name=el('cmName')?.value.trim()||'';
    if(!name){toast('Poné el nombre del alimento');return false}

    const grams=decimalV156(el('cmGrams')?.value);
    if(!(grams>0&&grams<=5000)){toast('Revisá la cantidad que consumiste');return false}

    const raw={
      kcal:decimalV156(el('cmKcal')?.value),
      protein_g:decimalV156(el('cmP')?.value),
      carbs_g:decimalV156(el('cmC')?.value),
      fat_g:decimalV156(el('cmF')?.value)
    };
    if(Object.values(raw).some(v=>v<0)){toast('Los macros no pueden ser negativos');return false}
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

  function visibleV156(elm){
    if(!elm||!elm.isConnected)return false;
    const s=getComputedStyle(elm),r=elm.getBoundingClientRect();
    return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0;
  }

  function scanV156(){
    const controls=[...document.querySelectorAll('input,select,textarea,button')].filter(visibleV156);
    const pointerBlocked=controls.filter(x=>getComputedStyle(x).pointerEvents==='none'&&!x.disabled);
    const zeroSized=controls.filter(x=>{
      const r=x.getBoundingClientRect();return r.width<2||r.height<2;
    });
    const duplicateIds=[...document.querySelectorAll('[id]')]
      .map(x=>x.id)
      .filter((id,i,a)=>id&&a.indexOf(id)!==i)
      .filter((id,i,a)=>a.indexOf(id)===i);
    const result={
      at:new Date().toISOString(),
      visibleControls:controls.length,
      pointerBlocked:pointerBlocked.map(x=>x.id||x.textContent?.trim().slice(0,40)||x.tagName),
      zeroSized:zeroSized.map(x=>x.id||x.tagName),
      duplicateIds
    };
    window.__fjzUiAuditV156.lastScan=result;
    return result;
  }

  window.__fjzUiAuditV156={
    version:VERSION,
    scheduledRenderFocusGuard:true,
    calculatorUnitsFixed:true,
    customDecimalComma:true,
    coachStudentLoggingFixed:true,
    mobileSafeArea:true,
    visualViewportModal:true,
    deferredRenders:0,
    lastScan:null,
    scan:scanV156
  };

  requestAnimationFrame(()=>scanV156());
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzUiAuditV156",
  "scheduledRenderFocusGuard:true",
  "calculatorUnitsFixed:true",
  "customDecimalComma:true",
  "coachStudentLoggingFixed:true",
  "mobileSafeArea:true",
  "visualViewportModal:true"
]:
    if marker not in html:
        raise RuntimeError("V15.6 missing marker: "+marker)

# Static safety checks for the interaction class of bugs being audited.
if re.search(r'(?:html|body)\s*\{[^}]*overflow-y\s*:\s*hidden',html,re.I|re.S):
    raise RuntimeError("V15.6 root vertical scroll is hidden")
if re.search(r'addEventListener\s*\(\s*[\'"]touchmove[\'"].*?preventDefault\s*\(',html,re.I|re.S):
    raise RuntimeError("V15.6 touchmove preventDefault detected")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V15.6 interaction/calculator audit hardening enabled")
