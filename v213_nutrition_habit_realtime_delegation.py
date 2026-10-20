import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.13 NUTRITION HABIT REALTIME DELEGATION
# =========================================================
# V13.2 unified realtime listens to nutrition_habit_logs, invalidates the
# nutrition cache, then schedules the canonical render. The V6.6 channel only
# scheduled a delayed render on nutrition views, so it is redundant.

def metrics(doc):
    return {
        "channel_defs":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

before=metrics(html)
if before["channel_defs"]!=7:
    raise RuntimeError("V20.13 unexpected channel baseline: "+repr(before))
if html.count("fjz-v66-habits")!=1:
    raise RuntimeError("V20.13 expected exactly one habits channel")
if "fjz-v132-unified" not in html:
    raise RuntimeError("V20.13 unified realtime authority missing")

start_marker="const _setupRealtimeV66=setupRealtime;"
end_marker="Object.assign(window,{"
if html.count(start_marker)!=1:
    raise RuntimeError("V20.13 habits start marker mismatch: "+str(html.count(start_marker)))

start=html.index(start_marker)
end=html.index(end_marker,start)
block=html[start:end]

required=[
    "fjz-v66-habits",
    "table:'nutrition_habit_logs'",
    "setTimeout(()=>render(),250)",
]
missing=[x for x in required if x not in block]
if missing:
    raise RuntimeError("V20.13 habits channel shape changed: "+repr(missing))
if block.count(".channel(")!=1:
    raise RuntimeError("V20.13 expected one channel in habits wrapper")

replacement="""window.__fjzV66RealtimeDelegatedV213=true;

"""
html=html[:start]+replacement+html[end:]

after=metrics(html)
if after["channel_defs"]!=6:
    raise RuntimeError("V20.13 expected channel defs 7 -> 6: "+repr({"before":before,"after":after}))
if "fjz-v66-habits" in html:
    raise RuntimeError("V20.13 legacy habits channel still present")

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
<script id="v213NutritionHabitRealtimeDelegationRuntime">
(function(){
  window.__fjzV213={
    version:'20.13',
    nutritionHabitRealtimeDelegated:true,
    habitUiPreserved:true,
    unifiedNutritionInvalidationPreserved:true,
    behaviorChange:false
  };
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.13 nutrition habit realtime delegation")
print("V20.13 BEFORE:",before)
print("V20.13 AFTER:",after)
print("V20.13 duplicate nutrition habit channel removed")
