const {test,expect}=require('@playwright/test');
const fs=require('fs');
const common=fs.readFileSync('scripts/dev_common.py','utf8');
const passwordMatch=common.match(/TEST_PASSWORD="([^"]+)"/);
if(!passwordMatch)throw new Error('No se encontró TEST_PASSWORD local.');
const PASSWORD=passwordMatch[1];
const PROD_REF='cujipwacwwpejhqjhnkr';

function isProductionBackend(url){
  try{const u=new URL(url);return u.hostname.endsWith('.supabase.co')||url.includes(PROD_REF)}
  catch(_){return String(url||'').includes(PROD_REF)}
}
async function safety(page){
  const state={prod:[],pageErrors:[],consoleErrors:[],http:[]};
  await page.route('**/*',async route=>{
    const url=route.request().url();
    if(isProductionBackend(url)){state.prod.push(url);await route.abort('blockedbyclient');return}
    await route.continue();
  });
  await page.routeWebSocket(/.*/,ws=>{
    if(isProductionBackend(ws.url())){state.prod.push(ws.url());ws.close();return}
    ws.connectToServer();
  });
  page.on('pageerror',e=>state.pageErrors.push(String(e?.message||e)));
  page.on('console',m=>{if(m.type()==='error')state.consoleErrors.push(m.text())});
  page.on('response',r=>{if(r.status()>=400&&/127\.0\.0\.1|localhost/.test(r.url()))state.http.push({status:r.status(),url:r.url()})});
  return state;
}
async function login(page,email){
  await page.goto('/');
  await expect(page.locator('#authEmail')).toBeVisible();
  await page.locator('#authEmail').fill(email);
  await page.locator('#authPass').fill(PASSWORD);
  await page.locator('#authGate .btn.primary').click();
  await expect(page.locator('#authGate')).toBeHidden({timeout:20000});
}
async function logout(page){
  let b=page.getByRole('button',{name:/Cerrar sesión/i}).first();
  if(!(await b.isVisible().catch(()=>false))){
    const cloud=page.locator('#cloudStatusBtn');
    if(await cloud.isVisible().catch(()=>false)){await cloud.click();b=page.locator('#modal').getByRole('button',{name:/Cerrar sesión/i}).first()}
  }
  await expect(b).toBeVisible({timeout:10000});await b.click();await expect(page.locator('#authEmail')).toBeVisible({timeout:10000});
}
async function rootSession(page){
  await page.goto('/');
  await expect(page.locator('#authGate')).toBeHidden({timeout:15000});
}
async function noOverflow(page){
  const d=await page.evaluate(()=>({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth}));
  expect(d.sw).toBeLessThanOrEqual(d.cw+2);
}
async function section(page,key){
  const b=page.locator('.fjz3b-nav button[data-section="'+key+'"]');
  await expect(b).toBeVisible({timeout:10000});await b.click();await expect(b).toHaveAttribute('aria-current','page');
}
async function coachNavigationSnapshot(page,label,testInfo){
  const snap=await page.evaluate(()=>{
    const visible=el=>!!el&&getComputedStyle(el).display!=='none'&&getComputedStyle(el).visibility!=='hidden'&&el.getBoundingClientRect().width>0&&el.getBoundingClientRect().height>0;
    let route=null;try{route=JSON.parse(sessionStorage.getItem('team-fjz-v22-athlete360-route')||'null')}catch(_e){}
    const command=document.querySelector('.fjz3a-command-center'),athlete=document.querySelector('.fjz3b-header'),back=document.querySelector('[data-3b-action="back"]');
    return {
      role:currentProfile?.role||null,
      mode:typeof mode==='undefined'?null:mode,
      coachTab:typeof coachTab==='undefined'?null:coachTab,
      coachStudentTab:typeof coachStudentTab==='undefined'?null:coachStudentTab,
      selectedStudentId:state?.selectedStudentId||null,
      route,
      athlete360:window.__fjzAthlete360StateV22?{
        studentId:window.__fjzAthlete360StateV22.studentId||null,
        athleteId:window.__fjzAthlete360StateV22.athleteId||null,
        sectionOverride:window.__fjzAthlete360StateV22.sectionOverride||null,
        loading:!!window.__fjzAthlete360StateV22.loading,
        loadedAthleteId:window.__fjzAthlete360StateV22.loadedAthleteId||null
      }:null,
      commandCenter:{exists:!!command,visible:visible(command),loading:!!window.__fjzCoachCommandCenterStateV22?.loading},
      athleteHeader:{exists:!!athlete,visible:visible(athlete)},
      backVisible:visible(back),
      bottomNavClass:document.getElementById('bottomNav')?.className||'',
      renderType:typeof render
    };
  });
  console.log('STAGE5_COACH_NAV '+label+' '+JSON.stringify(snap));
  if(testInfo){
    fs.mkdirSync('artifacts/stage5',{recursive:true});
    const suffix=testInfo.project.name+'-'+label.replace(/[^a-z0-9_-]+/gi,'-');
    fs.writeFileSync('artifacts/stage5/coach-nav-'+suffix+'.json',JSON.stringify(snap,null,2));
    const viewHtml=await page.locator('#view').evaluate(el=>el.outerHTML).catch(()=>'<div id="view" data-missing="true"></div>');
    fs.writeFileSync('artifacts/stage5/coach-nav-'+suffix+'.html',viewHtml);
    await page.screenshot({path:'artifacts/stage5/coach-nav-'+suffix+'.png',fullPage:true});
  }
  return snap;
}
async function ensureCoachCommandCenter(page,testInfo,label='return'){
  if(await page.locator('.fjz3a-command-center').isVisible().catch(()=>false))return true;
  const before=await coachNavigationSnapshot(page,label+'-before',testInfo);
  const back=page.locator('[data-3b-action="back"]').first();
  if(await back.isVisible().catch(()=>false)){
    expect(before.role).toBe('coach');
    expect(before.route?.studentId||'').not.toBe('');
    await back.click();
  }else{
    const studentsNav=page.locator('#bottomNav').getByRole('button',{name:'Alumnos',exact:true}).first();
    await expect(studentsNav).toBeVisible({timeout:10000});
    await studentsNav.click();
  }
  await expect(page.locator('.fjz3a-command-center')).toBeVisible({timeout:15000});
  await expect.poll(
    ()=>page.evaluate(()=>window.__fjzCoachCommandCenterStateV22?window.__fjzCoachCommandCenterStateV22.loading===false:true),
    {timeout:20000,message:'Command Center debe terminar su hidratación antes de abrir otro alumno'}
  ).toBeTruthy();
  const sync=page.locator('.fjz3a-sync span').first();
  if(await sync.count())await expect(sync).toContainText(/Actualizado/i,{timeout:20000});
  await coachNavigationSnapshot(page,label+'-after',testInfo);
  return true;
}
async function openAthlete(page,name,testInfo){
  await ensureCoachCommandCenter(page,testInfo,'open-'+name.replace(/\s+/g,'-'));
  const search=page.locator('#fjz3aStudentSearch');if(await search.count())await search.fill(name.replace('TEST ',''));
  const row=page.locator('#studentList .student-row',{hasText:name}).first();
  await expect(row).toBeVisible({timeout:15000});
  const open=row.getByRole('button',{name:/Abrir/i}).first();
  await expect(open).toBeVisible({timeout:15000});
  await expect(open).toBeEnabled({timeout:15000});
  await open.click();
  await expect(page.locator('.fjz3b-header')).toContainText(name,{timeout:20000});
}
async function closeModal(page){
  if(await page.locator('#modal').isVisible().catch(()=>false)){
    const b=page.locator('#modal').getByRole('button',{name:/Listo|Cerrar|✕/}).first();
    if(await b.count())await b.click();else await page.keyboard.press('Escape');
  }
}
async function timed(metrics,label,fn){
  const start=Date.now();const out=await fn();metrics[label]=Date.now()-start;return out;
}

