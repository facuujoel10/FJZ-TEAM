import os
import pathlib
import re
import sys

ROOT=pathlib.Path(__file__).resolve().parent
HTML=ROOT/"public"/"index.html"
errors=[]

if not HTML.exists():
    errors.append("public/index.html missing")
    html=""
else:
    html=HTML.read_text(encoding="utf-8")

def require(marker,label=None):
    if marker not in html:
        errors.append(label or f"missing marker: {marker}")

require("TEAM FJZ","TEAM FJZ identity missing")
require("__fjzV207","V20.7 confirmed save runtime missing")
require("__fjzV205","V20.5 workout/progress runtime missing")
require("__fjzV204","V20.4 reorder/runtime guard missing")
require("__fjzV198","method panel persistence missing")
require("v137-method-panel","method tracking panel missing")
require("renderTrackingStudent","student tracking renderer missing")
require("renderTrackingCoach","coach tracking renderer missing")
require("nutrition","nutrition surface missing")
require("progress","progress surface missing")

style_count=len(re.findall(r"<style\b",html,re.I))
if style_count!=1:
    errors.append(f"expected 1 consolidated stylesheet, found {style_count}")

static_dom=re.sub(r"<script\b.*?</script>","",html,flags=re.S|re.I)
static_dom=re.sub(r"<style\b.*?</style>","",static_dom,flags=re.S|re.I)
ids=re.findall(r'\bid=["\']([^"\']+)["\']',static_dom,re.I)
dups=sorted({x for x in ids if ids.count(x)>1})
if dups:
    errors.append("duplicate literal DOM ids: "+", ".join(dups[:12]))

if "cloudConfirmationBeforeSuccess:true" not in html:
    errors.append("confirmed-save state machine marker missing")
if "retryUsesSameSessionId:true" not in html:
    errors.append("idempotent retry marker missing")
if "previousWeightReferenceOnly:true" not in html:
    errors.append("previous-load reference-only marker missing")
if "methodPreviousReference:true" not in html:
    errors.append("method previous reference marker missing")

# V20.8 is an optional consolidation layer on the feature/develop branch.
# If present, it must reduce dead completion wrappers without replacing V20.7.
if "__fjzV208" in html:
    finish_count=len(re.findall(r"(?:window\\.)?finishWorkout\\s*=",html))
    partial_count=len(re.findall(r"(?:window\\.)?confirmPartialSessionV106\\s*=",html))
    if finish_count > 5:
        errors.append(f"V20.8 finishWorkout consolidation incomplete: {finish_count}")
    if partial_count > 6:
        errors.append(f"V20.8 partial-save consolidation incomplete: {partial_count}")
    if html.rfind('id="v207ConfirmedSessionCommitRuntime"') > html.rfind('id="v208WorkoutSaveConsolidationMarker"'):
        errors.append("V20.8 marker must come after V20.7 final save runtime")
    if "finalSaveAuthority:'V20.7'" not in html:
        errors.append("V20.8 lost V20.7 final-save authority marker")

env=os.environ.get("TEAM_FJZ_ENV","").strip().lower()
artifact_is_staging_local=(
    "productionNetworkBlocked:true" in html
    or "syntheticDataOnly:true" in html
    or "STAGING</b> · DATOS DE PRUEBA" in html
)
effective_env="staging-local" if artifact_is_staging_local else (env or "production")

if artifact_is_staging_local:
    require("productionNetworkBlocked:true","staging network kill-switch missing")
    require("cloudDisabled:true","staging cloud-disabled marker missing")
    require("syntheticDataOnly:true","staging synthetic-data marker missing")
    require("workoutSaveSimulator:true","staging workout save simulator missing")
    require("__fjzStagingSaveSimulator","staging save simulator API missing")
    require("STAGING</b> · DATOS DE PRUEBA","staging banner missing")
    for forbidden in (
        "cujipwacwwpejhqjhnkr",
        "sb_publishable_TWE-dICHv3QemUtM302CTg_8i2zVx3G",
    ):
        if forbidden in html:
            errors.append("production backend reference leaked into staging artifact")

if errors:
    print("TEAM FJZ SMOKE TEST FAILED")
    for e in errors:
        print("- "+e)
    sys.exit(1)

print("TEAM FJZ SMOKE TEST OK")
print(f"Environment: {effective_env}")
print(f"Styles: {style_count}")
print(f"Static IDs: {len(ids)}")
print("Critical workout/routine/tracking/progress markers: OK")
