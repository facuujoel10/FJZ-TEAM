import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.43 STUDENT JOURNEY + FEEDBACK PRIORITY
# =========================================================
# Connects pending session feedback to coach work queue and improves the
# student's post-session next step. No backend/realtime/listener/timer growth.

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
        raise RuntimeError("V20.43 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.43 no script change for "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-session-feedback-response" content="20.42"',
    "__fjzPendingSessionFeedbackCountV242",
    "openNextCoachPriorityV236",
    "coachFocusScoreV235",
    "coachReviewLoopStateV238",
    "cloudConfirmationBeforeSuccess:true"
]:
    if marker not in html:
        raise RuntimeError("V20.43 missing prerequisite: "+marker)

# ---------------------------------------------------------
# Coach dashboard/work queue
# ---------------------------------------------------------
helper_anchor="function coachFocusScoreV235(s){"
if html.count(helper_anchor)!=1:
    raise RuntimeError("V20.43 coach focus anchor mismatch")
helper=r"""
function pendingSessionFeedbackCountV243(s){
  try{return Number(window.__fjzPendingSessionFeedbackCountV242?.(s)||0)}
  catch(_e){return 0}
}

function coachSessionFeedbackStudentsV243(){
  return (state.students||[]).filter(s=>pendingSessionFeedbackCountV243(s)>0);
}

"""
html=html.replace(helper_anchor,helper+helper_anchor,1)

score_old="""function coachFocusScoreV235(s){
  const o=coachStateV235(s),r=coachReviewLoopStateV238(s);
  return coachCriticalV235(s)*8+
    coachPendingV235(s)*3+
    (o.review?5:0)+
    (o.low?3:0)+
    (o.inactive?2:0)+
    (r.changed?4:0)+
    (r.reviewDue?3:0)+
    (!r.hasBaseline?2:0);
}"""
score_new="""function coachFocusScoreV235(s){
  const o=coachStateV235(s),r=coachReviewLoopStateV238(s);
  const sf=pendingSessionFeedbackCountV243(s);
  return coachCriticalV235(s)*8+
    coachPendingV235(s)*3+
    sf*7+
    (o.review?5:0)+
    (o.low?3:0)+
    (o.inactive?2:0)+
    (r.changed?4:0)+
    (r.reviewDue?3:0)+
    (!r.hasBaseline?2:0);
}"""
if html.count(score_old)!=1:
    raise RuntimeError("V20.43 coach score mismatch")
html=html.replace(score_old,score_new,1)

filter_old="""    if(coachStudentFilterV235==='due')return coachReviewLoopStateV238(s).reviewDue;
    return true;"""
filter_new="""    if(coachStudentFilterV235==='due')return coachReviewLoopStateV238(s).reviewDue;
    if(coachStudentFilterV235==='session_feedback')return pendingSessionFeedbackCountV243(s)>0;
    return true;"""
if html.count(filter_old)!=1:
    raise RuntimeError("V20.43 coach filter mismatch")
html=html.replace(filter_old,filter_new,1)

filter_bar_old="""  <button class="btn small" data-v235-filter="due" onclick="setCoachStudentFilterV235('due')">Revisión vencida · <span id="v240DueCount">0</span></button>
  <span class="badge blue" id="v235StudentCount">"""
filter_bar_new="""  <button class="btn small" data-v235-filter="due" onclick="setCoachStudentFilterV235('due')">Revisión vencida · <span id="v240DueCount">0</span></button>
  <button class="btn small" data-v235-filter="session_feedback" onclick="setCoachStudentFilterV235('session_feedback')">Feedback sesión · <span id="v243SessionFeedbackCount">0</span></button>
  <span class="badge blue" id="v235StudentCount">"""
if html.count(filter_bar_old)!=1:
    raise RuntimeError("V20.43 filter bar mismatch")
html=html.replace(filter_bar_old,filter_bar_new,1)

