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

def edit_script(doc,sid,fn):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(sid)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m: raise RuntimeError("V21.12 missing script "+sid)
    body=fn(m.group(2))
    return doc[:m.start(2)]+body+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-permanent-profile-review" content="21.11"',
    'id="v302ReviewResolutionAuthorityRuntime"',
    "review-profile-v311:",
    "coachReviewLoopStateV238",
    "renderReviewHubV237",
    'id="v310SharedStudentAgendaRuntime"',
]:
    if marker not in html:
        raise RuntimeError("V21.12 prerequisite missing "+marker)

# ---------------------------------------------------------
# 1) Expose the permanent Profile 360 state from V21.11.
# ---------------------------------------------------------
def patch_v302(body):
    old="""  function profileReviewedV311(s){
    const id=athleteKeyV308(s);
    return !!id&&id!=='unknown'&&(profileReviewedAthletesV311.has(id)||resolved.has(PROFILE_PREFIX+id));
  }
  function hasAnyBaselineV308(s){"""
    new="""  function profileReviewedV311(s){
    const id=athleteKeyV308(s);
    return !!id&&id!=='unknown'&&(profileReviewedAthletesV311.has(id)||resolved.has(PROFILE_PREFIX+id));
  }
  window.__fjzProfileReviewedAthleteV311=function(id){
    id=String(id||'');
    return !!id&&(profileReviewedAthletesV311.has(id)||resolved.has(PROFILE_PREFIX+id));
  };
  window.__fjzProfileReviewStateLoadedV311=function(){return !!loaded};
  function hasAnyBaselineV308(s){"""
    if body.count(old)!=1:
        raise RuntimeError("V21.12 V311 exposure anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)
    return body

html=edit_script(html,"v302ReviewResolutionAuthorityRuntime",patch_v302)

# ---------------------------------------------------------
# 2) Legacy review surfaces are unified at runtime below.
#    We intentionally do not patch historical function source here because
#    V20.40/V20.43/V20.81 all evolved that function over time.
# ---------------------------------------------------------

# ---------------------------------------------------------
# 3) Student appointment card: direct authenticated reads.
# ---------------------------------------------------------
css=r"""
/* TEAM FJZ · V21.12 STUDENT APPOINTMENT CARD */
.v312-next-date{
  position:relative;
  overflow:hidden;
  margin:0 0 14px!important;
  padding:15px!important;
  border:1px solid rgba(255,62,82,.28)!important;
  background:
    radial-gradient(circle at 100% 0,rgba(255,43,64,.12),transparent 38%),
    linear-gradient(145deg,rgba(255,255,255,.02),transparent 55%),
    #101116!important;
}
.v312-next-date:before{
  content:"";
  position:absolute;left:0;top:0;bottom:0;width:3px;
  background:linear-gradient(#ff3047,#b70f27);
}
.v312-next-head{
  display:flex;justify-content:space-between;gap:12px;align-items:flex-start;
}
.v312-next-kicker{
  display:block;color:#ff6b78;font-size:8px;font-weight:950;letter-spacing:.12em;text-transform:uppercase;
}
.v312-next-head h3{
  margin:5px 0 0;color:#f6f7f9;font-size:16px;font-weight:920;letter-spacing:-.02em;
}
.v312-next-badge{
  flex:0 0 auto;display:inline-flex;align-items:center;min-height:27px;padding:5px 9px;
  border:1px solid rgba(255,65,83,.24);border-radius:999px;background:rgba(255,48,71,.07);
  color:#ff8f9a;font-size:8px;font-weight:900;text-transform:uppercase;
}
.v312-next-grid{
  display:grid;grid-template-columns:95px minmax(0,1fr);gap:11px;margin-top:12px;
}
.v312-next-datebox{
  display:grid;place-items:center;padding:10px 8px;border:1px solid #30343d;border-radius:12px;background:#0c0d11;
  text-align:center;
}
.v312-next-datebox strong{display:block;color:#fff;font-size:22px;line-height:1;font-weight:950}
.v312-next-datebox span{display:block;margin-top:5px;color:#969ca7;font-size:8px;font-weight:850;text-transform:uppercase}
.v312-next-copy{
  min-width:0;padding:10px 11px;border:1px solid #2c3038;border-radius:12px;background:#0c0d11;
}
.v312-next-copy strong{display:block;color:#f1f2f4;font-size:12px;font-weight:900}
.v312-next-copy p{margin:5px 0 0;color:#a0a5ae;font-size:9px;line-height:1.45}
.v312-next-copy small{display:block;margin-top:6px;color:#777d88;font-size:8px}
.v312-next-actions{display:flex;gap:8px;margin-top:11px}
@media(max-width:560px){
  .v312-next-head{display:grid}
  .v312-next-badge{width:max-content}
  .v312-next-grid{grid-template-columns:78px minmax(0,1fr)}
  .v312-next-actions .btn{width:100%}
}
"""
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V21.12 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

runtime=r"""
<script id="v312ReviewAgendaAuthorityRuntime">
(function(){
  const VERSION='21.12';
  let appointmentCacheV312={userId:null,at:0,data:null,inflight:null};

  function athleteIdForReviewV312(s){
    try{return String(coachAthleteV235?.(s)?.id||'')}catch(_e){return ''}
  }
  function permanentReviewedV312(s){
    const id=athleteIdForReviewV312(s);
    return !!id&&!!window.__fjzProfileReviewedAthleteV311?.(id);
  }

  const baseReviewLoopV312=window.coachReviewLoopStateV238||coachReviewLoopStateV238;
  window.coachReviewLoopStateV238=function(s){
    const out=baseReviewLoopV312?.(s)||{};
    if(permanentReviewedV312(s)&&!s?.coachReviewV237){
      return {
        ...out,
        hasBaseline:true,
        changed:false,
        reviewDue:false,
        reviewDueLabel:'Perfil 360 revisado',
        reason:'Perfil 360 revisado',
        newSessions:0,
        adherenceDelta:0
      };
    }
    return out;
  };
  try{coachReviewLoopStateV238=window.coachReviewLoopStateV238}catch(_e){}

  function normalizeLegacyReviewHubV312(){
    if(!(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'))return;
    let s=null;try{s=student()}catch(_e){}
    if(!s||!permanentReviewedV312(s)||s?.coachReviewV237)return;
    const hub=el('v237ReviewHub');if(!hub)return;
    const stamp=hub.querySelector('.v237-review-meta strong');
    if(stamp&&/sin revisi[oó]n/i.test(stamp.textContent||''))stamp.textContent='Revisado en nube';
    const due=hub.querySelector('.v240-review-due');
    if(due){due.textContent='Perfil 360 revisado';due.classList.remove('due');due.classList.add('ok')}
    const changeCol=hub.querySelector('.v237-review-col');
    if(changeCol){
      const oldItems=[...changeCol.querySelectorAll('.v237-review-item')];
      oldItems.forEach(x=>x.remove());
      changeCol.insertAdjacentHTML('beforeend',
        '<div class="v237-review-item good"><div><strong>Perfil 360 revisado</strong>'+
        '<p>Este perfil ya fue revisado. Solo se generarán nuevas revisiones por señales concretas o por una revisión programada real.</p></div></div>');
    }
  }

  const baseCoachSummaryV312=window.renderCoachSummary;
  if(typeof baseCoachSummaryV312==='function'){
    window.renderCoachSummary=function(){
      const out=baseCoachSummaryV312.apply(this,arguments);
      Promise.resolve().then(normalizeLegacyReviewHubV312);
      return out;
    };
    try{renderCoachSummary=window.renderCoachSummary}catch(_e){}
  }

  function localIsoV312(d){
    return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
  }
  function dayStartV312(v){
    const d=v instanceof Date?new Date(v):new Date(String(v||'')+'T00:00:00');
    if(Number.isNaN(d.getTime()))return null;
    d.setHours(0,0,0,0);return d;
  }
  function weekdayV312(d){return (d.getDay()+6)%7}
  function nextWeekdayV312(wd,from){
    const d=new Date(from),delta=(Number(wd)-weekdayV312(from)+7)%7;
    d.setDate(d.getDate()+delta);return d;
  }
  function monthV312(d){
    return new Intl.DateTimeFormat('es-AR',{month:'short'}).format(d).replace('.','').toUpperCase();
  }

  async function resolveOwnAthleteV312(){
    if(!currentUser?.id||!supabaseClient)return null;
    const {data,error}=await supabaseClient.from('athletes')
      .select('id,user_id,coach_id,name')
      .eq('user_id',currentUser.id)
      .maybeSingle();
    if(error)throw error;
    return data||null;
  }

  async function loadOwnAppointmentsV312(force=false){
    if(!(currentProfile?.role==='student'&&currentUser?.id&&cloudEnabled&&supabaseClient))return null;
    if(!force&&appointmentCacheV312.userId===currentUser.id&&appointmentCacheV312.data&&Date.now()-appointmentCacheV312.at<15000){
      return appointmentCacheV312.data;
    }
    if(appointmentCacheV312.inflight)return appointmentCacheV312.inflight;
    appointmentCacheV312.inflight=(async()=>{
      const athlete=await resolveOwnAthleteV312();
      if(!athlete?.id)return {athlete:null,items:[]};
      const [rr,ss]=await Promise.all([
        supabaseClient.from('athlete_reminders')
          .select('id,title,body,category,schedule_type,reminder_date,weekday,remind_time,active')
          .eq('athlete_id',athlete.id).eq('active',true),
        supabaseClient.from('athlete_schedule')
          .select('id,weekday,workout_day_name,start_time,notes,active')
          .eq('athlete_id',athlete.id).eq('active',true)
      ]);
      if(rr.error)throw rr.error;if(ss.error)throw ss.error;
      const today=dayStartV312(new Date()),limit=new Date(today);limit.setDate(limit.getDate()+60);
      const items=[];
      (rr.data||[]).forEach(r=>{
        let d=null;
        if(r.schedule_type==='once')d=dayStartV312(r.reminder_date);
        else if(Number.isInteger(Number(r.weekday)))d=nextWeekdayV312(Number(r.weekday),today);
        if(!d||d<today||d>limit)return;
        items.push({
          id:r.id,kind:'reminder',date:d,time:r.remind_time||null,
          title:r.title||'Fecha agendada',body:r.body||'Tu coach agendó una fecha para vos.'
        });
      });
      (ss.data||[]).forEach(s=>{
        if(!Number.isInteger(Number(s.weekday)))return;
        const d=nextWeekdayV312(Number(s.weekday),today);
        if(d>limit)return;
        items.push({
          id:s.id,kind:'training',date:d,time:s.start_time||null,
          title:s.workout_day_name||'Entrenamiento',
          body:s.notes||'Entrenamiento programado por tu coach.'
        });
      });
      items.sort((a,b)=>a.date-b.date||String(a.time||'').localeCompare(String(b.time||'')));
      const data={athlete,items};
      appointmentCacheV312={userId:currentUser.id,at:Date.now(),data,inflight:null};
      return data;
    })().finally(()=>{appointmentCacheV312.inflight=null});
    return appointmentCacheV312.inflight;
  }

  function cardHtmlV312(item){
    const d=item.date;
    return '<section class="card v312-next-date" id="v312NextAppointment">'+
      '<div class="v312-next-head"><div><span class="v312-next-kicker">PRÓXIMA FECHA AGENDADA</span>'+
      '<h3>Tenés una fecha programada</h3></div><span class="v312-next-badge">Agendado por tu coach</span></div>'+
      '<div class="v312-next-grid">'+
        '<div class="v312-next-datebox"><strong>'+String(d.getDate()).padStart(2,'0')+'</strong><span>'+monthV312(d)+'</span></div>'+
        '<div class="v312-next-copy"><strong>'+esc(item.title)+'</strong>'+
          '<p>'+esc(item.body||'')+'</p>'+
          '<small>'+esc((item.time?String(item.time).slice(0,5)+' · ':'')+
            new Intl.DateTimeFormat('es-AR',{weekday:'long',day:'numeric',month:'long',year:'numeric'}).format(d))+'</small></div>'+
      '</div>'+
      '<div class="v312-next-actions"><button class="btn primary small" onclick="studentTab=\'agenda\';render()">Ver agenda</button></div>'+
    '</section>';
  }

  async function injectNextAppointmentV312(force=false){
    if(!(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'))return;
    let data=null;
    try{data=await loadOwnAppointmentsV312(force)}catch(e){console.warn('TEAM FJZ V21.12 appointment load',e);return}
    if(!(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'))return;
    const view=el('view');if(!view)return;
    el('v312NextAppointment')?.remove();
    const next=data?.items?.[0];if(!next)return;
    const tmp=document.createElement('div');tmp.innerHTML=cardHtmlV312(next);
    const card=tmp.firstElementChild;if(!card)return;
    const hero=view.querySelector('.hero');
    if(hero)hero.insertAdjacentElement('afterend',card);else view.prepend(card);
  }

  const baseRenderStudentV312=window.renderStudent||renderStudent;
  window.renderStudent=function(){
    const out=baseRenderStudentV312.apply(this,arguments);
    if(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'){
      Promise.resolve().then(()=>injectNextAppointmentV312(true));
    }
    return out;
  };
  try{renderStudent=window.renderStudent}catch(_e){}

  window.__fjzRefreshStudentAppointmentV312=()=>injectNextAppointmentV312(true);
  window.__fjzLoadOwnAppointmentsV312=loadOwnAppointmentsV312;

  // Once V21.11 has loaded permanent review state, repaint all legacy review
  // surfaces so they cannot keep stale "Sin revisión" labels.
  Promise.resolve(window.__fjzLoadReviewStatesV302?.(false)).finally(()=>{
    try{decorateCoachReviewStateV238?.()}catch(_e){}
    try{renderCoachStudentsV235?.()}catch(_e){}
    try{renderCoachFocusV235?.()}catch(_e){}
    try{renderCoachPriorityCenterV252?.()}catch(_e){}
    try{normalizeLegacyReviewHubV312()}catch(_e){}
  });

  window.__fjzV312={
    version:VERSION,
    legacyReviewUsesPermanentCloudState:true,
    noDuplicateFirstReviewAfterReload:true,
    oldReviewHubCloudAware:true,
    directStudentAppointmentRead:true,
    appointmentVisibleOnStudentHome:true,
    appointmentScopedByAuthUser:true,
    noSchemaChange:true,
    noExtraTimers:true,
    noExtraListeners:true,
    noExtraObservers:true
  };
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-review-agenda-authority" content="21.12">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V21.12 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-review-agenda-authority" content="21.12"',
    'id="v312ReviewAgendaAuthorityRuntime"',
    "__fjzProfileReviewedAthleteV311",
    "Perfil 360 revisado",
    "legacyReviewUsesPermanentCloudState:true",
    "baseReviewLoopV312",
    "permanentReviewedV312",
    "normalizeLegacyReviewHubV312",
    "noDuplicateFirstReviewAfterReload:true",
    "directStudentAppointmentRead:true",
    "appointmentVisibleOnStudentHome:true",
    ".eq('user_id',currentUser.id)",
    ".eq('athlete_id',athlete.id)",
    "PRÓXIMA FECHA AGENDADA",
]:
    if marker not in html:
        raise RuntimeError("V21.12 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.12 review + agenda authority")
print("V21.12 BEFORE:",before)
print("V21.12 AFTER:",after)
