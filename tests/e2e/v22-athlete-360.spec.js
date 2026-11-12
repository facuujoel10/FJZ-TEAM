const {test,expect}=require('@playwright/test');
const PASSWORD='TEAMFJZ-Local-Only!22';
async function login(page,email='coach@test.local'){
  await page.goto('/');
  const gate=page.locator('#authGate');
  if(await gate.isVisible().catch(()=>false)){
    await page.locator('#authEmail').fill(email);await page.locator('#authPass').fill(PASSWORD);
    await page.locator('#authGate .btn.primary').click();
  }
  await expect(gate).toBeHidden({timeout:20000});
  if(email==='coach@test.local')await expect(page.locator('.fjz3a-command-center')).toBeVisible({timeout:20000});
}
async function openAthlete(page,name='TEST ALUMNO 01'){
  if(!(await page.locator('.fjz3a-command-center').isVisible().catch(()=>false))){
    await page.evaluate(()=>{coachTab='dashboard';render()});await expect(page.locator('.fjz3a-command-center')).toBeVisible({timeout:15000});
  }
  const search=page.locator('#fjz3aStudentSearch');if(await search.count())await search.fill(name.replace('TEST ',''));
  const row=page.locator('#studentList .student-row',{hasText:name}).first();
  await expect(row).toBeVisible({timeout:15000});await row.getByRole('button',{name:/Abrir/i}).click();
  await expect(page.locator('.fjz3b-header')).toBeVisible({timeout:15000});
  await expect(page.locator('.fjz3b-legacy-hero')).toContainText(name);
  await expect(page.locator('.fjz3b-header-context strong').first()).not.toHaveText('Consultando…',{timeout:20000});
}
async function section(page,key){const b=page.locator('.fjz3b-nav button[data-section="'+key+'"]');await expect(b).toBeVisible();await b.click();await expect(page.locator('.fjz3b-header')).toBeVisible({timeout:15000});await expect(page.locator('.fjz3b-nav button[data-section="'+key+'"]')).toHaveAttribute('aria-current','page')}
async function noOverflow(page){const x=await page.evaluate(()=>({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth}));expect(x.sw).toBeLessThanOrEqual(x.cw+2)}

