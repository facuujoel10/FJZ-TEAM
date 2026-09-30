import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v187PairedTrackingGridStyles">
/* =========================================================
   V18.7 · TRACKING FORMS: STRICT 2-BY-2 SYMMETRY
   ========================================================= */
.v187-pair-grid{
  display:grid!important;
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:10px!important;
  align-items:start!important;
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  box-sizing:border-box!important;
}

.v187-pair-grid>label{
  display:flex!important;
  flex-direction:column!important;
  justify-content:flex-start!important;
  gap:5px!important;
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  height:61px!important;
  min-height:61px!important;
  max-height:61px!important;
  margin:0!important;
  padding:0!important;
  line-height:14px!important;
  box-sizing:border-box!important;
  overflow:hidden!important;
}

.v187-pair-grid>label.span2{
  grid-column:1 / -1!important;
  width:100%!important;
}

.v187-pair-grid>label>.input,
.v187-pair-grid>label>input,
.v187-pair-grid>label>select,
.v187-pair-grid>label>.v181-date-clip{
  display:block!important;
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  height:42px!important;
  min-height:42px!important;
  max-height:42px!important;
  margin:0!important;
  box-sizing:border-box!important;
  flex:0 0 42px!important;
}

.v187-pair-grid>label>.v181-date-clip{
  padding:0!important;
  border:0!important;
  overflow:hidden!important;
  line-height:0!important;
}

.v187-pair-grid>label>.v181-date-clip>input[type="date"]{
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  height:42px!important;
  min-height:42px!important;
  max-height:42px!important;
  margin:0!important;
  box-sizing:border-box!important;
  position:static!important;
  top:auto!important;
  transform:none!important;
}

.v187-pair-grid input[type="number"],
.v187-pair-grid input[type="date"],
.v187-pair-grid select{
  padding-top:0!important;
  padding-bottom:0!important;
}

.v187-pair-grid input[type="date"]::-webkit-date-and-time-value,
.v187-pair-grid input[type="date"]::-webkit-datetime-edit,
.v187-pair-grid input[type="date"]::-webkit-datetime-edit-fields-wrapper{
  display:flex!important;
  align-items:center!important;
  height:100%!important;
  min-height:0!important;
  margin:0!important;
  padding:0!important;
  line-height:normal!important;
}

.v187-pair-grid input[type="date"]::-webkit-calendar-picker-indicator{
  align-self:center!important;
  flex:0 0 auto!important;
  margin:0 0 0 6px!important;
  padding:0!important;
}

.v187-pair-grid input[type="file"]{
  height:42px!important;
  min-height:42px!important;
  max-height:42px!important;
  line-height:normal!important;
}

/* Explicitly defeat older mobile rules that stacked these grids. */
@media(max-width:900px){
  .v187-pair-grid{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
  }
}
@media(max-width:390px){
  .v187-pair-grid{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:8px!important;
  }
}
</style>
"""

js=r"""
<script id="v187PairedTrackingGridRuntime">
(function(){
  const VERSION='18.7';

  const GROUPS=[
    ['ciWeight','ciWeek'],
    ['mDate','mWeight','mWaist','mAbd','mHip','mChest'],
    ['progressPhotoDate','progressPhotoPose','progressPhotoFile']
  ];

  function markGridFromIdV187(id){
    document.querySelectorAll('#'+id).forEach(node=>{
      const grid=node.closest('.form-grid');
      if(!grid)return;
      grid.classList.add('v187-pair-grid');

      [...grid.children].forEach(cell=>{
        if(cell?.tagName!=='LABEL')return;
        cell.style.removeProperty('height');
        cell.style.removeProperty('min-height');
        cell.style.removeProperty('max-height');
        cell.style.removeProperty('width');
      });
    });
  }

  function applyV187(){
    GROUPS.flat().forEach(markGridFromIdV187);
  }

  const basePostV187=window.__fjzPostRenderV176;
  window.__fjzPostRenderV176=function(){
    const out=basePostV187?.apply(this,arguments);
    applyV187();
    return out;
  };

  if(typeof window.renderTrackingCoachLoaded==='function'){
    const baseCoachV187=window.renderTrackingCoachLoaded;
    window.renderTrackingCoachLoaded=function(){
      const out=baseCoachV187.apply(this,arguments);
      requestAnimationFrame(applyV187);
      return out;
    };
    try{renderTrackingCoachLoaded=window.renderTrackingCoachLoaded}catch(_e){}
  }

  if(typeof window.renderStudentTrackingHistory==='function'){
    const baseStudentV187=window.renderStudentTrackingHistory;
    window.renderStudentTrackingHistory=function(){
      const out=baseStudentV187.apply(this,arguments);
      requestAnimationFrame(applyV187);
      return out;
    };
    try{renderStudentTrackingHistory=window.renderStudentTrackingHistory}catch(_e){}
  }

  requestAnimationFrame(applyV187);

  window.__fjzV187={
    version:VERSION,
    strictTwoColumnTracking:true,
    equalFieldWidth:true,
    equalFieldHeight:true,
    equalLabelHeight:true,
    mobileKeepsTwoColumns:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "v187PairedTrackingGridStyles",
  "strictTwoColumnTracking:true",
  "equalFieldWidth:true",
  "equalFieldHeight:true",
  "mobileKeepsTwoColumns:true"
]:
    if marker not in html:
        raise RuntimeError("V18.7 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V18.7 strict 2-by-2 tracking symmetry enabled")
