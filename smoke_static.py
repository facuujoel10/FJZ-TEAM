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

ids=re.findall(r'\bid=["\']([^"\']+)["\']',html,re.I)
dups=sorted({x for x in ids if ids.count(x)>1})
if dups:
    errors.append("duplicate static DOM ids: "+", ".join(dups[:12]))

if "cloudConfirmationBeforeSuccess:true" not in html:
    errors.append("confirmed-save state machine marker missing")
if "retryUsesSameSessionId:true" not in html:
    errors.append("idempotent retry marker missing")
if "previousWeightReferenceOnly:true" not in html:
    errors.append("previous-load reference-only marker missing")
if "methodPreviousReference:true" not in html:
    errors.append("method previous reference marker missing")

env=os.environ.get("TEAM_FJZ_ENV","production").strip().lower()
if env=="staging-local":
    require("productionNetworkBlocked:true","staging network kill-switch missing")
    require("syntheticDataOnly:true","staging synthetic-data marker missing")
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
print(f"Environment: {env}")
print(f"Styles: {style_count}")
print(f"Static IDs: {len(ids)}")
print("Critical workout/routine/tracking/progress markers: OK")
