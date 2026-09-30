import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v186ExactFieldAlignmentStyles">
/* Exact label/control geometry for tracking pairs.
   Both cells always reserve the same label row and the same control row. */
.v186-field-pair{
  display:grid!important;
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:9px!important;
  align-items:start!important;
  width:100%!important;
  min-width:0!important;
}

.v186-field-pair>label{
  display:grid!important;
  grid-template-rows:14px 42px!important;
  row-gap:5px!important;
  align-items:stretch!important;
  align-content:start!important;
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  height:auto!important;
  margin:0!important;
  padding:0!important;
  line-height:14px!important;
  box-sizing:border-box!important;
  overflow:hidden!important;
}

.v186-field-pair>label>.input,
.v186-field-pair>label>input,
.v186-field-pair>label>select,
.v186-field-pair>label>.v181-date-clip{
  grid-row:2!important;
  align-self:stretch!important;
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  height:42px!important;
  min-height:42px!important;
  max-height:42px!important;
  margin:0!important;
  box-sizing:border-box!important;
}

.v186-field-pair .v181-date-clip{
  display:block!important;
  position:relative!important;
  padding:0!important;
  border:0!important;
  line-height:0!important;
  overflow:hidden!important;
}

.v186-field-pair .v181-date-clip>#ciWeek,
.v186-field-pair .v181-date-clip>#mDate,
.v186-field-pair .v181-date-clip>#progressPhotoDate,
.v186-field-pair>#ciWeek,
.v186-field-pair>#mDate,
.v186-field-pair>#progressPhotoDate{
  position:relative!important;
  top:0!important;
  bottom:auto!important;
  transform:none!important;
  display:block!important;
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  height:42px!important;
  min-height:42px!important;
  max-height:42px!important;
  margin:0!important;
  box-sizing:border-box!important;
  vertical-align:top!important;
}

/* Native date text remains centered inside the now-aligned outer box. */
.v186-field-pair input[type="date"]::-webkit-date-and-time-value,
.v186-field-pair input[type="date"]::-webkit-datetime-edit,
.v186-field-pair input[type="date"]::-webkit-datetime-edit-fields-wrapper{
  height:100%!important;
  min-height:0!important;
  margin:0!important;
  padding:0!important;
  display:flex!important;
  align-items:center!important;
  line-height:normal!important;
}

.v186-field-pair input[type="date"]::-webkit-calendar-picker-indicator{
  align-self:center!important;
  margin:0 0 0 6px!important;
  padding:0!important;
}

@media(max-width:390px){
  .v186-field-pair{
    grid-template-columns:1fr!important;
  }
}
</style>
"""

js=r"""
<script id="v186ExactFieldAlignmentRuntime">
(function(){
  const VERSION='18.6';

  function alignPairV186(id){
    document.querySelectorAll('#'+id).forEach(control=>{
      const grid=control.closest('.form-grid');
      if(!grid)return;
      grid.classList.add('v186-field-pair');

      [...grid.children].forEach(cell=>{
        if(cell?.tagName!=='LABEL')return;
        cell.style.removeProperty('height');
        cell.style.removeProperty('min-height');
        cell.style.removeProperty('max-height');
      });
    });
  }

  function alignAllV186(){
    ['ciWeek','mDate','progressPhotoDate'].forEach(alignPairV186);
  }

  const basePostV186=window.__fjzPostRenderV176;
  window.__fjzPostRenderV176=function(){
    const out=basePostV186?.apply(this,arguments);
    alignAllV186();
    return out;
  };

  if(typeof window.renderTrackingCoachLoaded==='function'){
    const baseCoachV186=window.renderTrackingCoachLoaded;
    window.renderTrackingCoachLoaded=function(){
      const out=baseCoachV186.apply(this,arguments);
      requestAnimationFrame(alignAllV186);
      return out;
    };
    try{renderTrackingCoachLoaded=window.renderTrackingCoachLoaded}catch(_e){}
  }

  if(typeof window.renderStudentTrackingHistory==='function'){
    const baseStudentV186=window.renderStudentTrackingHistory;
    window.renderStudentTrackingHistory=function(){
      const out=baseStudentV186.apply(this,arguments);
      requestAnimationFrame(alignAllV186);
      return out;
    };
    try{renderStudentTrackingHistory=window.renderStudentTrackingHistory}catch(_e){}
  }

  requestAnimationFrame(alignAllV186);

  window.__fjzV186={
    version:VERSION,
    exactTrackingFieldAlignment:true,
    equalLabelRows:true,
    equalControlRows:true,
    dateWrapperOffsetNeutralized:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "v186ExactFieldAlignmentStyles",
  "exactTrackingFieldAlignment:true",
  "equalLabelRows:true",
  "equalControlRows:true",
  "dateWrapperOffsetNeutralized:true"
]:
    if marker not in html:
        raise RuntimeError("V18.6 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V18.6 exact tracking field alignment enabled")
