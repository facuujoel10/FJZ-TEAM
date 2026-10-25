import pathlib,re,json
html=pathlib.Path("public/index.html").read_text(encoding="utf-8")

required={
  "v267_meta":'meta name="fjz-coach-profile-input-contracts" content="20.67"',
  "avatar_direct":"coachAvatarDirectLinkedProfile:true",
  "avatar_cache_bypass":"coachAvatarBypassesStaleEmptyCache:true",
  "checkin_range":"strictCheckinRange1to10:true",
  "workout_numeric":"workoutNumericGuard:true",
  "routine_numeric":"routineNumericGuard:true",
  "measurement_numeric":"measurementNumericGuard:true",
  "comments_text":"commentsRemainText:true",
  "exact_reps_text":"exactRepsPatternRemainsText:true",
  "score_pattern":'pattern="[1-9]|10"',
  "input_rules":"__fjzApplyInputRulesV267",
}
missing=[k for k,v in required.items() if v not in html]

contracts={
  "canonical_checkin":html.count("canonicalCheckin:true"),
  "checkin_score_ids":sum(html.count(x) for x in ["ciSleep","ciHunger","ciStress","ciEnergy","ciAdh","ciMood","ciMotivation","ciRecovery"]),
  "workout_set_grid":html.count("set-grid"),
  "comments_textareas":len(re.findall(r"<textarea\b",html,re.I)),
  "number_inputs":len(re.findall(r'<input[^>]+type=["\']number["\']',html,re.I)),
  "numeric_input_modes":len(re.findall(r'inputmode=["\'](?:numeric|decimal)["\']',html,re.I)),
}

print("TEAM FJZ V20.67 INPUT CONTRACT AUDIT")
print(json.dumps({"missing":missing,"contracts":contracts},indent=2,ensure_ascii=False))

if missing:
  raise SystemExit("V20.67 missing input/avatar contracts: "+json.dumps(missing))
if contracts["canonical_checkin"]!=1:
  raise SystemExit("V20.67 canonical checkin authority changed")
if contracts["comments_textareas"]<10:
  raise SystemExit("V20.67 unexpected textarea regression")
if "textarea" not in html or "commentsRemainText:true" not in html:
  raise SystemExit("V20.67 comment fields contract missing")
print("TEAM FJZ V20.67 INPUT CONTRACT AUDIT OK")
