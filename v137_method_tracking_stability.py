import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v137MethodAndDesktopStabilityStyles">
html{scrollbar-gutter:stable}
@media(min-width:900px){html{overflow-y:scroll}}
#view,#coachStudentBody,#studentSubBody{min-width:0}
@media(min-width:900px){
  #coachStudentBody,#studentSubBody{min-height:640px}
}
.session-card,.exercise-row,.day-card,.card,.modal-card{box-sizing:border-box;min-width:0}
.session-card,.exercise-row,.day-card{transition:none!important;transform:none!important}
.v137-method-panel{margin:-8px 0 14px;padding:12px;border:1px solid rgba(255,55,70,.22);border-top:0;border-radius:0 0 14px 14px;background:linear-gradient(180deg,rgba(255,255,255,.018),rgba(255,45,58,.035))}
.v137-method-head{display:flex;justify-content:space-between;gap:10px;align-items:flex-start;margin-bottom:10px}
.v137-method-head strong{font-size:12px}
.v137-method-head .muted{margin-top:3px;line-height:1.4}
.v137-method-badge{display:inline-flex;flex:0 0 auto;padding:4px 7px;border-radius:999px;border:1px solid rgba(255,45,58,.28);background:rgba(255,45,58,.07);font-size:9px;font-weight:850}
.v137-method-set{border:1px solid var(--border);border-radius:12px;padding:10px;margin-top:8px;background:rgba(255,255,255,.018)}
.v137-method-set-title{font-size:10px;font-weight:850;margin-bottom:8px}
.v137-method-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.v137-method-step{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:7px;padding:8px;border:1px solid var(--border);border-radius:10px}
.v137-method-step-title{grid-column:1/-1;font-size:9px;font-weight:800;color:var(--muted)}
.v137-method-step label{min-width:0}
.v137-method-step .input{width:100%;min-width:0;box-sizing:border-box}
.v137-method-prev{margin-top:10px;padding-top:9px;border-top:1px dashed var(--border);font-size:9px;line-height:1.5;color:var(--muted)}
.v137-method-coach{grid-column:1/-1;border:1px solid rgba(255,45,58,.18);border-radius:12px;padding:11px;background:rgba(255,45,58,.025)}
.v137-method-coach-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-top:8px}
.v137-method-note{margin-top:8px}
.v137-method-chip{display:inline-flex;margin-top:5px;padding:3px 7px;border-radius:999px;border:1px solid rgba(255,45,58,.25);font-size:8px;color:var(--muted)}
body.v137-interacting #view{overflow-anchor:none}
@media(max-width:760px){
  .v137-method-grid,.v137-method-coach-grid{grid-template-columns:1fr}
}
@media(max-width:520px){
  .v137-method-step{grid-template-columns:1fr 1fr}
}
</style>
"""

# Disable the old V11 method block. V13.7 renders the complete weight+reps editor.
html,n_old=re.subn(
    r"function methodBlockV110\(e\)\{.*?\n  \}\n\n  const baseWorkoutV110",
    "function methodBlockV110(e){return '';}\n\n  const baseWorkoutV110",
    html,count=1,flags=re.S
)
if n_old!=1:
    raise RuntimeError(f"V13.7 could not disable old method block: {n_old}")

# Improve historical text for the new numeric keys.
new_log=r"""function methodLogTextV110(log){
    if(!log)return '';
    const labels={
      d1kg:'Descenso 1',d2kg:'Descenso 2',d3kg:'Descenso 3',
      rp1kg:'RP 1',rp2kg:'RP 2',
      bkg:'Ejercicio B',
      myo1kg:'Miniset 1',myo2kg:'Miniset 2',myo3kg:'Miniset 3',
      cl1kg:'Bloque 1',cl2kg:'Bloque 2',cl3kg:'Bloque 3'
    };
    const rows=Object.entries(log.sets||{}).map(([si,vals])=>{
      const parts=[];
      Object.entries(labels).forEach(([kgKey,label])=>{
        const repKey=kgKey.replace('kg','reps');
        const kg=vals?.[kgKey],reps=vals?.[repKey];
        if(kg!==undefined||reps!==undefined){
          parts.push(label+': '+(kg!==undefined?kg+' kg':'—')+' × '+(reps!==undefined?reps+' reps':'—'));
        }
      });
      return parts.length?'S'+(Number(si)+1)+' · '+parts.join(' · '):'';
    }).filter(Boolean);
    if(log.note)rows.push('Nota: '+log.note);
    return rows.join(' | ');
  }"""
html,n_log=re.subn(
    r"function methodLogTextV110\(log\)\{.*?\n  \}\n  function previousMethodLogV110",
    new_log+"\n  function previousMethodLogV110",
    html,count=1,flags=re.S
)
if n_log!=1:
    raise RuntimeError(f"V13.7 could not replace method log formatter: {n_log}")

# Persist coach-selected method fields in the canonical exercise object.
needle="override:old?.override||null};"
replacement="override:old?.override||null,method:el('fMethodV137')?.value||old?.method||'normal',methodNote:el('fMethodNoteV137')?.value.trim()||'',methodApply:el('fMethodApplyV137')?.value||old?.methodApply||'last'};"
if needle not in html:
    raise RuntimeError("V13.7 could not locate canonical saveExercise payload")
html=html.replace(needle,replacement,1)

# Defer cloud refresh while a workout or form interaction is active.
refresh_needle="async function refreshCloudFromRealtime(){"
if refresh_needle not in html:
    raise RuntimeError("V13.7 could not locate refreshCloudFromRealtime")
html=html.replace(
    refresh_needle,
    refresh_needle+"\n  if(window.__fjzShouldDeferRefreshV137?.()){window.__fjzDeferredCloudRefreshV137=true;return;}",
    1
)

js=r"""
<script id="v137MethodAndDesktopStabilityRuntime">
(function(){
  const METHOD_LABELS={
    dropset:'Dropset',
    rest_pause:'Rest-pause',
    superserie:'Superserie / biserie',
    myo_reps:'Myo-reps',
    cluster:'Cluster'
  };

  function escAttrV137(v){return esc(String(v??''))}
  function methodLabelV137(m){return METHOD_LABELS[m]||'Método'}

  function activeSetIndexesV137(e){
    const n=Math.max(1,Number(e?.sets)||1);
    const apply=e?.methodApply||((e?.method==='superserie')?'all':'last');
    if(apply==='all')return Array.from({length:n},(_,i)=>i);
    return [n-1];
  }

  function methodStepsV137(method){
    if(method==='dropset')return [
      ['d1','Descenso 1'],['d2','Descenso 2'],['d3','Descenso 3']
    ];
    if(method==='rest_pause')return [
      ['rp1','Rest-pause 1'],['rp2','Rest-pause 2']
    ];
    if(method==='superserie')return [
      ['b','Ejercicio B']
    ];
    if(method==='myo_reps')return [
      ['myo1','Miniset 1'],['myo2','Miniset 2'],['myo3','Miniset 3']
    ];
    if(method==='cluster')return [
      ['cl1','Bloque 1'],['cl2','Bloque 2'],['cl3','Bloque 3']
    ];
    return [];
  }

  function ensureMethodEntryV137(uidv,si){
    window.__fjzMethodDraftV110=window.__fjzMethodDraftV110||{};
    const root=window.__fjzMethodDraftV110;
    root[uidv]=root[uidv]||{sets:{},note:''};
    root[uidv].sets=root[uidv].sets||{};
    root[uidv].sets[si]=root[uidv].sets[si]||{};
    return root[uidv].sets[si];
  }

  window.setMethodPartV137=function(uidv,si,key,field,val){
    const row=ensureMethodEntryV137(uidv,si);
    const full=key+(field==='kg'?'kg':'reps');
    const raw=String(val??'').trim();
    if(raw===''){delete row[full];return}
    const n=Number(raw);
    if(Number.isFinite(n)&&n>=0)row[full]=n;
  };

  window.setMethodNoteV137=function(uidv,val){
    window.__fjzMethodDraftV110=window.__fjzMethodDraftV110||{};
    const root=window.__fjzMethodDraftV110;
    root[uidv]=root[uidv]||{sets:{},note:''};
    root[uidv].note=String(val||'').slice(0,180);
  };

  function prevMethodTextV137(log){
    if(!log)return '';
    const labels={
      d1:'Descenso 1',d2:'Descenso 2',d3:'Descenso 3',
      rp1:'RP 1',rp2:'RP 2',b:'Ejercicio B',
      myo1:'Miniset 1',myo2:'Miniset 2',myo3:'Miniset 3',
      cl1:'Bloque 1',cl2:'Bloque 2',cl3:'Bloque 3'
    };
    const out=[];
    Object.entries(log.sets||{}).forEach(([si,vals])=>{
      const parts=[];
      Object.entries(labels).forEach(([key,label])=>{
        const kg=vals?.[key+'kg'],reps=vals?.[key+'reps'];
        if(kg!==undefined||reps!==undefined){
          parts.push(label+' '+(kg!==undefined?kg+' kg':'—')+' × '+(reps!==undefined?reps:'—'));
        }
      });
      if(parts.length)out.push('S'+(Number(si)+1)+': '+parts.join(' · '));
    });
    if(log.note)out.push('Nota: '+log.note);
    return out.join(' | ');
  }

  function methodPanelV137(e){
    if(!e?.method||e.method==='normal')return '';
    const steps=methodStepsV137(e.method);
    if(!steps.length)return '';
    const root=window.__fjzMethodDraftV110||{};
    const current=root[e.uid]||{sets:{},note:''};
    const prev=latestHistory(e)?.methodLog||null;
    const setIndexes=activeSetIndexesV137(e);
    return '<div class="v137-method-panel" data-v137-method="'+escAttrV137(e.uid)+'">'+
      '<div class="v137-method-head"><div><strong>Registrar '+esc(methodLabelV137(e.method))+'</strong>'+
      '<div class="muted micro">Completá solo los tramos extra del método. La serie principal se registra arriba.</div>'+
      (e.methodNote?'<div class="v137-method-chip">'+esc(e.methodNote)+'</div>':'')+
      '</div><span class="v137-method-badge">'+esc(methodLabelV137(e.method))+'</span></div>'+
      setIndexes.map(si=>{
        const vals=current.sets?.[si]||{};
        return '<div class="v137-method-set"><div class="v137-method-set-title">Serie '+(si+1)+'</div>'+
          '<div class="v137-method-grid">'+steps.map(([key,label])=>
            '<div class="v137-method-step"><div class="v137-method-step-title">'+esc(label)+'</div>'+
              '<label class="tiny muted">Kg<input class="input" inputmode="decimal" type="number" min="0" step="0.5" value="'+(vals[key+'kg']??'')+'" oninput="setMethodPartV137(\''+e.uid+'\','+si+',\''+key+'\',\'kg\',this.value)"></label>'+
              '<label class="tiny muted">Reps<input class="input" inputmode="numeric" type="number" min="0" step="1" value="'+(vals[key+'reps']??'')+'" oninput="setMethodPartV137(\''+e.uid+'\','+si+',\''+key+'\',\'reps\',this.value)"></label>'+
            '</div>'
          ).join('')+'</div></div>';
      }).join('')+
      '<label class="tiny muted v137-method-note">Nota del método<input class="input" maxlength="180" value="'+escAttrV137(current.note||'')+'" placeholder="Opcional" oninput="setMethodNoteV137(\''+e.uid+'\',this.value)"></label>'+
      (prev?'<div class="v137-method-prev"><strong>Último registro:</strong> '+esc(prevMethodTextV137(prev))+'</div>':'')+
    '</div>';
  }

  // Final workout renderer: one method panel only, and only when the coach assigned a method.
  const baseWorkoutV137=workoutExercise;
  workoutExercise=function(e,i){
    return baseWorkoutV137.apply(this,arguments)+methodPanelV137(e);
  };

  function methodCoachHtmlV137(e){
    const current=e?.method||'normal';
    const apply=e?.methodApply||((current==='superserie')?'all':'last');
    return '<div class="v137-method-coach" id="v137MethodCoachBox">'+
      '<strong>Método de intensidad</strong><div class="muted tiny" style="margin-top:3px">Solo si elegís un método, el alumno verá campos extra para registrar Kg y reps.</div>'+
      '<div class="v137-method-coach-grid">'+
        '<label class="tiny muted">Método<select id="fMethodV137" class="input" onchange="syncMethodFormV137()">'+
          '<option value="normal" '+(current==='normal'?'selected':'')+'>Sin método</option>'+
          '<option value="dropset" '+(current==='dropset'?'selected':'')+'>Dropset</option>'+
          '<option value="rest_pause" '+(current==='rest_pause'?'selected':'')+'>Rest-pause</option>'+
          '<option value="superserie" '+(current==='superserie'?'selected':'')+'>Superserie / biserie</option>'+
          '<option value="myo_reps" '+(current==='myo_reps'?'selected':'')+'>Myo-reps</option>'+
          '<option value="cluster" '+(current==='cluster'?'selected':'')+'>Cluster</option>'+
        '</select></label>'+
        '<label class="tiny muted" id="v137MethodApplyLabel">Aplicar en<select id="fMethodApplyV137" class="input">'+
          '<option value="last" '+(apply==='last'?'selected':'')+'>Última serie</option>'+
          '<option value="all" '+(apply==='all'?'selected':'')+'>Todas las series</option>'+
        '</select></label>'+
      '</div>'+
      '<label class="tiny muted v137-method-note" id="v137MethodNoteLabel">Indicación del método<input id="fMethodNoteV137" class="input" maxlength="180" value="'+escAttrV137(e?.methodNote||'')+'" placeholder="Ej: 2 drops de 8-10 reps / 15 s de pausa"></label>'+
    '</div>';
  }

  window.syncMethodFormV137=function(){
    const m=el('fMethodV137')?.value||'normal';
    const show=m!=='normal';
    const a=el('v137MethodApplyLabel'),n=el('v137MethodNoteLabel');
    if(a)a.style.display=show?'block':'none';
    if(n)n.style.display=show?'block':'none';
    if(m==='superserie'&&el('fMethodApplyV137'))el('fMethodApplyV137').value='all';
  };

  const baseShowExerciseV137=showExerciseForm;
  showExerciseForm=function(dayIndex,exIndex,e){
    const out=baseShowExerciseV137.apply(this,arguments);
    const grid=el('modal')?.querySelector('.form-grid');
    if(grid&&!el('v137MethodCoachBox')){
      grid.insertAdjacentHTML('beforeend',methodCoachHtmlV137(e));
      syncMethodFormV137();
    }
    return out;
  };

  function methodBadgeV137(e){
    if(!e?.method||e.method==='normal')return '';
    const apply=(e.methodApply||'last')==='all'?'todas las series':'última serie';
    return '<span class="v137-method-chip">'+esc(methodLabelV137(e.method))+' · '+esc(apply)+'</span>';
  }

  function enhanceCoachRoutineV137(){
    if(currentProfile?.role!=='coach'||coachTab!=='student'||coachStudentTab!=='routine')return;
    const s=student();
    (s?.days||[]).forEach(d=>(d.exercises||[]).forEach(e=>{
      if(!e.method||e.method==='normal')return;
      const row=document.querySelector('[data-v73-exercise-uid="'+CSS.escape(e.uid)+'"]');
      if(!row||row.querySelector('.v137-method-chip'))return;
      const host=row.querySelector('div');
      if(host)host.insertAdjacentHTML('beforeend',methodBadgeV137(e));
    }));
  }

  // ---- interaction / background refresh stability ----
  let deferredRenderV137=false;
  let flushTimerV137=null;
  window.__fjzDeferredCloudRefreshV137=false;
  window.__fjzInteractionUntilV137=0;

  function activeFormV137(){
    const a=document.activeElement;
    return !!(a&&a.matches?.('input,select,textarea,[contenteditable="true"]'));
  }

  window.__fjzShouldDeferRefreshV137=function(){
    if(currentProfile?.role==='student'&&studentTab==='workout')return true;
    if(activeFormV137())return true;
    return Date.now()<Number(window.__fjzInteractionUntilV137||0);
  };

  function markInteractionV137(ms=500){
    window.__fjzInteractionUntilV137=Date.now()+ms;
    document.body?.classList.add('v137-interacting');
    clearTimeout(flushTimerV137);
    flushTimerV137=setTimeout(()=>{
      document.body?.classList.remove('v137-interacting');
      flushDeferredV137();
    },ms+40);
  }

  function flushDeferredV137(){
    if(window.__fjzShouldDeferRefreshV137())return;
    if(deferredRenderV137){
      deferredRenderV137=false;
      baseScheduleV137?.();
    }
    if(window.__fjzDeferredCloudRefreshV137){
      window.__fjzDeferredCloudRefreshV137=false;
      try{refreshCloudFromRealtime()}catch(e){}
    }
  }

  document.addEventListener('pointerdown',()=>markInteractionV137(450),true);
  document.addEventListener('input',()=>markInteractionV137(650),true);
  document.addEventListener('focusin',()=>markInteractionV137(650),true);
  document.addEventListener('focusout',()=>setTimeout(flushDeferredV137,180),true);
  document.addEventListener('pointerup',()=>setTimeout(flushDeferredV137,220),true);

  const baseScheduleV137=window.fjzScheduleRenderV125;
  if(typeof baseScheduleV137==='function'){
    window.fjzScheduleRenderV125=function(){
      if(window.__fjzShouldDeferRefreshV137()){
        deferredRenderV137=true;
        return;
      }
      return baseScheduleV137.apply(this,arguments);
    };
  }

  const baseRenderV137=render;
  render=function(){
    const out=baseRenderV137.apply(this,arguments);
    fjzPostRenderV125('routine-method-v137',enhanceCoachRoutineV137);
    if(!(currentProfile?.role==='student'&&studentTab==='workout'))setTimeout(flushDeferredV137,0);
    return out;
  };

  window.__fjzV137={
    version:'13.7',
    methodWeightAndReps:true,
    conditionalMethodFields:true,
    interactionRefreshGuard:true,
    desktopScrollbarStability:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

# Build-time validations.
for marker in [
    "Método de intensidad",
    "setMethodPartV137",
    "conditionalMethodFields:true",
    "__fjzShouldDeferRefreshV137",
    "scrollbar-gutter:stable"
]:
    if marker not in html:
        raise RuntimeError("V13.7 missing marker: "+marker)
if html.count("v137-method-panel")<2:
    raise RuntimeError("V13.7 method panel CSS/runtime incomplete")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V13.7 method tracking + desktop stability:",len(html),"bytes")
print("V13.7 old method block disabled:",n_old,"history formatter:",n_log)
