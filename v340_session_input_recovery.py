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
    if mid<0: raise RuntimeError("V21.40 missing script "+script_id)
    a=doc.find(">",mid); b=doc.find("</script>",a)
    if a<0 or b<0: raise RuntimeError("V21.40 malformed script "+script_id)
    old=doc[a+1:b]
    new=transform(old)
    if new==old: raise RuntimeError("V21.40 no changes in "+script_id)
    return doc[:a+1]+new+doc[b:]

before=metrics(html)

for marker in [
    'meta name="fjz-review-center-curtain" content="21.39"',
    'id="v145WorkoutAutosaveRuntime"',
    'id="v207ConfirmedSessionCommitRuntime"',
    'id="v316SessionLossProtectionRuntime"',
    "retryUsesSameSessionId:true",
    "snapshotAndProjectionConfirmation:true",
    "sessionSuccessRequiresDoubleVerification:true",
    "globalSaveIntegrity:true",
]:
    if marker not in html:
        raise RuntimeError("V21.40 prerequisite missing "+marker)

# --------------------------------------------------------------------
# 1) Preserve the original workout start across draft resume.
#    Legacy drafts did not have startedAt, so their last pre-save edit time
#    becomes the conservative fallback for delayed completion.
# --------------------------------------------------------------------
def patch_v145(body):
    old="""  function currentPackV145(){
    const s=student?.(),d=s?.days?.[currentDay];
    if(!s||!d)return null;
    return {
      version:VERSION,
      studentId:s.id,
      dayId:d.id,
      dayName:d.name,
      updatedAt:new Date().toISOString(),
      workoutDraft:safeCloneV145(workoutDraft||{}),
      methodDraft:safeCloneV145(window.__fjzMethodDraftV110||{})
    };
  }"""
    new="""  function currentPackV145(){
    const s=student?.(),d=s?.days?.[currentDay];
    if(!s||!d)return null;
    const prior=freshestV145(readLocalV145(s,d),readCloudV145(s,d));
    const candidate=prior?.startedAt||prior?.updatedAt||null;
    const candidateMs=Date.parse(candidate||0)||0;
    const now=Date.now();
    const startedAt=candidateMs&&now-candidateMs>=0&&now-candidateMs<=72*60*60*1000
      ?new Date(candidateMs).toISOString()
      :new Date(now).toISOString();
    return {
      version:VERSION,
      studentId:s.id,
      dayId:d.id,
      dayName:d.name,
      startedAt,
      updatedAt:new Date().toISOString(),
      workoutDraft:safeCloneV145(workoutDraft||{}),
      methodDraft:safeCloneV145(window.__fjzMethodDraftV110||{})
    };
  }"""
    if body.count(old)!=1:
        raise RuntimeError("V21.40 V145 draft pack anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""  window.__fjzWorkoutAutosaveV145={"""
    new="""  window.__fjzWorkoutStartedAtV340=function(){
    const s=student?.(),d=s?.days?.[currentDay];
    if(!s||!d)return null;
    const prior=freshestV145(readLocalV145(s,d),readCloudV145(s,d));
    const candidate=prior?.startedAt||prior?.updatedAt||null;
    const candidateMs=Date.parse(candidate||0)||0;
    if(!candidateMs||Date.now()-candidateMs<0||Date.now()-candidateMs>72*60*60*1000)return null;
    return new Date(candidateMs).toISOString();
  };
  window.__fjzWorkoutAutosaveV145={"""
    if body.count(old)!=1:
        raise RuntimeError("V21.40 V145 export anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)
    return body

html=edit_script(html,"v145WorkoutAutosaveRuntime",patch_v145)

# --------------------------------------------------------------------
# 2) Validate workout values before creating the local pending session.
#    This prevents an impossible reps/RIR value from reaching the RPC and
#    replaces the generic endless retry with an exact actionable message.
#    Also stamp a resumed draft with its original workout time.
# --------------------------------------------------------------------
def patch_v207(body):
    anchor="""  function createPendingV207(pack){"""
    if body.count(anchor)!=1:
        raise RuntimeError("V21.40 V207 create pending anchor mismatch")

    helper=r"""
  function swapEvidenceV340(e,kg,reps){
    if(!(Number.isFinite(kg)&&Number.isFinite(reps)&&reps>200&&kg>=1&&kg<=60))return false;
    const loads=[],repRefs=[];
    (e?.history||[]).slice(-8).forEach(h=>{
      (h?.sets||[]).forEach(set=>{
        const l=Number(set?.[0]),r=Number(set?.[1]);
        if(Number.isFinite(l)&&l>0)loads.push(l);
        if(Number.isFinite(r)&&r>=1&&r<=200)repRefs.push(r);
      });
    });
    (e?.repsExact||[]).forEach(v=>{const n=Number(v);if(Number.isFinite(n))repRefs.push(n)});
    [e?.min,e?.max].forEach(v=>{const n=Number(v);if(Number.isFinite(n))repRefs.push(n)});
    const priorLoad=loads.some(v=>Math.abs(v-reps)<=Math.max(0.5,Math.abs(reps)*0.01));
    const plausibleReps=repRefs.some(v=>Math.abs(v-kg)<=2);
    return priorLoad&&plausibleReps;
  }

  function validatePackV340(pack){
    for(const item of (pack?.registered||[])){
      const e=item?.e||{};
      const indexes=Array.isArray(item?.setIndexes)?item.setIndexes:[];
      for(let j=0;j<(item?.sets||[]).length;j++){
        const set=item.sets[j]||[];
        const kg=Number(set[0]),reps=Number(set[1]),rir=Number(set[2]);
        const setNumber=Number(indexes[j]??j)+1;
        if(!Number.isFinite(kg)||kg<0){
          return {e,setNumber,kg,reps,rir,reason:'La carga no es válida.'};
        }
        if(!Number.isInteger(reps)||reps<1||reps>200){
          const swap=swapEvidenceV340(e,kg,reps);
          return {
            e,setNumber,kg,reps,rir,swap,
            reason:reps>200
              ?'Hay '+String(reps)+' repeticiones cargadas y el máximo aceptado es 200.'
              :'Las repeticiones deben ser un número entero entre 1 y 200.'
          };
        }
        if(!Number.isFinite(rir)||rir<0||rir>10){
          return {e,setNumber,kg,reps,rir,reason:'El RIR debe estar entre 0 y 10.'};
        }
        if(setNumber<1||setNumber>20){
          return {e,setNumber,kg,reps,rir,reason:'El número de serie está fuera del rango permitido.'};
        }
      }
    }
    return null;
  }

  function modalInvalidPackV340(issue){
    const name=String(issue?.e?.name||'Ejercicio');
    const swapCopy=issue?.swap
      ?'<div class="v207-save-copy"><strong style="color:#fff">Parece que peso y repeticiones quedaron invertidos.</strong><br>Por el historial, revisá si querías registrar '+escV207(issue.reps)+' kg × '+escV207(issue.kg)+' reps.</div>'
      :'';
    showModal(
      '<div class="v207-save-state">'+
        '<div class="v207-save-icon error">!</div>'+
        '<div class="v207-save-title">Revisá una serie antes de guardar</div>'+
        '<div class="v207-save-copy"><strong style="color:#fff">'+escV207(name)+' · serie '+escV207(issue?.setNumber||'')+'</strong><br>'+escV207(issue?.reason||'Hay un dato inválido.')+'</div>'+
        swapCopy+
        '<div class="v207-save-actions"><button class="btn primary" onclick="closeModal()">Volver al entrenamiento</button></div>'+
      '</div>'
    );
  }

  function applyWorkoutStartedAtV340(pack,session){
    if(!pack||!session)return;
    const raw=window.__fjzWorkoutStartedAtV340?.();
    const started=Date.parse(raw||0)||0;
    const saved=Date.parse(session.date||0)||Date.now();
    const age=saved-started;
    if(!started||age<0||age>72*60*60*1000)return;
    const oldDate=session.date;
    const iso=new Date(started).toISOString();
    session.date=iso;

    (session.exerciseResults||[]).forEach(result=>{
      const e=(pack?.d?.exercises||[]).find(x=>String(x?.uid||'')===String(result?.exerciseUid||''));
      const h=e?.history?.[e.history.length-1];
      if(!h)return;
      const ht=Date.parse(h.date||0)||0;
      const ot=Date.parse(oldDate||0)||0;
      if(ht&&ot&&Math.abs(ht-ot)<=120000)h.date=iso;
    });

    try{
      const dates=(pack.s?.sessions||[]).map(x=>Date.parse(x?.date||0)||0).filter(Boolean);
      const latest=dates.length?Math.max(...dates):started;
      pack.s.lastWorkout=new Date(latest).toISOString();
    }catch(_e){}
  }

"""
    body=body.replace(anchor,helper+anchor,1)

    old="""    const session=window.__fjzSaveSessionV205?.(pack);
    if(!session)throw new Error('No se pudo preparar la sesión.');

    attachMethodHistoryV207(pack,session);"""
    new="""    const session=window.__fjzSaveSessionV205?.(pack);
    if(!session)throw new Error('No se pudo preparar la sesión.');

    applyWorkoutStartedAtV340(pack,session);
    attachMethodHistoryV207(pack,session);"""
    if body.count(old)!=1:
        raise RuntimeError("V21.40 V207 session stamp anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""  function beginCommitV207(pack){
    if(stateV207==='saving'||stateV207==='success'||!pack)return;
    try{
      createPendingV207(pack);"""
    new="""  function beginCommitV207(pack){
    if(stateV207==='saving'||stateV207==='success'||!pack)return;
    const issue=validatePackV340(pack);
    if(issue){
      stateV207='idle';
      pendingV207=null;
      modalInvalidPackV340(issue);
      return;
    }
    try{
      createPendingV207(pack);"""
    if body.count(old)!=1:
        raise RuntimeError("V21.40 V207 validation anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    failedSaveRemainsRetryable:true
  };"""
    new="""    failedSaveRemainsRetryable:true,
    workoutInputPreflightV340:true,
    repsRangeMatchesDatabaseV340:true,
    rirRangeMatchesDatabaseV340:true,
    invalidSetNeverReachesCloudV340:true,
    resumedWorkoutKeepsOriginalTimeV340:true
  };"""
    if body.count(old)!=1:
        raise RuntimeError("V21.40 V207 marker anchor mismatch")
    body=body.replace(old,new,1)
    return body

html=edit_script(html,"v207ConfirmedSessionCommitRuntime",patch_v207)

# --------------------------------------------------------------------
# 3) Repair only a VERY strong legacy load/reps inversion during recovery.
#    We require both sides of the swap to match prior/target evidence.
#    This allows Matias's preserved local backup to recover without silently
#    guessing arbitrary invalid data.
# --------------------------------------------------------------------
def patch_v316(body):
    anchor="""  async function recoverPackV316(pack){"""
    if body.count(anchor)!=1:
        raise RuntimeError("V21.40 V316 recovery anchor mismatch")

    helper=r"""
  function readLegacyDraftV340(pack){
    try{
      const key='fjz_workout_draft_v145:'+String(pack?.studentId||'student')+':'+String(pack?.dayId||'day');
      const raw=localStorage.getItem(key);
      return raw?JSON.parse(raw):null;
    }catch(_e){return null}
  }

  function swapEvidenceRecoveryV340(e,kg,reps){
    if(!(Number.isFinite(kg)&&Number.isFinite(reps)&&reps>200&&kg>=1&&kg<=60))return false;
    const loads=[],repRefs=[];
    (e?.history||[]).slice(-8).forEach(h=>{
      (h?.sets||[]).forEach(set=>{
        const l=Number(set?.[0]),r=Number(set?.[1]);
        if(Number.isFinite(l)&&l>0&&r<=200)loads.push(l);
        if(Number.isFinite(r)&&r>=1&&r<=200)repRefs.push(r);
      });
    });
    (e?.repsExact||[]).forEach(v=>{const n=Number(v);if(Number.isFinite(n))repRefs.push(n)});
    [e?.min,e?.max].forEach(v=>{const n=Number(v);if(Number.isFinite(n))repRefs.push(n)});
    const priorLoad=loads.some(v=>Math.abs(v-reps)<=Math.max(0.5,Math.abs(reps)*0.01));
    const plausibleReps=repRefs.some(v=>Math.abs(v-kg)<=2);
    return priorLoad&&plausibleReps;
  }

  function repairHistorySetV340(e,badKg,badReps,newKg,newReps,setIndex,oldDate,newDate){
    const history=Array.isArray(e?.history)?e.history:[];
    for(let hi=history.length-1;hi>=0;hi--){
      const h=history[hi];
      const sets=Array.isArray(h?.sets)?h.sets:[];
      const candidates=[Number(setIndex),Math.max(0,Number(setIndex)-1)].filter(Number.isFinite);
      let fixed=false;
      for(const idx of candidates){
        const set=sets[idx];
        if(!Array.isArray(set))continue;
        if(Number(set[0])===badKg&&Number(set[1])===badReps){
          set[0]=newKg;set[1]=newReps;fixed=true;break;
        }
      }
      if(!fixed){
        for(const set of sets){
          if(Array.isArray(set)&&Number(set[0])===badKg&&Number(set[1])===badReps){
            set[0]=newKg;set[1]=newReps;fixed=true;break;
          }
        }
      }
      if(fixed){
        const ht=Date.parse(h?.date||0)||0,ot=Date.parse(oldDate||0)||0;
        if(newDate&&ht&&ot&&Math.abs(ht-ot)<=180000)h.date=newDate;
        return true;
      }
    }
    return false;
  }

  function prepareRecoveryPackV340(pack){
    if(!pack?.session?.id||!pack?.day?.id)return pack;
    const session=pack.session;
    const oldDate=session.date;
    let recoveredDate=null;
    const draft=readLegacyDraftV340(pack);
    const candidate=draft?.startedAt||draft?.updatedAt||null;
    const ct=Date.parse(candidate||0)||0,st=Date.parse(oldDate||0)||0;
    if(ct&&st&&st-ct>=15*60*1000&&st-ct<=72*60*60*1000){
      recoveredDate=new Date(ct).toISOString();
      session.date=recoveredDate;
    }

    const corrections=[];
    for(const result of (session.exerciseResults||[])){
      const e=(pack.day.exercises||[]).find(x=>String(x?.uid||'')===String(result?.exerciseUid||''))||null;
      const indexes=Array.isArray(result?.setIndexes)?result.setIndexes:[];
      for(let j=0;j<(result?.sets||[]).length;j++){
        const set=result.sets[j]||[];
        const kg=Number(set[0]),reps=Number(set[1]),rir=Number(set[2]);
        const originalIndex=Number(indexes[j]??j);
        if(!Number.isFinite(kg)||kg<0||!Number.isFinite(rir)||rir<0||rir>10){
          throw new Error('El backup conserva una serie inválida que necesita revisión manual.');
        }
        if(!Number.isInteger(reps)||reps<1||reps>200){
          if(reps>200&&swapEvidenceRecoveryV340(e,kg,reps)){
            set[0]=reps;
            set[1]=kg;
            repairHistorySetV340(e,kg,reps,reps,kg,originalIndex,oldDate,recoveredDate);
            corrections.push({
              exerciseUid:String(result?.exerciseUid||''),
              exerciseName:String(result?.name||e?.name||'Ejercicio'),
              setNumber:originalIndex+1,
              from:[kg,reps,rir],
              to:[reps,kg,rir],
              reason:'strong_load_reps_swap_evidence_v340'
            });
          }else{
            throw new Error('El backup conserva repeticiones fuera de rango y no hay evidencia suficiente para corregirlas automáticamente.');
          }
        }
      }
    }

    if(recoveredDate){
      (pack.day.exercises||[]).forEach(e=>{
        const h=e?.history?.[e.history.length-1];
        const ht=Date.parse(h?.date||0)||0,ot=Date.parse(oldDate||0)||0;
        if(h&&ht&&ot&&Math.abs(ht-ot)<=180000)h.date=recoveredDate;
      });
    }

    if(corrections.length){
      session.integrityCorrections=[
        ...(Array.isArray(session.integrityCorrections)?session.integrityCorrections:[]),
        ...corrections
      ];
    }

    try{
      const key=backupKeyV316(session.id);
      const saved={...pack,session:cloneV316(session),day:cloneV316(pack.day),correctedAt:new Date().toISOString()};
      localStorage.setItem(key,JSON.stringify(saved));
    }catch(_e){}

    return pack;
  }

  function clearRecoveredDraftV340(pack){
    try{
      localStorage.removeItem(
        'fjz_workout_draft_v145:'+String(pack?.studentId||'student')+':'+String(pack?.dayId||'day')
      );
    }catch(_e){}
    try{
      const raw=localStorage.getItem('fjz_v201_pending_session');
      const pending=raw?JSON.parse(raw):null;
      if(pending?.sessionId&&String(pending.sessionId)===String(pack?.session?.id||'')){
        localStorage.removeItem('fjz_v201_pending_session');
      }
    }catch(_e){}
  }

"""
    body=body.replace(anchor,helper+anchor,1)

    old="""  async function recoverPackV316(pack){
    const sid=String(pack?.session?.id||'');
    if(!sid||localStorage.getItem(DONE_PREFIX+sid))return false;
    const athlete=await resolveAthleteV316(pack);"""
    new="""  async function recoverPackV316(pack){
    const sid=String(pack?.session?.id||'');
    if(!sid||localStorage.getItem(DONE_PREFIX+sid))return false;
    pack=prepareRecoveryPackV340(pack);
    const athlete=await resolveAthleteV316(pack);"""
    if body.count(old)!=1:
        raise RuntimeError("V21.40 V316 prepare recovery anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    localStorage.setItem(DONE_PREFIX+sid,new Date().toISOString());
    markBackupConfirmedV316(sid);
    return {athlete,session:pack.session};"""
    new="""    localStorage.setItem(DONE_PREFIX+sid,new Date().toISOString());
    markBackupConfirmedV316(sid);
    clearRecoveredDraftV340(pack);
    return {athlete,session:pack.session};"""
    if body.count(old)!=1:
        raise RuntimeError("V21.40 V316 cleanup anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""    noExtraObservers:true
  };"""
    new="""    noExtraObservers:true,
    legacyInvalidSetRecoveryV340:true,
    strongSwapEvidenceRequiredV340:true,
    recoveredDraftDateV340:true,
    recoveredDraftCleanupV340:true,
    noBlindAutoCorrectionV340:true
  };"""
    if body.count(old)!=1:
        raise RuntimeError("V21.40 V316 marker anchor mismatch")
    body=body.replace(old,new,1)
    return body

html=edit_script(html,"v316SessionLossProtectionRuntime",patch_v316)

html=html.replace("</head>",'<meta name="fjz-session-input-recovery" content="21.40">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V21.40 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-session-input-recovery" content="21.40"',
    "startedAt:startedAtV340",
    "__fjzWorkoutStartedAtV340",
    "workoutInputPreflightV340:true",
    "repsRangeMatchesDatabaseV340:true",
    "rirRangeMatchesDatabaseV340:true",
    "invalidSetNeverReachesCloudV340:true",
    "strongSwapEvidenceRequiredV340:true",
    "noBlindAutoCorrectionV340:true",
    "recoveredDraftDateV340:true",
    "recoveredDraftCleanupV340:true",
    "retryUsesSameSessionId:true",
    "snapshotAndProjectionConfirmation:true",
    "sessionSuccessRequiresDoubleVerification:true",
    "globalSaveIntegrity:true",
]:
    if marker not in html:
        raise RuntimeError("V21.40 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.40 session input + delayed recovery")
print("V21.40 BEFORE:",before)
print("V21.40 AFTER:",after)
