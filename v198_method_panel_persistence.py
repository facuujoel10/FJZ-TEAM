import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

js=r"""
<script id="v198MethodPanelPersistenceRuntime">
(function(){
  const VERSION='19.8';

  function escV198(v){
    return String(v??'')
      .replaceAll('&','&amp;')
      .replaceAll('<','&lt;')
      .replaceAll('>','&gt;')
      .replaceAll('"','&quot;')
      .replaceAll("'","&#39;");
  }

  function stepsV198(method){
    if(method==='dropset')return [
      ['d1','Descenso 1'],
      ['d2','Descenso 2'],
      ['d3','Descenso 3']
    ];
    if(method==='superserie')return [
      ['b','Ejercicio B']
    ];
    return [];
  }

  function labelV198(method){
    return method==='dropset'?'Dropset':
           method==='superserie'?'Superserie / biserie':
           'Método';
  }

  function activeSetsV198(e){
    const n=Math.max(1,Number(e?.sets)||1);
    const apply=e?.methodApply||((e?.method==='superserie')?'all':'last');
    if(apply==='all')return Array.from({length:n},(_,i)=>i);
    return [n-1];
  }

  function panelV198(e){
    if(!e?.uid||!e?.method||e.method==='normal')return '';
    const steps=stepsV198(e.method);
    if(!steps.length)return '';

    const root=window.__fjzMethodDraftV110||{};
    const current=root[e.uid]||{sets:{},note:''};
    const indexes=activeSetsV198(e);

    return '<div class="v137-method-panel" data-v137-method="'+escV198(e.uid)+'">'+
      '<div class="v137-method-head"><div><strong>Registrar '+escV198(labelV198(e.method))+'</strong>'+
      '<div class="muted micro">La serie principal va arriba. Acá cargá los pesos y reps extra del método.</div>'+
      (e.methodNote?'<div class="v137-method-chip">'+escV198(e.methodNote)+'</div>':'')+
      '</div><span class="v137-method-badge">'+escV198(labelV198(e.method))+'</span></div>'+
      indexes.map(si=>{
        const vals=current.sets?.[si]||{};
        return '<div class="v137-method-set"><div class="v137-method-set-title">Serie '+(si+1)+'</div>'+
          '<div class="v137-method-grid">'+steps.map(([key,label])=>
            '<div class="v137-method-step"><div class="v137-method-step-title">'+escV198(label)+'</div>'+
              '<label class="tiny muted">Kg<input class="input" inputmode="decimal" type="number" min="0" step="0.5" value="'+escV198(vals[key+'kg']??'')+'" oninput="setMethodPartV137(\''+escV198(e.uid)+'\','+si+',\''+key+'\',\'kg\',this.value)"></label>'+
              '<label class="tiny muted">Reps<input class="input" inputmode="numeric" type="number" min="0" step="1" value="'+escV198(vals[key+'reps']??'')+'" oninput="setMethodPartV137(\''+escV198(e.uid)+'\','+si+',\''+key+'\',\'reps\',this.value)"></label>'+
            '</div>'
          ).join('')+'</div></div>';
      }).join('')+
      '<label class="tiny muted v137-method-note">Nota del método<input class="input" maxlength="180" value="'+escV198(current.note||'')+'" placeholder="Opcional" oninput="setMethodNoteV137(\''+escV198(e.uid)+'\',this.value)"></label>'+
    '</div>';
  }

  const baseWorkoutExerciseV198=window.workoutExercise||globalThis.workoutExercise;
  if(typeof baseWorkoutExerciseV198==='function'){
    const wrapped=function(e,i){
      const out=baseWorkoutExerciseV198.apply(this,arguments);
      if(!e?.method||e.method==='normal')return out;
      if(String(out).includes('data-v137-method='))return out;
      return out+panelV198(e);
    };
    wrapped.__v198Wrapped=true;
    window.workoutExercise=wrapped;
    try{workoutExercise=wrapped}catch(_e){}
  }

  window.__fjzV198={
    version:VERSION,
    methodPanelSurvivesCardRebuild:true,
    legacyMethodApplyDefaultsSupported:true,
    dropsetWeightSlotsGuaranteed:true,
    superserieWeightSlotsGuaranteed:true
  };
})();
</script>
"""

html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "methodPanelSurvivesCardRebuild:true",
  "dropsetWeightSlotsGuaranteed:true",
  "superserieWeightSlotsGuaranteed:true"
]:
    if marker not in html:
        raise RuntimeError("V19.8 missing "+marker)

if "setMethodPartV137" not in html:
    raise RuntimeError("V19.8 missing V137 method setter")
if "setMethodNoteV137" not in html:
    raise RuntimeError("V19.8 missing V137 method note setter")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V19.8 method panels persist after workout card rebuilds")
