const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');

test('V22 4A-UX es presentation-only y no agrega topología runtime',()=>{
  const css=fs.readFileSync('src/ui/nutrition-ux-final-polish.css','utf8');
  const py=fs.readFileSync('v349_v22_4a_ux_nutrition_final_polish.py','utf8');
  assert.match(css,/4A-UX Nutrition final polish/);
  assert.match(css,/#view:has\(\.fjz4a-student-shell\)/);
  assert.match(css,/#view\.fjz3b-mounted:has\(\.fjz4a-coach-shell\)/);
  for(const forbidden of ['addEventListener(','.channel(','setTimeout(','setInterval(','MutationObserver','PerformanceObserver']){
    assert.equal(css.includes(forbidden),false,forbidden+' no debe existir en CSS 4A-UX');
  }
  assert.match(py,/before!=after/);
});

test('V22 4A-UX prioriza comida Coach antes de configuración general sin cambiar autoridades',()=>{
  const src=fs.readFileSync('src/modules/nutrition/premium.js','utf8');
  const meal=src.indexOf('<section class="fjz4a-meal-editor"');
  const settings=src.indexOf('<section class="fjz4a-plan-settings"');
  assert.ok(meal>0&&settings>meal,'la comida seleccionada debe preceder la prescripción');
  assert.match(src,/EDITOR NUTRICIONAL/);
  for(const authority of ['meal_group_id','optionMarker','actions().optionTotals','actions().savePlan']){
    assert.ok(src.includes(authority),'autoridad preservada: '+authority);
  }
});

test('V22 4A-UX define jerarquía mobile y desktop explícita',()=>{
  const css=fs.readFileSync('src/ui/nutrition-ux-final-polish.css','utf8');
  assert.match(css,/@media\(max-width:620px\)/);
  assert.match(css,/#studentMainTabs\{display:none!important\}/);
  assert.match(css,/grid-template-columns:repeat\(4,minmax\(0,1fr\)\)/);
  assert.match(css,/position:static!important/);
  assert.match(css,/@media\(min-width:901px\)/);
  assert.match(css,/grid-template-columns:minmax\(0,1\.45fr\) minmax\(310px,\.72fr\)/);
});
