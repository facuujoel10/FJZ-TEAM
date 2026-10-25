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
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

before=metrics(html)

for marker in [
    'meta name="fjz-save-integrity" content="21.03"',
    'id="v303SaveIntegrityRuntime"',
    'id="v207ConfirmedSessionCommitRuntime"',
    'id="v200StabilityAuthorityRuntime"',
    "__fjzQueueSessionSyncV201",
    "saveStudentScheduleV81",
    "saveReminderV81",
    "submitMeasurement",
    "uploadProgressPhoto",
    "saveNutritionPlan",
    "insertNutritionLog",
    "logPlanOption",
    "saveMealGroupV176",
    "deleteNutritionLog",
    "deleteMealGroupV176",
    "submitExerciseFeedbackV73",
    "reviewExerciseFeedbackV73",
]:
    if marker not in html:
        raise RuntimeError("V21.04 prerequisite missing "+marker)

# ---------------------------------------------------------
# 1) Reorder must be read back before V20.0 marks the
#    routine mutation complete.
# ---------------------------------------------------------
old_reorder=r"""            const {error}=await supabaseClient.rpc('reorder_athlete_exercises',{
              p_athlete_id:item.athleteId,
              p_day_id:item.dayId,
              p_order:item.order
            });
            if(error)throw error;"""
new_reorder=r"""            const {error}=await supabaseClient.rpc('reorder_athlete_exercises',{
              p_athlete_id:item.athleteId,
              p_day_id:item.dayId,
              p_order:item.order
            });
            if(error)throw error;
            const {data:verifySnapV304,error:verifyErrV304}=await supabaseClient
              .from('athlete_snapshots')
              .select('data,updated_at')
              .eq('athlete_id',item.athleteId)
              .single();
            if(verifyErrV304)throw verifyErrV304;
            const verifyDayV304=(verifySnapV304?.data?.days||[])
              .find(x=>String(x?.id)===String(item.dayId));
            const actualOrderV304=(verifyDayV304?.exercises||[]).map(x=>String(x?.uid));
            const expectedOrderV304=(item.order||[]).map(String);
            if(
              actualOrderV304.length!==expectedOrderV304.length||
              actualOrderV304.some((uid,i)=>uid!==expectedOrderV304[i])
            ){
              throw new Error('La nube no confirmó el nuevo orden de ejercicios.');
            }"""
if html.count(old_reorder)!=1:
    raise RuntimeError("V21.04 reorder authority mismatch: "+str(html.count(old_reorder)))
html=html.replace(old_reorder,new_reorder,1)

