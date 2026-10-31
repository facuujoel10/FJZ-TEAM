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
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V21.35 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V21.35 no changes in "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-smart-alerts-progress" content="20.78"',
    'meta name="fjz-review-center-athlete-accordion" content="21.34"',
    'id="v278SmartAlertsProgressRuntime"',
    'id="v331ProfessionalAlertGroupingRuntime"',
    "firstReviewCardsDisabledV327:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.35 prerequisite missing "+marker)

def patch_v278(body):
    replacements=[
        (
            "        'Subió la carga manteniendo repeticiones y un esfuerzo comparable.',",
            "        'La mejor carga pasó de '+fmtV278(prev.bestLoad,1)+' a '+fmtV278(cur.bestLoad,1)+' kg ('+(loadDiff>0?'+':'')+fmtV278(loadDiff,1)+' kg), con repeticiones y RIR comparables.',"
        ),
        (
            "        'Continuar la progresión actual si la ejecución sigue sólida.'",
            "        'Progreso de carga consistente. Mantener el ejercicio y volver a progresar solo si técnica, repeticiones y RIR se sostienen.'"
        ),
        (
            "        'Más repeticiones con una carga y un RIR comparables.',",
            "        'Las repeticiones máximas registradas pasaron de '+fmtV278(prev.bestReps,0)+' a '+fmtV278(cur.bestReps,0)+' con una carga y un RIR comparables.',"
        ),
        (
            "        'Mantener el criterio de progresión del ejercicio.'",
            "        'Progreso de repeticiones consistente. Mantener la carga hasta completar el rango previsto antes del próximo aumento.'"
        ),
        (
            "        repsFalling?(fmtV278(repsDiff,0)+' reps'):(fmtV278(volPct,0)+'% volumen'),",
            "        repsFalling?(fmtV278(repsDiff,0)+' reps'):(fmtV278(cur.volume-prev.volume,0)+' kg·rep'),"
        ),
        (
            "      const blockPct=pctV278(recVol,oldVol);",
            "      const blockPct=pctV278(recVol,oldVol);\n      const blockDiff=(Number.isFinite(recVol)&&Number.isFinite(oldVol))?recVol-oldVol:null;"
        ),
        (
            "          row.name+' · volumen +'+fmtV278(blockPct,0)+'%',",
            "          row.name+' · volumen '+(blockDiff>0?'+':'')+fmtV278(blockDiff,0)+' kg·rep',"
        ),
        (
            "          'El volumen medio de las últimas dos sesiones superó al bloque anterior.',",
            "          'El volumen medio pasó de '+fmtV278(oldVol,0)+' a '+fmtV278(recVol,0)+' kg·rep en las dos sesiones más recientes.',"
        ),
        (
            "          '+'+fmtV278(blockPct,0)+'%',",
            "          (blockDiff>0?'+':'')+fmtV278(blockDiff,0)+' kg·rep',"
        ),
        (
            "          'Confirmar que la mejora también sea compatible con RIR y recuperación.',",
            "          'La carga total de trabajo aumentó. Confirmar que la mejora venga acompañada de técnica estable, RIR razonable y buena recuperación.',"
        ),
        (
            "          row.name+' · volumen '+fmtV278(blockPct,0)+'%',",
            "          row.name+' · volumen '+fmtV278(blockDiff,0)+' kg·rep',"
        ),
        (
            "          'El volumen medio reciente cayó frente al bloque anterior.',",
            "          'El volumen medio pasó de '+fmtV278(oldVol,0)+' a '+fmtV278(recVol,0)+' kg·rep frente al bloque anterior.',"
        ),
        (
            "          fmtV278(blockPct,0)+'%',",
            "          fmtV278(blockDiff,0)+' kg·rep',"
        ),
        (
            "          'Revisar contexto, RIR, técnica y recuperación antes de cambiar el plan.',",
            "          'Hay una caída concreta del trabajo total. Revisar RIR, técnica, recuperación y contexto antes de modificar el plan.',"
        ),
        (
            "smart_meta:{type_label:'Adherencia · Positivo',previous:planned+' planificados',current:done+' realizados',delta:Math.round(done/planned*100)+'%',period:'Últimos 7 días',suggestion:'Mantener la estructura si recuperación y rendimiento acompañan.',action_label:'Ver resumen'}",
            "smart_meta:{type_label:'Adherencia · Positivo',previous:planned+' planificados',current:done+' realizados',delta:'Frecuencia cumplida',period:'Últimos 7 días',suggestion:'La frecuencia programada se cumplió. Mantener la estructura si recuperación y rendimiento acompañan.',action_label:'Ver resumen'}"
        ),
        (
            "smart_meta:{type_label:'Nutrición · Adherencia',previous:'7 días',current:days+' registrados',delta:Math.round(days/7*100)+'%',period:'Últimos 7 días',suggestion:'Usar el registro como contexto, sin depender de un único día.',action_label:'Ver nutrición'}",
            "smart_meta:{type_label:'Nutrición · Adherencia',previous:'Semana completa',current:days+'/7 días registrados',delta:days+' días con registro',period:'Últimos 7 días',suggestion:'El registro fue consistente. Usarlo como contexto junto con peso, rendimiento y adherencia general.',action_label:'Ver nutrición'}"
        ),
        (
            "smart_meta:{type_label:'Nutrición · Revisar',previous:'7 días',current:days+' registrados',delta:Math.round(days/7*100)+'%',period:'Últimos 7 días',suggestion:'Confirmar si el alumno está usando el registro antes de sacar conclusiones.',action_label:'Ver nutrición'}",
            "smart_meta:{type_label:'Nutrición · Revisar',previous:'Semana completa',current:days+'/7 días registrados',delta:'Registro insuficiente',period:'Últimos 7 días',suggestion:'Hay pocos registros para interpretar adherencia. Confirmar si el alumno está usando el registro antes de sacar conclusiones.',action_label:'Ver nutrición'}"
        ),
    ]
    for old,new in replacements:
        if old not in body:
            raise RuntimeError("V21.35 V278 anchor missing: "+old[:90])
        body=body.replace(old,new,1)

    old_filter="""    const filtered=(base||[]).filter(x=>{
      const generic=/progreso detectado|progresi[oó]n detectada/i.test(String(x?.title||'')+' '+String(x?.body||''));
      return !(generic&&specificAthletes.has(x?.athlete_id));
    });"""
    new_filter="""    const filtered=(base||[]).filter(x=>{
      const copy=String(x?.title||'')+' '+String(x?.body||'');
      const generic=/progreso detectado|progresi[oó]n detectada/i.test(copy);
      const percentageOnlyProgress=/\\b\\d+(?:[.,]\\d+)?\\s*%/.test(copy)&&/(?:progres|mejor|rendimiento|volumen|carga|repet|aument|subi)/i.test(copy);
      if(percentageOnlyProgress&&!x?.smart_meta)return false;
      return !(generic&&specificAthletes.has(x?.athlete_id));
    });"""
    if old_filter not in body:
        raise RuntimeError("V21.35 V278 generic filter anchor missing")
    body=body.replace(old_filter,new_filter,1)

    marker="""    athleteIntelligenceSummary:true,
    canonicalPriorityCenterSmartAlerts:true,"""
    replacement="""    athleteIntelligenceSummary:true,
    concreteProgressCopyV335:true,
    percentageOnlyProgressSuppressedV335:true,
    loadAlertsUseKgDeltaV335:true,
    volumeAlertsUseAbsoluteWorkV335:true,
    adherenceNutritionUseCountsV335:true,
    professionalCoachSuggestionsV335:true,
    canonicalPriorityCenterSmartAlerts:true,"""
    if marker not in body:
        raise RuntimeError("V21.35 V278 marker anchor missing")
    body=body.replace(marker,replacement,1)
    return body

