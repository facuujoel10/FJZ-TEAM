import pathlib,re,json,collections

root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()

def n(pat,flags=0):
    return len(re.findall(pat,html,flags))

metrics={
    "bytes":len(html.encode("utf-8")),
    "scripts":n(r"<script\b",re.I),
    "styles":n(r"<style\b",re.I),
    "render_assignments":n(r"(?:window\.)?render\s*="),
    "timeouts":n(r"setTimeout\s*\("),
    "intervals":n(r"setInterval\s*\("),
    "rafs":n(r"requestAnimationFrame\s*\("),
    "listeners":n(r"addEventListener\s*\("),
    "mutation_observers":n(r"new\s+MutationObserver"),
    "performance_observers":n(r"new\s+PerformanceObserver"),
    "smooth_scroll":n(r"behavior\s*:\s*['\"]smooth['\"]"),
    "transition_all":n(r"transition\s*:\s*all\b",re.I),
    "scroll_into_view":n(r"scrollIntoView\s*\("),
    "window_scroll_to":n(r"window\.scrollTo\s*\("),
    "scroll_top_writes":n(r"\.scrollTop\s*="),
    "query_selector_all":n(r"querySelectorAll\s*\("),
    "query_selector":n(r"querySelector\s*\("),
    "inner_html_writes":n(r"\.innerHTML\s*="),
    "insert_adjacent_html":n(r"insertAdjacentHTML\s*\("),
    "replace_children":n(r"\.replaceChildren\s*\("),
    "supabase_from_calls":n(r"\.from\s*\("),
    "supabase_rpc_calls":n(r"\.rpc\s*\("),
}

script_entries=[]
for m in re.finditer(r"<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>",html,re.S|re.I):
    attrs=m.group("attrs") or ""
    body=m.group("body") or ""
    mid=re.search(r"\bid=['\"]([^'\"]+)['\"]",attrs,re.I)
    src=re.search(r"\bsrc=['\"]([^'\"]+)['\"]",attrs,re.I)
    name=mid.group(1) if mid else (src.group(1) if src else "(inline)")
    script_entries.append({"name":name,"bytes":len(body.encode("utf-8"))})
largest_scripts=sorted(script_entries,key=lambda x:x["bytes"],reverse=True)[:15]

listener_types=collections.Counter()
for m in re.finditer(r"addEventListener\s*\(\s*['\"]([^'\"]+)['\"]",html):
    listener_types[m.group(1)]+=1

timeout_delays=collections.Counter()
for m in re.finditer(r"setTimeout\s*\([^,]{0,240},\s*(\d+)",html,re.S):
    try:
        v=int(m.group(1))
        bucket="0-49ms" if v<50 else "50-249ms" if v<250 else "250-999ms" if v<1000 else "1s+"
        timeout_delays[bucket]+=1
    except Exception:
        pass

# Approximate possible self-recursive RAF loops. A positive hit is advisory, not automatic failure.
raf_contexts=[]
for m in re.finditer(r"requestAnimationFrame\s*\(([^)]{0,140})\)",html,re.S):
    start=max(0,m.start()-700)
    prefix=html[start:m.start()]
    fm=list(re.finditer(r"(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(",prefix))
    fn=fm[-1].group(1) if fm else ""
    arg=" ".join(m.group(1).split())
    self_ref=bool(fn and re.search(r"\b"+re.escape(fn)+r"\b",arg))
    raf_contexts.append({"function":fn or "(unknown)","arg":arg[:120],"possible_self_loop":self_ref})
possible_self_raf_loops=[x for x in raf_contexts if x["possible_self_loop"]]

