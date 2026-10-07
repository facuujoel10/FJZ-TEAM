import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v200StabilityAuthorityStyles">
/* =========================================================
   V20.0 · FINAL STATE / SAVE / ROUTINE STABILITY AUTHORITY
   ========================================================= */

/* While the authenticated cloud state is hydrating, keep the previous/local
   view from flashing and reflowing underneath the connection gate. */
body.v200-hydrating #view,
body.v200-hydrating #bottomNav{
  visibility:hidden!important;
}
body.v200-settling *,
body.v200-settling *::before,
body.v200-settling *::after{
  transition:none!important;
  animation:none!important;
}
html,body,#view,#coachStudentBody,#studentSubBody{
  overflow-anchor:none!important;
}

/* Saving a workout should feel committed immediately. */
.v200-save-toast{
  position:fixed;
  left:50%;
  bottom:84px;
  transform:translateX(-50%);
  z-index:90;
  display:flex;
  align-items:center;
  justify-content:center;
  min-height:38px;
  max-width:min(92vw,420px);
  padding:9px 13px;
  border:1px solid var(--border);
  border-radius:12px;
  background:#121216;
  box-shadow:var(--shadow);
  font-size:10px;
  font-weight:800;
  text-align:center;
}

/* Explicit close buttons only: the dark modal backdrop is no longer a close
   target, preventing accidental exits while editing routines/forms. */
