import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V18.1 TRACKING DATE FIELD SYMMETRY
# - Check-in: Peso actual / Semana
# - Peso y medidas: Fecha / Peso
# - Fotos: Fecha / Vista
# =========================================================

css=r"""
<style id="v181TrackingDateSymmetryStyles">
/* Canonical geometry for the three tracking form pairs. */
.v181-sym-grid{
  display:grid!important;
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:9px!important;
  align-items:start!important;
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
}

.v181-sym-grid>label{
  display:flex!important;
  flex-direction:column!important;
  gap:4px!important;
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  overflow:hidden!important;
  box-sizing:border-box!important;
}

.v181-sym-grid>label>.input,
.v181-sym-grid>label>input,
.v181-sym-grid>label>select,
.v181-sym-grid .v181-date-clip{
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  box-sizing:border-box!important;
}

.v181-sym-grid input.input:not([type="file"]):not([type="checkbox"]):not([type="radio"]),
.v181-sym-grid select.input,
.v181-sym-grid select{
  min-height:42px!important;
  height:42px!important;
  max-height:42px!important;
  line-height:1.2!important;
}

.v181-date-clip{
  display:block!important;
  inline-size:100%!important;
  max-inline-size:100%!important;
  min-inline-size:0!important;
  overflow:hidden!important;
  border-radius:inherit!important;
}

#ciWeek,#mDate,#progressPhotoDate{
  display:block!important;
  inline-size:100%!important;
  width:100%!important;
  max-inline-size:100%!important;
  max-width:100%!important;
  min-inline-size:0!important;
  min-width:0!important;
  min-height:42px!important;
  height:42px!important;
  max-height:42px!important;
  margin:0!important;
  padding-left:10px!important;
  padding-right:8px!important;
  box-sizing:border-box!important;
  overflow:hidden!important;
  font-size:16px!important;
  line-height:1.2!important;
}

#ciWeek::-webkit-date-and-time-value,
#mDate::-webkit-date-and-time-value,
#progressPhotoDate::-webkit-date-and-time-value{
  display:block!important;
  inline-size:auto!important;
  width:auto!important;
  max-width:100%!important;
  min-inline-size:0!important;
  min-width:0!important;
  margin:0!important;
  padding:0!important;
  text-align:left!important;
}

#ciWeek::-webkit-calendar-picker-indicator,
#mDate::-webkit-calendar-picker-indicator,
#progressPhotoDate::-webkit-calendar-picker-indicator{
  flex:0 0 auto!important;
  margin:0!important;
  padding:2px!important;
}

@media(max-width:390px){
  .v181-sym-grid{
    grid-template-columns:1fr!important;
  }
}
</style>
"""

js=r"""
<script id="v181TrackingDateSymmetryRuntime">
(function(){
  const VERSION='18.1';
  const IDS=['ciWeek','mDate','progressPhotoDate'];

  function wrapDateV181(input){
    if(!input)return;
    const label=input.closest('label');
    const grid=input.closest('.form-grid');
    if(!label||!grid)return;

    grid.classList.add('v181-sym-grid');
    label.classList.add('v181-date-label');

    // Keep both cells in the pair constrained and visually identical.
    [...grid.children].forEach(cell=>{
      if(cell?.tagName!=='LABEL')return;
      cell.style.minWidth='0';
      cell.style.maxWidth='100%';
      cell.style.width='100%';
      cell.style.overflow='hidden';
    });

    if(!input.closest('.v181-date-clip')){
      const clip=document.createElement('span');
      clip.className='v181-date-clip';
      label.insertBefore(clip,input);
      clip.appendChild(input);
    }
  }

  function polishTrackingDatesV181(){
    IDS.forEach(id=>{
      document.querySelectorAll('#'+id).forEach(wrapDateV181);
    });
  }

  // Use the existing consolidated post-render pass: no extra render wrapper.
  const basePostV181=window.__fjzPostRenderV176;
  window.__fjzPostRenderV176=function(){
    const out=basePostV181?.apply(this,arguments);
    polishTrackingDatesV181();
    return out;
  };

  // Coach tracking body is hydrated asynchronously.
  if(typeof window.renderTrackingCoachLoaded==='function'){
    const baseCoachLoadedV181=window.renderTrackingCoachLoaded;
    window.renderTrackingCoachLoaded=function(){
      const out=baseCoachLoadedV181.apply(this,arguments);
      requestAnimationFrame(polishTrackingDatesV181);
      return out;
    };
    try{renderTrackingCoachLoaded=window.renderTrackingCoachLoaded}catch(_e){}
  }

  if(typeof window.renderStudentTrackingHistory==='function'){
    const baseStudentHistoryV181=window.renderStudentTrackingHistory;
    window.renderStudentTrackingHistory=function(){
      const out=baseStudentHistoryV181.apply(this,arguments);
      requestAnimationFrame(polishTrackingDatesV181);
      return out;
    };
    try{renderStudentTrackingHistory=window.renderStudentTrackingHistory}catch(_e){}
  }

  requestAnimationFrame(polishTrackingDatesV181);

  window.__fjzV181={
    version:VERSION,
    checkinWeekContained:true,
    measurementDateContained:true,
    progressPhotoDateContained:true,
    equalTrackingFieldGeometry:true,
    noExtraRenderWrapper:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "v181TrackingDateSymmetryStyles",
  "v181TrackingDateSymmetryRuntime",
  "checkinWeekContained:true",
  "measurementDateContained:true",
  "progressPhotoDateContained:true",
  "equalTrackingFieldGeometry:true"
]:
    if marker not in html:
        raise RuntimeError("V18.1 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V18.1 tracking date symmetry enabled")
