const {test,expect}=require('@playwright/test');
const PASSWORD='TEAMFJZ-Local-Only!22';
async function login(page,email='alumno01@test.local'){
  await page.goto('/');const gate=page.locator('#authGate');
  if(await gate.isVisible().catch(()=>false)){await page.locator('#authEmail').fill(email);await page.locator('#authPass').fill(PASSWORD);await page.locator('#authGate .btn.primary').click()}
  await expect(gate).toBeHidden({timeout:20000});
  if(email==='coach@test.local')await expect(page.locator('.fjz3a-command-center')).toBeVisible({timeout:20000});
}
async function openStudentNutrition(page){await page.getByRole('button',{name:'Nutrición'}).first().click();await expect(page.locator('.fjz4a-student-shell')).toBeVisible({timeout:20000})}
async function openAthlete(page,name='TEST ALUMNO 01'){
  const search=page.locator('#fjz3aStudentSearch');if(await search.count())await search.fill(name.replace('TEST ',''));
  const row=page.locator('#studentList .student-row',{hasText:name}).first();await expect(row).toBeVisible({timeout:15000});await row.getByRole('button',{name:/Abrir/i}).click();
  await expect(page.locator('.fjz3b-header')).toBeVisible({timeout:15000});
}
async function openCoachNutrition(page){const b=page.locator('.fjz3b-nav button[data-section="nutrition"]');await b.click();await expect(b).toHaveAttribute('aria-current','page');await expect(page.locator('.fjz4a-coach-shell')).toBeVisible({timeout:20000})}
async function noOverflow(page){const x=await page.evaluate(()=>({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth}));expect(x.sw).toBeLessThanOrEqual(x.cw+2)}
async function closeSaveModal(page){const modal=page.locator('#modal');if(await modal.isVisible().catch(()=>false)){const b=modal.getByRole('button',{name:/Listo|Cerrar/i}).first();if(await b.count())await b.click();else await page.keyboard.press('Escape')}}

