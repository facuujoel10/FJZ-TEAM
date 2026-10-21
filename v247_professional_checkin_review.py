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
    if not m: raise RuntimeError("V20.47 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body: raise RuntimeError("V20.47 no script change")
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-confirmed-checkin-success" content="20.46"',
    "coach_feedback","reviewed_at","weekly_checkins",
    "window.saveCheckinFeedback=async function"
]:
    if marker not in html:
        raise RuntimeError("V20.47 missing prerequisite: "+marker)

def patch_v170(body):
    anchor="  window.renderTrackingCoach=function(){"
    if body.count(anchor)!=1:
        raise RuntimeError("V20.47 coach tracking anchor mismatch")

    helper=r"""
  /* ---------- Professional check-in review V20.47 ---------- */
  function checkinDecisionLabelV247(v){
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

  function parseCheckinFeedbackV247(text){
    const raw=String(text||'').trim();
    const match=raw.match(/^Decisión:\s*(.+?)\nCómo seguimos:\s*([\s\S]*)$/i);
    if(!match)return {decision:'observe',nextStep:raw};
    const label=match[1].trim();
    const map={
      'Mantener plan':'maintain',
      'Progresar':'progress',
      'Ajustar entrenamiento':'adjust_training',
      'Ajustar nutrición':'adjust_nutrition',
      'Priorizar recuperación':'recovery',
      'Contactar alumno':'contact',
      'Seguir observando':'observe'
    };
    return {decision:map[label]||'observe',nextStep:match[2].trim()};
  }

  function formatCheckinFeedbackV247(decision,nextStep){
    return 'Decisión: '+checkinDecisionLabelV247(decision)+'\nCómo seguimos: '+String(nextStep||'').trim();
  }

  function checkinCoachReviewCardV247(c){
    const reviewed=!!c?.reviewed_at;
    const parsed=parseCheckinFeedbackV247(c?.coach_feedback||'');
    return '<div class="v247-checkin-review '+(reviewed?'reviewed':'pending')+'">'+
      '<div class="v247-checkin-review-copy">'+
        '<span>'+(reviewed?'REVISADO':'PENDIENTE DEL COACH')+'</span>'+
        '<strong>'+(reviewed?esc(checkinDecisionLabelV247(parsed.decision)):'Falta tu devolución')+'</strong>'+
        (reviewed&&parsed.nextStep?'<p>'+esc(parsed.nextStep)+'</p>':'')+
      '</div>'+
      '<button class="btn small '+(reviewed?'':'primary')+'" onclick="openCheckinReviewV247(\''+esc(c.id)+'\')">'+
        (reviewed?'Editar devolución':'Revisar check-in')+
      '</button>'+
    '</div>';
  }

  window.openCheckinReviewV247=function(id){
    const c=(trackingCache.checkins||[]).find(x=>x?.id===id);
    if(!c)return;
    const parsed=parseCheckinFeedbackV247(c.coach_feedback||'');

    showModal(
      '<div class="modal-head"><div><h3>Revisar check-in</h3><div class="muted tiny">Semana '+esc(c.week_start||'')+'</div></div>'+
      '<button class="btn small" type="button" aria-label="Cerrar" title="Cerrar" onclick="closeModal()">✕</button></div>'+
      '<div class="v247-review-form">'+
        '<div class="v247-checkin-source">'+
          '<div class="v247-source-kpis">'+
            '<span>Energía <b>'+esc(String(c.energy_level??'—'))+'/10</b></span>'+
            '<span>Recuperación <b>'+esc(String(c.recovery_level??'—'))+'/10</b></span>'+
            '<span>Estrés <b>'+esc(String(c.stress_level??'—'))+'/10</b></span>'+
            '<span>Adherencia <b>'+esc(String(c.adherence_level??'—'))+'/10</b></span>'+
          '</div>'+
          (c.notes?'<p><strong>Comentario:</strong> '+esc(c.notes)+'</p>':'<p class="muted">Sin comentario adicional.</p>')+
        '</div>'+
        '<label class="tiny muted">Decisión actual'+
          '<select id="v247Decision" class="input">'+
            '<option value="maintain">Mantener plan</option>'+
            '<option value="progress">Progresar</option>'+
            '<option value="adjust_training">Ajustar entrenamiento</option>'+
            '<option value="adjust_nutrition">Ajustar nutrición</option>'+
            '<option value="recovery">Priorizar recuperación</option>'+
            '<option value="contact">Contactar alumno</option>'+
            '<option value="observe">Seguir observando</option>'+
          '</select>'+
        '</label>'+
        '<label class="tiny muted">Cómo seguimos · visible para el alumno'+
          '<textarea id="v247NextStep" class="input" rows="4" maxlength="800" placeholder="Ej: mantenemos el plan, priorizá sueño esta semana y revisamos energía en el próximo check-in.">'+esc(parsed.nextStep||'')+'</textarea>'+
        '</label>'+
        '<button class="btn primary" style="width:100%" onclick="saveCheckinReviewV247(\''+esc(c.id)+'\')">Guardar devolución y marcar revisado</button>'+
      '</div>'
    );
    const sel=el('v247Decision');if(sel)sel.value=parsed.decision||'observe';
  };

  window.saveCheckinReviewV247=async function(id){
    const c=(trackingCache.checkins||[]).find(x=>x?.id===id);
    if(!c)return;
    const decision=String(el('v247Decision')?.value||'observe');
    const nextStep=String(el('v247NextStep')?.value||'').trim().slice(0,800);
    if(!nextStep){
      toast?.('Escribí cómo seguimos antes de guardar');
      return;
    }

    const value=formatCheckinFeedbackV247(decision,nextStep);
    const reviewedAt=new Date().toISOString();
    let data=null;

    if(window.__fjzStagingLocal?.enabled){
      data={id,coach_feedback:value,reviewed_at:reviewedAt};
    }else{
      if(!supabaseClient){toast?.('No hay conexión con la nube');return}
      const res=await supabaseClient
        .from('weekly_checkins')
        .update({coach_feedback:value,reviewed_at:reviewedAt})
        .eq('id',id)
        .select('id,coach_feedback,reviewed_at')
        .single();
      if(res.error){toast?.(cloudErr(res.error));return}
      data=res.data;
      if(!data?.id){toast?.('La nube no confirmó la devolución');return}
    }

    Object.assign(c,data);
    try{closeModal?.()}catch(_e){}
    renderTrackingCoachLoaded();

    showModal(
      '<div class="v207-save-state">'+
        '<div class="v207-save-icon success">✓</div>'+
        '<div class="v207-save-title">Check-in revisado con éxito</div>'+
        '<div class="v207-save-copy">La devolución quedó guardada. El alumno podrá ver cómo siguen.</div>'+
        '<div class="v207-save-actions"><button class="btn primary" onclick="closeModal()">Listo</button></div>'+
      '</div>'
    );
  };

"""
    body=body.replace(anchor,helper+anchor,1)

    old_controls="""      '<div class="form-grid" style="margin-top:10px"><textarea id="fb_'+esc(c.id)+'" class="input span2" rows="2" placeholder="Feedback para el alumno">'+esc(c.coach_feedback||'')+'</textarea><button class="btn small" onclick="saveCheckinFeedback(\''+esc(c.id)+'\')">Guardar feedback</button></div></div>'"""
    new_controls="""      checkinCoachReviewCardV247(c)+'</div>'"""
    if body.count(old_controls)!=1:
        raise RuntimeError("V20.47 coach check-in controls mismatch: "+str(body.count(old_controls)))
    body=body.replace(old_controls,new_controls,1)

    old_save="""  window.saveCheckinFeedback=async function(id){
    const value=(el('fb_'+id)?.value||'').trim();
    const {data,error}=await supabaseClient.from('weekly_checkins').update({coach_feedback:value,reviewed_at:new Date().toISOString()}).eq('id',id).select('id,coach_feedback,reviewed_at').single();
    if(error){toast(cloudErr(error));return}
    const row=(trackingCache.checkins||[]).find(x=>x.id===id);if(row&&data)Object.assign(row,data);toast('Feedback guardado');
  };"""
    new_save="""  window.saveCheckinFeedback=function(id){
    return window.openCheckinReviewV247(id);
  };"""
    if body.count(old_save)!=1:
        raise RuntimeError("V20.47 legacy saveCheckinFeedback mismatch")
    body=body.replace(old_save,new_save,1)

    marker_old="checkinRefreshFailureCannotMaskConfirmedSave:true"
    marker_new="checkinRefreshFailureCannotMaskConfirmedSave:true,professionalCheckinReview:true,checkinReviewCloudConfirmed:true"
    if body.count(marker_old)!=1:
        raise RuntimeError("V20.47 V170 marker mismatch")
    body=body.replace(marker_old,marker_new,1)

    # Final student-side check-in history authority.
    student_history=r"""
  window.renderStudentTrackingHistory=function(){
    const b=el('trackingStudentHistory');if(!b)return;
    const cs=(trackingCache.checkins||[]).slice(0,4),ms=(trackingCache.measurements||[]).slice(0,12);
    b.innerHTML='<div class="grid two"><div class="card"><div class="section-title"><div><h3>Últimos check-ins</h3><div class="muted tiny">Tu registro y la devolución del coach.</div></div></div>'+
      (cs.length?cs.map(c=>{
        const parsed=parseCheckinFeedbackV247(c.coach_feedback||'');
        return '<div class="track-row v247-student-checkin">'+
          '<div class="track-row-head"><div><strong>Semana '+esc(c.week_start)+'</strong><div class="muted tiny">'+
            (c.weight_kg?esc(String(c.weight_kg))+' kg · ':'')+'Adherencia '+esc(String(c.adherence_level))+'/10</div></div>'+
            '<span class="badge '+scoreClass(c.energy_level)+'">Energía '+esc(String(c.energy_level))+'</span></div>'+
          (c.notes?'<p class="muted tiny">'+esc(c.notes)+'</p>':'')+
          (c.reviewed_at&&c.coach_feedback
            ?'<div class="v247-student-reply"><div><span>DEVOLUCIÓN DEL COACH</span><strong>'+esc(checkinDecisionLabelV247(parsed.decision))+'</strong>'+
              '<p>'+esc(parsed.nextStep||c.coach_feedback)+'</p></div><span class="badge green">Revisado</span></div>'
            :'<div class="v247-student-waiting"><span class="badge amber">En revisión</span><p>Tu coach todavía no dejó una devolución para este check-in.</p></div>')+
        '</div>';
      }).join(''):'<div class="empty">Todavía no enviaste check-ins.</div>')+
      '</div><div class="card"><div class="section-title"><h3>Tendencia de peso</h3></div>'+simpleLineChart(ms,'weight_kg','Peso')+'</div></div>'+
      '<div class="card" style="margin-top:14px"><div class="section-title"><h3>Fotos de progreso</h3></div><div id="studentPhotoGrid"><div class="empty">Cargando fotos…</div></div></div>';
    renderPhotoGrid('studentPhotoGrid');
  };
  try{renderStudentTrackingHistory=window.renderStudentTrackingHistory}catch(_e){}

"""
    marker_pos=body.rfind("  window.__fjzRuntimeV170=")
    if marker_pos<0: raise RuntimeError("V20.47 V170 final marker location missing")
    body=body[:marker_pos]+student_history+body[marker_pos:]

    return body

