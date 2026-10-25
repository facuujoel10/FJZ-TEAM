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
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

def edit_script(doc,script_id,transform):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.99 missing script "+script_id)
    old=m.group(2)
    new=transform(old)
    if new==old:
        raise RuntimeError("V20.99 no changes in "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

def replace_between(src,start_marker,end_marker,replacement,label):
    start=src.find(start_marker)
    end=src.find(end_marker,start+len(start_marker))
    if start<0 or end<0 or end<=start:
        raise RuntimeError("V20.99 "+label+" bounds mismatch")
    return src[:start]+replacement+src[end:]

before=metrics(html)

for marker in [
    'meta name="fjz-review-ok-cockpit-fix" content="20.98"',
    'meta name="fjz-smart-alerts-progress" content="20.78"',
    'id="v96AlertCenterRuntime"',
    'id="v175ProfileAgendaCoachCenterRuntime"',
    'id="v280OperationalRecoveryRuntime"',
    "window.__fjzReviewedCoachKeysV297",
    "__fjzMarkCoachReviewOkV298",
]:
    if marker not in html:
        raise RuntimeError("V20.99 prerequisite missing "+marker)

# ------------------------------------------------------------------
# 1. V96: one alert lifecycle. Opening == seen/archived from active UI;
# OK == resolved. Every action synchronizes all Coach feed copies.
# ------------------------------------------------------------------
def patch_v96(body):
    card=r"""  function severityLabelV299(x){
    if(x?.severity==='critical')return 'ALTA';
    if(x?.severity==='warning')return 'REVISAR';
    if(x?.severity==='success')return 'POSITIVA';
    return 'INFO';
  }
  function coachActionLabelV299(x){
    if(x?.kind==='checkin'||x?.kind==='wellness')return 'Ver check-in';
    if(x?.kind==='exercise_feedback'||x?.kind==='training')return 'Ver entrenamiento';
    if(x?.kind==='progression')return 'Ver progreso';
    if(x?.kind==='nutrition')return 'Ver nutrición';
    return 'Ver detalle';
  }
  function coachAlertCardV96(x){
    const sm=x?.smart_meta||null;
    const detail=sm
      ?'<div class="v299-alert-metrics">'+
        ((sm.previous!=null||sm.current!=null||sm.delta!=null)
          ?'<div><span>Anterior</span><strong>'+esc(sm.previous??'—')+'</strong></div>'+
           '<div><span>Actual</span><strong>'+esc(sm.current??'—')+'</strong></div>'+
           '<div><span>Cambio</span><strong>'+esc(sm.delta??'—')+'</strong></div>'
          :'')+
        (sm.period?'<small>'+esc(sm.period)+'</small>':'')+
       '</div>'+
       (sm.suggestion?'<div class="v299-alert-action-copy"><strong>Qué revisar</strong><span>'+esc(sm.suggestion)+'</span></div>':'')
      :'';
    return '<article class="v96-alert-card v299-alert-card '+esc(x.severity||'info')+'">'+
      '<div class="v96-alert-icon">'+esc(iconV96(x.kind))+'</div>'+
      '<div class="v299-alert-copy">'+
        '<div class="v299-alert-topline"><span class="v299-severity '+esc(x.severity||'info')+'">'+esc(severityLabelV299(x))+'</span><span>'+esc(labelV96(x.kind))+' · '+esc(relativeV96(x.occurred_at))+'</span></div>'+
        '<div class="v96-alert-title">'+esc(x.athlete_name||'Alumno')+' · '+esc(x.title||'Aviso')+'</div>'+
        (x.body?'<div class="v96-alert-body">'+esc(x.body)+'</div>':'')+
        detail+
      '</div>'+
      '<div class="v96-alert-actions v299-alert-actions">'+
        '<button class="btn small primary" onclick="openCoachAlertV96(\''+x.athlete_id+'\',\''+escAttrV96(x.event_key)+'\',\''+escAttrV96(x.kind)+'\')">'+esc(coachActionLabelV299(x))+'</button>'+
        '<button class="btn small v299-ok" onclick="dismissCoachAlertV96(\''+escAttrV96(x.event_key)+'\')">✓ OK</button>'+
      '</div>'+
    '</article>';
  }
"""
    body=replace_between(
        body,
        "  function coachAlertCardV96(x){",
        "\n  function renderCoachAlertsV96(){",
        card,
        "V96 alert card"
    )

    renderer=r"""  function renderCoachAlertsV96(){
    const holder=el('v96CoachAlertBody');if(!holder)return;
    const arr=coachFilteredV96();
    const high=coachAlertsV96.filter(x=>x?.severity==='critical').length;
    const review=coachAlertsV96.filter(x=>x?.severity==='warning').length;
    holder.innerHTML=
      '<div class="v299-alert-summary">'+
        '<div><strong>'+high+'</strong><span>Alta prioridad</span></div>'+
        '<div><strong>'+review+'</strong><span>Para revisar</span></div>'+
        '<div><strong>'+coachAlertsV96.length+'</strong><span>Pendientes activos</span></div>'+
      '</div>'+
      '<div class="v96-alert-tools">'+
        [['all','Todas'],['priority','Prioridad'],['progression','Progreso'],['checkin','Check-ins'],['training','Entrenamiento'],['nutrition','Nutrición'],['exercise_feedback','Ejercicios']]
          .map(x=>'<button class="v96-chip '+(coachFilterV96===x[0]?'active':'')+'" onclick="setCoachAlertFilterV96(\''+x[0]+'\')">'+x[1]+'</button>').join('')+
        (coachAlertsV96.length?'<button class="btn ghost small" onclick="readAllCoachAlertsV96()">Marcar todo visto</button>':'')+
      '</div>'+
      '<div class="v299-lifecycle-note">Abrir una alerta la marca como vista y la saca de pendientes. <strong>OK</strong> la deja resuelta.</div>'+
      '<div class="v96-alert-list">'+
        (arr.length?arr.map(coachAlertCardV96).join(''):'<div class="v96-empty">No hay alertas pendientes en este filtro.</div>')+
      '</div>';
  }
"""
    body=replace_between(
        body,
        "  function renderCoachAlertsV96(){",
        "\n  async function refreshCoachAlertsV96",
        renderer,
        "V96 alert renderer"
    )

    # Keep the operational feed used by priorities/list badges in lockstep.
    refresh_anchor="      coachAlertsV96=normalizeCoachV96(feed);"
    if body.count(refresh_anchor)!=1:
        raise RuntimeError("V20.99 V96 refresh anchor mismatch: "+str(body.count(refresh_anchor)))
    body=body.replace(
        refresh_anchor,
        refresh_anchor+"\n      try{if(typeof coachFeedV235!=='undefined')coachFeedV235=normalizeCoachV96(feed)}catch(_e){}",
        1
    )

    action_block=r"""  function syncCoachCopiesV299(keys){
    const set=new Set((keys||[]).map(x=>String(x)));
    coachAlertsV96=coachAlertsV96.filter(x=>!set.has(String(x?.event_key||'')));
    try{coachFeedCache=(coachFeedCache||[]).filter(x=>!set.has(String(x?.event_key||'')))}catch(_e){}
    try{if(typeof coachFeedV235!=='undefined')coachFeedV235=(coachFeedV235||[]).filter(x=>!set.has(String(x?.event_key||'')))}catch(_e){}
    keys?.forEach?.(k=>window.__fjzReviewedCoachKeysV297?.add(String(k)));
    coachFeedLoadedAt=0;
    try{renderCoachAlertsV96()}catch(_e){}
    try{updateCoachBellV96()}catch(_e){}
    try{renderCoachFocusV235?.()}catch(_e){}
    try{decorateCoachAlertsV235?.()}catch(_e){}
    try{renderCoachStudentsV235?.()}catch(_e){}
    try{window.renderCoachPriorityCenterV252?.()}catch(_e){}
  }

  async function persistCoachKeysV299(keys,mode){
    const clean=[...new Set((keys||[]).filter(Boolean).map(String))];
    if(!clean.length)return true;
    const now=new Date().toISOString();
    if(cloudEnabled&&supabaseClient&&!window.__fjzStagingLocal?.enabled){
      const rows=clean.map(event_key=>({
        coach_id:currentUser.id,event_key,
        read_at:now,
        dismissed_at:mode==='ok'?now:null
      }));
      const {error}=await supabaseClient.from('coach_feed_state').upsert(rows,{onConflict:'coach_id,event_key'});
      if(error){toast(cloudErr(error));return false}
    }
    syncCoachCopiesV299(clean);
    return true;
  }

  window.__fjzArchiveCoachStudentV299=async function(athleteId,mode){
    const keys=[];
    (coachAlertsV96||[]).forEach(x=>{if(String(x?.athlete_id||'')===String(athleteId||''))keys.push(x.event_key)});
    try{(coachFeedV235||[]).forEach(x=>{if(String(x?.athlete_id||'')===String(athleteId||''))keys.push(x.event_key)})}catch(_e){}
    const ok=await persistCoachKeysV299(keys,mode==='ok'?'ok':'seen');
    return ok?keys:[];
  };

  window.readCoachAlertV96=async function(key){
    const ok=await persistCoachKeysV299([key],'seen');
    if(ok)toast?.('Vista · salió de pendientes');
    return ok;
  };

  window.dismissCoachAlertV96=async function(key){
    const ok=await persistCoachKeysV299([key],'ok');
    if(ok)toast?.('✓ Resuelta');
    return ok;
  };

  window.readAllCoachAlertsV96=async function(){
    const keys=(coachAlertsV96||[]).map(x=>x.event_key);
    if(!keys.length)return true;
    const ok=await persistCoachKeysV299(keys,'seen');
    if(ok)toast('Alertas vistas · panel limpio');
    return ok;
  };

  window.openCoachAlertV96=async function(athleteId,key,kind){
    const ok=await persistCoachKeysV299([key],'seen');
    if(!ok)return;
    const row=[...cloudAthletes.values()].find(x=>String(x.id)===String(athleteId));
    if(!row){toast('No encuentro esa ficha');return}
    state.selectedStudentId=row.client_id;saveState();coachTab='student';
    coachStudentTab=kind==='nutrition'?'nutrition':kind==='progression'?'progress':(kind==='exercise_feedback'||kind==='training')?'routine':'tracking';
    render();
  };
"""
    body=replace_between(
        body,
        "  window.readCoachAlertV96=async function(key){",
        "\n  window.refreshCoachAlertsV96=refreshCoachAlertsV96;",
        action_block,
        "V96 coach lifecycle"
    )
    return body

html=edit_script(html,"v96AlertCenterRuntime",patch_v96)

# ------------------------------------------------------------------
# 2. Base V80 feed actions: reading/dismissing must also clear V235 feed.
# ------------------------------------------------------------------
old_mark="async function markFeedRead(key){const payload={coach_id:currentUser.id,event_key:key,read_at:new Date().toISOString(),dismissed_at:null};const {error}=await supabaseClient.from('coach_feed_state').upsert(payload,{onConflict:'coach_id,event_key'});if(error){toast(cloudErr(error));return false}window.__fjzReviewedCoachKeysV297?.add(String(key));try{coachFeedCache=(coachFeedCache||[]).filter(x=>x?.event_key!==key)}catch(_e){}coachFeedLoadedAt=0;try{await refreshCoachFeed()}catch(_e){}try{await window.__fjzRenderPrioritySmartV278?.()}catch(_e){}return true}"
new_mark="async function markFeedRead(key){const payload={coach_id:currentUser.id,event_key:key,read_at:new Date().toISOString(),dismissed_at:null};const {error}=await supabaseClient.from('coach_feed_state').upsert(payload,{onConflict:'coach_id,event_key'});if(error){toast(cloudErr(error));return false}window.__fjzReviewedCoachKeysV297?.add(String(key));try{coachFeedCache=(coachFeedCache||[]).filter(x=>x?.event_key!==key)}catch(_e){}try{if(typeof coachFeedV235!=='undefined')coachFeedV235=(coachFeedV235||[]).filter(x=>x?.event_key!==key)}catch(_e){}coachFeedLoadedAt=0;try{await refreshCoachFeed()}catch(_e){}try{renderCoachFocusV235?.();decorateCoachAlertsV235?.();renderCoachStudentsV235?.()}catch(_e){}try{window.renderCoachPriorityCenterV252?.();await window.__fjzRenderPrioritySmartV278?.()}catch(_e){}return true}"
if html.count(old_mark)!=1:
    raise RuntimeError("V20.99 base markFeedRead mismatch: "+str(html.count(old_mark)))
html=html.replace(old_mark,new_mark,1)

old_dismiss="async function dismissFeed(key){const payload={coach_id:currentUser.id,event_key:key,dismissed_at:new Date().toISOString()};const {error}=await supabaseClient.from('coach_feed_state').upsert(payload,{onConflict:'coach_id,event_key'});if(error){toast(cloudErr(error));return false}window.__fjzReviewedCoachKeysV297?.add(String(key));try{coachFeedCache=(coachFeedCache||[]).filter(x=>x?.event_key!==key)}catch(_e){}coachFeedLoadedAt=0;try{await refreshCoachFeed()}catch(_e){}try{await window.__fjzRenderPrioritySmartV278?.()}catch(_e){}return true}"
new_dismiss="async function dismissFeed(key){const now=new Date().toISOString();const payload={coach_id:currentUser.id,event_key:key,read_at:now,dismissed_at:now};const {error}=await supabaseClient.from('coach_feed_state').upsert(payload,{onConflict:'coach_id,event_key'});if(error){toast(cloudErr(error));return false}window.__fjzReviewedCoachKeysV297?.add(String(key));try{coachFeedCache=(coachFeedCache||[]).filter(x=>x?.event_key!==key)}catch(_e){}try{if(typeof coachFeedV235!=='undefined')coachFeedV235=(coachFeedV235||[]).filter(x=>x?.event_key!==key)}catch(_e){}coachFeedLoadedAt=0;try{await refreshCoachFeed()}catch(_e){}try{renderCoachFocusV235?.();decorateCoachAlertsV235?.();renderCoachStudentsV235?.()}catch(_e){}try{window.renderCoachPriorityCenterV252?.();await window.__fjzRenderPrioritySmartV278?.()}catch(_e){}return true}"
if html.count(old_dismiss)!=1:
    raise RuntimeError("V20.99 base dismissFeed mismatch: "+str(html.count(old_dismiss)))
html=html.replace(old_dismiss,new_dismiss,1)

# ------------------------------------------------------------------
# 3. Review authority: always snapshot CURRENT state, archive the student's
# active alerts, persist a cross-device fingerprint acknowledgement.
# ------------------------------------------------------------------
def patch_v175(body):
    start=body.find("  function reviewSnapshotSafeV298(s){")
    end_marker="""  window.markCoachReviewV237=function(){
    const s=typeof student==='function'?student():null;
    return window.__fjzMarkCoachReviewOkV298(s?.id);
  };"""
    end=body.find(end_marker,start)
    if start<0 or end<0:
        raise RuntimeError("V20.99 V175 review authority bounds missing")
    end+=len(end_marker)

    authority=r"""  window.__fjzReviewAckKeysV299=window.__fjzReviewAckKeysV299||new Set();
  let reviewAcksLoadedV299=false,reviewAcksPromiseV299=null;

  function pendingReviewCountV299(s){
    try{
      if(typeof pendingSessionFeedbackCountV243==='function')return Number(pendingSessionFeedbackCountV243(s)||0);
    }catch(_e){}
    try{
      if(typeof coachPendingV235==='function')return Number(coachPendingV235(s)||0);
    }catch(_e){}
    return 0;
  }

  function freshReviewSnapshotV299(s){
    const prev=s?.coachReviewV237||{};
    let adh=0,status='Seguimiento';
    try{adh=Number(adherence(s)||0)}catch(_e){}
    try{status=statusFor(s)||'Seguimiento'}catch(_e){}
    return {
      reviewedAt:new Date().toISOString(),
      studentId:s?.id||null,
      adherence:adh,
      sessionsCount:Array.isArray(s?.sessions)?s.sessions.length:0,
      lastWorkout:s?.lastWorkout||null,
      status,
      checkinDate:prev?.checkinDate||null,
      energy:prev?.energy??null,
      recovery:prev?.recovery??null,
      stress:prev?.stress??null,
      weight:prev?.weight??null,
      pendingFeedback:pendingReviewCountV299(s),
      agendaTotal:Number(prev?.agendaTotal||0),
      agendaOverdue:Number(prev?.agendaOverdue||0),
      nutritionActive:!!prev?.nutritionActive
    };
  }

  function athleteForReviewV299(s){
    try{return cloudAthletes?.get?.(s?.id)||null}catch(_e){return null}
  }

  function reviewFingerprintV299(s){
    if(!s)return '';
    const a=athleteForReviewV299(s);
    let adh=0,status='Seguimiento';
    try{adh=Math.round(Number(adherence(s)||0))}catch(_e){}
    try{status=String(statusFor(s)||'Seguimiento')}catch(_e){}
    const sessions=Array.isArray(s?.sessions)?s.sessions.length:0;
    const last=Date.parse(s?.lastWorkout||0)||0;
    const pending=pendingReviewCountV299(s);
    return ['review-ack-v299',a?.id||s.id,sessions,last,adh,pending,encodeURIComponent(status)].join(':');
  }

  window.__fjzReviewFingerprintV299=reviewFingerprintV299;
  window.__fjzIsReviewAckedV299=function(s){
    const key=reviewFingerprintV299(s);
    return !!key&&window.__fjzReviewAckKeysV299.has(key);
  };

  window.__fjzLoadReviewAcksV299=async function(force=false){
    if(reviewAcksPromiseV299)return reviewAcksPromiseV299;
    if(reviewAcksLoadedV299&&!force)return true;
    if(!cloudEnabled||!supabaseClient||window.__fjzStagingLocal?.enabled){
      reviewAcksLoadedV299=true;
      return true;
    }
    reviewAcksPromiseV299=(async()=>{
      const {data,error}=await supabaseClient.from('coach_feed_state')
        .select('event_key,read_at,dismissed_at')
        .eq('coach_id',currentUser.id)
        .like('event_key','review-ack-v299:%');
      if(error)throw error;
      window.__fjzReviewAckKeysV299=new Set((data||[]).map(x=>String(x.event_key||'')).filter(Boolean));
      reviewAcksLoadedV299=true;
      try{window.renderCoachPriorityCenterV252?.()}catch(_e){}
      try{renderCoachFocusV235?.();renderCoachStudentsV235?.()}catch(_e){}
      return true;
    })().catch(e=>{console.warn('TEAM FJZ V20.99 review ack load',e);return false}).finally(()=>{reviewAcksPromiseV299=null});
    return reviewAcksPromiseV299;
  };

  async function saveReviewAckV299(s,mode){
    const key=reviewFingerprintV299(s);
    if(!key)return false;
    const now=new Date().toISOString();
    if(cloudEnabled&&supabaseClient&&!window.__fjzStagingLocal?.enabled){
      const {error}=await supabaseClient.from('coach_feed_state').upsert({
        coach_id:currentUser.id,event_key:key,read_at:now,dismissed_at:mode==='ok'?now:null
      },{onConflict:'coach_id,event_key'});
      if(error){toast?.(cloudErr(error));return false}
    }
    window.__fjzReviewAckKeysV299.add(key);
    return true;
  }

  function applyReviewBaselineV299(s,mode){
    const snap=freshReviewSnapshotV299(s);
    snap.reviewAckMode=mode||'seen';
    snap.reviewFingerprint=reviewFingerprintV299(s);
    s.coachReviewV237=clone(snap);
    try{saveState?.()}catch(_e){}
    try{
      const current=typeof student==='function'?student():null;
      if(current?.id===s.id){
        reviewCurrentV237=clone(snap);
        renderReviewHubV237(reviewCurrentV237);
        window.__fjzRenderCoachCockpitV268?.();
      }
    }catch(_e){}
    try{decorateCoachReviewStateV238?.()}catch(_e){}
    try{renderCoachFocusV235?.();renderCoachStudentsV235?.()}catch(_e){}
    try{window.renderCoachPriorityCenterV252?.()}catch(_e){}
    return snap;
  }

  function resolveReviewStudentV299(studentId){
    let s=null;
    try{s=(state?.students||[]).find(x=>String(x?.id)===String(studentId||''))||null}catch(_e){}
    if(!s){try{s=typeof student==='function'?student():null}catch(_e){}}
    return s;
  }

  window.__fjzMarkCoachReviewSeenV299=async function(studentId){
    const s=resolveReviewStudentV299(studentId);
    if(!s)return false;
    const a=athleteForReviewV299(s);
    if(a?.id)await window.__fjzArchiveCoachStudentV299?.(a.id,'seen');
    const ack=await saveReviewAckV299(s,'seen');
    if(!ack)return false;
    applyReviewBaselineV299(s,'seen');
    return true;
  };

  window.__fjzMarkCoachReviewOkV298=async function(studentId){
    const s=resolveReviewStudentV299(studentId);
    if(!s){toast?.('No pude identificar al alumno');return false}
    const a=athleteForReviewV299(s);
    if(a?.id)await window.__fjzArchiveCoachStudentV299?.(a.id,'ok');
    const ack=await saveReviewAckV299(s,'ok');
    if(!ack)return false;
    applyReviewBaselineV299(s,'ok');
    toast?.('✓ Revisado / OK · salió de pendientes');
    return true;
  };

  window.markCoachReviewV237=function(){
    const s=typeof student==='function'?student():null;
    return window.__fjzMarkCoachReviewOkV298(s?.id);
  };"""

    body=body[:start]+authority+body[end:]

    # Dashboard hydration also loads cross-device review acknowledgements.
    anchor="""    if(currentProfile?.role==='coach'){
      loadAgendaAttentionV175(false).then(()=>{"""
    repl="""    if(currentProfile?.role==='coach'){
      if(coachTab==='dashboard')window.__fjzLoadReviewAcksV299?.(false);
      loadAgendaAttentionV175(false).then(()=>{"""
    if body.count(anchor)!=1:
        raise RuntimeError("V20.99 V175 postRender ack anchor mismatch")
    body=body.replace(anchor,repl,1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

# ------------------------------------------------------------------
# 4. Priorities: only ACTIVE pending items stay on the panel. Cards show
# precise reasons. Opening a row marks that current review as seen first.
# ------------------------------------------------------------------
def patch_v280(body):
    anchor="  window.__fjzOpenPriorityV280=(id,tab)=>openStudent(id,tab);"
    if body.count(anchor)!=1:
        raise RuntimeError("V20.99 V280 open-priority anchor mismatch")

    override=r"""  function prioritySignalsV299(s,feed){
    const out=[];
    const add=v=>{v=String(v||'').trim();if(v&&!out.includes(v))out.push(v)};
    (feed||[]).slice(0,4).forEach(x=>{
      const body=String(x?.body||'').trim();
      add(String(x?.title||'Alerta')+(body?' · '+body:''));
    });
    let pendingFeedback=0,r=null,adh=0,inactive=daysSince(s?.lastWorkout),status='';
    try{pendingFeedback=Number(typeof pendingSessionFeedbackCountV243==='function'?pendingSessionFeedbackCountV243(s):0)||0}catch(_e){}
    try{r=typeof coachReviewLoopStateV238==='function'?(coachReviewLoopStateV238(s)||null):null}catch(_e){}
    try{adh=Number(typeof adherence==='function'?adherence(s):0)||0}catch(_e){}
    try{status=typeof statusFor==='function'?String(statusFor(s)||''):''}catch(_e){}
    if(pendingFeedback) add('Feedback: '+pendingFeedback+' comentario'+(pendingFeedback===1?'':'s')+' pendiente'+(pendingFeedback===1?'':'s'));
    if(r?.changed&&r?.reason) add('Cambios desde la última revisión: '+r.reason);
    if(adh<70) add('Adherencia: '+Math.round(adh)+'% · objetivo de seguimiento ≥70%');
    if(inactive>=7&&inactive<999) add('Actividad: '+inactive+' días sin registrar entrenamiento');
    if(r?.reviewDue) add('Revisión programada: vencida');
    if(status==='Revisar') add('Estado general: requiere revisión del coach');
    return out.slice(0,4);
  }

  priorityState=function(s){
    const feed=feedFor(s);
    const critical=feed.filter(x=>x?.severity==='critical').length;
    const warning=feed.filter(x=>x?.severity==='warning').length;
    let pendingFeedback=0,r=null,adh=0,inactive=daysSince(s?.lastWorkout),needsReview=false;
    try{pendingFeedback=Number(typeof pendingSessionFeedbackCountV243==='function'?pendingSessionFeedbackCountV243(s):0)||0}catch(_e){}
    try{r=typeof coachReviewLoopStateV238==='function'?(coachReviewLoopStateV238(s)||null):null}catch(_e){}
    try{adh=Number(typeof adherence==='function'?adherence(s):0)||0}catch(_e){}
    try{needsReview=typeof statusFor==='function'&&statusFor(s)==='Revisar'}catch(_e){}
    const acked=!!window.__fjzIsReviewAckedV299?.(s);
    const signals=prioritySignalsV299(s,feed);

    // New feed events always win over an older acknowledgement.
    if(feed.length||critical||warning){
      const bucket=critical>0?'urgent':'today';
      return {bucket,score:(critical?120:70)+warning*10+feed.length*4,label:signals[0]||'Alerta nueva',signals,count:feed.length};
    }
    // Same snapshot already seen/OK: it leaves the active panel.
    if(acked)return {bucket:'watch',score:0,label:'Revisado',signals:[],count:0};

    const changed=!!r?.changed,reviewDue=!!r?.reviewDue;
    if(pendingFeedback||reviewDue||changed||needsReview||adh<70||inactive>=7){
      return {
        bucket:pendingFeedback>0?'urgent':'today',
        score:pendingFeedback?105:55+(reviewDue?10:0)+(adh<70?5:0),
        label:signals[0]||'Revisar seguimiento',
        signals,
        count:Math.max(1,signals.length)
      };
    }
    return {bucket:'watch',score:0,label:'Seguimiento al día',signals:[],count:0};
  };

  priorityTab=function(s){
    const f=feedFor(s),x=f.find(v=>v?.severity==='critical')||f[0];
    if(x?.kind==='nutrition')return 'nutrition';
    if(x?.kind==='progression')return 'progress';
    if(x?.kind==='exercise_feedback'||x?.kind==='training')return 'routine';
    if(x?.kind==='checkin'||x?.kind==='wellness')return 'tracking';
    return 'summary';
  };

  renderPriority=function(){
    const host=el('v252PriorityCenter');if(!host)return;
    const urgent=priorityRows('urgent'),today=priorityRows('today');
    const row=x=>{
      const signals=(x.signals||[]).slice(0,3).map(v=>'<span class="v299-priority-signal">'+esc(v)+'</span>').join('');
      return '<div class="v299-priority-card '+esc(x.bucket)+'">'+
        '<button class="v299-priority-main" onclick="window.__fjzOpenPriorityV280(\''+esc(x.s.id)+'\',\''+esc(priorityTab(x.s))+'\')">'+
          '<span class="v280-priority-avatar">'+esc((x.s.name||'A').slice(0,2).toUpperCase())+'</span>'+
          '<span class="v299-priority-copy"><strong>'+esc(x.s.name||'Alumno')+'</strong>'+signals+'</span>'+
          '<span class="v299-priority-count">'+Number(x.count||1)+'</span>'+
        '</button>'+
        '<div class="v299-priority-actions">'+
          '<button class="btn small" onclick="window.__fjzOpenPriorityV280(\''+esc(x.s.id)+'\',\''+esc(priorityTab(x.s))+'\')">Ver</button>'+
          '<button class="btn small v299-ok" onclick="window.__fjzMarkCoachReviewOkV298?.(\''+esc(x.s.id)+'\')">✓ OK</button>'+
        '</div>'+
      '</div>';
    };
    const col=(title,cls,rows,empty)=>'<section class="v299-priority-column '+cls+'"><div class="v299-priority-headline"><strong>'+title+'</strong><span>'+rows.length+'</span></div>'+(rows.length?rows.slice(0,8).map(row).join(''):'<div class="v280-empty">'+empty+'</div>')+'</section>';
    host.innerHTML=
      '<div class="v280-priority-head"><div><div class="v225-section-kicker">CENTRO DE REVISIONES</div><h3>Pendientes activos</h3>'+
      '<p>Solo aparece lo que todavía no viste. Al entrar se archiva como visto; OK lo deja resuelto.</p></div></div>'+
      '<div class="v299-priority-grid">'+
        col('Urgente','urgent',urgent,'Sin urgencias pendientes')+
        col('Revisar','today',today,'Nada pendiente para revisar')+
      '</div>';
  };

  window.__fjzOpenPriorityV280=async function(id,tab){
    try{await window.__fjzMarkCoachReviewSeenV299?.(id)}catch(e){console.warn('TEAM FJZ V20.99 mark review seen',e)}
    openStudent(id,tab);
  };"""
    body=body.replace(anchor,override,1)

    old_guard="    if(hydratingV280||!(mode==='coach'&&coachTab==='dashboard'))return;"
    new_guard="    if(hydratingV280||!(currentProfile?.role==='coach'&&coachTab==='dashboard'))return;"
    if body.count(old_guard)!=1:
        raise RuntimeError("V20.99 V280 dashboard guard mismatch")
    body=body.replace(old_guard,new_guard,1)

    render_line="""    try{
      renderPriority();
      window.__fjzRenderCoachCalendarV284?.();
    }finally{hydratingV280=false}"""
    render_new="""    try{
      window.__fjzLoadReviewAcksV299?.(false);
      renderPriority();
      window.__fjzRenderCoachCalendarV284?.();
    }finally{hydratingV280=false}"""
    if body.count(render_line)!=1:
        raise RuntimeError("V20.99 V280 V20.84-delegated render block mismatch")
    body=body.replace(render_line,render_new,1)
    return body

html=edit_script(html,"v280OperationalRecoveryRuntime",patch_v280)

# ------------------------------------------------------------------
# 5. Old Coach focus/filter logic must respect the same acknowledgement.
# ------------------------------------------------------------------
old_state="""function coachStateV235(s){
  const a=Number(adherence(s)||0),days=coachDaysSinceV235(s?.lastWorkout);
  return {a,days,review:statusFor(s)==='Revisar',low:a<70,inactive:days>=7};
}"""
new_state="""function coachStateV235(s){
  const a=Number(adherence(s)||0),days=coachDaysSinceV235(s?.lastWorkout);
  let current=false;
  try{
    const r=typeof coachReviewLoopStateV238==='function'?(coachReviewLoopStateV238(s)||{}):{};
    current=!!r.hasBaseline&&!r.changed&&!r.reviewDue;
  }catch(_e){}
  try{current=current||!!window.__fjzIsReviewAckedV299?.(s)}catch(_e){}
  return {a,days,review:!current&&statusFor(s)==='Revisar',low:!current&&a<70,inactive:!current&&days>=7};
}"""
if html.count(old_state)!=1:
    raise RuntimeError("V20.99 coachStateV235 mismatch: "+str(html.count(old_state)))
html=html.replace(old_state,new_state,1)

# ------------------------------------------------------------------
# 6. Styling: denser, clearer and mobile-safe.
# ------------------------------------------------------------------
css=r"""
/* TEAM FJZ · V20.99 ALERT / REVIEW SYSTEM */
.v299-alert-summary{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:10px 0}
.v299-alert-summary>div{padding:10px;border:1px solid #2b3038;border-radius:10px;background:#0d0f13}
.v299-alert-summary strong{display:block;font-size:18px;color:#f4f6f8}.v299-alert-summary span{display:block;margin-top:3px;font-size:8px;color:#8d949e}
.v299-lifecycle-note{margin:8px 0 10px;padding:8px 10px;border:1px solid #292e36;border-radius:9px;background:#0d0f13;color:#8d949e;font-size:8px;line-height:1.45}
.v299-alert-card{grid-template-columns:34px minmax(0,1fr) auto!important;gap:10px!important;align-items:flex-start!important}
.v299-alert-copy{min-width:0}.v299-alert-topline{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:5px;color:#858d98;font-size:7px}
.v299-severity{display:inline-flex;align-items:center;min-height:18px;padding:0 7px;border:1px solid #323844;border-radius:999px;font-size:6.5px;font-weight:900;letter-spacing:.06em}
.v299-severity.critical{border-color:rgba(255,82,98,.45);color:#ff8f99}.v299-severity.warning{border-color:rgba(242,189,85,.4);color:#f2c96f}.v299-severity.success{border-color:rgba(59,213,138,.4);color:#86e7b0}
.v299-alert-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:5px;margin-top:8px}
.v299-alert-metrics>div{padding:6px 7px;border:1px solid #282d35;border-radius:7px;background:#111318}
.v299-alert-metrics span,.v299-alert-metrics small{display:block;color:#7f8792;font-size:6.5px}.v299-alert-metrics strong{display:block;margin-top:2px;font-size:8px;color:#eef1f4}
.v299-alert-metrics>small{grid-column:1/-1}.v299-alert-action-copy{margin-top:7px;padding:7px 8px;border-left:2px solid #d44;border-radius:6px;background:rgba(210,55,65,.04)}
.v299-alert-action-copy strong,.v299-alert-action-copy span{display:block}.v299-alert-action-copy strong{font-size:7px;color:#efb2b7}.v299-alert-action-copy span{margin-top:3px;font-size:7px;line-height:1.45;color:#9aa0a9}
.v299-alert-actions{min-width:112px;display:grid!important;gap:6px!important}.v299-ok{border-color:rgba(59,213,138,.35)!important;color:#a9efc6!important;background:rgba(59,213,138,.055)!important}
.v299-ok:hover{background:rgba(59,213,138,.11)!important}
.v299-priority-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
.v299-priority-column{min-width:0;border:1px solid #2b3038;border-top:3px solid #f2bd55;border-radius:0 11px 11px 11px;background:#0d0f13;overflow:hidden}
.v299-priority-column.urgent{border-top-color:#ff5262}.v299-priority-headline{display:flex;justify-content:space-between;align-items:center;padding:9px 10px;border-bottom:1px solid #252a31}
.v299-priority-headline strong{font-size:9px;color:#eef1f4}.v299-priority-headline span{font-size:8px;color:#858d98}
.v299-priority-card{border-bottom:1px solid #252a31}.v299-priority-card:last-child{border-bottom:0}
.v299-priority-main{appearance:none;width:100%;min-width:0;display:grid;grid-template-columns:32px minmax(0,1fr) auto;gap:8px;align-items:flex-start;padding:9px 10px;border:0;background:transparent;color:inherit;text-align:left}
.v299-priority-copy{min-width:0}.v299-priority-copy>strong{display:block;margin-bottom:4px;color:#f0f2f5;font-size:9.5px}.v299-priority-signal{display:block;margin-top:3px;color:#8f97a2;font-size:7px;line-height:1.4;overflow-wrap:anywhere}
.v299-priority-count{min-width:22px;height:22px;display:grid;place-items:center;border:1px solid #343b46;border-radius:999px;color:#aab1bb;font-size:7px;font-weight:900}
.v299-priority-actions{display:flex;justify-content:flex-end;gap:6px;padding:0 10px 9px}
@media(max-width:760px){
  .v299-priority-grid{grid-template-columns:1fr}
  .v299-alert-card{grid-template-columns:30px minmax(0,1fr)!important}
  .v299-alert-actions{grid-column:1/-1;grid-template-columns:1fr auto;min-width:0;padding-left:40px}
}
@media(max-width:430px){
  .v299-alert-summary{grid-template-columns:1fr 1fr}.v299-alert-summary>div:last-child{grid-column:1/-1}
  .v299-alert-metrics{grid-template-columns:1fr 1fr}.v299-alert-metrics>div:last-of-type{grid-column:1/-1}
  .v299-alert-actions{padding-left:0}
}
"""
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.99 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-alert-review-system" content="20.99">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V20.99 runtime topology changed "+key+": "+repr({"before":before,"after":after}))

required=[
    'meta name="fjz-alert-review-system" content="20.99"',
    "__fjzArchiveCoachStudentV299",
    "Vista · salió de pendientes",
    "✓ Revisado / OK · salió de pendientes",
    "review-ack-v299",
    "__fjzLoadReviewAcksV299",
    "__fjzIsReviewAckedV299",
    "__fjzMarkCoachReviewSeenV299",
    "Pendientes activos",
    "Al entrar se archiva como visto",
    "prioritySignalsV299",
    "coachFeedV235=(coachFeedV235||[]).filter",
    "currentProfile?.role==='coach'&&coachTab==='dashboard'",
]
for marker in required:
    if marker not in html:
        raise RuntimeError("V20.99 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.99 alert/review system")
print("V20.99 BEFORE:",before)
print("V20.99 AFTER:",after)
print("V20.99 lifecycle: new -> seen -> resolved; all Coach surfaces synchronized")
