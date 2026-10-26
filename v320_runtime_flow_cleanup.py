import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":doc.count(".channel("),
        "timeouts":doc.count("setTimeout("),
        "intervals":doc.count("setInterval("),
        "listeners":doc.count("addEventListener("),
        "mutation_observers":doc.count("new MutationObserver"),
        "performance_observers":doc.count("new PerformanceObserver"),
    }

def edit_script(doc,sid,fn):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(sid)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m: raise RuntimeError("V21.20 missing script "+sid)
    body=fn(m.group(2))
    return doc[:m.start(2)]+body+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-first-review-authority" content="21.19"',
    'id="v312ReviewAgendaAuthorityRuntime"',
    'id="v314OperationalIntegrityUxRuntime"',
    'id="v316SessionLossProtectionRuntime"',
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.20 prerequisite missing "+marker)

def patch_v312(body):
    old="""  const baseCoachSummaryV312=window.renderCoachSummary;
  if(typeof baseCoachSummaryV312==='function'){
    window.renderCoachSummary=function(){
      const out=baseCoachSummaryV312.apply(this,arguments);
      Promise.resolve().then(normalizeLegacyReviewHubV312);
      return out;
    };
    try{renderCoachSummary=window.renderCoachSummary}catch(_e){}
  }

"""
    if body.count(old)!=1:
        raise RuntimeError("V21.20 legacy coach-summary wrapper anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,"",1)

    old="""    const items=(data?.items||[]).filter(Boolean).slice(0,8);
    if(!items.length)return;
    const rows=items.map(item=>{
      const d=item.date;
      return '<div class="v310-agenda-item"><div class="v310-agenda-date">'+esc(String(d.getDate()).padStart(2,'0')+' '+monthV312(d))+'</div>'+
        '<div class="v310-agenda-copy"><strong>'+esc(item.title||'Fecha agendada')+'</strong>'+
        '<span>'+esc(item.body||'Agendado por tu coach')+'</span>'+
        '<small>'+esc((item.time?String(item.time).slice(0,5)+' · ':'')+
          new Intl.DateTimeFormat('es-AR',{weekday:'long',day:'numeric',month:'long',year:'numeric'}).format(d))+'</small></div></div>';
    }).join('');"""
    new="""    const items=(data?.items||[]).filter(Boolean).slice(0,8);
    const rows=items.length?items.map(item=>{
      const d=item.date;
      return '<div class="v310-agenda-item"><div class="v310-agenda-date">'+esc(String(d.getDate()).padStart(2,'0')+' '+monthV312(d))+'</div>'+
        '<div class="v310-agenda-copy"><strong>'+esc(item.title||'Fecha agendada')+'</strong>'+
        '<span>'+esc(item.body||'Agendado por tu coach')+'</span>'+
        '<small>'+esc((item.time?String(item.time).slice(0,5)+' · ':'')+
          new Intl.DateTimeFormat('es-AR',{weekday:'long',day:'numeric',month:'long',year:'numeric'}).format(d))+'</small></div></div>';
    }).join(''):'<div class="v314-empty-dates">No tenés fechas puntuales agendadas por tu coach en los próximos 60 días.</div>';"""
    if body.count(old)!=1:
        raise RuntimeError("V21.20 agenda empty-state anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old_home="Promise.resolve().then(()=>injectNextAppointmentV312(true));"
    old_agenda="Promise.resolve().then(()=>injectAgendaDatesV313(true));"
    if body.count(old_home)!=1 or body.count(old_agenda)!=1:
        raise RuntimeError("V21.20 forced appointment render anchors mismatch")
    body=body.replace(old_home,"Promise.resolve().then(()=>injectNextAppointmentV312(false));",1)
    body=body.replace(old_agenda,"Promise.resolve().then(()=>injectAgendaDatesV313(false));",1)

    old_flags="""    operationalCalendarRefreshAfterReviewSync:true,
    noSchemaChange:true,"""
    new_flags="""    operationalCalendarRefreshAfterReviewSync:true,
    renderUsesAppointmentCacheV320:true,
    agendaAlwaysVisibleOwnedByV312:true,
    legacyCoachSummaryWrapperRemovedV320:true,
    noSchemaChange:true,"""
    if body.count(old_flags)!=1:
        raise RuntimeError("V21.20 V312 flags anchor mismatch")
    body=body.replace(old_flags,new_flags,1)
    return body

html=edit_script(html,"v312ReviewAgendaAuthorityRuntime",patch_v312)

def patch_v314(body):
    start=body.find("  // Keep \"Fechas agendadas\" visible even when there are no future items.")
    end=body.find("  const baseCoachAgendaV314=",start)
    if start<0 or end<0:
        raise RuntimeError("V21.20 V314 obsolete empty-state bounds missing")
    body=body[:start]+body[end:]

    old="""  const baseRenderStudentV314=window.renderStudent||renderStudent;
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

"""
    if body.count(old)!=1:
        raise RuntimeError("V21.20 V314 duplicate student-render wrapper mismatch: "+str(body.count(old)))
    body=body.replace(old,"",1)

    old_flags="""    directAgendaAuthorityPreserved:true,
    reviewAuthorityPreserved:true,
    noSchemaChange:true,"""
    new_flags="""    directAgendaAuthorityPreserved:true,
    reviewAuthorityPreserved:true,
    studentAgendaRenderWrapperRemovedV320:true,
    emptyStateDelegatedToV312:true,
    studentAgendaLoaderV320:!!window.__fjzLoadOwnAppointmentsV312,
    studentAgendaSectionLabelV320:'Fechas agendadas',
    noSchemaChange:true,"""
    if body.count(old_flags)!=1:
        raise RuntimeError("V21.20 V314 flags anchor mismatch")
    body=body.replace(old_flags,new_flags,1)
    return body

html=edit_script(html,"v314OperationalIntegrityUxRuntime",patch_v314)

def patch_v316(body):
    old="""  const MAX_RECOVERY_AGE=72*60*60*1000;
  let recoveryRunning=false;"""
    new="""  const MAX_RECOVERY_AGE=72*60*60*1000;
  const RECOVERY_SWEEP_COOLDOWN_V320=15000;
  let recoveryRunning=false,lastRecoverySweepV320=0;"""
    if body.count(old)!=1:
        raise RuntimeError("V21.20 recovery constants anchor mismatch")
    body=body.replace(old,new,1)

    old="""  async function recoverRecentV316(){
    if(recoveryRunning||!supabaseClient||!currentUser||!cloudEnabled)return;
    const ready=currentProfile?.role==='coach'"""
    new="""  async function recoverRecentV316(force=false){
    if(recoveryRunning||!supabaseClient||!currentUser||!cloudEnabled)return;
    const nowV320=Date.now();
    if(!force&&lastRecoverySweepV320&&nowV320-lastRecoverySweepV320<RECOVERY_SWEEP_COOLDOWN_V320)return;
    lastRecoverySweepV320=nowV320;
    const ready=currentProfile?.role==='coach'"""
    if body.count(old)!=1:
        raise RuntimeError("V21.20 recovery throttle anchor mismatch")
    body=body.replace(old,new,1)

    old="""    Promise.resolve().then(()=>recoverRecentV316());
    return out;
  };

  pruneBackupsV316();
  Promise.resolve().then(()=>recoverRecentV316());"""
    new="""    Promise.resolve().then(()=>recoverRecentV316(false));
    return out;
  };

  pruneBackupsV316();
  Promise.resolve().then(()=>recoverRecentV316(true));"""
    if body.count(old)!=1:
        raise RuntimeError("V21.20 recovery call anchor mismatch")
    body=body.replace(old,new,1)

    old_flags="""    sessionSuccessRequiresDoubleVerification:true,
    noExtraTimers:true,"""
    new_flags="""    sessionSuccessRequiresDoubleVerification:true,
    recoverySweepThrottledV320:true,
    recoveryStartupStillImmediateV320:true,
    saveVerificationUnchangedV320:true,
    noExtraTimers:true,"""
    if body.count(old_flags)!=1:
        raise RuntimeError("V21.20 V316 flags anchor mismatch")
    body=body.replace(old_flags,new_flags,1)
    return body

html=edit_script(html,"v316SessionLossProtectionRuntime",patch_v316)

html=html.replace("</head>",'<meta name="fjz-runtime-flow-cleanup" content="21.20">\n</head>',1)

after=metrics(html)
if after["styles"]!=before["styles"]: raise RuntimeError("V21.20 stylesheet topology changed")
if after["renders"]!=before["renders"]-2: raise RuntimeError("V21.20 expected exactly two obsolete render wrappers removed: "+repr({"before":before,"after":after}))
for k in ("channels","timeouts","intervals","listeners","mutation_observers","performance_observers"):
    if after[k]!=before[k]:
        raise RuntimeError("V21.20 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-runtime-flow-cleanup" content="21.20"',
    "renderUsesAppointmentCacheV320:true",
    "agendaAlwaysVisibleOwnedByV312:true",
    "legacyCoachSummaryWrapperRemovedV320:true",
    "studentAgendaRenderWrapperRemovedV320:true",
    "emptyStateDelegatedToV312:true",
    "RECOVERY_SWEEP_COOLDOWN_V320=15000",
    "recoverySweepThrottledV320:true",
    "saveVerificationUnchangedV320:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.20 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.20 runtime flow cleanup")
print("V21.20 BEFORE:",before)
print("V21.20 AFTER:",after)
