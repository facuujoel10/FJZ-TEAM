import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.37 COACH REVIEW HUB
# =========================================================
# Adds a persistent coach-review baseline inside the existing student JSON
# snapshot. No schema/backend/realtime/timer/listener changes.

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
        raise RuntimeError("V20.37 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.37 no script change")
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-coach-work-queue" content="20.36"',
    "single360:true","richer360:true","assistantExecutiveSummary:true",
    "window.renderCoachSummary=function()","async function hydrateSummaryV175()",
    "function syncCoachState()","data:s"
]:
    if marker not in html:
        raise RuntimeError("V20.37 missing prerequisite: "+marker)

def patch_v175(body):
    anchor="  async function hydrateSummaryV175(){"
    if body.count(anchor)!=1:
        raise RuntimeError("V20.37 hydrate anchor mismatch")

    helpers=r"""
  /* ---------- Coach review hub V20.37 ---------- */
  let reviewCurrentV237=null;

  function reviewDateV237(v){
    if(!v)return 'Sin revisión previa';
    try{
      return new Date(v).toLocaleString('es-AR',{
        day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'
      });
    }catch(_e){return fmtDate(v)}
  }

  function reviewSnapshotV237(s,latest,weight,pending,agenda,nutrition){
    return {
      reviewedAt:new Date().toISOString(),
      studentId:s?.id||null,
      adherence:Number(adherence(s)||0),
      sessionsCount:Array.isArray(s?.sessions)?s.sessions.length:0,
      lastWorkout:s?.lastWorkout||null,
      status:statusFor(s),
      checkinDate:latest?.week_start||latest?.created_at||null,
      energy:latest?.energy_level??null,
      recovery:latest?.recovery_level??null,
      stress:latest?.stress_level??null,
      weight:weight??null,
      pendingFeedback:Array.isArray(pending)?pending.length:0,
      agendaTotal:Number(agenda?.total||0),
      agendaOverdue:Number(agenda?.overdue||0),
      nutritionActive:!!nutrition?.active
    };
  }

  function reviewDeltaV237(a,b,suffix=''){
    if(a==null||b==null)return null;
    const d=Number(a)-Number(b);
    if(!Number.isFinite(d)||d===0)return null;
    const sign=d>0?'+':'';
    const val=Math.abs(d)<10?round1(d):Math.round(d);
    return sign+val+suffix;
  }

  function reviewChangeItemsV237(cur,prev){
    if(!prev)return [
      {tone:'info',title:'Primera revisión',body:'Todavía no hay una referencia anterior. Marcá esta revisión como completada para empezar a comparar cambios.'}
    ];

    const out=[];
    const newSessions=Math.max(0,(cur.sessionsCount||0)-(prev.sessionsCount||0));
    if(newSessions)out.push({
      tone:'good',title:newSessions+' entreno'+(newSessions===1?'':'s')+' nuevo'+(newSessions===1?'':'s'),
      body:'Desde la última revisión se guardaron '+newSessions+' sesiones.'
    });

    const adh=reviewDeltaV237(cur.adherence,prev.adherence,'%');
    if(adh)out.push({
      tone:Number(cur.adherence)>=Number(prev.adherence)?'good':'warn',
      title:'Adherencia '+adh,
      body:'Ahora está en '+cur.adherence+'%.'
    });

    if(cur.status!==prev.status)out.push({
      tone:cur.status==='Revisar'?'warn':'good',
      title:'Estado: '+cur.status,
      body:'Antes figuraba como '+(prev.status||'sin estado')+'.'
    });

    if(cur.checkinDate&&cur.checkinDate!==prev.checkinDate)out.push({
      tone:'info',title:'Nuevo check-in',
      body:'Hay una actualización de seguimiento desde tu última revisión.'
    });

    const w=reviewDeltaV237(cur.weight,prev.weight,' kg');
    if(w)out.push({
      tone:'info',title:'Peso '+w,
      body:'Cambio respecto a la última referencia del coach.'
    });

    if(Number(cur.pendingFeedback)>Number(prev.pendingFeedback||0))out.push({
      tone:'warn',title:'Nuevos comentarios',
      body:'Hay '+cur.pendingFeedback+' comentario'+(cur.pendingFeedback===1?'':'s')+' pendiente'+(cur.pendingFeedback===1?'':'s')+'.'
    });

    if(Number(cur.agendaOverdue)>Number(prev.agendaOverdue||0))out.push({
      tone:'warn',title:'Agenda vencida',
      body:'Aparecieron tareas o chequeos vencidos desde la última revisión.'
    });

    if(!out.length)out.push({
      tone:'good',title:'Sin cambios importantes',
      body:'No aparecen variaciones relevantes frente a tu última revisión.'
    });

    return out.slice(0,5);
  }

  function reviewDecisionItemsV237(cur){
    const out=[];
    if(cur.status==='Revisar')out.push({
      tone:'warn',title:'Revisar entrenamiento',
      body:'El estado actual indica que conviene revisar progresión, técnica o carga.',
      tab:'progress',label:'Abrir progreso'
    });
    if(Number(cur.adherence)<70)out.push({
      tone:'warn',title:'Adherencia baja',
      body:'Está en '+cur.adherence+'%. Revisá barreras antes de aumentar exigencia.',
      tab:'summary',label:'Ver resumen'
    });
    if(cur.energy!=null&&Number(cur.energy)<=4||cur.recovery!=null&&Number(cur.recovery)<=4)out.push({
      tone:'warn',title:'Recuperación comprometida',
      body:'Energía o recuperación están bajas. Revisá el último check-in.',
      tab:'tracking',label:'Abrir check-in'
    });
    if(Number(cur.pendingFeedback)>0)out.push({
      tone:'warn',title:'Feedback pendiente',
      body:'Hay '+cur.pendingFeedback+' comentario'+(cur.pendingFeedback===1?'':'s')+' para revisar.',
      tab:'routine',label:'Abrir rutina'
    });
    if(Number(cur.agendaOverdue)>0)out.push({
      tone:'warn',title:'Agenda vencida',
      body:'Hay '+cur.agendaOverdue+' elemento'+(cur.agendaOverdue===1?'':'s')+' vencido'+(cur.agendaOverdue===1?'':'s')+'.',
      tab:'agenda',label:'Abrir agenda'
    });
    if(!cur.nutritionActive)out.push({
      tone:'info',title:'Sin plan nutricional activo',
      body:'Si corresponde a este alumno, revisá la sección de nutrición.',
      tab:'nutrition',label:'Abrir nutrición'
    });
    if(!out.length)out.push({
      tone:'good',title:'Sin decisiones urgentes',
      body:'La información disponible no muestra una intervención prioritaria ahora.',
      tab:'summary',label:'Mantener seguimiento'
    });
    return out.slice(0,4);
  }

  function reviewItemHtmlV237(x){
    const action=x.tab
      ?'<button class="btn small" onclick="coachStudentTab=\''+esc(x.tab)+'\';render()">'+esc(x.label||'Abrir')+'</button>'
      :'';
    return '<div class="v237-review-item '+esc(x.tone||'info')+'">'+
      '<div><strong>'+esc(x.title)+'</strong><p>'+esc(x.body||'')+'</p></div>'+action+
    '</div>';
  }

  function renderReviewHubV237(cur){
    const host=el('v237ReviewHub');if(!host)return;
    const s=student(),prev=s?.coachReviewV237||null;
    const changes=reviewChangeItemsV237(cur,prev);
    const decisions=reviewDecisionItemsV237(cur);
    const stamp=prev?.reviewedAt?reviewDateV237(prev.reviewedAt):'Sin revisión previa';

    host.innerHTML=
      '<div class="v237-review-head">'+
        '<div><div class="v225-section-kicker">REVISIÓN DEL COACH</div><h4>Desde tu última revisión</h4>'+
        '<p>Compará cambios y cerrá esta revisión cuando ya hayas tomado las decisiones necesarias.</p></div>'+
        '<div class="v237-review-meta"><span>Última revisión</span><strong>'+esc(stamp)+'</strong></div>'+
      '</div>'+
      '<div class="v237-review-grid">'+
        '<div class="v237-review-col"><div class="v237-review-label">QUÉ CAMBIÓ</div>'+
          changes.map(reviewItemHtmlV237).join('')+
        '</div>'+
        '<div class="v237-review-col"><div class="v237-review-label">QUÉ DECIDIR</div>'+
          decisions.map(reviewItemHtmlV237).join('')+
        '</div>'+
      '</div>'+
      '<div class="v237-review-footer">'+
        '<div class="muted tiny">Al marcarla como completada, esta foto del estado queda como referencia para la próxima revisión.</div>'+
        '<button class="btn primary" onclick="markCoachReviewV237()">Marcar revisión completada</button>'+
      '</div>';
  }

  window.markCoachReviewV237=function(){
    const s=student();
    if(!s||!reviewCurrentV237||reviewCurrentV237.studentId!==s.id){
      toast?.('Esperá a que termine de cargar el resumen');
      return;
    }
    s.coachReviewV237=clone(reviewCurrentV237);
    s.coachReviewV237.reviewedAt=new Date().toISOString();
    saveState();
    renderReviewHubV237(reviewCurrentV237);
    toast?.('Revisión del alumno guardada');
  };

"""
    body=body.replace(anchor,helpers+anchor,1)

    # Hook current snapshot after all connected data is available.
    snapshot_anchor="""    const pending=pendingFeedbackV175();

    if(el('v175Metrics'))"""
    snapshot_repl="""    const pending=pendingFeedbackV175();

    reviewCurrentV237=reviewSnapshotV237(s,latest,weight,pending,agenda,nutrition);
    renderReviewHubV237(reviewCurrentV237);

    if(el('v175Metrics'))"""
    if body.count(snapshot_anchor)!=1:
        raise RuntimeError("V20.37 hydrate snapshot anchor mismatch")
    body=body.replace(snapshot_anchor,snapshot_repl,1)

    # Insert review hub before connected status.
    status_anchor="""      '<div class="v175-360-section"><div class="v175-360-section-head"><div><h4>Estado conectado</h4><p>Señales rápidas del check-in, nutrición, feedback y Agenda.</p></div></div><div id="v175Status" class="v175-status-row">'+chipV175('Cargando datos…')+'</div></div>'+"""
    review_section="""      '<div class="v175-360-section v237-review-section" id="v237ReviewHub"><div class="empty">Preparando comparación con tu última revisión…</div></div>'+
"""
    if body.count(status_anchor)!=1:
        raise RuntimeError("V20.37 summary status anchor mismatch")
    body=body.replace(status_anchor,review_section+status_anchor,1)

    marker_anchor="""    cacheFirst:true
  };"""
    marker_repl="""    cacheFirst:true,
    coachReviewHub:true,
    reviewBaselineStoredInSnapshot:true
  };"""
    if body.count(marker_anchor)!=1:
        raise RuntimeError("V20.37 V175 marker anchor mismatch")
    body=body.replace(marker_anchor,marker_repl,1)

    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

