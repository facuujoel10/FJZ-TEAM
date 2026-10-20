import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.20 TRACKING REPAIR WRAPPER CONSOLIDATION
# =========================================================
# V17.7 wraps renderStudentTrackingHistory + renderTrackingCoachLoaded only to
# queueRepairV177(). V19.2 later wraps the same functions to run polishV192().
#
# Export queueRepairV177, remove those two V17.7 wrappers, and invoke the
# repair immediately from the V19.2 wrapper before Promise.finally(polishV192).
# This preserves runtime order while removing two nested tracking wrappers.
#
# V17.7 general render wrapper + resize/orientation listeners remain unchanged.

def metrics(doc):
    return {
        "render_assignments":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

def edit_script(doc,script_id,transform):
    pat=re.compile(
        r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',
        re.S|re.I
    )
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.20 missing script: "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.20 no change in "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)
if before["render_assignments"]!=22:
    raise RuntimeError("V20.20 unexpected render baseline: "+repr(before))

def patch_v177(body):
    old_student="""  if(typeof renderStudentTrackingHistory==='function'){
    const baseStudentHistoryV177=renderStudentTrackingHistory;
    renderStudentTrackingHistory=function(){
      const out=baseStudentHistoryV177.apply(this,arguments);
      queueRepairV177();
      return out;
    };
    try{window.renderStudentTrackingHistory=renderStudentTrackingHistory}catch(_e){}
  }

"""
    old_coach="""  if(typeof renderTrackingCoachLoaded==='function'){
    const baseCoachTrackingV177=renderTrackingCoachLoaded;
    renderTrackingCoachLoaded=function(){
      const out=baseCoachTrackingV177.apply(this,arguments);
      queueRepairV177();
      return out;
    };
    try{window.renderTrackingCoachLoaded=renderTrackingCoachLoaded}catch(_e){}
  }

"""
    if body.count(old_student)!=1:
        raise RuntimeError("V20.20 V17.7 student tracking wrapper mismatch: "+str(body.count(old_student)))
    if body.count(old_coach)!=1:
        raise RuntimeError("V20.20 V17.7 coach tracking wrapper mismatch: "+str(body.count(old_coach)))
    body=body.replace(old_student,"",1).replace(old_coach,"",1)

    export_anchor="""  window.addEventListener('resize',queueRepairV177,{passive:true});"""
    if body.count(export_anchor)!=1:
        raise RuntimeError("V20.20 V17.7 export anchor mismatch")
    body=body.replace(
        export_anchor,
        """  window.__fjzQueueRepairV177=queueRepairV177;

  window.addEventListener('resize',queueRepairV177,{passive:true});""",
        1
    )
    return body

html=edit_script(html,"v177MobileStabilityMeasurementRuntime",patch_v177)

def patch_v192(body):
    old="""  ['renderTrackingCoachLoaded','renderStudentTrackingHistory'].forEach(name=>{
    const fn=window[name];
    if(typeof fn!=='function'||fn.__v192Wrapped)return;
    const wrapped=function(){
      const out=fn.apply(this,arguments);
      Promise.resolve(out).finally(polishV192);
      return out;
    };
    wrapped.__v192Wrapped=true;
    window[name]=wrapped;
    try{globalThis[name]=wrapped}catch(_e){}
  });"""
    new="""  ['renderTrackingCoachLoaded','renderStudentTrackingHistory'].forEach(name=>{
    const fn=window[name];
    if(typeof fn!=='function'||fn.__v192Wrapped)return;
    const wrapped=function(){
      const out=fn.apply(this,arguments);
      window.__fjzQueueRepairV177?.();
      Promise.resolve(out).finally(polishV192);
      return out;
    };
    wrapped.__v192Wrapped=true;
    window[name]=wrapped;
    try{globalThis[name]=wrapped}catch(_e){}
  });"""
    if body.count(old)!=1:
        raise RuntimeError("V20.20 V19.2 tracking authority mismatch: "+str(body.count(old)))
    return body.replace(old,new,1)

html=edit_script(html,"v192GeneralStabilityRuntime",patch_v192)

after=metrics(html)
if after["render_assignments"]!=20:
    raise RuntimeError("V20.20 expected render assignments 22 -> 20: "+repr({"before":before,"after":after}))
for key in ("timeouts","rafs","listeners"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.20 must preserve "+key+": "+repr({"before":before,"after":after}))

critical=[
    "__fjzQueueRepairV177",
    "queueRepairV177",
    "repairV177",
    "ensureMeasurementEditV177",
    "hardContainNativeInputsV177",
    "measurementEditRepair:true",
    "stableViewport:true",
    "renderTrackingCoachLoaded",
    "renderStudentTrackingHistory",
    "Promise.resolve(out).finally(polishV192)",
    "__v192Wrapped",
    "recentGeometryWrappersConsolidated:true",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.20 missing tracking behavior: "+repr(missing))

runtime=r"""
<script id="v220TrackingRepairConsolidationRuntime">
(function(){
  window.__fjzV220={
    version:'20.20',
    trackingRepairWrappersBefore:2,
    trackingRepairWrappersAfter:0,
    v192AuthorityReused:true,
    repairOrderPreserved:true,
    measurementEditPreserved:true,
    nativeInputContainmentPreserved:true,
    resizeListenersPreserved:true,
    behaviorChange:false
  };
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.20 tracking repair wrapper consolidation")
print("V20.20 BEFORE:",before)
print("V20.20 AFTER:",after)
print("V20.20 V17.7 targeted tracking wrappers consolidated into V19.2: 2 -> 0")
