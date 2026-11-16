import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")
required=[
 'meta name="fjz-v22-4b-progress-checkins-premium" content="22.4B"',
 'meta name="fjz-v22-agenda-repository-read" content="enabled"',
 'id="v22AgendaRepositoryCore"',
 'id="v22AgendaReadPolicyCore"',
 'agendaExactReadBack:true',
 'reminderReadBack:true',
 'duplicateCriticalWriteLocks:true',
 'renderCoachAgendaV81',
 'renderCoachStudentAgendaV81',
 'renderStudentAgendaV81',
]
for marker in required:
    if marker not in html: raise RuntimeError("V22 4C prerequisite missing: "+marker)

js=pathlib.Path("src/modules/agenda/agenda-premium.js").read_text(encoding="utf-8")
css=pathlib.Path("src/ui/agenda-premium.css").read_text(encoding="utf-8")
if "</script" in js.lower(): raise RuntimeError("V22 4C module contains closing script markup")
if re.search(r'\.channel\s*\(|setTimeout\s*\(|setInterval\s*\(|new\s+(?:Mutation|Performance)Observer',js):
    raise RuntimeError("V22 4C must not add realtime, timers or observers")

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V22 4C expected one consolidated stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]
html=html.replace("</head>",'<meta name="fjz-v22-4c-agenda-premium" content="22.4C">\n</head>',1)

# Route the inherited V8.1 Coach Agenda dispatcher to the premium hook. This edits the existing dispatcher;
# it does not add a render wrapper or a new navigation authority.
legacy_agenda_dispatch_old="""renderCoach=function(){
  if(coachTab==='agenda')return renderCoachAgendaV81();
  return _renderCoachV81Base()
};"""
legacy_agenda_dispatch_new="""renderCoach=function(){
  if(coachTab==='agenda'&&typeof window.__fjzRenderAgendaPremiumCoachV22==='function')return window.__fjzRenderAgendaPremiumCoachV22();
  if(coachTab==='agenda')return renderCoachAgendaV81();
  return _renderCoachV81Base()
};"""
if html.count(legacy_agenda_dispatch_old)!=1: raise RuntimeError("V22 4C legacy Agenda dispatcher anchor changed")
html=html.replace(legacy_agenda_dispatch_old,legacy_agenda_dispatch_new,1)

# Integrate 4C into the already-certified Coach dispatcher without wrapping global render.
coach_dispatch_old="""  window.renderCoach=function(){
    if(coachTab==='dashboard'&&typeof window.__fjzAthlete360ResumeRouteV22==='function'&&window.__fjzAthlete360ResumeRouteV22()&&typeof window.__fjzRenderAthlete360V22==='function')return window.__fjzRenderAthlete360V22();
    if(coachTab==='dashboard'&&typeof window.__fjzRenderCoachCommandCenterV22==='function')return window.__fjzRenderCoachCommandCenterV22();
    if(coachTab==='dashboard')return renderCoachDashboardV170();
    if(coachTab==='student'&&typeof window.__fjzRenderAthlete360V22==='function')return window.__fjzRenderAthlete360V22();
    return baseRenderCoachV170.apply(this,arguments);
  };"""
coach_dispatch_new="""  window.renderCoach=function(){
    if(coachTab==='dashboard'&&typeof window.__fjzAthlete360ResumeRouteV22==='function'&&window.__fjzAthlete360ResumeRouteV22()&&typeof window.__fjzRenderAthlete360V22==='function')return window.__fjzRenderAthlete360V22();
    if(coachTab==='dashboard'&&typeof window.__fjzRenderCoachCommandCenterV22==='function')return window.__fjzRenderCoachCommandCenterV22();
    if(coachTab==='dashboard')return renderCoachDashboardV170();
    if(coachTab==='agenda'&&typeof window.__fjzRenderAgendaPremiumCoachV22==='function')return window.__fjzRenderAgendaPremiumCoachV22();
    if(coachTab==='student'&&typeof window.__fjzRenderAthlete360V22==='function')return window.__fjzRenderAthlete360V22();
    return baseRenderCoachV170.apply(this,arguments);
  };"""
if html.count(coach_dispatch_old)!=1: raise RuntimeError("V22 4C Coach dispatcher anchor changed")
html=html.replace(coach_dispatch_old,coach_dispatch_new,1)

