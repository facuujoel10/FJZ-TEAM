import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.14 GLOBAL MUSIC REALTIME DELEGATION
# =========================================================
# V13.2 unified realtime already listens to coach_media_settings,
# invalidates coachMediaV69 and schedules the canonical render.
# Remove only V6.9's duplicate channel; preserve all music UI/actions.

def metrics(doc):
    return {
        "channel_defs":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

before=metrics(html)
if before["channel_defs"]!=7:
    raise RuntimeError("V20.14 unexpected channel baseline: "+repr(before))
if html.count("fjz-v69-global-music")!=1:
    raise RuntimeError("V20.14 expected exactly one global music channel")
if "fjz-v132-unified" not in html:
    raise RuntimeError("V20.14 unified realtime authority missing")

start_marker="const _setupRealtimeV69Base=setupRealtime;"
end_marker="Object.assign(window,{"
if html.count(start_marker)!=1:
    raise RuntimeError("V20.14 music start marker mismatch: "+str(html.count(start_marker)))

start=html.index(start_marker)
end=html.index(end_marker,start)
block=html[start:end]

required=[
    "fjz-v69-global-music",
    "table:'coach_media_settings'",
    "coachMediaV69=null",
    "setTimeout(()=>render(),250)",
]
missing=[x for x in required if x not in block]
if missing:
    raise RuntimeError("V20.14 music channel shape changed: "+repr(missing))
if block.count(".channel(")!=1:
    raise RuntimeError("V20.14 expected one channel in music wrapper")

html=html[:start]+"window.__fjzV69RealtimeDelegatedV214=true;\n\n"+html[end:]

after=metrics(html)
if after["channel_defs"]!=6:
    raise RuntimeError("V20.14 expected channel defs 7 -> 6: "+repr({"before":before,"after":after}))
if "fjz-v69-global-music" in html:
    raise RuntimeError("V20.14 legacy music channel still present")

critical=[
    "fjz-v132-unified",
    "table==='coach_media_settings'",
    "coachMediaV69=null",
    "loadCoachMediaV69",
    "saveGlobalSpotifyV69",
    "clearGlobalSpotifyV69",
    "renderGlobalMusicCoachV69",
    "singleRealtimeAuthority:true",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.14 missing music behavior: "+repr(missing))

runtime=r"""
<script id="v214GlobalMusicRealtimeDelegationRuntime">
(function(){
  window.__fjzV214={
    version:'20.14',
    globalMusicRealtimeDelegated:true,
    musicUiPreserved:true,
    musicCacheInvalidationPreserved:true,
    unifiedRealtimePreserved:true,
    behaviorChange:false
  };
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.14 global music realtime delegation")
print("V20.14 BEFORE:",before)
print("V20.14 AFTER:",after)
print("V20.14 duplicate global music channel removed; music UX preserved")
