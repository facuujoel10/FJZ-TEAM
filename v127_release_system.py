import pathlib,re,json

OUT=pathlib.Path("public")
p=OUT/"index.html"
html=p.read_text(encoding="utf-8")
release=pathlib.Path("RELEASE").read_text(encoding="utf-8").strip()

# FINAL version authority: rewrite every historical release constant/assignment
# before scripts execute. This prevents old layers (e.g. V12.4) from restoring
# stale labels on every render.
html=re.sub(
    r"(const\s+RELEASE\s*=\s*)['\"]\d+(?:\.\d+)+['\"]",
    lambda m:m.group(1)+json.dumps(release),
    html
)
html=re.sub(
    r"(window\.__FJZ_RELEASE__\s*=\s*)['\"]\d+(?:\.\d+)+['\"]",
    lambda m:m.group(1)+json.dumps(release),
    html
)

# Single source of truth for every visible/static release label.
html=re.sub(r"TEAM FJZ V\d+(?:\.\d+)+",f"TEAM FJZ V{release}",html)
html=re.sub(
    r'(?i)(versi[oó]n\s*[:·-]?\s*)V?\d+(?:\.\d+)+',
    lambda m:m.group(1)+"V"+release,
    html
)

# Remove the legacy V11.9 PWA updater so only the centralized updater remains.
legacy_pwa_block = r"""
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
"""
html, legacy_pwa_removed = html.replace(legacy_pwa_block, ""), (1 if legacy_pwa_block in html else 0)

marker=f'<meta name="fjz-release" content="{release}">'
if re.search(r'<meta\s+name=["\']fjz-release["\']',html,re.I):
    html=re.sub(
        r'<meta\s+name=["\']fjz-release["\']\s+content=["\'][^"\']*["\']\s*/?>',
        marker,html,count=1,flags=re.I
    )
else:
    html=html.replace("</head>",marker+"\n</head>",1)

runtime=fr"""
<script id="fjzReleaseRuntime">
(function(){{
  const RELEASE={json.dumps(release)};
  window.__FJZ_RELEASE__=RELEASE;

  function fixTextNode(node){{
    if(!node||node.nodeType!==Node.TEXT_NODE)return;
    const before=node.nodeValue||'';
    let after=before
      .replace(/TEAM FJZ V\d+(?:\.\d+)+/gi,'TEAM FJZ V'+RELEASE)
      .replace(/(versi[oó]n\s*[:·-]?\s*)V?\d+(?:\.\d+)+/gi,'$1V'+RELEASE);
    if(after!==before)node.nodeValue=after;
  }}

  function normalizeReleaseLabels(root=document.body){{
    document.querySelectorAll('[data-fjz-version]').forEach(el=>el.textContent='V'+RELEASE);
    if(!root)return;
    const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
    while(walker.nextNode())fixTextNode(walker.currentNode);
  }}

  async function checkRelease(){{
    try{{
      const res=await fetch('./version.json?ts='+Date.now(),{{
        cache:'no-store',
        headers:{{'Cache-Control':'no-cache'}}
      }});
      if(!res.ok)return;
      const info=await res.json();
      const server=String(info?.release||'');
      if(server&&server!==RELEASE){{
        const key='fjz_release_reload_'+server;
        if(sessionStorage.getItem(key)!=='1'){{
          sessionStorage.setItem(key,'1');
          location.replace(location.pathname+'?v='+encodeURIComponent(server)+location.hash);
        }}
      }}
    }}catch(_e){{}}
  }}

  // Guard against any legacy runtime or delayed DOM injection writing an old version.
  const versionObserver=new MutationObserver(muts=>{{
    for(const m of muts){{
      if(m.type==='characterData')fixTextNode(m.target);
      for(const n of m.addedNodes||[]){{
        if(n.nodeType===Node.TEXT_NODE)fixTextNode(n);
        else if(n.nodeType===Node.ELEMENT_NODE)normalizeReleaseLabels(n);
      }}
    }}
  }});
  if(document.documentElement){{
    versionObserver.observe(document.documentElement,{{
      childList:true,subtree:true,characterData:true
    }});
  }}

  if('serviceWorker' in navigator){{
    window.addEventListener('load',async()=>{{
      try{{
        const regs=await navigator.serviceWorker.getRegistrations();
        for(const reg of regs){{
          if(reg.active?.scriptURL&&!reg.active.scriptURL.includes('sw.js')){{
            try{{await reg.unregister()}}catch(_e){{}}
          }}
        }}
        const reg=await navigator.serviceWorker.register(
          './sw.js?v='+encodeURIComponent(RELEASE),
          {{updateViaCache:'none'}}
        );
        await reg.update();
      }}catch(_e){{}}
      normalizeReleaseLabels();
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
    window.addEventListener('load',()=>{{
      normalizeReleaseLabels();
      checkRelease();
    }},{{once:true}});
  }}

  document.addEventListener('visibilitychange',()=>{{
    if(document.visibilityState==='visible'){{
      normalizeReleaseLabels();
      checkRelease();
    }}
  }});
  window.addEventListener('focus',()=>{{
    normalizeReleaseLabels();
    checkRelease();
  }});

  normalizeReleaseLabels();
}})();
</script>
"""

