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
    'meta name="fjz-session-resilience" content="20.94"',
    "v238-review-badge",
    "v205-prev-load",
    "v104-set-target",
    "v268StudentAvatarPanel",
    "v175CoachAvatarSlot",
    "openSessionFeedbackV241",
    "canSubmitSessionFeedbackV241",
]:
    if marker not in html:
        raise RuntimeError("V20.95 prerequisite missing "+marker)

# ------------------------------------------------------------------
# 1) Feedback must appear for a real student AND Coach -> Student preview.
#    Keep a source flag so review history can distinguish the origin.
# ------------------------------------------------------------------
old_can="""  function canSubmitSessionFeedbackV241(){
    return currentProfile?.role==='student' || !!window.__fjzStagingLocal?.enabled;
  }"""
new_can="""  function canSubmitSessionFeedbackV241(){
    const role=String(currentProfile?.role||'');
    return mode==='student'&&(role==='student'||role==='coach'||!!window.__fjzStagingLocal?.enabled);
  }"""
if html.count(old_can)!=1:
    raise RuntimeError("V20.95 feedback eligibility anchor mismatch: "+str(html.count(old_can)))
html=html.replace(old_can,new_can,1)

old_feedback="""      version:1,
      submittedAt:new Date().toISOString(),
      sessionFeel:clear?'normal':feel,"""
new_feedback="""      version:1,
      submittedAt:new Date().toISOString(),
      submittedByRole:String(currentProfile?.role||'student'),
      submittedFromCoachPreview:currentProfile?.role==='coach'&&mode==='student',
      sessionFeel:clear?'normal':feel,"""
if html.count(old_feedback)!=1:
    raise RuntimeError("V20.95 feedback source anchor mismatch: "+str(html.count(old_feedback)))
html=html.replace(old_feedback,new_feedback,1)

# The close affordance in this modal must not silently look like a completed save.
# Make it explicit that closing returns to the workout without committing.
old_close="""<button class="btn small" type="button" aria-label="Cerrar" title="Cerrar" onclick="closeModal()">✕</button></div>'+"""
new_close="""<button class="btn small" type="button" aria-label="Volver al entrenamiento" title="Volver al entrenamiento" onclick="cancelSessionFeedbackV241()">✕</button></div>'+"""
if html.count(old_close)<1:
    raise RuntimeError("V20.95 feedback close anchor missing")
# Only the feedback modal occurrence needs this semantic change.
idx=html.find("¿Cómo salió la sesión?")
pos=html.find(old_close,idx)
if pos<0:
    raise RuntimeError("V20.95 feedback close occurrence missing")
html=html[:pos]+new_close+html[pos+len(old_close):]

# ------------------------------------------------------------------
# 2) Canonical avatar surfaces: late legacy injectors may still run.
#    The canonical surfaces stay authoritative; legacy duplicates are removed.
# ------------------------------------------------------------------
runtime=r"""
<script id="v295VisualFeedbackRuntime">
(function(){
  function cleanupDuplicateProfilePhotosV295(){
    const coachSlot=document.getElementById('v175CoachAvatarSlot');
    if(coachSlot)document.getElementById('v70CoachStudentAvatar')?.remove();

    const studentPanel=document.getElementById('v268StudentAvatarPanel');
    if(studentPanel)document.getElementById('v70StudentProfile')?.remove();
  }

  const baseApplyProfileV295=window.__fjzApplyProfileUiV268;
  if(typeof baseApplyProfileV295==='function'){
    window.__fjzApplyProfileUiV268=function(){
      cleanupDuplicateProfilePhotosV295();
      const out=baseApplyProfileV295.apply(this,arguments);
      Promise.resolve(out).then(cleanupDuplicateProfilePhotosV295,cleanupDuplicateProfilePhotosV295);
      return out;
    };
  }

  cleanupDuplicateProfilePhotosV295();

  window.__fjzV295={
    version:'20.95',
    singleCanonicalProfilePhoto:true,
    reviewBadgeCentered:true,
    workoutSetGeometryV295:true,
    coachPreviewSessionFeedback:true,
    feedbackSourceTagged:true
  };
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)

# ------------------------------------------------------------------
# 3) Final visual authority for the screenshots supplied by the user.
# ------------------------------------------------------------------
css=r"""
/* TEAM FJZ · V20.95 VISUAL + SESSION FEEDBACK FIX */

/* Legacy avatar nodes can be inserted asynchronously by captured old wrappers.
   If the canonical profile surface exists, the legacy copy is never visible. */
