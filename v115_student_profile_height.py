import pathlib, re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v115StudentProfileFieldsStyles">
.v115-student-profile{margin-top:14px}
.v115-profile-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px;margin-top:12px}
.v115-profile-item{border:1px solid var(--border);background:rgba(255,255,255,.025);border-radius:12px;padding:10px;min-width:0}
.v115-profile-item span{display:block;font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px}
.v115-profile-item strong{display:block;font-size:12px;line-height:1.35}
.v115-form{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.v115-form .span2{grid-column:1/-1}
@media(max-width:760px){.v115-profile-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:520px){.v115-profile-grid,.v115-form{grid-template-columns:1fr}.v115-form .span2{grid-column:auto}}
</style>
"""

js=r"""
<script id="v115StudentProfileFieldsRuntime">
(function(){
  let myAthleteV115=null;

  function ageV115(date){
    if(!date)return null;
    const d=new Date(date+'T12:00:00');
    if(Number.isNaN(d.getTime()))return null;
    const n=new Date();
    let age=n.getFullYear()-d.getFullYear();
    const m=n.getMonth()-d.getMonth();
    if(m<0||(m===0&&n.getDate()<d.getDate()))age--;
    return age>=0&&age<120?age:null;
  }
  function sexLabelV115(v){
    return ({hombre:'Hombre',mujer:'Mujer',otro:'Otro',prefiero_no_decir:'Prefiero no decir'})[v]||'Sin cargar';
  }
  async function loadMyAthleteV115(force=false){
    if(currentProfile?.role!=='student'||!currentUser||!supabaseClient)return null;
    if(myAthleteV115&&!force)return myAthleteV115;
    const {data,error}=await supabaseClient.from('athletes')
      .select('id,name,goal,sex,birth_date,occupation_study,height_cm,start_date,user_id')
      .eq('user_id',currentUser.id).maybeSingle();
    if(error)throw error;
    myAthleteV115=data||null;
    return myAthleteV115;
  }
  function itemV115(label,value){
    return '<div class="v115-profile-item"><span>'+esc(label)+'</span><strong>'+esc(value||'Sin cargar')+'</strong></div>';
  }
  async function injectMyProfileV115(){
    if(currentProfile?.role!=='student'||mode!=='student'||studentTab!=='home')return;
    const view=el('view');
    if(!view||el('v115StudentProfileCard'))return;
    let r;
    try{r=await loadMyAthleteV115(false)}catch(e){console.warn('V11.5 profile load',e);return}
    if(!r)return;
    const age=ageV115(r.birth_date);
    const card=document.createElement('div');
    card.id='v115StudentProfileCard';
    card.className='card v115-student-profile';
    card.innerHTML=
      '<div class="section-title"><div><h3>Mis datos</h3><div class="muted tiny">Podés mantener actualizados tus datos básicos.</div></div><button class="btn small" onclick="openMyProfileV115()">Editar datos</button></div>'+
      '<div class="v115-profile-grid">'+
        itemV115('Sexo',sexLabelV115(r.sex))+
        itemV115('Edad',age!==null?age+' años':'Sin cargar')+
        itemV115('Altura',r.height_cm!=null?Number(r.height_cm).toFixed(Number(r.height_cm)%1?1:0)+' cm':'Sin cargar')+
        itemV115('Ocupación / estudio',r.occupation_study||'Sin cargar')+
      '</div>';
    const grids=view.querySelector('.grid.kpi');
    if(grids&&grids.parentNode)grids.parentNode.insertBefore(card,grids.nextSibling);
    else view.appendChild(card);
  }

  window.openMyProfileV115=async function(){
    let r;
    try{r=await loadMyAthleteV115(true)}catch(e){toast(cloudErr(e));return}
    if(!r){toast('No encuentro tu ficha');return}
    showModal(
      '<div class="modal-head"><div><h3>Editar mis datos</h3><div class="muted tiny">'+esc(r.name||student().name)+'</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="v115-form">'+
        '<label class="tiny muted">Sexo<select id="v115Sex" class="input">'+
          '<option value="">Sin especificar</option>'+
          '<option value="hombre" '+(r.sex==='hombre'?'selected':'')+'>Hombre</option>'+
          '<option value="mujer" '+(r.sex==='mujer'?'selected':'')+'>Mujer</option>'+
          '<option value="otro" '+(r.sex==='otro'?'selected':'')+'>Otro</option>'+
          '<option value="prefiero_no_decir" '+(r.sex==='prefiero_no_decir'?'selected':'')+'>Prefiero no decir</option>'+
        '</select></label>'+
        '<label class="tiny muted">Fecha de nacimiento<input id="v115Birth" class="input" type="date" value="'+esc(r.birth_date||'')+'"></label>'+
        '<label class="tiny muted">Altura (cm)<input id="v115Height" class="input" type="number" min="100" max="250" step="0.1" value="'+esc(r.height_cm??'')+'" placeholder="Ej: 174"></label>'+
        '<label class="tiny muted">Ocupación / estudio<input id="v115Occupation" class="input" maxlength="160" value="'+esc(r.occupation_study||'')+'" placeholder="Ej: Estudio / trabajo"></label>'+
      '</div>'+
      '<div class="muted tiny" style="margin-top:12px">Estos cambios actualizan tu ficha y también los verá tu coach.</div>'+
      '<button class="btn primary" style="width:100%;margin-top:14px" onclick="saveMyProfileV115()">Guardar cambios</button>'
    );
  };

  window.saveMyProfileV115=async function(){
    if(currentProfile?.role!=='student'||!supabaseClient){toast('Requiere cuenta de alumno conectada');return}
    const birth=el('v115Birth')?.value||null;
    const hRaw=el('v115Height')?.value;
    const height=hRaw===''||hRaw==null?null:Number(hRaw);
    if(height!==null&&(!Number.isFinite(height)||height<100||height>250)){toast('Revisá la altura');return}
    const {data,error}=await supabaseClient.rpc('update_my_athlete_profile_v2',{
      p_sex:el('v115Sex')?.value||null,
      p_birth_date:birth,
      p_occupation_study:(el('v115Occupation')?.value||'').trim()||null,
      p_height_cm:height
    });
    if(error){toast(cloudErr(error));return}
    myAthleteV115=data||null;
    closeModal();
    render();
    toast('Datos actualizados');
  };

  const baseRenderV115=window.render;
  window.render=function(){
    const out=baseRenderV115.apply(this,arguments);
    if(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'){
      setTimeout(injectMyProfileV115,80);
    }
    return out;
  };

  const baseRefreshV115=window.refreshCloudFromRealtime;
  if(typeof baseRefreshV115==='function'){
    window.refreshCloudFromRealtime=async function(){
      const out=await baseRefreshV115.apply(this,arguments);
      if(currentProfile?.role==='student')myAthleteV115=null;
      return out;
    };
  }
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)
p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8")
sw=re.sub(r"team-fjz-v\d+(?:-\d+)+","team-fjz-v11-5",sw)
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V11.5 student profile height:",len(html),"bytes")
