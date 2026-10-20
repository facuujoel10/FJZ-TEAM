import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.21 GENERAL MOBILE REPAIR RENDER CONSOLIDATION
# =========================================================
# V17.7's remaining general render wrapper only queues queueRepairV177().
# V18.0 is the immediately-later route/scroll authority.
#
# Move the repair queue call into V18.0 immediately after baseRenderV180()
# returns and BEFORE route-top scheduling. This preserves the original enqueue
# order while removing one nested general render wrapper.
#
# V17.7 tracking-specific repair is already preserved by V20.20/V19.2.
# Resize/orientation listeners stay untouched.

def metrics(doc):
    return {
        "render_assignments":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "v177_general_wrapper":doc.count("const baseRenderV177=render;"),
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
        raise RuntimeError("V20.21 missing script: "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.21 no change in "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)
if before["render_assignments"]!=22:
    raise RuntimeError("V20.21 unexpected render baseline: "+repr(before))
if before["v177_general_wrapper"]!=1:
    raise RuntimeError("V20.21 expected one V17.7 general wrapper: "+repr(before))
if "__fjzQueueRepairV177" not in html:
    raise RuntimeError("V20.21 V17.7 exported repair queue missing")

def patch_v177(body):
    old="""  // One post-render repair frame only. No MutationObserver and no repeating timer.
  if(typeof render==='function'){
    const baseRenderV177=render;
    render=function(){
      const out=baseRenderV177.apply(this,arguments);
      queueRepairV177();
      return out;
    };
  }

"""
    if body.count(old)!=1:
        raise RuntimeError("V20.21 V17.7 general wrapper mismatch: "+str(body.count(old)))
    return body.replace(
        old,
        """  // General render repair delegated to the V18.0 route authority by V20.21.

""",
        1
    )

html=edit_script(html,"v177MobileStabilityMeasurementRuntime",patch_v177)

def patch_v180(body):
    old="""      const out=baseRenderV180.apply(this,arguments);
      const after=routeKeyV180();"""
    new="""      const out=baseRenderV180.apply(this,arguments);

      // Preserve V17.7's original repair enqueue before route-top RAFs.
      window.__fjzQueueRepairV177?.();

      const after=routeKeyV180();"""
    if body.count(old)!=1:
        raise RuntimeError("V20.21 V18.0 render authority mismatch: "+str(body.count(old)))
    return body.replace(old,new,1)

html=edit_script(html,"v180VisualStabilityRuntime",patch_v180)

after=metrics(html)
if after["render_assignments"]!=21:
    raise RuntimeError("V20.21 expected render assignments 22 -> 21: "+repr({"before":before,"after":after}))
if after["v177_general_wrapper"]!=0:
    raise RuntimeError("V20.21 V17.7 general wrapper still present")
for key in ("timeouts","rafs","listeners"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.21 must preserve "+key+": "+repr({"before":before,"after":after}))

critical=[
    "__fjzQueueRepairV177",
    "queueRepairV177",
    "repairV177",
    "ensureMeasurementEditV177",
    "hardContainNativeInputsV177",
    "window.addEventListener('resize',queueRepairV177",
    "window.addEventListener('orientationchange',queueRepairV177",
    "routeKeyV180",
    "scheduleRouteTopV180",
    "routeScrollAuthority:true",
    "doubleRafTopReset:true",
    "window.__fjzQueueRepairV177?.();",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.21 missing mobile/navigation behavior: "+repr(missing))

runtime=r"""
<script id="v221GeneralRepairRenderConsolidationRuntime">
(function(){
  window.__fjzV221={
    version:'20.21',
    v177GeneralRenderWrapperRemoved:true,
    v180RouteAuthorityReused:true,
    repairEnqueueOrderPreserved:true,
    routeScrollPreserved:true,
    resizeListenersPreserved:true,
    trackingRepairPreserved:true,
    behaviorChange:false
  };
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.21 general mobile repair render consolidation")
print("V20.21 BEFORE:",before)
print("V20.21 AFTER:",after)
print("V20.21 V17.7 general render wrapper delegated to V18.0")
