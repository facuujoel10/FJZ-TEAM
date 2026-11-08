from __future__ import annotations
import os, shutil, subprocess, sys
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
    network="team-fjz-v22-local"
    check=subprocess.run([docker,"network","inspect",network],capture_output=True,text=True)
    if check.returncode!=0:
        run([docker,"network","create","-o","com.docker.network.bridge.host_binding_ipv4=127.0.0.1",network])

    cli=supabase_cmd()
    # supabase start prints local keys; capture it so CI logs never expose them.
    run(cli+["start","--network-id",network],env=env,capture=True)
    # Always name the target explicitly even though CLI v3 defaults to local.
    run(cli+["db","reset","--local"],env=env,capture=True)
    run([sys.executable,"scripts/dev_bootstrap.py"],env=env)
    run([sys.executable,"scripts/dev_smoke.py"],env=env)
    print("TEAM FJZ V22 LOCAL RESET + INTEGRATION OK")

if __name__=="__main__":
    main()
