
import pathlib

OUT = pathlib.Path("public")
p = OUT / "index.html"
html = p.read_text(encoding="utf-8")

html = html.replace("TEAM FJZ V8.6", "TEAM FJZ V8.7")

# Check-in: suma motivación como métrica semanal.
html = html.replace(
    "Sueño, estrés, energía, adherencia y estado general.",
    "Sueño, estrés, energía, motivación, adherencia y estado general."
)
html = html.replace(
    "['Ánimo','ciMood',7],['Recuperación','ciRecovery',7]",
    "['Ánimo','ciMood',7],['Motivación','ciMotivation',7],['Recuperación','ciRecovery',7]"
)
html = html.replace(
    "recovery_level:v('ciRecovery'),notes:",
    "recovery_level:v('ciRecovery'),motivation_level:v('ciMotivation'),notes:"
)
html = html.replace(
    "Sueño ${c.sleep_quality}/10 · Estrés ${c.stress_level}/10 · Adherencia ${c.adherence_level}/10",
    "Sueño ${c.sleep_quality}/10 · Estrés ${c.stress_level}/10 · Motivación ${c.motivation_level??'—'}/10 · Adherencia ${c.adherence_level}/10"
)
html = html.replace(
    "wellness:{sleep:avgV53(checks,'sleep_quality'),stress:avgV53(checks,'stress_level'),energy:avgV53(checks,'energy_level'),adherence:avgV53(checks,'adherence_level'),mood:avgV53(checks,'mood_level'),recovery:avgV53(checks,'recovery_level')}",
    "wellness:{sleep:avgV53(checks,'sleep_quality'),stress:avgV53(checks,'stress_level'),energy:avgV53(checks,'energy_level'),motivation:avgV53(checks,'motivation_level'),adherence:avgV53(checks,'adherence_level'),mood:avgV53(checks,'mood_level'),recovery:avgV53(checks,'recovery_level')}"
)

css = r"""
<style id="v87Polish">
/* V8.7 · pulido general de interfaz */
#view,.shell,.card,.hero,.grid,.student-row{min-width:0}
#v86StudentProfileCard{
  position:relative!important;
  inset:auto!important;
  z-index:1!important;
  width:100%!important;
  max-width:100%!important;
  clear:both!important;
  margin:14px 0 18px!important;
  overflow:hidden!important;
}
#v70StudentProfile{
  position:relative!important;
  z-index:2!important;
  max-width:100%;
}
.v86-profile-grid{align-items:stretch}
.v86-profile-field{min-height:64px;display:flex;flex-direction:column;justify-content:center}
.tracking-form{gap:16px!important}
.v701-checkin-scores,.tracking-grid{
  display:grid!important;
  grid-template-columns:repeat(4,minmax(0,1fr))!important;
  gap:10px!important;
}
.v701-checkin-scores .track-score,.tracking-grid .track-score{
  min-width:0!important;
  padding:11px!important;
  border-radius:12px!important;
}
.v701-checkin-scores .track-score label,.tracking-grid .track-score label{
  min-height:0!important;
  margin-bottom:7px!important;
  line-height:1.25;
}
.v70-recipe-grid{
  grid-template-columns:repeat(3,minmax(0,1fr))!important;
  gap:12px!important;
}
.v70-recipe-card{
  min-height:205px;
  padding:14px!important;
  border-radius:15px!important;
  overflow:hidden;
}
.v70-recipe-card h4{font-size:15px!important}
.v70-recipe-meta{margin-top:auto}
.v70-recipe-toolbar{gap:10px!important}
.bottom-nav{isolation:isolate}
@media(max-width:900px){
  .v701-checkin-scores,.tracking-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important}
  .v70-recipe-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important}
}
@media(max-width:760px){
  body{
    padding-bottom:calc(104px + env(safe-area-inset-bottom))!important;
    overflow-x:hidden!important;
  }
  .shell{
    padding:14px 12px calc(116px + env(safe-area-inset-bottom))!important;
    overflow:visible!important;
  }
  #view{width:100%;overflow:visible!important}
  .hero{
    position:relative!important;
    z-index:1!important;
    width:100%!important;
    margin-bottom:14px!important;
    padding:0!important;
    overflow:visible!important;
  }
  #v70StudentProfile{
    width:100%!important;
    margin-top:4px!important;
    padding:10px 0 0!important;
  }
  .v70-profile-head{
    width:100%!important;
    align-items:flex-start!important;
    flex-wrap:wrap!important;
  }
  .v70-profile-head>div:last-child{min-width:0;flex:1 1 180px}
  #v86StudentProfileCard{
    margin:12px 0 16px!important;
    padding:13px!important;
  }
  .v86-profile-grid{grid-template-columns:1fr 1fr!important;gap:8px!important}
  .bottom-nav{
    display:flex!important;
    position:fixed!important;
    left:0!important;
    right:0!important;
    bottom:0!important;
    z-index:90!important;
    overflow-x:auto!important;
    overflow-y:hidden!important;
    flex-wrap:nowrap!important;
    justify-content:flex-start!important;
    gap:3px!important;
    padding:8px max(8px,env(safe-area-inset-right)) calc(8px + env(safe-area-inset-bottom)) max(8px,env(safe-area-inset-left))!important;
    background:rgba(8,8,10,.98)!important;
    border-top:1px solid var(--border)!important;
    box-shadow:0 -10px 30px rgba(0,0,0,.38)!important;
    backdrop-filter:blur(16px)!important;
  }
  .bottom-nav button{
    flex:0 0 auto!important;
    min-width:78px!important;
    min-height:42px!important;
    padding:7px 10px!important;
    border-radius:10px!important;
    white-space:nowrap!important;
  }
  .bottom-nav button.active{background:rgba(255,31,47,.09)!important}
  .v701-checkin-scores,.tracking-grid{grid-template-columns:1fr 1fr!important;gap:8px!important}
  .tracking-form .form-grid{grid-template-columns:1fr 1fr!important}
  .v70-recipe-grid{grid-template-columns:1fr!important}
  .v70-recipe-card{min-height:0}
  .v70-recipe-toolbar{grid-template-columns:1fr!important}
  .modal{padding:14px!important}
  .card{max-width:100%;overflow-wrap:anywhere}
}
@media(max-width:430px){
  .v86-profile-grid{grid-template-columns:1fr!important}
  .tracking-form .form-grid{grid-template-columns:1fr!important}
  .v701-checkin-scores,.tracking-grid{grid-template-columns:1fr 1fr!important}
  .track-score{padding:9px!important}
}
</style>
"""

