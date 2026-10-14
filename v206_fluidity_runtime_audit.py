import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "bytes":len(doc.encode("utf-8")),
        "scripts":len(re.findall(r"<script\b",doc,re.I)),
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "render_assignments":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "scroll_calls":len(re.findall(r"(?:scrollTo|scrollIntoView)\s*\(",doc)),
        "channel_defs":len(re.findall(r"\.channel\s*\(",doc)),
    }

before=metrics(html)

# Mobile virtual keyboard changes viewport height and fires resize. The old
# listener recalculated tracking geometry even when width did not change,
# creating unnecessary layout work/visual jumps while typing.
resize_pat=re.compile(
r"""  let resizeRafV185=0;
  window\.addEventListener\('resize',\(\)=>\{
    if\(!isStudentTrackingV185\(\)\)return;
    cancelAnimationFrame\(resizeRafV185\);
    resizeRafV185=requestAnimationFrame\(exactTrackingGeometryV185\);
  \},\{passive:true\}\);"""
)
resize_repl="""  let resizeRafV185=0;
  let lastGeometryWidthV206=window.innerWidth||document.documentElement.clientWidth||0;
  window.addEventListener('resize',()=>{
    if(!isStudentTrackingV185())return;
    const width=window.innerWidth||document.documentElement.clientWidth||0;
    if(Math.abs(width-lastGeometryWidthV206)<3)return;
    lastGeometryWidthV206=width;
    cancelAnimationFrame(resizeRafV185);
    resizeRafV185=requestAnimationFrame(exactTrackingGeometryV185);
  },{passive:true});"""
html,n_resize=resize_pat.subn(resize_repl,html,count=1)
if n_resize!=1:
    raise RuntimeError(f"V20.6 resize geometry replacement mismatch: {n_resize}")

css=r"""
<style id="v206FluidityAuditStyles">
/* Avoid continuous repaints from decorative attention pulses. */
.v73-alert-badge.pulse{
  animation:none!important;
}

/* No smooth scrolling/layout animation on the primary app surfaces.
   Navigation and reorders should settle in the same frame. */
html,body,#view,#coachStudentBody,#studentSubBody{
  scroll-behavior:auto!important;
}

/* Keep paint/layout changes inside cards from visually bleeding into
   neighboring sections during async updates. */
.session-card,
.v205-chart,
.photo-month,
.track-row{
  min-width:0!important;
  transform:translateZ(0);
  backface-visibility:hidden;
}
@media (prefers-reduced-motion: reduce){
  *,*::before,*::after{
    scroll-behavior:auto!important;
    animation-duration:.001ms!important;
    animation-iteration-count:1!important;
  }
}
</style>
"""

js=r"""
<script id="v206FluidityAuditRuntime">
(function(){
  const VERSION='20.6';

  window.__fjzPerformanceHealthV206=function(){
    let channels=[];
    try{
      channels=(supabaseClient?.getChannels?.()||[]).map(c=>({
        topic:c.topic||'channel',
        state:c.state||null
      }));
    }catch(_e){}

    return {
      version:VERSION,
      route:{
        role:currentProfile?.role||null,
        coachTab:typeof coachTab!=='undefined'?coachTab:null,
        coachStudentTab:typeof coachStudentTab!=='undefined'?coachStudentTab:null,
        studentTab:typeof studentTab!=='undefined'?studentTab:null
      },
      interaction:{
        modalOpen:!!document.querySelector('#modalWrap[style*="display: flex"],#modalWrap[style*="display:flex"]'),
        workoutActive:typeof studentTab!=='undefined'&&studentTab==='workout',
        routineSaving:!!window.__fjzRoutineSavingV200
      },
      realtime:{
        channelCount:channels.length,
        channels
      },
      viewport:{
        width:window.innerWidth,
        height:window.innerHeight,
        scrollY:window.scrollY
      }
    };
  };

  window.__fjzV206={
    version:VERSION,
    widthOnlyTrackingResize:true,
    keyboardHeightResizeIgnored:true,
    infiniteAlertPulseRemoved:true,
    noSmoothPrimaryScroll:true,
    finalRuntimeAudit:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

# Consolidate style blocks again so the browser evaluates one CSS authority.
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
mergeable=[]
for m in styles:
    attrs=m.group("attrs") or ""
    if re.search(r"\b(media|nonce)\s*=",attrs,re.I):continue
    mergeable.append(m)
if len(mergeable)>1:
    chunks=[]
    for m in mergeable:
        ident=re.search(r'id=["\']([^"\']+)["\']',m.group("attrs") or "",re.I)
        name=ident.group(1) if ident else "anonymous"
        chunks.append("\n/* --- "+name+" --- */\n"+m.group("body").strip())
    for m in reversed(mergeable):
        html=html[:m.start()]+html[m.end():]
    html=html.replace("</head>",'<style id="fjzProductionStylesV206">'+''.join(chunks)+'\n</style>\n</head>',1)

after=metrics(html)

critical=[
  "__fjzPerformanceHealthV206",
  "widthOnlyTrackingResize:true",
  "keyboardHeightResizeIgnored:true",
  "infiniteAlertPulseRemoved:true",
  "noSmoothPrimaryScroll:true",
  "__fjzV205",
  "__fjzRuntimeHealthV192",
  "__fjzInteractionHealthV193"
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.6 missing critical markers: "+repr(missing))

# Regression caps. These intentionally leave some headroom while preventing
# old observer/render chains from silently returning.
if after["styles"]!=1:
    raise RuntimeError("V20.6 expected one final stylesheet")
if after["performance_observers"]!=0:
    raise RuntimeError("V20.6 PerformanceObserver regression")
if after["mutation_observers"]>3:
    raise RuntimeError("V20.6 too many MutationObservers: "+str(after["mutation_observers"]))
if after["render_assignments"]>28:
    raise RuntimeError("V20.6 render wrapper regression: "+str(after["render_assignments"]))
if after["timeouts"]>68:
    raise RuntimeError("V20.6 timeout regression: "+str(after["timeouts"]))
if after["rafs"]>26:
    raise RuntimeError("V20.6 RAF regression: "+str(after["rafs"]))
if after["listeners"]>54:
    raise RuntimeError("V20.6 listener regression: "+str(after["listeners"]))
if after["channel_defs"]>10:
    raise RuntimeError("V20.6 realtime channel regression: "+str(after["channel_defs"]))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.6 FLUIDITY AUDIT BEFORE:",before)
print("TEAM FJZ V20.6 FLUIDITY AUDIT AFTER:",after)
print("TEAM FJZ V20.6 keyboard-resize + repaint stabilization enabled")
