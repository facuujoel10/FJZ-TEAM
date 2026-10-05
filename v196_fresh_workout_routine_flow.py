import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V19.6 FRESH WORKOUT LOADS + ROUTINE BUILDER STABILITY
# =========================================================

# 1) Previous session weight is reference only: never prefill a fresh workout.
old_prev="""  function previousLoadV147(e,i){
    const prev=latestHistory(e)?.sets||[];
    const row=prev[i]||prev[prev.length-1]||null;
    return Number(row?.[0])||0;
  }"""
new_prev="""  function previousLoadV147(e,i){
    // V19.6: previous load is visible as history/reference only.
    // A new session must start with an empty Kg field.
    return 0;
  }"""
if html.count(old_prev)!=1:
    raise RuntimeError(f"V19.6 expected one previousLoadV147, got {html.count(old_prev)}")
html=html.replace(old_prev,new_prev,1)

# Make the visible history wording explicit.
html=html.replace(
    "<strong>Última sesión:</strong>",
    "<strong>Referencia última sesión:</strong>",
    1
)

# 2) Old autosave drafts should not silently become a new week's workout.
resume_old="""  window.resumeWorkoutDraftV145=function(dayId){
    const s=student();
    const i=(s.days||[]).findIndex(d=>d.id===dayId);
    if(i<0)return;
    startWorkout(i);
  };"""
resume_new="""  window.resumeWorkoutDraftV145=function(dayId){
    const s=student();
    const i=(s.days||[]).findIndex(d=>d.id===dayId);
    if(i<0)return;
    window.__fjzForceResumeDraftV196=dayId;
    startWorkout(i);
  };"""
if html.count(resume_old)!=1:
    raise RuntimeError(f"V19.6 expected one resume draft function, got {html.count(resume_old)}")
html=html.replace(resume_old,resume_new,1)

start_old="""  startWorkout=function(i){
    const p=restoreDraftV145(i);
    currentDay=i;
    workoutDraft=p?safeCloneV145(p.workoutDraft||{}):{};
    window.__fjzMethodDraftV110=p?safeCloneV145(p.methodDraft||{}):{};
    studentTab='workout';
    render();
    if(p){
      setStatusV145(p.updatedAt);
      toast('Recuperamos tu entrenamiento guardado');
    }
  };"""
start_new="""  startWorkout=function(i){
    let p=restoreDraftV145(i);
    const d=student()?.days?.[i];
    const force=!!(d?.id&&window.__fjzForceResumeDraftV196===d.id);
    window.__fjzForceResumeDraftV196=null;

    if(p&&!force){
      const age=Date.now()-(Date.parse(p.updatedAt||0)||0);
      // Recent interruptions are recovered automatically. Older drafts remain
      // available from "Continuar entrenamiento", but never populate a new week.
      if(!Number.isFinite(age)||age>18*60*60*1000)p=null;
    }

    currentDay=i;
    workoutDraft=p?safeCloneV145(p.workoutDraft||{}):{};
    window.__fjzMethodDraftV110=p?safeCloneV145(p.methodDraft||{}):{};
    studentTab='workout';
    render();
    if(p){
      setStatusV145(p.updatedAt);
      toast(force?'Continuamos tu entrenamiento guardado':'Recuperamos tu entrenamiento reciente');
    }
  };"""
if html.count(start_old)!=1:
    raise RuntimeError(f"V19.6 expected one V145 startWorkout wrapper, got {html.count(start_old)}")
html=html.replace(start_old,start_new,1)

css=r"""
<style id="v196FreshWorkoutRoutineFlowStyles">
.v196-prev-reference{
  margin:7px 0 10px;
  padding:7px 9px;
  border:1px solid rgba(90,167,255,.18);
  border-radius:9px;
  background:rgba(90,167,255,.035);
  font-size:9px;
  color:var(--muted);
}
.v196-prev-reference strong{color:var(--text)}

.modal.v196-routine-builder .modal-head{
  position:sticky;
  top:0;
  z-index:3;
  background:#0f0f12;
  padding-bottom:8px;
}
.modal.v196-routine-builder .library-item{
  touch-action:manipulation;
}
.modal.v196-routine-builder button{
  touch-action:manipulation;
}
</style>
"""

