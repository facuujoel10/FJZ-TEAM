const {test,expect}=require('@playwright/test');
const PASSWORD='TEAMFJZ-Local-Only!22';
async function login(page,email='coach@test.local'){await page.goto('/');const gate=page.locator('#authGate');if(await gate.isVisible().catch(()=>false)){await page.locator('#authEmail').fill(email);await page.locator('#authPass').fill(PASSWORD);await page.locator('#authGate .btn.primary').click()}await expect(gate).toBeHidden({timeout:20000});if(email==='coach@test.local')await expect(page.locator('.fjz3a-command-center')).toBeVisible({timeout:20000})}
async function openAthlete(page,name='TEST ALUMNO 01'){const search=page.locator('#fjz3aStudentSearch');if(await search.count())await search.fill(name.replace('TEST ',''));const row=page.locator('#studentList .student-row',{hasText:name}).first();await expect(row).toBeVisible({timeout:15000});await row.getByRole('button',{name:/Abrir/i}).click();await expect(page.locator('.fjz3b-header')).toBeVisible({timeout:15000});await expect(page.locator('.fjz3b-header-context strong').first()).not.toHaveText('Consultando…',{timeout:20000})}
async function section(page,key){const b=page.locator('.fjz3b-nav button[data-section="'+key+'"]');await b.click();await expect(b).toHaveAttribute('aria-current','page')}
async function noOverflow(page){const x=await page.evaluate(()=>({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth}));expect(x.sw).toBeLessThanOrEqual(x.cw+2)}
test.describe('V22 3C-UX final Coach experience polish',()=>{
 test('V22 3C-UX Athlete 360 hierarchy keeps identity, decision and pending evidence immediately accessible',async({page})=>{
   await login(page);await openAthlete(page);
   const header=page.locator('.fjz3b-header'),decision=page.locator('.fjz3b-action-card'),priority=page.locator('#fjz3cPriorityHost');
   await expect(header).toContainText('TEST ALUMNO 01');await expect(decision).toBeVisible();await expect(priority).toContainText(/Qué revisar primero/i);
   const boxes=await page.evaluate(()=>{const q=s=>document.querySelector(s)?.getBoundingClientRect();const h=q('.fjz3b-header'),d=q('.fjz3b-action-card'),p=q('#fjz3cPriorityHost');return{h:h&&{top:h.top,bottom:h.bottom},d:d&&{top:d.top,bottom:d.bottom},p:p&&{top:p.top,bottom:p.bottom},vh:innerHeight}});
   expect(boxes.h.top).toBeLessThan(boxes.d.top);expect(boxes.d.top).toBeLessThan(boxes.p.top);expect(boxes.p.top).toBeLessThan(boxes.vh);
   await noOverflow(page);
 });
 test('V22 3C-UX section navigation is single, touchable and does not duplicate legacy navigation',async({page})=>{
   await login(page);await openAthlete(page);
   await expect(page.locator('.fjz3b-nav')).toHaveCount(1);await expect(page.locator('#bottomNav:visible')).toHaveCount(0);await expect(page.locator('.fjz3a-command-center:visible')).toHaveCount(0);
   const sizes=await page.locator('.fjz3b-nav button').evaluateAll(bs=>bs.map(b=>({w:b.getBoundingClientRect().width,h:b.getBoundingClientRect().height})));
   expect(sizes.every(x=>x.h>=44&&x.w>=44)).toBeTruthy();
   for(const key of ['training','progress','checkins','agenda']){await section(page,key);await expect(page.locator('.fjz3b-section-title')).toBeVisible();await noOverflow(page)}
 });
 test('V22 3C-UX analytics expose exact values, date and source without chart overflow',async({page})=>{
   await login(page);await openAthlete(page);await section(page,'progress');
   const progress=page.locator('#fjz3cMeasurementsHost');await expect(progress).toContainText('71.8 kg');await expect(progress.locator('time').first()).toBeVisible();await expect(progress.locator('.fjz3c-spark')).toHaveCount(1);
   const geo=await progress.locator('.fjz3c-spark').first().evaluate(el=>({w:el.getBoundingClientRect().width,pw:el.parentElement.getBoundingClientRect().width}));expect(geo.w).toBeLessThanOrEqual(geo.pw+1);
   await section(page,'training');const training=page.locator('#fjz3cTrainingHost');await expect(training).toContainText(/17\.5 kg × 10/);await expect(training.getByRole('button',{name:/Ver sesión fuente/i}).first()).toBeVisible();
   await section(page,'checkins');const check=page.locator('#fjz3cCheckinsHost');await expect(check).toContainText(/Sueño/);await expect(check.locator('time').first()).toBeVisible();await noOverflow(page);
 });
 test('V22 3C-UX mobile secondary check-in charts are reduced to one primary visualization',async({page},testInfo)=>{
   test.skip(!testInfo.project.name.startsWith('mobile-'),'mobile-only hierarchy');
   await login(page);await openAthlete(page);await section(page,'checkins');
   const visible=await page.locator('#fjz3cCheckinsHost .fjz3c-spark').evaluateAll(xs=>xs.filter(x=>getComputedStyle(x).display!=='none'&&x.getBoundingClientRect().width>0).length);
   expect(visible).toBeLessThanOrEqual(1);await noOverflow(page);
 });
 test('V22 3C-UX exact comment modal and return path remain functional',async({page})=>{
   await login(page);await openAthlete(page);const c=page.locator('.fjz3b-comment',{hasText:'Molestia ficticia exacta 3B'});await expect(c).toBeVisible({timeout:15000});
   await c.getByRole('button',{name:/Abrir ejercicio/i}).click();await expect(page.locator('#modal')).toBeVisible({timeout:15000});await expect(page.locator('#modal')).toContainText(/Press QA|Molestia ficticia exacta 3B/);
   await page.keyboard.press('Escape').catch(()=>{});await noOverflow(page);
 });
 test('V22 3C-UX athlete switch and refresh preserve isolated context',async({page})=>{
   await login(page);await openAthlete(page,'TEST ALUMNO 01');await section(page,'progress');await expect(page.locator('#fjz3cMeasurementsHost')).toContainText('71.8 kg');
   await page.locator('[data-3b-action="back"]').first().click();await openAthlete(page,'TEST ALUMNO 02');await section(page,'progress');await expect(page.locator('#fjz3cMeasurementsHost')).toContainText('64.8 kg');await expect(page.locator('#fjz3cMeasurementsHost')).not.toContainText('71.8 kg');
   await page.reload();await expect(page.locator('.fjz3b-header')).toContainText('TEST ALUMNO 02',{timeout:20000});await expect(page.locator('#fjz3cMeasurementsHost')).toContainText('64.8 kg',{timeout:20000});await noOverflow(page);
 });
});
