import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")
html=html.replace("TEAM FJZ V9.6","TEAM FJZ V9.7")

css=r"""
<style id="v97MigrationProfileStyles">
.v97-profile-extra{display:contents}
</style>
"""

js=r"""
<script id="v97MigrationProfileRuntime">
(function(){
  let loadedV97=false,loadingV97=false;

  async function loadAthleteExtrasV97(){
    if(loadedV97||loadingV97||!window.supabaseClient||!window.currentUser)return;
    loadingV97=true;
    try{
      const {data,error}=await supabaseClient.from('athletes').select('id,client_id,start_date,height_cm');
      if(error)throw error;
      for(const row of (data||[])){
        const old=cloudAthletes.get(row.client_id);
        if(old)cloudAthletes.set(row.client_id,{...old,...row});
      }
      loadedV97=true;
    }catch(e){console.warn('athlete extras',e)}
    finally{loadingV97=false}
  }

  function fmtHeightV97(v){
    const n=Number(v);return Number.isFinite(n)?(n/100).toLocaleString('es-AR',{minimumFractionDigits:2,maximumFractionDigits:2})+' m':'—';
  }

  function injectExtrasV97(){
    const a=currentProfile?.role==='student'
      ?[...cloudAthletes.values()][0]
      :cloudAthletes.get(student()?.id);
    if(!a)return;

    const studentGrid=document.querySelector('#v86StudentProfileCard .v86-profile-grid');
    if(studentGrid&&!studentGrid.querySelector('[data-v97-extra]')){
      studentGrid.insertAdjacentHTML('beforeend',
        '<div class="v86-profile-field" data-v97-extra="height"><strong>'+esc(fmtHeightV97(a.height_cm))+'</strong><span>Altura</span></div>'+
        '<div class="v86-profile-field" data-v97-extra="start"><strong>'+(a.start_date?formatTrackingDate(a.start_date):'—')+'</strong><span>Inicio del seguimiento</span></div>');
    }

    const coachGrid=document.querySelector('#v86CoachProfile .v86-profile-grid');
    if(coachGrid&&!coachGrid.querySelector('[data-v97-extra]')){
      coachGrid.insertAdjacentHTML('beforeend',
        '<div class="v86-profile-field" data-v97-extra="height"><strong>'+esc(fmtHeightV97(a.height_cm))+'</strong><span>Altura</span></div>'+
        '<div class="v86-profile-field" data-v97-extra="start"><strong>'+(a.start_date?formatTrackingDate(a.start_date):'—')+'</strong><span>Inicio del seguimiento</span></div>');
    }
  }

  async function runV97(){
    await loadAthleteExtrasV97();
    injectExtrasV97();
  }

  const oldRenderV97=window.render;
  window.render=function(){
    oldRenderV97();
    setTimeout(runV97,100);
    setTimeout(injectExtrasV97,700);
  };
  setTimeout(runV97,250);
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)
p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8").replace("team-fjz-v9-6","team-fjz-v9-7")
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V9.7 perfiles migrados:",len(html),"bytes")
