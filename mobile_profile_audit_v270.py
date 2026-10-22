import pathlib,re,json

html=pathlib.Path("public/index.html").read_text(encoding="utf-8")
required=[
  'meta name="fjz-mobile-edge-avatar-resilience" content="20.70"',
  'meta name="fjz-routine-library-preparation" content="20.69"',
  "mainLibraryStrengthOnly:true",
  "preparationLibrarySeparated:true",
  "avatarCachedPathFallbackV270:true",
  "avatarEmptyStateExplicitV270:true",
  "TEAM FJZ · V20.70 MOBILE EDGE GEOMETRY + AVATAR RESILIENCE",
  "@media(max-width:390px)",
  "@media(max-width:360px)",
  "signedAvatarV270",
  "createSignedUrl(path,3600)",
  "Sin foto cargada · se muestran iniciales",
]
missing=[x for x in required if x not in html]

styles=len(re.findall(r"<style\b",html,re.I))
v269=html.find("TEAM FJZ · V20.69 ROUTINE LIBRARY / PREPARATION UI")
v270=html.find("TEAM FJZ · V20.70 MOBILE EDGE GEOMETRY + AVATAR RESILIENCE")
late_override=(v269>=0 and v270>v269)

forbidden=[
  "coachTab==='music'",
  "studentTab==='music'",
  "coachStudentTab==='music'",
  "renderGlobalMusicCoachV69",
  "saveGlobalSpotifyV69",
]
active_forbidden=[x for x in forbidden if x in html]

report={
  "missing":missing,
  "styles":styles,
  "v270_after_v269":late_override,
  "active_music_refs":active_forbidden,
  "mobile_breakpoints":{"390":("@media(max-width:390px)" in html),"360":("@media(max-width:360px)" in html)},
  "avatar_cache_fallback":("cachedAvatarPathV270" in html and "loaded-cache" in html),
}
print("TEAM FJZ V20.70 MOBILE/PROFILE AUDIT")
print(json.dumps(report,indent=2,ensure_ascii=False))

if missing:
  raise SystemExit("V20.70 missing: "+repr(missing))
if styles!=1:
  raise SystemExit("V20.70 stylesheet regression")
if not late_override:
  raise SystemExit("V20.70 mobile rules are not after V20.69")
if active_forbidden:
  raise SystemExit("V20.70 music regression: "+repr(active_forbidden))

print("TEAM FJZ V20.70 MOBILE/PROFILE AUDIT OK")
