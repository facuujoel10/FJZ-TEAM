from __future__ import annotations
import os, subprocess, sys
from dev_common import local_status

def main():
    subprocess.run([sys.executable,"scripts/dev_guard.py"],check=True)
    st=local_status()
    env=os.environ.copy()
    env["TEAM_FJZ_ENV"]="development"
    env["TEAM_FJZ_SUPABASE_URL"]=st["api"]
    env["TEAM_FJZ_SUPABASE_PUBLISHABLE_KEY"]=st["publishable"]
    env["SUPABASE_TELEMETRY_DISABLED"]="1"
    subprocess.run([sys.executable,"build.py"],env=env,check=True)
    subprocess.run([sys.executable,"scripts/dev_guard.py","--artifact"],env=env,check=True)
    print("TEAM FJZ V22 DEVELOPMENT BUILD OK")
    print("Supabase:",st["api"])
    print("Artifact: public/index.html")

if __name__=="__main__":
    main()
