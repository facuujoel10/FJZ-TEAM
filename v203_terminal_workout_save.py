import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# V20.3: once a workout is committed locally, the save flow is terminal.
complete_old="""    if(!hasMissing){
      saveSessionV106(pack);
      return;
    }"""
complete_new="""    if(!hasMissing){
      saveSessionV106(pack);
      window.__fjzCloseWorkoutFlowV203?.(pack.d.id);
      return;
    }"""
if html.count(complete_old)!=1:
    raise RuntimeError(f"V20.3 complete-session branch mismatch: {html.count(complete_old)}")
html=html.replace(complete_old,complete_new,1)

partial_old="""    closeModal();
    saveSessionV106(pack);
  };"""
partial_new="""    closeModal();
    saveSessionV106(pack);
    window.__fjzCloseWorkoutFlowV203?.(pack.d.id);
  };"""
if html.count(partial_old)!=1:
    raise RuntimeError(f"V20.3 partial-session branch mismatch: {html.count(partial_old)}")
html=html.replace(partial_old,partial_new,1)

js=r"""
<script id="v203TerminalWorkoutSaveRuntime">
(function(){
  const VERSION='20.3';
  let committedDayV203=null;
  let committedAtV203=0;

  window.__fjzCloseWorkoutFlowV203=function(dayId){
    committedDayV203=dayId||null;
    committedAtV203=Date.now();

    window.__v106PendingSession=null;
    window.__fjzPendingSavedSessionV190=null;

    try{
      if(dayId)clearDraftV145?.(dayId,true);
      workoutDraft={};
      window.__fjzMethodDraftV110={};
    }catch(_e){}

    try{closeModal?.()}catch(_e){}
    studentTab='home';
    render();
    toast('Sesión guardada');
  };

  // Final guard for stale buttons/clicks after the session was already committed.
  const baseFinishV203=window.finishWorkout||globalThis.finishWorkout;
  if(typeof baseFinishV203==='function'){
    const wrapped=function(){
      const d=student?.()?.days?.[currentDay];
      if(committedDayV203&&d?.id===committedDayV203&&Date.now()-committedAtV203<60000){
        window.__v106PendingSession=null;
        try{closeModal?.()}catch(_e){}
        studentTab='home';
        render();
        toast('La sesión ya fue guardada');
        return;
      }
      return baseFinishV203.apply(this,arguments);
    };
    window.finishWorkout=wrapped;
    try{finishWorkout=wrapped}catch(_e){}
  }

  const basePartialV203=window.confirmPartialSessionV106;
  if(typeof basePartialV203==='function'){
    const wrapped=function(){
      const d=student?.()?.days?.[currentDay];
      if(committedDayV203&&d?.id===committedDayV203&&Date.now()-committedAtV203<60000){
        window.__v106PendingSession=null;
        try{closeModal?.()}catch(_e){}
        studentTab='home';
        render();
        toast('La sesión ya fue guardada');
        return;
      }
      return basePartialV203.apply(this,arguments);
    };
    window.confirmPartialSessionV106=wrapped;
  }

  // Starting a genuinely new workout is the only thing that re-arms saving.
  const baseStartV203=window.startWorkout||globalThis.startWorkout;
  if(typeof baseStartV203==='function'){
    const wrapped=function(){
      committedDayV203=null;
      committedAtV203=0;
      window.__v106PendingSession=null;
      return baseStartV203.apply(this,arguments);
    };
    window.startWorkout=wrapped;
    try{startWorkout=wrapped}catch(_e){}
  }

  window.__fjzV203={
    version:VERSION,
    saveFlowTerminal:true,
    partialAcceptClosesImmediately:true,
    completeSaveClosesImmediately:true,
    staleSaveButtonBlocked:true
  };
})();
</script>
"""

html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "saveFlowTerminal:true",
  "partialAcceptClosesImmediately:true",
  "completeSaveClosesImmediately:true",
  "staleSaveButtonBlocked:true"
]:
    if marker not in html:
        raise RuntimeError("V20.3 missing "+marker)

if "saveSessionV106(pack);\n      window.__fjzCloseWorkoutFlowV203?.(pack.d.id);" not in html:
    raise RuntimeError("V20.3 terminal complete-save call missing")
if "saveSessionV106(pack);\n    window.__fjzCloseWorkoutFlowV203?.(pack.d.id);" not in html:
    raise RuntimeError("V20.3 terminal partial-save call missing")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.3 terminal workout save flow enabled")
