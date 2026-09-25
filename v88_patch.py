
import pathlib

OUT = pathlib.Path("public")
p = OUT / "index.html"
html = p.read_text(encoding="utf-8")

html = html.replace("TEAM FJZ V8.7", "TEAM FJZ V8.8")

css = r"""
<style id="v88Fixes">
.v65-lib-shortcuts{display:none!important}
.v88-version{font-size:9px;color:var(--muted);opacity:.65;margin-top:3px}
</style>
"""

js = r"""
<script id="v88Runtime">
(function(){
  function ensureMotivationV88(){
    if(currentProfile?.role!=='student'||studentTab!=='tracking')return;
    if(document.getElementById('ciMotivation'))return;
    var grid=document.querySelector('.tracking-grid');
    if(!grid)return;
    var card=document.createElement('div');
    card.className='track-score';
    card.innerHTML='<label>Motivación</label><input id="ciMotivation" class="input" type="number" min="1" max="10" value="7">';
    var recovery=document.getElementById('ciRecovery')?.closest('.track-score');
    if(recovery)grid.insertBefore(card,recovery); else grid.appendChild(card);
  }

  function cleanupLibraryShortcutsV88(){
    document.querySelectorAll('.v65-lib-shortcuts').forEach(function(n){n.remove();});
  }

  var oldRenderV88=window.render;
  window.render=function(){
    oldRenderV88();
    setTimeout(function(){ensureMotivationV88();cleanupLibraryShortcutsV88();},20);
    setTimeout(function(){ensureMotivationV88();cleanupLibraryShortcutsV88();},250);
  };

  var oldTrackingV88=window.renderTrackingStudent;
  if(typeof oldTrackingV88==='function'){
    window.renderTrackingStudent=function(){
      oldTrackingV88();
      setTimeout(ensureMotivationV88,0);
    };
  }

  var oldOpenLibraryV88=window.openLibrary;
  if(typeof oldOpenLibraryV88==='function'){
    window.openLibrary=function(dayIndex){
      oldOpenLibraryV88(dayIndex);
      setTimeout(cleanupLibraryShortcutsV88,0);
    };
  }

  setTimeout(function(){
    var brand=document.querySelector('.brand');
    if(brand&&!document.getElementById('v88Version')){
      var v=document.createElement('div');v.id='v88Version';v.className='v88-version';v.textContent='V8.8';brand.appendChild(v);
    }
  },100);
})();
</script>
"""

html = html.replace("</head>", css + "\n</head>", 1)
html = html.replace("</body>", js + "\n</body>", 1)
p.write_text(html, encoding="utf-8")

swp = OUT / "sw.js"
sw = swp.read_text(encoding="utf-8")
for old in ("team-fjz-v8-4","team-fjz-v8-5","team-fjz-v8-6","team-fjz-v8-7"):
    sw = sw.replace(old, "team-fjz-v8-8")
sw = sw.replace(
    "fetch(req).then(res=>{",
    "fetch(new Request(req,{cache:'no-store'})).then(res=>{"
)
swp.write_text(sw, encoding="utf-8")

print("TEAM FJZ V8.8 fixes aplicado:", len(html), "bytes")
