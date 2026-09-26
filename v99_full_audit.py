import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")
html=html.replace("TEAM FJZ V9.8","TEAM FJZ V9.9")

css=r"""
<style id="v99AuditPolish">
/* V9.9 · auditoría visual y estabilidad */

/* Ocultar restos técnicos de versiones antiguas */
.v88-version,#v88Version,#v92CoachPhotoUploader,#cloudFeedWrap{display:none!important}

/* Check-in: 8 variables, matriz perfectamente simétrica */
#studentSubBody .tracking-grid,
#studentSubBody .v701-checkin-scores{
  grid-template-columns:repeat(4,minmax(0,1fr))!important;
  gap:9px!important;
}
#studentSubBody .tracking-grid>.track-score,
#studentSubBody .v701-checkin-scores>.track-score{
  grid-column:auto!important;
  min-height:100px!important;
  height:100px!important;
  padding:11px!important;
}
#studentSubBody .tracking-grid>.track-score label,
#studentSubBody .v701-checkin-scores>.track-score label{
  min-height:28px!important;
  height:28px!important;
}
#studentSubBody .tracking-grid>.track-score input,
#studentSubBody .v701-checkin-scores>.track-score input{
  height:40px!important;
  min-height:40px!important;
}
@media(max-width:760px){
  #studentSubBody .tracking-grid,
  #studentSubBody .v701-checkin-scores{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
  }
}
@media(max-width:360px){
  #studentSubBody .tracking-grid,
  #studentSubBody .v701-checkin-scores{
    grid-template-columns:1fr!important;
  }
}

/* Oculta sin parpadeo campos de medidas obsoletos */
label:has(>#mAbd),
label:has(>#mArmRight),
label:has(>#mThighRight){display:none!important}

/* Botones y controles consistentes */
.btn.small{min-height:32px;display:inline-flex;align-items:center;justify-content:center}
.btn:not(.small){min-height:40px}
.pill-row{align-items:center!important}
.track-row-head,.meal-head,.option-head,.day-head,.v94-guide-head,.v96-center-head{
  align-items:flex-start!important;
}

/* Tablas/filas con ritmo visual estable */
.student-row,.exercise-row,.history-item,.track-row,.v93-measure-row,.v94-supp-row,.v96-notice-item{
  box-sizing:border-box!important;
}
.student-row{min-height:68px}
.exercise-row{min-height:58px}
.history-item{min-height:52px}
.v93-measure-row{min-height:46px}

/* Fotos: mejor comportamiento en pantallas pequeñas */
@media(max-width:700px){
  .photo-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important}
}
@media(max-width:430px){
  .photo-grid{grid-template-columns:1fr!important}
}

/* Nutrición */
.nutrition-targets,.macro-preview{align-items:stretch!important}
.nutrition-targets>.macro-card,.macro-preview>div{height:100%!important;box-sizing:border-box!important}
.food-item,.food-item-v61,.nutrition-log-row{min-width:0}
@media(max-width:520px){
  .nutrition-targets,.macro-preview{grid-template-columns:1fr 1fr!important}
  .food-item{grid-template-columns:1fr!important}
}

/* Modales y textos largos */
.modal,.modal-card,.modal-content{max-width:100%!important;box-sizing:border-box!important}
.modal-head>div{min-width:0}
.modal-head h3,.section-title h3,.exercise-row h4,.student-row h4{
  overflow-wrap:anywhere
}

/* Evitar overflow horizontal accidental */
#view,#studentSubBody,#coachStudentBody{min-width:0;max-width:100%}
.card,.hero,.grid,.form-grid{min-width:0}
</style>
"""

