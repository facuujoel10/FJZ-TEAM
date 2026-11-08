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
    mid=-1
    for marker in ('id="'+script_id+'"',"id='"+script_id+"'"):
        mid=doc.find(marker)
        if mid>=0: break
    if mid<0: raise RuntimeError("V21.39 missing script "+script_id)
    a=doc.find(">",mid); b=doc.find("</script>",a)
    if a<0 or b<0: raise RuntimeError("V21.39 malformed script "+script_id)
    old=doc[a+1:b]
    new=transform(old)
    if new==old: raise RuntimeError("V21.39 no changes in "+script_id)
    return doc[:a+1]+new+doc[b:]

before=metrics(html)

for marker in [
    'meta name="fjz-athlete-alert-curtain" content="21.38"',
    'id="v280OperationalRecoveryRuntime"',
    'id="v331ProfessionalAlertGroupingRuntime"',
    "groupedAlertCloudReadbackV336:true",
    "coachNeverSeesKgRepAsLoadV337:true",
    "athleteCurtainSingleCardV338:true",
    "firstReviewCardsDisabledV327:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.39 prerequisite missing "+marker)

def patch_v280(body):
    start=body.find("  renderPriority=function(){")
    end_marker="""  window.__fjzOpenPriorityV280=async function(id,tab){
    try{await window.__fjzMarkCoachReviewSeenV299?.(id)}catch(e){console.warn('TEAM FJZ V20.99 mark review seen',e)}
    openStudent(id,tab);
  };"""
    end=body.find(end_marker,start)
    if start<0 or end<0:
        raise RuntimeError("V21.39 review center bounds missing")
    end+=len(end_marker)

    replacement=r"""  const reviewCurtainOpenV339=window.__fjzReviewCurtainOpenV339 instanceof Set
    ?window.__fjzReviewCurtainOpenV339
    :new Set();
  window.__fjzReviewCurtainOpenV339=reviewCurtainOpenV339;

  function reviewKindLabelV339(kind){
    const map={
      progression:'Progreso',
      training:'Entrenamiento',
      checkin:'Check-in',
      wellness:'Recuperación',
      nutrition:'Nutrición',
      exercise_feedback:'Comentario',
      payment:'Cobranza'
    };
    return map[String(kind||'')]||'Seguimiento';
  }

  function reviewTabV339(kind){
    if(kind==='nutrition')return 'nutrition';
    if(kind==='progression')return 'progress';
    if(kind==='exercise_feedback'||kind==='training')return 'routine';
    if(kind==='checkin'||kind==='wellness')return 'tracking';
    if(kind==='payment')return 'payments';
    return 'summary';
  }

  function reviewSeverityLabelV339(severity){
    if(severity==='critical')return 'Prioridad alta';
    if(severity==='warning')return 'Revisar';
    if(severity==='success')return 'Progreso';
    return 'Info';
  }

  function reviewFeedRowsV339(s){
    const seen=new Map();
    (feedFor(s)||[]).forEach(x=>{
      const k=String(x?.event_key||[x?.kind,x?.title,x?.occurred_at].join('|'));
      const prev=seen.get(k);
      const prevTime=Date.parse(prev?.occurred_at||0)||0;
      const curTime=Date.parse(x?.occurred_at||0)||0;
      if(!prev||curTime>=prevTime)seen.set(k,x);
    });
    const rank={critical:4,warning:3,success:2,info:1};
    return [...seen.values()].sort((a,b)=>
      (rank[b?.severity]||0)-(rank[a?.severity]||0)||
      (Date.parse(b?.occurred_at||0)||0)-(Date.parse(a?.occurred_at||0)||0)
    );
  }

  function reviewAlertHtmlV339(s,x){
    const key=String(x?.event_key||'');
    return '<div class="v339-review-alert '+esc(x?.severity||'info')+'" data-v339-event-key="'+esc(key)+'">'+
      '<div class="v339-review-alert-copy">'+
        '<div class="v339-review-alert-meta"><span>'+esc(reviewKindLabelV339(x?.kind))+'</span><span>·</span><span>'+esc(reviewSeverityLabelV339(x?.severity))+'</span></div>'+
        '<strong>'+esc(x?.title||'Alerta')+'</strong>'+
        (x?.body?'<p>'+esc(x.body)+'</p>':'')+
      '</div>'+
      '<div class="v339-review-alert-actions">'+
        '<button class="btn small" onclick="window.__fjzOpenReviewAlertV339(\''+esc(s?.id||'')+'\',\''+esc(x?.kind||'')+'\')">Ver</button>'+
        '<button class="btn small v299-ok v339-review-ok" onclick="window.__fjzResolveReviewCenterAlertV339(\''+esc(key)+'\',this)">✓ OK</button>'+
      '</div>'+
    '</div>';
  }

  function reviewSyntheticHtmlV339(x){
    const signals=(x?.signals||[]).filter(Boolean);
    if(!signals.length)return '';
    return '<div class="v339-review-alert info v339-review-synthetic">'+
      '<div class="v339-review-alert-copy">'+
        '<div class="v339-review-alert-meta"><span>Seguimiento general</span></div>'+
        '<strong>Revisión del alumno</strong>'+
        '<div class="v339-review-synthetic-list">'+signals.map(v=>'<p>'+esc(v)+'</p>').join('')+'</div>'+
      '</div>'+
      '<div class="v339-review-alert-actions">'+
        '<button class="btn small" onclick="window.__fjzOpenReviewAlertV339(\''+esc(x?.s?.id||'')+'\',\'summary\')">Ver</button>'+
        '<button class="btn small v299-ok" onclick="window.__fjzResolveReviewSyntheticV339(\''+esc(x?.s?.id||'')+'\',this)">✓ OK</button>'+
      '</div>'+
    '</div>';
  }

  window.__fjzToggleReviewCurtainV339=function(studentId){
    const id=String(studentId||'');
    if(!id)return;
    if(reviewCurtainOpenV339.has(id))reviewCurtainOpenV339.delete(id);
    else reviewCurtainOpenV339.add(id);
    const host=el('v252PriorityCenter');
    if(!host)return;
    host.querySelectorAll('.v339-review-student[data-v339-student]').forEach(node=>{
      if(String(node.dataset.v339Student||'')!==id)return;
      const open=reviewCurtainOpenV339.has(id);
      node.classList.toggle('open',open);
      const detail=node.querySelector('.v339-review-detail');
      if(detail)detail.hidden=!open;
      const btn=node.querySelector('.v339-review-head');
      if(btn)btn.setAttribute('aria-expanded',open?'true':'false');
    });
  };

  window.__fjzOpenReviewAlertV339=function(studentId,kind){
    openStudent(studentId,reviewTabV339(kind));
  };

  window.__fjzResolveReviewCenterAlertV339=async function(eventKey,button){
    const key=String(eventKey||'');
    if(!key)return false;
    const previous=button?.textContent||'✓ OK';
    if(button){button.disabled=true;button.textContent='Guardando…'}
    try{
      let ok=false;
      if(typeof window.__fjzResolveGroupedAlertV336==='function'){
        ok=await window.__fjzResolveGroupedAlertV336(key,button);
      }else if(typeof dismissCoachAlertV96==='function'){
        ok=await dismissCoachAlertV96(key);
      }else if(typeof dismissFeed==='function'){
        ok=await dismissFeed(key);
      }
      if(ok===false)throw new Error('No se pudo resolver la alerta.');
      renderPriority();
      try{renderCoachFocusV235?.();decorateCoachAlertsV235?.();renderCoachStudentsV235?.()}catch(_e){}
      return true;
    }catch(e){
      console.warn('TEAM FJZ V21.39 individual review alert OK',e);
      if(button){button.disabled=false;button.textContent=previous}
      try{toast?.(typeof cloudErr==='function'?cloudErr(e):'No se pudo guardar el OK de la alerta.')}catch(_e){}
      return false;
    }
  };

  window.__fjzResolveReviewSyntheticV339=async function(studentId,button){
    const id=String(studentId||'');
    if(!id)return false;
    const s=(state?.students||[]).find(x=>String(x?.id||'')===id)||null;
    if(!s)return false;
    if((feedFor(s)||[]).length)return false;
    const previous=button?.textContent||'✓ OK';
    if(button){button.disabled=true;button.textContent='Guardando…'}
    try{
      const ok=await window.__fjzMarkCoachReviewOkV298?.(id);
      if(ok===false)throw new Error('No se pudo resolver el seguimiento.');
      renderPriority();
      return true;
    }catch(e){
      console.warn('TEAM FJZ V21.39 synthetic review OK',e);
      if(button){button.disabled=false;button.textContent=previous}
      return false;
    }
  };

  renderPriority=function(){
    const host=el('v252PriorityCenter');if(!host)return;
    const urgent=priorityRows('urgent'),today=priorityRows('today');

    const row=x=>{
      const feed=reviewFeedRowsV339(x.s);
      const hasFeed=feed.length>0;
      const detailCount=hasFeed?feed.length:(x.signals||[]).filter(Boolean).length;
      const id=String(x.s?.id||'');
      const open=reviewCurtainOpenV339.has(id);
      const categories=[...new Set(feed.map(a=>reviewKindLabelV339(a?.kind)))];
      const chips=(categories.length?categories:['Seguimiento']).slice(0,4)
        .map(c=>'<span class="v339-review-chip">'+esc(c)+'</span>').join('');
      const details=hasFeed
        ?feed.map(a=>reviewAlertHtmlV339(x.s,a)).join('')
        :reviewSyntheticHtmlV339(x);

      return '<section class="v299-priority-card v339-review-student '+esc(x.bucket)+' '+(open?'open':'')+'" data-v339-student="'+esc(id)+'">'+
        '<button type="button" class="v339-review-head" aria-expanded="'+(open?'true':'false')+'" onclick="window.__fjzToggleReviewCurtainV339(\''+esc(id)+'\')">'+
          '<span class="v280-priority-avatar">'+esc((x.s.name||'A').slice(0,2).toUpperCase())+'</span>'+
          '<span class="v339-review-head-copy"><strong>'+esc(x.s.name||'Alumno')+'</strong>'+
            '<small>'+(detailCount?detailCount+' alerta'+(detailCount===1?'':'s')+' pendiente'+(detailCount===1?'':'s'):'Seguimiento pendiente')+'</small>'+
            '<span class="v339-review-chips">'+chips+'</span>'+
          '</span>'+
          '<span class="v339-review-count">'+Math.max(1,detailCount)+'</span>'+
          '<span class="v339-review-chevron">⌄</span>'+
        '</button>'+
        '<div class="v339-review-detail" '+(open?'':'hidden')+'>'+
          details+
        '</div>'+
      '</section>';
    };

    const col=(title,cls,rows,empty)=>'<section class="v299-priority-column '+cls+'">'+
      '<div class="v299-priority-headline"><strong>'+title+'</strong><span>'+rows.length+'</span></div>'+
      (rows.length?rows.map(row).join(''):'<div class="v280-empty">'+empty+'</div>')+
    '</section>';

    host.innerHTML=
      '<div class="v280-priority-head"><div><div class="v225-section-kicker">CENTRO DE REVISIONES</div><h3>Pendientes activos</h3>'+
      '<p>Cada alumno aparece una sola vez. Abrí su cortina para leer todas las alertas y resolvelas individualmente con OK.</p></div></div>'+
      '<div class="v299-priority-grid">'+
        col('Urgente','urgent',urgent,'Sin urgencias pendientes')+
        col('Revisar','today',today,'Nada pendiente para revisar')+
      '</div>';
  };

  window.__fjzOpenPriorityV280=function(id,tab){
    openStudent(id,tab);
  };

  window.__fjzV339={
    version:'21.39',
    reviewCenterCurtainV339:true,
    reviewCenterAllFeedAlertsV339:true,
    reviewCenterIndividualOkV339:true,
    reviewCenterOpenDoesNotArchiveV339:true,
    reviewCenterNoPerAthleteSliceV339:true,
    noExtraTimers:true,
    noExtraListeners:true,
    noExtraObservers:true
  };"""

    body=body[:start]+replacement+body[end:]
    return body

