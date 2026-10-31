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

def edit_script(doc,sid,fn):
    mid=-1
    for marker in ('id="'+sid+'"',"id='"+sid+"'"):
        mid=doc.find(marker)
        if mid>=0:
            break
    if mid<0:
        raise RuntimeError("V21.36 missing script "+sid)
    a=doc.find(">",mid)
    b=doc.find("</script>",a)
    if a<0 or b<0:
        raise RuntimeError("V21.36 malformed script "+sid)
    body=doc[a+1:b]
    new=fn(body)
    if new==body:
        raise RuntimeError("V21.36 no changes in "+sid)
    return doc[:a+1]+new+doc[b:]

before=metrics(html)

for marker in [
    'meta name="fjz-review-center-athlete-accordion" content="21.34"',
    'meta name="fjz-professional-progress-alert-copy" content="21.35"',
    'id="v331ProfessionalAlertGroupingRuntime"',
    'id="v302ReviewResolutionAuthorityRuntime"',
    "reviewCenterAthleteFirstV334:true",
    "sessionCommentAckSnapshotVerifiedV333:true",
    "trainingCommentsInboxPendingOnlyV330:true",
    "firstReviewCardsDisabledV327:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.36 prerequisite missing "+marker)

def patch_v331(body):
    old_row="""    return '<div class="v331-alert-row '+safe(x?.severity||'info')+'">'+"""
    new_row="""    return '<div class="v331-alert-row '+safe(x?.severity||'info')+'" data-v336-event-key="'+safe(x?.event_key||'')+'">'+"""
    if body.count(old_row)!=1:
        raise RuntimeError("V21.36 grouped row anchor mismatch: "+str(body.count(old_row)))
    body=body.replace(old_row,new_row,1)

    old_button="""        (dismiss?'<button class="btn ghost small" onclick="window.__fjzDismissGroupedAlertV331(\\''+js(x?.event_key)+'\\')">Ocultar</button>':'')+"""
    new_button="""        (dismiss?'<button class="btn small v299-ok v336-alert-ok" data-v336-ok-key="'+safe(x?.event_key||'')+'" onclick="window.__fjzResolveGroupedAlertV336(\\''+js(x?.event_key)+'\\',this)">✓ OK</button>':'')+"""
    if body.count(old_button)!=1:
        raise RuntimeError("V21.36 grouped OK button anchor mismatch: "+str(body.count(old_button)))
    body=body.replace(old_button,new_button,1)

    old_fn="""  window.__fjzDismissGroupedAlertV331=async function(eventKey){
    if(typeof dismissFeed==='function')return dismissFeed(eventKey);
    if(typeof dismissCoachAlertV96==='function')return dismissCoachAlertV96(eventKey);
  };
"""
    new_fn=r"""  const groupedAlertAckBusyV336=window.__fjzGroupedAlertAckBusyV336 instanceof Set
    ?window.__fjzGroupedAlertAckBusyV336
    :new Set();
  window.__fjzGroupedAlertAckBusyV336=groupedAlertAckBusyV336;

  async function confirmGroupedAlertAckV336(eventKey){
    if(!(cloudEnabled&&supabaseClient&&!window.__fjzStagingLocal?.enabled))return true;
    const {data,error}=await supabaseClient.from('coach_feed_state')
      .select('event_key,read_at,dismissed_at')
      .eq('coach_id',currentUser.id)
      .eq('event_key',String(eventKey||''))
      .single();
    if(error)throw error;
    if(String(data?.event_key||'')!==String(eventKey||'')||!data?.read_at||!data?.dismissed_at){
      throw new Error('Supabase no confirmó el OK de la alerta.');
    }
    return true;
  }

  window.__fjzResolveGroupedAlertV336=async function(eventKey,button){
    const key=String(eventKey||'');
    if(!key||groupedAlertAckBusyV336.has(key))return false;
    groupedAlertAckBusyV336.add(key);

    const previousText=button?.textContent||'✓ OK';
    if(button){
      button.disabled=true;
      button.textContent='Guardando…';
    }

    try{
      let ok=false;
      if(typeof dismissCoachAlertV96==='function'){
        ok=await dismissCoachAlertV96(key);
      }else if(typeof dismissFeed==='function'){
        ok=await dismissFeed(key);
      }
      if(ok===false)throw new Error('No se pudo cerrar la alerta.');

      await confirmGroupedAlertAckV336(key);

      try{window.__fjzReviewedCoachKeysV297?.add?.(key)}catch(_e){}
      try{coachAlertsV96=(coachAlertsV96||[]).filter(x=>String(x?.event_key||'')!==key)}catch(_e){}
      try{coachFeedV235=(coachFeedV235||[]).filter(x=>String(x?.event_key||'')!==key)}catch(_e){}
      try{coachFeedCache=(coachFeedCache||[]).filter(x=>String(x?.event_key||'')!==key)}catch(_e){}
      try{coachFeedLoadedAt=0}catch(_e){}

      try{
        if(typeof refreshCoachFeed==='function')await refreshCoachFeed();
      }catch(_e){}
      try{
        document.querySelectorAll('[data-v336-event-key="'+CSS.escape(key)+'"]').forEach(node=>{
          const group=node.closest('.v331-alert-group');
          node.remove();
          if(!group)return;
          const remaining=group.querySelectorAll('.v331-alert-row[data-v336-event-key]').length;
          if(!remaining){
            group.remove();
            return;
          }
          const count=group.querySelector('.v331-alert-count');
          if(count)count.textContent=remaining+' alerta'+(remaining===1?'':'s');
        });
      }catch(_e){}
      try{renderCoachAlertsV96?.();updateCoachBellV96?.()}catch(_e){}
      try{await window.__fjzRenderPrioritySmartV278?.()}catch(_e){}
      try{toast?.('✓ Alerta revisada')}catch(_e){}
      return true;
    }catch(e){
      console.warn('TEAM FJZ V21.36 grouped alert OK',e);
      try{
        coachFeedLoadedAt=0;
        if(typeof refreshCoachFeed==='function')await refreshCoachFeed();
        renderCoachAlertsV96?.();
        updateCoachBellV96?.();
        await window.__fjzRenderPrioritySmartV278?.();
      }catch(_e){}
      try{toast?.(typeof cloudErr==='function'?cloudErr(e):'No se pudo guardar el OK de la alerta.')}catch(_e){}
      if(button){
        button.disabled=false;
        button.textContent=previousText;
      }
      return false;
    }finally{
      groupedAlertAckBusyV336.delete(key);
    }
  };

  window.__fjzDismissGroupedAlertV331=function(eventKey){
    return window.__fjzResolveGroupedAlertV336(eventKey,null);
  };
"""
    if body.count(old_fn)!=1:
        raise RuntimeError("V21.36 grouped dismiss authority anchor mismatch: "+str(body.count(old_fn)))
    body=body.replace(old_fn,new_fn,1)

    marker="""    coachReadingLabelV335:true
  };"""
    replacement="""    coachReadingLabelV335:true,
    groupedAlertOkUsesReviewAuthorityV336:true,
    groupedAlertCloudReadbackV336:true,
    groupedAlertOkBusyLockV336:true,
    groupedAlertPersistsAcrossRefreshV336:true
  };"""
    if body.count(marker)!=1:
        raise RuntimeError("V21.36 V331 marker anchor mismatch")
    body=body.replace(marker,replacement,1)
    return body

