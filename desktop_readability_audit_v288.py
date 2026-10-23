import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def vt(v):
    try:return tuple(int(x) for x in v.split("."))
    except:return (0,)

required=[
 'meta name="fjz-desktop-coach-readability" content="20.88"',
 ".v225-student-list .student-main>div>strong",
 "font-size:15px!important",
 ".v225-student-list .student-main>div>.muted.tiny",
 "font-size:12.5px!important",
 ".v80-attention-item h4",
 "font-size:14px!important",
 ".v80-attention-item .muted.tiny",
 "font-size:12px!important",
 'meta name="fjz-session-exercise-comments" content="20.87"'
]
missing=[x for x in required if x not in html]
metrics={
 "styles":len(re.findall(r"<style\b",html,re.I)),
 "renders":len(re.findall(r"(?:window\.)?render\s*=",html)),
 "intervals":len(re.findall(r"setInterval\s*\(",html)),
 "listeners":len(re.findall(r"addEventListener\s*\(",html)),
 "mutation_observers":len(re.findall(r"new\s+MutationObserver",html)),
 "performance_observers":len(re.findall(r"new\s+PerformanceObserver",html)),
}
logic={
 "desktop_only":"@media(min-width:1000px)" in html,
 "student_name_large":".v225-student-list .student-main>div>strong" in html,
 "student_subcopy_large":".v225-student-list .student-main>div>.muted.tiny" in html,
 "attention_title_large":".v80-attention-item h4" in html,
 "attention_body_large":".v80-attention-item .muted.tiny" in html,
}
print("TEAM FJZ V20.88 DESKTOP READABILITY AUDIT")
print(json.dumps({"release":release,"missing":missing,"logic":logic,"metrics":metrics},indent=2,ensure_ascii=False))
if vt(release)<vt("20.88"): raise SystemExit("Release older than V20.88")
if missing: raise SystemExit("Missing V20.88 markers: "+repr(missing))
if not all(logic.values()): raise SystemExit("V20.88 logic failed")
if metrics["styles"]!=1 or metrics["renders"]>18 or metrics["intervals"]!=0 or metrics["listeners"]>52 or metrics["mutation_observers"]>3 or metrics["performance_observers"]!=0:
    raise SystemExit("Topology regression: "+repr(metrics))
print("TEAM FJZ V20.88 DESKTOP READABILITY AUDIT OK")
