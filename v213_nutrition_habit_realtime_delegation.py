import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.13 REALTIME INVENTORY + HABIT DELEGATION GUARD
# =========================================================
# Some historical nutrition-habit code is already removed by older
# consolidation passes. Never assume the base-source channel survives into
# the final runtime. Inventory first; remove only if the exact legacy block
# still exists.

def metrics(doc):
    return {
        "channel_defs":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

def literal_topics(doc):
    return re.findall(r"\.channel\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",doc)

before=metrics(html)
topics_before=literal_topics(html)
if before["channel_defs"]!=7:
    raise RuntimeError("V20.13 unexpected channel baseline: "+repr(before))
if "fjz-v132-unified" not in html:
    raise RuntimeError("V20.13 unified realtime authority missing")
if "nutrition_habit_logs" not in html:
    raise RuntimeError("V20.13 unified nutrition habit coverage missing")

removed=False
topic="fjz-v66-habits"

if topic in html:
    if html.count(topic)!=1:
        raise RuntimeError("V20.13 unexpected habits topic count: "+str(html.count(topic)))

    start_marker="const _setupRealtimeV66=setupRealtime;"
    end_marker="Object.assign(window,{"
    if html.count(start_marker)!=1:
        raise RuntimeError("V20.13 habits start marker mismatch: "+str(html.count(start_marker)))

    start=html.index(start_marker)
    end=html.index(end_marker,start)
    block=html[start:end]

    required=[
        topic,
        "table:'nutrition_habit_logs'",
        "setTimeout(()=>render(),250)",
    ]
    missing=[x for x in required if x not in block]
    if missing:
        raise RuntimeError("V20.13 habits channel shape changed: "+repr(missing))
    if block.count(".channel(")!=1:
        raise RuntimeError("V20.13 expected one channel in habits wrapper")

    html=html[:start]+"window.__fjzV66RealtimeDelegatedV213=true;\n\n"+html[end:]
    removed=True

after=metrics(html)
topics_after=literal_topics(html)

expected_after=before["channel_defs"]-(1 if removed else 0)
if after["channel_defs"]!=expected_after:
    raise RuntimeError("V20.13 channel count mismatch: "+repr({"before":before,"after":after}))
if topic in html:
    raise RuntimeError("V20.13 legacy habits topic remained after attempted removal")

critical=[
    "fjz-v132-unified",
    "nutrition_habit_logs",
    "nutritionLoadedAthlete=null",
    "renderNutritionHabitsCoachV66",
    "renderNutritionHabitsStudentV66",
    "toggleCoachHabitV66",
    "toggleStudentHabitV66",
    "singleRealtimeAuthority:true",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.13 missing nutrition habit behavior: "+repr(missing))

runtime=r"""
<script id="v213RealtimeInventoryRuntime">
(function(){
  window.__fjzV213={
    version:'20.13',
    realtimeInventory:true,
    nutritionHabitRealtimeDelegated:true,
    habitUiPreserved:true,
    behaviorChange:false
  };
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.13 realtime inventory / habit guard")
print("V20.13 BEFORE:",before)
print("V20.13 AFTER:",after)
print("V20.13 HABIT CHANNEL REMOVED:",removed)
print("V20.13 CHANNEL TOPICS BEFORE:",topics_before)
print("V20.13 CHANNEL TOPICS AFTER:",topics_after)
