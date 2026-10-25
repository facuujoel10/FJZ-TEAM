import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

required=[
 'meta name="fjz-password-recovery-hardening" content="20.93"',
 "resetPasswordForEmail",
 "event==='PASSWORD_RECOVERY'",
 "window.__fjzRecoveryModeV293",
 "window.__fjzRecoverySendBusyV293",
 "window.__fjzRecoverySaveBusyV293",
 "updateUser({password:a})",
 'minlength="8"',
 'autocomplete="new-password"',
 "history.replaceState",
 "El enlace de recuperación venció",
 "Si ese email corresponde a una cuenta",
]
missing=[x for x in required if x not in html]

checks={
 "recovery_before_signed_in":"event==='PASSWORD_RECOVERY'" in html and "!window.__fjzRecoveryModeV293" in html,
 "no_late_duplicate_listener":"__fjzV81RecoveryListener" not in html,
 "reset_redirect_current_app":"options.redirectTo=location.origin+location.pathname" in html,
 "reset_busy_guard":"if(window.__fjzRecoverySendBusyV293)return;" in html,
 "save_busy_guard":"if(window.__fjzRecoverySaveBusyV293)return;" in html,
 "password_min_8":"if(a.length<8)" in html,
 "password_match":"if(a!==b)" in html,
 "expired_link_fallback":"El enlace de recuperación venció" in html,
 "token_cleanup":"history.replaceState" in html,
}

metrics={
 "styles":len(re.findall(r"<style\b",html,re.I)),
 "renders":len(re.findall(r"(?:window\.)?render\s*=",html)),
 "channels":len(re.findall(r"\.channel\s*\(",html)),
 "timeouts":len(re.findall(r"setTimeout\s*\(",html)),
 "intervals":len(re.findall(r"setInterval\s*\(",html)),
 "listeners":len(re.findall(r"addEventListener\s*\(",html)),
 "mutation_observers":len(re.findall(r"new\s+MutationObserver",html)),
}

print("TEAM FJZ V20.93 PASSWORD RECOVERY AUDIT")
print(json.dumps({"release":release,"missing":missing,"checks":checks,"metrics":metrics},indent=2,ensure_ascii=False))

if tuple(map(int,release.split("."))) < (20,93): raise SystemExit("Release older than 20.93")
if missing: raise SystemExit("Missing recovery markers: "+repr(missing))
if not all(checks.values()): raise SystemExit("Recovery behavior check failed: "+repr(checks))
if metrics["styles"]!=1: raise SystemExit("Stylesheet regression")
if metrics["renders"]>18: raise SystemExit("Render regression")
if metrics["intervals"]!=0: raise SystemExit("Interval regression")
if metrics["listeners"]>52: raise SystemExit("Listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("Observer regression")

print("TEAM FJZ V20.93 PASSWORD RECOVERY AUDIT OK")
