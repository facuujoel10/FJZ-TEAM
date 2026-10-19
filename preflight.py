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

# Canonical authority / wrapper regression audit.
runpy.run_path(str(ROOT / 'consolidation_audit.py'), run_name='__main__')

# Diagnostic ownership map for consolidation planning.
runpy.run_path(str(ROOT / 'authority_map.py'), run_name='__main__')
