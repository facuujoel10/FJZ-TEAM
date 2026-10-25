import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.39 COACH DECISION LOG
# =========================================================
# Adds decision + note to completed coach reviews and keeps a bounded
# per-student review history inside the existing snapshot JSON.
# No schema/backend/realtime/listener/timer changes.

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
        raise RuntimeError("V20.39 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.39 no script change")
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-coach-review-loop" content="20.38"',
    "reviewCurrentV237","renderReviewHubV237","markCoachReviewV237",
    "coachReviewV237","reviewBaselineStoredInSnapshot:true"
]:
    if marker not in html:
        raise RuntimeError("V20.39 missing prerequisite: "+marker)

def patch_v175(body):
    anchor="  function renderReviewHubV237(cur){"
    if body.count(anchor)!=1:
        raise RuntimeError("V20.39 renderReviewHub anchor mismatch")

    helpers=r"""
  /* ---------- Coach decision log V20.39 ---------- */
  function reviewHistoryV239(s=student()){
    return Array.isArray(s?.coachReviewHistoryV239)
      ?clone(s.coachReviewHistoryV239)
      :[];
  }

  function reviewDecisionLabelV239(v){
    const map={
      maintain:'Mantener plan',
      progress:'Progresar',
      adjust_routine:'Ajustar rutina',
      adjust_nutrition:'Ajustar nutrición',
      recovery:'Priorizar recuperación',
      contact:'Contactar alumno',
      followup:'Seguir observando'
    };
    return map[v]||'Seguimiento';
  }

  function reviewLastDecisionHtmlV239(last){
    if(!last)return '';
    const note=last.note
      ?'<p>'+esc(last.note)+'</p>'
      :'<p class="muted">Sin nota adicional.</p>';
    return '<div class="v239-last-decision">'+
      '<div><span>ÚLTIMA DECISIÓN</span><strong>'+esc(reviewDecisionLabelV239(last.decision))+'</strong>'+note+'</div>'+
      '<div class="v239-last-meta">'+esc(reviewDateV237(last.reviewedAt))+'</div>'+
    '</div>';
  }

  window.openCoachReviewDecisionV239=function(){
    const s=student();
    if(!s||!reviewCurrentV237||reviewCurrentV237.studentId!==s.id){
      toast?.('Esperá a que termine de cargar el resumen');
      return;
    }
    const last=reviewHistoryV239(s)[0]||null;
    showModal(
      '<div class="modal-head"><div><h3>Cerrar revisión</h3><div class="muted tiny">Dejá registrada la decisión principal de esta revisión.</div></div>'+
      '<button class="btn small" type="button" aria-label="Cerrar" title="Cerrar" onclick="closeModal()">✕</button></div>'+
      '<div class="v239-decision-form">'+
        '<label class="tiny muted">Decisión principal'+
          '<select id="v239Decision" class="input">'+
            '<option value="maintain">Mantener plan</option>'+
            '<option value="progress">Progresar</option>'+
            '<option value="adjust_routine">Ajustar rutina</option>'+
            '<option value="adjust_nutrition">Ajustar nutrición</option>'+
            '<option value="recovery">Priorizar recuperación</option>'+
            '<option value="contact">Contactar alumno</option>'+
            '<option value="followup">Seguir observando</option>'+
          '</select>'+
        '</label>'+
        '<label class="tiny muted">Nota del coach'+
          '<textarea id="v239DecisionNote" class="input" rows="4" maxlength="600" placeholder="Ej: mantener cargas esta semana y revisar sueño en el próximo check-in.">'+
          esc(last?.note||'')+
          '</textarea>'+
        '</label>'+
        '<div class="v239-decision-preview">'+
          '<span>Adherencia</span><strong>'+esc(String(reviewCurrentV237.adherence))+'%</strong>'+
          '<span>Estado</span><strong>'+esc(reviewCurrentV237.status||'—')+'</strong>'+
          '<span>Sesiones</span><strong>'+esc(String(reviewCurrentV237.sessionsCount||0))+'</strong>'+
        '</div>'+
        '<button class="btn primary" style="width:100%" onclick="saveCoachReviewDecisionV239()">Guardar y cerrar revisión</button>'+
      '</div>'
    );
  };

  window.saveCoachReviewDecisionV239=function(){
    const s=student();
    if(!s||!reviewCurrentV237||reviewCurrentV237.studentId!==s.id){
      toast?.('No se pudo guardar esta revisión');
      return;
    }

    const decision=el('v239Decision')?.value||'maintain';
    const note=(el('v239DecisionNote')?.value||'').trim().slice(0,600);
    const reviewedAt=new Date().toISOString();
    const snap=clone(reviewCurrentV237);
    snap.reviewedAt=reviewedAt;

    const entry={
      reviewedAt,
      decision,
      note,
      adherence:snap.adherence,
      status:snap.status,
      sessionsCount:snap.sessionsCount,
      lastWorkout:snap.lastWorkout,
      weight:snap.weight,
      energy:snap.energy,
      recovery:snap.recovery
    };

    const history=reviewHistoryV239(s);
    history.unshift(entry);
    s.coachReviewHistoryV239=history.slice(0,12);
    s.coachReviewV237=snap;

    saveState();
    closeModal?.();
    renderReviewHubV237(reviewCurrentV237);
    toast?.('Revisión y decisión guardadas');
  };

  window.showCoachReviewHistoryV239=function(){
    const s=student(),history=reviewHistoryV239(s);
    const rows=history.length
      ?history.map((x,i)=>
        '<div class="v239-history-item">'+
          '<div class="v239-history-head"><strong>'+esc(reviewDecisionLabelV239(x.decision))+'</strong><span>'+esc(reviewDateV237(x.reviewedAt))+'</span></div>'+
          '<div class="v239-history-metrics">'+
            '<span>Adherencia <b>'+esc(String(x.adherence??'—'))+'%</b></span>'+
            '<span>Estado <b>'+esc(x.status||'—')+'</b></span>'+
            '<span>Sesiones <b>'+esc(String(x.sessionsCount??'—'))+'</b></span>'+
          '</div>'+
          (x.note?'<p>'+esc(x.note)+'</p>':'<p class="muted">Sin nota.</p>')+
        '</div>'
      ).join('')
      :'<div class="empty">Todavía no hay revisiones cerradas con una decisión registrada.</div>';

    showModal(
      '<div class="modal-head"><div><h3>Historial de revisiones</h3><div class="muted tiny">'+esc(s?.name||'Alumno')+' · últimas '+Math.min(history.length,12)+' revisiones</div></div>'+
      '<button class="btn small" type="button" aria-label="Cerrar" title="Cerrar" onclick="closeModal()">✕</button></div>'+
      '<div class="v239-history-list">'+rows+'</div>'
    );
  };

"""
    body=body.replace(anchor,helpers+anchor,1)

    # Add history context in current review render.
    old_stamp="""    const stamp=prev?.reviewedAt?reviewDateV237(prev.reviewedAt):'Sin revisión previa';

    host.innerHTML="""
    new_stamp="""    const stamp=prev?.reviewedAt?reviewDateV237(prev.reviewedAt):'Sin revisión previa';
    const history=reviewHistoryV239(s);
    const lastDecision=history[0]||null;

    host.innerHTML="""
    if body.count(old_stamp)!=1:
        raise RuntimeError("V20.39 review stamp anchor mismatch")
    body=body.replace(old_stamp,new_stamp,1)

    # Show previous decision before current comparison.
    old_after_head="""      '</div>'+
      '<div class="v237-review-grid">'+"""
    new_after_head="""      '</div>'+
      reviewLastDecisionHtmlV239(lastDecision)+
      '<div class="v237-review-grid">'+"""
    if body.count(old_after_head)!=1:
        raise RuntimeError("V20.39 review head insertion mismatch")
    body=body.replace(old_after_head,new_after_head,1)

    # Replace direct close action with decision flow + history.
    old_footer="""      '<div class="v237-review-footer">'+
        '<div class="muted tiny">Al marcarla como completada, esta foto del estado queda como referencia para la próxima revisión.</div>'+
        '<button class="btn primary" onclick="markCoachReviewV237()">Marcar revisión completada</button>'+
      '</div>';"""
    new_footer="""      '<div class="v237-review-footer">'+
        '<div class="muted tiny">Al cerrar la revisión, guardamos esta foto del estado y la decisión principal como referencia.</div>'+
        '<div class="v239-review-actions">'+
          (history.length?'<button class="btn" onclick="showCoachReviewHistoryV239()">Historial · '+history.length+'</button>':'')+
          '<button class="btn primary" onclick="openCoachReviewDecisionV239()">Cerrar revisión</button>'+
        '</div>'+
      '</div>';"""
    if body.count(old_footer)!=1:
        raise RuntimeError("V20.39 review footer mismatch")
    body=body.replace(old_footer,new_footer,1)

    # Extend V17.5/V20.37 marker object.
    marker_old="""    coachReviewHub:true,
    reviewBaselineStoredInSnapshot:true
  };"""
    marker_new="""    coachReviewHub:true,
    reviewBaselineStoredInSnapshot:true,
    coachDecisionLog:true,
    reviewHistoryLimit:12
  };"""
    if body.count(marker_old)!=1:
        raise RuntimeError("V20.39 marker object mismatch")
    body=body.replace(marker_old,marker_new,1)

    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

