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

def edit_script(doc,script_id,transform):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.97 missing script "+script_id)
    old=m.group(2)
    new=transform(old)
    if new==old:
        raise RuntimeError("V20.97 no changes in "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-smart-alerts-progress" content="20.78"',
    'id="v96AlertCenterRuntime"',
    'id="v197AlertArchiveRuntime"',
    'id="v175ProfileAgendaCoachCenterRuntime"',
    "buildSmartAlertsV278",
    "renderCoachWeeklyBriefV250",
    "renderCoachFourWeekV260",
    "readMeansArchived:true",
]:
    if marker not in html:
        raise RuntimeError("V20.97 prerequisite missing "+marker)

def patch_v96(body):
    init_anchor="""  let studentAlertsV96=[];
  let studentAlertsLoadedAtV96=0;
"""
    init_repl="""  let studentAlertsV96=[];
  let studentAlertsLoadedAtV96=0;
  window.__fjzReviewedCoachKeysV297=window.__fjzReviewedCoachKeysV297||new Set();
"""
    if body.count(init_anchor)!=1:
        raise RuntimeError("V20.97 V96 init anchor mismatch")
    body=body.replace(init_anchor,init_repl,1)

    old_read_coach="""  window.readCoachAlertV96=async function(key){
    const payload={coach_id:currentUser.id,event_key:key,read_at:new Date().toISOString(),dismissed_at:null};
    const {error}=await supabaseClient.from('coach_feed_state').upsert(payload,{onConflict:'coach_id,event_key'});
    if(error){toast(cloudErr(error));return}
    const x=coachAlertsV96.find(a=>a.event_key===key);if(x)x.is_read=true;
    coachFeedLoadedAt=0;renderCoachAlertsV96();updateCoachBellV96();
  };"""
    new_read_coach="""  window.readCoachAlertV96=async function(key){
    const payload={coach_id:currentUser.id,event_key:key,read_at:new Date().toISOString(),dismissed_at:null};
    const {error}=await supabaseClient.from('coach_feed_state').upsert(payload,{onConflict:'coach_id,event_key'});
    if(error){toast(cloudErr(error));return false}
    window.__fjzReviewedCoachKeysV297.add(String(key));
    coachAlertsV96=coachAlertsV96.filter(a=>a.event_key!==key);
    try{coachFeedCache=(coachFeedCache||[]).filter(a=>a?.event_key!==key)}catch(_e){}
    coachFeedLoadedAt=0;
    renderCoachAlertsV96();
    updateCoachBellV96();
    return true
  };"""
    if body.count(old_read_coach)!=1:
        raise RuntimeError("V20.97 V96 coach read anchor mismatch")
    body=body.replace(old_read_coach,new_read_coach,1)

    old_dismiss_coach="""  window.dismissCoachAlertV96=async function(key){
    const payload={coach_id:currentUser.id,event_key:key,dismissed_at:new Date().toISOString()};
    const {error}=await supabaseClient.from('coach_feed_state').upsert(payload,{onConflict:'coach_id,event_key'});
    if(error){toast(cloudErr(error));return}
    coachAlertsV96=coachAlertsV96.filter(x=>x.event_key!==key);coachFeedLoadedAt=0;renderCoachAlertsV96();updateCoachBellV96();
  };"""
    new_dismiss_coach="""  window.dismissCoachAlertV96=async function(key){
    const payload={coach_id:currentUser.id,event_key:key,dismissed_at:new Date().toISOString()};
    const {error}=await supabaseClient.from('coach_feed_state').upsert(payload,{onConflict:'coach_id,event_key'});
    if(error){toast(cloudErr(error));return false}
    window.__fjzReviewedCoachKeysV297.add(String(key));
    coachAlertsV96=coachAlertsV96.filter(x=>x.event_key!==key);
    try{coachFeedCache=(coachFeedCache||[]).filter(a=>a?.event_key!==key)}catch(_e){}
    coachFeedLoadedAt=0;
    renderCoachAlertsV96();
    updateCoachBellV96();
    return true
  };"""
    if body.count(old_dismiss_coach)!=1:
        raise RuntimeError("V20.97 V96 coach dismiss anchor mismatch")
    body=body.replace(old_dismiss_coach,new_dismiss_coach,1)

    old_read_all="""  window.readAllCoachAlertsV96=async function(){
    const rows=coachAlertsV96.filter(x=>!x.is_read).map(x=>({coach_id:currentUser.id,event_key:x.event_key,read_at:new Date().toISOString(),dismissed_at:null}));
    if(!rows.length)return;
    const {error}=await supabaseClient.from('coach_feed_state').upsert(rows,{onConflict:'coach_id,event_key'});
    if(error){toast(cloudErr(error));return}
    coachAlertsV96.forEach(x=>x.is_read=true);coachFeedLoadedAt=0;renderCoachAlertsV96();updateCoachBellV96();toast('Alertas marcadas como leídas');
  };"""
    new_read_all="""  window.readAllCoachAlertsV96=async function(){
    const rows=(coachAlertsV96||[]).map(x=>({coach_id:currentUser.id,event_key:x.event_key,read_at:new Date().toISOString(),dismissed_at:null}));
    if(!rows.length)return;
    const {error}=await supabaseClient.from('coach_feed_state').upsert(rows,{onConflict:'coach_id,event_key'});
    if(error){toast(cloudErr(error));return false}
    rows.forEach(x=>window.__fjzReviewedCoachKeysV297.add(String(x.event_key)));
    const keys=new Set(rows.map(x=>String(x.event_key)));
    coachAlertsV96=[];
    try{coachFeedCache=(coachFeedCache||[]).filter(a=>!keys.has(String(a?.event_key||'')))}catch(_e){}
    coachFeedLoadedAt=0;
    renderCoachAlertsV96();
    updateCoachBellV96();
    toast('Alertas revisadas y archivadas');
    return true
  };"""
    if body.count(old_read_all)!=1:
        raise RuntimeError("V20.97 V96 coach read-all anchor mismatch")
    body=body.replace(old_read_all,new_read_all,1)

    old_student_read="""  window.readStudentAlertV96=async function(key){
    const payload={student_id:currentUser.id,event_key:key,read_at:new Date().toISOString(),dismissed_at:null};
    const {error}=await supabaseClient.from('student_alert_state').upsert(payload,{onConflict:'student_id,event_key'});
    if(error){toast(cloudErr(error));return}
    const x=studentAlertsV96.find(a=>a.event_key===key);if(x)x.is_read=true;
    studentAlertsLoadedAtV96=0;renderStudentAlertModalV96();updateStudentAlertsV96(false);
  };"""
    new_student_read="""  window.readStudentAlertV96=async function(key){
    const payload={student_id:currentUser.id,event_key:key,read_at:new Date().toISOString(),dismissed_at:null};
    const {error}=await supabaseClient.from('student_alert_state').upsert(payload,{onConflict:'student_id,event_key'});
    if(error){toast(cloudErr(error));return false}
    studentAlertsV96=studentAlertsV96.filter(a=>a.event_key!==key);
    studentAlertsLoadedAtV96=0;
    renderStudentAlertModalV96();
    updateStudentAlertsV96(false);
    return true
  };"""
    if body.count(old_student_read)!=1:
        raise RuntimeError("V20.97 V96 student read anchor mismatch")
    body=body.replace(old_student_read,new_student_read,1)

    old_student_all="""  window.readAllStudentAlertsV96=async function(){
    const rows=studentAlertsV96.filter(x=>!x.is_read).map(x=>({student_id:currentUser.id,event_key:x.event_key,read_at:new Date().toISOString(),dismissed_at:null}));
    if(rows.length){
      const {error}=await supabaseClient.from('student_alert_state').upsert(rows,{onConflict:'student_id,event_key'});
      if(error){toast(cloudErr(error));return}
    }
    studentAlertsV96.forEach(x=>x.is_read=true);studentAlertsLoadedAtV96=0;renderStudentAlertModalV96();updateStudentAlertsV96(false);toast('Avisos marcados como leídos');
  };"""
    new_student_all="""  window.readAllStudentAlertsV96=async function(){
    const rows=(studentAlertsV96||[]).map(x=>({student_id:currentUser.id,event_key:x.event_key,read_at:new Date().toISOString(),dismissed_at:null}));
    if(rows.length){
      const {error}=await supabaseClient.from('student_alert_state').upsert(rows,{onConflict:'student_id,event_key'});
      if(error){toast(cloudErr(error));return false}
    }
    studentAlertsV96=[];
    studentAlertsLoadedAtV96=0;
    renderStudentAlertModalV96();
    updateStudentAlertsV96(false);
    toast('Avisos revisados y archivados');
    return true
  };"""
    if body.count(old_student_all)!=1:
        raise RuntimeError("V20.97 V96 student read-all anchor mismatch")
    body=body.replace(old_student_all,new_student_all,1)
    return body

