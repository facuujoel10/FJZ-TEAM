import pathlib,re,json
html=pathlib.Path("public/index.html").read_text(encoding="utf-8")
required=[
 'meta name="fjz-routine-library-preparation" content="20.69"',
 "mainLibraryStrengthOnly:true",
 "preparationLibrarySeparated:true",
 "warmupBeforeWorkout:true",
 "stretchingAfterWorkout:true",
 "stableExerciseModalHeader:true",
 "mobileLibraryGeometry:true",
 "prepPersistsInAthleteSnapshot:true",
 "openPrepLibraryV269",
 "removePrepItemV269",
 "v269-prep-editor",
 "v269-library-shell",
]
missing=[x for x in required if x not in html]
print("TEAM FJZ V20.69 ROUTINE UI AUDIT")
print(json.dumps({"missing":missing,"styles":len(re.findall(r"<style\b",html,re.I))},indent=2))
if missing: raise SystemExit("V20.69 missing: "+repr(missing))
if len(re.findall(r"<style\\b",html,re.I))!=1: raise SystemExit("V20.69 stylesheet regression")
print("TEAM FJZ V20.69 ROUTINE UI AUDIT OK")