html=edit_script(html,"v278SmartAlertsProgressRuntime",patch_v278)

def patch_v331(body):
    old="""    const prev=sm.previous,current=sm.current,delta=sm.delta,period=sm.period;"""
    new="""    const prev=sm.previous,current=sm.current,rawDelta=sm.delta,period=sm.period;
    const delta=(x?.kind==='progression'&&/%/.test(String(rawDelta||'')))?'':rawDelta;"""
    if old not in body:
        raise RuntimeError("V21.35 V331 comparison anchor missing")
    body=body.replace(old,new,1)

    start=body.find("  function rowHtml(x,{dismiss=false}={}){")
    end=body.find("\n  const alertGroupsOpenV333=",start)
    if start<0 or end<0:
        raise RuntimeError("V21.35 V331 rowHtml bounds missing")
    replacement=r"""  function factV335(label,value){
    if(value==null||String(value).trim()==='')return '';
    return '<span class="v335-progress-fact"><small>'+safe(label)+'</small><b>'+safe(value)+'</b></span>';
  }
  function rowHtml(x,{dismiss=false}={}){
    const sm=x?.smart_meta||{};
    const metric=mainMetric(x),compare=comparison(x);
    const isProgress=x?.kind==='progression'&&!!x?.smart_meta;
    const rawDelta=String(sm.delta??'');
    const delta=isProgress&&/%/.test(rawDelta)?'':rawDelta;
    const facts=isProgress
      ?'<div class="v335-progress-facts">'+
        factV335('Anterior',sm.previous)+
        factV335('Actual',sm.current)+
        factV335('Cambio',delta)+
       '</div>'
      :'';
    const context=isProgress?String(x?.body||''):'';
    const note=String(sm.suggestion||(isProgress?'':x?.body)||'');
    return '<div class="v331-alert-row '+safe(x?.severity||'info')+'">'+
      '<div class="v331-alert-copy">'+
        '<div class="v331-alert-label"><i class="v331-alert-dot"></i><span>'+safe(category(x))+'</span></div>'+
        '<div class="v331-alert-main"><strong>'+safe(title(x))+'</strong>'+(metric?'<b>'+safe(metric)+'</b>':'')+'</div>'+
        (facts?facts:(compare?'<div class="v331-alert-compare">'+safe(compare)+'</div>':''))+
        (isProgress&&sm.period?'<div class="v331-alert-compare">'+safe(sm.period)+'</div>':'')+
        (context?'<div class="v335-progress-context">'+safe(context)+'</div>':'')+
        (note?'<div class="v331-alert-note"><span class="v335-note-label">Lectura coach</span><span>'+safe(note)+'</span></div>':'')+
      '</div>'+
      '<div class="v331-alert-actions">'+
        '<button class="btn small" onclick="window.__fjzOpenGroupedAlertV331(\''+js(x?.athlete_id)+'\',\''+js(x?.event_key)+'\',\''+js(x?.kind)+'\')">Ver</button>'+
        (dismiss?'<button class="btn ghost small" onclick="window.__fjzDismissGroupedAlertV331(\''+js(x?.event_key)+'\')">Ocultar</button>':'')+
      '</div>'+
    '</div>';
  }"""
    body=body[:start]+replacement+body[end:]

    marker="""    reviewCenterReadableTypographyV334:true
  };"""
    replacement_marker="""    reviewCenterReadableTypographyV334:true,
    progressFactsStructuredV335:true,
    progressPercentHiddenFromCoachV335:true,
    coachReadingLabelV335:true
  };"""
    if marker not in body:
        raise RuntimeError("V21.35 V331 marker anchor missing")
    body=body.replace(marker,replacement_marker,1)
    return body

