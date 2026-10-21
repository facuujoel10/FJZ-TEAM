import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.42 COACH SESSION FEEDBACK RESPONSE
# =========================================================
# Coach reviews structured session feedback stored inside the workout session.
# The student sees the latest coach response on Home.
# No new schema/backend/realtime/listener/timer.

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

def edit_script(doc,script_id,transform):
    pat=re.compile(
        r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',
        re.S|re.I
    )
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.42 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.42 no script change")
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-session-feedback" content="20.41"',
    "structuredSessionFeedback:true",
    "session.sessionFeedback",
    "coachReviewCadence:true",
    "renderReviewHubV237"
]:
    if marker not in html:
        raise RuntimeError("V20.42 missing prerequisite: "+marker)

def patch_v175(body):
    anchor="  /* ---------- Coach review hub V20.37 ---------- */"
    if body.count(anchor)!=1:
        raise RuntimeError("V20.42 V175 insertion anchor mismatch")

    helpers=r"""
  /* ---------- Session feedback response V20.42 ---------- */
  function sessionFeedbackRowsV242(s=student()){
    return (s?.sessions||[])
      .filter(x=>x?.sessionFeedback)
      .slice()
      .sort((a,b)=>(Date.parse(b?.date||0)||0)-(Date.parse(a?.date||0)||0));
  }

  function pendingSessionFeedbackV242(s=student()){
    return sessionFeedbackRowsV242(s).filter(x=>x?.sessionFeedback?.status==='pending');
  }

  function sessionDifficultyLabelV242(v){
    const map={
      technique:'Técnica',
      load:'Carga / peso',
      fatigue:'Fatiga / energía',
      discomfort:'Molestia',
      time:'Tiempo',
      equipment:'Equipo / gimnasio',
      motivation:'Motivación',
      other:'Otra'
    };
    return map[v]||v||'';
  }

  function sessionDecisionLabelV242(v){
    const map={
      maintain:'Mantener plan',
      adjust_load:'Ajustar carga',
      adjust_technique:'Priorizar técnica',
      adjust_volume:'Ajustar volumen',
      recovery:'Priorizar recuperación',
      contact:'Hablar con el alumno',
      checkin:'Revisar check-in',
      observe:'Seguir observando',
      other:'Otra decisión'
    };
    return map[v]||'Seguimiento';
  }

  function sessionFeedbackCardV242(ss){
    const fb=ss?.sessionFeedback||{};
    const review=fb.coachReview||null;
    const types=(fb.difficultyTypes||[]).map(sessionDifficultyLabelV242).filter(Boolean);
    const status=fb.status==='pending'
      ?'<span class="badge red">Pendiente</span>'
      :fb.status==='reviewed'
        ?'<span class="badge green">Revisado</span>'
        :'<span class="badge blue">Sin dificultad</span>';

    const difficulty=types.length
      ?'<div class="v242-feedback-tags">'+types.map(x=>'<span>'+esc(x)+'</span>').join('')+'</div>'
      :'';

    const studentText=fb.comment
      ?'<p class="v242-student-comment">'+esc(fb.comment)+'</p>'
      :'<p class="muted tiny">Sin comentario general.</p>';

    const coachText=review
      ?'<div class="v242-coach-response"><strong>'+esc(sessionDecisionLabelV242(review.decision))+'</strong>'+
        (review.nextStep?'<p>'+esc(review.nextStep)+'</p>':'')+
        (review.internalNote?'<div class="muted micro">Nota interna: '+esc(review.internalNote)+'</div>':'')+
      '</div>'
      :'';

    const action=fb.status==='pending'
      ?'<button class="btn small primary" onclick="openSessionFeedbackCoachV242(\''+esc(ss.id)+'\')">Revisar feedback</button>'
      :'';

    return '<div class="v242-session-card">'+
      '<div class="v242-session-head"><div><strong>'+esc(ss.dayName||'Entrenamiento')+'</strong>'+
      '<span>'+esc(fmtDate(ss.date))+' · '+esc(fb.sessionFeelLabel||'Normal')+'</span></div>'+status+'</div>'+
      difficulty+studentText+coachText+
      (action?'<div class="v242-session-actions">'+action+'</div>':'')+
    '</div>';
  }

  function renderSessionFeedbackCoachV242(){
    const host=el('v242SessionFeedbackCoach');
    if(!host)return;
    const rows=sessionFeedbackRowsV242();
    const pending=rows.filter(x=>x?.sessionFeedback?.status==='pending');
    const rest=rows.filter(x=>x?.sessionFeedback?.status!=='pending');
    const ordered=[...pending,...rest].slice(0,4);

    host.innerHTML=
      '<div class="v175-360-section-head"><div><h4>Feedback de sesiones</h4>'+
      '<p>Dificultades reportadas por el alumno y tu devolución sobre cómo seguir.</p></div>'+
      '<span class="badge '+(pending.length?'red':'green')+'">'+pending.length+' pendiente'+(pending.length===1?'':'s')+'</span></div>'+
      (ordered.length
        ?'<div class="v242-session-list">'+ordered.map(sessionFeedbackCardV242).join('')+'</div>'
        :'<div class="empty">Todavía no hay feedback de cierre de sesión.</div>');
  }

  window.__fjzPendingSessionFeedbackCountV242=function(s=student()){
    return pendingSessionFeedbackV242(s).length;
  };

  window.openSessionFeedbackCoachV242=function(sessionId){
    const ss=(student()?.sessions||[]).find(x=>x?.id===sessionId);
    const fb=ss?.sessionFeedback;
    if(!ss||!fb)return;

    const old=fb.coachReview||{};
    showModal(
      '<div class="modal-head"><div><h3>Revisar feedback</h3><div class="muted tiny">'+esc(ss.dayName||'Entrenamiento')+' · '+esc(fmtDate(ss.date))+'</div></div>'+
      '<button class="btn small" type="button" aria-label="Cerrar" title="Cerrar" onclick="closeModal()">✕</button></div>'+
      '<div class="v242-review-form">'+
        '<div class="v242-review-source">'+
          '<strong>Alumno · '+esc(fb.sessionFeelLabel||'Normal')+'</strong>'+
          ((fb.difficultyTypes||[]).length
            ?'<div class="v242-feedback-tags">'+(fb.difficultyTypes||[]).map(x=>'<span>'+esc(sessionDifficultyLabelV242(x))+'</span>').join('')+'</div>'
            :'')+
          '<p>'+esc(fb.comment||'Sin comentario general.')+'</p>'+
        '</div>'+
        '<label class="tiny muted">Decisión actual'+
          '<select id="v242CoachDecision" class="input">'+
            '<option value="maintain">Mantener plan</option>'+
            '<option value="adjust_load">Ajustar carga</option>'+
            '<option value="adjust_technique">Priorizar técnica</option>'+
            '<option value="adjust_volume">Ajustar volumen</option>'+
            '<option value="recovery">Priorizar recuperación</option>'+
            '<option value="contact">Hablar con el alumno</option>'+
            '<option value="checkin">Revisar check-in</option>'+
            '<option value="observe">Seguir observando</option>'+
            '<option value="other">Otra decisión</option>'+
          '</select>'+
        '</label>'+
        '<label class="tiny muted">Cómo seguimos · visible para el alumno'+
          '<textarea id="v242CoachNextStep" class="input" rows="4" maxlength="700" placeholder="Ej: mantenemos la carga esta semana y priorizamos la técnica.">'+esc(old.nextStep||'')+'</textarea>'+
        '</label>'+
        '<label class="tiny muted">Nota interna del coach · solo para vos'+
          '<textarea id="v242CoachInternal" class="input" rows="3" maxlength="600" placeholder="Contexto interno opcional.">'+esc(old.internalNote||'')+'</textarea>'+
        '</label>'+
        '<button class="btn primary" style="width:100%" onclick="saveSessionFeedbackCoachV242(\''+esc(ss.id)+'\')">Guardar devolución y marcar revisado</button>'+
      '</div>'
    );

    const select=el('v242CoachDecision');
    if(select&&old.decision)select.value=old.decision;
  };

  window.saveSessionFeedbackCoachV242=function(sessionId){
    const s=student();
    const ss=(s?.sessions||[]).find(x=>x?.id===sessionId);
    const fb=ss?.sessionFeedback;
    if(!s||!ss||!fb)return;

    const decision=String(el('v242CoachDecision')?.value||'maintain');
    const nextStep=String(el('v242CoachNextStep')?.value||'').trim().slice(0,700);
    const internalNote=String(el('v242CoachInternal')?.value||'').trim().slice(0,600);

    fb.status='reviewed';
    fb.coachReview={
      status:'reviewed',
      decision,
      nextStep,
      internalNote,
      reviewedAt:new Date().toISOString()
    };

    saveState();
    closeModal?.();
    renderSessionFeedbackCoachV242();
    toast?.('Feedback revisado y devolución guardada');
  };

  function latestStudentCoachReplyV242(s=student()){
    return sessionFeedbackRowsV242(s)
      .find(x=>x?.sessionFeedback?.coachReview?.status==='reviewed')||null;
  }

  function injectStudentCoachReplyV242(){
    if(!(mode==='student'&&studentTab==='home'))return;
    const view=el('view');if(!view)return;
    el('v242StudentCoachReply')?.remove();

    const ss=latestStudentCoachReplyV242();
    const review=ss?.sessionFeedback?.coachReview;
    if(!ss||!review)return;

    const card=document.createElement('section');
    card.id='v242StudentCoachReply';
    card.className='card v242-student-reply';
    card.innerHTML=
      '<div class="section-title"><div><div class="v225-section-kicker">DEVOLUCIÓN DEL COACH</div>'+
      '<h3>'+esc(ss.dayName||'Última sesión')+'</h3>'+
      '<div class="muted tiny">'+esc(fmtDate(ss.date))+'</div></div>'+
      '<span class="badge green">Revisado</span></div>'+
      '<div class="v242-student-decision"><strong>'+esc(sessionDecisionLabelV242(review.decision))+'</strong>'+
      '<p>'+esc(review.nextStep||'Tu coach revisó el feedback de esta sesión.')+'</p></div>'+
      '<div class="v242-student-reply-actions">'+
        '<button class="btn" onclick="studentTab=\'history\';render()">Ver historial</button>'+
        '<button class="btn primary" onclick="studentTab=\'progress\';render()">Ver progreso</button>'+
      '</div>';

    const anchor=el('v115StudentProfileCard')||el('v175StudentProfilePlaceholder')||view.querySelector('.hero');
    if(anchor)anchor.insertAdjacentElement('afterend',card);
    else view.prepend(card);
  }

"""
    body=body.replace(anchor,helpers+anchor,1)

    # Render coach feedback section after the review hub is hydrated.
    hydrate_old="""    reviewCurrentV237=reviewSnapshotV237(s,latest,weight,pending,agenda,nutrition);
    renderReviewHubV237(reviewCurrentV237);

    if(el('v175Metrics'))"""
    hydrate_new="""    reviewCurrentV237=reviewSnapshotV237(s,latest,weight,pending,agenda,nutrition);
    renderReviewHubV237(reviewCurrentV237);
    renderSessionFeedbackCoachV242();

    if(el('v175Metrics'))"""
    if body.count(hydrate_old)!=1:
        raise RuntimeError("V20.42 hydrate feedback anchor mismatch")
    body=body.replace(hydrate_old,hydrate_new,1)

    # Add section to canonical Resumen 360.
    review_section="""      '<div class="v175-360-section v237-review-section" id="v237ReviewHub"><div class="empty">Preparando comparación con tu última revisión…</div></div>'+
"""
    feedback_section="""      '<div class="v175-360-section v242-session-feedback-section" id="v242SessionFeedbackCoach"><div class="empty">Revisando feedback de sesiones…</div></div>'+
"""
    if body.count(review_section)!=1:
        raise RuntimeError("V20.42 review section anchor mismatch")
    body=body.replace(review_section,review_section+feedback_section,1)

    # Reuse existing centralized post-render; no new render wrapper.
    post_old="""    if(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'){
      try{
        const fn=typeof injectMyProfileV115==='function'?injectMyProfileV115:null;
        Promise.resolve(fn?.()).then(()=>{finalizeStudentProfileV175();fillStudentAvatarV175()}).catch(()=>{});
      }catch(e){}
    }"""
    post_new="""    if(mode==='student'&&studentTab==='home'){
      injectStudentCoachReplyV242();
      if(currentProfile?.role==='student'){
        try{
          const fn=typeof injectMyProfileV115==='function'?injectMyProfileV115:null;
          Promise.resolve(fn?.()).then(()=>{
            finalizeStudentProfileV175();
            fillStudentAvatarV175();
            injectStudentCoachReplyV242();
          }).catch(()=>{});
        }catch(e){}
      }
    }"""
    if body.count(post_old)!=1:
        raise RuntimeError("V20.42 postRender student anchor mismatch")
    body=body.replace(post_old,post_new,1)

    marker_old="""    coachReviewCadence:true,
    reviewCadenceOptions:[7,14,30]
  };"""
    marker_new="""    coachReviewCadence:true,
    reviewCadenceOptions:[7,14,30],
    sessionFeedbackCoachReview:true,
    studentSeesCoachNextStep:true,
    sessionFeedbackInternalNoteCoachOnly:true
  };"""
    if body.count(marker_old)!=1:
        raise RuntimeError("V20.42 marker object mismatch")
    body=body.replace(marker_old,marker_new,1)

    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