bridge=r'''<script id="v22AgendaPremiumAuthorityBridge">
(function(){
  let repoV22=null;
  const repository=()=>{
    if(!repoV22){
      if(!window.TeamFJZAgendaRepository?.createAgendaRepository)throw new Error('AgendaRepository no está disponible.');
      repoV22=window.TeamFJZAgendaRepository.createAgendaRepository({supabase:supabaseClient,ttlMs:15000});
    }
    return repoV22;
  };
  const selected=()=>{try{return student()}catch(_e){return null}};
  const athleteForStudent=s=>s?.id?cloudAthletes?.get?.(s.id)||null:null;
  window.__fjzAgendaPremiumContextV22=function(){
    const s=selected(),athlete=currentProfile?.role==='student'
      ?(typeof currentAthleteRowV73==='function'?currentAthleteRowV73():null)
      :athleteForStudent(s);
    return {
      profile:currentProfile,mode:mode,studentTab:studentTab,coachTab:coachTab,coachStudentTab:coachStudentTab,
      student:s,athlete,students:Array.isArray(state?.students)?state.students:[],userId:currentUser?.id||null
    };
  };
  async function loadAthlete(aid,force=false){
    if(!aid)throw new Error('No encuentro la ficha vinculada.');
    if(force)repository().clear(aid);
    return repository().listForAthlete(aid,{force:false});
  }
  async function loadStudent(force=false){
    let athlete=null;
    if(currentProfile?.role==='student')athlete=typeof currentAthleteRowV73==='function'?currentAthleteRowV73():null;
    else athlete=athleteForStudent(selected());
    if(!athlete?.id)throw new Error('No encuentro la agenda vinculada.');
    return loadAthlete(athlete.id,force);
  }
  async function loadCoach(force=false){
    if(currentProfile?.role!=='coach')return [];
    const jobs=(state?.students||[]).map(async s=>{
      const athlete=athleteForStudent(s);if(!athlete?.id)return null;
      try{return {student:s,athlete:{...athlete,name:s.name||athlete.name||'Alumno'},data:await loadAthlete(athlete.id,force)}}
      catch(e){
        // RLS-hidden portfolio rows are omitted fail-closed; transport/data errors remain explicit.
        if(e?.kind==='authorization')return null;
        throw e;
      }
    });
    const rows=await Promise.all(jobs);
    return rows.filter(Boolean);
  }
  function openAthlete(aid,tab='agenda'){
    const entry=(state?.students||[]).find(s=>String(athleteForStudent(s)?.id||'')===String(aid||''));
    if(!entry)return false;
    if(typeof openCoachStudentTabV235==='function')return openCoachStudentTabV235(entry.id,tab);
    state.selectedStudentId=entry.id;coachTab='student';coachStudentTab=tab;saveState?.();render?.();return true;
  }
  window.__fjzAgendaPremiumActionsV22={
    loadStudent,loadCoach,loadAthlete,
    backDashboard:()=>{coachTab='dashboard';render();return true},
    openAthlete,
    openAddReminder:()=>window.__fjzLegacyOpenAddReminderV22?.(),
    openLegacySchedule:()=>window.__fjzLegacyRenderCoachStudentAgendaV22?.(),
    deleteReminder:async(id,aid)=>{
      const before=await repository().getById(id);if(!before||String(before.athleteId)!==String(aid))throw new Error('El evento no pertenece al alumno seleccionado.');
      const ok=await window.__fjzLegacyDeleteReminderV22?.(id);
      repository().clear(aid);
      const after=await repository().getById(id);
      if(after)throw new Error('El servidor no confirmó la eliminación.');
      return ok!==false;
    },
    showError:e=>typeof toast==='function'?toast(typeof cloudErr==='function'?cloudErr(e):String(e?.message||e||'Error')):false
  };
})();
</script>
'''
runtime=bridge+'<script id="v22AgendaPremiumRuntime">\n'+js+'\n</script>\n'+r'''<script id="v22AgendaPremiumInstall">
(function(){
  if(!window.TeamFJZAgendaPremium?.install?.())throw new Error("TEAM FJZ V22 4C install failed");
  window.__fjzLegacyRenderStudentAgendaV22=window.renderStudentAgendaV81||globalThis.renderStudentAgendaV81;
  window.__fjzLegacyRenderCoachAgendaV22=window.renderCoachAgendaV81||globalThis.renderCoachAgendaV81;
  window.__fjzLegacyRenderCoachStudentAgendaV22=window.renderCoachStudentAgendaV81||globalThis.renderCoachStudentAgendaV81;
  window.__fjzLegacyOpenAddReminderV22=window.openAddReminderV81||globalThis.openAddReminderV81;
  window.__fjzLegacyDeleteReminderV22=window.deleteReminderV81||globalThis.deleteReminderV81;

  const studentAgenda4C=function(){return window.TeamFJZAgendaPremium.renderStudent(true)};
  const coachAgenda4C=function(){return window.TeamFJZAgendaPremium.renderCoach(true)};
  const coachAthleteAgenda4C=function(){return window.TeamFJZAgendaPremium.renderCoachAthlete(true)};
  window.renderStudentAgendaV81=studentAgenda4C;try{renderStudentAgendaV81=studentAgenda4C}catch(_e){}
  window.renderCoachAgendaV81=coachAgenda4C;try{renderCoachAgendaV81=coachAgenda4C}catch(_e){}
  window.renderCoachStudentAgendaV81=coachAthleteAgenda4C;try{renderCoachStudentAgendaV81=coachAthleteAgenda4C}catch(_e){}
  window.__fjzRenderAgendaPremiumCoachV22=coachAgenda4C;

  const athlete360Render=window.__fjzRenderAthlete360V22;
  if(typeof athlete360Render!=='function')throw new Error("TEAM FJZ V22 4C Athlete 360 hook missing");
  const athleteAgendaActive=()=>currentProfile?.role==='coach'&&coachTab==='student'&&(
    coachStudentTab==='agenda'||window.__fjzAthlete360StateV22?.sectionOverride==='agenda'
  );
  window.__fjzRenderAthlete360V22=function(){
    const out=athlete360Render.apply(this,arguments);
    if(athleteAgendaActive())queueMicrotask(()=>coachAthleteAgenda4C());
    return out;
  };
  const afterAthleteHydrate=window.__fjzAfterAthlete360HydrateV22;
  window.__fjzAfterAthlete360HydrateV22=function(payload){
    let out;try{out=afterAthleteHydrate?.apply(this,arguments)}catch(_e){}
    if(payload?.ok!==false&&athleteAgendaActive())queueMicrotask(()=>coachAthleteAgenda4C());
    return out;
  };
  const athleteNavigate=window.__fjzAthlete360NavigateV22;
  if(typeof athleteNavigate!=='function')throw new Error("TEAM FJZ V22 4C Athlete 360 navigation hook missing");
  window.__fjzAthlete360NavigateV22=function(tab){
    const out=athleteNavigate.apply(this,arguments);
    if(String(tab||'')==='agenda')queueMicrotask(()=>coachAthleteAgenda4C());
    return out;
  };
  const athleteHydrate=window.__fjzHydrateAthlete360V22;
  if(typeof athleteHydrate!=='function')throw new Error("TEAM FJZ V22 4C Athlete 360 hydrate hook missing");
  window.__fjzHydrateAthlete360V22=async function(){
    const out=await athleteHydrate.apply(this,arguments);
    if(athleteAgendaActive())await coachAthleteAgenda4C();
    return out;
  };

  window.__fjzAgendaPremiumRefreshV22=function(){
    try{
      const c=window.__fjzAgendaPremiumContextV22?.()||{};
      if(c.profile?.role==='student'&&c.studentTab==='agenda')return studentAgenda4C();
      if(c.profile?.role==='coach'&&c.coachTab==='agenda')return coachAgenda4C();
      if(c.profile?.role==='coach'&&c.coachTab==='student'&&c.coachStudentTab==='agenda')return coachAthleteAgenda4C();
    }catch(_e){}
  };
})();
</script>
'''
if html.count("</body>")!=1: raise RuntimeError("V22 4C body anchor mismatch")
html=html.replace("</body>",runtime+"</body>",1)

for marker in [
 'meta name="fjz-v22-4c-agenda-premium" content="22.4C"',
 'id="v22AgendaPremiumAuthorityBridge"','id="v22AgendaPremiumRuntime"','id="v22AgendaPremiumInstall"',
 "VERSION='22.4C'","TeamFJZAgendaRepository.createAgendaRepository","renderCoachAgendaV81=coachAgenda4C",
 "renderCoachStudentAgendaV81=coachAthleteAgenda4C","renderStudentAgendaV81=studentAgenda4C",
 "agendaExactReadBack:true","reminderReadBack:true","America/Argentina/Buenos_Aires"
]:
    if marker not in html: raise RuntimeError("V22 4C output marker missing: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V22 4C Agenda Premium injected",len(html))
