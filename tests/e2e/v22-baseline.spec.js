const { test, expect } = require('@playwright/test');

const PASSWORD = 'TEAMFJZ-Local-Only!22';
const PROD_REF = 'cujipwacwwpejhqjhnkr';

function isProductionBackend(url) {
  try {
    const u = new URL(url);
    return u.hostname.endsWith('.supabase.co') || url.includes(PROD_REF);
  } catch (_) {
    return String(url || '').includes(PROD_REF);
  }
}

async function installSafety(page, testInfo) {
  const state = { prod: [], http: [], pageErrors: [], consoleErrors: [], websockets: [] };

  // Active HTTP/HTTPS fail-closed barrier. A productive request never leaves Chromium.
  await page.route('**/*', async route => {
    const url = route.request().url();
    if (isProductionBackend(url)) {
      state.prod.push({ channel: 'http', url });
      await route.abort('blockedbyclient');
      return;
    }
    await route.continue();
  });

  // Supabase Realtime uses WebSockets. Route them before navigation and close
  // any hosted/productive socket instead of merely observing it.
  await page.routeWebSocket(/.*/, ws => {
    const url = ws.url();
    state.websockets.push(url);
    if (isProductionBackend(url)) {
      state.prod.push({ channel: 'websocket', url });
      ws.close();
      return;
    }
    ws.connectToServer();
  });

  page.on('request', req => {
    const url = req.url();
    if (isProductionBackend(url)) {
      state.prod.push({ channel: 'request-observer', url });
    }
  });

  page.on('websocket', ws => {
    const url = ws.url();
    if (isProductionBackend(url)) {
      state.prod.push({ channel: 'websocket-observer', url });
    }
  });

  page.on('response', res => {
    const status = res.status();
    const url = res.url();
    if (status >= 400) {
      try {
        const u = new URL(url);
        if (['127.0.0.1', 'localhost'].includes(u.hostname)) {
          state.http.push({ status, path: u.pathname });
        }
      } catch (_) {}
    }
  });

  page.on('pageerror', err => state.pageErrors.push(String(err?.stack || err?.message || err)));
  page.on('console', msg => {
    if (msg.type() === 'error') state.consoleErrors.push(msg.text());
  });

  testInfo._fjzSafety = state;
  return state;
}

async function login(page, email) {
  await page.goto('/');
  await expect(page.locator('#authEmail')).toBeVisible();
  await page.locator('#authEmail').fill(email);
  await page.locator('#authPass').fill(PASSWORD);
  const loginForm = page.locator('#authEmail').locator('xpath=ancestor::div[contains(@class,"auth-grid")]');
  await loginForm.getByRole('button', { name: /^Ingresar$/ }).click();
  await expect(page.locator('#authGate')).toBeHidden({ timeout: 15000 });
  await expect(page.locator('#view')).toBeVisible();
}

async function logout(page) {
  let btn = page.getByRole('button', { name: /Cerrar sesión/i }).first();
  if (!(await btn.count()) || !(await btn.isVisible())) {
    const cloudStatus = page.locator('#cloudStatusBtn');
    if (await cloudStatus.count() && await cloudStatus.isVisible()) {
      await cloudStatus.click();
      await expect(page.getByRole('heading', { name: 'TEAM FJZ Cloud' })).toBeVisible();
      btn = page.locator('#modal').getByRole('button', { name: /Cerrar sesión/i }).first();
    }
  }
  if (await btn.count() && await btn.isVisible()) {
    await btn.click();
    await expect(page.locator('#authEmail')).toBeVisible({ timeout: 10000 });
    return;
  }
  throw new Error('No existe una ruta visible al cierre de sesión desde el estado actual.');
}

async function logCoachRuntimeDebug(page, label) {
  const debug = await page.evaluate(() => {
    const view = document.getElementById('view');
    const safe = (fn, fallback = null) => {
      try { return fn(); } catch (_) { return fallback; }
    };
    return {
      mode: safe(() => typeof mode === 'undefined' ? 'undefined' : mode),
      coachTab: safe(() => typeof coachTab === 'undefined' ? 'undefined' : coachTab),
      currentProfileRole: safe(() => typeof currentProfile === 'undefined' ? 'undefined' : currentProfile?.role || null),
      commentsRenderer: typeof window.__fjzRenderTrainingCommentsV325,
      agendaEnsure: typeof window.__fjzEnsureCoachAgendaV342,
      v324: window.__fjzV324 || null,
      commentsHost: !!document.getElementById('v325TrainingCommentsCenter'),
      priorityHost: !!document.getElementById('v252PriorityCenter'),
      heroActions: !!view?.querySelector('.v225-hero-actions'),
      heroPillRow: !!view?.querySelector('.hero .pill-row'),
      agendaButtons: [...(view?.querySelectorAll('button') || [])]
        .map(x => (x.textContent || '').trim())
        .filter(x => /Agenda/i.test(x)),
      headings: [...(view?.querySelectorAll('h1,h2,h3,h4') || [])]
        .map(x => (x.textContent || '').trim())
        .slice(0, 30),
      viewSnippet: (view?.innerHTML || '').replace(/\s+/g, ' ').slice(0, 7000)
    };
  });
  console.log('E2E_COACH_RUNTIME_DEBUG '+label+' '+JSON.stringify(debug));
}

async function assertNoHorizontalOverflow(page) {
  const dims = await page.evaluate(() => ({
    width: window.innerWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }));
  expect(
    dims.scrollWidth,
    'La página genera overflow horizontal respecto del viewport.'
  ).toBeLessThanOrEqual(dims.width + 2);
}

async function finishSafety(testInfo) {
  const s = testInfo._fjzSafety;
  if (!s) return;
  if (s.http.length) console.log('BASELINE_LOCAL_HTTP_FAILURES', JSON.stringify(s.http.slice(0, 30)));
  if (s.consoleErrors.length) console.log('BASELINE_CONSOLE_ERRORS', JSON.stringify(s.consoleErrors.slice(0, 30)));
  expect(s.prod, 'El navegador intentó contactar Supabase productivo.').toEqual([]);
  expect(
    s.http.filter(x => x.status === 404),
    'Se detectaron 404 locales: el entorno QA no tiene paridad suficiente o la app pidió una ruta inexistente.'
  ).toEqual([]);
  expect(s.pageErrors, 'Se detectaron errores JavaScript no controlados.').toEqual([]);
}

function localDateArgentina() {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Argentina/Buenos_Aires',
    year: 'numeric', month: '2-digit', day: '2-digit'
  }).formatToParts(new Date());
  const map = Object.fromEntries(parts.map(x => [x.type, x.value]));
  return `${map.year}-${map.month}-${map.day}`;
}

test.beforeEach(async ({ page }, testInfo) => {
  await installSafety(page, testInfo);
});

test.afterEach(async ({}, testInfo) => {
  await finishSafety(testInfo);
});

test('Alumno: navegación principal, responsive y acceso a módulos visibles', async ({ page }, testInfo) => {
  await login(page, 'alumno01@test.local');

  await expect(page.locator('#view').getByText('TEST ALUMNO 01', { exact: true }).filter({ visible: true }).first()).toBeVisible();
  for (const name of ['Inicio', 'Entrenar', 'Nutrición', 'Progreso']) {
    await expect(page.getByRole('button', { name }).first()).toBeVisible();
  }
  await assertNoHorizontalOverflow(page);

  await page.getByRole('button', { name: 'Entrenar' }).first().click();
  await expect(page.getByRole('heading', { name: 'Día QA A' })).toBeVisible();
  await expect(page.getByRole('button', { name: /Finalizar sesión/i })).toBeVisible();
  await assertNoHorizontalOverflow(page);
  await page.getByRole('button', { name: /Inicio/i }).first().click();

  await page.getByRole('button', { name: 'Nutrición' }).first().click();
  await expect(page.getByText('PLAN QA A', { exact: true })).toBeVisible({ timeout: 10000 });
  await expect(page.getByRole('heading', { name: 'Calculadora de alimentos y comidas' })).toBeVisible();
  await assertNoHorizontalOverflow(page);

  await page.getByRole('button', { name: 'Progreso' }).first().click();
  await expect(page.getByRole('heading', { name: 'Progreso', exact: true })).toBeVisible();
  await assertNoHorizontalOverflow(page);

  await page.getByRole('button', { name: 'Inicio' }).first().click();
  const checkin = page.getByRole('button', { name: /Completar check-in|Check-in/i }).first();
  if (await checkin.count()) {
    await checkin.click();
    await expect(page.getByRole('heading', { name: /Check-in y seguimiento/i })).toBeVisible();
  } else {
    testInfo.annotations.push({ type: 'baseline-gap', description: 'No hay acceso visible al Check-in desde Inicio.' });
  }

  const historyRoute = page.getByRole('button', { name: /Historial|Ver sesión|Ver historial/i });
  if (!(await historyRoute.count())) {
    testInfo.annotations.push({
      type: 'baseline-gap',
      description: 'El HUD principal del Alumno no ofrece una ruta permanente visible al Historial.'
    });
  }
  console.log('E2E_FLOW_OK student-navigation '+testInfo.project.name);
});

