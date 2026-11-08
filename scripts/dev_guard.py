from __future__ import annotations
import argparse, os, pathlib, subprocess, sys
from dev_common import PROD_KEY,PROD_REF,PROD_URL,assert_local_url,reject_production

ROOT=pathlib.Path(__file__).resolve().parents[1]
EXPECTED_BRANCH="dev/team-fjz-v22"

def branch_name():
    try:
        p=subprocess.run(["git","branch","--show-current"],cwd=ROOT,text=True,
                         capture_output=True,check=True)
        return p.stdout.strip()
    except Exception:
        return ""

def scan_text(path):
    text=path.read_text(encoding="utf-8")
    low=text.lower()
    forbidden=[PROD_REF,PROD_URL.lower(),PROD_KEY]
    return [x for x in forbidden if x and x.lower() in low]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact",action="store_true")
    args=ap.parse_args()

    sentinel=ROOT/".team-fjz-development"
    if not sentinel.exists():
        raise SystemExit("FAIL: falta .team-fjz-development")

    b=branch_name()
    if b and b!=EXPECTED_BRANCH:
        raise SystemExit(f"FAIL: rama actual {b!r}; se esperaba {EXPECTED_BRANCH!r}")

    env=os.environ.get("TEAM_FJZ_ENV","").strip().lower()
    if env and env not in {"development","test"}:
        raise SystemExit("FAIL: TEAM_FJZ_ENV debe ser development/test en V22 dev")

    for name in ("TEAM_FJZ_SUPABASE_URL","TEAM_FJZ_SUPABASE_PUBLISHABLE_KEY"):
        value=os.environ.get(name,"")
        if value:
            reject_production(value)
    if os.environ.get("TEAM_FJZ_SUPABASE_URL"):
        assert_local_url(os.environ["TEAM_FJZ_SUPABASE_URL"])

    config=ROOT/"supabase"/"config.toml"
    if not config.exists():
        raise SystemExit("FAIL: falta supabase/config.toml")
    if scan_text(config):
        raise SystemExit("FAIL: config local contiene referencia productiva")

    for rel in ["supabase/seed.sql","scripts/dev_bootstrap.py"]:
        p=ROOT/rel
        if not p.exists(): raise SystemExit("FAIL: falta "+rel)
        txt=p.read_text(encoding="utf-8")
        if "test.local" not in txt and rel.endswith("dev_bootstrap.py"):
            raise SystemExit("FAIL: bootstrap no usa dominio test.local")

    temp=ROOT/"supabase"/".temp"
    if temp.exists():
        for p in temp.rglob("*"):
            if p.is_file():
                try:
                    leaks=scan_text(p)
                except Exception:
                    leaks=[]
                if leaks:
                    raise SystemExit("FAIL: vínculo productivo detectado en "+str(p))

    if args.artifact:
        artifact=ROOT/"public"/"index.html"
        if not artifact.exists(): raise SystemExit("FAIL: falta public/index.html")
        text=artifact.read_text(encoding="utf-8")
        low=text.lower()
        if PROD_REF in low or PROD_URL.lower() in low or PROD_KEY in text or ".supabase.co" in low:
            raise SystemExit("FAIL: artifact de desarrollo contiene backend productivo")
        if 'meta name="fjz-environment" content="development"' not in text and 'meta name="fjz-environment" content="test"' not in text:
            raise SystemExit("FAIL: artifact sin marcador de entorno")

    print("TEAM FJZ V22 DEV GUARD OK")
    print("branch:",b or "(no disponible)")
    print("production references: blocked")
    print("fixture policy: test.local / TEST names only")

if __name__=="__main__":
    main()
