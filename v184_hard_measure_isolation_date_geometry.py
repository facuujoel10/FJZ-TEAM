import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V18.4 HARD STUDENT MEASUREMENT ISOLATION + EXACT DATE GEOMETRY
# =========================================================

# 1) Kill the legacy V9.3 student measure injector at its source.
needle="async function injectCompareV93(){"
count=html.count(needle)
if count!=1:
    raise RuntimeError(f"V18.4 expected exactly one injectCompareV93, got {count}")
html=html.replace(
    needle,
    "async function injectCompareV93(){\n    if(currentProfile?.role==='student')return;",
    1
)

# 2) The old V9.3 eligibility must also remain disabled for students.
html,n_student_gate=re.subn(
    r"const\s+isStudent\s*=\s*[^;]+;",
    "const isStudent=false; /* V18.4 hard-disabled legacy student measure compare */",
    html,
    count=1
)
if n_student_gate!=1:
    raise RuntimeError(f"V18.4 expected one legacy isStudent gate, got {n_student_gate}")

css=r"""
<style id="v184HardMeasureIsolationDateGeometryStyles">
/* Student measurement history belongs only to Seguimiento. */
body.v184-student-outside-tracking #v93MeasureCompare,
body.v184-student-outside-tracking .v93-compare,
body.v184-student-outside-tracking #v176MeasurementHistory,
body.v184-student-outside-tracking .v176-measure-history{
  display:none!important;
}

/* Date controls: remove native outer geometry differences while keeping
   the input type=date behavior. Runtime mirrors the adjacent peer exactly. */
#ciWeek,
#mDate,
#progressPhotoDate{
  -webkit-appearance:none!important;
  appearance:none!important;
  box-sizing:border-box!important;
  margin:0!important;
  vertical-align:middle!important;
  max-width:100%!important;
  min-width:0!important;
  overflow:hidden!important;
}

#ciWeek::-webkit-date-and-time-value,
#mDate::-webkit-date-and-time-value,
#progressPhotoDate::-webkit-date-and-time-value,
#ciWeek::-webkit-datetime-edit,
#mDate::-webkit-datetime-edit,
#progressPhotoDate::-webkit-datetime-edit,
#ciWeek::-webkit-datetime-edit-fields-wrapper,
#mDate::-webkit-datetime-edit-fields-wrapper,
#progressPhotoDate::-webkit-datetime-edit-fields-wrapper{
  display:flex!important;
  align-items:center!important;
  height:100%!important;
  min-height:0!important;
  line-height:normal!important;
  margin:0!important;
  padding:0!important;
}

#ciWeek::-webkit-calendar-picker-indicator,
#mDate::-webkit-calendar-picker-indicator,
#progressPhotoDate::-webkit-calendar-picker-indicator{
  align-self:center!important;
  margin:0 0 0 6px!important;
  padding:0!important;
  flex:0 0 auto!important;
}

/* Pair cells themselves are identical. */
.v184-exact-pair{
  display:grid!important;
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:9px!important;
  align-items:start!important;
}

.v184-exact-pair>label{
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  box-sizing:border-box!important;
  overflow:hidden!important;
}

.v184-exact-pair .v181-date-clip{
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  box-sizing:border-box!important;
  overflow:hidden!important;
}

@media(max-width:390px){
  .v184-exact-pair{
    grid-template-columns:1fr!important;
  }
}
</style>
"""

