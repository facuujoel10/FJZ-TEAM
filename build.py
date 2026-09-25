import base64
import pathlib
import re
import urllib.request

SOURCE = "https://cujipwacwwpejhqjhnkr.supabase.co/functions/v1/team-fjz-source"
OUT = pathlib.Path("public")
OUT.mkdir(parents=True, exist_ok=True)

req = urllib.request.Request(SOURCE, headers={"User-Agent": "TEAM-FJZ-Render-Build/1.0"})
with urllib.request.urlopen(req, timeout=60) as response:
    html = response.read().decode("utf-8")

if "<!doctype html" not in html.lower() or "TEAM FJZ" not in html:
    raise RuntimeError("La fuente de TEAM FJZ no devolvió la aplicación esperada.")

# V8.4: misma aplicación V8.3, con ajustes finales de publicación/PWA.
html = html.replace("TEAM FJZ V8.3", "TEAM FJZ V8.4")
html = html.replace("// ===== TEAM FJZ V8.3", "// ===== TEAM FJZ V8.4")
html = html.replace("/* TEAM FJZ V8.3", "/* TEAM FJZ V8.4")
html = html.replace(
    "<link rel=\"manifest\" href=\"./manifest.webmanifest\">",
    "<link rel=\"manifest\" href=\"./manifest.webmanifest\">\n"
    "<link rel=\"apple-touch-icon\" href=\"./icon-v84.webp\">\n"
    "<meta name=\"format-detection\" content=\"telephone=no\">"
)

# Elimina el registro antiguo duplicado del service worker; se conserva registerPwaV82().
html = html.replace(
    "if('serviceWorker' in navigator && location.protocol.startsWith('http'))window.addEventListener('load',()=>navigator.serviceWorker.register('./sw.js').catch(()=>{}));",
    ""
)

# Extrae el logo WebP embebido para usarlo como icono PWA.
icons = re.findall(r"data:image/webp;base64,([A-Za-z0-9+/=]+)", html)
if icons:
    logo_b64 = max(icons, key=len)
    icon_bytes = base64.b64decode(logo_b64)
    if len(icon_bytes) < 1000:
        raise RuntimeError("El icono TEAM FJZ encontrado es demasiado pequeño.")
    (OUT / "icon-v84.webp").write_bytes(icon_bytes)
else:
    raise RuntimeError("No se encontró el icono TEAM FJZ embebido.")

(OUT / "index.html").write_text(html, encoding="utf-8")

manifest = """{
  "name": "TEAM FJZ",
  "short_name": "TEAM FJZ",
  "description": "Coaching de entrenamiento, seguimiento, nutrición y progreso.",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "background_color": "#08080a",
  "theme_color": "#0a0a0c",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "./icon-v84.webp",
      "sizes": "any",
      "type": "image/webp",
      "purpose": "any maskable"
    }
  ]
}
"""
(OUT / "manifest.webmanifest").write_text(manifest, encoding="utf-8")

sw = """const CACHE='team-fjz-v8-4';
const ASSETS=['./','./index.html','./manifest.webmanifest','./icon-v84.webp'];

self.addEventListener('install',event=>{
  event.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).catch(()=>{}));
  self.skipWaiting();
});

self.addEventListener('activate',event=>{
  event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener('fetch',event=>{
  const req=event.request;
  if(req.method!=='GET') return;
  const url=new URL(req.url);
  if(url.origin!==self.location.origin) return;
  if(req.mode==='navigate'){
    event.respondWith(
      fetch(req).then(res=>{
        if(res.ok){
          const copy=res.clone();
          caches.open(CACHE).then(c=>c.put('./index.html',copy)).catch(()=>{});
        }
        return res;
      }).catch(()=>caches.match('./index.html'))
    );
    return;
  }
  event.respondWith(caches.match(req).then(hit=>hit||fetch(req)));
});
"""
(OUT / "sw.js").write_text(sw, encoding="utf-8")

print("TEAM FJZ V8.4 lista para publicar:", len(html), "bytes")
