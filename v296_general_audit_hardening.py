import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "intervals":len(re.findall(r"setInterval\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

before=metrics(html)

for marker in [
    'meta name="fjz-visual-feedback-fix" content="20.95"',
    "submittedFromCoachPreview",
    "sessionFeedbackCoachReview:true",
    "sessionFeedbackAttachedBeforeCloudCommit:true",
]:
    if marker not in html:
        raise RuntimeError("V20.96 prerequisite missing "+marker)

# Coach preview feedback is valid session context but must never masquerade as
# pending student-origin feedback requiring a second Coach review.
old_needs="""    const needsCoach=!clear&&(types.length>0||comment.length>0||feel==='very_hard');

    pack.sessionFeedbackV241={"""
new_needs="""    const fromCoachPreview=currentProfile?.role==='coach'&&mode==='student';
    const needsCoach=!fromCoachPreview&&!clear&&(types.length>0||comment.length>0||feel==='very_hard');

    pack.sessionFeedbackV241={"""
if html.count(old_needs)!=1:
    raise RuntimeError("V20.96 needsCoach anchor mismatch: "+str(html.count(old_needs)))
html=html.replace(old_needs,new_needs,1)

old_source="""      submittedByRole:String(currentProfile?.role||'student'),
      submittedFromCoachPreview:currentProfile?.role==='coach'&&mode==='student',
      sessionFeel:clear?'normal':feel,"""
new_source="""      submittedByRole:String(currentProfile?.role||'student'),
      submittedFromCoachPreview:fromCoachPreview,
      sessionFeel:clear?'normal':feel,"""
if html.count(old_source)!=1:
    raise RuntimeError("V20.96 source anchor mismatch")
html=html.replace(old_source,new_source,1)

old_status="""      status:needsCoach?'pending':'clear',
      coachReview:null"""
new_status="""      status:fromCoachPreview?'reviewed':(needsCoach?'pending':'clear'),
      coachReview:null"""
if html.count(old_status)!=1:
    raise RuntimeError("V20.96 status anchor mismatch")
html=html.replace(old_status,new_status,1)

old_card="""      '<span>'+esc(fmtDate(ss.date))+' · '+esc(fb.sessionFeelLabel||'Normal')+'</span></div>'+status+'</div>'+"""
new_card="""      '<span>'+esc(fmtDate(ss.date))+' · '+esc(fb.sessionFeelLabel||'Normal')+(fb.submittedFromCoachPreview?' · cargado por Coach':'')+'</span></div>'+status+'</div>'+"""
if html.count(old_card)!=1:
    raise RuntimeError("V20.96 feedback card source anchor mismatch")
html=html.replace(old_card,new_card,1)

old_modal="""          '<strong>Alumno · '+esc(fb.sessionFeelLabel||'Normal')+'</strong>'+"""
new_modal="""          '<strong>'+(fb.submittedFromCoachPreview?'Coach · vista alumno':'Alumno')+' · '+esc(fb.sessionFeelLabel||'Normal')+'</strong>'+"""
if html.count(old_modal)!=1:
    raise RuntimeError("V20.96 feedback modal source anchor mismatch")
html=html.replace(old_modal,new_modal,1)

runtime=r"""
<script id="v296GeneralAuditHardeningRuntime">
window.__fjzV296={
  version:'20.96',
  coachPreviewFeedbackNotStudentPending:true,
  coachPreviewFeedbackOriginVisible:true,
  productionAuditGateExpected:true
};
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-general-audit-hardening" content="20.96">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V20.96 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-general-audit-hardening" content="20.96"',
    "coachPreviewFeedbackNotStudentPending:true",
    "coachPreviewFeedbackOriginVisible:true",
    "const fromCoachPreview=currentProfile?.role==='coach'&&mode==='student';",
    "status:fromCoachPreview?'reviewed':(needsCoach?'pending':'clear')",
    "cargado por Coach",
    "Coach · vista alumno",
]:
    if marker not in html:
        raise RuntimeError("V20.96 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.96 general audit hardening")
print("V20.96 BEFORE:",before)
print("V20.96 AFTER:",after)
