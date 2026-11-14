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
    const c=context();resetIdentity(c);if(c?.profil