# Replace any prior central release runtime with exactly one final runtime.
html=re.sub(r'<script id="fjzReleaseRuntime">.*?</script>','',html,flags=re.S)
html=html.replace("</body>",runtime+"\n</body>",1)
p.write_text(html,encoding="utf-8")

(OUT/"version.json").write_text(
    json.dumps({"release":release,"cache":"team-fjz-v"+release.replace(".","-")},ensure_ascii=False),
    encoding="utf-8"
)

swp=OUT/"sw.js"
sw=swp.read_text(encoding="utf-8")
cache_name="team-fjz-v"+release.replace(".","-")
sw=re.sub(r"const CACHE='[^']+';",f"const CACHE='{cache_name}';",sw,count=1)

# Do not precache version.json; it must always represent the server release.
sw=sw.replace("'./version.json',","")
sw=sw.replace(", './version.json'","")

fetch_guard="""
  if(url.pathname.endsWith('/version.json')){
    event.respondWith(fetch(req,{cache:'no-store'}));
    return;
  }
"""
needle="  if(req.mode==='navigate'){"
if fetch_guard.strip() not in sw:
    sw=sw.replace(needle,fetch_guard+"\n"+needle,1)

# Always prefer the network for the application shell; cache is only offline fallback.
sw=sw.replace(
"""      fetch(req).then(res=>{
        if(res.ok){
          const copy=res.clone();
          caches.open(CACHE).then(c=>c.put('./index.html',copy)).catch(()=>{});
        }
        return res;
      }).catch(()=>caches.match('./index.html'))""",
"""      fetch(req,{cache:'no-store'}).then(res=>{
        if(res.ok){
          const copy=res.clone();
          caches.open(CACHE).then(c=>c.put('./index.html',copy)).catch(()=>{});
        }
        return res;
      }).catch(()=>caches.match('./index.html'))"""
)

swp.write_text(sw,encoding="utf-8")

# Build-time assertions: fail deploy instead of publishing an inconsistent release.
final_html=p.read_text(encoding="utf-8")
legacy_constants=re.findall(r"const\s+RELEASE\s*=\s*['\"](\d+(?:\.\d+)+)['\"]",final_html)
wrong=[v for v in legacy_constants if v!=release]
if wrong:
    raise RuntimeError(f"Stale RELEASE constants remain: {wrong}")
if f'TEAM FJZ V{release}' not in final_html:
    raise RuntimeError("Current visible release label missing")
if f"const CACHE='{cache_name}'" not in sw:
    raise RuntimeError("Service Worker cache does not match release")
controller_handlers = final_html.count("controllerchange")
if controller_handlers != 1:
    raise RuntimeError(f"Expected exactly 1 controllerchange handler, found {controller_handlers}")

print("TEAM FJZ release authority:",release)
print("TEAM FJZ cache authority:",cache_name)
print("TEAM FJZ stale release constants:",len(wrong))
print("TEAM FJZ legacy PWA updater removed:",legacy_pwa_removed)
print("TEAM FJZ controllerchange handlers:",controller_handlers)