runtime=r"""
<script id="v304GlobalSaveIntegrityRuntime">
(function(){
  const VERSION='21.04';
  const locks=new Map();
  let verifyDepth=0;
  let deferredSuccess=null;

  const baseToast=window.toast||globalThis.toast;
  const baseConfirm=window.__fjzConfirmSavedV264;
  const baseQuick=window.__fjzQuickSavedV264;

  function msgV304(e){
    try{return typeof cloudErr==='function'?cloudErr(e):String(e?.message||e||'Error de guardado')}
    catch(_e){return String(e?.message||e||'Error de guardado')}
  }
  function successLike(v){
    return /(guardad|enviad|registrad|actualizad|eliminad|confirmad|sincronizad|publicad|cread)/i.test(String(v||''));
  }
  function failureLike(v){
    return /(no se|error|fall|pendiente|localmente|revis|falta|requiere|no encuentro|no pud)/i.test(String(v||''));
  }

  window.toast=function(v){
    if(verifyDepth>0&&successLike(v)&&!failureLike(v)){
      deferredSuccess={type:'toast',title:String(v||'Guardado')};
      return;
    }
    return typeof baseToast==='function'?baseToast.apply(this,arguments):undefined;
  };
  try{toast=window.toast}catch(_e){}

  window.__fjzConfirmSavedV264=function(title,copy){
    if(verifyDepth>0){
      deferredSuccess={type:'confirm',title:String(title||'Guardado'),copy:String(copy||'')};
      return true;
    }
    return typeof baseConfirm==='function'?baseConfirm.apply(this,arguments):true;
  };
  window.__fjzQuickSavedV264=function(title){
    if(verifyDepth>0){
      deferredSuccess={type:'quick',title:String(title||'Guardado')};
      return true;
    }
    return typeof baseQuick==='function'?baseQuick.apply(this,arguments):true;
  };

  function enterVerify(){verifyDepth++;if(verifyDepth===1)deferredSuccess=null}
  function leaveVerify(){verifyDepth=Math.max(0,verifyDepth-1)}

  function receipt(kind,title,meta={}){
    try{window.__fjzRecordConfirmedSaveV303?.(kind,title,{verified:true,version:VERSION,...meta})}catch(_e){}
  }
  function finalQuick(kind,title,meta={}){
    receipt(kind,title,meta);
    if(typeof baseQuick==='function')return baseQuick(title);
    if(typeof baseToast==='function')return baseToast('✓ '+title);
  }
  function finalConfirm(kind,title,copy,meta={}){
    receipt(kind,title,meta);
    if(typeof baseConfirm==='function')return baseConfirm(title,copy);
    if(typeof baseToast==='function')return baseToast('✓ '+title);
  }
  function fail(e){
    console.error('TEAM FJZ V21.04 verified save failed',e);
    if(typeof baseToast==='function')baseToast(msgV304(e));
    return false;
  }

  async function fresh(){
    if(!cloudEnabled||!supabaseClient)throw new Error('La operación requiere conexión con la nube.');
    const ok=await window.__fjzEnsureFreshAuthV194?.(false);
    if(ok===false)throw new Error('La sesión necesita actualizarse. Volvé a ingresar.');
    if(!currentUser?.id)throw new Error('No encuentro la sesión activa.');
    return true;
  }

  async function locked(name,task){
    if(locks.has(name))return locks.get(name);
    const p=Promise.resolve().then(task).finally(()=>locks.delete(name));
    locks.set(name,p);
    return p;
  }

  function athleteId(){
    try{
      if(currentProfile?.role==='student')return linkedAthleteId||trackingAthleteId?.()||null;
      const s=student?.();
      return cloudAthletes?.get?.(s?.id)?.id||trackingAthleteId?.()||null;
    }catch(_e){return null}
  }
  function studentId(){
    try{
      if(currentProfile?.role==='student')return currentUser?.id||null;
      return trackingStudentUserId?.()||cloudAthletes?.get?.(student?.()?.id)?.user_id||null;
    }catch(_e){return null}
  }

  function canonical(v){
    if(Array.isArray(v))return v.map(canonical);
    if(v&&typeof v==='object'){
      const out={};
      Object.keys(v).sort().forEach(k=>{out[k]=canonical(v[k])});
      return out;
    }
    return v;
  }
  function sameDeep(a,b){
    try{return JSON.stringify(canonical(a))===JSON.stringify(canonical(b))}
    catch(_e){return false}
  }
  function sameNum(a,b){
    if((a===null||a==='')&&(b===null||b===''))return true;
    return Number(a)===Number(b);
  }
  function normTime(v){return v?String(v).slice(0,5):''}

  function reconcileList(name,row,key='id'){
    try{
      if(!row||!globalThis[name])return;
      const list=globalThis[name];
      if(!Array.isArray(list))return;
      const next=[row,...list.filter(x=>String(x?.[key])!==String(row?.[key]))];
      globalThis[name]=next;
    }catch(_e){}
  }

  // -------------------------------------------------------
  // TRAINING SESSION: RPC success is followed by a separate
  // snapshot read-back for the exact session id.
  // -------------------------------------------------------
  const baseSessionQueue=window.__fjzQueueSessionSyncV201;
  if(typeof baseSessionQueue==='function'){
    window.__fjzQueueSessionSyncV201=async function(session,dayId){
      return locked('workout:'+String(session?.id||dayId||''),async()=>{
        await fresh();
        enterVerify();
        let ok=false;
        try{ok=await baseSessionQueue.apply(this,arguments)}
        finally{leaveVerify()}
        if(!ok)return false;

        const aid=athleteId();
        if(!aid||!session?.id)return false;
        const {data,error}=await supabaseClient.from('athlete_snapshots')
          .select('data,updated_at').eq('athlete_id',aid).single();
        if(error)throw error;
        const sessions=Array.isArray(data?.data?.sessions)?data.data.sessions:[];
        const saved=sessions.find(x=>String(x?.id)===String(session.id));
        const day=(data?.data?.days||[]).find(x=>String(x?.id)===String(dayId));
        if(!saved||!day)throw new Error('La nube no confirmó completamente la sesión.');
        receipt('workout','Sesión guardada',{sessionId:session.id,athleteId:aid});
        return true;
      }).catch(fail);
    };
  }

  // -------------------------------------------------------
  // ROUTINE: all full snapshot routine saves are read back.
  // V20.0 keeps its pending behavior if this wrapper throws.
  // -------------------------------------------------------
  const baseSync=window.syncCloudNow;
  if(typeof baseSync==='function'){
    window.syncCloudNow=async function(){
      const needsRoutine=!!window.__fjzRoutineSavingV200;
      const localDays=needsRoutine?canonical(student?.()?.days||[]):null;
      const aid=needsRoutine?athleteId():null;
      if(!needsRoutine)return baseSync.apply(this,arguments);

      return locked('routine-snapshot:'+String(aid||''),async()=>{
        await fresh();
        enterVerify();
        try{await baseSync.apply(this,arguments)}
        finally{leaveVerify()}
        if(!aid)throw new Error('No encuentro la ficha para confirmar la rutina.');
        const {data,error}=await supabaseClient.from('athlete_snapshots')
          .select('data,updated_at').eq('athlete_id',aid).single();
        if(error)throw error;
        if(!sameDeep(localDays,canonical(data?.data?.days||[]))){
          throw new Error('La nube no devolvió la misma rutina que se intentó guardar.');
        }
        finalQuick('routine','Rutina guardada',{athleteId:aid});
        return true;
      });
    };
    try{syncCloudNow=window.syncCloudNow}catch(_e){}
  }

  // -------------------------------------------------------
  // AGENDA: verify exact active weekly schedule. If the old
  // two-step upsert/delete ended partially, reconcile once and
  // verify again before success.
  // -------------------------------------------------------
  function desiredSchedule(){
    const s=student?.(),aid=athleteId();
    const rows=[];
    for(let i=0;i<7;i++){
      const dayId=document.getElementById('v81Day_'+i)?.value||'';
      if(!dayId)continue;
      const day=(s?.days||[]).find(x=>String(x?.id)===String(dayId));
      rows.push({
        athlete_id:aid,
        coach_id:currentUser?.id,
        weekday:i,
        workout_day_id:dayId,
        workout_day_name:day?.name||'Entrenamiento',
        start_time:document.getElementById('v81Time_'+i)?.value||null,
        reminder_enabled:document.getElementById('v81Rem_'+i)?.value!=='0',
        reminder_minutes_before:60,
        active:true
      });
    }
    return {aid,rows};
  }
  async function readSchedule(aid){
    const {data,error}=await supabaseClient.from('athlete_schedule')
      .select('*').eq('athlete_id',aid).order('weekday',{ascending:true});
    if(error)throw error;
    return (data||[]).filter(x=>x.active!==false);
  }
  function scheduleMatches(remote,desired){
    if(remote.length!==desired.length)return false;
    return desired.every(d=>{
      const r=remote.find(x=>Number(x.weekday)===Number(d.weekday));
      return !!r&&String(r.workout_day_id||'')===String(d.workout_day_id||'')&&
        normTime(r.start_time)===normTime(d.start_time)&&
        Boolean(r.reminder_enabled)===Boolean(d.reminder_enabled)&&
        Number(r.reminder_minutes_before||0)===Number(d.reminder_minutes_before||0)&&
        String(r.workout_day_name||'')===String(d.workout_day_name||'');
    });
  }
  async function reconcileSchedule(ctx){
    if(ctx.rows.length){
      const {error}=await supabaseClient.from('athlete_schedule')
        .upsert(ctx.rows,{onConflict:'athlete_id,weekday'});
      if(error)throw error;
    }
    const current=await readSchedule(ctx.aid);
    const wanted=new Set(ctx.rows.map(x=>Number(x.weekday)));
    const extra=current.filter(x=>!wanted.has(Number(x.weekday))).map(x=>x.id);
    if(extra.length){
      const {data,error}=await supabaseClient.from('athlete_schedule')
        .delete().in('id',extra).select('id');
      if(error)throw error;
      if((data||[]).length!==extra.length)throw new Error('No se pudieron quitar todos los días antiguos de la agenda.');
    }
  }
  const baseSchedule=window.saveStudentScheduleV81;
  if(typeof baseSchedule==='function'){
    window.saveStudentScheduleV81=function(){
      const ctx=desiredSchedule();
      return locked('agenda:'+String(ctx.aid||''),async()=>{
        await fresh();
        if(!ctx.aid)throw new Error('No encuentro la ficha vinculada para guardar la agenda.');
        let baseErr=null;
        enterVerify();
        try{await baseSchedule.apply(this,arguments)}
        catch(e){baseErr=e}
        finally{leaveVerify()}

        let remote=await readSchedule(ctx.aid);
        if(!scheduleMatches(remote,ctx.rows)){
          await reconcileSchedule(ctx);
          remote=await readSchedule(ctx.aid);
        }
        if(!scheduleMatches(remote,ctx.rows)){
          if(baseErr)throw baseErr;
          throw new Error('La agenda no quedó idéntica a lo seleccionado.');
        }
        try{await window.loadAgendaV81?.(true)}catch(_e){}
        try{window.renderCoachStudentAgendaV81?.()}catch(_e){}
        finalConfirm('agenda','Agenda guardada','La agenda semanal quedó confirmada y releída desde la nube.',{athleteId:ctx.aid});
        return true;
      }).catch(fail);
    };
    try{saveStudentScheduleV81=window.saveStudentScheduleV81}catch(_e){}
  }

  // Reminder create/delete already return rows; add an independent read-back.
  const baseReminder=window.saveReminderV81;
  if(typeof baseReminder==='function'){
    window.saveReminderV81=function(){
      const aid=athleteId();
      const title=(document.getElementById('v81RemTitle')?.value||'').trim();
      const type=(document.getElementById('v81RemType')?.value||'once')==='weekly'?'weekly':'once';
      const date=document.getElementById('v81RemDate')?.value||null;
      const weekday=Number(document.getElementById('v81RemWeekday')?.value);
      const started=new Date(Date.now()-5000).toISOString();
      return locked('reminder-create:'+String(aid||''),async()=>{
        await fresh();
        enterVerify();
        let baseErr=null;
        try{await baseReminder.apply(this,arguments)}
        catch(e){baseErr=e}
        finally{leaveVerify()}
        const {data,error}=await supabaseClient.from('athlete_reminders').select('*')
          .eq('athlete_id',aid).eq('title',title).gte('created_at',started)
          .order('created_at',{ascending:false}).limit(5);
        if(error)throw error;
        const row=(data||[]).find(x=>
          x.schedule_type===type&&
          (type==='once'?String(x.reminder_date||'')===String(date||''):Number(x.weekday)===weekday)
        );
        if(!row){if(baseErr)throw baseErr;throw new Error('La nube no confirmó el recordatorio.')}
        finalConfirm('agenda','Recordatorio guardado','El recordatorio quedó confirmado en la nube.',{id:row.id,athleteId:aid});
        return true;
      }).catch(fail);
    };
    try{saveReminderV81=window.saveReminderV81}catch(_e){}
  }
  const baseDeleteReminder=window.deleteReminderV81;
  if(typeof baseDeleteReminder==='function'){
    window.deleteReminderV81=function(id){
      return locked('reminder-delete:'+String(id||''),async()=>{
        await fresh();
        enterVerify();
        let baseErr=null;
        try{await baseDeleteReminder.apply(this,arguments)}
        catch(e){baseErr=e}
        finally{leaveVerify()}
        const {data,error}=await supabaseClient.from('athlete_reminders')
          .select('id').eq('id',id).maybeSingle();
        if(error)throw error;
        if(data){if(baseErr)throw baseErr;throw new Error('El recordatorio sigue presente en la nube.')}
        finalQuick('agenda','Recordatorio eliminado',{id});
        return true;
      }).catch(fail);
    };
    try{deleteReminderV81=window.deleteReminderV81}catch(_e){}
  }

  // -------------------------------------------------------
  // MEASUREMENTS: both creation and editing use the database
  // row as source of truth even if the history refresh fails.
  // -------------------------------------------------------
  function measurementPayload(){
    const n=id=>{
      const raw=document.getElementById(id)?.value;
      if(raw===undefined||raw===null||String(raw).trim()==='')return null;
      const v=Number(String(raw).replace(',','.'));
      return Number.isFinite(v)?v:null;
    };
    return {
      aid:athleteId(),
      date:document.getElementById('mDate')?.value||dateInputToday(),
      weight_kg:n('mWeight'),waist_cm:n('mWaist'),abdomen_cm:n('mAbd'),
      hip_cm:n('mHip'),chest_cm:n('mChest')
    };
  }
  function measurementMatches(row,p){
    return !!row&&String(row.athlete_id||'')===String(p.aid||'')&&
      String(row.measured_on||'')===String(p.date||'')&&
      ['weight_kg','waist_cm','abdomen_cm','hip_cm','chest_cm'].every(k=>sameNum(row[k],p[k]));
  }
  function reconcileMeasurement(row){
    try{
      const prev=Array.isArray(trackingCache?.measurements)?trackingCache.measurements:[];
      trackingCache.measurements=[row,...prev.filter(x=>String(x?.id)!==String(row.id)&&String(x?.measured_on)!==String(row.measured_on))]
        .sort((a,b)=>String(b.measured_on||'').localeCompare(String(a.measured_on||'')));
      trackingLoadedFor=athleteId();
    }catch(_e){}
  }
  const baseMeasurement=window.submitMeasurement||globalThis.submitMeasurement;
  if(typeof baseMeasurement==='function'){
    const wrapped=function(){
      const p=measurementPayload();
      return locked('measurement:'+String(p.aid||'')+':'+p.date,async()=>{
        await fresh();
        enterVerify();
        let baseErr=null;
        try{await baseMeasurement.apply(this,arguments)}
        catch(e){baseErr=e}
        finally{leaveVerify()}
        const {data,error}=await supabaseClient.from('body_measurements')
          .select('*').eq('athlete_id',p.aid).eq('measured_on',p.date).single();
        if(error)throw error;
        if(!measurementMatches(data,p)){
          if(baseErr)throw baseErr;
          throw new Error('La medición guardada no coincide con lo ingresado.');
        }
        reconcileMeasurement(data);
        finalConfirm('measurement','Medición guardada','La medición quedó confirmada en la nube.',{id:data.id,athleteId:p.aid,date:p.date});
        return data;
      }).catch(fail);
    };
    window.submitMeasurement=wrapped;
    try{submitMeasurement=wrapped}catch(_e){}
  }

  function editMeasurementPayload(){
    const n=id=>{
      const raw=document.getElementById(id)?.value;
      if(raw===undefined||raw===null||String(raw).trim()==='')return null;
      const v=Number(String(raw).replace(',','.'));
      return Number.isFinite(v)?v:null;
    };
    return {
      date:document.getElementById('v176MeasureDate')?.value||'',
      weight_kg:n('v176MeasureWeight'),waist_cm:n('v176MeasureWaist'),
      hip_cm:n('v176MeasureHip'),chest_cm:n('v176MeasureChest'),
      arm_left_cm:n('v176MeasureArm'),thigh_left_cm:n('v176MeasureThigh'),
      notes:(document.getElementById('v176MeasureNotes')?.value||'').trim()
    };
  }
  const baseEditMeasurement=window.saveMeasurementV176;
  if(typeof baseEditMeasurement==='function'){
    window.saveMeasurementV176=function(id){
      const p=editMeasurementPayload();
      return locked('measurement-edit:'+String(id||''),async()=>{
        await fresh();
        enterVerify();
        let baseErr=null;
        try{await baseEditMeasurement.apply(this,arguments)}
        catch(e){baseErr=e}
        finally{leaveVerify()}
        const {data,error}=await supabaseClient.from('body_measurements').select('*').eq('id',id).single();
        if(error)throw error;
        const ok=String(data.measured_on||'')===String(p.date||'')&&
          ['weight_kg','waist_cm','hip_cm','chest_cm','arm_left_cm','thigh_left_cm'].every(k=>sameNum(data[k],p[k]))&&
          String(data.notes||'')===String(p.notes||'');
        if(!ok){if(baseErr)throw baseErr;throw new Error('La nube no confirmó todos los cambios de la medición.')}
        reconcileMeasurement(data);
        finalConfirm('measurement','Medición actualizada','Los cambios quedaron confirmados en la nube.',{id});
        return data;
      }).catch(fail);
    };
    try{saveMeasurementV176=window.saveMeasurementV176}catch(_e){}
  }

  // -------------------------------------------------------
  // PROGRESS PHOTO: two-resource transaction with compensation.
  // If DB registration fails, delete the newly uploaded object.
  // After DB success, best-effort remove the replaced old object.
  // -------------------------------------------------------
  window.uploadProgressPhoto=function(){
    const file=document.getElementById('progressPhotoFile')?.files?.[0];
    const aid=athleteId();
    const pose=document.getElementById('progressPhotoPose')?.value||'front';
    const date=document.getElementById('progressPhotoDate')?.value||dateInputToday();
    return locked('photo:'+String(aid||'')+':'+date+':'+pose,async()=>{
      await fresh();
      if(!file)throw new Error('Elegí una foto.');
      if(!aid)throw new Error('No encuentro la ficha.');
      if(file.size>8*1024*1024)throw new Error('La foto supera 8 MB.');

      const {data:oldRow,error:oldErr}=await supabaseClient.from('progress_photos')
        .select('id,storage_path').eq('athlete_id',aid).eq('taken_on',date).eq('pose',pose).maybeSingle();
      if(oldErr)throw oldErr;

      const ext=(String(file.name||'jpg').split('.').pop()||'jpg').toLowerCase().replace(/[^a-z0-9]/g,'')||'jpg';
      const path=aid+'/'+date+'/'+pose+'_'+Date.now()+'_'+Math.random().toString(36).slice(2,7)+'.'+ext;
      let uploaded=false;
      try{
        const {error:upErr}=await supabaseClient.storage.from('progress-photos')
          .upload(path,file,{contentType:file.type||'image/jpeg',upsert:false});
        if(upErr)throw upErr;
        uploaded=true;

        const payload={athlete_id:aid,student_id:studentId(),taken_on:date,pose,storage_path:path};
        const {data:written,error:writeErr}=await supabaseClient.from('progress_photos')
          .upsert(payload,{onConflict:'athlete_id,taken_on,pose'}).select('*').single();
        if(writeErr)throw writeErr;
        const {data:readBack,error:readErr}=await supabaseClient.from('progress_photos')
          .select('*').eq('athlete_id',aid).eq('taken_on',date).eq('pose',pose).single();
        if(readErr)throw readErr;
        if(!readBack?.id||String(readBack.storage_path)!==String(path)){
          throw new Error('La nube no confirmó el vínculo de la foto.');
        }

        try{
          const prev=Array.isArray(trackingCache?.photos)?trackingCache.photos:[];
          trackingCache.photos=[readBack,...prev.filter(x=>String(x?.id)!==String(readBack.id)&&!(String(x?.taken_on)===date&&String(x?.pose)===pose))]
            .sort((a,b)=>String(b.taken_on||'').localeCompare(String(a.taken_on||'')));
          trackingLoadedFor=aid;
        }catch(_e){}

        if(oldRow?.storage_path&&oldRow.storage_path!==path){
          try{await supabaseClient.storage.from('progress-photos').remove([oldRow.storage_path])}catch(cleanErr){
            console.warn('TEAM FJZ V21.04 old photo cleanup pending',cleanErr);
          }
        }
        const input=document.getElementById('progressPhotoFile');if(input)input.value='';
        finalConfirm('photo','Foto guardada','La foto y su registro quedaron confirmados en la nube.',{id:readBack.id,athleteId:aid,date,pose});
        return readBack;
      }catch(e){
        if(uploaded){
          try{await supabaseClient.storage.from('progress-photos').remove([path])}catch(_e){}
        }
        throw e;
      }
    }).catch(fail);
  };
  try{uploadProgressPhoto=window.uploadProgressPhoto}catch(_e){}

  // -------------------------------------------------------
  // NUTRITION PLAN: exact read-back of plan + macros/revision.
  // -------------------------------------------------------
  function planPayload(){
    const p=nutritionCache?.plan;if(!p)return null;
    const val=id=>{
      const v=document.getElementById(id)?.value;
      return v===''||v==null?null:Number(v);
    };
    return {
      id:p.id,
      title:(document.getElementById('nutTitle')?.value||'').trim()||'Plan nutricional',
      notes:(document.getElementById('nutNotes')?.value||'').trim(),
      target_kcal:val('nutKcal'),target_protein_g:val('nutProtein'),
      target_carbs_g:val('nutCarbs'),target_fat_g:val('nutFat'),
      plan:typeof nutritionPlanData==='function'?canonical(nutritionPlanData()):canonical(p.plan||{}),
      revision:Number(p.revision||1)+1
    };
  }
  function planMatches(row,p){
    return !!row&&String(row.id)===String(p.id)&&String(row.title||'')===String(p.title||'')&&
      String(row.notes||'')===String(p.notes||'')&&
      ['target_kcal','target_protein_g','target_carbs_g','target_fat_g'].every(k=>sameNum(row[k],p[k]))&&
      Number(row.revision)===Number(p.revision)&&sameDeep(canonical(row.plan||{}),p.plan);
  }
  const basePlan=window.saveNutritionPlan||globalThis.saveNutritionPlan;
  if(typeof basePlan==='function'){
    const wrapped=function(){
      const p=planPayload();
      return locked('nutrition-plan:'+String(p?.id||''),async()=>{
        await fresh();
        if(!p)throw new Error('No encuentro el plan nutricional.');
        enterVerify();
        let baseErr=null;
        try{await basePlan.apply(this,arguments)}
        catch(e){baseErr=e}
        finally{leaveVerify()}
        let {data,error}=await supabaseClient.from('nutrition_plans').select('*').eq('id',p.id).single();
        if(error)throw error;
        if(!planMatches(data,p)){
          const {data:fixed,error:fixErr}=await supabaseClient.from('nutrition_plans')
            .update({
              title:p.title,notes:p.notes,target_kcal:p.target_kcal,target_protein_g:p.target_protein_g,
              target_carbs_g:p.target_carbs_g,target_fat_g:p.target_fat_g,plan:p.plan,revision:p.revision,
              published_at:new Date().toISOString()
            }).eq('id',p.id).select('*').single();
          if(fixErr)throw fixErr;
          data=fixed;
        }
        if(!planMatches(data,p)){if(baseErr)throw baseErr;throw new Error('La nube no confirmó el plan nutricional completo.')}
        try{nutritionCache.plan=data;window.renderNutritionCoachLoaded?.()}catch(_e){}
        finalConfirm('nutrition-plan','Plan nutricional guardado','El plan y sus cantidades quedaron verificados en la nube.',{id:p.id,revision:p.revision});
        return data;
      }).catch(fail);
    };
    window.saveNutritionPlan=wrapped;
    try{saveNutritionPlan=wrapped}catch(_e){}
  }

  async function nutritionIds(aid,date){
    const {data,error}=await supabaseClient.from('nutrition_logs')
      .select('id,meal_group_id,food_name,meal_label,grams,source,created_at')
      .eq('athlete_id',aid).eq('logged_on',date).order('created_at',{ascending:true});
    if(error)throw error;
    return data||[];
  }

  // Single calculator/custom log: confirm a genuinely new row.
  const baseInsertLog=window.insertNutritionLog||globalThis.insertNutritionLog;
  if(typeof baseInsertLog==='function'){
    const wrapped=function(data){
      const aid=athleteId();
      const date=nutritionCache?.date||dateInputToday();
      return locked('nutrition-log:'+String(aid||'')+':'+date,async()=>{
        await fresh();
        const before=await nutritionIds(aid,date),seen=new Set(before.map(x=>String(x.id)));
        enterVerify();
        let baseErr=null;
        try{await baseInsertLog.apply(this,arguments)}
        catch(e){baseErr=e}
        finally{leaveVerify()}
        const after=await nutritionIds(aid,date);
        const freshRows=after.filter(x=>!seen.has(String(x.id)));
        const row=freshRows.find(x=>String(x.food_name||'')===String(data?.food_name||'')&&
          String(x.meal_label||'')===String(data?.meal_label||'Comida')&&sameNum(x.grams,data?.grams));
        if(!row){if(baseErr)throw baseErr;throw new Error('La nube no confirmó el alimento registrado.')}
        try{await loadNutrition(true,date)}catch(_e){}
        finalQuick('nutrition-log','Registro guardado',{id:row.id,athleteId:aid,date});
        return row;
      }).catch(fail);
    };
    window.insertNutritionLog=wrapped;
    try{insertNutritionLog=wrapped}catch(_e){}
  }

  // Plan option: all expected food rows must appear as new rows.
  const basePlanOption=window.logPlanOption||globalThis.logPlanOption;
  if(typeof basePlanOption==='function'){
    const wrapped=function(mealId,optId){
      const aid=athleteId(),date=nutritionCache?.date||dateInputToday();
      const meal=typeof findNutritionMeal==='function'?findNutritionMeal(mealId):null;
      const opt=typeof findNutritionOption==='function'?findNutritionOption(mealId,optId):null;
      const expected=(opt?.items||[]).length;
      return locked('nutrition-option:'+String(aid||'')+':'+date,async()=>{
        await fresh();
        if(!expected)throw new Error('La opción no tiene alimentos para guardar.');
        const before=await nutritionIds(aid,date),seen=new Set(before.map(x=>String(x.id)));
        enterVerify();
        let baseErr=null;
        try{await basePlanOption.apply(this,arguments)}
        catch(e){baseErr=e}
        finally{leaveVerify()}
        const after=await nutritionIds(aid,date);
        const newRows=after.filter(x=>!seen.has(String(x.id))&&x.source==='plan'&&String(x.meal_label||'')===String(meal?.name||''));
        if(newRows.length<expected){if(baseErr)throw baseErr;throw new Error('No se confirmaron todos los alimentos de la opción.')}
        try{await loadNutrition(true,date)}catch(_e){}
        finalQuick('nutrition-log','Opción registrada',{athleteId:aid,date,count:newRows.length});
        return true;
      }).catch(fail);
    };
    window.logPlanOption=wrapped;
    try{logPlanOption=wrapped}catch(_e){}
  }

  // Grouped meal: verify one new meal_group_id with expected row count.
  const baseMealGroup=window.saveMealGroupV176;
  if(typeof baseMealGroup==='function'){
    window.saveMealGroupV176=function(){
      const aid=athleteId(),date=nutritionCache?.date||dateInputToday();
      const expected=document.querySelectorAll('.v176-meal-draft-row').length;
      return locked('nutrition-meal:'+String(aid||'')+':'+date,async()=>{
        await fresh();
        if(!expected)throw new Error('Agregá al menos un alimento.');
        const before=await nutritionIds(aid,date),seen=new Set(before.map(x=>String(x.id)));
        enterVerify();
        let baseErr=null;
        try{await baseMealGroup.apply(this,arguments)}
        catch(e){baseErr=e}
        finally{leaveVerify()}
        const after=await nutritionIds(aid,date);
        const newRows=after.filter(x=>!seen.has(String(x.id))&&x.meal_group_id);
        const groups=new Map();
        newRows.forEach(x=>{
          const k=String(x.meal_group_id);
          if(!groups.has(k))groups.set(k,[]);
          groups.get(k).push(x);
        });
        const group=[...groups.values()].find(x=>x.length===expected);
        if(!group){if(baseErr)throw baseErr;throw new Error('La comida no quedó completa en la nube.')}
        try{await loadNutrition(true,date)}catch(_e){}
        finalConfirm('nutrition-log','Comida guardada','Todos los alimentos de la comida quedaron confirmados en la nube.',{athleteId:aid,date,count:expected,groupId:group[0].meal_group_id});
        return true;
      }).catch(fail);
    };
  }

  const baseDeleteLog=window.deleteNutritionLog||globalThis.deleteNutritionLog;
  if(typeof baseDeleteLog==='function'){
    const wrapped=function(id){
      return locked('nutrition-delete:'+String(id||''),async()=>{
        await fresh();
        enterVerify();
        let baseErr=null;
        try{await baseDeleteLog.apply(this,arguments)}
        catch(e){baseErr=e}
        finally{leaveVerify()}
        const {data,error}=await supabaseClient.from('nutrition_logs').select('id').eq('id',id).maybeSingle();
        if(error)throw error;
        if(data){if(baseErr)throw baseErr;throw new Error('El registro nutricional sigue presente en la nube.')}
        finalQuick('nutrition-log','Registro eliminado',{id});
        return true;
      }).catch(fail);
    };
    window.deleteNutritionLog=wrapped;
    try{deleteNutritionLog=wrapped}catch(_e){}
  }

  const baseDeleteMeal=window.deleteMealGroupV176;
  if(typeof baseDeleteMeal==='function'){
    window.deleteMealGroupV176=function(gid){
      return locked('nutrition-group-delete:'+String(gid||''),async()=>{
        await fresh();
        enterVerify();
        let baseErr=null;
        try{await baseDeleteMeal.apply(this,arguments)}
        catch(e){baseErr=e}
        finally{leaveVerify()}
        const {data,error}=await supabaseClient.from('nutrition_logs').select('id').eq('meal_group_id',gid).limit(1);
        if(error)throw error;
        if((data||[]).length){if(baseErr)throw baseErr;throw new Error('La comida sigue presente en la nube.')}
        finalQuick('nutrition-log','Comida eliminada',{groupId:gid});
        return true;
      }).catch(fail);
    };
  }

  // -------------------------------------------------------
  // EXERCISE FEEDBACK: insert already returns a row; review
  // now also requires the reviewed row to exist in the DB.
  // -------------------------------------------------------
  const baseSubmitFeedback=window.submitExerciseFeedbackV73;
  if(typeof baseSubmitFeedback==='function'){
    window.submitExerciseFeedbackV73=function(){
      const aid=athleteId();
      return locked('exercise-feedback-create:'+String(aid||''),async()=>{
        await fresh();
        const {data:before,error:beforeErr}=await supabaseClient.from('exercise_feedback')
          .select('id').eq('athlete_id',aid).eq('student_id',currentUser.id);
        if(beforeErr)throw beforeErr;
        const seen=new Set((before||[]).map(x=>String(x.id)));
        enterVerify();
        let baseErr=null;
        try{await baseSubmitFeedback.apply(this,arguments)}
        catch(e){baseErr=e}
        finally{leaveVerify()}
        const {data:after,error:afterErr}=await supabaseClient.from('exercise_feedback')
          .select('id,status,feedback_type,created_at').eq('athlete_id',aid).eq('student_id',currentUser.id)
          .order('created_at',{ascending:false}).limit(20);
        if(afterErr)throw afterErr;
        const row=(after||[]).find(x=>!seen.has(String(x.id)));
        if(!row){if(baseErr)throw baseErr;throw new Error('La nube no confirmó el comentario del ejercicio.')}
        finalQuick('exercise-feedback',row.feedback_type==='discomfort'?'Molestia enviada':'Comentario enviado',{id:row.id});
        return row;
      }).catch(fail);
    };
  }

  const baseReviewFeedback=window.reviewExerciseFeedbackV73;
  if(typeof baseReviewFeedback==='function'){
    window.reviewExerciseFeedbackV73=function(id){
      return locked('exercise-feedback-review:'+String(id||''),async()=>{
        await fresh();
        enterVerify();
        let baseErr=null;
        try{await baseReviewFeedback.apply(this,arguments)}
        catch(e){baseErr=e}
        finally{leaveVerify()}
        const {data,error}=await supabaseClient.from('exercise_feedback')
          .select('id,status,reviewed_by,reviewed_at').eq('id',id).single();
        if(error)throw error;
        if(data.status!=='reviewed'||!data.reviewed_at){if(baseErr)throw baseErr;throw new Error('La revisión no quedó confirmada.')}
        finalQuick('exercise-feedback','Comentario revisado',{id});
        return true;
      }).catch(fail);
    };
  }

  // Coach feedback attached to a check-in also gets a read-back.
  const baseCheckinFeedback=window.saveCheckinFeedback||globalThis.saveCheckinFeedback;
  if(typeof baseCheckinFeedback==='function'){
    const wrapped=function(id){
      const value=(document.getElementById('fb_'+id)?.value||'').trim();
      return locked('checkin-feedback:'+String(id||''),async()=>{
        await fresh();
        enterVerify();
        let baseErr=null;
        try{await baseCheckinFeedback.apply(this,arguments)}
        catch(e){baseErr=e}
        finally{leaveVerify()}
        const {data,error}=await supabaseClient.from('weekly_checkins')
          .select('id,coach_feedback,reviewed_at').eq('id',id).single();
        if(error)throw error;
        if(String(data.coach_feedback||'')!==String(value||'')||!data.reviewed_at){
          if(baseErr)throw baseErr;
          throw new Error('El feedback del check-in no quedó confirmado.');
        }
        finalQuick('checkin-feedback','Feedback guardado',{id});
        return data;
      }).catch(fail);
    };
    window.saveCheckinFeedback=wrapped;
    try{saveCheckinFeedback=wrapped}catch(_e){}
  }

  window.__fjzV304={
    version:VERSION,
    globalSaveIntegrity:true,
    workoutReadBack:true,
    routineReadBack:true,
    reorderReadBack:true,
    agendaExactReadBack:true,
    agendaPartialRepair:true,
    reminderReadBack:true,
    measurementReadBack:true,
    measurementEditReadBack:true,
    photoTwoResourceCompensation:true,
    nutritionPlanReadBack:true,
    nutritionSingleLogReadBack:true,
    nutritionOptionReadBack:true,
    nutritionMealGroupReadBack:true,
    nutritionDeleteReadBack:true,
    exerciseFeedbackReadBack:true,
    checkinFeedbackReadBack:true,
    successDeferredUntilVerified:true,
    freshAuthForCriticalWrites:true,
    duplicateCriticalWriteLocks:true,
    noExtraTimers:true,
    noExtraListeners:true,
    noExtraObservers:true
  };
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-global-save-integrity" content="21.04">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V21.04 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-global-save-integrity" content="21.04"',
    'id="v304GlobalSaveIntegrityRuntime"',
    "globalSaveIntegrity:true",
    "workoutReadBack:true",
    "routineReadBack:true",
    "reorderReadBack:true",
    "agendaExactReadBack:true",
    "agendaPartialRepair:true",
    "measurementReadBack:true",
    "photoTwoResourceCompensation:true",
    "nutritionPlanReadBack:true",
    "nutritionSingleLogReadBack:true",
    "nutritionOptionReadBack:true",
    "nutritionMealGroupReadBack:true",
    "nutritionDeleteReadBack:true",
    "exerciseFeedbackReadBack:true",
    "successDeferredUntilVerified:true",
    "duplicateCriticalWriteLocks:true",
    "La nube no confirmó completamente la sesión.",
    "La agenda no quedó idéntica a lo seleccionado.",
    "La foto y su registro quedaron confirmados en la nube.",
    "La comida no quedó completa en la nube.",
    "actualOrderV304",
]:
    if marker not in html:
        raise RuntimeError("V21.04 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.04 global save integrity")
print("V21.04 BEFORE:",before)
print("V21.04 AFTER:",after)
