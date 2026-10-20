import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.10 ALERT REALTIME CONSOLIDATION
# =========================================================
# Keep V9.6 alert UI/logic, but retire its duplicate Supabase channel.
# V13.2 already subscribes to the same alert-related tables. Before removing
# the old channel, extend V13.2 invalidation to reset the exact V9.6 caches.
#
# V12.2 followup/payment realtime is intentionally NOT changed here.

def metrics(doc):
    return {
        "channel_defs":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

def edit_script(doc,script_id,fn):
    pat=re.compile(
        r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',
        re.S|re.I
    )
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.10 missing script: "+script_id)
    body=m.group(2)
    new=fn(body)
    if new==body:
        raise RuntimeError("V20.10 no change in "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)
if before["channel_defs"]!=10:
    raise RuntimeError("V20.10 unexpected channel baseline: "+repr(before))
if html.count("fjz-v96-alerts")!=1:
    raise RuntimeError("V20.10 expected one V9.6 alert channel")
if "fjz-v132-unified" not in html:
    raise RuntimeError("V20.10 unified realtime authority missing")

# Extend the unified invalidator with the exact alert-cache invalidation
# previously owned by the V9.6 channel callback.
def patch_v132(body):
    anchor="  function invalidateV132(table){\n"
    if body.count(anchor)!=1:
        raise RuntimeError("V20.10 V13.2 invalidate anchor mismatch")
    add="""  function invalidateV132(table){
    if(['student_notices','weekly_checkins','athlete_reminders','athlete_schedule','nutrition_plans','exercise_feedback'].includes(table)){
      try{coachFeedLoadedAt=0}catch(e){}
      try{studentAlertsLoadedAtV96=0}catch(e){}
    }
"""
    return body.replace(anchor,add,1)

html=edit_script(html,"v132CoachAssistantRealtime",patch_v132)

# Remove only the duplicate realtime wrapper from V9.6. Keep every alert
# render, action, notice, read/dismiss and UI helper intact.
def patch_v96(body):
    pat=re.compile(
        r"""\n\s*const oldSetupRealtimeV96=window\.setupRealtime;\s*
            if\(typeof oldSetupRealtimeV96==='function'\)\{\s*
              window\.setupRealtime=function\(\)\{.*?
              \n\s*\};\s*
            \}\s*
            (?=\n\s*Object\.assign\(window,)""",
        re.S|re.X
    )
    new,n=pat.subn("\n  window.__fjzV96RealtimeDelegatedV210=true;\n",body,count=1)
    if n!=1:
        raise RuntimeError("V20.10 V9.6 realtime wrapper mismatch: "+str(n))
    return new

html=edit_script(html,"v96AlertCenterRuntime",patch_v96)

after=metrics(html)
if after["channel_defs"]!=9:
    raise RuntimeError("V20.10 expected channel defs 10 -> 9: "+repr({"before":before,"after":after}))
if "fjz-v96-alerts" in html:
    raise RuntimeError("V20.10 legacy V9.6 channel still present")

critical=[
    "fjz-v132-unified",
    "refreshCoachAlertsV96",
    "updateStudentAlertsV96",
    "injectCoachAlertPanelV96",
    "injectStudentBellV96",
    "student_notices",
    "weekly_checkins",
    "athlete_reminders",
    "athlete_schedule",
    "nutrition_plans",
    "exercise_feedback",
    "singleRealtimeAuthority:true",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.10 missing alert/realtime behavior: "+repr(missing))

runtime=r"""
<script id="v210AlertRealtimeConsolidationRuntime">
(function(){
  window.__fjzV210={
    version:'20.10',
    alertUiPreserved:true,
    v96RealtimeDelegated:true,
    v132AlertCacheCoverage:true,
    unifiedRealtimePreserved:true,
    paymentRealtimeUntouched:true,
    behaviorChange:false
  };
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.10 alert realtime consolidation")
print("V20.10 BEFORE:",before)
print("V20.10 AFTER:",after)
print("V20.10 V9.6 duplicate realtime removed; alert UI preserved")
