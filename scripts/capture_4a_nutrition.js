const {chromium}=require('@playwright/test');
const fs=require('fs');const path=require('path');
const PASSWORD=process.env.FJZ_E2E_PASSWORD||'TEAMFJZ-Local-Only!22';
const out=process.argv[2]||'artifacts/4a-comparison';
const v2141=process.argv[3]||'http://127.0.0.1:8001';
const pre4a=process.argv[4]||'http://127.0.0.1:8007';
const current=process.argv[5]||'http://127.0.0.1:8000';
fs.mkdirSync(out,{recursive:true});
function pngSize(buf){return{width:buf.readUInt32BE(16),height:buf.readUInt32BE(20)}}
async function verifiedShot(page,name,fullPage=false,strict=true){
 const vp=page.viewportSize();if(!vp)throw Error('Missing viewport '+name);
 const css=await page.evaluate(()=>{
   const root=document.scrollingElement||document.documentElement,oldX=scrollX,oldY=scrollY;
   window.scrollTo(100000,oldY);const maxScrollX=scrollX;window.scrollTo(oldX,oldY);
   const shell=[...document.querySelectorAll('.fjz4a-coach-shell,.fjz4a-student-shell')].find(el=>{const r=el.getBoundingClientRect(),s=getComputedStyle(el);return s.display!=='none'&&r.width>0&&r.height>0})||null;
   const rect=shell?shell.getBoundingClientRect():null;
   return {width:innerWidth,height:innerHeight,dpr:devicePixelRatio,scrollWidth:document.documentElement.scrollWidth,scrollHeight:document.documentElement.scrollHeight,bodyScrollWidth:document.body?.scrollWidth||0,bodyScrollHeight:document.body?.scrollHeight||0,rootScrollWidth:root.scrollWidth,rootClientWidth:root.clientWidth,maxScrollX,shellRect:rect?{left:rect.left,right:rect.right,width:rect.width}:null};
 });
 if(css.width!==vp.width||css.height!==vp.height)throw Error('CSS viewport mismatch '+name+' '+JSON.stringify({vp,css}));
 if(strict&&(css.rootScrollWidth>css.rootClientWidth+2||css.maxScrollX>2||(css.shellRect&&(css.shellRect.left<-2||css.shellRect.right>css.width+2))))throw Error('Horizontal page overflow '+name+' '+JSON.stringify(css));
 const file=path.join(out,name+(fullPage?'-full':'-viewport')+'.png');
 const fullCssHeight=Math.max(css.scrollHeight,css.bodyScrollHeight,css.height);
 await page.evaluate(()=>scrollTo(0,0));
 const beforeShot=fullPage?await page.evaluate(()=>({scrollHeight:Math.max(document.documentElement.scrollHeight,document.body?.scrollHeight||0,innerHeight),width:innerWidth,height:innerHeight,dpr:devicePixelRatio})):null;
 let buf;
 if(fullPage){
   const cdp=await page.context().newCDPSession(page);
   try{
     const shot=await cdp.send('Page.captureScreenshot',{
       format:'png',
       fromSurface:true,
       captureBeyondViewport:true,
       clip:{x:0,y:0,width:css.width,height:fullCssHeight,scale:1}
     });
     buf=Buffer.from(shot.data,'base64');
     fs.writeFileSync(file,buf);
   }finally{await cdp.detach()}
 }else{
   buf=await page.screenshot({path:file,fullPage:false});
 }
 const png=pngSize(buf);
 const expectedWidth=Math.round(css.width*css.dpr),expectedHeight=Math.round(css.height*css.dpr),expectedFullHeight=Math.round(fullCssHeight*css.dpr);
 const actualCssHeight=png.height/css.dpr;
 const widthMatches=png.width===expectedWidth;
 const fullHeightMatches=!fullPage||Math.abs(png.height-expectedFullHeight)<=2;
 if(strict&&!widthMatches)throw Error('PNG width/DPR mismatch '+name+' '+JSON.stringify({css,png,expectedWidth}));
 if(strict&&!fullPage&&png.height!==expectedHeight)throw Error('PNG viewport height/DPR mismatch '+name+' '+JSON.stringify({css,png,expectedHeight}));
 if(strict&&fullPage&&!fullHeightMatches)throw Error('PNG full-page height/DPR mismatch '+name+' '+JSON.stringify({css,png,expectedFullHeight,actualCssHeight,beforeShot}));
 if(!strict&&fullPage&&png.height<expectedHeight)throw Error('Full PNG shorter than viewport '+name+' '+JSON.stringify({css,png,expectedHeight}));
 fs.writeFileSync(path.join(out,name+(fullPage?'-full':'-viewport')+'.json'),JSON.stringify({cssViewport:{width:css.width,height:css.height},devicePixelRatio:css.dpr,document:{scrollWidth:css.scrollWidth,scrollHeight:css.scrollHeight,bodyScrollWidth:css.bodyScrollWidth,bodyScrollHeight:css.bodyScrollHeight,rootScrollWidth:css.rootScrollWidth,rootClientWidth:css.rootClientWidth,maxScrollX:css.maxScrollX,shellRect:css.shellRect},pngPixels:png,expectedPixels:{width:expectedWidth,viewportHeight:expectedHeight,fullPageHeight:expectedFullHeight},actualCssHeight,beforeShot,widthMatchesCssDpr:widthMatches,fullHeightMatchesCssDpr:fullHeightMatches,strictCurrent4A:strict,historicalGeometryMismatch:!strict&&!widthMatches,fullPage,fullPageCaptureMode:'chromium-capture-beyond-viewport'},null,2));
}
async function login(page,url,email){await page.goto(url,{waitUntil:'domcontentloaded'});const gate=page.locator('#authGate');if(await gate.isVisible().catch(()=>false)){await page.locator('#authEmail').fill(email);await page.locator('#authPass').fill(PASSWORD);await page.locator('#authGate .btn.primary').click()}await gate.waitFor({state:'hidden',timeout:20000});await page.locator('#view').waitFor({state:'visible',timeout:15000})}
async function openStudentNutrition(page){const b=page.getByRole('button',{name:/^Nutrición$/}).first();await b.waitFor({state:'visible',timeout:15000});await b.click();await page.waitForTimeout(500)}
async function openCoachNutrition(page,current4a=false){
 const cc=page.locator('.fjz3a-command-center');
 if(await cc.count()){const search=page.locator('#fjz3aStudentSearch');if(await search.count())await search.fill('ALUMNO 01');const row=page.locator('#studentList .student-row',{hasText:'TEST ALUMNO 01'}).first();await row.getByRole('button',{name:/Abrir/i}).click();await page.locator('.fjz3b-header').waitFor({state:'visible',timeout:15000});await page.locator('.fjz3b-nav button[data-section="nutrition"]').click();}
 else{const row=page.locator('.student-row',{hasText:'TEST ALUMNO 01'}).first();await row.waitFor({state:'visible',timeout:15000});await row.getByRole('button',{name:/Abrir/i}).click();const n=page.getByRole('button',{name:/^Nutrición$/}).last();if(await n.count())await n.click();}
 await page.locator('#coachStudentBody').waitFor({state:'visible',timeout:15000});if(current4a)await page.locator('.fjz4a-coach-shell').waitFor({state:'visible',timeout:20000});await page.waitForTimeout(450);
}
async function captureVersion(browser,label,url,vp,current4a=false){
 let page=await browser.newPage({viewport:vp});await login(page,url,'alumno01@test.local');await openStudentNutrition(page);if(current4a)await page.locator('.fjz4a-student-shell').waitFor({state:'visible',timeout:20000});await verifiedShot(page,label+'-student',false,current4a);await verifiedShot(page,label+'-student',true,current4a);await page.close();
 page=await browser.newPage({viewport:vp});await login(page,url,'coach@test.local');await openCoachNutrition(page,current4a);await verifiedShot(page,label+'-coach-editor',false,current4a);await verifiedShot(page,label+'-coach-editor',true,current4a);await page.close();
}
async function currentDetails(browser,vp,label){
 let page=await browser.newPage({viewport:vp});await login(page,current,'alumno01@test.local');await openStudentNutrition(page);await page.locator('.fjz4a-student-shell').waitFor({state:'visible',timeout:20000});
 await page.evaluate(()=>{const p=__fjzNutritionContextV22().cache.plan.plan;const m=p.meals.find(x=>x.id==='meal_qa_breakfast');if(m&&!m.options.some(x=>x.id==='opt_qa_visual'))m.options.push({id:'opt_qa_visual',name:'Opción QA Alternativa',items:[{id:'item_qa_visual',name:'QA Tostadas ficticias',grams:60,kcal:150,protein_g:6,carbs_g:28,fat_g:2,measure_type:'units',quantity:2,unit_name:'tostadas'}]});TeamFJZNutritionPremium.renderStudent()});
 const lunch=page.locator('.fjz4a-meal',{hasText:'Desayuno'});await lunch.scrollIntoViewIfNeeded();await verifiedShot(page,label+'-meal-options',false);await page.locator('#fjz4aCalculator').scrollIntoViewIfNeeded();await verifiedShot(page,label+'-calculator',false);await page.locator('.fjz4a-consumption').scrollIntoViewIfNeeded();await verifiedShot(page,label+'-consumption',false);await page.close();
 page=await browser.newPage({viewport:vp});await page.route('**/rest/v1/nutrition_plans*',route=>route.request().method()==='GET'?route.fulfill({status:200,contentType:'application/json',headers:{'content-range':'*/0'},body:'[]'}):route.continue());await login(page,current,'alumno02@test.local');await openStudentNutrition(page);await page.locator('.fjz4a-empty-state').waitFor({state:'visible',timeout:15000});await verifiedShot(page,label+'-empty-plan',false);await page.close();
 page=await browser.newPage({viewport:vp});await login(page,current,'alumno01@test.local');await page.route('**/rest/v1/nutrition_plans*',route=>route.request().method()==='GET'?route.abort('failed'):route.continue());await page.getByRole('button',{name:/^Nutrición$/}).first().click();await page.locator('.fjz4a-error-state').waitFor({state:'visible',timeout:15000});await verifiedShot(page,label+'-recoverable-error',false);await page.close();
}
(async()=>{const browser=await chromium.launch({headless:true});try{
 for(const vp of [{width:390,height:844},{width:1440,height:900}]){const s=vp.width+'x'+vp.height;await captureVersion(browser,'v2141-'+s,v2141,vp,false);await captureVersion(browser,'pre4a-'+s,pre4a,vp,false);await captureVersion(browser,'4a-'+s,current,vp,true)}
 for(const vp of [{width:360,height:800},{width:390,height:844},{width:430,height:932}])await currentDetails(browser,vp,'4a-'+vp.width+'x'+vp.height);
}finally{await browser.close()}console.log('TEAM FJZ V22 4A nutrition visual comparison captured with CSS/DPR/PNG verification')})().catch(e=>{console.error(e);process.exit(1)});
