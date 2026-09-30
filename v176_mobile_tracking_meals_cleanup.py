import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# 1) RETIRE UNUSED NUTRITION EDUCATION / HABITS AT BUILD TIME
# =========================================================

# V13.6 Learn runtime is no longer needed. Keep its generic box-model CSS,
# but remove all runtime/education content and restore a two-tab nav below.
html,n136_script=re.subn(
    r'<script id="v136NutritionAndStabilityRuntime">.*?</script>',
    '',
    html,
    count=1,
    flags=re.S
)

# V13.8 Habits runtime is fully retired.
html,n138_script=re.subn(
    r'<script id="v138NutritionHabitsGuideRuntime">.*?</script>',
    '',
    html,
    count=1,
    flags=re.S
)
html=re.sub(
    r'<style id="v138NutritionHabitsGuideStyles">.*?</style>',
    '',
    html,
    count=1,
    flags=re.S
)

# Remove the older V6.6 habits engine too: it queried nutrition_habit_logs on
# every nutrition load and created its own realtime channel even though the
# feature is no longer part of the product.
html,n66=re.subn(
    r'// ===== TEAM FJZ V8\.3 · HÁBITOS DE NUTRICIÓN =====.*?(?=// ===== TEAM FJZ V8\.3 · SPOTIFY / MÚSICA =====)',
    '',
    html,
    count=1,
    flags=re.S
)

# V6.8 later redefined only the visual habits renderer before its Spotify fix.
# Remove that habits-only subsection while preserving Spotify.
html,n68_habits=re.subn(
    r'// --- Hábitos: pasan a ser consejos de lectura, no checklist ---.*?(?=// --- Spotify: búsqueda robusta de la ficha y pestaña propia ---)',
    '',
    html,
    count=1,
    flags=re.S
)

# Remove consolidated calls/table listeners that only existed for the retired
# habits feature. Optional chaining made these safe, but leaving them would be
# dead code.
html=html.replace("    window.__fjzPostRenderV136?.();\n","")
html=html.replace("    window.__fjzEnsureHabitsTabsV138?.();\n","")
html=html.replace("'nutrition_habit_logs',","")
html=html.replace('"nutrition_habit_logs",',"")

# Restore canonical student nutrition sub-navigation: Plan + Recipes only.
nav_re=r"""function nutritionRecipesNavV70\(active\)\{.*?\n\}"""
nav_fn=r"""function nutritionRecipesNavV70(active){
  return '<div class="v70-recipe-tabs v176-nutrition-tabs" id="v176NutritionTabs">'+
    '<button class="btn '+(active==='plan'?'primary':'')+'" onclick="switchNutritionViewV70(\'plan\')">Mi plan</button>'+
    '<button class="btn '+(active==='recipes'?'primary':'')+'" onclick="switchNutritionViewV70(\'recipes\')">Recetas</button>'+
  '</div>'
}"""
html,n_nav=re.subn(nav_re,nav_fn,html,count=1,flags=re.S)
if n_nav!=1:
    raise RuntimeError(f"V17.6 expected one nutritionRecipesNavV70, got {n_nav}")

# Remove the Learn dispatch branch that V13.6 had injected into the lexical
# nutrition renderer. The V13.8 habits branch lived inside its runtime and was
# removed above.
html,n_learn_branch=re.subn(
    r"\s*if\(nutritionStudentViewV70==='learn'\)return renderNutritionLearnV136\(\);",
    "",
    html,
    count=1
)

