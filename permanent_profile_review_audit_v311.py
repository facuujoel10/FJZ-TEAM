import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()
m=re.search(r'<script[^>]*id=["\']v302ReviewResolutionAuthorityRuntime["\'][^>]*>(.*?)</script>',html,re.S|re.I)
body=m.group(1) if m else ""
checks={
 "release":tuple(map(int,release.split("."))) >= (21,11),
 "meta":'meta name="fjz-permanent-profile-review" content="21.11"' in html,
 "runtime":bool(body),
 "stable_profile_key":"review-profile-v311:" in body,
 "profile_set":"profileReviewedAthletesV311" in body,
 "first_review_filter":"String(d.source||'').startsWith('first_review:')&&profileReviewedV311(s)" in body,
 "baseline_promotion":"existingBaselinesPromotedToProfileReview:true" in body,
 "hash_cannot_reopen":"dynamicHashCannotReopenFirstReview:true" in body,
 "resolve_persists_profile":"keys.push(profileKeyV311(s))" in body,
 "profile_prefix_loaded":"PROFILE_PREFIX+'%'" in body,
}
failed=[k for k,v in checks.items() if not v]
print("TEAM FJZ V21.11 PERMANENT PROFILE REVIEW AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.11 PERMANENT PROFILE REVIEW AUDIT FAILED")
print("TEAM FJZ V21.11 PERMANENT PROFILE REVIEW AUDIT OK")
