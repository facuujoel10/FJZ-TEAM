import pathlib
import re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def counts(doc):
    return {
        "finish":len(re.findall(r"(?:window\\.)?finishWorkout\\s*=",doc)),
        "partial":len(re.findall(r"(?:window\\.)?confirmPartialSessionV106\\s*=",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

before=counts(html)

def edit_script(doc, script_id, pattern, label):
    rx=re.compile(
        r'(<script\\s+id=["\\']'+re.escape(script_id)+r'["\\'][^>]*>)(.*?)(</script>)',
        re.S|re.I,
    )
    m=rx.search(doc)
    if not m:
        raise RuntimeError(f"V20.8 missing script {script_id}")
    body=m.group(2)
    new_body,n=re.subn(pattern,"\\n",body,count=1,flags=re.S)
    if n!=1:
        raise RuntimeError(f"V20.8 could not remove exactly one {label} block from {script_id}: {n}")
    return doc[:m.start()]+m.group(1)+new_body+m.group(3)+doc[m.end():]

# V19.0: finalization double-tap wrappers are superseded by the V20.7 state machine.
html=edit_script(
    html,
    "v190SessionSaveBadgeHardeningRuntime",
    r"""\n\s*/\* Guard against double-taps / duplicate sessions while a save transaction.*?
\s*window\.__fjzV190=\{""",
    "V19.0 finish/partial",
)
# Restore marker consumed as the regex terminator.
html=html.replace(
    '<script id="v190SessionSaveBadgeHardeningRuntime">\n(function(){',
    '<script id="v190SessionSaveBadgeHardeningRuntime">\n(function(){',
    1,
)
# The previous substitution consumes window.__fjzV190={; put it back before its fields.
m=re.search(r'(<script\s+id=["\']v190SessionSaveBadgeHardeningRuntime["\'][^>]*>)(.*?)(</script>)',html,re.S|re.I)
if not m:
    raise RuntimeError("V20.8 V19.0 script disappeared")
b=m.group(2)
needle="\n    version:VERSION,\n    cloudConfirmedSessionSave:true,"
if needle not in b:
    raise RuntimeError("V20.8 V19.0 marker restoration anchor missing")
b=b.replace(needle,"\n  window.__fjzV190={"+needle,1)
html=html[:m.start()]+m.group(1)+b+m.group(3)+html[m.end():]

# V20.0: keep cloud confirmation, start reset, routine mutations and modal protection.
html=edit_script(
    html,
    "v200StabilityAuthorityRuntime",
    r"""\n\s*const baseFinishV200=.*?
\s*const baseStartV200=""",
    "V20.0 finish/partial",
)
# Restore the start-wrapper declaration consumed as terminator.
html=html.replace(
    "const baseStartV200=window.startWorkout||globalThis.startWorkout;",
    "const baseStartV200=window.startWorkout||globalThis.startWorkout;",
    1,
)
# If terminator was consumed, restore using unique following text.
m=re.search(r'(<script\s+id=["\']v200StabilityAuthorityRuntime["\'][^>]*>)(.*?)(</script>)',html,re.S|re.I)
if not m: raise RuntimeError("V20.8 V20.0 script disappeared")
b=m.group(2)
if "const baseStartV200=" not in b:
    anchor="\n  if(typeof baseStartV200==='function'){"
    if anchor not in b: raise RuntimeError("V20.8 V20.0 start anchor missing")
    b=b.replace(anchor,"\n  const baseStartV200=window.startWorkout||globalThis.startWorkout;"+anchor,1)
html=html[:m.start()]+m.group(1)+b+m.group(3)+html[m.end():]

# V20.2: keep targeted snapshot/RPC sync, retry machinery and start reset.
html=edit_script(
    html,
    "v201WorkoutSaveRuntime",
    r"""\n\s*/\* Final duplicate guard: once the local commit happened.*?
\s*const baseStartV201=""",
    "V20.2 finish/partial",
)
m=re.search(r'(<script\s+id=["\']v201WorkoutSaveRuntime["\'][^>]*>)(.*?)(</script>)',html,re.S|re.I)
if not m: raise RuntimeError("V20.8 V20.2 script disappeared")
b=m.group(2)
if "const baseStartV201=" not in b:
    anchor="\n  if(typeof baseStartV201==='function'){"
    if anchor not in b: raise RuntimeError("V20.8 V20.2 start anchor missing")
    b=b.replace(anchor,"\n  const baseStartV201=window.startWorkout||globalThis.startWorkout;"+anchor,1)
html=html[:m.start()]+m.group(1)+b+m.group(3)+html[m.end():]

# V20.4: keep atomic reorder, render guard and start reset.
html=edit_script(
    html,
    "v204WorkoutClosureReorderRuntime",
    r"""\n\s*// Final click guards\..*?
\s*// Only explicitly starting a new workout re-arms the save flow\.""",
    "V20.4 finish/partial",
)
# Restore comment terminator for readability.
m=re.search(r'(<script\s+id=["\']v204WorkoutClosureReorderRuntime["\'][^>]*>)(.*?)(</script>)',html,re.S|re.I)
if not m: raise RuntimeError("V20.8 V20.4 script disappeared")
b=m.group(2)
if "// Only explicitly starting a new workout re-arms the save flow." not in b:
    anchor="\n  const baseStartV204="
    if anchor not in b: raise RuntimeError("V20.8 V20.4 start anchor missing")
    b=b.replace(anchor,"\n  // Only explicitly starting a new workout re-arms the save flow."+anchor,1)
html=html[:m.start()]+m.group(1)+b+m.group(3)+html[m.end():]

# V20.5: keep previous-load UI, method history/reference, progress charts and render guard.
# V20.7 owns the final completion state machine.
html=edit_script(
    html,
    "v205CanonicalWorkoutProgressRuntime",
    r"""\n\s*// Canonical final save flow\. It bypasses every historical finish wrapper\..*?
\s*// Explicitly starting a new workout re-arms that day\.""",
    "V20.5 finish/partial",
)
m=re.search(r'(<script\s+id=["\']v205CanonicalWorkoutProgressRuntime["\'][^>]*>)(.*?)(</script>)',html,re.S|re.I)
if not m: raise RuntimeError("V20.8 V20.5 script disappeared")
b=m.group(2)
if "// Explicitly starting a new workout re-arms that day." not in b:
    anchor="\n  const baseStartV205="
    if anchor not in b: raise RuntimeError("V20.8 V20.5 start anchor missing")
    b=b.replace(anchor,"\n  // Explicitly starting a new workout re-arms that day."+anchor,1)
html=html[:m.start()]+m.group(1)+b+m.group(3)+html[m.end():]

after=counts(html)

# V20.7 must remain the final save authority and all supporting authorities must survive.
required=[
    'id="v207ConfirmedSessionCommitRuntime"',
    "cloudConfirmationBeforeSuccess:true",
    "retryUsesSameSessionId:true",
    "compactSessionRpc:true",
    "modalReorderUsesAtomicRpc:true",
    "previousWeightReferenceOnly:true",
    "methodPreviousReference:true",
    "professionalProgressCharts:true",
]
missing=[x for x in required if x not in html]
if missing:
    raise RuntimeError("V20.8 lost required behavior markers: "+repr(missing))

# Expected first-pass reduction: 10 finish assignments and 6 partial assignments.
if before["finish"]-after["finish"]!=10:
    raise RuntimeError(f"V20.8 unexpected finish reduction: {before} -> {after}")
if before["partial"]-after["partial"]!=6:
    raise RuntimeError(f"V20.8 unexpected partial reduction: {before} -> {after}")

window_marker=r"""
<script id="v208WorkoutSaveConsolidationMarker">
window.__fjzV208={
  version:'20.8',
  finalSaveAuthority:'V20.7',
  legacyFinishWrappersRemoved:10,
  legacyPartialWrappersRemoved:6,
  behaviorChangeIntended:false
};
</script>
"""
html=html.replace("</body>",window_marker+"\n</body>",1)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.8 workout save wrapper consolidation")
print("V20.8 BEFORE:",before)
print("V20.8 AFTER:",after)
print("V20.8 removed finish assignments:",before["finish"]-after["finish"])
print("V20.8 removed partial assignments:",before["partial"]-after["partial"])
