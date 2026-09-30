import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# V17.7: stable mobile viewport, hard containment for native date/time inputs,
# and non-destructive measurement-history refresh.

css=r"""
<style id="v177MobileStabilityMeasurementStyles">
html,body{
  width:100%!important;
  max-width:100%!important;
  overflow-x:hidden!important;
  overscroll-behavior-x:none!important;
}
#view,#coachStudentBody,#studentSubBody,.shell{
  min-width:0!important;
  max-width:100%!important;
  box-sizing:border-box!important;
}
input[type="date"],input[type="time"]{
  display:block!important;
  width:100%!important;
  max-width:100%!important;
  min-width:0!important;
  min-inline-size:0!important;
  box-sizing:border-box!important;
  overflow:hidden!important;
}
input[type="date"]::-webkit-date-and-time-value,
input[type="time"]::-webkit-date-and-time-value{
  min-width:0!important;
  width:100%!important;
  text-align:left!important;
}
#ciWeek,#mDate,#progressPhotoDate,#nutritionLogDate,
#v165Time,#v165Date,
.v165-week-row input[type="time"],
.v165-week-row input[type="date"]{
  width:100%!important;
  max-width:100%!important;
  min-width:0!important;
  min-inline-size:0!important;
  box-sizing:border-box!important;
  overflow:hidden!important;
}
.v165-week-row,.v165-week-row>*,
.form-grid,.form-grid>*,
.tracking-form,.tracking-form>*{
  min-width:0!important;
  max-width:100%;
  box-sizing:border-box;
}
@media(max-width:900px){
  /* 100dvh changes while mobile browser chrome opens/closes and causes visible jumps. */
  #view,
  body.v158-rendering #view{
    min-height:calc(100svh - 128px)!important;
  }
  #coachStudentBody,#studentSubBody{
    min-height:calc(100svh - 170px)!important;
  }
  .shell{
    width:100%!important;
    max-width:100vw!important;
    overflow-x:hidden!important;
  }
  .card,.hero,.modal,.student-row,.exercise-row,.day-card,.history-item{
    max-width:100%!important;
    min-width:0!important;
    box-sizing:border-box!important;
  }
}
@media(max-width:520px){
  input[type="date"],input[type="time"]{
    font-size:16px!important;
    padding-left:10px!important;
    padding-right:8px!important;
  }
  .v176-measure-row{
    grid-template-columns:1fr!important;
  }
  .v176-measure-row>.btn{
    width:100%!important;
  }
}
</style>
"""

# Replace V17.6 measurement injection with a stable upsert. It no longer removes
# and recreates the card on every tracking render when the data did not change.
old=r"""  function injectMeasurementHistoryV176(){
    let host=null,anchor=null;
    if(studentTrackingActiveV176()){
      host=el('trackingStudentHistory');
      if(!host)return;
      cleanupLegacyMeasurementEvolutionV176(host);
      el('v176MeasurementHistory')?.remove();
      host.insertAdjacentHTML('beforeend',measurementHistoryHtmlV176());
      return;
    }
    if(coachTrackingActiveV176()){
      host=el('coachStudentBody');
      if(!host)return;
      cleanupLegacyMeasurementEvolutionV176(host);
      el('v176MeasurementHistory')?.remove();
      anchor=el('coachPhotoGrid')?.closest('.card')||null;
      if(anchor)anchor.insertAdjacentHTML('beforebegin',measurementHistoryHtmlV176());
      else host.insertAdjacentHTML('beforeend',measurementHistoryHtmlV176());
    }
  }"""

new=r"""  function injectMeasurementHistoryV176(){
    let host=null,anchor=null;
    if(studentTrackingActiveV176()){
      host=el('trackingStudentHistory');
    }else if(coachTrackingActiveV176()){
      host=el('coachStudentBody');
      anchor=el('coachPhotoGrid')?.closest('.card')||null;
    }else return;
    if(!host)return;

    cleanupLegacyMeasurementEvolutionV176(host);
    const rows=(trackingCache?.measurements||[]).slice(0,12);
    const signature=rows.map(x=>[
      x.id,x.measured_on,x.updated_at,x.weight_kg,x.waist_cm,x.hip_cm,
      x.chest_cm,x.arm_left_cm,x.thigh_left_cm
    ].join(':')).join('|');

    const existing=host.querySelector('#v176MeasurementHistory')||el('v176MeasurementHistory');
    if(existing&&existing.dataset.v177Signature===signature)return;

    const tmp=document.createElement('div');
    tmp.innerHTML=measurementHistoryHtmlV176();
    const card=tmp.firstElementChild;
    if(!card)return;
    card.dataset.v177Signature=signature;

    if(existing&&existing.isConnected){
      existing.replaceWith(card);
      return;
    }
    if(anchor&&anchor.isConnected)anchor.insertAdjacentElement('beforebegin',card);
    else host.appendChild(card);
  }"""

