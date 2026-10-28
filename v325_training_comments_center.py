import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":doc.lower().count("<style"),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":doc.count(".channel("),
        "timeouts":doc.count("setTimeout("),
        "intervals":doc.count("setInterval("),
        "listeners":doc.count("addEventListener("),
        "mutation_observers":doc.count("new MutationObserver"),
        "performance_observers":doc.count("new PerformanceObserver"),
    }

def edit_script(doc,sid,fn):
    mid=-1
    for marker in ('id="'+sid+'"',"id='"+sid+"'"):
        mid=doc.find(marker)
        if mid>=0: break
    if mid<0:
        raise RuntimeError("V21.25 missing script "+sid)
    a=doc.find(">",mid); b=doc.find("</script>",a)
    if a<0 or b<0:
        raise RuntimeError("V21.25 malformed script "+sid)
    body=doc[a+1:b]
    body=fn(body)
    return doc[:a+1]+body+doc[b:]

before=metrics(html)

for marker in [
    'meta name="fjz-review-dashboard-hydration" content="21.24"',
    'id="v302ReviewResolutionAuthorityRuntime"',
    'id="v175ProfileAgendaCoachCenterRuntime"',
    "renderSessionFeedbackCoachV242",
    "session.sessionFeedback",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.25 prerequisite missing "+marker)

def patch_v302(body):
    anchor="""  function renderCenter(){"""
    if body.count(anchor)!=1:
        raise RuntimeError("V21.25 V302 renderCenter anchor mismatch")

    helpers=r"""
  function difficultyLabelV325(v){
    const map={
      technique:'Técnica',load:'Carga / peso',fatigue:'Fatiga / energía',
      discomfort:'Molestia',time:'Tiempo',equipment:'Equipo / gimnasio',
      motivation:'Motivación',other:'Otra'
    };
    return map[v]||v||'';
  }

  function commentRowsForStudentV325(s){
    const out=[];
    (Array.isArray(s?.sessions)?s.sessions:[]).forEach(ss=>{
      const fb=ss?.sessionFeedback||null;
      const general=String(fb?.comment||'').trim();
      if(general){
        out.push({
          studentId:String(s?.id||''),studentName:s?.name||'Alumno',
          sessionId:String(ss?.id||''),sessionDate:ss?.date||null,dayName:ss?.dayName||'Entrenamiento',
          kind:'session',exerciseName:'',message:general,
          status:fb?.status||'pending',difficultyTypes:Array.isArray(fb?.difficultyTypes)?fb.difficultyTypes:[],
          sessionFeel:fb?.sessionFeelLabel||'',at:Date.parse(ss?.date||0)||0
        });
      }

      (Array.isArray(ss?.exerciseResults)?ss.exerciseResults:[]).forEach(er=>{
        (Array.isArray(er?.exerciseFeedback)?er.exerciseFeedback:[]).forEach(x=>{
          const message=String(x?.message||'').trim();
          if(!message)return;
          out.push({
            studentId:String(s?.id||''),studentName:s?.name||'Alumno',
            sessionId:String(ss?.id||''),sessionDate:ss?.date||null,dayName:ss?.dayName||'Entrenamiento',
            kind:'exercise',exerciseName:er?.exerciseName||er?.name||'Ejercicio',message,
            status:x?.status||'pending',difficultyTypes:[],
            sessionFeel:fb?.sessionFeelLabel||'',at:Date.parse(x?.createdAt||ss?.date||0)||0
          });
        });
      });
    });
    return out.sort((a,b)=>{
      const ap=a.status==='pending'?1:0,bp=b.status==='pending'?1:0;
      return bp-ap||b.at-a.at;
    });
  }

  function allTrainingCommentsV325(){
    const out=[];
    students().forEach(s=>out.push(...commentRowsForStudentV325(s)));
    return out.sort((a,b)=>{
      const ap=a.status==='pending'?1:0,bp=b.status==='pending'?1:0;
      return bp-ap||b.at-a.at;
    });
  }

  function ensureTrainingCommentsHostV325(){
    if(!(currentProfile?.role==='coach'&&coachTab==='dashboard'))return null;
    let host=el('v325TrainingCommentsCenter');
    if(host)return host;
    const review=el('v252PriorityCenter');
    if(!review)return null;
    host=document.createElement('section');
    host.id='v325TrainingCommentsCenter';
    host.className='card v325-training-comments-center';
    review.insertAdjacentElement('afterend',host);
    return host;
  }

  function trainingCommentCardV325(x){
    const pending=x.status==='pending';
    const tags=(x.difficultyTypes||[]).map(difficultyLabelV325).filter(Boolean);
    return '<article class="v325-comment-card '+(pending?'pending':'')+'" data-v325-session="'+safe(x.sessionId)+'">'+
      '<div class="v325-comment-head"><div><span class="v325-comment-student">'+safe(x.studentName)+'</span>'+
      '<strong>'+safe(x.kind==='exercise'?x.exerciseName:x.dayName)+'</strong>'+
      '<small>'+safe(fmtDate(x.sessionDate))+(x.kind==='exercise'?' · '+safe(x.dayName):'')+'</small></div>'+
      '<span class="badge '+(pending?'amber':'green')+'">'+(pending?'Pendiente':'Revisado')+'</span></div>'+
      (tags.length?'<div class="v325-comment-tags">'+tags.map(t=>'<span>'+safe(t)+'</span>').join('')+'</div>':'')+
      '<div class="v325-comment-message"><span>'+(x.kind==='exercise'?'COMENTARIO DEL EJERCICIO':'COMENTARIO DEL ENTRENAMIENTO')+'</span><p>'+safe(x.message)+'</p></div>'+
      '<div class="v325-comment-actions"><button class="btn small primary" onclick="window.__fjzOpenTrainingCommentV325?.(\''+safe(x.studentId)+'\',\''+safe(x.sessionId)+'\')">Abrir alumno</button></div>'+
    '</article>';
  }

  function renderTrainingCommentsV325(){
    const host=ensureTrainingCommentsHostV325();if(!host)return;
    const rows=allTrainingCommentsV325();
    const pending=rows.filter(x=>x.status==='pending').length;
    const visible=rows.slice(0,8);
    host.innerHTML='<div class="v325-comments-head"><div><div class="v225-section-kicker">COMENTARIOS DE ENTRENAMIENTO</div>'+
      '<h3>Lo que te dejaron tus alumnos</h3><p>Comentarios escritos al cerrar una sesión o sobre un ejercicio. Los pendientes aparecen primero.</p></div>'+
      '<span class="badge '+(pending?'amber':'green')+'">'+pending+' pendiente'+(pending===1?'':'s')+'</span></div>'+
      (visible.length?'<div class="v325-comments-grid">'+visible.map(trainingCommentCardV325).join('')+'</div>':
      '<div class="v301-empty"><strong>Sin comentarios recientes</strong><span>Cuando un alumno escriba algo en su entrenamiento va a aparecer acá.</span></div>');
  }

  window.__fjzOpenTrainingCommentV325=function(studentId,sessionId){
    const s=byId(studentId);if(!s)return false;
    window.__fjzFocusTrainingCommentV325=String(sessionId||'');
    state.selectedStudentId=s.id;saveState();
    coachTab='student';coachStudentTab='summary';render();
    Promise.resolve().then(()=>{
      try{
        const target=[...document.querySelectorAll('[data-v325-session]')]
          .find(n=>String(n.dataset.v325Session||'')===String(sessionId||''));
        target?.scrollIntoView?.({block:'center',behavior:'auto'});
      }catch(_e){}
    });
    return true;
  };

"""
    body=body.replace(anchor,helpers+anchor,1)

    end_anchor="""      (rows.length?'<div class="v301-center-grid">'+rows.map(card).join('')+'</div>':'<div class="v301-empty"><strong>Centro limpio</strong><span>No hay revisiones pendientes.</span></div>');
  }"""
    repl="""      (rows.length?'<div class="v301-center-grid">'+rows.map(card).join('')+'</div>':'<div class="v301-empty"><strong>Centro limpio</strong><span>No hay revisiones pendientes.</span></div>');
    renderTrainingCommentsV325();
  }"""
    if body.count(end_anchor)!=1:
        raise RuntimeError("V21.25 V302 center render tail mismatch: "+str(body.count(end_anchor)))
    body=body.replace(end_anchor,repl,1)

    flag_anchor="""    cloudAuthorityRepaintsReviewCenterV322:true,"""
    if flag_anchor not in body:
        raise RuntimeError("V21.25 V302 flag anchor missing")
    body=body.replace(flag_anchor,flag_anchor+"""
    trainingCommentsCenterV325:true,
    trainingCommentsPendingFirstV325:true,
    trainingCommentsUsesSessionSnapshotV325:true,""",1)
    return body

html=edit_script(html,"v302ReviewResolutionAuthorityRuntime",patch_v302)

def patch_v175(body):
    anchor="""  function renderSessionFeedbackCoachV242(){"""
    if body.count(anchor)!=1:
        raise RuntimeError("V21.25 V175 feedback renderer anchor mismatch: "+str(body.count(anchor)))

    helpers=r"""
  function trainingCommentsForStudentV325(s=student()){
    const out=[];
    (Array.isArray(s?.sessions)?s.sessions:[]).forEach(ss=>{
      const fb=ss?.sessionFeedback||null;
      const general=String(fb?.comment||'').trim();
      if(general){
        out.push({
          session:ss,kind:'session',exerciseName:'',message:general,status:fb?.status||'pending',
          difficultyTypes:Array.isArray(fb?.difficultyTypes)?fb.difficultyTypes:[],
          at:Date.parse(ss?.date||0)||0
        });
      }
      (Array.isArray(ss?.exerciseResults)?ss.exerciseResults:[]).forEach(er=>{
        (Array.isArray(er?.exerciseFeedback)?er.exerciseFeedback:[]).forEach(x=>{
          const message=String(x?.message||'').trim();
          if(!message)return;
          out.push({
            session:ss,kind:'exercise',exerciseName:er?.exerciseName||er?.name||'Ejercicio',
            message,status:x?.status||'pending',difficultyTypes:[],
            at:Date.parse(x?.createdAt||ss?.date||0)||0
          });
        });
      });
    });
    return out.sort((a,b)=>{
      const ap=a.status==='pending'?1:0,bp=b.status==='pending'?1:0;
      return bp-ap||b.at-a.at;
    });
  }

  function trainingDifficultyLabelV325(v){
    const map={
      technique:'Técnica',load:'Carga / peso',fatigue:'Fatiga / energía',
      discomfort:'Molestia',time:'Tiempo',equipment:'Equipo / gimnasio',
      motivation:'Motivación',other:'Otra'
    };
    return map[v]||v||'';
  }

  function trainingCommentStudentCardV325(x){
    const ss=x.session||{},pending=x.status==='pending';
    const tags=(x.difficultyTypes||[]).map(trainingDifficultyLabelV325).filter(Boolean);
    const canReview=x.kind==='session'&&ss?.sessionFeedback&&typeof window.openSessionFeedbackCoachV242==='function';
    return '<article class="v325-student-comment '+(pending?'pending':'')+'" data-v325-session="'+esc(ss.id||'')+'">'+
      '<div class="v325-comment-head"><div><strong>'+esc(x.kind==='exercise'?x.exerciseName:(ss.dayName||'Entrenamiento'))+'</strong>'+
      '<small>'+esc(fmtDate(ss.date))+(x.kind==='exercise'?' · '+esc(ss.dayName||'Entrenamiento'):'')+'</small></div>'+
      '<span class="badge '+(pending?'amber':'green')+'">'+(pending?'Pendiente':'Revisado')+'</span></div>'+
      (tags.length?'<div class="v325-comment-tags">'+tags.map(t=>'<span>'+esc(t)+'</span>').join('')+'</div>':'')+
      '<div class="v325-comment-message"><span>'+(x.kind==='exercise'?'COMENTARIO DEL EJERCICIO':'COMENTARIO DEL ENTRENAMIENTO')+'</span><p>'+esc(x.message)+'</p></div>'+
      (canReview&&pending?'<div class="v325-comment-actions"><button class="btn small primary" onclick="openSessionFeedbackCoachV242(\''+esc(ss.id)+'\')">Revisar y responder</button></div>':'')+
    '</article>';
  }

  function renderStudentTrainingCommentsV325(){
    const host=el('v325StudentTrainingComments');if(!host)return;
    const rows=trainingCommentsForStudentV325();
    const pending=rows.filter(x=>x.status==='pending').length;
    host.innerHTML='<div class="v175-360-section-head"><div><h4>Comentarios de entrenamiento</h4>'+
      '<p>Texto que el alumno dejó al terminar una sesión o sobre un ejercicio. Los pendientes aparecen primero.</p></div>'+
      '<span class="badge '+(pending?'amber':'green')+'">'+pending+' pendiente'+(pending===1?'':'s')+'</span></div>'+
      (rows.length?'<div class="v325-student-comments-list">'+rows.slice(0,10).map(trainingCommentStudentCardV325).join('')+'</div>':
      '<div class="empty">Este alumno todavía no dejó comentarios en sus entrenamientos.</div>');

    const focus=String(window.__fjzFocusTrainingCommentV325||'');
    if(focus){
      try{
        const target=[...host.querySelectorAll('[data-v325-session]')]
          .find(n=>String(n.dataset.v325Session||'')===focus);
        target?.classList?.add('v325-focus');
      }catch(_e){}
      window.__fjzFocusTrainingCommentV325='';
    }
  }

"""
    body=body.replace(anchor,helpers+anchor,1)

    section_anchor="""      '<div class="v175-360-section v242-session-feedback-section" id="v242SessionFeedbackCoach"><div class="empty">Revisando feedback de sesiones…</div></div>'+"""
    section_repl=section_anchor+"""
      '<div class="v175-360-section v325-training-comments-section" id="v325StudentTrainingComments"><div class="empty">Revisando comentarios de entrenamiento…</div></div>'+"""
    if body.count(section_anchor)!=1:
        raise RuntimeError("V21.25 V175 summary section anchor mismatch: "+str(body.count(section_anchor)))
    body=body.replace(section_anchor,section_repl,1)

    hydrate_anchor="""    renderSessionFeedbackCoachV242();"""
    hydrate_repl="""    renderSessionFeedbackCoachV242();
    renderStudentTrainingCommentsV325();"""
    if body.count(hydrate_anchor)<1:
        raise RuntimeError("V21.25 V175 hydration anchor missing")
    body=body.replace(hydrate_anchor,hydrate_repl,1)

    flag_anchor="""    sessionFeedbackInternalNoteCoachOnly:true"""
    if flag_anchor not in body:
        raise RuntimeError("V21.25 V175 flags anchor missing")
    body=body.replace(flag_anchor,flag_anchor+""",
    dedicatedTrainingCommentsV325:true,
    sessionAndExerciseCommentsVisibleV325:true,
    pendingCommentsFirstV325:true""",1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

css=r"""
/* TEAM FJZ · V21.25 TRAINING COMMENTS CENTER */
.v325-training-comments-center{
  margin:0 0 14px;
  border-color:#30343c;
  background:
    linear-gradient(145deg,rgba(103,173,255,.045),transparent 46%),
    var(--card);
}
.v325-comments-head{
  display:flex;
  justify-content:space-between;
  gap:14px;
  align-items:flex-start;
  margin-bottom:12px;
}
.v325-comments-head h3{
  margin:4px 0 0;
  color:#f5f6f8;
  font-size:16px;
  font-weight:920;
  letter-spacing:-.02em;
}
.v325-comments-head p{
  margin:5px 0 0;
  color:#959aa4;
  font-size:10px;
  line-height:1.5;
}
.v325-comments-grid,
.v325-student-comments-list{
  display:grid;
  gap:9px;
}
.v325-comments-grid{
  grid-template-columns:repeat(2,minmax(0,1fr));
}
.v325-comment-card,
.v325-student-comment{
  min-width:0;
  padding:12px;
  border:1px solid #2c3038;
  border-left:3px solid #59606c;
  border-radius:0 12px 12px 0;
  background:#0d0e12;
}
.v325-comment-card.pending,
.v325-student-comment.pending{
  border-left-color:#f2bd55;
  background:linear-gradient(90deg,rgba(242,189,85,.035),transparent 36%),#0d0e12;
}
.v325-student-comment.v325-focus{
  outline:2px solid rgba(242,189,85,.28);
  outline-offset:2px;
}
.v325-comment-head{
  display:flex;
  justify-content:space-between;
  gap:10px;
  align-items:flex-start;
}
.v325-comment-head>div{min-width:0}
.v325-comment-student{
  display:block;
  margin-bottom:3px;
  color:#ff7b88;
  font-size:9px;
  font-weight:900;
  letter-spacing:.08em;
  text-transform:uppercase;
}
.v325-comment-head strong{
  display:block;
  color:#f1f2f4;
  font-size:11px;
  line-height:1.35;
  overflow-wrap:anywhere;
}
.v325-comment-head small{
  display:block;
  margin-top:3px;
  color:#858b96;
  font-size:9px;
}
.v325-comment-tags{
  display:flex;
  gap:5px;
  flex-wrap:wrap;
  margin-top:8px;
}
.v325-comment-tags span{
  padding:4px 7px;
  border:1px solid rgba(242,189,85,.20);
  border-radius:999px;
  background:rgba(242,189,85,.055);
  color:#e8c578;
  font-size:8px;
  font-weight:800;
}
.v325-comment-message{
  margin-top:10px;
  padding:10px 11px;
  border:1px solid #272b32;
  border-radius:10px;
  background:#101217;
}
.v325-comment-message>span{
  display:block;
  color:#737985;
  font-size:8px;
  font-weight:900;
  letter-spacing:.08em;
}
.v325-comment-message p{
  margin:5px 0 0;
  color:#d5d8de;
  font-size:11px;
  line-height:1.5;
  overflow-wrap:anywhere;
}
.v325-comment-actions{
  display:flex;
  justify-content:flex-end;
  margin-top:9px;
}
.v325-training-comments-section{
  border-color:rgba(103,173,255,.18);
}
@media(max-width:820px){
  .v325-comments-grid{grid-template-columns:1fr}
}
@media(max-width:560px){
  .v325-comments-head{display:grid}
  .v325-comment-head{display:grid}
  .v325-comment-head>.badge{justify-self:start}
  .v325-comment-actions .btn{width:100%}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V21.25 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-training-comments-center" content="21.25">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V21.25 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-training-comments-center" content="21.25"',
    "trainingCommentsCenterV325:true",
    "trainingCommentsPendingFirstV325:true",
    "dedicatedTrainingCommentsV325:true",
    "sessionAndExerciseCommentsVisibleV325:true",
    "v325TrainingCommentsCenter",
    "v325StudentTrainingComments",
    "Lo que te dejaron tus alumnos",
    "Comentarios de entrenamiento",
    "__fjzOpenTrainingCommentV325",
    "renderStudentTrainingCommentsV325",
    "Revisar y responder",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.25 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.25 training comments center")
print("V21.25 BEFORE:",before)
print("V21.25 AFTER:",after)
