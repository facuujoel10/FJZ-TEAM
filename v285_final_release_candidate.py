import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "intervals":len(re.findall(r"setInterval\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

before=metrics(html)

for marker in [
    'meta name="fjz-final-calendar-authority" content="20.84"',
    'meta name="fjz-mobile-legacy-isolation" content="20.83"',
    "duplicateAsyncSaveGuard:true",
    "specificProgressAlerts:true",
    "finalMonthlyCalendarAuthorityV284:true",
]:
    if marker not in html:
        raise RuntimeError("V20.85 prerequisite missing "+marker)

# Payments/cobranzas were explicitly postponed. Remove every actionable legacy
# button that can still assign coachTab='payments'. Underlying historical code
# can remain inert for compatibility, but no UI or alert may navigate there.
payment_btn_rx=re.compile(
    r'<button\b[^>]*onclick="[^"]*coachTab\s*=\s*\\?[\'\"]payments\\?[\'\"][^"]*"[^>]*>.*?</button>',
    re.I|re.S
)
html,payment_buttons_removed=payment_btn_rx.subn("",html)

# Remove the old alert filter item (all historical quoting/comma variants).
for token in [
    ",['payment','Pagos']",
    "['payment','Pagos'],",
    ",[\'payment\',\'Pagos\']",
    "[\'payment\',\'Pagos\'],",
]:
    html=html.replace(token,"")

# A stale historical payment alert should never open a retired route. Send it
# safely back to the Coach dashboard instead.
old_payment_alert="""    if(kind==='payment'){
      coachTab='payments';
      render();
      return;
    }"""
new_payment_alert="""    if(kind==='payment'){
      coachTab='dashboard';
      render();
      return;
    }"""
html,payment_alert_patched=re.subn(re.escape(old_payment_alert),lambda _m:new_payment_alert,html,count=1)

# Remove any surviving direct payment assignment in inline/template handlers.
# This is intentionally limited to assignments, never equality checks.
html,payment_assignments_removed=re.subn(
    r"coachTab\s*=\s*\\?(['\"])payments\\?\1\s*;?",
    "coachTab='dashboard';",
    html
)

# Mark the existing mobile recovery authority as the final route policy.
pat=re.compile(r'(<script[^>]*\bid=["\']v283MobileLegacyIsolationRuntime["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
m=pat.search(html)
if not m:
    raise RuntimeError("V20.85 missing V283 runtime")
body=m.group(2)
if "legacyPaymentRoutesRemoved:true" not in body:
    anchor="    productionUntouched:true,"
    if anchor not in body:
        raise RuntimeError("V20.85 V283 marker anchor missing")
    body=body.replace(anchor,"    paymentsDeferred:true,\n    legacyPaymentRoutesRemoved:true,\n"+anchor,1)
html=html[:m.start(2)]+body+html[m.end(2):]

html=html.replace("</head>",'<meta name="fjz-final-release-candidate" content="20.85">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.85 topology changed "+key+": "+repr({"before":before,"after":after}))

# No direct assignment to the retired route may remain.
remaining_payment_assignments=re.findall(r"coachTab\s*=\s*\\?(['\"])payments\\?\1",html)
if remaining_payment_assignments:
    raise RuntimeError("V20.85 payment route assignment survived")

for marker in [
    'meta name="fjz-final-release-candidate" content="20.85"',
    "paymentsDeferred:true",
    "legacyPaymentRoutesRemoved:true",
    "finalMonthlyCalendarAuthorityV284:true",
    "duplicateAsyncSaveGuard:true",
    "specificProgressAlerts:true",
]:
    if marker not in html:
        raise RuntimeError("V20.85 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.85 final release-candidate hardening")
print("V20.85 BEFORE:",before)
print("V20.85 AFTER:",after)
print("V20.85 payment buttons removed:",payment_buttons_removed)
print("V20.85 payment alert patched:",payment_alert_patched)
print("V20.85 direct payment assignments rerouted:",payment_assignments_removed)
