import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def topology(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "intervals":len(re.findall(r"setInterval\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
    }

def edit_script(doc,script_id,fn):
    pattern=re.compile(r'(<script[^>]*id=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    matches=list(pattern.finditer(doc))
    if len(matches)!=1:
        raise RuntimeError("V22 2A script authority mismatch "+script_id+": "+str(len(matches)))
    m=matches[0]
    return doc[:m.start(2)]+fn(m.group(2))+doc[m.end(2):]

before=topology(html)

for marker in [
    'meta name="fjz-v22-1b-data-sync-foundation" content="agenda-read-pilot"',
    'id="v205CanonicalWorkoutProgressRuntime"',
    'id="v315DecimalWorkoutWeightsRuntime"',
    'id="v145WorkoutAutosaveRuntime"',
    'id="v207ConfirmedSessionCommitRuntime"',
    "openExerciseFeedbackV73",
    "submitExerciseFeedbackV73",
]:
    if marker not in html:
        raise RuntimeError("V22 2A prerequisite missing "+marker)

module_code=pathlib.Path("src/modules/workouts/premium-workout.js").read_text(encoding="utf-8").strip()
session_history_code=pathlib.Path("src/modules/workouts/session-history.js").read_text(encoding="utf-8").strip()
visual_code=pathlib.Path("src/modules/workouts/visual-redesign.js").read_text(encoding="utf-8").strip()
design_css=pathlib.Path("src/ui/design-system.css").read_text(encoding="utf-8").strip()
premium_css=pathlib.Path("src/ui/premium-workout.css").read_text(encoding="utf-8").strip()
history_css=pathlib.Path("src/ui/premium-history.css").read_text(encoding="utf-8").strip()
if "</script" in module_code.lower() or "</script" in session_history_code.lower() or "</script" in visual_code.lower():
    raise RuntimeError("V22 module cannot contain closing script markup")

html=html.replace("</head>",'<script id="v22PremiumWorkoutModule">\n'+module_code+'\n</script>\n<script id="v22SessionHistoryModule">\n'+session_history_code+'\n</script>\n<script id="v22VisualRedesignModule">\n'+visual_code+'\n</script>\n<meta name="fjz-v22-2a-premium-workout" content="enabled">\n<meta name="fjz-v22-2b-session-history" content="enabled">\n<meta name="fjz-v22-2bv-visual-redesign" content="enabled">\n</head>',1)

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V22 2A expected one consolidated stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+design_css+"\n"+premium_css+"\n"+history_css+"\n"+html[sm.end("body"):]

def patch_v205(body):
    old="      return baseRenderWorkoutV205.apply(this,arguments);\n"
    new="      const out=baseRenderWorkoutV205.apply(this,arguments);\n      try{globalThis.TeamFJZPremiumWorkout?.enhanceWorkout()}catch(_e){}\n      return out;\n"
    if body.count(old)!=1:
        raise RuntimeError("V22 2A V205 renderWorkout anchor mismatch: "+str(body.count(old)))
    return body.replace(old,new,1)
html=edit_script(html,"v205CanonicalWorkoutProgressRuntime",patch_v205)

def patch_v315(body):
    old="""    window.setWorkout=function(uidv,si,field,val){
      if(Number(field)===0)val=normalizeDecimalV315(val);
      return baseSetWorkoutV315.call(this,uidv,si,field,val);
    };"""
    new="""    window.setWorkout=function(uidv,si,field,val){
      if(Number(field)===0)val=normalizeDecimalV315(val);
      const out=baseSetWorkoutV315.call(this,uidv,si,field,val);
      try{globalThis.TeamFJZPremiumWorkout?.markDraftChanged()}catch(_e){}
      try{globalThis.TeamFJZPremiumWorkout?.enhanceWorkout()}catch(_e){}
      return out;
    };"""
    if body.count(old)!=1:
        raise RuntimeError("V22 2A V315 setWorkout anchor mismatch: "+str(body.count(old)))
    return body.replace(old,new,1)
html=edit_script(html,"v315DecimalWorkoutWeightsRuntime",patch_v315)

def patch_v145(body):
    old="""    if(n){
      const d=new Date(lastSavedAt);
      n.textContent='Último guardado '+d.toLocaleTimeString('es-AR',{hour:'2-digit',minute:'2-digit'});
    }
  }"""
    new="""    if(n){
      const d=new Date(lastSavedAt);
      n.textContent='Último guardado '+d.toLocaleTimeString('es-AR',{hour:'2-digit',minute:'2-digit'});
    }
    try{globalThis.TeamFJZPremiumWorkout?.draftProtected(lastSavedAt)}catch(_e){}
  }"""
    if body.count(old)!=1:
        raise RuntimeError("V22 2A V145 draft status anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""      startedAt,
      updatedAt:new Date().toISOString(),"""
    new="""      startedAt,
      sessionId:globalThis.TeamFJZSessionHistory?.ensureSessionId({studentId:s.id,dayId:d.id,priorSessionId:prior?.sessionId,startedAt})||prior?.sessionId||null,
      updatedAt:new Date().toISOString(),"""
    if body.count(old)!=1:
        raise RuntimeError("V22 2B V145 session id pack anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    anchor="""  window.__fjzWorkoutAutosaveV145={"""
    if body.count(anchor)!=1:
        raise RuntimeError("V22 2B V145 export anchor mismatch")
    helper="""  window.__fjzEnsureWorkoutSessionIdentityV2B=function(){
    const s=student?.(),d=s?.days?.[currentDay];
    if(!s||!d)return null;
    const prior=freshestV145(readLocalV145(s,d),readCloudV145(s,d));
    const sessionId=globalThis.TeamFJZSessionHistory?.ensureSessionId({
      studentId:s.id,dayId:d.id,priorSessionId:prior?.sessionId,startedAt:prior?.startedAt||null
    })||prior?.sessionId||null;
    try{globalThis.TeamFJZSessionHistory?.activate({studentId:s.id,dayId:d.id,sessionId,startedAt:prior?.startedAt||null})}catch(_e){}
    return sessionId;
  };
  window.__fjzWorkoutSessionIdV2B=function(){
    return globalThis.TeamFJZSessionHistory?.activeSessionId?.()||window.__fjzEnsureWorkoutSessionIdentityV2B?.()||null;
  };
  """
    body=body.replace(anchor,helper+anchor,1)
    return body
html=edit_script(html,"v145WorkoutAutosaveRuntime",patch_v145)

def patch_v106(body):
    old="      id:uid('ss'),"
    new="      id:(globalThis.TeamFJZSessionHistory?.activeSessionId?.()||uid('ss')),"
    if body.count(old)!=1:
        raise RuntimeError("V22 2B V106 stable session id anchor mismatch: "+str(body.count(old)))
    return body.replace(old,new,1)
html=edit_script(html,"v106PartialSessionsRuntime",patch_v106)

def patch_v207(body):
    pairs=[
      ("stateV207='saving';","stateV207='saving';\n    try{globalThis.TeamFJZPremiumWorkout?.setSaveState('saving')}catch(_e){}"),
      ("stateV207='success';","stateV207='success';\n      try{globalThis.TeamFJZPremiumWorkout?.setSaveState('success')}catch(_e){}"),
      ("stateV207='failed';\n      // Keep pendingV207","stateV207='failed';\n      try{globalThis.TeamFJZPremiumWorkout?.setSaveState('failed')}catch(_e){}\n      // Keep pendingV207"),
      ("stateV207='failed';\n      modalErrorV207('No pudimos preparar","stateV207='failed';\n      try{globalThis.TeamFJZPremiumWorkout?.setSaveState('failed')}catch(_e){}\n      modalErrorV207('No pudimos preparar"),
      ("      stateV207='idle';\n      pendingV207=null;","      stateV207='idle';\n      try{globalThis.TeamFJZPremiumWorkout?.setSaveState('idle')}catch(_e){}\n      pendingV207=null;"),
    ]
    for old,new in pairs:
        count=body.count(old)
        if count<1:
            raise RuntimeError("V22 2A V207 state anchor missing: "+repr(old))
        body=body.replace(old,new)
    old="      modalSuccessV207();"
    new="      modalSuccessV207();\n      try{globalThis.TeamFJZPremiumWorkout?.decorateSuccessModal()}catch(_e){}"
    count=body.count(old)
    if count<1:
        raise RuntimeError("V22 2A V207 success modal call anchor missing")
    body=body.replace(old,new)

    old="""    const session=window.__fjzSaveSessionV205?.(pack);
    if(!session)throw new Error('No se pudo preparar la sesión.');

    applyWorkoutStartedAtV340(pack,session);"""
    new="""    const session=window.__fjzSaveSessionV205?.(pack);
    if(!session)throw new Error('No se pudo preparar la sesión.');
    const stableIdV2B=globalThis.TeamFJZSessionHistory?.activeSessionId?.();
    if(stableIdV2B&&String(session.id)!==String(stableIdV2B))throw new Error('La identidad de sesión cambió durante el guardado.');

    applyWorkoutStartedAtV340(pack,session);"""
    if body.count(old)!=1:
        raise RuntimeError("V22 2B V207 prepared session identity anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""      window.__fjzSessionCloudConfirmedId=session.id;

      stateV207='success';"""
    new="""      window.__fjzSessionCloudConfirmedId=session.id;
      try{globalThis.TeamFJZSessionHistory?.markConfirmed(session.id)}catch(_e){}

      stateV207='success';"""
    if body.count(old)!=1:
        raise RuntimeError("V22 2B V207 confirmation identity anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""      return baseStartV207.apply(this,arguments);
    };"""
    new="""      const out=baseStartV207.apply(this,arguments);
      try{window.__fjzEnsureWorkoutSessionIdentityV2B?.()}catch(_e){}
      return out;
    };"""
    if body.count(old)!=1:
        raise RuntimeError("V22 2B V207 start identity anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old_block="""    const sessionTime=Date.parse(session.date||0)||Date.now();
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
    });"""
    new_block="""    const sessionTime=Date.parse(session.date||0)||Date.now();
    const maxAge=18*60*60*1000;

    (session.exerciseResults||[]).forEach(r=>{
      const exact=rows.filter(x=>
        String(x?.session_id||'')===String(session.id||'')&&
        String(x?.exercise_uid||'')===String(r?.exerciseUid||'')
      );
      const legacy=rows.filter(x=>{
        if(x?.session_id)return false;
        if(String(x?.exercise_uid||'')!==String(r?.exerciseUid||''))return false;
        const dayMatch=!x?.workout_day_id||!pack?.d?.id||String(x.workout_day_id)===String(pack.d.id);
        if(!dayMatch)return false;
        const t=Date.parse(x?.created_at||0);
        return !!t && Math.abs(sessionTime-t)<=maxAge;
      });
      const matches=(exact.length?exact:legacy)
        .sort((a,b)=>(Date.parse(a?.created_at||0)||0)-(Date.parse(b?.created_at||0)||0));

      if(!matches.length)return;
      r.exerciseFeedback=matches.map(x=>({
        id:x.id||null,
        sessionId:x.session_id||null,
        linkMode:x.session_id?'exact':'historical-compatible',
        type:x.feedback_type||'comment',
        message:String(x.message||'').trim(),
        createdAt:x.created_at||null,
        status:x.status||'pending'
      })).filter(x=>x.message);
    });"""
    if body.count(old_block)!=1:
        raise RuntimeError("V22 2B V287 snapshot matching anchor mismatch: "+str(body.count(old_block)))
    body=body.replace(old_block,new_block,1)
    return body
html=edit_script(html,"v207ConfirmedSessionCommitRuntime",patch_v207)

old="""  exerciseFeedbackTargetV73={uid,name,dayId:d?.id||'',dayName:d?.name||''};
  showModal(`"""
new="""  exerciseFeedbackTargetV73={uid,name,dayId:d?.id||'',dayName:d?.name||''};
  const premiumDraftV22=globalThis.TeamFJZPremiumWorkout?.commentDraft(uid)||null;
  showModal(`"""
if html.count(old)!=1:
    raise RuntimeError("V22 2A comment target anchor mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

old='placeholder="Ej: sentí una molestia al bajar / me costó mantener la técnica / esta carga se sintió muy pesada..."></textarea>'
new='placeholder="Ej: sentí una molestia al bajar / me costó mantener la técnica / esta carga se sintió muy pesada...">${premiumDraftV22?.message?esc(premiumDraftV22.message):\'\'}</textarea>'
if html.count(old)!=1:
    raise RuntimeError("V22 2A comment textarea anchor mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

old="""    <button class="btn primary" style="width:100%;margin-top:12px" onclick="submitExerciseFeedbackV73()">Enviar al coach</button>`)
}"""
new="""    <button class="btn primary" style="width:100%;margin-top:12px" onclick="submitExerciseFeedbackV73()">Enviar al coach</button>`)
  try{globalThis.TeamFJZPremiumWorkout?.bindCommentDraft(exerciseFeedbackTargetV73)}catch(_e){}
}"""
if html.count(old)!=1:
    raise RuntimeError("V22 2A comment bind anchor mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

old="""  const message=el('v73FeedbackMessage')?.value.trim()||'';
  if(message.length<3){toast('Escribí un comentario breve');return}

  const athleteId=currentAthleteIdV73();"""
new="""  const message=el('v73FeedbackMessage')?.value.trim()||'';
  if(message.length<3){toast('Escribí un comentario breve');return}
  if(globalThis.TeamFJZPremiumWorkout&&!globalThis.TeamFJZPremiumWorkout.beginCommentSubmit(t.uid,message,type))return;

  const athleteId=currentAthleteIdV73();"""
if html.count(old)!=1:
    raise RuntimeError("V22 2A comment submit anchor mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

old="""    if(error){toast(cloudErr(error));return}
    const key=feedbackKeyV73(athleteId),rows=exerciseFeedbackCacheV73.get(key)||[];"""
new="""    if(error){try{globalThis.TeamFJZPremiumWorkout?.endCommentSubmit(t.uid,false)}catch(_e){}toast(cloudErr(error));return}
    const key=feedbackKeyV73(athleteId),rows=exerciseFeedbackCacheV73.get(key)||[];"""
if html.count(old)!=1:
    raise RuntimeError("V22 2A comment error anchor mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

old="""  closeModal();
  toast(type==='discomfort'?'Molestia enviada al coach':'Comentario enviado al coach');
  render()
}"""
new="""  try{globalThis.TeamFJZPremiumWorkout?.endCommentSubmit(t.uid,true)}catch(_e){}
  closeModal();
  toast(type==='discomfort'?'Molestia enviada al coach':'Comentario enviado al coach');
  render()
}"""
if html.count(old)!=1:
    raise RuntimeError("V22 2A comment success anchor mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

old="""      workout_day_name:t.dayName||null,
      feedback_type:type,"""
new="""      workout_day_name:t.dayName||null,
      session_id:globalThis.TeamFJZSessionHistory?.activeSessionId?.()||null,
      feedback_type:type,"""
if html.count(old)!=1:
    raise RuntimeError("V22 2B cloud comment session link anchor mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

old="""      id:uid('fb'),exercise_uid:t.uid,exercise_name:t.name,workout_day_id:t.dayId,
      workout_day_name:t.dayName,feedback_type:type,message,status:'pending',created_at:nowISO()"""
new="""      id:uid('fb'),session_id:globalThis.TeamFJZSessionHistory?.activeSessionId?.()||null,exercise_uid:t.uid,exercise_name:t.name,workout_day_id:t.dayId,
      workout_day_name:t.dayName,feedback_type:type,message,status:'pending',created_at:nowISO()"""
if html.count(old)!=1:
    raise RuntimeError("V22 2B local comment session link anchor mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

def patch_v244(body):
    pattern=re.compile(r"  function exerciseFeedbackForSessionV287\(ss,r,rows\)\{.*?\n  \}\n\n  function commentFocusMatchesV329",re.S)
    m=pattern.search(body)
    if not m:
        raise RuntimeError("V22 2B V244 feedback resolver missing")
    resolver=r"""  function exerciseFeedbackForSessionV287(ss,r,rows){
    const all=Array.isArray(rows)?rows:[];
    const exact=all
      .filter(x=>String(x?.session_id||'')===String(ss?.id||'')&&String(x?.exercise_uid||'')===String(r?.exerciseUid||''))
      .sort((a,b)=>(Date.parse(a?.created_at||0)||0)-(Date.parse(b?.created_at||0)||0))
      .map(x=>({id:x.id||null,sessionId:x.session_id||null,linkMode:'exact',type:x.feedback_type||'comment',message:String(x.message||'').trim(),createdAt:x.created_at||null,status:x.status||'pending'}))
      .filter(x=>x.message);
    if(exact.length)return exact;

    const snap=(Array.isArray(r?.exerciseFeedback)?r.exerciseFeedback:[])
      .filter(x=>String(x?.message||'').trim())
      .map(x=>({...x,linkMode:x?.linkMode||(x?.sessionId?'exact':'snapshot')}));
    if(snap.length)return snap;

    const sessionTime=Date.parse(ss?.date||0)||0;
    const maxDelta=18*60*60*1000;
    return all
      .filter(x=>{
        if(x?.session_id)return false;
        if(String(x?.exercise_uid||'')!==String(r?.exerciseUid||''))return false;
        const dayOk=!ss?.dayId||!x?.workout_day_id||String(x.workout_day_id)===String(ss.dayId);
        if(!dayOk)return false;
        const t=Date.parse(x?.created_at||0)||0;
        return !!sessionTime&&!!t&&Math.abs(sessionTime-t)<=maxDelta;
      })
      .sort((a,b)=>(Date.parse(a?.created_at||0)||0)-(Date.parse(b?.created_at||0)||0))
      .map(x=>({id:x.id||null,sessionId:null,linkMode:'historical-compatible',type:x.feedback_type||'comment',message:String(x.message||'').trim(),createdAt:x.created_at||null,status:x.status||'pending'}))
      .filter(x=>x.message);
  }

  function commentFocusMatchesV329"""
    body=body[:m.start()]+resolver+body[m.end():]

    old="""          '<p>'+esc(x.message)+'</p>'+
          (canAck?"""
    new="""          '<p>'+esc(x.message)+'</p>'+
          '<div class="v22-comment-meta">'+
            '<time>'+(x?.createdAt?esc(new Date(x.createdAt).toLocaleString('es-AR')):'Sin fecha')+'</time>'+
            '<span class="v22-comment-link '+(x?.linkMode==='historical-compatible'?'compat':'')+'">'+
              esc(globalThis.TeamFJZSessionHistory?.linkLabel?.(x?.linkMode)||'Comentario guardado')+
            '</span>'+
          '</div>'+
          (canAck?"""
    if body.count(old)!=1:
        raise RuntimeError("V22 2B V244 comment metadata anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    const comments=exerciseFeedbackForSessionV287(ss,r,feedbackRows);
    const focusExerciseV329=exerciseFocusMatchesV329(ss,r,comments);

    return '<div class="v244-exercise '+(focusExerciseV329?'v329-comment-exercise-focus':'')+'">'+"""
    new="""    const comments=exerciseFeedbackForSessionV287(ss,r,feedbackRows);
    const focusExerciseV329=exerciseFocusMatchesV329(ss,r,comments);
    const comparisonV2B=globalThis.TeamFJZSessionHistory?.compareExercise?.(student()?.sessions||[],ss?.id,r?.exerciseUid)||null;
    const comparisonHtmlV2B=comparisonV2B?.previous
      ?'<div class="v22-history-compare"><div class="v22-history-compare-box"><small>Sesión anterior</small><strong>'+esc(String(comparisonV2B.previous.load))+' kg × '+esc(String(comparisonV2B.previous.reps))+'</strong></div><span>→</span><div class="v22-history-compare-box current"><small>Esta sesión</small><strong>'+esc(String(comparisonV2B.current.load))+' kg × '+esc(String(comparisonV2B.current.reps))+'</strong></div></div>'
      :'';

    return '<div class="v244-exercise '+(focusExerciseV329?'v329-comment-exercise-focus':'')+'">'+"""
    if body.count(old)!=1:
        raise RuntimeError("V22 2B V244 comparison anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""      methodHtml+
      exerciseCommentHtmlV287(comments,ss,r)+"""
    new="""      methodHtml+
      comparisonHtmlV2B+
      exerciseCommentHtmlV287(comments,ss,r)+"""
    if body.count(old)!=1:
        raise RuntimeError("V22 2B V244 comparison placement mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    body=body.replace("'<div class=\"card v244-history-card\">'+","'<div class=\"card v244-history-card v22-premium-history\">'+",1)
    body=body.replace("'<div class=\"history-item v244-history-item\">'+","'<div class=\"history-item v244-history-item v22-history-session\">'+",1)
    old="""'<div class="v244-history-badges">'+feedbackBadgeV244(x)+"""
    new="""'<div class="v244-history-badges"><span class="badge green v22-session-confirmed">Confirmada</span>'+feedbackBadgeV244(x)+"""
    if body.count(old)!=1:
        raise RuntimeError("V22 2B V244 confirmed badge anchor mismatch")
    body=body.replace(old,new,1)

    old="""      '<div class="muted tiny">'+esc(new Date(ss.date).toLocaleString('es-AR'))+'</div></div>'+"""
    new="""      '<div class="muted tiny">'+esc(new Date(ss.date).toLocaleString('es-AR'))+'</div><div class="v22-session-detail-status"><span class="badge green v22-session-confirmed">Sesión confirmada</span></div></div>'+"""
    if body.count(old)!=1:
        raise RuntimeError("V22 2B V244 detail status anchor mismatch")
    body=body.replace(old,new,1)

    old="""      :'<div class="empty">Todavía no hay sesiones registradas.</div>';
  };"""
    new="""      :'<div class="empty">Todavía no hay sesiones registradas.</div>';
    try{globalThis.TeamFJZVisualRedesign?.enhanceHistory(b)}catch(_e){}
  };"""
    if body.count(old)!=1:
        raise RuntimeError("V22 2B-V history visual hook mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    if(linkedCommentV328){"""
    new="""    try{globalThis.TeamFJZVisualRedesign?.enhanceSessionDetail(document.getElementById('modal'))}catch(_e){}
    if(linkedCommentV328){"""
    if body.count(old)!=1:
        raise RuntimeError("V22 2B-V session detail visual hook mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    marker="""    exactExerciseCommentAutoScrollV329:true"""
    if marker not in body:
        raise RuntimeError("V22 2B V244 marker anchor missing")
    body=body.replace(marker,marker+""",
    exactSessionCommentLinkV2B:true,
    premiumHistoryV2B:true,
    previousSessionComparisonV2B:true""",1)
    return body

html=edit_script(html,"v244UnifiedSessionHistoryRuntime",patch_v244)

html=html.replace("</body>",'<script id="v22PremiumWorkoutBoot">try{globalThis.TeamFJZPremiumWorkout?.enhanceWorkout()}catch(_e){}</script>\n</body>',1)

after=topology(html)
for key in ("styles","renders","channels","timeouts","intervals","listeners","mutation_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V22 2A topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'id="v22PremiumWorkoutModule"',
    'meta name="fjz-v22-2a-premium-workout" content="enabled"',
    'meta name="fjz-v22-2b-session-history" content="enabled"',
    'meta name="fjz-v22-2bv-visual-redesign" content="enabled"',
    "TeamFJZPremiumWorkout?.enhanceWorkout",
    "TeamFJZPremiumWorkout?.setSaveState('saving')",
    "TeamFJZPremiumWorkout?.bindCommentDraft",
    "beginCommentSubmit(t.uid,message,type)",
    "endCommentSubmit(t.uid,true)",
    "decorateSuccessModal",
    'id="v22SessionHistoryModule"',
    'id="v22VisualRedesignModule"',
    "TeamFJZVisualRedesign?.enhanceWorkout",
    "TeamFJZVisualRedesign?.enhanceHistory",
    "TeamFJZVisualRedesign?.enhanceSessionDetail",
    "TeamFJZSessionHistory?.activeSessionId",
    "session_id:globalThis.TeamFJZSessionHistory",
    "exactSessionCommentLinkV2B:true",
    "premiumHistoryV2B:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V22 2A missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V22 2B-V VISUAL REDESIGN")
print("V22 2A BEFORE:",before)
print("V22 2A AFTER:",after)
