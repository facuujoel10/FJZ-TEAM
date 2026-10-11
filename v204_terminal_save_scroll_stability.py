import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.4 FINAL WORKOUT CLOSURE + ZERO-JUMP EXERCISE REORDER
# =========================================================

# Route both base save branches directly to the new terminal authority.
n_close=html.count("window.__fjzCloseWorkoutFlowV203?.(pack.d.id);")
if n_close!=2:
    raise RuntimeError(f"V20.4 expected 2 V20.3 close calls, got {n_close}")
html=html.replace(
    "window.__fjzCloseWorkoutFlowV203?.(pack.d.id);",
    "window.__fjzCloseWorkoutFlowV204?.(pack.d.id);"
)

# Remove the old terminal runtime so it cannot wrap finish/confirm again.
html,n_old=re.subn(
    r'<script id="v203TerminalWorkoutSaveRuntime">.*?</script>\s*',
    '',
    html,
    count=1,
    flags=re.S
)
if n_old!=1:
    raise RuntimeError(f"V20.4 expected one V20.3 runtime, got {n_old}")

js=r"""
<script id="v204WorkoutClosureReorderRuntime">
(function(){
  const VERSION='20.4';
  let closedV204=null;
  let reorderBusyV204=false;

  function safeCloneV204(x){
    try{return JSON.parse(JSON.stringify(x))}catch(_e){return x}
  }

  function pageScrollV204(){
    return {
      y:window.scrollY||document.documentElement.scrollTop||document.body.scrollTop||0,
      view:document.getElementById('view')?.scrollTop||0,
      body:document.getElementById('coachStudentBody')?.scrollTop||0
    };
  }

  function restoreScrollV204(pos){
    if(!pos)return;
    const apply=()=>{
      window.scrollTo(0,pos.y);
      const v=document.getElementById('view');
      const b=document.getElementById('coachStudentBody');
      if(v)v.scrollTop=pos.view;
      if(b)b.scrollTop=pos.body;
    };
    requestAnimationFrame(()=>{
      apply();
      requestAnimationFrame(apply);
    });
    setTimeout(apply,60);
  }

  function athleteIdV204(s){
    if(!s)return null;
    if(currentProfile?.role==='student')return linkedAthleteId||null;
    return cloudAthletes?.get?.(s.id)?.id||null;
  }

  async function persistOrderV204(s,day){
    const aid=athleteIdV204(s);
    if(!aid||!day||!supabaseClient)return false;
    const order=(day.exercises||[]).map(e=>String(e.uid));
    const {error}=await supabaseClient.rpc('reorder_athlete_exercises',{
      p_athlete_id:aid,
      p_day_id:String(day.id),
      p_order:order
    });
    if(error)throw error;
    return true;
  }

  // -------------------------------------------------------
  // EXERCISE REORDER: exact scroll preservation + atomic RPC.
  // This replaces the V11.3 modal path that previously did
  // splice -> saveState -> closeModal -> render and caused a jump.
  // -------------------------------------------------------
  window.confirmMoveExerciseV113=async function(di,ei){
    if(reorderBusyV204)return;
    const s=student?.();
    const d=s?.days?.[di];
    const a=d?.exercises;
    if(!s||!d||!a||!a[ei])return;

    let target=Number(el('v113MovePos')?.value);
    if(!Number.isInteger(target)||target<0||target>=a.length)return;
    if(target===ei){closeModal();return}

    const scroll=pageScrollV204();
    reorderBusyV204=true;
    window.__fjzRoutineSavingV200=true;
    try{cloudLastWrite=Date.now()}catch(_e){}

    const [item]=a.splice(ei,1);
    a.splice(target,0,item);

    // Persist locally without starting the old broad sync.
    const prevApplying=window.__fjzCloudApplying;
    window.__fjzCloudApplying=true;
    try{saveState()}finally{window.__fjzCloudApplying=prevApplying}

    closeModal();
    render();
    restoreScrollV204(scroll);
    toast('Ejercicio movido a la posición '+(target+1));

    try{
      await window.__fjzEnsureFreshAuthV194?.(false);
      await persistOrderV204(s,d);
      try{cloudLastWrite=Date.now()}catch(_e){}
    }catch(e){
      console.warn('TEAM FJZ V20.4 reorder pending',e);
      // Local order remains authoritative; fallback sync is background only.
      setTimeout(()=>window.syncCloudNow?.().catch(()=>{}),250);
    }finally{
      reorderBusyV204=false;
      window.__fjzRoutineSavingV200=false;
      restoreScrollV204(scroll);
    }
  };

  // -------------------------------------------------------
  // WORKOUT SAVE: once accepted, the workout is CLOSED.
  // No later render/wrapper/realtime event may put the user back
  // into the just-saved workout.
  // -------------------------------------------------------
  function markClosedV204(dayId){
    const s=student?.();
    const last=window.__fjzLastLocalSessionV201;
    const sessionId=last?.sessionId||(s?.sessions||[]).at(-1)?.id||null;
    closedV204={
      studentId:s?.id||null,
      dayId:dayId||last?.dayId||null,
      sessionId,
      at:Date.now()
    };
    window.__fjzWorkoutClosedV204=safeCloneV204(closedV204);
  }

  function sameClosedDayV204(){
    if(!closedV204)return false;
    const s=student?.();
    const d=s?.days?.[currentDay];
    return !!(
      s&&d&&
      closedV204.studentId===s.id&&
      closedV204.dayId===d.id
    );
  }

  window.__fjzCloseWorkoutFlowV204=function(dayId){
    markClosedV204(dayId);

    // Destroy every path that can reopen the current save flow.
    window.__v106PendingSession=null;
    window.__fjzPendingSavedSessionV190=null;
    window.__fjzPendingDraftClearV190=null;

    try{
      if(dayId)clearDraftV145?.(dayId,true);
      workoutDraft={};
      window.__fjzMethodDraftV110={};
    }catch(_e){}

    try{closeModal?.()}catch(_e){}
    studentTab='home';
    render();
    toast('Sesión guardada');

    // Keep currentDay valid until older synchronous wrappers finish attaching
    // method logs, then invalidate the old workout completely.
    setTimeout(()=>{
      if(studentTab!=='workout')currentDay=-1;
      try{closeModal?.()}catch(_e){}
    },0);
  };

  // Absolute rendering guard. Even if an old wrapper or realtime callback
  // tries to render the workout again, a closed session stays on Home.
  const baseRenderStudentV204=window.renderStudent||globalThis.renderStudent;
  if(typeof baseRenderStudentV204==='function'){
    const wrapped=function(){
      if(studentTab==='workout'&&sameClosedDayV204()){
        studentTab='home';
      }
      return baseRenderStudentV204.apply(this,arguments);
    };
    window.renderStudent=wrapped;
    try{renderStudent=wrapped}catch(_e){}
  }

  const baseRenderWorkoutV204=window.renderWorkout||globalThis.renderWorkout;
  if(typeof baseRenderWorkoutV204==='function'){
    const wrapped=function(){
      if(sameClosedDayV204()){
        studentTab='home';
        return (window.renderStudent||globalThis.renderStudent)?.();
      }
      return baseRenderWorkoutV204.apply(this,arguments);
    };
    window.renderWorkout=wrapped;
    try{renderWorkout=wrapped}catch(_e){}
  }

  // Final click guards.
  const baseFinishV204=window.finishWorkout||globalThis.finishWorkout;
  if(typeof baseFinishV204==='function'){
    const wrapped=function(){
      if(sameClosedDayV204()){
        window.__v106PendingSession=null;
        try{closeModal?.()}catch(_e){}
        studentTab='home';
        render();
        toast('La sesión ya fue guardada');
        return;
      }
      return baseFinishV204.apply(this,arguments);
    };
    window.finishWorkout=wrapped;
    try{finishWorkout=wrapped}catch(_e){}
  }

  const basePartialV204=window.confirmPartialSessionV106;
  if(typeof basePartialV204==='function'){
    const wrapped=function(){
      if(sameClosedDayV204()){
        window.__v106PendingSession=null;
        try{closeModal?.()}catch(_e){}
        studentTab='home';
        render();
        toast('La sesión ya fue guardada');
        return;
      }
      return basePartialV204.apply(this,arguments);
    };
    window.confirmPartialSessionV106=wrapped;
  }

  // Only explicitly starting a new workout re-arms the save flow.
  const baseStartV204=window.startWorkout||globalThis.startWorkout;
  if(typeof baseStartV204==='function'){
    const wrapped=function(){
      closedV204=null;
      window.__fjzWorkoutClosedV204=null;
      window.__v106PendingSession=null;
      return baseStartV204.apply(this,arguments);
    };
    window.startWorkout=wrapped;
    try{startWorkout=wrapped}catch(_e){}
  }

  window.__fjzV204={
    version:VERSION,
    savedWorkoutCannotReopen:true,
    saveAcceptanceIsTerminal:true,
    staleSaveStateDestroyed:true,
    moveExerciseKeepsExactScroll:true,
    modalReorderUsesAtomicRpc:true
  };
})();
</script>
"""

html=html.replace("</body>",js+"\n</body>",1)

critical=[
  "savedWorkoutCannotReopen:true",
  "saveAcceptanceIsTerminal:true",
  "staleSaveStateDestroyed:true",
  "moveExerciseKeepsExactScroll:true",
  "modalReorderUsesAtomicRpc:true"
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.4 missing critical markers: "+repr(missing))

if "window.__fjzCloseWorkoutFlowV203?.(pack.d.id);" in html:
    raise RuntimeError("V20.4 old terminal close calls remain")
if 'id="v203TerminalWorkoutSaveRuntime"' in html:
    raise RuntimeError("V20.4 old terminal runtime remains")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.4 terminal save + zero-jump reorder enabled")
print("TEAM FJZ V20.4 old terminal runtime removed:",n_old)
print("TEAM FJZ V20.4 save close calls rerouted:",n_close)
