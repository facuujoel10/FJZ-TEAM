import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()
m175=re.search(r'<script[^>]*id=["\']v175ProfileAgendaCoachCenterRuntime["\'][^>]*>(.*?)</script>',html,re.S|re.I)
v175=m175.group(1) if m175 else ""
checks={
 "release":tuple(map(int,release.split("."))) >= (21,7),
 "meta":'meta name="fjz-coach-profile-sync-ui" content="21.07"' in html,
 "v175":bool(v175),
 "no_actualizando":"Actualizando…" not in v175,
 "silent_success":"textContent='';" in v175,
 "failure_only_warning":"Datos parciales · la ficha sigue disponible" in v175,
 "instant_profile_retained":"profileHtmlV114(immediate)" in html,
}
failed=[k for k,v in checks.items() if not v]
print("TEAM FJZ V21.07 COACH PROFILE SYNC UI AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.07 COACH PROFILE SYNC UI AUDIT FAILED")
print("TEAM FJZ V21.07 COACH PROFILE SYNC UI AUDIT OK")
