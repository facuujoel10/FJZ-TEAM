import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

old=r"""  // Opening a student from a previously scrolled dashboard can preserve the
  // browser's old scroll before render runs. Catch student selection itself.
  document.addEventListener('click',e=>{
    const row=e.target?.closest?.('.student-row,[data-client-id]');
    if(!row)return;
    requestAnimationFrame(hardTopV180);
  },{capture:true,passive:true});
"""

if html.count(old)!=1:
    raise RuntimeError(f"V18.8 expected one broad dashboard click-scroll listener, got {html.count(old)}")

html=html.replace(old,"",1)

# Safety: navigation scroll should remain route-based only.
if "closest?.('.student-row,[data-client-id]')" in html:
    raise RuntimeError("V18.8 broad student-row click scroll still present")

if "scheduleRouteTopV180(seq)" not in html or "routeKeyV180()" not in html:
    raise RuntimeError("V18.8 route-based scroll authority missing")

js=r"""
<script id="v188ScrollInteractionFixRuntime">
(function(){
  window.__fjzV188={
    version:'18.8',
    broadClickScrollRemoved:true,
    routeOnlyScrollReset:true,
    panelClicksPreserveScroll:true
  };
})();
</script>
"""
html=html.replace("</body>",js+"\n</body>",1)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V18.8 panel click scroll fix enabled")
