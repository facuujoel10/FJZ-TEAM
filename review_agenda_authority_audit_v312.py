import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()
m=re.search(r'<script[^>]*id=["\']v312ReviewAgendaAuthorityRuntime["\'][^>]*>(.*?)</script>',html,re.S|re.I)
body=m.group(1) if m else ""
checks={
 "release":tuple(map(int,release.split("."))) >= (21,12),
 "meta":'meta name="fjz-review-agenda-authority" content="21.12"' in html,
 "runtime":bool(body),
 "v311_exposed":"__fjzProfileReviewedAthleteV311" in html,
 "legacy_review_cloud":"profileReviewedV312" in html and "Perfil 360 revisado" in html,
 "hub_cloud_aware":"Revisado en nube" in html,
 "no_duplicate_first":"noDuplicateFirstReviewAfterReload:true" in body,
 "student_direct_lookup":".eq('user_id',currentUser.id)" in body,
 "reminder_scoped":".from('athlete_reminders')" in body and ".eq('athlete_id',athlete.id)" in body,
 "schedule_scoped":".from('athlete_schedule')" in body,
 "student_card":"PRÓXIMA FECHA AGENDADA" in body and "v312NextAppointment" in body,
 "render_student_hook":"baseRenderStudentV312" in body,
 "no_schema_change":"noSchemaChange:true" in body,
}
failed=[k for k,v in checks.items() if not v]
print("TEAM FJZ V21.12 REVIEW + AGENDA AUTHORITY AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.12 REVIEW + AGENDA AUTHORITY AUDIT FAILED")
print("TEAM FJZ V21.12 REVIEW + AGENDA AUTHORITY AUDIT OK")
