import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()
m=re.search(r"(<script[^>]*\\bid=[\"']v302ReviewResolutionAuthorityRuntime[\"'][^>]*>)(.*?)(</script>)",html,re.S|re.I)
body=m.group(2) if m else ""
checks={
 "release":tuple(map(int,release.split("."))) >= (21,17),
 "meta":'meta name="fjz-review-epoch-authority" content="21.17"' in html,
 "runtime":bool(body),
 "epoch_prefix":"review-epoch-v317:" in body,
 "epoch_loaded":"EPOCH_PREFIX+'%'" in body,
 "profile_migrates_epoch":"rememberEpochV317(id,x.dismissed_at)" in body,
 "event_epoch_filter":"eventCoveredByEpochV317(s,d)" in body,
 "event_key_resolved":"(d.eventKeys||[]).some" in body,
 "resolve_persists_epoch":"keys.push(epochKeyV317(s))" in body,
 "dismiss_persists_epoch":"d.reviewKey,d.stateKey,epochKeyV317(s)" in body,
 "new_real_event_flag":"realEventsAfterLastReviewRemainVisible:true" in body,
 "no_new_timers":body.count("setInterval(")==0 and body.count("setTimeout(")==0,
}
failed=[k for k,v in checks.items() if not v]
print("TEAM FJZ V21.17 REVIEW EPOCH AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.17 REVIEW EPOCH AUDIT FAILED")
print("TEAM FJZ V21.17 REVIEW EPOCH AUDIT OK")