decorate_old="""  if(el('v240DueCount'))el('v240DueCount').textContent=String(c.due||0);
}"""
decorate_new="""  if(el('v240DueCount'))el('v240DueCount').textContent=String(c.due||0);
  if(el('v243SessionFeedbackCount'))el('v243SessionFeedbackCount').textContent=String(coachSessionFeedbackStudentsV243().length);
}"""
if html.count(decorate_old)!=1:
    raise RuntimeError("V20.43 count decoration mismatch")
html=html.replace(decorate_old,decorate_new,1)

best_tab_old="""function coachBestTabV236(s){
  const ath=coachAthleteV235(s);"""
best_tab_new="""function coachBestTabV236(s){
  if(pendingSessionFeedbackCountV243(s)>0)return 'summary';
  const ath=coachAthleteV235(s);"""
if html.count(best_tab_old)!=1:
    raise RuntimeError("V20.43 best-tab mismatch")
html=html.replace(best_tab_old,best_tab_new,1)

reason_old="""    const rv=coachReviewLoopStateV238(s);
    if(rv.reviewDue)bits.unshift(rv.reviewDueLabel);
    if(rv.changed)bits.unshift(rv.reason);"""
reason_new="""    const rv=coachReviewLoopStateV238(s);
    const sf=pendingSessionFeedbackCountV243(s);
    if(sf)bits.unshift(sf+' feedback de sesión pendiente'+(sf===1?'':'s'));
    if(rv.reviewDue)bits.unshift(rv.reviewDueLabel);
    if(rv.changed)bits.unshift(rv.reason);"""
if html.count(reason_old)!=1:
    raise RuntimeError("V20.43 focus reason mismatch")
html=html.replace(reason_old,reason_new,1)

# Session feedback must keep a student in the "changed" review loop.
changed_old="""  const pending=coachPendingV235(s);

  if(!prev){"""
changed_new="""  const pending=coachPendingV235(s);
  const sessionPending=pendingSessionFeedbackCountV243(s);

  if(!prev){"""
if html.count(changed_old)!=1:
    raise RuntimeError("V20.43 review-loop pending anchor mismatch")
html=html.replace(changed_old,changed_new,1)

no_prev_old="""      adherenceDelta:null,
      pending
    };"""
no_prev_new="""      adherenceDelta:null,
      pending,
      sessionPending
    };"""
if html.count(no_prev_old)!=1:
    raise RuntimeError("V20.43 no-prev return mismatch")
html=html.replace(no_prev_old,no_prev_new,1)

changed_expr_old="""    newSessions>0||
    pending>0||
    statusChanged||"""
changed_expr_new="""    newSessions>0||
    pending>0||
    sessionPending>0||
    statusChanged||"""
if html.count(changed_expr_old)!=1:
    raise RuntimeError("V20.43 changed expression mismatch")
html=html.replace(changed_expr_old,changed_expr_new,1)

bits_old="""  if(pending)bits.push(pending+' pendiente'+(pending===1?'':'s'));
  if(statusChanged)bits.push('estado '+currentStatus.toLowerCase());"""
bits_new="""  if(pending)bits.push(pending+' pendiente'+(pending===1?'':'s'));
  if(sessionPending)bits.push(sessionPending+' feedback sesión');
  if(statusChanged)bits.push('estado '+currentStatus.toLowerCase());"""
if html.count(bits_old)!=1:
    raise RuntimeError("V20.43 changed bits mismatch")
html=html.replace(bits_old,bits_new,1)

return_old="""    adherenceDelta,
    pending
  };"""
return_new="""    adherenceDelta,
    pending,
    sessionPending
  };"""
if html.count(return_old)!=1:
    raise RuntimeError("V20.43 review return mismatch")
html=html.replace(return_old,return_new,1)

