import pathlib, re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v119LegacyProfileHardHide">
/* Canonical student profile is V11.5/V11.6 only. Never show retired copies. */
#v86StudentProfileCard,
#v70StudentProfile,
#v86ProfileBtn{
  display:none!important;
  visibility:hidden!important;
  pointer-events:none!important;
  height:0!important;
  min-height:0!important;
  margin:0!important;
  padding:0!important;
  border:0!important;
  overflow:hidden!important;
}
</style>
"""

js=r"""
<script id="v119LegacyProfileHardGuard">
(function(){
  const LEGACY=['v86StudentProfileCard','v70StudentProfile','v86ProfileBtn'];

  function removeLegacyProfileV119(root=document){
    for(const id of LEGACY){
      const node=root.getElementById?root.getElementById(id):document.getElementById(id);
      if(node)node.remove();
    }

    // Defensive dedup of canonical blocks too.
    const profile=[...document.querySelectorAll('#v115StudentProfileCard')];
    profile.slice(1).forEach(n=>n.remove());
    const avatar=[...document.querySelectorAll('#v116AvatarBox')];
    avatar.slice(1).forEach(n=>n.remove());
  }

  // Remove legacy nodes immediately if an older delayed callback tries to reinsert them.
  const obs=new MutationObserver(muts=>{
    if(currentProfile?.role!=='student')return;
    let relevant=false;
    for(const m of muts){
      if(m.addedNodes?.length){relevant=true;break}
    }
    if(relevant)removeLegacyProfileV119();
  });
  obs.observe(document.documentElement,{childList:true,subtree:true});

  const baseRenderV119=window.render;
  window.render=function(){
    const out=baseRenderV119.apply(this,arguments);
    removeLegacyProfileV119();
    queueMicrotask(removeLegacyProfileV119);
    return out;
  };

  document.addEventListener('DOMContentLoaded',removeLegacyProfileV119,{once:true});
  removeLegacyProfileV119();

  // PWA update hardening: reload once when a newer service worker takes control.
  if('serviceWorker' in navigator){
    let refreshed=false;
    navigator.serviceWorker.addEventListener('controllerchange',()=>{
      if(refreshed)return;
      refreshed=true;
      const key='fjz_sw_reload_v119';
      if(sessionStorage.getItem(key)==='1')return;
      sessionStorage.setItem(key,'1');
      location.reload();
    });
    window.addEventListener('load',()=>{
      navigator.serviceWorker.getRegistration().then(reg=>reg?.update?.()).catch(()=>{});
    });
  }

  window.__fjzProfileGuardV119={
    version:'11.9',
    canonicalProfile:'v115StudentProfileCard',
    canonicalAvatar:'v116AvatarBox',
    hardHiddenLegacy:LEGACY
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)
p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8")
sw=re.sub(r"team-fjz-v\d+(?:-\d+)+","team-fjz-v11-9",sw)
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V11.9 profile hard dedup/PWA refresh:",len(html),"bytes")
