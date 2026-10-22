import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

before=metrics(html)

for marker in [
    'meta name="fjz-coach-cockpit-music-removal" content="20.68"',
    "__fjzWarmupMobilityV251",
    "__fjzStretchLibraryV144",
    "openLibrary=function(dayIndex)",
    "showExerciseForm=function",
    "function dayEditor(d,i)",
    "function renderWorkout()"
]:
    if marker not in html:
        raise RuntimeError("V20.69 missing prerequisite: "+marker)

runtime=r"""
<script id="v269RoutineModalPreparationRuntime">
(function(){
  const PREP_WARM='Calentamiento / Activación';
  const PREP_STRETCH='Estiramientos / Movilidad';

  /* ---------------------------------------------------------
     Separate preparation / mobility from the main exercise library.
     V14.4 + V20.51 historically appended these records to exerciseLibrary.
     We capture them, then retire them from the strength-exercise surface.
     --------------------------------------------------------- */
  const prepCapturedV269=exerciseLibrary.filter(x=>x&&(x.muscle===PREP_WARM||x.muscle===PREP_STRETCH));
  const warmupLibraryV269=prepCapturedV269.filter(x=>x.muscle===PREP_WARM).map(x=>({...x}));
  const stretchLibraryV269=prepCapturedV269.filter(x=>x.muscle===PREP_STRETCH).map(x=>({...x}));

  for(let i=exerciseLibrary.length-1;i>=0;i--){
    const x=exerciseLibrary[i];
    if(x&&(x.muscle===PREP_WARM||x.muscle===PREP_STRETCH))exerciseLibrary.splice(i,1);
  }

  window.__fjzWarmupLibraryV269=warmupLibraryV269;
  window.__fjzStretchLibraryV269=stretchLibraryV269;

  function normalizeV269(s){
    return String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
  }

  function mainExerciseLibraryV269(){
    return exerciseLibrary.filter(x=>x&&x.muscle!==PREP_WARM&&x.muscle!==PREP_STRETCH);
  }

  function selectedPrepV269(day,phase){
    const key=phase==='cooldown'?'cooldownItems':'warmupItems';
    if(!Array.isArray(day[key]))day[key]=[];
    return day[key];
  }

  function prepSourceV269(phase){
    return phase==='cooldown'?stretchLibraryV269:warmupLibraryV269;
  }

  function prepLabelV269(phase){
    return phase==='cooldown'
      ?{title:'Al finalizar',sub:'Movilidad y estiramientos del final de la sesión',action:'Estiramientos'}
      :{title:'Antes de entrenar',sub:'Calentamiento, activación y preparación del movimiento',action:'Calentamiento'};
  }

  function prepEditorHtmlV269(day,dayIndex){
    const warm=Array.isArray(day?.warmupItems)?day.warmupItems:[];
    const cool=Array.isArray(day?.cooldownItems)?day.cooldownItems:[];
    const list=(arr,phase)=>arr.length
      ?'<div class="v269-prep-list">'+arr.map((x,idx)=>
          '<div class="v269-prep-chip"><span>'+esc(x.name||'Opción')+'</span>'+
          '<button type="button" aria-label="Quitar '+esc(x.name||'opción')+'" onclick="removePrepItemV269('+dayIndex+',\''+phase+'\','+idx+')">×</button></div>'
        ).join('')+'</div>'
      :'<div class="v269-prep-empty">Sin opciones cargadas.</div>';

    return '<section class="v269-prep-editor" data-v269-day-prep="'+dayIndex+'">'+
      '<div class="v269-prep-col">'+
        '<div class="v269-prep-head"><div><span>ANTES DE ENTRENAR</span><strong>Calentamiento</strong></div>'+
        '<button class="btn small" onclick="openPrepLibraryV269('+dayIndex+',\'warmup\')">+ Agregar</button></div>'+
        list(warm,'warmup')+
      '</div>'+
      '<div class="v269-prep-col">'+
        '<div class="v269-prep-head"><div><span>AL FINALIZAR</span><strong>Estiramientos</strong></div>'+
        '<button class="btn small" onclick="openPrepLibraryV269('+dayIndex+',\'cooldown\')">+ Agregar</button></div>'+
        list(cool,'cooldown')+
      '</div>'+
    '</section>';
  }

  function prepWorkoutCardV269(items,phase){
    if(!Array.isArray(items)||!items.length)return '';
    const meta=prepLabelV269(phase);
    return '<section class="card v269-workout-prep '+phase+'">'+
      '<div class="v269-workout-prep-head"><div><span>'+esc(meta.title.toUpperCase())+'</span><strong>'+esc(meta.action)+'</strong></div>'+
      '<span class="badge blue">'+items.length+'</span></div>'+
      '<p class="muted tiny">'+esc(meta.sub)+'.</p>'+
      '<div class="v269-workout-prep-list">'+items.map((x,i)=>
        '<div class="v269-workout-prep-item"><span>'+(i+1)+'</span><div><strong>'+esc(x.name||'Opción')+'</strong>'+
        '<small>'+esc(x.cue||x.equipment||'')+'</small></div></div>'
      ).join('')+'</div>'+
    '</section>';
  }

  /* ---------------------------------------------------------
     Canonical Exercise Library — strength exercises only.
     --------------------------------------------------------- */
  window.openLibrary=function(dayIndex){
    const all=mainExerciseLibraryV269();
    const muscles=[...new Set(all.map(x=>x.muscle).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'es'));
    const equipment=[...new Set(all.map(x=>x.equipment).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'es'));

    showModal(
      '<div class="v269-library-shell">'+
        '<div class="modal-head v269-modal-head v269-library-head">'+
          '<div class="v269-title-block"><span class="v269-eyebrow">RUTINA</span><h3>Biblioteca de ejercicios</h3>'+
          '<small id="v269LibraryCount">'+all.length+' ejercicios de fuerza</small></div>'+
          '<button class="btn small v269-close" aria-label="Cerrar biblioteca" onclick="closeModal()">✕</button>'+
        '</div>'+
        '<div class="v269-search-row">'+
          '<input id="libSearch" class="input" placeholder="Buscar ejercicio, músculo o equipo..." autocomplete="off">'+
          '<button class="btn v269-custom-btn" onclick="customExercise('+dayIndex+')">+ Personalizado</button>'+
        '</div>'+
        '<div class="filters v269-library-filters">'+
          '<select id="muscleFilter" class="input"><option value="">Todos los músculos</option>'+
            muscles.map(x=>'<option>'+esc(x)+'</option>').join('')+
          '</select>'+
          '<select id="equipFilter" class="input"><option value="">Todo el equipamiento</option>'+
            equipment.map(x=>'<option>'+esc(x)+'</option>').join('')+
          '</select>'+
        '</div>'+
        '<div class="library v269-library-grid" id="libraryGrid"></div>'+
      '</div>'
    );

    const refresh=()=>{
      const q=normalizeV269(el('libSearch')?.value);
      const m=el('muscleFilter')?.value||'';
      const e=el('equipFilter')?.value||'';
      const arr=all.filter(x=>{
        const hay=normalizeV269((x.name||'')+' '+(x.muscle||'')+' '+(x.equipment||''));
        return (!q||hay.includes(q))&&(!m||x.muscle===m)&&(!e||x.equipment===e);
      });
      const host=el('libraryGrid');if(!host)return;
      host.innerHTML=arr.length?arr.map(x=>
        '<div class="library-item v269-library-item">'+
          '<div class="v269-library-copy"><h4>'+esc(x.name)+'</h4><p>'+esc(x.muscle||'')+' · '+esc(x.equipment||'')+'</p></div>'+
          '<button class="btn primary small" onclick="configureExercise('+dayIndex+',\''+esc(x.id)+'\')">Agregar</button>'+
        '</div>'
      ).join(''):'<div class="empty">No encontré ejercicios con esos filtros.</div>';
      const count=el('v269LibraryCount');if(count)count.textContent=arr.length+' de '+all.length+' ejercicios';
    };
    window.__v65LibraryRefresh=refresh;
    ['libSearch','muscleFilter','equipFilter'].forEach(id=>{const node=el(id);if(node)node.oninput=refresh});
    refresh();
  };
  try{openLibrary=window.openLibrary}catch(_e){}

  /* ---------------------------------------------------------
     Exercise editor header: stable Back / Title / Close geometry.
     --------------------------------------------------------- */
  const baseShowExerciseV269=window.showExerciseForm||showExerciseForm;
  window.showExerciseForm=function(dayIndex,exIndex,e){
    const out=baseShowExerciseV269.apply(this,arguments);
    const modal=el('modal');
    const head=modal?.querySelector('.modal-head');
    if(head){
      const isNew=exIndex==null;
      head.className='modal-head v269-modal-head v269-exercise-form-head';
      head.innerHTML=
        '<div class="v269-form-head-left">'+
          (isNew?'<button type="button" class="btn ghost small v269-back-btn" onclick="openLibrary('+dayIndex+')">← Biblioteca</button>':'')+
          '<div class="v269-title-block"><span class="v269-eyebrow">RUTINA</span><h3>'+(isNew?'Agregar ejercicio':'Editar ejercicio')+'</h3></div>'+
        '</div>'+
        '<button class="btn small v269-close" aria-label="Cerrar" onclick="closeModal()">✕</button>';
    }
    modal?.classList.add('v269-exercise-modal');
    return out;
  };
  try{showExerciseForm=window.showExerciseForm}catch(_e){}

  /* ---------------------------------------------------------
     Dedicated Warm-up / Stretching libraries.
     --------------------------------------------------------- */
  window.openPrepLibraryV269=function(dayIndex,phase){
    const d=student()?.days?.[dayIndex];if(!d)return;
    const source=prepSourceV269(phase),selected=selectedPrepV269(d,phase),meta=prepLabelV269(phase);
    const chosen=new Set(selected.map(x=>x.id));
    showModal(
      '<div class="v269-library-shell v269-prep-modal">'+
        '<div class="modal-head v269-modal-head">'+
          '<div class="v269-title-block"><span class="v269-eyebrow">'+esc(meta.title.toUpperCase())+'</span><h3>'+esc(meta.action)+'</h3>'+
          '<small>'+esc(meta.sub)+'</small></div>'+
          '<button class="btn small v269-close" onclick="closeModal()">✕</button>'+
        '</div>'+
        '<div class="v269-search-row one"><input id="v269PrepSearch" class="input" placeholder="Buscar opción..." autocomplete="off"></div>'+
        '<div id="v269PrepGrid" class="library v269-library-grid"></div>'+
      '</div>'
    );
    const refresh=()=>{
      const q=normalizeV269(el('v269PrepSearch')?.value);
      const rows=source.filter(x=>!q||normalizeV269((x.name||'')+' '+(x.equipment||'')+' '+(x.cue||'')).includes(q));
      const host=el('v269PrepGrid');if(!host)return;
      host.innerHTML=rows.map(x=>{
        const on=chosen.has(x.id);
        return '<div class="library-item v269-library-item '+(on?'selected':'')+'">'+
          '<div class="v269-library-copy"><h4>'+esc(x.name)+'</h4><p>'+esc(x.equipment||'')+'</p><small>'+esc(x.cue||'')+'</small></div>'+
          '<button class="btn '+(on?'ghost':'primary')+' small" onclick="togglePrepItemV269('+dayIndex+',\''+phase+'\',\''+esc(x.id)+'\')">'+(on?'Quitar':'Agregar')+'</button>'+
        '</div>';
      }).join('')||'<div class="empty">No encontré opciones.</div>';
    };
    window.__fjzPrepRefreshV269=refresh;
    el('v269PrepSearch').oninput=refresh;
    refresh();
  };

  window.togglePrepItemV269=function(dayIndex,phase,id){
    const d=student()?.days?.[dayIndex];if(!d)return;
    const arr=selectedPrepV269(d,phase),source=prepSourceV269(phase),idx=arr.findIndex(x=>x.id===id);
    if(idx>=0)arr.splice(idx,1);
    else{
      const src=source.find(x=>x.id===id);if(!src)return;
      arr.push({id:src.id,name:src.name,equipment:src.equipment||'',cue:src.cue||''});
    }
    saveState();
    window.__fjzQuickSavedV264?.(phase==='cooldown'?'Estiramientos guardados':'Calentamiento guardado');
    openPrepLibraryV269(dayIndex,phase);
  };

  window.removePrepItemV269=function(dayIndex,phase,index){
    const d=student()?.days?.[dayIndex];if(!d)return;
    const arr=selectedPrepV269(d,phase);
    if(index<0||index>=arr.length)return;
    arr.splice(index,1);
    saveState();
    render();
    window.__fjzQuickSavedV264?.(phase==='cooldown'?'Estiramientos guardados':'Calentamiento guardado');
  };

  /* Day editor: preparation is a separate surface, never an exercise row. */
  const baseDayEditorV269=dayEditor;
  dayEditor=function(d,i){
    let out=baseDayEditorV269.apply(this,arguments);
    if(!out||out.includes('data-v269-day-prep='))return out;
    const pos=out.lastIndexOf('</div>');
    if(pos<0)return out;
    return out.slice(0,pos)+prepEditorHtmlV269(d,i)+out.slice(pos);
  };
  try{window.dayEditor=dayEditor}catch(_e){}

  /* Student workout: show preparation before exercise cards and stretching after. */
  function enhanceWorkoutPrepV269(){
    if(!(mode==='student'&&studentTab==='workout'))return;
    const d=student()?.days?.[currentDay],v=el('view');if(!d||!v)return;
    v.querySelectorAll('.v269-workout-prep').forEach(x=>x.remove());

    const warm=prepWorkoutCardV269(d.warmupItems||[],'warmup');
    const cool=prepWorkoutCardV269(d.cooldownItems||[],'cooldown');

    if(warm){
      const progress=v.querySelector('.session-progress');
      if(progress)progress.insertAdjacentHTML('afterend',warm);
      else v.querySelector('.hero')?.insertAdjacentHTML('afterend',warm);
    }
    if(cool)v.insertAdjacentHTML('beforeend',cool);
  }

  const baseRenderWorkoutV269=window.renderWorkout||renderWorkout;
  window.renderWorkout=function(){
    const out=baseRenderWorkoutV269.apply(this,arguments);
    enhanceWorkoutPrepV269();
    return out;
  };
  try{renderWorkout=window.renderWorkout}catch(_e){}

  window.__fjzV269={
    version:'20.69',
    mainLibraryStrengthOnly:true,
    preparationLibrarySeparated:true,
    warmupBeforeWorkout:true,
    stretchingAfterWorkout:true,
    stableExerciseModalHeader:true,
    mobileLibraryGeometry:true,
    prepPersistsInAthleteSnapshot:true
  };
})();
</script>
"""

