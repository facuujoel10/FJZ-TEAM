import pathlib
import re

p = pathlib.Path("public/index.html")
html = p.read_text(encoding="utf-8")

# TEAM FJZ V11.1 · release cleanup
# Solo terminación de producción: no modifica rutinas, alumnos ni estructura de datos.
html = re.sub(r"<title>.*?</title>", "<title>TEAM FJZ · Coaching</title>", html, count=1, flags=re.I | re.S)

if 'name="description"' not in html.lower():
    html = html.replace(
        "</title>",
        '</title>\n<meta name="description" content="TEAM FJZ · Entrenamiento, seguimiento, nutrición y progreso.">',
        1,
    )

html = re.sub(
    r'<div class="footer-note">.*?</div>',
    '<div class="footer-note">TEAM FJZ · COACHING · PROGRESO · RESULTADOS</div>',
    html,
    count=1,
    flags=re.S,
)

html = re.sub(
    r"Chequeo funcional de TEAM FJZ V\d+(?:\.\d+)*\.",
    "Chequeo funcional de TEAM FJZ.",
    html,
)

html = html.replace(
    "La recuperación de contraseña queda lista para producción. El enlace de email funcionará con normalidad cuando configuremos la URL pública definitiva en Supabase.",
    "Recuperación de contraseña lista para producción.",
)

# Mínimo de contraseña más razonable en alta y recuperación.
html = html.replace('minlength="6"', 'minlength="8"')
html = html.replace("password.length<6", "password.length<8")
html = html.replace("a.length<6", "a.length<8")
html = html.replace("Mínimo 6 caracteres", "Mínimo 8 caracteres")
html = html.replace("al menos 6 caracteres", "al menos 8 caracteres")
html = html.replace("Usá al menos 6 caracteres.", "Usá al menos 8 caracteres.")

css = r"""
<style id="v111ReleaseCleanupStyles">
html{-webkit-text-size-adjust:100%}
button{-webkit-tap-highlight-color:transparent;touch-action:manipulation}
button:disabled{opacity:.55;cursor:not-allowed;filter:none!important}
button:focus-visible,.btn:focus-visible,.tab:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{
  outline:2px solid rgba(255,70,82,.95);
  outline-offset:2px;
}
.bottom-nav{padding-bottom:max(8px,env(safe-area-inset-bottom))}
.toast{bottom:max(18px,calc(env(safe-area-inset-bottom) + 10px))}
@media(max-width:520px){
  input,select,textarea{font-size:16px}
}
@media(prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  *,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}
}
</style>
"""

html = html.replace("</head>", css + "\n</head>", 1)
p.write_text(html, encoding="utf-8")

swp = pathlib.Path("public/sw.js")
sw = swp.read_text(encoding="utf-8")
sw = re.sub(r"team-fjz-v\d+(?:-\d+)+", "team-fjz-v11-1", sw)
swp.write_text(sw, encoding="utf-8")

print("TEAM FJZ V11.1 release cleanup:", len(html), "bytes")