js=r"""
<script id="v99AuditRuntime">
(function(){
  function clamp110V99(input){
    if(!input)return;
    let raw=String(input.value??'').replace(/[^0-9]/g,'');
    if(raw===''){input.value='';return}
    let n=parseInt(raw,10);
    if(!Number.isFinite(n))n=1;
    input.value=String(Math.max(1,Math.min(10,n)));
  }

  function moveHungerIntoGridV99(){
    const input=document.getElementById('ciHunger');
    const grid=document.querySelector('#studentSubBody .tracking-grid, #studentSubBody .v701-checkin-scores');
    if(!input||!grid)return;

    let card=input.closest('.track-score');
    if(!card){
      const oldLabel=input.closest('label');
      card=document.createElement('div');
      card.className='track-score';
      const label=document.createElement('label');
      label.textContent='Hambre';
      card.appendChild(label);
      card.appendChild(input);
      if(oldLabel&&oldLabel.parentNode)oldLabel.remove();
    }
    card.setAttribute('data-v99-hunger','1');

    const motivation=document.getElementById('ciMotivation')?.closest('.track-score');
    if(motivation)grid.insertBefore(card,motivation);
    else grid.appendChild(card);
  }

  function normalizeScoresV99(){
    moveHungerIntoGridV99();
    const ids=['ciSleep','ciStress','ciEnergy','ciAdh','ciMood','ciHunger','ciMotivation','ciRecovery'];
    ids.forEach(function(id){
      const inputs=[...document.querySelectorAll('#'+id)];
      inputs.slice(1).forEach(function(x){
        const card=x.closest('.track-score');if(card)card.remove();else x.remove();
      });
      const input=document.getElementById(id);
      if(!input)return;
      input.min='1';input.max='10';input.step='1';input.inputMode='numeric';
      input.oninput=function(){clamp110V99(input)};
      input.onchange=function(){clamp110V99(input)};
      const card=input.closest('.track-score');
      if(card){card.style.gridColumn='auto';card.style.width='100%'}
    });

    const grid=document.querySelector('#studentSubBody .tracking-grid, #studentSubBody .v701-checkin-scores');
    if(grid){
      ids.forEach(function(id){
        const card=document.getElementById(id)?.closest('.track-score');
        if(card)grid.appendChild(card);
      });
    }
  }

  function removeLegacyV99(){
    document.querySelectorAll('#v88Version,#v92CoachPhotoUploader,#cloudFeedWrap').forEach(n=>n.remove());
  }

  function removeDuplicateIdV99(id){
    const nodes=[...document.querySelectorAll('#'+id)];
    nodes.slice(1).forEach(n=>n.remove());
  }

  function tidyDuplicatesV99(){
    [
      'v93MeasureCompare','v96CoachAlerts','v96StudentPreview','v94SuppCoach',
      'v94SuppStudent','v86StudentProfileCard','v86CoachProfile',
      'v93CoachPhotoUploader','v96NoticeCoachCard'
    ].forEach(removeDuplicateIdV99);
  }

  function prettyDateV99(s){
    const m=String(s||'').match(/^(\d{4})-(\d{2})-(\d{2})$/);
    return m?m[3]+'/'+m[2]+'/'+m[1]:s;
  }

  function prettyDatesInCompareV99(){
    document.querySelectorAll('.v93-compare-head .muted.tiny').forEach(function(n){
      n.textContent=n.textContent.replace(/\b(\d{4})-(\d{2})-(\d{2})\b/g,'$3/$2/$1');
    });
  }

  const oldChartV99=window.simpleLineChart;
  if(typeof oldChartV99==='function'){
    window.simpleLineChart=function(){
      const out=oldChartV99.apply(this,arguments);
      return typeof out==='string'
        ?out.replace(/\b(\d{4})-(\d{2})-(\d{2})\b/g,'$3/$2/$1')
        :out;
    };
  }

  const oldSubmitV99=window.submitWeeklyCheckin;
  if(typeof oldSubmitV99==='function'){
    window.submitWeeklyCheckin=async function(){
      normalizeScoresV99();
      const ids=['ciSleep','ciStress','ciEnergy','ciAdh','ciMood','ciHunger','ciMotivation','ciRecovery'];
      for(const id of ids){
        const input=document.getElementById(id);
        if(!input)continue;
        clamp110V99(input);
        const n=Number(input.value);
        if(!Number.isFinite(n)||n<1||n>10){
          toast('Todos los valores del check-in deben estar entre 1 y 10');
          input.focus();return;
        }
      }
      return oldSubmitV99.apply(this,arguments);
    };
  }

  function auditPolishV99(){
    removeLegacyV99();
    tidyDuplicatesV99();
    normalizeScoresV99();
    prettyDatesInCompareV99();
  }

  const oldRenderV99=window.render;
  window.render=function(){
    oldRenderV99();
    setTimeout(auditPolishV99,30);
    setTimeout(auditPolishV99,220);
    setTimeout(auditPolishV99,800);
  };

  const obsV99=new MutationObserver(function(){
    clearTimeout(window.__v99AuditTimer);
    window.__v99AuditTimer=setTimeout(auditPolishV99,45);
  });

  setTimeout(function(){
    const view=document.getElementById('view');
    if(view)obsV99.observe(view,{childList:true,subtree:true});
    auditPolishV99();
  },180);
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)
p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8").replace("team-fjz-v9-8","team-fjz-v9-9")
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V9.9 auditoria general:",len(html),"bytes")
