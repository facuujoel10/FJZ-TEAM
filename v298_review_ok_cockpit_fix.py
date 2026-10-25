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
        raise RuntimeError("V20.98 missing script "+script_id)
    old=m.group(2)
    new=transform(old)
    if new==old:
        raise RuntimeError("V20.98 no changes in "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-coach-summary-alert-archive" content="20.97"',
    'id="v175ProfileAgendaCoachCenterRuntime"',
    'id="v280OperationalRecoveryRuntime"',
    "renderCoachCockpitV268",
    "coachReviewLoopStateV238",
    "markCoachReviewV237",
]:
    if marker not in html:
        raise RuntimeError("V20.98 prerequisite missing "+marker)

# 1) The exact production placeholder is created by the canonical
# renderCoachStudent surface, outside v175's script scope.
old_placeholder='<div class="empty">Preparando lectura operativa…</div>'
if html.count(old_placeholder)!=1:
    raise RuntimeError("V20.98 operational placeholder mismatch: "+str(html.count(old_placeholder)))
html=html.replace(
    old_placeholder,
    '<div class="v268-empty-note">Actualizando datos del alumno…</div>',
    1
)

def patch_v175(body):
    # 2) Replace the strict V20.68 cockpit launcher. mode==='coach' was an
    # unnecessary extra gate and could leave the sibling cockpit untouched.
    start=body.find("  window.__fjzRenderCoachCockpitV268=function(){")
    end=body.find("\n  };",start)
    if start<0 or end<0:
        raise RuntimeError("V20.98 cockpit launcher bounds missing")
    end+=len("\n  };")
    robust=r"""  function fallbackCoachCockpitV298(s,message){
    const host=el('v268CoachCockpit');if(!host)return;
    let adh=0,last='—',status='Seguimiento';
    try{adh=Number(adherence(s)||0)}catch(_e){}
    try{last=fmtDate(s?.lastWorkout)||'—'}catch(_e){}
    try{status=statusFor(s)||'Seguimiento'}catch(_e){}
    host.innerHTML=
      '<div class="v268-cockpit-head"><div><div class="v268-kicker">COACH COCKPIT</div><h4>Lectura operativa del alumno</h4>'+
      '<p>Resumen disponible con los datos que ya tiene la ficha.</p></div><span class="badge blue">'+esc(status)+'</span></div>'+
      '<div class="v268-metrics">'+
        cockpitMetricV268('Adherencia',adh+'%','Estado actual')+
        cockpitMetricV268('Último entreno',last,'Registro más reciente')+
        cockpitMetricV268('Sesiones',Array.isArray(s?.sessions)?s.sessions.length:0,'Guardadas')+
      '</div>'+
      '<div class="v268-empty-note">'+esc(message||'No hay más señales disponibles por ahora.')+'</div>';
  }

  window.__fjzRenderCoachCockpitV268=function(){
    if(!(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'))return;
    const host=el('v268CoachCockpit');if(!host)return;
    let s=null;
    try{s=typeof student==='function'?student():null}catch(_e){}
    if(!s){
      fallbackCoachCockpitV298(null,'No pude resolver la ficha del alumno. Volvé a Alumnos y abrila nuevamente.');
      return;
    }
    try{
      const latest=trackingCache?.checkins?.[0]||null;
      renderCoachCockpitV268(s,latest);
      if(/Actualizando datos del alumno/i.test(host.textContent||'')){
        fallbackCoachCockpitV298(s,'La lectura quedó disponible con los datos locales de la ficha.');
      }
    }catch(e){
      console.warn('TEAM FJZ V20.98 cockpit recovery',e);
      fallbackCoachCockpitV298(s,'La lectura completa no pudo calcularse, pero la ficha sigue disponible.');
    }
  };"""
    body=body[:start]+robust+body[end:]

    # 3) Give the whole review system one clear acknowledgement authority.
    mark_start=body.find("  window.markCoachReviewV237=function(){")
    mark_end=body.find("\n  };",mark_start)
    if mark_start<0 or mark_end<0:
        raise RuntimeError("V20.98 review marker bounds missing")
    mark_end+=len("\n  };")
    review_authority=r"""  function reviewSnapshotSafeV298(s){
    try{
      if(reviewCurrentV237&&reviewCurrentV237.studentId===s?.id)return clone(reviewCurrentV237);
    }catch(_e){}
    let pending=0;
    try{
      if(typeof pendingSessionFeedbackCountV243==='function')pending=Number(pendingSessionFeedbackCountV243(s)||0);
      else if(typeof coachPendingV235==='function')pending=Number(coachPendingV235(s)||0);
    }catch(_e){}
    const prev=s?.coachReviewV237||{};
    return {
      reviewedAt:new Date().toISOString(),
      studentId:s?.id||null,
      adherence:(()=>{try{return Number(adherence(s)||0)}catch(_e){return 0}})(),
      sessionsCount:Array.isArray(s?.sessions)?s.sessions.length:0,
      lastWorkout:s?.lastWorkout||null,
      status:(()=>{try{return statusFor(s)}catch(_e){return 'Seguimiento'}})(),
      checkinDate:prev?.checkinDate||null,
      energy:prev?.energy??null,
      recovery:prev?.recovery??null,
      stress:prev?.stress??null,
      weight:prev?.weight??null,
      pendingFeedback:pending,
      agendaTotal:Number(prev?.agendaTotal||0),
      agendaOverdue:Number(prev?.agendaOverdue||0),
      nutritionActive:!!prev?.nutritionActive
    };
  }

  window.__fjzMarkCoachReviewOkV298=function(studentId){
    let s=null;
    try{s=(state?.students||[]).find(x=>String(x?.id)===String(studentId||''))||null}catch(_e){}
    if(!s){
      try{s=typeof student==='function'?student():null}catch(_e){}
    }
    if(!s){
      toast?.('No pude identificar al alumno');
      return false;
    }
    const snap=reviewSnapshotSafeV298(s);
    snap.reviewedAt=new Date().toISOString();
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
    try{renderCoachPriorityCenterV252?.()}catch(_e){}
    try{window.__fjzOperationalDashboardV280?.()}catch(_e){}
    toast?.('✓ Revisado / OK');
    return true;
  };

  window.markCoachReviewV237=function(){
    const s=typeof student==='function'?student():null;
    return window.__fjzMarkCoachReviewOkV298(s?.id);
  };"""
    body=body[:mark_start]+review_authority+body[mark_end:]

    # Make the existing review CTA unmistakable.
    body=body.replace(
      '<button class="btn primary" onclick="markCoachReviewV237()">Marcar revisión completada</button>',
      '<button class="btn primary v298-review-main-ok" onclick="markCoachReviewV237()">✓ Revisado / OK</button>',
      1
    )
    body=body.replace(
      'Al marcarla como completada, esta foto del estado queda como referencia para la próxima revisión.',
      'Cuando ya revisaste lo que te pide la app, tocá OK. No vuelve a quedar pendiente hasta que haya cambios nuevos o llegue la próxima revisión.',
      1
    )

    # Re-run the cockpit after connected data settles; if it ever remains in a
    # loading state, force the safe final renderer immediately.
    fin_anchor="""    const status=el('v175Status');
    if(status&&/Cargando datos|Preparando/i.test(status.textContent||'')){
      try{status.innerHTML=chipV175('Datos disponibles','good')}catch(_e){status.textContent='Datos disponibles'}
    }

    document.querySelectorAll('#v175Coach360 .empty,#coachStudentBody .empty').forEach(node=>{"""
    fin_repl="""    const status=el('v175Status');
    if(status&&/Cargando datos|Preparando/i.test(status.textContent||'')){
      try{status.innerHTML=chipV175('Datos disponibles','good')}catch(_e){status.textContent='Datos disponibles'}
    }

    try{window.__fjzRenderCoachCockpitV268?.()}catch(e){console.warn('TEAM FJZ V20.98 final cockpit pass',e)}

    document.querySelectorAll('#v175Coach360 .empty,#coachStudentBody .empty').forEach(node=>{"""
    if body.count(fin_anchor)!=1:
        raise RuntimeError("V20.98 summary finalizer anchor mismatch")
    body=body.replace(fin_anchor,fin_repl,1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

def patch_v280(body):
    # Once the current state has explicitly been reviewed, persistent conditions
    # such as status='Revisar', low adherence or inactivity must not immediately
    # recreate the same review request. They become pending again on new changes
    # or when the configured review cadence expires.
    old=r"""    let reviewDue=false,changed=false;
    try{if(typeof coachReviewLoopStateV238==='function'){const r=coachReviewLoopStateV238(s)||{};reviewDue=!!r.reviewDue;changed=!!r.changed}}catch(_e){}
    const adh=Number(typeof adherence==='function'?adherence(s):0)||0;
    const inactive=daysSince(s?.lastWorkout);
    const needsReview=(()=>{try{return typeof statusFor==='function'&&statusFor(s)==='Revisar'}catch(_e){return false}})();
    if(critical>0||pendingFeedback>0)return {bucket:'urgent',score:100+critical*20+pendingFeedback*12,label:pendingFeedback?pendingFeedback+' feedback pendiente':critical+' señal crítica'};
    if(reviewDue||changed||needsReview||adh<70||inactive>=7||feed.length>0){
      const bits=[];if(reviewDue)bits.push('revisión vencida');if(changed)bits.push('cambios nuevos');if(adh<70)bits.push('adherencia '+adh+'%');if(inactive>=7&&inactive<999)bits.push(inactive+' días sin entrenar');if(feed.length)bits.push(feed.length+' alertas');
      return {bucket:'today',score:50+feed.length*3+(reviewDue?8:0)+(adh<70?4:0),label:bits.slice(0,2).join(' · ')||'Revisar seguimiento'};
    }"""
    new=r"""    let reviewDue=false,changed=false,hasBaseline=false;
    try{if(typeof coachReviewLoopStateV238==='function'){const r=coachReviewLoopStateV238(s)||{};reviewDue=!!r.reviewDue;changed=!!r.changed;hasBaseline=!!r.hasBaseline}}catch(_e){}
    const reviewCurrent=hasBaseline&&!changed&&!reviewDue;
    const adh=Number(typeof adherence==='function'?adherence(s):0)||0;
    const inactive=daysSince(s?.lastWorkout);
    const needsReview=(()=>{try{return !reviewCurrent&&typeof statusFor==='function'&&statusFor(s)==='Revisar'}catch(_e){return false}})();
    const lowAdherence=!reviewCurrent&&adh<70;
    const inactivityReview=!reviewCurrent&&inactive>=7;
    if(critical>0||pendingFeedback>0)return {bucket:'urgent',score:100+critical*20+pendingFeedback*12,label:pendingFeedback?pendingFeedback+' feedback pendiente':critical+' señal crítica'};
    if(reviewDue||changed||needsReview||lowAdherence||inactivityReview||feed.length>0){
      const bits=[];if(reviewDue)bits.push('revisión vencida');if(changed)bits.push('cambios nuevos');if(lowAdherence)bits.push('adherencia '+adh+'%');if(inactivityReview&&inactive<999)bits.push(inactive+' días sin entrenar');if(feed.length)bits.push(feed.length+' alertas');
      return {bucket:'today',score:50+feed.length*3+(reviewDue?8:0)+(lowAdherence?4:0),label:bits.slice(0,2).join(' · ')||'Revisar seguimiento'};
    }"""
    if body.count(old)!=1:
        raise RuntimeError("V20.98 priority review-state anchor mismatch")
    body=body.replace(old,new,1)

    row_old="""    const row=x=>'<button class="v280-priority-row" onclick="window.__fjzOpenPriorityV280(\\''+esc(x.s.id)+'\\',\\''+esc(priorityTab(x.s))+'\\')"><span class="v280-priority-avatar">'+esc((x.s.name||'A').slice(0,2).toUpperCase())+'</span><span class="v280-priority-copy"><strong>'+esc(x.s.name||'Alumno')+'</strong><small>'+esc(x.label||'Seguimiento')+'</small></span><span class="v280-priority-arrow">›</span></button>';"""
    row_new=r"""    const reviewAckNeeded=x=>{
      try{
        const r=typeof coachReviewLoopStateV238==='function'?(coachReviewLoopStateV238(x.s)||{}):{};
        if(r.hasBaseline&&!r.changed&&!r.reviewDue)return false;
        const adh=Number(typeof adherence==='function'?adherence(x.s):0)||0;
        const inactive=daysSince(x.s?.lastWorkout);
        const status=typeof statusFor==='function'?statusFor(x.s):'';
        return !r.hasBaseline||!!r.changed||!!r.reviewDue||status==='Revisar'||adh<70||inactive>=7;
      }catch(_e){return false}
    };
    const row=x=>{
      const open='<button class="v280-priority-row" onclick="window.__fjzOpenPriorityV280(\''+esc(x.s.id)+'\',\''+esc(priorityTab(x.s))+'\')"><span class="v280-priority-avatar">'+esc((x.s.name||'A').slice(0,2).toUpperCase())+'</span><span class="v280-priority-copy"><strong>'+esc(x.s.name||'Alumno')+'</strong><small>'+esc(x.label||'Seguimiento')+'</small></span><span class="v280-priority-arrow">›</span></button>';
      const ok=reviewAckNeeded(x)?'<button class="btn small v298-priority-ok" onclick="window.__fjzMarkCoachReviewOkV298?.(\''+esc(x.s.id)+'\')">✓ OK</button>':'';
      return '<div class="v298-priority-wrap">'+open+ok+'</div>';
    };"""
    if body.count(row_old)!=1:
        raise RuntimeError("V20.98 priority row anchor mismatch")
    body=body.replace(row_old,row_new,1)
    return body

html=edit_script(html,"v280OperationalRecoveryRuntime",patch_v280)

css=r"""
/* TEAM FJZ · V20.98 REVIEW ACK + COCKPIT FINAL STATE */
.v298-review-main-ok{
  min-width:138px;
}
.v298-priority-wrap{
  display:grid;
  grid-template-columns:minmax(0,1fr) auto;
  gap:6px;
  align-items:stretch;
  min-width:0;
}
.v298-priority-wrap>.v280-priority-row{
  width:100%;
  min-width:0;
}
.v298-priority-ok{
  align-self:stretch;
  min-width:62px;
  padding-inline:8px!important;
  border-color:rgba(59,213,138,.30)!important;
  color:#aef0ca!important;
  background:rgba(59,213,138,.055)!important;
}
.v298-priority-ok:hover{
  border-color:rgba(59,213,138,.50)!important;
  background:rgba(59,213,138,.10)!important;
}
@media(max-width:560px){
  .v298-priority-wrap{
    grid-template-columns:minmax(0,1fr) 58px;
    gap:5px;
  }
  .v298-priority-ok{
    min-width:58px;
    padding-inline:5px!important;
  }
}
"""
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.98 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-review-ok-cockpit-fix" content="20.98">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V20.98 runtime topology changed "+key+": "+repr({"before":before,"after":after}))

required=[
    'meta name="fjz-review-ok-cockpit-fix" content="20.98"',
    "fallbackCoachCockpitV298",
    "__fjzMarkCoachReviewOkV298",
    "✓ Revisado / OK",
    "v298-priority-ok",
    "reviewCurrent=hasBaseline&&!changed&&!reviewDue",
    "window.__fjzRenderCoachCockpitV268?.()",
]
for marker in required:
    if marker not in html:
        raise RuntimeError("V20.98 missing marker "+marker)

if "Preparando lectura operativa" in html:
    raise RuntimeError("V20.98 stale operational-reading placeholder survived")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.98 review OK + coach cockpit final-state fix")
print("V20.98 BEFORE:",before)
print("V20.98 AFTER:",after)
print("V20.98 exact operational placeholder removed; review acknowledgement enabled")
