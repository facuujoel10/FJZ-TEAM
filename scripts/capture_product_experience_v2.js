const {chromium}=require('@playwright/test');
const fs=require('fs'),path=require('path');
const PASSWORD='TEAMFJZ-Local-Only!22',PROD='cujipwacwwpejhqjhnkr';
const label=process.argv[2],base=process.argv[3],out=process.argv[4];
if(!label||!base||!out)throw new Error('usage: node capture_product_experience_v2.js label baseURL outDir');
fs.mkdirSync(out,{recursive:true});
const viewports=[['mobile-360',360,800],['mobile-390',390,844],['mobile-430',430,932],['desktop-1440',1440,900]];
async function safePage(context){const page=await context.newPage();await page.route('**/*',async route=>{const u=route.request().url();if(u.includes(PROD)||u.includes('.supabase.co'))return route.abort('blockedbyclient');return route.continue()});return page}
async function login(page){await page.goto(base,{waitUntil:'domcontentloaded'});await page.locator('#authEmail').waitFor({state:'visible',timeout:15000});await page.locator('#authEmail').fill('alumno01@test.local');await page.locator('#authPass').fill(PASSWORD);const form=page.locator('#authEmail').locator('xpath=ancestor::div[contains(@class,"auth-grid")]');await form.getByRole('button',{name:/^Ingresar$/}).click();await page.locator('#authGate').waitFor({state:'hidden',timeout:15000})}
async function nav(page,name){const b=page.getByRole('button',{name}).filter({visible:true}).first();if(await b.count())await b.click()}
async function shot(page,vp,state){await page.screenshot({path:path.join(out,label+'-'+vp+'-'+state+'.png'),fullPage:false})}
async function ensureWorkout(page){await nav(page,'Entrenar');await page.waitForTimeout(180);if(await page.locator('.session-card').count())return;const start=page.getByRole('button',{name:/Iniciar entrenamiento|Comenzar|Entrenar ahora|Continuar entrenamiento/i}).filter({visible:true}).first();if(await start.count())await start.click();if(!(await page.locator('.session-card').count()))await page.evaluate(()=>{try{if(typeof startWorkout==='function')startWorkout(0);else if(typeof currentDay!=='undefined'&&typeof render==='function'){currentDay=0;render()}}catch(_e){}});await page.locator('.session-card').first().waitFor({state:'visible',timeout:12000})}
(async()=>{const browser=await chromium.launch({headless:true});try{
 for(const [vp,w,h] of viewports){
  const context=await browser.newContext({viewport:{width:w,height:h},locale:'es-AR',timezoneId:'America/Argentina/Buenos_Aires',serviceWorkers:'block'});
  const page=await safePage(context);await login(page);
  await nav(page,'Historial');await page.waitForTimeout(220);await page.evaluate(()=>window.scrollTo(0,0));await shot(page,vp,'history');
  const session=page.locator('.v22-history-session,.v244-history-item,.history-item').first();
  if(await session.count()){const open=session.getByRole('button',{name:/Ver sesión|Ver|Abrir/i}).first();if(await open.count()){await open.click();await page.waitForTimeout(180);await shot(page,vp,'session-detail');await shot(page,vp,'comments');const close=page.locator('#modal button[aria-label*="Cerrar"],#modal button[title*="Cerrar"],#modal .modal-head button').first();if(await close.count())await close.click()}}
  await ensureWorkout(page);await page.evaluate(()=>window.scrollTo(0,0));await page.waitForTimeout(120);await shot(page,vp,'workout-initial');await shot(page,vp,'workout');
  const inputs=page.locator('.session-card').first().locator('input');if(await inputs.count()>=3){await inputs.nth(0).fill('37.5');await inputs.nth(1).fill('9');await inputs.nth(2).fill('1.5')}
  await page.waitForTimeout(100);await shot(page,vp,'series');
  const comment=page.locator('.session-card').first().getByRole('button',{name:/Comentario/i}).first();if(await comment.count()){await comment.click();const ta=page.locator('#v73FeedbackMessage');if(await ta.count())await ta.fill('Comentario visual QA · técnica estable');await page.waitForTimeout(100);await shot(page,vp,'comment-compose')}
  await context.close();
 }
}finally{await browser.close()}console.log('PRODUCT_EXPERIENCE_CAPTURE_OK '+label)})().catch(e=>{console.error(e);process.exit(1)});
