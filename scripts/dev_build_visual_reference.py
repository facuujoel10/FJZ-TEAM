from __future__ import annotations
import os, pathlib, subprocess, sys
from dev_common import local_status

PROD_REF="cujipwacwwpejhqjhnkr"
def main():
    if len(sys.argv)!=2: raise SystemExit("usage: dev_build_visual_reference.py <checkout-root>")
    root=pathlib.Path(sys.argv[1]).resolve()
    if not (root/"build.py").exists(): raise RuntimeError("reference build.py missing: "+str(root))
    st=local_status()
    env=os.environ.copy()
    env.update({
      "TEAM_FJZ_ENV":"development",
      "TEAM_FJZ_SUPABASE_URL":st["api"],
      "TEAM_FJZ_SUPABASE_PUBLISHABLE_KEY":st["publishable"],
      "SUPABASE_TELEMETRY_DISABLED":"1",
      "DO_NOT_TRACK":"1",
    })
    subprocess.run([sys.executable,"build.py"],cwd=root,env=env,check=True)
    artifact=(root/"public/index.html").read_text(encoding="utf-8")
    if PROD_REF in artifact: raise RuntimeError("visual reference points to production")
    if st["api"] not in artifact: raise RuntimeError("visual reference did not bind local Supabase")
    print("VISUAL REFERENCE BUILD OK",root,st["api"])
if __name__=="__main__": main()