test('Entrenamiento + comentario + persistencia + revisión Coach', async ({ page }, testInfo) => {
  const comment = `E2E ${testInfo.project.name} · comentario Press QA`;

  await login(page, 'alumno01@test.local');
  await page.getByRole('button', { name: 'Entrenar' }).first().click();
  await expect(page.getByRole('heading', { name: 'Día QA A' })).toBeVisible();

  const cards = page.locator('.session-card');
  await expect(cards).toHaveCount(2);
  await expect(cards.nth(0)).toContainText('Press QA');

  const allSets = page.locator('.set-grid');
  const setCount = await allSets.count();
  expect(setCount).toBeGreaterThanOrEqual(6);

  for (let i = 0; i < setCount; i++) {
    const row = allSets.nth(i);
    const inputs = row.locator('input');
    await inputs.nth(0).fill(i < 3 ? '25' : '30');
    await expect(inputs.nth(0)).toBeFocused();
    await inputs.nth(1).fill(i % 3 === 0 ? '10' : '9');
    await inputs.nth(2).fill('2');
  }

  await cards.nth(0).getByRole('button', { name: /Comentario/i }).click();
  await expect(page.getByRole('heading', { name: 'Comentario del ejercicio' })).toBeVisible();
  await page.locator('#v73FeedbackMessage').fill(comment);
  await page.getByRole('button', { name: /Enviar al coach/i }).click();
  await expect(cards.nth(0)).toContainText(/Comentario enviado/i);

  await page.getByRole('button', { name: /Finalizar sesión/i }).click();
  await expect(page.getByRole('heading', { name: '¿Cómo salió la sesión?' })).toBeVisible();
  await page.getByRole('button', { name: /Todo bien · finalizar/i }).click();
  await expect(page.locator('#modalWrap')).toBeVisible({ timeout: 15000 });
  await expect(page.locator('#modal')).toContainText(/Sesión guardada|Entrenamiento completado|guardad/i, { timeout: 15000 });

  const back = page.getByRole('button', { name: /Volver al inicio/i });
  if (await back.count()) await back.click();
  else {
    const close = page.locator('#modal').getByRole('button', { name: '✕' }).first();
    if (await close.count()) await close.click();
  }

  await page.reload();
  await expect(page.locator('#authGate')).toBeHidden({ timeout: 15000 });
  await expect(page.locator('#view').getByText('TEST ALUMNO 01', { exact: true }).filter({ visible: true }).first()).toBeVisible();

  const visibleHistory = page.getByRole('button', { name: /Historial|Ver sesión|Ver historial/i }).first();
  if (await visibleHistory.count()) {
    await visibleHistory.click();
    await expect(page.getByText('Día QA A', { exact: false }).first()).toBeVisible();
  } else {
    testInfo.annotations.push({
      type: 'baseline-gap',
      description: 'No se pudo verificar el Historial por navegación real porque no existe una ruta visible permanente desde este estado.'
    });
  }

  await logout(page);
  await login(page, 'coach@test.local');
  await logCoachRuntimeDebug(page, 'workout-'+testInfo.project.name);

  await expect(page.getByRole('heading', { name: 'Lo que te dejaron tus alumnos', exact: true })).toBeVisible({ timeout: 15000 });
  await expect(page.getByText(comment, { exact: true }).first()).toBeVisible({ timeout: 15000 });
  const commentNode = page.getByText(comment, { exact: true }).first();
  const container = commentNode.locator('xpath=ancestor::*[self::article or contains(@class,"card") or contains(@class,"feedback-item")][1]');
  const openAction = container.getByRole('button', { name: /Abrir|Ver/i }).first();

  if (!(await openAction.count())) {
    throw new Error('El comentario pendiente aparece al Coach pero no ofrece una acción visible para abrir su origen.');
  }

  await openAction.click();
  console.log('E2E_COMMENT_STAGE opened-session '+testInfo.project.name);
  await expect(page.getByText('Press QA', { exact: false }).first()).toBeVisible({ timeout: 10000 });
  console.log('E2E_COMMENT_STAGE exercise-visible '+testInfo.project.name);

  const commentAgain = page.getByText(comment, { exact: true }).first();
  await expect(commentAgain).toBeVisible();
  console.log('E2E_COMMENT_STAGE comment-visible '+testInfo.project.name);

  const reviewContainer = commentAgain.locator('xpath=ancestor::*[contains(concat(" ", normalize-space(@class), " "), " v287-exercise-comment ")][1]');
  await expect(reviewContainer, 'El comentario abierto debe conservar su contenedor exacto de revisión.').toBeVisible();
  console.log('E2E_COMMENT_STAGE exact-container-visible '+testInfo.project.name);
  const ok = reviewContainer.getByRole('button', { name: /OK|Marcar revisado/i }).first();
  if (!(await ok.count())) {
    throw new Error('No existe botón OK/revisado dentro del comentario exacto abierto.');
  }
  await expect(ok, 'El OK del comentario exacto debe ser visible antes de confirmar la revisión.').toBeVisible();
  console.log('E2E_COMMENT_STAGE ok-visible '+testInfo.project.name);
  await ok.click();
  console.log('E2E_COMMENT_STAGE ok-clicked '+testInfo.project.name);

  await expect(
    reviewContainer.getByText('Revisado', { exact: true }),
    'El OK debe reflejarse en el comentario exacto sólo después de la confirmación durable.'
  ).toBeVisible({ timeout: 15000 });
  await expect(
    reviewContainer.getByRole('button', { name: /OK|Marcar revisado/i }),
    'El OK no debe quedar disponible después de una revisión confirmada.'
  ).toHaveCount(0);
  console.log('E2E_COMMENT_STAGE durable-review-visible '+testInfo.project.name);

  const modalAfterAck = page.locator('#modalWrap');
  await expect(modalAfterAck).toBeVisible();
  await page.locator('#modal').getByRole('button', { name: 'Cerrar' }).click();
  await expect(modalAfterAck).toBeHidden();
  console.log('E2E_COMMENT_STAGE modal-closed '+testInfo.project.name);

  await page.getByRole('button', { name: /Alumnos/i }).filter({ visible: true }).first().click();
  await page.reload();
  await expect(page.locator('#authGate')).toBeHidden({ timeout: 15000 });
  await expect(page.getByText(comment, { exact: true })).toHaveCount(0);
  console.log('E2E_FLOW_OK workout-comment-coach '+testInfo.project.name);
});



test('2A Premium: registro, foco, comentario contextual y recuperación tras refresh', async ({ page }, testInfo) => {
  const comment='2A '+testInfo.project.name+' · comentario premium';
  await login(page,'alumno01@test.local');
  await page.getByRole('button',{name:'Entrenar'}).first().click();
  await expect(page.getByRole('heading',{name:'Día QA A'})).toBeVisible();
  await expect(page.locator('#view')).toHaveClass(/v22-premium-workout/);
  await expect(page.locator('#v22WorkoutSaveState')).toContainText(/Entrenamiento en curso|Borrador protegido/);

  const cards=page.locator('.session-card.v22-premium-exercise');
  await expect(cards).toHaveCount(2);
  const firstInputs=cards.nth(0).locator('.set-grid').first().locator('input');

  await firstInputs.nth(0).fill('17.5');
  await expect(firstInputs.nth(0)).toBeFocused();
  await expect(firstInputs.nth(0)).toHaveValue('17.5');
  await firstInputs.nth(1).fill('10');
  await expect(firstInputs.nth(1)).toBeFocused();
  await firstInputs.nth(2).fill('1.5');
  await expect(firstInputs.nth(2)).toBeFocused();
  await expect(firstInputs.nth(2)).toHaveValue('1.5');

  await expect(cards.nth(0).locator('.v22-previous-load').first()).toBeVisible();
  await expect(cards.nth(0).locator('.v22-recommendation').first()).toBeVisible();
  await expect(page.locator('#v22WorkoutSaveState')).toContainText(/Borrador protegido|Cambios pendientes/);
  console.log('E2E_2A_STAGE input-and-references '+testInfo.project.name);

  await cards.nth(0).getByRole('button',{name:/Comentario/i}).click();
  await expect(page.locator('#modal')).toHaveClass(/v22-comment-modal/);
  await page.locator('#v73FeedbackMessage').fill(comment);
  await page.getByRole('button',{name:'Cerrar comentario'}).click();

  await cards.nth(0).getByRole('button',{name:/Comentario/i}).click();
  await expect(page.locator('#v73FeedbackMessage')).toHaveValue(comment);
  await page.getByRole('button',{name:/Enviar al coach/i}).click();
  await expect(page.locator('#v264QuickSaved')).toContainText(/Comentario (guardado|enviado)/i);
  await expect(cards.nth(0).locator('.set-grid').first().locator('input').nth(0)).toHaveValue('17.5');
  console.log('E2E_2A_STAGE comment-saved-with-session-draft-intact '+testInfo.project.name);

  await page.reload();
  await expect(page.locator('#authGate')).toBeHidden({timeout:15000});

  const activeWorkout=page.locator('#view .session-card');
  if(!(await activeWorkout.count())){
    const resume=page.getByRole('button',{name:/Continuar entrenamiento/i}).first();
    await expect(resume).toBeVisible({timeout:10000});
    await resume.click();
  }
  await expect(page.locator('.session-card').first().locator('.set-grid').first().locator('input').nth(0)).toHaveValue('17.5');
  await assertNoHorizontalOverflow(page);
  await page.screenshot({path:'artifacts/2a/premium-draft-'+testInfo.project.name+'.png',fullPage:true});
  console.log('E2E_FLOW_OK premium-draft-recovery-2a '+testInfo.project.name);
});

