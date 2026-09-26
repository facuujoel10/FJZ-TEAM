import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")
html=html.replace("TEAM FJZ V9.7","TEAM FJZ V9.8")

css=r"""
<style id="v98PrecisionPolish">
/* V9.8 · pulido visual final y simetría */

/* Elementos base */
.input,
input.input,
select.input,
textarea.input{
  box-sizing:border-box!important;
  max-width:100%!important;
}
input.input:not([type="file"]):not([type="checkbox"]):not([type="radio"]),
select.input{
  min-height:42px!important;
  height:42px!important;
  padding-top:0!important;
  padding-bottom:0!important;
}
textarea.input{
  min-height:92px!important;
  resize:vertical;
}
.btn{
  box-sizing:border-box;
}
.section-title{
  display:flex!important;
  align-items:flex-start!important;
  justify-content:space-between!important;
  gap:12px!important;
}
.section-title>div:first-child{
  min-width:0;
}
.section-title h3{
  line-height:1.25!important;
}
.card{
  box-sizing:border-box!important;
}

/* Check-in: todos exactamente iguales.
   Resetea reglas heredadas que hacían Recuperación de ancho completo en móvil. */
#studentSubBody .tracking-grid,
#studentSubBody .v701-checkin-scores{
  display:grid!important;
  grid-template-columns:repeat(7,minmax(0,1fr))!important;
  gap:9px!important;
  align-items:stretch!important;
}
#studentSubBody .tracking-grid>.track-score,
#studentSubBody .v701-checkin-scores>.track-score{
  grid-column:auto!important;
  grid-row:auto!important;
  min-width:0!important;
  width:100%!important;
  min-height:102px!important;
  height:102px!important;
  padding:11px!important;
  border-radius:12px!important;
  display:flex!important;
  flex-direction:column!important;
  justify-content:space-between!important;
  align-self:stretch!important;
  box-sizing:border-box!important;
}
#studentSubBody .tracking-grid>.track-score label,
#studentSubBody .v701-checkin-scores>.track-score label{
  display:flex!important;
  align-items:center!important;
  min-height:30px!important;
  height:30px!important;
  margin:0 0 7px!important;
  line-height:1.15!important;
  font-size:10px!important;
}
#studentSubBody .tracking-grid>.track-score input,
#studentSubBody .v701-checkin-scores>.track-score input{
  min-height:40px!important;
  height:40px!important;
  width:100%!important;
  margin:0!important;
  text-align:center!important;
  font-variant-numeric:tabular-nums;
}
@media(max-width:1100px){
  #studentSubBody .tracking-grid,
  #studentSubBody .v701-checkin-scores{
    grid-template-columns:repeat(4,minmax(0,1fr))!important;
  }
}
@media(max-width:700px){
  #studentSubBody .tracking-grid,
  #studentSubBody .v701-checkin-scores{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:8px!important;
  }
  #studentSubBody .tracking-grid>.track-score,
  #studentSubBody .v701-checkin-scores>.track-score{
    grid-column:auto!important;
    width:100%!important;
    min-height:98px!important;
    height:98px!important;
  }
}
@media(max-width:360px){
  #studentSubBody .tracking-grid,
  #studentSubBody .v701-checkin-scores{
    grid-template-columns:1fr!important;
  }
}

/* Formularios: mismos ritmos y alturas */
.tracking-form .form-grid,
.form-grid{
  align-items:end!important;
}
.form-grid>label{
  min-width:0!important;
}
.form-grid>label>.input,
.form-grid>label>input,
.form-grid>label>select{
  margin-top:5px!important;
}

/* KPIs, perfiles, macros y paneles */
.grid.kpi,
.metric-grid,
.summary-grid,
.v72-progress-kpis,
.v81-agenda-kpis,
.v96-alert-summary{
  align-items:stretch!important;
}
.grid.kpi>.card,
.metric-grid>*,
.summary-grid>*,
.v72-progress-kpi,
.v81-agenda-kpi,
.v96-alert-kpi{
  height:100%!important;
  min-height:86px!important;
  display:flex!important;
  flex-direction:column!important;
  justify-content:center!important;
  box-sizing:border-box!important;
}

.v86-profile-grid{
  grid-auto-rows:1fr!important;
  align-items:stretch!important;
}
.v86-profile-field{
  height:100%!important;
  min-height:72px!important;
  padding:10px 11px!important;
  justify-content:center!important;
}

.nutrition-targets{
  align-items:stretch!important;
}
.nutrition-targets>.macro-card{
  height:100%!important;
  min-height:92px!important;
  display:flex!important;
  flex-direction:column!important;
  justify-content:center!important;
  box-sizing:border-box!important;
}

/* Rutina / calentamiento / cardio */
.v94-day-tools{
  grid-auto-rows:auto;
}
.v94-guide-box{
  width:100%!important;
  box-sizing:border-box!important;
}
.v94-guide-head{
  min-height:38px!important;
}
.v94-guide-item{
  min-height:48px!important;
  box-sizing:border-box!important;
}

/* Seguimiento */
.v93-measure-row{
  min-height:45px!important;
  box-sizing:border-box!important;
}
.v94-chart{
  min-height:265px!important;
  box-sizing:border-box!important;
}
.v94-chart svg{
  height:190px!important;
}

/* Alertas */
.v96-alert-card{
  min-height:72px!important;
  box-sizing:border-box!important;
}
.v96-alert-kpi{
  min-height:78px!important;
}
.v96-notice-item{
  min-height:58px!important;
  box-sizing:border-box!important;
}

/* Recetas */
.v70-recipe-grid{
  align-items:stretch!important;
}
.v70-recipe-card{
  height:100%!important;
  display:flex!important;
  flex-direction:column!important;
  box-sizing:border-box!important;
}

/* Fotos */
.photo-grid{
  align-items:stretch!important;
}
.photo-card,
.photo-slot{
  height:100%!important;
  box-sizing:border-box!important;
}

/* Evita overflow y pequeñas desalineaciones en móvil */
@media(max-width:760px){
  .card,.hero,.track-row,.v93-measure-row,.v94-guide-box,.v96-alert-card{
    max-width:100%!important;
  }
  .section-title{
    flex-wrap:wrap!important;
  }
  .section-title>.badge,
  .section-title>.btn{
    flex:0 0 auto;
  }
}
</style>
"""

