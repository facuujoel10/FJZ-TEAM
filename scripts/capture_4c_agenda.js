const {chromium}=require('@playwright/test');
const fs=require('fs'),path=require('path');
const PASSWORD=process.env.FJZ_E2E_PASSWORD||'TEAMFJZ-Local-Only!22';
const out=process.argv[2]||'artifacts/4c-comparison';
const v21=process.argv[3]||'http://127.0.0.1:8001';
const pre=process.argv[4]||'http://127.0.0.1:8010';
const cur=process.argv[5]||'http://127.0.0.1:8000';
fs.mkdirSync(out,{recursive:true});

async function shot(p,n,full=false){
  const x=await p.evaluate(()=>({w:innerWidth,h:innerHeight,dpr:devicePixelRatio,sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth}));
  if(x.sw>x.cw+2)throw Error('overflow '+n+' '+JSON.stringify(x));
  await p.screenshot({path:path.join(out,n+(full?'-full':'-viewport')+'.png'),fullPage:full});
  fs.writeFileSync(path.join(out,n+(full?'-full':'-viewport')+'.json'),JSON.stringify(x,null,2));
}
async function both(p,n){await shot(p,n);await shot(p,n,true)}
async function focus(p,selector){
  const loc=p.locator(selector).first();
  if(await loc.count()){await loc.scrollIntoViewIfNeeded();await p.waitForTimeout(180)}
}
async function login(p,u,e){
  await p.goto(u);
  const g=p.locator('#authGate');
  if(await g.isVisible().catch(()=>false)){
    await p.locator('#authEmail').fill(e);
    await p.locator('#authPass').fill(PASSWORD);
    await p.locator('#authGate .btn.primary').click();
  }
  await g.waitFor({state:'hidden',timeout:20000});
}

async function student(p,u,l){
  await login(p,u,'alumno01@test.local');
  if(l.startsWith('v224c')){
    const agenda=p.getByRole('button',{name:'Agenda',exact:true}).first();
    await agenda.waitFor({state:'visible',timeout:15000});
    await agenda.click();
    await p.locator('.fjz4c-student').waitFor({state:'visible',timeout:20000});
    await focus(p,'.fjz4c-student');
  }else{
    await p.evaluate(()=>{studentTab='agenda';render()});
  }
  await p.waitForTimeout(350);
  await both(p,l+'-student-agenda');

  if(l.startsWith('v224c')){
    await p.evaluate(async()=>{
      const a=window.__fjzAgendaPremiumActionsV22;
      window.__fjzCaptureLoadStudent4C=a.loadStudent;
      a.loadStudent=async()=>({schedule:[],reminders:[]});
      await window.TeamFJZAgendaPremium.renderStudent(true);
    });
    await p.getByText('Sin fechas próximas',{exact:true}).waitFor({state:'visible',timeout:10000});
    await focus(p,'.fjz4c-student');
    await both(p,l+'-student-agenda-empty');

    await p.evaluate(async()=>{
      const a=window.__fjzAgendaPremiumActionsV22;
      a.loadStudent=async()=>{throw new Error('QA · error recuperable de lectura')};
      await window.TeamFJZAgendaPremium.renderStudent(true);
    });
    await p.locator('.fjz4c-error').waitFor({state:'visible',timeout:10000});
    await focus(p,'.fjz4c-error');
    await both(p,l+'-student-agenda-error');

    await p.evaluate(async()=>{
      const a=window.__fjzAgendaPremiumActionsV22;
      a.loadStudent=window.__fjzCaptureLoadStudent4C;
      delete window.__fjzCaptureLoadStudent4C;
      await window.TeamFJZAgendaPremium.renderStudent(true);
    });
    await p.locator('.fjz4c-calendar').waitFor({state:'visible',timeout:15000});
    await focus(p,'.fjz4c-student');
    await both(p,l+'-student-agenda-recovered');
  }

  const home=p.getByRole('button',{name:'Inicio',exact:true}).first();
  if(await home.count()){
    await home.click();
    await p.waitForTimeout(500);
    await p.evaluate(()=>window.scrollTo({top:0,left:0,behavior:'auto'}));
    await both(p,l+'-student-home');
  }
}

async function coach(p,u,l){
  await login(p,u,'coach@test.local');
  if(l.startsWith('v224c')){
    await p.evaluate(()=>window.__fjzCoachNavigateV22?.('agenda'));
    await p.locator('.fjz4c-coach[data-4c-ready="true"]').waitFor({state:'visible',timeout:20000});
  }else{
    await p.evaluate(()=>{coachTab='agenda';render()});
  }
  await p.waitForTimeout(450);
  await both(p,l+'-coach-agenda');

  if(!l.startsWith('v224c'))return;

  const event=p.locator('.fjz4c-coach [data-4c-event]:visible').first();
  if(await event.count()){
    await event.click();
    await p.locator('.fjz4c-detail[data-event-id]').waitFor({state:'visible',timeout:10000});
    await focus(p,'.fjz4c-detail[data-event-id]');
    await both(p,l+'-coach-agenda-detail');
  }

  await p.evaluate(()=>window.__fjzCoachNavigateV22?.('dashboard'));
  await p.waitForTimeout(350);
  const search=p.locator('#fjz3aStudentSearch');
  if(await search.count())await search.fill('ALUMNO 01');
  const row=p.locator('#studentList .student-row',{hasText:'TEST ALUMNO 01'}).first();
  if(!(await row.count()))return;

  await row.getByRole('button',{name:/Abrir/i}).click();
  await p.locator('.fjz3b-header').waitFor({state:'visible',timeout:15000});
  await p.evaluate(()=>window.__fjzAthlete360NavigateV22?.('agenda'));
  await p.locator('#fjz4cAddReminder').waitFor({state:'visible',timeout:15000});
  await p.locator('.fjz4c-coach-athlete').waitFor({state:'visible',timeout:15000});
  await p.evaluate(()=>window.scrollTo({top:0,left:0,behavior:'auto'}));
  await both(p,l+'-athlete360-agenda');

  await p.locator('#fjz4cAddReminder').click();
  await p.locator('#v165Title').waitFor({state:'visible',timeout:10000});
  await both(p,l+'-athlete360-new-reminder-form');
  await p.evaluate(()=>closeModal());
  await p.locator('#v165Title').waitFor({state:'detached',timeout:10000});

  await p.locator('#fjz4cEditWeekly').click();
  await p.locator('.v81-config-row').first().waitFor({state:'visible',timeout:15000});
  await focus(p,'.v81-config-row');
  await both(p,l+'-athlete360-weekly-editor');
}

(async()=>{
  const b=await chromium.launch({headless:true});
  try{
    for(const vp of[{width:390,height:844},{width:1440,height:900}]){
      for(const [l,u] of[['v2141',v21],['pre4c',pre],['v224c',cur]]){
        let p=await b.newPage({viewport:vp});
        await student(p,u,l+'-'+vp.width+'x'+vp.height);
        await p.close();
        p=await b.newPage({viewport:vp});
        await coach(p,u,l+'-'+vp.width+'x'+vp.height);
        await p.close();
      }
    }
  }finally{await b.close()}
  console.log('TEAM FJZ V22 4C comparative evidence captured');
})().catch(e=>{console.error(e);process.exit(1)});
