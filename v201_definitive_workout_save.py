import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.1 DEFINITIVE WORKOUT SAVE + EMPTY LOAD INPUTS
# =========================================================

# ---------------------------------------------------------
# 1) The workout row renderer must never use previous history as
#    the input value. History remains visible only in the reference note.
# ---------------------------------------------------------
old_vals="const vals=draft||p;"
new_vals="""const vals=draft||[
  0,
  (e?.repMode==='exact'&&Array.isArray(e.repsExact)&&e.repsExact.length
    ? Number(e.repsExact[si]??e.repsExact[e.repsExact.length-1])
    : Number(e.min||1)),
  Number(e.rirMax??e.rirMin??2)
];"""
n_vals=html.count(old_vals)
if n_vals<1:
    raise RuntimeError("V20.1 could not find previous-load renderer fallback")
html=html.replace(old_vals,new_vals)

# Replace the base draft helpers too, so no historical load can be copied
# later when the first field is edited.
pat_ensure=re.compile(
    r"""function ensureDraft\(e\)\{if\(!workoutDraft\[e\.uid\]\)\{const prev=baselineSets\(e\);workoutDraft\[e\.uid\]=Array\.from\(\{length:e\.sets\},\(_,i\)=>\[\.\.\.\(prev\[i\]\|\|prev\[prev\.length-1\]\|\|\[0,e\.min,e\.rirMax\]\)\]\)\}return workoutDraft\[e\.uid\]\}"""
)
repl_ensure="""function ensureDraft(e){if(!workoutDraft[e.uid]){workoutDraft[e.uid]=Array.from({length:e.sets},(_,i)=>[0,(e?.repMode==='exact'&&Array.isArray(e.repsExact)&&e.repsExact.length?Number(e.repsExact[i]??e.repsExact[e.repsExact.length-1]):Number(e.min||1)),Number(e.rirMax??e.rirMin??2)])}return workoutDraft[e.uid]}"""
html,n_ensure=pat_ensure.subn(repl_ensure,html,count=1)
if n_ensure!=1:
    raise RuntimeError(f"V20.1 ensureDraft replacement mismatch: {n_ensure}")

pat_current=re.compile(
    r"""function currentSets\(e\)\{return workoutDraft\[e\.uid\]\|\|Array\.from\(\{length:e\.sets\},\(_,i\)=>\{const prev=baselineSets\(e\);return \[\.\.\.\(prev\[i\]\|\|prev\[prev\.length-1\]\|\|\[0,e\.min,e\.rirMax\]\)\]\}\)\}"""
)
repl_current="""function currentSets(e){return workoutDraft[e.uid]||Array.from({length:e.sets},(_,i)=>[0,(e?.repMode==='exact'&&Array.isArray(e.repsExact)&&e.repsExact.length?Number(e.repsExact[i]??e.repsExact[e.repsExact.length-1]):Number(e.min||1)),Number(e.rirMax??e.rirMin??2)])}"""
html,n_current=pat_current.subn(repl_current,html,count=1)
if n_current!=1:
    raise RuntimeError(f"V20.1 currentSets replacement mismatch: {n_current}")

# ---------------------------------------------------------
# 2) Replace the blocking V19.0 async session save with an immediate
#    local commit. Cloud persistence is queued after all synchronous
#    wrappers (method logs, autosave hooks) finish.
# ---------------------------------------------------------
save_pat=re.compile(
    r"""  async function saveSessionV106\(pack\)\{.*?\n  \}\n\n  window\.finishWorkout=function\(\)\{""",
    re.S
)
save_repl=r"""  function saveSessionV106(pack){
    const {s,d,registered,skipped}=pack;
    let up=0,hold=0,review=0,partial=0,totalSets=0,completedExercises=0;
    const exerciseResults=[];

    registered.forEach(({e,sets,setIndexes,complete})=>{
      let r;
      if(complete){
        r=currentRecommendation(e);
        completedExercises++;
        const baseType=r.type==='override'?(r.auto?.type||'hold'):r.type;
        if(['up','rep','load'].includes(baseType))up++;
        else if(['down','plateau'].includes(baseType))review++;
        else hold++;
        e.history=e.history||[];
        e.history.push({
          date:nowISO(),
          sets:sets.map(x=>[...x]),
          target:targetSigV106(e),
          recommendation:clone(r),
          loadMode:loadModeV106(e)
        });
      }else{
        partial++;
        r={
          type:'partial',
          title:'Registro parcial',
          copy:'Se guardaron '+sets.length+' de '+e.sets+' series. No se actualizó la recomendación automática de este ejercicio.'
        };
      }
      totalSets+=sets.length;
      exerciseResults.push({
        exerciseUid:e.uid,
        name:e.name,
        sets:sets.map(x=>[...x]),
        setIndexes:[...setIndexes],
        completed:complete,
        recommendation:clone(r),
        loadMode:loadModeV106(e)
      });
    });

    const session={
      id:uid('ss'),
      date:nowISO(),
      dayId:d.id,
      dayName:d.name,
      summary:{
        up,hold,review,partial,totalSets,
        completedExercises,
        registeredExercises:registered.length,
        skippedExercises:skipped.length,
        totalExercises:d.exercises.length
      },
      skippedExerciseNames:skipped.map(e=>e.name),
      exerciseResults
    };

    s.sessions=s.sessions||[];

    /* Hard idempotency inside the snapshot: never append the same session id twice. */
    if(!s.sessions.some(x=>x?.id===session.id))s.sessions.push(session);
    s.lastWorkout=session.date;

    /* Suppress the expensive general cloud sync during this synchronous commit.
       Outer wrappers still get to attach method logs before the queued targeted
       write executes on the next task. */
    const previousApplying=window.__fjzCloudApplying;
    window.__fjzCloudApplying=true;
    try{saveState()}finally{}

    window.__fjzLastLocalSessionV201={sessionId:session.id,dayId:d.id,at:Date.now()};
    window.__fjzSessionCloudConfirmedId=null;

    setTimeout(()=>{
      window.__fjzCloudApplying=previousApplying;
      try{
        clearDraftV145?.(d.id,true);
        workoutDraft={};
      }catch(_e){}
      window.__fjzQueueSessionSyncV201?.(session,d.id);
    },0);

    return session;
  }

  window.finishWorkout=function(){"""
