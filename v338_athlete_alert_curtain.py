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
    if mid<0: raise RuntimeError("V21.38 missing script "+script_id)
    a=doc.find(">",mid); b=doc.find("</script>",a)
    if a<0 or b<0: raise RuntimeError("V21.38 malformed script "+script_id)
    old=doc[a+1:b]
    new=transform(old)
    if new==old: raise RuntimeError("V21.38 no changes in "+script_id)
    return doc[:a+1]+new+doc[b:]

before=metrics(html)

for marker in [
    'meta name="fjz-coach-alert-logic" content="21.37"',
    'id="v331ProfessionalAlertGroupingRuntime"',
    "reviewCenterAthleteFirstV334:true",
    "groupedAlertCloudReadbackV336:true",
    "coachNeverSeesKgRepAsLoadV337:true",
    "firstReviewCardsDisabledV327:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.38 prerequisite missing "+marker)

def patch_v331(body):
    # Remove per-alert OK from the athlete curtain. Detail rows remain visible together;
    # acknowledgement is now one durable action for the whole athlete group.
    old_button="""        (dismiss?'<button class="btn small v299-ok v336-alert-ok" data-v336-ok-key="'+safe(x?.event_key||'')+'" onclick="window.__fjzResolveGroupedAlertV336(\\''+js(x?.event_key)+'\\',this)">✓ OK</button>':'')+"""
    new_button="""        ''+"""
    if body.count(old_button)!=1:
        raise RuntimeError("V21.38 individual OK anchor mismatch: "+str(body.count(old_button)))
    body=body.replace(old_button,new_button,1)

    old_list="""      '<div class="v331-alert-list" '+(open?'':'hidden')+'>'+g.rows.map(x=>rowHtml(x,{dismiss})).join('')+'</div>'+
    '</section>';"""
    new_list="""      '<div class="v331-alert-list" '+(open?'':'hidden')+'>'+g.rows.map(x=>rowHtml(x,{dismiss})).join('')+
        (dismiss?'<div class="v338-athlete-alert-footer"><span>'+g.rows.length+' alerta'+(g.rows.length===1?'':'s')+' de '+safe(g.name)+' · se revisan juntas</span><button type="button" class="btn small v299-ok v338-athlete-ok" onclick="window.__fjzResolveAthleteAlertGroupV338(this)">✓ OK todas</button></div>':'')+
      '</div>'+
    '</section>';"""
    if body.count(old_list)!=1:
        raise RuntimeError("V21.38 athlete footer anchor mismatch: "+str(body.count(old_list)))
    body=body.replace(old_list,new_list,1)

    insert_anchor="""  window.__fjzDismissGroupedAlertV331=function(eventKey){
    return window.__fjzResolveGroupedAlertV336(eventKey,null);
  };
"""
    if body.count(insert_anchor)!=1:
        raise RuntimeError("V21.38 grouped resolver anchor mismatch")

    bulk=r"""
  const athleteGroupAckBusyV338=window.__fjzAthleteGroupAckBusyV338 instanceof Set
    ?window.__fjzAthleteGroupAckBusyV338
    :new Set();
  window.__fjzAthleteGroupAckBusyV338=athleteGroupAckBusyV338;

  async function confirmAthleteAlertGroupAckV338(keys){
    if(!(cloudEnabled&&supabaseClient&&!window.__fjzStagingLocal?.enabled))return true;
    const clean=[...new Set((keys||[]).filter(Boolean).map(String))];
    if(!clean.length)return true;
    const {data,error}=await supabaseClient.from('coach_feed_state')
      .select('event_key,read_at,dismissed_at')
      .eq('coach_id',currentUser.id)
      .in('event_key',clean);
    if(error)throw error;
    const confirmed=new Map((data||[]).map(x=>[String(x?.event_key||''),x]));
    const missing=clean.filter(k=>{
      const row=confirmed.get(k);
      return !row?.read_at||!row?.dismissed_at;
    });
    if(missing.length)throw new Error('Supabase no confirmó todas las alertas del alumno.');
    return true;
  }

  window.__fjzResolveAthleteAlertGroupV338=async function(button){
    const group=button?.closest?.('.v331-alert-group');
    if(!group)return false;
    const groupKey=String(group.dataset.v333Key||'');
    const name=String(group.querySelector('.v331-alert-student>strong')?.textContent||'Alumno').trim();
    const keys=[...group.querySelectorAll('.v331-alert-row[data-v336-event-key]')]
      .map(node=>String(node.dataset.v336EventKey||''))
      .filter(Boolean);
    const clean=[...new Set(keys)];
    if(!clean.length){
      group.remove();
      return true;
    }

    const busyKey=groupKey||name||clean.join('|');
    if(athleteGroupAckBusyV338.has(busyKey))return false;
    athleteGroupAckBusyV338.add(busyKey);

    const previousText=button?.textContent||'✓ OK todas';
    if(button){
      button.disabled=true;
      button.textContent='Guardando…';
    }

    try{
      const now=new Date().toISOString();
      if(cloudEnabled&&supabaseClient&&!window.__fjzStagingLocal?.enabled){
        const rows=clean.map(event_key=>({
          coach_id:currentUser.id,
          event_key,
          read_at:now,
          dismissed_at:now
        }));
        const {error}=await supabaseClient.from('coach_feed_state')
          .upsert(rows,{onConflict:'coach_id,event_key'});
        if(error)throw error;
      }

      await confirmAthleteAlertGroupAckV338(clean);

      try{clean.forEach(k=>window.__fjzReviewedCoachKeysV297?.add?.(k))}catch(_e){}
      const keySet=new Set(clean);
      try{coachAlertsV96=(coachAlertsV96||[]).filter(x=>!keySet.has(String(x?.event_key||'')))}catch(_e){}
      try{coachFeedV235=(coachFeedV235||[]).filter(x=>!keySet.has(String(x?.event_key||'')))}catch(_e){}
      try{coachFeedCache=(coachFeedCache||[]).filter(x=>!keySet.has(String(x?.event_key||'')))}catch(_e){}
      try{coachFeedLoadedAt=0}catch(_e){}
      try{if(groupKey)window.__fjzAlertGroupsOpenV333?.delete?.(groupKey)}catch(_e){}

      group.remove();

      try{
        if(typeof refreshCoachFeed==='function')await refreshCoachFeed();
      }catch(_e){}
      try{
        if(typeof hydrateCoachDashboardV80==='function')await hydrateCoachDashboardV80();
      }catch(_e){}
      try{renderCoachAlertsV96?.();updateCoachBellV96?.()}catch(_e){}
      try{renderCoachFocusV235?.();decorateCoachAlertsV235?.();renderCoachStudentsV235?.()}catch(_e){}
      try{window.renderCoachPriorityCenterV252?.()}catch(_e){}
      try{await window.__fjzRenderPrioritySmartV278?.()}catch(_e){}
      try{toast?.('✓ '+clean.length+' alerta'+(clean.length===1?'':'s')+' de '+name+' revisada'+(clean.length===1?'':'s'))}catch(_e){}
      return true;
    }catch(e){
      console.warn('TEAM FJZ V21.38 athlete alert curtain OK',e);
      try{
        coachFeedLoadedAt=0;
        if(typeof hydrateCoachDashboardV80==='function')await hydrateCoachDashboardV80();
        else if(typeof refreshCoachFeed==='function')await refreshCoachFeed();
      }catch(_e){}
      try{toast?.(typeof cloudErr==='function'?cloudErr(e):'No se pudieron guardar todas las alertas del alumno.')}catch(_e){}
      if(button){
        button.disabled=false;
        button.textContent=previousText;
      }
      return false;
    }finally{
      athleteGroupAckBusyV338.delete(busyKey);
    }
  };

"""
    body=body.replace(insert_anchor,bulk+insert_anchor,1)

    marker="""    coachNeverSeesKgRepAsLoadV337:true
  };"""
    replacement="""    coachNeverSeesKgRepAsLoadV337:true,
    athleteCurtainSingleCardV338:true,
    athleteCurtainShowsAllRowsV338:true,
    athleteCurtainBulkOkV338:true,
    athleteCurtainBulkCloudReadbackV338:true,
    individualAlertOkRemovedFromCurtainV338:true,
    oneRefreshAfterAthleteAckV338:true
  };"""
    if body.count(marker)!=1:
        raise RuntimeError("V21.38 marker anchor mismatch")
    body=body.replace(marker,replacement,1)
    return body