css=r"""
<style id="v176MobileTrackingMealsCleanupStyles">
/* ===== global responsive containment ===== */
#view,#coachStudentBody,#studentSubBody,
.card,.hero,.grid,.form-grid,.metric-grid,.modal,
.tracking-form,.nutrition-datebar,.v165-agenda-shell,.v165-week-row{
  min-width:0!important;
  max-width:100%;
  box-sizing:border-box
}
.form-grid>*,
.form-grid>label,
.tracking-form>*,
.v165-week-row>*,
.v165-week-row label,
.nutrition-datebar>*{
  min-width:0!important;
  max-width:100%;
  box-sizing:border-box
}
.form-grid input,.form-grid select,.form-grid textarea,
.tracking-form input,.tracking-form select,.tracking-form textarea,
.v165-week-row input,.v165-week-row select,
.v166-date-panel input,.v166-weekly-panel select,
.nutrition-datebar input,.nutrition-datebar select{
  width:100%!important;
  max-width:100%!important;
  min-width:0!important;
  min-inline-size:0!important;
  box-sizing:border-box!important
}
input[type="date"],input[type="time"]{
  max-width:100%!important;
  min-width:0!important;
  min-inline-size:0!important;
  box-sizing:border-box!important
}

/* Never break action labels in the middle of a word. */
.v176-nowrap-btn{
  white-space:nowrap!important;
  word-break:normal!important;
  overflow-wrap:normal!important;
  hyphens:none!important
}

/* ===== canonical measurement evolution ===== */
.v176-measure-history{
  margin-top:14px
}
.v176-measure-list{
  display:grid;
  gap:8px;
  margin-top:10px
}
.v176-measure-row{
  display:grid;
  grid-template-columns:100px minmax(0,1fr) auto;
  gap:10px;
  align-items:center;
  padding:10px 11px;
  border:1px solid var(--border);
  border-radius:12px;
  background:rgba(255,255,255,.02);
  min-width:0
}
.v176-measure-date strong{
  display:block;
  font-size:11px
}
.v176-measure-values{
  display:flex;
  flex-wrap:wrap;
  gap:5px;
  min-width:0
}
.v176-measure-chip{
  display:inline-flex;
  align-items:center;
  gap:4px;
  border:1px solid var(--border);
  border-radius:999px;
  padding:4px 7px;
  font-size:9px;
  color:var(--muted);
  background:rgba(255,255,255,.015)
}
.v176-measure-chip b{color:var(--text);font-weight:850}

/* ===== grouped meal composer ===== */
.v176-meal-composer{
  margin-top:12px;
  padding:12px;
  border:1px solid rgba(90,167,255,.26);
  border-radius:13px;
  background:rgba(90,167,255,.035)
}
.v176-meal-composer-head{
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  gap:10px
}
.v176-meal-composer-head h4{margin:0;font-size:12px}
.v176-meal-composer-head p{margin:3px 0 0;font-size:9px;color:var(--muted)}
.v176-meal-draft-list{
  display:grid;
  gap:7px;
  margin:10px 0
}
.v176-meal-draft-row{
  display:grid;
  grid-template-columns:minmax(0,1fr) auto;
  gap:9px;
  align-items:center;
  padding:8px 9px;
  border:1px solid var(--border);
  border-radius:10px;
  background:rgba(255,255,255,.02)
}
.v176-meal-draft-row strong{display:block;font-size:10px}
.v176-meal-draft-row .muted{margin-top:2px}
.v176-meal-group{
  border:1px solid rgba(90,167,255,.22);
  border-radius:13px;
  padding:10px;
  background:rgba(90,167,255,.025)
}
.v176-meal-group+.v176-meal-group,
.v176-meal-group+.nutrition-log-row,
.nutrition-log-row+.v176-meal-group{margin-top:8px}
.v176-meal-group-head{
  display:flex;
  justify-content:space-between;
  gap:10px;
  align-items:flex-start
}
.v176-meal-group-head h4{margin:0;font-size:11px}
.v176-meal-group-foods{
  display:grid;
  gap:5px;
  margin-top:8px;
  padding-top:8px;
  border-top:1px dashed rgba(255,255,255,.08)
}
.v176-meal-group-food{
  display:flex;
  justify-content:space-between;
  gap:8px;
  color:var(--muted);
  font-size:9px;
  line-height:1.35
}
.v176-meal-total{
  display:flex;
  flex-wrap:wrap;
  gap:5px;
  margin-top:7px
}

/* ===== Agenda mobile / intrinsic-width controls ===== */
@media(max-width:760px){
  .v165-week-row{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:8px!important;
    align-items:end!important
  }
  .v165-week-row .v165-day{
    grid-column:1/-1!important;
    width:100%!important
  }
  .v165-week-row input[type="time"],
  #v165Time,#v165Date,#ciWeek,#mDate,#progressPhotoDate,#nutritionLogDate{
    width:100%!important;
    max-width:100%!important;
    min-width:0!important;
    min-inline-size:0!important
  }
  .tracking-form .form-grid{
    grid-template-columns:1fr!important
  }
  .v176-measure-row{
    grid-template-columns:minmax(0,1fr) auto
  }
  .v176-measure-date{
    grid-column:1/2
  }
  .v176-measure-values{
    grid-column:1/-1
  }
  .v176-meal-composer-head,.v176-meal-group-head{
    display:block
  }
  .v176-meal-composer-head>.btn,.v176-meal-group-head>.btn{
    margin-top:8px
  }
}
@media(max-width:520px){
  .v165-week-row{
    grid-template-columns:1fr!important
  }
  .v165-week-row .v165-day{
    grid-column:auto!important
  }
  .v165-week-row label,
  .v165-week-row input,
  .v165-week-row select{
    width:100%!important;
    max-width:100%!important
  }
  .v176-measure-row{
    grid-template-columns:1fr!important
  }
  .v176-measure-row>.btn{
    width:100%
  }
  .v176-meal-draft-row{
    grid-template-columns:1fr auto
  }
  .nutrition-datebar{
    display:grid!important;
    grid-template-columns:1fr!important
  }
  .nutrition-datebar .btn{
    width:100%!important
  }
}
</style>
"""

