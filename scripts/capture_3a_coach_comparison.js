const { chromium } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const PASSWORD = process.env.FJZ_E2E_PASSWORD;
if (!PASSWORD) throw new Error('FJZ_E2E_PASSWORD is required');

async function login(page, baseURL) {
  await page.goto(baseURL, { waitUntil: 'domcontentloaded' });
  await page.locator('#authEmail').fill('coach@test.local');
  await page.locator('#authPass').fill(PASSWORD);
  const form = page.locator('#authEmail').locator('xpath=ancestor::div[contains(@class,"auth-grid")]');
  await form.getByRole('button', { name: /^Ingresar$/ }).click();
  await page.locator('#authGate').waitFor({ state: 'hidden', timeout: 20000 });
  await page.locator('#view').waitFor({ state: 'visible' });
}

async function capture(label, baseURL, outDir, current=false) {
  const browser = await chromium.launch({ headless: true });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();
    await login(page, baseURL);
    await page.screenshot({ path: path.join(outDir, label + '-dashboard-desktop.png'), fullPage: true });

    if (current) {
      await page.locator('.fjz3a-command-center').waitFor({ state: 'visible', timeout: 20000 });
      const group = page.locator('.fjz3a-group-head').first();
      if (await group.count()) {
        await group.click();
        await page.screenshot({ path: path.join(outDir, label + '-activity-group-open.png'), fullPage: true });
      }
      await page.locator('#fjz3a-students').scrollIntoViewIfNeeded();
      await page.screenshot({ path: path.join(outDir, label + '-students.png'), fullPage: true });
      await page.locator('#fjz3a-agenda').scrollIntoViewIfNeeded();
      await page.screenshot({ path: path.join(outDir, label + '-agenda.png'), fullPage: true });

      await page.evaluate(() => { window.__fjz3aOriginalLoadCoachFeed = window.loadCoachFeed; window.loadCoachFeed = async () => []; });
      await page.evaluate(async () => { await window.__fjzHydrateCoachCommandCenterV22(true); });
      await page.screenshot({ path: path.join(outDir, label + '-empty.png'), fullPage: true });

      await page.evaluate(() => { window.loadCoachFeed = async () => { throw new Error('QA read failure'); }; });
      await page.evaluate(async () => { await window.__fjzHydrateCoachCommandCenterV22(true); });
      await page.screenshot({ path: path.join(outDir, label + '-error-retry.png'), fullPage: true });

      await page.evaluate(() => { window.loadCoachFeed = window.__fjz3aOriginalLoadCoachFeed; });
      await page.setViewportSize({ width: 390, height: 844 });
      await page.reload({ waitUntil: 'domcontentloaded' });
      await page.locator('#authGate').waitFor({ state: 'hidden', timeout: 20000 });
      await page.locator('.fjz3a-command-center').waitFor({ state: 'visible', timeout: 20000 });
      await page.screenshot({ path: path.join(outDir, label + '-mobile-390.png'), fullPage: true });
    }
    await context.close();
  } finally {
    await browser.close();
  }
}

(async () => {
  const outDir = process.argv[2] || 'artifacts/3a-comparison';
  fs.mkdirSync(outDir, { recursive: true });
  await capture('v2141', 'http://127.0.0.1:8001', outDir, false);
  await capture('v22-pre3a', 'http://127.0.0.1:8003', outDir, false);
  await capture('v22-3a', 'http://127.0.0.1:8000', outDir, true);
  console.log('TEAM FJZ V22 3A visual comparison captured');
})().catch(err => { console.error(err); process.exit(1); });
