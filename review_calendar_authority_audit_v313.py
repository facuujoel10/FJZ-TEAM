import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()
m280=re.search(r'<script[^>]*id=["\']v280OperationalRecoveryRuntime["\'][^>]*>(.*?)</script>',html,re.S|re.I)
m312=re.search(r'<script[^>]*id=["\']v312ReviewAgendaAuthorityRuntime["\'][^>]*>(.*?)</script>',html,re.S|re.I)
b280=m280.group(1) if m280 else ""
b312=m312.group(1) if m312 else ""
checks={
 "release":tuple(map(int,release.split("."))) >= (21,13),
 "meta":'meta name="fjz-review-calendar-authority" content="21.13"' in html,
 "v280_runtime":bool(b280),
 "v312_runtime":bool(b312),
 "cloud_review_helper":"cloudProfileReviewedV313" in b280,
 "waits_for_cloud_state":"reviewStateReadyV313" in b280 and "return null" in b280,
 "filters_null_reviews":"reviewEventsV313" in b280 and ".filter(Boolean)" in b280,
 "no_direct_old_map":"students().map(reviewEvent)" not in b280,
 "closed_profiles_excluded":"closedProfilesExcludedFromCalendar:true" in b280,
 "no_synthetic_first":"noSyntheticFirstCheckBeforeReviewSync:true" in b280,
 "calendar_refresh_after_sync":"refreshCoachOperationalV280" in b312 and "operationalCalendarRefreshAfterReviewSync:true" in b312,
 "profile_authority_present":"__fjzProfileReviewedAthleteV311" in html,
}
failed=[k for k,v in checks.items() if not v]
print("TEAM FJZ V21.13 REVIEW CALENDAR AUTHORITY AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.13 REVIEW CALENDAR AUTHORITY AUDIT FAILED")
print("TEAM FJZ V21.13 REVIEW CALENDAR AUTHORITY AUDIT OK")
