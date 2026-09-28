import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v147ProgramAuthorityStyles">
.v147-plan-note{
  margin-top:8px;padding:8px 10px;border:1px solid rgba(90,167,255,.22);
  border-radius:10px;background:rgba(90,167,255,.045);font-size:9px;color:var(--muted)
}
.v147-plan-note strong{color:var(--text)}
</style>
"""

js=r"""
<script id="v147ProgramAuthorityRuntime">
(function(){
  const VERSION='14.7';

  function programmedRepV147(e,i){
    if(e?.repMode==='exact'&&Array.isArray(e.repsExact)&&e.repsExact.length){
      return Number(e.repsExact[i]??e.repsExact[e.repsExact.length-1])||Number(e.min)||1;
    }
    return Number(e?.min)||1;
  }

  function previousLoadV147(e,i){
    const prev=latestHistory(e)?.sets||[];
    const row=prev[i]||prev[prev.length-1]||null;
    return Number(row?.[0])||0;
  }

  function programmedStartSetV147(e,i){
    return [
      previousLoadV147(e,i),
      programmedRepV147(e,i),
      Number(e?.rirMax??e?.rirMin??2)
    ];
  }

  // IMPORTANT: history is reference only. It never becomes next-session structure.
  ensureDraft=function(e){
    if(!workoutDraft[e.uid]){
      workoutDraft[e.uid]=Array.from({length:Number(e.sets)||0},(_,i)=>programmedStartSetV147(e,i));
    }
    return workoutDraft[e.uid];
  };

  currentSets=function(e){
    if(workoutDraft[e.uid])return workoutDraft[e.uid];
    return Array.from({length:Number(e.sets)||0},(_,i)=>programmedStartSetV147(e,i));
  };

  const baseRecommendationV147=currentRecommendation;
  currentRecommendation=function(e){
    // A freshly opened workout has no "next prescription" generated from history.
    // The coach-programmed target remains authoritative until the athlete enters data.
    if(!workoutDraft[e.uid]){
      if(e.override?.active){
        return {
          type:'override',
          title:e.override.title||'Indicación del coach',
          copy:e.override.note||'Seguí la indicación manual del coach.',
          auto:{type:'plan',title:'La estructura de la rutina no cambia automáticamente'}
        };
      }
      return {
        type:'plan',
        title:'Seguí el objetivo programado',
        copy:'Las series y repeticiones las define tu coach. El historial anterior es solo una referencia de carga.'
      };
    }
    return baseRecommendationV147.apply(this,arguments);
  };

  const baseRecommendationHtmlV147=recommendationHtml;
  recommendationHtml=function(e,r){
    const out=baseRecommendationHtmlV147.apply(this,arguments);
    if(r?.type==='plan')return '<div class="recommend coach"><strong>'+esc(r.title)+'</strong><div class="muted tiny" style="margin-top:4px">'+esc(r.copy)+'</div></div>';
    if(!r||r.type==='override')return out;
    return out.replace(
      '</div>',
      '<div class="v147-plan-note"><strong>Sugerencia automática:</strong> no cambia las series ni las repeticiones cargadas por tu coach.</div></div>'
    );
  };

  // Final workout renderer: previous session remains visible, but only the last
  // WEIGHT is carried forward. Reps/RIR always start from the programmed target.
  const baseWorkoutExerciseV147=workoutExercise;
  workoutExercise=function(e,i){
    let out=baseWorkoutExerciseV147.apply(this,arguments);
    const prev=latestHistory(e)?.sets||[];
    if(!prev.length)return out;

    // Replace the rendered input defaults only when there is no active draft.
    if(!workoutDraft[e.uid]){
      const temp=document.createElement('div');
      temp.innerHTML=out;
      const card=temp.firstElementChild;
      const rows=[...card.querySelectorAll('.set-grid')];
      rows.forEach((row,si)=>{
        const inputs=row.querySelectorAll('input');
        if(inputs[0])inputs[0].value=previousLoadV147(e,si)||'';
        if(inputs[1])inputs[1].value=programmedRepV147(e,si);
        if(inputs[2])inputs[2].value=Number(e?.rirMax??e?.rirMin??2);
      });
      const rec=card.querySelector('[id^="rec_"]');
      if(rec)rec.innerHTML=recommendationHtml(e,currentRecommendation(e));
      out=card.outerHTML;
    }
    return out;
  };

  window.__fjzProgramAuthorityV147={
    version:VERSION,
    programmedStructureAlwaysWins:true,
    carryForwardWeightOnly:true,
    previousRepsNeverBecomeTarget:true,
    automaticRecommendationNeverChangesPlan:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "programmedStructureAlwaysWins:true",
  "carryForwardWeightOnly:true",
  "previousRepsNeverBecomeTarget:true",
  "automaticRecommendationNeverChangesPlan:true"
]:
    if marker not in html:
        raise RuntimeError("V14.7 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V14.7 programmed routine authority enabled")
