import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")
html=html.replace("TEAM FJZ V9.9","TEAM FJZ V10.0")

# V10 consolida parches visuales/check-in ya reemplazados por una única capa.
obsolete_styles=[
  "v88Fixes","v91CheckinPolish","v92CoachPhotoUpload",
  "v98PrecisionPolish","v99AuditPolish"
]
obsolete_scripts=[
  "v88Runtime","v90MotivationFix","v91CheckinClamp",
  "v92CoachPhotoUploadRuntime","v98PrecisionPolishRuntime","v99AuditRuntime"
]
for sid in obsolete_styles:
    html=re.sub(r'<style\\s+id=["\\\']'+re.escape(sid)+r'["\\\'][^>]*>.*?</style>\\s*','',html,flags=re.S|re.I)
for sid in obsolete_scripts:
    html=re.sub(r'<script\\s+id=["\\\']'+re.escape(sid)+r'["\\\'][^>]*>.*?</script>\\s*','',html,flags=re.S|re.I)

css=r"""
<style id="v100CorePolish">
/* TEAM FJZ V10 · capa visual consolidada */
.v65-lib-shortcuts,.v88-version,#v88Version,#v92CoachPhotoUploader,#cloudFeedWrap{display:none!important}

.input,input.input,select.input,textarea.input{box-sizing:border-box!important;max-width:100%!important}
input.input:not([type="file"]):not([type="checkbox"]):not([type="radio"]),select.input{
  min-height:42px!important;height:42px!important;padding-top:0!important;padding-bottom:0!important
}
textarea.input{min-height:92px!important;resize:vertical}
.card,.hero,.grid,.form-grid,#view,#studentSubBody,#coachStudentBody{min-width:0;max-width:100%;box-sizing:border-box}
.section-title{display:flex!important;align-items:flex-start!important;justify-content:space-between!important;gap:12px!important}
.section-title>div:first-child,.modal-head>div{min-width:0}
.section-title h3,.modal-head h3,.exercise-row h4,.student-row h4{overflow-wrap:anywhere}
.btn.small{min-height:32px;display:inline-flex;align-items:center;justify-content:center}
.btn:not(.small){min-height:40px}
.pill-row{align-items:center!important}

/* Check-in: 8 métricas, mismas dimensiones y sin reglas heredadas */
#studentSubBody .tracking-grid,
#studentSubBody .v701-checkin-scores{
  display:grid!important;
  grid-template-columns:repeat(4,minmax(0,1fr))!important;
  gap:9px!important;
  align-items:stretch!important
}
#studentSubBody .tracking-grid>.track-score,
#studentSubBody .v701-checkin-scores>.track-score{
  grid-column:auto!important;grid-row:auto!important;
  min-width:0!important;width:100%!important;
  min-height:100px!important;height:100px!important;
  padding:11px!important;border-radius:12px!important;
  display:flex!important;flex-direction:column!important;justify-content:space-between!important;
  align-self:stretch!important;box-sizing:border-box!important
}
#studentSubBody .tracking-grid>.track-score label,
#studentSubBody .v701-checkin-scores>.track-score label{
  display:flex!important;align-items:center!important;
  min-height:28px!important;height:28px!important;
  margin:0 0 7px!important;line-height:1.15!important;font-size:10px!important
}
#studentSubBody .tracking-grid>.track-score input,
#studentSubBody .v701-checkin-scores>.track-score input{
  min-height:40px!important;height:40px!important;width:100%!important;
  margin:0!important;text-align:center!important;font-weight:800!important;
  box-sizing:border-box!important;font-variant-numeric:tabular-nums
}
@media(max-width:760px){
  #studentSubBody .tracking-grid,#studentSubBody .v701-checkin-scores{
    grid-template-columns:repeat(2,minmax(0,1fr))!important
  }
}
@media(max-width:360px){
  #studentSubBody .tracking-grid,#studentSubBody .v701-checkin-scores{grid-template-columns:1fr!important}
}

/* Campos de medición retirados */
label:has(>#mAbd),label:has(>#mArmRight),label:has(>#mThighRight){display:none!important}

/* Ritmo visual consistente */
.form-grid{align-items:end!important}
.form-grid>label{min-width:0!important}
.form-grid>label>.input,.form-grid>label>input,.form-grid>label>select{margin-top:5px!important}
.grid.kpi,.metric-grid,.summary-grid,.v72-progress-kpis,.v81-agenda-kpis,.v96-alert-summary{align-items:stretch!important}
.grid.kpi>.card,.metric-grid>*,.summary-grid>*,.v72-progress-kpi,.v81-agenda-kpi,.v96-alert-kpi{
  height:100%!important;min-height:86px!important;
  display:flex!important;flex-direction:column!important;justify-content:center!important;
  box-sizing:border-box!important
}
.v86-profile-grid{grid-auto-rows:1fr!important;align-items:stretch!important}
.v86-profile-field{height:100%!important;min-height:72px!important;padding:10px 11px!important;justify-content:center!important}
.nutrition-targets,.macro-preview{align-items:stretch!important}
.nutrition-targets>.macro-card,.macro-preview>div{height:100%!important;box-sizing:border-box!important}
.v94-guide-box,.v93-measure-row,.v96-alert-card,.v96-notice-item{box-sizing:border-box!important}
.v94-guide-head{min-height:38px!important}
.v94-guide-item{min-height:48px!important;box-sizing:border-box!important}
.v93-measure-row{min-height:46px!important}
.v94-chart{min-height:265px!important;box-sizing:border-box!important}
.v94-chart svg{height:190px!important}
.v96-alert-card{min-height:72px!important}
.v96-alert-kpi{min-height:78px!important}
.v96-notice-item{min-height:58px!important}
.v70-recipe-grid,.photo-grid{align-items:stretch!important}
.v70-recipe-card,.photo-card,.photo-slot{height:100%!important;box-sizing:border-box!important}
.v70-recipe-card{display:flex!important;flex-direction:column!important}

.student-row{min-height:68px;box-sizing:border-box!important}
.exercise-row{min-height:58px;box-sizing:border-box!important}
.history-item{min-height:52px;box-sizing:border-box!important}
.food-item,.food-item-v61,.nutrition-log-row{min-width:0}

@media(max-width:700px){.photo-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important}}
@media(max-width:520px){
  .nutrition-targets,.macro-preview{grid-template-columns:1fr 1fr!important}
  .food-item{grid-template-columns:1fr!important}
}
@media(max-width:430px){.photo-grid{grid-template-columns:1fr!important}}
@media(max-width:760px){
  .section-title{flex-wrap:wrap!important}
  .section-title>.badge,.section-title>.btn{flex:0 0 auto}
  .card,.hero,.track-row,.v93-measure-row,.v94-guide-box,.v96-alert-card{max-width:100%!important}
}
</style>
"""

