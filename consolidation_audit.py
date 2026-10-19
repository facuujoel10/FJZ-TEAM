import pathlib
import re
import json

ROOT=pathlib.Path(__file__).resolve().parent
HTML=ROOT/"public"/"index.html"
if not HTML.exists():
    raise SystemExit("public/index.html missing")

html=HTML.read_text(encoding="utf-8")

def count(pattern,flags=0):
    return len(re.findall(pattern,html,flags))

metrics={
    "bytes":len(html.encode("utf-8")),
    "scripts":count(r"<script\b",re.I),
    "styles":count(r"<style\b",re.I),
    "render_assignments":count(r"(?:window\.)?render\s*="),
    "finishWorkout_assignments":count(r"(?:window\.)?finishWorkout\s*="),
    "confirmPartial_assignments":count(r"(?:window\.)?confirmPartialSessionV106\s*="),
    "workoutExercise_assignments":count(r"(?:window\.)?workoutExercise\s*="),
    "showModal_assignments":count(r"(?:window\.)?showModal\s*="),
    "closeModal_assignments":count(r"(?:window\.)?closeModal\s*="),
    "realtime_channel_defs":count(r"\.channel\s*\("),
    "mutation_observers":count(r"new\s+MutationObserver"),
    "performance_observers":count(r"new\s+PerformanceObserver"),
    "timeouts":count(r"setTimeout\s*\("),
    "rafs":count(r"requestAnimationFrame\s*\("),
    "listeners":count(r"addEventListener\s*\("),
}

authorities={
    "release_v127":"TEAM FJZ release authority" in html or "__TEAM_FJZ_RELEASE__" in html,
    "save_v207":"cloudConfirmationBeforeSuccess:true" in html,
    "progress_v205":"professionalProgressCharts:true" in html,
    "reorder_v204":"modalReorderUsesAtomicRpc:true" in html,
    "fresh_weight_v205":"previousWeightReferenceOnly:true" in html,
    "method_reference_v205":"methodPreviousReference:true" in html,
    "method_panel_v198":"methodPanelSurvivesCardRebuild:true" in html,
    "interaction_v193":"__fjzInteractionHealthV193" in html,
    "realtime_v192":"__fjzRuntimeHealthV192" in html,
    "auth_v194":"__fjzEnsureFreshAuthV194" in html,
}

print("TEAM FJZ CONSOLIDATION AUDIT")
print(json.dumps({"metrics":metrics,"authorities":authorities},indent=2,ensure_ascii=False))

missing=[k for k,v in authorities.items() if not v]
if missing:
    raise SystemExit("Missing canonical authorities: "+", ".join(missing))

# Guardrails only; these are intentionally not exact counts.
if metrics["styles"]!=1:
    raise SystemExit(f"Expected one stylesheet, found {metrics['styles']}")
if metrics["performance_observers"]!=0:
    raise SystemExit("PerformanceObserver regression")
if metrics["mutation_observers"]>3:
    raise SystemExit("MutationObserver regression")
if metrics["render_assignments"]>30:
    raise SystemExit("Render wrapper count exceeded consolidation ceiling")

print("TEAM FJZ CONSOLIDATION AUDIT OK")