test('2A Premium: finalización confirmada, historial e idempotencia', async ({ page }, testInfo) => {
  await login(page,'alumno01@test.local');
  await page.getByRole('button',{name:'Entrenar'}).first().click();
  await expect(page.getByRole('heading',{name:'Día QA A'})).toBeVisible();

  const sets=page.locator('.set-grid');
  const count=await sets.count();
  for(let i=0;i<count;i++){
    const inputs=sets.nth(i).locator('input');
    await inputs.nth(0).fill(i<3?'25':'30');
    await inputs.nth(1).fill('10');
    await inputs.nth(2).fill('2');
  }

  const before=await page.evaluate(()=>student().sessions?.length||0);
  await page.getByRole('button',{name:/Finalizar sesión/i}).click();
  const sessionFeedback=page.getByRole('heading',{name:/¿Cómo salió la sesión\?/i});
  if(await sessionFeedback.count()){
    await expect(sessionFeedback).toBeVisible();
    await page.getByRole('button',{name:/Todo bien · finalizar/i}).click();
  }

  await expect(page.locator('#modal')).toContainText(/Sesión guardada con éxito|Sesión guardada|Entrenamiento completado/i,{timeout:20000});
  const saveState=await page.evaluate(()=>window.__fjzSessionSaveStateV207?.());
  expect(saveState?.state).toBe('success');
  expect(saveState?.cloudConfirmed).toBeTruthy();

  const after=await page.evaluate(()=>student().sessions?.length||0);
  expect(after).toBe(before+1);

  await page.evaluate(()=>finishWorkout());
  expect(await page.evaluate(()=>student().sessions?.length||0)).toBe(after);

  const history=page.locator('#modal .v22-history-after-save');
  await expect(history,'El éxito confirmado debe ofrecer acceso directo al historial.').toBeVisible({timeout:10000});
  await history.click({timeout:10000});
  await expect(page.locator('#modalWrap')).toBeHidden({timeout:10000});
  await expect(page.getByText('Día QA A',{exact:false}).first()).toBeVisible({timeout:10000});
  await assertNoHorizontalOverflow(page);
  await page.screenshot({path:'artifacts/2a/premium-complete-'+testInfo.project.name+'.png',fullPage:true});
  console.log('E2E_FLOW_OK premium-finish-history-idempotent-2a '+testInfo.project.name);
});

test('2A Premium: fallo de red conserva sesión y reintenta sin duplicar', async ({ page }, testInfo) => {
  await login(page,'alumno01@test.local');
  await page.getByRole('button',{name:'Entrenar'}).first().click();
  await expect(page.getByRole('heading',{name:'Día QA A'})).toBeVisible();

  const sets=page.locator('.set-grid');
  const count=await sets.count();
  for(let i=0;i<count;i++){
    const inputs=sets.nth(i).locator('input');
    await inputs.nth(0).fill(i<3?'22.5':'27.5');
    await inputs.nth(1).fill('9');
    await inputs.nth(2).fill('2');
  }

  const before=await page.evaluate(()=>student().sessions?.length||0);
  await page.route('**/rest/v1/rpc/commit_workout_session_v202',async route=>{
    await route.abort('failed');
  });

  await page.getByRole('button',{name:/Finalizar sesión/i}).click();
  const sessionFeedback=page.getByRole('heading',{name:/¿Cómo salió la sesión\?/i});
  if(await sessionFeedback.count()){
    await page.getByRole('button',{name:/Todo bien · finalizar/i}).click();
  }

  await expect(page.locator('#modal')).toContainText(/No se pudo confirmar el guardado/i,{timeout:20000});
  const failed=await page.evaluate(()=>window.__fjzSessionSaveStateV207?.());
  expect(failed?.state).toBe('failed');
  expect(failed?.cloudConfirmed).toBeFalsy();

  const pendingCount=await page.evaluate(()=>student().sessions?.length||0);
  expect(pendingCount).toBe(before+1);
  const pendingId=failed.sessionId;

  await page.unroute('**/rest/v1/rpc/commit_workout_session_v202');
  await page.getByRole('button',{name:/Reintentar/i}).click();
  await expect(page.locator('#modal')).toContainText(/Sesión guardada con éxito/i,{timeout:20000});

  const success=await page.evaluate(()=>window.__fjzSessionSaveStateV207?.());
  expect(success?.state).toBe('success');
  expect(success?.cloudConfirmed).toBeTruthy();
  expect(success?.sessionId).toBe(pendingId);
  expect(await page.evaluate(()=>student().sessions?.length||0)).toBe(pendingCount);

  console.log('E2E_FLOW_OK premium-workout-retry-2a '+testInfo.project.name);
});

test('2A Premium responsive: controles táctiles sin overflow', async ({ page }, testInfo) => {
  await login(page,'alumno01@test.local');
  await page.getByRole('button',{name:'Entrenar'}).first().click();
  await expect(page.locator('#view')).toHaveClass(/v22-premium-workout/);
  await assertNoHorizontalOverflow(page);

  const input=page.locator('.v22-premium-set input').first();
  const finish=page.getByRole('button',{name:/Finalizar sesión/i}).first();
  const [ibox,bbox]=await Promise.all([input.boundingBox(),finish.boundingBox()]);
  expect(ibox?.height||0).toBeGreaterThanOrEqual(44);
  expect(bbox?.height||0).toBeGreaterThanOrEqual(44);

  await page.screenshot({path:'artifacts/2a/responsive-'+testInfo.project.name+'.png',fullPage:true});
  console.log('E2E_FLOW_OK premium-responsive-2a '+testInfo.project.name);
});

test('2B exacto: identidad estable, comentario pre-finalización e historial exacto', async ({ page }, testInfo) => {
  const comment='2B exact '+testInfo.project.name;
  await login(page,'alumno01@test.local');
  await page.getByRole('button',{name:'Entrenar'}).first().click();
  await expect(page.getByRole('heading',{name:'Día QA A'})).toBeVisible();

  const firstSet=page.locator('.set-grid').first().locator('input');
  await firstSet.nth(0).fill('32.5');
  await firstSet.nth(1).fill('9');
  await firstSet.nth(2).fill('1.5');
  const sessionId=await page.evaluate(()=>window.__fjzWorkoutSessionIdV2B?.());
  expect(sessionId).toMatch(/^ss_/);

  const firstCard=page.locator('.session-card.v22-premium-exercise').first();
  await firstCard.getByRole('button',{name:/Comentario/i}).click();
  await page.locator('#v73FeedbackMessage').fill(comment);
  await page.getByRole('button',{name:/Enviar al coach/i}).click();
  await expect(page.locator('#v264QuickSaved')).toContainText(/Comentario (guardado|enviado)/i);

  const linkedBefore=await page.evaluate(async ({comment,sessionId})=>{
    const {data,error}=await supabaseClient.from('exercise_feedback')
      .select('id,session_id,exercise_uid,status,message')
      .eq('message',comment).single();
    if(error)throw error;
    return {id:data.id,session_id:data.session_id,exercise_uid:data.exercise_uid,status:data.status};
  },{comment,sessionId});
  expect(linkedBefore.session_id).toBe(sessionId);

  await page.reload();
  await expect(page.locator('#authGate')).toBeHidden({timeout:15000});
  if(!(await page.locator('#view .session-card').count())){
    await page.getByRole('button',{name:/Continuar entrenamiento/i}).first().click();
  }
  expect(await page.evaluate(()=>window.__fjzWorkoutSessionIdV2B?.())).toBe(sessionId);

  const sets=page.locator('.set-grid');
  for(let i=0;i<await sets.count();i++){
    const inputs=sets.nth(i).locator('input');
    if(!(await inputs.nth(0).inputValue()))await inputs.nth(0).fill(i<3?'32.5':'35');
    await inputs.nth(1).fill('9'); await inputs.nth(2).fill('1.5');
  }
  await page.getByRole('button',{name:/Finalizar sesión/i}).click();
  const fb=page.getByRole('heading',{name:/¿Cómo salió la sesión\?/i});
  if(await fb.count())await page.getByRole('button',{name:/Todo bien · finalizar/i}).click();
  await expect(page.locator('#modal')).toContainText(/Sesión guardada con éxito/i,{timeout:20000});
  const save=await page.evaluate(()=>window.__fjzSessionSaveStateV207?.());
  expect(save.sessionId).toBe(sessionId);expect(save.cloudConfirmed).toBeTruthy();

  const projection=await page.evaluate(async sid=>{
    const {data,error}=await supabaseClient.from('workout_sessions')
      .select('source_session_id,status').eq('source_session_id',sid).single();
    if(error)throw error; return data;
  },sessionId);
  expect(projection.source_session_id).toBe(sessionId);
  expect(projection.status).toBe('completed');

  await page.locator('#modal .v22-history-after-save').click();
  const row=page.locator('.v22-history-session',{hasText:'Día QA A'}).first();
  await expect(row).toBeVisible(); await row.getByRole('button',{name:/Ver sesión/i}).click();
  await expect(page.locator('#modal')).toContainText(comment);
  await expect(page.locator('#modal')).toContainText('Vinculado a esta sesión');
  await page.screenshot({path:'artifacts/2b/exact-history-'+testInfo.project.name+'.png',fullPage:true});
  console.log('E2E_FLOW_OK session-comment-history-2b '+testInfo.project.name);
});

