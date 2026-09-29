import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

old_head = """    const ath=currentAthleteRowV73?.()||cloudAthletes?.get?.(s?.id);
    const pending=typeof pendingFeedbackV73==='function'?pendingFeedbackV73().length:0;
    const days=typeof daysSince==='function'?daysSince(s?.lastWorkout):null;
    const status=statusFor(s);
    const avatar='<div id="v161AvatarSlot">'+
      '<div class="v70-avatar big">'+esc((s?.name||'AL').slice(0,2).toUpperCase())+'</div>'+
    '</div>';
"""
new_head = """    const pending=typeof pendingFeedbackV73==='function'?pendingFeedbackV73().length:0;
    const days=typeof daysSince==='function'?daysSince(s?.lastWorkout):null;
"""
if old_head not in html:
    raise RuntimeError("V16.3 local summary identity block not found")
html=html.replace(old_head,new_head,1)

old_markup = """      '<div class="v161-overview-head">'+
        '<div class="v161-overview-person">'+avatar+
          '<div><h3>'+esc(s?.name||'Alumno')+'</h3>'+
          '<p class="muted tiny">'+esc(s?.goal||'Sin objetivo cargado')+'</p>'+
          '<div class="pill-row" style="margin-top:7px">'+badge(status)+'</div></div>'+
        '</div>'+
        '<div class="muted micro">Resumen 360 · una sola vista</div>'+
      '</div>'+"""
new_markup = """      '<div class="v161-overview-head v163-summary-head">'+
        '<div><h3 style="margin:0">Resumen 360</h3>'+
        '<div class="muted tiny" style="margin-top:3px">Estado, seguimiento y señales útiles para decidir qué revisar.</div></div>'+
        '<span class="badge blue">Vista integral</span>'+
      '</div>'+"""
if old_markup not in html:
    raise RuntimeError("V16.3 old summary header markup not found")
html=html.replace(old_markup,new_markup,1)

old_hydrate = """  async function hydrateAvatarV161(key){
    try{
      const s=student(),ath=currentAthleteRowV73?.()||cloudAthletes?.get?.(s?.id);
      if(!ath?.user_id||typeof avatarHtmlV70!=='function')return;
      const html=await avatarHtmlV70(ath.user_id,s.name,'big');
      if(studentKeyV161()!==key)return;
      const slot=el('v161AvatarSlot');
      if(slot)slot.innerHTML=html;
    }catch(e){}
  }
"""
new_hydrate = """  async function hydrateAvatarV161(){ return; }
"""
if old_hydrate not in html:
    raise RuntimeError("V16.3 avatar hydrator not found")
html=html.replace(old_hydrate,new_hydrate,1)

old_call = """      updateOverviewV161(key);
      hydrateAvatarV161(key);
      return results;"""
new_call = """      updateOverviewV161(key);
      return results;"""
if old_call not in html:
    raise RuntimeError("V16.3 avatar hydrate call not found")
html=html.replace(old_call,new_call,1)

css=r"""
<style id="v163SummaryIdentityCleanupStyles">
.v163-summary-head{
  align-items:center!important;
  margin-bottom:12px!important
}
.v163-summary-head>div:first-child{
  min-width:0
}
.v163-summary-head h3{
  font-size:15px;
  line-height:1.2
}
/* Identity belongs only to the profile header above the tabs. */
#v161CoachOverview .v161-overview-person,
#v161CoachOverview #v161AvatarSlot{
  display:none!important
}
@media(max-width:700px){
  .v163-summary-head{
    display:flex!important;
    align-items:flex-start!important
  }
  .v163-summary-head .badge{
    flex:0 0 auto
  }
}
</style>
"""

js=r"""
<script id="v163SummaryIdentityCleanupRuntime">
(function(){
  const VERSION='16.3';

  function enforceV163(){
    if(!(currentProfile?.role==='coach'&&coachTab==='student'))return;

    // The profile hero is the only identity header: avatar + name + goal.
    const overview=el('v161CoachOverview');
    if(overview){
      overview.querySelector('.v161-overview-person')?.remove();
      overview.querySelector('#v161AvatarSlot')?.remove();

      const head=overview.querySelector('.v161-overview-head');
      if(head&&!head.classList.contains('v163-summary-head')){
        head.classList.add('v163-summary-head');
        head.innerHTML='<div><h3 style="margin:0">Resumen 360</h3>'+
          '<div class="muted tiny" style="margin-top:3px">Estado, seguimiento y señales útiles para decidir qué revisar.</div></div>'+
          '<span class="badge blue">Vista integral</span>';
      }
    }

    // Never allow a second coach-profile avatar below the main hero.
    const hero=el('view')?.querySelector('.hero');
    document.querySelectorAll('#v70CoachStudentAvatar').forEach(node=>{
      if(!hero?.contains(node))node.remove();
    });
  }

  const baseRenderV163=window.render;
  window.render=function(){
    const out=baseRenderV163.apply(this,arguments);
    if(typeof fjzPostRenderV125==='function'){
      fjzPostRenderV125('v163-summary-identity',enforceV163);
    }else{
      queueMicrotask(enforceV163);
    }
    return out;
  };

  window.__fjzSummaryIdentityV163={
    version:VERSION,
    identityOnlyInHero:true,
    summaryAvatarRemoved:true,
    summaryNameRemoved:true,
    duplicateAvatarFetchRemoved:true,
    compactSummaryHeader:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzSummaryIdentityV163",
  "identityOnlyInHero:true",
  "summaryAvatarRemoved:true",
  "summaryNameRemoved:true",
  "duplicateAvatarFetchRemoved:true",
  "compactSummaryHeader:true"
]:
    if marker not in html:
        raise RuntimeError("V16.3 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V16.3 streamlined coach summary identity enabled")