# Critical product contracts that should survive every cleanup/performance pass.
contracts={
    "release_21_30_or_newer": tuple(map(int,release.split("."))) >= (21,30),
    "global_save_integrity": "globalSaveIntegrity:true" in html and "successDeferredUntilVerified:true" in html,
    "session_double_verification": "sessionSuccessRequiresDoubleVerification:true" in html and "snapshotAndProjectionConfirmation:true" in html,
    "workout_cloud_confirmation": "cloudConfirmationBeforeSuccess:true" in html,
    "duplicate_save_guard": "duplicateAsyncSaveGuard:true" in html or "duplicateSaveByDesignBlocked:true" in html,
    "checkin_confirmed_state": "checkinUsesConfirmedState:true" in html or "confirmedCheckinSuccess" in html,
    "single_coach_navigation": 'meta name="fjz-single-coach-athlete-nav" content="20.92"' in html,
    "profile_photo_authority": "singleCanonicalProfilePhoto:true" in html,
    "exercise_comments_history": "exerciseCommentsVisiblePerSessionV287:true" in html,
    "comment_exact_focus": "exactExerciseCommentHighlightV329:true" in html and "exactExerciseCommentAutoScrollV329:true" in html,
    "comments_pending_inbox": "trainingCommentsInboxPendingOnlyV330:true" in html and "reviewedCommentsLeaveDashboardV330:true" in html,
    "first_review_disabled": "firstReviewCardsDisabledV327:true" in html and "missingBaselineNeverCreatesReviewV327:true" in html,
    "review_server_authority": "reviewServerAuthorityV322" in html or 'fjz-review-server-authority' in html,
    "agenda_shared": 'fjz-shared-agenda' in html or "studentAppointment" in html or "sharedAgenda" in html,
    "decimal_workout_weights": 'fjz-decimal-workout-weights' in html or "decimalWorkoutWeightsV315" in html,
    "auth_resilience": "recoverUnexpectedSignedOutV294" in html and "showSessionRecoveryV294" in html,
    "no_automatic_messages": not any(x in html for x in ["sendAutomaticMessageV290","sendAutomaticMessageV291","scheduledMessageV291"]),
}

hard_limits={
    "styles": metrics["styles"]==1,
    "render_assignments": metrics["render_assignments"]<=18,
    "intervals": metrics["intervals"]==0,
    "listeners": metrics["listeners"]<=52,
    "mutation_observers": metrics["mutation_observers"]<=3,
    "performance_observers": metrics["performance_observers"]==0,
    "smooth_scroll": metrics["smooth_scroll"]==0,
    "transition_all": metrics["transition_all"]==0,
}

advisories=[]
if metrics["bytes"]>1800000:
    advisories.append("Compiled HTML is above 1.8 MB; startup parse/compile cost is the clearest remaining performance risk.")
if metrics["scripts"]>100:
    advisories.append("More than 100 script blocks remain; legacy-patch consolidation could reduce startup work and maintenance risk.")
if metrics["rafs"]>=20:
    advisories.append("requestAnimationFrame call-sites are relatively numerous; they are currently bounded by existing stability gates but merit consolidation.")
if metrics["timeouts"]>=50:
    advisories.append("setTimeout call-sites are numerous; no repeating setInterval exists, but one-shot scheduling remains a cleanup target.")
if metrics["query_selector_all"]>=40:
    advisories.append("High querySelectorAll count; repeated full-DOM sweeps should stay scoped/cached during future work.")
if possible_self_raf_loops:
    advisories.append("Possible self-recursive requestAnimationFrame contexts detected; inspect before any animation expansion.")

failed_contracts=[k for k,v in contracts.items() if not v]
failed_limits=[k for k,v in hard_limits.items() if not v]

report={
    "release":release,
    "metrics":metrics,
    "listener_types":dict(listener_types.most_common()),
    "timeout_delay_buckets":dict(timeout_delays),
    "largest_scripts":largest_scripts,
    "possible_self_raf_loops":possible_self_raf_loops[:20],
    "contracts":contracts,
    "hard_limits":hard_limits,
    "failed_contracts":failed_contracts,
    "failed_limits":failed_limits,
    "advisories":advisories,
}
print("TEAM FJZ V21.30 DEEP RUNTIME / LAG AUDIT")
print(json.dumps(report,indent=2,ensure_ascii=False))

if failed_contracts or failed_limits:
    raise SystemExit("TEAM FJZ DEEP RUNTIME AUDIT FAILED")
print("TEAM FJZ V21.30 DEEP RUNTIME / LAG AUDIT OK")
