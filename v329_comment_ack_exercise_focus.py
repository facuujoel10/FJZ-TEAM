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
        raise RuntimeError("V21.29 missing script "+sid)
    a=doc.find(">",mid); b=doc.find("</script>",a)
    if a<0 or b<0:
        raise RuntimeError("V21.29 malformed script "+sid)
    body=doc[a+1:b]
    body=fn(body)
    return doc[:a+1]+body+doc[b:]

before=metrics(html)

for marker in [
    'meta name="fjz-comment-session-deeplink" content="21.28"',
    'id="v244UnifiedSessionHistoryRuntime"',
    'id="v302ReviewResolutionAuthorityRuntime"',
    'id="v175ProfileAgendaCoachCenterRuntime"',
    "exerciseCommentsVisiblePerSessionV287:true",
    "trainingCommentsCenterV325:true",
    "trainingCommentOpensExactSessionV328:true",
    "firstReviewCardsDisabledV327:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
    "reviewExerciseFeedbackV73",
]:
    if marker not in html:
        raise RuntimeError("V21.29 prerequisite missing "+marker)

# ------------------------------------------------------------------
# 1) Comment center: durable OK + pass exact exercise identity.
# ------------------------------------------------------------------
def patch_v302(body):
    old="""          kind:'session',exerciseName:'',message:general,
          status:fb?.status||'pending',difficultyTypes:Array.isArray(fb?.difficultyTypes)?fb.difficultyTypes:[],"""
    new="""          kind:'session',exerciseName:'',exerciseUid:'',feedbackId:'',message:general,
          status:fb?.status||'pending',difficultyTypes:Array.isArray(fb?.difficultyTypes)?fb.difficultyTypes:[],"""
    if body.count(old)!=1:
        raise RuntimeError("V21.29 dashboard session-comment identity anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""            kind:'exercise',exerciseName:er?.exerciseName||er?.name||'Ejercicio',message,
            status:x?.status||'pending',difficultyTypes:[],"""
    new="""            kind:'exercise',exerciseName:er?.exerciseName||er?.name||'Ejercicio',
            exerciseUid:String(er?.exerciseUid||''),feedbackId:String(x?.id||''),message,
            status:x?.status||'pending',difficultyTypes:[],"""
    if body.count(old)!=1:
        raise RuntimeError("V21.29 dashboard exercise-comment identity anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""      '<div class="v325-comment-actions"><button class="btn small primary" onclick="window.__fjzOpenTrainingCommentV325?.(\\''+safe(x.studentId)+'\\',\\''+safe(x.sessionId)+'\\')">Ver sesión del día</button></div>'+
    '</article>';"""
    new="""      '<div class="v325-comment-actions '+(pending?'v329-has-ok':'')+'">'+
        '<button class="btn small primary" onclick="window.__fjzOpenTrainingCommentV325?.(\\''+safe(x.studentId)+'\\',\\''+safe(x.sessionId)+'\\',\\''+safe(x.kind)+'\\',\\''+safe(x.feedbackId||'')+'\\',\\''+safe(x.exerciseUid||'')+'\\')">Ver sesión del día</button>'+
        (pending?'<button class="btn small v329-comment-ok" onclick="window.__fjzAckTrainingCommentV329?.(\\''+safe(x.studentId)+'\\',\\''+safe(x.sessionId)+'\\',\\''+safe(x.kind)+'\\',\\''+safe(x.feedbackId||'')+'\\',\\''+safe(x.exerciseUid||'')+'\\')">OK</button>':'')+
      '</div>'+
    '</article>';"""
    if body.count(old)!=1:
        raise RuntimeError("V21.29 dashboard comment actions anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    open_func=re.search(
        r"  window\.__fjzOpenTrainingCommentV325=async function\(studentId,sessionId\)\{.*?\n  \};",
        body,re.S
    )
    if not open_func:
        raise RuntimeError("V21.29 V328 deeplink function not found")

    new_open=r"""  window.__fjzOpenTrainingCommentV325=async function(studentId,sessionId,commentKind,feedbackId,exerciseUid){
    const s=byId(studentId);
    const sid=String(sessionId||'');
    const kind=String(commentKind||'session');
    const fid=String(feedbackId||'');
    const euid=String(exerciseUid||'');
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

    const targetExercise=(Array.isArray(target?.exerciseResults)?target.exerciseResults:[])
      .find(r=>{
        if(euid&&String(r?.exerciseUid||'')===euid)return true;
        if(fid&&(Array.isArray(r?.exerciseFeedback)?r.exerciseFeedback:[])
          .some(x=>String(x?.id||'')===fid))return true;
        return false;
      })||null;

    window.__fjzFocusTrainingCommentV328={
      studentId:String(s.id||''),
      sessionId:sid,
      dayName:String(target?.dayName||'Entrenamiento'),
      date:target?.date||null,
      kind,
      feedbackId:fid,
      exerciseUid:euid||String(targetExercise?.exerciseUid||''),
      exerciseName:String(targetExercise?.exerciseName||targetExercise?.name||'')
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
      console.warn('TEAM FJZ V21.29 comment exact exercise deeplink',e);
    }

    return false;
  };"""
    body=body[:open_func.start()]+new_open+body[open_func.end():]

    insert_anchor="""  function renderTrainingCommentsV325(){"""
    if body.count(insert_anchor)!=1:
        raise RuntimeError("V21.29 ack insertion anchor mismatch")

    ack=r"""
  const trainingCommentAckBusyV329=new Set();

  async function persistSessionCommentAckV333(s,ss,reviewedAt){
    if(!(cloudEnabled&&supabaseClient))return true;
    const row=cloudAthletes?.get?.(String(s?.id||''));
    if(!row?.id)throw new Error('No se encontró la ficha cloud del alumno.');

    const next=typeof clone==='function'?clone(s):JSON.parse(JSON.stringify(s));
    const target=(Array.isArray(next?.sessions)?next.sessions:[])
      .find(x=>String(x?.id||'')===String(ss?.id||''));
    const fb=target?.sessionFeedback;
    if(!target||!fb)throw new Error('No se encontró el comentario en el snapshot.');

    fb.status='reviewed';
    fb.reviewedAt=reviewedAt;
    fb.reviewedBy=currentUser?.id||null;

    try{cloudLastWrite=Date.now()}catch(_e){}

    const {error:upErr}=await supabaseClient.from('athlete_snapshots')
      .upsert({athlete_id:row.id,data:next,updated_at:reviewedAt},{onConflict:'athlete_id'});
    if(upErr)throw upErr;

    const {data:confirmed,error:readErr}=await supabaseClient.from('athlete_snapshots')
      .select('data,updated_at')
      .eq('athlete_id',row.id)
      .single();
    if(readErr)throw readErr;

    const persisted=(Array.isArray(confirmed?.data?.sessions)?confirmed.data.sessions:[])
      .find(x=>String(x?.id||'')===String(ss?.id||''));
    if(persisted?.sessionFeedback?.status!=='reviewed'){
      throw new Error('Supabase no confirmó el OK del comentario.');
    }
    return true;
  }

  window.__fjzAckTrainingCommentV329=async function(studentId,sessionId,commentKind,feedbackId,exerciseUid){
    if(currentProfile?.role!=='coach')return false;
    const s=byId(studentId);
    const sid=String(sessionId||'');
    const kind=String(commentKind||'session');
    const fid=String(feedbackId||'');
    const euid=String(exerciseUid||'');
    const ss=(Array.isArray(s?.sessions)?s.sessions:[]).find(x=>String(x?.id||'')===sid);
    if(!s||!ss)return false;

    const lock=[String(s?.id||''),sid,kind,fid,euid].join('|');
    if(trainingCommentAckBusyV329.has(lock))return false;
    trainingCommentAckBusyV329.add(lock);

    try{
      const reviewedAt=new Date().toISOString();

      if(kind==='exercise'){
        let row=null;
        let exercise=null;
        const results=Array.isArray(ss?.exerciseResults)?ss.exerciseResults:[];
        for(const r of results){
          const rows=Array.isArray(r?.exerciseFeedback)?r.exerciseFeedback:[];
          const hit=rows.find(x=>fid&&String(x?.id||'')===fid);
          if(hit){row=hit;exercise=r;break}
        }
        if(!row&&euid){
          exercise=results.find(r=>String(r?.exerciseUid||'')===euid)||null;
          row=(Array.isArray(exercise?.exerciseFeedback)?exercise.exerciseFeedback:[])
            .find(x=>x?.status==='pending')||null;
        }
        if(!row){
          try{toast?.('No pude encontrar ese comentario en la sesión.')}catch(_e){}
          return false;
        }

        if(cloudEnabled&&supabaseClient&&fid){
          const {data,error}=await supabaseClient.from('exercise_feedback')
            .update({
              status:'reviewed',
              reviewed_by:currentUser?.id||null,
              reviewed_at:reviewedAt
            })
            .eq('id',fid)
            .select('id,status')
            .single();
          if(error)throw error;
          if(String(data?.id||'')!==fid||data?.status!=='reviewed'){
            throw new Error('No se pudo verificar el OK del comentario.');
          }
        }

        row.status='reviewed';
        row.reviewedAt=reviewedAt;
        row.reviewedBy=currentUser?.id||null;
        try{exerciseFeedbackCacheV73?.clear?.()}catch(_e){}
        try{exerciseFeedbackAllCoachV73=[]}catch(_e){}
        try{coachFeedLoadedAt=0}catch(_e){}
      }else{
        const fb=ss?.sessionFeedback;
        if(!fb){
          try{toast?.('No pude encontrar el comentario de esa sesión.')}catch(_e){}
          return false;
        }

        await persistSessionCommentAckV333(s,ss,reviewedAt);

        fb.status='reviewed';
        fb.reviewedAt=reviewedAt;
        fb.reviewedBy=currentUser?.id||null;
      }

      saveState();
      try{render()}catch(_e){}
      try{renderTrainingCommentsV325()}catch(_e){}
      try{toast?.('Comentario marcado como revisado')}catch(_e){}
      return true;
    }catch(e){
      console.warn('TEAM FJZ V21.29 comment OK',e);
      try{toast?.(typeof cloudErr==='function'?cloudErr(e):'No se pudo guardar el OK.')}catch(_e){}
      return false;
    }finally{
      trainingCommentAckBusyV329.delete(lock);
    }
  };

"""
    body=body.replace(insert_anchor,ack+insert_anchor,1)

    flag="""    missingCommentSessionFallsBackSafelyV328:true,"""
    if body.count(flag)!=1:
        raise RuntimeError("V21.29 V302 flag anchor mismatch")
    body=body.replace(flag,flag+"""
    trainingCommentOkV329:true,
    trainingCommentOkCloudVerifiedV329:true,
    trainingCommentSnapshotStatusSyncedV329:true,
    trainingCommentCarriesExerciseIdentityV329:true,
    sessionCommentAckSnapshotVerifiedV333:true,
    sessionCommentAckReadbackV333:true,""",1)
    return body

html=edit_script(html,"v302ReviewResolutionAuthorityRuntime",patch_v302)

# ------------------------------------------------------------------
# 2) Athlete 360 comment panel gets the same OK action.
# ------------------------------------------------------------------
def patch_v175(body):
    old="""          session:ss,kind:'session',exerciseName:'',message:general,status:fb?.status||'pending',
          difficultyTypes:Array.isArray(fb?.difficultyTypes)?fb.difficultyTypes:[],"""
    new="""          session:ss,kind:'session',exerciseName:'',exerciseUid:'',feedbackId:'',message:general,status:fb?.status||'pending',
          difficultyTypes:Array.isArray(fb?.difficultyTypes)?fb.difficultyTypes:[],"""
    if body.count(old)!=1:
        raise RuntimeError("V21.29 360 session-comment identity anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""            session:ss,kind:'exercise',exerciseName:er?.exerciseName||er?.name||'Ejercicio',
            message,status:x?.status||'pending',difficultyTypes:[],"""
    new="""            session:ss,kind:'exercise',exerciseName:er?.exerciseName||er?.name||'Ejercicio',
            exerciseUid:String(er?.exerciseUid||''),feedbackId:String(x?.id||''),
            message,status:x?.status||'pending',difficultyTypes:[],"""
    if body.count(old)!=1:
        raise RuntimeError("V21.29 360 exercise-comment identity anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""      (canReview&&pending?'<div class="v325-comment-actions"><button class="btn small primary" onclick="openSessionFeedbackCoachV242(\\''+esc(ss.id)+'\\')">Revisar y responder</button></div>':'')+
    '</article>';"""
    new="""      (pending?'<div class="v325-comment-actions v329-has-ok">'+
        (canReview?'<button class="btn small primary" onclick="openSessionFeedbackCoachV242(\\''+esc(ss.id)+'\\')">Revisar y responder</button>':'')+
        '<button class="btn small v329-comment-ok" onclick="window.__fjzAckTrainingCommentV329?.(\\''+esc(student()?.id||'')+'\\',\\''+esc(ss.id||'')+'\\',\\''+esc(x.kind)+'\\',\\''+esc(x.feedbackId||'')+'\\',\\''+esc(x.exerciseUid||'')+'\\')">OK</button>'+
      '</div>':'')+
    '</article>';"""
    if body.count(old)!=1:
        raise RuntimeError("V21.29 360 comment action anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    flag="""    pendingCommentsFirstV325:true"""
    if body.count(flag)!=1:
        raise RuntimeError("V21.29 V175 flag anchor mismatch")
    body=body.replace(flag,flag+""",
    trainingCommentOkIn360V329:true""",1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

# ------------------------------------------------------------------
# 3) Session history: highlight the exact exercise and exact comment.
# ------------------------------------------------------------------
def patch_v244(body):
    old_func=re.search(r"  function exerciseCommentHtmlV287\(rows\)\{.*?\n  \}\n\n  function exerciseHtmlV244",body,re.S)
    if not old_func:
        raise RuntimeError("V21.29 exerciseCommentHtmlV287 block missing")

    replacement=r"""  function commentFocusMatchesV329(ss,r,x){
    const f=window.__fjzFocusTrainingCommentV328||null;
    if(!f||f.kind!=='exercise')return false;
    if(String(f.sessionId||'')!==String(ss?.id||''))return false;
    if(f.feedbackId&&x?.id)return String(f.feedbackId)===String(x.id);
    if(f.exerciseUid)return String(f.exerciseUid)===String(r?.exerciseUid||'');
    return false;
  }

  function exerciseFocusMatchesV329(ss,r,rows){
    const f=window.__fjzFocusTrainingCommentV328||null;
    if(!f||f.kind!=='exercise')return false;
    if(String(f.sessionId||'')!==String(ss?.id||''))return false;
    if(f.feedbackId&&(Array.isArray(rows)?rows:[]).some(x=>String(x?.id||'')===String(f.feedbackId)))return true;
    return !!f.exerciseUid&&String(f.exerciseUid)===String(r?.exerciseUid||'');
  }

  function exerciseCommentHtmlV287(rows,ss,r){
    if(!rows?.length)return '';
    return '<div class="v287-exercise-comments">'+
      rows.map(x=>{
        const focused=commentFocusMatchesV329(ss,r,x);
        return '<div class="v287-exercise-comment '+(x.type==='discomfort'?'discomfort ':'')+(focused?'v329-comment-target':'')+'">'+
          '<div class="v287-exercise-comment-head">'+
            '<strong>'+feedbackTypeLabelV287(x.type)+'</strong>'+
            (x.status==='reviewed'?'<span class="badge green">Revisado</span>':'<span class="badge amber">Pendiente</span>')+
          '</div>'+
          '<p>'+esc(x.message)+'</p>'+
        '</div>';
      }).join('')+
    '</div>';
  }

  function exerciseHtmlV244"""
    body=body[:old_func.start()]+replacement+body[old_func.end()-len("  function exerciseHtmlV244"):]

    old="""    const comments=exerciseFeedbackForSessionV287(ss,r,feedbackRows);

    return '<div class="v244-exercise">'+"""
    new="""    const comments=exerciseFeedbackForSessionV287(ss,r,feedbackRows);
    const focusExerciseV329=exerciseFocusMatchesV329(ss,r,comments);

    return '<div class="v244-exercise '+(focusExerciseV329?'v329-comment-exercise-focus':'')+'">'+"""
    if body.count(old)!=1:
        raise RuntimeError("V21.29 exercise focus root anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""      exerciseCommentHtmlV287(comments)+"""
    new="""      exerciseCommentHtmlV287(comments,ss,r)+"""
    if body.count(old)!=1:
        raise RuntimeError("V21.29 exercise comment call anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    if(linkedCommentV328)window.__fjzFocusTrainingCommentV328=null;
  };"""
    new="""    if(linkedCommentV328){
      try{
        const exact=document.querySelector('.v329-comment-target')
          ||document.querySelector('.v329-comment-exercise-focus');
        exact?.scrollIntoView?.({block:'center',behavior:'auto'});
      }catch(_e){}
      window.__fjzFocusTrainingCommentV328=null;
    }
  };"""
    if body.count(old)!=1:
        raise RuntimeError("V21.29 focus clear/scroll anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    flag="""    linkedCommentSessionBannerV328:true"""
    if body.count(flag)!=1:
        raise RuntimeError("V21.29 V244 flag anchor mismatch")
    body=body.replace(flag,flag+""",
    exactExerciseCommentHighlightV329:true,
    exactExerciseCommentAutoScrollV329:true""",1)
    return body

html=edit_script(html,"v244UnifiedSessionHistoryRuntime",patch_v244)

css=r"""
/* TEAM FJZ · V21.29 COMMENT OK + EXACT EXERCISE FOCUS */
.v325-comment-actions{
  gap:7px;
  flex-wrap:wrap;
}
.v329-comment-ok{
  min-width:54px;
  border-color:rgba(59,213,138,.28)!important;
  background:rgba(59,213,138,.08)!important;
  color:#9fe5be!important;
  font-weight:900!important;
}
.v329-comment-exercise-focus{
  border-color:rgba(242,189,85,.52)!important;
  box-shadow:0 0 0 2px rgba(242,189,85,.10);
  background:
    linear-gradient(90deg,rgba(242,189,85,.055),transparent 42%),
    #101116!important;
}
.v329-comment-target{
  border-color:rgba(242,189,85,.52)!important;
  border-left-color:#f2bd55!important;
  background:rgba(242,189,85,.075)!important;
  box-shadow:0 0 0 2px rgba(242,189,85,.08);
}
@media(max-width:560px){
  .v325-comment-actions.v329-has-ok{
    display:grid;
    grid-template-columns:minmax(0,1fr) 58px;
  }
  .v325-comment-actions.v329-has-ok .btn{
    width:100%;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V21.29 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-comment-ok-exercise-focus" content="21.29">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V21.29 topology changed "+key+": "+repr({"before":before,"after":after}))

required=[
    'meta name="fjz-comment-ok-exercise-focus" content="21.29"',
    "__fjzAckTrainingCommentV329",
    "trainingCommentOkCloudVerifiedV329:true",
    "trainingCommentSnapshotStatusSyncedV329:true",
    "trainingCommentCarriesExerciseIdentityV329:true",
    "trainingCommentOkIn360V329:true",
    "commentFocusMatchesV329",
    "exerciseFocusMatchesV329",
    "v329-comment-exercise-focus",
    "v329-comment-target",
    "exerciseCommentHtmlV287(comments,ss,r)",
    "exactExerciseCommentHighlightV329:true",
    "exactExerciseCommentAutoScrollV329:true",
    ".select('id,status')",
    "firstReviewCardsDisabledV327:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]
for marker in required:
    if marker not in html:
        raise RuntimeError("V21.29 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.29 comment OK + exact exercise focus")
print("V21.29 BEFORE:",before)
print("V21.29 AFTER:",after)
