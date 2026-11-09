from __future__ import annotations
import os, re, shutil, subprocess, sys
from dev_common import run,supabase_cmd

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    os.chdir(ROOT)
    run([sys.executable,"scripts/dev_guard.py"])
    docker=shutil.which("docker")
    if not docker:
        raise SystemExit("BLOCKED: Docker/runtime compatible no disponible.")
    try:
        run([docker,"info"],capture=True)
    except Exception:
        raise SystemExit("BLOCKED: Docker está instalado pero el daemon no está disponible.")

    env=os.environ.copy()
    env["SUPABASE_TELEMETRY_DISABLED"]="1"
    cli=supabase_cmd()
    # Supabase manages its own Docker network. A custom --network-id caused
    # Storage to lose DNS resolution after db reset on GitHub-hosted runners.
    # A cancelled CI run can leave local containers behind on a reused runner,
    # so clear this development project before binding its fixed local ports.
    # This remains local-only and targets project_id=team-fjz-v22-local.
    subprocess.run(cli+["stop","--no-backup"],env=env,text=True,capture_output=True,check=False)
    # supabase start prints local keys, so capture it. On failure print only a
    # sanitized diagnostic so CI can distinguish Docker/CLI/config failures
    # without leaking JWTs or API keys.
    try:
        run(cli+["start"],env=env,capture=True)
    except subprocess.CalledProcessError as exc:
        raw=((exc.stdout or "")+"\n"+(exc.stderr or "")).strip()
        safe=re.sub(r'(?i)(anon key|service_role key|publishable key|secret key|jwt secret|access token)\\s*[:=]\\s*\\S+',r'\\1: [REDACTED]',raw)
        safe=re.sub(r'eyJ[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+','[REDACTED_JWT]',safe)
        safe=re.sub(r'sb_(?:publishable|secret)_[A-Za-z0-9._-]+','[REDACTED_SUPABASE_KEY]',safe)
        print("SUPABASE START FAILED (sanitized):",file=sys.stderr)
        print(safe[-12000:] if safe else "(no diagnostic output)",file=sys.stderr)
        raise
    # Always name the target explicitly even though CLI v3 defaults to local.
    run(cli+["db","reset","--local"],env=env)
    run([sys.executable,"scripts/dev_bootstrap.py"],env=env)
    run([sys.executable,"scripts/dev_smoke.py"],env=env)
    print("TEAM FJZ V22 LOCAL RESET + INTEGRATION OK")

if __name__=="__main__":
    main()
