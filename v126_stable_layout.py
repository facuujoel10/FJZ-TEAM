import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v126StableLayoutStyles">
/* V12.6 · stable layout: no box jumps */
#view,#coachStudentBody,#studentSubBody{min-width:0}
#coachStudentBody,#studentSubBody{width:100%}

.card,.hero,.metric,.student-row,.exercise-row,.option-card,
.v114-profile-field,.v115-profile-item,.v122-event,.v122-kpi{
  box-sizing:border-box;
  min-width:0;
  max-width:100%;
}

.grid,.metric-grid,.form-grid,.v114-profile-grid,.v115-profile-grid,
.v122-grid,.v122-row{
  min-width:0;
}

.grid>*,
.metric-grid>*,
.form-grid>*,
.v114-profile-grid>*,
.v115-profile-grid>*,
.v122-grid>*,
.v122-row>*{
  min-width:0;
}

.grid.two{align-items:start}
.section-title,.hero,.day-head,.option-head,.student-main{
  min-width:0;
}
.section-title>div,.hero>div,.day-head>div,.option-head>div,.student-main>div{
  min-width:0;
}
.section-title h3,.hero h2,.hero p,.card strong,.card span,.card p{
  overflow-wrap:anywhere;
}

.tabs{
  overflow-x:auto;
  overflow-y:hidden;
  scrollbar-width:thin;
  -webkit-overflow-scrolling:touch;
}
.tabs .tab{flex:0 0 auto}

.pill-row,.day-actions,.exercise-actions,.v122-actions{
  flex-wrap:wrap;
}

/* Remove motion that could look like cards shifting/re-rendering. */
#coachStudentBody>.card,
#studentSubBody>.card,
#view>.card{
  animation:none!important;
  transform:none!important;
}

/* Stable top stack inside student profile. */
#coachStudentBody.v126-summary-layout{
  display:flex;
  flex-direction:column;
  gap:14px;
}
#coachStudentBody.v126-summary-layout>.v114-profile-card{order:-30;margin:0}
#coachStudentBody.v126-summary-layout>#cloudInviteCard{order:-20;margin:0}
#coachStudentBody.v126-summary-layout>.grid.kpi{order:-10;margin:0}
#coachStudentBody.v126-summary-layout>.grid.two{order:0;margin:0}

/* Student's own "Mis datos" stays first after hero/tabs. */
#view.v126-student-home #v115StudentProfileCard{margin-top:0!important}