test.describe('V22 4A Nutrition Premium',()=>{
  test('V22 4A alumno: plan premium, alternativas, macros y selección visual sin consumo inventado',async({page})=>{
    await login(page);await openStudentNutrition(page);
    await expect(page.getByRole('heading',{name:'Mi alimentación'})).toBeVisible();await expect(page.locator('.fjz4a-student-shell')).toContainText('PLAN QA A');
    await expect(page.locator('.fjz4a-targets')).toContainText(/2200/);await expect(page.locator('.fjz4a-targets')).toContainText(/160/);
    await page.evaluate(()=>{const p=__fjzNutritionContextV22().cache.plan.plan;const m=p.meals.find(x=>x.id==='meal_qa_breakfast');m.options.push({id:'opt_qa_1b',name:'Opción QA 1B',items:[{id:'item_qa_1b',name:'QA Tostadas ficticias',grams:60,kcal:150,protein_g:6,carbs_g:28,fat_g:2,measure_type:'units',quantity:2,unit_name:'tostadas',grams_per_unit:30}]});TeamFJZNutritionPremium.renderStudent()});
    const breakfast=page.locator('.fjz4a-meal',{hasText:'Desayuno'});const tabs=breakfast.locator('[role="tab"]');await expect(tabs).toHaveCount(2);
    const logsBefore=await page.locator('.nutrition-log-row').count();await tabs.nth(1).click();await expect(tabs.nth(1)).toHaveAttribute('aria-selected','true');
    const visible=breakfast.locator('.meal-option-student:visible');await expect(visible).toContainText('Opción QA 1B');await expect(visible).toContainText(/kcal/);await expect(visible).toContainText(/g/);
    expect(await page.locator('.nutrition-log-row').count()).toBe(logsBefore);await noOverflow(page);
  });

  test('V22 4A registro de opción usa persistencia real con meal_group_id e identidad exacta',async({page})=>{
    await login(page);await openStudentNutrition(page);
    const lunch=page.locator('.fjz4a-meal',{hasText:'Almuerzo'});const option=lunch.locator('.meal-option-student',{hasText:'Opción QA 2'});await option.getByRole('button',{name:/Registrar hoy/i}).click();
    await expect(page.locator('#v264QuickSaved')).toContainText(/Opción registrada/i,{timeout:15000});await expect(page.locator('.nutrition-log')).toContainText('QA Arroz cocido');await expect(page.locator('.nutrition-log')).toContainText('QA Proteína ficticia');
    const persisted=await page.evaluate(async()=>{const c=__fjzNutritionContextV22();const {data,error}=await c.supabase.from('nutrition_logs').select('id,meal_group_id,note,meal_label,food_name').eq('athlete_id',c.athleteId).like('note','FJZ4A_OPTION:%');if(error)throw error;return data});
    expect(persisted.length).toBeGreaterThanOrEqual(2);const newest=persisted.slice(-2);expect(newest.every(x=>!!x.meal_group_id)).toBeTruthy();expect(new Set(newest.map(x=>x.meal_group_id)).size).toBe(1);expect(newest.every(x=>/meal_qa_lunch/.test(x.note)&&/opt_qa_2/.test(x.note))).toBeTruthy();
    const gid=newest[0].meal_group_id;await page.evaluate(async gid=>{const c=__fjzNutritionContextV22();const {error}=await c.supabase.from('nutrition_logs').delete().eq('meal_group_id',gid);if(error)throw error;await __fjzNutritionActionsV22.load(true,c.cache.date);TeamFJZNutritionPremium.renderStudent()},gid);await noOverflow(page);
  });

  test('V22 4A recetas y calculadora reutilizan herramientas existentes',async({page})=>{
    await login(page);await openStudentNutrition(page);await page.getByRole('button',{name:/Recetas/i}).first().click();
    await expect(page.getByText('Receta QA local',{exact:true})).toBeVisible({timeout:15000});await page.getByRole('button',{name:'Ver receta'}).first().click();await expect(page.locator('#modal')).toContainText('Ingrediente QA');await page.locator('#modal').getByRole('button',{name:/Cerrar|✕/}).first().click();
    await page.getByRole('button',{name:/Mi plan/i}).first().click();await expect(page.locator('.fjz4a-student-shell')).toBeVisible({timeout:15000});await page.getByRole('button',{name:/Calculadora/i}).first().click();
    await expect(page.locator('#macroFood')).toBeVisible();await expect(page.locator('#macroPreview')).toContainText(/Proteína|Calorías/i);await noOverflow(page);
  });

  test('V22 4A registro deshabilitado no inventa incumplimiento ni permite registrar opción',async({page})=>{
    await login(page,'alumno02@test.local');await openStudentNutrition(page);await expect(page.locator('.fjz4a-student-shell')).toContainText('PLAN QA B');
    await expect(page.locator('.fjz4a-register')).toHaveCount(0);await expect(page.locator('.fjz4a-disabled-note')).toContainText(/desactivado/i);await expect(page.locator('.fjz4a-consumption')).toContainText(/Sin registrar|CONSUMO REGISTRADO/i);await expect(page.locator('.fjz4a-consumption')).not.toContainText(/No cumplió/i);await noOverflow(page);
  });

  test('V22 4A estado sin plan es explícito y recuperable',async({page})=>{
    await page.route('**/rest/v1/nutrition_plans*',async route=>{if(route.request().method()==='GET')return route.fulfill({status:200,contentType:'application/json',headers:{'content-range':'*/0'},body:'[]'});return route.continue()});
    await login(page,'alumno02@test.local');await page.getByRole('button',{name:'Nutrición'}).first().click();await expect(page.locator('.fjz4a-empty-state')).toContainText(/Sin plan activo/i,{timeout:15000});await expect(page.locator('.fjz4a-student-shell')).not.toContainText('PLAN QA A');await noOverflow(page);
  });

  test('V22 4A Coach: editor premium guarda sólo con confirmación real y conserva planes históricos',async({page})=>{
    await login(page,'coach@test.local');await openAthlete(page);await openCoachNutrition(page);
    await expect(page.locator('.fjz4a-coach-shell')).toContainText('PLAN QA A');await expect(page.locator('.fjz4a-editor-rail nav button')).toHaveCount(2);await expect(page.locator('.fjz4a-coach-options')).toContainText(/QA Yogur ficticio|Opción QA 1/);
    const title=page.locator('#nutTitle');const original=await title.inputValue();await title.fill(original+' · 4A QA');await expect(page.locator('#fjz4aSaveState')).toContainText(/Cambios pendientes/i);await page.getByRole('button',{name:'Guardar cambios'}).click();
    await expect(page.locator('#modal')).toContainText(/Plan nutricional guardado/i,{timeout:15000});await closeSaveModal(page);await expect(page.locator('#fjz4aSaveState')).toContainText(/Guardado/i);expect(await page.locator('#nutTitle').inputValue()).toContain('4A QA');
    await page.reload();await expect(page.locator('.fjz3b-header')).toBeVisible({timeout:20000});await expect(page.locator('#nutTitle')).toHaveValue(/4A QA/,{timeout:20000});
    await page.locator('#nutTitle').fill(original);await page.getByRole('button',{name:'Guardar cambios'}).click();await expect(page.locator('#modal')).toContainText(/Plan nutricional guardado/i,{timeout:15000});await closeSaveModal(page);await noOverflow(page);
  });

  test('V22 4A Coach: error de guardado no muestra éxito falso',async({page})=>{
    await login(page,'coach@test.local');await openAthlete(page);await openCoachNutrition(page);const notes=page.locator('#nutNotes'),before=await notes.inputValue();await notes.fill(before+' QA error');
    await page.route('**/rest/v1/nutrition_plans*',route=>{if(route.request().method()==='PATCH')return route.abort('failed');return route.continue()});await page.getByRole('button',{name:'Guardar cambios'}).click();await expect(page.locator('#fjz4aSaveState')).toContainText(/Error al guardar/i,{timeout:15000});await expect(page.locator('#modal')).not.toBeVisible();
    await page.unroute('**/rest/v1/nutrition_plans*');await notes.fill(before);await page.getByRole('button',{name:'Guardar cambios'}).click();await expect(page.locator('#modal')).toContainText(/Plan nutricional guardado/i,{timeout:15000});await closeSaveModal(page);
  });

  test('V22 4A Athlete 360 mantiene aislamiento A/B y navegación única',async({page})=>{
    await login(page,'coach@test.local');await openAthlete(page,'TEST ALUMNO 01');await openCoachNutrition(page);await expect(page.locator('.fjz4a-coach-shell')).toContainText('PLAN QA A');await expect(page.locator('.fjz3b-nav:visible')).toHaveCount(1);
    await page.locator('[data-3b-action="back"]').first().click();await expect(page.locator('.fjz3a-command-center')).toBeVisible();await openAthlete(page,'TEST ALUMNO 02');await openCoachNutrition(page);await expect(page.locator('.fjz4a-coach-shell')).toContainText('PLAN QA B');await expect(page.locator('.fjz4a-coach-shell')).not.toContainText('PLAN QA A');await noOverflow(page);
  });

  test('V22 4A alumno no accede al editor Coach y macros no desbordan',async({page})=>{
    await login(page);await openStudentNutrition(page);await expect(page.locator('.fjz4a-coach-shell')).toHaveCount(0);const boxes=await page.locator('.fjz4a-macros').evaluateAll(xs=>xs.map(x=>({sw:x.scrollWidth,cw:x.clientWidth})));expect(boxes.every(x=>x.sw<=x.cw+2)).toBeTruthy();await noOverflow(page);
  });
});