html=edit_script(html,"v170ConsolidatedRuntime",patch_v170)

css=r"""
/* TEAM FJZ · V20.47 PROFESSIONAL CHECK-IN REVIEW */
.v247-checkin-review{
  display:flex;
  justify-content:space-between;
  gap:10px;
  align-items:center;
  margin-top:10px;
  padding:10px 11px;
  border:1px solid #2d3038;
  border-left:3px solid #f2bd55;
  border-radius:0 11px 11px 0;
  background:#0d0e12;
}
.v247-checkin-review.reviewed{border-left-color:#3bd58a}
.v247-checkin-review-copy{min-width:0}
.v247-checkin-review-copy>span{
  display:block;color:#8f939e;font-size:7px;font-weight:900;letter-spacing:.09em
}
.v247-checkin-review-copy>strong{
  display:block;margin-top:4px;color:#f2f3f5;font-size:11px
}
.v247-checkin-review-copy>p{
  margin:4px 0 0;color:#a7abb4;font-size:9px;line-height:1.45
}
.v247-review-form{display:grid;gap:12px}
.v247-review-form label{display:grid;gap:6px}
.v247-checkin-source{
  padding:10px 11px;border:1px solid #2d3038;border-radius:11px;background:#0d0e12
}
.v247-source-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px}
.v247-source-kpis span{
  padding:7px;border:1px solid #292c33;border-radius:8px;color:#8f939e;font-size:8px
}
.v247-source-kpis b{display:block;margin-top:3px;color:#f3f4f6;font-size:11px}
.v247-checkin-source>p{margin:9px 0 0;color:#adb1ba;font-size:9px;line-height:1.45}
.v247-student-reply{
  display:flex;justify-content:space-between;gap:10px;align-items:flex-start;
  margin-top:9px;padding:10px;border:1px solid rgba(59,213,138,.18);
  border-left:3px solid #3bd58a;border-radius:0 10px 10px 0;background:rgba(59,213,138,.04)
}
.v247-student-reply span:not(.badge){display:block;color:#79c99c;font-size:7px;font-weight:900;letter-spacing:.08em}
.v247-student-reply strong{display:block;margin-top:4px;color:#a9e9c6;font-size:10px}
.v247-student-reply p{margin:5px 0 0;color:#c0c4cc;font-size:9px;line-height:1.45}
.v247-student-waiting{
  margin-top:9px;padding:9px 10px;border:1px solid rgba(242,189,85,.16);
  border-radius:10px;background:rgba(242,189,85,.035)
}
.v247-student-waiting p{margin:5px 0 0;color:#a7a9b0;font-size:9px}
@media(max-width:620px){
  .v247-checkin-review{display:grid}
  .v247-checkin-review .btn{width:100%}
  .v247-source-kpis{grid-template-columns:1fr 1fr}
  .v247-student-reply{display:grid}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V20.47 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-checkin-review" content="20.47">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.47 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-checkin-review" content="20.47"',
    "openCheckinReviewV247","saveCheckinReviewV247",
    "checkinDecisionLabelV247","formatCheckinFeedbackV247",
    "Check-in revisado con éxito",
    "professionalCheckinReview:true","checkinReviewCloudConfirmed:true",
    "DEVOLUCIÓN DEL COACH","En revisión"
]:
    if marker not in html:
        raise RuntimeError("V20.47 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.47 professional check-in review")
print("V20.47 BEFORE:",before)
print("V20.47 AFTER:",after)
print("V20.47 coach decision/next-step + student check-in reply enabled")