css=r"""
/* TEAM FJZ · V20.42 COACH SESSION FEEDBACK RESPONSE */
.v242-session-feedback-section{
  border-color:rgba(103,173,255,.16);
}
.v242-session-list{
  display:grid;
  gap:8px;
}
.v242-session-card{
  padding:11px;
  border:1px solid #2c3038;
  border-radius:12px;
  background:#0d0e12;
}
.v242-session-head{
  display:flex;
  justify-content:space-between;
  gap:10px;
  align-items:flex-start;
}
.v242-session-head strong{
  display:block;
  color:#f4f5f7;
  font-size:11px;
}
.v242-session-head span:not(.badge){
  display:block;
  margin-top:3px;
  color:#8f939e;
  font-size:9px;
}
.v242-feedback-tags{
  display:flex;
  gap:5px;
  flex-wrap:wrap;
  margin-top:8px;
}
.v242-feedback-tags span{
  padding:4px 7px;
  border:1px solid rgba(242,189,85,.20);
  border-radius:999px;
  background:rgba(242,189,85,.055);
  color:#e8c578;
  font-size:8px;
  font-weight:780;
}
.v242-student-comment{
  margin:8px 0 0;
  color:#b7bac2;
  font-size:10px;
  line-height:1.48;
}
.v242-coach-response{
  margin-top:9px;
  padding:9px 10px;
  border-left:3px solid #3bd58a;
  border-radius:0 9px 9px 0;
  background:rgba(59,213,138,.045);
}
.v242-coach-response strong{
  color:#a5e7c2;
  font-size:10px;
}
.v242-coach-response p{
  margin:4px 0 0;
  color:#c3c7ce;
  font-size:9px;
  line-height:1.45;
}
.v242-session-actions{
  display:flex;
  justify-content:flex-end;
  margin-top:9px;
}
.v242-review-form{
  display:grid;
  gap:12px;
}
.v242-review-form label{
  display:grid;
  gap:6px;
}
.v242-review-source{
  padding:10px 11px;
  border:1px solid #2d3038;
  border-radius:11px;
  background:#0d0e12;
}
.v242-review-source>strong{
  color:#f4f5f7;
  font-size:11px;
}
.v242-review-source>p{
  margin:8px 0 0;
  color:#b6b9c1;
  font-size:10px;
  line-height:1.48;
}
.v242-student-reply{
  border-color:rgba(59,213,138,.18);
  background:
    linear-gradient(145deg,rgba(59,213,138,.045),transparent 50%),
    var(--card);
}
.v242-student-decision{
  padding:11px;
  border:1px solid rgba(59,213,138,.18);
  border-radius:12px;
  background:rgba(59,213,138,.035);
}
.v242-student-decision strong{
  color:#a9e9c6;
  font-size:12px;
}
.v242-student-decision p{
  margin:6px 0 0;
  color:#c0c4cb;
  font-size:10px;
  line-height:1.5;
}
.v242-student-reply-actions{
  display:flex;
  justify-content:flex-end;
  gap:7px;
  margin-top:10px;
}
@media(max-width:560px){
  .v242-session-head{
    display:grid;
  }
  .v242-student-reply-actions{
    display:grid;
    grid-template-columns:1fr 1fr;
  }
  .v242-student-reply-actions .btn{
    width:100%;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.42 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-session-feedback-response" content="20.42">\n</head>',1)

after=metrics(html)
for key in (
    "styles","renders","channels","timeouts","rafs","listeners",
    "mutation_observers","performance_observers"
):
    if after[key]!=before[key]:
        raise RuntimeError("V20.42 topology changed "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-session-feedback-response" content="20.42"',
    "pendingSessionFeedbackV242","renderSessionFeedbackCoachV242",
    "openSessionFeedbackCoachV242","saveSessionFeedbackCoachV242",
    "injectStudentCoachReplyV242","coachReview",
    "nextStep","internalNote",
    "sessionFeedbackCoachReview:true",
    "studentSeesCoachNextStep:true",
    "sessionFeedbackInternalNoteCoachOnly:true",
    "v242SessionFeedbackCoach","v242StudentCoachReply"
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.42 missing response marker: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.42 coach session feedback response")
print("V20.42 BEFORE:",before)
print("V20.42 AFTER:",after)
print("V20.42 coach decision/next-step + student reply added; topology unchanged")
