import pathlib,re,json
from html.parser import HTMLParser
from collections import Counter

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V18.5 PRODUCTION RUNTIME CONSOLIDATION / PERFORMANCE AUDIT
# =========================================================

def metrics(doc):
    return {
      "bytes":len(doc.encode("utf-8")),
      "scripts":len(re.findall(r"<script\b",doc,re.I)),
      "styles":len(re.findall(r"<style\b",doc,re.I)),
      "render_assignments":len(re.findall(r"(?:window\.)?render\s*=\s*function",doc)),
      "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
      "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
      "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
      "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
      "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
    }

before=metrics(html)

def edit_script(doc, ident, transform):
    pat=re.compile(r'(<script id=["\']'+re.escape(ident)+r'["\']>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m:return doc,0
    body=transform(m.group(2))
    return doc[:m.start()]+m.group(1)+body+m.group(3)+doc[m.end():],1

def remove_script(doc, ident):
    pat=re.compile(r'\s*<script id=["\']'+re.escape(ident)+r'["\']>.*?</script>\s*',re.S|re.I)
    return pat.subn("\n",doc,count=1)

removed_runtime=[]

# ---------------------------------------------------------
# A) Remove legacy UI/check-in runtimes fully superseded by
#    V17.2 canonical profile/check-in rendering.
# ---------------------------------------------------------
for ident in [
    "v87PolishRuntime",
    "v88Runtime",
    "v90MotivationFix",
    "v91CheckinClamp",
]:
    html,n=remove_script(html,ident)
    if n: removed_runtime.append(ident)

# These four recent runtimes are consolidated below into one pass.
for ident in [
    "v181TrackingDateSymmetryRuntime",
    "v182GeometryCoachDashboardRuntime",
    "v183StudentScopeAlignmentRuntime",
    "v184HardMeasureIsolationDateGeometryRuntime",
]:
    html,n=remove_script(html,ident)
    if n: removed_runtime.append(ident)

# ---------------------------------------------------------
# B) Export useful legacy tasks and remove their general
#    render wrappers / mutation observers. Functionality is
#    preserved in one V18.5 post-render pass.
# ---------------------------------------------------------

def t86(b):
    marker="  var renderV86Base=window.render;"
    if marker in b and "__fjzPostV86" not in b:
        b=b.replace(marker,
            "  window.__fjzPostV86=function(){injectStudentProfileV86();injectCoachProfileV86();};\n\n"+marker,1)
    b,_=re.subn(
        r"""  var renderV86Base=window\.render;\s*window\.render=function\(\)\{\s*renderV86Base\(\);\s*setTimeout\(function\(\)\{injectStudentProfileV86\(\);injectCoachProfileV86\(\);\},140\);\s*setTimeout\(function\(\)\{injectCoachProfileV86\(\);\},700\);\s*\};""",
        "",b,count=1,flags=re.S)
    return b
html,n86=edit_script(html,"v86Runtime",t86)

def strip_general_v92(b):
    b,_=re.subn(
        r"""  const oldRenderV92=window\.render;\s*window\.render=function\(\)\{\s*oldRenderV92\(\);\s*setTimeout\(injectCoachPhotoUploaderV92,120\);\s*setTimeout\(injectCoachPhotoUploaderV92,700\);\s*\};""",
        "",b,count=1,flags=re.S)
    return b
html,n92=edit_script(html,"v92CoachPhotoUploadRuntime",strip_general_v92)

def strip_general_v93(b):
    b,_=re.subn(
        r"""  const oldRenderV93=window\.render;\s*window\.render=function\(\)\{\s*oldRenderV93\(\);\s*setTimeout\(injectToolsV93,120\);\s*setTimeout\(injectToolsV93,700\);\s*\};""",
        "",b,count=1,flags=re.S)
    return b
html,n93=edit_script(html,"v93ProgressToolsRuntime",strip_general_v93)

def t94nutrition(b):
    marker="  const oldRenderV94=window.render;"
    if marker in b and "__fjzPostRenderV94" not in b:
        b=b.replace(marker,"  window.__fjzPostRenderV94=polishAllV94;\n\n"+marker,1)
    b,_=re.subn(
        r"""  const oldRenderV94=window\.render;\s*window\.render=function\(\)\{oldRenderV94\(\);setTimeout\(polishAllV94,60\);setTimeout\(polishAllV94,500\);setTimeout\(polishAllV94,1100\)\};""",
        "",b,count=1,flags=re.S)
    b,_=re.subn(
        r"""  const obs=new MutationObserver\(function\(\)\{cleanMeasureCompareV94\(\);normalizeMeasureFormV94\(\)\}\);\s*setTimeout\(function\(\)\{const v=el\('view'\);if\(v\)obs\.observe\(v,\{childList:true,subtree:true\}\);polishAllV94\(\)\},150\);""",
        "",b,count=1,flags=re.S)
    return b
html,n94n=edit_script(html,"v94NutritionTrackingRuntime",t94nutrition)

def t94training(b):
    marker="  const oldRenderTrainingV94=window.render;"
    post="""  window.__fjzPostTrainingV94=function(){
    loadExerciseLibraryCloudV95();
    enhanceRoutineEditorV94();
    injectWorkoutGuideV94();
  };

"""
    if marker in b and "__fjzPostTrainingV94" not in b:
        b=b.replace(marker,post+marker,1)
    b,_=re.subn(
        r"""  const oldRenderTrainingV94=window\.render;\s*window\.render=function\(\)\{\s*oldRenderTrainingV94\(\);\s*setTimeout\(function\(\)\{loadExerciseLibraryCloudV95\(\);enhanceRoutineEditorV94\(\);injectWorkoutGuideV94\(\)\},80\);\s*setTimeout\(function\(\)\{loadExerciseLibraryCloudV95\(\);enhanceRoutineEditorV94\(\);injectWorkoutGuideV94\(\)\},500\);\s*\};""",
        "",b,count=1,flags=re.S)
    b,_=re.subn(
        r"""\s*setTimeout\(function\(\)\{loadExerciseLibraryCloudV95\(\);enhanceRoutineEditorV94\(\);injectWorkoutGuideV94\(\)\},200\);""",
        "\n",b,count=1,flags=re.S)
    return b
html,n94t=edit_script(html,"v94TrainingProRuntime",t94training)

def t96(b):
    marker="  const oldRenderV96=window.render;"
    if marker in b and "__fjzInjectAlertsV96" not in b:
        b=b.replace(marker,"  window.__fjzInjectAlertsV96=injectAlertsV96;\n\n"+marker,1)
    # V12.5 transformed form.
    b,_=re.subn(
        r"""  const oldRenderV96=window\.render;\s*window\.render=function\(\)\{\s*const out=oldRenderV96\.apply\(this,arguments\);\s*fjzPostRenderV125\('alerts-v96',injectAlertsV96\);\s*return out;\s*\};""",
        "",b,count=1,flags=re.S)
    # Fallback / V17.2 form.
    b,_=re.subn(
        r"""  const oldRenderV96=window\.render;\s*window\.render=function\(\)\{\s*oldRenderV96\(\);.*?\s*\};""",
        "",b,count=1,flags=re.S)
    return b
html,n96=edit_script(html,"v96AlertCenterRuntime",t96)

def t97(b):
    marker="  const oldRenderV97=window.render;"
    if marker in b and "__fjzRunV97" not in b:
        b=b.replace(marker,"  window.__fjzRunV97=runV97;\n\n"+marker,1)
    b,_=re.subn(
        r"""  const oldRenderV97=window\.render;\s*window\.render=function\(\)\{\s*oldRenderV97\(\);\s*setTimeout\(runV97,100\);\s*setTimeout\(injectExtrasV97,700\);\s*\};""",
        "",b,count=1,flags=re.S)
    b=b.replace("  setTimeout(runV97,250);","")
    return b
html,n97=edit_script(html,"v97MigrationProfileRuntime",t97)

def t98(b):
    marker="  const oldRenderV98=window.render;"
    if marker in b and "__fjzPolishV98" not in b:
        b=b.replace(marker,"  window.__fjzPolishV98=polishV98;\n\n"+marker,1)
    b,_=re.subn(
        r"""  const oldRenderV98=window\.render;\s*window\.render=function\(\)\{\s*const out=oldRenderV98\.apply\(this,arguments\);\s*fjzPostRenderV125\('polish-v98',polishV98\);\s*return out;\s*\};""",
        "",b,count=1,flags=re.S)
    b,_=re.subn(
        r"""  const observerV98=new MutationObserver\(function\(\)\{\s*fjzPostRenderV125\('polish-v98',polishV98\);\s*\}\);\s*fjzPostRenderV125\('polish-v98-init',function\(\)\{\s*const view=document\.getElementById\('view'\);\s*if\(view\)observerV98\.observe\(view,\{childList:true,subtree:true\}\);\s*polishV98\(\);\s*\}\);""",
        "",b,count=1,flags=re.S)
    return b
html,n98=edit_script(html,"v98PrecisionPolishRuntime",t98)

def t99(b):
    marker="  const oldRenderV99=window.render;"
    if marker in b and "__fjzAuditV99" not in b:
        b=b.replace(marker,"  window.__fjzAuditV99=auditPolishV99;\n\n"+marker,1)
    b,_=re.subn(
        r"""  const oldRenderV99=window\.render;\s*window\.render=function\(\)\{\s*const out=oldRenderV99\.apply\(this,arguments\);\s*fjzPostRenderV125\('audit-v99',auditPolishV99\);\s*return out;\s*\};""",
        "",b,count=1,flags=re.S)
    b,_=re.subn(
        r"""  const obsV99=new MutationObserver\(function\(\)\{\s*fjzPostRenderV125\('audit-v99',auditPolishV99\);\s*\}\);\s*fjzPostRenderV125\('audit-v99-init',function\(\)\{\s*const view=document\.getElementById\('view'\);\s*if\(view\)obsV99\.observe\(view,\{childList:true,subtree:true\}\);\s*auditPolishV99\(\);\s*\}\);""",
        "",b,count=1,flags=re.S)
    return b
html,n99=edit_script(html,"v99AuditRuntime",t99)

def t100(b):
    marker="  const previousRender=window.render;"
    if marker in b and "__fjzCorePolishV100" not in b:
        b=b.replace(marker,"  window.__fjzCorePolishV100=polish;\n\n"+marker,1)
    b,_=re.subn(
        r"""  const previousRender=window\.render;\s*window\.render=function\(\)\{\s*const out=previousRender\.apply\(this,arguments\);\s*fjzPostRenderV125\('core-polish-v100',polish\);\s*return out;\s*\};""",
        "",b,count=1,flags=re.S)
    b,_=re.subn(
        r"""  const observer=new MutationObserver\(\(\)=>\{\s*fjzPostRenderV125\('core-polish-v100',polish\);\s*\}\);\s*fjzPostRenderV125\('core-polish-v100-init',\(\)=>\{\s*const view=document\.getElementById\('view'\);\s*if\(view\)observer\.observe\(view,\{childList:true,subtree:true\}\);\s*polish\(\);\s*\}\);""",
        "",b,count=1,flags=re.S)
    return b
html,n100=edit_script(html,"v100CoreRuntime",t100)

def t101(b):
    marker="  const oldRender=window.render;"
    if marker in b and "__fjzAvatarAdjustV101" not in b:
        b=b.replace(marker,"  window.__fjzAvatarAdjustV101=inject;\n\n"+marker,1)
    b,_=re.subn(
        r"""  const oldRender=window\.render;\s*window\.render=function\(\)\{const out=oldRender\.apply\(this,arguments\);fjzPostRenderV125\('avatar-adjust-v101',inject\);return out\};""",
        "",b,count=1,flags=re.S)
    return b
html,n101=edit_script(html,"v101AvatarAdjustRuntime",t101)

def t110(b):
    marker="  const baseRenderV110=window.render;"
    if marker in b and "__fjzAlertsPolishV110" not in b:
        b=b.replace(marker,"  window.__fjzAlertsPolishV110=polishCoachAlertsV110;\n\n"+marker,1)
    b,_=re.subn(
        r"""  const baseRenderV110=window\.render;\s*window\.render=function\(\)\{\s*const out=baseRenderV110\.apply\(this,arguments\);\s*fjzPostRenderV125\('alerts-polish-v110',polishCoachAlertsV110\);\s*return out;\s*\};""",
        "",b,count=1,flags=re.S)
    return b
html,n110=edit_script(html,"v110FinalRuntime",t110)

# ---------------------------------------------------------
# C) Remove production-only diagnostics that scan/observe
#    layout but do not provide user functionality.
# ---------------------------------------------------------
html,n_perf=re.subn(
    r"""  if\('PerformanceObserver' in window\)\{.*?\n  \}\n\n  window\.__fjzFluidityV158=stats;""",
    "  stats.layoutShift=0;\n\n  window.__fjzFluidityV158=stats;",
    html,count=1,flags=re.S
)

html,n_ui_audit=re.subn(
    r"""  function auditLayoutV178\(\)\{.*?\n  scheduleAuditV178\(\);\n\n  window\.__fjzV178=""",
    "  window.__fjzUiAuditV178={version:VERSION,disabledInProduction:true};\n\n  window.__fjzV178=",
    html,count=1,flags=re.S
)

# ---------------------------------------------------------
# D) Single production post-render runtime for recent fixes
#    + exported legacy polish tasks.
# ---------------------------------------------------------
js=r"""
<script id="v185ProductionRuntime">
(function(){
  const VERSION='18.5';
  const safe=(name,fn)=>{
    if(typeof fn!=='function')return;
    try{
      const out=fn();
      if(out&&typeof out.catch==='function')out.catch(e=>console.warn('TEAM FJZ '+name,e));
    }catch(e){console.warn('TEAM FJZ '+name,e)}
  };

  function isStudentV185(){
    return currentProfile?.role==='student'&&mode==='student';
  }
  function isStudentTrackingV185(){
    return isStudentV185()&&studentTab==='tracking';
  }

  function purgeMeasuresV185(){
    const outside=isStudentV185()&&!isStudentTrackingV185();
    document.body?.classList.toggle('v183-student-nontracking',outside);
    document.body?.classList.toggle('v184-student-outside-tracking',outside);
    if(!outside)return;
    [document.getElementById('view'),document.getElementById('studentSubBody')]
      .filter(Boolean)
      .forEach(root=>root.querySelectorAll(
        '#v93MeasureCompare,.v93-compare,#v176MeasurementHistory,.v176-measure-history'
      ).forEach(node=>node.remove()));
  }

  function wrapDateV185(input){
    if(!input)return;
    const label=input.closest('label');
    const grid=input.closest('.form-grid');
    if(!label||!grid)return;
    grid.classList.add('v181-sym-grid','v184-exact-pair');
    label.classList.add('v181-date-label');
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

  function mirrorPeerGeometryV185(date){
    if(!date)return;
    wrapDateV185(date);
    const grid=date.closest('.form-grid');
    const label=date.closest('label');
    if(!grid||!label)return;
    const peer=[...grid.querySelectorAll('input,select')]
      .find(x=>x!==date&&x.type!=='file'&&x.type!=='hidden');
    if(!peer)return;
    const cs=getComputedStyle(peer);
    [
      'height','min-height','max-height',
      'padding-top','padding-right','padding-bottom','padding-left',
      'border-top-width','border-right-width','border-bottom-width','border-left-width',
      'border-top-style','border-right-style','border-bottom-style','border-left-style',
      'border-top-color','border-right-color','border-bottom-color','border-left-color',
      'border-top-left-radius','border-top-right-radius','border-bottom-right-radius','border-bottom-left-radius',
      'font-size','font-family','font-weight','letter-spacing','background-color','color'
    ].forEach(prop=>{
      const value=cs.getPropertyValue(prop);
      if(value)date.style.setProperty(prop,value,'important');
    });
    date.style.setProperty('box-sizing','border-box','important');
    date.style.setProperty('width','100%','important');
    date.style.setProperty('min-width','0','important');
    date.style.setProperty('max-width','100%','important');
    date.style.setProperty('margin','0','important');
    const clip=date.closest('.v181-date-clip');
    const h=cs.getPropertyValue('height');
    if(clip&&h){
      clip.style.setProperty('height',h,'important');
      clip.style.setProperty('min-height',h,'important');
      clip.style.setProperty('max-height',h,'important');
    }
  }

  function exactTrackingGeometryV185(){
    ['ciWeek','mDate','progressPhotoDate'].forEach(id=>{
      document.querySelectorAll('#'+id).forEach(mirrorPeerGeometryV185);
    });
  }

  function renderStudentRowsV185(arr){
    return (arr||[]).map(function(s){
      const goal=(s.goal||'Sin objetivo cargado').trim?.()||'Sin objetivo cargado';
      return '<div class="student-row v182-student-row" data-client-id="'+esc(s.id)+'">'+
        '<div class="student-main">'+
          '<div class="v70-student-avatar-slot"><div class="v70-avatar">'+esc((s.name||'?').slice(0,2).toUpperCase())+'</div></div>'+
          '<div class="v182-student-copy"><strong class="v182-student-name">'+esc(s.name||'Alumno')+'</strong>'+
          '<div class="muted tiny v182-student-goal">'+esc(goal)+'</div></div>'+
        '</div>'+
        '<div><strong>'+adherence(s)+'%</strong><div class="muted tiny">Adherencia</div></div>'+
        '<div><strong>'+fmtDate(s.lastWorkout)+'</strong><div class="muted tiny">Último entreno</div></div>'+
        '<div>'+badge(statusFor(s))+'</div>'+
        '<div class="pill-row v182-student-actions">'+
          '<button class="btn small" onclick="openStudent(\''+s.id+'\')">Abrir</button>'+
          '<button class="btn small" style="border-color:rgba(255,31,47,.55);color:#ff7a84" onclick="deleteStudentCloud(\''+s.id+'\')">Eliminar</button>'+
        '</div>'+
      '</div>';
    }).join('');
  }
  window.studentRows=renderStudentRowsV185;
  try{studentRows=window.studentRows}catch(_e){}

  function decorateRowsV185(){
    document.querySelectorAll('.student-row[data-client-id]').forEach(row=>{
      row.classList.add('v182-student-row');
      const main=row.querySelector('.student-main');
      if(!main)return;
      const copy=main.querySelector('.v182-student-copy')||
        [...main.children].find(x=>!x.classList.contains('v70-student-avatar-slot')&&!x.classList.contains('avatar')&&!x.classList.contains('v80-student-alert-count'));
      if(copy){
        copy.classList.add('v182-student-copy');
        copy.querySelector('strong')?.classList.add('v182-student-name');
        copy.querySelector('.muted')?.classList.add('v182-student-goal');
      }
      row.querySelector(':scope > .pill-row:last-child')?.classList.add('v182-student-actions');
    });
  }

  function legacyPostV185(){
    safe('profile-v86',window.__fjzPostV86);
    safe('nutrition-v94',window.__fjzPostRenderV94);
    safe('training-v94',window.__fjzPostTrainingV94);
    safe('alerts-v96',window.__fjzInjectAlertsV96);
    safe('profile-data-v97',window.__fjzRunV97);
    safe('precision-v98',window.__fjzPolishV98);
    safe('audit-v99',window.__fjzAuditV99);
    safe('core-v100',window.__fjzCorePolishV100);
    safe('avatar-v101',window.__fjzAvatarAdjustV101);
    safe('alerts-v110',window.__fjzAlertsPolishV110);
  }

  function polishV185(){
    legacyPostV185();
    decorateRowsV185();
    purgeMeasuresV185();
    exactTrackingGeometryV185();
  }

  const basePostV185=window.__fjzPostRenderV176;
  window.__fjzPostRenderV176=function(){
    const out=basePostV185?.apply(this,arguments);
    polishV185();
    return out;
  };

  if(typeof window.renderTrackingCoachLoaded==='function'){
    const baseCoachTrackingV185=window.renderTrackingCoachLoaded;
    window.renderTrackingCoachLoaded=function(){
      const out=baseCoachTrackingV185.apply(this,arguments);
      requestAnimationFrame(polishV185);
      return out;
    };
    try{renderTrackingCoachLoaded=window.renderTrackingCoachLoaded}catch(_e){}
  }

  if(typeof window.renderStudentTrackingHistory==='function'){
    const baseStudentHistoryV185=window.renderStudentTrackingHistory;
    window.renderStudentTrackingHistory=function(){
      if(isStudentV185()&&!isStudentTrackingV185()){
        purgeMeasuresV185();
        return;
      }
      const out=baseStudentHistoryV185.apply(this,arguments);
      requestAnimationFrame(polishV185);
      return out;
    };
    try{renderStudentTrackingHistory=window.renderStudentTrackingHistory}catch(_e){}
  }

  let resizeRafV185=0;
  window.addEventListener('resize',()=>{
    if(!isStudentTrackingV185())return;
    cancelAnimationFrame(resizeRafV185);
    resizeRafV185=requestAnimationFrame(exactTrackingGeometryV185);
  },{passive:true});

  requestAnimationFrame(polishV185);

  const compat={version:VERSION,consolidated:true};
  window.__fjzV181={...compat,equalTrackingFieldGeometry:true};
  window.__fjzV182={...compat,dashboardStudentGeometry:true};
  window.__fjzV183={...compat,measurementsTrackingOnly:true,reviewBadgeNoWrap:true};
  window.__fjzV184={...compat,legacyMeasureInjectorStudentGuard:true,exactDatePeerGeometry:true};

  window.__fjzV185={
    version:VERSION,
    productionConsolidation:true,
    legacyCheckinRuntimeRemoved:true,
    recentRuntimeChainCollapsed:true,
    productionDiagnosticsRemoved:true,
    mutationPolishersRemoved:true,
    singleRecentPostRender:true,
    exactDatePeerGeometry:true
  };
})();
</script>
"""
html=html.replace("</body>",js+"\n</body>",1)

# ---------------------------------------------------------
# E) Final stylesheet consolidation. Preserve exact CSS order.
# ---------------------------------------------------------
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
mergeable=[]
for m in styles:
    attrs=m.group("attrs") or ""
    if re.search(r"\b(media|nonce)\s*=",attrs,re.I):continue
    mergeable.append(m)

if len(mergeable)>1:
    chunks=[]
    for m in mergeable:
        ident=re.search(r'id=["\']([^"\']+)["\']',m.group("attrs") or "",re.I)
        name=ident.group(1) if ident else "anonymous"
        chunks.append("\n/* --- "+name+" --- */\n"+m.group("body").strip())
    for m in reversed(mergeable):
        html=html[:m.start()]+html[m.end():]
    merged='<style id="fjzProductionStylesV185">'+''.join(chunks)+'\n</style>'
    html=html.replace("</head>",merged+"\n</head>",1)

after=metrics(html)

# ---------------------------------------------------------
# F) Production safety assertions.
# ---------------------------------------------------------
critical=[
  "function renderCoachDashboardV170",
  "window.renderTrackingStudent=function",
  "window.submitWeeklyCheckin=async function",
  "window.renderTrackingCoachLoaded=function",
  "window.renderNutritionStudentLoaded",
  "window.renderNutritionCoachLoaded",
  "window.saveMeasurementV176",
  "openMeasurementManagerV179",
  "window.studentRows=renderStudentRowsV185",
  "v145", # workout autosave generation remains in final source
  "deleteSessionV148",
  "deleteDayV152",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V18.5 critical functionality missing: "+repr(missing))

for ident in [
  "v87PolishRuntime","v88Runtime","v90MotivationFix","v91CheckinClamp",
  "v181TrackingDateSymmetryRuntime","v182GeometryCoachDashboardRuntime",
  "v183StudentScopeAlignmentRuntime","v184HardMeasureIsolationDateGeometryRuntime"
]:
    if f'id="{ident}"' in html:
        raise RuntimeError("V18.5 obsolete runtime still present: "+ident)

if after["render_assignments"]>=before["render_assignments"]:
    raise RuntimeError("V18.5 render wrapper count did not improve")
if after["mutation_observers"]>before["mutation_observers"]:
    raise RuntimeError("V18.5 mutation observer count regressed")
if after["timeouts"]>before["timeouts"]:
    raise RuntimeError("V18.5 timeout count regressed")
if after["styles"]>2:
    raise RuntimeError("V18.5 stylesheet consolidation failed: "+str(after["styles"]))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V18.5 production optimization BEFORE:",before)
print("TEAM FJZ V18.5 production optimization AFTER:",after)
print("TEAM FJZ V18.5 removed runtimes:",removed_runtime)
print("TEAM FJZ V18.5 wrapper edits:",{
  "v86":n86,"v92":n92,"v93":n93,"v94nutrition":n94n,"v94training":n94t,
  "v96":n96,"v97":n97,"v98":n98,"v99":n99,"v100":n100,"v101":n101,"v110":n110,
  "performance_observer":n_perf,"ui_audit":n_ui_audit
})