css=r"""
/* TEAM FJZ · V20.39 COACH DECISION LOG */
.v239-last-decision{
  display:flex;
  justify-content:space-between;
  gap:14px;
  align-items:flex-start;
  margin:0 0 11px;
  padding:10px 11px;
  border:1px solid rgba(103,173,255,.20);
  border-left:3px solid var(--blue);
  border-radius:0 11px 11px 0;
  background:rgba(103,173,255,.045);
}
.v239-last-decision span{
  display:block;
  color:#82bdfd;
  font-size:8px;
  font-weight:900;
  letter-spacing:.09em;
}
.v239-last-decision strong{
  display:block;
  margin-top:4px;
  color:#eef4fb;
  font-size:11px;
  font-weight:880;
}
.v239-last-decision p{
  margin:5px 0 0;
  color:#a8b2bf;
  font-size:9px;
  line-height:1.45;
}
.v239-last-meta{
  flex:0 0 auto;
  color:#858a95;
  font-size:9px;
  white-space:nowrap;
}
.v239-review-actions{
  display:flex;
  gap:7px;
  flex-wrap:wrap;
  justify-content:flex-end;
}
.v239-decision-form{
  display:grid;
  gap:12px;
}
.v239-decision-form label{
  display:grid;
  gap:6px;
}
.v239-decision-form textarea{
  resize:vertical;
  line-height:1.5;
}
.v239-decision-preview{
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:7px;
}
.v239-decision-preview span,
.v239-decision-preview strong{
  padding:8px 9px;
  border:1px solid #2c3038;
  background:#0d0e12;
}
.v239-decision-preview span{
  border-radius:10px 10px 0 0;
  color:#8f939e;
  font-size:8px;
  font-weight:800;
  text-transform:uppercase;
}
.v239-decision-preview strong{
  margin-top:-8px;
  border-top:0;
  border-radius:0 0 10px 10px;
  color:#f4f5f7;
  font-size:12px;
}
.v239-history-list{
  display:grid;
  gap:9px;
  max-height:min(64vh,620px);
  overflow:auto;
}
.v239-history-item{
  padding:11px 12px;
  border:1px solid #2c3038;
  border-radius:12px;
  background:#0d0e12;
}
.v239-history-head{
  display:flex;
  justify-content:space-between;
  gap:10px;
}
.v239-history-head strong{
  color:#f4f5f7;
  font-size:12px;
}
.v239-history-head span{
  color:#8f939e;
  font-size:9px;
}
.v239-history-metrics{
  display:flex;
  gap:6px;
  flex-wrap:wrap;
  margin-top:8px;
}
.v239-history-metrics span{
  padding:4px 7px;
  border:1px solid #292c33;
  border-radius:999px;
  color:#9296a1;
  font-size:8px;
}
.v239-history-metrics b{
  color:#e4e6ea;
}
.v239-history-item p{
  margin:8px 0 0;
  color:#a3a7b1;
  font-size:9px;
  line-height:1.45;
}
@media(max-width:620px){
  .v239-last-decision{
    display:grid;
  }
  .v239-last-meta{
    white-space:normal;
  }
  .v239-review-actions{
    width:100%;
    display:grid;
    grid-template-columns:1fr;
  }
  .v239-review-actions .btn{
    width:100%;
  }
  .v239-decision-preview{
    grid-template-columns:1fr;
  }
  .v239-decision-preview span,
  .v239-decision-preview strong{
    border-radius:10px;
    margin-top:0;
    border-top:1px solid #2c3038;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.39 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-coach-decision-log" content="20.39">\n</head>',1)

after=metrics(html)
for key in (
    "styles","renders","channels","timeouts","rafs","listeners",
    "mutation_observers","performance_observers"
):
    if after[key]!=before[key]:
        raise RuntimeError("V20.39 topology changed "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-coach-decision-log" content="20.39"',
    "coachReviewHistoryV239","reviewDecisionLabelV239",
    "openCoachReviewDecisionV239","saveCoachReviewDecisionV239",
    "showCoachReviewHistoryV239","Cerrar revisión",
    "Historial de revisiones","reviewHistoryLimit:12",
    "coachDecisionLog:true","coachReviewV237",
    "v122FollowupPaymentsRuntime"
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.39 missing decision-log marker: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.39 coach decision log")
print("V20.39 BEFORE:",before)
print("V20.39 AFTER:",after)
print("V20.39 decisions + bounded review history added; topology unchanged")
