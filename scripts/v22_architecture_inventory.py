import argparse,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
BUILD=(ROOT/"build.py").read_text(encoding="utf-8")
patches=re.findall(r'exec\(compile\(open\("([^"]+\.py)"',BUILD)
sources=[]
for pattern in ("*.py","base/*.html","src/**/*.js"): sources.extend(ROOT.glob(pattern))
tables=set();rpcs=set()
for path in sources:
    if not path.is_file(): continue
    try: text=path.read_text(encoding="utf-8")
    except UnicodeDecodeError: continue
    tables.update(re.findall(r"\.from\(['\"]([A-Za-z0-9_]+)['\"]\)",text))
    rpcs.update(re.findall(r"\.rpc\(['\"]([A-Za-z0-9_]+)['\"]",text))
artifact=ROOT/"public"/"index.html"; runtime={}
if artifact.exists():
    html=artifact.read_text(encoding="utf-8")
    runtime={
        "render_assignments":len(re.findall(r"(?:window\.)?render\s*=",html)),
        "channels":len(re.findall(r"\.channel\s*\(",html)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",html)),
        "intervals":len(re.findall(r"setInterval\s*\(",html)),
        "listeners":len(re.findall(r"addEventListener\s*\(",html)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",html)),
        "date_core":'id="v22CanonicalDateCore"' in html,
        "date_pilot":'globalThis.TeamFJZDate.calendarDate' in html,
    }
result={
 "build_patch_count":len(patches),"first_patches":patches[:10],"last_patches":patches[-12:],
 "supabase_tables":sorted(tables),"supabase_rpcs":sorted(rpcs),"runtime":runtime,
 "contracts":{"date_core":(ROOT/"src/core/date.js").exists(),"save_contract":(ROOT/"src/core/save-contract.js").exists(),"repository_contracts":(ROOT/"src/data/repository-contracts.js").exists()}
}
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--check",action="store_true");args=parser.parse_args()
    if args.check:
        required=["v342_v22_0c_ui_authority.py","v343_v22_1a_architecture_foundation.py"]
        if not all(x in patches for x in required): raise SystemExit("V22 1A build order markers missing")
        if patches.index(required[1])<=patches.index(required[0]): raise SystemExit("V22 1A must execute after 0C authority")
        if not all(result["contracts"].values()): raise SystemExit("V22 1A canonical contracts missing")
        if not runtime.get("date_core") or not runtime.get("date_pilot"): raise SystemExit("V22 1A generated date pilot missing")
    print("TEAM FJZ V22 1A ARCHITECTURE INVENTORY")
    print(json.dumps(result,indent=2,ensure_ascii=False))