html=edit_script(html,"v331ProfessionalAlertGroupingRuntime",patch_v331)

def patch_v302(body):
    ack_anchor="""  window.__fjzAckTrainingCommentV329=async function(studentId,sessionId,commentKind,feedbackId,exerciseUid){"""
    if body.count(ack_anchor)!=1:
        raise RuntimeError("V21.36 exercise snapshot helper anchor mismatch")

    helper=r"""
  async function persistExerciseCommentAckSnapshotV336(s,ss,feedbackId,exerciseUid,reviewedAt){
    if(!(cloudEnabled&&supabaseClient))return true;
    const cloudRow=cloudAthletes?.get?.(String(s?.id||''));
    if(!cloudRow?.id)throw new Error('No se encontró la ficha cloud del alumno.');

    const next=typeof clone==='function'?clone(s):JSON.parse(JSON.stringify(s));
    const target=(Array.isArray(next?.sessions)?next.sessions:[])
      .find(x=>String(x?.id||'')===String(ss?.id||''));
    if(!target)throw new Error('No se encontró la sesión del comentario en el snapshot.');

    const fid=String(feedbackId||'');
    const euid=String(exerciseUid||'');
    const results=Array.isArray(target?.exerciseResults)?target.exerciseResults:[];
    let targetExercise=null,targetFeedback=null;

    for(const r of results){
      const rows=Array.isArray(r?.exerciseFeedback)?r.exerciseFeedback:[];
      const hit=rows.find(x=>fid&&String(x?.id||'')===fid);
      if(hit){targetExercise=r;targetFeedback=hit;break}
    }
    if(!targetFeedback&&euid){
      targetExercise=results.find(r=>String(r?.exerciseUid||'')===euid)||null;
      targetFeedback=(Array.isArray(targetExercise?.exerciseFeedback)?targetExercise.exerciseFeedback:[])
        .find(x=>x?.status==='pending')||null;
    }
    if(!targetExercise||!targetFeedback){
      throw new Error('No se encontró el comentario de ejercicio en el snapshot.');
    }

    targetFeedback.status='reviewed';
    targetFeedback.reviewedAt=reviewedAt;
    targetFeedback.reviewedBy=currentUser?.id||null;

    try{cloudLastWrite=Date.now()}catch(_e){}

    const {error:upErr}=await supabaseClient.from('athlete_snapshots')
      .upsert({athlete_id:cloudRow.id,data:next,updated_at:reviewedAt},{onConflict:'athlete_id'});
    if(upErr)throw upErr;

    const {data:confirmed,error:readErr}=await supabaseClient.from('athlete_snapshots')
      .select('data,updated_at')
      .eq('athlete_id',cloudRow.id)
      .single();
    if(readErr)throw readErr;

    const persistedSession=(Array.isArray(confirmed?.data?.sessions)?confirmed.data.sessions:[])
      .find(x=>String(x?.id||'')===String(ss?.id||''));
    const persistedResults=Array.isArray(persistedSession?.exerciseResults)?persistedSession.exerciseResults:[];
    let persistedFeedback=null;
    for(const r of persistedResults){
      const rows=Array.isArray(r?.exerciseFeedback)?r.exerciseFeedback:[];
      persistedFeedback=rows.find(x=>fid&&String(x?.id||'')===fid)||persistedFeedback;
      if(persistedFeedback)break;
    }
    if(!persistedFeedback&&euid){
      const ex=persistedResults.find(r=>String(r?.exerciseUid||'')===euid)||null;
      persistedFeedback=(Array.isArray(ex?.exerciseFeedback)?ex.exerciseFeedback:[])
        .find(x=>x?.status==='reviewed')||null;
    }
    if(persistedFeedback?.status!=='reviewed'){
      throw new Error('Supabase no confirmó el OK del comentario de ejercicio.');
    }
    return true;
  }

"""
    body=body.replace(ack_anchor,helper+ack_anchor,1)

    old_table=r"""        if(cloudEnabled&&supabaseClient&&fid){
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

        row.status='reviewed';"""
    new_table=r"""        if(cloudEnabled&&supabaseClient&&fid){
          const {data,error}=await supabaseClient.from('exercise_feedback')
            .update({
              status:'reviewed',
              reviewed_by:currentUser?.id||null,
              reviewed_at:reviewedAt
            })
            .eq('id',fid)
            .select('id,status,reviewed_at')
            .single();
          if(error)throw error;
          if(String(data?.id||'')!==fid||data?.status!=='reviewed'||!data?.reviewed_at){
            throw new Error('No se pudo verificar el OK del comentario.');
          }
        }

        await persistExerciseCommentAckSnapshotV336(s,ss,fid,euid,reviewedAt);

        row.status='reviewed';"""
    if body.count(old_table)!=1:
        raise RuntimeError("V21.36 exercise durable OK anchor mismatch: "+str(body.count(old_table)))
    body=body.replace(old_table,new_table,1)

    marker="""    sessionCommentAckReadbackV333:true,"""
    replacement="""    sessionCommentAckReadbackV333:true,
    exerciseCommentAckSnapshotVerifiedV336:true,
    exerciseCommentAckReadbackV336:true,
    exerciseCommentOkRequiresDurableSnapshotV336:true,"""
    if body.count(marker)!=1:
        raise RuntimeError("V21.36 V302 marker anchor mismatch")
    body=body.replace(marker,replacement,1)
    return body