# ---------------------------------------------------------
# V20.7 post-session success actions
# ---------------------------------------------------------
def patch_v207(body):
    success_old="""  function modalSuccessV207(){
    showModal(
      '<div class="v207-save-state">'+
        '<div class="v207-save-icon success">✓</div>'+
        '<div class="v207-save-title">Sesión guardada con éxito</div>'+
        '<div class="v207-save-copy">El entrenamiento quedó registrado correctamente. Ya podés salir con tranquilidad.</div>'+
        '<div class="v207-save-actions"><button class="btn primary" onclick="finishConfirmedSessionV207()">Listo</button></div>'+
      '</div>'
    );
  }"""
    success_new="""  function modalSuccessV207(){
    const fb=pendingV207?.session?.sessionFeedback||null;
    const feedbackText=fb?.status==='pending'
      ?' Tu feedback quedó enviado al coach para revisión.'
      :fb?.status==='clear'
        ?' No reportaste dificultades en esta sesión.'
        :'';
    showModal(
      '<div class="v207-save-state">'+
        '<div class="v207-save-icon success">✓</div>'+
        '<div class="v207-save-title">Sesión guardada con éxito</div>'+
        '<div class="v207-save-copy">El entrenamiento quedó registrado correctamente.'+feedbackText+'</div>'+
        '<div class="v207-save-actions">'+
          '<button class="btn" onclick="finishConfirmedSessionV243(\\'home\\')">Ir al inicio</button>'+
          '<button class="btn primary" onclick="finishConfirmedSessionV243(\\'progress\\')">Ver progreso</button>'+
        '</div>'+
      '</div>'
    );
  }"""
    if body.count(success_old)!=1:
        raise RuntimeError("V20.43 success modal mismatch")
    body=body.replace(success_old,success_new,1)

    finish_old="""  window.finishConfirmedSessionV207=function(){
    if(stateV207!=='success')return;
    try{closeModal?.()}catch(_e){}
    studentTab='home';
    currentDay=-1;
    render();
  };"""
    finish_new="""  window.finishConfirmedSessionV243=function(destination){
    if(stateV207!=='success')return;
    try{closeModal?.()}catch(_e){}
    studentTab=destination==='progress'?'progress':'home';
    currentDay=-1;
    render();
  };

  window.finishConfirmedSessionV207=function(){
    return window.finishConfirmedSessionV243('home');
  };"""
    if body.count(finish_old)!=1:
        raise RuntimeError("V20.43 finish success action mismatch")
    body=body.replace(finish_old,finish_new,1)

    marker_old="""    productionCoachCannotSubmitStudentFeedback:true
  };"""
    marker_new="""    productionCoachCannotSubmitStudentFeedback:true,
    postSessionProgressShortcut:true,
    feedbackStatusShownAfterSave:true
  };"""
    if body.count(marker_old)!=1:
        raise RuntimeError("V20.43 V207 marker mismatch")
    body=body.replace(marker_old,marker_new,1)
    return body

html=edit_script(html,"v207ConfirmedSessionCommitRuntime",patch_v207)

