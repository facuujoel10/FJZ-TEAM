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
    if not m: raise RuntimeError("V20.87 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body: raise RuntimeError("V20.87 no changes in "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-typography-mobile-nav-feedback" content="20.86"',
    'meta name="fjz-unified-session-history" content="20.44"',
    "openExerciseFeedbackV73",
    "feedbackRowsV73",
    "v244UnifiedSessionHistoryRuntime",
    "v207ConfirmedSessionCommitRuntime",
]:
    if marker not in html:
        raise RuntimeError("V20.87 prerequisite missing "+marker)

# ------------------------------------------------------------------
# 1) Attach a durable snapshot of exercise comments to new sessions.
# ------------------------------------------------------------------
def patch_v207(body):
    anchor="""  function attachMethodHistoryV207(pack,session){
"""
    if body.count(anchor)!=1:
        raise RuntimeError("V20.87 V207 helper anchor mismatch")

    helpers=r"""
  function sessionExerciseFeedbackSnapshotV287(pack,session){
    if(!pack||!session)return;
    let rows=[];
    try{rows=typeof feedbackRowsV73==='function'?(feedbackRowsV73()||[]):[]}catch(_e){rows=[]}
    if(!Array.isArray(rows)||!rows.length)return;

    const sessionTime=Date.parse(session.date||0)||Date.now();
    const maxAge=18*60*60*1000;

    (session.exerciseResults||[]).forEach(r=>{
      const matches=rows.filter(x=>{
        if(String(x?.exercise_uid||'')!==String(r?.exerciseUid||''))return false;
        const dayMatch=!x?.workout_day_id||!pack?.d?.id||String(x.workout_day_id)===String(pack.d.id);
        if(!dayMatch)return false;
        const t=Date.parse(x?.created_at||0);
        return !!t && Math.abs(sessionTime-t)<=maxAge;
      }).sort((a,b)=>(Date.parse(a?.created_at||0)||0)-(Date.parse(b?.created_at||0)||0));

      if(!matches.length)return;
      r.exerciseFeedback=matches.map(x=>({
        id:x.id||null,
        type:x.feedback_type||'comment',
        message:String(x.message||'').trim(),
        createdAt:x.created_at||null,
        status:x.status||'pending'
      })).filter(x=>x.message);
    });
  }

"""
    body=body.replace(anchor,helpers+anchor,1)

    old="""    const session=window.__fjzSaveSessionV205?.(pack);
    if(!session)throw new Error('No se pudo preparar la sesión.');

    attachMethodHistoryV207(pack,session);
"""
    new="""    const session=window.__fjzSaveSessionV205?.(pack);
    if(!session)throw new Error('No se pudo preparar la sesión.');

    sessionExerciseFeedbackSnapshotV287(pack,session);
    attachMethodHistoryV207(pack,session);
"""
    if body.count(old)!=1:
        raise RuntimeError("V20.87 V207 session snapshot anchor mismatch")
    body=body.replace(old,new,1)

    marker="""    failedSaveRemainsRetryable:true,
"""
    if marker not in body:
        raise RuntimeError("V20.87 V207 marker anchor missing")
    body=body.replace(marker,marker+"    exerciseFeedbackSnapshotInSessionV287:true,\n",1)
    return body

html=edit_script(html,"v207ConfirmedSessionCommitRuntime",patch_v207)

