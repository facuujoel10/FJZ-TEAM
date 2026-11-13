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
   await expect(page.locator('.fjz3b-header')).toHaveCount(1);await expect(page.locator('.fjz3b-layout')).toHaveCount(1);await expect(page.locator('#coachStudentBody')).toHaveCount(1);await expect(page.locator('#fjz3cPriorityHost')).toHaveCount(1);
   const boxes=await page.evaluate(()=>{
     const rect=s=>{const el=document.querySelector(s);if(!el)return null;const r=el.getBoundingClientRect(),cs=getComputedStyle(el);return{top:r.top,bottom:r.bottom,left:r.left,width:r.width,height:r.height,display:cs.display,position:cs.position,marginTop:cs.marginTop,marginBottom:cs.marginBottom,paddingTop:cs.paddingTop,paddingBottom:cs.paddingBottom,transform:cs.transform}};
     const view=document.querySelector('#view');
     return{scrollY,scrollX,docH:document.documentElement.scrollHeight,bodyH:document.body.scrollHeight,vh:innerHeight,
       view:rect('#view'),header:rect('.fjz3b-header'),hero:rect('.fjz3b-legacy-hero'),layout:rect('.fjz3b-layout'),nav:rect('.fjz3b-nav-wrap'),main:rect('.fjz3b-main'),title:rect('.fjz3b-section-title'),body:rect('#coachStudentBody'),summary:rect('#fjz3bSummary'),decision:rect('#fjz3bSummary > .fjz3b-action-card'),priority:rect('#fjz3bSummary > #fjz3cPriorityHost'),
       viewChildren:view?[...view.children].map(el=>{const r=el.getBoundingClientRect(),cs=getComputedStyle(el);return{tag:el.tagName,id:el.id,cls:el.className,top:r.top,height:r.height,display:cs.display,position:cs.position}}):[]};
   });
   console.log('FJZ3CUX_GEOMETRY '+JSON.stringify(boxes));
   expect(boxes.header.top).toBeLessThan(boxes.decision.top);expect(boxes.decision.top).toBeLessThan(boxes.priority.top);expect(boxes.priority.top).toBeLessThan(boxes.vh);
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
