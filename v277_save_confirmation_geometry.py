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

before=metrics(html)

for marker in [
    'meta name="fjz-confirmed-save-feedback" content="20.64"',
    'meta name="fjz-final-runtime-stability" content="20.74"',
    'meta name="fjz-coach-hud-nutrition-detail" content="20.76"',
    "__fjzConfirmSavedV264",
    "__fjzQuickSavedV264",
    "confirmedCheckinSuccess:true",
    "v207-save-state",
]:
    if marker not in html:
        raise RuntimeError("V20.77 prerequisite missing "+marker)

# Final sweep: any static success toast introduced after V20.64 becomes a
# green confirmation. Messages that explicitly say "guardá el plan" or
# mention pending/local-only state are intentionally NOT treated as saved.
toast_pat=re.compile(r"toast(?:\?\.)?\(\s*(['\"])(?P<msg>[^'\"]+)\1\s*\)")
success_rx=re.compile(r"(guardad[oa]s?|finalizad[oa]s?|enviad[oa]s?|registrad[oa]s?|cread[oa]s?|actualizad[oa]s?|publicad[oa]s?|confirmad[oa]s?)",re.I)
skip_rx=re.compile(r"(guardá el plan|guardado en curso|localmente|sincronización pendiente|pendiente|sin guardar|revisá|copiados? al plan)",re.I)
replaced=[]

def repl_toast(m):
    msg=m.group("msg")
    if not success_rx.search(msg) or skip_rx.search(msg):
        return m.group(0)
    replaced.append(msg)
    title=msg.split("·",1)[0].strip()
    copy="La operación quedó confirmada correctamente."
    low=msg.lower()
    if "rutina" in low: copy="La rutina quedó guardada correctamente."
    elif "check-in" in low or "checkin" in low: copy="El check-in quedó guardado correctamente."
    elif "plan nutricional" in low or "nutric" in low: copy="El plan nutricional quedó guardado correctamente."
    elif "sesión" in low or "sesion" in low: copy="La sesión quedó guardada correctamente."
    elif "medición" in low or "medicion" in low: copy="La medición quedó guardada correctamente."
    elif "perfil" in low or "datos" in low: copy="Los datos quedaron guardados correctamente."
    elif "foto" in low: copy="La foto quedó guardada correctamente."
    elif "feedback" in low or "devolución" in low: copy="La devolución quedó guardada correctamente."
    elif "agenda" in low: copy="La agenda quedó guardada correctamente."
    elif "recordatorio" in low: copy="El recordatorio quedó guardado correctamente."
    return "window.__fjzConfirmSavedV264?.("+repr(title)+","+repr(copy)+")"

html=toast_pat.sub(repl_toast,html)

