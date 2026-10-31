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
        if mid>=0:
            break
    if mid<0:
        raise RuntimeError("V21.37 missing script "+script_id)
    a=doc.find(">",mid)
    b=doc.find("</script>",a)
    if a<0 or b<0:
        raise RuntimeError("V21.37 malformed script "+script_id)
    old=doc[a+1:b]
    new=transform(old)
    if new==old:
        raise RuntimeError("V21.37 no changes in "+script_id)
    return doc[:a+1]+new+doc[b:]

before=metrics(html)

for marker in [
    'meta name="fjz-professional-progress-alert-copy" content="21.35"',
    'meta name="fjz-review-comment-hardening" content="21.36"',
    'id="v278SmartAlertsProgressRuntime"',
    'id="v331ProfessionalAlertGroupingRuntime"',
    "concreteProgressCopyV335:true",
    "groupedAlertCloudReadbackV336:true",
    "firstReviewCardsDisabledV327:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.37 prerequisite missing "+marker)

def patch_v278(body):
    # 1) Suppress exact duplicate exercise results saved twice on the same calendar day.
    old_push="""        map.get(key).items.push({date:ss.date,sessionId:ss.id,dayName:ss.dayName,...stats});"""
    new_push="""        const item={date:ss.date,sessionId:ss.id,dayName:ss.dayName,...stats};
        const series=map.get(key).items;
        const duplicate=series.some(x=>
          isoDayV278(x?.date)===isoDayV278(item.date)&&
          Number(x?.setCount)===Number(item.setCount)&&
          Math.abs(Number(x?.bestLoad||0)-Number(item.bestLoad||0))<.01&&
          Math.abs(Number(x?.bestReps||0)-Number(item.bestReps||0))<.01&&
          Math.abs(Number(x?.totalReps||0)-Number(item.totalReps||0))<.01&&
          Math.abs(Number(x?.avgRir??-999)-Number(item.avgRir??-999))<.01
        );
        if(!duplicate)series.push(item);"""
    if body.count(old_push)!=1:
        raise RuntimeError("V21.37 exercise duplicate anchor mismatch: "+str(body.count(old_push)))
    body=body.replace(old_push,new_push,1)

    # Work only inside the canonical exercise comparator.
    start=body.find("  function compareExerciseV278(row,athleteId,athleteName){")
    end=body.find("\n  function exerciseAlertsV278(",start)
    if start<0 or end<0:
        raise RuntimeError("V21.37 compareExercise bounds missing")
    block=body[start:end]

    old_diff="""    const repsDiff=(Number.isFinite(cur.bestReps)&&Number.isFinite(prev.bestReps))?cur.bestReps-prev.bestReps:null;
    const rirDiff="""
    new_diff="""    const repsDiff=(Number.isFinite(cur.bestReps)&&Number.isFinite(prev.bestReps))?cur.bestReps-prev.bestReps:null;
    const totalRepsDiff=(Number.isFinite(cur.totalReps)&&Number.isFinite(prev.totalReps))?cur.totalReps-prev.totalReps:null;
    const rirDiff="""
    if block.count(old_diff)!=1:
        raise RuntimeError("V21.37 total reps diff anchor mismatch")
    block=block.replace(old_diff,new_diff,1)

    old_fatigue="""    const repsFalling=repsDiff!=null&&repsDiff<=-2;
    const volumeFalling=volPct!=null&&volPct<=-12;
    if(lowRirRepeated&&(repsFalling||volumeFalling)){
      alerts.push(make(
        'fatigue','critical',
        row.name+' · posible fatiga',
        'RIR muy bajo repetido junto con una caída de rendimiento.',
        'RIR '+fmtV278(prev.avgRir,1),
        'RIR '+fmtV278(cur.avgRir,1),
        repsFalling?(fmtV278(repsDiff,0)+' reps'):(fmtV278(cur.volume-prev.volume,0)+' kg·rep'),
        'Revisar recuperación, técnica y carga antes de progresar.',
        'RIR · Atención'
      ));
      return alerts;
    }"""
    new_fatigue="""    const repsFalling=repsDiff!=null&&repsDiff<=-2;
    const totalRepsFalling=totalRepsDiff!=null&&totalRepsDiff<=-3;
    if(lowRirRepeated&&(repsFalling||totalRepsFalling)){
      alerts.push(make(
        'fatigue','critical',
        row.name+' · posible fatiga',
        'RIR muy bajo repetido junto con menos repeticiones registradas.',
        'RIR '+fmtV278(prev.avgRir,1)+' · '+fmtV278(prev.totalReps,0)+' reps totales',
        'RIR '+fmtV278(cur.avgRir,1)+' · '+fmtV278(cur.totalReps,0)+' reps totales',
        repsFalling?(fmtV278(repsDiff,0)+' reps en el mejor set'):(fmtV278(totalRepsDiff,0)+' reps totales'),
        'Revisar recuperación, técnica y carga antes de progresar. No interpretar una suma carga×reps como kilos levantados.',
        'RIR · Atención'
      ));
      return alerts;
    }"""
    if block.count(old_fatigue)!=1:
        raise RuntimeError("V21.37 fatigue anchor mismatch: "+str(block.count(old_fatigue)))
    block=block.replace(old_fatigue,new_fatigue,1)

    # 2) A real regression at the same load is shown with actual reps, never an abstract volume number.
    rir_anchor="""    if(loadSimilar&&repsSimilar&&rirDiff!=null&&rirDiff>=1){"""
    reps_down="""    if(loadSimilar&&repsDiff!=null&&repsDiff<=-2&&rirSimilar){
      alerts.push(make(
        'reps-down','warning',
        row.name+' · '+fmtV278(repsDiff,0)+' reps en el mejor set',
        'Con una carga máxima y un RIR comparables, bajaron las repeticiones del mejor set.',
        fmtV278(prev.bestLoad,1)+' kg × '+fmtV278(prev.bestReps,0)+' reps · '+fmtV278(prev.totalReps,0)+' reps totales · RIR '+fmtV278(prev.avgRir,1),
        fmtV278(cur.bestLoad,1)+' kg × '+fmtV278(cur.bestReps,0)+' reps · '+fmtV278(cur.totalReps,0)+' reps totales · RIR '+fmtV278(cur.avgRir,1),
        fmtV278(repsDiff,0)+' reps',
        'Revisar si hubo fatiga, técnica, descanso o un cambio intencional del esquema antes de ajustar la rutina.',
        'Repeticiones · Revisar'
      ));
      return alerts;
    }

"""
    if block.count(rir_anchor)!=1:
        raise RuntimeError("V21.37 reps-down insertion anchor mismatch")
    block=block.replace(rir_anchor,reps_down+rir_anchor,1)

    # 3) Replace coach-facing load×reps "volume" alerts with a conservative reps trend.
    trend_start=block.find("    if(items.length>=4){")
    trend_end=block.find("\n    return alerts;",trend_start)
    if trend_start<0 or trend_end<0:
        raise RuntimeError("V21.37 trend block bounds missing")
    trend=r"""    if(items.length>=4){
      const rec=items.slice(-2),old=items.slice(-4,-2);
      const recReps=avgV278(rec.map(x=>x.totalReps).filter(Number.isFinite));
      const oldReps=avgV278(old.map(x=>x.totalReps).filter(Number.isFinite));
      const recSets=avgV278(rec.map(x=>x.setCount).filter(Number.isFinite));
      const oldSets=avgV278(old.map(x=>x.setCount).filter(Number.isFinite));
      const recLoad=avgV278(rec.map(x=>x.bestLoad).filter(x=>Number.isFinite(x)&&x>0));
      const oldLoad=avgV278(old.map(x=>x.bestLoad).filter(x=>Number.isFinite(x)&&x>0));
      const recRir=avgV278(rec.map(x=>x.avgRir).filter(Number.isFinite));
      const oldRir=avgV278(old.map(x=>x.avgRir).filter(Number.isFinite));
      const repsTrend=(Number.isFinite(recReps)&&Number.isFinite(oldReps))?recReps-oldReps:null;
      const setsStable=Number.isFinite(recSets)&&Number.isFinite(oldSets)&&Math.abs(recSets-oldSets)<=.5;
      const loadStable=Number.isFinite(recLoad)&&Number.isFinite(oldLoad)&&Math.abs(recLoad-oldLoad)<=Math.max(1,oldLoad*.025);
      const blockContext=(setsStable&&loadStable&&repsTrend!=null);
      if(blockContext&&repsTrend>=3){
        alerts.push(make(
          'reps-trend','success',
          row.name+' · promedio +'+fmtV278(repsTrend,0)+' reps/sesión',
          'En las últimas dos sesiones aumentó el promedio de repeticiones totales con series y carga máxima comparables.',
          fmtV278(oldReps,0)+' reps totales · '+fmtV278(oldSets,1)+' series · '+fmtV278(oldLoad,1)+' kg máx',
          fmtV278(recReps,0)+' reps totales · '+fmtV278(recSets,1)+' series · '+fmtV278(recLoad,1)+' kg máx',
          '+'+fmtV278(repsTrend,0)+' reps/sesión',
          'Tendencia positiva con contexto comparable. Confirmar técnica y RIR antes de progresar.',
          'Repeticiones · Tendencia'
        ));
      }else if(blockContext&&repsTrend<=-3){
        alerts.push(make(
          'reps-trend','warning',
          row.name+' · promedio '+fmtV278(repsTrend,0)+' reps/sesión',
          'En las últimas dos sesiones bajó el promedio de repeticiones totales con series y carga máxima comparables.',
          fmtV278(oldReps,0)+' reps totales · '+fmtV278(oldSets,1)+' series · '+fmtV278(oldLoad,1)+' kg máx',
          fmtV278(recReps,0)+' reps totales · '+fmtV278(recSets,1)+' series · '+fmtV278(recLoad,1)+' kg máx',
          fmtV278(repsTrend,0)+' reps/sesión',
          'Revisar recuperación, técnica y contexto. Si cambió la carga o el número de series, esta señal no se genera.',
          'Repeticiones · Tendencia'
        ));
      }
    }"""
    block=block[:trend_start]+trend+block[trend_end:]

    body=body[:start]+block+body[end:]

    marker="""    professionalCoachSuggestionsV335:true,"""
    replacement="""    professionalCoachSuggestionsV335:true,
    coachFacingKgRepRemovedV337:true,
    repsDropAlertV337:true,
    repsTrendUsesComparableContextV337:true,
    exactSameDayExerciseDuplicateSuppressedV337:true,
    volumeKeptInternalOnlyV337:true,"""
    if body.count(marker)!=1:
        raise RuntimeError("V21.37 V278 marker anchor mismatch")
    body=body.replace(marker,replacement,1)
    return body