css=r"""
/* =========================================================
   TEAM FJZ · V20.69 ROUTINE LIBRARY / PREPARATION UI
   ========================================================= */
.modal{
  max-width:min(920px,calc(100vw - 28px))!important;
  max-height:min(88vh,900px)!important;
  overflow:auto!important;
  overscroll-behavior:contain;
}
.modal>*{min-width:0}
.v269-library-shell,
.v269-library-shell>*,
.v269-exercise-modal>*{
  min-width:0;
  max-width:100%;
}
.v269-modal-head{
  display:grid!important;
  grid-template-columns:minmax(0,1fr) auto!important;
  align-items:start!important;
  gap:10px!important;
  margin:0 0 12px!important;
  padding:0 0 11px!important;
  border-bottom:1px solid #292d34;
}
.v269-title-block{
  min-width:0;
  overflow:hidden;
}
.v269-title-block h3{
  margin:3px 0 0!important;
  max-width:100%;
  color:#f5f6f8;
  font-size:18px!important;
  line-height:1.18!important;
  overflow-wrap:anywhere;
}
.v269-title-block small{
  display:block;
  margin-top:5px;
  color:#8e949e;
  font-size:8px;
  line-height:1.35;
  overflow-wrap:anywhere;
}
.v269-eyebrow{
  display:block;
  color:#ff6877;
  font-size:7px;
  font-weight:950;
  letter-spacing:.14em;
  text-transform:uppercase;
}
.v269-close{
  width:36px!important;
  min-width:36px!important;
  height:36px!important;
  min-height:36px!important;
  padding:0!important;
  display:grid!important;
  place-items:center!important;
}
.v269-search-row{
  display:grid;
  grid-template-columns:minmax(0,1fr) auto;
  gap:8px;
  align-items:stretch;
  margin-bottom:9px;
}
.v269-search-row.one{grid-template-columns:1fr}
.v269-search-row .input,
.v269-library-filters .input{
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
}
.v269-custom-btn{
  min-width:126px;
  white-space:nowrap;
}
.v269-library-filters{
  display:grid!important;
  grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;
  gap:8px!important;
  min-width:0;
  margin-bottom:10px;
}
.v269-library-grid{
  display:grid!important;
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:8px!important;
  min-width:0!important;
}
.v269-library-item{
  min-width:0!important;
  width:100%!important;
  max-width:100%!important;
  display:grid!important;
  grid-template-columns:minmax(0,1fr) auto!important;
  gap:10px!important;
  align-items:center!important;
  padding:11px 12px!important;
}
.v269-library-copy{min-width:0}
.v269-library-copy h4,
.v269-library-copy p,
.v269-library-copy small{
  max-width:100%;
  overflow-wrap:anywhere;
}
.v269-library-copy h4{margin:0 0 4px!important}
.v269-library-copy p{margin:0!important}
.v269-library-copy small{
  display:block;
  margin-top:5px;
  color:#858b95;
  font-size:7.5px;
  line-height:1.4;
}
.v269-library-item>.btn{
  flex:0 0 auto;
  min-width:76px;
}
.v269-library-item.selected{
  border-color:rgba(255,70,87,.32)!important;
  background:rgba(255,38,57,.04)!important;
}

/* Add/Edit exercise modal header */
.v269-exercise-form-head{
  position:sticky;
  top:-1px;
  z-index:3;
  background:#111217;
  padding-top:2px!important;
}
.v269-form-head-left{
  min-width:0;
  display:flex;
  align-items:flex-start;
  gap:9px;
  flex-wrap:wrap;
}
.v269-back-btn{
  flex:0 0 auto;
  white-space:nowrap;
  min-height:34px!important;
}
.v269-form-head-left .v269-title-block{
  flex:1 1 180px;
}

/* Dedicated routine preparation surface */
.v269-prep-editor{
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:8px;
  margin-top:12px;
  padding-top:12px;
  border-top:1px solid #292d34;
}
.v269-prep-col{
  min-width:0;
  padding:10px;
  border:1px solid #292d34;
  border-radius:12px;
  background:#0d0e12;
}
.v269-prep-head{
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  gap:8px;
}
.v269-prep-head>div{min-width:0}
.v269-prep-head span{
  display:block;
  color:#7f8590;
  font-size:6.5px;
  font-weight:900;
  letter-spacing:.1em;
}
.v269-prep-head strong{
  display:block;
  margin-top:3px;
  color:#f2f4f6;
  font-size:10px;
  overflow-wrap:anywhere;
}
.v269-prep-list{
  display:flex;
  flex-wrap:wrap;
  gap:5px;
  margin-top:9px;
}
.v269-prep-chip{
  max-width:100%;
  display:inline-flex;
  align-items:center;
  gap:5px;
  padding:5px 7px;
  border:1px solid #30343c;
  border-radius:999px;
  background:#12141a;
  color:#d9dde3;
  font-size:7.5px;
}
.v269-prep-chip span{
  min-width:0;
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
}
.v269-prep-chip button{
  width:18px;height:18px;min-width:18px;
  border:0;border-radius:50%;
  background:#252832;color:#aeb4be;
  cursor:pointer;
}
.v269-prep-empty{
  margin-top:8px;
  color:#737985;
  font-size:7.5px;
}

/* Student workout preparation cards */
.v269-workout-prep{
  margin:12px 0!important;
  border-color:#30343c!important;
}
.v269-workout-prep.cooldown{margin-top:14px!important}
.v269-workout-prep-head{
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  gap:8px;
}
.v269-workout-prep-head span:first-child{
  display:block;
  color:#ff6877;
  font-size:7px;
  font-weight:950;
  letter-spacing:.1em;
}
.v269-workout-prep-head strong{
  display:block;
  margin-top:3px;
  color:#f5f6f8;
  font-size:13px;
}
.v269-workout-prep-list{
  display:grid;
  gap:6px;
  margin-top:10px;
}
.v269-workout-prep-item{
  display:grid;
  grid-template-columns:24px minmax(0,1fr);
  gap:8px;
  align-items:start;
  padding:8px;
  border:1px solid #292d34;
  border-radius:9px;
  background:#0d0e12;
}
.v269-workout-prep-item>span{
  width:24px;height:24px;
  display:grid;place-items:center;
  border-radius:7px;
  background:#191b21;
  color:#ff7784;
  font-size:8px;
  font-weight:950;
}
.v269-workout-prep-item strong{
  display:block;
  color:#eef0f3;
  font-size:9px;
}
.v269-workout-prep-item small{
  display:block;
  margin-top:3px;
  color:#858b95;
  font-size:7.5px;
  line-height:1.4;
}

@media(max-width:760px){
  .modal{
    width:calc(100vw - 16px)!important;
    max-width:calc(100vw - 16px)!important;
    max-height:92vh!important;
    padding:13px!important;
    border-radius:15px!important;
  }
  .v269-title-block h3{font-size:16px!important}
  .v269-search-row{
    grid-template-columns:1fr!important;
  }
  .v269-custom-btn{
    width:100%!important;
    min-width:0!important;
  }
  .v269-library-filters{
    grid-template-columns:1fr!important;
  }
  .v269-library-grid{
    grid-template-columns:1fr!important;
  }
  .v269-library-item{
    grid-template-columns:minmax(0,1fr) auto!important;
  }
  .v269-prep-editor{
    grid-template-columns:1fr!important;
  }
  .v269-form-head-left{
    display:grid!important;
    grid-template-columns:1fr!important;
  }
  .v269-back-btn{
    width:max-content!important;
    max-width:100%!important;
  }
}
@media(max-width:430px){
  .v269-modal-head{gap:7px!important}
  .v269-library-item{
    grid-template-columns:1fr!important;
    align-items:stretch!important;
  }
  .v269-library-item>.btn{
    width:100%!important;
    min-width:0!important;
  }
  .v269-prep-head{
    display:grid;
    grid-template-columns:minmax(0,1fr) auto;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.69 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-routine-library-preparation" content="20.69">\n</head>',1)

after=metrics(html)
for key in ("styles","channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.69 runtime topology changed "+key+": "+repr({"before":before,"after":after}))
if after["renders"]!=before["renders"]:
    raise RuntimeError("V20.69 render assignment topology changed: "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-routine-library-preparation" content="20.69"',
    "mainLibraryStrengthOnly:true",
    "preparationLibrarySeparated:true",
    "warmupBeforeWorkout:true",
    "stretchingAfterWorkout:true",
    "stableExerciseModalHeader:true",
    "mobileLibraryGeometry:true",
    "prepPersistsInAthleteSnapshot:true",
    "openPrepLibraryV269",
    "v269-prep-editor",
    "v269-library-shell"
]:
    if marker not in html:
        raise RuntimeError("V20.69 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.69 routine library/preparation cleanup")
print("V20.69 BEFORE:",before)
print("V20.69 AFTER:",after)
print("V20.69 main exercise library separated from warm-up/stretching; modal geometry stabilized")
