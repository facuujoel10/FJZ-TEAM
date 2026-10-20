import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.15 V80 REALTIME DELEGATION
# =========================================================
# V13.2 unified realtime fully covers exercise_media + exercise_feedback
# invalidation. V80 render/hydration remains intact; only its duplicate
# Supabase channel is removed.

def metrics(doc):
    return {
        "channel_defs":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

before=metrics(html)
if before["channel_defs"]!=6:
    raise RuntimeError("V20.15 unexpected channel baseline: "+repr(before))
if html.count("fjz-v80")!=1:
    raise RuntimeError("V20.15 expected exactly one V80 channel")
if "fjz-v132-unified" not in html:
    raise RuntimeError("V20.15 unified realtime authority missing")

start_marker="const _setupRealtimeV80Base=setupRealtime;"
end_marker="Object.assign(window,{"
if html.count(start_marker)!=1:
    raise RuntimeError("V20.15 V80 start marker mismatch: "+str(html.count(start_marker)))

start=html.index(start_marker)
end=html.index(end_marker,start)
block=html[start:end]

required=[
    "fjz-v80",
    "table:'exercise_media'",
    "table:'exercise_feedback'",
    "exerciseMediaCacheV80.clear()",
    "exerciseMediaCoachV80=null",
    "exerciseMediaSignedV80.clear()",
    "coachFeedLoadedAt=0",
]
missing=[x for x in required if x not in block]
if missing:
    raise RuntimeError("V20.15 V80 channel shape changed: "+repr(missing))
if block.count(".channel(")!=1:
    raise RuntimeError("V20.15 expected one channel in V80 wrapper")

html=html[:start]+"window.__fjzV80RealtimeDelegatedV215=true;\n\n"+html[end:]

after=metrics(html)
if after["channel_defs"]!=5:
    raise RuntimeError("V20.15 expected channel defs 6 -> 5: "+repr({"before":before,"after":after}))
if "fjz-v80" in html:
    raise RuntimeError("V20.15 legacy V80 channel still present")

critical=[
    "fjz-v132-unified",
    "table==='exercise_media'",
    "table==='exercise_feedback'",
    "exerciseMediaCacheV80.clear()",
    "exerciseMediaCoachV80=null",
    "exerciseMediaSignedV80.clear()",
    "coachFeedLoadedAt=0",
    "hydrateExerciseVideosV80",
    "hydrateCoachDashboardV80",
    "injectStudent360V80",
    "uploadExerciseVideoV80",
    "removeExerciseVideoV80",
    "singleRealtimeAuthority:true",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.15 missing V80 behavior: "+repr(missing))

runtime=r"""
<script id="v215V80RealtimeDelegationRuntime">
(function(){
  window.__fjzV215={
    version:'20.15',
    v80RealtimeDelegated:true,
    exerciseMediaUiPreserved:true,
    dashboardHydrationPreserved:true,
    mediaCacheInvalidationPreserved:true,
    feedbackInvalidationPreserved:true,
    unifiedRealtimePreserved:true,
    behaviorChange:false
  };
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.15 V80 realtime delegation")
print("V20.15 BEFORE:",before)
print("V20.15 AFTER:",after)
print("V20.15 duplicate V80 channel removed; media/dashboard UX preserved")