if old not in html:
    raise RuntimeError("V17.7 could not locate V17.6 measurement injector")
html=html.replace(old,new,1)

js=r"""
<script id="v177MobileStabilityMeasurementRuntime">
(function(){
  const VERSION='17.7';
  let repairQueued=false;

  function trackingActiveV177(){
    return (mode==='student'&&studentTab==='tracking') ||
      (mode==='coach'&&coachTab==='student'&&coachStudentTab==='tracking');
  }

  function ensureMeasurementEditV177(){
    if(!trackingActiveV177())return;
    const card=document.getElementById('v176MeasurementHistory');
    const rows=(trackingCache?.measurements||[]);
    if(!card||!rows.length)return;

    const domRows=[...card.querySelectorAll('.v176-measure-row')];
    domRows.forEach((row,i)=>{
      if(row.querySelector('button[onclick*="openEditMeasurementV176"]'))return;
      const m=rows[i];
      if(!m?.id)return;
      const b=document.createElement('button');
      b.type='button';
      b.className='btn small v176-nowrap-btn';
      b.textContent='Editar';
      b.onclick=()=>window.openEditMeasurementV176?.(m.id);
      row.appendChild(b);
    });
  }

  function hardContainNativeInputsV177(){
    if(window.innerWidth>900)return;
    document.querySelectorAll('input[type="date"],input[type="time"]').forEach(x=>{
      x.style.minWidth='0';
      x.style.maxWidth='100%';
      x.style.width='100%';
      x.style.boxSizing='border-box';
      const parent=x.parentElement;
      if(parent){
        parent.style.minWidth='0';
        parent.style.maxWidth='100%';
      }
    });
  }

  function repairV177(){
    repairQueued=false;
    hardContainNativeInputsV177();
    ensureMeasurementEditV177();
  }

  function queueRepairV177(){
    if(repairQueued)return;
    repairQueued=true;
    requestAnimationFrame(repairV177);
  }

  // One post-render repair frame only. No MutationObserver and no repeating timer.
  if(typeof render==='function'){
    const baseRenderV177=render;
    render=function(){
      const out=baseRenderV177.apply(this,arguments);
      queueRepairV177();
      return out;
    };
  }

  if(typeof renderStudentTrackingHistory==='function'){
    const baseStudentHistoryV177=renderStudentTrackingHistory;
    renderStudentTrackingHistory=function(){
      const out=baseStudentHistoryV177.apply(this,arguments);
      queueRepairV177();
      return out;
    };
    try{window.renderStudentTrackingHistory=renderStudentTrackingHistory}catch(_e){}
  }

  if(typeof renderTrackingCoachLoaded==='function'){
    const baseCoachTrackingV177=renderTrackingCoachLoaded;
    renderTrackingCoachLoaded=function(){
      const out=baseCoachTrackingV177.apply(this,arguments);
      queueRepairV177();
      return out;
    };
    try{window.renderTrackingCoachLoaded=renderTrackingCoachLoaded}catch(_e){}
  }

  window.addEventListener('resize',queueRepairV177,{passive:true});
  window.addEventListener('orientationchange',queueRepairV177,{passive:true});
  queueRepairV177();

  window.__fjzMobileStabilityV177={
    version:VERSION,
    stableViewport:true,
    nativeInputContainment:true,
    measurementEditRepair:true,
    repeatingObservers:false
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "v177MobileStabilityMeasurementStyles",
  "__fjzMobileStabilityV177",
  "stableViewport:true",
  "measurementEditRepair:true",
  "100svh"
]:
    if marker not in html:
        raise RuntimeError("V17.7 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V17.7 mobile stability + measurement edit hardening enabled")