html=edit_script(html,"v280OperationalRecoveryRuntime",patch_v280)

def patch_v331(body):
    # V21.38 used one bulk OK in this secondary grouped surface. Restore
    # the same per-alert semantics requested for the canonical review center.
    row_start=body.find("  function rowHtml(")
    row_end=body.find("\n  const alertGroupsOpenV333",row_start)
    if row_start<0 or row_end<0:
        raise RuntimeError("V21.39 V331 rowHtml bounds missing")
    row_block=body[row_start:row_end]
    empty_action="""        ''+"""
    restored_action="""        (dismiss?'<button class="btn small v299-ok v336-alert-ok" data-v336-ok-key="'+safe(x?.event_key||'')+'" onclick="window.__fjzResolveGroupedAlertV336(\\''+js(x?.event_key)+'\\',this)">✓ OK</button>':'')+"""
    if row_block.count(empty_action)!=1:
        raise RuntimeError("V21.39 V331 empty action anchor mismatch: "+str(row_block.count(empty_action)))
    row_block=row_block.replace(empty_action,restored_action,1)
    body=body[:row_start]+row_block+body[row_end:]

    old_footer="""      '<div class="v331-alert-list" '+(open?'':'hidden')+'>'+g.rows.map(x=>rowHtml(x,{dismiss})).join('')+
        (dismiss?'<div class="v338-athlete-alert-footer"><span>'+g.rows.length+' alerta'+(g.rows.length===1?'':'s')+' de '+safe(g.name)+' · se revisan juntas</span><button type="button" class="btn small v299-ok v338-athlete-ok" onclick="window.__fjzResolveAthleteAlertGroupV338(this)">✓ OK todas</button></div>':'')+
      '</div>'+"""
    new_footer="""      '<div class="v331-alert-list" '+(open?'':'hidden')+'>'+g.rows.map(x=>rowHtml(x,{dismiss})).join('')+'</div>'+"""
    if body.count(old_footer)!=1:
        raise RuntimeError("V21.39 V331 bulk footer anchor mismatch: "+str(body.count(old_footer)))
    body=body.replace(old_footer,new_footer,1)

    marker="""    oneRefreshAfterAthleteAckV338:true
  };"""
    replacement="""    oneRefreshAfterAthleteAckV338:true,
    individualOkRestoredV339:true,
    bulkOkUiRemovedV339:true,
    curtainReadOnlyOnToggleV339:true
  };"""
    if body.count(marker)!=1:
        raise RuntimeError("V21.39 V331 marker anchor mismatch")
    body=body.replace(marker,replacement,1)
    return body

