import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

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
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m: raise RuntimeError("V20.48 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body: raise RuntimeError("V20.48 no script change "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-checkin-review" content="20.47"',
    "checkinCoachReviewCardV247",
    "studentSmartActionHub:true",
    "coachReplyAcknowledgement:true"
]:
    if marker not in html:
        raise RuntimeError("V20.48 missing prerequisite: "+marker)

# Coach sees whether the student acknowledged the check-in reply.
def patch_v170(body):
    old="""  function checkinCoachReviewCardV247(c){
    const reviewed=!!c?.reviewed_at;
    const parsed=parseCheckinFeedbackV247(c?.coach_feedback||'');
    return '<div class="v247-checkin-review '+(reviewed?'reviewed':'pending')+'">'+"""
    new="""  function checkinCoachReviewCardV247(c){
    const reviewed=!!c?.reviewed_at;
    const parsed=parseCheckinFeedbackV247(c?.coach_feedback||'');
    const seen=student()?.checkinReplyAckV248?.[c?.id]||null;
    return '<div class="v247-checkin-review '+(reviewed?'reviewed':'pending')+'">'+"""
    if body.count(old)!=1:
        raise RuntimeError("V20.48 check-in card head mismatch")
    body=body.replace(old,new,1)

    old_copy="""        (reviewed&&parsed.nextStep?'<p>'+esc(parsed.nextStep)+'</p>':'')+
      '</div>'+"""
    new_copy="""        (reviewed&&parsed.nextStep?'<p>'+esc(parsed.nextStep)+'</p>':'')+
        (seen?'<div class="v248-checkin-seen">✓ Alumno lo vio · '+esc(new Date(seen).toLocaleString('es-AR'))+'</div>':'')+
      '</div>'+"""
    if body.count(old_copy)!=1:
        raise RuntimeError("V20.48 check-in seen insertion mismatch")
    body=body.replace(old_copy,new_copy,1)

    marker_old="checkinReviewCloudConfirmed:true"
    marker_new="checkinReviewCloudConfirmed:true,checkinReplyAcknowledgement:true"
    if body.count(marker_old)!=1:
        raise RuntimeError("V20.48 V170 marker mismatch")
    body=body.replace(marker_old,marker_new,1)
    return body

html=edit_script(html,"v170ConsolidatedRuntime",patch_v170)