# ------------------------------------------------------------------
# 2) Unified session history: show comments under the matching exercise.
#    Existing sessions fall back to exercise_feedback cache/load matching.
# ------------------------------------------------------------------
def patch_v244(body):
    old_func=re.search(r"  function exerciseHtmlV244\(r\)\{.*?\n  \}\n\n  function studentFeedbackHtmlV244",body,re.S)
    if not old_func:
        raise RuntimeError("V20.87 exerciseHtmlV244 block missing")

    new_func=r"""  function feedbackTypeLabelV287(v){
    return v==='discomfort'?'Molestia':'Comentario';
  }

  function exerciseFeedbackForSessionV287(ss,r,rows){
    const snap=Array.isArray(r?.exerciseFeedback)?r.exerciseFeedback.filter(x=>String(x?.message||'').trim()):[];
    if(snap.length)return snap;

    const sessionTime=Date.parse(ss?.date||0)||0;
    const maxDelta=18*60*60*1000;
    return (Array.isArray(rows)?rows:[])
      .filter(x=>{
        if(String(x?.exercise_uid||'')!==String(r?.exerciseUid||''))return false;
        const dayOk=!ss?.dayId||!x?.workout_day_id||String(x.workout_day_id)===String(ss.dayId);
        if(!dayOk)return false;
        const t=Date.parse(x?.created_at||0)||0;
        return !!sessionTime&&!!t&&Math.abs(sessionTime-t)<=maxDelta;
      })
      .sort((a,b)=>(Date.parse(a?.created_at||0)||0)-(Date.parse(b?.created_at||0)||0))
      .map(x=>({
        id:x.id||null,
        type:x.feedback_type||'comment',
        message:String(x.message||'').trim(),
        createdAt:x.created_at||null,
        status:x.status||'pending'
      }))
      .filter(x=>x.message);
  }

  function exerciseCommentHtmlV287(rows){
    if(!rows?.length)return '';
    return '<div class="v287-exercise-comments">'+
      rows.map(x=>
        '<div class="v287-exercise-comment '+(x.type==='discomfort'?'discomfort':'')+'">'+
          '<div class="v287-exercise-comment-head">'+
            '<strong>'+feedbackTypeLabelV287(x.type)+'</strong>'+
            (x.status==='reviewed'?'<span class="badge green">Revisado</span>':'<span class="badge amber">Pendiente</span>')+
          '</div>'+
          '<p>'+esc(x.message)+'</p>'+
        '</div>'
      ).join('')+
    '</div>';
  }

  function exerciseHtmlV244(r,ss,feedbackRows){
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
    const comments=exerciseFeedbackForSessionV287(ss,r,feedbackRows);

    return '<div class="v244-exercise">'+
      '<div class="v244-exercise-head"><strong>'+esc(r?.name||'Ejercicio')+'</strong>'+
      (r?.completed===false?'<span class="badge amber">Parcial</span>':'')+'</div>'+
      '<div class="muted tiny">'+(setText||'Sin series detalladas')+'</div>'+
      methodHtml+
      exerciseCommentHtmlV287(comments)+
      (rec?.title?'<div class="recommend"><strong>'+esc(rec.title)+'</strong>'+
        (rec?.copy?'<div class="muted tiny">'+esc(rec.copy)+'</div>':'')+
      '</div>':'')+
    '</div>';
  }

  function studentFeedbackHtmlV244"""
    body=body[:old_func.start()]+new_func+body[old_func.end()-len("  function studentFeedbackHtmlV244"):]

    old_session="""  window.sessionDetails=function(id){
    const ss=(student()?.sessions||[]).find(x=>x?.id===id);
    if(!ss)return;

    const sum=ss.summary||{};
    const isCoachView=mode==='coach'&&currentProfile?.role==='coach';
    const exercises=Array.isArray(ss.exerciseResults)&&ss.exerciseResults.length
      ?ss.exerciseResults.map(exerciseHtmlV244).join('')
      :'<div class="empty">Esta sesión no contiene detalle por ejercicio.</div>';

    showModal(
"""
    new_session="""  window.sessionDetails=async function(id){
    const ss=(student()?.sessions||[]).find(x=>x?.id===id);
    if(!ss)return;

    let exerciseFeedbackRows=[];
    try{
      if(typeof loadExerciseFeedbackV73==='function'){
        exerciseFeedbackRows=await loadExerciseFeedbackV73(false)||[];
      }else if(typeof feedbackRowsV73==='function'){
        exerciseFeedbackRows=feedbackRowsV73()||[];
      }
    }catch(_e){
      try{exerciseFeedbackRows=typeof feedbackRowsV73==='function'?(feedbackRowsV73()||[]):[]}catch(__e){}
    }

    const sum=ss.summary||{};
    const isCoachView=mode==='coach'&&currentProfile?.role==='coach';
    const exercises=Array.isArray(ss.exerciseResults)&&ss.exerciseResults.length
      ?ss.exerciseResults.map(r=>exerciseHtmlV244(r,ss,exerciseFeedbackRows)).join('')
      :'<div class="empty">Esta sesión no contiene detalle por ejercicio.</div>';

    showModal(
"""
    if body.count(old_session)!=1:
        raise RuntimeError("V20.87 sessionDetails anchor mismatch")
    body=body.replace(old_session,new_session,1)

    marker="""    coachCanEditResponseFromSession:true
"""
    if marker not in body:
        raise RuntimeError("V20.87 V244 marker anchor missing")
    body=body.replace(marker,"    coachCanEditResponseFromSession:true,\n    exerciseCommentsVisiblePerSessionV287:true,\n    historicalExerciseCommentFallbackV287:true\n",1)
    return body

html=edit_script(html,"v244UnifiedSessionHistoryRuntime",patch_v244)

css=r"""
/* TEAM FJZ · V20.87 EXERCISE COMMENTS IN SESSION REVIEW */
.v287-exercise-comments{
  display:grid;
  gap:6px;
  margin-top:8px;
}
.v287-exercise-comment{
  padding:8px 9px;
  border:1px solid rgba(103,173,255,.20);
  border-left:3px solid #67adff;
  border-radius:0 9px 9px 0;
  background:rgba(103,173,255,.045);
}
.v287-exercise-comment.discomfort{
  border-color:rgba(255,70,87,.23);
  border-left-color:#ff4657;
  background:rgba(255,70,87,.045);
}
.v287-exercise-comment-head{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:8px;
  margin-bottom:5px;
}
.v287-exercise-comment-head strong{
  color:#dce7f7;
  font-size:9px;
  font-weight:900;
  letter-spacing:.04em;
  text-transform:uppercase;
}
.v287-exercise-comment.discomfort .v287-exercise-comment-head strong{
  color:#ffc3c9;
}
.v287-exercise-comment p{
  margin:0;
  color:#c1c6cf;
  font-size:10px;
  line-height:1.45;
  overflow-wrap:anywhere;
}
@media(max-width:560px){
  .v287-exercise-comment{
    padding:8px;
  }
  .v287-exercise-comment-head{
    align-items:flex-start;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.87 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-session-exercise-comments" content="20.87">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.87 topology changed "+key+": "+repr({"before":before,"after":after}))

required=[
    'meta name="fjz-session-exercise-comments" content="20.87"',
    "exerciseFeedbackSnapshotInSessionV287:true",
    "exerciseCommentsVisiblePerSessionV287:true",
    "historicalExerciseCommentFallbackV287:true",
    "sessionExerciseFeedbackSnapshotV287",
    "exerciseFeedbackForSessionV287",
    "exerciseCommentHtmlV287",
    "window.sessionDetails=async function",
]
for marker in required:
    if marker not in html:
        raise RuntimeError("V20.87 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.87 exercise comments in session review")
print("V20.87 BEFORE:",before)
print("V20.87 AFTER:",after)
