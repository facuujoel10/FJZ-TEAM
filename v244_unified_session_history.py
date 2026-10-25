import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.44 UNIFIED SESSION HISTORY
# =========================================================
# Final authority for history/detail: workout + student session feedback +
# coach response in one place. No backend/realtime/listener/timer growth.

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

before=metrics(html)

for marker in [
    'meta name="fjz-student-journey" content="20.43"',
    "openSessionFeedbackCoachV242",
    "sessionDifficultyLabelV242",
    "sessionDecisionLabelV242",
    "studentSeesCoachNextStep:true"
]:
    if marker not in html:
        raise RuntimeError("V20.44 missing prerequisite: "+marker)

# Add one final script authority. We deliberately do not wrap render().
js=r"""
<script id="v244UnifiedSessionHistoryRuntime">
(function(){
  const VERSION='20.44';

  function summaryNumberV244(v){
    const n=Number(v);
    return Number.isFinite(n)?n:0;
  }

  function feedbackBadgeV244(ss){
    const fb=ss?.sessionFeedback;
    if(!fb)return '';
    if(fb.status==='pending')return '<span class="badge red">Feedback pendiente</span>';
    if(fb.status==='reviewed')return '<span class="badge green">Feedback revisado</span>';
    if(fb.status==='clear')return '<span class="badge blue">Sin dificultad</span>';
    return '';
  }

  function feedbackHistoryMetaV244(ss){
    const fb=ss?.sessionFeedback;
    if(!fb)return '';
    const difficulty=(fb.difficultyTypes||[]).length;
    if(fb.status==='pending'){
      return ' · feedback por revisar'+(difficulty?' · '+difficulty+' dificultad'+(difficulty===1?'':'es'):'');
    }
    if(fb.status==='reviewed')return ' · devolución del coach';
    return ' · sin dificultades';
  }

  function loadTextV244(r,set){
    const kg=Number(set?.[0]);
    if(r?.loadMode==='bodyweight'&&kg===0)return 'peso corporal';
    if(Number.isFinite(kg))return kg+' kg';
    return '—';
  }

  function exerciseHtmlV244(r){
    const sets=Array.isArray(r?.sets)?r.sets:[];
    const setText=sets.map((x,i)=>
      'S'+(Number(r?.setIndexes?.[i]??i)+1)+': '+
      loadTextV244(r,x)+' × '+esc(String(x?.[1]??'—'))+
      ' · RIR '+esc(String(x?.[2]??'—'))
    ).join(' · ');

    const rec=r?.recommendation||{};
    const method=r?.methodLog;
    const methodHtml=method
      ?'<div class="v244-method"><strong>Método:</strong> '+esc(method.type||'intensificación')+
        (method.note?' · '+esc(method.note):'')+'</div>'
      :'';

    return '<div class="v244-exercise">'+
      '<div class="v244-exercise-head"><strong>'+esc(r?.name||'Ejercicio')+'</strong>'+
      (r?.completed===false?'<span class="badge amber">Parcial</span>':'')+'</div>'+
      '<div class="muted tiny">'+(setText||'Sin series detalladas')+'</div>'+
      methodHtml+
      (rec?.title?'<div class="recommend"><strong>'+esc(rec.title)+'</strong>'+
        (rec?.copy?'<div class="muted tiny">'+esc(rec.copy)+'</div>':'')+
      '</div>':'')+
    '</div>';
  }

  function studentFeedbackHtmlV244(ss){
    const fb=ss?.sessionFeedback;
    if(!fb)return '';

    const tags=(fb.difficultyTypes||[]).map(x=>
      '<span>'+esc(typeof sessionDifficultyLabelV242==='function'?sessionDifficultyLabelV242(x):x)+'</span>'
    ).join('');

    return '<section class="v244-timeline-block student">'+
      '<div class="v244-block-head"><div><span class="v244-step">ALUMNO</span><h4>Feedback de la sesión</h4></div>'+
      feedbackBadgeV244(ss)+'</div>'+
      '<div class="v244-feel"><span>Sesión</span><strong>'+esc(fb.sessionFeelLabel||'Normal')+'</strong></div>'+
      (tags?'<div class="v242-feedback-tags">'+tags+'</div>':'')+
      '<p>'+(fb.comment?esc(fb.comment):'Sin comentario general.')+'</p>'+
    '</section>';
  }

  function coachFeedbackHtmlV244(ss,isCoachView){
    const fb=ss?.sessionFeedback;
    if(!fb)return '';
    const r=fb.coachReview||null;

    if(!r&&fb.status==='pending'){
      return '<section class="v244-timeline-block coach pending">'+
        '<div class="v244-block-head"><div><span class="v244-step">COACH</span><h4>Devolución pendiente</h4></div></div>'+
        '<p>'+(
          isCoachView
            ?'Este feedback todavía necesita tu revisión.'
            :'Tu coach todavía no cerró la revisión de este feedback.'
        )+'</p>'+
        (isCoachView
          ?'<button class="btn primary" onclick="openSessionFeedbackCoachV242(\''+esc(ss.id)+'\')">Revisar ahora</button>'
          :'')+
      '</section>';
    }

    if(!r)return '';

    const label=typeof sessionDecisionLabelV242==='function'
      ?sessionDecisionLabelV242(r.decision)
      :(r.decision||'Seguimiento');

    return '<section class="v244-timeline-block coach">'+
      '<div class="v244-block-head"><div><span class="v244-step">COACH</span><h4>Cómo seguimos</h4></div>'+
      '<span class="badge green">Revisado</span></div>'+
      '<div class="v244-decision"><strong>'+esc(label)+'</strong>'+
      '<p>'+esc(r.nextStep||'Feedback revisado por el coach.')+'</p></div>'+
      (isCoachView&&r.internalNote
        ?'<div class="v244-internal"><strong>Nota interna</strong><p>'+esc(r.internalNote)+'</p></div>'
        :'')+
      (isCoachView
        ?'<button class="btn small" onclick="openSessionFeedbackCoachV242(\''+esc(ss.id)+'\')">Editar devolución</button>'
        :'')+
    '</section>';
  }

  window.renderHistory=function(isCoach,targetId){
    const s=student();
    const b=el(targetId||(isCoach?'coachStudentBody':'studentSubBody'));
    if(!b)return;
    const ss=(s?.sessions||[]).slice().sort(
      (a,b)=>(Date.parse(b?.date||0)||0)-(Date.parse(a?.date||0)||0)
    );

    b.innerHTML=ss.length
      ?'<div class="card v244-history-card">'+
        '<div class="section-title"><div><h3>Historial de entrenamientos</h3>'+
        '<div class="muted tiny">Entrenamiento, feedback y devolución conectados por sesión.</div></div>'+
        '<span class="badge blue">'+ss.length+' sesiones</span></div>'+
        '<div class="history-list v244-history-list">'+
          ss.map(x=>{
            const sum=x.summary||{};
            return '<div class="history-item v244-history-item">'+
              '<div class="v244-history-copy"><strong>'+esc(x.dayName||'Entrenamiento')+'</strong>'+
              '<div class="muted tiny">'+esc(fmtDate(x.date))+' · '+summaryNumberV244(sum.totalSets)+' series'+
              feedbackHistoryMetaV244(x)+'</div>'+
              '<div class="v244-history-badges">'+feedbackBadgeV244(x)+
              (summaryNumberV244(sum.review)?'<span class="badge amber">'+summaryNumberV244(sum.review)+' revisar</span>':'')+
              '</div></div>'+
              '<button class="btn small" onclick="sessionDetails(\''+esc(x.id)+'\')">Ver sesión</button>'+
            '</div>';
          }).join('')+
        '</div></div>'
      :'<div class="empty">Todavía no hay sesiones registradas.</div>';
  };
  try{renderHistory=window.renderHistory}catch(_e){}

  window.sessionDetails=function(id){
    const ss=(student()?.sessions||[]).find(x=>x?.id===id);
    if(!ss)return;

    const sum=ss.summary||{};
    const isCoachView=mode==='coach'&&currentProfile?.role==='coach';
    const exercises=Array.isArray(ss.exerciseResults)&&ss.exerciseResults.length
      ?ss.exerciseResults.map(exerciseHtmlV244).join('')
      :'<div class="empty">Esta sesión no contiene detalle por ejercicio.</div>';

    showModal(
      '<div class="modal-head"><div><h3>'+esc(ss.dayName||'Entrenamiento')+'</h3>'+
      '<div class="muted tiny">'+esc(new Date(ss.date).toLocaleString('es-AR'))+'</div></div>'+
      '<button class="btn small" type="button" aria-label="Cerrar" title="Cerrar" onclick="closeModal()">✕</button></div>'+
      '<div class="v244-summary-grid">'+
        '<div><strong>'+summaryNumberV244(sum.totalSets)+'</strong><span>Series</span></div>'+
        '<div><strong>'+summaryNumberV244(sum.completedExercises||sum.registeredExercises)+'</strong><span>Ejercicios</span></div>'+
        '<div><strong>'+summaryNumberV244(sum.up)+'</strong><span>Progresaron</span></div>'+
        '<div><strong>'+summaryNumberV244(sum.review)+'</strong><span>Revisar</span></div>'+
      '</div>'+
      '<div class="v244-timeline">'+
        '<section class="v244-timeline-block workout">'+
          '<div class="v244-block-head"><div><span class="v244-step">ENTRENAMIENTO</span><h4>Registro de la sesión</h4></div></div>'+
          (ss.skippedExerciseNames?.length
            ?'<div class="v244-skipped"><strong>Omitidos:</strong> '+esc(ss.skippedExerciseNames.join(' · '))+'</div>'
            :'')+
          '<div class="v244-exercise-list">'+exercises+'</div>'+
        '</section>'+
        studentFeedbackHtmlV244(ss)+
        coachFeedbackHtmlV244(ss,isCoachView)+
      '</div>'
    );
  };
  try{sessionDetails=window.sessionDetails}catch(_e){}

  window.__fjzV244={
    version:VERSION,
    unifiedSessionTimeline:true,
    feedbackVisibleInHistory:true,
    coachResponseVisibleInHistory:true,
    coachInternalNoteHiddenFromStudent:true,
    coachCanEditResponseFromSession:true
  };
})();
</script>
"""

