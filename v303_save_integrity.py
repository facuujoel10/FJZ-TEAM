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
    'meta name="fjz-review-resolution-authority" content="21.02"',
    'id="v170ConsolidatedRuntime"',
    "__fjzConfirmSavedV264",
    "duplicateAsyncSaveGuard:true",
    "checkinUsesConfirmedState:true",
    "confirmedCheckinSuccess:true",
    "checkinSuccessOnlyAfterCloudConfirmation:true",
]:
    if marker not in html:
        raise RuntimeError("V21.03 prerequisite missing "+marker)

runtime=r"""
<script id="v303SaveIntegrityRuntime">
(function(){
  const RECEIPT_KEY='fjz_last_confirmed_save_v303';
  const CHECKIN_FIELDS=[
    ['Sueño','ciSleep','sleep_quality'],
    ['Hambre','ciHunger','hunger_level'],
    ['Estrés','ciStress','stress_level'],
    ['Energía','ciEnergy','energy_level'],
    ['Adherencia','ciAdh','adherence_level'],
    ['Ánimo','ciMood','mood_level'],
    ['Motivación','ciMotivation','motivation_level'],
    ['Recuperación','ciRecovery','recovery_level']
  ];
  let checkinPromise=null;

  const safe=v=>String(v??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
  const nowIso=()=>new Date().toISOString();

  function saveReceipt(kind,title,meta={}){
    const receipt={kind:String(kind||'save'),title:String(title||'Guardado confirmado'),at:nowIso(),userId:currentUser?.id||null,...meta};
    try{localStorage.setItem(RECEIPT_KEY,JSON.stringify(receipt))}catch(_e){}
    window.__fjzLastConfirmedSaveV303=receipt;
    return receipt;
  }
  function readReceipt(){
    if(window.__fjzLastConfirmedSaveV303)return window.__fjzLastConfirmedSaveV303;
    try{
      const raw=localStorage.getItem(RECEIPT_KEY);
      const r=raw?JSON.parse(raw):null;
      if(r&&(!r.userId||String(r.userId)===String(currentUser?.id||'')))return r;
    }catch(_e){}
    return null;
  }
  window.__fjzRecordConfirmedSaveV303=saveReceipt;

  const baseConfirm=window.__fjzConfirmSavedV264;
  if(typeof baseConfirm==='function'){
    window.__fjzConfirmSavedV264=function(title,copy){
      saveReceipt('confirmed',title||'Guardado confirmado',{copy:String(copy||'')});
      return baseConfirm.apply(this,arguments);
    };
  }
  const baseQuick=window.__fjzQuickSavedV264;
  if(typeof baseQuick==='function'){
    window.__fjzQuickSavedV264=function(title){
      saveReceipt('confirmed',title||'Guardado confirmado');
      return baseQuick.apply(this,arguments);
    };
  }

  function trackingReceipt(){
    const r=readReceipt();
    if(!r||r.kind!=='checkin'||String(r.userId||'')!==String(currentUser?.id||''))return null;
    return r;
  }
  function injectCheckinReceipt(){
    const host=document.getElementById('v170CheckinStatus');
    const r=trackingReceipt();
    if(!host||!r)return;
    const age=Date.now()-Date.parse(r.at||0);
    if(!Number.isFinite(age)||age>14*86400000)return;
    const time=new Intl.DateTimeFormat('es-AR',{hour:'2-digit',minute:'2-digit'}).format(new Date(r.at));
    const existing=document.getElementById('v303CheckinReceipt');
    if(existing)existing.remove();
    host.insertAdjacentHTML('afterbegin',
      '<div class="v303-save-receipt" id="v303CheckinReceipt">'+
        '<span class="v303-save-check">✓</span>'+
        '<div><strong>Check-in confirmado en la nube</strong>'+
        '<small>Semana '+safe(r.week||'—')+' · '+safe(time)+' · ID '+safe(String(r.rowId||'').slice(0,8))+'</small></div>'+
      '</div>');
  }

  const baseRenderTrackingStudent=window.renderTrackingStudent;
  if(typeof baseRenderTrackingStudent==='function'){
    window.renderTrackingStudent=function(){
      const out=baseRenderTrackingStudent.apply(this,arguments);
      try{injectCheckinReceipt()}catch(_e){}
      return out;
    };
  }

  const score=id=>{
    const n=Number(document.getElementById(id)?.value);
    return Number.isFinite(n)&&n>=1&&n<=10?n:null;
  };
  const weekStart=()=>{
    try{return weekStartISO()}catch(_e){
      const d=new Date(),day=(d.getDay()+6)%7;d.setDate(d.getDate()-day);return d.toISOString().slice(0,10);
    }
  };
  const athleteId=()=>{
    try{return trackingAthleteId()}catch(_e){return linkedAthleteId||null}
  };

  function setCheckinButton(busy){
    const btn=[...document.querySelectorAll('.tracking-form button')].find(x=>/Enviar check-in|Guardando/.test(x.textContent||''));
    if(!btn)return;
    btn.disabled=!!busy;
    btn.classList.toggle('v277-saving',!!busy);
    btn.setAttribute('aria-busy',busy?'true':'false');
    btn.textContent=busy?'Guardando y verificando…':'Enviar check-in';
    if(!busy)btn.removeAttribute('aria-busy');
  }

  function sameNumeric(a,b){
    if(a==null&&b==null)return true;
    return Number(a)===Number(b);
  }
  function verifyCheckinRow(row,payload){
    if(!row?.id)return false;
    if(String(row.athlete_id||'')!==String(payload.athlete_id||''))return false;
    if(String(row.student_id||'')!==String(payload.student_id||''))return false;
    if(String(row.week_start||'')!==String(payload.week_start||''))return false;
    if(!sameNumeric(row.weight_kg,payload.weight_kg))return false;
    for(const [,,key] of CHECKIN_FIELDS)if(!sameNumeric(row[key],payload[key]))return false;
    return String(row.notes||'')===String(payload.notes||'');
  }

  function reconcileTracking(row,aid){
    try{
      const prev=Array.isArray(trackingCache?.checkins)?trackingCache.checkins:[];
      trackingCache.checkins=[row,...prev.filter(x=>String(x?.id)!==String(row.id)&&String(x?.week_start)!==String(row.week_start))];
      trackingLoadedFor=aid;
    }catch(_e){}
    try{const s=student?.();if(s){s.checkin='Recibido';saveState?.()}}catch(_e){}
  }

  window.submitWeeklyCheckin=async function(){
    if(checkinPromise)return checkinPromise;
    checkinPromise=(async()=>{
      if(!cloudEnabled||!supabaseClient){toast?.('El check-in requiere conexión con la nube');return false}
      try{
        const fresh=await window.__fjzEnsureFreshAuthV194?.(false);
        if(fresh===false)throw new Error('Tu sesión necesita actualizarse. Volvé a ingresar y reenviá el check-in.');
      }catch(e){
        if(String(e?.message||'').includes('actualizarse'))throw e;
      }

      const aid=athleteId();
      if(!aid){toast?.('No encuentro tu ficha vinculada');return false}
      const missing=CHECKIN_FIELDS.filter(([,id])=>score(id)==null).map(x=>x[0]);
      if(missing.length){toast?.('Falta completar: '+missing.join(', '));return false}

      const weightRaw=document.getElementById('ciWeight')?.value||'';
      const weight=weightRaw?Number(weightRaw):null;
      if(weight!=null&&(!Number.isFinite(weight)||weight<20||weight>400)){toast?.('Revisá el peso ingresado');return false}

      const payload={
        athlete_id:aid,
        student_id:currentUser.id,
        week_start:document.getElementById('ciWeek')?.value||weekStart(),
        weight_kg:weight,
        notes:(document.getElementById('ciNotes')?.value||'').trim(),
        submitted_at:nowIso()
      };
      for(const [,,key] of CHECKIN_FIELDS){
        const id=CHECKIN_FIELDS.find(x=>x[2]===key)[1];
        payload[key]=score(id);
      }

      setCheckinButton(true);
      const columns='id,athlete_id,student_id,week_start,weight_kg,sleep_quality,stress_level,energy_level,adherence_level,mood_level,hunger_level,recovery_level,motivation_level,notes,submitted_at,created_at,updated_at';
      const {data:written,error:writeError}=await supabaseClient.from('weekly_checkins')
        .upsert(payload,{onConflict:'athlete_id,week_start'})
        .select(columns)
        .single();
      if(writeError)throw writeError;
      if(!verifyCheckinRow(written,payload))throw new Error('La nube respondió, pero los datos guardados no coinciden con el check-in enviado.');

      // Independent read-back: protects the UI from stale tracking/realtime state.
      let verified=written;
      try{
        const {data:readBack,error:readError}=await supabaseClient.from('weekly_checkins')
          .select(columns)
          .eq('athlete_id',aid)
          .eq('week_start',payload.week_start)
          .single();
        if(!readError&&verifyCheckinRow(readBack,payload))verified=readBack;
      }catch(_e){}

      reconcileTracking(verified,aid);
      saveReceipt('checkin','Check-in guardado',{
        week:verified.week_start,rowId:verified.id,athleteId:aid,submittedAt:verified.submitted_at
      });

      try{window.renderTrackingStudent?.()}catch(_e){}
      try{injectCheckinReceipt()}catch(_e){}
      window.__fjzConfirmSavedV264?.(
        'Check-in guardado con éxito',
        'La base confirmó tu check-in de la semana '+String(verified.week_start||'')+'. Tu coach ya puede revisarlo.'
      );
      return true;
    })().catch(e=>{
      console.error('TEAM FJZ V21.03 check-in save integrity',e);
      const msg=typeof cloudErr==='function'?cloudErr(e):(e?.message||'No se pudo guardar el check-in');
      toast?.(msg);
      return false;
    }).finally(()=>{
      checkinPromise=null;
      setCheckinButton(false);
    });
    return checkinPromise;
  };

  window.__fjzVerifyLatestCheckinV303=async function(){
    const aid=athleteId();if(!aid||!supabaseClient)return null;
    const week=document.getElementById('ciWeek')?.value||weekStart();
    const {data,error}=await supabaseClient.from('weekly_checkins')
      .select('id,athlete_id,student_id,week_start,weight_kg,sleep_quality,stress_level,energy_level,adherence_level,mood_level,hunger_level,recovery_level,motivation_level,notes,submitted_at,updated_at')
      .eq('athlete_id',aid).eq('week_start',week).single();
    if(error)return null;
    reconcileTracking(data,aid);
    saveReceipt('checkin','Check-in verificado',{week:data.week_start,rowId:data.id,athleteId:aid,submittedAt:data.submitted_at});
    try{injectCheckinReceipt()}catch(_e){}
    return data;
  };

  window.__fjzV303={
    version:'21.03',
    checkinWriteReadBack:true,
    checkinUiUsesVerifiedRow:true,
    persistentSaveReceipt:true,
    duplicateCheckinGuard:true,
    freshAuthBeforeCheckin:true,
    noRealtimeDependencyForSaveConfirmation:true,
    confirmedSaveReceiptAcrossUi:true,
    noExtraTimers:true,
    noExtraListeners:true,
    noExtraObservers:true
  };
})();
</script>
"""