js=r"""
<script id="v196FreshWorkoutRoutineFlowRuntime">
(function(){
  const VERSION='19.6';
  let routineBuilderV196=false;
  let routineDayV196=null;

  function modalV196(){return document.getElementById('modal')}
  function wrapV196(){return document.getElementById('modalWrap')}

  function markRoutineModalV196(){
    const m=modalV196();
    if(!m)return;
    m.classList.toggle('v196-routine-builder',!!routineBuilderV196);
  }

  // Routine library/editor becomes a protected interaction flow.
  const baseOpenLibraryV196=window.openLibrary||globalThis.openLibrary;
  if(typeof baseOpenLibraryV196==='function'){
    const wrapped=function(dayIndex){
      routineBuilderV196=true;
      routineDayV196=dayIndex;
      const out=baseOpenLibraryV196.apply(this,arguments);
      markRoutineModalV196();
      return out;
    };
    window.openLibrary=wrapped;
    try{openLibrary=wrapped}catch(_e){}
  }

  const baseConfigureV196=window.configureExercise||globalThis.configureExercise;
  if(typeof baseConfigureV196==='function'){
    const wrapped=function(dayIndex,id){
      routineBuilderV196=true;
      routineDayV196=dayIndex;
      const out=baseConfigureV196.apply(this,arguments);
      markRoutineModalV196();
      return out;
    };
    window.configureExercise=wrapped;
    try{configureExercise=wrapped}catch(_e){}
  }

  const baseCustomV196=window.customExercise||globalThis.customExercise;
  if(typeof baseCustomV196==='function'){
    const wrapped=function(di){
      routineBuilderV196=true;
      routineDayV196=di;
      const out=baseCustomV196.apply(this,arguments);
      markRoutineModalV196();
      return out;
    };
    window.customExercise=wrapped;
    try{customExercise=wrapped}catch(_e){}
  }

  const baseEditV196=window.editExercise||globalThis.editExercise;
  if(typeof baseEditV196==='function'){
    const wrapped=function(di,ei){
      routineBuilderV196=true;
      routineDayV196=di;
      const out=baseEditV196.apply(this,arguments);
      markRoutineModalV196();
      return out;
    };
    window.editExercise=wrapped;
    try{editExercise=wrapped}catch(_e){}
  }

  // The base app closes modals when tapping the dark backdrop. While building
  // a routine that is too easy to trigger accidentally on mobile, so only the
  // explicit X/Cancel/Save controls may close it.
  const w=wrapV196();
  if(w){
    w.onclick=function(e){
      if(e.target!==w)return;
      if(routineBuilderV196){
        e.preventDefault();
        e.stopPropagation();
        return false;
      }
      closeModal();
    };
  }

  const baseCloseV196=window.closeModal||globalThis.closeModal;
  if(typeof baseCloseV196==='function'){
    const wrapped=function(){
      const out=baseCloseV196.apply(this,arguments);
      routineBuilderV196=false;
      routineDayV196=null;
      markRoutineModalV196();
      return out;
    };
    window.closeModal=wrapped;
    try{closeModal=wrapped}catch(_e){}
  }

  // Add a safe back path from "Agregar ejercicio" to the library instead of
  // forcing the coach to close the whole flow.
  const baseShowExerciseV196=window.showExerciseForm||globalThis.showExerciseForm;
  if(typeof baseShowExerciseV196==='function'){
    const wrapped=function(dayIndex,exIndex,e){
      routineBuilderV196=true;
      routineDayV196=dayIndex;
      const out=baseShowExerciseV196.apply(this,arguments);
      markRoutineModalV196();

      if(exIndex==null){
        const head=modalV196()?.querySelector('.modal-head');
        if(head&&!head.querySelector('.v196-back-library')){
          const btn=document.createElement('button');
          btn.className='btn small v196-back-library';
          btn.type='button';
          btn.textContent='← Biblioteca';
          btn.onclick=function(ev){
            ev.preventDefault();
            ev.stopPropagation();
            if(routineDayV196!=null)openLibrary(routineDayV196);
          };
          head.insertBefore(btn,head.lastElementChild);
        }
      }
      return out;
    };
    window.showExerciseForm=wrapped;
    try{showExerciseForm=wrapped}catch(_e){}
  }

  window.__fjzRoutineFlowV196=function(){
    return {active:routineBuilderV196,dayIndex:routineDayV196};
  };

  window.__fjzV196={
    version:VERSION,
    freshWorkoutKgBlank:true,
    previousLoadReferenceOnly:true,
    staleDraftNoAutoResume:true,
    explicitOldDraftResume:true,
    routineBackdropCloseBlocked:true,
    routineLibraryBackButton:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

# Consolidate styles.
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
mergeable=[]
for m in styles:
    attrs=m.group("attrs") or ""
    if re.search(r"\b(media|nonce)\s*=",attrs,re.I):continue
    mergeable.append(m)
if len(mergeable)>1:
    chunks=[]
    for m in mergeable:
        ident=re.search(r'id=["\']([^"\']+)["\']',m.group("attrs") or "",re.I)
        name=ident.group(1) if ident else "anonymous"
        chunks.append("\n/* --- "+name+" --- */\n"+m.group("body").strip())
    for m in reversed(mergeable):
        html=html[:m.start()]+html[m.end():]
    html=html.replace("</head>",'<style id="fjzProductionStylesV196">'+''.join(chunks)+'\n</style>\n</head>',1)

critical=[
  "freshWorkoutKgBlank:true",
  "previousLoadReferenceOnly:true",
  "staleDraftNoAutoResume:true",
  "routineBackdropCloseBlocked:true",
  "window.__fjzForceResumeDraftV196=dayId",
  "function previousLoadV147(e,i)",
  "__fjzConfirmSessionSavedV190"
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V19.6 missing critical markers: "+repr(missing))
if "return Number(row?.[0])||0;" in html:
    raise RuntimeError("V19.6 previous weight autofill still present")
if len(re.findall(r"<style\b",html,re.I))!=1:
    raise RuntimeError("V19.6 expected one final stylesheet")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V19.6 fresh workout loads + routine builder stability enabled")
