import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()
m=re.search(r'<script[^>]*id=["\']v315DecimalWorkoutWeightsRuntime["\'][^>]*>(.*?)</script>',html,re.S|re.I)
body=m.group(1) if m else ""
checks={
 "release":tuple(map(int,release.split("."))) >= (21,15),
 "meta":'meta name="fjz-decimal-workout-weights" content="21.15"' in html,
 "runtime":bool(body),
 "dot_decimal":"workoutWeightDotDecimal:true" in body,
 "comma_decimal":"workoutWeightCommaDecimal:true" in body,
 "comma_normalized":"replace(',','.')" in body,
 "text_decimal_input":"input.type='text'" in body and "input.inputMode='decimal'" in body,
 "weight_only":"isWeightFieldV315" in body and "\\brir\\b|rep" in body,
 "set_workout_normalization":"Number(field)===0" in body,
 "reps_integer":"repsRemainInteger:true" in body,
 "rir_integer":"rirRemainInteger:true" in body,
 "numeric_storage":"numericStoragePreserved:true" in body,
 "no_listeners":"addEventListener" not in body,
 "no_timers":"setTimeout" not in body and "setInterval" not in body,
}
failed=[k for k,v in checks.items() if not v]
print("TEAM FJZ V21.15 DECIMAL WORKOUT WEIGHTS AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.15 DECIMAL WORKOUT WEIGHTS AUDIT FAILED")
print("TEAM FJZ V21.15 DECIMAL WORKOUT WEIGHTS AUDIT OK")
