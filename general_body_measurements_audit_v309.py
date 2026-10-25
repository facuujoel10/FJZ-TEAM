import pathlib,re,json
root=pathlib.Path(__file__).resolve().parent
html=(root/"public"/"index.html").read_text(encoding="utf-8")
release=(root/"RELEASE").read_text(encoding="utf-8").strip()
m=re.search(r'<script[^>]*id=["\']v309GeneralBodyMeasurementsRuntime["\'][^>]*>(.*?)</script>',html,re.S|re.I)
body=m.group(1) if m else ""
checks={
 "release":tuple(map(int,release.split("."))) >= (21,9),
 "meta":'meta name="fjz-general-body-measurements" content="21.09"' in html,
 "runtime":bool(body),
 "single_arm":"generalArmOnly:true" in body,
 "single_thigh":"generalThighOnly:true" in body,
 "legacy_compatible":"legacySideDataCompatible:true" in body,
 "right_hidden":"rightSideUiRemoved:true" in body,
 "fallback_arm":"firstMeasureV309(m.arm_left_cm,m.arm_right_cm)" in body,
 "fallback_thigh":"firstMeasureV309(m.thigh_left_cm,m.thigh_right_cm)" in body,
 "right_chart_removed":"k==='arm_right_cm'||k==='thigh_right_cm'" in body,
 "labels_general":"'Brazo'" in body and "'Muslo'" in body,
 "no_delete":"noDataDeletion:true" in body,
}
failed=[k for k,v in checks.items() if not v]
print("TEAM FJZ V21.09 GENERAL BODY MEASUREMENTS AUDIT")
print(json.dumps({"release":release,"checks":checks,"failed_checks":failed},indent=2,ensure_ascii=False))
if failed: raise SystemExit("V21.09 GENERAL BODY MEASUREMENTS AUDIT FAILED")
print("TEAM FJZ V21.09 GENERAL BODY MEASUREMENTS AUDIT OK")