html=edit_script(html,"v96AlertCenterRuntime",patch_v96)

# The V19.7 layer correctly introduced archive semantics, but it executes in a
# different IIFE and therefore cannot safely mutate V96's private arrays.
# Keep the feature marker while letting V96 own its state.
def patch_v197(body):
    return r"""
(function(){
  window.__fjzV197={
    version:'19.7',
    readMeansArchived:true,
    immediateLocalRemoval:true,
    dismissedAndReadExcludedServerSide:true,
    noVisibleAlertAccumulation:true,
    canonicalArchiveOwnedByV96:true
  };
})();
"""

html=edit_script(html,"v197AlertArchiveRuntime",patch_v197)

def patch_v278(body):
    old_state="""        const st=cloud.states.get(x.event_key);
        if(st?.dismissed_at)return;
        x.is_read=!!st?.read_at;
        out.push(x);"""
    new_state="""        const st=cloud.states.get(x.event_key);
        if(window.__fjzReviewedCoachKeysV297?.has(String(x.event_key)))return;
        if(st?.dismissed_at||st?.read_at)return;
        x.is_read=false;
        out.push(x);"""
    if body.count(old_state)!=1:
        raise RuntimeError("V20.97 V278 state filter anchor mismatch")
    body=body.replace(old_state,new_state,1)

    old_merged="""    const merged=[...smart,...filtered].filter(x=>{
      const k=x?.event_key||[x?.athlete_id,x?.title,x?.occurred_at].join(':');
      if(keys.has(k))return false;keys.add(k);return true;
    });"""
    new_merged="""    const merged=[...smart,...filtered].filter(x=>{
      const k=x?.event_key||[x?.athlete_id,x?.title,x?.occurred_at].join(':');
      if(x?.is_read)return false;
      if(window.__fjzReviewedCoachKeysV297?.has(String(k)))return false;
      if(keys.has(k))return false;keys.add(k);return true;
    });"""
    if body.count(old_merged)!=1:
        raise RuntimeError("V20.97 V278 merged feed anchor mismatch")
    body=body.replace(old_merged,new_merged,1)

    old_attention="""    try{await markFeedRead?.(key)}catch(_e){}
    const row=[...cloudAthletes.values()].find(x=>x.id===athleteId);"""
    new_attention="""    try{
      const ok=await markFeedRead?.(key);
      window.__fjzReviewedCoachKeysV297?.add(String(key));
      smartCloudCacheV278.at=0;
      try{coachFeedCache=(coachFeedCache||[]).filter(x=>x?.event_key!==key)}catch(_e){}
    }catch(_e){}
    const row=[...cloudAthletes.values()].find(x=>x.id===athleteId);"""
    if body.count(old_attention)!=1:
        raise RuntimeError("V20.97 V278 attention read anchor mismatch")
    body=body.replace(old_attention,new_attention,1)
    return body

