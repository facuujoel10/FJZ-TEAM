import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.13 FINAL REALTIME INVENTORY
# =========================================================
# Diagnostic-only stabilization checkpoint. Historical V6.6 habit realtime
# and its legacy habit-log flow have already been removed by earlier
# consolidation layers, so V20.13 must not alter runtime behavior.

def metrics(doc):
    return {
        "channel_defs":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

def literal_topics(doc):
    return re.findall(r"\.channel\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",doc)

before=metrics(html)
topics=literal_topics(html)

if before["channel_defs"]!=7:
    raise RuntimeError("V20.13 unexpected channel baseline: "+repr(before))
if "fjz-v132-unified" not in html:
    raise RuntimeError("V20.13 unified realtime authority missing")
if "fjz-v66-habits" in html:
    raise RuntimeError("V20.13 unexpected legacy V6.6 habit channel survived")
if "nutrition_habit_logs" in html:
    raise RuntimeError("V20.13 unexpected legacy habit-log flow survived")

runtime=r"""
<script id="v213RealtimeInventoryRuntime">
(function(){
  window.__fjzV213={
    version:'20.13',
    realtimeInventory:true,
    behaviorChange:false,
    legacyHabitRealtimeAlreadyRemoved:true
  };
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)

after=metrics(html)
if after["channel_defs"]!=before["channel_defs"]:
    raise RuntimeError("V20.13 diagnostic changed channel count")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.13 final realtime inventory")
print("V20.13 METRICS:",before)
print("V20.13 CHANNEL TOPICS:",topics)
print("V20.13 legacy V6.6 habits already absent; no behavior change")
