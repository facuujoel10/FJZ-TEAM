import pathlib,re,json

html=pathlib.Path("public/index.html").read_text(encoding="utf-8")

# Versioned TEAM FJZ symbols invoked as bare functions. Restricting to Vxx/Vxxx
# avoids browser/native names and makes this a targeted structural scan.
calls=set(re.findall(r"(?<![.\w$])([A-Za-z_$][\w$]*V\d{2,3})\s*\(",html))
defs=set(re.findall(r"(?:async\s+)?function\s+([A-Za-z_$][\w$]*V\d{2,3})\s*\(",html))
defs.update(re.findall(r"(?:window\.)?([A-Za-z_$][\w$]*V\d{2,3})\s*=\s*(?:async\s*)?function\s*\(",html))
defs.update(re.findall(r"(?:const|let|var)\s+([A-Za-z_$][\w$]*V\d{2,3})\s*=\s*(?:async\s*)?\([^)]*\)\s*=>",html))
defs.update(re.findall(r"window\.([A-Za-z_$][\w$]*V\d{2,3})\s*=\s*(?:async\s*)?\([^)]*\)\s*=>",html))

missing=sorted(calls-defs)
print("TEAM FJZ FINAL VERSIONED SYMBOL SCAN")
print(json.dumps({"calls":len(calls),"definitions":len(defs),"missing":missing},ensure_ascii=False,indent=2))
