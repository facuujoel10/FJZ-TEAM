const {chromium}=require('@playwright/test');
const fs=require('fs');const path=require('path');
const PASSWORD=process.env.FJZ_E2E_PASSWORD||'TEAMFJZ-Local-Only!22';
const out=process.argv[2]||'artifacts/4a-ux-comparison';
const old4a=process.argv[3]||'http://127.0.0.1:8008';
const current=process.argv[4]||'http://127.0.0.1:8000';
fs.mkdirSync(out,{recursive:true});
function pngSize(buf){return{width:buf.readUInt32BE(16),height:buf.readUInt32BE(20)}}
async function shot(page,name,fullPage=false){
  const vp=page.viewportSize();const css=await page.evaluate(()=>{const r=document.scrollingElement||document.documentElement,ox=scrollX,oy=scrollY;scrollTo(100000,oy);const mx=scrollX;scrollTo(ox,oy);return{w:innerWidth,h:innerHeight,dpr:devicePixelRatio,sw:r.scrollWidth,cw:r.clientWidth,sh:Math.max(document.documentElement.scrollHeight,document.body?.scrollHeight||0,innerHeight),mx}});
  if(css.sw>css.cw+2||css.mx>2)throw Error('Horizontal overflow '+name+' '+JSON.stringify(css));
  const file=path.join(out,name+(fullPage?'-full':'-viewport')+'.png');await page.evaluate(()=>scrollTo(0,0));
  let buf;if(fullPage){const cdp=await page.context().newCDPSession(page);try{const x=await cdp.send('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:true,clip:{x:0,y:0,width:css.w,height:css.sh,scale:1}});buf=Buffer.from(x.data,'base64');fs.writeFileSync(file,buf)}finally{await cdp.detach()}}else buf=await page.screenshot({path:file});
  const png=pngSize(buf),ew=Math.round(css.w*css.dpr),eh=Math.round((fullPage?css.sh:css.h)*css.dpr);
  if(png.width!==ew||Math.abs(png.height-eh)>2)throw Error('PNG CSS/DPR mismatch '+name+' '+JSON.stringify({css,png,ew,eh}));
  fs.writeFileSync(file.replace('.png','.json'),JSON.stringify({css,png,expected:{width:ew,height:eh},fullPage},null,2));
}
async function both(page,name){await shot(page,name,false);await shot(page,name,true)}
async function login(page,url,email){await page.goto(url,{waitUntil:'domcontentloaded'});const g=page.locator('#authGate');if(await g.isVisible().catch(()=>false)){await page.locator('#authEmail').fill(email);await page.locator('#authPass').fill(PASSWORD);await page.locator('#authGate .btn.primary').click()}await g.waitFor({state:'hidden',timeout:20000})}
async function student(page,url){await login(page,url,'alumno01@test.local');await page.getByRole('button',{name:/^Nutrición$/}).first().click();await page.locator('.fjz4a-student-shell').waitFor({state:'visible',timeout:20000})}
async function coach(page,url){await login(page,url,'coach@test.local');const s=page.locator('#fjz3aStudentSearch');if(await s.count())await s.fill('ALUMNO 01');const row=page.locator('#studentList .student-row',{hasText:'TEST ALUMNO 01'}).first();await row.getByRole('button',{name:/Abrir/i}).click();await page.locator('.fjz3b-nav button[data-section="nutrition"]').click();await page.locator('.fjz4a-coach-shell').waitFor({state:'visible',timeout:20000})}
async function layout(page){return page.evaluate(()=>{const r=x=>x?x.getBoundingClientRect():null;return{viewport:{w:innerWidth,h:innerHeight},studentMeal:r(document.querySelector('.fjz4a-meal')),coachMeal:r(document.querySelector('.fjz4a-meal-editor')),targets:r(document.querySelector('.fjz4a-targets'))}})}
(async()=>{const b=await chromium.launch({headless:true});const metrics={};try{
  for(const vp of [{width:390,height:844},{width:1440,height:900}]){
    const key=vp.width+'x'+vp.height;
    for(const [label,url] of [['4a',old4a],['4aux',current]]){
      let p=await b.newPage({viewport:vp});await student(p,url);metrics[label+'-student-'+key]=await layout(p);await both(p,label+'-'+key+'-student-start');await p.close();
      p=await b.newPage({viewport:vp});await coach(p,url);metrics[label+'-coach-'+key]=await layout(p);await both(p,label+'-'+key+'-coach-editor');await p.close();
    }
  }
  const before=metrics['4a-student-390x844'].studentMeal?.top??9999,after=metrics['4aux-student-390x844'].studentMeal?.top??9999;
  const cb=metrics['4a-coach-1440x900'].coachMeal?.top??9999,ca=metrics['4aux-coach-1440x900'].coachMeal?.top??9999;
  if(!(after<before&&after<844))throw Error('Student first-meal hierarchy did not improve '+JSON.stringify({before,after}));
  if(!(ca<cb&&ca<900))throw Error('Coach editor hierarchy did not improve '+JSON.stringify({before:cb,after:ca}));
  fs.writeFileSync(path.join(out,'4a-vs-4aux-layout-metrics.json'),JSON.stringify(metrics,null,2));

  let p=await b.newPage({viewport:{width:390,height:844}});await student(p,current);
  await pageAddAlt(p);const meal=p.locator('.fjz4a-meal',{hasText:'Desayuno'});await meal.scrollIntoViewIfNeeded();await both(p,'4aux-390x844-first-meal-alternatives');
  await meal.locator('.fjz4a-macros').first().scrollIntoViewIfNeeded();await both(p,'4aux-390x844-macros');
  await p.locator('.fjz4a-consumption').scrollIntoViewIfNeeded();await both(p,'4aux-390x844-consumption');await p.close();

  p=await b.newPage({viewport:{width:390,height:844}});await coach(p,current);await both(p,'4aux-390x844-coach-mobile');
  const notes=p.locator('#nutNotes'),orig=await notes.inputValue();await notes.fill(orig+' CAPTURE');await p.getByRole('button',{name:'Guardar cambios'}).click();await p.locator('#modal').waitFor({state:'visible',timeout:15000});await both(p,'4aux-390x844-save-success');const close=p.locator('#modal').getByRole('button',{name:/Listo|Cerrar/i}).first();if(await close.count())await close.click();await p.close();

  p=await b.newPage({viewport:{width:390,height:844}});await coach(p,current);const n=p.locator('#nutNotes'),o=await n.inputValue();await n.fill(o+' ERROR');await p.route('**/rest/v1/nutrition_plans*',r=>r.request().method()==='PATCH'?r.abort('failed'):r.continue());await p.getByRole('button',{name:'Guardar cambios'}).click();await p.locator('#fjz4aSaveState').filter({hasText:/Error al guardar/i}).waitFor({state:'visible',timeout:15000});await both(p,'4aux-390x844-save-error');await p.close();

  p=await b.newPage({viewport:{width:390,height:844}});await p.route('**/rest/v1/nutrition_plans*',r=>r.request().method()==='GET'?r.fulfill({status:200,contentType:'application/json',headers:{'content-range':'*/0'},body:'[]'}):r.continue());await login(p,current,'alumno02@test.local');await p.getByRole('button',{name:/^Nutrición$/}).first().click();await p.locator('.fjz4a-empty-state').waitFor({state:'visible',timeout:15000});await both(p,'4aux-390x844-empty-plan');await p.close();
}finally{await b.close()}console.log('TEAM FJZ V22 4A-UX visual evidence captured and hierarchy improvement verified')})().catch(e=>{console.error(e);process.exit(1)});
async function pageAddAlt(page){await page.evaluate(()=>{const p=__fjzNutritionContextV22().cache.plan.plan,m=p.meals.find(x=>x.id==='meal_qa_breakfast');if(m&&!m.options.some(x=>x.id==='opt_qa_ux_capture'))m.options.push({id:'opt_qa_ux_capture',name:'Opción QA Alternativa',items:[{id:'item_qa_ux_capture',name:'QA Tostadas ficticias',grams:60,kcal:150,protein_g:6,carbs_g:28,fat_g:2,measure_type:'units',quantity:2,unit_name:'tostadas'}]});TeamFJZNutritionPremium.renderStudent()})}
