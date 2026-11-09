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

test('Coach: dashboard, agenda y workspace 360 sin romper navegación', async ({ page }, testInfo) => {
  await login(page, 'coach@test.local');
  await logCoachRuntimeDebug(page, 'workspace-'+testInfo.project.name);

  await expect(page.locator('#view').getByText('TEST ALUMNO 01', { exact: true }).filter({ visible: true }).first()).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Panel Coach', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Agenda' }).filter({ visible: true }).first()).toBeVisible();
  await assertNoHorizontalOverflow(page);

  const row = page.locator('.student-row', { hasText: 'TEST ALUMNO 01' });
  await expect(row).toBeVisible();
  await row.getByRole('button', { name: /Abrir/i }).click();

  await expect(page.getByText('ATHLETE WORKSPACE · TEAM FJZ', { exact: true })).toBeVisible();
  const expectedTabs = ['Resumen', 'Rutina', 'Progreso', 'Historial', 'Seguimiento', 'Nutrición'];
  for (const tab of expectedTabs) {
    const btn = page.locator('button.tab[onclick*="coachStudentTab"]').filter({ hasText: new RegExp('^' + tab) }).first();
    await expect(btn, `Falta pestaña Coach ${tab}`).toBeVisible();
    await btn.click();
    await expect(page.locator('#coachStudentBody')).not.toBeEmpty();
    await assertNoHorizontalOverflow(page);
  }

  const agendaTab = page.locator('button.tab[onclick*="coachStudentTab"]').filter({ hasText: /^Agenda/ }).first();
  if (await agendaTab.count()) {
    await agendaTab.click();
    await expect(page.locator('#coachStudentBody')).not.toBeEmpty();
  } else {
    testInfo.annotations.push({ type: 'schema-or-ui-gap', description: 'Agenda no figura como pestaña permanente del workspace del alumno.' });
  }

  const paymentsTab = page.locator('button.tab[onclick*="coachStudentTab"]').filter({ hasText: /Pago|Cobranza/i }).first();
  if (!(await paymentsTab.count())) {
    testInfo.annotations.push({ type: 'baseline-gap', description: 'No se detectó pestaña visible de pagos/cobranzas en el workspace actual.' });
  }

  await page.locator("button[onclick*=\"coachTab='agenda'\"]").filter({ hasText: /^Agenda/ }).first().click();
  await expect(page.getByText(/CALENDARIO DEL COACH|Chequeos y seguimiento/i).first()).toBeVisible({ timeout: 10000 });
  await assertNoHorizontalOverflow(page);
  console.log('E2E_FLOW_OK coach-workspace '+testInfo.project.name);
});
