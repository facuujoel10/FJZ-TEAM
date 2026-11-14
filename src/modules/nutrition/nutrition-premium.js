(function(root,factory){
  const api=factory(root||{});
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.TeamFJZNutritionPremium=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(root){
  'use strict';
  const VERSION='22.4A';
  const ui={selectedMeal:'',optionByMeal:Object.create(null),dirtyPlans:new Set(),drafts:new Map(),saving:false,preview:false};
  const text=v=>String(v??'').trim();
  const num=v=>{const n=Number(v);return Number.isFinite(n)?n:0};
  const clone=v=>{try{return JSON.parse(JSON.stringify(v))}catch(_e){return v}};
  const esc=v=>text(v).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const fmt=(v,d=0)=>Number.isFinite(Number(v))?new Intl.NumberFormat('es-AR',{maximumFractionDigits:d}).format(Number(v)):'—';
  function planData(plan){const p=plan?.plan&&typeof plan.plan==='object'?plan.plan:{meals:[]};return {...p,meals:Array.isArray(p.meals)?p.meals:[]}}
  function fallbackOptionTotals(opt){return (opt?.items||[]).reduce((a,x)=>({kcal:a.kcal+num(x.kcal),protein_g:a.protein_g+num(x.protein_g),carbs_g:a.carbs_g+num(x.carbs_g),fat_g:a.fat_g+num(x.fat_g)}),{kcal:0,protein_g:0,carbs_g:0,fat_g:0})}
  function logTotals(rows=[]){return rows.reduce((a,x)=>({kcal:a.kcal+num(x.kcal),protein_g:a.protein_g+num(x.protein_g),carbs_g:a.carbs_g+num(x.carbs_g),fat_g:a.fat_g+num(x.fat_g)}),{kcal:0,protein_g:0,carbs_g:0,fat_g:0})}
  function context(){try{return root.__fjzNutritionContextV22?.()||{}}catch(_e){return{}}}
  function sameAuthority(c){const p=c?.cache?.plan;if(!p||!c?.athleteId)return true;return !p.athlete_id||text(p.athlete_id)===text(c.athleteId)}
  function amount(i,c){try{if(c.helpers?.amountText)return c.helpers.amountText(i)}catch(_e){}if(text(i?.measure_type||'grams')==='units'&&i?.quantity!=null)return fmt(i.quantity,1)+' '+esc(i.unit_name||'unidad');return fmt(i?.grams,0)+' g'}
  function totals(opt,c){try{return c.helpers?.optionTotals?c.helpers.optionTotals(opt):fallbackOptionTotals(opt)}catch(_e){return fallbackOptionTotals(opt)}}
  function macroStrip(m,kind='option'){return '<div class="fjz4a-macros '+kind+'" aria-label="Macros"><span><b>'+fmt(m.kcal,0)+'</b><small>kcal</small></span><span><b>'+fmt(m.protein_g,1)+'</b><small>prot.</small></span><span><b>'+fmt(m.carbs_g,1)+'</b><small>carbos</small></span><span><b>'+fmt(m.fat_g,1)+'</b><small>grasas</small></span></div>'}
  function targetStrip(p){const vals=[['Energía',p?.target_kcal,'kcal'],['Proteína',p?.target_protein_g,'g'],['Carbohidratos',p?.target_carbs_g,'g'],['Grasas',p?.target_fat_g,'g']];return '<div class="fjz4a-targets">'+vals.map(x=>'<div><span>'+x[0]+'</span><strong>'+(x[1]==null?'—':fmt(x[1],0)+' '+x[2])+'</strong></div>').join('')+'</div>'}
  function currentOption(meal){const opts=meal?.options||[];const wanted=ui.optionByMeal[meal.id];return opts.find(o=>text(o.id)===text(wanted))||opts[0]||null}
  function chooseMeal(pd){const meals=pd.meals||[];if(!meals.length){ui.selectedMeal='';return null}let m=meals.find(x=>text(x.id)===text(ui.selectedMeal));if(!m){m=meals[0];ui.selectedMeal=m.id}return m}
  function statusText(plan){if(ui.saving)return'Guardando…';return ui.dirtyPlans.has(text(plan?.id))?'Cambios sin guardar':'Guardado'}
  function preserveDraft(plan){if(!plan?.id)return;ui.drafts.set(text(plan.id),clone(plan));ui.dirtyPlans.add(text(plan.id))}
  function applyDraft(c){const p=c?.cache?.plan;if(!p?.id)return p;const d=ui.drafts.get(text(p.id));if(d&&text(d.athlete_id)===text(p.athlete_id))Object.assign(p,clone(d));return p}
  function syncPlanFields(c){
    const p=c?.cache?.plan;if(!p)return;
    const get=id=>root.document?.getElementById(id)?.value;
    const n=id=>{const v=get(id);return v===''||v==null?null:Number(v)};
    if(root.document?.getElementById('nutTitle'))p.title=text(get('nutTitle'))||'Plan nutricional';
    if(root.document?.getElementById('nutNotes'))p.notes=text(get('nutNotes'));
    if(root.document?.getElementById('nutKcal'))p.target_kcal=n('nutKcal');
    if(root.document?.getElementById('nutProtein'))p.target_protein_g=n('nutProtein');
    if(root.document?.getElementById('nutCarbs'))p.target_carbs_g=n('nutCarbs');
    if(root.document?.getElementById('nutFat'))p.target_fat_g=n('nutFat');
    const log=root.document?.getElementById('nutLoggingEnabled');if(log)p.student_logging_enabled=!!log.checked;
    preserveDraft(p);
  }
  function identityLoading(host){host.innerHTML='<div class="fjz4a-state"><span class="fjz4a-kicker">NUTRICIÓN</span><strong>Actualizando el plan del alumno…</strong><p>La ficha anterior no se muestra mientras cambia la identidad.</p></div>';return true}
  function itemRows(opt,c,coach=false){
    const items=opt?.items||[];if(!items.length)return '<div class="fjz4a-empty-inline">Sin alimentos cargados.</div>';
    return '<div class="fjz4a-foods">'+items.map(i=>'<div class="fjz4a-food"><div><strong>'+esc(i.name||'Alimento')+'</strong><span>'+amount(i,c)+'</span></div><small>'+fmt(i.kcal,0)+' kcal · P '+fmt(i.protein_g,1)+' · C '+fmt(i.carbs_g,1)+' · G '+fmt(i.fat_g,1)+'</small>'+(coach?'<button class="fjz4a-text-action" type="button" data-nut-action="edit-amount" data-meal="'+esc(ui.selectedMeal)+'" data-option="'+esc(opt.id)+'" data-item="'+esc(i.id)+'">Cantidad</button>':'')+'</div>').join('')+'</div>'
  }
  function optionSelector(meal){
    const opts=meal?.options||[],active=currentOption(meal);if(!opts.length)return'';
    return '<div class="fjz4a-option-tabs" role="tablist" aria-label="Opciones de '+esc(meal.name||'comida')+'">'+opts.map((o,i)=>'<button type="button" role="tab" aria-selected="'+(active&&text(active.id)===text(o.id)?'true':'false')+'" data-nut-action="option" data-meal="'+esc(meal.id)+'" data-option="'+esc(o.id)+'">'+esc(o.name||('Opción '+(i+1)))+'</button>').join('')+'</div>'
  }
  function studentMeal(meal,c){
    const opt=currentOption(meal),logging=c.cache?.plan?.student_logging_enabled!==false;
    return '<section class="fjz4a-meal"><header><div><span>COMIDA</span><h3>'+esc(meal.name||'Comida')+'</h3></div><small>'+(meal.options||[]).length+' alternativa'+((meal.options||[]).length===1?'':'s')+'</small></header>'+optionSelector(meal)+(opt?'<div class="fjz4a-option-detail"><div class="fjz4a-option-title"><div><span>OPCIÓN VISIBLE</span><h4>'+esc(opt.name||'Opción')+'</h4></div>'+macroStrip(totals(opt,c))+'</div>'+itemRows(opt,c,false)+(logging?'<button class="btn fjz4a-log-option" type="button" data-nut-action="log-option" data-meal="'+esc(meal.id)+'" data-option="'+esc(opt.id)+'">Registrar hoy</button><p class="fjz4a-help">Registra los alimentos consumidos. Cambiar de opción sólo cambia la vista y nunca modifica tu plan.</p>':'<p class="fjz4a-help">Registro diario desactivado por tu Coach. Podés consultar el plan sin guardar consumo.</p>')+'</div>':'<div class="fjz4a-empty-inline">Tu Coach todavía no cargó alternativas para esta comida.</div>')+'</section>'
  }
  function renderLogs(c,studentView=true){
    const rows=c.cache?.logs||[];if(!rows.length)return '<div class="fjz4a-log-empty"><strong>Sin registrar</strong><span>No hay consumo guardado para esta fecha.</span></div>';
    return '<div class="fjz4a-log-list">'+rows.map(x=>'<div class="fjz4a-log-row"><div><strong>'+esc(x.food_name||'Alimento')+'</strong><span>'+esc(x.meal_label||'Comida')+' · '+amount(x,c)+'</span></div><small>'+fmt(x.kcal,0)+' kcal · P '+fmt(x.protein_g,1)+' · C '+fmt(x.carbs_g,1)+' · G '+fmt(x.fat_g,1)+'</small>'+(studentView?'<button type="button" class="fjz4a-delete" aria-label="Eliminar '+esc(x.food_name||'registro')+'" data-nut-action="delete-log" data-log="'+esc(x.id)+'">×</button>':'')+'</div>').join('')+'</div>'
  }
  function calculator(c){
    const foods=c.cache?.foods||[],logging=c.cache?.plan?.student_logging_enabled!==false;
    return '<div class="fjz4a-tool" id="fjz4aCalculator"><div class="fjz4a-tool-head"><div><span>CALCULADORA</span><h3>Alimentos y cantidades</h3></div><small>Estimación por alimento</small></div>'+(foods.length?'<div class="fjz4a-calc-grid"><label>Alimento<select id="macroFood" onchange="updateMacroPreview()">'+foods.map(f=>'<option value="'+esc(f.id)+'">'+esc(f.name)+' · '+esc(f.category||'')+'</option>').join('')+'</select></label><label>Medir por<select id="macroMeasure" onchange="updateMacroPreview()"><option value="grams">Gramos</option><option value="units">Unidades</option></select></label><label id="macroGramsWrap">Cantidad (g)<input id="macroGrams" type="number" min="1" step="1" value="100" oninput="updateMacroPreview()"></label><label id="macroUnitsWrap" style="display:none">Cantidad de <span id="macroUnitLabel">unidades</span><input id="macroUnits" type="number" min=".25" step=".25" value="1" oninput="updateMacroPreview()"></label><label>Comida<select id="macroMeal"><option>Desayuno</option><option>Almuerzo</option><option>Merienda</option><option>Cena</option><option>Pre entreno</option><option>Post entreno</option><option>Colación</option><option>Otra</option></select></label></div><div id="macroPreview" class="macro-preview fjz4a-preview"></div><div class="fjz4a-tool-actions">'+(logging?'<button class="btn primary" type="button" data-nut-action="calculator-log">Agregar al registro</button><button class="btn" type="button" data-nut-action="custom-log">+ Personalizado</button>':'<span class="fjz4a-help">El registro está desactivado; la calculadora sigue disponible como referencia.</span>')+'</div>':'<div class="fjz4a-empty-inline">La biblioteca de alimentos todavía no está disponible.</div>')+'</div>'
  }
  function renderStudent(){
    const host=root.document?.getElementById('studentSubBody');if(!host)return false;const c=context();if(!sameAuthority(c))return identityLoading(host);const p=applyDraft(c);
    if(!p||p.active===false){host.innerHTML='<main class="fjz4a-student"><header class="fjz4a-student-head"><div><span class="fjz4a-kicker">MI ALIMENTACIÓN</span><h2>Tu plan</h2><p>Nutrición TEAM FJZ</p></div><button type="button" data-nut-action="recipes">Ver recetas</button></header><div class="fjz4a-state"><strong>Sin plan nutricional activo</strong><p>Cuando tu Coach publique un plan, aparecerá acá. No interpretamos la ausencia como incumplimiento.</p></div></main>';bind(host,'student');return true}
    const pd=planData(p),logs=c.cache?.logs||[];
    host.innerHTML='<main class="fjz4a-student"><header class="fjz4a-student-head"><div><span class="fjz4a-kicker">MI ALIMENTACIÓN</span><h2>'+esc(p.title||'Plan nutricional')+'</h2><p>'+(p.revision?'Revisión '+esc(p.revision):'Plan asignado por tu Coach')+'</p></div><div class="fjz4a-head-actions"><button type="button" data-nut-action="scroll" data-target="fjz4aPlan">Plan</button><button type="button" data-nut-action="scroll" data-target="fjz4aLog">Registro</button><button type="button" data-nut-action="recipes">Recetas</button></div></header><section id="fjz4aPlan" class="fjz4a-plan-intro"><div><span class="fjz4a-kicker">OBJETIVOS DEL PLAN</span><p>Referencias prescritas. No representan lo que consumiste hoy.</p></div>'+targetStrip(p)+(p.notes?'<div class="fjz4a-coach-note"><span>INDICACIONES</span><p>'+esc(p.notes)+'</p></div>':'')+'</section><section class="fjz4a-meals"><div class="fjz4a-section-head"><div><span class="fjz4a-kicker">TU DÍA</span><h2>Comidas y alternativas</h2></div><p>Consultá una opción por vez. Ver una alternativa no la registra.</p></div>'+(pd.meals.length?pd.meals.map(m=>studentMeal(m,c)).join(''):'<div class="fjz4a-state compact"><strong>Sin comidas cargadas</strong><p>Tu Coach todavía no agregó opciones al plan.</p></div>')+'</section><section id="fjz4aLog" class="fjz4a-log-section"><div class="fjz4a-section-head"><div><span class="fjz4a-kicker">REGISTRO REAL</span><h2>Lo que sí quedó guardado</h2></div><label class="fjz4a-date">Fecha<input id="nutritionLogDate" type="date" value="'+esc(c.cache?.date||'')+'" data-nut-change="date"></label></div>'+(logs.length?'<div class="fjz4a-consumed"><span>Consumo registrado</span>'+macroStrip(logTotals(logs),'consumed')+'</div>':'')+renderLogs(c,true)+'</section><section class="fjz4a-tools"><div class="fjz4a-section-head"><div><span class="fjz4a-kicker">HERRAMIENTAS</span><h2>Recetas y calculadora</h2></div><button class="btn" type="button" data-nut-action="recipes">Explorar recetas</button></div>'+calculator(c)+'</section></main>';
    bind(host,'student');try{root.updateMacroPreview?.()}catch(_e){}return true
  }
  function coachMealEditor(meal,c){
    if(!meal)return '<div class="fjz4a-state compact"><strong>Sin comidas</strong><p>Agregá una comida para empezar.</p></div>';
    const opts=meal.options||[];
    return '<div class="fjz4a-editor-main"><header class="fjz4a-editor-meal-head"><div><span class="fjz4a-kicker">COMIDA SELECCIONADA</span><h2>'+esc(meal.name||'Comida')+'</h2><p>'+opts.length+' alternativa'+(opts.length===1?'':'s')+'</p></div><div class="fjz4a-editor-actions"><button class="btn" type="button" data-nut-action="meal-macros" data-meal="'+esc(meal.id)+'">Macros comida</button><button class="btn" type="button" data-nut-action="rename-meal" data-meal="'+esc(meal.id)+'">Renombrar</button><button class="btn primary" type="button" data-nut-action="add-option" data-meal="'+esc(meal.id)+'">+ Alternativa</button></div></header><div class="fjz4a-coach-options">'+(opts.length?opts.map((o,i)=>'<article class="fjz4a-coach-option"><div class="fjz4a-coach-option-head"><div><span>OPCIÓN '+(i+1)+'</span><h3>'+esc(o.name||('Opción '+(i+1)))+'</h3></div>'+macroStrip(totals(o,c))+'</div>'+itemRows(o,c,true)+'<div class="fjz4a-option-actions"><button class="btn" type="button" data-nut-action="add-food" data-meal="'+esc(meal.id)+'" data-option="'+esc(o.id)+'">+ Alimento</button><button class="btn ghost" type="button" data-nut-action="delete-option" data-meal="'+esc(meal.id)+'" data-option="'+esc(o.id)+'">Eliminar opción</button></div></article>').join(''):'<div class="fjz4a-state compact"><strong>Sin alternativas</strong><p>Agregá una opción y después sus alimentos.</p></div>')+'</div><button class="fjz4a-danger-link" type="button" data-nut-action="delete-meal" data-meal="'+esc(meal.id)+'">Eliminar esta comida</button></div>'
  }
  function previewPlan(p,c){const pd=planData(p);return '<div class="fjz4a-preview-panel"><div class="fjz4a-preview-head"><div><span class="fjz4a-kicker">PREVISUALIZACIÓN ALUMNO</span><h2>'+esc(p.title||'Plan nutricional')+'</h2></div><button type="button" class="btn" data-nut-action="toggle-preview">Cerrar</button></div>'+targetStrip(p)+(pd.meals.length?pd.meals.map(m=>{const o=currentOption(m);return '<div class="fjz4a-preview-meal"><strong>'+esc(m.name||'Comida')+'</strong>'+optionSelector(m)+(o?'<div class="fjz4a-option-detail"><h4>'+esc(o.name||'Opción')+'</h4>'+macroStrip(totals(o,c))+itemRows(o,c,false)+'</div>':'')+'</div>'}).join(''):'<div class="fjz4a-empty-inline">Sin comidas.</div>')+'</div>'}
  function renderCoach(){
    const host=root.document?.getElementById('coachStudentBody');if(!host)return false;const c=context();if(c.profile?.role!=='coach')return false;if(!sameAuthority(c))return identityLoading(host);const p=applyDraft(c);
    if(!p){host.innerHTML='<main class="fjz4a-coach"><header class="fjz4a-coach-head"><div><span class="fjz4a-kicker">NUTRICIÓN · ATHLETE 360</span><h2>Plan nutricional</h2><p>'+esc(c.student?.name||'Alumno')+'</p></div></header><div class="fjz4a-state"><strong>Este alumno todavía no tiene un plan</strong><p>Crealo sobre la autoridad nutricional existente. No se genera ningún dato automático.</p><button class="btn primary" type="button" data-nut-action="create-plan">Crear plan nutricional</button></div></main>';bind(host,'coach');return true}
    const pd=planData(p),meal=chooseMeal(pd),logs=c.cache?.logs||[];
    host.innerHTML='<main class="fjz4a-coach"><header class="fjz4a-coach-head"><div><span class="fjz4a-kicker">NUTRICIÓN · ATHLETE 360</span><h2>'+esc(p.title||'Plan nutricional')+'</h2><p>'+esc(c.student?.name||'Alumno')+' · Revisión '+esc(p.revision||1)+'</p></div><div class="fjz4a-save-zone"><span id="fjz4aSaveState" class="'+(ui.dirtyPlans.has(text(p.id))?'dirty':'')+'">'+statusText(p)+'</span><button class="btn" type="button" data-nut-action="toggle-preview">Vista alumno</button><button id="fjz4aSave" class="btn primary" type="button" data-nut-action="save">Guardar plan</button></div></header><section class="fjz4a-plan-settings"><div class="fjz4a-settings-copy"><span class="fjz4a-kicker">CONFIGURACIÓN</span><h3>Plan y objetivos</h3><p>Objetivos prescritos separados del consumo registrado.</p></div><div class="fjz4a-settings-grid"><label>Nombre del plan<input id="nutTitle" value="'+esc(p.title||'Plan nutricional')+'"></label><label>Calorías<input id="nutKcal" type="number" min="0" value="'+(p.target_kcal??'')+'" placeholder="Opcional"></label><label>Proteína (g)<input id="nutProtein" type="number" min="0" value="'+(p.target_protein_g??'')+'" placeholder="Opcional"></label><label>Carbos (g)<input id="nutCarbs" type="number" min="0" value="'+(p.target_carbs_g??'')+'" placeholder="Opcional"></label><label>Grasas (g)<input id="nutFat" type="number" min="0" value="'+(p.target_fat_g??'')+'" placeholder="Opcional"></label><label class="wide">Indicaciones<textarea id="nutNotes" rows="3">'+esc(p.notes||'')+'</textarea></label><label class="fjz4a-toggle wide"><input id="nutLoggingEnabled" type="checkbox" '+(p.student_logging_enabled!==false?'checked':'')+'><span><strong>Registro de comidas</strong><small>Guarda consumo real en nutrition_logs. No cambia el plan prescrito.</small></span></label></div></section><div class="fjz4a-editor-layout"><aside class="fjz4a-meal-sidebar"><div><span class="fjz4a-kicker">ESTRUCTURA</span><h3>Comidas</h3></div><nav aria-label="Comidas del plan">'+pd.meals.map((m,i)=>'<button type="button" class="'+(meal&&text(meal.id)===text(m.id)?'active':'')+'" data-nut-action="meal" data-meal="'+esc(m.id)+'"><span>'+esc(m.name||('Comida '+(i+1)))+'</span><small>'+(m.options||[]).length+' opciones</small></button>').join('')+'</nav><button class="btn" type="button" data-nut-action="add-meal">+ Agregar comida</button><div class="fjz4a-side-tools"><button type="button" data-nut-action="coach-recipes">Biblioteca de recetas</button><button type="button" data-nut-action="macro-calculator">Calculadora avanzada</button></div></aside>'+coachMealEditor(meal,c)+'</div>'+(ui.preview?previewPlan(p,c):'')+'<section class="fjz4a-coach-log"><div class="fjz4a-section-head"><div><span class="fjz4a-kicker">CONSUMO REGISTRADO</span><h2>Registro del alumno</h2><p>Datos guardados, separados del plan prescrito.</p></div><button class="btn" type="button" data-nut-action="reload-log">Actualizar</button></div>'+(logs.length?'<div class="fjz4a-consumed">'+macroStrip(logTotals(logs),'consumed')+'</div>':'')+renderLogs(c,false)+'</section></main>';
    bind(host,'coach');return true
  }
  function updateSaveState(p){const s=root.document?.getElementById('fjz4aSaveState');if(s){s.textContent=statusText(p);s.classList.toggle('dirty',ui.dirtyPlans.has(text(p?.id)))}const b=root.document?.getElementById('fjz4aSave');if(b){b.disabled=ui.saving;b.textContent=ui.saving?'Guardando…':'Guardar plan'}}
  async function callAction(c,name,...args){const fn=c.actions?.[name];return typeof fn==='function'?await fn(...args):null}
  async function handle(mode,e){
    const b=e.target.closest?.('[data-nut-action]');if(!b)return;const a=b.dataset.nutAction,c=context(),p=c.cache?.plan;
    if(a==='option'){ui.optionByMeal[b.dataset.meal]=b.dataset.option;mode==='coach'?renderCoach():renderStudent();return}
    if(a==='meal'){syncPlanFields(c);ui.selectedMeal=b.dataset.meal;renderCoach();return}
    if(a==='scroll'){root.document?.getElementById(b.dataset.target)?.scrollIntoView?.({behavior:'smooth',block:'start'});return}
    if(a==='recipes'){root.switchNutritionViewV70?.('recipes');return}
    if(a==='coach-recipes'){root.openCoachRecipesV70?.();return}
    if(a==='macro-calculator'){root.openMacroTargetCalculatorV272?.();return}
    if(a==='custom-log'){await callAction(c,'customLog');return}
    if(a==='calculator-log'){b.disabled=true;try{await callAction(c,'calculatorLog')}finally{b.disabled=false}return}
    if(a==='log-option'){b.disabled=true;try{await callAction(c,'logOption',b.dataset.meal,b.dataset.option)}finally{b.disabled=false}return}
    if(a==='delete-log'){await callAction(c,'deleteLog',b.dataset.log);return}
    if(a==='create-plan'){await callAction(c,'createPlan');return}
    if(a==='reload-log'){await callAction(c,'reloadLog');return}
    if(a==='toggle-preview'){syncPlanFields(c);ui.preview=!ui.preview;renderCoach();return}
    if(a==='save'){
      syncPlanFields(c);const before=Number(p?.revision||0);ui.saving=true;updateSaveState(p);
      try{const row=await callAction(c,'savePlan');const now=context().cache?.plan;if(row&&now&&Number(now.revision)>before){ui.dirtyPlans.delete(text(now.id));ui.drafts.delete(text(now.id));ui.saving=false;renderCoach()}else{ui.saving=false;updateSaveState(now||p)}}catch(_e){ui.saving=false;updateSaveState(p)}return
    }
    if(['add-meal','rename-meal','add-option','delete-meal','delete-option','add-food','edit-amount','meal-macros'].includes(a))syncPlanFields(c);
    if(a==='add-meal')await callAction(c,'addMeal');
    if(a==='rename-meal')await callAction(c,'renameMeal',b.dataset.meal);
    if(a==='add-option')await callAction(c,'addOption',b.dataset.meal);
    if(a==='delete-meal')await callAction(c,'deleteMeal',b.dataset.meal);
    if(a==='delete-option')await callAction(c,'deleteOption',b.dataset.meal,b.dataset.option);
    if(a==='add-food')await callAction(c,'addFood',b.dataset.meal,b.dataset.option);
    if(a==='edit-amount')await callAction(c,'editAmount',b.dataset.meal,b.dataset.option,b.dataset.item);
    if(a==='meal-macros')await callAction(c,'mealMacros',b.dataset.meal)
  }
  function bind(host,mode){
    host.onclick=e=>handle(mode,e);
    host.oninput=e=>{if(mode==='coach'&&e.target.closest('.fjz4a-plan-settings')){const c=context();syncPlanFields(c);updateSaveState(c.cache?.plan)}};
    host.onchange=e=>{if(mode==='student'&&e.target?.dataset?.nutChange==='date')callAction(context(),'changeDate',e.target.value)}
  }
  function install(){if(root.__fjzNutritionPremiumInstalledV22)return true;root.__fjzNutritionPremiumInstalledV22=true;root.__fjzRenderNutritionStudentV22=renderStudent;root.__fjzRenderNutritionCoachV22=renderCoach;return true}
  return Object.freeze({VERSION,planData,fallbackOptionTotals,logTotals,sameAuthority,currentOption,renderStudent,renderCoach,install,state:ui});
});