js=r"""
<script id="v98PrecisionPolishRuntime">
(function(){
  function removeDuplicateIdsV98(id){
    const nodes=[...document.querySelectorAll('#'+id)];
    nodes.slice(1).forEach(n=>n.remove());
  }

  function normalizeCheckinV98(){
    const grid=document.querySelector('#studentSubBody .tracking-grid, #studentSubBody .v701-checkin-scores');
    if(!grid)return;

    ['ciSleep','ciStress','ciEnergy','ciAdh','ciMood','ciMotivation','ciRecovery'].forEach(function(id){
      const inputs=[...document.querySelectorAll('#'+id)];
      inputs.slice(1).forEach(function(input){
        const card=input.closest('.track-score');
        if(card)card.remove(); else input.remove();
      });
      const input=document.getElementById(id);
      if(input){
        input.min='1';input.max='10';input.step='1';input.inputMode='numeric';
        const card=input.closest('.track-score');
        if(card){
          card.style.gridColumn='auto';
          card.style.width='100%';
        }
      }
    });

    const order=['ciSleep','ciStress','ciEnergy','ciAdh','ciMood','ciMotivation','ciRecovery'];
    order.forEach(function(id){
      const card=document.getElementById(id)?.closest('.track-score');
      if(card)grid.appendChild(card);
    });
  }

  function cleanupKnownDuplicatesV98(){
    ['v93MeasureCompare','v96CoachAlerts','v96StudentPreview','v94SuppCoach','v94SuppStudent','v86StudentProfileCard','v86CoachProfile','v93CoachPhotoUploader'].forEach(removeDuplicateIdsV98);
    normalizeCheckinV98();
  }

  function polishV98(){
    cleanupKnownDuplicatesV98();

    document.querySelectorAll('.form-grid').forEach(function(grid){
      grid.querySelectorAll(':scope > label').forEach(function(label){
        label.style.minWidth='0';
      });
    });

    document.querySelectorAll('.v86-profile-grid').forEach(function(grid){
      const fields=[...grid.children].filter(x=>x.classList.contains('v86-profile-field'));
      fields.forEach(f=>f.style.minHeight='72px');
    });
  }

  const oldRenderV98=window.render;
  window.render=function(){
    oldRenderV98();
    setTimeout(polishV98,40);
    setTimeout(polishV98,250);
    setTimeout(polishV98,850);
  };

  const observerV98=new MutationObserver(function(){
    clearTimeout(window.__v98PolishTimer);
    window.__v98PolishTimer=setTimeout(polishV98,35);
  });

  setTimeout(function(){
    const view=document.getElementById('view');
    if(view)observerV98.observe(view,{childList:true,subtree:true});
    polishV98();
  },200);
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)
p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8").replace("team-fjz-v9-7","team-fjz-v9-8")
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V9.8 precision UI:",len(html),"bytes")