html=html.replace("</body>",js+"\n</body>",1)

css=r"""
/* TEAM FJZ · V20.44 UNIFIED SESSION HISTORY */
.v244-history-card{
  border-color:#30343b;
}
.v244-history-list{
  display:grid;
  gap:7px;
}
.v244-history-item{
  gap:12px;
}
.v244-history-copy{
  min-width:0;
}
.v244-history-badges{
  display:flex;
  flex-wrap:wrap;
  gap:5px;
  margin-top:6px;
}
.v244-summary-grid{
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:7px;
  margin-bottom:12px;
}
.v244-summary-grid>div{
  padding:10px;
  border:1px solid #2c3038;
  border-radius:11px;
  background:#0d0e12;
}
.v244-summary-grid strong{
  display:block;
  color:#f6f7f9;
  font-size:20px;
  line-height:1;
  font-weight:920;
}
.v244-summary-grid span{
  display:block;
  margin-top:6px;
  color:#8e929d;
  font-size:8px;
  font-weight:780;
  text-transform:uppercase;
  letter-spacing:.05em;
}
.v244-timeline{
  display:grid;
  gap:9px;
}
.v244-timeline-block{
  padding:12px;
  border:1px solid #2c3038;
  border-left-width:3px;
  border-radius:0 12px 12px 0;
  background:#0d0e12;
}
.v244-timeline-block.workout{border-left-color:#7f8591}
.v244-timeline-block.student{border-left-color:#f2bd55}
.v244-timeline-block.coach{border-left-color:#3bd58a}
.v244-timeline-block.coach.pending{border-left-color:#ff4657}
.v244-block-head{
  display:flex;
  justify-content:space-between;
  gap:10px;
  align-items:flex-start;
  margin-bottom:9px;
}
.v244-block-head h4{
  margin:3px 0 0;
  color:#f4f5f7;
  font-size:12px;
}
.v244-step{
  display:block;
  color:#828793;
  font-size:7px;
  font-weight:900;
  letter-spacing:.12em;
}
.v244-timeline-block>p{
  margin:8px 0 0;
  color:#b6bac2;
  font-size:10px;
  line-height:1.5;
}
.v244-feel{
  display:flex;
  gap:7px;
  align-items:center;
}
.v244-feel span{
  color:#8d929c;
  font-size:9px;
}
.v244-feel strong{
  color:#f1f2f4;
  font-size:10px;
}
.v244-exercise-list{
  display:grid;
  gap:7px;
}
.v244-exercise{
  padding:9px 10px;
  border:1px solid #292c33;
  border-radius:10px;
  background:#101116;
}
.v244-exercise-head{
  display:flex;
  justify-content:space-between;
  gap:8px;
  margin-bottom:5px;
}
.v244-exercise-head strong{
  color:#f0f1f3;
  font-size:10px;
}
.v244-exercise .recommend{
  margin-top:8px;
}
.v244-method{
  margin-top:5px;
  color:#9da1aa;
  font-size:8px;
  line-height:1.4;
}
.v244-skipped{
  margin-bottom:8px;
  padding:7px 8px;
  border:1px solid rgba(242,189,85,.16);
  border-radius:8px;
  color:#c9b37f;
  font-size:8px;
  line-height:1.4;
}
.v244-decision{
  padding:9px 10px;
  border:1px solid rgba(59,213,138,.16);
  border-radius:10px;
  background:rgba(59,213,138,.04);
}
.v244-decision strong{
  color:#a5e7c2;
  font-size:11px;
}
.v244-decision p{
  margin:5px 0 0;
  color:#c3c7ce;
  font-size:9px;
  line-height:1.48;
}
.v244-internal{
  margin:8px 0;
  padding:8px 9px;
  border:1px dashed #3a3e47;
  border-radius:9px;
  color:#989da7;
}
.v244-internal strong{
  color:#c7cad0;
  font-size:8px;
  text-transform:uppercase;
  letter-spacing:.06em;
}
.v244-internal p{
  margin:4px 0 0;
  font-size:9px;
  line-height:1.45;
}
@media(max-width:620px){
  .v244-summary-grid{
    grid-template-columns:1fr 1fr;
  }
  .v244-history-item{
    align-items:flex-start;
  }
  .v244-history-item>.btn{
    flex:0 0 auto;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.44 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-unified-session-history" content="20.44">\n</head>',1)

after=metrics(html)
for key in (
    "styles","renders","channels","timeouts","rafs","listeners",
    "mutation_observers","performance_observers"
):
    if after[key]!=before[key]:
        raise RuntimeError("V20.44 topology changed "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-unified-session-history" content="20.44"',
    "v244UnifiedSessionHistoryRuntime",
    "unifiedSessionTimeline:true",
    "feedbackVisibleInHistory:true",
    "coachResponseVisibleInHistory:true",
    "coachInternalNoteHiddenFromStudent:true",
    "coachCanEditResponseFromSession:true",
    "Feedback pendiente",
    "Editar devolución",
    "openSessionFeedbackCoachV242"
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.44 missing history marker: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.44 unified session history")
print("V20.44 BEFORE:",before)
print("V20.44 AFTER:",after)
print("V20.44 workout + student feedback + coach response unified per session")
