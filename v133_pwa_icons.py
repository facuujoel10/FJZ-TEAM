import pathlib,re,subprocess,sys,io

OUT=pathlib.Path("public")
html_path=OUT/"index.html"
manifest_path=OUT/"manifest.json"
sw_path=OUT/"sw.js"

# Ensure Pillow is available to convert the embedded TEAM FJZ WebP logo to
# platform-standard PNG icons. Pin the version for reproducible builds.
try:
    from PIL import Image
except Exception:
    subprocess.run([sys.executable,"-m","pip","install","Pillow==11.3.0"],check=True)
    from PIL import Image

source=OUT/"icon-v84.webp"
if not source.exists():
    raise RuntimeError("TEAM FJZ source icon is missing")

img=Image.open(source).convert("RGBA")
bbox=img.getbbox()
if bbox:
    img=img.crop(bbox)

def square_icon(size,pad_ratio=0.08,bg=(8,8,10,255)):
    canvas=Image.new("RGBA",(size,size),bg)
    usable=int(size*(1-pad_ratio*2))
    copy=img.copy()
    copy.thumbnail((usable,usable),Image.Resampling.LANCZOS)
    x=(size-copy.width)//2
    y=(size-copy.height)//2
    canvas.alpha_composite(copy,(x,y))
    return canvas.convert("RGB")

# Standard icon set. Maskable gets a slightly larger safety padding.
square_icon(512,0.08).save(OUT/"icon-512-v133.png","PNG",optimize=True)
square_icon(512,0.14).save(OUT/"icon-maskable-512-v133.png","PNG",optimize=True)
square_icon(192,0.08).save(OUT/"icon-192-v133.png","PNG",optimize=True)
square_icon(180,0.08).save(OUT/"apple-touch-icon-v133.png","PNG",optimize=True)
square_icon(32,0.04).save(OUT/"favicon-32-v133.png","PNG",optimize=True)

html=html_path.read_text(encoding="utf-8")

# Replace all historical icon declarations with one canonical, versioned set.
html=re.sub(r'<link\s+rel=["\']apple-touch-icon["\'][^>]*>','',html,flags=re.I)
html=re.sub(r'<link\s+rel=["\']icon["\'][^>]*>','',html,flags=re.I)
icon_links="""<link rel="apple-touch-icon" sizes="180x180" href="./apple-touch-icon-v133.png">
<link rel="icon" type="image/png" sizes="32x32" href="./favicon-32-v133.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="TEAM FJZ">
<meta name="application-name" content="TEAM FJZ">"""
html=html.replace("</head>",icon_links+"\n</head>",1)
html_path.write_text(html,encoding="utf-8")

manifest="""{
  "name": "TEAM FJZ",
  "short_name": "TEAM FJZ",
  "description": "Coaching de entrenamiento, seguimiento, nutrición y progreso.",
  "id": "./?app=team-fjz-v133",
  "start_url": "./?source=pwa",
  "scope": "./",
  "display": "standalone",
  "background_color": "#08080a",
  "theme_color": "#0a0a0c",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "./icon-192-v133.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "./icon-512-v133.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "./icon-maskable-512-v133.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable"
    }
  ]
}
"""
manifest_path.write_text(manifest,encoding="utf-8")

sw=sw_path.read_text(encoding="utf-8")
assets=[
    "'./icon-192-v133.png'",
    "'./icon-512-v133.png'",
    "'./icon-maskable-512-v133.png'",
    "'./apple-touch-icon-v133.png'",
    "'./favicon-32-v133.png'"
]
# Add versioned icons to the precache array if an ASSETS array exists.
m=re.search(r"const ASSETS=\[(.*?)\];",sw,re.S)
if m:
    body=m.group(1)
    for a in assets:
        if a not in body:
            body += ","+a
    sw=sw[:m.start(1)]+body+sw[m.end(1):]
sw_path.write_text(sw,encoding="utf-8")

# Build-time validation.
for name,size in [
    ("icon-192-v133.png",(192,192)),
    ("icon-512-v133.png",(512,512)),
    ("icon-maskable-512-v133.png",(512,512)),
    ("apple-touch-icon-v133.png",(180,180)),
    ("favicon-32-v133.png",(32,32)),
]:
    q=OUT/name
    if not q.exists() or Image.open(q).size!=size:
        raise RuntimeError("Invalid PWA icon: "+name)

if '"sizes": "any"' in manifest:
    raise RuntimeError("Legacy manifest icon sizing remains")
if "icon-v84.webp" in manifest:
    raise RuntimeError("Legacy WebP manifest icon remains")

print("TEAM FJZ V13.3 PWA icons:", "PNG 192/512/maskable/180/32")