html,n_save=save_pat.subn(save_repl,html,count=1)
if n_save!=1:
    raise RuntimeError(f"V20.1 saveSessionV106 replacement mismatch: {n_save}")

css=r"""
<style id="v201WorkoutSaveStyles">
body.v201-session-committed button[onclick*="finishWorkout"],
body.v201-session-committed button[onclick*="confirmPartialSessionV106"]{
  pointer-events:none!important;
  opacity:.68!important;
}
</style>
"""

js=r"""
<script id="v201WorkoutSaveRuntime">
(function(){
  const VERSION='20.1';
  const PENDING_KEY='fjz_v201_pending_session';
  let syncPromiseV201=null;
  let retryTimerV201=0;

  function cloneV201(x){
    return x==null?x:JSON.parse(JSON.stringify(x));
  }

  function currentAthleteIdV201(){
    const s=student?.();
    if(!s)return null;
    if(currentProfile?.role==='student')return linkedAthleteId||null;
    return cloudAthletes?.get?.(s.id)?.id||null;
  }

  function pendingV201(){
    try{return JSON.parse(localStorage.getItem(PENDING_KEY)||'null')}catch(_e){return null}
  }

  function savePendingV201(session,dayId){
    try{
      localStorage.setItem(PENDING_KEY,JSON.stringify({
        userId:currentUser?.id||null,
        studentId:student?.()?.id||null,
        athleteId:currentAthleteIdV201(),
        sessionId:session?.id||null,
        dayId:dayId||null,
        at:new Date().toISOString()
      }));
    }catch(_e){}
  }

  function clearPendingV201(sessionId){
    const p=pendingV201();
    if(!p||!sessionId||p.sessionId===sessionId){
      try{localStorage.removeItem(PENDING_KEY)}catch(_e){}
    }
  }

  async function persistSelectedSnapshotV201(session,dayId){
    if(!session?.id)return false;
    if(syncPromiseV201)return syncPromiseV201;

    savePendingV201(session,dayId);
    document.body?.classList.add('v201-session-committed');

    syncPromiseV201=(async()=>{
      try{
        await window.__fjzEnsureFreshAuthV194?.(false);

        const s=student?.();
        const athleteId=currentAthleteIdV201();
        if(!s||!athleteId||!supabaseClient)throw new Error('Ficha o nube no disponible');

        /* V20.2 fast path: send only the completed session + affected
           routine day. The RPC atomically merges both into the snapshot and
           the optimized trigger normalizes only this changed session. */
        const day=(s.days||[]).find(x=>x?.id===dayId)||null;
        if(!day)throw new Error('Día de rutina no disponible');

        const {error}=await supabaseClient.rpc('commit_workout_session_v202',{
          p_athlete_id:athleteId,
          p_day_id:String(dayId),
          p_day:cloneV201(day),
          p_session:cloneV201(session)
        });
        if(error)throw error;

        window.__fjzSessionCloudConfirmedId=session.id;
        window.__fjzPendingSavedSessionV190=null;
        window.__fjzPendingDraftClearV190=null;
        clearPendingV201(session.id);
        try{window.setCloudStatus?.('online','Sesión guardada')}catch(_e){}
        return true;
      }catch(e){
        console.warn('TEAM FJZ V20.1 targeted session sync pending',e);
        try{window.setCloudStatus?.('error','Sesión pendiente')}catch(_e){}
        clearTimeout(retryTimerV201);
        retryTimerV201=setTimeout(()=>retryPendingV201('timer'),5000);
        return false;
      }finally{
        syncPromiseV201=null;
        document.body?.classList.remove('v201-session-committed');
      }
    })();

    return syncPromiseV201;
  }

  window.__fjzQueueSessionSyncV201=function(session,dayId){
    /* Start after method-log wrappers finish mutating the newly-created
       session in the current JS task. */
    return persistSelectedSnapshotV201(session,dayId);
  };

  async function retryPendingV201(reason){
    if(syncPromiseV201||navigator.onLine===false)return;
    const p=pendingV201();
    if(!p||!currentUser||p.userId!==currentUser.id)return;

    const s=student?.();
    const session=(s?.sessions||[]).find(x=>x?.id===p.sessionId);
    if(!session){
      clearPendingV201(p.sessionId);
      return;
    }
    try{
      await persistSelectedSnapshotV201(session,p.dayId);
    }catch(e){
      console.warn('TEAM FJZ V20.1 retry '+reason,e);
    }
  }

  window.addEventListener('online',()=>retryPendingV201('online'),{passive:true});
  window.addEventListener('focus',()=>retryPendingV201('focus'),{passive:true});
  document.addEventListener('visibilitychange',()=>{
    if(document.visibilityState==='visible')retryPendingV201('visible');
  },{passive:true});

  /* Final duplicate guard: once the local commit happened, repeated taps or
     a stale success/partial modal cannot append another session. */
  const baseFinishV201=window.finishWorkout||globalThis.finishWorkout;
  if(typeof baseFinishV201==='function'){
    const wrapped=function(){
      const s=student?.(),d=s?.days?.[currentDay];
      const last=window.__fjzLastLocalSessionV201;
      if(last&&last.dayId===d?.id&&Date.now()-Number(last.at||0)<30000){
        studentTab='home';
        closeModal?.();
        render();
        toast('La sesión ya fue guardada');
        return;
      }
      const out=baseFinishV201.apply(this,arguments);
      const nowLast=window.__fjzLastLocalSessionV201;
      if(nowLast&&nowLast.dayId===d?.id){
        closeModal?.();
        studentTab='home';
        render();
        toast('Sesión guardada');
      }
      return out;
    };
    window.finishWorkout=wrapped;
    try{finishWorkout=wrapped}catch(_e){}
  }

  const basePartialV201=window.confirmPartialSessionV106;
  if(typeof basePartialV201==='function'){
    const wrapped=function(){
      const s=student?.(),d=s?.days?.[currentDay];
      const last=window.__fjzLastLocalSessionV201;
      if(last&&last.dayId===d?.id&&Date.now()-Number(last.at||0)<30000){
        closeModal?.();
        studentTab='home';
        render();
        toast('La sesión ya fue guardada');
        return;
      }
      const out=basePartialV201.apply(this,arguments);
      const nowLast=window.__fjzLastLocalSessionV201;
      if(nowLast&&nowLast.dayId===d?.id){
        closeModal?.();
        studentTab='home';
        render();
        toast('Sesión guardada');
      }
      return out;
    };
    window.confirmPartialSessionV106=wrapped;
  }

  const baseStartV201=window.startWorkout||globalThis.startWorkout;
  if(typeof baseStartV201==='function'){
    const wrapped=function(){
      window.__fjzLastLocalSessionV201=null;
      return baseStartV201.apply(this,arguments);
    };
    window.startWorkout=wrapped;
    try{startWorkout=wrapped}catch(_e){}
  }

  setTimeout(()=>retryPendingV201('boot'),1200);

  window.__fjzV201={
    version:VERSION,
    weightInputsNeverUseHistory:true,
    baseDraftNeverCopiesHistory:true,
    sessionLocalCommitImmediate:true,
    targetedAthleteSnapshotWrite:true,
    compactSessionRpc:true,
    incrementalSessionTrigger:true,
    noBlockingCloudConfirmation:true,
    repeatedSaveGuard:true,
    pendingSessionRetry:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

# Consolidate styles once more.
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
    html=html.replace("</head>",'<style id="fjzProductionStylesV201">'+''.join(chunks)+'\n</style>\n</head>',1)

critical=[
  "weightInputsNeverUseHistory:true",
  "sessionLocalCommitImmediate:true",
  "targetedAthleteSnapshotWrite:true",
  "noBlockingCloudConfirmation:true",
  "repeatedSaveGuard:true",
  "pendingSessionRetry:true"
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.1 missing critical markers: "+repr(missing))

if "const vals=draft||p;" in html:
    raise RuntimeError("V20.1 historical load fallback still exists")
if "async function saveSessionV106(pack)" in html:
    raise RuntimeError("V20.1 blocking async saveSessionV106 still exists")
if "const cloudConfirmed=await window.__fjzConfirmSessionSavedV190" in html:
    raise RuntimeError("V20.1 V19.0 blocking confirmation still exists")
if len(re.findall(r"<style\b",html,re.I))!=1:
    raise RuntimeError("V20.1 expected one final stylesheet")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.1 definitive workout save + empty load inputs enabled")
print("TEAM FJZ V20.1 historical input fallbacks replaced:",n_vals)
print("TEAM FJZ V20.1 base draft helpers replaced:",n_ensure,n_current)
print("TEAM FJZ V20.1 blocking save function replaced:",n_save)