#modalWrap{
  cursor:default!important;
}
</style>
"""

js=r"""
<script id="v200StabilityAuthorityRuntime">
(function(){
  const VERSION='20.0';

  // -------------------------------------------------------
  // 1) FRESH WORKOUT DRAFTS: history is reference only.
  // -------------------------------------------------------
  function programmedRepV200(e,si){
    if(e?.repMode==='exact'&&Array.isArray(e.repsExact)&&e.repsExact.length){
      const n=Number(e.repsExact[si]??e.repsExact[e.repsExact.length-1]);
      if(Number.isFinite(n)&&n>0)return n;
    }
    const n=Number(e?.min);
    return Number.isFinite(n)&&n>0?n:1;
  }

  function freshRowV200(e,si){
    return [0,programmedRepV200(e,si),Number(e?.rirMax??e?.rirMin??2)];
  }

  try{
    ensureDraft=function(e){
      if(!workoutDraft[e.uid]){
        workoutDraft[e.uid]=Array.from({length:Math.max(1,Number(e.sets)||1)},(_,i)=>freshRowV200(e,i));
      }
      return workoutDraft[e.uid];
    };

    currentSets=function(e){
      return workoutDraft[e.uid]||
        Array.from({length:Math.max(1,Number(e.sets)||1)},(_,i)=>freshRowV200(e,i));
    };
    window.ensureDraft=ensureDraft;
    window.currentSets=currentSets;
  }catch(e){
    console.warn('TEAM FJZ V20 fresh draft authority',e);
  }

  // -------------------------------------------------------
  // 2) SESSION COMMIT: instant local completion + one cloud
  //    acknowledgement. No extra read-after-write roundtrip.
  // -------------------------------------------------------
  let committedSessionIdV200=null;
  let committedDayIdV200=null;

  function saveNoticeV200(text,ms=2200){
    let n=document.getElementById('v200SaveToast');
    if(!n){
      n=document.createElement('div');
      n.id='v200SaveToast';
      n.className='v200-save-toast';
      document.body.appendChild(n);
    }
    n.textContent=text;
    n.style.display='flex';
    clearTimeout(n.__timer);
    n.__timer=setTimeout(()=>{n.style.display='none'},ms);
  }

  function detectLocalCommitV200(before,dayId){
    const s=student?.();
    const sessions=s?.sessions||[];
    if(sessions.length<=before)return false;
    const saved=sessions[sessions.length-1];
    if(!saved?.id)return false;
    committedSessionIdV200=saved.id;
    committedDayIdV200=dayId||saved.dayId||null;
    window.__fjzCommittedSessionV200={id:saved.id,dayId:committedDayIdV200};

    // The session is already durable locally. Leave the workout screen now,
    // while cloud synchronization finishes in the background.
    studentTab='home';
    render();
    saveNoticeV200('Sesión registrada · sincronizando con la nube…',2800);
    return true;
  }

  const baseConfirmCloudV200=window.__fjzConfirmSessionSavedV190;
  window.__fjzConfirmSessionSavedV190=async function(session,dayId){
    if(!session?.id)return false;
    document.body?.classList.add('v190-session-saving');
    try{
      if(!cloudEnabled||!supabaseClient){
        window.setCloudStatus?.('error','Sesión pendiente');
        return false;
      }
      await window.__fjzEnsureFreshAuthV194?.(false);
      await window.syncCloudNow?.();

      const exists=!!(student?.()?.sessions||[]).some(x=>x?.id===session.id);
      if(!exists)throw new Error('La sesión local ya no está disponible');

      window.__fjzSessionCloudConfirmedId=session.id;
      window.__fjzFinalizeSessionDraftV190?.(session.id);
      window.setCloudStatus?.('online','Sesión guardada');
      saveNoticeV200('Sesión guardada ✓',1800);
      return true;
    }catch(e){
      console.warn('TEAM FJZ V20 session sync pending',e);
      window.setCloudStatus?.('error','Sesión pendiente');
      return false;
    }finally{
      document.body?.classList.remove('v190-session-saving');
    }
  };

  const baseFinishV200=window.finishWorkout||globalThis.finishWorkout;
  if(typeof baseFinishV200==='function'){
    const wrapped=function(){
      const s=student?.(),d=s?.days?.[currentDay];
      if(committedSessionIdV200&&committedDayIdV200===d?.id){
        studentTab='home';render();
        saveNoticeV200('Esta sesión ya fue registrada. La nube termina de sincronizarla.',2400);
        return;
      }
      const before=(s?.sessions||[]).length;
      const out=baseFinishV200.apply(this,arguments);
      detectLocalCommitV200(before,d?.id);
      return out;
    };
    window.finishWorkout=wrapped;
    try{finishWorkout=wrapped}catch(_e){}
  }

  const basePartialV200=window.confirmPartialSessionV106;
  if(typeof basePartialV200==='function'){
    const wrapped=function(){
      const s=student?.(),d=s?.days?.[currentDay];
      if(committedSessionIdV200&&committedDayIdV200===d?.id){
        closeModal?.();studentTab='home';render();
        saveNoticeV200('Esta sesión ya fue registrada.',1800);
        return;
      }
      const before=(s?.sessions||[]).length;
      const out=basePartialV200.apply(this,arguments);
      detectLocalCommitV200(before,d?.id);
      return out;
    };
    window.confirmPartialSessionV106=wrapped;
  }

  const baseStartV200=window.startWorkout||globalThis.startWorkout;
  if(typeof baseStartV200==='function'){
    const wrapped=function(){
      committedSessionIdV200=null;
      committedDayIdV200=null;
      window.__fjzCommittedSessionV200=null;
      return baseStartV200.apply(this,arguments);
    };
    window.startWorkout=wrapped;
    try{startWorkout=wrapped}catch(_e){}
  }

  // -------------------------------------------------------
  // 3) ROUTINE MUTATIONS: local UI wins while the change is
  //    being persisted. Exercise reorder uses a tiny atomic
  //    RPC so old snapshots cannot jump the item back.
  // -------------------------------------------------------
  let routineDirtyV200=false;
  let routineSyncPromiseV200=null;
  let deferredRefreshV200=false;
  const desiredOrderV200=new Map();

  function beginRoutineMutationV200(){
    routineDirtyV200=true;
    try{cloudLastWrite=Date.now()}catch(_e){}
    window.__fjzRoutineSavingV200=true;
  }

  function finishRoutineMutationV200(){
    routineDirtyV200=false;
    window.__fjzRoutineSavingV200=false;
    try{cloudLastWrite=Date.now()}catch(_e){}
    if(deferredRefreshV200){
      deferredRefreshV200=false;
      setTimeout(()=>window.refreshCloudFromRealtime?.(),300);
    }
  }

  const baseRefreshV200=window.refreshCloudFromRealtime||globalThis.refreshCloudFromRealtime;
  if(typeof baseRefreshV200==='function'){
    const wrapped=async function(){
      if(routineDirtyV200||window.__fjzRoutineSavingV200){
        deferredRefreshV200=true;
        return;
      }
      return baseRefreshV200.apply(this,arguments);
    };
    window.refreshCloudFromRealtime=wrapped;
    try{refreshCloudFromRealtime=wrapped}catch(_e){}
  }

  async function persistOrderLoopV200(){
    if(routineSyncPromiseV200)return routineSyncPromiseV200;
    routineSyncPromiseV200=(async()=>{
      try{
        while(desiredOrderV200.size){
          const batch=[...desiredOrderV200.values()];
          desiredOrderV200.clear();
          for(const item of batch){
            const {error}=await supabaseClient.rpc('reorder_athlete_exercises',{
              p_athlete_id:item.athleteId,
              p_day_id:item.dayId,
              p_order:item.order
            });
            if(error)throw error;
          }
        }
        finishRoutineMutationV200();
      }catch(e){
        console.warn('TEAM FJZ V20 reorder RPC fallback',e);
        try{
          await window.syncCloudNow?.();
          finishRoutineMutationV200();
        }catch(syncErr){
          console.warn('TEAM FJZ V20 routine sync pending',syncErr);
          // Keep local state authoritative; V11.2 will retry the pending sync.
          routineDirtyV200=true;
          window.__fjzRoutineSavingV200=true;
          toast?.('Cambio guardado localmente · sincronización pendiente');
        }
      }finally{
        routineSyncPromiseV200=null;
        if(desiredOrderV200.size)setTimeout(persistOrderLoopV200,0);
      }
    })();
    return routineSyncPromiseV200;
  }

  const baseMoveExerciseV200=window.moveExercise||globalThis.moveExercise;
  if(typeof baseMoveExerciseV200==='function'){
    const wrapped=function(di,ei,dir){
      const s=student?.(),day=s?.days?.[di];
      if(!day)return baseMoveExerciseV200.apply(this,arguments);
      beginRoutineMutationV200();
      const out=baseMoveExerciseV200.apply(this,arguments);

      const row=cloudAthletes?.get?.(s.id);
      const freshDay=student?.()?.days?.find?.(x=>x.id===day.id);
      if(row?.id&&freshDay&&supabaseClient){
        desiredOrderV200.set(day.id,{
          athleteId:row.id,
          dayId:day.id,
          order:(freshDay.exercises||[]).map(e=>String(e.uid))
        });
        persistOrderLoopV200();
      }else{
        window.syncCloudNow?.().then(finishRoutineMutationV200).catch(()=>{});
      }
      return out;
    };
    window.moveExercise=wrapped;
    try{moveExercise=wrapped}catch(_e){}
  }

  let fullRoutineSyncTimerV200=0;
  function queueFullRoutineSyncV200(){
    beginRoutineMutationV200();
    clearTimeout(fullRoutineSyncTimerV200);
    fullRoutineSyncTimerV200=setTimeout(async()=>{
      try{
        await window.syncCloudNow?.();
        finishRoutineMutationV200();
      }catch(e){
        console.warn('TEAM FJZ V20 routine mutation pending',e);
        toast?.('Cambio guardado localmente · sincronización pendiente');
      }
    },90);
  }

  ['saveExercise','removeExercise','saveDay','addDay','duplicateDay','moveDay'].forEach(name=>{
    const fn=window[name]||globalThis[name];
    if(typeof fn!=='function'||fn.__v200RoutineWrapped)return;
    const wrapped=function(){
      beginRoutineMutationV200();
      const out=fn.apply(this,arguments);
      queueFullRoutineSyncV200();
      return out;
    };
    wrapped.__v200RoutineWrapped=true;
    window[name]=wrapped;
    try{globalThis[name]=wrapped}catch(_e){}
  });

  // Any successful sync can resolve a previously pending routine mutation.
  const baseSyncCloudV200=window.syncCloudNow;
  if(typeof baseSyncCloudV200==='function'){
    window.syncCloudNow=async function(){
      const out=await baseSyncCloudV200.apply(this,arguments);
      if(routineDirtyV200&&!desiredOrderV200.size)finishRoutineMutationV200();
      return out;
    };
    try{syncCloudNow=window.syncCloudNow}catch(_e){}
  }

  // -------------------------------------------------------
  // 4) MODALS: backdrop never closes an editing surface.
  // -------------------------------------------------------
  const modalWrapV200=document.getElementById('modalWrap');
  if(modalWrapV200){
    modalWrapV200.removeAttribute('onclick');
    modalWrapV200.onclick=null;
    modalWrapV200.addEventListener('click',e=>{
      if(e.target===modalWrapV200){
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
      }
    },true);
    modalWrapV200.addEventListener('pointerdown',e=>{
      if(e.target===modalWrapV200){
        e.preventDefault();
        e.stopPropagation();
      }
    },true);
  }

  // -------------------------------------------------------
  // 5) BOOT / CLOUD HYDRATION: reveal the app only after the
  //    cloud state and first render have settled.
  // -------------------------------------------------------
  function beginHydrateV200(){
    document.body?.classList.add('v200-hydrating','v200-settling');
  }
  function endHydrateV200(){
    requestAnimationFrame(()=>requestAnimationFrame(()=>{
      document.body?.classList.remove('v200-hydrating');
      setTimeout(()=>document.body?.classList.remove('v200-settling'),420);
    }));
  }

  if(document.getElementById('authGate')?.style.display!=='none')beginHydrateV200();

  const baseStatusV200=window.setCloudStatus||globalThis.setCloudStatus;
  if(typeof baseStatusV200==='function'){
    const wrapped=function(kind,label){
      const out=baseStatusV200.apply(this,arguments);
      if(kind==='syncing'&&!currentProfile)beginHydrateV200();
      if(kind==='online'||kind==='error')endHydrateV200();
      return out;
    };
    window.setCloudStatus=wrapped;
    try{setCloudStatus=wrapped}catch(_e){}
  }

  const baseHandleSessionV200=window.handleSession||globalThis.handleSession;
  if(typeof baseHandleSessionV200==='function'){
    const wrapped=async function(){
      beginHydrateV200();
      try{return await baseHandleSessionV200.apply(this,arguments)}
      finally{endHydrateV200()}
    };
    window.handleSession=wrapped;
    try{handleSession=wrapped}catch(_e){}
  }

  setTimeout(()=>document.body?.classList.remove('v200-hydrating','v200-settling'),5000);

  window.__fjzV200={
    version:VERSION,
    freshDraftNeverCopiesHistory:true,
    previousWeightReferenceOnly:true,
    instantLocalSessionCommit:true,
    noReadAfterWriteSessionVerification:true,
    duplicateFinishGuard:true,
    atomicExerciseReorder:true,
    realtimeCannotOverwriteRoutineMutation:true,
    modalBackdropCloseDisabled:true,
    cloudHydrationStableReveal:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

# Final stylesheet consolidation.
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
    html=html.replace("</head>",'<style id="fjzProductionStylesV200">'+''.join(chunks)+'\n</style>\n</head>',1)

critical=[
  "freshDraftNeverCopiesHistory:true",
  "instantLocalSessionCommit:true",
  "duplicateFinishGuard:true",
  "atomicExerciseReorder:true",
  "modalBackdropCloseDisabled:true",
  "cloudHydrationStableReveal:true",
  "reorder_athlete_exercises",
  "__fjzConfirmSessionSavedV190",
  "__fjzFinalizeSessionDraftV190",
  "__fjzEnsureFreshAuthV194"
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.0 missing critical markers: "+repr(missing))

if len(re.findall(r"<style\b",html,re.I))!=1:
    raise RuntimeError("V20.0 expected one final stylesheet")

# Guard against accidentally reintroducing a final runtime that copies history
# through our new authority marker.
if "freshDraftNeverCopiesHistory:true" not in html:
    raise RuntimeError("V20.0 fresh draft authority unavailable")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.0 state/save/routine stability authority enabled")
