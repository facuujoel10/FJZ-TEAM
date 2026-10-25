import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.41 STUDENT SESSION FEEDBACK
# =========================================================
# Structured session feedback is attached to the SAME workout session before
# V20.7 cloud confirmation. No new backend/schema/realtime/listener/timer.

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
        raise RuntimeError("V20.41 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.41 no script change")
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-coach-review-cadence" content="20.40"',
    "cloudConfirmationBeforeSuccess:true",
    "retryUsesSameSessionId:true",
    "__fjzQueueSessionSyncV201",
    "__fjzSaveSessionV205"
]:
    if marker not in html:
        raise RuntimeError("V20.41 missing prerequisite: "+marker)

def patch_v207(body):
    create_anchor="  function createPendingV207(pack){"
    if body.count(create_anchor)!=1:
        raise RuntimeError("V20.41 createPending anchor mismatch")

    helpers=r"""
  /* ---------- Student session feedback V20.41 ---------- */
  let feedbackPackV241=null;

  function canSubmitSessionFeedbackV241(){
    return currentProfile?.role==='student' || !!window.__fjzStagingLocal?.enabled;
  }

  function sessionFeelLabelV241(v){
    const map={
      easy:'Liviana',
      normal:'Normal',
      hard:'Exigente',
      very_hard:'Muy exigente'
    };
    return map[v]||'Normal';
  }

  function openSessionFeedbackV241(pack){
    if(!pack)return;

    // Production coaches must never submit on behalf of a student.
    if(!canSubmitSessionFeedbackV241()){
      beginCommitV207(pack);
      return;
    }

    feedbackPackV241=pack;
    showModal(
      '<div class="modal-head"><div><h3>¿Cómo salió la sesión?</h3><div class="muted tiny">Tu respuesta queda ligada a este entrenamiento para que tu coach la revise.</div></div>'+
      '<button class="btn small" type="button" aria-label="Cerrar" title="Cerrar" onclick="closeModal()">✕</button></div>'+
      '<div class="v241-feedback-form">'+
        '<label class="tiny muted">Cómo se sintió la sesión'+
          '<select id="v241SessionFeel" class="input">'+
            '<option value="easy">Liviana</option>'+
            '<option value="normal" selected>Normal</option>'+
            '<option value="hard">Exigente</option>'+
            '<option value="very_hard">Muy exigente</option>'+
          '</select>'+
        '</label>'+
        '<div>'+
          '<div class="tiny muted" style="margin-bottom:7px">¿Tuviste alguna dificultad? Marcá lo que corresponda.</div>'+
          '<div class="v241-difficulty-grid">'+
            '<label><input type="checkbox" name="v241Difficulty" value="technique"><span>Técnica</span></label>'+
            '<label><input type="checkbox" name="v241Difficulty" value="load"><span>Carga / peso</span></label>'+
            '<label><input type="checkbox" name="v241Difficulty" value="fatigue"><span>Fatiga / energía</span></label>'+
            '<label><input type="checkbox" name="v241Difficulty" value="discomfort"><span>Molestia</span></label>'+
            '<label><input type="checkbox" name="v241Difficulty" value="time"><span>Tiempo</span></label>'+
            '<label><input type="checkbox" name="v241Difficulty" value="equipment"><span>Equipo / gimnasio</span></label>'+
            '<label><input type="checkbox" name="v241Difficulty" value="motivation"><span>Motivación</span></label>'+
            '<label><input type="checkbox" name="v241Difficulty" value="other"><span>Otra</span></label>'+
          '</div>'+
        '</div>'+
        '<label class="tiny muted">Comentario general'+
          '<textarea id="v241SessionComment" class="input" rows="4" maxlength="700" placeholder="Ej: hoy me costó sostener la técnica al final / me sentí con poca energía / todo salió muy bien."></textarea>'+
        '</label>'+
        '<div class="v241-feedback-note">También podés seguir usando el comentario de cada ejercicio cuando quieras señalar algo puntual.</div>'+
        '<div class="v241-feedback-actions">'+
          '<button class="btn" onclick="submitSessionFeedbackV241(true)">Todo bien · finalizar</button>'+
          '<button class="btn primary" onclick="submitSessionFeedbackV241(false)">Enviar feedback y finalizar</button>'+
        '</div>'+
      '</div>'
    );
  }

  window.submitSessionFeedbackV241=function(clear){
    const pack=feedbackPackV241;
    if(!pack)return;

    const feel=String(el('v241SessionFeel')?.value||'normal');
    const types=clear?[]:[...document.querySelectorAll('input[name="v241Difficulty"]:checked')]
      .map(x=>String(x.value||''))
      .filter(Boolean);
    const comment=clear?'':String(el('v241SessionComment')?.value||'').trim().slice(0,700);
    const needsCoach=!clear&&(types.length>0||comment.length>0||feel==='very_hard');

    pack.sessionFeedbackV241={
      version:1,
      submittedAt:new Date().toISOString(),
      sessionFeel:clear?'normal':feel,
      sessionFeelLabel:sessionFeelLabelV241(clear?'normal':feel),
      difficultyTypes:types,
      hadDifficulty:types.length>0,
      comment,
      status:needsCoach?'pending':'clear',
      coachReview:null
    };

    feedbackPackV241=null;
    try{closeModal?.()}catch(_e){}
    beginCommitV207(pack);
  };

  window.cancelSessionFeedbackV241=function(){
    feedbackPackV241=null;
    try{closeModal?.()}catch(_e){}
  };

"""
    body=body.replace(create_anchor,helpers+create_anchor,1)

    attach_old="""    attachMethodHistoryV207(pack,session);
    try{saveState()}catch(_e){}"""
    attach_new="""    attachMethodHistoryV207(pack,session);
    if(pack?.sessionFeedbackV241){
      session.sessionFeedback=cloneV207(pack.sessionFeedbackV241);
    }
    try{saveState()}catch(_e){}"""
    if body.count(attach_old)!=1:
        raise RuntimeError("V20.41 session attach anchor mismatch")
    body=body.replace(attach_old,attach_new,1)

    direct_old="""    if(!missing){
      beginCommitV207(pack);
      return;
    }"""
    direct_new="""    if(!missing){
      openSessionFeedbackV241(pack);
      return;
    }"""
    if body.count(direct_old)!=1:
        raise RuntimeError("V20.41 complete finish anchor mismatch")
    body=body.replace(direct_old,direct_new,1)

    partial_old="""    const pack=window.__v106PendingSession;
    window.__v106PendingSession=null;
    if(!pack){closeModal?.();return}
    beginCommitV207(pack);"""
    partial_new="""    const pack=window.__v106PendingSession;
    window.__v106PendingSession=null;
    if(!pack){closeModal?.();return}
    openSessionFeedbackV241(pack);"""
    if body.count(partial_old)!=1:
        raise RuntimeError("V20.41 partial finish anchor mismatch")
    body=body.replace(partial_old,partial_new,1)

    start_old="""      window.__v106PendingSession=null;
      document.body?.classList.remove('v207-session-saving');"""
    start_new="""      window.__v106PendingSession=null;
      feedbackPackV241=null;
      document.body?.classList.remove('v207-session-saving');"""
    if body.count(start_old)!=1:
        raise RuntimeError("V20.41 start reset anchor mismatch")
    body=body.replace(start_old,start_new,1)

    marker_old="""    failedSaveRemainsRetryable:true
  };"""
    marker_new="""    failedSaveRemainsRetryable:true,
    structuredSessionFeedback:true,
    sessionFeedbackAttachedBeforeCloudCommit:true,
    productionCoachCannotSubmitStudentFeedback:true
  };"""
    if body.count(marker_old)!=1:
        raise RuntimeError("V20.41 V207 marker mismatch")
    body=body.replace(marker_old,marker_new,1)

    return body

