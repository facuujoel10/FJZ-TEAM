import pathlib,re,json

OUT=pathlib.Path("public")
p=OUT/"index.html"
html=p.read_text(encoding="utf-8")
release=pathlib.Path("RELEASE").read_text(encoding="utf-8").strip()

# Single source of truth for every visible/static release label.
html=re.sub(r"TEAM FJZ V\d+(?:\.\d+)+",f"TEAM FJZ V{release}",html)
html=re.sub(r'(?i)(versi[oó]n\s*[:·-]?\s*)V?\d+(?:\.\d+)+',lambda m:m.group(1)+"V"+release,html)

marker=f'<meta name="fjz-release" content="{release}">'
if re.search(r'<meta\s+name=["\']fjz-release["\']',html,re.I):
    html=re.sub(r'<meta\s+name=["\']fjz-release["\']\s+content=["\'][^"\']*["\']\s*/?>',marker,html,count=1,flags=re.I)
else:
    html=html.replace("</head>",marker+"\n</head>",1)

runtime=f"""
<script id="fjzReleaseRuntime">
(function(){{
  const RELEASE={json.dumps(release)};
  window.__FJZ_RELEASE__=RELEASE;

  function normalizeReleaseLabels(){{
    document.querySelectorAll('[data-fjz-version]').forEach(el=>el.textContent='V'+RELEASE);
  }}

  async function checkRelease(){{
    try{{
      const res=await fetch('./version.json?ts='+Date.now(),{{cache:'no-store'}});
      if(!res.ok)return;
      const info=await res.json();
      if(info?.release&&String(info.release)!==RELEASE){{
        const key='fjz_release_reload_'+info.release;
        if(sessionStorage.getItem(key)!=='1'){{
          sessionStorage.setItem(key,'1');
          location.reload();
        }}
      }}
    }}catch(_e){{}}
  }}

  if('serviceWorker' in navigator){{
    window.addEventListener('load',async()=>{{
      try{{
        const reg=await navigator.serviceWorker.register('./sw.js?v='+encodeURIComponent(RELEASE),{{updateViaCache:'none'}});
        await reg.update();
      }}catch(_e){{}}
      checkRelease();
    }},{{once:true}});

    let reloaded=false;
    navigator.serviceWorker.addEventListener('controllerchange',()=>{{
      if(reloaded)return;
      reloaded=true;
      const key='fjz_sw_controller_'+RELEASE;
      if(sessionStorage.getItem(key)==='1')return;
      sessionStorage.setItem(key,'1');
      location.reload();
    }});
  }}else{{
    window.addEventListener('load',checkRelease,{{once:true}});
  }}

  document.addEventListener('visibilitychange',()=>{{
    if(document.visibilityState==='visible')checkRelease();
  }});
  window.addEventListener('focus',checkRelease);
  normalizeReleaseLabels();
}})();
</script>
"""

# Remove previous central release runtime if this build ever runs twice.
html=re.sub(r'<script id="fjzReleaseRuntime">.*?</script>','',html,flags=re.S)
html=html.replace("</body>",runtime+"\n</body>",1)
p.write_text(html,encoding="utf-8")

(OUT/"version.json").write_text(json.dumps({{"release":release}},ensure_ascii=False),encoding="utf-8")

swp=OUT/"sw.js"
sw=swp.read_text(encoding="utf-8")
cache_name="team-fjz-v"+release.replace(".","-")
sw=re.sub(r"const CACHE='[^']+';",f"const CACHE='{cache_name}';",sw,count=1)
if "'./version.json'" not in sw:
    sw=sw.replace("const ASSETS=[", "const ASSETS=['./version.json',")
# Ensure version.json never comes from a stale cache.
fetch_guard="""
  if(url.pathname.endsWith('/version.json')){
    event.respondWith(fetch(req,{cache:'no-store'}));
    return;
  }
"""
needle="  if(req.mode==='navigate'){"
if fetch_guard.strip() not in sw:
    sw=sw.replace(needle,fetch_guard+"\n"+needle,1)
swp.write_text(sw,encoding="utf-8")

print("TEAM FJZ centralized release:",release,"cache:",cache_name)