js=r"""
<script id="v184HardMeasureIsolationDateGeometryRuntime">
(function(){
  const VERSION='18.4';
  let routeObserverV184=null;

  function isStudentV184(){
    return currentProfile?.role==='student'&&mode==='student';
  }

  function isStudentTrackingV184(){
    return isStudentV184()&&studentTab==='tracking';
  }

  function purgeMeasuresV184(){
    const outside=isStudentV184()&&!isStudentTrackingV184();
    document.body?.classList.toggle('v184-student-outside-tracking',outside);
    if(!outside)return;

    [document.getElementById('view'),document.getElementById('studentSubBody')]
      .filter(Boolean)
      .forEach(root=>{
        root.querySelectorAll(
          '#v93MeasureCompare,.v93-compare,#v176MeasurementHistory,.v176-measure-history'
        ).forEach(node=>node.remove());
      });
  }

  function armRouteGuardV184(){
    routeObserverV184?.disconnect();
    routeObserverV184=null;
    if(!(isStudentV184()&&!isStudentTrackingV184()))return;

    const root=document.getElementById('view');
    if(!root)return;

    routeObserverV184=new MutationObserver(()=>{
      if(isStudentTrackingV184()){
        routeObserverV184?.disconnect();
        routeObserverV184=null;
        return;
      }
      root.querySelectorAll(
        '#v93MeasureCompare,.v93-compare,#v176MeasurementHistory,.v176-measure-history'
      ).forEach(node=>node.remove());
    });
    routeObserverV184.observe(root,{childList:true,subtree:true});
  }

  function cssValueV184(style,prop){
    return style.getPropertyValue(prop)||'';
  }

  function mirrorPeerGeometryV184(date){
    if(!date)return;
    const grid=date.closest('.form-grid');
    const label=date.closest('label');
    if(!grid||!label)return;

    grid.classList.add('v184-exact-pair');

    const peers=[...grid.querySelectorAll('input,select')]
      .filter(x=>x!==date&&x.type!=='file'&&x.type!=='hidden');
    const peer=peers[0];
    if(!peer)return;

    const cs=getComputedStyle(peer);
    const props=[
      'height','min-height','max-height',
      'padding-top','padding-right','padding-bottom','padding-left',
      'border-top-width','border-right-width','border-bottom-width','border-left-width',
      'border-top-style','border-right-style','border-bottom-style','border-left-style',
      'border-top-color','border-right-color','border-bottom-color','border-left-color',
      'border-top-left-radius','border-top-right-radius','border-bottom-right-radius','border-bottom-left-radius',
      'font-size','font-family','font-weight','letter-spacing',
      'background-color','color'
    ];

    props.forEach(prop=>{
      const value=cssValueV184(cs,prop);
      if(value)date.style.setProperty(prop,value,'important');
    });

    date.style.setProperty('box-sizing','border-box','important');
    date.style.setProperty('width','100%','important');
    date.style.setProperty('min-width','0','important');
    date.style.setProperty('max-width','100%','important');
    date.style.setProperty('margin','0','important');

    const clip=date.closest('.v181-date-clip');
    if(clip){
      const h=cssValueV184(cs,'height');
      if(h){
        clip.style.setProperty('height',h,'important');
        clip.style.setProperty('min-height',h,'important');
        clip.style.setProperty('max-height',h,'important');
      }
    }

    label.style.setProperty('min-width','0','important');
    label.style.setProperty('max-width','100%','important');
  }

  function exactDateGeometryV184(){
    ['ciWeek','mDate','progressPhotoDate'].forEach(id=>{
      document.querySelectorAll('#'+id).forEach(mirrorPeerGeometryV184);
    });
  }

  function polishV184(){
    purgeMeasuresV184();
    armRouteGuardV184();
    exactDateGeometryV184();
  }

  /* Prevent stale async callers from painting tracking history in other tabs. */
  if(typeof window.renderStudentTrackingHistory==='function'){
    const baseStudentHistoryV184=window.renderStudentTrackingHistory;
    window.renderStudentTrackingHistory=function(){
      if(isStudentV184()&&!isStudentTrackingV184()){
        purgeMeasuresV184();
        return;
      }
      const out=baseStudentHistoryV184.apply(this,arguments);
      requestAnimationFrame(exactDateGeometryV184);
      return out;
    };
    try{renderStudentTrackingHistory=window.renderStudentTrackingHistory}catch(_e){}
  }

  /* Reuse final consolidated post-render transaction. */
  const basePostV184=window.__fjzPostRenderV176;
  window.__fjzPostRenderV176=function(){
    const out=basePostV184?.apply(this,arguments);
    polishV184();
    return out;
  };

  window.addEventListener('resize',()=>{
    if(isStudentTrackingV184())requestAnimationFrame(exactDateGeometryV184);
  },{passive:true});

  requestAnimationFrame(polishV184);

  window.__fjzV184={
    version:VERSION,
    legacyMeasureInjectorStudentGuard:true,
    lateMeasureLeakGuard:true,
    trackingHistoryRouteGuard:true,
    exactDatePeerGeometry:true,
    sourceAssertionEnabled:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "v184HardMeasureIsolationDateGeometryStyles",
  "legacyMeasureInjectorStudentGuard:true",
  "lateMeasureLeakGuard:true",
  "trackingHistoryRouteGuard:true",
  "exactDatePeerGeometry:true",
  "sourceAssertionEnabled:true"
]:
    if marker not in html:
        raise RuntimeError("V18.4 missing marker: "+marker)

# Hard build guarantees: old V9.3 student compare path cannot be eligible.
if "studentTab==='progress'||studentTab==='home'" in html:
    raise RuntimeError("V18.4 legacy student measure eligibility still present")
if "async function injectCompareV93(){\n    if(currentProfile?.role==='student')return;" not in html:
    raise RuntimeError("V18.4 source guard was not injected")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V18.4 hard measurement isolation/exact date geometry enabled")
