import pathlib, re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# V11.8 audit cleanup:
# Remove superseded student-facing profile/avatar injectors at build time.
# Coach-facing avatar/profile logic remains intact.

html, n1 = re.subn(
    r"async function injectStudentProfileV70\(\)\{.*?\n\}\n\nasync function loadCoachAvatarsV70\(\)",
    "async function injectStudentProfileV70(){return;}\n\nasync function loadCoachAvatarsV70()",
    html,
    count=1,
    flags=re.S,
)

html, n2 = re.subn(
    r"async function injectStudentProfileV86\(\)\{.*?\n  \}\n\n  async function injectCoachProfileV86\(\)",
    "async function injectStudentProfileV86(){return;}\n\n  async function injectCoachProfileV86()",
    html,
    count=1,
    flags=re.S,
)

# Remove V9.7 legacy additions that only targeted the retired student profile card.
html = re.sub(
    r"\n\s*const studentGrid=document\.querySelector\('#v86StudentProfileCard \.v86-profile-grid'\);\s*"
    r"if\(studentGrid&&!studentGrid\.querySelector\('\[data-v97-extra\]'\)\)\{.*?\n\s*\}\n",
    "\n",
    html,
    count=1,
    flags=re.S,
)

# Final runtime guard: keep one canonical student profile card/avatar block.
guard = r"""
<script id="v118AuditCleanupRuntime">
(function(){
  function enforceSingleStudentProfileV118(){
    if(currentProfile?.role!=='student'||mode!=='student'||studentTab!=='home')return;
    document.querySelectorAll('#v86StudentProfileCard,#v70StudentProfile').forEach(x=>x.remove());

    const cards=[...document.querySelectorAll('#v115StudentProfileCard')];
    cards.slice(1).forEach(x=>x.remove());

    const avatars=[...document.querySelectorAll('#v116AvatarBox')];
    avatars.slice(1).forEach(x=>x.remove());
  }

  const baseRenderV118=window.render;
  window.render=function(){
    const out=baseRenderV118.apply(this,arguments);
    setTimeout(enforceSingleStudentProfileV118,50);
    setTimeout(enforceSingleStudentProfileV118,400);
    return out;
  };

  setTimeout(enforceSingleStudentProfileV118,250);

  window.__fjzAuditV118={
    version:'11.8',
    legacyStudentProfileDisabled:true,
    legacyStudentAvatarDisabled:true,
    canonicalProfile:'v115StudentProfileCard',
    canonicalAvatar:'v116AvatarBox'
  };
})();
</script>
"""
html=html.replace("</body>",guard+"\n</body>",1)

p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8")
sw=re.sub(r"team-fjz-v\d+(?:-\d+)+","team-fjz-v11-8",sw)
swp.write_text(sw,encoding="utf-8")

print("TEAM FJZ V11.8 audit cleanup:",len(html),"bytes","legacy70",n1,"legacy86",n2)