css=r"""
/* TEAM FJZ · V21.03 SAVE INTEGRITY */
.v303-save-receipt{
  display:flex;
  align-items:center;
  gap:10px;
  margin:0 0 10px;
  padding:10px 12px;
  border:1px solid rgba(59,213,138,.30);
  border-radius:11px;
  background:rgba(59,213,138,.065);
  color:#eaf9f1;
}
.v303-save-check{
  display:grid;
  place-items:center;
  width:28px;height:28px;flex:0 0 28px;
  border-radius:50%;
  background:rgba(59,213,138,.16);
  color:#63e7a5;
  font-size:16px;
  font-weight:950;
}
.v303-save-receipt strong{display:block;font-size:11px;line-height:1.3}
.v303-save-receipt small{display:block;margin-top:3px;color:#aeb9b3;font-size:9px;line-height:1.3}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V21.03 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-save-integrity" content="21.03">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V21.03 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-save-integrity" content="21.03"',
    'id="v303SaveIntegrityRuntime"',
    "checkinWriteReadBack:true",
    "checkinUiUsesVerifiedRow:true",
    "persistentSaveReceipt:true",
    "duplicateCheckinGuard:true",
    "freshAuthBeforeCheckin:true",
    "noRealtimeDependencyForSaveConfirmation:true",
    "confirmedSaveReceiptAcrossUi:true",
    ".upsert(payload,{onConflict:'athlete_id,week_start'})",
    ".eq('athlete_id',aid)",
    ".eq('week_start',payload.week_start)",
    "Check-in confirmado en la nube",
    "Guardando y verificando…",
]:
    if marker not in html: raise RuntimeError("V21.03 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.03 save integrity")
print("V21.03 BEFORE:",before)
print("V21.03 AFTER:",after)