html=edit_script(html,"v331ProfessionalAlertGroupingRuntime",patch_v331)

css=r"""
/* TEAM FJZ · V21.39 CANONICAL REVIEW CENTER CURTAIN */
.v339-review-student{
  overflow:hidden;
}
.v339-review-head{
  width:100%;
  display:grid;
  grid-template-columns:36px minmax(0,1fr) auto 26px;
  gap:10px;
  align-items:center;
  padding:11px 12px;
  border:0;
  background:transparent;
  color:inherit;
  text-align:left;
  cursor:pointer;
}
.v339-review-head:hover{background:rgba(255,255,255,.018)}
.v339-review-head-copy{min-width:0}
.v339-review-head-copy>strong{
  display:block;
  color:#f1f3f5;
  font-size:12px;
}
.v339-review-head-copy>small{
  display:block;
  margin-top:3px;
  color:#9299a4;
  font-size:9px;
}
.v339-review-chips{
  display:flex;
  flex-wrap:wrap;
  gap:4px;
  margin-top:6px;
}
.v339-review-chip{
  display:inline-flex;
  padding:2px 6px;
  border:1px solid rgba(255,255,255,.07);
  border-radius:999px;
  color:#aab1bb;
  font-size:7.5px;
  background:rgba(255,255,255,.02);
}
.v339-review-count{
  min-width:26px;
  height:26px;
  display:grid;
  place-items:center;
  border:1px solid #353b45;
  border-radius:999px;
  color:#d6dae0;
  font-size:9px;
  font-weight:900;
}
.v339-review-chevron{
  display:grid;
  place-items:center;
  width:24px;
  height:24px;
  border:1px solid #30353d;
  border-radius:999px;
  color:#aeb5bf;
  transition:transform .16s ease;
}
.v339-review-student.open .v339-review-chevron{transform:rotate(180deg)}
.v339-review-detail{
  border-top:1px solid rgba(255,255,255,.06);
}
.v339-review-detail[hidden]{display:none!important}
.v339-review-alert{
  display:grid;
  grid-template-columns:minmax(0,1fr) auto;
  gap:12px;
  align-items:center;
  padding:12px;
  border-top:1px solid rgba(255,255,255,.045);
}
.v339-review-alert:first-child{border-top:0}
.v339-review-alert-copy{min-width:0}
.v339-review-alert-meta{
  display:flex;
  gap:5px;
  color:#8e96a1;
  font-size:8px;
  font-weight:800;
  text-transform:uppercase;
}
.v339-review-alert-copy>strong{
  display:block;
  margin-top:5px;
  color:#eef1f4;
  font-size:11px;
  line-height:1.35;
}
.v339-review-alert-copy p{
  margin:4px 0 0;
  color:#949ca7;
  font-size:9.5px;
  line-height:1.45;
}
.v339-review-alert-actions{
  display:flex;
  gap:6px;
  align-items:center;
}
.v339-review-alert-actions .btn{min-width:64px}
.v339-review-synthetic-list{display:grid;gap:2px}
@media(max-width:640px){
  .v339-review-head{
    grid-template-columns:34px minmax(0,1fr) auto 24px;
    padding:11px 10px;
  }
  .v339-review-alert{
    grid-template-columns:minmax(0,1fr);
    padding:11px 10px;
  }
  .v339-review-alert-actions{
    display:grid;
    grid-template-columns:1fr 1fr;
  }
  .v339-review-alert-actions .btn{width:100%;min-width:0}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V21.39 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-review-center-curtain" content="21.39">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V21.39 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-review-center-curtain" content="21.39"',
    "reviewCenterCurtainV339:true",
    "reviewCenterAllFeedAlertsV339:true",
    "reviewCenterIndividualOkV339:true",
    "reviewCenterOpenDoesNotArchiveV339:true",
    "reviewCenterNoPerAthleteSliceV339:true",
    "__fjzToggleReviewCurtainV339",
    "__fjzResolveReviewCenterAlertV339",
    "Cada alumno aparece una sola vez",
    "individualOkRestoredV339:true",
    "bulkOkUiRemovedV339:true",
    "groupedAlertCloudReadbackV336:true",
    "coachNeverSeesKgRepAsLoadV337:true",
    "firstReviewCardsDisabledV327:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.39 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.39 canonical review center curtain")
print("V21.39 BEFORE:",before)
print("V21.39 AFTER:",after)
