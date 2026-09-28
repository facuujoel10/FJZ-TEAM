import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v150LoadModeStyles">
.v150-load-box{grid-column:1/-1;border:1px solid rgba(90,167,255,.24);background:rgba(90,167,255,.045);border-radius:12px;padding:11px}
.v150-load-help{margin-top:6px;color:var(--muted);font-size:10px;line-height:1.45}
.v150-load-static{height:42px;display:flex;align-items:center;padding:0 11px;border:1px solid var(--border);border-radius:10px;background:#0d0d0f;color:#fff;font-weight:850}
.v150-load-chip{display:inline-flex;align-items:center;padding:4px 7px;border:1px solid rgba(90,167,255,.28);background:rgba(90,167,255,.06);border-radius:999px;font-size:9px;font-weight:850;color:#a8d0ff;margin-top:5px}
</style>
"""

js=r"""
<script id="v150LoadModeRuntime">
(function(){
  const VERSION='15.0';

  function loadModeV150(e){
    const explicit=String(e?.loadMode||'').toLowerCase();
    if(['external','bodyweight','weighted','assisted'].includes(explicit))return explicit;
    const name=String(e?.name||'').toLowerCase();
    if(/asistid|assisted/.test(name))return 'assisted';
    if(/lastre|weighted/.test(name))return 'weighted';
    if(/dominad|chin[- ]?up|pull[- ]?up|fondos?|dips?|flexi[oó]n|push[- ]?up/.test(name))return 'bodyweight';
    if(/peso corporal|bodyweight/i.test(String(e?.equipment||'')))return 'bodyweight';
    return 'external';
  }

  function loadModeLabelV150(mode){
    return ({
      external:'Carga externa',
      bodyweight:'Peso corporal',
      weighted:'Con lastre',
      assisted:'Con asistencia'
    })[mode]||'Carga externa';
  }

  function loadInputLabelV150(mode){
    return mode==='weighted'?'Lastre (kg)':mode==='assisted'?'Asistencia (kg)':'Kg';
  }

  function targetRepV150(e,i,top=false){
    if(e?.repMode==='exact'&&Array.isArray(e.repsExact)&&e.repsExact.length){
      return Number(e.repsExact[i]??e.repsExact[e.repsExact.length-1])||Number(e.min)||1;
    }
    return Number(top?e?.max:e?.min)||1;
  }

  function safeSetsV150(entry){
    return Array.isArray(entry?.sets)?entry.sets.filter(x=>Array.isArray(x)):[];
  }

  function totalRepsV150(entry){
    return safeSetsV150(entry).reduce((a,x)=>a+(Number(x[1])||0),0);
  }

  function avgRirV150(entry){
    const vals=safeSetsV150(entry).map(x=>Number(x[2])).filter(Number.isFinite);
    return vals.length?vals.reduce((a,x)=>a+x,0)/vals.length:null;
  }

  function avgLoadV150(sets){
    const vals=(sets||[]).map(x=>Number(x[0])).filter(Number.isFinite);
    return vals.length?vals.reduce((a,x)=>a+x,0)/vals.length:0;
  }

  function loadValueV150(e,entry){
    const sets=safeSetsV150(entry);
    if(!sets.length)return 0;
    if(loadModeV150(e)==='assisted')return avgLoadV150(sets);
    return Math.max(...sets.map(x=>Number(x[0])||0));
  }

  function targetSigLoadV150(e){
    let sig=targetSig(e);
    if(e?.repMode==='exact'&&Array.isArray(e.repsExact)&&e.repsExact.length)sig+='|'+e.repsExact.join('-');
    const mode=loadModeV150(e);
    if(mode!=='external')sig+='|load:'+mode;
    return sig;
  }

  function formatSetV150(mode,set,i,short=false){
    const kg=Number(set?.[0])||0,reps=Number(set?.[1])||0,rir=Number(set?.[2]);
    const prefix=short?'':'S'+(i+1)+': ';
    const rirText=Number.isFinite(rir)?' · RIR '+round1(rir):'';
    if(mode==='bodyweight')return prefix+reps+' reps'+rirText;
    if(mode==='weighted')return prefix+'+'+round1(kg)+' kg × '+reps+rirText;
    if(mode==='assisted')return prefix+round1(kg)+' kg asistencia × '+reps+rirText;
    return prefix+round1(kg)+' kg × '+reps+rirText;
  }

  window.fjzLoadModeV150=loadModeV150;

  // ---------- Coach exercise editor ----------
  const baseShowExerciseFormV150=showExerciseForm;
  showExerciseForm=function(dayIndex,exIndex,e){
    baseShowExerciseFormV150.apply(this,arguments);
    const grid=document.querySelector('.modal .form-grid');
    if(!grid||el('fLoadModeV150'))return;
    const mode=loadModeV150(e);
    const box=document.createElement('div');
    box.className='v150-load-box';
    box.innerHTML=
      '<label class="tiny muted">Tipo de carga<select id="fLoadModeV150" class="input" onchange="updateLoadModeUIV150()">'+
      '<option value="external">Carga externa normal</option>'+
      '<option value="bodyweight">Peso corporal</option>'+
      '<option value="weighted">Con lastre</option>'+
      '<option value="assisted">Con asistencia</option>'+
      '</select></label>'+
      '<div id="fLoadHelpV150" class="v150-load-help"></div>';
    const cue=el('fCue')?.closest('label');
    cue?grid.insertBefore(box,cue):grid.appendChild(box);
    el('fLoadModeV150').value=mode;
    updateLoadModeUIV150();
  };

  window.updateLoadModeUIV150=function(){
    const mode=el('fLoadModeV150')?.value||'external';
    const help=el('fLoadHelpV150');
    const inc=el('fInc');
    const incLabel=inc?.closest('label');
    if(help){
      help.textContent=
        mode==='bodyweight'
          ? 'El alumno carga solo repeticiones y RIR. La app registra internamente peso corporal sin pedir kilos.'
          : mode==='weighted'
          ? 'El alumno escribe únicamente los kilos agregados como lastre.'
          : mode==='assisted'
          ? 'El alumno escribe los kilos de ayuda. Menos asistencia se interpreta como progreso.'
          : 'Usá este modo para máquinas, barras, mancuernas, poleas y otras cargas externas.';
    }
    if(incLabel){
      const input=inc.outerHTML;
      incLabel.innerHTML=
        (mode==='assisted'?'Paso de asistencia (kg)':mode==='weighted'?'Incremento de lastre (kg)':'Incremento kg')+input;
    }
  };

  const baseSaveExerciseV150=saveExercise;
  saveExercise=function(di,ei){
    const mode=el('fLoadModeV150')?.value||null;
    const out=baseSaveExerciseV150.apply(this,arguments);
    const arr=student()?.days?.[di]?.exercises||[];
    const idx=ei==null?arr.length-1:Number(ei);
    const ex=arr[idx];
    if(ex){
      ex.loadMode=mode||loadModeV150(ex);
      saveState();
      render();
    }
    return out;
  };

  // ---------- Workout input ----------
  const baseSetWorkoutV150=setWorkout;
  setWorkout=function(uidv,si,field,val){
    const ex=allExercises().find(x=>x.e.uid===uidv)?.e;
    if(ex&&loadModeV150(ex)==='bodyweight'){
      const draft=ensureDraft(ex);
      if(draft?.[si])draft[si][0]=0;
      if(Number(field)===0)return;
    }
    return baseSetWorkoutV150.apply(this,arguments);
  };

  const baseWorkoutExerciseV150=workoutExercise;
  workoutExercise=function(e,i){
    const mode=loadModeV150(e);
    if(mode==='bodyweight'&&workoutDraft[e.uid]){
      workoutDraft[e.uid].forEach(x=>{if(Array.isArray(x))x[0]=0});
    }
    let out=baseWorkoutExerciseV150.apply(this,arguments);
    const temp=document.createElement('div');
    temp.innerHTML=out;
    const card=temp.firstElementChild;
    if(!card)return out;

    const rows=[...card.querySelectorAll('.set-grid')];
    rows.forEach(row=>{
      const labels=row.querySelectorAll('label');
      const loadLabel=labels[0];
      if(!loadLabel)return;
      if(mode==='bodyweight'){
        loadLabel.innerHTML='Carga<div class="v150-load-static">Peso corporal</div>';
      }else{
        const input=loadLabel.querySelector('input');
        if(input)loadLabel.innerHTML=loadInputLabelV150(mode)+input.outerHTML;
      }
    });

    const head=card.querySelector('.day-head > div');
    if(head&&!head.querySelector('.v150-load-chip')){
      head.insertAdjacentHTML('beforeend','<div class="v150-load-chip">'+esc(loadModeLabelV150(mode))+'</div>');
    }

    const prev=latestHistory(e);
    const note=card.querySelector('.coach-note');
    if(note&&prev?.sets?.length){
      note.innerHTML='<strong>Última sesión:</strong> '+safeSetsV150(prev).map((x,j)=>formatSetV150(mode,x,j,true)).join(' · ');
    }else if(note&&mode==='bodyweight'){
      note.innerHTML='<strong>Primera sesión:</strong> registrá repeticiones y RIR; no hace falta cargar kilos.';
    }

    return card.outerHTML;
  };

  // ---------- Recommendation logic ----------
  const baseAutoRecommendationV150=autoRecommendation;
  autoRecommendation=function(e,sets){
    const mode=loadModeV150(e);
    if(mode==='external')return baseAutoRecommendationV150.apply(this,arguments);

    sets=Array.isArray(sets)?sets:[];
    const valid=sets.length===Number(e.sets)&&sets.every(x=>{
      const reps=Number(x?.[1]),rir=Number(x?.[2]),kg=Number(x?.[0]);
      const loadOk=mode==='bodyweight'?true:Number.isFinite(kg)&&kg>0;
      return loadOk&&Number.isFinite(reps)&&reps>0&&Number.isFinite(rir)&&rir>=0;
    });
    if(!valid)return{type:'none',title:'Completá todas las series',copy:mode==='bodyweight'?'Necesito repeticiones y RIR válidos para analizar la sesión.':'Necesito carga, repeticiones y RIR válidos para analizar la sesión.'};

    const last=latestHistory(e);
    const sig=targetSigLoadV150(e);
    if(last&&last.target&&last.target!==sig){
      return{type:'reset',title:'Nueva referencia',copy:'Cambió el tipo de carga u objetivo. Esta sesión va a crear una nueva base de comparación.'};
    }
    if(!last)return{type:'first',title:'Primera referencia',copy:'Guardá esta sesión. La próxima vez podremos comparar el progreso.'};

    const exact=e?.repMode==='exact'&&Array.isArray(e.repsExact)&&e.repsExact.length;
    const hit=sets.every((x,idx)=>Number(x[1])>=targetRepV150(e,idx,true)&&Number(x[2])>=Number(e.rirMin)&&Number(x[2])<=Number(e.rirMax));
    const tooHard=sets.filter((x,idx)=>Number(x[1])<targetRepV150(e,idx,false)||Number(x[2])<Number(e.rirMin)).length>=Math.ceil(Number(e.sets)/2);
    const reps=sets.reduce((a,x)=>a+(Number(x[1])||0),0);
    const prev=last.sets||[];
    const prevReps=prev.reduce((a,x)=>a+(Number(x?.[1])||0),0);

    if(mode==='bodyweight'){
      if(hit&&reps>prevReps)return{type:'rep',title:'Mejoraste las repeticiones',copy:'Progresaste manteniendo el ejercicio con peso corporal y dentro del RIR objetivo.'};
      if(hit)return{type:'hold',title:'Objetivo cumplido',copy:'Mantené la calidad de ejecución. El paso a lastre solo se hace si tu coach lo programa.'};
      if(tooHard)return{type:'down',title:'Mantené el peso corporal',copy:'No agregues dificultad. Buscá recuperar repeticiones y RIR con buena técnica.'};
      if(reps>prevReps)return{type:'rep',title:'Sumaste repeticiones',copy:'Seguí progresando en reps sin cambiar el tipo de carga programado.'};
      return{type:'hold',title:'Mantené el objetivo',copy:'Buscá mejorar repeticiones, técnica o RIR antes de cambiar la dificultad.'};
    }

    const load=avgLoadV150(sets),prevLoad=avgLoadV150(prev);
    const sameLoad=sets.every(x=>Math.abs((Number(x[0])||0)-(Number(sets[0][0])||0))<.001);

    if(mode==='weighted'){
      if(hit&&sameLoad){
        const next=round1((Number(sets[0][0])||0)+(Number(e.increment)||2.5));
        return{type:'up',title:'Próxima sesión: probá +'+next+' kg de lastre',copy:'Completaste el objetivo dentro del RIR indicado.'};
      }
      if(tooHard)return{type:'down',title:'Mantené o reducí el lastre',copy:'Varias series quedaron por debajo del objetivo o demasiado cerca del fallo.'};
      if(reps>prevReps)return{type:'rep',title:'Mejoraste las repeticiones',copy:'Mantené el lastre hasta consolidar el objetivo programado.'};
      return{type:'hold',title:'Mantené el lastre',copy:'Priorizá completar el rango y el RIR antes de sumar kilos.'};
    }

    if(mode==='assisted'){
      if(load<prevLoad&&reps>=prevReps&&!tooHard){
        return{type:'load',title:'Usaste menos asistencia',copy:'Eso representa progreso: hiciste el ejercicio con menos ayuda manteniendo el rendimiento.'};
      }
      if(hit&&sameLoad){
        const next=Math.max(0,round1((Number(sets[0][0])||0)-(Number(e.increment)||2.5)));
        if(next>0)return{type:'up',title:'Próxima sesión: probá '+next+' kg de asistencia',copy:'Menos asistencia aumenta la dificultad. Mantené técnica y RIR.'};
        return{type:'hold',title:'Asistencia mínima alcanzada',copy:'Tu coach puede decidir cuándo pasar a peso corporal sin asistencia.'};
      }
      if(tooHard)return{type:'down',title:'Mantené o aumentá un poco la asistencia',copy:'Priorizá completar repeticiones y RIR antes de volver a reducir la ayuda.'};
      if(reps>prevReps)return{type:'rep',title:'Mejoraste las repeticiones',copy:'Mantené la asistencia y consolidá el objetivo antes de reducirla.'};
      return{type:'hold',title:'Mantené la asistencia',copy:'Buscá mejorar repeticiones, técnica o RIR antes de reducir la ayuda.'};
    }

    return baseAutoRecommendationV150.apply(this,arguments);
  };

  // ---------- Progress ----------
  function progressChartV150(e,metric){
    const mode=loadModeV150(e);
    if(mode==='bodyweight')metric='reps';
    const hist=e?.history||[];
    const vals=hist.map(x=>{
      if(metric==='reps')return totalRepsV150(x);
      return loadValueV150(e,x);
    });
    if(!vals.length)return '<div class="empty">Todavía no hay datos suficientes para graficar.</div>';
    const w=700,hg=220,pad=30,min=Math.min(...vals),max=Math.max(...vals),span=Math.max(1,max-min);
    const pts=vals.map((v,i)=>({x:pad+(vals.length===1?(w-2*pad)/2:i*(w-2*pad)/(vals.length-1)),y:hg-pad-(v-min)/span*(hg-2*pad),v}));
    const metricLabel=metric==='reps'?'repeticiones totales':mode==='assisted'?'asistencia promedio (kg)':mode==='weighted'?'lastre (kg)':'carga máxima (kg)';
    return '<div class="chart-wrap"><svg viewBox="0 0 '+w+' '+hg+'" preserveAspectRatio="none">'+
      '<line x1="'+pad+'" y1="'+(hg-pad)+'" x2="'+(w-pad)+'" y2="'+(hg-pad)+'" class="chart-axis"/>'+
      '<line x1="'+pad+'" y1="'+pad+'" x2="'+pad+'" y2="'+(hg-pad)+'" class="chart-axis"/>'+
      '<polyline class="chart-line" points="'+pts.map(q=>q.x+','+q.y).join(' ')+'"/>'+
      pts.map((q,i)=>'<circle class="chart-point" cx="'+q.x+'" cy="'+q.y+'" r="4"/><text class="chart-text" x="'+q.x+'" y="'+Math.max(12,q.y-9)+'" text-anchor="middle">'+(Math.round(q.v*10)/10)+'</text><text class="chart-text" x="'+q.x+'" y="'+(hg-7)+'" text-anchor="middle">'+(i+1)+'</text>').join('')+
      '</svg><div class="muted micro">Eje X: sesiones registradas · Métrica: '+metricLabel+'</div></div>';
  }

  renderProgress=function(isCoach,targetId){
    const s=student(),target=targetId||(isCoach?'coachStudentBody':'studentSubBody'),b=el(target);
    if(!b)return;
    const items=allExercises(s).filter(x=>x.e.history?.length);
    if(!items.length){b.innerHTML='<div class="empty">Todavía no hay historial suficiente para mostrar progreso.</div>';return}
    if(!selectedProgressExercise||!items.some(x=>x.e.uid===selectedProgressExercise))selectedProgressExercise=items[0].e.uid;
    const ex=items.find(x=>x.e.uid===selectedProgressExercise).e,h=ex.history||[],latest=h[h.length-1],first=h[0],mode=loadModeV150(ex);
    if(progressMetric==='volume')progressMetric='reps';
    if(mode==='bodyweight')progressMetric='reps';
    if(!['load','reps'].includes(progressMetric))progressMetric='load';

    const latestLoad=loadValueV150(ex,latest),firstLoad=loadValueV150(ex,first);
    const latestReps=totalRepsV150(latest),avgRir=avgRirV150(latest);
    let loadButton='';
    if(mode!=='bodyweight'){
      const lbl=mode==='weighted'?'Lastre':mode==='assisted'?'Asistencia':'Carga';
      loadButton='<button class="'+(progressMetric==='load'?'active':'')+'" onclick="progressMetric=\'load\';render()">'+lbl+'</button>';
    }
    const metric1=mode==='bodyweight'
      ? '<div class="metric"><strong>Peso corporal</strong><span class="muted tiny">Tipo de carga</span></div>'
      : '<div class="metric"><strong>'+round1(latestLoad)+' kg</strong><span class="muted tiny">'+(mode==='weighted'?'Lastre actual':mode==='assisted'?'Asistencia promedio':'Carga máxima')+'</span></div>';
    const metric4=mode==='bodyweight'
      ? '<div class="metric"><strong>'+h.length+'</strong><span class="muted tiny">Sesiones del ejercicio</span></div>'
      : '<div class="metric"><strong>'+((latestLoad-firstLoad)>0?'+':'')+round1(latestLoad-firstLoad)+' kg</strong><span class="muted tiny">'+(mode==='assisted'?'Cambio de asistencia':mode==='weighted'?'Cambio de lastre':'Cambio desde inicio')+'</span></div>';

    b.innerHTML=
      '<div class="grid two"><div class="card"><div class="section-title"><h3>Progreso por ejercicio</h3><select id="progressExercise" class="input" style="max-width:310px">'+
      items.map(x=>'<option value="'+x.e.uid+'" '+(x.e.uid===ex.uid?'selected':'')+'>'+esc(x.e.name)+'</option>').join('')+
      '</select></div><div class="segmented" style="width:max-content;margin-bottom:12px">'+loadButton+
      '<button class="'+(progressMetric==='reps'?'active':'')+'" onclick="progressMetric=\'reps\';render()">Reps</button></div>'+
      progressChartV150(ex,progressMetric)+
      '<div class="metric-grid" style="margin-top:12px">'+metric1+
      '<div class="metric"><strong>'+latestReps+'</strong><span class="muted tiny">Reps última sesión</span></div>'+
      '<div class="metric"><strong>'+(avgRir==null?'—':round1(avgRir))+'</strong><span class="muted tiny">RIR promedio</span></div>'+
      metric4+'</div></div>'+
      '<aside class="card"><h3 style="margin-top:0">Recomendación actual</h3>'+recommendationHtml(ex,autoRecommendation(ex,safeSetsV150(latest)))+
      (isCoach?'<button class="btn primary" style="width:100%;margin-top:12px" onclick="setCoachOverride(\''+ex.uid+'\')">'+(ex.override?.active?'Editar indicación':'Sobrescribir recomendación')+'</button>'+(ex.override?.active?'<button class="btn" style="width:100%;margin-top:8px" onclick="clearCoachOverride(\''+ex.uid+'\')">Quitar indicación manual</button>':''):'')+
      '<hr style="border:0;border-top:1px solid var(--border);margin:16px 0"><h4>Últimas sesiones</h4>'+
      h.slice(-4).reverse().map(x=>'<div class="history-item"><div><strong>'+fmtDate(x.date)+'</strong><div class="muted tiny">'+safeSetsV150(x).map((s,j)=>formatSetV150(mode,s,j,true)).join(' · ')+'</div></div><span class="badge amber">RIR '+(avgRirV150(x)==null?'—':round1(avgRirV150(x)))+'</span></div>').join('')+
      '</aside></div>';
    const picker=el('progressExercise');
    if(picker)picker.onchange=e=>{selectedProgressExercise=e.target.value;render()};
  };

  // ---------- Session detail formatting ----------
  sessionDetails=function(id){
    const ss=student().sessions.find(x=>x.id===id);
    if(!ss)return;
    const cards=(ss.exerciseResults||[]).map(r=>{
      const ex=allExercises(student()).find(x=>x.e.uid===r.exerciseUid)?.e;
      const mode=r.loadMode||loadModeV150(ex||{name:r.name});
      return '<div class="card" style="margin-top:10px"><strong>'+esc(r.name)+'</strong>'+
        '<div class="muted tiny" style="margin-top:4px">'+(r.sets||[]).map((x,i)=>formatSetV150(mode,x,i,false)).join(' · ')+'</div>'+
        (r.recommendation?'<div class="recommend"><strong>'+esc(r.recommendation.title||'Registro guardado')+'</strong><div class="muted tiny">'+esc(r.recommendation.copy||'')+'</div></div>':'')+
        '</div>';
    }).join('');

    showModal(
      '<div class="modal-head"><div><h3>'+esc(ss.dayName)+'</h3><div class="muted tiny">'+new Date(ss.date).toLocaleString('es-AR')+'</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="grid summary-grid">'+
      '<div class="card"><strong class="stat-good" style="font-size:26px">'+(ss.summary?.up||0)+'</strong><div class="muted tiny">Progresaron</div></div>'+
      '<div class="card"><strong class="stat-warn" style="font-size:26px">'+(ss.summary?.hold||0)+'</strong><div class="muted tiny">Estables</div></div>'+
      '<div class="card"><strong class="stat-bad" style="font-size:26px">'+(ss.summary?.review||0)+'</strong><div class="muted tiny">Revisar</div></div>'+
      '</div>'+
      (cards||'<p class="muted tiny">Esta sesión fue importada desde una versión anterior y no contiene detalle por ejercicio.</p>')+
      '<div class="pill-row" style="justify-content:flex-end;margin-top:14px">'+
      '<button class="btn" onclick="closeModal()">Cerrar</button>'+
      (typeof confirmDeleteSessionV148==='function'?'<button class="btn v148-danger" onclick="confirmDeleteSessionV148(\''+ss.id+'\')">Eliminar sesión</button>':'')+
      '</div>'
    );
  };

  window.__fjzLoadModesV150={
    version:VERSION,
    bodyweight:true,
    weighted:true,
    assisted:true,
    autoBodyweightInference:true,
    progressAware:true,
    historyAware:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzLoadModesV150",
  "bodyweight:true",
  "weighted:true",
  "assisted:true",
  "autoBodyweightInference:true",
  "progressAware:true",
  "historyAware:true"
]:
    if marker not in html:
        raise RuntimeError("V15.0 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V15.0 bodyweight/load modes enabled")
