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
  const row=page.locator('#studentList .student-row',{hasText:name}).first();await expect(row).toBeVisible({timeout:15000});await row.getByRole('button',{name:/Abrir/i}).click();await expect(page.locator('.fjz3b-header')).toBeVisible({timeout:15000});
}
async function openCoachNutrition(page){const b=page.locator('.fjz3b-nav button[data-section="nutrition"]');await b.click();await expect(b).toHaveAttribute('aria-current','page');await expect(page.locator('.fjz4a-coach-shell')).toBeVisible({timeout:20000})}
async function noOverflow(page){const g=await page.evaluate(()=>{const r=document.scrollingElement||document.documentElement,ox=scrollX,oy=scrollY;scrollTo(100000,oy);const mx=scrollX;scrollTo(ox,oy);return{sw:r.scrollWidth,cw:r.clientWidth,mx}});expect(g.sw).toBeLessThanOrEqual(g.cw+2);expect(g.mx).toBeLessThanOrEqual(2)}

test.describe('V22 4A-UX Nutrition final polish',()=>{
  test('V22 4A-UX alumno: primera comida entra antes y navegación mobile no se duplica',async({page})=>{
    await login(page);await openStudentNutrition(page);
    await expect(page.locator('.fjz4a-student-head')).toBeVisible({timeout:15000});
    await expect(page.locator('.fjz4a-targets')).toBeVisible({timeout:15000});
    await expect(page.locator('.fjz4a-meal').first()).toBeVisible({timeout:15000});
    const geo=await page.evaluate(()=>{
      const meal=document.querySelector('.fjz4a-meal'),head=document.querySelector('.fjz4a-student-head'),targets=document.querySelector('.fjz4a-targets'),tabs=document.querySelector('#studentMainTabs'),bottom=document.querySelector('#bottomNav');
      const rect=x=>x?x.getBoundingClientRect():null;
      return{w:innerWidth,h:innerHeight,meal:rect(meal),head:rect(head),targets:rect(targets),tabsDisplay:tabs?getComputedStyle(tabs).display:null,bottomDisplay:bottom?getComputedStyle(bottom).display:null};
    });
    expect(geo.head.top).toBeGreaterThanOrEqual(-2);expect(geo.targets.bottom).toBeLessThan(geo.h);
    if(geo.w<=620){expect(geo.meal.top).toBeLessThan(geo.h);expect(geo.tabsDisplay).toBe('none');expect(geo.bottomDisplay).not.toBe('none')}
    await expect(page.locator('.fjz4a-targets')).toContainText(/Calorías/i);await noOverflow(page);
  });

  test('V22 4A-UX alumno: macros compactos, alternativas táctiles y selección sin escritura',async({page})=>{
    await login(page);await openStudentNutrition(page);
    const before=await page.evaluate(async()=>{const c=__fjzNutritionContextV22();const {count,error}=await c.supabase.from('nutrition_logs').select('id',{count:'exact',head:true}).eq('athlete_id',c.athleteId);if(error)throw error;return count||0});
    await page.evaluate(()=>{const p=__fjzNutritionContextV22().cache.plan.plan,m=p.meals.find(x=>x.id==='meal_qa_breakfast');if(!m.options.some(x=>x.id==='opt_qa_ux'))m.options.push({id:'opt_qa_ux',name:'Opción QA UX',items:[{id:'item_qa_ux',name:'QA Tostadas UX',grams:60,kcal:150,protein_g:6,carbs_g:28,fat_g:2,measure_type:'units',quantity:2,unit_name:'tostadas'}]});TeamFJZNutritionPremium.renderStudent()});
    const meal=page.locator('.fjz4a-meal',{hasText:'Desayuno'}),tab=meal.getByRole('tab',{name:'Opción QA UX'});
    await tab.click();await expect(tab).toHaveAttribute('aria-selected','true');await expect(meal.locator('.meal-option-student:visible')).toContainText('QA Tostadas UX');
    const after=await page.evaluate(async()=>{const c=__fjzNutritionContextV22();const {count,error}=await c.supabase.from('nutrition_logs').select('id',{count:'exact',head:true}).eq('athlete_id',c.athleteId);if(error)throw error;return count||0});
    expect(after).toBe(before);
    const dims=await page.evaluate(()=>({w:innerWidth,macro:[...document.querySelectorAll('.fjz4a-macros')].filter(x=>x.getClientRects().length).map(x=>({sw:x.scrollWidth,cw:x.clientWidth,text:x.textContent.trim().slice(0,80)})),touch:[...document.querySelectorAll('.fjz4a-option-tabs button,.fjz4a-register')].filter(x=>x.getClientRects().length).map(x=>({h:x.getBoundingClientRect().height,text:x.textContent.trim(),cls:x.className,display:getComputedStyle(x).display,minHeight:getComputedStyle(x).minHeight,transform:getComputedStyle(x).transform}))}));
    const macroOverflow=dims.macro.filter(x=>x.sw>x.cw+2),touchMin=dims.w<=620?44:40,touchTooSmall=dims.touch.filter(x=>x.h<touchMin);
    expect(macroOverflow,'macro geometry '+JSON.stringify(dims.macro)).toEqual([]);expect(dims.touch.length).toBeGreaterThan(0);expect(touchTooSmall,'touch geometry '+JSON.stringify(dims.touch)).toEqual([]);await noOverflow(page);
  });

  test('V22 4A-UX Coach: editor principal entra en primer viewport y no duplica cabeceras',async({page})=>{
    await login(page,'coach@test.local');await openAthlete(page);await openCoachNutrition(page);
    const geo=await page.evaluate(()=>{
      const meal=document.querySelector('.fjz4a-meal-editor'),settings=document.querySelector('.fjz4a-plan-settings'),save=document.querySelector('.fjz4a-coach-save'),title=document.querySelector('.fjz3b-section-title'),ctx=document.querySelector('#fjz3bSectionContext'),workspace=document.querySelector('#v266CoachWorkspace');
      const r=x=>x?x.getBoundingClientRect():null;
      return{w:innerWidth,h:innerHeight,meal:r(meal),settings:r(settings),savePosition:save?getComputedStyle(save).position:null,titleDisplay:title?getComputedStyle(title).display:null,ctxDisplay:ctx?getComputedStyle(ctx).display:null,workspaceDisplay:workspace?getComputedStyle(workspace).display:null};
    });
    expect(geo.meal.top).toBeLessThan(geo.h);
    expect(geo.titleDisplay).toBe('none');expect(geo.ctxDisplay).toBe('none');
    if(geo.workspaceDisplay!==null)expect(geo.workspaceDisplay).toBe('none');
    if(geo.w>=901){expect(geo.meal.left).toBeLessThan(geo.settings.left)}else{expect(['fixed','sticky']).not.toContain(geo.savePosition)}
    await expect(page.locator('.fjz4a-coach-head')).toContainText('EDITOR NUTRICIONAL');await noOverflow(page);
  });

  test('V22 4A-UX Coach mobile: comidas y edición táctil antes de prescripción general',async({page})=>{
    await login(page,'coach@test.local');await openAthlete(page);await openCoachNutrition(page);
    const g=await page.evaluate(()=>{
      const meal=document.querySelector('.fjz4a-meal-editor')?.getBoundingClientRect(),settings=document.querySelector('.fjz4a-plan-settings')?.getBoundingClientRect();
      const nav=[...document.querySelectorAll('.fjz4a-editor-rail nav>button')].map(x=>x.getBoundingClientRect().height);
      return{w:innerWidth,h:innerHeight,mealTop:meal?.top,settingsTop:settings?.top,nav};
    });
    if(g.w<=620){expect(g.mealTop).toBeLessThan(g.h);expect(g.mealTop).toBeLessThan(g.settingsTop);expect(g.nav.every(x=>x>=44)).toBeTruthy()}
    await noOverflow(page);
  });

  test('V22 4A-UX conserva guardado confirmado, error recuperable y refresh',async({page})=>{
    await login(page,'coach@test.local');await openAthlete(page);await openCoachNutrition(page);
    const notes=page.locator('#nutNotes'),original=await notes.inputValue();await notes.fill(original+' · UX QA');await expect(page.locator('#fjz4aSaveState')).toContainText(/Cambios pendientes/i);
    await page.route('**/rest/v1/nutrition_plans*',r=>r.request().method()==='PATCH'?r.abort('failed'):r.continue());await page.getByRole('button',{name:'Guardar cambios'}).click();await expect(page.locator('#fjz4aSaveState')).toContainText(/Error al guardar/i,{timeout:15000});
    await page.unroute('**/rest/v1/nutrition_plans*');await notes.fill(original);await page.getByRole('button',{name:'Guardar cambios'}).click();await expect(page.locator('#modal')).toContainText(/Plan nutricional guardado/i,{timeout:15000});const close=page.locator('#modal').getByRole('button',{name:/Listo|Cerrar/i}).first();if(await close.count())await close.click();
    await page.reload();await expect(page.locator('.fjz4a-coach-shell')).toBeVisible({timeout:20000});await expect(page.locator('#fjz4aSaveState')).toContainText(/Guardado/i);await noOverflow(page);
  });

  test('V22 4A-UX mantiene aislamiento A/B e historial nutricional',async({page})=>{
    await login(page,'coach@test.local');await openAthlete(page,'TEST ALUMNO 01');await openCoachNutrition(page);await expect(page.locator('.fjz4a-coach-shell')).toContainText('PLAN QA A');
    await expect(page.locator('.fjz4a-consumption')).toBeVisible();await page.locator('[data-3b-action="back"]').first().click();await openAthlete(page,'TEST ALUMNO 02');await openCoachNutrition(page);await expect(page.locator('.fjz4a-coach-shell')).toContainText('PLAN QA B');await expect(page.locator('.fjz4a-coach-shell')).not.toContainText('PLAN QA A');await noOverflow(page);
  });
});
