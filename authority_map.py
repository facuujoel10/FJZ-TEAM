import pathlib
import re
import json

html=(pathlib.Path(__file__).resolve().parent/"public"/"index.html").read_text(encoding="utf-8")

rows=[]
for m in re.finditer(r"<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>",html,re.S|re.I):
    attrs=m.group("attrs") or ""
    body=m.group("body") or ""
    ident=re.search(r'id=["\']([^"\']+)["\']',attrs,re.I)
    sid=ident.group(1) if ident else "(anonymous)"
    counts={
        "finish":len(re.findall(r"(?:window\.)?finishWorkout\s*=",body)),
        "partial":len(re.findall(r"(?:window\.)?confirmPartialSessionV106\s*=",body)),
        "exercise":len(re.findall(r"(?:window\.)?workoutExercise\s*=",body)),
        "render":len(re.findall(r"(?:window\.)?render\s*=",body)),
        "showModal":len(re.findall(r"(?:window\.)?showModal\s*=",body)),
        "closeModal":len(re.findall(r"(?:window\.)?closeModal\s*=",body)),
        "channel":len(re.findall(r"\.channel\s*\(",body)),
    }
    if any(counts.values()):
        rows.append({"script":sid,**counts})

print("TEAM FJZ AUTHORITY MAP")
print(json.dumps(rows,indent=2,ensure_ascii=False))