@media(max-width:760px){
  .hero{gap:12px}
  .hero .pill-row{width:100%;justify-content:flex-start}
  .grid.two{grid-template-columns:1fr!important}
  .section-title{gap:10px}
}
@media(max-width:520px){
  .card{padding-left:12px!important;padding-right:12px!important}
  .v114-profile-grid,.v115-profile-grid,.metric-grid{grid-template-columns:1fr!important}
  .btn{max-width:100%}
}
</style>
"""

js=r"""
<script id="v126StableRenderRuntime">
(function(){
  const RELEASE='12.6';

  function ageV126(date){
    if(!date)return null;
    const d=new Date(date+'T12:00:00');
    if(Number.isNaN(d.getTime()))return null;
    const n=new Date();
    let a=n.getFullYear()-d.getFullYear();
    const m=n.getMonth()-d.getMonth();
    if(m<0||(m===0&&n.getDate()<d.getDate()))a--;
    return a>=0&&a<120?a:null;
  }
  function dateV126(v){
    if(!v)return 'Sin cargar';
    const p=String(v).slice(0,10).split('-');
    return p.length===3?p[2]+'/'+p[1]+'/'+p[0]:'Sin cargar';
  }
  function sexV126(v){
    return ({hombre:'Hombre',mujer:'Mujer',otro:'Otro',prefiero_no_decir:'Prefiero no decir'})[v]||'Sin cargar';
  }
  function valV126(v,s=''){
    return v!==null&&v!==undefined&&String(v).trim()!==''?String(v)+s:'Sin cargar';
  }

  function profileHtmlV126(row,s){
    const age=ageV126(row?.birth_date);
    return '<div class="card v114-profile-card" id="v114ProfileCard">'+
      '<div class="section-title"><div><h3>Datos del alumno</h3><div class="muted tiny">Información principal de la ficha.</div></div>'+
      '<button class="btn small" onclick="openEditStudentProfileV114()">Editar perfil</button></div>'+
      '<div class="v114-profile-grid">'+
        '<div class="v114-profile-field"><span>Nombre</span><strong>'+esc(row?.name||s?.name||'Sin cargar')+'</strong></div>'+
        '<div class="v114-profile-field"><span>Edad</span><strong>'+(age!==null?age+' años':'Sin cargar')+'</strong></div>'+
        '<div class="v114-profile-field"><span>Sexo</span><strong>'+esc(sexV126(row?.sex))+'</strong></div>'+
        '<div class="v114-profile-field"><span>Fecha de nacimiento</span><strong>'+esc(dateV126(row?.birth_date))+'</strong></div>'+
        '<div class="v114-profile-field"><span>Altura</span><strong>'+esc(valV126(row?.height_cm,' cm'))+'</strong></div>'+
        '<div class="v114-profile-field"><span>Inicio del plan</span><strong>'+esc(dateV126(row?.start_date))+'</strong></div>'+
        '<div class="v114-profile-field"><span>Ocupación / estudio</span><strong>'+esc(valV126(row?.occupation_study))+'</strong></div>'+
        '<div class="v114-profile-field"><span>Cuenta</span><strong>'+(row?.user_id?'Vinculada':'Sin vincular')+'</strong></div>'+
        '<div class="v114-profile-field v114-goal"><span>Objetivo</span><strong>'+esc(row?.goal||s?.goal||'Sin cargar')+'</strong></div>'+
      '</div></div>';
  }

  function ensureCoachProfileFirstV126(){
    if(currentProfile?.role!=='coach'||coachTab!=='student'||coachStudentTab!=='summary')return;
    const body=el('coachStudentBody');
    const s=student();
    if(!body||!s)return;

    body.classList.add('v126-summary-layout');

    const row=cloudAthletes?.get?.(s.id)||null;
    let profile=el('v114ProfileCard');

    // Render from already-loaded athlete data on the first frame.
    if(!profile){
      const loading=el('v114ProfileLoading');
      if(loading)loading.remove();
      body.insertAdjacentHTML('afterbegin',profileHtmlV126(row,s));
      profile=el('v114ProfileCard');
    }

    // Enforce canonical order even if older injectors add cards later.
    if(profile&&body.firstElementChild!==profile){
      body.insertBefore(profile,body.firstElementChild);
    }

    const invite=el('cloudInviteCard');
    if(invite&&profile&&profile.nextElementSibling!==invite){
      body.insertBefore(invite,profile.nextSibling);
    }

    // Remove accidental duplicate cards by id/content.
    const profiles=[...body.querySelectorAll('#v114ProfileCard,.v114-profile-card')];
    profiles.forEach((x,i)=>{if(i>0)x.remove()});
    document.querySelectorAll('#v114ProfileLoading').forEach(x=>x.remove());
  }

  function ensureStudentOwnDataFirstV126(){
    if(currentProfile?.role!=='student'||mode!=='student'||studentTab!=='home')return;
    const view=el('view');
    const card=el('v115StudentProfileCard');
    if(!view)return;
    view.classList.add('v126-student-home');
    if(!card)return;

    // Put personal data before KPI/agenda/content, immediately after hero/tabs.
    const tabs=el('studentMainTabs');
    const hero=view.querySelector('.hero');
    const anchor=tabs||hero;
    if(anchor&&anchor.nextElementSibling!==card){
      anchor.insertAdjacentElement('afterend',card);
    }
  }

  function normalizeBoxesV126(){
    const root=el('view');
    if(!root)return;
    root.querySelectorAll('.grid,.metric-grid,.form-grid').forEach(g=>{
      g.style.minWidth='0';
    });
    root.querySelectorAll('.card,.metric,.student-row,.exercise-row').forEach(box=>{
      box.style.minWidth='0';
      box.style.boxSizing='border-box';
    });
  }

  function postLayoutV126(){
    ensureCoachProfileFirstV126();
    ensureStudentOwnDataFirstV126();
    normalizeBoxesV126();
  }

  // Make profile first during the actual student-profile render, not hundreds of ms later.
  const baseCoachStudentV126=renderCoachStudent;
  renderCoachStudent=function(){
    const out=baseCoachStudentV126.apply(this,arguments);
    ensureCoachProfileFirstV126();
    fjzPostRenderV125('layout-v126',postLayoutV126);
    return out;
  };

  // cloudInviteCard is inserted by this function; re-assert order immediately afterward.
  if(typeof renderCloudExtras==='function'){
    const baseCloudExtrasV126=renderCloudExtras;
    renderCloudExtras=function(){
      const out=baseCloudExtrasV126.apply(this,arguments);
      ensureCoachProfileFirstV126();
      return out;
    };
  }

  // Student side: place "Mis datos" first as soon as it exists.
  const baseRenderV126=render;
  render=function(){
    const out=baseRenderV126.apply(this,arguments);
    fjzPostRenderV125('layout-v126',postLayoutV126);
    return out;
  };

  // One lightweight observer only while a student summary/home is visible.
  let queued=false;
  const observer=new MutationObserver(()=>{
    const relevant=
      (currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary')||
      (currentProfile?.role==='student'&&studentTab==='home');
    if(!relevant||queued)return;
    queued=true;
    requestAnimationFrame(()=>{
      queued=false;
      postLayoutV126();
    });
  });
  const view=el('view');
  if(view)observer.observe(view,{childList:true,subtree:false});

  window.__fjzRenderV126={
    version:RELEASE,
    stableBoxes:true,
    profileFirst:true,
    studentDataFirst:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

html=re.sub(r"TEAM FJZ V\d+(?:\.\d+)+","TEAM FJZ V12.6",html)
html=re.sub(r'(<meta\s+name=["\']fjz-release["\']\s+content=["\'])[^"\']*(["\'])',r'\g<1>12.6\g<2>',html,flags=re.I)

p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8")
sw=re.sub(r"team-fjz-v\d+(?:-\d+)+","team-fjz-v12-6",sw)
swp.write_text(sw,encoding="utf-8")

print("TEAM FJZ V12.6 stable layout/profile first:",len(html),"bytes")
