import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.9 ROUTINE AUTHORITY CONSOLIDATION
# =========================================================
# Characterized on staging after V20.8:
#   saveExercise assignments: 4
#   confirmMoveExerciseV113 assignments: 2
#
# Final authorities intentionally preserved:
#   - V15.1: canonical one-pass saveExercise (exact reps + methods + load mode)
#   - V20.4: canonical modal reorder with exact scroll + atomic RPC
#   - V19.6: protected routine-builder modal flow
#   - V20.0: routine mutation/realtime guard and quick reorder persistence
#
# This transform removes only definitions that are fully superseded before
# any user interaction can occur. It does not change the UI or data model.

def script_body(doc, script_id):
    m=re.search(
        r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',
        doc,re.S|re.I
    )
    if not m:
        raise RuntimeError("V20.9 missing script: "+script_id)
    return m

def replace_script_body(doc, script_id, transform):
    m=script_body(doc,script_id)
    body=m.group(2)
    new_body=transform(body)
    if new_body==body:
        raise RuntimeError("V20.9 no change in "+script_id)
    return doc[:m.start(2)]+new_body+doc[m.end(2):]

def remove_exact(body, pattern, replacement, label):
    new,n=re.subn(pattern,replacement,body,count=1,flags=re.S)
    if n!=1:
        raise RuntimeError("V20.9 "+label+" mismatch: "+str(n))
    return new

def counts(doc):
    return {
        "saveExercise":len(re.findall(r"(?:window\.)?saveExercise\s*=",doc)),
        "confirmMoveExercise":len(re.findall(r"(?:window\.)?confirmMoveExerciseV113\s*=",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

before=counts(html)
expected_before={"saveExercise":4,"confirmMoveExercise":2}
for k,v in expected_before.items():
    if before[k]!=v:
        raise RuntimeError("V20.9 unexpected "+k+" baseline: "+repr(before))

# V8.6 method-aware save is superseded by V15.1, which preserves method,
# methodNote, methodApply, exact reps, load mode, history and override.
html=replace_script_body(
    html,"v86Runtime",
    lambda body:remove_exact(
        body,
        r'\n\s*window\.saveExercise=function\(di,ei,exUid,libId,muscle,equipment\)\{.*?\n\s*\};\n(?=\s*var dayEditorV86Base=)',
        "\n",
        "v86 saveExercise removal"
    )
)

# V10.4 exact-rep save is superseded by V15.1's canonical one-pass save.
html=replace_script_body(
    html,"v104ExactRepsRuntime",
    lambda body:remove_exact(
        body,
        r'\n\s*window\.saveExercise=function\(di,ei,exUid,libId,muscle,equipment\)\{.*?\n\s*\};\n(?=\s*const baseDay=)',
        "\n",
        "v104 saveExercise removal"
    )
)

# V15.0 wrapped the then-current save only to append loadMode and caused a
# second save/render. V15.1 writes loadMode inside the canonical transaction.
html=replace_script_body(
    html,"v150LoadModeRuntime",
    lambda body:remove_exact(
        body,
        r'\n\s*const baseSaveExerciseV150=saveExercise;\s*\n\s*saveExercise=function\(di,ei\)\{.*?\n\s*\};\n(?=\s*// ---------- Workout input ----------)',
        "\n",
        "v150 saveExercise wrapper removal"
    )
)

# V11.3's local-only modal reorder is completely superseded by V20.4.
# Keep openMoveExerciseV113 and its UI; only remove the old confirm handler.
html=replace_script_body(
    html,"v113ExerciseOrderRuntime",
    lambda body:remove_exact(
        body,
        r'\n\s*window\.confirmMoveExerciseV113=function\(di,ei\)\{.*?\n\s*\};\n(?=\s*const baseDayV113=)',
        "\n",
        "v113 confirmMove removal"
    )
)

after=counts(html)

if after["saveExercise"]!=1:
    raise RuntimeError("V20.9 expected one saveExercise authority: "+repr(after))
if after["confirmMoveExercise"]!=1:
    raise RuntimeError("V20.9 expected one confirmMove authority: "+repr(after))

critical=[
    "singleExerciseSave:true",
    "loadModeInputPreserved:true",
    "modalReorderUsesAtomicRpc:true",
    "moveExerciseKeepsExactScroll:true",
    "reorder_athlete_exercises",
    "__fjzRoutineSavingV200",
    "__fjzRoutineFlowV196",
    "routineBackdropCloseBlocked:true",
    "preservesSessionHistory:true",
    "openMoveExerciseV113",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.9 missing routine behavior markers: "+repr(missing))

runtime=r"""
<script id="v209RoutineAuthorityConsolidationRuntime">
(function(){
  window.__fjzV209={
    version:'20.9',
    canonicalExerciseSave:'v151',
    canonicalModalReorder:'v204',
    routineMutationGuard:'v200',
    routineBuilderFlow:'v196',
    legacyExerciseSavesRemoved:3,
    legacyModalReorderRemoved:1,
    behaviorChange:false
  };
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.9 routine authority consolidation")
print("V20.9 BEFORE:",before)
print("V20.9 AFTER:",after)
print("V20.9 removed legacy exercise saves: 3")
print("V20.9 removed legacy modal reorder confirmers: 1")
