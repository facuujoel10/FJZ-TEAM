import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def topology(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "intervals":len(re.findall(r"setInterval\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
    }

def edit_script(doc,script_id,fn):
    pattern=re.compile(r'(<script[^>]*id=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    matches=list(pattern.finditer(doc))
    if len(matches)!=1:
        raise RuntimeError("V22 2C script authority mismatch "+script_id+": "+str(len(matches)))
    m=matches[0]
    return doc[:m.start(2)]+fn(m.group(2))+doc[m.end(2):]

before=topology(html)
for marker in [
    'id="v22PremiumWorkoutModule"',
    'id="v22SessionHistoryModule"',
    'id="v22VisualRedesignModule"',
    'id="v207ConfirmedSessionCommitRuntime"',
    'id="v244UnifiedSessionHistoryRuntime"',
    "exactSessionCommentLinkV2B:true",
]:
    if marker not in html: raise RuntimeError("V22 2C prerequisite missing "+marker)

module=pathlib.Path("src/modules/workouts/intelligent-training.js").read_text(encoding="utf-8").strip()
css=pathlib.Path("src/ui/intelligent-training.css").read_text(encoding="utf-8").strip()
if "</script" in module.lower(): raise RuntimeError("V22 2C module cannot contain closing script markup")
html=html.replace("</head>",'<script id="v22IntelligentTrainingModule">\n'+module+'\n</script>\n<meta name="fjz-v22-2c-intelligent-training" content="enabled">\n</head>',1)

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V22 2C expected one consolidated stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

def patch_visual(body):
    old="""  if(typeof queueMicrotask==='function')queueMicrotask(()=>{
    if(!view.isConnected)return;
    [...view.querySelectorAll('.session-card.v22-premium-exercise,.v22v2-exercise')].forEach(compactFeedbackStatus);
  });
  return !!composition;"""
    new="""  if(typeof queueMicrotask==='function')queueMicrotask(()=>{
    if(!view.isConnected)return;
    [...view.querySelectorAll('.session-card.v22-premium-exercise,.v22v2-exercise')].forEach(compactFeedbackStatus);
    try{globalThis.TeamFJZIntelligentTraining?.enhanceWorkout(view)}catch(_e){}
  });
  try{globalThis.TeamFJZIntelligentTraining?.enhanceWorkout(view)}catch(_e){}
  return !!composition;"""
    if body.count(old)!=1: raise RuntimeError("V22 2C visual integration anchor mismatch "+str(body.count(old)))
    return body.replace(old,new,1)
html=edit_script(html,"v22VisualRedesignModule",patch_visual)

def patch_v207(body):
    old="""      window.__fjzSessionCloudConfirmedId=session.id;
      try{globalThis.TeamFJZSessionHistory?.markConfirmed(session.id)}catch(_e){}

      stateV207='success';"""
    new="""      window.__fjzSessionCloudConfirmedId=session.id;
      try{globalThis.TeamFJZSessionHistory?.markConfirmed(session.id)}catch(_e){}
      try{
        session.confirmed=true;session.cloudConfirmed=true;
        globalThis.TeamFJZIntelligentTraining?.markSessionConfirmed(session.id);
        saveState();
      }catch(_e){}

      stateV207='success';"""
    if body.count(old)!=1: raise RuntimeError("V22 2C confirmed-session anchor mismatch "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""      modalSuccessV207();
      try{globalThis.TeamFJZPremiumWorkout?.decorateSuccessModal()}catch(_e){}"""
    new="""      modalSuccessV207();
      try{globalThis.TeamFJZPremiumWorkout?.decorateSuccessModal()}catch(_e){}
      try{
        const summaryV2C=globalThis.TeamFJZIntelligentTraining?.buildConfirmedSummary(session);
        if(summaryV2C)globalThis.TeamFJZIntelligentTraining?.renderSummaryModal(summaryV2C);
      }catch(_e){}"""
    if body.count(old)<1: raise RuntimeError("V22 2C success summary anchor missing")
    body=body.replace(old,new,1)

    old="""    if(stateV207==='success'){
      modalSuccessV207();
      try{globalThis.TeamFJZPremiumWorkout?.decorateSuccessModal()}catch(_e){}
      return;
    }"""
    new="""    if(stateV207==='success'){
      modalSuccessV207();
      try{globalThis.TeamFJZPremiumWorkout?.decorateSuccessModal()}catch(_e){}
      try{
        const summaryV2C=globalThis.TeamFJZIntelligentTraining?.buildConfirmedSummary(pendingV207?.session);
        if(summaryV2C)globalThis.TeamFJZIntelligentTraining?.renderSummaryModal(summaryV2C);
      }catch(_e){}
      return;
    }"""
    if body.count(old)<1: raise RuntimeError("V22 2C repeat success anchor missing")
    body=body.replace(old,new)
    return body
html=edit_script(html,"v207ConfirmedSessionCommitRuntime",patch_v207)

def patch_history(body):
    old="""    const comparisonV2B=globalThis.TeamFJZSessionHistory?.compareExercise?.(student()?.sessions||[],ss?.id,r?.exerciseUid)||null;
    const comparisonHtmlV2B=comparisonV2B?.previous
      ?'<div class="v22-history-compare"><div class="v22-history-compare-box"><small>Sesión anterior</small><strong>'+esc(String(comparisonV2B.previous.load))+' kg × '+esc(String(comparisonV2B.previous.reps))+'</strong></div><span>→</span><div class="v22-history-compare-box current"><small>Esta sesión</small><strong>'+esc(String(comparisonV2B.current.load))+' kg × '+esc(String(comparisonV2B.current.reps))+'</strong></div></div>'
      :'';"""
    new="""    const comparisonV2B=globalThis.TeamFJZSessionHistory?.compareExercise?.(student()?.sessions||[],ss?.id,r?.exerciseUid)||null;
    const intelligentV2C=globalThis.TeamFJZIntelligentTraining?.analyzeExercise?.({
      sessions:student()?.sessions||[],currentSession:ss,exerciseUid:r?.exerciseUid,confirmedSessionId:ss?.confirmed||ss?.cloudConfirmed?ss.id:null
    })||null;
    const suggestionV2C=globalThis.TeamFJZIntelligentTraining?.progressionSuggestion?.(intelligentV2C)||null;
    const intelligentHtmlV2C=intelligentV2C
      ?(intelligentV2C.comparable
        ?'<div class="v22c-performance-note" data-comparison-state="'+esc(intelligentV2C.trend||'comparable')+'"><strong>Progreso verificable</strong><small>'+esc(intelligentV2C.comparison||intelligentV2C.improvements?.[0]?.message||'Sin cambio relevante frente a la sesión comparable anterior.')+'</small>'+(suggestionV2C?'<small><b>'+esc(suggestionV2C.label)+':</b> '+esc(suggestionV2C.message)+'</small>':'')+'</div>'
        :'<div class="v22c-performance-note v22c-no-reference" data-comparison-state="none"><strong>Sin referencia comparable</strong><small>'+esc(intelligentV2C.reason||'No hay datos confirmados suficientes para comparar esta sesión.')+'</small></div>')
      :'';
    const comparisonHtmlV2B=(intelligentV2C?.comparable&&comparisonV2B?.previous&&String(comparisonV2B.previousSessionId||'')===String(intelligentV2C.previousSessionId||''))
      ?'<div class="v22-history-compare"><div class="v22-history-compare-box"><small>Sesión anterior</small><strong>'+esc(String(comparisonV2B.previous.load))+' kg × '+esc(String(comparisonV2B.previous.reps))+'</strong></div><span>→</span><div class="v22-history-compare-box current"><small>Esta sesión</small><strong>'+esc(String(comparisonV2B.current.load))+' kg × '+esc(String(comparisonV2B.current.reps))+'</strong></div></div>'
      :'';"""
    if body.count(old)!=1: raise RuntimeError("V22 2C history analysis anchor mismatch "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""      comparisonHtmlV2B+
      exerciseCommentHtmlV287(comments,ss,r)+"""
    new="""      comparisonHtmlV2B+
      intelligentHtmlV2C+
      exerciseCommentHtmlV287(comments,ss,r)+"""
    if body.count(old)!=1: raise RuntimeError("V22 2C history placement anchor mismatch "+str(body.count(old)))
    body=body.replace(old,new,1)

    old_row="'<div class=\"history-item v244-history-item v22-history-session\">'+"
    new_row="'<div class=\"history-item v244-history-item v22-history-session\" data-session-id=\"'+esc(x.id)+'\">'+"
    if body.count(old_row)!=1: raise RuntimeError("V22 2C history session identity anchor mismatch "+str(body.count(old_row)))
    body=body.replace(old_row,new_row,1)

    old_metrics="""    const sum=ss.summary||{};"""
    new_metrics="""    const sum=ss.summary||{};
    const detailResultsV2C=Array.isArray(ss.exerciseResults)?ss.exerciseResults:[];
    const detailSetsV2C=detailResultsV2C.reduce((n,r)=>n+(Array.isArray(r?.sets)?r.sets.filter(x=>Array.isArray(x)&&x.some(v=>String(v??'').trim()!=='')).length:0),0);
    const totalSetsV2C=Number.isFinite(Number(sum.totalSets))&&Number(sum.totalSets)>0?Number(sum.totalSets):detailSetsV2C;
    const completedExercisesV2C=Number.isFinite(Number(sum.completedExercises||sum.registeredExercises))&&Number(sum.completedExercises||sum.registeredExercises)>0
      ?Number(sum.completedExercises||sum.registeredExercises)
      :detailResultsV2C.filter(r=>Array.isArray(r?.sets)&&r.sets.some(x=>Array.isArray(x)&&x.some(v=>String(v??'').trim()!==''))).length;"""
    if body.count(old_metrics)!=1: raise RuntimeError("V22 2C history metric fallback anchor mismatch "+str(body.count(old_metrics)))
    body=body.replace(old_metrics,new_metrics,1)

    old_grid="""        '<div><strong>'+summaryNumberV244(sum.totalSets)+'</strong><span>Series</span></div>'+
        '<div><strong>'+summaryNumberV244(sum.completedExercises||sum.registeredExercises)+'</strong><span>Ejercicios</span></div>'+"""
    new_grid="""        '<div><strong>'+summaryNumberV244(totalSetsV2C)+'</strong><span>Series</span></div>'+
        '<div><strong>'+summaryNumberV244(completedExercisesV2C)+'</strong><span>Ejercicios</span></div>'+"""
    if body.count(old_grid)!=1: raise RuntimeError("V22 2C history metric grid anchor mismatch "+str(body.count(old_grid)))
    body=body.replace(old_grid,new_grid,1)
    return body
html=edit_script(html,"v244UnifiedSessionHistoryRuntime",patch_history)

after=topology(html)
for key in ("styles","renders","channels","listeners","mutation_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V22 2C topology changed "+key+": "+repr({"before":before,"after":after}))
# One bounded timeout call site belongs to the single autocancelable rest ticker.
if after["timeouts"]!=before["timeouts"]+1:
    raise RuntimeError("V22 2C timeout topology mismatch: "+repr({"before":before,"after":after}))
# Preserve the certified zero-interval topology.
if after["intervals"]!=before["intervals"]:
    raise RuntimeError("V22 2C interval topology changed: "+repr({"before":before,"after":after}))

for marker in [
    'id="v22IntelligentTrainingModule"',
    'meta name="fjz-v22-2c-intelligent-training" content="enabled"',
    "TeamFJZIntelligentTraining?.enhanceWorkout",
    "TeamFJZIntelligentTraining?.markSessionConfirmed",
    "TeamFJZIntelligentTraining?.buildConfirmedSummary",
    "TeamFJZIntelligentTraining?.analyzeExercise",
    "session.confirmed=true",
]:
    if marker not in html: raise RuntimeError("V22 2C runtime marker missing "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V22 2C INTELLIGENT TRAINING")
print("V22 2C BEFORE:",before)
print("V22 2C AFTER:",after)
