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
    'meta name="fjz-review-workflow-pro" content="21.01"',
    'id="v301ReviewWorkflowProRuntime"',
    "__fjzResolveCenterReviewV301",
    "__fjzResolveGuidedReviewV301",
    "__fjzReviewFingerprintV299",
    "__fjzMarkCoachReviewOkV298",
]:
    if marker not in html:
        raise RuntimeError("V21.02 prerequisite missing "+marker)

runtime=r"""
<script id="v302ReviewResolutionAuthorityRuntime">
(function(){
  const REVIEW_PREFIX='review-v302:';
  const STATE_PREFIX='review-state-v302:';
  const ITEM_PREFIX='review-item-v301:';
  const resolved=new Set(),read=new Set(),registry=new Map(),center=new Map(),resolving=new Set();
  let loaded=false,loadPromise=null;

  const students=()=>Array.isArray(state?.students)?state.students:[];
  const byId=id=>students().find(s=>String(s?.id)===String(id||''))||null;
  const current=()=>{try{return student?.()||null}catch(_e){return null}};
  const athlete=s=>{try{return cloudAthletes?.get?.(s?.id)||null}catch(_e){return null}};
  const feed=s=>{try{const a=athlete(s),f=Array.isArray(coachFeedV235)?coachFeedV235:[];return a?f.filter(x=>String(x?.athlete_id||'')===String(a.id)):[]}catch(_e){return []}};
  const adh=s=>{try{return Math.round(Number(adherence?.(s)||0))}catch(_e){return 0}};
  const days=v=>{const t=Date.parse(v||0);return t?Math.max(0,Math.floor((Date.now()-t)/86400000)):999};
  const label=tab=>({summary:'Resumen 360',routine:'Entrenamiento',tracking:'Check-in',history:'Historial',progress:'Progreso',nutrition:'Nutrición',agenda:'Agenda'})[tab]||'Detalle';
  const safe=v=>{try{return esc(String(v??''))}catch(_e){return String(v??'')}};
  function hash(v){let h=2166136261,s=String(v||'');for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return (h>>>0).toString(36)}

  function pendingFeedbackInfo(s){
    const rows=(Array.isArray(s?.sessions)?s.sessions:[]).filter(x=>x?.sessionFeedback?.status==='pending');
    const ids=rows.map(x=>String(x?.id||x?.date||'')).filter(Boolean).sort();
    let count=ids.length;
    if(!count){try{count=Number(pendingSessionFeedbackCountV243?.(s)||0)}catch(_e){}}
    return {count,token:ids.length?hash(ids.join('|')):String(count||0)};
  }

  function stateFingerprint(s){
    const pf=pendingFeedbackInfo(s);
    let base='';try{base=String(window.__fjzReviewFingerprintV299?.(s)||'')}catch(_e){}
    if(!base){
      let status='';try{status=String(statusFor?.(s)||'')}catch(_e){}
      base=[s?.id,(s?.sessions||[]).length,Date.parse(s?.lastWorkout||0)||0,adh(s),pf.count,status].join(':');
    }
    return base+':pf:'+pf.token;
  }

  function stateKey(s){
    const a=athlete(s);
    return STATE_PREFIX+String(a?.id||s?.id||'unknown')+':'+hash(stateFingerprint(s));
  }

  function detail(s){
    const f=feed(s).slice().sort((a,b)=>({critical:4,warning:3,info:2,success:1}[b?.severity]||0)-({critical:4,warning:3,info:2,success:1}[a?.severity]||0));
    const top=f[0]||null;
    const pf=pendingFeedbackInfo(s);
    const r=(()=>{try{return coachReviewLoopStateV238?.(s)||null}catch(_e){return null}})();
    const inactive=days(s?.lastWorkout),a=adh(s),kind=top?.kind||'';
    const tab=kind==='nutrition'?'nutrition':kind==='checkin'||kind==='wellness'?'tracking':kind==='progression'?'progress':kind==='exercise_feedback'||kind==='training'?'routine':pf.count?'routine':inactive>=7?'history':'summary';
    let title,why,look,sourceType='state',source='';
    if(top){
      title=top.title||'Señal nueva para revisar';
      why=top.body||'Hay una alerta nueva del alumno.';
      look=top.smart_meta?.suggestion||'Abrí '+label(tab)+' y compará el dato nuevo con el registro anterior antes de decidir un cambio.';
      sourceType='event';source='event:'+String(top.event_key||hash([title,why,kind].join('|')));
    }else if(pf.count){
      title='Comentarios de entrenamiento pendientes';
      why=pf.count+' comentario'+(pf.count===1?'':'s')+' requiere'+(pf.count===1?'':'n')+' respuesta.';
      look='Abrí Entrenamiento y revisá los comentarios de cada ejercicio antes de ajustar cargas, volumen o técnica.';
      sourceType='feedback';source='feedback:'+pf.token;
    }else if(r?.reviewDue||!r?.hasBaseline){
      title=!r?.hasBaseline?'Primera revisión del alumno':'Revisión de seguimiento vencida';
      why=r?.reviewDueLabel||'No hay revisión de referencia.';
      look='Revisá el 360 completo: adherencia, últimas sesiones, check-in y progreso.';
      source='review_due:'+stateFingerprint(s);
    }else if(r?.changed){
      title='Cambios desde la última revisión';
      why=r.reason||'Hay actividad nueva.';
      look='Compará qué cambió desde el último chequeo y confirmá si requiere ajuste.';
      source='changed:'+stateFingerprint(s);
    }else if(a<70){
      title='Adherencia por debajo del objetivo';
      why='Adherencia actual: '+a+'%.';
      look='Revisá sesiones realizadas vs. previstas y detectá la barrera principal.';
      source='adherence:'+stateFingerprint(s);
    }else{
      title='Continuidad de entrenamiento';
      why=inactive<999?inactive+' días sin entrenamiento registrado.':'Falta actividad reciente.';
      look='Abrí Historial y verificá si faltan sesiones por registrar o hubo una interrupción real.';
      source='continuity:'+stateFingerprint(s);
    }
    const at=athlete(s),reviewKey=REVIEW_PREFIX+String(at?.id||s.id)+':'+sourceType+':'+hash(source);
    return {
      studentId:s.id,name:s.name||'Alumno',tab,title,why,look,
      urgent:top?.severity==='critical'||pf.count>0,
      sourceType,source,reviewKey,stateKey:stateKey(s),
      eventKeys:top?.event_key?[String(top.event_key)]:[]
    };
  }

  function isResolved(s,d){
    if(!d)return false;
    if(d.sourceType==='event'||d.sourceType==='feedback')return resolved.has(d.reviewKey);
    if(resolved.has(d.stateKey)||resolved.has(d.reviewKey))return true;
    try{return !!window.__fjzIsReviewAckedV299?.(s)}catch(_e){return false}
  }

  async function persist(keys,mode){
    const clean=[...new Set((keys||[]).filter(Boolean).map(String))];
    if(!clean.length)return true;
    const now=new Date().toISOString();
    if(cloudEnabled&&supabaseClient&&!window.__fjzStagingLocal?.enabled){
      const rows=clean.map(event_key=>mode==='ok'
        ?{coach_id:currentUser.id,event_key,read_at:now,dismissed_at:now}
        :{coach_id:currentUser.id,event_key,read_at:now});
      const {data,error}=await supabaseClient.from('coach_feed_state')
        .upsert(rows,{onConflict:'coach_id,event_key'})
        .select('event_key,read_at,dismissed_at');
      if(error){toast?.(cloudErr?.(error)||'No se pudo guardar la revisión');return false}
      const got=new Map((data||[]).map(x=>[String(x.event_key),x]));
      const ok=clean.every(k=>got.get(k)?.read_at&&(mode!=='ok'||got.get(k)?.dismissed_at));
      if(!ok){toast?.('No pude confirmar el OK en la nube');return false}
    }
    clean.forEach(k=>read.add(k));
    if(mode==='ok')clean.forEach(k=>resolved.add(k));
    return true;
  }

  async function loadStates(force=false){
    if(loadPromise)return loadPromise;
    if(loaded&&!force)return true;
    if(!cloudEnabled||!supabaseClient||window.__fjzStagingLocal?.enabled){loaded=true;return true}
    loadPromise=(async()=>{
      const prefixes=[ITEM_PREFIX+'%',REVIEW_PREFIX+'%',STATE_PREFIX+'%','review-ack-v299:%'];
      const batches=await Promise.all(prefixes.map(async pattern=>{
        const {data,error}=await supabaseClient.from('coach_feed_state')
          .select('event_key,read_at,dismissed_at')
          .eq('coach_id',currentUser.id)
          .like('event_key',pattern);
        if(error)throw error;
        return data||[];
      }));
      read.clear();resolved.clear();
      batches.flat().forEach(x=>{
        const k=String(x?.event_key||'');if(!k)return;
        if(x.read_at)read.add(k);
        if(x.dismissed_at)resolved.add(k);
      });
      loaded=true;
      return true;
    })().catch(e=>{console.warn('TEAM FJZ V21.02 review state load',e);return false}).finally(()=>{loadPromise=null});
    return loadPromise;
  }
  window.__fjzLoadReviewStatesV302=loadStates;

  function syncEventCopies(keys){
    const set=new Set((keys||[]).map(String));if(!set.size)return;
    try{if(typeof coachAlertsV96!=='undefined')coachAlertsV96=(coachAlertsV96||[]).filter(x=>!set.has(String(x?.event_key||'')))}catch(_e){}
    try{if(typeof coachFeedV235!=='undefined')coachFeedV235=(coachFeedV235||[]).filter(x=>!set.has(String(x?.event_key||'')))}catch(_e){}
    try{coachFeedCache=(coachFeedCache||[]).filter(x=>!set.has(String(x?.event_key||'')))}catch(_e){}
    try{keys.forEach(k=>window.__fjzReviewedCoachKeysV297?.add?.(String(k)))}catch(_e){}
    try{coachFeedLoadedAt=0}catch(_e){}
  }

  function removeCards(key){
    document.querySelectorAll('[data-v302-key="'+CSS.escape(String(key))+'"]').forEach(x=>x.remove());
  }
  function removeItemCard(key){
    document.querySelectorAll('[data-v301-key="'+CSS.escape(String(key))+'"]').forEach(x=>x.remove());
  }

  function refreshSurfaces(){
    try{renderCenter()}catch(_e){}
    try{renderFocus()}catch(_e){}
    try{renderCoachAlertsV96?.();updateCoachBellV96?.()}catch(_e){}
    try{renderCoachStudentsV235?.()}catch(_e){}
  }

  function openTab(id,tab){
    if(typeof openCoachStudentTabV235==='function')openCoachStudentTabV235(id,tab);
    else{state.selectedStudentId=id;coachTab='student';coachStudentTab=tab;saveState?.();render?.()}
    showContext();
    try{fjzPostRenderV125?.('v302-guide',showContext)}catch(_e){}
  }

  function showContext(){
    const c=window.__fjzReviewContextV302,s=current(),host=el('coachStudentBody');
    if(!c||!s||!host||coachTab!=='student'||String(s.id)!==String(c.studentId)||coachStudentTab!==c.tab)return;
    el('v301GuidedReview')?.remove();el('v302GuidedReview')?.remove();
    host.insertAdjacentHTML('afterbegin',
      '<section class="card v301-guide" id="v302GuidedReview">'+
      '<div class="v301-guide-head"><div><span class="v301-kicker">REVISIÓN PENDIENTE · '+safe(label(c.tab))+'</span><h3>'+safe(c.title)+'</h3></div><span class="badge '+(c.urgent?'red':'amber')+'">Pendiente de OK</span></div>'+
      '<div class="v301-guide-grid"><div><span>QUÉ REVISAR</span><strong>'+safe(c.look)+'</strong></div><div><span>POR QUÉ APARECIÓ</span><strong>'+safe(c.why)+'</strong></div></div>'+
      '<div class="v301-actions"><button class="btn small v299-ok" onclick="window.__fjzResolveContextReviewV302?.()">✓ OK · cerrar revisión</button>'+
      '<button class="btn ghost small" onclick="window.__fjzBackTo360V302?.()">Volver al Resumen 360</button></div></section>');
  }

  const baseRegister=window.__fjzRegisterReviewItemV301;
  window.__fjzRegisterReviewItemV301=function(x){
    const key=baseRegister?.(x)||'';
    const s=current();
    if(key&&s)registry.set(String(key),{...x,key:String(key),studentId:s.id,name:s.name||'Alumno'});
    return key;
  };
  window.__fjzReviewItemSeenV301=key=>!!key&&resolved.has(String(key));

  const baseLoad301=window.__fjzLoadReviewItemStatesV301;
  window.__fjzLoadReviewItemStatesV301=async function(force=false){
    try{await baseLoad301?.(force)}catch(_e){}
    return loadStates(force);
  };

  window.__fjzOpenGuidedReviewV301=async function(key){
    const x=registry.get(String(key));if(!x)return false;
    if(!(await persist([String(key)],'seen')))return false;
    window.__fjzReviewContextV302={type:'item',key:String(key),studentId:x.studentId,tab:x.tab,title:x.title,look:x.action,why:x.evidence,urgent:x.type==='review'};
    openTab(x.studentId,x.tab);
    toast?.('Revisión abierta · sigue pendiente hasta tocar OK');
    return true;
  };

  window.__fjzResolveGuidedReviewV301=async function(key){
    key=String(key||'');if(!key||resolving.has(key))return false;
    resolving.add(key);removeItemCard(key);
    const ok=await persist([key],'ok');
    resolving.delete(key);
    if(!ok){try{window.renderCoachSummary?.()}catch(_e){};return false}
    if(window.__fjzReviewContextV302?.key===key){window.__fjzReviewContextV302=null;el('v302GuidedReview')?.remove()}
    try{window.renderCoachSummary?.()}catch(_e){}
    refreshSurfaces();toast?.('✓ Revisión cerrada');
    return true;
  };

  function active(s){try{const p=coachPriorityStateV252?.(s)||{};return p.bucket==='urgent'||p.bucket==='today'?p:null}catch(_e){return null}}

  function rowFor(s){
    const p=active(s);if(!p)return null;
    const d=detail(s);if(isResolved(s,d))return null;
    center.set(String(s.id),d);return {s,p,d};
  }

  function renderCenter(){
    const host=el('v252PriorityCenter');if(!host)return;center.clear();
    const rows=students().map(rowFor).filter(Boolean).sort((a,b)=>(b.p.score||0)-(a.p.score||0));
    const urgent=rows.filter(x=>x.p.bucket==='urgent').length;
    const card=x=>'<article class="v301-center-card '+safe(x.p.bucket)+'" data-v302-key="'+safe(x.d.reviewKey)+'">'+
      '<div class="v301-top"><div><span class="v301-kicker">'+(x.p.bucket==='urgent'?'PRIORIDAD ALTA':'REVISAR')+'</span><h4>'+safe(x.d.name)+'</h4></div><span class="badge '+(x.p.bucket==='urgent'?'red':'amber')+'">'+safe(label(x.d.tab))+'</span></div>'+
      '<h5>'+safe(x.d.title)+'</h5><div class="v301-detail"><span>MOTIVO</span><p>'+safe(x.d.why)+'</p></div>'+
      '<div class="v301-detail"><span>QUÉ REVISAR</span><p>'+safe(x.d.look)+'</p></div>'+
      '<div class="v301-actions"><button class="btn small primary" onclick="window.__fjzOpenCenterReviewV301?.(\''+safe(x.s.id)+'\')">Revisar ahora</button>'+
      '<button class="btn small v299-ok" onclick="window.__fjzResolveCenterReviewV301?.(\''+safe(x.s.id)+'\')">✓ OK</button></div></article>';
    host.innerHTML='<div class="v301-center-head"><div class="v225-section-kicker">CENTRO DE REVISIONES</div><h3>Qué requiere tu atención</h3>'+
      '<p><strong>Abrir</strong> solo marca la revisión como vista. <strong>OK</strong> la cierra y la elimina. La misma revisión no vuelve hasta que exista un cambio nuevo real.</p></div>'+
      '<div class="v301-stats"><div><strong>'+urgent+'</strong><span>Prioridad alta</span></div><div><strong>'+(rows.length-urgent)+'</strong><span>Para revisar</span></div><div><strong>'+rows.length+'</strong><span>Pendientes activos</span></div></div>'+
      (rows.length?'<div class="v301-center-grid">'+rows.map(card).join('')+'</div>':'<div class="v301-empty"><strong>Centro limpio</strong><span>No hay revisiones pendientes.</span></div>');
  }

  function renderFocus(){
    const host=el('v235CoachFocus');if(!host)return;
    const rows=students().map(rowFor).filter(Boolean).sort((a,b)=>(b.p.score||0)-(a.p.score||0)).slice(0,4);
    host.innerHTML='<div class="v301-focus-intro"><strong>Próximas acciones</strong><span>Solo aparecen revisiones activas que todavía no cerraste con OK.</span></div>'+
      (rows.length?'<div class="v301-focus-list">'+rows.map(x=>'<article class="v301-focus-card '+safe(x.p.bucket)+'" data-v302-key="'+safe(x.d.reviewKey)+'">'+
      '<div class="v301-top"><div><span class="v301-kicker">'+(x.p.bucket==='urgent'?'URGENTE':'REVISAR')+'</span><h4>'+safe(x.d.name)+'</h4></div><span class="badge '+(x.p.bucket==='urgent'?'red':'amber')+'">'+safe(label(x.d.tab))+'</span></div>'+
      '<strong class="v301-focus-title">'+safe(x.d.title)+'</strong><p>'+safe(x.d.why)+'</p><div class="v301-next"><span>SIGUIENTE PASO</span><strong>'+safe(x.d.look)+'</strong></div>'+
      '<div class="v301-actions"><button class="btn small primary" onclick="window.__fjzOpenCenterReviewV301?.(\''+safe(x.s.id)+'\')">Revisar ahora</button>'+
      '<button class="btn small v299-ok" onclick="window.__fjzResolveCenterReviewV301?.(\''+safe(x.s.id)+'\')">✓ OK</button></div></article>').join('')+'</div>':
      '<div class="v301-empty"><strong>Sin alumnos foco ahora</strong><span>No hay revisiones activas pendientes de OK.</span></div>');
  }

  window.__fjzOpenCenterReviewV301=async function(id){
    const s=byId(id);if(!s)return false;
    const d=center.get(String(id))||detail(s);
    if(isResolved(s,d)){refreshSurfaces();return true}
    if(!(await persist([d.reviewKey],'seen')))return false;
    window.__fjzReviewContextV302={type:'center',key:d.reviewKey,stateKey:d.stateKey,studentId:s.id,tab:d.tab,title:d.title,look:d.look,why:d.why,urgent:d.urgent,eventKeys:d.eventKeys};
    openTab(s.id,d.tab);
    toast?.('Revisión abierta · sigue pendiente hasta tocar OK');
    return true;
  };

  const baseOk=window.__fjzMarkCoachReviewOkV298;
  async function resolveStudent(id,fromContext=false){
    const s=byId(id);if(!s)return false;
    const d=(fromContext&&window.__fjzReviewContextV302?.studentId===s.id)
      ?{...detail(s),...window.__fjzReviewContextV302}
      :(center.get(String(id))||detail(s));
    const lock=String(d.reviewKey||d.key||'');if(!lock||resolving.has(lock))return false;
    resolving.add(lock);removeCards(lock);
    const keys=[lock,d.stateKey||stateKey(s),...(d.eventKeys||[])].filter(Boolean);
    const ok=await persist(keys,'ok');
    if(!ok){resolving.delete(lock);refreshSurfaces();return false}
    syncEventCopies(d.eventKeys||[]);
    try{await baseOk?.(s.id)}catch(e){console.warn('TEAM FJZ V21.02 legacy review baseline',e)}
    resolving.delete(lock);
    resolved.add(lock);resolved.add(d.stateKey||stateKey(s));
    if(window.__fjzReviewContextV302?.studentId===s.id){window.__fjzReviewContextV302=null;el('v302GuidedReview')?.remove()}
    refreshSurfaces();
    try{window.renderCoachSummary?.()}catch(_e){}
    showSaveSuccessV264?.('Revisión cerrada');
    return true;
  }

  window.__fjzResolveCenterReviewV301=id=>resolveStudent(id,false);
  window.__fjzResolveContextReviewV302=()=>{
    const c=window.__fjzReviewContextV302;if(!c)return false;
    if(c.type==='item')return window.__fjzResolveGuidedReviewV301?.(c.key);
    return resolveStudent(c.studentId,true);
  };

  window.__fjzMarkCoachReviewOkV298=async function(id){
    const s=byId(id);if(!s)return baseOk?.(id);
    return resolveStudent(id,false);
  };

  window.__fjzBackTo360V302=()=>{
    const id=window.__fjzReviewContextV302?.studentId||current()?.id;
    window.__fjzReviewContextV302=null;if(id)openTab(id,'summary');
  };
  window.__fjzBackTo360V301=window.__fjzBackTo360V302;

  const baseDismiss=window.dismissCoachAlertV96;
  window.dismissCoachAlertV96=async function(key){
    const k=String(key||'');
    let row=null;try{row=(coachAlertsV96||[]).find(x=>String(x?.event_key||'')===k)||null}catch(_e){}
    if(!row){try{row=(coachFeedV235||[]).find(x=>String(x?.event_key||'')===k)||null}catch(_e){}}
    const s=row?[...students()].find(x=>String(athlete(x)?.id||'')===String(row.athlete_id||'')):null;
    const d=s?detail(s):null;
    const ok=await baseDismiss?.(key);if(ok===false)return false;
    if(s&&d){
      const keys=[d.reviewKey,d.stateKey].filter(Boolean);
      const saved=await persist(keys,'ok');
      if(saved){resolved.add(d.reviewKey);resolved.add(d.stateKey)}
    }
    refreshSurfaces();
    return ok!==false;
  };

  window.renderCoachPriorityCenterV252=renderCenter;try{renderCoachPriorityCenterV252=renderCenter}catch(_e){}
  window.renderCoachFocusV235=renderFocus;try{renderCoachFocusV235=renderFocus}catch(_e){}

  const baseOperational=window.__fjzOperationalDashboardV280;
  window.__fjzOperationalDashboardV280=function(){
    const out=baseOperational?.apply(this,arguments);
    if(currentProfile?.role==='coach'&&coachTab==='dashboard'){
      loadStates(false).finally(()=>{renderCenter();renderFocus()});
    }
    return out;
  };

  loadStates(false).finally(()=>{
    if(currentProfile?.role==='coach'&&coachTab==='dashboard'){renderCenter();renderFocus()}
    if(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'){try{window.renderCoachSummary?.()}catch(_e){}}
  });

  window.__fjzV302={
    version:'21.02',
    resolvedStateAuthoritative:true,
    seenDoesNotResolve:true,
    okRemovesImmediately:true,
    derivedReviewStableUntilRealChange:true,
    centerFiltersResolved:true,
    focusFiltersResolved:true,
    alertOkSynchronizesReview:true,
    cloudConfirmationRequired:true,
    noExtraTimers:true,
    noExtraListeners:true,
    noExtraObservers:true
  };
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-review-resolution-authority" content="21.02">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V21.02 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-review-resolution-authority" content="21.02"',
    'id="v302ReviewResolutionAuthorityRuntime"',
    "resolvedStateAuthoritative:true",
    "seenDoesNotResolve:true",
    "okRemovesImmediately:true",
    "derivedReviewStableUntilRealChange:true",
    "centerFiltersResolved:true",
    "focusFiltersResolved:true",
    "alertOkSynchronizesReview:true",
    "cloudConfirmationRequired:true",
    "review-state-v302:",
    "review-v302:",
    "__fjzResolveContextReviewV302",
    "sigue pendiente hasta tocar OK",
    ".upsert(rows,{onConflict:'coach_id,event_key'})",
    ".select('event_key,read_at,dismissed_at')",
]:
    if marker not in html:
        raise RuntimeError("V21.02 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.02 review resolution authority")
print("V21.02 BEFORE:",before)
print("V21.02 AFTER:",after)
