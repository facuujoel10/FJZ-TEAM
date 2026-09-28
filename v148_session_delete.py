import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v148SessionDeleteStyles">
.v148-history-actions{display:flex;gap:7px;flex-wrap:wrap;justify-content:flex-end}
.v148-danger{border-color:rgba(255,82,95,.35)!important;color:#ff8a94!important;background:rgba(255,82,95,.06)!important}
.v148-danger:hover{background:rgba(255,82,95,.11)!important}
.v148-confirm{border:1px solid rgba(255,82,95,.22);background:rgba(255,82,95,.045);border-radius:12px;padding:12px}
</style>
"""

js=r"""
<script id="v148SessionDeleteRuntime">
(function(){
  const VERSION='14.8';

  function cloneV148(x){
    return x==null?x:JSON.parse(JSON.stringify(x));
  }

  function athleteRowV148(s){
    try{
      const vals=[...((cloudAthletes&&cloudAthletes.values)?cloudAthletes.values():[])];
      return cloudAthletes?.get?.(s?.id)
        || vals.find(a=>a.client_id===s?.id)
        || vals.find(a=>currentProfile?.role==='student'&&a.user_id===currentUser?.id)
        || vals.find(a=>linkedAthleteId&&a.id===linkedAthleteId)
        || null;
    }catch(e){return null}
  }

  function sameSetsV148(a,b){
    try{return JSON.stringify(a||[])===JSON.stringify(b||[])}catch(e){return false}
  }

  function removeHistoryForSessionV148(s,session){
    const results=session?.exerciseResults||[];
    results.forEach(r=>{
      const ex=allExercises(s).find(x=>x.e.uid===r.exerciseUid)?.e;
      if(!ex||!Array.isArray(ex.history)||!ex.history.length)return;

      // Prefer explicit future linkage if present.
      const explicit=ex.history.findIndex(h=>h?.sourceSessionId===session.id);
      if(explicit>=0){
        ex.history.splice(explicit,1);
        return;
      }

      // Legacy sessions did not store sourceSessionId in exercise history.
      // Remove only the nearest matching record by time + set payload.
      const st=Date.parse(session.date||0)||0;
      let best=-1,bestDelta=Infinity;
      ex.history.forEach((h,i)=>{
        if(!sameSetsV148(h?.sets,r?.sets))return;
        const ht=Date.parse(h?.date||0)||0;
        const d=Math.abs(ht-st);
        if(d<bestDelta){best=i;bestDelta=d}
      });
      if(best>=0&&bestDelta<=30000)ex.history.splice(best,1);
    });
  }

  function annotateHistoryLinksV148(s){
    const sessions=(s?.sessions||[]).slice(-12);
    sessions.forEach(session=>{
      (session.exerciseResults||[]).forEach(r=>{
        const ex=allExercises(s).find(x=>x.e.uid===r.exerciseUid)?.e;
        if(!ex||!Array.isArray(ex.history))return;
        if(ex.history.some(h=>h?.sourceSessionId===session.id))return;
        const st=Date.parse(session.date||0)||0;
        let best=null,bestDelta=Infinity;
        ex.history.forEach(h=>{
          if(h?.sourceSessionId)return;
          if(!sameSetsV148(h?.sets,r?.sets))return;
          const d=Math.abs((Date.parse(h?.date||0)||0)-st);
          if(d<bestDelta){best=h;bestDelta=d}
        });
        if(best&&bestDelta<=30000)best.sourceSessionId=session.id;
      });
    });
  }

  const baseSaveStateV148=saveState;
  saveState=function(){
    try{annotateHistoryLinksV148(student?.())}catch(e){}
    return baseSaveStateV148.apply(this,arguments);
  };

  function recomputeLastWorkoutV148(s){
    const sessions=s?.sessions||[];
    if(!sessions.length){s.lastWorkout=null;return}
    s.lastWorkout=sessions
      .map(x=>x.date)
      .filter(Boolean)
      .sort((a,b)=>new Date(a)-new Date(b))
      .slice(-1)[0]||null;
  }

  function localPersistQuietV148(){
    try{
      window.__fjzCloudApplying=true;
      localStorage.setItem('fjz_v4_state',JSON.stringify(state));
    }finally{
      window.__fjzCloudApplying=false;
    }
  }

  window.confirmDeleteSessionV148=function(id){
    const s=student(),ss=(s.sessions||[]).find(x=>x.id===id);
    if(!ss)return;
    showModal(
      '<div class="modal-head"><div><h3>Eliminar sesión</h3><div class="muted tiny">'+esc(ss.dayName)+' · '+esc(new Date(ss.date).toLocaleString('es-AR'))+'</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="v148-confirm"><strong>¿Seguro que querés eliminar esta sesión?</strong>'+
      '<div class="muted tiny" style="margin-top:6px">Se quitarán las series registradas, el historial asociado y las recomendaciones generadas desde esta sesión. La rutina programada no se modifica.</div></div>'+
      '<div class="pill-row" style="justify-content:flex-end;margin-top:12px">'+
      '<button class="btn" onclick="closeModal()">Cancelar</button>'+
      '<button id="v148DeleteBtn" class="btn v148-danger" onclick="deleteSessionV148(\''+id+'\')">Eliminar sesión</button>'+
      '</div>'
    );
  };

  window.deleteSessionV148=async function(id){
    const s=student(),idx=(s.sessions||[]).findIndex(x=>x.id===id);
    if(idx<0){closeModal();return}

    const btn=el('v148DeleteBtn');
    if(btn){btn.disabled=true;btn.textContent='Eliminando…'}

    const original=cloneV148(s);
    const updated=cloneV148(s);
    const session=updated.sessions[idx];

    updated.sessions.splice(idx,1);
    removeHistoryForSessionV148(updated,session);
    recomputeLastWorkoutV148(updated);

    const athlete=athleteRowV148(s);
    const athleteId=athlete?.id||linkedAthleteId||null;

    try{
      if(supabaseClient&&currentUser&&athleteId){
        const payload=cloneV148(updated);
        const {data,error}=await supabaseClient
          .from('athlete_snapshots')
          .update({data:payload,updated_at:new Date().toISOString()})
          .eq('athlete_id',athleteId)
          .select('athlete_id')
          .maybeSingle();
        if(error)throw error;
        if(!data)throw new Error('No se pudo confirmar el borrado en la nube.');
      }

      const stateIdx=state.students.findIndex(x=>x.id===s.id);
      if(stateIdx>=0)state.students[stateIdx]=updated;
      localPersistQuietV148();

      // A normal save after the cloud write is now safe: remote and local agree.
      if(window.__fjzCloudReady&&supabaseClient&&currentUser){
        try{baseSaveStateV148.call(window)}catch(e){}
      }

      closeModal();
      render();
      toast('Sesión eliminada');
    }catch(e){
      const stateIdx=state.students.findIndex(x=>x.id===original.id);
      if(stateIdx>=0)state.students[stateIdx]=original;
      localPersistQuietV148();
      if(btn){btn.disabled=false;btn.textContent='Eliminar sesión'}
      toast('No se pudo eliminar: '+cloudErr(e));
    }
  };

  renderHistory=function(isCoach,targetId){
    const s=student(),b=el(targetId||(isCoach?'coachStudentBody':'studentSubBody')),
      ss=(s.sessions||[]).slice().reverse();

    b.innerHTML=ss.length
      ? '<div class="card"><div class="section-title"><h3>Historial de entrenamientos</h3><span class="badge blue">'+ss.length+' sesiones</span></div>'+
        '<div class="history-list">'+ss.map(x=>
          '<div class="history-item"><div><strong>'+esc(x.dayName)+'</strong>'+
          '<div class="muted tiny">'+fmtDate(x.date)+' · '+(x.summary?.totalSets||0)+' series · '+(x.summary?.up||0)+' progresaron · '+(x.summary?.review||0)+' revisar</div></div>'+
          '<div class="v148-history-actions">'+
          '<button class="btn small" onclick="sessionDetails(\''+x.id+'\')">Ver</button>'+
          '<button class="btn small v148-danger" onclick="confirmDeleteSessionV148(\''+x.id+'\')">Eliminar</button>'+
          '</div></div>'
        ).join('')+'</div></div>'
      : '<div class="empty">Todavía no hay sesiones registradas.</div>';
  };

  sessionDetails=function(id){
    const ss=student().sessions.find(x=>x.id===id);
    if(!ss)return;
    showModal(
      '<div class="modal-head"><div><h3>'+esc(ss.dayName)+'</h3><div class="muted tiny">'+new Date(ss.date).toLocaleString('es-AR')+'</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="grid summary-grid">'+
      '<div class="card"><strong class="stat-good" style="font-size:26px">'+(ss.summary?.up||0)+'</strong><div class="muted tiny">Progresaron</div></div>'+
      '<div class="card"><strong class="stat-warn" style="font-size:26px">'+(ss.summary?.hold||0)+'</strong><div class="muted tiny">Estables</div></div>'+
      '<div class="card"><strong class="stat-bad" style="font-size:26px">'+(ss.summary?.review||0)+'</strong><div class="muted tiny">Revisar</div></div>'+
      '</div>'+
      (ss.exerciseResults?.length?ss.exerciseResults.map(r=>
        '<div class="card" style="margin-top:10px"><strong>'+esc(r.name)+'</strong>'+
        '<div class="muted tiny" style="margin-top:4px">'+(r.sets||[]).map((x,i)=>'S'+(i+1)+': '+x[0]+'kg × '+x[1]+' · RIR '+x[2]).join(' · ')+'</div>'+
        (r.recommendation?'<div class="recommend"><strong>'+esc(r.recommendation.title||'Registro guardado')+'</strong><div class="muted tiny">'+esc(r.recommendation.copy||'')+'</div></div>':'')+
        '</div>'
      ).join(''):'<p class="muted tiny">Esta sesión fue importada desde una versión anterior y no contiene detalle por ejercicio.</p>')+
      '<div class="pill-row" style="justify-content:flex-end;margin-top:14px">'+
      '<button class="btn" onclick="closeModal()">Cerrar</button>'+
      '<button class="btn v148-danger" onclick="confirmDeleteSessionV148(\''+ss.id+'\')">Eliminar sesión</button>'+
      '</div>'
    );
  };

  window.__fjzSessionDeleteV148={
    version:VERSION,
    coach:true,
    student:true,
    cloudCascade:true,
    historyCleanup:true,
    confirmation:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzSessionDeleteV148",
  "confirmDeleteSessionV148",
  "deleteSessionV148",
  "cloudCascade:true",
  "historyCleanup:true"
]:
  if marker not in html:
    raise RuntimeError("V14.8 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V14.8 session deletion enabled")
