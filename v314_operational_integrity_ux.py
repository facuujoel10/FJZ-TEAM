import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "intervals":len(re.findall(r"setInterval\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

before=metrics(html)

for marker in [
    'meta name="fjz-review-calendar-authority" content="21.13"',
    'id="v312ReviewAgendaAuthorityRuntime"',
    "injectAgendaDatesV313",
    "Fechas agendadas",
    "saveReminderV81",
    "saveStudentScheduleV81",
]:
    if marker not in html:
        raise RuntimeError("V21.14 prerequisite missing "+marker)

css=r"""
/* TEAM FJZ · V21.14 OPERATIONAL INTEGRITY UX */
.v314-agenda-link{
  margin:0 0 12px!important;
  padding:12px 13px!important;
  border:1px solid #2d3139!important;
  background:#0e1014!important;
}
.v314-agenda-link.ok{border-color:rgba(71,210,137,.28)!important;background:rgba(71,210,137,.045)!important}
.v314-agenda-link.warn{border-color:rgba(255,166,69,.3)!important;background:rgba(255,166,69,.05)!important}
.v314-agenda-link strong{display:block;font-size:11px;color:#f2f4f6}
.v314-agenda-link span{display:block;margin-top:4px;font-size:9px;line-height:1.45;color:#9198a3}
.v314-empty-dates{
  padding:13px;border:1px dashed #343943;border-radius:12px;background:#0c0e12;
  color:#8f96a1;font-size:9px;line-height:1.5;text-align:center;
}
"""
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V21.14 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

runtime=r"""
<script id="v314OperationalIntegrityUxRuntime">
(function(){
  const VERSION='21.14';
  let linkCache={aid:null,at:0,row:null,inflight:null};

  function coachAgendaAthleteIdV314(){
    try{
      const s=student?.();
      const a=coachAthleteV235?.(s);
      if(a?.id)return String(a.id);
    }catch(_e){}
    try{
      const id=athleteId?.();
      if(id)return String(id);
    }catch(_e){}
    return '';
  }

  async function loadAgendaTargetV314(force=false){
    const aid=coachAgendaAthleteIdV314();
    if(!aid||!cloudEnabled||!supabaseClient)return null;
    if(!force&&linkCache.aid===aid&&linkCache.row&&Date.now()-linkCache.at<30000)return linkCache.row;
    if(linkCache.inflight)return linkCache.inflight;
    linkCache.inflight=(async()=>{
      const {data,error}=await supabaseClient.from('athletes')
        .select('id,name,user_id,client_id')
        .eq('id',aid).single();
      if(error)throw error;
      linkCache={aid,at:Date.now(),row:data,inflight:null};
      return data;
    })().finally(()=>{linkCache.inflight=null});
    return linkCache.inflight;
  }

  async function injectCoachAgendaLinkV314(force=false){
    if(!(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='agenda'))return;
    const host=el('coachStudentBody')||el('view');if(!host)return;
    el('v314AgendaLink')?.remove();
    let row=null;
    try{row=await loadAgendaTargetV314(force)}catch(e){
      console.warn('TEAM FJZ V21.14 agenda target',e);return;
    }
    if(!(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='agenda'))return;
    if(!row)return;
    const linked=!!row.user_id;
    const card=document.createElement('div');
    card.id='v314AgendaLink';
    card.className='card v314-agenda-link '+(linked?'ok':'warn');
    card.innerHTML=linked
      ?'<strong>✓ Cuenta de alumno vinculada</strong><span>Las fechas y recordatorios que guardes acá pueden mostrarse en Inicio y Agenda del alumno.</span>'
      :'<strong>⚠ Alumno sin cuenta vinculada</strong><span>Podés guardar la fecha para tu organización, pero el alumno no podrá verla en su app hasta que su cuenta quede vinculada.</span>';
    host.prepend(card);
  }

  // Keep "Fechas agendadas" visible even when there are no future items.
  async function ensureStudentAgendaEmptyStateV314(force=false){
    if(!(currentProfile?.role==='student'&&mode==='student'&&studentTab==='agenda'))return;
    let data=null;
    try{data=await window.__fjzLoadOwnAppointmentsV312?.(force)}catch(e){
      console.warn('TEAM FJZ V21.14 student agenda state',e);return;
    }
    if(!(currentProfile?.role==='student'&&mode==='student'&&studentTab==='agenda'))return;
    const host=el('studentSubBody')||el('view');if(!host)return;
    if(el('v313StudentAgendaDates'))return;
    const section=document.createElement('section');
    section.id='v313StudentAgendaDates';
    section.className='card v310-student-agenda';
    section.innerHTML='<div class="v310-head"><div><h3>Fechas agendadas</h3>'+
      '<p class="muted tiny">Tus próximas fechas y avisos cargados por tu coach.</p></div>'+
      '<span class="v312-next-badge">Agenda</span></div>'+
      '<div class="v314-empty-dates">'+
      ((data?.items||[]).length
        ?'Actualizando tus próximas fechas…'
        :'No tenés fechas puntuales agendadas por tu coach en los próximos 60 días.')+
      '</div>';
    const weekly=host.querySelector('.v81-agenda-grid,.agenda-grid,.v81-week-grid');
    if(weekly)weekly.insertAdjacentElement('beforebegin',section);else host.prepend(section);
  }

  const baseCoachAgendaV314=window.renderCoachStudentAgendaV81;
  if(typeof baseCoachAgendaV314==='function'){
    window.renderCoachStudentAgendaV81=function(){
      const out=baseCoachAgendaV314.apply(this,arguments);
      Promise.resolve().then(()=>injectCoachAgendaLinkV314(false));
      return out;
    };
    try{renderCoachStudentAgendaV81=window.renderCoachStudentAgendaV81}catch(_e){}
  }

  const baseRenderStudentV314=window.renderStudent||renderStudent;
  window.renderStudent=function(){
    const out=baseRenderStudentV314.apply(this,arguments);
    if(currentProfile?.role==='student'&&mode==='student'&&studentTab==='agenda'){
      Promise.resolve()
        .then(()=>window.__fjzLoadOwnAppointmentsV312?.(true))
        .then(()=>ensureStudentAgendaEmptyStateV314(false))
        .catch(e=>console.warn('TEAM FJZ V21.14 agenda render',e));
    }
    return out;
  };
  try{renderStudent=window.renderStudent}catch(_e){}

  window.__fjzAgendaTargetStateV314=loadAgendaTargetV314;
  window.__fjzV314={
    version:VERSION,
    coachAgendaLinkState:true,
    warnsWhenStudentAccountMissing:true,
    studentAgendaSectionAlwaysVisible:true,
    directAgendaAuthorityPreserved:true,
    reviewAuthorityPreserved:true,
    noSchemaChange:true,
    noExtraTimers:true,
    noExtraListeners:true,
    noExtraObservers:true
  };
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-operational-integrity-ux" content="21.14">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V21.14 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-operational-integrity-ux" content="21.14"',
    'id="v314OperationalIntegrityUxRuntime"',
    "warnsWhenStudentAccountMissing:true",
    "studentAgendaSectionAlwaysVisible:true",
    "Cuenta de alumno vinculada",
    "Alumno sin cuenta vinculada",
    "Fechas agendadas",
    "__fjzLoadOwnAppointmentsV312",
]:
    if marker not in html:
        raise RuntimeError("V21.14 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.14 operational integrity UX")
print("V21.14 BEFORE:",before)
print("V21.14 AFTER:",after)
