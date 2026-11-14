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
    const remembered=ui.studentOptions[mid],activeIndex=Math.max(0,opts.findIndex(o=>text(o?.id)===remembered)