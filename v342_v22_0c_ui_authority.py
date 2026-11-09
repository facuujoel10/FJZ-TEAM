import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "intervals":len(re.findall(r"setInterval\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

def edit_script(doc,script_id,transform):
    mid=-1
    for marker in ('id="'+script_id+'"',"id='"+script_id+"'"):
        mid=doc.find(marker)
        if mid>=0: break
    if mid<0:
        raise RuntimeError("V22 0C missing script "+script_id)
    a=doc.find(">",mid); b=doc.find("</script>",a)
    if a<0 or b<0:
        raise RuntimeError("V22 0C malformed script "+script_id)
    old=doc[a+1:b]
    new=transform(old)
    if new==old:
        raise RuntimeError("V22 0C no changes in "+script_id)
    return doc[:a+1]+new+doc[b:]

before=metrics(html)

for marker in [
    'meta name="fjz-mobile-workout-stability" content="21.41"',
    'meta name="fjz-coach-dashboard" content="20.25"',
    "function renderCoachDashboardV80()",
    "trainingCommentsGlobalRendererV325:true",
    "trainingCommentsAfterHydrationV325:true",
    "trainingCommentsHostIndependentV325:true",
    "reviewCenterRepaintsTrainingCommentsV339:true",
]:
    if marker not in html:
        raise RuntimeError("V22 0C final UI prerequisite missing "+marker)

start=html.find("function renderCoachDashboardV80()")
end=html.find("const _renderCoachV80Base",start)
if start<0 or end<0 or end<=start:
    raise RuntimeError("V22 0C dashboard function bounds missing")
block=html[start:end]

hero=re.compile(r'(<div class="v225-hero-actions">)(.*?)(</div>)',re.S)
m=hero.search(block)
if not m:
    raise RuntimeError("V22 0C dashboard hero actions missing")
actions=m.group(2)

# Final dashboard authority: exactly one visible Agenda route and no retired Music route.
actions=re.sub(r"""\s*<button[^>]*onclick="coachTab='agenda';render\(\)"[^>]*>\s*Agenda\s*</button>""","",actions)
actions=re.sub(r"""\s*<button[^>]*onclick="coachTab='music';render\(\)"[^>]*>\s*Música\s*</button>""","",actions)
agenda="""\n      <button class="btn v342-coach-agenda" onclick="coachTab='agenda';render()">Agenda</button>"""
status='<button class="btn ghost" onclick="showSystemStatusV80()">Estado</button>'
if status in actions:
    actions=actions.replace(status,status+agenda,1)
else:
    actions=agenda+actions
new_hero=m.group(1)+actions+m.group(3)
block=block[:m.start()]+new_hero+block[m.end():]

if 'id="v325TrainingCommentsCenter"' not in block:
    grid_anchor='  <div class="grid v225-dashboard-grid">'
    if block.count(grid_anchor)!=1:
        raise RuntimeError("V22 0C dashboard comments host anchor mismatch: "+str(block.count(grid_anchor)))
    comments_host='  <section class="card v325-training-comments-center" id="v325TrainingCommentsCenter"><div class="empty">Cargando comentarios…</div></section>\n\n'+grid_anchor
    block=block.replace(grid_anchor,comments_host,1)

html=html[:start]+block+html[end:]

# Runtime guarantee: later dashboard wrappers may rebuild the DOM after the
# canonical source rendered. Reuse V324's existing hydration repaint instead
# of adding timers/listeners/observers or another render wrapper.
def patch_v324(body):
    old="""  function repaintReviewsV324(){
    try{window.renderCoachPriorityCenterV252?.()}catch(_e){}
    try{window.renderCoachFocusV235?.()}catch(_e){}
    try{window.__fjzRenderTrainingCommentsV325?.()}catch(_e){}
  }"""
    new="""  function ensureCoachAgendaV342(){
    if(!(mode==='coach'&&coachTab==='dashboard'))return null;
    if(Number(window.innerWidth||0)<901)return null;
    const view=el('view');if(!view)return null;
    let button=view.querySelector('.v342-coach-agenda');
    if(button)return button;
    let actions=view.querySelector('.v225-hero-actions,.v170-coach-actions,.hero .pill-row');
    if(!actions){
      const hero=view.querySelector('.hero');if(!hero)return null;
      actions=document.createElement('div');
      actions.className='v225-hero-actions v342-runtime-actions';
      hero.appendChild(actions);
    }
    button=document.createElement('button');
    button.type='button';
    button.className='btn v342-coach-agenda';
    button.textContent='Agenda';
    button.setAttribute('onclick',"coachTab='agenda';render()");
    actions.appendChild(button);
    return button;
  }
  window.__fjzEnsureCoachAgendaV342=ensureCoachAgendaV342;

  function repaintReviewsV324(){
    try{window.renderCoachPriorityCenterV252?.()}catch(_e){}
    try{window.renderCoachFocusV235?.()}catch(_e){}
    try{window.__fjzRenderTrainingCommentsV325?.()}catch(_e){}
    try{ensureCoachAgendaV342()}catch(_e){}
  }"""
    if body.count(old)!=1:
        raise RuntimeError("V22 0C V324 runtime dashboard anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)
    marker="""    trainingCommentsAfterHydrationV325:true,"""
    if body.count(marker)!=1:
        raise RuntimeError("V22 0C V324 marker anchor mismatch: "+str(body.count(marker)))
    body=body.replace(marker,marker+"""\n    desktopAgendaRuntimeAuthorityV342:true,""",1)
    return body

html=edit_script(html,"v324ReviewDashboardHydrationRuntime",patch_v324)

# Guarantee the Coach fallback after every coalesced post-render batch. This
# reuses the existing V125 RAF scheduler: no new timer, listener, observer or
# render wrapper is introduced.
def patch_v125(body):
    old="""      for(const task of batch){
        try{task()}catch(e){console.warn('TEAM FJZ post-render',e)}
      }
    });"""
    new="""      for(const task of batch){
        try{task()}catch(e){console.warn('TEAM FJZ post-render',e)}
      }
      try{
        if(typeof mode!=='undefined'&&mode==='coach'&&typeof coachTab!=='undefined'&&coachTab==='dashboard'){
          const commentsHost=document.getElementById('v325TrainingCommentsCenter');
          if(!commentsHost||!commentsHost.querySelector('h3'))window.__fjzRenderTrainingCommentsV325?.();
          if(Number(window.innerWidth||0)>=901&&!document.querySelector('.v342-coach-agenda'))window.__fjzEnsureCoachAgendaV342?.();
        }
      }catch(e){console.warn('TEAM FJZ V22 final Coach post-render',e)}
      /* v342FinalCoachPostRender:true */
    });"""
    if body.count(old)!=1:
        raise RuntimeError("V22 0C V125 post-render batch anchor mismatch: "+str(body.count(old)))
    return body.replace(old,new,1)

html=edit_script(html,"v125RenderSchedulerHead",patch_v125)

# The certified browser diagnostics proved the visible Coach dashboard is still
# rendered by V170. Finalize that active authority directly instead of relying
# on V80 hydration hooks that are not part of this dashboard path.
v170_start=html.find("function renderCoachDashboardV170(){")
v170_end=html.find("\n  const baseRenderCoachV170=window.renderCoach;",v170_start)
if v170_start<0 or v170_end<0 or v170_end<=v170_start:
    raise RuntimeError("V22 0C active V170 dashboard bounds missing")
v170_block=html[v170_start:v170_end]

v170_actions_anchor="""      '<div class="v170-coach-actions"><button class="btn" onclick="showTemplates()">Plantillas</button>'+"""
v170_actions_repl="""      '<div class="v170-coach-actions"><button class="btn" onclick="showTemplates()">Plantillas</button>'+
      '<button class="btn v342-coach-agenda" onclick="coachTab=\\'agenda\\';render()">Agenda</button>'+"""
if v170_block.count(v170_actions_anchor)!=1:
    raise RuntimeError("V22 0C active V170 actions anchor mismatch: "+str(v170_block.count(v170_actions_anchor)))
v170_block=v170_block.replace(v170_actions_anchor,v170_actions_repl,1)

v170_dashboard_anchor="""      '<div class="v170-dashboard"><div id="v96CoachAlerts" class="card v170-alert-card">'+"""
v170_dashboard_repl="""      '<section class="card v325-training-comments-center" id="v325TrainingCommentsCenter"><div class="empty">Cargando comentarios…</div></section>'+
      '<div class="v170-dashboard"><div id="v96CoachAlerts" class="card v170-alert-card">'+"""
if v170_block.count(v170_dashboard_anchor)!=1:
    raise RuntimeError("V22 0C active V170 comments host anchor mismatch: "+str(v170_block.count(v170_dashboard_anchor)))
v170_block=v170_block.replace(v170_dashboard_anchor,v170_dashboard_repl,1)

v170_anchor="""    loadCoachFeed(false).then(decorateCoachFeedV170).catch(()=>{if(el('v170AlertTotal'))el('v170AlertTotal').textContent='—'});
  }"""
v170_repl="""    loadCoachFeed(false).then(decorateCoachFeedV170).catch(()=>{if(el('v170AlertTotal'))el('v170AlertTotal').textContent='—'});
    try{window.__fjzRenderTrainingCommentsV325?.()}catch(_e){}
    try{window.__fjzEnsureCoachAgendaV342?.()}catch(_e){}
  }"""
if v170_block.count(v170_anchor)!=1:
    raise RuntimeError("V22 0C active V170 finalize anchor mismatch: "+str(v170_block.count(v170_anchor)))
v170_block=v170_block.replace(v170_anchor,v170_repl,1)
v170_block=v170_block.replace("function renderCoachDashboardV170(){","function renderCoachDashboardV170(){\n    /* v170DashboardStaticAuthorityV342:true */",1)
html=html[:v170_start]+v170_block+html[v170_end:]

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V22 0C expected one stylesheet")
css=r"""
/* TEAM FJZ V22 · ETAPA 0C FINAL DESKTOP AGENDA AUTHORITY */
@media(min-width:901px){
  .v225-coach-hero .v225-hero-actions{
    display:flex!important;
    visibility:visible!important;
    opacity:1!important;
  }
  .v225-coach-hero .v225-hero-actions .v342-coach-agenda,
  #view .v342-coach-agenda{
    display:inline-flex!important;
    visibility:visible!important;
    opacity:1!important;
    pointer-events:auto!important;
  }
  #view .v342-runtime-actions{
    display:flex!important;
    visibility:visible!important;
    opacity:1!important;
    gap:8px;
    flex-wrap:wrap;
  }
}
"""
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]
html=html.replace("</head>",'<meta name="fjz-v22-0c-final-ui-authority" content="0C.10">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V22 0C runtime topology changed "+key+": "+repr({"before":before,"after":after}))

final_start=html.find("function renderCoachDashboardV80()")
final_end=html.find("const _renderCoachV80Base",final_start)
final_block=html[final_start:final_end]
if final_block.count("v342-coach-agenda")!=1:
    raise RuntimeError("V22 0C Agenda authority count mismatch: "+str(final_block.count("v342-coach-agenda")))
if "coachTab='music';render()" in final_block or ">Música</button>" in final_block:
    raise RuntimeError("V22 0C retired dashboard Music route survived")

active_v170_start=html.find("function renderCoachDashboardV170(){")
active_v170_end=html.find("\n  const baseRenderCoachV170=window.renderCoach;",active_v170_start)
active_v170_block=html[active_v170_start:active_v170_end]
for marker in [
    "window.__fjzRenderTrainingCommentsV325?.()",
    "window.__fjzEnsureCoachAgendaV342?.()",
    "v170DashboardStaticAuthorityV342:true",
    "v342-coach-agenda",
    "v325TrainingCommentsCenter",
    ".v170-coach-actions",
]:
    if marker not in active_v170_block and marker!=".v170-coach-actions":
        raise RuntimeError("V22 0C active V170 authority missing "+marker)
if ".v170-coach-actions" not in html:
    raise RuntimeError("V22 0C active V170 action row missing")

for marker in [
    'meta name="fjz-v22-0c-final-ui-authority" content="0C.10"',
    'class="btn v342-coach-agenda"',
    "reviewCenterRepaintsTrainingCommentsV339:true",
    "trainingCommentsAfterHydrationV325:true",
    "trainingCommentsHostIndependentV325:true",
    "desktopAgendaRuntimeAuthorityV342:true",
    "trainingCommentsUsesModeAuthorityV325:true",
    "v342FinalCoachPostRender:true",
    "v170DashboardStaticAuthorityV342:true",
    "__fjzEnsureCoachAgendaV342",
]:
    if marker not in html:
        raise RuntimeError("V22 0C final UI marker missing "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V22 ETAPA 0C final UI authority")
print("V22 0C BEFORE:",before)
print("V22 0C AFTER:",after)
print("V22 0C desktop Agenda + training comments repaint: OK")
