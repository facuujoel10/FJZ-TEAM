import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()
m=re.search(r'<script[^>]*id=["\']v314OperationalIntegrityUxRuntime["\'][^>]*>(.*?)</script>',html,re.S|re.I)
body=m.group(1) if m else ""
checks={
 "release":tuple(map(int,release.split("."))) >= (21,14),
 "meta":'meta name="fjz-operational-integrity-ux" content="21.14"' in html,
 "runtime":bool(body),
 "coach_link_state":"coachAgendaLinkState:true" in body,
 "missing_account_warning":"warnsWhenStudentAccountMissing:true" in body and "Alumno sin cuenta vinculada" in body,
 "linked_account_ok":"Cuenta de alumno vinculada" in body,
 "student_section_always":"studentAgendaSectionAlwaysVisible:true" in body and "Fechas agendadas" in body,
 "direct_student_read":"__fjzLoadOwnAppointmentsV312" in body,
 "review_authority_preserved":"reviewAuthorityPreserved:true" in body,
 "agenda_authority_preserved":"directAgendaAuthorityPreserved:true" in body,
 "no_timer":"setInterval(" not in body and "setTimeout(" not in body,
 "no_listener":"addEventListener(" not in body,
 "no_observer":"MutationObserver" not in body and "PerformanceObserver" not in body,
}
failed=[k for k,v in checks.items() if not v]
print("TEAM FJZ V21.14 OPERATIONAL INTEGRITY UX AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.14 OPERATIONAL INTEGRITY UX AUDIT FAILED")
print("TEAM FJZ V21.14 OPERATIONAL INTEGRITY UX AUDIT OK")
