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
        raise RuntimeError("V22 2A script authority mismatch "+script_id+": "+str(len(matches)))
    m=matches[0]
    return doc[:m.start(2)]+fn(m.group(2))+doc[m.end(2):]

before=topology(html)

for marker in [
    'meta name="fjz-v22-1b-data-sync-foundation" content="agenda-read-pilot"',
    'id="v205CanonicalWorkoutProgressRuntime"',
    'id="v315DecimalWorkoutWeightsRuntime"',
    'id="v145WorkoutAutosaveRuntime"',
    'id="v207ConfirmedSessionCommitRuntime"',
    "openExerciseFeedbackV73",
    "submitExerciseFeedbackV73",
]:
    if marker not in html:
        raise RuntimeError("V22 2A prerequisite missing "+marker)

module_code=pathlib.Path("src/modules/workouts/premium-workout.js").read_text(encoding="utf-8").strip()
premium_css=pathlib.Path("src/ui/premium-workout.css").read_text(encoding="utf-8").strip()
if "</script" in module_code.lower():
    raise RuntimeError("V22 2A module cannot contain closing script markup")

html=html.replace("</head>",'<script id="v22PremiumWorkoutModule">\n'+module_code+'\n</script>\n<meta name="fjz-v22-2a-premium-workout" content="enabled">\n</head>',1)

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V22 2A expected one consolidated stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+premium_css+"\n"+html[sm.end("body"):]

def patch_v205(body):
    old="      return baseRenderWorkoutV205.apply(this,arguments);\n"
    new="      const out=baseRenderWorkoutV205.apply(this,arguments);\n      try{globalThis.TeamFJZPremiumWorkout?.enhanceWorkout()}catch(_e){}\n      return out;\n"
    if body.count(old)!=1:
        raise RuntimeError("V22 2A V205 renderWorkout anchor mismatch: "+str(body.count(old)))
    return body.replace(old,new,1)
html=edit_script(html,"v205CanonicalWorkoutProgressRuntime",patch_v205)

def patch_v315(body):
    old="""    window.setWorkout=function(uidv,si,field,val){
      if(Number(field)===0)val=normalizeDecimalV315(val);
      return baseSetWorkoutV315.call(this,uidv,si,field,val);
    };"""
    new="""    window.setWorkout=function(uidv,si,field,val){
      if(Number(field)===0)val=normalizeDecimalV315(val);
      const out=baseSetWorkoutV315.call(this,uidv,si,field,val);
      try{globalThis.TeamFJZPremiumWorkout?.markDraftChanged()}catch(_e){}
      try{globalThis.TeamFJZPremiumWorkout?.enhanceWorkout()}catch(_e){}
      return out;
    };"""
    if body.count(old)!=1:
        raise RuntimeError("V22 2A V315 setWorkout anchor mismatch: "+str(body.count(old)))
    return body.replace(old,new,1)
html=edit_script(html,"v315DecimalWorkoutWeightsRuntime",patch_v315)

def patch_v145(body):
    old="""    if(n){
      const d=new Date(lastSavedAt);
      n.textContent='Último guardado '+d.toLocaleTimeString('es-AR',{hour:'2-digit',minute:'2-digit'});
    }
  }"""
    new="""    if(n){
      const d=new Date(lastSavedAt);
      n.textContent='Último guardado '+d.toLocaleTimeString('es-AR',{hour:'2-digit',minute:'2-digit'});
    }
    try{globalThis.TeamFJZPremiumWorkout?.draftProtected(lastSavedAt)}catch(_e){}
  }"""
    if body.count(old)!=1:
        raise RuntimeError("V22 2A V145 draft status anchor mismatch: "+str(body.count(old)))
    return body.replace(old,new,1)
html=edit_script(html,"v145WorkoutAutosaveRuntime",patch_v145)

def patch_v207(body):
    pairs=[
      ("stateV207='saving';","stateV207='saving';\n    try{globalThis.TeamFJZPremiumWorkout?.setSaveState('saving')}catch(_e){}"),
      ("stateV207='success';","stateV207='success';\n      try{globalThis.TeamFJZPremiumWorkout?.setSaveState('success')}catch(_e){}"),
      ("stateV207='failed';\n      // Keep pendingV207","stateV207='failed';\n      try{globalThis.TeamFJZPremiumWorkout?.setSaveState('failed')}catch(_e){}\n      // Keep pendingV207"),
      ("stateV207='failed';\n      modalErrorV207('No pudimos preparar","stateV207='failed';\n      try{globalThis.TeamFJZPremiumWorkout?.setSaveState('failed')}catch(_e){}\n      modalErrorV207('No pudimos preparar"),
      ("      stateV207='idle';\n      pendingV207=null;","      stateV207='idle';\n      try{globalThis.TeamFJZPremiumWorkout?.setSaveState('idle')}catch(_e){}\n      pendingV207=null;"),
    ]
    for old,new in pairs:
        count=body.count(old)
        if count<1:
            raise RuntimeError("V22 2A V207 state anchor missing: "+repr(old))
        body=body.replace(old,new)
    old="""        '<div class="v207-save-actions"><button class="btn primary" onclick="finishConfirmedSessionV207()">Listo</button></div>'+"""
    new="""        '<div class="v207-save-actions"><button class="btn" onclick="closeModal();studentTab=\\'history\\';currentDay=-1;render()">Ver historial</button><button class="btn primary" onclick="finishConfirmedSessionV207()">Listo</button></div>'+"""
    if body.count(old)!=1:
        raise RuntimeError("V22 2A V207 success actions anchor mismatch")
    return body.replace(old,new,1)
