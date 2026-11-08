from __future__ import annotations
import os, pathlib, subprocess, sys

from dev_common import PROD_URL

ROOT=pathlib.Path(__file__).resolve().parents[1]

def run_case(label,cmd,extra_env,expected_failure=True):
    env=os.environ.copy()
    env.pop("TEAM_FJZ_SUPABASE_URL",None)
    env.pop("TEAM_FJZ_SUPABASE_PUBLISHABLE_KEY",None)
    env.update(extra_env)
    p=subprocess.run(
        cmd,cwd=ROOT,env=env,text=True,
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL
    )
    failed=p.returncode!=0
    if failed!=expected_failure:
        raise RuntimeError("Negative guard expectation failed: "+label)
    print(label+": OK")

def main():
    run_case(
        "reject production TEAM_FJZ_ENV",
        [sys.executable,"scripts/dev_guard.py"],
        {"TEAM_FJZ_ENV":"production"}
    )
    run_case(
        "reject production Supabase URL",
        [sys.executable,"scripts/dev_guard.py"],
        {
          "TEAM_FJZ_ENV":"development",
          "TEAM_FJZ_SUPABASE_URL":PROD_URL,
          "TEAM_FJZ_SUPABASE_PUBLISHABLE_KEY":"local-placeholder"
        }
    )
    run_case(
        "reject any hosted Supabase URL",
        [sys.executable,"scripts/dev_guard.py"],
        {
          "TEAM_FJZ_ENV":"development",
          "TEAM_FJZ_SUPABASE_URL":"https://forbidden-hosted-project.supabase.co",
          "TEAM_FJZ_SUPABASE_PUBLISHABLE_KEY":"local-placeholder"
        }
    )
    run_case(
        "build refuses missing explicit environment",
        [sys.executable,"build.py"],
        {}
    )
    run_case(
        "build refuses production environment on V22 branch",
        [sys.executable,"build.py"],
        {"TEAM_FJZ_ENV":"production"}
    )
    print("TEAM FJZ V22 NEGATIVE ISOLATION TESTS OK")

if __name__=="__main__":
    main()
