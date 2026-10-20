import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.11 CORE REALTIME DELEGATION
# =========================================================
# The original V4 channel is fully covered by V13.2 unified realtime:
# athlete_snapshots, athletes, weekly_checkins and body_measurements.
# Keep setupRealtime() itself as the compatibility root for later wrappers,
# but remove its redundant Supabase subscription.

def metrics(doc):
    return {
        "channel_defs":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

before=metrics(html)
if before["channel_defs"]!=9:
    raise RuntimeError("V20.11 unexpected channel baseline: "+repr(before))
if html.count("fjz-v4-sync")!=1:
    raise RuntimeError("V20.11 expected exactly one V4 realtime channel")
if "fjz-v132-unified" not in html:
    raise RuntimeError("V20.11 unified realtime authority missing")

start_marker="function setupRealtime(){if(!supabaseClient)return;if(realtimeChannel)"
if html.count(start_marker)!=1:
    raise RuntimeError("V20.11 setupRealtime root marker mismatch: "+str(html.count(start_marker)))

start=html.index(start_marker)
end_marker=".subscribe()}"
end=html.find(end_marker,start)
if end<0:
    raise RuntimeError("V20.11 base realtime end marker missing")
end+=len(end_marker)
block=html[start:end]

required_in_block=[
    "fjz-v4-sync",
    "table:'athlete_snapshots'",
    "table:'athletes'",
    "table:'weekly_checkins'",
    "table:'body_measurements'",
    "refreshCloudFromRealtime",
]
missing=[x for x in required_in_block if x not in block]
if missing:
    raise RuntimeError("V20.11 base channel shape changed: "+repr(missing))
if block.count(".channel(")!=1:
    raise RuntimeError("V20.11 expected one channel inside base setup")

replacement="""function setupRealtime(){
  window.__fjzV4RealtimeDelegatedV211=true;
}"""
html=html[:start]+replacement+html[end:]

after=metrics(html)
if after["channel_defs"]!=8:
    raise RuntimeError("V20.11 expected channel defs 9 -> 8: "+repr({"before":before,"after":after}))
if "fjz-v4-sync" in html:
    raise RuntimeError("V20.11 legacy core channel still present")

critical=[
    "fjz-v132-unified",
    "function refreshCloudFromRealtime",
    "singleRealtimeAuthority:true",
    "__fjzShouldRenderRealtimeV146",
    "weekly_checkins",
    "body_measurements",
    "athlete_snapshots",
    "athletes",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.11 missing core realtime behavior: "+repr(missing))

runtime=r"""
<script id="v211CoreRealtimeDelegationRuntime">
(function(){
  window.__fjzV211={
    version:'20.11',
    v4RealtimeDelegated:true,
    unifiedRealtimePreserved:true,
    setupRealtimeCompatibilityRoot:true,
    coreCloudRefreshPreserved:true,
    behaviorChange:false
  };
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.11 core realtime delegation")
print("V20.11 BEFORE:",before)
print("V20.11 AFTER:",after)
print("V20.11 legacy fjz-v4-sync removed; unified realtime preserved")
