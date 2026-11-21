const {test,expect}=require('@playwright/test');

/* Staging-specific mobile geometry regression, using isolated local QA accounts.
   Never targets production; executed only against the local V22 QA build. */
const PASSWORD='TEAMFJZ-Local-Only!22';
async function login(page,email){
  await page.goto('/');
  const gate=page.locator('#authGate');
  if(await gate.isVisible().catch(()=>false)){
    await page.locator('#authEmail').fill(email);
    await page.locator('#authPass').fill(PASSWORD);
    await gate.getByRole('button',{name:/Ingresar/i}).first().click();
  }
  await expect(gate).toBeHidden({timeout:20000});
}
async function geometry(page,targets=[]){
  const report=await page.evaluate(selectors=>{
    const visible=e=>{const r=e.getBoundingClientRect(),c=getComputedStyle(e);return c.display!=='none'&&c.visibility!=='hidden'&&r.width>1&&r.height>1};
    const outer=document.documentElement;
    const widths={viewport:innerWidth,document:outer.scrollWidth,client:outer.clientWidth};
    const offenders=[];
    const clipped=[];
    for(const selector of selectors){
      const els=[...document.querySelectorAll(selector)].filter(visible);
      for(const el of els){
        const r=el.getBoundingClientRect();
        if(r.left < -3||r.right>innerWidth+3)
          offenders.push({selector,tag:el.tagName,cls:String(el.className||'').slice(0,100),left:Math.round(r.left),right:Math.round(r.right)});
        const style=getComputedStyle(el);
        const scrollAllowed=/auto|scroll/.test(style.overflowX);
        if(!scrollAllowed&&el.scrollWidth>el.clientWidth+3)
          clipped.push({selector,cls:String(el.className||'').slice(0,100),scrollWidth:el.scrollWidth,clientWidth:el.clientWidth});
      }
    }
    return {widths,offenders,clipped};
  },targets);
  expect(report.widths.document,'Document overflow horizontal').toBeLessThanOrEqual(report.widths.client+2);
  expect(report.offenders,'Card bounds must stay inside viewport').toEqual([]);
  expect(report.clipped,'Cards must not hide overflowing text/content').toEqual([]);
}
async function assertNoCardOverlap(page,selector){
  const collisions=await page.evaluate(sel=>{
    const visible=el=>{const r=el.getBoundingClientRect(),cs=getComputedStyle(el);return cs.display!=='none'&&r.width>1&&r.height>1};
    const nodes=[...document.querySelectorAll(sel)].filter(visible);
    const issues=[];
    for(let i=1;i<nodes.length;i++){
      const a=nodes[i-1].getBoundingClientRect(),b=nodes[i].getBoundingClientRect();
      if(a.bottom>b.top+3&&Math.min(a.right,b.right)-Math.max(a.left,b.left)>8)
        issues.push({first:i-1,second:i,overlap:Math.round(a.bottom-b.top)});
    }
    return issues;
  },selector);
  expect(collisions,'Visible mobile cards may not overlap').toEqual([]);
}
async function screenshot(page,name){
  await page.screenshot({path:'test-results/'+name+'.png',fullPage:true,animations:'disabled'});
}
test.describe('Staging V21.41-first mobile UI geometry',()=>{
  test('Alumno: inicio, entrenamiento, check-in e historial no desbordan ni pisan tarjetas',async({page},testInfo)=>{
    await page.setViewportSize({width:390,height:844});
    await login(page,'alumno01@test.local');
    await expect(page.locator('.v224-student-hero')).toBeVisible();
    await geometry(page,['.v224-student-hero','.v224-kpi-card','.v224-plan-card','.v224-day-row','.v224-coach-card','.v224-recent-card']);
    await assertNoCardOverlap(page,'.v224-dashboard-grid > *');
    await screenshot(page,'stage-v21-mobile-home-'+testInfo.project.name);
    await page.locator('.v224-day-action').first().click();
    await expect(page.locator('#view .session-card').first()).toBeVisible();
    await geometry(page,['#view .session-card','#view .set-grid','#view .set-grid input']);
    await screenshot(page,'stage-v21-mobile-workout-'+testInfo.project.name);
    await page.evaluate(()=>{studentTab='tracking';render()});
    await expect(page.locator('#studentSubBody')).toBeVisible();
    await geometry(page,['#studentSubBody>.card','#studentSubBody .form-grid','#studentSubBody input.input']);
    await screenshot(page,'stage-v21-mobile-checkin-'+testInfo.project.name);
    await page.evaluate(()=>{studentTab='history';render()});
    await geometry(page,['#studentSubBody>.card','#studentSubBody .history-item']);
  });
  test('Alumno: nutrición cambia comida y conserva registro, sin desbordar',async({page},testInfo)=>{
    await page.setViewportSize({width:360,height:800});
    await login(page,'alumno01@test.local');
    await page.getByRole('button',{name:'Nutrición'}).first().click();
    await expect(page.locator('.fjz4a-student-shell')).toBeVisible({timeout:20000});
    const tabs=page.locator('.fjz4a-student-meal-nav [data-4a-action="student-meal"]');
    expect(await tabs.count(),'At least two meals are required for selector QA').toBeGreaterThan(1);
    for(let i=0;i<await tabs.count();i++){
      await tabs.nth(i).click();
      await expect(tabs.nth(i)).toHaveAttribute('aria-selected','true');
      const meals=page.locator('.fjz4a-student-meals-v21 > .fjz4a-meal:visible');
      await expect(meals).toHaveCount(1);
      await geometry(page,['.fjz4a-student-shell','.fjz4a-meals','.fjz4a-meal:visible','.fjz4a-macros:visible','.nutrition-log-row:visible']);
    }
    await assertNoCardOverlap(page,'.fjz4a-student-shell > section');
    await screenshot(page,'stage-v21-mobile-nutrition-'+testInfo.project.name);
  });
  test('Coach: navigation is single on mobile and athlete cards fit',async({page},testInfo)=>{
    await page.setViewportSize({width:430,height:932});
    await login(page,'coach@test.local');
    await expect(page.locator('.fjz3a-command-center')).toBeVisible({timeout:20000});
    await geometry(page,['.fjz3a-v21-mobile .v225-coach-hero','.fjz3a-v21-mobile .v225-kpi-card','#fjzCoachGlobalNav']);
    await assertNoCardOverlap(page,'.fjz3a-v21-mobile .v225-kpi-grid > *');
    await screenshot(page,'stage-v21-mobile-coach-'+testInfo.project.name);
    const nav=page.locator('#fjzCoachGlobalNav .fjz-coach-mobile-links');
    await expect(nav).toBeVisible();
    const before=await nav.boundingBox();
    await page.evaluate(()=>window.scrollTo(0,Math.max(0,document.documentElement.scrollHeight-innerHeight)));
    const after=await nav.boundingBox();
    expect(before&&after).toBeTruthy();
    expect(Math.abs(before.y-after.y),'Bottom navigation stays fixed while scrolling').toBeLessThanOrEqual(3);
    await expect(page.locator('#view .fjz3a-mobile-nav:visible')).toHaveCount(0);
    const row=page.locator('#studentList .student-row').first();
    await expect(row).toBeVisible({timeout:15000});
    await row.getByRole('button',{name:/Abrir/i}).click();
    await expect(page.locator('.fjz3b-header')).toBeVisible({timeout:15000});
    await geometry(page,['.fjz3b-header','.fjz3b-layout','.fjz3b-main','.fjz3b-section-context']);
    await screenshot(page,'stage-v21-mobile-athlete-'+testInfo.project.name);
  });
});
