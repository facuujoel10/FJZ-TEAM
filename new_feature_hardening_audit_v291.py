import pathlib,re,json

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

required=[
 'meta name="fjz-new-feature-hardening" content="20.91"',
 "prBannerV291:true",
 "robustPrDetectionV291:true",
 "localizedWeightParsingV291:true",
 "normalizedExercisePrKeyV291:true",
 "numericV291",
 "exerciseKeyV291",
 "sessionId:last.sessionId",
 "v291-pr-banner",
 "v291-finish-head",
 "v291-finish-summary",
 "v291-finish-actions",
 "NUEVO PESO · NUEVO PR",
 "NUEVO RÉCORD DE VOLUMEN",
 "successModalAfterConfirmedSave:true",
 "duplicateSaveByDesignBlocked:true",
]
missing=[x for x in required if x not in html]

forbidden=[
 "sendAutomaticMessageV290",
 "sendAutomaticMessageV291",
 "autoMessageV290",
 "autoMessageV291",
 "scheduledMessageV291",
]
survived=[x for x in forbidden if x in html]

metrics={
 "styles":len(re.findall(r"<style\b",html,re.I)),
 "renders":len(re.findall(r"(?:window\.)?render\s*=",html)),
 "channels":len(re.findall(r"\.channel\s*\(",html)),
 "timeouts":len(re.findall(r"setTimeout\s*\(",html)),
 "intervals":len(re.findall(r"setInterval\s*\(",html)),
 "listeners":len(re.findall(r"addEventListener\s*\(",html)),
 "mutation_observers":len(re.findall(r"new\s+MutationObserver",html)),
 "smooth_scroll":len(re.findall(r"behavior\s*:\s*['\"]smooth['\"]",html)),
}

checks={
 "localized_decimal_support":"replace(',','.')" in html,
 "pr_seen_once":"localStorage.setItem(String(key||''),'1')" in html,
 "pr_session_identity":"String(x?.sessionId||x?.date||'')" in html,
 "pr_requires_history":"if(items.length<2)return;" in html,
 "pr_requires_positive_load":"Number(last.bestLoad)>0" in html,
 "pr_recent_guard":"Number.isFinite(parsed)" in html,
 "finish_title_readable":"font-size:20px!important" in html and ".v291-finish-head h3" in html,
 "finish_mobile_buttons":"min-height:48px!important" in html and ".v291-finish-actions>.btn" in html,
 "save_copy_readable":".v207-save-state .v207-save-copy" in html and "font-size:12.5px!important" in html,
}

print("TEAM FJZ V20.91 NEW FEATURE HARDENING AUDIT")
print(json.dumps({"release":release,"missing":missing,"forbidden":survived,"metrics":metrics,"checks":checks},indent=2,ensure_ascii=False))

if tuple(map(int,release.split("."))) < (20,91): raise SystemExit("Release older than 20.91")
if missing: raise SystemExit("Missing V20.91 markers: "+repr(missing))
if survived: raise SystemExit("Automatic-message feature survived: "+repr(survived))
if not all(checks.values()): raise SystemExit("V20.91 behavior check failed: "+repr(checks))
if metrics["styles"]!=1: raise SystemExit("Stylesheet regression")
if metrics["renders"]>18: raise SystemExit("Render regression")
if metrics["intervals"]!=0: raise SystemExit("Interval regression")
if metrics["listeners"]>52: raise SystemExit("Listener regression")
if metrics["mutation_observers"]>3: raise SystemExit("MutationObserver regression")
if metrics["smooth_scroll"]!=0: raise SystemExit("Smooth-scroll regression")

print("TEAM FJZ V20.91 NEW FEATURE HARDENING AUDIT OK")
