import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

issues=[]

def require(marker,label=None):
    if marker not in html:
        issues.append(label or ("missing: "+marker))

# Core runtime / release
for marker in [
    'meta name="fjz-final-product-layer" content="20.90"',
    'meta name="fjz-new-feature-hardening" content="20.91"',
    "cloudConfirmationBeforeSuccess:true",
    "duplicateSaveByDesignBlocked:true",
    "retryUsesSameSessionId:true",
    "greenCheckOnConfirmedSaves:true",
    "duplicateAsyncSaveGuard:true",
    "finalProductLayerV290:true",
    "prBannerV291:true",
    "robustPrDetectionV291:true",
    "localizedWeightParsingV291:true",
    "normalizedExercisePrKeyV291:true",
    "habitAssignmentDateAwareV291:true",
    "prSessionDedupV291:true",
    "prSafeStorageKeyV291:true",
    "sessionExerciseCommentsV287:true",
]:
    require(marker)

# New feature behavior
for marker in [
    "NUEVO PESO · NUEVO PR",
    "NUEVO RÉCORD DE VOLUMEN",
    "if(items.length<2)return;",
    "Number(last.bestLoad)>0",
    "Number.isFinite(parsed)",
    "const perSession=new Map();",
    "return encodeURIComponent(raw);",
    "habitEligibleOnV291",
    "total+=eligible.length",
    "done.size===eligible.length",
    "ASISTENTE DE CHECK-IN",
    "Riesgo de desconexión",
    "sin mensajes automáticos",
]:
    require(marker)

# Finish/save UX
for marker in [
    "Finalizar entrenamiento",
    "Guardar y finalizar",
    "Sesión guardada con éxito",
    ".v207-save-state .v207-save-title",
    ".v207-save-state .v207-save-copy",
    ".modal-head h3",
    ".modal .pill-row>.btn",
]:
    require(marker)

# Mobile / profile / coach review / comments
for marker in [
    "#v266CoachWorkspace .v266-quick-actions",
    "display:none!important;",
    "#coachStudentTabs",
    "v241-difficulty-grid",
    "exerciseComment",
    "sessionExerciseCommentsV287:true",
]:
    require(marker)

# Retired features must stay retired.
for marker in [
    "sendAutomaticMessageV290",
    "sendAutomaticMessageV291",
    "scheduledMessageV291",
    "automaticMessagingV291",
]:
    if marker in html:
        issues.append("forbidden automatic messaging marker: "+marker)

# Static duplicate IDs.
ids=re.findall(r'\bid=["\']([^"\']+)["\']',html,re.I)
dups=sorted({x for x in ids if ids.count(x)>1})
if dups:
    issues.append("duplicate static ids: "+repr(dups[:20]))

metrics={
    "styles":len(re.findall(r"<style\b",html,re.I)),
    "renders":len(re.findall(r"(?:window\.)?render\s*=",html)),
    "channels":len(re.findall(r"\.channel\s*\(",html)),
    "timeouts":len(re.findall(r"setTimeout\s*\(",html)),
    "intervals":len(re.findall(r"setInterval\s*\(",html)),
    "rafs":len(re.findall(r"requestAnimationFrame\s*\(",html)),
    "listeners":len(re.findall(r"addEventListener\s*\(",html)),
    "mutation_observers":len(re.findall(r"new\s+MutationObserver",html)),
    "performance_observers":len(re.findall(r"new\s+PerformanceObserver",html)),
    "smooth_scroll":len(re.findall(r"behavior\s*:\s*['\"]smooth['\"]",html)),
    "transition_all":len(re.findall(r"transition\s*:\s*all\b",html,re.I)),
}
limits={
    "styles":1,
    "renders":18,
    "channels":2,
    "timeouts":55,
    "intervals":0,
    "listeners":52,
    "mutation_observers":3,
    "performance_observers":0,
    "smooth_scroll":0,
    "transition_all":0,
}
for k,v in limits.items():
    if k in ("renders","channels","timeouts","listeners","mutation_observers"):
        if metrics[k]>v: issues.append(f"{k} regression: {metrics[k]} > {v}")
    else:
        if metrics[k]!=v: issues.append(f"{k} regression: {metrics[k]} != {v}")

# Sensitive old runtime routes should remain quarantined.
for pattern,label in [
    (r"coachTab\s*=\s*['\"]music['\"]","music route assignment"),
    (r"studentTab\s*=\s*['\"]music['\"]","student music route assignment"),
    (r"\.channel\s*\([^)]*music","music realtime channel"),
    (r"\.channel\s*\([^)]*payment","payment realtime channel"),
]:
    if re.search(pattern,html,re.I):
        issues.append("retired runtime survived: "+label)

# Responsive breakpoints must still exist.
for bp in ["@media(max-width:760px)","@media(max-width:430px)","@media(max-width:360px)","@media(min-width:1000px)"]:
    require(bp,"missing responsive breakpoint "+bp)

print("TEAM FJZ FINAL RELEASE GATE")
print(json.dumps({
    "release":release,
    "metrics":metrics,
    "duplicate_ids":dups,
    "issues":issues,
},indent=2,ensure_ascii=False))

if tuple(map(int,release.split("."))) < (20,91):
    raise SystemExit("Release older than 20.91")
if issues:
    raise SystemExit("FINAL RELEASE GATE FAILED: "+repr(issues))

print("TEAM FJZ FINAL RELEASE GATE OK")
