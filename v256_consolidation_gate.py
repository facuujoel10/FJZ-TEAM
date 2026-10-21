import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.56 CONSOLIDATION GATE
# =========================================================
# Removes one proven-dead student-home DOM pass and freezes the expected
# authority/topology inventory. No feature behavior or backend changes.

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "render_assignments":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "start_assignments":len(re.findall(r"(?:window\.)?startWorkout\s*=",doc)),
        "finish_assignments":len(re.findall(r"(?:window\.)?finishWorkout\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
        "submit_checkin":len(re.findall(r"window\.submitWeeklyCheckin\s*=\s*async\s+function",doc)),
        "save_exercise":len(re.findall(r"(?:window\.)?saveExercise\s*=\s*(?:async\s+)?function",doc)),
        "coach_dashboard_defs":len(re.findall(r"function\s+renderCoachDashboardV80\s*\(",doc)),
    }

def edit_script(doc,script_id,transform):
    pat=re.compile(
        r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',
        re.S|re.I
    )
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.56 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.56 no script change")
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

submit_scripts=[]
for m in re.finditer(r'<script([^>]*)>(.*?)</script>',html,re.S|re.I):
    if re.search(r'window\.submitWeeklyCheckin\s*=\s*async\s+function',m.group(2)):
        idm=re.search(r'\bid=["\']([^"\']+)["\']',m.group(1),re.I)
        submit_scripts.append(idm.group(1) if idm else '(script sin id)')
print("V20.56 submitWeeklyCheckin authorities:",submit_scripts)

for marker in [
    'meta name="fjz-mobile-stability" content="20.55"',
    "studentSmartActionHub:true",
    "studentWeekFlow:true",
    "exercisePerformanceProgress:true",
    "coachWeeklyBrief:true",
    "cloudConfirmationBeforeSuccess:true",
    "confirmedCheckinSuccess:true",
    "pendingMarkerPreservedWhenLocalMissing:true",
    "modalReorderUsesAtomicRpc:true"
]:
    if marker not in html:
        raise RuntimeError("V20.56 missing current authority: "+marker)

# V100 still carried a legacy submitWeeklyCheckin wrapper that only repeated
# the 1–10 validation before delegating. V170 is now the canonical authority
# and already performs the same validation plus confirmed cloud persistence.
def patch_v100(body):
    start=body.find("  const previousSubmit=window.submitWeeklyCheckin;")
    end=body.find("  const previousOpenLibrary=window.openLibrary;",start)
    if start<0 or end<0:
        raise RuntimeError("V20.56 legacy V100 check-in wrapper boundaries missing")
    block=body[start:end]
    if "window.submitWeeklyCheckin=async function()" not in block or "previousSubmit.apply" not in block:
        raise RuntimeError("V20.56 V100 check-in wrapper shape changed")
    return body[:start]+body[end:]

html=edit_script(html,"v100CoreRuntime",patch_v100)

# The V20.43 card became obsolete once V20.45 made the Action Hub canonical.
# V20.45 explicitly removes #v243StudentNextStep on every Home render, so
# building it immediately beforehand is pure DOM churn.
def patch_v175(body):
    calls=body.count("injectStudentNextStepV243();")
    if calls!=2:
        raise RuntimeError("V20.56 expected two obsolete V20.43 calls, got "+str(calls))
    body=body.replace("      injectStudentNextStepV243();\n","",1)
    body=body.replace("            injectStudentNextStepV243();\n","",1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

# Add immutable consolidation marker.
html=html.replace("</head>",'<meta name="fjz-consolidation-gate" content="20.56">\n</head>',1)

after=metrics(html)

# Topology must remain fixed; consolidation only removes redundant function calls.
expected={
    "styles":1,
    "render_assignments":20,
    "channels":2,
    "timeouts":55,
    "rafs":24,
    "listeners":49,
    "mutation_observers":3,
    "performance_observers":0,
    "submit_checkin":1,
    "save_exercise":1,
    "coach_dashboard_defs":1,
}
for key,val in expected.items():
    if after.get(key)!=val:
        extra={"expected":val,"actual":after.get(key)}
        if key=="submit_checkin": extra["scripts"]=submit_scripts
        raise RuntimeError("V20.56 authority/topology mismatch "+key+": "+repr(extra))

for key in (
    "styles","render_assignments","start_assignments","finish_assignments",
    "channels","timeouts","rafs","listeners","mutation_observers",
    "performance_observers","save_exercise","coach_dashboard_defs"
):
    if after[key]!=before[key]:
        raise RuntimeError("V20.56 topology unexpectedly changed "+key+": "+repr({"before":before,"after":after}))

if before["submit_checkin"]!=2 or after["submit_checkin"]!=1:
    raise RuntimeError("V20.56 check-in authority consolidation mismatch: "+repr({"before":before["submit_checkin"],"after":after["submit_checkin"],"scripts":submit_scripts}))
if "injectStudentNextStepV243();" in html:
    raise RuntimeError("V20.56 obsolete V20.43 post-render call remains")
if re.search(r'<script[^>]*id=["\']v100CoreRuntime["\'][^>]*>[\s\S]*?window\.submitWeeklyCheckin\s*=\s*async\s+function',html,re.I):
    raise RuntimeError("V20.56 legacy V100 check-in authority remains")

# Critical feature/authority inventory.
critical=[
    'meta name="fjz-consolidation-gate" content="20.56"',
    'meta name="fjz-mobile-stability" content="20.55"',
    'meta name="fjz-exercise-performance-progress" content="20.54"',
    'meta name="fjz-student-week-flow" content="20.53"',
    'meta name="fjz-coach-priority-center" content="20.52"',
    'meta name="fjz-warmup-mobility-library" content="20.51"',
    "window.__fjzQueueSessionSyncV201",
    "cloudConfirmationBeforeSuccess:true",
    "pendingMarkerPreservedWhenLocalMissing:true",
    "confirmedCheckinSuccess:true",
    "professionalCheckinReview:true",
    "studentSmartActionHub:true",
    "coachPriorityStateV252",
    "exerciseProgressRowsV254",
    "Calentamiento / Activación",
    "Estiramientos / Movilidad",
    "v122FollowupPaymentsRuntime"
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.56 critical feature missing: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.56 consolidation gate")
print("V20.56 BEFORE:",before)
print("V20.56 AFTER:",after)
print("V20.56 removed legacy V100 check-in wrapper + obsolete V20.43 Home DOM pass; canonical authorities/topology frozen")
