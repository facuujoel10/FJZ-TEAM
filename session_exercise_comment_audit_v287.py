import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def vt(v):
    try:return tuple(int(x) for x in v.split("."))
    except Exception:return (0,)

required=[
 'meta name="fjz-session-exercise-comments" content="20.87"',
 "exerciseFeedbackSnapshotInSessionV287:true",
 "exerciseCommentsVisiblePerSessionV287:true",
 "historicalExerciseCommentFallbackV287:true",
 "sessionExerciseFeedbackSnapshotV287",
 "exerciseFeedbackForSessionV287",
 "exerciseCommentHtmlV287",
 "window.sessionDetails=async function",
 "loadExerciseFeedbackV73(false)",
 "r.exerciseFeedback=matches.map",
 "v287-exercise-comments",
 'meta name="fjz-typography-mobile-nav-feedback" content="20.86"',
 "duplicateAsyncSaveGuard:true",
 "finalMonthlyCalendarAuthorityV284:true",
]
missing=[x for x in required if x not in html]

logic={
 "snapshot_before_commit":bool(re.search(r"const session=window\.__fjzSaveSessionV205\?\.\(pack\);.*?sessionExerciseFeedbackSnapshotV287\(pack,session\);.*?attachMethodHistoryV207",html,re.S)),
 "session_detail_loads_feedback":"loadExerciseFeedbackV73(false)" in html,
 "exercise_match_by_uid":"String(x?.exercise_uid||'')!==String(r?.exerciseUid||'')" in html,
 "day_match":"String(x.workout_day_id)===String(ss.dayId)" in html or "String(x.workout_day_id)===String(pack.d.id)" in html,
 "time_window":"18*60*60*1000" in html,
 "snapshot_preferred":"Array.isArray(r?.exerciseFeedback)" in html,
 "comment_status_visible":"Revisado" in html and "Pendiente" in html,
 "mobile_comment_wrap":"overflow-wrap:anywhere" in html,
}

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
}

print("TEAM FJZ V20.87 SESSION EXERCISE COMMENT AUDIT")
print(json.dumps({"release":release,"missing":missing,"logic":logic,"metrics":metrics},indent=2,ensure_ascii=False))

if vt(release)<vt("20.87"): raise SystemExit("Release older than V20.87: "+release)
if missing: raise SystemExit("Missing V20.87 markers: "+repr(missing))
if not all(logic.values()): raise SystemExit("V20.87 logic audit failed: "+repr(logic))
if metrics["styles"]!=1: raise SystemExit("Stylesheet regression")
if metrics["renders"]>18: raise SystemExit("Render assignment regression")
if metrics["intervals"]!=0: raise SystemExit("Interval regression")
if metrics["listeners"]>52: raise SystemExit("Listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("PerformanceObserver regression")

print("TEAM FJZ V20.87 SESSION EXERCISE COMMENT AUDIT OK")