body:has(#v175CoachAvatarSlot) #v70CoachStudentAvatar,
body:has(#v268StudentAvatarPanel) #v70StudentProfile{
  display:none!important;
}

/* Prevent a long athlete name from being squeezed by obsolete identity geometry. */
.v175-coach-profile-info h2{
  word-break:normal!important;
  overflow-wrap:normal!important;
  hyphens:none!important;
}

/* Dashboard review state: center it as a distinct second line instead of leaving
   it attached to the avatar/name flex row. */
@media(max-width:900px){
  .v225-student-list .student-row .student-main{
    display:grid!important;
    grid-template-columns:auto minmax(0,1fr)!important;
    grid-template-rows:auto auto!important;
    column-gap:11px!important;
    row-gap:0!important;
    align-items:center!important;
    min-width:0!important;
  }
  .v225-student-list .student-row .student-main>.v70-student-avatar-slot{
    grid-column:1!important;
    grid-row:1!important;
  }
  .v225-student-list .student-row .student-main>.v70-student-avatar-slot+div{
    grid-column:2!important;
    grid-row:1!important;
    min-width:0!important;
  }
  .v225-student-list .student-row .student-main>.v238-review-badge{
    grid-column:1/-1!important;
    grid-row:2!important;
    justify-self:center!important;
    margin:8px 0 0!important;
    min-height:25px!important;
    padding:5px 10px!important;
    text-align:center!important;
  }
  .v225-student-list .student-row .student-main>.v80-student-alert-count{
    grid-column:2!important;
    justify-self:start!important;
  }
}

/* Workout rows: one consistent baseline for Set/Meta, Kg reference, Reps and RIR. */
.session-card .set-grid{
  grid-template-columns:68px minmax(96px,1.25fr) minmax(62px,.82fr) minmax(62px,.82fr)!important;
  gap:7px!important;
  align-items:stretch!important;
  padding:8px!important;
}
.session-card .set-grid>label{
  display:grid!important;
  grid-template-rows:17px 22px minmax(46px,1fr)!important;
  align-items:center!important;
  min-width:0!important;
  min-height:85px!important;
  margin:0!important;
  text-align:center!important;
  line-height:1.15!important;
}
.session-card .set-grid>label>.v205-prev-load{
  grid-row:2!important;
  align-self:center!important;
  width:100%!important;
  margin:0!important;
  overflow:hidden!important;
  text-overflow:ellipsis!important;
  white-space:nowrap!important;
  text-align:center!important;
  font-size:8px!important;
  letter-spacing:.015em!important;
  text-transform:none!important;
}
.session-card .set-grid>label>.input{
  grid-row:3!important;
  align-self:stretch!important;
  width:100%!important;
  min-width:0!important;
  min-height:46px!important;
  margin:0!important;
  padding:8px 6px!important;
  text-align:center!important;
  font-size:15px!important;
  line-height:1.1!important;
}
.session-card .set-grid>label>.input::placeholder{
  font-size:12px!important;
  font-weight:720!important;
  letter-spacing:0!important;
  text-transform:none!important;
  opacity:.68!important;
}
.session-card .set-grid>.set-n{
  width:100%!important;
  height:auto!important;
  min-height:85px!important;
  margin:0!important;
  padding:8px 4px!important;
  display:flex!important;
  flex-direction:column!important;
  align-items:center!important;
  justify-content:center!important;
  gap:5px!important;
  text-align:center!important;
  line-height:1.05!important;
  overflow:hidden!important;
}
.session-card .set-grid>.set-n>.v104-set-target{
  width:100%!important;
  margin:0!important;
  font-size:10px!important;
  line-height:1.15!important;
  text-align:center!important;
  white-space:normal!important;
  color:#9ec8ff!important;
}
.session-card .set-grid>label:not(:has(.v205-prev-load))>.input{
  grid-row:3!important;
}

/* Feedback itself stays clean on narrow phones. */
.v241-feedback-form .v241-difficulty-grid label{
  justify-content:flex-start!important;
}
@media(max-width:420px){
  .session-card .set-grid{
    grid-template-columns:62px minmax(88px,1.3fr) minmax(58px,.8fr) minmax(58px,.8fr)!important;
    gap:5px!important;
    padding:6px!important;
  }
  .session-card .set-grid>label{
    grid-template-rows:16px 21px minmax(45px,1fr)!important;
    min-height:82px!important;
    font-size:8px!important;
    letter-spacing:.035em!important;
  }
  .session-card .set-grid>.set-n{
    min-height:82px!important;
  }
  .session-card .set-grid>label>.input{
    min-height:45px!important;
    padding:7px 4px!important;
    font-size:14px!important;
  }
  .session-card .set-grid>label>.input::placeholder{
    font-size:11px!important;
  }
  .session-card .set-grid>label>.v205-prev-load{
    font-size:7.5px!important;
  }
}
@media(max-width:360px){
  .session-card .set-grid{
    grid-template-columns:58px minmax(82px,1.25fr) minmax(54px,.78fr) minmax(54px,.78fr)!important;
    gap:4px!important;
  }
}
"""
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.95 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-visual-feedback-fix" content="20.95">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V20.95 topology changed "+key+": "+repr({"before":before,"after":after}))

required=[
    'meta name="fjz-visual-feedback-fix" content="20.95"',
    "singleCanonicalProfilePhoto:true",
    "reviewBadgeCentered:true",
    "workoutSetGeometryV295:true",
    "coachPreviewSessionFeedback:true",
    "feedbackSourceTagged:true",
    "submittedFromCoachPreview",
    "cleanupDuplicateProfilePhotosV295",
    "body:has(#v175CoachAvatarSlot) #v70CoachStudentAvatar",
    "body:has(#v268StudentAvatarPanel) #v70StudentProfile",
    "grid-template-columns:68px minmax(96px,1.25fr)",
    "justify-self:center!important",
]
for marker in required:
    if marker not in html:
        raise RuntimeError("V20.95 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.95 visual/session feedback fix")
print("V20.95 BEFORE:",before)
print("V20.95 AFTER:",after)