html=edit_script(html,"v207ConfirmedSessionCommitRuntime",patch_v207)

css=r"""
/* TEAM FJZ · V20.41 STUDENT SESSION FEEDBACK */
.v241-feedback-form{
  display:grid;
  gap:13px;
}
.v241-feedback-form label{
  display:grid;
  gap:6px;
}
.v241-difficulty-grid{
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:7px;
}
.v241-difficulty-grid label{
  display:flex;
  align-items:center;
  gap:8px;
  min-height:38px;
  padding:8px 9px;
  border:1px solid #2d3038;
  border-radius:10px;
  background:#0d0e12;
  color:#b8bbc3;
  font-size:10px;
  font-weight:760;
  cursor:pointer;
}
.v241-difficulty-grid input{
  width:16px;
  height:16px;
  accent-color:var(--red);
}
.v241-feedback-note{
  padding:9px 10px;
  border:1px solid rgba(103,173,255,.16);
  border-radius:10px;
  background:rgba(103,173,255,.04);
  color:#9299a5;
  font-size:9px;
  line-height:1.45;
}
.v241-feedback-actions{
  display:flex;
  justify-content:flex-end;
  gap:8px;
  flex-wrap:wrap;
}
.v241-feedback-actions .btn{
  min-height:42px;
}
@media(max-width:560px){
  .v241-difficulty-grid{
    grid-template-columns:1fr 1fr;
  }
  .v241-feedback-actions{
    display:grid;
    grid-template-columns:1fr;
  }
  .v241-feedback-actions .btn{
    width:100%;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.41 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-session-feedback" content="20.41">\n</head>',1)

after=metrics(html)
for key in (
    "styles","renders","channels","timeouts","rafs","listeners",
    "mutation_observers","performance_observers"
):
    if after[key]!=before[key]:
        raise RuntimeError("V20.41 topology changed "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-session-feedback" content="20.41"',
    "openSessionFeedbackV241","submitSessionFeedbackV241",
    "sessionFeedbackV241","session.sessionFeedback",
    "difficultyTypes","sessionFeel","comment",
    "structuredSessionFeedback:true",
    "sessionFeedbackAttachedBeforeCloudCommit:true",
    "productionCoachCannotSubmitStudentFeedback:true",
    "cloudConfirmationBeforeSuccess:true",
    "retryUsesSameSessionId:true",
    "pendingMarkerPreservedWhenLocalMissing:true"
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.41 missing feedback marker: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.41 student session feedback")
print("V20.41 BEFORE:",before)
print("V20.41 AFTER:",after)
print("V20.41 structured feedback attached to same confirmed session; topology unchanged")