js = r"""
<script id="v87PolishRuntime">
(function(){
  function removeDuplicateIdV87(id){
    var nodes=document.querySelectorAll('#'+id);
    for(var i=1;i<nodes.length;i++)nodes[i].remove();
  }
  function cleanupUiV87(){
    ['v86StudentProfileCard','v70StudentProfile','v86ProfileBtn','v80Student360'].forEach(removeDuplicateIdV87);
    var nav=document.getElementById('bottomNav');
    if(nav){
      var seen={};
      Array.from(nav.children).forEach(function(btn){
        var key=(btn.textContent||'').trim().toLowerCase();
        if(key&&seen[key])btn.remove(); else if(key)seen[key]=true;
      });
    }
  }

  var oldRenderV87=window.render;
  window.render=function(){
    oldRenderV87();
    setTimeout(cleanupUiV87,30);
    setTimeout(cleanupUiV87,250);
    setTimeout(cleanupUiV87,850);
  };

  var oldTrackingV87=window.renderTrackingStudent;
  if(typeof oldTrackingV87==='function'){
    window.renderTrackingStudent=function(){
      oldTrackingV87();
      setTimeout(function(){
        var scores=document.querySelector('.tracking-grid');
        if(scores)scores.classList.add('v701-checkin-scores');
      },0);
    };
  }

  cleanupUiV87();
})();
</script>
"""

html = html.replace("</head>", css + "\n</head>", 1)
html = html.replace("</body>", js + "\n</body>", 1)

p.write_text(html, encoding="utf-8")

swp = OUT / "sw.js"
sw = swp.read_text(encoding="utf-8")
for old in ("team-fjz-v8-4","team-fjz-v8-5","team-fjz-v8-6"):
    sw = sw.replace(old, "team-fjz-v8-7")
swp.write_text(sw, encoding="utf-8")

print("TEAM FJZ V8.7 polish aplicado:", len(html), "bytes")
