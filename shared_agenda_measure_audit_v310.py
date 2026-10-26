import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()
m94=re.search(r'<script[^>]*id=["\']v94NutritionTrackingRuntime["\'][^>]*>(.*?)</script>',html,re.S|re.I)
m310=re.search(r'<script[^>]*id=["\']v310SharedStudentAgendaRuntime["\'][^>]*>(.*?)</script>',html,re.S|re.I)
v94=m94.group(1) if m94 else ""
v310=m310.group(1) if m310 else ""
checks={
 "release":tuple(map(int,release.split("."))) >= (21,10),
 "meta":'meta name="fjz-shared-agenda-measure-fix" content="21.10"' in html,
 "v94":bool(v94),
 "v310":bool(v310),
 "measure_row_authority":"card.querySelectorAll('.v93-measure-row')" in v94,
 "arm_dedupe":"armKept=false,thighKept=false" in v94,
 "right_side_removed":"if(right||armKept)" in v94 and "if(right||thighKept)" in v94,
 "general_labels":"strong.textContent='Brazo'" in v94 and "strong.textContent='Muslo'" in v94,
 "student_auth_lookup":".eq('user_id',currentUser.id)" in v310,
 "scoped_schedule":".from('athlete_schedule')" in v310 and ".eq('athlete_id',athlete.id)" in v310,
 "scoped_reminders":".from('athlete_reminders')" in v310,
 "home_upcoming":"upcomingReminderOnHome:true" in v310 and "v310StudentAgendaHome" in v310,
 "agenda_future":"futureReminderList:true" in v310 and "Próximos recordatorios" in v310,
 "shared":"sharedCoachStudentAgenda:true" in v310,
 "no_schema_change":"noSchemaChange:true" in v310,
}
failed=[k for k,v in checks.items() if not v]
print("TEAM FJZ V21.10 SHARED AGENDA + MEASUREMENTS AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.10 SHARED AGENDA + MEASUREMENTS AUDIT FAILED")
print("TEAM FJZ V21.10 SHARED AGENDA + MEASUREMENTS AUDIT OK")