test.describe('V22 3B Athlete 360 Workspace',()=>{
 test('abre desde Command Center, navega una sola vez y vuelve conservando contexto',async({page},testInfo)=>{
   await login(page);const search=page.locator('#fjz3aStudentSearch');await search.fill('ALUMNO 01');await openAthlete(page);
   await expect(page.getByText('ATHLETE WORKSPACE · TEAM FJZ',{exact:true})).toBeVisible();
   await expect(page.locator('.fjz3b-nav:visible')).toHaveCount(1);await expect(page.locator('#coachStudentTabs:visible')).toHaveCount(0);
   for(const key of ['summary','training','nutrition','progress','checkins','agenda','info']){await section(page,key);await expect(page.locator('#coachStudentBody')).not.toBeEmpty();await noOverflow(page)}
   await page.locator('[data-3b-action="back"]').first().click();await expect(page.locator('.fjz3a-command-center')).toBeVisible({timeout:15000});
   await expect(page.locator('#fjz3aStudentSearch')).toHaveValue('ALUMNO 01');
   console.log('E2E_FLOW_OK V22 3B navigation-context '+testInfo.project.name);
 });

 test('dos alumnos consecutivos mantienen identidad y no contaminan datos',async({page},testInfo)=>{
   await login(page);await openAthlete(page,'TEST ALUMNO 01');
   expect(await page.evaluate(()=>__fjzAthlete360StateV22.studentId)).toBe('dev_student_01');
   await page.locator('[data-3b-action="back"]').first().click();await expect(page.locator('.fjz3a-command-center')).toBeVisible();
   await openAthlete(page,'TEST ALUMNO 02');
   await expect(page.locator('.fjz3b-legacy-hero')).toContainText('TEST ALUMNO 02');
   const state=await page.evaluate(()=>({studentId:__fjzAthlete360StateV22.studentId,athleteId:__fjzAthlete360StateV22.athleteId,comments:__fjzAthlete360StateV22.comments.map(x=>x.athlete_id)}));
   expect(state.studentId).toBe('dev_student_02');expect(state.athleteId).toBe('10000000-0000-4000-8000-000000000002');expect(state.comments.every(x=>x===state.athleteId)).toBeTruthy();
   await expect(page.locator('#coachStudentBody')).not.toContainText('Molestia ficticia exacta 3B');await noOverflow(page);
   console.log('E2E_FLOW_OK V22 3B identity-isolation '+testInfo.project.name);
 });

 test('resumen usa sesión confirmada, PR válido y comentario exacto',async({page},testInfo)=>{
   await login(page);await openAthlete(page);
   await expect(page.locator('#fjz3bSummary')).toContainText('Día QA A',{timeout:20000});
   await expect(page.locator('#fjz3bSummary')).toContainText(/PR válidos/i);
   await expect(page.locator('#fjz3bSummary')).toContainText('Molestia ficticia exacta 3B');
   const state=await page.evaluate(()=>{const s=student();return {confirmed:TeamFJZIntelligentTraining.sessionConfirmed((s.sessions||[]).find(x=>x.id==='dev_session_history_02')),latest:TeamFJZAthlete360.latestConfirmedSession(s.sessions)?.id}});
   expect(state.confirmed).toBeTruthy();expect(state.latest).toBe('dev_session_history_02');
   const exact=page.locator('.fjz3b-comment',{hasText:'Molestia ficticia exacta 3B'});await exact.getByRole('button',{name:/Abrir ejercicio/i}).click();
   await expect(page.locator('#modal')).toBeVisible({timeout:15000});await expect(page.locator('#modal')).toContainText(/Press QA|Molestia ficticia exacta 3B/);
   await noOverflow(page);
   console.log('E2E_FLOW_OK V22 3B exact-comment '+testInfo.project.name);
 });

 test('nutrición, progreso físico, fotos, check-in y agenda reutilizan datos reales',async({page},testInfo)=>{
   await login(page);await openAthlete(page);
   await section(page,'nutrition');await expect(page.locator('#coachStudentBody')).toContainText(/PLAN QA A|QA Yogur ficticio/,{timeout:15000});await noOverflow(page);
   await section(page,'progress');await expect(page.locator('.fjz3b-measure-list')).toContainText(/71\.8 kg|72\.5 kg/);await expect(page.locator('#coachPhotoGrid')).toBeVisible({timeout:15000});await expect(page.locator('#coachPhotoGrid img')).toHaveCount(1,{timeout:15000});await noOverflow(page);
   await section(page,'checkins');await expect(page.locator('#coachStudentBody')).toContainText(/Último check-in|Check-ins semanales/i);await expect(page.locator('#coachStudentBody')).toContainText(/Pendiente|Falta tu devolución/i);await noOverflow(page);
   await section(page,'agenda');await expect(page.locator('#fjz3bSectionContext')).toContainText(/PRÓXIMA FECHA VÁLIDA|Día QA A/i);await expect(page.locator('#fjz3bSectionContext')).not.toContainText('20 ene 2026');await noOverflow(page);
   console.log('E2E_FLOW_OK V22 3B data-sections '+testInfo.project.name);
 });

 test('refresh rehidrata el mismo alumno y alumno normal no accede al workspace Coach',async({page},testInfo)=>{
   await login(page);await openAthlete(page);await section(page,'progress');await page.reload();await expect(page.locator('#authGate')).toBeHidden({timeout:15000});await expect(page.locator('.fjz3b-header')).toContainText('TEST ALUMNO 01',{timeout:20000});expect(await page.evaluate(()=>__fjzAthlete360StateV22.studentId)).toBe('dev_student_01');await noOverflow(page);
   await page.evaluate(()=>supabaseClient.auth.signOut());await page.reload();await login(page,'alumno01@test.local');await expect(page.locator('.fjz3b-header')).toHaveCount(0);await expect(page.locator('.fjz3b-nav')).toHaveCount(0);
   console.log('E2E_FLOW_OK V22 3B refresh-role-guard '+testInfo.project.name);
 });

 test('fallo de lectura es recuperable y no mezcla estado anterior',async({page},testInfo)=>{
   await login(page);
   await page.route('**/rest/v1/exercise_feedback**',route=>route.abort('failed'));
   await openAthlete(page);
   await page.evaluate(()=>window.__fjzHydrateAthlete360V22(true));
   await expect(page.locator('.fjz3b-error')).toBeVisible({timeout:15000});await expect(page.locator('.fjz3b-error')).toContainText(/Reintentar/i);
   await page.unroute('**/rest/v1/exercise_feedback**');await page.locator('.fjz3b-error [data-3b-action="retry"]').click();await expect(page.locator('#fjz3bSummary')).toContainText(/PRÓXIMA DECISIÓN/i,{timeout:20000});await noOverflow(page);
   console.log('E2E_FLOW_OK V22 3B recoverable-error '+testInfo.project.name);
 });

 test('OK de comentario persiste después de refresh sin marcar por apertura',async({page},testInfo)=>{
   await login(page);await openAthlete(page);
   const exact=page.locator('.fjz3b-comment',{hasText:'Molestia ficticia exacta 3B'});await expect(exact).toBeVisible({timeout:15000});
   const statusBefore=await page.evaluate(async()=>{const r=await TeamFJZCommentRepository.createCommentRepository({supabase:supabaseClient}).getById('40000000-0000-4000-8000-000000000002');return r?.row?.status});
   expect(statusBefore).toBe('pending');
   await exact.getByRole('button',{name:'OK',exact:true}).click();await expect(page.locator('.fjz3b-comment',{hasText:'Molestia ficticia exacta 3B'})).toHaveCount(0,{timeout:15000});
   const statusAfter=await page.evaluate(async()=>{const r=await TeamFJZCommentRepository.createCommentRepository({supabase:supabaseClient}).getById('40000000-0000-4000-8000-000000000002');return r?.row?.status});expect(statusAfter).toBe('reviewed');
   await page.reload();await expect(page.locator('.fjz3b-header')).toBeVisible({timeout:20000});await expect(page.locator('#fjz3bSummary')).not.toContainText('Molestia ficticia exacta 3B',{timeout:20000});
   console.log('E2E_FLOW_OK V22 3B durable-comment-ok '+testInfo.project.name);
 });
});
