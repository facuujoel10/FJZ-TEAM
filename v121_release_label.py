import pathlib, re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# V12.1: final release-label normalization.
# Runs last in build.py so no older patch can leave a stale visible version.
html = re.sub(r"TEAM FJZ V\d+(?:\.\d+)+", "TEAM FJZ V12.1", html)
html = re.sub(r"(?i)(versi[oó]n\s*[:·-]?\s*)V?11\.0\b", r"\1V12.1", html)

# Stable machine-readable release marker.
marker = '<meta name="fjz-release" content="12.1">'
if 'name="fjz-release"' in html:
    html = re.sub(r'<meta\s+name=["\']fjz-release["\']\s+content=["\'][^"\']*["\']\s*/?>', marker, html, count=1, flags=re.I)
else:
    html = html.replace("</head>", marker + "\n</head>", 1)

runtime = r"""
<script id="v121ReleaseRuntime">
(function(){
  const RELEASE='12.1';
  window.__FJZ_RELEASE__=RELEASE;

  function normalizeReleaseLabels(){
    const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
    const nodes=[];
    while(walker.nextNode())nodes.push(walker.currentNode);
    for(const n of nodes){
      if(/TEAM FJZ V\d+(?:\.\d+)+/i.test(n.nodeValue||'')){
        n.nodeValue=n.nodeValue.replace(/TEAM FJZ V\d+(?:\.\d+)+/gi,'TEAM FJZ V'+RELEASE);
      }
      if(/versi[oó]n\s*[:·-]?\s*V?11\.0\b/i.test(n.nodeValue||'')){
        n.nodeValue=n.nodeValue.replace(/(versi[oó]n\s*[:·-]?\s*)V?11\.0\b/gi,'$1V'+RELEASE);
      }
    }
  }

  document.addEventListener('DOMContentLoaded',normalizeReleaseLabels,{once:true});
  const mo=new MutationObserver(()=>normalizeReleaseLabels());
  mo.observe(document.documentElement,{childList:true,subtree:true});
  setTimeout(normalizeReleaseLabels,100);
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)
p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8")
sw=re.sub(r"team-fjz-v\d+(?:-\d+)+","team-fjz-v12-1",sw)
swp.write_text(sw,encoding="utf-8")

print("TEAM FJZ V12.1 release label normalized:",len(html),"bytes")
