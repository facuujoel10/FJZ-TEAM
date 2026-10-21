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
    }

def edit_script(doc,script_id,transform):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m: raise RuntimeError("V20.53 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body: raise RuntimeError("V20.53 no script change")
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-coach-priority-center" content="20.52"',
    "studentSmartActionHub:true","checkinReplyOnStudentHome:true",
    "injectStudentActionHubV245","latestSessionV245","latestReviewedCheckinV248"
]:
    if marker not in html:
        raise RuntimeError("V20.53 missing prerequisite: "+marker)

def patch_v175(body):
    anchor="  /* ---------- Student action hub V20.45 ---------- */"
    if body.count(anchor)!=1:
        raise RuntimeError("V20.53 insertion anchor mismatch")

    helpers=r"""
  /* ---------- Student Week Flow V20.53 ---------- */
  function weekFlowStatusV253(s){
    const latest=latestSessionV245(s);
    const fb=latest?.sessionFeedback||null;
    const latestCheckin=latestReviewedCheckinV248()||
      (trackingCache?.checkins||[]).slice().sort(
        (a,b)=>String(b?.week_start||'').localeCompare(String(a?.week_start||''))
      )[0]||null;

    let workout={
      state:latest?'done':'pending',
      title:'Entrenamiento',
      text:latest?((latest.dayName||'Sesión')+' · '+fmtDate(latest.date)):'Todavía no hay una sesión registrada'
    };

    let feedback={
      state:'neutral',
      title:'Feedback',
      text:'Sin feedback reciente'
    };
    if(fb?.status==='pending')feedback={state:'wait',title:'Feedback',text:'Enviado · esperando revisión'};
    else if(fb?.status==='reviewed')feedback={state:'done',title:'Feedback',text:'Revisado por tu coach'};
    else if(fb?.status==='clear')feedback={state:'done',title:'Feedback',text:'Sesión sin dificultades reportadas'};
    else if(latest)feedback={state:'neutral',title:'Feedback',text:'Sin comentario de cierre'};

    let checkin={
      state:(s?.checkin||'Pendiente')==='Pendiente'?'pending':'done',
      title:'Check-in',
      text:(s?.checkin||'Pendiente')==='Pendiente'?'Pendiente':'Enviado'
    };
    if(latestCheckin){
      checkin={
        state:latestCheckin.reviewed_at?'done':'wait',
        title:'Check-in',
        text:latestCheckin.reviewed_at
          ?'Revisado · semana '+(latestCheckin.week_start||'')
          :'Enviado · esperando devolución'
      };
    }

    const sessionReply=latestCoachReplySessionV245(s);
    const sessionReview=sessionReply?.sessionFeedback?.coachReview||null;
    const checkinReply=latestReviewedCheckinV248();
    const checkinSeen=checkinReply?s?.checkinReplyAckV248?.[checkinReply.id]:null;

    let coach={state:'neutral',title:'Coach',text:'Sin devolución nueva'};
    if(sessionReview&&!sessionReview.studentAcknowledgedAt){
      coach={state:'new',title:'Coach',text:'Tenés una devolución nueva de sesión'};
    }else if(checkinReply&&!checkinSeen){
      coach={state:'new',title:'Coach',text:'Tenés una devolución nueva de check-in'};
    }else if(sessionReview?.studentAcknowledgedAt||checkinSeen){
      coach={state:'done',title:'Coach',text:'Última indicación vista'};
    }else if(fb?.status==='pending'||(latestCheckin&&!latestCheckin.reviewed_at)){
      coach={state:'wait',title:'Coach',text:'Revisión en proceso'};
    }

    return {workout,feedback,checkin,coach};
  }

  function weekFlowItemV253(item,index){
    const icon=item.state==='done'?'✓':item.state==='new'?'!':item.state==='wait'?'…':index+1;
    return '<div class="v253-flow-item '+esc(item.state)+'">'+
      '<span class="v253-flow-icon">'+esc(String(icon))+'</span>'+
      '<div><strong>'+esc(item.title)+'</strong><p>'+esc(item.text)+'</p></div>'+
    '</div>';
  }

  function injectStudentWeekFlowV253(){
    if(!(mode==='student'&&studentTab==='home'))return;
    const view=el('view');if(!view)return;
    el('v253StudentWeekFlow')?.remove();

    const s=student?.();if(!s)return;
    const f=weekFlowStatusV253(s);
    const rows=[f.workout,f.feedback,f.checkin,f.coach];

    const card=document.createElement('section');
    card.id='v253StudentWeekFlow';
    card.className='card v253-week-flow';
    card.innerHTML=
      '<div class="section-title v253-flow-head">'+
        '<div><div class="v225-section-kicker">MI SEMANA</div><h3>Entrenamiento y seguimiento</h3>'+
        '<div class="muted tiny">Todo el circuito en una sola vista.</div></div>'+
        '<span class="badge blue">4 pasos</span>'+
      '</div>'+
      '<div class="v253-flow-grid">'+rows.map(weekFlowItemV253).join('')+'</div>'+
      '<div class="v253-flow-actions">'+
        '<button class="btn" onclick="studentTab=\\'history\\';render()">Sesiones</button>'+
        '<button class="btn" onclick="studentTab=\\'tracking\\';render()">Check-in</button>'+
        '<button class="btn primary" onclick="studentTab=\\'progress\\';render()">Progreso</button>'+
      '</div>';

    const anchor=el('v245StudentActionHub')||
      el('v242StudentCoachReply')||
      el('v115StudentProfileCard')||
      el('v175StudentProfilePlaceholder')||
      view.querySelector('.hero');
    if(anchor)anchor.insertAdjacentElement('afterend',card);
    else view.prepend(card);
  }

"""
    body=body.replace(anchor,helpers+anchor,1)

    post_old="""      injectStudentActionHubV245();
      hydrateStudentCheckinReplyV248();"""
    post_new="""      injectStudentActionHubV245();
      injectStudentWeekFlowV253();
      hydrateStudentCheckinReplyV248();"""
    if body.count(post_old)!=1:
        raise RuntimeError("V20.53 postRender anchor mismatch")
    body=body.replace(post_old,post_new,1)

    promise_old="""            injectStudentActionHubV245();
            hydrateStudentCheckinReplyV248();"""
    promise_new="""            injectStudentActionHubV245();
            injectStudentWeekFlowV253();
            hydrateStudentCheckinReplyV248();"""
    if body.count(promise_old)!=1:
        raise RuntimeError("V20.53 profile promise anchor mismatch")
    body=body.replace(promise_old,promise_new,1)

    # When tracking finishes asynchronously, refresh both smart cards.
    async_old="""      if(mode==='student'&&studentTab==='home')injectStudentActionHubV245();"""
    async_new="""      if(mode==='student'&&studentTab==='home'){
        injectStudentActionHubV245();
        injectStudentWeekFlowV253();
      }"""
    if body.count(async_old)!=1:
        raise RuntimeError("V20.53 async tracking anchor mismatch")
    body=body.replace(async_old,async_new,1)

    marker_old="""    coachWeeklyBriefUsesExistingData:true
  };"""
    marker_new="""    coachWeeklyBriefUsesExistingData:true,
    studentWeekFlow:true,
    studentFollowupUnified:true
  };"""
    if body.count(marker_old)!=1:
        raise RuntimeError("V20.53 marker mismatch: "+str(body.count(marker_old)))
    body=body.replace(marker_old,marker_new,1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

css=r"""
/* TEAM FJZ · V20.53 STUDENT WEEK FLOW */
.v253-week-flow{
  border-color:#30343c;
}
.v253-flow-head{align-items:flex-start}
.v253-flow-grid{
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:7px;
}
.v253-flow-item{
  position:relative;
  min-width:0;
  padding:10px;
  border:1px solid #2c3038;
  border-top:3px solid #555b66;
  border-radius:0 10px 10px 10px;
  background:#0d0e12;
}
.v253-flow-item.done{border-top-color:#3bd58a}
.v253-flow-item.new{border-top-color:#ff4657}
.v253-flow-item.wait{border-top-color:#f2bd55}
.v253-flow-item.pending{border-top-color:#f2bd55}
.v253-flow-icon{
  width:25px;height:25px;display:grid;place-items:center;
  margin-bottom:8px;border:1px solid #343842;border-radius:8px;
  color:#e8eaee;font-size:9px;font-weight:900;background:#14161b
}
.v253-flow-item.done .v253-flow-icon{color:#9ce4bb}
.v253-flow-item.new .v253-flow-icon{color:#ff9aa4}
.v253-flow-item.wait .v253-flow-icon,.v253-flow-item.pending .v253-flow-icon{color:#efc978}
.v253-flow-item strong{
  display:block;color:#f1f2f4;font-size:10px;font-weight:880
}
.v253-flow-item p{
  margin:4px 0 0;color:#8f949f;font-size:8px;line-height:1.4;overflow-wrap:anywhere
}
.v253-flow-actions{
  display:flex;
  justify-content:flex-end;
  gap:7px;
  margin-top:10px;
}
@media(max-width:760px){
  .v253-flow-grid{grid-template-columns:1fr 1fr}
}
@media(max-width:480px){
  .v253-flow-grid{grid-template-columns:1fr}
  .v253-flow-actions{display:grid;grid-template-columns:1fr 1fr}
  .v253-flow-actions .btn:last-child{grid-column:1/-1}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V20.53 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-student-week-flow" content="20.53">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.53 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-student-week-flow" content="20.53"',
    "weekFlowStatusV253","injectStudentWeekFlowV253",
    "MI SEMANA","Entrenamiento y seguimiento",
    "studentWeekFlow:true","studentFollowupUnified:true"
]:
    if marker not in html:
        raise RuntimeError("V20.53 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.53 student week flow")
print("V20.53 BEFORE:",before)
print("V20.53 AFTER:",after)
print("V20.53 workout/feedback/check-in/coach follow-up unified on Student Home")