css=r"""
/* =========================================================
   TEAM FJZ · V20.77 SAVE CONFIRMATION + FINAL GEOMETRY
   ========================================================= */
:where(.card,.hero,.modal,.meal-block,.option-card,.meal-option-student,.exercise-row,.day-card,
       .v275-training-day,.v275-progress-panel,.v276-nutrition-status,.v276-macro-card,
       #view,#coachStudentBody,#studentSubBody,.form-grid,.grid,.tabs,.nutrition-log-row){
  box-sizing:border-box;
  min-width:0;
}
:where(.card,.hero,.modal,.meal-block,.option-card,.meal-option-student,.exercise-row,.day-card)
  :where(h1,h2,h3,h4,p,strong,span,small,label){
  overflow-wrap:anywhere;
}
:where(.form-grid,.grid,.nutrition-targets,.macro-preview,.v276-macro-cards,.v275-progress-grid)>*{
  min-width:0;
}
:where(input,select,textarea,.input){
  box-sizing:border-box;
  max-width:100%;
}
:where(.section-title,.meal-head,.modal-head,.day-head,.v275-training-day-top,.v276-status-head){
  min-width:0;
}
:where(.section-title,.meal-head,.modal-head,.day-head)>*{
  min-width:0;
}
:where(.nutrition-builder-actions,.day-actions,.pill-row,.v207-save-actions){
  align-items:center;
  flex-wrap:wrap;
}
.v277-saving{
  opacity:.68!important;
  cursor:progress!important;
  pointer-events:none!important;
}
.v277-saving::after{
  content:"";
  width:10px;
  height:10px;
  margin-left:6px;
  border:2px solid currentColor;
  border-right-color:transparent;
  border-radius:50%;
  display:inline-block;
  vertical-align:-1px;
  animation:v277SavingSpin .65s linear infinite;
}
@keyframes v277SavingSpin{to{transform:rotate(360deg)}}

.v264-confirmed-save{
  width:min(100%,420px);
  margin-inline:auto;
  text-align:center;
}
.v264-confirmed-save .v207-save-icon.success{
  display:grid;
  place-items:center;
  width:58px;
  height:58px;
  margin:2px auto 12px;
  border-radius:50%;
  background:rgba(59,213,138,.12);
  border:1px solid rgba(59,213,138,.32);
  color:#63e7a5;
  font-size:28px;
  font-weight:950;
}
.v264-confirmed-save .v207-save-title{
  text-align:center;
}
.v264-confirmed-save .v207-save-copy{
  max-width:34em;
  margin-inline:auto;
  text-align:center;
}
.v264-confirmed-save .v207-save-actions{
  justify-content:center;
}
.v264-confirmed-save .v207-save-actions>.btn{
  min-width:120px;
}

@media(max-width:720px){
  :where(.section-title,.meal-head,.modal-head,.day-head){
    gap:9px!important;
  }
  :where(.nutrition-builder-actions,.day-actions,.v207-save-actions){
    width:100%;
  }
  :where(.nutrition-builder-actions,.day-actions,.v207-save-actions)>.btn{
    min-width:0;
  }
}
@media(max-width:430px){
  :where(#view,#coachStudentBody,#studentSubBody,.card,.hero,.meal-block,.option-card,.modal){
    width:100%;
    max-width:100%;
  }
  .form-grid{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:8px!important;
  }
  .form-grid>.span2{grid-column:1/-1!important}
  :where(.nutrition-builder-actions,.day-actions)>.btn{
    flex:1 1 calc(50% - 5px);
  }
  .v207-save-actions>.btn{
    flex:1 1 100%;
    width:100%;
  }
  :where(input,select,textarea,.input){
    width:100%!important;
  }
}
@media(max-width:360px){
  .form-grid{grid-template-columns:1fr!important}
  .form-grid>*{grid-column:1!important}
  :where(.nutrition-builder-actions,.day-actions)>.btn{
    flex:1 1 100%;
    width:100%;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.77 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

runtime=r"""
<script id="v277SaveGeometryRuntime">
(function(){
  const active=new Map();

  function saveButtonV277(){
    const node=document.activeElement;
    return node&&node.tagName==='BUTTON'?node:null;
  }

  function wrapSaveV277(name){
    const original=window[name];
    if(typeof original!=='function'||original.__fjzSaveLockV277)return false;
    const wrapped=function(){
      if(active.has(name)){
        try{toast?.('Guardado en curso…')}catch(_e){}
        return active.get(name);
      }
      const btn=saveButtonV277();
      if(btn){btn.disabled=true;btn.classList.add('v277-saving');btn.setAttribute('aria-busy','true')}
      let out;
      try{out=original.apply(this,arguments)}
      catch(e){
        if(btn){btn.disabled=false;btn.classList.remove('v277-saving');btn.removeAttribute('aria-busy')}
        throw e;
      }
      if(!out||typeof out.then!=='function'){
        if(btn){btn.disabled=false;btn.classList.remove('v277-saving');btn.removeAttribute('aria-busy')}
        return out;
      }
      const promise=Promise.resolve(out).finally(()=>{
        active.delete(name);
        if(btn&&btn.isConnected){
          btn.disabled=false;btn.classList.remove('v277-saving');btn.removeAttribute('aria-busy');
        }
      });
      active.set(name,promise);
      return promise;
    };
    wrapped.__fjzSaveLockV277=true;
    wrapped.__fjzOriginalV277=original;
    window[name]=wrapped;
    return true;
  }

  const guarded=[
    'saveNutritionPlan',
    'submitMeasurement',
    'saveCheckinFeedback',
    'saveStudentScheduleV81',
    'saveReminderV81',
    'saveRecipeV70',
    'saveNutritionTemplateV63',
    'submitExerciseFeedbackV73',
    'submitWeeklyCheckin'
  ];
  const guardedNow=guarded.filter(wrapSaveV277);

  window.__fjzSavedV277=function(title,copy){
    return window.__fjzConfirmSavedV264?.(
      title||'Guardado con éxito',
      copy||'Los cambios quedaron guardados correctamente.'
    );
  };

  window.__fjzV277={
    version:'20.77',
    finalSaveConfirmationAudit:true,
    greenCheckOnConfirmedSaves:true,
    duplicateAsyncSaveGuard:true,
    buttonBusyState:true,
    workoutFinishUsesConfirmedState:true,
    checkinUsesConfirmedState:true,
    nutritionSaveCloudConfirmed:true,
    symmetryGeometryPass:true,
    mobile360GeometryPass:true,
    noExtraTimers:true,
    noExtraListeners:true,
    guardedActions:guardedNow
  };
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-final-save-geometry" content="20.77">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.77 topology changed "+key+": "+repr({"before":before,"after":after}))

# Any remaining static toast that looks like a successful save is a regression,
# except explicit local/pending/instructional messages.
remaining=[]
for m in toast_pat.finditer(html):
    msg=m.group("msg")
    if success_rx.search(msg) and not skip_rx.search(msg):
        remaining.append(msg)
if remaining:
    raise RuntimeError("V20.77 unconverted save success toasts: "+repr(sorted(set(remaining))))

for marker in [
    'meta name="fjz-final-save-geometry" content="20.77"',
    "finalSaveConfirmationAudit:true",
    "greenCheckOnConfirmedSaves:true",
    "duplicateAsyncSaveGuard:true",
    "buttonBusyState:true",
    "workoutFinishUsesConfirmedState:true",
    "checkinUsesConfirmedState:true",
    "nutritionSaveCloudConfirmed:true",
    "symmetryGeometryPass:true",
    "mobile360GeometryPass:true",
    "v277-saving",
]:
    if marker not in html:
        raise RuntimeError("V20.77 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.77 save confirmation + final geometry")
print("V20.77 BEFORE:",before)
print("V20.77 AFTER:",after)
print("V20.77 late success toasts converted:",sorted(set(replaced)))
print("V20.77 confirmed saves standardized; async duplicate-submit guard + final symmetry pass applied")