html=edit_script(html,"v278SmartAlertsProgressRuntime",patch_v278)

def patch_v331(body):
    old_cat="""      if(metric==='reps')return 'REPETICIONES';
      if(metric.includes('volume'))return 'VOLUMEN';"""
    new_cat="""      if(metric==='reps'||metric==='reps-down'||metric==='reps-trend')return 'REPETICIONES';
      if(metric.includes('volume'))return 'RENDIMIENTO';"""
    if body.count(old_cat)!=1:
        raise RuntimeError("V21.37 V331 category anchor mismatch")
    body=body.replace(old_cat,new_cat,1)

    old_labels="""      const labels={load:'Carga',reps:'Repeticiones',volume:'Volumen','volume-down':'Volumen','high-rir':'RIR alto',fatigue:'Posible fatiga','rir-reserve':'RIR','rir-demand':'RIR'};"""
    new_labels="""      const labels={load:'Carga',reps:'Repeticiones','reps-down':'Repeticiones','reps-trend':'Tendencia de repeticiones','high-rir':'RIR alto',fatigue:'Posible fatiga','rir-reserve':'RIR','rir-demand':'RIR'};"""
    if body.count(old_labels)!=1:
        raise RuntimeError("V21.37 V331 labels anchor mismatch")
    body=body.replace(old_labels,new_labels,1)

    old_rows="""    (rows||[]).filter(Boolean).forEach(x=>{"""
    new_rows="""    (rows||[]).filter(Boolean).filter(x=>{
      const sm=x?.smart_meta||{},metric=String(sm.metric||'').toLowerCase();
      const copy=[x?.title,x?.body,sm?.previous,sm?.current,sm?.delta,sm?.type_label].filter(Boolean).join(' ');
      return !(x?.kind==='progression'&&(metric.includes('volume')||/kg\\s*[·x*]\\s*rep/i.test(copy)));
    }).forEach(x=>{"""
    if body.count(old_rows)!=1:
        raise RuntimeError("V21.37 V331 ambiguous volume filter anchor mismatch")
    body=body.replace(old_rows,new_rows,1)

    marker="""    groupedAlertPersistsAcrossRefreshV336:true
  };"""
    replacement="""    groupedAlertPersistsAcrossRefreshV336:true,
    ambiguousVolumeAlertsSuppressedV337:true,
    repsTrendLabelingV337:true,
    coachNeverSeesKgRepAsLoadV337:true
  };"""
    if body.count(marker)!=1:
        raise RuntimeError("V21.37 V331 marker anchor mismatch")
    body=body.replace(marker,replacement,1)
    return body

html=edit_script(html,"v331ProfessionalAlertGroupingRuntime",patch_v331)

html=html.replace("</head>",'<meta name="fjz-coach-alert-logic" content="21.37">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V21.37 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-coach-alert-logic" content="21.37"',
    "coachFacingKgRepRemovedV337:true",
    "repsDropAlertV337:true",
    "repsTrendUsesComparableContextV337:true",
    "exactSameDayExerciseDuplicateSuppressedV337:true",
    "volumeKeptInternalOnlyV337:true",
    "ambiguousVolumeAlertsSuppressedV337:true",
    "coachNeverSeesKgRepAsLoadV337:true",
    "groupedAlertCloudReadbackV336:true",
    "firstReviewCardsDisabledV327:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.37 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.37 coach alert logic")
print("V21.37 BEFORE:",before)
print("V21.37 AFTER:",after)
