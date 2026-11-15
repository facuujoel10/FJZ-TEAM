import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")
required=[
 'meta name="fjz-nutrition-ux-final-polish" content="22.4A-UX"',
 'meta name="fjz-athlete-360-workspace" content="22.3B"',
 'meta name="fjz-coach-analytics-followup" content="22.3C"',
 'meta name="fjz-save-integrity" content="21.03"',
 'meta name="fjz-global-save-integrity" content="21.04"',
 'meta name="fjz-checkin-resubmission-lifecycle" content="21.05"',
 "checkinWriteReadBack:true","measurementReadBack:true","duplicateCheckinGuard:true",
 "from('weekly_checkins')","from('body_measurements')","from('progress_photos')","storage.from('progress-photos')",
]
for marker in required:
    if marker not in html: raise RuntimeError("V22 4B prerequisite missing: "+marker)
js=pathlib.Path("src/modules/tracking/progress-checkins-premium.js").read_text(encoding="utf-8")
css=pathlib.Path("src/ui/progress-checkins-premium.css").read_text(encoding="utf-8")
if "</script" in js.lower(): raise RuntimeError("V22 4B module contains closing script markup")
if re.search(r'\b(?:window\.)?render\s*=\s*function|const\s+_render\w*\s*=\s*render\b',js): raise RuntimeError("V22 4B must not wrap global render")
if re.search(r'\.channel\s*\(|setTimeout\s*\(|setInterval\s*\(|new\s+(?:Mutation|Performance)Observer',js): raise RuntimeError("V22 4B must not add realtime, timers or observers")
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V22 4B expected one consolidated stylesheet")
sm=styles[0];html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]
html=html.replace("</head>",'<meta name="fjz-v22-4b-progress-checkins-premium" content="22.4B">\n</head>',1)
bridge=r'''<script id="v22ProgressCheckinsAuthorityBridge">
(function(){
  const cloneV22=x=>{try{return JSON.parse(JSON.stringify(x))}catch(_e){return x}};
  const numberOrNull=id=>{const raw=document.getElementById(id)?.value;if(raw==null||String(raw).trim()==='')return null;const v=Number(String(raw).replace(',','.'));return Number.isFinite(v)?v:null};
  window.__fjzProgressCheckinsContextV22=function(){
    let s=null,aid=null;try{s=student()}catch(_e){}try{aid=trackingAthleteId()}catch(_e){}
    return {profile:typeof currentProfile!=='undefined'?currentProfile:null,userId:typeof currentUser!=='undefined'?currentUser?.id:null,studentTab:typeof studentTab!=='undefined'?studentTab:null,coachTab:typeof coachTab!=='undefined'?coachTab:null,coachStudentTab:typeof coachStudentTab!=='undefined'?coachStudentTab:null,student:s,athleteId:aid,tracking:typeof trackingCache!=='undefined'?cloneV22(trackingCache):{checkins:[],measurements:[],photos:[]},supabase:typeof supabaseClient!=='undefined'?supabaseClient:null};
  };
  async function saveMeasurement4B(){
    if(!cloudEnabled||!supabaseClient)throw new Error('Las mediciones requieren conexión con la nube.');
    const aid=typeof trackingAthleteId==='function'?trackingAthleteId():null;if(!aid)throw new Error('No encuentro la ficha vinculada.');
    try{const fresh=await window.__fjzEnsureFreshAuthV194?.(false);if(fresh===false)throw new Error('Tu sesión necesita actualizarse antes de guardar.')}catch(e){if(String(e?.message||'').includes('actualizarse'))throw e}
    const date=document.getElementById('mDate')?.value||(typeof dateInputToday==='function'?dateInputToday():new Date().toISOString().slice(0,10));
    const payload={athlete_id:aid,student_id:typeof trackingStudentUserId==='function'?trackingStudentUserId():currentUser?.id||null,measured_on:date,weight_kg:numberOrNull('mWeight'),waist_cm:numberOrNull('mWaist'),abdomen_cm:numberOrNull('mAbd'),hip_cm:numberOrNull('mHip'),chest_cm:numberOrNull('mChest'),arm_left_cm:numberOrNull('mArmL'),thigh_left_cm:numberOrNull('mThighL')};
    const limits={weight_kg:[20,400],waist_cm:[20,300],abdomen_cm:[20,300],hip_cm:[20,300],chest_cm:[20,300],arm_left_cm:[10,100],thigh_left_cm:[15,150]};
    for(const [key,[lo,hi]] of Object.entries(limits)){const v=payload[key];if(v!=null&&(v<lo||v>hi))throw new Error('Revisá el valor de '+key.replaceAll('_',' ')+'.')}
    if(Object.keys(limits).every(k=>payload[k]==null))throw new Error('Ingresá al menos un valor antes de guardar.');
    const {data:written,error}=await supabaseClient.from('body_measurements').upsert(payload,{onConflict:'athlete_id,measured_on'}).select('*').single();if(error)throw error;
    const {data:readBack,error:readErr}=await supabaseClient.from('body_measurements').select('*').eq('athlete_id',aid).eq('measured_on',date).single();if(readErr)throw readErr;
    const same=(a,b)=>a==null&&b==null||Number(a)===Number(b);if(!readBack?.id||Object.keys(limits).some(k=>!same(readBack[k],payload[k])))throw new Error('La nube no confirmó todos los valores de la medición.');
    try{const prev=Array.isArray(trackingCache?.measurements)?trackingCache.measurements:[];trackingCache.measurements=[readBack,...prev.filter(x=>String(x?.id)!==String(readBack.id)&&String(x?.measured_on)!==String(date))].sort((a,b)=>String(b.measured_on||'').localeCompare(String(a.measured_on||'')));trackingLoadedFor=aid}catch(_e){}
    window.__fjzRecordConfirmedSaveV303?.('measurement','Medición guardada',{id:readBack.id,athleteId:aid,date});window.__fjzConfirmSavedV264?.('Medición guardada','La medición quedó confirmada en la nube.');return readBack;
  }
  window.__fjzProgressCheckinsActionsV22={
    load:force=>loadTracking(!!force),submitCheckin:()=>window.submitWeeklyCheckin?.(),submitMeasurement:()=>saveMeasurement4B(),uploadPhoto:()=>window.uploadProgressPhoto?.(),signedPhoto:path=>signedPhotoUrl(path),saveFeedback:id=>window.saveCheckinFeedback?.(id),editMeasurement:id=>window.openEditMeasurementV176?.(id),showModal:body=>showModal(body),showError:msg=>typeof toast==='function'?toast(String(msg||'Error')):false,today:()=>typeof dateInputToday==='function'?dateInputToday():new Date().toISOString().slice(0,10),weekStart:()=>typeof weekStartISO==='function'?weekStartISO():new Date().toISOString().slice(0,10),cloudError:e=>typeof cloudErr==='function'?cloudErr(e):String(e?.message||e||'Error')
  };
})();
</script>
'''
runtime=bridge+'<script id="v22ProgressCheckinsPremiumRuntime">\n'+js+'\n</script>\n'+r'''<script id="v22ProgressCheckinsPremiumInstall">
(function(){
  if(!window.TeamFJZProgressCheckinsPremium?.install?.())throw new Error("TEAM FJZ V22 4B install failed");
  window.__fjzRenderTrackingStudentLegacyV22=window.renderTrackingStudent||globalThis.renderTrackingStudent;
  const renderStudent4B=function(){return window.TeamFJZProgressCheckinsPremium.renderStudent()};
  window.renderTrackingStudent=renderStudent4B;try{renderTrackingStudent=renderStudent4B}catch(_e){}
  const previousAfterHydrate=window.__fjzAfterAthlete360HydrateV22;
  window.__fjzAfterAthlete360HydrateV22=function(payload){
    try{previousAfterHydrate?.(payload)}catch(_e){}
    if(payload?.ok===false)return;
    const state=window.__fjzAthlete360StateV22;
    const section=state?.sectionOverride||(typeof coachStudentTab!=='undefined'&&coachStudentTab==='tracking'?'checkins':null);
    if(section==='progress'||section==='checkins')window.TeamFJZProgressCheckinsPremium.renderCoachSection(section);
  };
  window.__fjzProgressCheckinsPremiumV22=window.TeamFJZProgressCheckinsPremium;
})();
</script>
'''
html=html.replace("</body>",runtime+"</body>",1)
for marker in ['meta name="fjz-v22-4b-progress-checkins-premium" content="22.4B"','id="v22ProgressCheckinsAuthorityBridge"','id="v22ProgressCheckinsPremiumRuntime"','id="v22ProgressCheckinsPremiumInstall"',"VERSION='22.4B'","Check-in guardado correctamente.","Tu evolución, sin ruido","weekly_checkins","body_measurements","progress_photos","progress-photos","duplicateCheckinGuard:true","measurementReadBack:true","TeamFJZProgressCheckinsPremium.renderStudent","TeamFJZProgressCheckinsPremium.renderCoachSection"]:
    if marker not in html: raise RuntimeError("V22 4B output marker missing: "+marker)
p.write_text(html,encoding="utf-8")
print("TEAM FJZ V22 4B Progress + Check-ins Premium injected",len(html))