js=r"""
<script id="v176MobileTrackingMealsCleanupRuntime">
(function(){
  const VERSION='17.6';

  /* =====================================================
     1) ROUTINE: ENTER AT TOP / FIRST EXERCISE
     ===================================================== */
  let lastRouteV176='';
  let routineScrollTokenV176=0;
  let lastUserInteractionV176=0;

  ['pointerdown','touchstart','wheel'].forEach(type=>{
    document.addEventListener(type,()=>{lastUserInteractionV176=performance.now()},{passive:true,capture:true});
  });

  function routeKeyV176(){
    return [
      currentProfile?.role||'',
      mode||'',
      coachTab||'',
      coachStudentTab||'',
      studentTab||'',
      state?.selectedStudentId||''
    ].join('|');
  }

  function routineActiveV176(){
    return currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='routine';
  }

  function resetRoutineScrollV176(token,entryAt){
    if(token!==routineScrollTokenV176||!routineActiveV176())return;
    const body=el('coachStudentBody');
    if(!body)return;
    const top=Math.max(0,body.getBoundingClientRect().top+window.scrollY-92);
    window.scrollTo({top,behavior:'auto'});
    const scroller=document.scrollingElement;
    if(scroller&&Math.abs(scroller.scrollTop-top)>4)scroller.scrollTop=top;
  }

  function scheduleRoutineTopV176(){
    const token=++routineScrollTokenV176;
    const entryAt=performance.now();
    requestAnimationFrame(()=>resetRoutineScrollV176(token,entryAt));
    [260,850].forEach(ms=>setTimeout(()=>{
      if(lastUserInteractionV176>entryAt)return;
      resetRoutineScrollV176(token,entryAt);
    },ms));
  }

  /* =====================================================
     2) TRACKING ASYNC GUARDS + EDITABLE MEASUREMENTS
     ===================================================== */
  function studentTrackingActiveV176(){
    if(!(currentProfile?.role==='student'&&mode==='student'&&studentTab==='tracking'))return false;
    const aid=typeof trackingAthleteId==='function'?trackingAthleteId():null;
    return !!aid&&trackingLoadedFor===aid;
  }

  function coachTrackingActiveV176(){
    if(!(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='tracking'))return false;
    const aid=typeof trackingAthleteId==='function'?trackingAthleteId():null;
    return !!aid&&trackingLoadedFor===aid;
  }

  function fmtMeasureV176(v,suffix){
    const n=Number(v);
    return Number.isFinite(n)?n.toLocaleString('es-AR',{maximumFractionDigits:1})+(suffix||''):'';
  }

  function measureChipsV176(m){
    const vals=[
      ['Peso',m.weight_kg,' kg'],
      ['Cintura',m.waist_cm,' cm'],
      ['Cadera',m.hip_cm,' cm'],
      ['Pecho',m.chest_cm,' cm'],
      ['Brazo',m.arm_left_cm,' cm'],
      ['Muslo',m.thigh_left_cm,' cm']
    ].filter(x=>x[1]!=null&&Number.isFinite(Number(x[1])));
    if(!vals.length)return '<span class="muted tiny">Sin valores cargados</span>';
    return vals.map(x=>'<span class="v176-measure-chip">'+esc(x[0])+' <b>'+esc(fmtMeasureV176(x[1],x[2]))+'</b></span>').join('');
  }

  function measurementHistoryHtmlV176(){
    const ms=(trackingCache?.measurements||[]).slice(0,12);
    return '<div class="card v176-measure-history" id="v176MeasurementHistory">'+
      '<div class="section-title"><div><h3>Evolución de medidas</h3>'+
      '<div class="muted tiny">Historial por fecha. Si hubo un error de carga, podés corregir ese registro.</div></div>'+
      '<span class="badge blue">'+ms.length+' registro'+(ms.length===1?'':'s')+'</span></div>'+
      (ms.length?'<div class="v176-measure-list">'+ms.map(m=>
        '<div class="v176-measure-row">'+
          '<div class="v176-measure-date"><strong>'+esc(fmtDate(m.measured_on))+'</strong><span class="muted micro">Medición</span></div>'+
          '<div class="v176-measure-values">'+measureChipsV176(m)+'</div>'+
          '<button type="button" class="btn small v176-nowrap-btn" onclick="openEditMeasurementV176(\''+esc(m.id)+'\')">Editar</button>'+
        '</div>'
      ).join('')+'</div>':'<div class="empty">Todavía no hay mediciones guardadas.</div>')+
    '</div>';
  }

  function cleanupLegacyMeasurementEvolutionV176(root){
    if(!root)return;
    root.querySelectorAll('#v93MeasureCompare,.v93-compare').forEach(x=>x.remove());
    const cards=[...root.querySelectorAll('#v176MeasurementHistory')];
    cards.slice(1).forEach(x=>x.remove());
  }

  function injectMeasurementHistoryV176(){
    let host=null,anchor=null;
    if(studentTrackingActiveV176()){
      host=el('trackingStudentHistory');
      if(!host)return;
      cleanupLegacyMeasurementEvolutionV176(host);
      el('v176MeasurementHistory')?.remove();
      host.insertAdjacentHTML('beforeend',measurementHistoryHtmlV176());
      return;
    }
    if(coachTrackingActiveV176()){
      host=el('coachStudentBody');
      if(!host)return;
      cleanupLegacyMeasurementEvolutionV176(host);
      el('v176MeasurementHistory')?.remove();
      anchor=el('coachPhotoGrid')?.closest('.card')||null;
      if(anchor)anchor.insertAdjacentHTML('beforebegin',measurementHistoryHtmlV176());
      else host.insertAdjacentHTML('beforeend',measurementHistoryHtmlV176());
    }
  }

  function decimalV176(v){
    if(v===null||v===undefined||String(v).trim()==='')return null;
    const n=Number(String(v).trim().replace(',','.'));
    return Number.isFinite(n)?n:NaN;
  }

  function measurementInputV176(id,label,value,min,max){
    return '<label class="tiny muted">'+esc(label)+
      '<input id="'+id+'" class="input" type="text" inputmode="decimal" value="'+esc(value==null?'':String(value))+'" data-min="'+min+'" data-max="'+max+'"></label>';
  }

  window.openEditMeasurementV176=function(id){
    const m=(trackingCache?.measurements||[]).find(x=>String(x.id)===String(id));
    if(!m){toast('No encuentro esa medición');return}
    showModal(
      '<div class="modal-head"><div><h3>Editar medición</h3><div class="muted tiny">Corregí solo lo que haga falta.</div></div>'+
      '<button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="form-grid">'+
        '<label class="tiny muted span2">Fecha<input id="v176MeasureDate" class="input" type="date" value="'+esc(m.measured_on||dateInputToday())+'"></label>'+
        measurementInputV176('v176MeasureWeight','Peso (kg)',m.weight_kg,20,400)+
        measurementInputV176('v176MeasureWaist','Cintura (cm)',m.waist_cm,20,300)+
        measurementInputV176('v176MeasureHip','Cadera (cm)',m.hip_cm,20,300)+
        measurementInputV176('v176MeasureChest','Pecho (cm)',m.chest_cm,20,300)+
        measurementInputV176('v176MeasureArm','Brazo (cm)',m.arm_left_cm,10,100)+
        measurementInputV176('v176MeasureThigh','Muslo (cm)',m.thigh_left_cm,15,150)+
        '<label class="tiny muted span2">Nota<textarea id="v176MeasureNotes" class="input" rows="2">'+esc(m.notes||'')+'</textarea></label>'+
      '</div>'+
      '<button id="v176MeasureSave" class="btn primary" style="width:100%;margin-top:12px" onclick="saveMeasurementV176(\''+esc(m.id)+'\')">Guardar cambios</button>'
    );
  };

  function readMeasureV176(id,label){
    const x=el(id),v=decimalV176(x?.value);
    if(v===null)return null;
    if(!Number.isFinite(v))throw new Error('Revisá '+label);
    const min=Number(x?.dataset?.min),max=Number(x?.dataset?.max);
    if(Number.isFinite(min)&&v<min)throw new Error(label+' debe ser al menos '+min);
    if(Number.isFinite(max)&&v>max)throw new Error(label+' supera el máximo permitido');
    return v;
  }

  window.saveMeasurementV176=async function(id){
    if(!supabaseClient){toast('Requiere conexión');return}
    const row=(trackingCache?.measurements||[]).find(x=>String(x.id)===String(id));
    if(!row){toast('No encuentro esa medición');return}
    const btn=el('v176MeasureSave');
    try{
      const date=el('v176MeasureDate')?.value;
      if(!date)throw new Error('Elegí una fecha');
      const payload={
        measured_on:date,
        weight_kg:readMeasureV176('v176MeasureWeight','Peso'),
        waist_cm:readMeasureV176('v176MeasureWaist','Cintura'),
        hip_cm:readMeasureV176('v176MeasureHip','Cadera'),
        chest_cm:readMeasureV176('v176MeasureChest','Pecho'),
        arm_left_cm:readMeasureV176('v176MeasureArm','Brazo'),
        thigh_left_cm:readMeasureV176('v176MeasureThigh','Muslo'),
        notes:(el('v176MeasureNotes')?.value||'').trim(),
        updated_at:new Date().toISOString()
      };
      if(btn){btn.disabled=true;btn.textContent='Guardando…'}
      const {data,error}=await supabaseClient.from('body_measurements')
        .update(payload).eq('id',id).select('*').single();
      if(error){
        if(error.code==='23505')throw new Error('Ya existe una medición cargada en esa fecha');
        throw error;
      }
      trackingLoadedFor=null;
      await loadTracking(true);
      closeModal();
      if(currentProfile?.role==='student'&&studentTab==='tracking')window.renderStudentTrackingHistory?.();
      if(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='tracking')window.renderTrackingCoachLoaded?.();
      toast('Medición actualizada');
      return data;
    }catch(e){
      toast(e?.message||cloudErr(e));
    }finally{
      if(btn){btn.disabled=false;btn.textContent='Guardar cambios'}
    }
  };

  const baseStudentTrackingHistoryV176=window.renderStudentTrackingHistory;
  if(typeof baseStudentTrackingHistoryV176==='function'){
    window.renderStudentTrackingHistory=function(){
      if(!studentTrackingActiveV176())return;
      const out=baseStudentTrackingHistoryV176.apply(this,arguments);
      injectMeasurementHistoryV176();
      return out;
    };
    try{renderStudentTrackingHistory=window.renderStudentTrackingHistory}catch(e){}
  }

  const baseCoachTrackingLoadedV176=window.renderTrackingCoachLoaded;
  if(typeof baseCoachTrackingLoadedV176==='function'){
    window.renderTrackingCoachLoaded=function(){
      if(!coachTrackingActiveV176())return;
      const out=baseCoachTrackingLoadedV176.apply(this,arguments);
      injectMeasurementHistoryV176();
      return out;
    };
    try{renderTrackingCoachLoaded=window.renderTrackingCoachLoaded}catch(e){}
  }

  /* =====================================================
     3) GROUPED "COMPLETE MEAL" IN MACRO CALCULATOR
     ===================================================== */
  let mealDraftV176=[];
  let mealComposerOpenV176=false;
  let mealLabelV176='Comida fuera del plan';

  function uuidV176(){
    if(globalThis.crypto?.randomUUID)return crypto.randomUUID();
    const a=new Uint8Array(16);
    globalThis.crypto?.getRandomValues?.(a);
    if(!a.some(Boolean)){
      for(let i=0;i<a.length;i++)a[i]=Math.floor(Math.random()*256);
    }
    a[6]=(a[6]&15)|64;a[8]=(a[8]&63)|128;
    return [...a].map((x,i)=>([4,6,8,10].includes(i)?'-':'')+x.toString(16).padStart(2,'0')).join('');
  }

  function mealDraftTotalsV176(){
    return mealDraftV176.reduce((a,x)=>({
      kcal:a.kcal+Number(x.kcal||0),
      protein_g:a.protein_g+Number(x.protein_g||0),
      carbs_g:a.carbs_g+Number(x.carbs_g||0),
      fat_g:a.fat_g+Number(x.fat_g||0)
    }),{kcal:0,protein_g:0,carbs_g:0,fat_g:0});
  }

  function renderMealComposerV176(){
    const holder=el('v176MealComposer');if(!holder)return;
    if(!mealComposerOpenV176){holder.innerHTML='';holder.style.display='none';return}
    holder.style.display='block';
    const t=mealDraftTotalsV176();
    const mealOptions=['Comida fuera del plan','Desayuno','Almuerzo','Merienda','Cena','Pre entreno','Post entreno','Colación','Otra'];
    holder.innerHTML=
      '<div class="v176-meal-composer-head"><div><h4>Comida completa</h4>'+
      '<p>Agregá varios alimentos y guardalos juntos como una sola comida.</p></div>'+
      '<button type="button" class="btn ghost small v176-nowrap-btn" onclick="toggleMealComposerV176(false)">Cerrar</button></div>'+
      '<div class="form-grid" style="margin-top:10px">'+
        '<label class="tiny muted span2">Tipo de comida<select id="v176MealLabel" class="input" onchange="setMealLabelV176(this.value)">'+
          mealOptions.map(x=>'<option '+(x===mealLabelV176?'selected':'')+'>'+esc(x)+'</option>').join('')+
        '</select></label>'+
      '</div>'+
      '<div class="v176-meal-draft-list">'+
        (mealDraftV176.length?mealDraftV176.map((x,i)=>
          '<div class="v176-meal-draft-row"><div><strong>'+esc(x.food_name)+'</strong>'+
          '<div class="muted micro">'+esc(x.amount_text||Math.round(x.grams)+' g')+' · '+Math.round(x.kcal)+' kcal · P '+Number(x.protein_g).toFixed(1)+' · C '+Number(x.carbs_g).toFixed(1)+' · G '+Number(x.fat_g).toFixed(1)+'</div></div>'+
          '<button class="btn ghost small" type="button" onclick="removeMealDraftItemV176('+i+')">✕</button></div>'
        ).join(''):'<div class="empty">Todavía no agregaste alimentos a esta comida.</div>')+
      '</div>'+
      '<div class="macro-row"><span class="macro-chip">'+Math.round(t.kcal)+' kcal</span><span class="macro-chip">P '+t.protein_g.toFixed(1)+'</span><span class="macro-chip">C '+t.carbs_g.toFixed(1)+'</span><span class="macro-chip">G '+t.fat_g.toFixed(1)+'</span></div>'+
      '<div class="nutrition-builder-actions" style="margin-top:10px">'+
        '<button class="btn" type="button" onclick="addCurrentFoodToMealV176()">+ Alimento actual</button>'+
        '<button class="btn" type="button" onclick="openCustomMealItemV176()">+ Personalizado</button>'+
        '<button id="v176SaveMeal" class="btn primary" type="button" '+(mealDraftV176.length?'':'disabled')+' onclick="saveMealGroupV176()">Guardar comida completa</button>'+
      '</div>';
  }

  window.setMealLabelV176=function(v){mealLabelV176=String(v||'Comida fuera del plan')};
  window.toggleMealComposerV176=function(open=true){
    mealComposerOpenV176=!!open;
    renderMealComposerV176();
  };
  window.removeMealDraftItemV176=function(i){
    mealDraftV176.splice(Number(i),1);
    renderMealComposerV176();
  };

  function currentMacroItemV176(){
    const s=typeof macroInputState==='function'?macroInputState():null;
    const f=s?.food||nutritionCache?.foods?.find(x=>x.id===el('macroFood')?.value);
    if(!f)return null;
    const grams=Math.max(.1,Number(s?.grams||el('macroGrams')?.value||100));
    const m=macroCalcFrom100(f,grams);
    const amount=(s?.measure_type==='units'&&s.quantity!=null)
      ?String(s.quantity)+' '+(s.unit_name||'unidad')
      :Math.round(grams*10)/10+' g';
    return {
      food_id:f.id,
      food_name:f.name,
      grams,
      measure_type:s?.measure_type||'grams',
      quantity:s?.measure_type==='units'?s.quantity:null,
      unit_name:s?.measure_type==='units'?s.unit_name:null,
      ...m,
      amount_text:amount
    };
  }

  window.addCurrentFoodToMealV176=function(){
    const item=currentMacroItemV176();
    if(!item){toast('Elegí un alimento');return}
    mealDraftV176.push(item);
    mealComposerOpenV176=true;
    renderMealComposerV176();
    toast('Alimento sumado a la comida');
  };

  window.openCustomMealItemV176=function(){
    showModal(
      '<div class="modal-head"><div><h3>Alimento personalizado</h3><div class="muted tiny">Se agregará a la comida completa que estás armando.</div></div>'+
      '<button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="form-grid">'+
        '<label class="tiny muted span2">Nombre<input id="v176CustomName" class="input" placeholder="Ej: porción de tarta"></label>'+
        '<label class="tiny muted">Cantidad (g/ml)<input id="v176CustomGrams" class="input" type="text" inputmode="decimal" value="100"></label>'+
        '<label class="tiny muted">Calorías de esa porción<input id="v176CustomKcal" class="input" type="text" inputmode="decimal"></label>'+
        '<label class="tiny muted">Proteína (g)<input id="v176CustomP" class="input" type="text" inputmode="decimal"></label>'+
        '<label class="tiny muted">Carbohidratos (g)<input id="v176CustomC" class="input" type="text" inputmode="decimal"></label>'+
        '<label class="tiny muted">Grasas (g)<input id="v176CustomF" class="input" type="text" inputmode="decimal"></label>'+
      '</div>'+
      '<button class="btn primary" style="width:100%;margin-top:12px" onclick="addCustomMealItemV176()">Agregar a la comida</button>'
    );
  };

  window.addCustomMealItemV176=function(){
    const name=(el('v176CustomName')?.value||'').trim();
    const grams=decimalV176(el('v176CustomGrams')?.value);
    const kcal=decimalV176(el('v176CustomKcal')?.value)??0;
    const protein_g=decimalV176(el('v176CustomP')?.value)??0;
    const carbs_g=decimalV176(el('v176CustomC')?.value)??0;
    const fat_g=decimalV176(el('v176CustomF')?.value)??0;
    if(!name){toast('Poné un nombre');return}
    if(!Number.isFinite(grams)||grams<=0||grams>5000){toast('Revisá la cantidad');return}
    if([kcal,protein_g,carbs_g,fat_g].some(x=>!Number.isFinite(x)||x<0)){toast('Revisá los macros');return}
    mealDraftV176.push({
      food_id:null,food_name:name,grams,kcal,protein_g,carbs_g,fat_g,
      measure_type:'grams',quantity:null,unit_name:null,amount_text:grams+' g'
    });
    mealComposerOpenV176=true;
    closeModal();
    renderMealComposerV176();
    toast('Alimento sumado a la comida');
  };

  window.saveMealGroupV176=async function(){
    if(!mealDraftV176.length){toast('Agregá al menos un alimento');return}
    if(currentProfile?.role==='student'){
      const plan=nutritionCache?.plan;
      if(!plan||plan.active===false){toast('Tu registro nutricional todavía no está habilitado');return}
      if(plan.student_logging_enabled===false){toast('Tu coach tiene desactivado el registro de comidas');return}
    }
    const athleteId=typeof ensureNutritionAthleteId==='function'?await ensureNutritionAthleteId():nutritionAthleteId();
    const studentId=currentProfile?.role==='student'?currentUser?.id:trackingStudentUserId();
    if(!athleteId){toast('No encuentro la ficha nutricional');return}
    const gid=uuidV176();
    const rows=mealDraftV176.map(x=>({
      athlete_id:athleteId,
      student_id:studentId||null,
      logged_on:nutritionCache.date||dateInputToday(),
      meal_label:mealLabelV176||'Comida fuera del plan',
      meal_group_id:gid,
      food_id:x.food_id||null,
      food_name:x.food_name,
      grams:x.grams,
      kcal:x.kcal,
      protein_g:x.protein_g,
      carbs_g:x.carbs_g,
      fat_g:x.fat_g,
      source:'calculator',
      note:'Comida completa',
      measure_type:x.measure_type||'grams',
      quantity:(x.measure_type||'grams')==='units'?x.quantity:null,
      unit_name:(x.measure_type||'grams')==='units'?x.unit_name:null
    }));
    const btn=el('v176SaveMeal');
    if(btn){btn.disabled=true;btn.textContent='Guardando…'}
    try{
      const {error}=await supabaseClient.from('nutrition_logs').insert(rows);
      if(error)throw error;
      mealDraftV176=[];
      mealComposerOpenV176=false;
      await loadNutrition(true,nutritionCache.date);
      if(currentProfile?.role==='student')window.renderNutritionStudentLoaded?.();
      else window.renderNutritionCoachLoaded?.();
      toast('Comida completa registrada');
    }catch(e){
      toast(cloudErr(e));
      if(btn){btn.disabled=false;btn.textContent='Guardar comida completa'}
    }
  };

  window.deleteMealGroupV176=async function(gid){
    if(!gid)return;
    const athleteId=nutritionAthleteId();
    let q=supabaseClient.from('nutrition_logs').delete().eq('meal_group_id',gid);
    if(athleteId)q=q.eq('athlete_id',athleteId);
    const {error}=await q;
    if(error){toast(cloudErr(error));return}
    await loadNutrition(true,nutritionCache.date);
    if(currentProfile?.role==='student')window.renderNutritionStudentLoaded?.();
    else window.renderNutritionCoachLoaded?.();
    toast('Comida eliminada');
  };

  function singleNutritionRowV176(x,studentView){
    return '<div class="nutrition-log-row"><div><strong>'+esc(x.food_name)+'</strong>'+
      '<div class="muted tiny">'+esc(x.meal_label)+' · '+nutritionLogAmountText(x)+'</div></div>'+
      '<div class="macro-row"><span class="macro-chip">'+nFmt(x.kcal,0)+' kcal</span><span class="macro-chip">P '+nFmt(x.protein_g,1)+'</span><span class="macro-chip">C '+nFmt(x.carbs_g,1)+'</span><span class="macro-chip">G '+nFmt(x.fat_g,1)+'</span></div>'+
      (studentView?'<button class="btn ghost small" onclick="deleteNutritionLog(\''+esc(x.id)+'\')">✕</button>':'')+
    '</div>';
  }

  window.renderNutritionLogs=function(studentView=true){
    const rows=nutritionCache?.logs||[];
    if(!rows.length)return '<div class="empty">No hay alimentos registrados para este día.</div>';
    const ordered=[],groups=new Map();
    rows.forEach(x=>{
      const gid=x.meal_group_id?String(x.meal_group_id):'';
      if(!gid){ordered.push({type:'single',row:x});return}
      if(!groups.has(gid)){
        const g={type:'group',id:gid,rows:[]};
        groups.set(gid,g);ordered.push(g);
      }
      groups.get(gid).rows.push(x);
    });
    return '<div class="nutrition-log">'+ordered.map(item=>{
      if(item.type==='single')return singleNutritionRowV176(item.row,studentView);
      const rs=item.rows,t=nutritionLogTotals(rs),label=rs[0]?.meal_label||'Comida completa';
      return '<div class="v176-meal-group">'+
        '<div class="v176-meal-group-head"><div><h4>'+esc(label)+'</h4><div class="muted micro">'+rs.length+' alimento'+(rs.length===1?'':'s')+' · comida agrupada</div></div>'+
        (studentView?'<button class="btn ghost small v176-nowrap-btn" onclick="deleteMealGroupV176(\''+esc(item.id)+'\')">Eliminar comida</button>':'')+'</div>'+
        '<div class="v176-meal-total"><span class="macro-chip">'+nFmt(t.kcal,0)+' kcal</span><span class="macro-chip">P '+nFmt(t.protein_g,1)+'</span><span class="macro-chip">C '+nFmt(t.carbs_g,1)+'</span><span class="macro-chip">G '+nFmt(t.fat_g,1)+'</span></div>'+
        '<div class="v176-meal-group-foods">'+rs.map(x=>
          '<div class="v176-meal-group-food"><span>'+esc(x.food_name)+'</span><span>'+nutritionLogAmountText(x)+' · '+nFmt(x.kcal,0)+' kcal</span></div>'
        ).join('')+'</div>'+
      '</div>';
    }).join('')+'</div>';
  };
  try{renderNutritionLogs=window.renderNutritionLogs}catch(e){}

  function enhanceMacroComposerV176(){
    if(!(mode==='student'&&studentTab==='nutrition'))return;
    const host=el('studentSubBody');if(!host)return;
    const title=[...host.querySelectorAll('h3')].find(x=>(x.textContent||'').trim()==='Calculadora de macros');
    const card=title?.closest('.card');if(!card)return;
    const actions=card.querySelector('.nutrition-builder-actions');
    if(actions&&!el('v176MealModeBtn')){
      const btn=document.createElement('button');
      btn.id='v176MealModeBtn';
      btn.type='button';
      btn.className='btn';
      btn.textContent='Comida completa';
      btn.onclick=()=>window.toggleMealComposerV176(true);
      actions.appendChild(btn);
    }
    if(!el('v176MealComposer')){
      const box=document.createElement('div');
      box.id='v176MealComposer';
      box.className='v176-meal-composer';
      card.appendChild(box);
    }
    renderMealComposerV176();
  }

  /* =====================================================
     4) NUTRITION NAV: PLAN + RECIPES ONLY
     ===================================================== */
  function nutritionNavV176(active){
    const a=active==='recipes'?'recipes':'plan';
    return '<div class="v70-recipe-tabs v176-nutrition-tabs" id="v176NutritionTabs">'+
      '<button class="btn '+(a==='plan'?'primary':'')+'" onclick="switchNutritionViewV70(\'plan\')">Mi plan</button>'+
      '<button class="btn '+(a==='recipes'?'primary':'')+'" onclick="switchNutritionViewV70(\'recipes\')">Recetas</button>'+
    '</div>';
  }

  try{nutritionRecipesNavV70=nutritionNavV176}catch(e){}
  try{window.nutritionRecipesNavV70=nutritionNavV176}catch(e){}

  function cleanupRetiredNutritionV176(){
    document.querySelectorAll(
      '#v66CoachHabits,#v66StudentHabits,#v136CoachLearnLink,#v138NutritionTabs,'+
      '.v136-learn-hero,.v136-learn-grid,.v138-habits-hero,.v138-general'
    ).forEach(x=>x.remove());
    document.querySelectorAll('button,.btn').forEach(b=>{
      const t=(b.textContent||'').trim();
      if(t==='Aprender'||t==='Hábitos')b.remove();
    });
    if(typeof nutritionStudentViewV70!=='undefined'&&['learn','habits'].includes(nutritionStudentViewV70)){
      nutritionStudentViewV70='plan';
    }
  }

  function ensureNutritionNavV176(){
    cleanupRetiredNutritionV176();
    if(currentProfile?.role==='student'&&studentTab==='nutrition'){
      const host=el('studentSubBody');if(!host)return;
      const active=nutritionStudentViewV70==='recipes'?'recipes':'plan';
      const navs=[...host.querySelectorAll('.v70-recipe-tabs,.v176-nutrition-tabs')];
      if(!navs.length)host.insertAdjacentHTML('afterbegin',nutritionNavV176(active));
      else{
        navs[0].outerHTML=nutritionNavV176(active);
        navs.slice(1).forEach(x=>x.remove());
      }
      enhanceMacroComposerV176();
    }
    if(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='nutrition'){
      const host=el('coachStudentBody');if(!host)return;
      host.querySelectorAll('#v176CoachNutritionNav,#v136CoachLearnLink').forEach((x,i)=>{if(i>0)x.remove()});
      if(!el('v176CoachNutritionNav')){
        host.insertAdjacentHTML('afterbegin',
          '<div id="v176CoachNutritionNav" class="v70-recipe-tabs v176-nutrition-tabs">'+
          '<button class="btn primary">Plan del alumno</button>'+
          '<button class="btn" onclick="openCoachRecipesV70()">Recetas</button></div>'
        );
      }
    }
  }

  const baseStudentNutritionLoadedV176=window.renderNutritionStudentLoaded;
  if(typeof baseStudentNutritionLoadedV176==='function'){
    window.renderNutritionStudentLoaded=function(){
      const out=baseStudentNutritionLoadedV176.apply(this,arguments);
      ensureNutritionNavV176();
      return out;
    };
    try{renderNutritionStudentLoaded=window.renderNutritionStudentLoaded}catch(e){}
  }

  const baseCoachNutritionLoadedV176=window.renderNutritionCoachLoaded;
  if(typeof baseCoachNutritionLoadedV176==='function'){
    window.renderNutritionCoachLoaded=function(){
      const out=baseCoachNutritionLoadedV176.apply(this,arguments);
      ensureNutritionNavV176();
      return out;
    };
    try{renderNutritionCoachLoaded=window.renderNutritionCoachLoaded}catch(e){}
  }

  /* =====================================================
     5) GENERAL MOBILE POLISH + ROUTE HOOK
     ===================================================== */
  function polishActionLabelsV176(){
    document.querySelectorAll('button,.btn').forEach(btn=>{
      const t=(btn.textContent||'').replace(/\s+/g,' ').trim().toLowerCase();
      if(['eliminar alumno','eliminar','actualizar'].includes(t))btn.classList.add('v176-nowrap-btn');
    });
  }

  function postRenderV176(){
    cleanupRetiredNutritionV176();
    ensureNutritionNavV176();
    polishActionLabelsV176();
    if(studentTrackingActiveV176()||coachTrackingActiveV176())injectMeasurementHistoryV176();
  }

  const baseRenderV176=window.render;
  window.render=function(){
    const next=routeKeyV176();
    const enteringRoutine=routineActiveV176()&&next!==lastRouteV176;
    const out=baseRenderV176.apply(this,arguments);
    lastRouteV176=next;
    if(enteringRoutine)scheduleRoutineTopV176();
    if(typeof fjzPostRenderV125==='function')fjzPostRenderV125('v176-polish',postRenderV176);
    else requestAnimationFrame(postRenderV176);
    return out;
  };
  try{render=window.render}catch(e){}

  // If an old habits realtime channel was created before this final runtime,
  // remove it. The V6.6 setup wrapper is also stripped at build time above.
  try{
    if(window.__fjzV66HabitChannel&&supabaseClient){
      supabaseClient.removeChannel(window.__fjzV66HabitChannel);
      window.__fjzV66HabitChannel=null;
    }
  }catch(e){}

  window.__fjzV176={
    version:VERSION,
    routineStartsAtTop:true,
    trackingAsyncGuard:true,
    measurementEdit:true,
    dateTimeMobileContainment:true,
    agendaMobileContainment:true,
    groupedMealLogging:true,
    mealGroupColumn:'meal_group_id',
    learnRemoved:true,
    habitsRemoved:true,
    nowrapActions:true,
    responsiveAudit:true
  };

  requestAnimationFrame(postRenderV176);
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

required=[
  "__fjzV176","routineStartsAtTop:true","trackingAsyncGuard:true","measurementEdit:true",
  "dateTimeMobileContainment:true","agendaMobileContainment:true","groupedMealLogging:true",
  "mealGroupColumn:'meal_group_id'","learnRemoved:true","habitsRemoved:true","responsiveAudit:true"
]
for marker in required:
    if marker not in html:
        raise RuntimeError("V17.6 missing marker: "+marker)

# Build-level cleanup assertions. Visible nutrition navigation may no longer
# contain the retired tabs.
if '<script id="v136NutritionAndStabilityRuntime">' in html:
    raise RuntimeError("V17.6 Learn runtime still present")
if '<script id="v138NutritionHabitsGuideRuntime">' in html:
    raise RuntimeError("V17.6 Habits runtime still present")
if "Aprender</button>" in html:
    raise RuntimeError("V17.6 visible Aprender button still present")
if "Hábitos</button>" in html:
    raise RuntimeError("V17.6 visible Habits button still present")

ids=re.findall(r'id="(v176[^"]+)"',html)
dupes=sorted({x for x in ids if ids.count(x)>1})
if dupes:
    raise RuntimeError("V17.6 duplicate static ids: "+", ".join(dupes))

print("TEAM FJZ V17.6 mobile/tracking/meals/cleanup enabled")
print("V17.6 cleanup:",{
    "v136_runtime_removed":n136_script,
    "v138_runtime_removed":n138_script,
    "v66_habits_removed":n66,
    "v68_habits_removed":n68_habits,
    "learn_branch_removed":n_learn_branch,
    "new_id_duplicates":len(dupes)
})
print("V17.6 audit:",{
    "bytes":len(html),
    "scripts":html.count("<script"),
    "styles":html.count("<style"),
    "observers":html.count("new MutationObserver"),
    "timeouts":html.count("setTimeout("),
    "habit_log_refs":html.count("nutrition_habit_logs")
})

p.write_text(html,encoding="utf-8")
