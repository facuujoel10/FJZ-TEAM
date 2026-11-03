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
        if mid>=0: break
    if mid<0:
        raise RuntimeError("V21.41 missing script "+script_id)
    a=doc.find(">",mid); b=doc.find("</script>",a)
    if a<0 or b<0:
        raise RuntimeError("V21.41 malformed script "+script_id)
    old=doc[a+1:b]
    new=transform(old)
    if new==old:
        raise RuntimeError("V21.41 no changes in "+script_id)
    return doc[:a+1]+new+doc[b:]

before=metrics(html)

for marker in [
    'meta name="fjz-session-input-recovery" content="21.40"',
    'id="v112SyncHardeningRuntime"',
    'id="v146RenderStabilityRuntime"',
    "activeWorkoutFreeze:true",
    "viewScopedRealtime:true",
    "sessionSuccessRequiresDoubleVerification:true",
    "globalSaveIntegrity:true",
    "retryUsesSameSessionId:true",
]:
    if marker not in html:
        raise RuntimeError("V21.41 prerequisite missing "+marker)

# -------------------------------------------------------------------
# 1) The original global save scheduler toggled cloud UI immediately
#    and fired a broad snapshot sync 650 ms after every workout draft
#    cloud save. During a workout this caused repeated whole-snapshot
#    traffic and visible status churn on mobile.
#
#    Keep every local draft write immediate. Only the cloud snapshot
#    scheduler is coalesced while the workout screen is active.
# -------------------------------------------------------------------
old_schedule="""function scheduleCloudSync(){if(!cloudEnabled||!currentUser||!currentProfile)return;clearTimeout(cloudSyncTimer);setCloudStatus('syncing','Sincronizando');cloudSyncTimer=setTimeout(()=>syncCloudNow().catch(e=>{console.error(e);setCloudStatus('error','Error')}),650)}"""

new_schedule="""function scheduleCloudSync(){
  if(!cloudEnabled||!currentUser||!currentProfile)return;
  clearTimeout(cloudSyncTimer);
  const workoutActiveV341=mode==='student'&&studentTab==='workout';
  const delayV341=workoutActiveV341?4200:650;
  if(!workoutActiveV341)setCloudStatus('syncing','Sincronizando');
  try{
    if(workoutActiveV341&&window.__fjzV341WorkoutStability){
      window.__fjzV341WorkoutStability.coalescedWorkoutSchedules++;
      window.__fjzV341WorkoutStability.lastScheduledAt=new Date().toISOString();
    }
  }catch(_e){}
  cloudSyncTimer=setTimeout(()=>{
    try{
      if(workoutActiveV341&&window.__fjzV341WorkoutStability){
        window.__fjzV341WorkoutStability.workoutCloudFlushes++;
        window.__fjzV341WorkoutStability.lastFlushAt=new Date().toISOString();
      }
    }catch(_e){}
    syncCloudNow().catch(e=>{console.error(e);setCloudStatus('error','Error')});
  },delayV341);
}"""

if html.count(old_schedule)!=1:
    raise RuntimeError("V21.41 scheduleCloudSync anchor mismatch: "+str(html.count(old_schedule)))
html=html.replace(old_schedule,new_schedule,1)

