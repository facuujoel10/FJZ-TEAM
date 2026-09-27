import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v123AlertCenterCleanupStyles">
.v123-alert-toolbar{position:sticky;top:0;z-index:2;background:var(--card);padding:7px 0 9px}
.v123-dashboard-note{margin-bottom:14px}
#v80AttentionFilters,#v80AttentionBody{display:none!important}
</style>
"""

# Improve the V9.6 center wording and keep every relevant category permanently available.
html=html.replace(
  '<h3>Centro de alertas</h3><div class="muted tiny">Lo que requiere tu atención, ordenado por prioridad.</div>',
  '<h3>Centro de seguimiento</h3><div class="muted tiny">Un único lugar para revisar alertas, check-ins, recuperación, entrenamiento, nutrición y cobranzas.</div>'
)

old_filters="""[['all','Todas'],['priority','Prioridad'],['checkin','Check-ins'],['training','Entrenamiento'],['nutrition','Nutrición'],['exercise_feedback','Ejercicios']]"""
new_filters="""[['all','Todas'],['priority','Prioridad'],['checkin','Check-ins'],['wellness','Recuperación'],['exercise_feedback','Ejercicios'],['training','Entrenamiento'],['progression','Progresión'],['nutrition','Nutrición'],['payment','Pagos']]"""
html=html.replace(old_filters,new_filters)

# Make the toolbar visually stable even when a filter is empty.
html=html.replace(
  """'<div class="v96-alert-tools">'+""",
  """'<div class="v96-alert-tools v123-alert-toolbar">'+"""
)

js=r"""
<script id="v123AlertCenterCleanupRuntime">
(function(){
  function removeLegacyAttentionV123(){
    if(currentProfile?.role!=='coach'||coachTab!=='dashboard')return;
    const body=el('v80AttentionBody');
    const card=body?.closest('.card');
    if(card)card.remove();

    // The old side shortcuts manipulated the retired V8 filter.
    document.querySelectorAll('button').forEach(btn=>{
      const oc=btn.getAttribute('onclick')||'';
      if(oc.includes('attentionFilterV80')&&oc.includes('hydrateCoachDashboardV80'))btn.remove();
    });
  }

  function injectDashboardGuideV123(){
    if(currentProfile?.role!=='coach'||coachTab!=='dashboard'||el('v123DashboardGuide'))return;
    const list=el('studentList')?.closest('.card');
    if(!list)return;
    const note=document.createElement('div');
    note.id='v123DashboardGuide';
    note.className='card v123-dashboard-note';
    note.innerHTML='<div class="section-title"><div><h3>Seguimiento de hoy</h3><div class="muted tiny">El Centro de seguimiento de arriba concentra todo lo que requiere una acción. La lista de alumnos queda solo para abrir fichas y ver su estado general.</div></div></div>';
    list.insertAdjacentElement('beforebegin',note);
  }

  // Correct destinations for every current alert type.
  window.openCoachAlertV96=async function(athleteId,key,kind){
    if(key){
      try{await window.readCoachAlertV96(key)}catch(e){}
    }
    if(kind==='payment'){
      coachTab='payments';
      render();
      return;
    }
    const row=[...cloudAthletes.values()].find(x=>x.id===athleteId);
    if(!row){toast('No encuentro esa ficha');return}
    state.selectedStudentId=row.client_id;
    saveState();
    coachTab='student';
    const target={
      exercise_feedback:'routine',
      checkin:'tracking',
      wellness:'tracking',
      training:'summary',
      progression:'progress',
      nutrition:'nutrition'
    };
    coachStudentTab=target[kind]||'summary';
    render();
  };

  // A filter must only change the list, never navigation or controls.
  const baseSetFilter=window.setCoachAlertFilterV96;
  window.setCoachAlertFilterV96=function(v){
    try{
      baseSetFilter(v);
      requestAnimationFrame(()=>{
        const panel=el('v96CoachAlerts');
        if(panel)panel.scrollIntoView({block:'nearest'});
      });
    }catch(e){
      console.warn('V12.3 alert filter',e);
      toast('No se pudo aplicar el filtro');
    }
  };

  const baseRenderV123=window.render;
  window.render=function(){
    const out=baseRenderV123.apply(this,arguments);
    setTimeout(removeLegacyAttentionV123,20);
    setTimeout(injectDashboardGuideV123,120);
    setTimeout(removeLegacyAttentionV123,450);
    return out;
  };

  // Guard against delayed legacy hydration re-adding visual noise.
  const mo=new MutationObserver(()=>{
    if(currentProfile?.role==='coach'&&coachTab==='dashboard'){
      removeLegacyAttentionV123();
      injectDashboardGuideV123();
    }
  });
  mo.observe(document.documentElement,{childList:true,subtree:true});

  window.__fjzAlertsV123={
    version:'12.3',
    canonicalCenter:'v96CoachAlerts',
    legacyAttentionRemoved:true,
    categories:['all','priority','checkin','wellness','exercise_feedback','training','progression','nutrition','payment']
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)
html=re.sub(r"TEAM FJZ V\d+(?:\.\d+)+","TEAM FJZ V12.3",html)

p.write_text(html,encoding="utf-8")
swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8")
sw=re.sub(r"team-fjz-v\d+(?:-\d+)+","team-fjz-v12-3",sw)
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V12.3 alert center consolidation:",len(html),"bytes")