test.describe('V22 Stage5 integral certification',()=>{
  test.setTimeout(150000);

  test('V22 Stage5 Coach: navegación visible A → Command Center → B conserva identidad, aislamiento y refresh',async({page},testInfo)=>{
    const state=await safety(page);
    await login(page,'coach@test.local');
    await ensureCoachCommandCenter(page,testInfo,'regression-login');

    await openAthlete(page,'TEST ALUMNO 01',testInfo);
    await section(page,'nutrition');
    await section(page,'progress');
    await section(page,'checkins');
    await section(page,'agenda');
    await page.locator('[data-3b-action="back"]').first().click();
    await expect(page.locator('.fjz3a-command-center')).toBeVisible({timeout:15000});

    await openAthlete(page,'TEST ALUMNO 02',testInfo);
    await expect(page.locator('.fjz3b-header')).toContainText('TEST ALUMNO 02');
    await expect(page.locator('.fjz3b-header')).not.toContainText('TEST ALUMNO 01');
    expect(await page.evaluate(()=>window.__fjzAthlete360StateV22?.athleteId)).toBe('10000000-0000-4000-8000-000000000002');
    await section(page,'agenda');
    await section(page,'checkins');
    await page.locator('[data-3b-action="back"]').first().click();
    await expect(page.locator('.fjz3a-command-center')).toBeVisible({timeout:15000});

    await page.reload();
    await expect(page.locator('#authGate')).toBeHidden({timeout:15000});
    await expect(page.locator('.fjz3a-command-center')).toBeVisible({timeout:15000});
    await noOverflow(page);
    expect(state.prod).toEqual([]);
    expect(state.pageErrors).toEqual([]);
    console.log('E2E_FLOW_OK V22 Stage5 Coach navigation '+testInfo.project.name);
  });

  test('V22 Stage5 recorrido integral Alumno → Coach con persistencia, A/B y reingreso',async({page},testInfo)=>{
    const state=await safety(page);
    const metrics={};
    const comment='STAGE5 '+testInfo.project.name+' · comentario exacto';
    const checkNotes='STAGE5 '+testInfo.project.name+' · check-in integral';
    const coachFeedback='STAGE5 '+testInfo.project.name+' · devolución coach';
    const reminderTitle='STAGE5 '+testInfo.project.name+' · seguimiento';
    const measureDate='2026-12-30';
    const checkWeek='2026-12-28';
    let mealGroup=null,reminderId=null,sessionId=null,originalTitle=null;

    await timed(metrics,'student_login_ms',()=>login(page,'alumno01@test.local'));
    await expect(page.getByText('TEST ALUMNO 01',{exact:true}).filter({visible:true}).first()).toBeVisible();

    await timed(metrics,'workout_open_ms',async()=>{
      await page.getByRole('button',{name:'Entrenar'}).first().click();
      await expect(page.getByRole('heading',{name:'Día QA A'})).toBeVisible();
    });
    const rest=page.locator('.v22c-rest-control').first();
    await expect(rest).toBeVisible();
    await rest.locator('button[data-rest-action="start"]').click();
    await expect(rest).toHaveAttribute('data-timer-state','running');
    await rest.getByRole('button',{name:'Pausar'}).click();
    await rest.getByRole('button',{name:'Reanudar'}).click();
    await rest.getByRole('button',{name:'Omitir'}).click();

    const sets=page.locator('.set-grid');
    for(let i=0;i<await sets.count();i++){
      const inputs=sets.nth(i).locator('input');
      await inputs.nth(0).fill(i<3?'32.5':'35.5');
      await inputs.nth(1).fill(i%2?'9':'10');
      await inputs.nth(2).fill('1.5');
    }
    const firstCard=page.locator('.session-card').first();
    await firstCard.getByRole('button',{name:/Comentario/i}).click();
    await page.locator('#v73FeedbackMessage').fill(comment);
    await page.getByRole('button',{name:/Enviar al coach/i}).click();
    await expect(firstCard).toContainText(/Comentario enviado/i);

    await timed(metrics,'workout_confirm_ms',async()=>{
      await page.getByRole('button',{name:/Finalizar sesión/i}).click();
      const fb=page.getByRole('heading',{name:/¿Cómo salió la sesión\?/i});
      if(await fb.count())await page.getByRole('button',{name:/Todo bien · finalizar/i}).click();
      await expect(page.locator('#modal')).toContainText(/Sesión guardada|Entrenamiento completado/i,{timeout:20000});
    });
    const save=await page.evaluate(()=>window.__fjzSessionSaveStateV207?.());
    expect(save?.cloudConfirmed).toBeTruthy();sessionId=save.sessionId;
    const serverSession=await page.evaluate(async sid=>{
      const {data,error}=await supabaseClient.from('workout_sessions').select('source_session_id,status').eq('source_session_id',sid).single();
      if(error)throw error;return data;
    },sessionId);
    expect(serverSession.status).toBe('completed');
    const historyBtn=page.locator('#modal .v22-history-after-save');
    await expect(historyBtn).toBeVisible();await historyBtn.click();
    await expect(page.getByText('Día QA A',{exact:false}).first()).toBeVisible({timeout:10000});

    await rootSession(page);
    await timed(metrics,'nutrition_open_ms',async()=>{
      await page.getByRole('button',{name:'Nutrición',exact:true}).first().click();
      await expect(page.locator('.fjz4a-student-shell')).toBeVisible({timeout:20000});
    });
    const logsBefore=await page.evaluate(async()=>{
      const c=__fjzNutritionContextV22();const {data,error}=await c.supabase.from('nutrition_logs').select('id').eq('athlete_id',c.athleteId);
      if(error)throw error;return data.length;
    });
    await page.evaluate(()=>{
      const p=__fjzNutritionContextV22().cache.plan.plan;
      const m=p.meals.find(x=>x.id==='meal_qa_breakfast');
      if(m&&!m.options.some(x=>x.id==='stage5_alt'))m.options.push({id:'stage5_alt',name:'Alternativa Stage5',items:[{id:'stage5_alt_item',name:'Alternativa visual',grams:50,kcal:120,protein_g:5,carbs_g:20,fat_g:2}]});
      TeamFJZNutritionPremium.renderStudent();
    });
    const breakfast=page.locator('.fjz4a-meal',{hasText:'Desayuno'});
    const alt=breakfast.locator('[role="tab"]',{hasText:'Alternativa Stage5'});
    await expect(alt).toBeVisible();await alt.click();
    const logsAfterAlt=await page.evaluate(async()=>{
      const c=__fjzNutritionContextV22();const {data,error}=await c.supabase.from('nutrition_logs').select('id').eq('athlete_id',c.athleteId);
      if(error)throw error;return data.length;
    });
    expect(logsAfterAlt).toBe(logsBefore);

    const lunch=page.locator('.fjz4a-meal',{hasText:'Almuerzo'});
    await lunch.locator('.meal-option-student',{hasText:'Opción QA 2'}).getByRole('button',{name:/Registrar hoy/i}).click();
    await expect(page.locator('#v264QuickSaved')).toContainText(/Opción registrada/i,{timeout:15000});
    mealGroup=await page.evaluate(async()=>{
      const c=__fjzNutritionContextV22();const {data,error}=await c.supabase.from('nutrition_logs')
        .select('meal_group_id,note,created_at').eq('athlete_id',c.athleteId).like('note','FJZ4A_OPTION:%opt_qa_2%')
        .order('created_at',{ascending:false}).limit(1);
      if(error)throw error;return data?.[0]?.meal_group_id||null;
    });
    expect(mealGroup).toBeTruthy();

    await rootSession(page);
    await timed(metrics,'progress_open_ms',async()=>{
      await page.getByRole('button',{name:'Check-in',exact:true}).first().click();
      await expect(page.locator('.fjz4b-shell')).toBeVisible({timeout:20000});
    });
    await page.locator('#mDate').fill(measureDate);
    await page.locator('#mWeight').fill('73.9');
    await page.locator('#mArmL').fill('33.4');
    await page.locator('[data-4b-action="save-measure"]').click();
    await expect(page.locator('#modal')).toContainText(/Medición guardada/i,{timeout:15000});
    await closeModal(page);

    await page.locator('[data-4b-view="checkins"]').click();
    await page.locator('#ciWeek').fill(checkWeek);
    await page.locator('#ciWeight').fill('73.9');
    await page.locator('#ciNotes').fill(checkNotes);
    await page.locator('[data-4b-action="save-checkin"]').click();
    await expect(page.locator('#v170CheckinStatus')).toContainText(/guardado correctamente/i,{timeout:15000});
    const persisted=await page.evaluate(async ({measureDate,checkWeek})=>{
      const c=__fjzProgressCheckinsContextV22();
      const [m,q]=await Promise.all([
        c.supabase.from('body_measurements').select('id,weight_kg,arm_left_cm').eq('athlete_id',c.athleteId).eq('measured_on',measureDate).single(),
        c.supabase.from('weekly_checkins').select('id,notes,week_start').eq('athlete_id',c.athleteId).eq('week_start',checkWeek).single()
      ]);
      if(m.error)throw m.error;if(q.error)throw q.error;
      return {m:m.data,q:q.data};
    },{measureDate,checkWeek});
    expect(Number(persisted.m.weight_kg)).toBe(73.9);expect(persisted.q.notes).toBe(checkNotes);

    await rootSession(page);
    await timed(metrics,'agenda_open_ms',async()=>{
      await page.getByRole('button',{name:'Agenda',exact:true}).first().click();
      await expect(page.locator('.fjz4c-student')).toBeVisible({timeout:20000});
    });
    await noOverflow(page);
    fs.mkdirSync('artifacts/stage5',{recursive:true});
    await page.screenshot({path:'artifacts/stage5/student-integral-'+testInfo.project.name+'.png',fullPage:true});

    await page.reload();await expect(page.locator('#authGate')).toBeHidden({timeout:15000});
    await logout(page);await login(page,'alumno01@test.local');
    const reentry=await page.evaluate(async ({sessionId,mealGroup,measureDate,checkWeek})=>{
      const athlete=(await supabaseClient.from('athletes').select('id').eq('user_id',currentUser.id).single()).data;
      const [s,n,m,c]=await Promise.all([
        supabaseClient.from('workout_sessions').select('id').eq('source_session_id',sessionId),
        supabaseClient.from('nutrition_logs').select('id').eq('athlete_id',athlete.id).eq('meal_group_id',mealGroup),
        supabaseClient.from('body_measurements').select('id').eq('athlete_id',athlete.id).eq('measured_on',measureDate),
        supabaseClient.from('weekly_checkins').select('id').eq('athlete_id',athlete.id).eq('week_start',checkWeek)
      ]);
      return {s:s.data?.length||0,n:n.data?.length||0,m:m.data?.length||0,c:c.data?.length||0};
    },{sessionId,mealGroup,measureDate,checkWeek});
    expect(reentry.s).toBe(1);expect(reentry.n).toBeGreaterThan(0);expect(reentry.m).toBe(1);expect(reentry.c).toBe(1);

    await logout(page);
    await timed(metrics,'coach_login_ms',()=>login(page,'coach@test.local'));
    await expect(page.locator('.fjz3a-command-center')).toBeVisible({timeout:20000});
    await expect(page.locator('.fjz3a-sync span')).toContainText(/Actualizado/i,{timeout:20000});
    const groupWithComment=page.locator('.fjz3a-group').filter({hasText:comment}).first();
    await expect(groupWithComment).toBeVisible({timeout:20000});
    const groupToggle=groupWithComment.locator('.fjz3a-group-head').first();
    const groupBody=groupWithComment.locator('.fjz3a-group-body').first();
    if((await groupToggle.getAttribute('aria-expanded'))!=='true')await groupToggle.click();
    await expect(groupToggle).toHaveAttribute('aria-expanded','true',{timeout:5000});
    await expect(groupBody).toBeVisible({timeout:5000});
    const commentNode=groupBody.getByText(comment,{exact:true}).first();
    await expect(commentNode).toBeVisible({timeout:10000});
    const container=commentNode.locator('xpath=ancestor::*[self::article or contains(@class,"card") or contains(@class,"feedback-item")][1]');
    const open=container.getByRole('button',{name:/Abrir|Ver/i}).first();await expect(open).toBeVisible();await open.click();
    const exact=page.getByText(comment,{exact:true}).first();await expect(exact).toBeVisible({timeout:10000});
    const review=exact.locator('xpath=ancestor::*[contains(concat(" ", normalize-space(@class), " "), " v287-exercise-comment ")][1]');
    await review.getByRole('button',{name:/OK|Marcar revisado/i}).click();
    await expect(review.getByText('Revisado',{exact:true})).toBeVisible({timeout:15000});
    await closeModal(page);

    await logout(page);
    await login(page,'coach@test.local');
    await openAthlete(page,'TEST ALUMNO 01',testInfo);

    await section(page,'training');await noOverflow(page);
    await section(page,'nutrition');
    originalTitle=await page.locator('#nutTitle').inputValue();
    await page.locator('#nutTitle').fill(originalTitle+' · Stage5');
    await page.getByRole('button',{name:'Guardar cambios'}).click();
    await expect(page.locator('#modal')).toContainText(/Plan nutricional guardado/i,{timeout:15000});
    await closeModal(page);
    const edited=await page.evaluate(async()=>{
      const a=__fjzAthlete360StateV22.athleteId;
      const {data,error}=await supabaseClient.from('nutrition_plans').select('title').eq('athlete_id',a).eq('active',true).single();
      if(error)throw error;return data.title;
    });
    expect(edited).toContain('Stage5');
    await page.locator('#nutTitle').fill(originalTitle);
    await page.getByRole('button',{name:'Guardar cambios'}).click();
    await expect(page.locator('#modal')).toContainText(/Plan nutricional guardado/i,{timeout:15000});
    await closeModal(page);

    await section(page,'progress');
    await expect(page.locator('.fjz4b-progress')).toBeVisible({timeout:20000});
    await expect(page.locator('.fjz3b-measure-list')).toContainText('73.9',{timeout:20000});
    await section(page,'checkins');
    const checkCard=page.locator('.fjz4b-check-card',{hasText:checkNotes}).first();
    await expect(checkCard).toBeVisible({timeout:15000});
    const feedbackBox=checkCard.locator('textarea').first();
    const feedbackSave=checkCard.getByRole('button',{name:/Guardar devolución/i}).first();
    await expect(feedbackBox).toBeVisible({timeout:15000});
    await expect(feedbackSave).toBeVisible({timeout:15000});
    await feedbackBox.fill(coachFeedback);
    await feedbackSave.click();
    await expect(page.locator('.fjz4b-checkins')).toContainText(coachFeedback,{timeout:15000});

    await section(page,'agenda');
    await expect(page.locator('#fjz4cAddReminder')).toBeVisible({timeout:15000});
    await page.locator('#fjz4cAddReminder').click();
    await expect(page.locator('#modalWrap')).toBeVisible({timeout:10000});
    await expect(page.locator('#v165Title')).toBeVisible({timeout:10000});
    await page.locator('#v165Title').fill(reminderTitle);
    await page.locator('#v165Date').fill('2026-12-31');
    await page.locator('#v165Time').fill('18:15');
    await page.locator('[data-v165-action="save-reminder"]').click();
    await expect(page.locator('#modalWrap')).toBeHidden({timeout:15000});
    reminderId=await page.evaluate(async title=>{
      const a=__fjzAthlete360StateV22.athleteId;
      const {data,error}=await supabaseClient.from('athlete_reminders').select('id').eq('athlete_id',a).eq('title',title).single();
      if(error)throw error;return data.id;
    },reminderTitle);
    expect(reminderId).toBeTruthy();
    await page.screenshot({path:'artifacts/stage5/coach-integral-'+testInfo.project.name+'.png',fullPage:true});

    await page.locator('[data-3b-action="back"]').first().click();
    await expect(page.locator('.fjz3a-command-center')).toBeVisible({timeout:15000});
    await openAthlete(page,'TEST ALUMNO 02',testInfo);
    expect(await page.evaluate(()=>__fjzAthlete360StateV22.athleteId)).toBe('10000000-0000-4000-8000-000000000002');
    await section(page,'agenda');await expect(page.locator('#coachStudentBody')).not.toContainText(reminderTitle);
    await section(page,'checkins');await expect(page.locator('#coachStudentBody')).not.toContainText(checkNotes);

    await logout(page);await login(page,'alumno01@test.local');
    await page.getByRole('button',{name:'Agenda',exact:true}).first().click();
    await expect(page.locator('.fjz4c-student')).toContainText(reminderTitle,{timeout:20000});
    await page.getByRole('button',{name:'Check-in',exact:true}).first().click();
    await page.locator('[data-4b-view="checkins"]').click();
    const finalCard=page.locator('.fjz4b-check-card',{hasText:checkNotes}).first();
    await expect(finalCard).toContainText(coachFeedback,{timeout:15000});

    await logout(page);await login(page,'coach@test.local');await openAthlete(page,'TEST ALUMNO 01',testInfo);
    await page.evaluate(async ({mealGroup,measureDate,checkWeek,reminderId})=>{
      const a=__fjzAthlete360StateV22.athleteId;
      const rs=await Promise.all([
        supabaseClient.from('nutrition_logs').delete().eq('meal_group_id',mealGroup),
        supabaseClient.from('body_measurements').delete().eq('athlete_id',a).eq('measured_on',measureDate),
        supabaseClient.from('weekly_checkins').delete().eq('athlete_id',a).eq('week_start',checkWeek),
        supabaseClient.from('athlete_reminders').delete().eq('id',reminderId)
      ]);
      for(const r of rs)if(r.error)throw r.error;
    },{mealGroup,measureDate,checkWeek,reminderId});

    metrics.total_measured_ms=Object.values(metrics).reduce((a,b)=>a+b,0);
    fs.writeFileSync('artifacts/stage5/performance-'+testInfo.project.name+'.json',JSON.stringify(metrics,null,2));
    await noOverflow(page);
    expect(state.prod).toEqual([]);expect(state.pageErrors).toEqual([]);
    expect(state.http.filter(x=>x.status===404)).toEqual([]);
    console.log('STAGE5_PERF '+testInfo.project.name+' '+JSON.stringify(metrics));
    console.log('E2E_FLOW_OK V22 Stage5 integral '+testInfo.project.name);
  });
});