# ---------------------------------------------------------
# Student Home "next step" card using existing V17.5 post-render
# ---------------------------------------------------------
def patch_v175(body):
    anchor="  /* ---------- Session feedback response V20.42 ---------- */"
    if body.count(anchor)!=1:
        raise RuntimeError("V20.43 V175 insertion anchor mismatch")

    helper=r"""
  /* ---------- Student next step V20.43 ---------- */
  function injectStudentNextStepV243(){
    if(!(mode==='student'&&studentTab==='home'))return;
    const view=el('view');if(!view)return;
    el('v243StudentNextStep')?.remove();

    const s=student?.();
    const latest=(s?.sessions||[]).slice().sort(
      (a,b)=>(Date.parse(b?.date||0)||0)-(Date.parse(a?.date||0)||0)
    )[0]||null;
    if(!latest)return;

    const fb=latest.sessionFeedback||null;
    if(fb?.status==='reviewed')return; // V20.42 response card is the authority.

    const pending=fb?.status==='pending';
    const card=document.createElement('section');
    card.id='v243StudentNextStep';
    card.className='card v243-next-step';
    card.innerHTML=
      '<div class="section-title"><div><div class="v225-section-kicker">PRÓXIMO PASO</div>'+
      '<h3>'+(pending?'Feedback enviado':'Sesión guardada')+'</h3>'+
      '<div class="muted tiny">'+esc(latest.dayName||'Última sesión')+' · '+esc(fmtDate(latest.date))+'</div></div>'+
      '<span class="badge '+(pending?'amber':'green')+'">'+(pending?'En revisión':'Completado')+'</span></div>'+
      '<p>'+(pending
        ?'Tu coach puede ver la dificultad y el comentario que dejaste. Cuando lo revise, su devolución va a aparecer acá.'
        :'Podés revisar cómo viene tu progreso o completar el seguimiento para darle más contexto a tu coach.')+'</p>'+
      '<div class="v243-next-actions">'+
        '<button class="btn" onclick="studentTab=\\'tracking\\';render()">Check-in</button>'+
        '<button class="btn primary" onclick="studentTab=\\'progress\\';render()">Ver progreso</button>'+
      '</div>';

    const anchor=el('v242StudentCoachReply')||
      el('v115StudentProfileCard')||
      el('v175StudentProfilePlaceholder')||
      view.querySelector('.hero');
    if(anchor)anchor.insertAdjacentElement('afterend',card);
    else view.prepend(card);
  }

"""
    body=body.replace(anchor,helper+anchor,1)

    post_old="""    if(mode==='student'&&studentTab==='home'){
      injectStudentCoachReplyV242();"""
    post_new="""    if(mode==='student'&&studentTab==='home'){
      injectStudentCoachReplyV242();
      injectStudentNextStepV243();"""
    if body.count(post_old)!=1:
        raise RuntimeError("V20.43 student postRender anchor mismatch")
    body=body.replace(post_old,post_new,1)

    promise_old="""            injectStudentCoachReplyV242();
          }).catch(()=>{});"""
    promise_new="""            injectStudentCoachReplyV242();
            injectStudentNextStepV243();
          }).catch(()=>{});"""
    if body.count(promise_old)!=1:
        raise RuntimeError("V20.43 profile promise anchor mismatch")
    body=body.replace(promise_old,promise_new,1)

    marker_old="""    sessionFeedbackInternalNoteCoachOnly:true
  };"""
    marker_new="""    sessionFeedbackInternalNoteCoachOnly:true,
    studentNextStepCard:true
  };"""
    if body.count(marker_old)!=1:
        raise RuntimeError("V20.43 V175 marker mismatch")
    body=body.replace(marker_old,marker_new,1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

css=r"""
/* TEAM FJZ · V20.43 STUDENT JOURNEY + FEEDBACK PRIORITY */
.v243-next-step{
  border-color:rgba(103,173,255,.17);
  background:
    linear-gradient(145deg,rgba(103,173,255,.045),transparent 52%),
    var(--card);
}
.v243-next-step>p{
  margin:0;
  color:#aeb2bb;
  font-size:10px;
  line-height:1.5;
}
.v243-next-actions{
  display:flex;
  justify-content:flex-end;
  gap:7px;
  margin-top:11px;
}
@media(max-width:560px){
  .v243-next-actions{
    display:grid;
    grid-template-columns:1fr 1fr;
  }
  .v243-next-actions .btn{
    width:100%;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.43 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-student-journey" content="20.43">\n</head>',1)

after=metrics(html)
for key in (
    "styles","renders","channels","timeouts","rafs","listeners",
    "mutation_observers","performance_observers"
):
    if after[key]!=before[key]:
        raise RuntimeError("V20.43 topology changed "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-student-journey" content="20.43"',
    "pendingSessionFeedbackCountV243",
    "session_feedback",
    "Feedback sesión",
    "finishConfirmedSessionV243",
    "postSessionProgressShortcut:true",
    "feedbackStatusShownAfterSave:true",
    "injectStudentNextStepV243",
    "studentNextStepCard:true",
    "__fjzPendingSessionFeedbackCountV242",
    "openNextCoachPriorityV236",
    "cloudConfirmationBeforeSuccess:true"
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.43 missing journey marker: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.43 student journey + feedback priority")
print("V20.43 BEFORE:",before)
print("V20.43 AFTER:",after)
print("V20.43 pending session feedback now drives coach priority; student next-step improved")