html=edit_script(html,"v331ProfessionalAlertGroupingRuntime",patch_v331)

css=r"""
/* =========================================================
   TEAM FJZ · V21.35 PROFESSIONAL PROGRESS ALERT COPY
   ========================================================= */
.v335-progress-facts{
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:7px;
  margin-top:8px;
}
.v335-progress-fact{
  min-width:0;
  padding:8px 9px;
  border:1px solid rgba(255,255,255,.07);
  border-radius:10px;
  background:#0a0c10;
}
.v335-progress-fact small{
  display:block;
  color:#737c88;
  font-size:8px;
  font-weight:900;
  letter-spacing:.055em;
  text-transform:uppercase;
}
.v335-progress-fact b{
  display:block;
  margin-top:4px;
  color:#edf0f4;
  font-size:11px;
  line-height:1.3;
  font-variant-numeric:tabular-nums;
  overflow-wrap:anywhere;
}
.v335-progress-context{
  margin-top:7px;
  color:#9aa2ad;
  font-size:10px;
  line-height:1.45;
}
.v331-alert-note{
  display:flex;
  gap:7px;
  align-items:flex-start;
  margin-top:8px;
  padding:8px 9px;
  border:1px solid rgba(103,173,255,.12);
  border-radius:10px;
  background:rgba(103,173,255,.025);
  color:#9ba4af;
}
.v335-note-label{
  flex:0 0 auto;
  color:#9fc8f8;
  font-size:8px;
  font-weight:900;
  letter-spacing:.05em;
  text-transform:uppercase;
}
.v331-smart-dashboard .v331-alert-note{display:flex}
@media(max-width:640px){
  .v335-progress-facts{
    grid-template-columns:1fr 1fr;
  }
  .v335-progress-fact:last-child:nth-child(3){
    grid-column:1/-1;
  }
  .v331-alert-note{
    display:grid;
    grid-template-columns:1fr;
    gap:4px;
  }
}
@media(max-width:390px){
  .v335-progress-facts{grid-template-columns:1fr}
  .v335-progress-fact:last-child:nth-child(3){grid-column:auto}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V21.35 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-professional-progress-alert-copy" content="21.35">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V21.35 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-professional-progress-alert-copy" content="21.35"',
    "concreteProgressCopyV335:true",
    "percentageOnlyProgressSuppressedV335:true",
    "loadAlertsUseKgDeltaV335:true",
    "volumeAlertsUseAbsoluteWorkV335:true",
    "adherenceNutritionUseCountsV335:true",
    "professionalCoachSuggestionsV335:true",
    "progressFactsStructuredV335:true",
    "progressPercentHiddenFromCoachV335:true",
    "coachReadingLabelV335:true",
    "firstReviewCardsDisabledV327:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.35 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.35 professional progress alert copy")
print("V21.35 BEFORE:",before)
print("V21.35 AFTER:",after)
