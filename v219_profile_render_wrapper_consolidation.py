import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.19 PROFILE RENDER WRAPPER CONSOLIDATION
# =========================================================
# V14 already removed V11.9's render wrapper and owns the consolidated
# post-render position. V12.5 already coalesced V11.4-V11.8 visual work.
#
# Export V11.4-V11.8 post tasks, remove their five general render wrappers,
# then schedule those tasks from V14 immediately before final-v140.
# This preserves:
# - the same requestAnimationFrame batch,
# - the same task keys/order,
# - V11.4 renderCoachStudent's same-key dedupe,
# - V14's existing finalPass position,
# while reducing render wrapper depth by five.

def metrics(doc):
    return {
        "render_assignments":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

def edit_script(doc,script_id,transform):
    pat=re.compile(
        r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',
        re.S|re.I
    )
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.19 missing script: "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.19 no change in "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

def exact(body,old,new,label):
    if body.count(old)!=1:
        raise RuntimeError("V20.19 "+label+" mismatch: "+str(body.count(old)))
    return body.replace(old,new,1)

before=metrics(html)
if before["render_assignments"]!=27:
    raise RuntimeError("V20.19 unexpected render baseline: "+repr(before))

# V11.4 direct task. Its separate renderCoachStudent hook remains intact and
# uses the same scheduler key, so V14 scheduling dedupes rather than duplicates.
def p114(body):
    old="""  const baseRenderV114=window.render;
  window.render=function(){
    const out=baseRenderV114.apply(this,arguments);
    if(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'){
      fjzPostRenderV125('coach-profile-v114',injectProfileV114);
    }
    return out;
  };"""
    new="""  window.__fjzProfilePostV114=injectProfileV114;"""
    return exact(body,old,new,"V11.4 render wrapper")
html=edit_script(html,"v114CoachProfileRuntime",p114)

# V11.5 direct student-profile task.
def p115(body):
    old="""  const baseRenderV115=window.render;
  window.render=function(){
    const out=baseRenderV115.apply(this,arguments);
    if(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'){
      fjzPostRenderV125('student-profile-v115',injectMyProfileV115);
    }
    return out;
  };"""
    new="""  window.__fjzProfilePostV115=injectMyProfileV115;"""
    return exact(body,old,new,"V11.5 render wrapper")
html=edit_script(html,"v115StudentProfileFieldsRuntime",p115)

# V11.6 direct avatar task.
def p116(body):
    old="""  const baseRenderV116=window.render;
  window.render=function(){
    const out=baseRenderV116.apply(this,arguments);
    if(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'){
      fjzPostRenderV125('student-avatar-v116',injectAvatarV116);
    }
    return out;
  };"""
    new="""  window.__fjzProfilePostV116=injectAvatarV116;"""
    return exact(body,old,new,"V11.6 render wrapper")
html=edit_script(html,"v116StudentAvatarFixRuntime",p116)

# V11.7 direct dedupe task.
def p117(body):
    old="""  const baseRenderV117=window.render;
  window.render=function(){
    const out=baseRenderV117.apply(this,arguments);
    if(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'){
      fjzPostRenderV125('profile-clean-v117',cleanupStudentProfileV117);
    }
    return out;
  };"""
    new="""  window.__fjzProfilePostV117=cleanupStudentProfileV117;"""
    return exact(body,old,new,"V11.7 render wrapper")
html=edit_script(html,"v117ProfileDedupRuntime",p117)

# V11.8 direct single-profile enforcement task.
def p118(body):
    old="""  const baseRenderV118=window.render;
  window.render=function(){
    const out=baseRenderV118.apply(this,arguments);
    fjzPostRenderV125('profile-single-v118',enforceSingleStudentProfileV118);
    return out;
  };"""
    new="""  window.__fjzProfilePostV118=enforceSingleStudentProfileV118;"""
    return exact(body,old,new,"V11.8 render wrapper")
html=edit_script(html,"v118AuditCleanupRuntime",p118)

# V14 owns the exact historical outer position. Schedule the exported profile
# tasks in the same order/conditions that the nested wrappers used, then keep
# final-v140 exactly where it already was.
def p140(body):
    old="""  const baseRenderV140=render;
  render=function(){
    const out=baseRenderV140.apply(this,arguments);
    fjzPostRenderV125('final-v140',finalPass);
    return out;
  };"""
    new="""  const baseRenderV140=render;
  render=function(){
    const out=baseRenderV140.apply(this,arguments);

    if(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'){
      fjzPostRenderV125('coach-profile-v114',window.__fjzProfilePostV114);
    }
    if(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'){
      fjzPostRenderV125('student-profile-v115',window.__fjzProfilePostV115);
      fjzPostRenderV125('student-avatar-v116',window.__fjzProfilePostV116);
      fjzPostRenderV125('profile-clean-v117',window.__fjzProfilePostV117);
    }
    fjzPostRenderV125('profile-single-v118',window.__fjzProfilePostV118);

    fjzPostRenderV125('final-v140',finalPass);
    return out;
  };"""
    return exact(body,old,new,"V14 render authority")
html=edit_script(html,"v140ConsolidatedRuntime",p140)

after=metrics(html)
if after["render_assignments"]!=22:
    raise RuntimeError("V20.19 expected render assignments 27 -> 22: "+repr({"before":before,"after":after}))
if after["timeouts"]!=before["timeouts"]:
    raise RuntimeError("V20.19 must not add/remove timeout behavior")
if after["rafs"]!=before["rafs"]:
    raise RuntimeError("V20.19 must not add/remove RAF behavior")

critical=[
    "__fjzProfilePostV114",
    "__fjzProfilePostV115",
    "__fjzProfilePostV116",
    "__fjzProfilePostV117",
    "__fjzProfilePostV118",
    "coach-profile-v114",
    "student-profile-v115",
    "student-avatar-v116",
    "profile-clean-v117",
    "profile-single-v118",
    "final-v140",
    "window.__fjzRemoveLegacyProfileV119",
    "injectProfileV114",
    "injectMyProfileV115",
    "injectAvatarV116",
    "cleanupStudentProfileV117",
    "enforceSingleStudentProfileV118",
    "openEditStudentProfileV114",
    "openMyProfileV115",
    "__fjzProfileGuardV119",
    "consolidatedRuntime:true",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.19 missing profile behavior: "+repr(missing))

runtime=r"""
<script id="v219ProfileRenderConsolidationRuntime">
(function(){
  window.__fjzV219={
    version:'20.19',
    profileGeneralRenderWrappersBefore:5,
    profileGeneralRenderWrappersAfter:0,
    v14AuthorityReused:true,
    sameFrameSchedulingPreserved:true,
    schedulerKeysPreserved:true,
    coachTargetedHookPreserved:true,
    profileUiPreserved:true,
    avatarUiPreserved:true,
    dedupGuardsPreserved:true,
    behaviorChange:false
  };
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.19 profile render wrapper consolidation")
print("V20.19 BEFORE:",before)
print("V20.19 AFTER:",after)
print("V20.19 V11.4-V11.8 general render wrappers consolidated into V14: 5 -> 0")
