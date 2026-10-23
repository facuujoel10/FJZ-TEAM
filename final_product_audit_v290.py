import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

required=[
 'meta name="fjz-final-product-layer" content="20.90"',
 "finalProductLayerV290:true",
 "todayDashboardV290:true",
 "habitStreaksV290:true",
 "prAchievementsV290:true",
 "engagementRiskV290:true",
 "checkinAssistantV290:true",
 "athlete_habits",
 "nutrition_habit_logs",
 "toggleHabitV290",
 "addHabitV290",
 "removeHabitV290",
 "Riesgo de desconexión",
 "ASISTENTE DE CHECK-IN",
 "sin mensajes automáticos"
]
missing=[x for x in required if x not in html]

forbidden=[
 "sendAutomaticMessageV290",
 "autoMessageV290",
 "scheduledMessageV290",
 "automaticMessagingV290"
]
survived=[x for x in forbidden if x in html]

metrics={
 "styles":len(re.findall(r"<style\\b",html,re.I)),
 "renders":len(re.findall(r"(?:window\\.)?render\\s*=",html)),
 "channels":len(re.findall(r"\\.channel\\s*\\(",html)),
 "timeouts":len(re.findall(r"setTimeout\\s*\\(",html)),
 "intervals":len(re.findall(r"setInterval\\s*\\(",html)),
 "listeners":len(re.findall(r"addEventListener\\s*\\(",html)),
 "mutation_observers":len(re.findall(r"new\\s+MutationObserver",html)),
 "performance_observers":len(re.findall(r"new\\s+PerformanceObserver",html)),
}

print("TEAM FJZ V20.90 FINAL PRODUCT AUDIT")
print(json.dumps({"release":release,"missing":missing,"forbidden":survived,"metrics":metrics},indent=2,ensure_ascii=False))

if tuple(map(int,release.split("."))) < (20,90): raise SystemExit("Release older than 20.90")
if missing: raise SystemExit("Missing V20.90 markers: "+repr(missing))
if survived: raise SystemExit("Automatic-message feature survived: "+repr(survived))
if metrics["styles"]!=1: raise SystemExit("Stylesheet regression")
if metrics["renders"]>18: raise SystemExit("Render regression")
if metrics["intervals"]!=0: raise SystemExit("Interval regression")
if metrics["listeners"]>52: raise SystemExit("Listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("MutationObserver regression")
if metrics["performance_observers"]!=0: raise SystemExit("PerformanceObserver regression")

print("TEAM FJZ V20.90 FINAL PRODUCT AUDIT OK")