css=r"""
/* TEAM FJZ · V20.37 COACH REVIEW HUB */
.v237-review-section{
  border-color:rgba(255,38,57,.20);
  background:
    linear-gradient(145deg,rgba(255,38,57,.045),transparent 48%),
    #101116;
}
.v237-review-head{
  display:flex;
  justify-content:space-between;
  gap:16px;
  align-items:flex-start;
  margin-bottom:12px;
}
.v237-review-head h4{
  margin:4px 0 0;
  color:#f6f7f9;
  font-size:15px;
  font-weight:900;
  letter-spacing:-.018em;
}
.v237-review-head p{
  margin:5px 0 0;
  color:#969aa5;
  font-size:10px;
  line-height:1.45;
  max-width:620px;
}
.v237-review-meta{
  flex:0 0 auto;
  min-width:150px;
  padding:9px 10px;
  border:1px solid #2f333b;
  border-radius:11px;
  background:#0d0e12;
}
.v237-review-meta span{
  display:block;
  color:#858a95;
  font-size:8px;
  font-weight:800;
  letter-spacing:.06em;
  text-transform:uppercase;
}
.v237-review-meta strong{
  display:block;
  margin-top:5px;
  color:#e9eaed;
  font-size:10px;
  font-weight:850;
}
.v237-review-grid{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:10px;
}
.v237-review-col{
  min-width:0;
  display:grid;
  gap:7px;
  align-content:start;
}
.v237-review-label{
  color:#ff7985;
  font-size:8px;
  font-weight:900;
  letter-spacing:.11em;
}
.v237-review-item{
  display:grid;
  grid-template-columns:minmax(0,1fr) auto;
  gap:9px;
  align-items:center;
  padding:10px 11px;
  border:1px solid #2c3038;
  border-left-width:3px;
  border-radius:11px;
  background:#0d0e12;
}
.v237-review-item.good{border-left-color:#3bd58a}
.v237-review-item.warn{border-left-color:#f2bd55}
.v237-review-item.info{border-left-color:#67adff}
.v237-review-item strong{
  display:block;
  color:#f3f4f6;
  font-size:11px;
  font-weight:860;
}
.v237-review-item p{
  margin:4px 0 0;
  color:#969aa5;
  font-size:9px;
  line-height:1.42;
}
.v237-review-item .btn{
  min-height:29px;
  white-space:nowrap;
}
.v237-review-footer{
  display:flex;
  justify-content:space-between;
  gap:12px;
  align-items:center;
  margin-top:12px;
  padding-top:11px;
  border-top:1px solid #292c33;
}
.v237-review-footer>.muted{
  max-width:650px;
}
@media(max-width:760px){
  .v237-review-head{
    display:grid;
  }
  .v237-review-meta{
    width:100%;
  }
  .v237-review-grid{
    grid-template-columns:1fr;
  }
  .v237-review-footer{
    display:grid;
  }
  .v237-review-footer .btn{
    width:100%;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.37 stylesheet surface changed")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-coach-review-hub" content="20.37">\n</head>',1)

after=metrics(html)
for key in (
    "styles","renders","channels","timeouts","rafs","listeners",
    "mutation_observers","performance_observers"
):
    if after[key]!=before[key]:
        raise RuntimeError("V20.37 topology changed "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-coach-review-hub" content="20.37"',
    "coachReviewV237",
    "reviewSnapshotV237",
    "reviewChangeItemsV237",
    "reviewDecisionItemsV237",
    "markCoachReviewV237",
    "v237ReviewHub",
    "Marcar revisión completada",
    "reviewBaselineStoredInSnapshot:true",
    "coachReviewHub:true",
    "athlete_snapshots",
    "data:s",
    "v122FollowupPaymentsRuntime"
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.37 missing review marker: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.37 coach review hub")
print("V20.37 BEFORE:",before)
print("V20.37 AFTER:",after)
print("V20.37 persistent review baseline + changes/decisions added; topology unchanged")
