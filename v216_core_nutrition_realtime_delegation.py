import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.16 CORE NUTRITION REALTIME DELEGATION
# =========================================================
# V13.2 unified realtime listens to nutrition_plans + nutrition_logs and
# invalidates nutritionLoadedAthlete before the canonical render.
# Remove only the duplicate V6 channel; keep all nutrition UI/data loaders.

def metrics(doc):
    return {
        "channel_defs":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

before=metrics(html)
if before["channel_defs"]!=5:
    raise RuntimeError("V20.16 unexpected channel baseline: "+repr(before))
if html.count("fjz-v6-nutrition")!=1:
    raise RuntimeError("V20.16 expected exactly one V6 nutrition channel")
if "fjz-v132-unified" not in html:
    raise RuntimeError("V20.16 unified realtime authority missing")

start_marker="const _setupRealtimeV61=setupRealtime;"
end_marker="// ===== TEAM FJZ V8.3 · PLANTILLAS"
if html.count(start_marker)!=1:
    raise RuntimeError("V20.16 nutrition start marker mismatch: "+str(html.count(start_marker)))
if html.count(end_marker)!=1:
    raise RuntimeError("V20.16 nutrition end marker mismatch: "+str(html.count(end_marker)))

start=html.index(start_marker)
end=html.index(end_marker,start)
block=html[start:end]

required=[
    "fjz-v6-nutrition",
    "table:'nutrition_plans'",
    "table:'nutrition_logs'",
    "nutritionLoadedAthlete=null",
]
missing=[x for x in required if x not in block]
if missing:
    raise RuntimeError("V20.16 nutrition channel shape changed: "+repr(missing))
if block.count(".channel(")!=1:
    raise RuntimeError("V20.16 expected one channel in V6 wrapper")

html=html[:start]+"window.__fjzV6RealtimeDelegatedV216=true;\n\n"+html[end:]

after=metrics(html)
if after["channel_defs"]!=4:
    raise RuntimeError("V20.16 expected channel defs 5 -> 4: "+repr({"before":before,"after":after}))
if "fjz-v6-nutrition" in html:
    raise RuntimeError("V20.16 legacy V6 nutrition channel still present")

critical=[
    "fjz-v132-unified",
    "'nutrition_logs','nutrition_plans'",
    "nutritionLoadedAthlete=null",
    "loadNutrition",
    "renderNutritionCoachLoaded",
    "renderNutritionStudentLoaded",
    "nutritionCache",
    "singleRealtimeAuthority:true",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.16 missing nutrition behavior: "+repr(missing))

runtime=r"""
<script id="v216CoreNutritionRealtimeDelegationRuntime">
(function(){
  window.__fjzV216={
    version:'20.16',
    coreNutritionRealtimeDelegated:true,
    nutritionUiPreserved:true,
    nutritionReloadInvalidationPreserved:true,
    unifiedRealtimePreserved:true,
    behaviorChange:false
  };
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.16 core nutrition realtime delegation")
print("V20.16 BEFORE:",before)
print("V20.16 AFTER:",after)
print("V20.16 duplicate V6 nutrition channel removed; nutrition UX preserved")
