import pathlib, re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

js=r"""
<script id="v117ProfileDedupRuntime">
(function(){
  function cleanupStudentProfileV117(){
    if(currentProfile?.role!=='student'||mode!=='student'||studentTab!=='home')return;

    // V8.6/V9.7 legacy personal-data card: superseded by V11.5.
    const legacyProfile=el('v86StudentProfileCard');
    if(legacyProfile)legacyProfile.remove();

    // V7 legacy avatar block: superseded by avatar inside V11.5/V11.6 "Mis datos".
    const legacyAvatar=el('v70StudentProfile');
    if(legacyAvatar)legacyAvatar.remove();

    // Safety: remove any legacy personal-data button left in old containers.
    const legacyBtn=el('v86ProfileBtn');
    if(legacyBtn)legacyBtn.remove();
  }

  const baseRenderV117=window.render;
  window.render=function(){
    const out=baseRenderV117.apply(this,arguments);
    if(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'){
      setTimeout(cleanupStudentProfileV117,20);
      setTimeout(cleanupStudentProfileV117,180);
      setTimeout(cleanupStudentProfileV117,800);
    }
    return out;
  };

  // Older injectors can still fire from delayed callbacks after render.
  // Neutralize only the student-facing duplicates; coach avatar/profile remain untouched.
  if(typeof window.injectStudentProfileV70==='function'){
    window.injectStudentProfileV70=async function(){ return; };
  }

  setTimeout(cleanupStudentProfileV117,200);
})();
</script>
"""

html=html.replace("</body>",js+"\n</body>",1)
p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8")
sw=re.sub(r"team-fjz-v\d+(?:-\d+)+","team-fjz-v11-7",sw)
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V11.7 profile dedup:",len(html),"bytes")