# -------------------------------------------------------------------
# 2) V11.2 safely merges remote configuration before a student write.
#    That is correct, but during an active workout it also replaced the
#    in-memory student and rewrote the entire localStorage state after
#    every pre-sync GET. On iPhone that can create a late UI hitch.
#
#    Active workout path:
#      - read remote snapshot
#      - merge remote config + local progress
#      - explicitly preserve the local workout draft
#      - upsert the merged payload directly
#      - DO NOT replace the active in-memory student
#      - DO NOT stringify/write the whole app state again
#
#    Outside an active workout, V11.2 behavior stays unchanged.
# -------------------------------------------------------------------
def patch_v112(body):
    old=r"""  const baseSyncStudentStateV112=window.syncStudentState;
  window.syncStudentState=async function(){
    const local=cloneV112(student());
    if(local&&linkedAthleteId&&supabaseClient){
      try{
        const {data,error}=await supabaseClient
          .from('athlete_snapshots')
          .select('data,updated_at')
          .eq('athlete_id',linkedAthleteId)
          .maybeSingle();
        if(error)throw error;
        if(data?.data){
          const merged=mergeForStudentV112(local,data.data);
          const idx=state.students.findIndex(x=>x.id===local.id);
          if(idx>=0)state.students[idx]=merged;
          writeStateQuietV112();
        }
      }catch(e){
        console.warn('V11.2 pre-sync alumno',e);
      }
    }
    return baseSyncStudentStateV112.apply(this,arguments);
  };"""

    new=r"""  const baseSyncStudentStateV112=window.syncStudentState;

  function activeWorkoutSyncV341(){
    return mode==='student'&&studentTab==='workout'&&currentProfile?.role==='student';
  }

  window.syncStudentState=async function(){
    const local=cloneV112(student());
    if(local&&linkedAthleteId&&supabaseClient){
      try{
        const {data,error}=await supabaseClient
          .from('athlete_snapshots')
          .select('data,updated_at')
          .eq('athlete_id',linkedAthleteId)
          .maybeSingle();
        if(error)throw error;
        if(data?.data){
          const merged=mergeForStudentV112(local,data.data);

          // Workout drafts are transient local progress and must survive the
          // remote-config merge. They were not part of attachProgressV112.
          if(local?.workoutDrafts){
            merged.workoutDrafts=cloneV112(local.workoutDrafts);
          }else if('workoutDrafts' in merged){
            delete merged.workoutDrafts;
          }

          if(activeWorkoutSyncV341()){
            const {error:upErr}=await supabaseClient
              .from('athlete_snapshots')
              .upsert({
                athlete_id:linkedAthleteId,
                data:merged,
                updated_at:new Date().toISOString()
              },{onConflict:'athlete_id'});
            if(upErr)throw upErr;
            try{cloudLastWrite=Date.now()}catch(_e){}
            try{
              if(window.__fjzV341WorkoutStability){
                window.__fjzV341WorkoutStability.activeWorkoutMergedWrites++;
                window.__fjzV341WorkoutStability.lastMergedWriteAt=new Date().toISOString();
              }
            }catch(_e){}
            return true;
          }

          const idx=state.students.findIndex(x=>x.id===local.id);
          if(idx>=0)state.students[idx]=merged;
          writeStateQuietV112();
        }
      }catch(e){
        console.warn('V11.2 pre-sync alumno',e);
      }
    }
    return baseSyncStudentStateV112.apply(this,arguments);
  };"""

    if body.count(old)!=1:
        raise RuntimeError("V21.41 V112 student sync anchor mismatch: "+str(body.count(old)))
    return body.replace(old,new,1)

html=edit_script(html,"v112SyncHardeningRuntime",patch_v112)

runtime=r"""
<script id="v341MobileWorkoutStabilityRuntime">
(function(){
  window.__fjzV341WorkoutStability={
    version:'21.41',
    workoutCloudDebounceMs:4200,
    localDraftStillImmediate:true,
    activeWorkoutMergedWrite:true,
    activeWorkoutStateReplacementBlocked:true,
    activeWorkoutLocalStorageRewriteBlocked:true,
    remoteConfigMergePreserved:true,
    localWorkoutDraftPreserved:true,
    realtimeWorkoutFreezePreserved:true,
    explicitFinalSaveUntouched:true,
    coalescedWorkoutSchedules:0,
    workoutCloudFlushes:0,
    activeWorkoutMergedWrites:0,
    lastScheduledAt:null,
    lastFlushAt:null,
    lastMergedWriteAt:null
  };
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-mobile-workout-stability" content="21.41">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V21.41 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-mobile-workout-stability" content="21.41"',
    'id="v341MobileWorkoutStabilityRuntime"',
    "workoutCloudDebounceMs:4200",
    "activeWorkoutStateReplacementBlocked:true",
    "activeWorkoutLocalStorageRewriteBlocked:true",
    "remoteConfigMergePreserved:true",
    "localWorkoutDraftPreserved:true",
    "realtimeWorkoutFreezePreserved:true",
    "explicitFinalSaveUntouched:true",
    "activeWorkoutSyncV341",
    "merged.workoutDrafts=cloneV112(local.workoutDrafts)",
    "activeWorkoutFreeze:true",
    "viewScopedRealtime:true",
    "sessionSuccessRequiresDoubleVerification:true",
    "globalSaveIntegrity:true",
    "retryUsesSameSessionId:true",
]:
    if marker not in html:
        raise RuntimeError("V21.41 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.41 mobile workout stability")
print("V21.41 BEFORE:",before)
print("V21.41 AFTER:",after)