html=edit_script(html,"v302ReviewResolutionAuthorityRuntime",patch_v302)

css=r"""
/* TEAM FJZ · V21.36 REVIEW + COMMENT ACK HARDENING */
.v336-alert-ok{
  min-width:64px!important;
  border-color:rgba(59,213,138,.30)!important;
  background:rgba(59,213,138,.075)!important;
  color:#9fe5be!important;
  font-weight:900!important;
}
.v336-alert-ok:disabled{
  opacity:.65;
  cursor:wait;
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V21.36 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-review-comment-hardening" content="21.36">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V21.36 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-review-comment-hardening" content="21.36"',
    "groupedAlertOkUsesReviewAuthorityV336:true",
    "groupedAlertCloudReadbackV336:true",
    "groupedAlertOkBusyLockV336:true",
    "groupedAlertPersistsAcrossRefreshV336:true",
    "__fjzResolveGroupedAlertV336",
    "✓ OK",
    "exerciseCommentAckSnapshotVerifiedV336:true",
    "exerciseCommentAckReadbackV336:true",
    "exerciseCommentOkRequiresDurableSnapshotV336:true",
    "persistExerciseCommentAckSnapshotV336",
    "sessionCommentAckSnapshotVerifiedV333:true",
    "trainingCommentsInboxPendingOnlyV330:true",
    "reviewCenterAthleteFirstV334:true",
    "alertsCollapsedByDefaultV333:true",
    "firstReviewCardsDisabledV327:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.36 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.36 review + comment acknowledgement hardening")
print("V21.36 BEFORE:",before)
print("V21.36 AFTER:",after)
