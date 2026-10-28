import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()
m=re.search(r'<script[^>]*id=["\']v302ReviewResolutionAuthorityRuntime["\'][^>]*>(.*?)</script>',html,re.S|re.I)
body=m.group(1) if m else ""
checks={
 "release":tuple(map(int,release.split("."))) >= (21,8),
 "meta":'meta name="fjz-review-recurrence-fix" content="21.08"' in html,
 "runtime":bool(body),
 "baseline_prefix":"review-baseline-v308:" in body,
 "stable_baseline_flag":"stableBaselineAuthority:true" in body,
 "legacy_migration_flag":"legacyResolvedMigration:true" in body,
 "no_repeat_flag":"noRepeatedFirstReview:true" in body,
 "legacy_promotion":"ensureLegacyBaselineV308" in body and "legacyResolvedAthletes" in body,
 "baseline_loaded":"BASE_PREFIX+'%'" in body,
 "baseline_resolves_state":"if(baselineCurrentV308(s))return true" in body,
 "state_ok_writes_baseline":"baselineKeyV308(s)" in body and "d.sourceType==='state'" in body,
 "first_review_stable":(
   ("firstReviewCardsDisabledV327:true" in body and "first_review:'+athleteKeyV308(s)" not in body)
   if tuple(map(int,release.split("."))) >= (21,27)
   else "first_review:'+athleteKeyV308(s)" in body
 ),
 "new_change_path":"cloudBaseline&&!cloudBaselineCurrent" in body,
 "cloud_verified":".upsert(rows,{onConflict:'coach_id,event_key'})" in body and ".select('event_key,read_at,dismissed_at')" in body,
}
failed=[k for k,v in checks.items() if not v]
print("TEAM FJZ V21.08 REVIEW RECURRENCE AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.08 REVIEW RECURRENCE AUDIT FAILED")
print("TEAM FJZ V21.08 REVIEW RECURRENCE AUDIT OK")
