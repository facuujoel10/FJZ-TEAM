import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v145WorkoutAutosaveStyles">
.v145-autosave{
  display:flex;align-items:center;justify-content:space-between;gap:12px;
  margin:10px 0 14px;padding:10px 12px;border:1px solid rgba(80,200,140,.22);
  border-radius:12px;background:rgba(80,200,140,.045)
}
.v145-autosave-main{min-width:0}
.v145-autosave-main strong{display:block;font-size:11px}
.v145-autosave-main span{display:block;margin-top:3px;font-size:9px;color:var(--muted)}
.v145-autosave-actions{display:flex;gap:7px;flex-wrap:wrap}
.v145-resume{
  margin:0 0 14px;padding:12px;border:1px solid rgba(90,167,255,.24);
  border-radius:13px;background:rgba(90,167,255,.045)
}
.v145-resume-head{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
.v145-resume-actions{display:flex;gap:7px;flex-wrap:wrap;margin-top:10px}
@media(max-width:640px){
  .v145-autosave,.v145-resume-head{align-items:flex-start;flex-direction:column}
  .v145-autosave-actions,.v145-resume-actions{width:100%}
  .v145-autosave-actions .btn,.v145-resume-actions .btn{flex:1}
}
</style>
"""

js=r"""
<script id="v145WorkoutAutosaveRuntime">
(function(){
  const VERSION='14.5';
  let cloudTimer=null;
  let lastSavedAt=null;

  function safeCloneV145(x){
    try{return JSON.parse(JSON.stringify(x))}catch(e){return x}
  }

  function localKeyV145(s,d){
    return 'fjz_workout_draft_v145:'+String(s?.id||'student')+':'+String(d?.id||'day');
  }

  function meaningfulV145(p){
    if(!p)return false;
    return !!(
      Object.keys(p.workoutDraft||{}).length ||
      Object.keys(p.methodDraft||{}).length
    );
  }

  function currentPackV145(){
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
  }

  function readLocalV145(s,d){
    try{
      const raw=localStorage.getItem(localKeyV145(s,d));
      return raw?JSON.parse(raw):null;
    }catch(e){return null}
  }

  function readCloudV145(s,d){
    return s?.workoutDrafts?.[d?.id]||null;
  }

  function freshestV145(a,b){
    if(!a)return b||null;
    if(!b)return a||null;
    const ta=Date.parse(a.updatedAt||0)||0,tb=Date.parse(b.updatedAt||0)||0;
    return tb>ta?b:a;
  }

  function validForDayV145(p,s,d){
    return !!(p&&p.studentId===s?.id&&p.dayId===d?.id&&meaningfulV145(p));
  }

  function pruneForDayV145(p,d){
    if(!p||!d)return p;
    const uids=new Set((d.exercises||[]).map(e=>e.uid));
    const wd={},md={};
    Object.entries(p.workoutDraft||{}).forEach(([k,v])=>{if(uids.has(k))wd[k]=v});
    Object.entries(p.methodDraft||{}).forEach(([k,v])=>{if(uids.has(k))md[k]=v});
    return {...p,workoutDraft:wd,methodDraft:md};
  }

  function setStatusV145(when){
    lastSavedAt=when||new Date().toISOString();
    const n=el('v145AutosaveStatus');
    if(n){
      const d=new Date(lastSavedAt);
      n.textContent='Último guardado '+d.toLocaleTimeString('es-AR',{hour:'2-digit',minute:'2-digit'});
    }
  }

  function persistLocalV145(){
    const p=currentPackV145();
    if(!p||!meaningfulV145(p))return null;
    try{localStorage.setItem(localKeyV145(student(),student().days[currentDay]),JSON.stringify(p))}catch(e){}
    setStatusV145(p.updatedAt);
    return p;
  }

  function persistCloudV145(pack){
    const p=pack||currentPackV145();
    const s=student?.(),d=s?.days?.[currentDay];
    if(!p||!s||!d||!meaningfulV145(p))return;
    s.workoutDrafts=s.workoutDrafts||{};
    s.workoutDrafts[d.id]=safeCloneV145(p);
    saveState();
  }

  function schedulePersistV145(){
    const p=persistLocalV145();
    if(!p)return;
    clearTimeout(cloudTimer);
    cloudTimer=setTimeout(()=>{
      cloudTimer=null;
      persistCloudV145(p);
    },650);
  }
  window.__fjzPersistWorkoutDraftV145=schedulePersistV145;

  function clearDraftV145(dayId,save=true){
    const s=student?.();
    const d=s?.days?.find(x=>x.id===dayId);
    if(!s||!d)return;
    try{localStorage.removeItem(localKeyV145(s,d))}catch(e){}
    if(s.workoutDrafts&&s.workoutDrafts[dayId]){
      delete s.workoutDrafts[dayId];
      if(!Object.keys(s.workoutDrafts).length)delete s.workoutDrafts;
    }
    clearTimeout(cloudTimer);
    cloudTimer=null;
    if(save)saveState();
  }

  function restoreDraftV145(i){
    const s=student?.(),d=s?.days?.[i];
    if(!s||!d)return null;
    let p=freshestV145(readLocalV145(s,d),readCloudV145(s,d));
    if(!validForDayV145(p,s,d))return null;
    p=pruneForDayV145(p,d);
    if(!meaningfulV145(p))return null;
    return p;
  }

  window.resumeWorkoutDraftV145=function(dayId){
    const s=student();
    const i=(s.days||[]).findIndex(d=>d.id===dayId);
    if(i<0)return;
    startWorkout(i);
  };

  window.confirmDiscardWorkoutDraftV145=function(dayId){
    const s=student();
    const d=(s.days||[]).find(x=>x.id===dayId);
    if(!d)return;
    showModal(
      '<div class="modal-head"><div><h3>Descartar borrador</h3><div class="muted tiny">Se eliminarán los datos todavía no finalizados de este entrenamiento.</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="card"><strong>'+esc(d.name)+'</strong><div class="muted tiny" style="margin-top:5px">La rutina y el historial ya guardado no se modifican.</div></div>'+
      '<div class="pill-row" style="justify-content:flex-end;margin-top:12px"><button class="btn" onclick="closeModal()">Cancelar</button><button class="btn primary" onclick="discardWorkoutDraftV145(\''+d.id+'\')">Descartar</button></div>'
    );
  };

  window.discardWorkoutDraftV145=function(dayId){
    const active=student()?.days?.[currentDay]?.id===dayId&&studentTab==='workout';
    clearDraftV145(dayId,true);
    if(active){
      workoutDraft={};
      window.__fjzMethodDraftV110={};
    }
    closeModal();
    render();
    toast('Borrador descartado');
  };

  const baseStartWorkoutV145=startWorkout;
  startWorkout=function(i){
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
  };

  const baseSetWorkoutV145=setWorkout;
  setWorkout=function(uidv,si,field,val){
    const out=baseSetWorkoutV145.apply(this,arguments);
    schedulePersistV145();
    return out;
  };

  if(typeof window.setMethodPartV137==='function'){
    const baseMethodPartV145=window.setMethodPartV137;
    window.setMethodPartV137=function(){
      const out=baseMethodPartV145.apply(this,arguments);
      schedulePersistV145();
      return out;
    };
  }

  if(typeof window.setMethodNoteV137==='function'){
    const baseMethodNoteV145=window.setMethodNoteV137;
    window.setMethodNoteV137=function(){
      const out=baseMethodNoteV145.apply(this,arguments);
      schedulePersistV145();
      return out;
    };
  }

  function clearIfSessionSavedV145(dayId,beforeCount){
    const s=student();
    if((s.sessions||[]).length>beforeCount){
      clearDraftV145(dayId,true);
      workoutDraft={};
      window.__fjzMethodDraftV110={};
      return true;
    }
    return false;
  }

  const baseFinishWorkoutV145=finishWorkout;
  finishWorkout=function(){
    const s=student(),d=s.days[currentDay],before=(s.sessions||[]).length;
    const out=baseFinishWorkoutV145.apply(this,arguments);
    clearIfSessionSavedV145(d.id,before);
    return out;
  };

  if(typeof window.confirmPartialSessionV106==='function'){
    const baseConfirmPartialV145=window.confirmPartialSessionV106;
    window.confirmPartialSessionV106=function(){
      const s=student(),d=s.days[currentDay],before=(s.sessions||[]).length;
      const out=baseConfirmPartialV145.apply(this,arguments);
      clearIfSessionSavedV145(d.id,before);
      return out;
    };
  }

  function latestDraftForStudentV145(){
    const s=student();
    if(!s)return null;
    let best=null,bestDay=null;
    (s.days||[]).forEach(d=>{
      const p=freshestV145(readLocalV145(s,d),readCloudV145(s,d));
      if(!validForDayV145(p,s,d))return;
      if(!best||(Date.parse(p.updatedAt||0)||0)>(Date.parse(best.updatedAt||0)||0)){
        best=p;bestDay=d;
      }
    });
    return best&&bestDay?{pack:best,day:bestDay}:null;
  }

  function injectHomeResumeV145(){
    if(currentProfile?.role!=='student'||studentTab!=='home')return;
    if(el('v145ResumeCard'))return;
    const item=latestDraftForStudentV145();
    if(!item)return;
    const hero=el('view')?.querySelector('.hero');
    if(!hero)return;
    const box=document.createElement('div');
    box.id='v145ResumeCard';
    box.className='v145-resume';
    const time=new Date(item.pack.updatedAt);
    box.innerHTML=
      '<div class="v145-resume-head"><div><strong>Entrenamiento en progreso</strong>'+
      '<div class="muted tiny" style="margin-top:4px">'+esc(item.day.name)+' · guardado '+esc(time.toLocaleTimeString('es-AR',{hour:'2-digit',minute:'2-digit'}))+'</div></div>'+
      '<span class="badge blue">Autoguardado</span></div>'+
      '<div class="v145-resume-actions"><button class="btn primary" onclick="resumeWorkoutDraftV145(\''+item.day.id+'\')">Continuar entrenamiento</button>'+
      '<button class="btn" onclick="confirmDiscardWorkoutDraftV145(\''+item.day.id+'\')">Descartar</button></div>';
    hero.insertAdjacentElement('afterend',box);
  }

  function injectWorkoutStatusV145(){
    if(currentProfile?.role!=='student'||studentTab!=='workout')return;
    if(el('v145AutosaveBox'))return;
    const v=el('view'),hero=v?.querySelector('.hero');
    if(!hero)return;
    const d=student()?.days?.[currentDay];
    const box=document.createElement('div');
    box.id='v145AutosaveBox';
    box.className='v145-autosave';
    const p=d?freshestV145(readLocalV145(student(),d),readCloudV145(student(),d)):null;
    const when=p?.updatedAt||lastSavedAt;
    box.innerHTML=
      '<div class="v145-autosave-main"><strong>Autoguardado activo</strong>'+
      '<span id="v145AutosaveStatus">'+(when?'Último guardado '+new Date(when).toLocaleTimeString('es-AR',{hour:'2-digit',minute:'2-digit'}):'Se guarda cada cambio de peso, reps y RIR')+'</span></div>'+
      '<div class="v145-autosave-actions">'+
      (d?'<button class="btn small" onclick="confirmDiscardWorkoutDraftV145(\''+d.id+'\')">Descartar borrador</button>':'')+
      '</div>';
    hero.insertAdjacentElement('afterend',box);
  }

  const baseRenderStudentV145=renderStudent;
  renderStudent=function(){
    const out=baseRenderStudentV145.apply(this,arguments);
    if(studentTab==='home')injectHomeResumeV145();
    if(studentTab==='workout')injectWorkoutStatusV145();
    return out;
  };

  function emergencyPersistV145(){
    if(currentProfile?.role!=='student'||studentTab!=='workout')return;
    const p=persistLocalV145();
    if(p){
      const s=student(),d=s?.days?.[currentDay];
      if(s&&d){
        s.workoutDrafts=s.workoutDrafts||{};
        s.workoutDrafts[d.id]=safeCloneV145(p);
        try{
          const v=state;
          v.version=5;
          localStorage.setItem('fjz_v4_state',JSON.stringify(v));
        }catch(e){}
      }
    }
  }

  window.addEventListener('pagehide',emergencyPersistV145);
  document.addEventListener('visibilitychange',()=>{
    if(document.visibilityState==='hidden')emergencyPersistV145();
  });

  window.__fjzWorkoutAutosaveV145={
    version:VERSION,
    localImmediate:true,
    cloudDebounceMs:650,
    restoresAfterClose:true,
    methodDrafts:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "Autoguardado activo",
  "Continuar entrenamiento",
  "__fjzWorkoutAutosaveV145",
  "restoresAfterClose:true",
  "pagehide"
]:
    if marker not in html:
        raise RuntimeError("V14.5 missing autosave marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V14.5 workout autosave enabled")
