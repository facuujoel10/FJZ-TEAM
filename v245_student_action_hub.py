import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.45 STUDENT ACTION HUB + COACH-REPLY ACK
# =========================================================
# Smart student Home next-action + acknowledgement of coach session response.
# Persists inside session JSON. Reuses V17.5 post-render; no new render wrapper,
# listener, timer, realtime channel or backend schema.

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
    pat=re.compile(
        r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',
        re.S|re.I
    )
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.45 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.45 no script change")
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-unified-session-history" content="20.44"',
    "injectStudentCoachReplyV242",
    "injectStudentNextStepV243",
    "sessionFeedbackCoachReview:true",
    "studentNextStepCard:true"
]:
    if marker not in html:
        raise RuntimeError("V20.45 missing prerequisite: "+marker)

def patch_v175(body):
    anchor="  /* ---------- Session feedback response V20.42 ---------- */"
    if body.count(anchor)!=1:
        raise RuntimeError("V20.45 insertion anchor mismatch")

    helpers=r"""
  /* ---------- Student action hub V20.45 ---------- */
  function sessionsThisWeekV245(s){
    const now=new Date();
    const dow=(now.getDay()+6)%7;
    const start=new Date(now.getFullYear(),now.getMonth(),now.getDate()-dow,0,0,0,0).getTime();
    return (s?.sessions||[]).filter(x=>(Date.parse(x?.date||0)||0)>=start).length;
  }

  function latestSessionV245(s=student()){
    return (s?.sessions||[]).slice().sort(
      (a,b)=>(Date.parse(b?.date||0)||0)-(Date.parse(a?.date||0)||0)
    )[0]||null;
  }

  function latestCoachReplySessionV245(s=student()){
    return (s?.sessions||[]).slice().sort(
      (a,b)=>(Date.parse(b?.date||0)||0)-(Date.parse(a?.date||0)||0)
    ).find(x=>x?.sessionFeedback?.coachReview?.status==='reviewed')||null;
  }

  function nextWorkoutV245(s){
    const days=s?.days||[];
    if(!days.length)return null;
    const last=latestSessionV245(s);
    if(!last)return {day:days[0],index:0};
    const idx=days.findIndex(d=>d.id===last.dayId);
    const next=idx>=0?(idx+1)%days.length:0;
    return {day:days[next],index:next};
  }

  window.acknowledgeCoachSessionV245=function(sessionId){
    const s=student();
    const ss=(s?.sessions||[]).find(x=>x?.id===sessionId);
    const review=ss?.sessionFeedback?.coachReview;
    if(!s||!ss||!review)return;

    if(!review.studentAcknowledgedAt){
      review.studentAcknowledgedAt=new Date().toISOString();
      saveState();
      toast?.('Devolución marcada como vista');
    }
    render();
  };

  function actionHubStateV245(s){
    const reply=latestCoachReplySessionV245(s);
    const review=reply?.sessionFeedback?.coachReview;
    if(reply&&review&&!review.studentAcknowledgedAt){
      return {
        type:'coach_reply',
        kicker:'DEVOLUCIÓN NUEVA',
        title:'Tu coach revisó tu sesión',
        copy:review.nextStep||'Hay una nueva indicación sobre cómo seguir.',
        badge:'Nueva',
        badgeClass:'green',
        session:reply
      };
    }

    const latest=latestSessionV245(s);
    if(latest?.sessionFeedback?.status==='pending'){
      return {
        type:'feedback_pending',
        kicker:'SEGUIMIENTO',
        title:'Tu feedback está en revisión',
        copy:'Tu coach ya puede ver lo que reportaste en la última sesión. Mientras tanto podés seguir tu progreso o completar el check-in.',
        badge:'En revisión',
        badgeClass:'amber',
        session:latest
      };
    }

    if((s?.checkin||'Pendiente')==='Pendiente'){
      return {
        type:'checkin',
        kicker:'SIGUIENTE ACCIÓN',
        title:'Completá tu check-in',
        copy:'Sumá sueño, energía, estrés, adherencia y recuperación para que tu coach tenga el contexto completo.',
        badge:'Pendiente',
        badgeClass:'amber'
      };
    }

    const next=nextWorkoutV245(s);
    if(next?.day){
      return {
        type:'workout',
        kicker:'SIGUIENTE ENTRENAMIENTO',
        title:next.day.name||'Entrenamiento',
        copy:(next.day.muscles||'Rutina del coach')+' · '+(next.day.exercises?.length||0)+' ejercicios.',
        badge:'Listo',
        badgeClass:'blue',
        next
      };
    }

    return {
      type:'progress',
      kicker:'TU PROGRESO',
      title:'Revisá tu evolución',
      copy:'Tus registros quedan conectados para comparar las próximas semanas.',
      badge:'Progreso',
      badgeClass:'blue'
    };
  }

  function injectStudentActionHubV245(){
    if(!(mode==='student'&&studentTab==='home'))return;
    const view=el('view');if(!view)return;

    el('v243StudentNextStep')?.remove();
    el('v245StudentActionHub')?.remove();

    const s=student?.();if(!s)return;
    const a=actionHubStateV245(s);
    const done=sessionsThisWeekV245(s);
    const planned=Math.max(1,Number(s.plannedPerWeek)||s.days?.length||1);

    let actions='';
    if(a.type==='coach_reply'){
      actions=
        '<button class="btn" onclick="studentTab=\'history\';render()">Ver sesión</button>'+
        '<button class="btn primary" onclick="acknowledgeCoachSessionV245(\''+esc(a.session.id)+'\')">Entendido</button>';
    }else if(a.type==='feedback_pending'){
      actions=
        '<button class="btn" onclick="studentTab=\'tracking\';render()">Check-in</button>'+
        '<button class="btn primary" onclick="studentTab=\'progress\';render()">Ver progreso</button>';
    }else if(a.type==='checkin'){
      actions=
        '<button class="btn" onclick="studentTab=\'progress\';render()">Ver progreso</button>'+
        '<button class="btn primary" onclick="studentTab=\'tracking\';render()">Completar check-in</button>';
    }else if(a.type==='workout'){
      actions=
        '<button class="btn" onclick="studentTab=\'progress\';render()">Ver progreso</button>'+
        '<button class="btn primary" onclick="startWorkout('+Number(a.next.index)+')">Empezar entrenamiento</button>';
    }else{
      actions='<button class="btn primary" onclick="studentTab=\'progress\';render()">Ver progreso</button>';
    }

    const card=document.createElement('section');
    card.id='v245StudentActionHub';
    card.className='card v245-action-hub '+esc(a.type);
    card.innerHTML=
      '<div class="v245-action-top">'+
        '<div><div class="v225-section-kicker">'+esc(a.kicker)+'</div><h3>'+esc(a.title)+'</h3>'+
        '<p>'+esc(a.copy)+'</p></div>'+
        '<span class="badge '+esc(a.badgeClass)+'">'+esc(a.badge)+'</span>'+
      '</div>'+
      '<div class="v245-week">'+
        '<div><strong>'+done+'/'+planned+'</strong><span>Sesiones esta semana</span></div>'+
        '<div><strong>'+adherence(s)+'%</strong><span>Adherencia 7 días</span></div>'+
        '<div><strong>'+esc(statusFor(s))+'</strong><span>Estado</span></div>'+
      '</div>'+
      '<div class="v245-action-buttons">'+actions+'</div>';

    const anchor=el('v242StudentCoachReply')||
      el('v115StudentProfileCard')||
      el('v175StudentProfilePlaceholder')||
      view.querySelector('.hero');
    if(anchor)anchor.insertAdjacentElement('afterend',card);
    else view.prepend(card);
  }

"""
    body=body.replace(anchor,helpers+anchor,1)

    # Coach feedback card: show student acknowledgement.
    coach_text_old="""    const coachText=review
      ?'<div class="v242-coach-response"><strong>'+esc(sessionDecisionLabelV242(review.decision))+'</strong>'+
        (review.nextStep?'<p>'+esc(review.nextStep)+'</p>':'')+
        (review.internalNote?'<div class="muted micro">Nota interna: '+esc(review.internalNote)+'</div>':'')+
      '</div>'
      :'';"""
    coach_text_new="""    const coachText=review
      ?'<div class="v242-coach-response"><strong>'+esc(sessionDecisionLabelV242(review.decision))+'</strong>'+
        (review.nextStep?'<p>'+esc(review.nextStep)+'</p>':'')+
        (review.internalNote?'<div class="muted micro">Nota interna: '+esc(review.internalNote)+'</div>':'')+
        (review.studentAcknowledgedAt?'<div class="v245-seen">✓ Alumno lo vio · '+esc(reviewDateV237(review.studentAcknowledgedAt))+'</div>':'')+
      '</div>'
      :'';"""
    if body.count(coach_text_old)!=1:
        raise RuntimeError("V20.45 coach response card anchor mismatch")
    body=body.replace(coach_text_old,coach_text_new,1)

    # Student reply card adds acknowledgement status/action.
    reply_actions_old="""      '<div class="v242-student-reply-actions">'+
        '<button class="btn" onclick="studentTab=\\'history\\';render()">Ver historial</button>'+
        '<button class="btn primary" onclick="studentTab=\\'progress\\';render()">Ver progreso</button>'+
      '</div>';"""
    reply_actions_new="""      '<div class="v242-student-reply-actions">'+
        '<button class="btn" onclick="studentTab=\\'history\\';render()">Ver historial</button>'+
        (review.studentAcknowledgedAt
          ?'<button class="btn primary" onclick="studentTab=\\'progress\\';render()">Ver progreso</button>'
          :'<button class="btn primary" onclick="acknowledgeCoachSessionV245(\\''+esc(ss.id)+'\\')">Entendido</button>')+
      '</div>';"""
    if body.count(reply_actions_old)!=1:
        raise RuntimeError("V20.45 student reply actions mismatch")
    body=body.replace(reply_actions_old,reply_actions_new,1)

    # Existing V20.43 call remains but V20.45 replaces that card after it.
    post_anchor="""      injectStudentCoachReplyV242();
      injectStudentNextStepV243();"""
    post_repl="""      injectStudentCoachReplyV242();
      injectStudentNextStepV243();
      injectStudentActionHubV245();"""
    if body.count(post_anchor)!=1:
        raise RuntimeError("V20.45 postRender action hub anchor mismatch")
    body=body.replace(post_anchor,post_repl,1)

    promise_anchor="""            injectStudentCoachReplyV242();
            injectStudentNextStepV243();"""
    promise_repl="""            injectStudentCoachReplyV242();
            injectStudentNextStepV243();
            injectStudentActionHubV245();"""
    if body.count(promise_anchor)!=1:
        raise RuntimeError("V20.45 profile-promise action hub anchor mismatch")
    body=body.replace(promise_anchor,promise_repl,1)

    marker_old="""    studentNextStepCard:true
  };"""
    marker_new="""    studentNextStepCard:true,
    studentSmartActionHub:true,
    coachReplyAcknowledgement:true
  };"""
    if body.count(marker_old)!=1:
        raise RuntimeError("V20.45 marker object mismatch")
    body=body.replace(marker_old,marker_new,1)

    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