html=edit_script(html,"v331ProfessionalAlertGroupingRuntime",patch_v331)

css=r"""
/* TEAM FJZ · V21.38 ATHLETE ALERT CURTAIN */
.v338-athlete-alert-footer{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  padding:12px 15px 14px;
  border-top:1px solid rgba(255,255,255,.065);
  background:rgba(255,255,255,.012);
}
.v338-athlete-alert-footer>span{
  min-width:0;
  color:#969eaa;
  font-size:10px;
  line-height:1.4;
}
.v338-athlete-ok{
  flex:0 0 auto;
  min-width:108px!important;
  min-height:36px!important;
  border-color:rgba(59,213,138,.32)!important;
  background:rgba(59,213,138,.08)!important;
  color:#a5e8c3!important;
  font-weight:900!important;
}
.v338-athlete-ok:disabled{
  opacity:.62;
  cursor:wait;
}
@media(max-width:640px){
  .v338-athlete-alert-footer{
    display:grid;
    grid-template-columns:minmax(0,1fr);
    padding:12px;
  }
  .v338-athlete-ok{
    width:100%;
    min-width:0!important;
  }
}
"""
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V21.38 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-athlete-alert-curtain" content="21.38">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V21.38 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-athlete-alert-curtain" content="21.38"',
    "athleteCurtainSingleCardV338:true",
    "athleteCurtainShowsAllRowsV338:true",
    "athleteCurtainBulkOkV338:true",
    "athleteCurtainBulkCloudReadbackV338:true",
    "individualAlertOkRemovedFromCurtainV338:true",
    "oneRefreshAfterAthleteAckV338:true",
    "__fjzResolveAthleteAlertGroupV338",
    "✓ OK todas",
    "reviewCenterAthleteFirstV334:true",
    "groupedAlertCloudReadbackV336:true",
    "coachNeverSeesKgRepAsLoadV337:true",
    "firstReviewCardsDisabledV327:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.38 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.38 athlete alert curtain")
print("V21.38 BEFORE:",before)
print("V21.38 AFTER:",after)
