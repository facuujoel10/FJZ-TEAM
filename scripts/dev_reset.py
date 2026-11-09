from __future__ import annotations
import os, re, shutil, socket, subprocess, sys, time
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
    # Cancelled/partial starts can leave containers behind, including a stopped
    # project container or (on CI) another stale Supabase container still
    # publishing one of the fixed local ports. Clean only Supabase/V22-local
    # containers; never touch arbitrary user containers on a developer machine.
    def cleanup_local_stack():
        subprocess.run(cli+["stop","--no-backup"],env=env,text=True,capture_output=True,check=False)
        names=subprocess.run(
            [docker,"ps","-a","--format","{{.Names}}"],
            env=env,text=True,capture_output=True,check=False
        ).stdout.splitlines()
        project_names=[n.strip() for n in names if "team-fjz-v22-local" in n]
        if project_names:
            subprocess.run([docker,"rm","-f",*project_names],env=env,text=True,capture_output=True,check=False)

        # GitHub-hosted runners are disposable and dedicated to this job. If a
        # previous partial Supabase start is still binding V22's local ports,
        # remove only the conflicting Supabase container. Locally we fail
        # closed instead of killing another developer's Supabase project.
        if str(env.get("CI","")).lower()=="true":
            rows=subprocess.run(
                [docker,"ps","--format","{{.Names}}|{{.Ports}}"],
                env=env,text=True,capture_output=True,check=False
            ).stdout.splitlines()
            stale=[]
            for row in rows:
                name,_,ports=row.partition("|")
                if name.startswith("supabase_") and any((":"+p+"->" in ports or "0.0.0.0:"+p+"->" in ports or "[::]:"+p+"->" in ports) for p in ("54321","54322","54323","54324","54325","54326","54327","54328","54329")):
                    stale.append(name)
            if stale:
                subprocess.run([docker,"rm","-f",*stale],env=env,text=True,capture_output=True,check=False)

    def local_ports_busy():
        busy=[]
        for port in (54321,54322,54323,54324,54325,54326,54327,54328,54329):
            sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            try:
                sock.bind(("127.0.0.1",port))
            except OSError:
                busy.append(port)
            finally:
                sock.close()
        return busy

    def await_local_ports_release():
        # Docker can return from rm/stop before the host's published-port rule
        # is fully released. On disposable CI runners, re-clean only Supabase
        # containers and require all fixed local ports to become bindable
        # before starting a fresh stack.
        for _ in range(20):
            busy=local_ports_busy()
            if not busy:
                return
            if str(env.get("CI","")).lower()=="true":
                rows=subprocess.run(
                    [docker,"ps","-a","--format","{{.Names}}"],
                    env=env,text=True,capture_output=True,check=False
                ).stdout.splitlines()
                stale=[n.strip() for n in rows if n.strip().startswith("supabase_")]
                if stale:
                    subprocess.run([docker,"rm","-f",*stale],env=env,text=True,capture_output=True,check=False)
            time.sleep(0.5)
        raise RuntimeError("Local Supabase ports still busy after cleanup: "+",".join(map(str,local_ports_busy())))

    cleanup_local_stack()
    await_local_ports_release()
    # supabase start prints local keys, so capture it. Cold hosted runners can
    # occasionally time out a container health check immediately after pulling
    # images. Retry exactly once after a local cleanup; a persistent second
    # failure still fails closed and prints only a sanitized diagnostic.
    start_exc=None
    for attempt in (1,2):
        try:
            run(cli+["start"],env=env,capture=True)
            start_exc=None
            break
        except subprocess.CalledProcessError as exc:
            start_exc=exc
            if attempt==1:
                cleanup_local_stack()
                await_local_ports_release()
                continue
    if start_exc is not None:
        raw=((start_exc.stdout or "")+"\n"+(start_exc.stderr or "")).strip()
        safe=re.sub(r'(?i)(anon key|service_role key|publishable key|secret key|jwt secret|access token)\\s*[:=]\\s*\\S+',r'\\1: [REDACTED]',raw)
        safe=re.sub(r'eyJ[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+','[REDACTED_JWT]',safe)
        safe=re.sub(r'sb_(?:publishable|secret)_[A-Za-z0-9._-]+','[REDACTED_SUPABASE_KEY]',safe)
        print("SUPABASE START FAILED AFTER RETRY (sanitized):",file=sys.stderr)
        print(safe[-12000:] if safe else "(no diagnostic output)",file=sys.stderr)
        raise start_exc
    # Always name the target explicitly even though CLI v3 defaults to local.
    run(cli+["db","reset","--local"],env=env)
    run([sys.executable,"scripts/dev_bootstrap.py"],env=env)
    run([sys.executable,"scripts/dev_smoke.py"],env=env)
    print("TEAM FJZ V22 LOCAL RESET + INTEGRATION OK")

if __name__=="__main__":
    main()
