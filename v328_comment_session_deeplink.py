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
        raise RuntimeError("V21.28 missing script "+sid)
    a=doc.find(">",mid); b=doc.find("</script>",a)
    if a<0 or b<0:
        raise RuntimeError("V21.28 malformed script "+sid)
    body=doc[a+1:b]
    body=fn(body)
    return doc[:a+1]+body+doc[b:]

before=metrics(html)

for marker in [
    'meta name="fjz-no-first-review-alerts" content="21.27"',
    'meta name="fjz-unified-session-history" content="20.44"',
    'meta name="fjz-session-exercise-comments" content="20.87"',
    'meta name="fjz-training-comments-center" content="21.25"',
    'id="v244UnifiedSessionHistoryRuntime"',
    'id="v302ReviewResolutionAuthorityRuntime"',
    "exerciseCommentsVisiblePerSessionV287:true",
    "trainingCommentsCenterV325:true",
    "firstReviewCardsDisabledV327:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.28 prerequisite missing "+marker)

def patch_v302(body):
    old_button=">Abrir alumno</button>"
    new_button=">Ver sesión del día</button>"
    if body.count(old_button)!=1:
        raise RuntimeError("V21.28 dashboard comment button text mismatch: "+str(body.count(old_button)))
    body=body.replace(old_button,new_button,1)

    old_func=re.search(
        r"  window\.__fjzOpenTrainingCommentV325=function\(studentId,sessionId\)\{.*?\n  \};",
        body,re.S
    )
    if not old_func:
        raise RuntimeError("V21.28 comment deeplink function missing")

    new_func=r"""  window.__fjzOpenTrainingCommentV325=async function(studentId,sessionId){
    const s=byId(studentId);
    const sid=String(sessionId||'');
    if(!s||!sid)return false;

    const target=(Array.isArray(s?.sessions)?s.sessions:[])
      .find(x=>String(x?.id||'')===sid);

    state.selectedStudentId=s.id;
    saveState();
    coachTab='student';

    if(!target){
      coachStudentTab='summary';
      render();
      try{toast?.('La sesión de este comentario ya no está disponible.')}catch(_e){}
      return false;
    }

    window.__fjzFocusTrainingCommentV328={
      studentId:String(s.id||''),
      sessionId:sid,
      dayName:String(target?.dayName||'Entrenamiento'),
      date:target?.date||null
    };

    coachStudentTab='history';
    render();

    await Promise.resolve();
    try{
      if(typeof window.sessionDetails==='function'){
        await window.sessionDetails(sid);
        return true;
      }
    }catch(e){
      console.warn('TEAM FJZ V21.28 comment session deeplink',e);
    }

    return false;
  };"""
    body=body[:old_func.start()]+new_func+body[old_func.end():]

    flag="""    newStudentsNeedRealActivityForReviewCardV327:true,"""
    if body.count(flag)!=1:
        raise RuntimeError("V21.28 V302 flag anchor mismatch")
    body=body.replace(flag,flag+"""
    trainingCommentOpensExactSessionV328:true,
    trainingCommentRoutesToHistoryV328:true,
    missingCommentSessionFallsBackSafelyV328:true,""",1)
    return body

html=edit_script(html,"v302ReviewResolutionAuthorityRuntime",patch_v302)

def patch_v244(body):
    old="""    const sum=ss.summary||{};
    const isCoachView=mode==='coach'&&currentProfile?.role==='coach';
    const exercises=Array.isArray(ss.exerciseResults)&&ss.exerciseResults.length"""
    new="""    const sum=ss.summary||{};
    const isCoachView=mode==='coach'&&currentProfile?.role==='coach';
    const linkedCommentV328=String(window.__fjzFocusTrainingCommentV328?.sessionId||'')===String(ss.id||'');
    const exercises=Array.isArray(ss.exerciseResults)&&ss.exerciseResults.length"""
    if body.count(old)!=1:
        raise RuntimeError("V21.28 session details linked-comment anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""      '<button class="btn small" type="button" aria-label="Cerrar" title="Cerrar" onclick="closeModal()">✕</button></div>'+
      '<div class="v244-summary-grid">'+"""
    new="""      '<button class="btn small" type="button" aria-label="Cerrar" title="Cerrar" onclick="closeModal()">✕</button></div>'+
      (linkedCommentV328?'<div class="v328-comment-session-banner"><strong>Comentario del alumno</strong><span>Esta es la sesión exacta donde dejó el comentario.</span></div>':'')+
      '<div class="v244-summary-grid">'+"""
    if body.count(old)!=1:
        raise RuntimeError("V21.28 session modal banner anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    );
  };
  try{sessionDetails=window.sessionDetails}catch(_e){}"""
    new="""    );
    if(linkedCommentV328)window.__fjzFocusTrainingCommentV328=null;
  };
  try{sessionDetails=window.sessionDetails}catch(_e){}"""
    if body.count(old)!=1:
        raise RuntimeError("V21.28 session detail clear-focus anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    flag="""    historicalExerciseCommentFallbackV287:true"""
    if body.count(flag)!=1:
        raise RuntimeError("V21.28 V244 flag anchor mismatch")
    body=body.replace(flag,flag+""",
    exactCommentSessionDeeplinkV328:true,
    linkedCommentSessionBannerV328:true""",1)
    return body

html=edit_script(html,"v244UnifiedSessionHistoryRuntime",patch_v244)

css=r"""
/* TEAM FJZ · V21.28 COMMENT → EXACT SESSION */
.v328-comment-session-banner{
  display:flex;
  gap:8px;
  align-items:center;
  margin:0 0 10px;
  padding:9px 10px;
  border:1px solid rgba(242,189,85,.22);
  border-radius:10px;
  background:rgba(242,189,85,.055);
}
.v328-comment-session-banner strong{
  color:#f0c766;
  font-size:9px;
  font-weight:900;
  text-transform:uppercase;
  letter-spacing:.05em;
}
.v328-comment-session-banner span{
  color:#c8cbd1;
  font-size:9px;
  line-height:1.35;
}
@media(max-width:560px){
  .v328-comment-session-banner{
    display:grid;
    gap:3px;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V21.28 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-comment-session-deeplink" content="21.28">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V21.28 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-comment-session-deeplink" content="21.28"',
    "trainingCommentOpensExactSessionV328:true",
    "trainingCommentRoutesToHistoryV328:true",
    "missingCommentSessionFallsBackSafelyV328:true",
    "exactCommentSessionDeeplinkV328:true",
    "linkedCommentSessionBannerV328:true",
    "coachStudentTab='history'",
    "await window.sessionDetails(sid)",
    "Ver sesión del día",
    "Esta es la sesión exacta donde dejó el comentario.",
    "exerciseCommentsVisiblePerSessionV287:true",
    "firstReviewCardsDisabledV327:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.28 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.28 comment exact-session deeplink")
print("V21.28 BEFORE:",before)
print("V21.28 AFTER:",after)
