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
    if not m: raise RuntimeError("V20.50 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body: raise RuntimeError("V20.50 no script change")
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-progress-pulse" content="20.49"',
    "reviewCurrentV237","renderReviewHubV237",
    "renderSessionFeedbackCoachV242","recentSessionsV175",
    "agendaSummaryV175","nutritionSummaryV175"
]:
    if marker not in html:
        raise RuntimeError("V20.50 missing prerequisite: "+marker)

def patch_v175(body):
    anchor="  async function hydrateSummaryV175(){"
    if body.count(anchor)!=1:
        raise RuntimeError("V20.50 hydrate anchor mismatch")

    helpers=r"""
  /* ---------- Coach Weekly Brief V20.50 ---------- */
  function weeklyBriefV250(s,latest,agenda,nutrition,pendingExercise){
    const sessions=recentSessionsV175(s,7);
    const sets=sessions.reduce((a,x)=>a+(Number(x?.summary?.totalSets)||0),0);
    const progressed=sessions.reduce((a,x)=>a+(Number(x?.summary?.up)||0),0);
    const sessionFeedback=Number(window.__fjzPendingSessionFeedbackCountV242?.(s)||0);
    const checkinNeedsReview=!!(latest&&!latest.reviewed_at);
    const recoveryLow=latest?.recovery_level!=null&&Number(latest.recovery_level)<=4;
    const energyLow=latest?.energy_level!=null&&Number(latest.energy_level)<=4;

    let next={
      tone:'good',
      title:'Seguimiento al día',
      copy:'No aparece una intervención prioritaria con los datos actuales.',
      tab:'progress',
      label:'Ver progreso'
    };

    if(sessionFeedback>0){
      next={
        tone:'warn',
        title:'Revisar feedback de sesión',
        copy:sessionFeedback+' feedback de entrenamiento '+(sessionFeedback===1?'espera':'esperan')+' tu devolución.',
        tab:'summary',
        label:'Revisar feedback'
      };
    }else if(checkinNeedsReview){
      next={
        tone:'warn',
        title:'Revisar último check-in',
        copy:'El alumno envió un check-in que todavía no tiene una devolución tuya.',
        tab:'tracking',
        label:'Abrir check-in'
      };
    }else if(recoveryLow||energyLow){
      next={
        tone:'warn',
        title:'Mirar recuperación',
        copy:'Energía o recuperación están bajas en el último check-in. Conviene revisar contexto antes de ajustar el plan.',
        tab:'tracking',
        label:'Abrir seguimiento'
      };
    }else if(Number(agenda?.overdue||0)>0){
      next={
        tone:'warn',
        title:'Resolver agenda vencida',
        copy:'Hay '+Number(agenda.overdue)+' recordatorio'+(Number(agenda.overdue)===1?'':'s')+' vencido'+(Number(agenda.overdue)===1?'':'s')+'.',
        tab:'agenda',
        label:'Abrir agenda'
      };
    }else if(Array.isArray(pendingExercise)&&pendingExercise.length){
      next={
        tone:'warn',
        title:'Responder comentarios',
        copy:'Hay '+pendingExercise.length+' comentario'+(pendingExercise.length===1?'':'s')+' de ejercicios pendiente'+(pendingExercise.length===1?'':'s')+'.',
        tab:'routine',
        label:'Abrir rutina'
      };
    }else if(!nutrition?.active){
      next={
        tone:'info',
        title:'Revisar nutrición',
        copy:'No figura un plan nutricional activo para este alumno.',
        tab:'nutrition',
        label:'Abrir nutrición'
      };
    }else if(!sessions.length){
      next={
        tone:'info',
        title:'Sin entrenamientos esta semana',
        copy:'No hay sesiones registradas en los últimos 7 días. Revisá disponibilidad o planificación.',
        tab:'routine',
        label:'Abrir rutina'
      };
    }

    return {
      sessions:sessions.length,
      sets,
      progressed,
      adherence:Number(adherence(s)||0),
      sessionFeedback,
      checkinNeedsReview,
      next
    };
  }

  function renderCoachWeeklyBriefV250(s,latest,agenda,nutrition,pendingExercise){
    const host=el('v250CoachWeeklyBrief');if(!host)return;
    const b=weeklyBriefV250(s,latest,agenda,nutrition,pendingExercise);
    host.innerHTML=
      '<div class="v175-360-section-head v250-head"><div><h4>Brief semanal</h4>'+
      '<p>Una lectura operativa de los últimos 7 días para decidir qué hacer ahora.</p></div>'+
      '<span class="badge '+(b.next.tone==='warn'?'amber':b.next.tone==='good'?'green':'blue')+'">7 días</span></div>'+
      '<div class="v250-grid">'+
        '<div><strong>'+b.sessions+'</strong><span>Entrenos</span></div>'+
        '<div><strong>'+b.sets+'</strong><span>Series</span></div>'+
        '<div><strong>'+b.progressed+'</strong><span>Progresiones</span></div>'+
        '<div><strong>'+b.adherence+'%</strong><span>Adherencia</span></div>'+
      '</div>'+
      '<div class="v250-action '+esc(b.next.tone)+'">'+
        '<div><span>PRÓXIMA ACCIÓN</span><strong>'+esc(b.next.title)+'</strong><p>'+esc(b.next.copy)+'</p></div>'+
        '<button class="btn small '+(b.next.tone==='warn'?'primary':'')+'" onclick="openCoachWeeklyActionV250(\''+esc(b.next.tab)+'\')">'+esc(b.next.label)+'</button>'+
      '</div>';
  }

  window.openCoachWeeklyActionV250=function(tab){
    coachStudentTab=tab||'summary';
    render();
  };

"""
    body=body.replace(anchor,helpers+anchor,1)

    hydrate_old="""    reviewCurrentV237=reviewSnapshotV237(s,latest,weight,pending,agenda,nutrition);
    renderReviewHubV237(reviewCurrentV237);
    renderSessionFeedbackCoachV242();

    if(el('v175Metrics'))"""
    hydrate_new="""    reviewCurrentV237=reviewSnapshotV237(s,latest,weight,pending,agenda,nutrition);
    renderReviewHubV237(reviewCurrentV237);
    renderSessionFeedbackCoachV242();
    renderCoachWeeklyBriefV250(s,latest,agenda,nutrition,pending);

    if(el('v175Metrics'))"""
    if body.count(hydrate_old)!=1:
        raise RuntimeError("V20.50 hydrate insertion mismatch")
    body=body.replace(hydrate_old,hydrate_new,1)

    review_section="""      '<div class="v175-360-section v237-review-section" id="v237ReviewHub"><div class="empty">Preparando comparación con tu última revisión…</div></div>'+
"""
    brief_section="""      '<div class="v175-360-section v250-weekly-brief" id="v250CoachWeeklyBrief"><div class="empty">Preparando brief semanal…</div></div>'+
"""
    if body.count(review_section)!=1:
        raise RuntimeError("V20.50 review-section insertion mismatch")
    body=body.replace(review_section,brief_section+review_section,1)

    marker_old="""    progressPulseAvoidsBodyJudgement:true
  };"""
    marker_new="""    progressPulseAvoidsBodyJudgement:true,
    coachWeeklyBrief:true,
    coachWeeklyBriefUsesExistingData:true
  };"""
    if body.count(marker_old)!=1:
        raise RuntimeError("V20.50 marker mismatch")
    body=body.replace(marker_old,marker_new,1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

css=r"""
/* TEAM FJZ · V20.50 COACH WEEKLY BRIEF */
.v250-weekly-brief{
  border-color:rgba(103,173,255,.18);
  background:
    linear-gradient(145deg,rgba(103,173,255,.04),transparent 50%),
    #101116;
}
.v250-head{align-items:flex-start}
.v250-grid{
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:7px;
}
.v250-grid>div{
  padding:10px;
  border:1px solid #2b2f37;
  border-radius:10px;
  background:#0d0e12;
}
.v250-grid strong{
  display:block;
  color:#f5f6f8;
  font-size:18px;
  line-height:1;
  font-weight:920;
}
.v250-grid span{
  display:block;
  margin-top:5px;
  color:#898e99;
  font-size:8px;
  font-weight:780;
  text-transform:uppercase;
  letter-spacing:.05em;
}
.v250-action{
  display:grid;
  grid-template-columns:minmax(0,1fr) auto;
  gap:12px;
  align-items:center;
  margin-top:9px;
  padding:10px 11px;
  border:1px solid #2c3038;
  border-left:3px solid #67adff;
  border-radius:0 11px 11px 0;
  background:#0d0e12;
}
.v250-action.warn{border-left-color:#f2bd55}
.v250-action.good{border-left-color:#3bd58a}
.v250-action>div>span{
  display:block;
  color:#858a95;
  font-size:7px;
  font-weight:900;
  letter-spacing:.10em;
}
.v250-action strong{
  display:block;
  margin-top:4px;
  color:#f2f3f5;
  font-size:11px;
  font-weight:880;
}
.v250-action p{
  margin:4px 0 0;
  color:#a2a6b0;
  font-size:9px;
  line-height:1.45;
}
@media(max-width:620px){
  .v250-grid{grid-template-columns:1fr 1fr}
  .v250-action{grid-template-columns:1fr}
  .v250-action .btn{width:100%}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V20.50 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-coach-weekly-brief" content="20.50">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.50 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-coach-weekly-brief" content="20.50"',
    "weeklyBriefV250","renderCoachWeeklyBriefV250","openCoachWeeklyActionV250",
    "Brief semanal","PRÓXIMA ACCIÓN",
    "coachWeeklyBrief:true","coachWeeklyBriefUsesExistingData:true"
]:
    if marker not in html:
        raise RuntimeError("V20.50 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.50 coach weekly brief")
print("V20.50 BEFORE:",before)
print("V20.50 AFTER:",after)
print("V20.50 selected-student weekly brief added using already-loaded data")
