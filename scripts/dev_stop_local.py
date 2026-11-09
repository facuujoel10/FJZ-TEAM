from __future__ import annotations
import os,shutil,subprocess,time
from dev_common import supabase_cmd
PROJECT="team-fjz-v22-local"
def running(docker,all_containers=False):
    args=[docker,"ps"]+(["-a"] if all_containers else [])+["--format","{{.Names}}"];rows=subprocess.run(args,text=True,capture_output=True,check=False).stdout.splitlines();return [x.strip() for x in rows if PROJECT in x]
def main():
    docker=shutil.which("docker")
    if not docker: raise SystemExit("Docker unavailable")
    env=os.environ.copy();env["SUPABASE_TELEMETRY_DISABLED"]="1";subprocess.run(supabase_cmd()+["stop","--no-backup"],env=env,text=True,capture_output=True,check=False)
    for _ in range(20):
        if not running(docker): print("TEAM FJZ V22 LOCAL STACK SHUTDOWN OK");print("Project containers running: 0");return
        time.sleep(0.5)
    raise SystemExit("V22 local containers still running: "+",".join(running(docker,True)))
if __name__=="__main__": main()
