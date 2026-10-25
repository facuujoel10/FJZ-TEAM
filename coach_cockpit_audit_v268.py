import pathlib,re,json
html=pathlib.Path("public/index.html").read_text(encoding="utf-8")

required=[
  'meta name="fjz-coach-cockpit-music-removal" content="20.68"',
  "musicFeatureRemoved:true",
  "coachMediaRealtimeRemoved:true",
  "coachCockpitV268:true",
  "coachDecisionSignals:true",
  "coachDataCoverage:true",
  "coachAvatarProductionLinkedProfile:true",
  "studentAvatarProductionLinkedProfile:true",
  "stagingAvatarClearlyDemo:true",
  "COACH COCKPIT",
  "v268CoachCockpit",
  "__fjzApplyProfileUiV268",
]
forbidden=[
  "coach_media_settings",
  "renderGlobalMusicCoachV69",
  "saveGlobalSpotifyV69",
  "renderSpotifyStudentV69",
  "saveSpotifyV68",
  "spotify_url",
  "coachTab==='music'",
  "studentTab==='music'",
  "coachStudentTab==='music'",
]
missing=[x for x in required if x not in html]
present=[x for x in forbidden if x in html]

metrics={
  "styles":len(re.findall(r"<style\b",html,re.I)),
  "render_assignments":len(re.findall(r"(?:window\.)?render\s*=",html)),
  "channels":len(re.findall(r"\.channel\s*\(",html)),
  "timeouts":len(re.findall(r"setTimeout\s*\(",html)),
  "rafs":len(re.findall(r"requestAnimationFrame\s*\(",html)),
  "listeners":len(re.findall(r"addEventListener\s*\(",html)),
  "mutation_observers":len(re.findall(r"new\s+MutationObserver",html)),
}

print("TEAM FJZ V20.68 COCKPIT / MUSIC REMOVAL AUDIT")
print(json.dumps({"missing":missing,"forbidden_present":present,"metrics":metrics},indent=2,ensure_ascii=False))
if missing: raise SystemExit("V20.68 missing markers: "+repr(missing))
if present: raise SystemExit("V20.68 music runtime remains: "+repr(present))
if metrics["styles"]!=1: raise SystemExit("V20.68 expected one stylesheet")
if metrics["channels"]>2: raise SystemExit("V20.68 realtime channel regression")
if metrics["mutation_observers"]>3: raise SystemExit("V20.68 observer regression")
print("TEAM FJZ V20.68 COCKPIT / MUSIC REMOVAL AUDIT OK")