css=r"""
/* TEAM FJZ · V20.45 STUDENT ACTION HUB */
.v245-action-hub{
  border-color:#30343c;
  background:
    linear-gradient(145deg,rgba(103,173,255,.042),transparent 52%),
    var(--card);
}
.v245-action-hub.coach_reply{
  border-color:rgba(59,213,138,.20);
  background:
    linear-gradient(145deg,rgba(59,213,138,.052),transparent 52%),
    var(--card);
}
.v245-action-hub.feedback_pending,
.v245-action-hub.checkin{
  border-color:rgba(242,189,85,.20);
  background:
    linear-gradient(145deg,rgba(242,189,85,.045),transparent 52%),
    var(--card);
}
.v245-action-top{
  display:flex;
  justify-content:space-between;
  gap:12px;
  align-items:flex-start;
}
.v245-action-top h3{
  margin:4px 0 0;
  color:#f5f6f8;
  font-size:16px;
  font-weight:920;
  letter-spacing:-.02em;
}
.v245-action-top p{
  margin:6px 0 0;
  max-width:680px;
  color:#a5a9b2;
  font-size:10px;
  line-height:1.5;
}
.v245-week{
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:7px;
  margin-top:12px;
}
.v245-week>div{
  padding:9px 10px;
  border:1px solid #2b2e36;
  border-radius:10px;
  background:#0d0e12;
}
.v245-week strong{
  display:block;
  color:#f3f4f6;
  font-size:14px;
  font-weight:900;
}
.v245-week span{
  display:block;
  margin-top:4px;
  color:#878c97;
  font-size:8px;
  line-height:1.3;
  font-weight:750;
}
.v245-action-buttons{
  display:flex;
  justify-content:flex-end;
  gap:7px;
  margin-top:11px;
}
.v245-seen{
  margin-top:7px;
  color:#8fdcaf;
  font-size:8px;
  font-weight:780;
}
@media(max-width:560px){
  .v245-action-top{
    display:grid;
  }
  .v245-week{
    grid-template-columns:1fr 1fr;
  }
  .v245-week>div:last-child{
    grid-column:1/-1;
  }
  .v245-action-buttons{
    display:grid;
    grid-template-columns:1fr 1fr;
  }
  .v245-action-buttons .btn{
    width:100%;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.45 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-student-action-hub" content="20.45">\n</head>',1)

after=metrics(html)
for key in (
    "styles","renders","channels","timeouts","rafs","listeners",
    "mutation_observers","performance_observers"
):
    if after[key]!=before[key]:
        raise RuntimeError("V20.45 topology changed "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-student-action-hub" content="20.45"',
    "injectStudentActionHubV245",
    "acknowledgeCoachSessionV245",
    "studentAcknowledgedAt",
    "studentSmartActionHub:true",
    "coachReplyAcknowledgement:true",
    "Sesiones esta semana",
    "Completar check-in",
    "Empezar entrenamiento",
    "Alumno lo vio"
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.45 missing action-hub marker: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.45 student smart action hub")
print("V20.45 BEFORE:",before)
print("V20.45 AFTER:",after)
print("V20.45 smart next action + coach reply acknowledgement added")
