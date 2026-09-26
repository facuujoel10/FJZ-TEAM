import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

for sid in ["v88Fixes","v91CheckinPolish","v92CoachPhotoUpload","v98PrecisionPolish","v99AuditPolish"]:
    pattern=r'<style\s+id=["\']'+re.escape(sid)+r'["\'][^>]*>.*?</style>\s*'
    html=re.sub(pattern,'',html,flags=re.S|re.I)

for sid in ["v88Runtime","v90MotivationFix","v91CheckinClamp","v92CoachPhotoUploadRuntime","v98PrecisionPolishRuntime","v99AuditRuntime"]:
    pattern=r'<script\s+id=["\']'+re.escape(sid)+r'["\'][^>]*>.*?</script>\s*'
    html=re.sub(pattern,'',html,flags=re.S|re.I)

html=re.sub(r'\n{4,}','\n\n\n',html)
p.write_text(html,encoding="utf-8")
print("TEAM FJZ V10.0 legacy layers removed:",len(html),"bytes")