js=r"""
<script id="v100CoreRuntime">
(function(){
  const SCORE_IDS=['ciSleep','ciStress','ciEnergy','ciAdh','ciMood','ciHunger','ciMotivation','ciRecovery'];
  let polishTimer=null;

  function clamp110(input){
    if(!input)return;
    const raw=String(input.value??'').replace(/[^0-9]/g,'');
    if(raw===''){input.value='';return}
    let n=parseInt(raw,10);
    if(!Number.isFinite(n))n=1;
    input.value=String(Math.max(1,Math.min(10,n)));
  }

  function ensureMotivation(){
    if(document.getElementById('ciMotivation'))return;
    const grid=document.querySelector('#studentSubBody .tracking-grid, #studentSubBody .v701-checkin-scores');
    if(!grid)return;
    const card=document.createElement('div');
    card.className='track-score';
    card.innerHTML='<label>Motivación</label><input id="ciMotivation" class="input" type="number" min="1" max="10" step="1" inputmode="numeric" value="7">';
    const recovery=document.getElementById('ciRecovery')?.closest('.track-score');
    recovery?grid.insertBefore(card,recovery):grid.appendChild(card);
  }

  function moveHunger(){
    const input=document.getElementById('ciHunger');
    const grid=document.querySelector('#studentSubBody .tracking-grid, #studentSubBody .v701-checkin-scores');
    if(!input||!grid)return;
    let card=input.closest('.track-score');
    if(!card){
      const oldLabel=input.closest('label');
      card=document.createElement('div');
      card.className='track-score';
      const label=document.createElement('label');
      label.textContent='Hambre';
      card.appendChild(label);
      card.appendChild(input);
      if(oldLabel&&oldLabel!==card&&oldLabel.parentNode)oldLabel.remove();
    }
    const motivation=document.getElementById('ciMotivation')?.closest('.track-score');
    motivation?grid.insertBefore(card,motivation):grid.appendChild(card);
  }

  function normalizeCheckin(){
    ensureMotivation();
    moveHunger();
    const grid=document.querySelector('#studentSubBody .tracking-grid, #studentSubBody .v701-checkin-scores');
    SCORE_IDS.forEach(id=>{
      const inputs=[...document.querySelectorAll('#'+id)];
      inputs.slice(1).forEach(x=>{
        const card=x.closest('.track-score');
        card?card.remove():x.remove();
      });
      const input=document.getElementById(id);
      if(!input)return;
      input.min='1';input.max='10';input.step='1';input.inputMode='numeric';input.pattern='[0-9]*';
      input.oninput=()=>clamp110(input);
      input.onchange=()=>clamp110(input);
      input.onblur=()=>{clamp110(input);if(input.value==='')input.value='1'};
      const card=input.closest('.track-score');
      if(card){card.style.gridColumn='auto';card.style.width='100%'}
    });
    if(grid){
      SCORE_IDS.forEach(id=>{
        const card=document.getElementById(id)?.closest('.track-score');
        if(card)grid.appendChild(card);
      });
    }
    const badge=document.querySelector('#studentSubBody .section-title .badge.blue');
    if(badge&&/1.?10|10/.test(badge.textContent||''))badge.textContent='1–10';
  }

  function removeDuplicateId(id){
    const nodes=[...document.querySelectorAll('#'+id)];
    nodes.slice(1).forEach(n=>n.remove());
  }

  function cleanupDom(){
    document.querySelectorAll('.v65-lib-shortcuts,#v88Version,#v92CoachPhotoUploader,#cloudFeedWrap').forEach(n=>n.remove());
    [
      'v93MeasureCompare','v96CoachAlerts','v96StudentPreview','v94SuppCoach',
      'v94SuppStudent','v86StudentProfileCard','v86CoachProfile',
      'v93CoachPhotoUploader','v96NoticeCoachCard'
    ].forEach(removeDuplicateId);
  }

  function prettyDates(){
    document.querySelectorAll('.v93-compare-head .muted.tiny').forEach(n=>{
      n.textContent=n.textContent.replace(/\b(\d{4})-(\d{2})-(\d{2})\b/g,'$3/$2/$1');
    });
  }

  function polish(){
    cleanupDom();
    normalizeCheckin();
    prettyDates();
  }

  const previousChart=window.simpleLineChart;
  if(typeof previousChart==='function'){
    window.simpleLineChart=function(){
      const out=previousChart.apply(this,arguments);
      return typeof out==='string'?out.replace(/\b(\d{4})-(\d{2})-(\d{2})\b/g,'$3/$2/$1'):out;
    };
  }

  const previousSubmit=window.submitWeeklyCheckin;
  if(typeof previousSubmit==='function'){
    window.submitWeeklyCheckin=async function(){
      normalizeCheckin();
      for(const id of SCORE_IDS){
        const input=document.getElementById(id);
        if(!input)continue;
        clamp110(input);
        const n=Number(input.value);
        if(!Number.isFinite(n)||n<1||n>10){
          toast('Todos los valores del check-in deben estar entre 1 y 10');
          input.focus();
          return;
        }
      }
      return previousSubmit.apply(this,arguments);
    };
  }

  const previousOpenLibrary=window.openLibrary;
  if(typeof previousOpenLibrary==='function'){
    window.openLibrary=function(){
      const out=previousOpenLibrary.apply(this,arguments);
      setTimeout(()=>document.querySelectorAll('.v65-lib-shortcuts').forEach(n=>n.remove()),0);
      return out;
    };
  }

  const previousRender=window.render;
  window.render=function(){
    const out=previousRender.apply(this,arguments);
    setTimeout(polish,40);
    setTimeout(polish,300);
    return out;
  };

  const observer=new MutationObserver(()=>{
    clearTimeout(polishTimer);
    polishTimer=setTimeout(polish,45);
  });

  setTimeout(()=>{
    const view=document.getElementById('view');
    if(view)observer.observe(view,{childList:true,subtree:true});
    polish();
  },180);
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

# Limpieza de espacios excesivos generados por capas eliminadas.
html=re.sub(r'\n{4,}','\n\n\n',html)

p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8").replace("team-fjz-v9-9","team-fjz-v10-0")
swp.write_text(sw,encoding="utf-8")

print("TEAM FJZ V10.0 core cleanup:",len(html),"bytes")


# V10.1 · encuadre ajustable de foto de perfil
html=p.read_text(encoding="utf-8")
html=html.replace("TEAM FJZ V10.0","TEAM FJZ V10.1")
avatar_css=r"""
<style id="v101AvatarAdjustStyles">
.v70-avatar{overflow:hidden!important}
.v70-avatar img{width:100%!important;height:100%!important;object-fit:cover!important;display:block!important}
.v101-avatar-preview{width:min(280px,72vw);aspect-ratio:1;margin:0 auto 14px;border-radius:50%;overflow:hidden;border:2px solid rgba(255,255,255,.82);background:#09090b}
.v101-avatar-preview img{width:100%;height:100%;object-fit:cover;display:block}
.v101-adjust-grid{display:grid;gap:12px}
.v101-adjust-row{display:grid;grid-template-columns:86px minmax(0,1fr) 42px;gap:10px;align-items:center}
.v101-adjust-row input[type="range"]{width:100%;accent-color:var(--red)}
.v101-adjust-value{text-align:right;font-size:11px;color:var(--muted);font-variant-numeric:tabular-nums}
@media(max-width:520px){.v101-adjust-row{grid-template-columns:68px minmax(0,1fr) 38px}}
</style>
"""
avatar_js=r"""
<script id="v101AvatarAdjustRuntime">
(function(){
  const cache=new Map();
  async function getFrame(id,force=false){
    if(!id)return{x:50,y:50,z:1};
    if(!force&&cache.has(id))return cache.get(id);
    const r=await supabaseClient.from('profiles').select('id,avatar_position_x,avatar_position_y,avatar_zoom').eq('id',id).maybeSingle();
    if(r.error)return{x:50,y:50,z:1};
    const v={x:Number(r.data?.avatar_position_x??50),y:Number(r.data?.avatar_position_y??50),z:Number(r.data?.avatar_zoom??1)};
    cache.set(id,v);return v;
  }
  window.avatarHtmlV70=async function(userId,name,size=''){
    const path=await profilePathV70(userId),url=await signedAvatarV70(path),a=await getFrame(userId);
    const body=url?'<img src="'+url+'" alt="'+esc(name||'Perfil')+'" style="object-position:'+a.x+'% '+a.y+'%;transform:scale('+a.z+');transform-origin:'+a.x+'% '+a.y+'%;">':esc((name||'?').slice(0,2).toUpperCase());
    return '<div class="v70-avatar '+size+'">'+body+'</div>';
  };
  function inject(){
    if(currentProfile?.role!=='student'||!currentProfile?.avatar_url)return;
    const actions=document.querySelector('#v70StudentProfile .v70-profile-actions');
    if(!actions||document.getElementById('v101AdjustAvatarBtn'))return;
    const b=document.createElement('button');b.id='v101AdjustAvatarBtn';b.className='btn ghost small';b.textContent='Acomodar';b.onclick=openAvatarAdjustV101;
    actions.insertBefore(b,actions.children[1]||null);
  }
  window.openAvatarAdjustV101=async function(){
    const url=await signedAvatarV70(currentProfile.avatar_url),a=await getFrame(currentUser.id,true);
    showModal('<div class="modal-head"><div><h3>Acomodar foto de perfil</h3><div class="muted tiny">Mové el encuadre y el zoom hasta que quede como te gusta.</div></div><button class="btn small" onclick="closeModal()">✕</button></div><div class="v101-avatar-preview"><img id="v101AvatarPreviewImg" src="'+url+'"></div><div class="v101-adjust-grid"><div class="v101-adjust-row"><strong class="tiny">Horizontal</strong><input id="v101AvatarX" type="range" min="0" max="100" value="'+a.x+'" oninput="previewAvatarAdjustV101()"><span id="v101AvatarXVal" class="v101-adjust-value"></span></div><div class="v101-adjust-row"><strong class="tiny">Vertical</strong><input id="v101AvatarY" type="range" min="0" max="100" value="'+a.y+'" oninput="previewAvatarAdjustV101()"><span id="v101AvatarYVal" class="v101-adjust-value"></span></div><div class="v101-adjust-row"><strong class="tiny">Zoom</strong><input id="v101AvatarZoom" type="range" min="1" max="3" step=".05" value="'+a.z+'" oninput="previewAvatarAdjustV101()"><span id="v101AvatarZoomVal" class="v101-adjust-value"></span></div><div class="pill-row" style="justify-content:flex-end"><button class="btn ghost" onclick="resetAvatarAdjustV101()">Centrar</button><button class="btn" onclick="closeModal()">Cancelar</button><button class="btn primary" onclick="saveAvatarAdjustV101()">Guardar encuadre</button></div></div>');
    previewAvatarAdjustV101();
  };
  window.previewAvatarAdjustV101=function(){
    const img=el('v101AvatarPreviewImg');if(!img)return;
    const x=+el('v101AvatarX').value,y=+el('v101AvatarY').value,z=+el('v101AvatarZoom').value;
    img.style.objectPosition=x+'% '+y+'%';img.style.transform='scale('+z+')';img.style.transformOrigin=x+'% '+y+'%';
    el('v101AvatarXVal').textContent=Math.round(x)+'%';el('v101AvatarYVal').textContent=Math.round(y)+'%';el('v101AvatarZoomVal').textContent=z.toFixed(1)+'×';
  };
  window.resetAvatarAdjustV101=function(){el('v101AvatarX').value=50;el('v101AvatarY').value=50;el('v101AvatarZoom').value=1;previewAvatarAdjustV101()};
  window.saveAvatarAdjustV101=async function(){
    const x=+el('v101AvatarX').value,y=+el('v101AvatarY').value,z=+el('v101AvatarZoom').value;
    const r=await supabaseClient.from('profiles').update({avatar_position_x:x,avatar_position_y:y,avatar_zoom:z}).eq('id',currentUser.id);
    if(r.error){toast(cloudErr(r.error));return}
    cache.set(currentUser.id,{x,y,z});closeModal();toast('Encuadre guardado');render();
  };
  const oldUpload=window.uploadProfilePhotoV70;
  if(typeof oldUpload==='function')window.uploadProfilePhotoV70=async function(input){await oldUpload(input);if(currentUser?.id){await supabaseClient.from('profiles').update({avatar_position_x:50,avatar_position_y:50,avatar_zoom:1}).eq('id',currentUser.id);cache.set(currentUser.id,{x:50,y:50,z:1})}};
  const oldRender=window.render;
  window.render=function(){const out=oldRender.apply(this,arguments);setTimeout(inject,120);setTimeout(inject,600);return out};
  Object.assign(window,{openAvatarAdjustV101,previewAvatarAdjustV101,resetAvatarAdjustV101,saveAvatarAdjustV101});
  setTimeout(inject,250);
})();
</script>
"""
html=html.replace("</head>",avatar_css+"\n</head>",1)
html=html.replace("</body>",avatar_js+"\n</body>",1)
p.write_text(html,encoding="utf-8")
swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8").replace("team-fjz-v10-0","team-fjz-v10-1")
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V10.1 avatar adjust:",len(html),"bytes")


# V10.2 · editor completo de opciones nutricionales
html=p.read_text(encoding="utf-8")
html=html.replace("TEAM FJZ V10.1","TEAM FJZ V10.2")
nutedit_css=r"""
<style id="v102NutritionEditStyles">
.v102-option-note{margin-top:7px;padding:7px 9px;border-left:2px solid rgba(255,255,255,.18);color:var(--muted);font-size:10px;background:rgba(255,255,255,.02);border-radius:0 8px 8px 0}
.v102-edit-list{display:grid;gap:10px;margin-top:12px}
.v102-edit-item{border:1px solid var(--border);background:#0d0d10;border-radius:12px;padding:11px}
.v102-edit-item-grid{display:grid;grid-template-columns:minmax(0,2fr) repeat(5,minmax(80px,.7fr));gap:8px;align-items:end}
.v102-edit-item-grid .wide{grid-column:auto}
.v102-edit-actions{display:flex;gap:7px;justify-content:flex-end;margin-top:8px}
.v102-option-toolbar{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}
@media(max-width:900px){
 .v102-edit-item-grid{grid-template-columns:1fr 1fr}
 .v102-edit-item-grid .wide{grid-column:1/-1}
}
@media(max-width:520px){
 .v102-edit-item-grid{grid-template-columns:1fr}
 .v102-edit-item-grid .wide{grid-column:auto}
 .v102-option-toolbar{justify-content:flex-start}
}
</style>
"""
nutedit_js=r"""
<script id="v102NutritionEditRuntime">
(function(){
  function numV102(v){const n=Number(v);return Number.isFinite(n)?n:0}
  function optV102(mealId,optId){return findNutritionOption(mealId,optId)}

  window.renderNutritionOptionCoach=function(meal,opt){
    const t=nutritionOptionTotals(opt);
    return '<div class="option-card"><div class="option-head"><div><strong>'+esc(opt.name||'Opción')+'</strong>'+
      '<div class="macro-row" style="margin-top:5px"><span class="macro-chip">'+nFmt(t.kcal,0)+' kcal</span><span class="macro-chip">P '+nFmt(t.protein_g,1)+' g</span><span class="macro-chip">C '+nFmt(t.carbs_g,1)+' g</span><span class="macro-chip">G '+nFmt(t.fat_g,1)+' g</span></div>'+
      (opt.note?'<div class="v102-option-note">'+esc(opt.note)+'</div>':'')+
      '</div><div class="v102-option-toolbar"><button class="btn small" onclick="openNutritionOptionEditorV102(\''+meal.id+'\',\''+opt.id+'\')">Editar opción</button><button class="btn small" onclick="openNutritionFoodPicker(\''+meal.id+'\',\''+opt.id+'\')">+ Alimento</button><button class="btn ghost small" onclick="deleteNutritionOption(\''+meal.id+'\',\''+opt.id+'\')">Eliminar</button></div></div>'+
      '<div>'+((opt.items||[]).length?opt.items.map(i=>{
        const grams=i.grams!=null&&Number(i.grams)>0?nFmt(i.grams,0)+' g':'Cantidad personalizada';
        return '<div class="food-item-v61"><div><strong>'+esc(i.name)+'</strong><div class="muted micro">'+esc(grams)+' · '+nFmt(i.kcal,0)+' kcal · P '+nFmt(i.protein_g,1)+' · C '+nFmt(i.carbs_g,1)+' · G '+nFmt(i.fat_g,1)+'</div></div><div class="food-item-v61-actions"><button class="btn small" onclick="openNutritionItemEditorV102(\''+meal.id+'\',\''+opt.id+'\',\''+i.id+'\')">Editar</button><button class="btn ghost small" onclick="removeNutritionItem(\''+meal.id+'\',\''+opt.id+'\',\''+i.id+'\')">✕</button></div></div>';
      }).join(''):'<div class="muted tiny" style="margin-top:10px">Agregá alimentos a esta opción.</div>')+'</div></div>';
  };
  try{renderNutritionOptionCoach=window.renderNutritionOptionCoach}catch(_){}

  function editorItemHtmlV102(i,idx){
    return '<div class="v102-edit-item" data-v102-index="'+idx+'">'+
      '<div class="v102-edit-item-grid">'+
      '<label class="tiny muted wide">Descripción / alimento<input class="input v102-name" value="'+esc(i.name||'')+'"></label>'+
      '<label class="tiny muted">Gramos<input class="input v102-grams" type="number" min="0" step="1" value="'+(i.grams??'')+'" placeholder="Opcional"></label>'+
      '<label class="tiny muted">kcal<input class="input v102-kcal" type="number" min="0" step="1" value="'+numV102(i.kcal)+'"></label>'+
      '<label class="tiny muted">Proteína g<input class="input v102-p" type="number" min="0" step=".1" value="'+numV102(i.protein_g)+'"></label>'+
      '<label class="tiny muted">Carbos g<input class="input v102-c" type="number" min="0" step=".1" value="'+numV102(i.carbs_g)+'"></label>'+
      '<label class="tiny muted">Grasas g<input class="input v102-f" type="number" min="0" step=".1" value="'+numV102(i.fat_g)+'"></label>'+
      '</div><div class="v102-edit-actions"><button class="btn ghost small" onclick="removeNutritionEditorRowV102(this)">Quitar de opción</button></div></div>';
  }

  window.openNutritionOptionEditorV102=function(mealId,optId){
    const o=optV102(mealId,optId);if(!o)return;
    showModal('<div class="modal-head"><div><h3>Editar opción de comida</h3><div class="muted tiny">Podés corregir cantidades, descripción y macros sin borrar la opción.</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="form-grid"><label class="tiny muted span2">Nombre de la opción<input id="v102OptName" class="input" value="'+esc(o.name||'Opción')+'"></label><label class="tiny muted span2">Nota<input id="v102OptNote" class="input" value="'+esc(o.note||'')+'" placeholder="Ej: recomendable en día de piernas"></label></div>'+
      '<div id="v102EditItems" class="v102-edit-list">'+(o.items||[]).map(editorItemHtmlV102).join('')+'</div>'+
      '<div class="nutrition-note" style="margin-top:12px"><strong>Edición manual</strong><div class="muted tiny" style="margin-top:4px">Si es una opción importada del PDF, podés corregir directamente el texto y los macros. Si es un alimento de la biblioteca y cambiás los gramos, la app recalcula usando sus valores por 100 g.</div></div>'+
      '<button class="btn primary" style="width:100%;margin-top:12px" onclick="saveNutritionOptionEditorV102(\''+mealId+'\',\''+optId+'\')">Guardar cambios</button>');
  };

  window.removeNutritionEditorRowV102=function(btn){btn.closest('.v102-edit-item')?.remove()};

  function readRowsV102(o){
    const oldById=new Map((o.items||[]).map(x=>[x.id,x]));
    return [...document.querySelectorAll('#v102EditItems .v102-edit-item')].map((row,idx)=>{
      const old=(o.items||[])[Number(row.dataset.v102Index)]||{};
      const name=row.querySelector('.v102-name')?.value.trim()||old.name||'Alimento';
      const gramsRaw=row.querySelector('.v102-grams')?.value;
      const grams=gramsRaw===''?null:Math.max(0,numV102(gramsRaw));
      let kcal=numV102(row.querySelector('.v102-kcal')?.value);
      let protein_g=numV102(row.querySelector('.v102-p')?.value);
      let carbs_g=numV102(row.querySelector('.v102-c')?.value);
      let fat_g=numV102(row.querySelector('.v102-f')?.value);
      if(grams&&old.kcal_100g!=null){
        const m=macroCalcFrom100(old,grams);kcal=m.kcal;protein_g=m.protein_g;carbs_g=m.carbs_g;fat_g=m.fat_g;
      }
      return {...old,id:old.id||uid('food'),name,grams,kcal,protein_g,carbs_g,fat_g};
    });
  }

  window.saveNutritionOptionEditorV102=async function(mealId,optId){
    const o=optV102(mealId,optId);if(!o)return;
    o.name=el('v102OptName')?.value.trim()||o.name||'Opción';
    o.note=el('v102OptNote')?.value.trim()||'';
    o.items=readRowsV102(o);
    closeModal();
    renderNutritionCoachLoaded();
    await saveNutritionPlan();
    toast('Opción actualizada');
  };

  window.openNutritionItemEditorV102=function(mealId,optId,itemId){
    const o=optV102(mealId,optId),i=o?.items?.find(x=>x.id===itemId);if(!o||!i)return;
    showModal('<div class="modal-head"><div><h3>Editar alimento</h3><div class="muted tiny">Corregí cantidad o información de esta opción.</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="form-grid"><label class="tiny muted span2">Descripción<input id="v102ItemName" class="input" value="'+esc(i.name||'')+'"></label><label class="tiny muted">Gramos<input id="v102ItemGrams" class="input" type="number" min="0" step="1" value="'+(i.grams??'')+'" placeholder="Opcional"></label><label class="tiny muted">kcal<input id="v102ItemKcal" class="input" type="number" min="0" step="1" value="'+numV102(i.kcal)+'"></label><label class="tiny muted">Proteína g<input id="v102ItemP" class="input" type="number" min="0" step=".1" value="'+numV102(i.protein_g)+'"></label><label class="tiny muted">Carbos g<input id="v102ItemC" class="input" type="number" min="0" step=".1" value="'+numV102(i.carbs_g)+'"></label><label class="tiny muted">Grasas g<input id="v102ItemF" class="input" type="number" min="0" step=".1" value="'+numV102(i.fat_g)+'"></label></div>'+
      '<button class="btn primary" style="width:100%;margin-top:12px" onclick="saveNutritionItemEditorV102(\''+mealId+'\',\''+optId+'\',\''+itemId+'\')">Guardar alimento</button>');
  };

  window.saveNutritionItemEditorV102=async function(mealId,optId,itemId){
    const o=optV102(mealId,optId),i=o?.items?.find(x=>x.id===itemId);if(!i)return;
    i.name=el('v102ItemName')?.value.trim()||i.name;
    const raw=el('v102ItemGrams')?.value;i.grams=raw===''?null:Math.max(0,numV102(raw));
    if(i.grams&&i.kcal_100g!=null)Object.assign(i,macroCalcFrom100(i,i.grams));
    else{
      i.kcal=numV102(el('v102ItemKcal')?.value);
      i.protein_g=numV102(el('v102ItemP')?.value);
      i.carbs_g=numV102(el('v102ItemC')?.value);
      i.fat_g=numV102(el('v102ItemF')?.value);
    }
    closeModal();renderNutritionCoachLoaded();await saveNutritionPlan();toast('Alimento actualizado');
  };

  Object.assign(window,{openNutritionOptionEditorV102,saveNutritionOptionEditorV102,removeNutritionEditorRowV102,openNutritionItemEditorV102,saveNutritionItemEditorV102});
})();
</script>
"""
html=html.replace("</head>",nutedit_css+"\n</head>",1)
html=html.replace("</body>",nutedit_js+"\n</body>",1)
p.write_text(html,encoding="utf-8")
swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8").replace("team-fjz-v10-1","team-fjz-v10-2")
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V10.2 nutrition option editor:",len(html),"bytes")