def patch_v175(body):
    anchor="  /* ---------- Student action hub V20.45 ---------- */"
    if body.count(anchor)!=1:
        raise RuntimeError("V20.48 V175 action hub anchor mismatch")

    helpers=r"""
  /* ---------- Check-in reply acknowledgement V20.48 ---------- */
  function checkinDecisionLabelV248(v){
    const map={
      maintain:'Mantener plan',
      progress:'Progresar',
      adjust_training:'Ajustar entrenamiento',
      adjust_nutrition:'Ajustar nutrición',
      recovery:'Priorizar recuperación',
      contact:'Contactar alumno',
      observe:'Seguir observando'
    };
    return map[v]||'Seguimiento';
  }

  function parseCheckinFeedbackV248(text){
    const raw=String(text||'').trim();
    const match=raw.match(/^Decisión:\s*(.+?)\nCómo seguimos:\s*([\s\S]*)$/i);
    if(!match)return {decision:'observe',nextStep:raw};
    const reverse={
      'Mantener plan':'maintain',
      'Progresar':'progress',
      'Ajustar entrenamiento':'adjust_training',
      'Ajustar nutrición':'adjust_nutrition',
      'Priorizar recuperación':'recovery',
      'Contactar alumno':'contact',
      'Seguir observando':'observe'
    };
    return {decision:reverse[match[1].trim()]||'observe',nextStep:match[2].trim()};
  }

  function latestReviewedCheckinV248(){
    return (trackingCache?.checkins||[])
      .slice()
      .sort((a,b)=>String(b?.week_start||'').localeCompare(String(a?.week_start||'')))
      .find(x=>x?.reviewed_at&&x?.coach_feedback)||null;
  }

  function unreadCheckinReplyV248(s=student()){
    const row=latestReviewedCheckinV248();
    if(!row)return null;
    if(s?.checkinReplyAckV248?.[row.id])return null;
    return row;
  }

  window.acknowledgeCheckinReplyV248=function(id){
    const s=student();if(!s||!id)return;
    s.checkinReplyAckV248={...(s.checkinReplyAckV248||{}),[id]:new Date().toISOString()};
    saveState();
    toast?.('Devolución del check-in marcada como vista');
    render();
  };

  function hydrateStudentCheckinReplyV248(){
    if(!(mode==='student'&&studentTab==='home'))return;
    if(currentProfile?.role!=='student'&&!window.__fjzStagingLocal?.enabled)return;
    if(!cloudEnabled||!supabaseClient){
      injectStudentActionHubV245();
      return;
    }
    const athleteId=trackingAthleteId?.();
    if(athleteId&&trackingLoadedFor===athleteId){
      injectStudentActionHubV245();
      return;
    }
    loadTracking(false).then(()=>{
      if(mode==='student'&&studentTab==='home')injectStudentActionHubV245();
    }).catch(()=>{});
  }

"""
    body=body.replace(anchor,helpers+anchor,1)

    state_anchor="""  function actionHubStateV245(s){
    const reply=latestCoachReplySessionV245(s);"""
    state_repl="""  function actionHubStateV245(s){
    const checkinReply=unreadCheckinReplyV248(s);
    if(checkinReply){
      const parsed=parseCheckinFeedbackV248(checkinReply.coach_feedback||'');
      return {
        type:'checkin_reply',
        kicker:'DEVOLUCIÓN DEL CHECK-IN',
        title:checkinDecisionLabelV248(parsed.decision),
        copy:parsed.nextStep||'Tu coach revisó el último check-in.',
        badge:'Nueva',
        badgeClass:'green',
        checkin:checkinReply
      };
    }

    const reply=latestCoachReplySessionV245(s);"""
    if body.count(state_anchor)!=1:
        raise RuntimeError("V20.48 actionHub state anchor mismatch")
    body=body.replace(state_anchor,state_repl,1)

    action_anchor="""    if(a.type==='coach_reply'){
      actions="""
    action_repl="""    if(a.type==='checkin_reply'){
      actions=
        '<button class="btn" onclick="studentTab=\\'tracking\\';render()">Ver check-in</button>'+
        '<button class="btn primary" onclick="acknowledgeCheckinReplyV248(\\''+esc(a.checkin.id)+'\\')">Entendido</button>';
    }else if(a.type==='coach_reply'){
      actions="""
    if body.count(action_anchor)!=1:
        raise RuntimeError("V20.48 action button anchor mismatch")
    body=body.replace(action_anchor,action_repl,1)

    post_anchor="""      injectStudentActionHubV245();
      if(currentProfile?.role==='student'){"""
    post_repl="""      injectStudentActionHubV245();
      hydrateStudentCheckinReplyV248();
      if(currentProfile?.role==='student'){"""
    if body.count(post_anchor)!=1:
        raise RuntimeError("V20.48 postRender hydrate anchor mismatch")
    body=body.replace(post_anchor,post_repl,1)

    promise_anchor="""            injectStudentActionHubV245();
          }).catch(()=>{});"""
    promise_repl="""            injectStudentActionHubV245();
            hydrateStudentCheckinReplyV248();
          }).catch(()=>{});"""
    if body.count(promise_anchor)!=1:
        raise RuntimeError("V20.48 profile promise hydrate anchor mismatch")
    body=body.replace(promise_anchor,promise_repl,1)

    marker_old="""    coachReplyAcknowledgement:true
  };"""
    marker_new="""    coachReplyAcknowledgement:true,
    checkinReplyOnStudentHome:true,
    checkinReplyAcknowledgement:true
  };"""
    if body.count(marker_old)!=1:
        raise RuntimeError("V20.48 marker object mismatch")
    body=body.replace(marker_old,marker_new,1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

css=r"""
/* TEAM FJZ · V20.48 CHECK-IN REPLY ACKNOWLEDGEMENT */
.v245-action-hub.checkin_reply{
  border-color:rgba(59,213,138,.22);
  background:
    linear-gradient(145deg,rgba(59,213,138,.06),transparent 52%),
    var(--card);
}
.v248-checkin-seen{
  margin-top:6px;
  color:#8fdcaf;
  font-size:8px;
  font-weight:780;
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V20.48 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-checkin-reply-loop" content="20.48">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.48 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-checkin-reply-loop" content="20.48"',
    "acknowledgeCheckinReplyV248","unreadCheckinReplyV248",
    "hydrateStudentCheckinReplyV248","checkin_reply",
    "DEVOLUCIÓN DEL CHECK-IN","checkinReplyAckV248",
    "checkinReplyOnStudentHome:true","checkinReplyAcknowledgement:true",
    "Alumno lo vio"
]:
    if marker not in html:
        raise RuntimeError("V20.48 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.48 check-in reply loop")
print("V20.48 BEFORE:",before)
print("V20.48 AFTER:",after)
print("V20.48 coach check-in reply promoted to Student Home until acknowledged")
