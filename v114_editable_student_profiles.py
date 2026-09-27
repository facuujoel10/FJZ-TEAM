import pathlib, re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v114CoachProfileStyles">
.v114-profile-card{margin-top:14px}
.v114-profile-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;margin-top:12px}
.v114-profile-field{border:1px solid var(--border);background:rgba(255,255,255,.025);border-radius:12px;padding:11px;min-width:0}
.v114-profile-field span{display:block;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px}
.v114-profile-field strong{display:block;font-size:13px;line-height:1.35;overflow-wrap:anywhere}
.v114-goal{grid-column:1/-1}
.v114-profile-form{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.v114-profile-form .span2{grid-column:1/-1}
.v114-profile-note{padding:10px 11px;border:1px solid rgba(90,167,255,.22);background:rgba(90,167,255,.05);border-radius:10px}
@media(max-width:720px){.v114-profile-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:520px){.v114-profile-grid,.v114-profile-form{grid-template-columns:1fr}.v114-profile-form .span2,.v114-goal{grid-column:auto}}
</style>
"""

js=r"""
<script id="v114CoachProfileRuntime">
(function(){
  let profileCacheV114=new Map();

  function ageV114(date){
    if(!date)return null;
    const d=new Date(date+'T12:00:00');
    if(Number.isNaN(d.getTime()))return null;
    const now=new Date();
    let age=now.getFullYear()-d.getFullYear();
    const m=now.getMonth()-d.getMonth();
    if(m<0||(m===0&&now.getDate()<d.getDate()))age--;
    return age>=0&&age<120?age:null;
  }
  function fmtDateV114(v){
    if(!v)return 'Sin cargar';
    const d=new Date(v+'T12:00:00');
    if(Number.isNaN(d.getTime()))return 'Sin cargar';
    return d.toLocaleDateString('es-AR',{day:'2-digit',month:'2-digit',year:'numeric'});
  }
  function sexLabelV114(v){
    return ({hombre:'Hombre',mujer:'Mujer',otro:'Otro',prefiero_no_decir:'Prefiero no decir'})[v]||'Sin cargar';
  }
  function valV114(v,suffix=''){
    return v!==null&&v!==undefined&&String(v).trim()!==''?String(v)+suffix:'Sin cargar';
  }
  function escAttrV114(v){
    return String(v??'').replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }
  async function profileRowV114(force=false){
    const s=student(), cached=profileCacheV114.get(s.id);
    if(!force&&cached)return cached;
    const mapRow=cloudAthletes?.get?.(s.id);
    if(!supabaseClient||!mapRow?.id){
      const fallback={client_id:s.id,name:s.name,goal:s.goal};
      profileCacheV114.set(s.id,fallback);
      return fallback;
    }
    const {data,error}=await supabaseClient.from('athletes')
      .select('id,coach_id,user_id,client_id,name,goal,sex,birth_date,occupation_study,start_date,height_cm,invite_code,created_at')
      .eq('id',mapRow.id).single();
    if(error)throw error;
    profileCacheV114.set(s.id,data);
    return data;
  }

  function profileHtmlV114(r){
    const age=ageV114(r.birth_date);
    return '<div class="card v114-profile-card" id="v114ProfileCard">'+
      '<div class="section-title"><div><h3>Datos del alumno</h3><div class="muted tiny">Información básica de la ficha. La edad se calcula automáticamente desde la fecha de nacimiento.</div></div>'+
      '<button class="btn small" onclick="openEditStudentProfileV114()">Editar perfil</button></div>'+
      '<div class="v114-profile-grid">'+
        '<div class="v114-profile-field"><span>Nombre</span><strong>'+esc(r.name||'Sin cargar')+'</strong></div>'+
        '<div class="v114-profile-field"><span>Edad</span><strong>'+(age!==null?age+' años':'Sin cargar')+'</strong></div>'+
        '<div class="v114-profile-field"><span>Sexo</span><strong>'+esc(sexLabelV114(r.sex))+'</strong></div>'+
        '<div class="v114-profile-field"><span>Fecha de nacimiento</span><strong>'+esc(fmtDateV114(r.birth_date))+'</strong></div>'+
        '<div class="v114-profile-field"><span>Altura</span><strong>'+esc(valV114(r.height_cm,' cm'))+'</strong></div>'+
        '<div class="v114-profile-field"><span>Inicio del plan</span><strong>'+esc(fmtDateV114(r.start_date))+'</strong></div>'+
        '<div class="v114-profile-field"><span>Ocupación / estudio</span><strong>'+esc(valV114(r.occupation_study))+'</strong></div>'+
        '<div class="v114-profile-field"><span>Cuenta</span><strong>'+(r.user_id?'Vinculada':'Sin vincular')+'</strong></div>'+
        '<div class="v114-profile-field v114-goal"><span>Objetivo</span><strong>'+esc(r.goal||'Sin cargar')+'</strong></div>'+
      '</div></div>';
  }

  async function injectProfileV114(){
    if(currentProfile?.role!=='coach'||coachTab!=='student'||coachStudentTab!=='summary')return;
    const b=el('coachStudentBody');
    if(!b||el('v114ProfileCard'))return;
    const holder=document.createElement('div');
    holder.id='v114ProfileLoading';
    holder.className='card v114-profile-card';
    holder.innerHTML='<div class="empty">Cargando datos del alumno…</div>';
    b.prepend(holder);
    try{
      const r=await profileRowV114(false);
      holder.outerHTML=profileHtmlV114(r);
    }catch(e){
      holder.innerHTML='<div class="empty">No se pudieron cargar los datos del perfil.</div>';
      console.warn('profile V11.4',e);
    }
  }

  window.openEditStudentProfileV114=async function(){
    let r;
    try{r=await profileRowV114(true)}catch(e){toast(cloudErr(e));return}
    const age=ageV114(r.birth_date);
    showModal(
      '<div class="modal-head"><div><h3>Editar perfil del alumno</h3><div class="muted tiny">'+esc(r.name||student().name)+'</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="v114-profile-form">'+
        '<label class="tiny muted span2">Nombre y apellido<input id="v114Name" class="input" maxlength="100" value="'+escAttrV114(r.name||'')+'"></label>'+
        '<label class="tiny muted span2">Objetivo / descripción<textarea id="v114Goal" class="input" rows="3" maxlength="500">'+esc(r.goal||'')+'</textarea></label>'+
        '<label class="tiny muted">Sexo<select id="v114Sex" class="input">'+
          '<option value="">Sin especificar</option>'+
          '<option value="hombre" '+(r.sex==='hombre'?'selected':'')+'>Hombre</option>'+
          '<option value="mujer" '+(r.sex==='mujer'?'selected':'')+'>Mujer</option>'+
          '<option value="otro" '+(r.sex==='otro'?'selected':'')+'>Otro</option>'+
          '<option value="prefiero_no_decir" '+(r.sex==='prefiero_no_decir'?'selected':'')+'>Prefiero no decir</option>'+
        '</select></label>'+
        '<label class="tiny muted">Fecha de nacimiento<input id="v114Birth" class="input" type="date" value="'+escAttrV114(r.birth_date||'')+'" onchange="updateAgePreviewV114()"></label>'+
        '<label class="tiny muted">Altura (cm)<input id="v114Height" class="input" type="number" min="100" max="250" step="0.1" value="'+escAttrV114(r.height_cm??'')+'"></label>'+
        '<label class="tiny muted">Fecha de inicio<input id="v114Start" class="input" type="date" value="'+escAttrV114(r.start_date||'')+'"></label>'+
        '<label class="tiny muted span2">Ocupación / estudio<input id="v114Occupation" class="input" maxlength="160" value="'+escAttrV114(r.occupation_study||'')+'" placeholder="Ej: Empresa · 8:00 a 17:00"></label>'+
      '</div>'+
      '<div class="v114-profile-note muted tiny" style="margin-top:12px">Edad actual: <strong id="v114AgePreview">'+(age!==null?age+' años':'sin fecha cargada')+'</strong>. Editar estos datos no modifica la cuenta vinculada, la rutina ni el historial.</div>'+
      '<button class="btn primary" style="width:100%;margin-top:14px" onclick="saveStudentProfileV114()">Guardar cambios</button>'
    );
  };

  window.updateAgePreviewV114=function(){
    const a=ageV114(el('v114Birth')?.value);
    const h=el('v114AgePreview');
    if(h)h.textContent=a!==null?a+' años':'sin fecha cargada';
  };

  window.saveStudentProfileV114=async function(){
    if(currentProfile?.role!=='coach'||!supabaseClient){toast('Requiere cuenta Coach conectada');return}
    const s=student(), row=cloudAthletes?.get?.(s.id);
    if(!row?.id){toast('No encuentro la ficha en la nube');return}

    const name=(el('v114Name')?.value||'').trim();
    const goal=(el('v114Goal')?.value||'').trim();
    if(!name){toast('El nombre no puede quedar vacío');return}

    const hRaw=el('v114Height')?.value;
    const height=hRaw===''?null:Number(hRaw);
    if(height!==null&&(!Number.isFinite(height)||height<100||height>250)){
      toast('Revisá la altura');return;
    }

    const payload={
      name,
      goal:goal||'Plan personalizado',
      sex:el('v114Sex')?.value||null,
      birth_date:el('v114Birth')?.value||null,
      occupation_study:(el('v114Occupation')?.value||'').trim()||null,
      start_date:el('v114Start')?.value||null,
      height_cm:height
    };

    const btn=document.querySelector('.modal .btn.primary');
    if(btn){btn.disabled=true;btn.textContent='Guardando…'}
    const {data,error}=await supabaseClient.from('athletes')
      .update(payload).eq('id',row.id)
      .select('id,coach_id,user_id,client_id,name,goal,sex,birth_date,occupation_study,start_date,height_cm,invite_code,created_at')
      .single();

    if(error){
      if(btn){btn.disabled=false;btn.textContent='Guardar cambios'}
      toast(cloudErr(error));return;
    }

    s.name=data.name;
    s.goal=data.goal;
    s.profile={
      ...(s.profile||{}),
      sex:data.sex||null,
      birth_date:data.birth_date||null,
      occupation_study:data.occupation_study||null,
      start_date:data.start_date||null,
      height_cm:data.height_cm??null
    };
    cloudAthletes.set(s.id,{...row,...data});
    profileCacheV114.set(s.id,data);
    saveState();
    try{await syncCloudNow()}catch(e){console.warn('profile sync V11.4',e)}
    closeModal();
    render();
    toast('Perfil actualizado');
  };

  const baseRenderCoachStudentV114=window.renderCoachStudent;
  window.renderCoachStudent=function(){
    const out=baseRenderCoachStudentV114.apply(this,arguments);
    if(currentProfile?.role==='coach'&&coachStudentTab==='summary'){
      setTimeout(injectProfileV114,50);
    }
    return out;
  };

  const baseRenderV114=window.render;
  window.render=function(){
    const out=baseRenderV114.apply(this,arguments);
    if(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'){
      setTimeout(injectProfileV114,80);
    }
    return out;
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)
p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8")
sw=re.sub(r"team-fjz-v\d+(?:-\d+)+","team-fjz-v11-4",sw)
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V11.4 editable student profiles:",len(html),"bytes")
