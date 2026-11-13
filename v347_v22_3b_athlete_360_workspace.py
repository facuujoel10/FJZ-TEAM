import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")
required=[
 'meta name="fjz-coach-command-center" content="22.3A"',
 'meta name="fjz-v22-2c-intelligent-training" content="enabled"',
 'meta name="fjz-comment-ok-exercise-focus" content="21.29"',
 'meta name="fjz-mobile-workout-stability" content="21.41"',
 'cloudConfirmationBeforeSuccess:true',
 'id="v22CoachCommandCenterAuthorityBridge"',
]
for marker in required:
    if marker not in html: raise RuntimeError("V22 3B prerequisite missing: "+marker)
js=pathlib.Path("src/modules/coach/athlete-360.js").read_text(encoding="utf-8")
css=pathlib.Path("src/ui/athlete-360.css").read_text(encoding="utf-8")
if "</script" in js.lower(): raise RuntimeError("V22 3B module contains closing script markup")
active="""window.__fjzRenderLegacyCoachStudentV22=function(){return baseRenderCoachV170.apply(this,arguments);};
  window.renderCoach=function(){
    if(coachTab==='dashboard'&&typeof window.__fjzAthlete360ResumeRouteV22==='function'&&window.__fjzAthlete360ResumeRouteV22()&&typeof window.__fjzRenderAthlete360V22==='function')return window.__fjzRenderAthlete360V22();
    if(coachTab==='dashboard'&&typeof window.__fjzRenderCoachCommandCenterV22==='function')return window.__fjzRenderCoachCommandCenterV22();
    if(coachTab==='dashboard')return renderCoachDashboardV170();
    if(coachTab==='student'&&typeof window.__fjzRenderAthlete360V22==='function')return window.__fjzRenderAthlete360V22();
    return baseRenderCoachV170.apply(this,arguments);
  };"""
before="""window.renderCoach=function(){
    if(coachTab==='dashboard'&&typeof window.__fjzRenderCoachCommandCenterV22==='function')return window.__fjzRenderCoachCommandCenterV22();
    if(coachTab==='dashboard')return renderCoachDashboardV170();
    return baseRenderCoachV170.apply(this,arguments);
  };"""
