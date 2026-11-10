const {chromium}=require('@playwright/test');const fs=require('fs'),path=require('path');
const dir=process.argv[2];if(!dir)throw new Error('usage: node build_visual_contact_sheets.js dir');
const versions=[['V21.41','v2141'],['V22 2B','v22-2b'],['V22 2B-V','v22-2bv']];
const vps=['mobile-390','desktop-1440'],states=['workout','series','history','session-detail','comments','comment-compose'];
(async()=>{const browser=await chromium.launch({headless:true});try{for(const vp of vps){for(const state of states){
 const imgs=[];for(const [name,prefix] of versions){const file=path.join(dir,prefix+'-'+vp+'-'+state+'.png');if(fs.existsSync(file))imgs.push({name,data:fs.readFileSync(file).toString('base64')})}
 if(imgs.length<2)continue;
 const page=await browser.newPage({viewport:{width:1600,height:1000}});
 await page.setContent('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#09090b;color:#f5f6f8;font-family:Arial,sans-serif;padding:24px}.title{font-size:22px;font-weight:800;margin-bottom:18px}.grid{display:grid;grid-template-columns:repeat('+imgs.length+',minmax(0,1fr));gap:16px}.cell{background:#111216;border:1px solid #2a2d34;border-radius:16px;padding:12px}.cell h2{font-size:15px;margin:0 0 10px;color:#ff6678}.cell img{width:100%;height:auto;display:block;border-radius:10px}</style><div class="title">TEAM FJZ · '+vp+' · '+state+'</div><div class="grid">'+imgs.map(x=>'<div class="cell"><h2>'+x.name+'</h2><img src="data:image/png;base64,'+x.data+'"></div>').join('')+'</div>');
 await page.screenshot({path:path.join(dir,'compare-'+vp+'-'+state+'.png'),fullPage:true});await page.close();
 }} }finally{await browser.close()}console.log('VISUAL_CONTACT_SHEETS_OK')})().catch(e=>{console.error(e);process.exit(1)});
