import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

def edit_script(doc,script_id,transform):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.71 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.71 no script change "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)


for marker in [
    'meta name="fjz-mobile-edge-avatar-resilience" content="20.70"',
    "avatarCachedPathFallbackV270:true",
    "__fjzRenderBusyV178",
    "__fjzRunRenderV158",
    "v178-final-pass",
]:
    if marker not in html:
        raise RuntimeError("V20.71 missing prerequisite: "+marker)

def patch_v178(body):
    old="""        out=window.__fjzRunRenderV158
          ?window.__fjzRunRenderV158(baseRenderV178,this,arguments)
          :baseRenderV178.apply(this,arguments);
"""
    new=old+"""        window.__fjzEnsureCoachPreviewV271?.();
"""
    if body.count(old)!=1:
        raise RuntimeError("V20.71 consolidated render hook mismatch: "+str(body.count(old)))
    return body.replace(old,new,1)

html=edit_script(html,"v177MobileStabilityMeasurementRuntime",patch_v178)

def patch_v268(body):
    anchor="""  window.__fjzApplyProfileUiV268=function(){
"""
    if body.count(anchor)!=1:
        raise RuntimeError("V20.71 profile helper anchor mismatch")

    helper=r"""
  function coachPreviewActiveV271(){
    return currentProfile?.role==='coach'&&mode==='student';
  }

  window.__fjzEnsureCoachPreviewV271=function(){
    const root=el('view');
    if(!root)return;

    const active=coachPreviewActiveV271();
    document.body.classList.toggle('v271-coach-preview-active',!!active);
    root.querySelectorAll('.v271-coach-preview').forEach(x=>x.remove());
    if(!active)return;

    const s=student?.();
    const bar=document.createElement('section');
    bar.id='v271CoachPreview';
    bar.className='v271-coach-preview';
    bar.innerHTML=
      '<div class="v271-preview-copy"><span>VISTA PREVIA DEL ALUMNO</span>'+
      '<strong>Estás viendo la app como '+esc(s?.name||'alumno')+'</strong>'+
      '<small>Seguís conectado como Coach. Los datos y acciones corresponden al alumno seleccionado.</small></div>'+
      '<button type="button" class="btn primary v271-preview-exit" onclick="exitCoachStudentPreviewV271()">Volver al panel Coach</button>';
    root.prepend(bar);
  };

  window.exitCoachStudentPreviewV271=function(){
    if(currentProfile?.role!=='coach')return;
    mode='coach';
    coachTab='student';
    coachStudentTab='summary';
    studentTab='home';
    render();
  };

"""
    body=body.replace(anchor,helper+anchor,1)

    marker="""    avatarEmptyStateExplicitV270:true,
    stagingAvatarClearlyDemo:true,
"""
    repl="""    avatarEmptyStateExplicitV270:true,
    coachStudentPreviewContextV271:true,
    coachStudentPreviewOneTapExitV271:true,
    coachStudentPreviewSynchronousV271:true,
    stagingAvatarClearlyDemo:true,
"""
    if body.count(marker)!=1:
        raise RuntimeError("V20.71 V20.68 marker mismatch")
    return body.replace(marker,repl,1)

html=edit_script(html,"v268CoachCockpitAvatarRuntime",patch_v268)

css=r"""
/* =========================================================
   TEAM FJZ · V20.71 COACH -> STUDENT PREVIEW CONTEXT
   Synchronous context strip; no timer/listener/render wrapper.
   ========================================================= */
.v271-coach-preview{
  width:100%;
  max-width:100%;
  box-sizing:border-box;
  display:grid;
  grid-template-columns:minmax(0,1fr) auto;
  gap:12px;
  align-items:center;
  margin:0 0 12px;
  padding:12px 14px;
  border:1px solid rgba(255,62,79,.34);
  border-radius:14px;
  background:
    linear-gradient(135deg,rgba(255,42,61,.10),rgba(255,42,61,.025) 58%),
    #101116;
  box-shadow:0 8px 24px rgba(0,0,0,.12);
}
.v271-preview-copy{min-width:0}
.v271-preview-copy>span{
  display:block;
  color:#ff6b79;
  font-size:7px;
  font-weight:950;
  letter-spacing:.14em;
}
.v271-preview-copy>strong{
  display:block;
  margin-top:4px;
  color:#f5f6f8;
  font-size:13px;
  line-height:1.25;
  font-weight:920;
  overflow-wrap:anywhere;
}
.v271-preview-copy>small{
  display:block;
  margin-top:4px;
  color:#9096a1;
  font-size:8px;
  line-height:1.45;
}
.v271-preview-exit{
  min-width:170px;
  white-space:normal!important;
  text-align:center;
}
@media(max-width:560px){
  .v271-coach-preview{
    grid-template-columns:minmax(0,1fr);
    gap:9px;
    padding:11px;
    border-radius:12px;
  }
  .v271-preview-exit{
    width:100%!important;
    min-width:0!important;
  }
}
@media(max-width:390px){
  .v271-coach-preview{padding:10px;margin-bottom:10px}
  .v271-preview-copy>strong{font-size:12px}
}
"""

if metrics(html)["styles"]!=1:
    raise RuntimeError("V20.71 stylesheet mismatch before insert")
style_end=html.lower().find("</style>")
if style_end<0:
    raise RuntimeError("V20.71 style close missing")
html=html[:style_end]+css+"\n"+html[style_end:]

html=html.replace("</head>",'<meta name="fjz-coach-student-preview-context" content="20.71">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.71 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-coach-student-preview-context" content="20.71"',
    "coachStudentPreviewSynchronousV271:true",
    "coachStudentPreviewContextV271:true",
    "coachStudentPreviewOneTapExitV271:true",
    "__fjzEnsureCoachPreviewV271",
    "exitCoachStudentPreviewV271",
    "VISTA PREVIA DEL ALUMNO",
]:
    if marker not in html:
        raise RuntimeError("V20.71 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.71 coach/student preview context")
print("V20.71 BEFORE:",before)
print("V20.71 AFTER:",after)
print("V20.71 coach preview strip + one-tap return added synchronously with zero topology growth")
