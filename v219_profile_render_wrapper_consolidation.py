import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.19 PROFILE RENDER WRAPPER CONSOLIDATION
# =========================================================
# V12.5 already coalesced V11.4-V11.9 visual work into fjzPostRenderV125.
# The six historical render wrappers still form a nested call chain.
#
# Preserve the V11.9 position in the render authority chain and move V11.4-
# V11.8 post-render scheduling into callbacks invoked by that one wrapper.
# Profile UI, async loaders, avatar, cleanup guards and V11.4's separate
# renderCoachStudent hook remain untouched.

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

# V11.4: preserve coach-summary condition and V12.5 scheduler key.
def p114(body):
    old="""  const baseRenderV114=window.render;
  window.render=function(){
    const out=baseRenderV114.apply(this,arguments);
    if(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'){
      fjzPostRenderV125('coach-profile-v114',injectProfileV114);
    }
    return out;
  };"""
    new="""  window.__fjzProfilePostV114=function(){
    if(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'){
      fjzPostRenderV125('coach-profile-v114',injectProfileV114);
    }
  };"""
    return exact(body,old,new,"V11.4 render wrapper")
html=edit_script(html,"v114CoachProfileRuntime",p114)

# V11.5: student profile card.
def p115(body):
    old="""  const baseRenderV115=window.render;
  window.render=function(){
    const out=baseRenderV115.apply(this,arguments);
    if(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'){
      fjzPostRenderV125('student-profile-v115',injectMyProfileV115);
    }
    return out;
  };"""
    new="""  window.__fjzProfilePostV115=function(){
    if(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'){
      fjzPostRenderV125('student-profile-v115',injectMyProfileV115);
    }
  };"""
    return exact(body,old,new,"V11.5 render wrapper")
html=edit_script(html,"v115StudentProfileFieldsRuntime",p115)

# V11.6: student avatar.
def p116(body):
    old="""  const baseRenderV116=window.render;
  window.render=function(){
    const out=baseRenderV116.apply(this,arguments);
    if(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'){
      fjzPostRenderV125('student-avatar-v116',injectAvatarV116);
    }
    return out;
  };"""
    new="""  window.__fjzProfilePostV116=function(){
    if(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'){
      fjzPostRenderV125('student-avatar-v116',injectAvatarV116);
    }
  };"""
    return exact(body,old,new,"V11.6 render wrapper")
html=edit_script(html,"v116StudentAvatarFixRuntime",p116)

# V11.7: dedupe guard.
def p117(body):
    old="""  const baseRenderV117=window.render;
  window.render=function(){
    const out=baseRenderV117.apply(this,arguments);
    if(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'){
      fjzPostRenderV125('profile-clean-v117',cleanupStudentProfileV117);
    }
    return out;
  };"""
    new="""  window.__fjzProfilePostV117=function(){
    if(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'){
      fjzPostRenderV125('profile-clean-v117',cleanupStudentProfileV117);
    }
  };"""
    return exact(body,old,new,"V11.7 render wrapper")
html=edit_script(html,"v117ProfileDedupRuntime",p117)

# V11.8: canonical-card enforcement.
def p118(body):
    old="""  const baseRenderV118=window.render;
  window.render=function(){
    const out=baseRenderV118.apply(this,arguments);
    fjzPostRenderV125('profile-single-v118',enforceSingleStudentProfileV118);
    return out;
  };"""
    new="""  window.__fjzProfilePostV118=function(){
    fjzPostRenderV125('profile-single-v118',enforceSingleStudentProfileV118);
  };"""
    return exact(body,old,new,"V11.8 render wrapper")
html=edit_script(html,"v118AuditCleanupRuntime",p118)

# V11.9 remains at the exact historical location in the nested render chain,
# now dispatching the five preceding profile post tasks before its own guard.
def p119(body):
    old="""  const baseRenderV119=window.render;
  window.render=function(){
    const out=baseRenderV119.apply(this,arguments);
    fjzPostRenderV125('profile-guard-v119',removeLegacyProfileV119);
    return out;
  };"""
    new="""  const baseRenderV119=window.render;
  window.render=function(){
    const out=baseRenderV119.apply(this,arguments);
    window.__fjzProfilePostV114?.();
    window.__fjzProfilePostV115?.();
    window.__fjzProfilePostV116?.();
    window.__fjzProfilePostV117?.();
    window.__fjzProfilePostV118?.();
    fjzPostRenderV125('profile-guard-v119',removeLegacyProfileV119);
    return out;
  };"""
    return exact(body,old,new,"V11.9 consolidated render wrapper")
html=edit_script(html,"v119LegacyProfileHardGuard",p119)

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
    "profile-guard-v119",
    "injectProfileV114",
    "injectMyProfileV115",
    "injectAvatarV116",
    "cleanupStudentProfileV117",
    "enforceSingleStudentProfileV118",
    "removeLegacyProfileV119",
    "openEditStudentProfileV114",
    "openMyProfileV115",
    "__fjzProfileGuardV119",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.19 missing profile behavior: "+repr(missing))

runtime=r"""
<script id="v219ProfileRenderConsolidationRuntime">
(function(){
  window.__fjzV219={
    version:'20.19',
    profileRenderWrappersBefore:6,
    profileRenderWrappersAfter:1,
    profilePostOrderPreserved:true,
    schedulerKeysPreserved:true,
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
print("V20.19 V11.4-V11.9 render wrappers consolidated 6 -> 1")
