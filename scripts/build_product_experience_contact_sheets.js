const {chromium}=require('@playwright/test');const fs=require('fs'),path=require('path');
const dir=process.argv[2];if(!dir)throw new Error('usage: node build_product_experience_contact_sheets.js dir');
const versions=[['V21.41','v2141'],['V22 2B-V.1','v22-2bv1'],['V22 2B-V2','v22-2bv2']];
const vps=['mobile-360','mobile-390','mobile-430','desktop-1440'];
const states=['workout-initial','workout','series','history','session-detail','comments','comment-compose'];
(async()=>{const browser=await chromium.launch({headless:true});try{for(const vp of vps){for(const state of states){
 const imgs=[];for(const [name,prefix] of versions){const file=path.join(dir,prefix+'-'+vp+'-'+state+'.png');if(fs.existsSync(file))imgs.push({name,data:fs.readFileSync(file).toString('base64')})}
 if(imgs.length<2)continue;const page=await browser.newPage({viewport:{width:1800,height:1000}});
 await page.setContent('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#08090b;color:#f5f6f8;font-family:Arial,sans-serif;padding:22px}.title{font-size:22px;font-weight:900;margin-bottom:16px}.grid{display:grid;grid-template-columns:repeat('+imgs.length+',minmax(0,1fr));gap:14px;align-items:start}.cell{background:#101216;border:1px solid #292d35;border-radius:14px;padding:10px}.cell h2{font-size:14px;margin:0 0 9px;color:#ff6678}.cell img{width:100%;height:auto;display:block;border-radius:8px}</style><div class="title">TEAM FJZ · '+vp+' · '+state+'</div><div class="grid">'+imgs.map(x=>'<div class="cell"><h2>'+x.name+'</h2><img src="data:image/png;base64,'+x.data+'"></div>').join('')+'</div>');await page.screenshot({path:path.join(dir,'compare-'+vp+'-'+state+'.png'),fullPage:true});await page.close()
}}}finally{await browser.close()}console.log('PRODUCT_EXPERIENCE_CONTACT_SHEETS_OK')})().catch(e=>{console.error(e);process.exit(1)});