test('2B History responsive: historial premium sin overflow', async ({ page }, testInfo) => {
  await login(page,'alumno01@test.local');
  await page.getByRole('button',{name:'Historial'}).filter({visible:true}).first().click();
  await assertNoHorizontalOverflow(page);
  const history=page.locator('.v22-premium-history');
  if(await history.count())await expect(history).toBeVisible();
  await page.screenshot({path:'artifacts/2b/history-responsive-'+testInfo.project.name+'.png',fullPage:true});
  console.log('E2E_FLOW_OK history-responsive-2b '+testInfo.project.name);
});


test('2B-V visual system: legibility, touch targets, focus and composition', async ({page},testInfo)=>{
  await login(page,'alumno01@test.local');
  await page.getByRole('button',{name:'Entrenar'}).first().click();
  await expect(page.locator('#view.v22v-performance-shell')).toBeVisible();
  const card=page.locator('.v22v-exercise').first();
  await expect(card.locator('.v22v-series-header')).toBeVisible();
  const m=await page.evaluate(()=>{const q=s=>document.querySelector(s),f=n=>n?parseFloat(getComputedStyle(n).fontSize):0,r=n=>n?.getBoundingClientRect?.()||{height:0};const input=q('.v22-set-field .input'),comment=q('.v22v-exercise-actions .v22-comment-action'),title=q('.v22v-exercise-title strong');return{inputFont:f(input),titleFont:f(title),inputHeight:r(input).height,commentHeight:r(comment).height,width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}});
  expect(m.inputFont).toBeGreaterThanOrEqual(16);expect(m.titleFont).toBeGreaterThanOrEqual(17);expect(m.inputHeight).toBeGreaterThanOrEqual(44);expect(m.commentHeight).toBeGreaterThanOrEqual(44);expect(m.scroll).toBeLessThanOrEqual(m.width+1);
  const input=card.locator('input').first();await input.fill('37.5');await expect(input).toBeFocused();
  await page.screenshot({path:'artifacts/2bv/workout-'+testInfo.project.name+'.png',fullPage:true});
  console.log('E2E_FLOW_OK visual-redesign-workout-2bv '+testInfo.project.name);
});

test('2B-V visual system: navegación contextual, contraste básico y dock sin tapar input activo', async ({page},testInfo)=>{
  await login(page,'alumno01@test.local');
  await page.getByRole('button',{name:'Entrenar'}).first().click();
  const view=page.locator('#view.v22v-performance-shell');await expect(view).toBeVisible();
  const data=await page.evaluate(()=>{
    const visible=n=>!!(n&&n.getBoundingClientRect().width&&n.getBoundingClientRect().height);
    const tabs=[...document.querySelectorAll('#view .v22v-context-nav .tab')].filter(visible).map(x=>x.textContent.trim());
    const dock=document.querySelector('.v22v-finish-dock')?.getBoundingClientRect();
    const active=document.querySelector('.v22-set-field input')?.getBoundingClientRect();
    const css=n=>n?getComputedStyle(n):null;
    const title=css(document.querySelector('.v22v-exercise-title strong'));
    const contextual=[...document.querySelectorAll('.v22v-exercise .v72-tech-card .muted,.v22v-exercise .v22-previous-load,.v22v-exercise .v22-reference-label,.v22v-exercise .v22v-exercise-progress')]
      .filter(visible).map(n=>parseFloat(getComputedStyle(n).fontSize)||0).filter(Boolean);
    return{tabs,dock:dock?{h:dock.height,b:dock.bottom}:null,active:active?{h:active.height}:null,titleFont:parseFloat(title?.fontSize||0),contextualFonts:contextual};
  });
  expect(data.tabs.filter(x=>/^Inicio$/i.test(x)).length).toBe(0);
  expect(data.tabs.filter(x=>/^Nutrici[oó]n$/i.test(x)).length).toBe(0);
  expect(data.dock?.h||0).toBeGreaterThanOrEqual(48);
  expect(data.active?.h||0).toBeGreaterThanOrEqual(44);
  expect(data.titleFont).toBeGreaterThanOrEqual(18);
  expect(data.contextualFonts.length).toBeGreaterThan(0);
  expect(Math.min(...data.contextualFonts)).toBeGreaterThanOrEqual(12);
  await assertNoHorizontalOverflow(page);
  console.log('E2E_FLOW_OK visual-context-a11y-2bv '+testInfo.project.name);
});

test('2B-V comentarios: compose accesible y táctil', async ({page},testInfo)=>{
  await login(page,'alumno01@test.local');await page.getByRole('button',{name:'Entrenar'}).first().click();
  const comment=page.locator('.v22v-exercise').first().getByRole('button',{name:/Comentario/i});await comment.click();
  const modal=page.locator('#modal.v22v-comment-sheet');await expect(modal).toBeVisible();
  const ta=modal.locator('textarea'),send=modal.getByRole('button',{name:/Enviar al coach/i});
  const [tb,sb]=await Promise.all([ta.boundingBox(),send.boundingBox()]);
  expect(tb?.height||0).toBeGreaterThanOrEqual(120);expect(sb?.height||0).toBeGreaterThanOrEqual(44);
  await ta.fill('Comentario visual de prueba');await expect(ta).toBeFocused();await assertNoHorizontalOverflow(page);
  console.log('E2E_FLOW_OK visual-comment-sheet-2bv '+testInfo.project.name);
});

