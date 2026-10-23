import pathlib,re,json

html=pathlib.Path("public/index.html").read_text(encoding="utf-8")

# Versioned TEAM FJZ symbols invoked as bare functions. Restricting to Vxx/Vxxx
# avoids browser/native names and makes this a targeted structural scan.
calls=set(re.findall(r"(?<![.\w$])([A-Za-z_$][\w$]*V\d{2,3})\s*\(",html))
defs=set(re.findall(r"(?:async\s+)?function\s+([A-Za-z_$][\w$]*V\d{2,3})\s*\(",html))
defs.update(re.findall(r"(?:window\.)?([A-Za-z_$][\w$]*V\d{2,3})\s*=\s*(?:async\s*)?function\s*\(",html))
# Count every explicit assignment authority as a definition too. This covers
# captured wrappers such as const oldRenderV93=render and final compatibility
# assignments such as window.renderCoachFocusV235=...
defs.update(re.findall(r"(?:const|let|var)\s+([A-Za-z_$][\w$]*V\d{2,3})\s*=",html))
defs.update(re.findall(r"window\.([A-Za-z_$][\w$]*V\d{2,3})\s*=",html))
defs.update(re.findall(r"(?<![.\w$])([A-Za-z_$][\w$]*V\d{2,3})\s*=",html))

missing=sorted(calls-defs)
print("TEAM FJZ FINAL VERSIONED SYMBOL SCAN")
print(json.dumps({"calls":len(calls),"definitions":len(defs),"missing":missing},ensure_ascii=False,indent=2))

# An unresolved versioned bare call is exactly the class of regression that
# caused the Coach priority/calendar issue. Make it a hard preflight gate.
if missing:
    raise SystemExit("Unresolved TEAM FJZ versioned symbols: "+repr(missing))
print("TEAM FJZ FINAL VERSIONED SYMBOL SCAN OK")
