import pathlib
import re
import sys
import runpy

ROOT = pathlib.Path(__file__).resolve().parent
BUILD = ROOT / "build.py"
RELEASE = ROOT / "RELEASE"
PINNED = ROOT / "base" / "team-fjz-source-v20.7.html"

errors = []

if not BUILD.exists():
    errors.append("build.py missing")
if not RELEASE.exists():
    errors.append("RELEASE missing")
if not PINNED.exists():
    errors.append("Pinned base source missing")

build = BUILD.read_text(encoding="utf-8") if BUILD.exists() else ""
release = RELEASE.read_text(encoding="utf-8").strip() if RELEASE.exists() else ""

if not re.fullmatch(r"\d+\.\d+", release):
    errors.append(f"Invalid RELEASE value: {release!r}")

if 'PINNED_SOURCE = pathlib.Path("base/team-fjz-source-v20.7.html")' not in build:
    errors.append("Build is not pinned to the V20.7 base source")

if "urllib.request.urlopen(req" in build:
    errors.append("Mutable remote base fetch is still enabled")

if "TEAM_FJZ_SUPABASE_URL" not in build or "TEAM_FJZ_SUPABASE_PUBLISHABLE_KEY" not in build:
    errors.append("Staging Supabase env guards are missing")

if (
    "PRODUCTION_SUPABASE_URL" not in build
    or 'APP_ENV == "staging-local"' not in build
    or "TEAM_FJZ_SUPABASE_URL" not in build
    or "TEAM_FJZ_SUPABASE_PUBLISHABLE_KEY" not in build
    or "staging_local_guard.py" not in build
):
    errors.append("Production Supabase isolation guards are incomplete")

tail = build.strip().splitlines()[-6:]
if not any("v127_release_system.py" in line for line in tail):
    errors.append("v127_release_system.py is not at the end of the build pipeline")

source = PINNED.read_text(encoding="utf-8") if PINNED.exists() else ""
if source and "<!doctype html" not in source.lower():
    errors.append("Pinned base does not look like HTML")
if source and "TEAM FJZ" not in source:
    errors.append("Pinned base does not identify TEAM FJZ")

if errors:
    print("TEAM FJZ PREFLIGHT FAILED")
    for item in errors:
        print(f"- {item}")
    sys.exit(1)

print("TEAM FJZ PREFLIGHT OK")
print(f"Release: {release}")
print("Pinned base: base/team-fjz-source-v20.7.html")
print("Production/staging isolation guards: OK")

# Artifact-level regression checks.
runpy.run_path(str(ROOT / 'smoke_static.py'), run_name='__main__')

# Focused routine/mobile/profile regression checks.
runpy.run_path(str(ROOT / 'routine_ui_audit_v269.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'mobile_profile_audit_v270.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'coach_preview_audit_v271.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'final_stability_audit_v274.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'hud_progress_audit_v275.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'coach_hud_nutrition_audit_v276.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'final_save_geometry_audit_v277.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'smart_alert_progress_audit_v278.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'final_stability_audit_v279.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'priority_calendar_audit_v280.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'coach_integrity_audit_v281.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'calendar_route_audit_v282.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'mobile_legacy_geometry_audit_v283.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'final_calendar_audit_v284.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'release_candidate_audit_v285.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'typography_mobile_nav_feedback_audit_v286.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'session_exercise_comment_audit_v287.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'desktop_readability_audit_v288.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'legacy_runtime_save_audit_v289.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'final_product_audit_v290.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'new_feature_hardening_audit_v291.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'single_coach_nav_audit_v292.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'password_recovery_audit_v293.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'auth_session_resilience_audit_v294.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'final_release_gate_v291.py'), run_name='__main__')
runpy.run_path(str(ROOT / 'final_symbol_scan.py'), run_name='__main__')

# Canonical authority / wrapper regression audit.
runpy.run_path(str(ROOT / 'consolidation_audit.py'), run_name='__main__')

# Diagnostic ownership map for consolidation planning.
runpy.run_path(str(ROOT / 'authority_map.py'), run_name='__main__')
