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
        "read_errors":'id="v22ReadErrorsCore"' in html,
        "agenda_repository":'id="v22AgendaRepositoryCore"' in html,
        "agenda_read_policy":'id="v22AgendaReadPolicyCore"' in html,
        "agenda_repository_integration":"TeamFJZAgendaReadPolicy.readAgendaWithCompatibility" in html,
        "agenda_repository_flag":'meta name="fjz-v22-agenda-repository-read" content="enabled"' in html,
        "second_date_pilot":"function isoV310(d)" in html and "TeamFJZDate.calendarDate(d,'America/Argentina/Buenos_Aires')" in html,
        "premium_workout_module":'id="v22PremiumWorkoutModule"' in html,
        "premium_workout_flag":'meta name="fjz-v22-2a-premium-workout" content="enabled"' in html,
        "premium_workout_ui":'v22-premium-workout' in html and 'v22-workout-save-state' in html,
        "session_history_module":'id="v22SessionHistoryModule"' in html,
        "session_history_flag":'meta name="fjz-v22-2b-session-history" content="enabled"' in html,
        "exact_session_comments":"exactSessionCommentLinkV2B:true" in html,
        "premium_history":"premiumHistoryV2B:true" in html,
        "visual_redesign_module":'id="v22VisualRedesignModule"' in html,
        "visual_redesign_flag":'meta name="fjz-v22-2bv-visual-redesign" content="enabled"' in html,
    }
result={
 "build_patch_count":len(patches),"first_patches":patches[:10],"last_patches":patches[-12:],
 "supabase_tables":sorted(tables),"supabase_rpcs":sorted(rpcs),"runtime":runtime,
 "contracts":{
    "date_core":(ROOT/"src/core/date.js").exists(),
    "save_contract":(ROOT/"src/core/save-contract.js").exists(),
    "repository_contracts":(ROOT/"src/data/repository-contracts.js").exists(),
    "read_errors":(ROOT/"src/data/read-errors.js").exists(),
    "agenda_repository":(ROOT/"src/data/agenda-repository.js").exists(),
    "comment_repository":(ROOT/"src/data/comment-repository.js").exists(),
    "agenda_read_policy":(ROOT/"src/data/agenda-read-policy.js").exists(),
    "premium_workout_module":(ROOT/"src/modules/workouts/premium-workout.js").exists(),
    "premium_workout_ui":(ROOT/"src/ui/premium-workout.css").exists(),
    "session_history_module":(ROOT/"src/modules/workouts/session-history.js").exists(),
    "premium_history_ui":(ROOT/"src/ui/premium-history.css").exists(),
    "visual_redesign_module":(ROOT/"src/modules/workouts/visual-redesign.js").exists(),
    "design_system":(ROOT/"src/ui/design-system.css").exists()
 }
}
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--check",action="store_true");args=parser.parse_args()
    if args.check:
        required=["v342_v22_0c_ui_authority.py","v343_v22_1a_architecture_foundation.py","v344_v22_2a_premium_workout.py"]
        if not all(x in patches for x in required): raise SystemExit("V22 2B build order markers missing")
        if not (patches.index(required[0])<patches.index(required[1])<patches.index(required[2])): raise SystemExit("V22 2B bridge must execute after 1A/1C foundation")
        if not all(result["contracts"].values()): raise SystemExit("V22 1A canonical contracts missing")
        if not runtime.get("date_core") or not runtime.get("date_pilot"): raise SystemExit("V22 1A generated date pilot missing")
        for key in ("read_errors","agenda_repository","agenda_read_policy","agenda_repository_integration","agenda_repository_flag","second_date_pilot","premium_workout_module","premium_workout_flag","premium_workout_ui","session_history_module","session_history_flag","exact_session_comments","premium_history","visual_redesign_module","visual_redesign_flag"):
            if not runtime.get(key): raise SystemExit("V22 runtime marker missing: "+key)
        expected={"render_assignments":18,"channels":2,"timeouts":56,"intervals":0,"listeners":51,"mutation_observers":3}
        actual={k:runtime.get(k) for k in expected}
        if actual!=expected: raise SystemExit("V22 1C topology regression: "+repr({"expected":expected,"actual":actual}))
        if len(patches)!=229: raise SystemExit("V22 2B-V keeps exactly one V22 workout integration bridge patch; count="+str(len(patches)))
    print("TEAM FJZ V22 2B-V ARCHITECTURE INVENTORY")
    print(json.dumps(result,indent=2,ensure_ascii=False))
