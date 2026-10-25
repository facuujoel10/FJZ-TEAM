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
    'meta name="fjz-alert-review-system" content="20.99"',
    'id="v175ProfileAgendaCoachCenterRuntime"',
    'id="v280OperationalRecoveryRuntime"',
    'id="v281CoachIntegrityRuntime"',
    "__fjzMarkCoachReviewOkV298",
    "__fjzReviewFingerprintV299",
]:
    if marker not in html:
        raise RuntimeError("V21.01 prerequisite missing "+marker)

# Resumen 360: convert generic navigation cards into persistent guided reviews.
pat=re.compile(r'(<script[^>]*\bid=["\']v175ProfileAgendaCoachCenterRuntime["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
m=pat.search(html)
if not m: raise RuntimeError("V21.01 V175 runtime missing")
body=m.group(2)

old="""    jobs.push(loadAgendaAttentionV175(false));

    await Promise.allSettled(jobs);"""
new="""    jobs.push(loadAgendaAttentionV175(false));
    try{const q=window.__fjzLoadReviewItemStatesV301?.(false);if(q)jobs.push(q)}catch(_e){}

    await Promise.allSettled(jobs);"""
if body.count(old)!=1: raise RuntimeError("V21.01 V175 load anchor mismatch")
body=body.replace(old,new,1)

start=body.find("  function adviceHtmlV175(x,i){")
end=body.find("\n\n  async function hydrateSummaryV175(){",start)
if start<0 or end<0: raise RuntimeError("V21.01 V175 advice bounds missing")
advice=r"""  function adviceHtmlV175(x,i){
    const key=window.__fjzRegisterReviewItemV301?.(x)||'';
    const badge=x.type==='review'?'<span class="badge red">Prioridad '+(i+1)+'</span>':x.type==='good'?'<span class="badge green">Oportunidad</span>':'<span class="badge blue">Revisar</span>';
    const labels={routine:'Entrenamiento',tracking:'Check-in',history:'Historial',progress:'Progreso',nutrition:'Nutrición',agenda:'Agenda'};
    return '<article class="v175-advice '+esc(x.type)+' v301-review-card" data-v301-key="'+esc(key)+'">'+
      '<div class="v175-advice-top"><div><span class="v301-kicker">REVISIÓN GUIADA</span><h5>'+esc(x.title)+'</h5></div>'+badge+'</div>'+
      '<div class="v301-detail"><span>QUÉ REVISAR</span><p>'+esc(x.action)+'</p></div>'+
      '<div class="v301-detail"><span>POR QUÉ APARECIÓ</span><p>'+esc(x.evidence)+'</p></div>'+
      '<div class="v301-actions"><button class="btn small primary" onclick="window.__fjzOpenGuidedReviewV301?.(\''+key+'\')">Revisar ahora · '+esc(labels[x.tab]||'detalle')+'</button>'+
      '<button class="btn small v299-ok" onclick="window.__fjzResolveGuidedReviewV301?.(\''+key+'\')">✓ OK</button></div>'+
    '</article>';
  }"""
body=body[:start]+advice+body[end:]

old="""    const a=assistantV175(agenda);
    if(el('v175Executive'))el('v175Executive').textContent=a.executive;
    if(el('v175Coverage'))el('v175Coverage').textContent='Cobertura '+a.confidence+' · '+(a.dataPoints.join(' · ')||'pocos datos');
    if(el('v175Assistant'))el('v175Assistant').innerHTML=a.items.map(adviceHtmlV175).join('');
    if(el('v175SummaryState'))el('v175SummaryState').textContent='Actualizado';"""
new="""    const a=assistantV175(agenda);
    const active=(a.items||[]).filter(x=>{const k=window.__fjzRegisterReviewItemV301?.(x)||'';return !k||!window.__fjzReviewItemSeenV301?.(k)});
    if(el('v175Executive'))el('v175Executive').textContent=active.length?a.executive:'No hay revisiones pendientes. Si aparece un cambio nuevo, se genera una nueva revisión.';
    if(el('v175Coverage'))el('v175Coverage').textContent='Cobertura '+a.confidence+' · '+(a.dataPoints.join(' · ')||'pocos datos');
    if(el('v175Assistant'))el('v175Assistant').innerHTML=active.length?active.map(adviceHtmlV175).join(''):'<div class="v301-empty"><strong>Seguimiento al día</strong><span>No quedan revisiones activas para este alumno.</span></div>';
    if(el('v175SummaryState'))el('v175SummaryState').textContent=active.length?active.length+' pendiente'+(active.length===1?'':'s'):'Al día';"""
if body.count(old)!=1: raise RuntimeError("V21.01 V175 summary anchor mismatch")
body=body.replace(old,new,1)
html=html[:m.start(2)]+body+html[m.end(2):]

runtime=r"""
<script id="v301ReviewWorkflowProRuntime">
(function(){
  const PREFIX='review-item-v301:',items=new Map(),center=new Map();
  let loaded=false,inflight=null;
  window.__fjzReviewItemKeysV301=window.__fjzReviewItemKeysV301||new Set();
  window.__fjzReviewContextV301=null;

  const students=()=>Array.isArray(state?.students)?state.students:[];
  const byId=id=>students().find(s=>String(s?.id)===String(id||''))||null;
  const athlete=s=>{try{return cloudAthletes?.get?.(s?.id)||null}catch(_e){return null}};
  const feed=s=>{try{const a=athlete(s),f=Array.isArray(coachFeedV235)?coachFeedV235:[];return a?f.filter(x=>String(x?.athlete_id||'')===String(a.id)):[]}catch(_e){return []}};
  const adh=s=>{try{return Math.round(Number(adherence?.(s)||0))}catch(_e){return 0}};
  const days=v=>{const t=Date.parse(v||0);return t?Math.max(0,Math.floor((Date.now()-t)/86400000)):999};
  const current=()=>{try{return student?.()||null}catch(_e){return null}};
  const label=tab=>({summary:'Resumen 360',routine:'Entrenamiento',tracking:'Check-in',history:'Historial',progress:'Progreso',nutrition:'Nutrición',agenda:'Agenda'})[tab]||'Detalle';
  const safe=v=>{try{return esc(String(v??''))}catch(_e){return String(v??'')}};
  function hash(v){let h=2166136261,s=String(v||'');for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return (h>>>0).toString(36)}

  async function persist(keys,mode){
    const clean=[...new Set((keys||[]).filter(Boolean).map(String))];if(!clean.length)return true;
    if(!cloudEnabled||!supabaseClient||window.__fjzStagingLocal?.enabled)return true;
    const now=new Date().toISOString();
    const rows=clean.map(event_key=>mode==='ok'?{coach_id:currentUser.id,event_key,read_at:now,dismissed_at:now}:{coach_id:currentUser.id,event_key,read_at:now});
    const {data,error}=await supabaseClient.from('coach_feed_state').upsert(rows,{onConflict:'coach_id,event_key'}).select('event_key,read_at,dismissed_at');
    if(error){toast?.(cloudErr?.(error)||'No se pudo guardar la revisión');return false}
    const map=new Map((data||[]).map(x=>[String(x.event_key),x]));
    const ok=clean.every(k=>map.get(k)?.read_at&&(mode!=='ok'||map.get(k)?.dismissed_at));
    if(!ok){toast?.('No pude confirmar el guardado de la revisión');return false}
    return true;
  }

  window.__fjzLoadReviewItemStatesV301=async force=>{
    if(inflight)return inflight;if(loaded&&!force)return true;
    if(!cloudEnabled||!supabaseClient||window.__fjzStagingLocal?.enabled){loaded=true;return true}
    inflight=(async()=>{const {data,error}=await supabaseClient.from('coach_feed_state').select('event_key,read_at,dismissed_at').eq('coach_id',currentUser.id).like('event_key',PREFIX+'%');if(error)throw error;window.__fjzReviewItemKeysV301=new Set((data||[]).filter(x=>x.read_at||x.dismissed_at).map(x=>String(x.event_key)));loaded=true;return true})().catch(e=>{console.warn('TEAM FJZ V21.01 review state',e);return false}).finally(()=>{inflight=null});
    return inflight;
  };
  window.__fjzReviewItemSeenV301=k=>!!k&&window.__fjzReviewItemKeysV301.has(String(k));
  window.__fjzRegisterReviewItemV301=x=>{
    const s=current();if(!x||!s)return '';const a=athlete(s),k=PREFIX+String(a?.id||s.id)+':'+String(x.tab||'summary')+':'+hash([x.title,x.action,x.evidence,x.type].join('|'));
    items.set(k,{...x,key:k,studentId:s.id,name:s.name||'Alumno'});return k;
  };

  function showContext(){
    const c=window.__fjzReviewContextV301,s=current(),host=el('coachStudentBody');
    if(!c||!s||!host||coachTab!=='student'||String(s.id)!==String(c.studentId)||coachStudentTab!==c.tab)return;
    el('v301GuidedReview')?.remove();
    host.insertAdjacentHTML('afterbegin','<section class="card v301-guide" id="v301GuidedReview"><div class="v301-guide-head"><div><span class="v301-kicker">REVISIÓN GUIADA · '+safe(label(c.tab))+'</span><h3>'+safe(c.title)+'</h3></div><span class="badge '+(c.urgent?'red':'amber')+'">Qué mirar</span></div><div class="v301-guide-grid"><div><span>QUÉ REVISAR</span><strong>'+safe(c.look)+'</strong></div><div><span>POR QUÉ APARECIÓ</span><strong>'+safe(c.why)+'</strong></div></div><div class="v301-actions">'+(c.itemKey?'<button class="btn small v299-ok" onclick="window.__fjzResolveGuidedReviewV301?.(\''+c.itemKey+'\')">✓ OK · resuelto</button>':'<button class="btn small v299-ok" onclick="window.__fjzResolveCenterReviewV301?.(\''+c.studentId+'\')">✓ OK · resuelto</button>')+'<button class="btn ghost small" onclick="window.__fjzBackTo360V301?.()">Volver al Resumen 360</button></div></section>');
  }
  function openTab(id,tab){if(typeof openCoachStudentTabV235==='function')openCoachStudentTabV235(id,tab);else{state.selectedStudentId=id;coachTab='student';coachStudentTab=tab;saveState?.();render?.()}showContext();try{fjzPostRenderV125?.('v301-guide',showContext)}catch(_e){}}

  window.__fjzOpenGuidedReviewV301=async key=>{
    const x=items.get(String(key));if(!x||!(await persist([x.key],'seen')))return false;
    window.__fjzReviewItemKeysV301.add(x.key);window.__fjzReviewContextV301={itemKey:x.key,studentId:x.studentId,tab:x.tab,title:x.title,look:x.action,why:x.evidence,urgent:x.type==='review'};openTab(x.studentId,x.tab);toast?.('Revisión abierta · salió de pendientes');return true;
  };
  window.__fjzResolveGuidedReviewV301=async key=>{
    if(!(await persist([String(key)],'ok')))return false;window.__fjzReviewItemKeysV301.add(String(key));document.querySelector('[data-v301-key="'+String(key)+'"]')?.remove();
    if(window.__fjzReviewContextV301?.itemKey===String(key)){window.__fjzReviewContextV301=null;el('v301GuidedReview')?.remove()}
    if(coachTab==='student'&&coachStudentTab==='summary')window.renderCoachSummary?.();toast?.('✓ Revisión resuelta');return true;
  };
  window.__fjzBackTo360V301=()=>{const id=window.__fjzReviewContextV301?.studentId||current()?.id;window.__fjzReviewContextV301=null;if(id)openTab(id,'summary')};

  function detail(s){
    const f=feed(s).slice().sort((a,b)=>({critical:4,warning:3,info:2,success:1}[b?.severity]||0)-({critical:4,warning:3,info:2,success:1}[a?.severity]||0)),top=f[0]||null;
    const r=(()=>{try{return coachReviewLoopStateV238?.(s)||null}catch(_e){return null}})();let feedback=0;try{feedback=Number(pendingSessionFeedbackCountV243?.(s)||0)}catch(_e){}
    const inactive=days(s?.lastWorkout),a=adh(s),kind=top?.kind||'',tab=kind==='nutrition'?'nutrition':kind==='checkin'||kind==='wellness'?'tracking':kind==='progression'?'progress':kind==='exercise_feedback'||kind==='training'?'routine':feedback?'routine':inactive>=7?'history':'summary';
    let title,why,look;
    if(top){title=top.title||'Señal nueva para revisar';why=top.body||'Hay una alerta nueva del alumno.';look=top.smart_meta?.suggestion||'Abrí '+label(tab)+' y compará el dato nuevo con el registro anterior antes de decidir un cambio.'}
    else if(feedback){title='Comentarios de entrenamiento pendientes';why=feedback+' comentario'+(feedback===1?'':'s')+' requiere'+(feedback===1?'':'n')+' respuesta.';look='Abrí Entrenamiento y revisá los comentarios de cada ejercicio antes de ajustar cargas, volumen o técnica.'}
    else if(r?.reviewDue||!r?.hasBaseline){title=!r?.hasBaseline?'Primera revisión del alumno':'Revisión de seguimiento vencida';why=r?.reviewDueLabel||'No hay revisión de referencia.';look='Revisá el 360 completo: adherencia, últimas sesiones, check-in y progreso.'}
    else if(r?.changed){title='Cambios desde la última revisión';why=r.reason||'Hay actividad nueva.';look='Compará qué cambió desde el último chequeo y confirmá si requiere ajuste.'}
    else if(a<70){title='Adherencia por debajo del objetivo';why='Adherencia actual: '+a+'%.';look='Revisá sesiones realizadas vs. previstas y detectá la barrera principal.'}
    else{title='Continuidad de entrenamiento';why=inactive<999?inactive+' días sin entrenamiento registrado.':'Falta actividad reciente.';look='Abrí Historial y verificá si faltan sesiones por registrar o hubo una interrupción real.'}
    return {studentId:s.id,name:s.name||'Alumno',tab,title,why,look,keys:f.map(x=>x.event_key).filter(Boolean),urgent:top?.severity==='critical'||feedback>0};
  }
  function active(s){try{const p=coachPriorityStateV252?.(s)||{};return p.bucket==='urgent'||p.bucket==='today'?p:null}catch(_e){return null}}

  function renderCenter(){
    const host=el('v252PriorityCenter');if(!host)return;center.clear();
    const rows=students().map(s=>{const p=active(s);if(!p)return null;const d=detail(s);center.set(String(s.id),d);return {s,p,d}}).filter(Boolean).sort((a,b)=>(b.p.score||0)-(a.p.score||0));
    const urgent=rows.filter(x=>x.p.bucket==='urgent').length;
    const card=x=>'<article class="v301-center-card '+safe(x.p.bucket)+'"><div class="v301-top"><div><span class="v301-kicker">'+(x.p.bucket==='urgent'?'PRIORIDAD ALTA':'REVISAR')+'</span><h4>'+safe(x.d.name)+'</h4></div><span class="badge '+(x.p.bucket==='urgent'?'red':'amber')+'">'+safe(label(x.d.tab))+'</span></div><h5>'+safe(x.d.title)+'</h5><div class="v301-detail"><span>MOTIVO</span><p>'+safe(x.d.why)+'</p></div><div class="v301-detail"><span>QUÉ REVISAR</span><p>'+safe(x.d.look)+'</p></div><div class="v301-actions"><button class="btn small primary" onclick="window.__fjzOpenCenterReviewV301?.(\''+safe(x.s.id)+'\')">Revisar ahora</button><button class="btn small v299-ok" onclick="window.__fjzResolveCenterReviewV301?.(\''+safe(x.s.id)+'\')">✓ OK</button></div></article>';
    host.innerHTML='<div class="v301-center-head"><div class="v225-section-kicker">CENTRO DE REVISIONES</div><h3>Qué requiere tu atención</h3><p>Cada revisión muestra el motivo y el dato que tenés que mirar. Revisar ahora la archiva como vista; OK la resuelve. Si aparece un cambio nuevo, vuelve a generarse.</p></div><div class="v301-stats"><div><strong>'+urgent+'</strong><span>Prioridad alta</span></div><div><strong>'+(rows.length-urgent)+'</strong><span>Para revisar</span></div><div><strong>'+rows.length+'</strong><span>Pendientes activos</span></div></div>'+(rows.length?'<div class="v301-center-grid">'+rows.map(card).join('')+'</div>':'<div class="v301-empty"><strong>Centro limpio</strong><span>No hay revisiones pendientes.</span></div>');
  }

  async function persistStudent(s,mode){
    const d=detail(s);if(d.keys.length&&!(await persist(d.keys,mode)))return false;
    const ack=window.__fjzReviewFingerprintV299?.(s)||'';if(ack&&!(await persist([ack],mode)))return false;
    if(ack)window.__fjzReviewAckKeysV299?.add?.(ack);return true;
  }
  const baseSeen=window.__fjzMarkCoachReviewSeenV299,baseOk=window.__fjzMarkCoachReviewOkV298;
  window.__fjzMarkCoachReviewSeenV299=async id=>{const s=byId(id);if(!s||!(await persistStudent(s,'seen')))return false;const out=await baseSeen?.(id);return out!==false};
  window.__fjzMarkCoachReviewOkV298=async id=>{const s=byId(id);if(!s||!(await persistStudent(s,'ok')))return false;const out=await baseOk?.(id);if(out===false)return false;renderCenter();window.renderCoachFocusV235?.();window.renderCoachStudentsV235?.();toast?.('✓ Revisión resuelta y guardada');return true};

  window.__fjzOpenCenterReviewV301=async id=>{const s=byId(id),d=center.get(String(id))||detail(s);if(!s||!d||await window.__fjzMarkCoachReviewSeenV299?.(id)===false)return false;window.__fjzReviewContextV301={studentId:s.id,tab:d.tab,title:d.title,look:d.look,why:d.why,urgent:d.urgent};openTab(s.id,d.tab);toast?.('Revisión abierta · salió del centro');return true};
  window.__fjzResolveCenterReviewV301=async id=>{const ok=await window.__fjzMarkCoachReviewOkV298?.(id);if(ok===false)return false;if(String(window.__fjzReviewContextV301?.studentId||'')===String(id)){window.__fjzReviewContextV301=null;el('v301GuidedReview')?.remove()}renderCenter();return true};

  function renderFocus(){
    const host=el('v235CoachFocus');if(!host)return;
    const rows=students().map(s=>{const p=active(s);return p?{s,p,d:detail(s)}:null}).filter(Boolean).sort((a,b)=>(b.p.score||0)-(a.p.score||0)).slice(0,4);
    host.innerHTML='<div class="v301-focus-intro"><strong>Próximas acciones</strong><span>Te muestra a quién revisar primero, por qué y cuál es el siguiente paso.</span></div>'+(rows.length?'<div class="v301-focus-list">'+rows.map(x=>'<article class="v301-focus-card '+safe(x.p.bucket)+'"><div class="v301-top"><div><span class="v301-kicker">'+(x.p.bucket==='urgent'?'URGENTE':'REVISAR')+'</span><h4>'+safe(x.d.name)+'</h4></div><span class="badge '+(x.p.bucket==='urgent'?'red':'amber')+'">'+safe(label(x.d.tab))+'</span></div><strong class="v301-focus-title">'+safe(x.d.title)+'</strong><p>'+safe(x.d.why)+'</p><div class="v301-next"><span>SIGUIENTE PASO</span><strong>'+safe(x.d.look)+'</strong></div><div class="v301-actions"><button class="btn small primary" onclick="window.__fjzOpenCenterReviewV301?.(\''+safe(x.s.id)+'\')">Revisar ahora</button><button class="btn small v299-ok" onclick="window.__fjzResolveCenterReviewV301?.(\''+safe(x.s.id)+'\')">✓ OK</button></div></article>').join('')+'</div>':'<div class="v301-empty"><strong>Sin alumnos foco ahora</strong><span>No hay señales activas que requieran una acción inmediata.</span></div>');
  }
  window.renderCoachFocusV235=renderFocus;try{renderCoachFocusV235=renderFocus}catch(_e){}
  const baseOperational=window.__fjzOperationalDashboardV280;
  window.renderCoachPriorityCenterV252=renderCenter;try{renderCoachPriorityCenterV252=renderCenter}catch(_e){}
  window.__fjzOperationalDashboardV280=function(){const out=baseOperational?.apply(this,arguments);if(currentProfile?.role==='coach'&&coachTab==='dashboard'){renderCenter();renderFocus()}return out};

  if(currentProfile?.role==='coach'&&coachTab==='dashboard')try{renderCenter();renderFocus()}catch(e){console.warn('TEAM FJZ V21.01 review surfaces',e)}

  window.__fjzV301={version:'21.01',guided360Reviews:true,verifiedOkPersistence:true,reviewCenterPro:true,focusPanelActionable:true,reviewContextBanner:true,seenLeavesPending:true,okResolves:true,newSnapshotCanReturn:true,noExtraTimers:true,noExtraListeners:true,noExtraObservers:true};
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)

css=r"""
/* TEAM FJZ · V21.01 REVIEW WORKFLOW PRO */
.v301-kicker{display:block;margin-bottom:5px;color:#979faa;font-size:9px;font-weight:900;letter-spacing:.08em}.v301-review-card{padding:15px!important}.v301-review-card h5{font-size:14px!important;line-height:1.35!important}.v301-detail{margin-top:9px;padding:9px 10px;border:1px solid #2b3038;border-radius:9px;background:#0e1116}.v301-detail>span,.v301-guide-grid span,.v301-next span{display:block;margin-bottom:4px;color:#89919c;font-size:9px;font-weight:900;letter-spacing:.06em}.v301-detail p{margin:0!important;color:#c2c8d0!important;font-size:11.5px!important;line-height:1.5!important}.v301-actions{display:flex;gap:7px;flex-wrap:wrap;margin-top:10px}.v301-actions .btn{min-height:35px;font-size:10.5px!important}.v301-empty{padding:17px;border:1px dashed #333943;border-radius:11px;background:#0d1015;text-align:center}.v301-empty strong{display:block;color:#eef1f4;font-size:14px}.v301-empty span{display:block;margin-top:5px;color:#929aa5;font-size:11px}
.v301-guide{margin-bottom:13px!important;border-color:rgba(103,173,255,.3)!important;background:linear-gradient(145deg,rgba(103,173,255,.07),transparent 50%),#101319!important}.v301-guide-head,.v301-top{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}.v301-guide-head h3{margin:0;color:#f5f7f9;font-size:18px}.v301-guide-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-top:11px}.v301-guide-grid>div{padding:10px 11px;border:1px solid #2c323a;border-radius:10px;background:#0d1015}.v301-guide-grid strong{display:block;color:#dce1e8;font-size:12px;line-height:1.5}
.v301-center-head h3{margin:4px 0 0;color:#f5f6f8;font-size:19px}.v301-center-head p{margin:6px 0 0;max-width:850px;color:#9fa7b1;font-size:11.5px;line-height:1.5}.v301-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:11px 0}.v301-stats>div{padding:10px 11px;border:1px solid #2c3139;border-radius:10px;background:#0d1015}.v301-stats strong{display:block;color:#f4f6f8;font-size:19px}.v301-stats span{display:block;margin-top:3px;color:#8f97a2;font-size:10px}.v301-center-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.v301-center-card{padding:13px;border:1px solid #2c3139;border-top:3px solid #f2bd55;border-radius:0 11px 11px 11px;background:#0d1015}.v301-center-card.urgent{border-top-color:#ff5262}.v301-top h4{margin:0;color:#f3f5f7;font-size:14px}.v301-center-card>h5{margin:9px 0 0;color:#e7eaee;font-size:13px}
.v301-focus-intro{margin-bottom:9px;padding:10px;border:1px solid #2b3038;border-radius:10px;background:#0d1015}.v301-focus-intro strong{display:block;color:#eef1f4;font-size:13px}.v301-focus-intro span{display:block;margin-top:4px;color:#969ea8;font-size:10.5px;line-height:1.45}.v301-focus-list{display:grid;gap:9px}.v301-focus-card{padding:12px;border:1px solid #2c3139;border-left:3px solid #f2bd55;border-radius:0 10px 10px 0;background:#0d1015}.v301-focus-card.urgent{border-left-color:#ff5262}.v301-focus-title{display:block;margin-top:8px;color:#e8ebef;font-size:12.5px}.v301-focus-card>p{margin:5px 0 0;color:#afb6c0;font-size:11.5px;line-height:1.5}.v301-next{margin-top:8px;padding:9px;border-radius:9px;background:#12161c}.v301-next strong{display:block;color:#d8dde4;font-size:11.5px;line-height:1.45}
@media(min-width:1000px){.v301-kicker{font-size:10px}.v301-detail p,.v301-guide-grid strong,.v301-focus-card>p,.v301-next strong{font-size:12.5px!important}.v301-actions .btn{font-size:11px!important}}
@media(max-width:760px){.v301-center-grid,.v301-guide-grid{grid-template-columns:1fr}.v301-detail p,.v301-guide-grid strong{font-size:11.5px!important}.v301-actions{display:grid;grid-template-columns:1fr auto}.v301-actions .btn{min-width:0}}
@media(max-width:430px){.v301-stats{grid-template-columns:1fr 1fr}.v301-stats>div:last-child{grid-column:1/-1}.v301-guide-head,.v301-top{display:grid}.v301-actions{grid-template-columns:1fr}}
"""
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V21.01 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]
html=html.replace("</head>",'<meta name="fjz-review-workflow-pro" content="21.01">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]: raise RuntimeError("V21.01 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-review-workflow-pro" content="21.01"',
    'id="v301ReviewWorkflowProRuntime"',
    "guided360Reviews:true","verifiedOkPersistence:true","reviewCenterPro:true","focusPanelActionable:true",
    "__fjzOpenGuidedReviewV301","__fjzResolveGuidedReviewV301","__fjzOpenCenterReviewV301","__fjzResolveCenterReviewV301",
    "REVISIÓN GUIADA","QUÉ REVISAR","POR QUÉ APARECIÓ","Próximas acciones","upsert(rows,{onConflict:'coach_id,event_key'}).select"
]:
    if marker not in html: raise RuntimeError("V21.01 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.01 review workflow pro")
print("V21.01 BEFORE:",before)
print("V21.01 AFTER:",after)