test('2B-V historial: timeline y detalle legibles', async ({page},testInfo)=>{
  await login(page,'alumno01@test.local');
  await page.getByRole('button',{name:'Historial'}).filter({visible:true}).first().click();
  const history=page.locator('.v22v-history');
  const duplicateGlobalTabs=page.locator('#view .tabs .v22v-duplicate-nav:visible');
  expect(await duplicateGlobalTabs.count()).toBe(0);
  const historyGlobalLabels=await page.locator('#view .tabs .tab:visible').allTextContents();
  expect(historyGlobalLabels.map(x=>x.trim().toLowerCase()).filter(x=>['inicio','nutrición','nutricion','progreso','entrenar'].includes(x))).toEqual([]);
  if(await history.count()){await expect(history).toBeVisible();await assertNoHorizontalOverflow(page);const open=history.locator('.v22v-history-open').first();if(await open.count()){await open.click();await expect(page.locator('#modal.v22v-session-modal')).toBeVisible();const s=await page.evaluate(()=>({comments:[...document.querySelectorAll('.v22v-context-comment p')].map(x=>parseFloat(getComputedStyle(x).fontSize)),kpi:[...document.querySelectorAll('.v22v-session-kpis span')].map(x=>parseFloat(getComputedStyle(x).fontSize)),width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));expect(s.comments.every(x=>x>=12)).toBeTruthy();expect(s.kpi.every(x=>x>=12)).toBeTruthy();expect(s.scroll).toBeLessThanOrEqual(s.width+1);await page.screenshot({path:'artifacts/2bv/session-detail-'+testInfo.project.name+'.png',fullPage:true});}}
  console.log('E2E_FLOW_OK visual-redesign-history-2bv '+testInfo.project.name);
});


test('2B-V.1 visual polish: series headers, previous reference and dock/input geometry', async ({page},testInfo)=>{
  await login(page,'alumno01@test.local');
  await page.getByRole('button',{name:'Entrenar'}).first().click();
  const view=page.locator('#view.v22v-performance-shell');
  await expect(view).toBeVisible();

  const geometry=await page.evaluate(()=>{
    const visible=n=>!!(n&&n.getBoundingClientRect().width&&n.getBoundingClientRect().height);
    const headers=[...document.querySelectorAll('.v22v-series-header>span')].filter(visible).map(n=>{
      const r=n.getBoundingClientRect(),s=getComputedStyle(n);
      return {text:n.textContent.trim(),w:r.width,h:r.height,line:parseFloat(s.lineHeight)||parseFloat(s.fontSize)*1.2,whiteSpace:s.whiteSpace};
    });
    const refs=[...document.querySelectorAll('.v22v-previous-load,.v22-exercise .v205-prev-load')].filter(visible).map(n=>({
      text:n.textContent.trim(),client:n.clientWidth,scroll:n.scrollWidth,whiteSpace:getComputedStyle(n).whiteSpace,textOverflow:getComputedStyle(n).textOverflow
    }));
    return {headers,refs,width:innerWidth,scroll:document.documentElement.scrollWidth};
  });
  expect(geometry.headers.map(x=>x.text.toUpperCase())).toEqual(expect.arrayContaining(['SERIE','CARGA','REPS','RIR']));
  expect(geometry.headers.every(x=>x.h<=x.line*1.65)).toBeTruthy();
  expect(geometry.headers.every(x=>x.whiteSpace==='nowrap')).toBeTruthy();
  expect(geometry.refs.every(x=>x.whiteSpace!=='nowrap'&&x.textOverflow!=='ellipsis')).toBeTruthy();
  expect(geometry.scroll).toBeLessThanOrEqual(geometry.width+2);

  const lastInput=page.locator('.v22-set-field input').last();
  await lastInput.scrollIntoViewIfNeeded();
  await lastInput.fill('17.5');
  await expect(lastInput).toBeFocused();
  await lastInput.evaluate(el=>el.scrollIntoView({block:'center',inline:'nearest'}));
  const focused=await page.evaluate(()=>{
    const input=document.activeElement?.getBoundingClientRect?.();
    const dock=document.querySelector('.v22v-finish-dock');
    const d=dock?.getBoundingClientRect?.();
    const s=dock?getComputedStyle(dock):null;
    return {vw:innerWidth,vh:innerHeight,input:input?{top:input.top,bottom:input.bottom}:null,dock:d?{top:d.top,bottom:d.bottom,opacity:Number(s.opacity),pointer:s.pointerEvents}:null};
  });
  expect(focused.input?.bottom||0).toBeLessThanOrEqual(focused.vh+1);
  if(focused.vw<1000&&focused.dock&&focused.dock.opacity>0){
    expect(focused.input?.bottom||0).toBeLessThanOrEqual(focused.dock.top-4);
  }
  await assertNoHorizontalOverflow(page);
  await page.screenshot({path:'artifacts/2bv/polish-series-'+testInfo.project.name+'.png',fullPage:true});
  if(testInfo.project.name==='mobile-390'){
    await page.setViewportSize({width:390,height:520});
    await lastInput.scrollIntoViewIfNeeded();
    await expect(lastInput).toBeFocused();
    await expect(page.locator('.v22v-finish-dock')).toHaveCSS('opacity','0');
    await page.screenshot({path:'artifacts/2bv/polish-series-mobile-390-reduced-height-focus.png',fullPage:false});
    const reduced=await page.evaluate(()=>({vh:innerHeight,bottom:document.activeElement?.getBoundingClientRect?.().bottom||0,dockOpacity:Number(getComputedStyle(document.querySelector('.v22v-finish-dock')).opacity)}));
    expect(reduced.bottom).toBeLessThanOrEqual(reduced.vh+1);
    expect(reduced.dockOpacity).toBe(0);
    await page.setViewportSize({width:390,height:844});
  }
  console.log('E2E_FLOW_OK visual-polish-series-2bv1 '+testInfo.project.name);
});

test('2B-V.1 visual polish: comment modal has one close path and stable textarea focus', async ({page},testInfo)=>{
  await login(page,'alumno01@test.local');
  await page.getByRole('button',{name:'Entrenar'}).first().click();
  await page.locator('.v22v-exercise').first().getByRole('button',{name:/Comentario/i}).click();
  const modal=page.locator('#modal.v22v-comment-sheet');
  await expect(modal).toBeVisible();
  const closeActions=modal.getByRole('button',{name:/Cerrar/i}).filter({visible:true});
  expect(await closeActions.count()).toBe(1);
  expect(await modal.locator('#v22CommentClose').count()).toBe(0);
  const ta=modal.locator('textarea');
  await ta.fill('Foco V22 2B-V.1');
  await expect(ta).toBeFocused();
  const box=await ta.boundingBox();
  expect(box?.height||0).toBeGreaterThanOrEqual(120);
  await assertNoHorizontalOverflow(page);
  console.log('E2E_FLOW_OK visual-polish-comment-2bv1 '+testInfo.project.name);
});

test('2B-V.1 visual polish: history KPIs and previous/current comparison do not collapse', async ({page},testInfo)=>{
  await login(page,'alumno01@test.local');
  await page.getByRole('button',{name:'Historial'}).filter({visible:true}).first().click();
  const open=page.locator('.v22v-history-open').first();
  if(await open.count()){
    await open.click();
    const modal=page.locator('#modal.v22v-session-modal');
    await expect(modal).toBeVisible();
    const metrics=await page.evaluate(()=>{
      const visible=n=>!!(n&&n.getBoundingClientRect().width&&n.getBoundingClientRect().height);
      const kpis=[...document.querySelectorAll('.v22v-session-kpis>div')].filter(visible).map(n=>{
        const strong=n.querySelector('strong'),label=n.querySelector('span'),sr=strong?.getBoundingClientRect(),lr=label?.getBoundingClientRect();
        return {strong:strong?.textContent.trim()||'',strongW:sr?.width||0,strongH:sr?.height||0,label:label?.textContent.trim()||'',labelW:lr?.width||0,labelH:lr?.height||0};
      });
      const compare=[...document.querySelectorAll('.v22-history-compare')].filter(visible).map(n=>({
        boxes:n.querySelectorAll('.v22-history-compare-box').length,
        previous:!!n.querySelector('.v22v-compare-previous'),
        current:!!n.querySelector('.v22v-compare-current')
      }));
      return {kpis,compare,width:innerWidth,scroll:document.documentElement.scrollWidth};
    });
    expect(metrics.kpis.length).toBeGreaterThan(0);
    expect(metrics.kpis.every(x=>x.strongW>0&&x.strongH<48&&x.labelW>0)).toBeTruthy();
    expect(metrics.compare.every(x=>x.boxes===2&&x.previous&&x.current)).toBeTruthy();
    expect(metrics.scroll).toBeLessThanOrEqual(metrics.width+2);
    await page.screenshot({path:'artifacts/2bv/polish-history-'+testInfo.project.name+'.png',fullPage:true});
  }
  console.log('E2E_FLOW_OK visual-polish-history-2bv1 '+testInfo.project.name);
});


test('2B-V2 UX: primer ejercicio y primera serie son accionables en el viewport inicial', async ({page},testInfo)=>{
  await login(page,'alumno01@test.local');
  await page.getByRole('button',{name:'Entrenar'}).first().click();
  const view=page.locator('#view.v22v2-workout-active');
  await expect(view).toBeVisible();
  await expect(view).toHaveAttribute('data-v22-product-experience','performance-training-v2');

  const header=page.locator('.v22v2-workout-header');
  const firstExercise=page.locator('.v22v2-exercise').first();
  const firstInput=firstExercise.locator('.set-grid input').first();
  await expect(header).toBeVisible();
  await expect(firstExercise).toBeVisible();
  await expect(firstInput).toBeVisible();

  const initial=await page.evaluate(()=>{
    const box=s=>document.querySelector(s)?.getBoundingClientRect?.();
    const h=box('.v22v2-workout-header'),e=box('.v22v2-exercise'),i=box('.v22v2-exercise .set-grid input');
    const bottom=document.querySelector('#bottomNav');
    const finish=document.querySelector('.v22v2-finish-zone');
    return {
      vw:innerWidth,vh:innerHeight,
      header:h?{top:h.top,bottom:h.bottom,height:h.height}:null,
      exercise:e?{top:e.top,bottom:e.bottom}:null,
      input:i?{top:i.top,bottom:i.bottom}:null,
      bottomDisplay:bottom?getComputedStyle(bottom).display:null,
      finishPosition:finish?getComputedStyle(finish).position:null,
      overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth
    };
  });
  expect(initial.header?.height||999).toBeLessThan(120);
  expect(initial.exercise?.top||9999).toBeLessThan(initial.vh*.42);
  expect(initial.input?.bottom||9999).toBeLessThanOrEqual(initial.vh);
  expect(initial.bottomDisplay).toBe('none');
  expect(initial.finishPosition).not.toBe('fixed');
  expect(initial.overflow).toBeLessThanOrEqual(2);

  const discard=page.getByRole('button',{name:/Descartar borrador/i}).filter({visible:true});
  expect(await discard.count()).toBe(0);
  const feedbackLabels=await firstExercise.locator('.v73-comment-badge:visible,.v73-alert-badge:visible').allTextContents();
  const normalizedFeedback=feedbackLabels.map(x=>x.replace(/\s*·\s*\d+\s*$/,'').trim().toLowerCase()).filter(Boolean);
  expect(new Set(normalizedFeedback).size).toBe(normalizedFeedback.length);
  const technique=firstExercise.locator('.v22v2-technique-disclosure').first();
  if(await technique.count())expect(await technique.getAttribute('open')).toBeNull();
  const menu=header.locator('.v22v2-session-menu');
  await menu.locator('summary').click();
  await expect(page.getByRole('button',{name:/Descartar borrador/i}).filter({visible:true})).toBeVisible();
  await menu.locator('summary').click();

  await firstInput.fill('17.5');
  await expect(firstInput).toBeFocused();
  await expect(firstInput).toHaveValue('17.5');
  const primaryInside=page.locator('#view .tabs .tab:visible').filter({hasText:/^(Inicio|Entrenar|Nutrición|Nutricion|Progreso)$/i});
  expect(await primaryInside.count()).toBe(0);

  await page.screenshot({path:'artifacts/2bv2/initial-workout-'+testInfo.project.name+'.png',fullPage:false});
  console.log('E2E_FLOW_OK product-experience-initial-2bv2 '+testInfo.project.name);
});

test('2B-V2 UX: serie activa no queda tapada y finalización no compite con la carga', async ({page},testInfo)=>{
  await login(page,'alumno01@test.local');
  await page.getByRole('button',{name:'Entrenar'}).first().click();
  const input=page.locator('.v22v2-exercise').first().locator('.set-grid input').first();
  await input.fill('22.5');
  await expect(input).toBeFocused();
  const geometry=await page.evaluate(()=>{
    const i=document.activeElement?.getBoundingClientRect?.();
    const finish=document.querySelector('.v22v2-finish-zone')?.getBoundingClientRect?.();
    const overlays=[...document.querySelectorAll('body *')].filter(n=>{
      const s=getComputedStyle(n);if(!['fixed','sticky'].includes(s.position)||s.display==='none'||s.visibility==='hidden')return false;
      const r=n.getBoundingClientRect();return r.width>0&&r.height>0&&r.top<innerHeight&&r.bottom>0;
    }).map(n=>{const r=n.getBoundingClientRect();return{cls:n.className||n.id||n.tagName,top:r.top,bottom:r.bottom,left:r.left,right:r.right}});
    return {
      vh:innerHeight,
      input:i?{top:i.top,bottom:i.bottom,left:i.left,right:i.right}:null,
      finish:finish?{top:finish.top,bottom:finish.bottom,left:finish.left,right:finish.right}:null,
      overlays
    };
  });
  expect(geometry.input?.bottom||0).toBeLessThanOrEqual(geometry.vh);
  if(geometry.finish&&geometry.input){
    const horizontalOverlap=geometry.finish.left<geometry.input.right&&geometry.finish.right>geometry.input.left;
    if(horizontalOverlap)expect(geometry.finish.top).toBeGreaterThan(geometry.input.bottom);
  }
  expect(geometry.overlays.some(x=>{
    if(!String(x.cls).includes('v22v-finish-dock')||!geometry.input)return false;
    const horizontalOverlap=x.left<geometry.input.right&&x.right>geometry.input.left;
    const verticalOverlap=x.top<geometry.input.bottom&&x.bottom>geometry.input.top;
    return horizontalOverlap&&verticalOverlap;
  })).toBeFalsy();
  await assertNoHorizontalOverflow(page);
  console.log('E2E_FLOW_OK product-experience-no-overlay-2bv2 '+testInfo.project.name);
});

test('2B-V2 UX: comentario contextual vuelve al flujo sin navegación secundaria', async ({page},testInfo)=>{
  await login(page,'alumno01@test.local');
  await page.getByRole('button',{name:'Entrenar'}).first().click();
  const first=page.locator('.v22v2-exercise').first();
  await first.getByRole('button',{name:/Comentario/i}).click();
  const modal=page.locator('#modal.v22v2-comment-sheet');
  await expect(modal).toBeVisible();
  const ta=modal.locator('#v73FeedbackMessage');
  await ta.fill('Comentario UX V2');
  await expect(ta).toBeFocused();
  expect(await modal.getByRole('button',{name:/Cerrar comentario/i}).count()).toBe(1);
  await modal.getByRole('button',{name:/Cerrar comentario/i}).click();
  await expect(page.locator('#modalWrap')).toBeHidden();
  await expect(first.locator('.set-grid input').first()).toBeVisible();
  console.log('E2E_FLOW_OK product-experience-comment-return-2bv2 '+testInfo.project.name);
});

test('2B-V2 UX: historial funciona como performance log y conserva detalle exacto', async ({page},testInfo)=>{
  await login(page,'alumno01@test.local');
  await page.getByRole('button',{name:'Historial'}).filter({visible:true}).first().click();
  const history=page.locator('.v22v2-history');
  await expect(history).toBeVisible();
  await expect(page.locator('#view')).toHaveAttribute('data-v22-product-experience','performance-history-v2');
  const rows=history.locator('.v22v2-history-session');
  expect(await rows.count()).toBeGreaterThan(0);
  const first=rows.first();
  const b=first.locator('.v22v2-history-open');
  await expect(b).toBeVisible();
  const rowGeo=await first.evaluate(n=>{const r=n.getBoundingClientRect();return{height:r.height,top:r.top,bottom:r.bottom}});
  expect(rowGeo.height).toBeLessThan(150);
  await b.click();
  const modal=page.locator('#modal.v22v2-session-modal');
  await expect(modal).toBeVisible();
  await expect(modal.locator('.v22v2-session-kpis')).toBeVisible();
  const comments=modal.locator('.v22v2-context-comment');
  if(await comments.count())await expect(comments.first()).toBeVisible();
  await assertNoHorizontalOverflow(page);
  await page.screenshot({path:'artifacts/2bv2/history-'+testInfo.project.name+'.png',fullPage:false});
  console.log('E2E_FLOW_OK product-experience-history-2bv2 '+testInfo.project.name);
});


test('2C temporizador: ciclo completo, una sola autoridad y recuperación por refresh', async ({page},testInfo)=>{
  await login(page,'alumno01@test.local');
  await page.getByRole('button',{name:'Entrenar'}).first().click();
  const rest=page.locator('.v22c-rest-control').first();
  await expect(rest).toBeVisible();
  const custom=rest.locator('input[aria-label*="Duración personal"]');
  if(await custom.count())await custom.fill('15');
  await rest.locator('button[data-rest-action="start"]').click();
  await expect(rest).toHaveAttribute('data-active','true');
  expect(await page.evaluate(()=>window.TeamFJZIntelligentTraining.timerCount())).toBe(1);
  const before=await page.evaluate(()=>window.TeamFJZIntelligentTraining.timerSnapshot().remainingMs);
  await page.waitForTimeout(1100);
  const after=await page.evaluate(()=>window.TeamFJZIntelligentTraining.timerSnapshot().remainingMs);
  expect(after).toBeLessThan(before);

  await rest.getByRole('button',{name:'Pausar'}).click();
  expect(await page.evaluate(()=>window.TeamFJZIntelligentTraining.timerCount())).toBe(0);
  await rest.getByRole('button',{name:'Reanudar'}).click();
  expect(await page.evaluate(()=>window.TeamFJZIntelligentTraining.timerCount())).toBe(1);

  const sid=await page.evaluate(()=>window.__fjzWorkoutSessionIdV2B?.());
  await page.screenshot({path:'artifacts/2c/rest-active-'+testInfo.project.name+'.png',fullPage:false});
  await page.reload();
  await expect(page.locator('#authGate')).toBeHidden({timeout:15000});
  const restoredControl=page.locator('.v22c-rest-control').first();
  if(!(await restoredControl.count())){
    const resume=page.getByRole('button',{name:/Continuar entrenamiento/i}).first();
    const train=page.getByRole('button',{name:'Entrenar',exact:true}).filter({visible:true}).first();
    if(await resume.isVisible().catch(()=>false))await resume.click();
    else{await expect(train).toBeVisible({timeout:10000});await train.click();}
  }
  await expect(page.locator('.v22c-rest-control').first()).toBeVisible({timeout:10000});
  const restored=await page.evaluate(sid=>({sid:window.TeamFJZIntelligentTraining.timerSnapshot()?.sessionId,count:window.TeamFJZIntelligentTraining.timerCount()}),sid);
  expect(restored.sid).toBe(sid);expect(restored.count).toBe(1);
  await page.locator('.v22c-rest-control').first().getByRole('button',{name:'Reiniciar'}).click();
  expect((await page.evaluate(()=>window.TeamFJZIntelligentTraining.timerSnapshot().state))).toBe('paused');
  await page.locator('.v22c-rest-control').first().getByRole('button',{name:'Omitir'}).click();
  expect(await page.evaluate(()=>window.TeamFJZIntelligentTraining.timerSnapshot())).toBeNull();
  await assertNoHorizontalOverflow(page);
  console.log('E2E_FLOW_OK intelligent-rest-2c '+testInfo.project.name);
});

test('2C récords y progresión: comparación verificable, RIR y modalidades incompatibles', async ({page},testInfo)=>{
  await login(page,'alumno01@test.local');
  const result=await page.evaluate(()=>{
    const e=window.TeamFJZIntelligentTraining;
    const a={id:'qa-prior',date:'2026-11-09T10:00:00Z',status:'completed',confirmed:true,cloudConfirmed:true,exerciseResults:[{exerciseUid:'press-qa',sets:[[80,10,2]],loadMode:'external'}]};
    const b={id:'qa-current',date:'2026-11-10T10:00:00Z',status:'completed',exerciseResults:[{exerciseUid:'press-qa',sets:[[82.5,10,2]],loadMode:'external'}]};
    const x=e.analyzeExercise({sessions:[a,b],currentSession:b,exerciseUid:'press-qa',confirmedSessionId:'qa-current'});
    const suggestion=e.progressionSuggestion(x);
    const assisted={id:'qa-assisted',date:'2026-11-09T09:00:00Z',status:'completed',confirmed:true,cloudConfirmed:true,exerciseResults:[{exerciseUid:'press-qa',sets:[[25,10,2]],loadMode:'assisted'}]};
    const incompatible=e.analyzeExercise({sessions:[assisted,b],currentSession:b,exerciseUid:'press-qa',confirmedSessionId:'qa-current'});
    return {record:x.records[0],suggestion,incompatible};
  });
  expect(result.record.message).toBe('80 kg × 10 → 82.5 kg × 10');
  expect(result.record.message).not.toContain('%');
  expect(result.suggestion.label).toBe('Sugerencia calculada');
  expect(result.incompatible.comparable).toBeFalsy();
  console.log('E2E_FLOW_OK intelligent-records-2c '+testInfo.project.name);
});

test('2C historial y Coach: progreso calculado se presenta sin sustituir prescripción', async ({page},testInfo)=>{
  await login(page,'alumno01@test.local');
  await page.evaluate(()=>{
    const s=student(),d=s.days[0],e=d.exercises[0],uid=e.uid;
    const prior={id:'qa-2c-history-a',date:'2026-11-08T10:00:00Z',dayId:d.id,dayName:d.name,status:'completed',confirmed:true,cloudConfirmed:true,exerciseResults:[{exerciseUid:uid,exerciseName:e.name,sets:[[40,10,2]]}]};
    const current={id:'qa-2c-history-b',date:'2026-11-09T10:00:00Z',dayId:d.id,dayName:d.name,status:'completed',confirmed:true,cloudConfirmed:true,exerciseResults:[{exerciseUid:uid,exerciseName:e.name,sets:[[42.5,10,2]]}]};
    s.sessions=(s.sessions||[]).filter(x=>!String(x.id||'').startsWith('qa-2c-history-')).concat([prior,current]);
    saveState();
  });
  await page.getByRole('button',{name:'Historial'}).filter({visible:true}).first().click();
  const row=page.locator('.v22v2-history-session[data-session-id="qa-2c-history-b"]');
  await expect(row).toBeVisible();await row.locator('.v22v2-history-open').click();
  const historyMetrics=page.locator('#modal .v244-summary-grid strong');
  await expect(historyMetrics.nth(0)).toHaveText('1');
  await expect(historyMetrics.nth(1)).toHaveText('1');
  const note=page.locator('#modal .v22c-performance-note').first();
  await expect(note).toBeVisible();
  await expect(note).toContainText(/Progreso verificable/i);
  await expect(note).toContainText(/Sugerencia calculada/i);
  await page.screenshot({path:'artifacts/2c/progression-'+testInfo.project.name+'.png',fullPage:false});
  await page.getByRole('button',{name:/Cerrar/i}).click();
  await page.evaluate(()=>{
    const s=student(),d=s.days[0],e=d.exercises[0];
    const solo={id:'qa-2c-history-no-ref',date:'2026-11-10T10:00:00Z',dayId:d.id,dayName:d.name,status:'completed',confirmed:true,cloudConfirmed:true,exerciseResults:[{exerciseUid:e.uid,exerciseName:e.name,loadMode:'assisted',sets:[[25,10,2]]}]};
    s.sessions=(s.sessions||[]).filter(x=>x.id!=='qa-2c-history-no-ref').concat([solo]);saveState();render();
  });
  const noRef=page.locator('.v22v2-history-session[data-session-id="qa-2c-history-no-ref"]');
  await expect(noRef).toBeVisible();await noRef.locator('.v22v2-history-open').click();
  await expect(page.locator('#modal .v22c-no-reference')).toContainText(/Sin referencia comparable/i);
  await page.screenshot({path:'artifacts/2c/no-reference-'+testInfo.project.name+'.png',fullPage:false});
  await assertNoHorizontalOverflow(page);
  console.log('E2E_FLOW_OK intelligent-progression-2c '+testInfo.project.name);
});

test('2C resumen final: sólo aparece después de confirmación real y mantiene idempotencia', async ({page},testInfo)=>{
  await login(page,'alumno01@test.local');
  await page.getByRole('button',{name:'Entrenar'}).first().click();
  await expect(page.locator('.v22c-rest-control').first()).toBeVisible();
  await page.evaluate(()=>{
    const s=student(),d=s.days[currentDay],e=d.exercises[0];
    const prior={id:'qa-2c-prior-summary',date:'2026-11-07T10:00:00Z',dayId:d.id,dayName:d.name,status:'completed',confirmed:true,cloudConfirmed:true,exerciseResults:[{exerciseUid:e.uid,exerciseName:e.name,sets:[[10,8,2]]}]};
    s.sessions=(s.sessions||[]).filter(x=>x.id!=='qa-2c-prior-summary').concat([prior]);saveState();
  });
  const sets=page.locator('.set-grid');
  for(let i=0;i<await sets.count();i++){
    const inputs=sets.nth(i).locator('input');
    await inputs.nth(0).fill(i<3?'20':'25');
    await inputs.nth(1).fill('10');
    await inputs.nth(2).fill('2');
  }
  const before=await page.evaluate(()=>student().sessions?.length||0);
  await page.getByRole('button',{name:/Finalizar sesión/i}).click();
  const fb=page.getByRole('heading',{name:/¿Cómo salió la sesión\?/i});
  if(await fb.count())await page.getByRole('button',{name:/Todo bien · finalizar/i}).click();
  await expect(page.locator('#modal .v22c-summary')).toBeVisible({timeout:20000});
  const save=await page.evaluate(()=>window.__fjzSessionSaveStateV207?.());
  expect(save.state).toBe('success');expect(save.cloudConfirmed).toBeTruthy();
  await expect(page.locator('#modal .v22c-summary')).toContainText(/SESIÓN CONFIRMADA/i);
  await expect(page.locator('#modal .v22c-summary')).toContainText(/PR · Récord/i);
  await page.screenshot({path:'artifacts/2c/summary-'+testInfo.project.name+'.png',fullPage:false});
  await page.screenshot({path:'artifacts/2c/record-valid-'+testInfo.project.name+'.png',fullPage:false});
  const after=await page.evaluate(()=>student().sessions?.length||0);
  expect(after).toBe(before+1);
  await page.evaluate(()=>finishWorkout());
  await expect(page.locator('#modal .v22c-summary')).toBeVisible();
  expect(await page.evaluate(()=>student().sessions?.length||0)).toBe(after);
  const historyAction=page.locator('#modal .v22-history-after-save');
  await expect(historyAction).toBeVisible();
  await historyAction.click();
  await expect(page.locator('.v22v2-history-session').first()).toBeVisible();
  await page.screenshot({path:'artifacts/2c/student-history-'+testInfo.project.name+'.png',fullPage:false});
  console.log('E2E_FLOW_OK intelligent-summary-2c '+testInfo.project.name);
});


test('2C Coach: historial conserva progreso verificable y comentarios exactos', async ({page},testInfo)=>{
  await login(page,'coach@test.local');
  await page.evaluate(()=>{
    const s=(window.students||[]).find(x=>String(x?.name||'').includes('TEST ALUMNO 01'))||student();
    const d=s.days[0],e=d.exercises[0],uid=e.uid;
    const rows=[
      {id:'qa-2c-coach-a',date:'2026-11-06T10:00:00Z',dayId:d.id,dayName:d.name,status:'completed',confirmed:true,cloudConfirmed:true,exerciseResults:[{exerciseUid:uid,exerciseName:e.name,sets:[[35,10,2]]}]},
      {id:'qa-2c-coach-b',date:'2026-11-07T10:00:00Z',dayId:d.id,dayName:d.name,status:'completed',confirmed:true,cloudConfirmed:true,exerciseResults:[{exerciseUid:uid,exerciseName:e.name,sets:[[37.5,10,2]]}]}
    ];
    s.sessions=(s.sessions||[]).filter(x=>!String(x.id||'').startsWith('qa-2c-coach-')).concat(rows);
    saveState();render();
  });
  const row=page.locator('.student-row',{hasText:'TEST ALUMNO 01'});
  await expect(row).toBeVisible();await row.getByRole('button',{name:/Abrir/i}).click();
  const historyTab=page.locator('button.tab[onclick*="coachStudentTab"]').filter({hasText:/^Historial/}).first();
  await expect(historyTab).toBeVisible();await historyTab.click();
  const sessionRow=page.locator('#coachStudentBody .v22v2-history-session[data-session-id="qa-2c-coach-b"]');
  await expect(sessionRow).toBeVisible();
  {
    await sessionRow.locator('.v22v2-history-open').click();
    const coachMetrics=page.locator('#modal .v244-summary-grid strong');
    await expect(coachMetrics.nth(0)).toHaveText('1');
    await expect(coachMetrics.nth(1)).toHaveText('1');
    const note=page.locator('#modal .v22c-performance-note').first();
    await expect(note).toBeVisible();
    await expect(note).toContainText(/Progreso verificable/i);
  }
  await page.screenshot({path:'artifacts/2c/coach-session-'+testInfo.project.name+'.png',fullPage:false});
  await assertNoHorizontalOverflow(page);
  console.log('E2E_FLOW_OK intelligent-coach-2c '+testInfo.project.name);
});

test('Nutrición: plan, registro, macros, calculadora, personalizado, persistencia y eliminación', async ({ page }, testInfo) => {
  await login(page, 'alumno01@test.local');
  await page.getByRole('button', { name: 'Nutrición' }).first().click();

  await expect(page.getByText('PLAN QA A', { exact: true })).toBeVisible({ timeout: 10000 });
  const option = page.locator('.meal-option-student', { hasText: 'Opción QA 2' });
  await expect(option).toBeVisible();
  const planBefore = (await option.innerText()).replace(/\s+/g, ' ').trim();

  await option.getByRole('button', { name: /Registrar hoy/i }).click();
  await expect(page.locator('#v264QuickSaved')).toContainText(/Opción registrada/i);
  const daily = page.locator('.nutrition-log');
  await expect(daily).toContainText('QA Arroz cocido');
  await expect(daily).toContainText('QA Proteína ficticia');

  const status = page.locator('#v276NutritionStatus');
  if (await status.count()) {
    await expect(status).toContainText(/Estado de hoy/i);
    await expect(status).toContainText(/restantes/i);
  }

  await expect(page.locator('#nutritionLogDate')).toHaveValue(localDateArgentina());

  await page.reload();
  await expect(page.locator('#authGate')).toBeHidden({ timeout: 15000 });
  await page.getByRole('button', { name: 'Nutrición' }).first().click();
  await expect(page.locator('.nutrition-log')).toContainText('QA Arroz cocido');

  const select = page.locator('#macroFood');
  const yogurtValue = await select.locator('option').filter({ hasText: 'QA Yogur ficticio' }).first().getAttribute('value');
  expect(yogurtValue).toBeTruthy();
  await select.selectOption(yogurtValue);
  await page.locator('#macroGrams').fill('180');
  await page.getByRole('button', { name: /Agregar al registro/i }).click();
  await expect(page.locator('#v264QuickSaved')).toContainText(/Registro guardado/i);
  await expect(page.locator('.nutrition-log')).toContainText('QA Yogur ficticio');

  await page.getByRole('button', { name: /Personalizado/i }).click();
  await expect(page.getByRole('heading', { name: /Registrar alimento personalizado|Alimento personalizado/i })).toBeVisible();
  await page.locator('#cmName').fill('QA E2E personalizado');
  await page.locator('#cmGrams').fill('100');
  await page.locator('#cmKcal').fill('100');
  await page.locator('#cmP').fill('10');
  await page.locator('#cmC').fill('12');
  await page.locator('#cmF').fill('2');
  await page.getByRole('button', { name: 'Guardar en mi registro', exact: true }).click();
  await expect(page.locator('.nutrition-log')).toContainText('QA E2E personalizado');

  const customRow = page.locator('.nutrition-log-row', { hasText: 'QA E2E personalizado' });
  await expect(customRow).toBeVisible();
  await customRow.getByRole('button').click();
  await expect(page.locator('.nutrition-log')).not.toContainText('QA E2E personalizado');

  const optionAfter = (await page.locator('.meal-option-student', { hasText: 'Opción QA 2' }).innerText())
    .replace(/\s+/g, ' ').trim();
  expect(optionAfter).toBe(planBefore);

  await page.reload();
  await expect(page.locator('#authGate')).toBeHidden({ timeout: 15000 });
  await page.getByRole('button', { name: 'Nutrición' }).first().click();
  await expect(page.locator('.nutrition-log')).toContainText('QA Arroz cocido');
  await expect(page.locator('.nutrition-log')).not.toContainText('QA E2E personalizado');
  console.log('E2E_FLOW_OK nutrition '+testInfo.project.name);
});

test('AgendaRepository V22: lectura canónica, integración controlada y aislamiento RLS', async ({ page }, testInfo) => {
  const A1='10000000-0000-4000-8000-000000000001';
  const A2='10000000-0000-4000-8000-000000000002';
  const S1='50000000-0000-4000-8000-000000000001';
  const S2='50000000-0000-4000-8000-000000000002';
  const R2='51000000-0000-4000-8000-000000000002';
  const MISSING='59999999-0000-4000-8000-000000000099';

  await login(page, 'alumno01@test.local');

  const studentResult=await page.evaluate(async ({A1,A2,S1,S2,R2,MISSING})=>{
    const flag=document.querySelector('meta[name="fjz-v22-agenda-repository-read"]')?.content||'';
    const integrated=await window.__fjzLoadOwnAppointmentsV312(false);
    const ownAthlete=await supabaseClient.from('athletes')
      .select('id').eq('user_id',currentUser.id).maybeSingle();
    if(ownAthlete.error)throw ownAthlete.error;
    const repo=window.TeamFJZAgendaRepository.createAgendaRepository({supabase:supabaseClient,ttlMs:30000});
    const own=await repo.listForAthlete(ownAthlete.data.id);
    const cross=await repo.listForAthlete(A2);
    const ownEvent=await repo.getById(S1);
    const crossEvent=await repo.getById(S2);
    const crossReminder=await repo.getById(R2);
    const missing=await repo.getById(MISSING);
    return {
      flag,
      integrationSource:integrated?.source||null,
      ownAthleteId:ownAthlete.data.id,
      ownSchedule:own.schedule.map(x=>({id:x.id,athlete_id:x.athlete_id,start_time:x.start_time})),
      ownReminders:own.reminders.map(x=>({id:x.id,athlete_id:x.athlete_id,remind_time:x.remind_time})),
      crossSchedule:cross.schedule.length,
      crossReminders:cross.reminders.length,
      ownEvent:ownEvent?{kind:ownEvent.kind,athleteId:ownEvent.athleteId,id:ownEvent.row.id}:null,
      crossEvent,
      crossReminder,
      missing,
      a1:A1
    };
  },{A1,A2,S1,S2,R2,MISSING});

  expect(studentResult.flag).toBe('enabled');
  expect(studentResult.integrationSource).toBe('agenda-repository-v22');
  expect(studentResult.ownAthleteId).toBe(A1);
  expect(studentResult.ownSchedule).toHaveLength(1);
  expect(studentResult.ownSchedule[0]).toEqual({id:S1,athlete_id:A1,start_time:'09:00:00'});
  expect(studentResult.ownReminders).toHaveLength(1);
  expect(studentResult.crossSchedule).toBe(0);
  expect(studentResult.crossReminders).toBe(0);
  expect(studentResult.ownEvent).toEqual({kind:'schedule',athleteId:A1,id:S1});
  expect(studentResult.crossEvent).toBeNull();
  expect(studentResult.crossReminder).toBeNull();
  expect(studentResult.missing).toBeNull();

  await logout(page);
  await login(page, 'coach@test.local');

  const coachResult=await page.evaluate(async ({A2,S2,R2})=>{
    const repo=window.TeamFJZAgendaRepository.createAgendaRepository({supabase:supabaseClient,ttlMs:30000});
    const rows=await repo.listForAthlete(A2);
    const schedule=await repo.getById(S2);
    const reminder=await repo.getById(R2);
    return {
      scheduleCount:rows.schedule.length,
      reminderCount:rows.reminders.length,
      schedule:schedule?{kind:schedule.kind,athleteId:schedule.athleteId,id:schedule.row.id}:null,
      reminder:reminder?{
        kind:reminder.kind,
        athleteId:reminder.athleteId,
        id:reminder.row.id,
        reminder_date:reminder.row.reminder_date
      }:null
    };
  },{A2,S2,R2});

  expect(coachResult.scheduleCount).toBe(1);
  expect(coachResult.reminderCount).toBe(1);
  expect(coachResult.schedule).toEqual({kind:'schedule',athleteId:A2,id:S2});
  expect(coachResult.reminder).toEqual({
    kind:'reminder',athleteId:A2,id:R2,reminder_date:'2026-01-20'
  });

  console.log('E2E_FLOW_OK agenda-repository '+testInfo.project.name);
});

test('Coach: dashboard y workspace 360 sin romper navegación', async ({ page }, testInfo) => {
  await login(page, 'coach@test.local');
  await logCoachRuntimeDebug(page, 'workspace-'+testInfo.project.name);

  await expect(page.locator('#view').getByText('TEST ALUMNO 01', { exact: true }).filter({ visible: true }).first()).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Panel Coach', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Agenda' }).filter({ visible: true }).first()).toBeVisible();
  await assertNoHorizontalOverflow(page);

  const row = page.locator('.student-row', { hasText: 'TEST ALUMNO 01' });
  await expect(row).toBeVisible();
  await row.getByRole('button', { name: /Abrir/i }).click({ timeout: 10000 });
  await expect(page.getByText('ATHLETE WORKSPACE · TEAM FJZ', { exact: true })).toBeVisible({ timeout: 10000 });
  console.log('E2E_COACH_STAGE workspace-open '+testInfo.project.name);

  const expectedTabs = ['Resumen', 'Rutina', 'Progreso', 'Historial', 'Seguimiento', 'Nutrición'];
  for (const tab of expectedTabs) {
    const btn = page.locator('button.tab[onclick*="coachStudentTab"]').filter({ hasText: new RegExp('^' + tab) }).first();
    await expect(btn, `Falta pestaña Coach ${tab}`).toBeVisible({ timeout: 10000 });
    await btn.click({ timeout: 10000 });
    await expect(page.locator('#coachStudentBody')).not.toBeEmpty({ timeout: 10000 });
    await assertNoHorizontalOverflow(page);
    console.log('E2E_COACH_STAGE tab-'+tab+' '+testInfo.project.name);
  }

  const agendaTab = page.locator('button.tab[onclick*="coachStudentTab"]').filter({ hasText: /^Agenda/ }).first();
  if (await agendaTab.count()) {
    await agendaTab.click({ timeout: 10000 });
    await expect(page.locator('#coachStudentBody')).not.toBeEmpty({ timeout: 10000 });
    console.log('E2E_COACH_STAGE athlete-agenda '+testInfo.project.name);
  } else {
    testInfo.annotations.push({ type: 'schema-or-ui-gap', description: 'Agenda no figura como pestaña permanente del workspace del alumno.' });
  }

  const paymentsTab = page.locator('button.tab[onclick*="coachStudentTab"]').filter({ hasText: /Pago|Cobranza/i }).first();
  if (!(await paymentsTab.count())) {
    testInfo.annotations.push({ type: 'baseline-gap', description: 'No se detectó pestaña visible de pagos/cobranzas en el workspace actual.' });
  }
  console.log('E2E_FLOW_OK coach-workspace '+testInfo.project.name);
});

test('Coach: acceso visible a Agenda mensual desde dashboard', async ({ page }, testInfo) => {
  await login(page, 'coach@test.local');
  await expect(page.getByRole('heading', { name: 'Panel Coach', exact: true })).toBeVisible();
  const agendaButton = page.locator("button[onclick*=\"coachTab='agenda'\"]").filter({ hasText: /^Agenda/ }).filter({ visible: true }).first();
  await expect(agendaButton, 'El dashboard Coach debe mantener una ruta visible a Agenda.').toBeVisible({ timeout: 10000 });
  await agendaButton.click({ timeout: 10000 });
  await expect(page.getByText(/CALENDARIO DEL COACH|Chequeos y seguimiento/i).first()).toBeVisible({ timeout: 10000 });
  await assertNoHorizontalOverflow(page);
  console.log('E2E_FLOW_OK coach-agenda '+testInfo.project.name);
});
