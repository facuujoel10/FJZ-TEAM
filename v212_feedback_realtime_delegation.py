import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.12 EXERCISE FEEDBACK REALTIME DELEGATION
# =========================================================
# V13.2 unified realtime already owns exercise_feedback and invalidates:
#   exerciseFeedbackCacheV73, exerciseFeedbackAllCoachV73, coachFeedLoadedAt.
# V20.10 also invalidates the alert caches for exercise_feedback.
# Remove only V7.3's duplicate subscription; preserve all feedback UI/actions.

def metrics(doc):
    return {
        "channel_defs":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

before=metrics(html)
if before["channel_defs"]!=8:
    raise RuntimeError("V20.12 unexpected channel baseline: "+repr(before))
if html.count("fjz-v73-exercise-feedback")!=1:
    raise RuntimeError("V20.12 expected exactly one feedback channel")
if "fjz-v132-unified" not in html:
    raise RuntimeError("V20.12 unified realtime authority missing")

start_marker="const _setupRealtimeV73Base=setupRealtime;"
end_marker="// Dashboard y pestaña Rutina muestran el aviso rojo."
if html.count(start_marker)!=1:
    raise RuntimeError("V20.12 feedback start marker mismatch: "+str(html.count(start_marker)))
if html.count(end_marker)!=1:
    raise RuntimeError("V20.12 feedback end marker mismatch: "+str(html.count(end_marker)))

start=html.index(start_marker)
end=html.index(end_marker,start)
block=html[start:end]

required=[
    "fjz-v73-exercise-feedback",
    "table:'exercise_feedback'",
    "exerciseFeedbackCacheV73.clear()",
    "exerciseFeedbackAllCoachV73=[]",
]
missing=[x for x in required if x not in block]
if missing:
    raise RuntimeError("V20.12 feedback channel shape changed: "+repr(missing))
if block.count(".channel(")!=1:
    raise RuntimeError("V20.12 expected one channel in feedback wrapper")

replacement="""window.__fjzV73RealtimeDelegatedV212=true;

"""
html=html[:start]+replacement+html[end:]

after=metrics(html)
if after["channel_defs"]!=7:
    raise RuntimeError("V20.12 expected channel defs 8 -> 7: "+repr({"before":before,"after":after}))
if "fjz-v73-exercise-feedback" in html:
    raise RuntimeError("V20.12 legacy feedback channel still present")

critical=[
    "fjz-v132-unified",
    "exerciseFeedbackCacheV73.clear()",
    "exerciseFeedbackAllCoachV73=[]",
    "studentAlertsLoadedAtV96=0",
    "openExerciseFeedbackV73",
    "submitExerciseFeedbackV73",
    "reviewExerciseFeedbackV73",
    "injectStudentWorkoutFeedbackV73",
    "injectRoutineExerciseAlertsV73",
    "singleRealtimeAuthority:true",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.12 missing feedback behavior: "+repr(missing))

runtime=r"""
<script id="v212FeedbackRealtimeDelegationRuntime">
(function(){
  window.__fjzV212={
    version:'20.12',
    feedbackRealtimeDelegated:true,
    feedbackUiPreserved:true,
    feedbackCacheInvalidationPreserved:true,
    alertCacheInvalidationPreserved:true,
    unifiedRealtimePreserved:true,
    behaviorChange:false
  };
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.12 exercise feedback realtime delegation")
print("V20.12 BEFORE:",before)
print("V20.12 AFTER:",after)
print("V20.12 duplicate feedback channel removed; feedback UX preserved")
