const test=require('node:test');
const assert=require('node:assert/strict');
const api=require('../../src/modules/nutrition/premium.js');

test('4A sums only one prescribed option and never adjacent alternatives',()=>{
  const chosen={items:[{kcal:195,protein_g:4.05,carbs_g:42,fat_g:.45},{kcal:247.5,protein_g:46.5,carbs_g:0,fat_g:5.4}]};
  const other={items:[{kcal:999,protein_g:99,carbs_g:99,fat_g:99}]};
  const t=api.optionTotals(chosen);
  assert.equal(t.kcal,442.5);assert.equal(t.protein_g,50.55);assert.equal(t.carbs_g,42);assert.ok(Math.abs(t.fat_g-5.85)<1e-9);
  assert.notEqual(t.kcal,api.optionTotals(chosen).kcal+api.optionTotals(other).kcal);
});

test('4A option marker round-trips exact meal and option identity',()=>{
  const note=api.optionMarker('meal_qa_lunch','opt_qa_2');
  assert.deepEqual(api.parseOptionMarker(note),{mealId:'meal_qa_lunch',optionId:'opt_qa_2'});
  assert.equal(api.parseOptionMarker('legacy note'),null);
});

test('4A groups one consumed option by persisted meal_group_id without double counting',()=>{
  const note=api.optionMarker('m1','o2');
  const pd={meals:[{id:'m1',name:'Almuerzo',options:[{id:'o2',name:'Opción 2'}]}]};
  const rows=[
    {id:'a',meal_group_id:'g1',meal_label:'Almuerzo',food_name:'Arroz',kcal:195,protein_g:4,carbs_g:42,fat_g:.5,note,source:'plan'},
    {id:'b',meal_group_id:'g1',meal_label:'Almuerzo',food_name:'Pollo',kcal:250,protein_g:45,carbs_g:0,fat_g:6,note,source:'plan'}
  ];
  const g=api.consumptionGroups(rows,pd);
  assert.equal(g.length,1);assert.equal(g[0].identified,true);assert.equal(g[0].mealName,'Almuerzo');assert.equal(g[0].optionName,'Opción 2');assert.equal(g[0].totals.kcal,445);
});

test('4A historical plan logs remain visible but never invent an option identity',()=>{
  const g=api.consumptionGroups([{id:'legacy',meal_label:'Cena',food_name:'Carne',kcal:300,source:'plan',note:''}],{meals:[]});
  assert.equal(g.length,1);assert.equal(g[0].identified,false);assert.equal(g[0].optionName,'');
});

test('4A install exposes bounded nutrition hook without replacing global render',()=>{
  const sentinel=()=>{};const old=global.render,oldHook=global.__fjzNutritionPremiumV22;
  try{global.render=sentinel;assert.equal(api.install(),true);assert.equal(global.__fjzNutritionPremiumV22,api);assert.equal(global.render,sentinel)}finally{global.render=old;global.__fjzNutritionPremiumV22=oldHook}
});