if html.count(before)!=1: raise RuntimeError("V22 3B active Coach dispatcher authority changed")
html=html.replace(before,active,1)
legacy_label='ATHLETE WORKSPACE · TEAM FJZ'
if legacy_label not in html: raise RuntimeError("V22 3B legacy workspace label missing")
html=html.replace(legacy_label,'FICHA DEL ALUMNO · TEAM FJZ')
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V22 3B expected one consolidated stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]
html=html.replace("</head>",'<meta name="fjz-athlete-360-workspace" content="22.3B">\n</head>',1)
bridge=r'''<script id="v22Athlete360AuthorityBridge">
window.__fjzAthlete360ContextV22=function(){
  let s=null;try{s=student()}catch(_e){}
  const athlete=s?.id?cloudAthletes?.get?.(s.id)||null:null;
  return {profile:currentProfile,coachTab:coachTab,coachStudentTab:coachStudentTab,selectedStudentId:state?.selectedStudentId||'',student:s,athlete:athlete,supabase:supabaseClient};
};
window.__fjzAthlete360ResumeRouteV22=function(){
  if(currentProfile?.role!=='coach'||coachTab!=='dashboard')return false;
  let route=null;try{route=JSON.parse(sessionStorage.getItem('team-fjz-v22-athlete360-route')||'null')}catch(_e){}
  const sid=String(route?.studentId||''),target=(state?.students||[]).find(x=>String(x?.id||'')===sid);
  if(!sid||!target)return false;
  state.selectedStudentId=target.id;saveState();
  coachStudentTab=String(route?.tab||'summary');coachTab='student';return true;
};
window.__fjzAthlete360NavigateV22=function(tab){
  coachStudentTab=tab||'summary';render();return true;
};
window.__fjzAthlete360ReturnV22=function(){
  coachTab='dashboard';render();return true;
};
window.__fjzAthlete360LoadLegacyDataV22=async function(expectedStudentId,forceRead){
  const cloneV22=x=>{try{return JSON.parse(JSON.stringify(x))}catch(_e){return x}};
  const current=()=>{try{return student()}catch(_e){return null}};
  const s=current();
  if(!s||String(s.id)!==String(expectedStudentId||''))return {cancelled:true};
  const jobs=[];
  try{
    const aid=typeof trackingAthleteId==='function'?trackingAthleteId():null;
    const ready=aid&&typeof trackingLoadedFor!=='undefined'&&trackingLoadedFor===aid&&typeof trackingCache!=='undefined'&&trackingCache&&Array.isArray(trackingCache.measurements)&&Array.isArray(trackingCache.checkins);
    if(aid&&typeof loadTracking==='function'&&(forceRead||!ready))jobs.push(loadTracking(false));
  }catch(_e){}
  try{
    const aid=typeof nutritionAthleteId==='function'?nutritionAthleteId():null;
    const ready=aid&&typeof nutritionLoadedAthlete!=='undefined'&&nutritionLoadedAthlete===aid&&typeof nutritionFoodsLoaded!=='undefined'&&nutritionFoodsLoaded===true&&typeof nutritionCache!=='undefined'&&nutritionCache;
    if(aid&&(forceRead||!ready)&&typeof loadNutrition==='function')jobs.push(loadNutrition(false,typeof dateInputToday==='function'?dateInputToday():undefined));
  }catch(_e){}
  await Promise.allSettled(jobs);
  const after=current();
  if(!after||String(after.id)!==String(expectedStudentId||'')||String(state?.selectedStudentId||'')!==String(expectedStudentId||''))return {cancelled:true};
  return {
    tracking:typeof trackingCache!=='undefined'?cloneV22(trackingCache):{checkins:[],measurements:[],photos:[]},
    nutrition:typeof nutritionCache!=='undefined'?cloneV22(nutritionCache):null
  };
};
</script>
'''
runtime=bridge+'<script id="v22Athlete360Runtime">\n'+js+'\n</script>\n<script id="v22Athlete360Install">\nif(!window.TeamFJZAthlete360?.install?.())throw new Error("TEAM FJZ V22 3B install failed");\n</script>\n'
if "</body>" not in html: raise RuntimeError("V22 3B body anchor missing")
html=html.replace("</body>",runtime+"</body>",1)
markers=[
 'meta name="fjz-athlete-360-workspace" content="22.3B"','id="v22Athlete360AuthorityBridge"','id="v22Athlete360Runtime"',
 "VERSION='22.3B'","__fjzRenderLegacyCoachStudentV22","__fjzRenderAthlete360V22","__fjzAthlete360LoadLegacyDataV22","__fjzAthlete360ResumeRouteV22",
 "if(coachTab==='student'&&typeof window.__fjzRenderAthlete360V22==='function')",
 'cloudConfirmationBeforeSuccess:true','meta name="fjz-mobile-workout-stability" content="21.41"',
 "firstReviewCardsDisabledV327:true","sessionSuccessRequiresDoubleVerification:true"
]
for marker in markers:
    if marker not in html: raise RuntimeError("V22 3B output marker missing: "+marker)
body=re.search(r'<script id="v22Athlete360Runtime">(.*?)</script>',html,re.S)
if not body: raise RuntimeError("V22 3B runtime missing")
if re.search(r'\b(?:window\.)?render\s*=\s*function|const\s+_render\w*\s*=\s*render\b',body.group(1)):
    raise RuntimeError("V22 3B must not add a global render wrapper")
p.write_text(html,encoding="utf-8")
print("TEAM FJZ V22 3B Athlete 360 Workspace injected",len(html))
