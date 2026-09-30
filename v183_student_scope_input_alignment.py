import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V18.3 STUDENT MEASUREMENT SCOPE + INPUT ALIGNMENT + BADGES
# =========================================================

# Legacy V9.3 comparison must never inject into student tabs anymore.
# V17.6 owns the canonical editable measurement history in Tracking.
old_student="""    const isStudent=currentProfile?.role==='student'&&(studentTab==='tracking'||studentTab==='progress'||studentTab==='home');"""
new_student="""    const isStudent=false; /* V18.3: canonical student measurements live only in Tracking (V17.6) */"""
if old_student in html:
    html=html.replace(old_student,new_student,1)

# V17.9 no longer needs to watch student Home/Progress for the legacy card.
old_watch="""    const studentRelevant=mode==='student'&&['progress','home'].includes(studentTab);"""
new_watch="""    const studentRelevant=false; /* V18.3: prevent legacy measurement card leakage across student tabs */"""
if old_watch in html:
    html=html.replace(old_watch,new_watch,1)

css=r"""
<style id="v183StudentScopeAlignmentStyles">
/* ========================================================
   Badges: short words like "Revisar" must always stay whole.
   ======================================================== */
.badge,
.v175-agenda-row-badge,
.v73-alert-badge{
  display:inline-flex!important;
  align-items:center!important;
  justify-content:center!important;
  width:auto!important;
  min-width:max-content!important;
  max-width:100%!important;
  white-space:nowrap!important;
  word-break:keep-all!important;
  overflow-wrap:normal!important;
  line-height:1!important;
  padding-left:8px!important;
  padding-right:8px!important;
  flex-shrink:0!important;
}

/* ========================================================
   Canonical 42px control geometry in Tracking.
   ======================================================== */
.v181-sym-grid>label{
  justify-content:flex-start!important;
}

.v181-sym-grid .input,
.v181-sym-grid input,
.v181-sym-grid select{
  min-height:42px!important;
  height:42px!important;
  max-height:42px!important;
  box-sizing:border-box!important;
  margin:0!important;
}

.v181-sym-grid input:not([type="file"]),
.v181-sym-grid select{
  padding-top:0!important;
  padding-bottom:0!important;
  line-height:42px!important;
}

#ciWeek,
#mDate,
#progressPhotoDate{
  display:flex!important;
  align-items:center!important;
  justify-content:flex-start!important;
  min-height:42px!important;
  height:42px!important;
  max-height:42px!important;
  padding-top:0!important;
  padding-bottom:0!important;
  line-height:42px!important;
  vertical-align:middle!important;
}

.v181-date-clip{
  display:flex!important;
  align-items:center!important;
  justify-content:stretch!important;
  min-height:42px!important;
  height:42px!important;
  max-height:42px!important;
}

/* The actual value rendered by Safari/Chrome inside a date field. */
#ciWeek::-webkit-date-and-time-value,
#mDate::-webkit-date-and-time-value,
#progressPhotoDate::-webkit-date-and-time-value{
  display:flex!important;
  align-items:center!important;
  justify-content:flex-start!important;
  height:42px!important;
  min-height:42px!important;
  line-height:42px!important;
  margin:0!important;
  padding:0!important;
  transform:none!important;
}

#ciWeek::-webkit-datetime-edit,
#mDate::-webkit-datetime-edit,
#progressPhotoDate::-webkit-datetime-edit{
  display:flex!important;
  align-items:center!important;
  height:42px!important;
  line-height:42px!important;
  padding:0!important;
}

#ciWeek::-webkit-datetime-edit-fields-wrapper,
#mDate::-webkit-datetime-edit-fields-wrapper,
#progressPhotoDate::-webkit-datetime-edit-fields-wrapper{
  display:flex!important;
  align-items:center!important;
  height:42px!important;
  padding:0!important;
}

#ciWeek::-webkit-calendar-picker-indicator,
#mDate::-webkit-calendar-picker-indicator,
#progressPhotoDate::-webkit-calendar-picker-indicator{
  align-self:center!important;
  margin:auto 0 auto 6px!important;
}

/* Match number/select neighbors visually with the date fields. */
#ciWeight,
#mWeight,
#progressPhotoPose{
  min-height:42px!important;
  height:42px!important;
  max-height:42px!important;
  padding-top:0!important;
  padding-bottom:0!important;
  line-height:42px!important;
  box-sizing:border-box!important;
}

#progressPhotoPose{
  line-height:normal!important;
}

/* No hidden legacy measurement card can affect layout outside Tracking. */
body.v183-student-nontracking #v93MeasureCompare,
body.v183-student-nontracking .v93-compare,
body.v183-student-nontracking #v176MeasurementHistory{
  display:none!important;
}
</style>
"""

js=r"""
<script id="v183StudentScopeAlignmentRuntime">
(function(){
  const VERSION='18.3';

  function studentTrackingV183(){
    return currentProfile?.role==='student'&&mode==='student'&&studentTab==='tracking';
  }

  function enforceStudentMeasurementScopeV183(){
    const isStudent=currentProfile?.role==='student'&&mode==='student';
    document.body?.classList.toggle('v183-student-nontracking',!!isStudent&&!studentTrackingV183());

    if(!isStudent||studentTrackingV183())return;

    const roots=[
      document.getElementById('view'),
      document.getElementById('studentSubBody')
    ].filter(Boolean);

    roots.forEach(root=>{
      root.querySelectorAll('#v93MeasureCompare,.v93-compare,#v176MeasurementHistory').forEach(node=>node.remove());
    });
  }

  function centerTrackingControlsV183(){
    ['ciWeek','mDate','progressPhotoDate','ciWeight','mWeight','progressPhotoPose'].forEach(id=>{
      document.querySelectorAll('#'+id).forEach(node=>{
        node.style.boxSizing='border-box';
        node.style.minHeight='42px';
        node.style.height='42px';
        node.style.maxHeight='42px';
      });
    });
  }

  function polishV183(){
    enforceStudentMeasurementScopeV183();
    centerTrackingControlsV183();
  }

  /* Run inside the consolidated post-render transaction. */
  const basePostV183=window.__fjzPostRenderV176;
  window.__fjzPostRenderV176=function(){
    const out=basePostV183?.apply(this,arguments);
    polishV183();
    return out;
  };

  /* Async student tracking load can finish after the main render. */
  if(typeof window.renderStudentTrackingHistory==='function'){
    const baseStudentHistoryV183=window.renderStudentTrackingHistory;
    window.renderStudentTrackingHistory=function(){
      const out=baseStudentHistoryV183.apply(this,arguments);
      requestAnimationFrame(polishV183);
      return out;
    };
    try{renderStudentTrackingHistory=window.renderStudentTrackingHistory}catch(_e){}
  }

  requestAnimationFrame(polishV183);

  window.__fjzV183={
    version:VERSION,
    legacyStudentMeasurementsDisabled:true,
    measurementsTrackingOnly:true,
    dateValueVerticallyCentered:true,
    trackingControlsSymmetric:true,
    reviewBadgeNoWrap:true,
    noExtraRenderWrapper:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "v183StudentScopeAlignmentStyles",
  "legacyStudentMeasurementsDisabled:true",
  "measurementsTrackingOnly:true",
  "dateValueVerticallyCentered:true",
  "reviewBadgeNoWrap:true"
]:
    if marker not in html:
        raise RuntimeError("V18.3 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V18.3 student measurement scope/alignment enabled")