html=edit_script(html,"v278SmartAlertsProgressRuntime",patch_v278)

def patch_v175(body):
    start=body.find("  async function hydrateSummaryV175(){")
    end=body.find("\n  window.renderCoachSummary=function(){",start)
    if start<0 or end<0 or end<=start:
        raise RuntimeError("V20.97 summary hydrator bounds missing")
    core=body[start:end]
    if core.count("hydrateSummaryV175")!=1:
        raise RuntimeError("V20.97 summary hydrate declaration mismatch")
    core=core.replace("hydrateSummaryV175","hydrateSummaryCoreV297",1)

    wrapper=r"""
  function finalizeCoachSummaryV297(failed){
    if(!(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'))return;
    let s=null,latest=null,measurement=null,weight=null,agenda={total:0,overdue:0},nutrition={active:false},pending=[];
    try{s=student()}catch(_e){}
    try{latest=trackingCache?.checkins?.[0]||null;measurement=trackingCache?.measurements?.[0]||null;weight=measurement?.weight_kg??latest?.weight_kg??null}catch(_e){}
    try{const ath=coachAthleteV175();agenda=agendaSummaryV175(ath?.id)||agenda}catch(_e){}
    try{nutrition=nutritionSummaryV175()||nutrition}catch(_e){}
    try{pending=pendingFeedbackV175()||[]}catch(_e){}

    if(s){
      try{
        const reviewHost=el('v237ReviewHub');
        if(reviewHost&&/Preparando/i.test(reviewHost.textContent||'')&&typeof reviewSnapshotV237==='function'&&typeof renderReviewHubV237==='function'){
          const snap=reviewSnapshotV237(s,latest,weight,pending,agenda,nutrition);
          try{reviewCurrentV237=snap}catch(_e){}
          renderReviewHubV237(snap);
        }
      }catch(e){console.warn('TEAM FJZ V20.97 review fallback',e)}
      try{
        const four=el('v260CoachFourWeek');
        if(four&&/Preparando/i.test(four.textContent||'')&&typeof renderCoachFourWeekV260==='function')renderCoachFourWeekV260(s,latest);
      }catch(e){console.warn('TEAM FJZ V20.97 4-week fallback',e)}
      try{
        const brief=el('v250CoachWeeklyBrief');
        if(brief&&/Preparando/i.test(brief.textContent||'')&&typeof renderCoachWeeklyBriefV250==='function')renderCoachWeeklyBriefV250(s,latest,agenda,nutrition,pending);
      }catch(e){console.warn('TEAM FJZ V20.97 weekly brief fallback',e)}
      try{
        if(typeof renderSessionFeedbackCoachV242==='function')renderSessionFeedbackCoachV242();
      }catch(e){console.warn('TEAM FJZ V20.97 session feedback fallback',e)}
    }

    const summaryState=el('v175SummaryState');
    if(summaryState&&/Actualizando|Preparando|Cargando/i.test(summaryState.textContent||'')){
      summaryState.textContent=failed?'Actualizado · datos parciales':'Actualizado';
    }
    const coverage=el('v175Coverage');
    if(coverage&&/Evaluando|Preparando|Cargando/i.test(coverage.textContent||'')){
      coverage.textContent='Cobertura disponible · datos cargados';
    }
    const executive=el('v175Executive');
    if(executive&&/Analizando|Preparando|Cargando/i.test(executive.textContent||'')){
      executive.textContent=s
        ?'Adherencia '+Number(adherence(s)||0)+'%. Revisá las señales disponibles antes de ajustar el plan.'
        :'Sin datos suficientes para una recomendación adicional.';
    }
    const status=el('v175Status');
    if(status&&/Cargando datos|Preparando/i.test(status.textContent||'')){
      try{status.innerHTML=chipV175('Datos disponibles','good')}catch(_e){status.textContent='Datos disponibles'}
    }

    document.querySelectorAll('#v175Coach360 .empty,#coachStudentBody .empty').forEach(node=>{
      if(/^\s*Preparando\b/i.test(node.textContent||'')){
        node.textContent='Sin datos adicionales para mostrar en esta sección.';
      }
    });
  }

  async function hydrateSummaryV175(){
    let failed=false;
    try{
      await hydrateSummaryCoreV297();
    }catch(e){
      failed=true;
      console.warn('TEAM FJZ V20.97 coach summary hydration recovered',e);
    }finally{
      finalizeCoachSummaryV297(failed);
    }
  }
"""
    return body[:start]+core+wrapper+body[end:]

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

html=html.replace("</head>",'<meta name="fjz-coach-summary-alert-archive" content="20.97">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V20.97 runtime topology changed "+key+": "+repr({"before":before,"after":after}))

required=[
    'meta name="fjz-coach-summary-alert-archive" content="20.97"',
    "canonicalArchiveOwnedByV96:true",
    "window.__fjzReviewedCoachKeysV297",
    "if(st?.dismissed_at||st?.read_at)return",
    "if(x?.is_read)return false",
    "coachAlertsV96=coachAlertsV96.filter(a=>a.event_key!==key)",
    "studentAlertsV96=studentAlertsV96.filter(a=>a.event_key!==key)",
    "hydrateSummaryCoreV297",
    "finalizeCoachSummaryV297",
    "Actualizado · datos parciales",
    "Sin datos adicionales para mostrar en esta sección.",
]
for marker in required:
    if marker not in html:
        raise RuntimeError("V20.97 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.97 coach summary + alert archive hardening")
print("V20.97 BEFORE:",before)
print("V20.97 AFTER:",after)
