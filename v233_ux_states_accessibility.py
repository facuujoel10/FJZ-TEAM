import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.33 UX STATES + ACCESSIBILITY
# =========================================================
# Static semantics + CSS only. No runtime listeners/wrappers/timers/channels.

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "render_assignments":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "start_assignments":len(re.findall(r"(?:window\.)?startWorkout\s*=",doc)),
        "finish_assignments":len(re.findall(r"(?:window\.)?finishWorkout\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

before=metrics(html)
if before["styles"]!=1:
    raise RuntimeError("V20.33 expected one stylesheet: "+repr(before))

# ---------- Static app-shell semantics ----------
replacements=[
    (
      '<main class="shell" id="view"></main>',
      '<main class="shell" id="view" aria-label="Contenido principal"></main>',
      "main landmark"
    ),
    (
      '<nav class="bottom-nav" id="bottomNav"></nav>',
      '<nav class="bottom-nav" id="bottomNav" aria-label="Navegación principal"></nav>',
      "bottom nav label"
    ),
    (
      '<div class="toast" id="toast"></div>',
      '<div class="toast" id="toast" role="status" aria-live="polite" aria-atomic="true"></div>',
      "toast live region"
    ),
    (
      '<div class="modal-wrap" id="modalWrap" onclick="if(event.target===this)closeModal()"><div class="modal" id="modal"></div></div>',
      '<div class="modal-wrap" id="modalWrap" role="presentation" onclick="if(event.target===this)closeModal()"><div class="modal" id="modal" role="dialog" aria-modal="true" tabindex="-1"></div></div>',
      "modal semantics"
    ),
    (
      '<button id="cloudStatusBtn" class="btn small cloud-chip" type="button">',
      '<button id="cloudStatusBtn" class="btn small cloud-chip" type="button" aria-label="Estado de sincronización" aria-live="polite">',
      "cloud status semantics"
    )
]

for old,new,label in replacements:
    if html.count(old)!=1:
        raise RuntimeError("V20.33 "+label+" mismatch: "+str(html.count(old)))
    html=html.replace(old,new,1)

# ---------- Accessible close buttons ----------
# Preserve onclick/class/text exactly; only add type + accessible name.
close_pat=re.compile(
    r'<button class="btn small" onclick="closeModal\(\)">✕</button>'
)
close_count=len(close_pat.findall(html))
if close_count<1:
    raise RuntimeError("V20.33 no canonical close buttons found")
html=close_pat.sub(
    '<button class="btn small" type="button" aria-label="Cerrar" title="Cerrar" onclick="closeModal()">✕</button>',
    html
)

css=r"""
/* TEAM FJZ · V20.33 UX STATES + ACCESSIBILITY */

/* Empty / no-data states */
.empty{
  min-height:92px;
  display:flex;
  align-items:center;
  justify-content:center;
  padding:20px 16px!important;
  border:1px dashed #333740;
  border-radius:14px;
  background:
    linear-gradient(180deg,rgba(255,255,255,.012),transparent 70%),
    #0c0d10;
  color:#8f939e!important;
  font-size:11px;
  line-height:1.55;
  text-align:center;
}

/* Consistent loading/busy surfaces, including future aria-busy usage. */
[aria-busy="true"],
.loading,
.is-loading{
  cursor:progress;
}

[aria-busy="true"]{
  opacity:.78;
}

.v207-save-state{
  min-width:0;
}

.v207-save-copy{
  line-height:1.55;
}

/* Toast is now an aria-live status region. */
.toast{
  max-width:min(390px,calc(100vw - 28px));
  padding:11px 13px;
  border-color:#393d46;
  background:
    linear-gradient(180deg,rgba(255,255,255,.024),transparent 60%),
    #15171c;
  color:#f4f5f7;
  font-size:11px;
  line-height:1.45;
  font-weight:720;
}

/* Cloud state should read like status, not a random button. */
.cloud-chip{
  min-width:86px;
  justify-content:center;
  gap:7px;
}

.cloud-dot{
  box-shadow:0 0 0 3px rgba(255,255,255,.025);
}

.cloud-status-label{
  font-weight:780;
  font-variant-numeric:tabular-nums;
}

/* Modal semantics / close affordance */
.modal[role="dialog"]{
  outline:none;
}

.modal-head>.btn[aria-label="Cerrar"]{
  flex:0 0 auto;
  width:36px;
  min-width:36px;
  height:36px;
  min-height:36px;
  padding:0;
  display:grid;
  place-items:center;
  border-radius:10px;
  color:#c5c8d0;
  font-size:16px;
  line-height:1;
}

.modal-head>.btn[aria-label="Cerrar"]:focus-visible{
  border-color:rgba(255,38,57,.62);
  box-shadow:var(--focus-ring);
}

/* Strong, consistent keyboard focus across interactive elements. */
a:focus-visible,
[role="button"]:focus-visible,
[tabindex]:focus-visible{
  outline:none;
  box-shadow:var(--focus-ring);
}

.student-row:focus-within,
.library-item:focus-within,
.history-item:focus-within,
.track-row:focus-within{
  border-color:#444954;
}

/* Disabled/busy states should remain readable. */
.btn:disabled,
button:disabled,
input:disabled,
select:disabled,
textarea:disabled{
  opacity:.5!important;
  cursor:not-allowed!important;
}

input:disabled,
select:disabled,
textarea:disabled{
  background:#0a0b0e!important;
  color:#777b85!important;
}

/* Status variants */
.inline-note,
.nutrition-note,
.recommend,
.v175-executive{
  overflow-wrap:anywhere;
}

.badge{
  white-space:nowrap;
}

/* Error / warning text surfaces already present in runtime */
.error,
.text-error,
.stat-bad{
  overflow-wrap:anywhere;
}

/* Respect user text scaling and avoid clipped modal actions. */
.modal,
.card,
.hero,
.student-row,
.session-card{
  text-size-adjust:100%;
  -webkit-text-size-adjust:100%;
}

.modal .pill-row,
.v207-save-actions{
  flex-wrap:wrap;
}

@media(max-width:520px){
  .empty{
    min-height:82px;
    padding:17px 13px!important;
  }

  .toast{
    left:14px;
    right:14px;
    width:auto;
    max-width:none;
  }

  .modal-head>.btn[aria-label="Cerrar"]{
    width:38px;
    min-width:38px;
    height:38px;
    min-height:38px;
  }

  .v207-save-actions .btn{
    flex:1 1 140px;
  }
}

@media(prefers-reduced-motion:reduce){
  .toast,
  .modal,
  .modal-wrap{
    transition:none!important;
    animation:none!important;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.33 stylesheet surface changed: "+str(len(styles)))
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

marker='<meta name="fjz-ux-accessibility" content="20.33">'
if re.search(r'<meta\s+name=["\']fjz-ux-accessibility["\']',html,re.I):
    html=re.sub(
        r'<meta\s+name=["\']fjz-ux-accessibility["\']\s+content=["\'][^"\']*["\']\s*/?>',
        marker,html,count=1,flags=re.I
    )
else:
    html=html.replace("</head>",marker+"\n</head>",1)

after=metrics(html)

for key in (
    "styles","render_assignments","start_assignments","finish_assignments",
    "channels","mutation_observers","performance_observers",
    "timeouts","rafs","listeners"
):
    if after[key]!=before[key]:
        raise RuntimeError("V20.33 runtime topology changed for "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-ux-accessibility" content="20.33"',
    'role="status" aria-live="polite" aria-atomic="true"',
    'role="dialog" aria-modal="true" tabindex="-1"',
    'aria-label="Navegación principal"',
    'aria-label="Estado de sincronización"',
    'aria-label="Cerrar" title="Cerrar"',
    "TEAM FJZ · V20.33 UX STATES + ACCESSIBILITY",
    "pendingMarkerPreservedWhenLocalMissing:true",
    'meta name="fjz-routine-builder-ui" content="20.31"'
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.33 missing UX/accessibility marker: "+repr(missing))

if html.count('aria-label="Cerrar"')<close_count:
    raise RuntimeError("V20.33 close button accessibility regression")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.33 UX states + accessibility")
print("V20.33 close buttons labeled:",close_count)
print("V20.33 BEFORE:",before)
print("V20.33 AFTER:",after)
print("V20.33 static semantics/states polished; runtime topology unchanged")
