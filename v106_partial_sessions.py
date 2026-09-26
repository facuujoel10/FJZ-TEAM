import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")
html=html.replace("TEAM FJZ V10.5","TEAM FJZ V10.6")

css=r"""
<style id="v106PartialSessionsStyles">
.v106-partial-summary{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:12px 0}
.v106-partial-summary .card{padding:11px;text-align:center}
.v106-partial-summary strong{display:block;font-size:22px}
.v106-partial-list{margin-top:10px;padding:10px 12px;border:1px solid var(--border);border-radius:12px;background:rgba(255,255,255,.025)}
@media(max-width:520px){.v106-partial-summary{grid-template-columns:1fr}}
</style>
"""

js=r"""
<script id="v106PartialSessionsRuntime">
(function(){
  function isBodyweightV106(e){
    return /peso corporal|bodyweight/i.test(String(e?.equipment||''));
  }
  function validSetV106(e,set){
    if(!Array.isArray(set))return false;
    const kg=Number(set[0]),reps=Number(set[1]),rir=Number(set[2]);
    const loadOk=isBodyweightV106(e)?Number.isFinite(kg)&&kg>=0:Number.isFinite(kg)&&kg>0;
    return loadOk&&Number.isFinite(reps)&&reps>0&&Number.isFinite(rir)&&rir>=0;
  }
  function sessionDraftV106(){
    const s=student(),d=s.days[currentDay];
    const registered=[],skipped=[];
    for(const e of d.exercises){
      const draft=workoutDraft[e.uid];
      if(!draft){skipped.push(e);continue}
      const sets=[],setIndexes=[];
      draft.forEach((x,i)=>{
        if(validSetV106(e,x)){
          sets.push([Number(x[0]),Number(x[1]),Number(x[2])]);
          setIndexes.push(i);
        }
      });
      if(!sets.length){skipped.push(e);continue}
      registered.push({e,sets,setIndexes,complete:sets.length===e.sets});
    }
    return {s,d,registered,skipped};
  }
  function targetSigV106(e){
    const base=targetSig(e);
    return e?.repMode==='exact'&&Array.isArray(e.repsExact)&&e.repsExact.length
      ? base+'|'+e.repsExact.join('-')
      : base;
  }

  function saveSessionV106(pack){
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
          recommendation:clone(r)
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
        recommendation:clone(r)
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
    s.sessions.push(session);
    s.lastWorkout=session.date;
    saveState();

    const skippedText=skipped.length
      ? '<div class="v106-partial-list"><strong>'+skipped.length+' ejercicio'+(skipped.length===1?'':'s')+' sin registrar</strong><div class="muted tiny" style="margin-top:4px">'+esc(skipped.map(e=>e.name).join(' · '))+'</div></div>'
      :'';
    const partialText=partial
      ? '<div class="v106-partial-list"><strong>'+partial+' ejercicio'+(partial===1?'':'s')+' con registro parcial</strong><div class="muted tiny" style="margin-top:4px">Esas series quedan guardadas en la sesión, pero no modifican la progresión automática hasta completar el ejercicio.</div></div>'
      :'';

    showModal(
      '<div class="modal-head"><h3>Sesión guardada</h3><button class="btn small" onclick="closeModal();studentTab=\'home\';render()">✕</button></div>'+
      '<div class="v106-partial-summary">'+
        '<div class="card"><strong>'+registered.length+'</strong><div class="muted tiny">Ejercicios registrados</div></div>'+
        '<div class="card"><strong>'+totalSets+'</strong><div class="muted tiny">Series guardadas</div></div>'+
        '<div class="card"><strong>'+skipped.length+'</strong><div class="muted tiny">Ejercicios omitidos</div></div>'+
      '</div>'+
      skippedText+partialText+
      '<p class="muted" style="margin-top:12px">La sesión queda en el historial aunque no se haya completado toda la rutina.</p>'+
      '<button class="btn primary" style="width:100%" onclick="closeModal();studentTab=\'home\';render()">Volver al inicio</button>'
    );
  }

  window.finishWorkout=function(){
    const pack=sessionDraftV106();
    if(!pack.d.exercises.length){studentTab='home';render();return}
    if(!pack.registered.length){
      toast('Cargá al menos una serie para guardar la sesión');
      return;
    }

    const partialExercises=pack.registered.filter(x=>!x.complete);
    const hasMissing=pack.skipped.length||partialExercises.length;
    if(!hasMissing){
      saveSessionV106(pack);
      return;
    }

    const missingParts=[];
    if(pack.skipped.length)missingParts.push(pack.skipped.length+' ejercicio'+(pack.skipped.length===1?'':'s')+' sin cargar');
    if(partialExercises.length)missingParts.push(partialExercises.length+' ejercicio'+(partialExercises.length===1?'':'s')+' incompleto'+(partialExercises.length===1?'':'s'));

    window.__v106PendingSession=pack;
    showModal(
      '<div class="modal-head"><div><h3>Guardar sesión incompleta</h3><div class="muted tiny">No hace falta completar toda la rutina para guardar el entrenamiento.</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="card"><strong>'+esc(missingParts.join(' · '))+'</strong><div class="muted tiny" style="margin-top:6px">Solo se guardarán los ejercicios y series que tengan datos válidos. Lo que no hiciste o no cargaste quedará como omitido.</div></div>'+
      '<div class="pill-row" style="justify-content:flex-end;margin-top:12px"><button class="btn" onclick="closeModal()">Seguir cargando</button><button class="btn primary" onclick="confirmPartialSessionV106()">Guardar sesión igual</button></div>'
    );
  };

  window.confirmPartialSessionV106=function(){
    const pack=window.__v106PendingSession;
    window.__v106PendingSession=null;
    if(!pack){closeModal();return}
    closeModal();
    saveSessionV106(pack);
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)
p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8").replace("team-fjz-v10-5","team-fjz-v10-6").replace("team-fjz-v10-4","team-fjz-v10-6")
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V10.6 partial sessions:",len(html),"bytes")
