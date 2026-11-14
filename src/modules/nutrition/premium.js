(function(root,factory){
  const api=factory(root||{});
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.TeamFJZNutritionPremium=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(root){
  'use strict';
  const VERSION='22.4A';
  const MARKER='FJZ4A_OPTION:';
  const ui={identityKey:'',studentOptions:{},coachMealId:'',savedSignature:'',saving:false,registering:new Set(),lastSaveState:'idle'};
  const text=v=>String(v??'').trim();
  const esc=v=>text(v).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const num=v=>{const n=Number(v);return Number.isFinite(n)?n:0};
  const fmt=(v,d=0)=>Number.isFinite(Number(v))?Number(v).toLocaleString('es-AR',{minimumFractionDigits:0,maximumFractionDigits:d}):'—';
  const clone=v=>{try{return JSON.parse(JSON.stringify(v))}catch(_e){return v}};
  function context(){try{return root.__fjzNutritionContextV22?.()||{}}catch(_e){return{}}}
  function actions(){try{return root.__fjzNutritionActionsV22||{}}catch(_e){return{}}}
  function identity(c=context()){
    return [text(c?.profile?.role),text(c?.athleteId),text(c?.student?.id),text(c?.studentTab),text(c?.coachTab),text(c?.coachStudentTab)].join('|');
  }
  function resetIdentity(c=context()){
    const key=identity(c);if(key===ui.identityKey)return;
    ui.identityKey=key;ui.studentOptions={};ui.coachMealId='';ui.savedSignature='';ui.saving=false;ui.registering.clear();ui.lastSaveState='idle';
  }
  function planData(c=context()){
    const p=c?.cache?.plan;if(!p)return null;
    const pd=p.plan&&typeof p.plan==='object'?p.plan:{meals:[]};
    return {...pd,meals:Array.isArray(pd.meals)?pd.meals:[]};
  }
  function signature(c=context()){
    const p=c?.cache?.plan;if(!p)return'';
    try{return JSON.stringify({id:p.id,revision:p.revision,title:p.title,notes:p.notes,target_kcal:p.target_kcal,target_protein_g:p.target_protein_g,target_carbs_g:p.target_carbs_g,target_fat_g:p.target_fat_g,student_logging_enabled:p.student_logging_enabled,active:p.active,plan:p.plan})}catch(_e){return text(p.id)+'|'+text(p.revision)}
  }
  function optionTotals(opt){
    const fn=actions().optionTotals;
    if(typeof fn==='function'){try{return fn(opt)||{kcal:0,protein_g:0,carbs_g:0,fat_g:0}}catch(_e){}}
    return (opt?.items||[]).reduce((a,x)=>({kcal:a.kcal+num(x?.kcal),protein_g:a.protein_g+num(x?.protein_g),carbs_g:a.carbs_g+num(x?.carbs_g),fat_g:a.fat_g+num(x?.fat_g)}),{kcal:0,protein_g:0,carbs_g:0,fat_g:0});
  }
  function logTotals(rows=[]){return (rows||[]).reduce((a,x)=>({kcal:a.kcal+num(x?.kcal),protein_g:a.protein_g+num(x?.protein_g),carbs_g:a.carbs_g+num(x?.carbs_g),fat_g:a.fat_g+num(x?.fat_g)}),{kcal:0,protein_g:0,carbs_g:0,fat_g:0})}
  function optionMarker(mealId,optId){return MARKER+JSON.stringify({mealId:text(mealId),optionId:text(optId)})}
  function parseOptionMarker(note){
    const s=text(note);if(!s.startsWith(MARKER))return null;
    try{const x=JSON.parse(s.slice(MARKER.length));const mealId=text(x?.mealId),optionId=text(x?.optionId);return mealId&&optionId?{mealId,optionId}:null}catch(_e){return null}
  }
  function findMeal(pd,id){return (pd?.meals||[]).find(x=>text(x?.id)===text(id))||null}
  function findOption(pd,mealId,optId){return findMeal(pd,mealId)?.options?.find(x=>text(x?.id)===text(optId))||null}
  function amountText(item){
    const fn=actions().amountText;if(typeof fn==='function'){try{return fn(item)}catch(_e){}}
    if(text(item?.measure_type)==='units'){const q=num(item?.quantity||1),u=text(item?.unit_name||'unidad');return fmt(q,Number.isInteger(q)?0:1)+' '+u}
    return fmt(item?.grams,0)+' g';
  }
  function consumptionGroups(rows=[],pd=null){
    const map=new Map();
    for(const row of rows||[]){
      const marker=parseOptionMarker(row?.note),groupId=text(row?.meal_group_id),key=groupId?'group:'+groupId:'row:'+text(row?.id);
      if(!map.has(key))map.set(key,{key,groupId:groupId||null,rows:[],marker:null,mealLabel:text(row?.meal_label||'Comida'),createdAt:row?.created_at||null});
      const g=map.get(key);g.rows.push(row);if(marker)g.marker=marker;if((row?.created_at||'')>(g.createdAt||''))g.createdAt=row.created_at;
    }
    return [...map.values()].map(g=>{
      const meal=g.marker?findMeal(pd,g.marker.mealId):null,opt=g.marker?findOption(pd,g.marker.mealId,g.marker.optionId):null;
      return {...g,mealName:text(meal?.name||g.mealLabel||'Comida'),optionName:text(opt?.name||''),totals:logTotals(g.rows),identified:!!(g.marker&&meal&&opt)};
    }).sort((a,b)=>text(a.createdAt).localeCompare(text(b.createdAt)));
  }
  function macrosHtml(t,cls='fjz4a-macros'){
    return '<div class="'+cls+'" aria-label="Macros">'+
      '<div><span>Calorías</span><strong>'+fmt(t?.kcal,0)+'</strong><small>kcal</small></div>'+
      '<div><span>Proteínas</span><strong>'+fmt(t?.protein_g,1)+'</strong><small>g</small></div>'+
      '<div><span>Carbohidratos</span><strong>'+fmt(t?.carbs_g,1)+'</strong><small>g</small></div>'+
      '<div><span>Grasas</span><strong>'+fmt(t?.fat_g,1)+'</strong><small>g</small></div></div>';
  }
  function targetsHtml(p){
    const rows=[['Calorías',p?.target_kcal,'kcal'],['Proteínas',p?.target_protein_g,'g'],['Carbohidratos',p?.target_carbs_g,'g'],['Grasas',p?.target_fat_g,'g']];
    if(!rows.some(x=>x[1]!=null&&x[1]!==''))return '<div class="fjz4a-target-empty">Sin objetivos diarios configurados.</div>';
    return '<div class="fjz4a-targets" aria-label="Objetivos diarios del plan">'+rows.map(([l,v,u])=>'<div><span>'+l+'</span><strong>'+(v==null||v===''?'—':fmt(v,l==='Calorías'?0:1))+'</strong><small>'+(v==null||v===''?'':u)+'</small></div>').join('')+'</div>';
  }
  function itemHtml(i,coach=false,mealId='',optId=''){
    return '<li class="fjz4a-food"><div><strong>'+esc(i?.name||'Alimento')+'</strong><span>'+esc(amountText(i))+(text(i?.measure_type)==='units'&&num(i?.grams)>0?' · ≈ '+fmt(i.grams,0)+' g para macros':'')+'</span></div>'+
      '<div class="fjz4a-food-macro">'+fmt(i?.kcal,0)+' kcal · P '+fmt(i?.protein_g,1)+' · C '+fmt(i?.carbs_g,1)+' · G '+fmt(i?.fat_g,1)+'</div>'+
      (coach&&text(i?.id)?'<div class="fjz4a-food-actions"><button type="button" data-4a-action="amount" data-meal="'+esc(mealId)+'" data-option="'+esc(optId)+'" data-item="'+esc(i.id)+'">Cantidad</button><button type="button" class="danger" data-4a-action="remove-food" data-meal="'+esc(mealId)+'" data-option="'+esc(optId)+'" data-item="'+esc(i.id)+'" aria-label="Quitar '+esc(i?.name||'alimento')+'">Quitar</button></div>':'')+
      ((i?.alternatives||[]).length?'<div class="fjz4a-alternatives"><span>Alternativas autorizadas</span>'+i.alternatives.map(x=>'<em>'+esc(x)+'</em>').join('')+'</div>':'')+'</li>';
  }
  function optionStudentHtml(meal,opt,index,active,logging,preview=false){
    const t=optionTotals(opt),mid=text(meal?.id),oid=text(opt?.id);
    return '<article class="meal-option-student fjz4a-option '+(active?'active':'')+'" data-4a-option="'+esc(oid||String(index))+'" '+(active?'':'hidden')+'>'+
      '<div class="fjz4a-option-head"><div><span>OPCIÓN '+(index+1)+'</span><h3>'+esc(opt?.name||('Opción '+(index+1)))+'</h3></div>'+(!preview&&logging&&mid&&oid?'<button type="button" class="fjz4a-register" data-4a-action="register-option" data-meal="'+esc(mid)+'" data-option="'+esc(oid)+'">Registrar hoy</button>':'')+'</div>'+macrosHtml(t)+
      '<ul class="fjz4a-foods">'+((opt?.items||[]).length?(opt.items||[]).map(i=>itemHtml(i,false)).join(''):'<li class="fjz4a-empty-line">Sin alimentos cargados en esta opción.</li>')+'</ul>'+(!preview?'<p class="fjz4a-option-note">Ver o cambiar de opción no registra consumo. Sólo se guarda al usar “Registrar hoy”.</p>':'')+'</article>';
  }
  function mealStudentHtml(meal,mealIndex,logging,preview=false){
    const opts=Array.isArray(meal?.options)?meal.options:[],mid=text(meal?.id)||'legacy-'+mealIndex;
    const remembered=ui.studentOptions[mid],activeIndex=Math.max(0,opts.findIndex(o=>text(o?.id)===remembered));
    const ai=activeIndex>=0?activeIndex:0;
    return '<section class="fjz4a-meal" data-4a-meal="'+esc(mid)+'"><header><div><span class="fjz4a-meal-index">'+String(mealIndex+1).padStart(2,'0')+'</span><div><h2>'+esc(meal?.name||'Comida')+'</h2><p>'+opts.length+' alternativa'+(opts.length===1?'':'s')+' prescrita'+(opts.length===1?'':'s')+'</p></div></div></header>'+
      (opts.length>1?'<div class="fjz4a-option-tabs" role="tablist" aria-label="Opciones de '+esc(meal?.name||'comida')+'">'+opts.map((o,i)=>'<button type="button" role="tab" aria-selected="'+(i===ai?'true':'false')+'" class="'+(i===ai?'active':'')+'" data-4a-action="select-option" data-meal="'+esc(mid)+'" data-option="'+esc(text(o?.id)||String(i))+'">'+esc(o?.name||('Opción '+(i+1)))+'</button>').join('')+'</div>':'')+
      (opts.length?opts.map((o,i)=>optionStudentHtml(meal,o,i,i===ai,logging,preview)).join(''):'<div class="fjz4a-empty-block"><strong>Sin alternativas cargadas</strong><span>Tu coach todavía no agregó opciones a esta comida.</span></div>')+'</section>';
  }
  function resourcesHtml(pd,student=true){
    const supp=Array.isArray(pd?.supplements)?pd.supplements:[],habits=Array.isArray(pd?.habits)?pd.habits.filter(x=>x?.enabled!==false):[];
    return '<section class="fjz4a-resources"><div class="fjz4a-section-heading"><span>RECURSOS</span><h2>Herramientas de tu plan</h2></div><div class="fjz4a-resource-actions">'+
      '<button type="button" data-4a-action="recipes"><strong>Recetas</strong><span>Biblioteca TEAM FJZ</span></button><button type="button" data-4a-action="calculator-focus"><strong>Calculadora</strong><span>Estimá una porción</span></button>'+
      (!student?'<button type="button" data-4a-action="coach-recipes"><strong>Gestionar recetas</strong><span>Biblioteca del Coach</span></button><button type="button" data-4a-action="coach-calculator"><strong>Calculadora Coach</strong><span>Objetivos del plan</span></button>':'')+'</div>'+ 
      (supp.length||!student?'<div class="fjz4a-resource-list"><div class="fjz4a-resource-title"><h3>Suplementación indicada</h3>'+(!student?'<button type="button" data-4a-action="add-supplement">+ Suplemento</button>':'')+'</div>'+(supp.length?supp.map((s,i)=>'<div><strong>'+esc(s.name||'Suplemento')+'</strong><span>'+esc([s.amount&&s.unit?(s.amount+' '+s.unit):'',s.timing||'',s.notes||''].filter(Boolean).join(' · '))+'</span>'+(!student?'<div class="fjz4a-mini-actions"><button type="button" data-4a-action="edit-supplement" data-index="'+i+'">Editar</button><button type="button" data-4a-action="remove-supplement" data-index="'+i+'">Quitar</button></div>':'')+'</div>').join(''):'<p class="fjz4a-resource-empty">Sin suplementos cargados.</p>')+'</div>':'')+
      (habits.length||!student?'<div class="fjz4a-resource-list"><div class="fjz4a-resource-title"><h3>Hábitos y recordatorios</h3>'+(!student?'<button type="button" data-4a-action="add-habit">+ Hábito</button>':'')+'</div>'+(habits.length?habits.map(h=>'<div><strong>'+esc(h.title||h.name||'Hábito')+'</strong><span>'+esc(h.text||h.description||'')+'</span>'+(!student&&h.id?'<label class="fjz4a-mini-toggle"><input type="checkbox" data-4a-action="toggle-habit" data-habit="'+esc(h.id)+'" '+(h.enabled!==false?'checked':'')+'><span>Activo</span></label>':'')+(!student&&h.custom&&h.id?'<div class="fjz4a-mini-actions"><button type="button" data-4a-action="delete-habit" data-habit="'+esc(h.id)+'">Eliminar</button></div>':'')+'</div>').join(''):'<p class="fjz4a-resource-empty">Sin hábitos configurados.</p>')+'</div>':'')+'</section>';
  }
  function consumptionHtml(c,student=true){
    const rows=c?.cache?.logs||[],pd=planData(c),groups=consumptionGroups(rows,pd),tot=logTotals(rows),date=text(c?.cache?.date||'');
    return '<section class="fjz4a-consumption"><div class="fjz4a-section-heading"><span>CONSUMO REGISTRADO</span><h2>'+esc(date||'Hoy')+'</h2><p>Esto refleja únicamente registros guardados, no el plan prescrito.</p></div>'+ 
      (rows.length?macrosHtml(tot,'fjz4a-macros fjz4a-consumed-macros'):'<div class="fjz4a-unregistered"><strong>Sin registrar</strong><span>No se interpreta como incumplimiento.</span></div>')+
      '<div class="nutrition-log fjz4a-log">'+groups.map(g=>'<article class="nutrition-log-row"><div class="fjz4a-log-main"><span>'+esc(g.mealName)+'</span><strong>'+esc(g.optionName||(g.rows.length>1?'Registro agrupado':g.rows[0]?.food_name||'Registro'))+'</strong><small>'+(g.identified?'Opción identificada':(g.rows.some(x=>text(x?.source)==='plan')?'Registro histórico · opción no identificada':'Registro individual'))+'</small></div><div class="fjz4a-log-macros"><span class="fjz4a-log-foods">'+g.rows.map(x=>esc(x.food_name||'Alimento')).join(' · ')+'</span>'+fmt(g.totals.kcal,0)+' kcal · P '+fmt(g.totals.protein_g,1)+' · C '+fmt(g.totals.carbs_g,1)+' · G '+fmt(g.totals.fat_g,1)+'</div>'+(student?'<button type="button" class="fjz4a-log-delete" data-4a-action="delete-log" data-group="'+esc(g.groupId||'')+'" data-row="'+esc(text(g.rows[0]?.id))+'" aria-label="Eliminar registro">Eliminar</button>':'')+'</article>').join('')+'</div></section>';
  }
  function calculatorHtml(c){
    const foods=c?.cache?.foods||[],logging=c?.cache?.plan?.student_logging_enabled!==false&&c?.cache?.plan?.active!==false;
    return '<section class="fjz4a-calculator" id="fjz4aCalculator" tabindex="-1"><div class="fjz4a-section-heading"><span>CALCULADORA</span><h2>Calculá una porción</h2><p>Estimación desde la biblioteca existente. No modifica tu plan.</p></div><div class="fjz4a-calc-form"><label>Alimento<select id="macroFood">'+foods.map(f=>'<option value="'+esc(f.id)+'">'+esc(f.name)+' · '+esc(f.category||'')+'</option>').join('')+'</select></label><label>Medir por<select id="macroMeasure"><option value="grams">Gramos</option><option value="units">Unidades</option></select></label><label id="macroGramsWrap">Gramos<input id="macroGrams" type="number" min="1" step="1" value="100"></label><label id="macroUnitsWrap" style="display:none">Cantidad de <span id="macroUnitLabel">unidades</span><input id="macroUnits" type="number" min="0.25" step="0.25" value="1"></label><label>Comida<select id="macroMeal"><option>Desayuno</option><option>Media mañana</option><option>Almuerzo</option><option>Merienda</option><option>Pre entreno</option><option>Post entreno</option><option>Cena</option><option>Colación</option><option>Otra</option></select></label></div><div id="macroPreview" class="macro-preview fjz4a-preview"></div><div class="fjz4a-inline-actions">'+(logging?'<button type="button" class="primary" data-4a-action="calculator-add">Agregar al registro</button><button type="button" data-4a-action="custom-log">+ Personalizado</button>':'<span class="fjz4a-disabled-note">El registro diario está desactivado. La calculadora sigue disponible como referencia.</span>')+'</div></section>';
  }
  function loadErrorHtml(role,message){return '<div class="fjz4a-'+(role==='coach'?'coach':'student')+'-shell"><section class="fjz4a-error-state"><span>NUTRICIÓN</span><strong>No pudimos cargar la información</strong><p>'+esc(message||'Error de lectura')+'</p><button type="button" data-4a-action="retry-load" data-role="'+role+'">Reintentar</button></section></div>'}
  async function startStudent(force=false){
    const c=context();resetIdentity(c);if(c?.profile?.role!=='student')return false;
    if(text(c?.nutritionStudentView)==='recipes'&&typeof actions().renderRecipesStudent==='function')return actions().renderRecipesStudent();
    const host=root.document?.getElementById('studentSubBody');if(!host)return false;
    host.innerHTML='<div class="fjz4a-student-shell"><div class="fjz4a-loading">Cargando tu alimentación…</div></div>';
    try{await actions().load?.(force,c?.cache?.date);return renderStudent()}catch(err){host.innerHTML=loadErrorHtml('student',actions().cloudError?.(err)||err?.message);bindHost(host);return false}
  }
  async function startCoach(force=false){
    const c=context();resetIdentity(c);if(c?.profile?.role!=='coach')return false;
    const host=root.document?.getElementById('coachStudentBody');if(!host)return false;
    host.innerHTML='<div class="fjz4a-coach-shell"><div class="fjz4a-loading">Cargando nutrición del alumno…</div></div>';
    try{await actions().load?.(force,c?.cache?.date);return renderCoach()}catch(err){host.innerHTML=loadErrorHtml('coach',actions().cloudError?.(err)||err?.message);bindHost(host);return false}
  }
  function renderStudent(){
    const c=context();resetIdentity(c);if(c?.profile?.role!=='student')return false;
    const host=root.document?.getElementById('studentSubBody');if(!host)return false;
    const p=c?.cache?.plan,pd=planData(c);
    if(!p||p.active===false){host.innerHTML='<div class="fjz4a-student-shell"><header class="fjz4a-student-head"><div><span>NUTRICIÓN</span><h1>Mi alimentación</h1><p>Tu espacio diario de nutrición.</p></div></header><section class="fjz4a-empty-state"><strong>Sin plan activo</strong><span>Tu coach todavía no publicó un plan nutricional activo.</span><button type="button" data-4a-action="recipes">Ver recetas disponibles</button></section>'+resourcesHtml(pd||{},true)+'</div>';bindHost(host);return true}
    if(!ui.savedSignature)ui.savedSignature=signature(c);
    const logging=p.student_logging_enabled!==false;
    host.innerHTML='<div class="fjz4a-student-shell"><header class="fjz4a-student-head"><div><span>NUTRICIÓN</span><h1>Mi alimentación</h1><p>'+esc(p.title||'Plan nutricional')+' · revisión '+esc(p.revision||1)+(p.updated_at?' · actualizada '+esc(actions().formatDate?.(p.updated_at)||''):'')+'</p></div><div class="fjz4a-plan-state"><i></i><strong>'+(p.active===false?'Pausado':'Plan asignado')+'</strong></div></header>'+ 
      '<section class="fjz4a-plan-overview"><div><span>OBJETIVOS DEL PLAN</span><h2>Referencias diarias</h2><p>No representan consumo real.</p></div>'+targetsHtml(p)+(p.notes?'<aside><strong>Indicaciones del Coach</strong><p>'+esc(p.notes)+'</p></aside>':'')+'</section>'+ 
      '<section class="fjz4a-meals"><div class="fjz4a-section-heading"><span>PLAN DEL DÍA</span><h2>Comidas y alternativas</h2><p>Elegí qué opción consultar. Cambiar de opción no registra nada.</p></div>'+((pd?.meals||[]).length?pd.meals.map((m,i)=>mealStudentHtml(m,i,logging,false)).join(''):'<div class="fjz4a-empty-block"><strong>Sin comidas cargadas</strong><span>Tu coach todavía no agregó comidas al plan.</span></div>')+'</section>'+ 
      resourcesHtml(pd,true)+calculatorHtml(c)+consumptionHtml(c,true)+'</div>';
    bindHost(host);actions().previewMacro?.();return true;
  }
  function coachMealSelected(pd){
    const meals=pd?.meals||[];if(!meals.length)return null;
    let m=findMeal(pd,ui.coachMealId);if(!m){m=meals[0];ui.coachMealId=text(m.id)}return m;
  }
  function coachOptionHtml(meal,opt,index){
    const t=optionTotals(opt),mid=text(meal?.id),oid=text(opt?.id),editable=!!(mid&&oid);
    return '<article class="fjz4a-coach-option"><div class="fjz4a-coach-option-head"><div><span>OPCIÓN '+(index+1)+'</span><input class="fjz4a-option-name" data-4a-action="option-name" data-meal="'+esc(mid)+'" data-option="'+esc(oid)+'" value="'+esc(opt?.name||('Opción '+(index+1)))+'" aria-label="Nombre de opción"></div>'+macrosHtml(t,'fjz4a-macros fjz4a-option-macros')+'</div><ul class="fjz4a-foods coach">'+((opt?.items||[]).length?opt.items.map(i=>itemHtml(i,true,mid,oid)).join(''):'<li class="fjz4a-empty-line">Sin alimentos en esta opción.</li>')+'</ul><div class="fjz4a-option-actions">'+(editable?'<button type="button" data-4a-action="add-food" data-meal="'+esc(mid)+'" data-option="'+esc(oid)+'">+ Alimento</button><button type="button" class="danger" data-4a-action="delete-option" data-meal="'+esc(mid)+'" data-option="'+esc(oid)+'">Eliminar opción</button>':'<span>Opción histórica sin identificador: lectura protegida.</span>')+'</div></article>';
  }
  function saveStateHtml(dirty){
    const state=ui.saving?'saving':ui.lastSaveState==='error'?'error':dirty?'dirty':'saved';
    const label=state==='saving'?'Guardando…':state==='error'?'Error al guardar':state==='dirty'?'Cambios pendientes':'Guardado';
    return '<span id="fjz4aSaveState" class="fjz4a-save-state '+state+'"><i></i>'+label+'</span>';
  }
  function coachToolsHtml(){return '<div class="fjz4a-coach-tools"><button type="button" data-4a-action="preview">Vista Alumno</button><button type="button" data-4a-action="coach-calculator">Calculadora</button><button type="button" data-4a-action="coach-recipes">Recetas</button><button type="button" data-4a-action="templates">Plantillas</button><button type="button" data-4a-action="save-template">Guardar plantilla</button></div>'}
  function renderCoach(){
    const c=context();resetIdentity(c);if(c?.profile?.role!=='coach')return false;
    const host=root.document?.getElementById('coachStudentBody');if(!host)return false;
    const p=c?.cache?.plan,pd=planData(c);
    if(p&&text(p.athlete_id)&&text(c.athleteId)&&text(p.athlete_id)!==text(c.athleteId)){host.innerHTML='<div class="fjz4a-loading">Actualizando nutrición del alumno…</div>';actions().load?.(true,c?.cache?.date).then(()=>renderCoach()).catch(()=>{});return true}
    if(!p){host.innerHTML='<div class="fjz4a-coach-shell empty-plan"><header class="fjz4a-coach-head"><div><span>NUTRICIÓN DEL ALUMNO</span><h1>Editor nutricional</h1><p>'+esc(c?.student?.name||'Alumno')+'</p></div></header><section class="fjz4a-empty-state"><strong>Sin plan nutricional</strong><span>Creá un plan sin reemplazar ninguna otra autoridad del perfil.</span><button type="button" class="primary" data-4a-action="create-plan">Crear plan nutricional</button></section></div>';bindHost(host);return true}
    if(!ui.savedSignature)ui.savedSignature=signature(c);
    const dirty=signature(c)!==ui.savedSignature||ui.lastSaveState==='dirty';
    const meal=coachMealSelected(pd),meals=pd?.meals||[];
    host.innerHTML='<div class="fjz4a-coach-shell"><header class="fjz4a-coach-head"><div><span>ATHLETE 360 · NUTRICIÓN</span><h1>'+esc(c?.student?.name||'Alumno')+'</h1><p>'+esc(p.title||'Plan nutricional')+' · revisión '+esc(p.revision||1)+'</p></div><div class="fjz4a-coach-save">'+saveStateHtml(dirty)+'<button type="button" class="primary" data-4a-action="save-plan" '+(ui.saving?'disabled':'')+'>Guardar cambios</button></div></header>'+ 
      '<div class="fjz4a-coach-workspace"><aside class="fjz4a-editor-rail"><div class="fjz4a-rail-head"><span>COMIDAS</span><button type="button" data-4a-action="add-meal">+ Agregar</button></div><nav aria-label="Comidas del plan">'+meals.map((m,i)=>'<button type="button" class="'+(text(m.id)===text(meal?.id)?'active':'')+'" data-4a-action="coach-meal" data-meal="'+esc(text(m.id))+'"><span>'+String(i+1).padStart(2,'0')+'</span><div><strong>'+esc(m.name||'Comida')+'</strong><small>'+((m.options||[]).length)+' opciones</small></div></button>').join('')+'</nav>'+coachToolsHtml()+'</aside><main class="fjz4a-editor-main">'+ 
      '<section class="fjz4a-plan-settings"><div class="fjz4a-section-heading"><span>CONFIGURACIÓN DEL PLAN</span><h2>Prescripción</h2><p>Los objetivos del plan se mantienen separados del consumo registrado.</p></div><div class="fjz4a-settings-grid"><label class="span2">Nombre del plan<input id="nutTitle" value="'+esc(p.title||'Plan nutricional')+'"></label><label>Calorías<input id="nutKcal" type="number" min="0" step="1" value="'+esc(p.target_kcal??'')+'"></label><label>Proteínas (g)<input id="nutProtein" type="number" min="0" step="1" value="'+esc(p.target_protein_g??'')+'"></label><label>Carbohidratos (g)<input id="nutCarbs" type="number" min="0" step="1" value="'+esc(p.target_carbs_g??'')+'"></label><label>Grasas (g)<input id="nutFat" type="number" min="0" step="1" value="'+esc(p.target_fat_g??'')+'"></label><label class="span2">Indicaciones<textarea id="nutNotes" rows="3">'+esc(p.notes||'')+'</textarea></label><label class="fjz4a-toggle span2"><input id="nutLoggingEnabled" type="checkbox" '+(p.student_logging_enabled!==false?'checked':'')+'><span><strong>Registro diario del alumno</strong><small>'+(p.student_logging_enabled!==false?'Habilitado con persistencia real':'Desactivado · el alumno sólo consulta el plan')+'</small></span></label></div></section>'+ 
      (meal?'<section class="fjz4a-meal-editor"><div class="fjz4a-meal-editor-head"><div><span>COMIDA SELECCIONADA</span><h2>'+esc(meal.name||'Comida')+'</h2><p>'+((meal.options||[]).length)+' alternativa'+((meal.options||[]).length===1?'':'s')+'</p></div><div><button type="button" data-4a-action="meal-macros" data-meal="'+esc(text(meal.id))+'">Macros comida</button><button type="button" data-4a-action="rename-meal" data-meal="'+esc(text(meal.id))+'">Renombrar</button><button type="button" data-4a-action="add-option" data-meal="'+esc(text(meal.id))+'">+ Opción</button><button type="button" class="danger" data-4a-action="delete-meal" data-meal="'+esc(text(meal.id))+'">Eliminar</button></div></div><div class="fjz4a-coach-options">'+((meal.options||[]).length?meal.options.map((o,i)=>coachOptionHtml(meal,o,i)).join(''):'<div class="fjz4a-empty-block"><strong>Sin alternativas</strong><span>Agregá la primera opción para esta comida.</span></div>')+'</div></section>':'<section class="fjz4a-empty-block"><strong>Sin comidas</strong><span>Agregá una comida para comenzar el plan.</span></section>')+
      resourcesHtml(pd,false)+consumptionHtml(c,false)+(typeof actions().historyHtml==='function'?actions().historyHtml():'')+'</main></div></div>';
    bindHost(host);return true;
  }
  function setDirty(on=true){ui.lastSaveState=on?'dirty':'saved';const node=root.document?.getElementById('fjz4aSaveState');if(node){node.className='fjz4a-save-state '+(on?'dirty':'saved');node.innerHTML='<i></i>'+(on?'Cambios pendientes':'Guardado')}}
  async function savePlan(button){
    if(ui.saving)return false;const c=context(),p=c?.cache?.plan;if(!p)return false;
    const beforeRev=Number(p.revision||0),beforeId=text(p.id);ui.saving=true;ui.lastSaveState='saving';if(button){button.disabled=true;button.textContent='Guardando…'}
    try{
      const result=await actions().savePlan?.();const now=context().cache?.plan;
      if(!now||text(now.id)!==beforeId||Number(now.revision||0)<=beforeRev)throw new Error('El servidor no confirmó una nueva revisión del plan.');
      ui.savedSignature=signature(context());ui.lastSaveState='saved';ui.saving=false;root.__fjzConfirmSavedV264?.('Plan nutricional guardado','Los cambios quedaron confirmados en la nube.');renderCoach();return result!==false;
    }catch(err){ui.saving=false;ui.lastSaveState='error';root.toast?.(text(err?.message||'No se pudo guardar el plan.'));if(button){button.disabled=false;button.textContent='Guardar cambios'}const n=root.document?.getElementById('fjz4aSaveState');if(n){n.className='fjz4a-save-state error';n.innerHTML='<i></i>Error al guardar'}return false}
  }
  async function registerOption(mealId,optId,button){
    const c=context(),pd=planData(c),meal=findMeal(pd,mealId),opt=findOption(pd,mealId,optId),key=text(mealId)+'|'+text(optId);
    if(!meal||!opt||(opt.items||[]).length===0){root.toast?.('Esta opción no tiene alimentos.');return false}
    if(c?.profile?.role!=='student'||!c?.cache?.plan||c.cache.plan.active===false||c.cache.plan.student_logging_enabled===false){root.toast?.('El registro nutricional no está habilitado.');return false}
    if(ui.registering.has(key))return false;const sb=c?.supabase;if(!sb||!c.athleteId||!c.userId){root.toast?.('No está disponible la persistencia nutricional.');return false}
    ui.registering.add(key);const old=button?.textContent||'Registrar hoy';if(button){button.disabled=true;button.textContent='Guardando…'}
    try{
      const group=(root.crypto?.randomUUID?.()||actions().uuid?.());if(!group)throw new Error('No se pudo crear la identidad del registro.');
      const date=text(c?.cache?.date||actions().today?.()),note=optionMarker(mealId,optId);
      const rows=(opt.items||[]).map(i=>({athlete_id:c.athleteId,student_id:c.userId,logged_on:date,meal_label:text(meal.name||'Comida'),food_id:i.food_id||null,food_name:text(i.name||'Alimento'),grams:num(i.grams),kcal:num(i.kcal),protein_g:num(i.protein_g),carbs_g:num(i.carbs_g),fat_g:num(i.fat_g),source:'plan',note,measure_type:text(i.measure_type)==='units'?'units':'grams',quantity:text(i.measure_type)==='units'?(i.quantity??null):null,unit_name:text(i.measure_type)==='units'?(i.unit_name||null):null,meal_group_id:group}));
      if(rows.some(r=>!(r.grams>0)))throw new Error('La opción contiene una cantidad inválida.');
      const {data,error}=await sb.from('nutrition_logs').insert(rows).select('id,meal_group_id,note');if(error)throw error;
      if(!Array.isArray(data)||data.length!==rows.length||data.some(x=>text(x.meal_group_id)!==group||parseOptionMarker(x.note)?.optionId!==text(optId)))throw new Error('El servidor no confirmó el registro completo.');
      await actions().load?.(true,date);root.__fjzQuickSavedV264?.('Opción registrada');root.toast?.('Opción registrada');renderStudent();return true;
    }catch(err){root.toast?.(actions().cloudError?.(err)||text(err?.message||'No se pudo registrar la opción.'));if(button){button.disabled=false;button.textContent=old}return false}
    finally{ui.registering.delete(key)}
  }
  async function deleteLog(groupId,rowId){
    const c=context(),sb=c?.supabase;if(!sb)return false;
    try{let q=sb.from('nutrition_logs').delete();q=groupId?q.eq('meal_group_id',groupId):q.eq('id',rowId);const {error}=await q;if(error)throw error;await actions().load?.(true,c?.cache?.date);root.__fjzQuickSavedV264?.('Cambio guardado');renderStudent();return true}catch(err){root.toast?.(actions().cloudError?.(err)||text(err?.message||'No se pudo eliminar el registro.'));return false}
  }
  function preview(){const c=context(),p=c?.cache?.plan,pd=planData(c);if(!p)return false;const html='<div class="fjz4a-preview-modal"><div class="fjz4a-preview-modal-head"><div><span>VISTA ALUMNO</span><h2>'+esc(p.title||'Mi alimentación')+'</h2></div><button type="button" onclick="closeModal()">Cerrar</button></div><div class="fjz4a-plan-overview compact">'+targetsHtml(p)+'</div><div class="fjz4a-meals preview">'+(pd?.meals||[]).map((m,i)=>mealStudentHtml(m,i,false,true)).join('')+'</div></div>';actions().showModal?.(html);return true}
  function selectStudentOption(button){
    const mid=text(button?.dataset?.meal),oid=text(button?.dataset?.option),meal=button?.closest?.('[data-4a-meal]');if(!meal)return;
    ui.studentOptions[mid]=oid;meal.querySelectorAll('[role="tab"]').forEach(b=>{const on=text(b.dataset.option)===oid;b.classList.toggle('active',on);b.setAttribute('aria-selected',on?'true':'false')});meal.querySelectorAll('[data-4a-option]').forEach((a,i)=>{const on=text(a.dataset['4aOption'])===oid||(!text(a.dataset['4aOption'])&&i===0);a.hidden=!on;a.classList.toggle('active',on)});
  }
  function bindHost(host){
    if(!host)return;host.onclick=async e=>{
      const b=e.target.closest?.('[data-4a-action]');if(!b)return;const a=b.dataset['4aAction'];
      if(a==='select-option'){selectStudentOption(b);return}
      if(a==='register-option'){await registerOption(b.dataset.meal,b.dataset.option,b);return}
      if(a==='recipes'){actions().recipes?.();return}
      if(a==='calculator-focus'){const h=root.document?.getElementById('fjz4aCalculator');h?.scrollIntoView?.({behavior:'auto',block:'start'});h?.focus?.({preventScroll:true});return}
      if(a==='calculator-add'){await actions().calculatorAdd?.();return}
      if(a==='custom-log'){actions().customLog?.();return}
      if(a==='delete-log'){await deleteLog(b.dataset.group,b.dataset.row);return}
      if(a==='create-plan'){await actions().createPlan?.();return}
      if(a==='save-plan'){await savePlan(b);return}
      if(a==='coach-meal'){ui.coachMealId=b.dataset.meal;renderCoach();return}
      if(a==='add-meal'){actions().addMeal?.();return}
      if(a==='rename-meal'){actions().renameMeal?.(b.dataset.meal);return}
      if(a==='delete-meal'){actions().deleteMeal?.(b.dataset.meal);setDirty();return}
      if(a==='add-option'){actions().addOption?.(b.dataset.meal);setDirty();return}
      if(a==='delete-option'){actions().deleteOption?.(b.dataset.meal,b.dataset.option);setDirty();return}
      if(a==='add-food'){actions().openFood?.(b.dataset.meal,b.dataset.option);return}
      if(a==='amount'){actions().editAmount?.(b.dataset.meal,b.dataset.option,b.dataset.item);return}
      if(a==='remove-food'){actions().removeFood?.(b.dataset.meal,b.dataset.option,b.dataset.item);setDirty();return}
      if(a==='meal-macros'){actions().mealMacros?.(b.dataset.meal);return}
      if(a==='preview'){preview();return}
      if(a==='coach-calculator'){actions().coachCalculator?.();return}
      if(a==='coach-recipes'){actions().coachRecipes?.();return}
      if(a==='templates'){actions().templates?.();return}
      if(a==='save-template'){actions().saveTemplate?.();return}
      if(a==='add-supplement'){actions().addSupplement?.();return}
      if(a==='edit-supplement'){actions().editSupplement?.(Number(b.dataset.index));return}
      if(a==='remove-supplement'){actions().removeSupplement?.(Number(b.dataset.index));setDirty();return}
      if(a==='add-habit'){actions().addHabit?.();return}
      if(a==='delete-habit'){actions().deleteHabit?.(b.dataset.habit);setDirty();return}
      if(a==='retry-load'){if(b.dataset.role==='coach')await startCoach(true);else await startStudent(true);return}
    };
    host.oninput=e=>{const t=e.target;if(!t)return;if(['nutTitle','nutKcal','nutProtein','nutCarbs','nutFat','nutNotes'].includes(t.id)){setDirty(true);return}if(t.matches?.('[data-4a-action="option-name"]')){const pd=planData(),o=findOption(pd,t.dataset.meal,t.dataset.option);if(o){o.name=t.value;setDirty(true)}}};
    host.onchange=e=>{const t=e.target;if(!t)return;if(t.id==='nutLoggingEnabled'){setDirty(true);return}if(t.matches?.('[data-4a-action="toggle-habit"]')){actions().toggleHabit?.(t.dataset.habit,!!t.checked);setDirty();return}if(['macroFood','macroMeasure','macroGrams','macroUnits'].includes(t.id)){actions().previewMacro?.();return}};
    const food=root.document?.getElementById('macroFood'),measure=root.document?.getElementById('macroMeasure'),grams=root.document?.getElementById('macroGrams'),units=root.document?.getElementById('macroUnits');
    for(const el of [food,measure])if(el)el.onchange=()=>actions().previewMacro?.();for(const el of [grams,units])if(el)el.oninput=()=>actions().previewMacro?.();
  }
  function install(){root.__fjzNutritionPremiumV22=api;return true}
  const api={VERSION,optionTotals,logTotals,optionMarker,parseOptionMarker,consumptionGroups,startStudent,startCoach,renderStudent,renderCoach,registerOption,savePlan,install,state:ui};
  return Object.freeze(api);
});
