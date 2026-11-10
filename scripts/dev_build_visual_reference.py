from __future__ import annotations
import os, pathlib, subprocess, sys, re
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
    if st["api"] not in artifact: raise RuntimeError("visual reference did not bind local Supabase")
    active_urls=re.findall(r"const DEFAULT_SUPABASE_URL=['\"]([^'\"]+)['\"];",artifact)
    if not active_urls or active_urls[-1].rstrip("/")!=st["api"].rstrip("/"):
        raise RuntimeError("visual reference active Supabase URL is not local: "+repr(active_urls[-3:]))
    if any(url.rstrip("/").endswith(PROD_REF+".supabase.co") for url in active_urls[-1:]):
        raise RuntimeError("visual reference active URL points to production")
    print("VISUAL REFERENCE BUILD OK",root,st["api"])
if __name__=="__main__": main()
