import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

required=[
 'meta name="fjz-session-resilience" content="20.94"',
 '@supabase/supabase-js@2.118.0/+esm',
 "signOut({scope:'local'})",
 "handleSession=handleSessionV294",
 "retryActiveSessionV294",
 "recoverUnexpectedSignedOutV294",
 "showSessionRecoveryV294",
 "La autenticación fue correcta, pero falló una carga de datos",
 "No borramos tu sesión ni tus datos",
 "persistSession:true",
 "autoRefreshToken:true",
]
missing=[x for x in required if x not in html]

checks={
 "supabase_client_pinned":"@supabase/supabase-js@2/+esm" not in html and "@supabase/supabase-js@2.118.0/+esm" in html,
 "logout_local_only":re.search(r"auth\.signOut\(\s*\)",html) is None and "signOut({scope:'local'})" in html,
 "unexpected_signedout_verified":"recoverUnexpectedSignedOutV294" in html and "auth.getSession()" in html,
 "core_load_failure_keeps_session":"La autenticación fue correcta, pero falló una carga de datos" in html,
 "boot_failure_not_config_reset":"No borramos tu sesión ni tus datos" in html,
 "login_normalized":".trim().toLowerCase()" in html,
}
metrics={
 "styles":len(re.findall(r"<style\b",html,re.I)),
 "renders":len(re.findall(r"(?:window\.)?render\s*=",html)),
 "channels":len(re.findall(r"\.channel\s*\(",html)),
 "timeouts":len(re.findall(r"setTimeout\s*\(",html)),
 "intervals":len(re.findall(r"setInterval\s*\(",html)),
 "listeners":len(re.findall(r"addEventListener\s*\(",html)),
 "mutation_observers":len(re.findall(r"new\s+MutationObserver",html)),
 "performance_observers":len(re.findall(r"new\s+PerformanceObserver",html)),
}

print("TEAM FJZ V20.94 AUTH SESSION RESILIENCE AUDIT")
print(json.dumps({"release":release,"missing":missing,"checks":checks,"metrics":metrics},indent=2,ensure_ascii=False))

if tuple(map(int,release.split("."))) < (20,94): raise SystemExit("Release older than 20.94")
if missing: raise SystemExit("Missing V20.94 markers: "+repr(missing))
if not all(checks.values()): raise SystemExit("V20.94 auth check failed: "+repr(checks))
if metrics["styles"]!=1: raise SystemExit("Stylesheet regression")
if metrics["renders"]>18: raise SystemExit("Render regression")
if metrics["intervals"]!=0: raise SystemExit("Interval regression")
if metrics["listeners"]>52: raise SystemExit("Listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("Observer regression")
if metrics["performance_observers"]!=0: raise SystemExit("Performance observer regression")
print("TEAM FJZ V20.94 AUTH SESSION RESILIENCE AUDIT OK")