html=edit_script(html,"v207ConfirmedSessionCommitRuntime",patch_v207)

old="""  exerciseFeedbackTargetV73={uid,name,dayId:d?.id||'',dayName:d?.name||''};
  showModal(`"""
new="""  exerciseFeedbackTargetV73={uid,name,dayId:d?.id||'',dayName:d?.name||''};
  const premiumDraftV22=globalThis.TeamFJZPremiumWorkout?.commentDraft(uid)||null;
  showModal(`"""
if html.count(old)!=1:
    raise RuntimeError("V22 2A comment target anchor mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

old='placeholder="Ej: sentí una molestia al bajar / me costó mantener la técnica / esta carga se sintió muy pesada..."></textarea>'
new='placeholder="Ej: sentí una molestia al bajar / me costó mantener la técnica / esta carga se sintió muy pesada...">${premiumDraftV22?.message?esc(premiumDraftV22.message):\'\'}</textarea>'
if html.count(old)!=1:
    raise RuntimeError("V22 2A comment textarea anchor mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

old="""    <button class="btn primary" style="width:100%;margin-top:12px" onclick="submitExerciseFeedbackV73()">Enviar al coach</button>`)
}"""
new="""    <button class="btn primary" style="width:100%;margin-top:12px" onclick="submitExerciseFeedbackV73()">Enviar al coach</button>`)
  try{globalThis.TeamFJZPremiumWorkout?.bindCommentDraft(exerciseFeedbackTargetV73)}catch(_e){}
}"""
if html.count(old)!=1:
    raise RuntimeError("V22 2A comment bind anchor mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

old="""  const message=el('v73FeedbackMessage')?.value.trim()||'';
  if(message.length<3){toast('Escribí un comentario breve');return}

  const athleteId=currentAthleteIdV73();"""
new="""  const message=el('v73FeedbackMessage')?.value.trim()||'';
  if(message.length<3){toast('Escribí un comentario breve');return}
  if(globalThis.TeamFJZPremiumWorkout&&!globalThis.TeamFJZPremiumWorkout.beginCommentSubmit(t.uid,message,type))return;

  const athleteId=currentAthleteIdV73();"""
if html.count(old)!=1:
    raise RuntimeError("V22 2A comment submit anchor mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

old="""    if(error){toast(cloudErr(error));return}
    const key=feedbackKeyV73(athleteId),rows=exerciseFeedbackCacheV73.get(key)||[];"""
new="""    if(error){try{globalThis.TeamFJZPremiumWorkout?.endCommentSubmit(t.uid,false)}catch(_e){}toast(cloudErr(error));return}
    const key=feedbackKeyV73(athleteId),rows=exerciseFeedbackCacheV73.get(key)||[];"""
if html.count(old)!=1:
    raise RuntimeError("V22 2A comment error anchor mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

old="""  closeModal();
  toast(type==='discomfort'?'Molestia enviada al coach':'Comentario enviado al coach');
  render()
}"""
new="""  try{globalThis.TeamFJZPremiumWorkout?.endCommentSubmit(t.uid,true)}catch(_e){}
  closeModal();
  toast(type==='discomfort'?'Molestia enviada al coach':'Comentario enviado al coach');
  render()
}"""
if html.count(old)!=1:
    raise RuntimeError("V22 2A comment success anchor mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

html=html.replace("</body>",'<script id="v22PremiumWorkoutBoot">try{globalThis.TeamFJZPremiumWorkout?.enhanceWorkout()}catch(_e){}</script>\n</body>',1)

after=topology(html)
for key in ("styles","renders","channels","timeouts","intervals","listeners","mutation_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V22 2A topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'id="v22PremiumWorkoutModule"',
    'meta name="fjz-v22-2a-premium-workout" content="enabled"',
    "TeamFJZPremiumWorkout?.enhanceWorkout",
    "TeamFJZPremiumWorkout?.setSaveState('saving')",
    "TeamFJZPremiumWorkout?.bindCommentDraft",
    "beginCommentSubmit(t.uid,message,type)",
    "endCommentSubmit(t.uid,true)",
    "Ver historial",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V22 2A missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V22 2A PREMIUM WORKOUT EXPERIENCE")
print("V22 2A BEFORE:",before)
print("V22 2A AFTER:",after)
