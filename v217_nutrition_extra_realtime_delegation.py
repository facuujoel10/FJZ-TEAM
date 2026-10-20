import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.17 NUTRITION EXTRA REALTIME DELEGATION
# =========================================================
# V13.2 already subscribes to nutrition_templates and
# nutrition_plan_revisions. Extend its nutrition invalidation to templates,
# then retire the duplicate V6.3 channel. Template/revision UI remains intact.

def metrics(doc):
    return {
        "channel_defs":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

before=metrics(html)
if before["channel_defs"]!=4:
    raise RuntimeError("V20.17 unexpected channel baseline: "+repr(before))
if html.count("fjz-v63-nutrition-extra")!=1:
    raise RuntimeError("V20.17 expected exactly one V63 nutrition channel")
if "fjz-v132-unified" not in html:
    raise RuntimeError("V20.17 unified realtime authority missing")

# Make nutrition_templates use the same canonical stale-data invalidation.
old_inv="['nutrition_logs','nutrition_plans','nutrition_plan_revisions'].includes(table)"
new_inv="['nutrition_logs','nutrition_plans','nutrition_plan_revisions','nutrition_templates'].includes(table)"
if html.count(old_inv)!=1:
    raise RuntimeError("V20.17 nutrition invalidation anchor mismatch: "+str(html.count(old_inv)))
html=html.replace(old_inv,new_inv,1)

start_marker="const _setupRealtimeV62=setupRealtime;"
end_marker="Object.assign(window,{"
if html.count(start_marker)!=1:
    raise RuntimeError("V20.17 V63 start marker mismatch: "+str(html.count(start_marker)))

start=html.index(start_marker)
end=html.index(end_marker,start)
block=html[start:end]

required=[
    "fjz-v63-nutrition-extra",
    "table:'nutrition_templates'",
    "table:'nutrition_plan_revisions'",
]
missing=[x for x in required if x not in block]
if missing:
    raise RuntimeError("V20.17 V63 channel shape changed: "+repr(missing))
if block.count(".channel(")!=1:
    raise RuntimeError("V20.17 expected one channel in V63 wrapper")

html=html[:start]+"window.__fjzV63RealtimeDelegatedV217=true;\n\n"+html[end:]

after=metrics(html)
if after["channel_defs"]!=3:
    raise RuntimeError("V20.17 expected channel defs 4 -> 3: "+repr({"before":before,"after":after}))
if "fjz-v63-nutrition-extra" in html:
    raise RuntimeError("V20.17 legacy V63 channel still present")

critical=[
    "fjz-v132-unified",
    "'nutrition_plan_revisions','nutrition_templates'",
    "nutritionLoadedAthlete=null",
    "openSaveNutritionTemplateV63",
    "saveNutritionTemplateV63",
    "openNutritionTemplatesV63",
    "applyNutritionTemplateV63",
    "deleteNutritionTemplateV63",
    "openNutritionRevisionV63",
    "restoreNutritionRevisionV63",
    "openNutritionAlternativesV63",
    "saveNutritionAlternativesV63",
    "singleRealtimeAuthority:true",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.17 missing nutrition-extra behavior: "+repr(missing))

runtime=r"""
<script id="v217NutritionExtraRealtimeDelegationRuntime">
(function(){
  window.__fjzV217={
    version:'20.17',
    nutritionExtraRealtimeDelegated:true,
    nutritionTemplatesInvalidation:true,
    nutritionTemplateUiPreserved:true,
    nutritionRevisionUiPreserved:true,
    unifiedRealtimePreserved:true,
    behaviorChange:false
  };
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.17 nutrition extra realtime delegation")
print("V20.17 BEFORE:",before)
print("V20.17 AFTER:",after)
print("V20.17 duplicate V63 nutrition channel removed; templates/revisions preserved")
