import pathlib, re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v120ProgressPhotoManageStyles">
.v120-photo-actions{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.v120-photo-actions .btn{font-size:10px;padding:6px 8px}
.v120-photo-input{display:none}
.v120-photo-busy{opacity:.65;pointer-events:none}
</style>
"""

js=r"""
<script id="v120ProgressPhotoManageRuntime">
(function(){
  let photoBusyV120=false;

  function photoByIdV120(id){
    return (trackingCache?.photos||[]).find(p=>String(p.id)===String(id))||null;
  }

  async function refreshPhotosV120(){
    trackingLoadedFor=null;
    await loadTracking(true);
    if(currentProfile?.role==='student'){
      renderStudentTrackingHistory();
    }else{
      renderTrackingCoachLoaded();
    }
  }

  window.replaceProgressPhotoV120=function(id){
    if(photoBusyV120)return;
    const input=document.getElementById('v120Replace_'+id);
    if(input)input.click();
  };

  window.handleReplaceProgressPhotoV120=async function(id,input){
    if(photoBusyV120)return;
    const file=input?.files?.[0];
    if(!file)return;
    const photo=photoByIdV120(id);
    if(!photo){toast('No encuentro esa foto');input.value='';return}
    if(file.size>8*1024*1024){toast('La foto supera 8 MB');input.value='';return}
    if(file.type&&!file.type.startsWith('image/')){toast('Elegí una imagen válida');input.value='';return}

    photoBusyV120=true;
    const card=input.closest('.photo-slot,.photo-card');
    if(card)card.classList.add('v120-photo-busy');

    try{
      const ext=(file.name.split('.').pop()||'jpg').toLowerCase().replace(/[^a-z0-9]/g,'');
      const safeExt=ext||'jpg';
      const newPath=`${photo.athlete_id}/${photo.taken_on}/${photo.pose}_${Date.now()}.${safeExt}`;

      toast('Reemplazando foto…');

      const {error:upErr}=await supabaseClient.storage
        .from('progress-photos')
        .upload(newPath,file,{contentType:file.type||'image/jpeg',upsert:false});
      if(upErr)throw upErr;

      const {error:updateErr}=await supabaseClient
        .from('progress_photos')
        .update({storage_path:newPath})
        .eq('id',photo.id);
      if(updateErr){
        try{await supabaseClient.storage.from('progress-photos').remove([newPath])}catch(_e){}
        throw updateErr;
      }

      if(photo.storage_path&&photo.storage_path!==newPath){
        try{await supabaseClient.storage.from('progress-photos').remove([photo.storage_path])}catch(_e){}
      }

      input.value='';
      await refreshPhotosV120();
      toast('Foto reemplazada');
    }catch(e){
      console.error('replace photo V12.0',e);
      toast(cloudErr(e));
      input.value='';
    }finally{
      photoBusyV120=false;
      if(card)card.classList.remove('v120-photo-busy');
    }
  };

  window.deleteProgressPhotoV120=async function(id){
    if(photoBusyV120)return;
    const photo=photoByIdV120(id);
    if(!photo){toast('No encuentro esa foto');return}
    if(!confirm('¿Eliminar esta foto de progreso? Después vas a poder subir otra.'))return;

    photoBusyV120=true;
    try{
      const {error:dbErr}=await supabaseClient
        .from('progress_photos')
        .delete()
        .eq('id',photo.id);
      if(dbErr)throw dbErr;

      if(photo.storage_path){
        try{await supabaseClient.storage.from('progress-photos').remove([photo.storage_path])}catch(_e){}
      }

      await refreshPhotosV120();
      toast('Foto eliminada');
    }catch(e){
      console.error('delete photo V12.0',e);
      toast(cloudErr(e));
    }finally{
      photoBusyV120=false;
    }
  };

  function photoActionsV120(p){
    const id=String(p.id);
    return '<div class="v120-photo-actions">'+
      '<button class="btn small" type="button" onclick="replaceProgressPhotoV120(\''+esc(id)+'\')">Reemplazar</button>'+
      '<button class="btn ghost small" type="button" onclick="deleteProgressPhotoV120(\''+esc(id)+'\')">Eliminar</button>'+
      '<input id="v120Replace_'+esc(id)+'" class="v120-photo-input" type="file" accept="image/*" onchange="handleReplaceProgressPhotoV120(\''+esc(id)+'\',this)">'+
    '</div>';
  }

  const baseRenderPhotoGridV120=window.renderPhotoGrid;
  window.renderPhotoGrid=async function(targetId){
    await baseRenderPhotoGridV120.apply(this,arguments);
    const b=el(targetId);
    if(!b)return;

    const cards=[...b.querySelectorAll('.photo-slot,.photo-card')].filter(x=>x.querySelector('img'));
    if(!cards.length)return;

    const photos=trackingCache.photos.slice(0,36);
    const poseOrder=['front','side','back'];

    const groups={};
    photos.forEach(p=>{
      const key=(p.taken_on||'').slice(0,7)||'sin-fecha';
      (groups[key]??=[]).push(p);
    });

    let cardIndex=0;
    for(const key of Object.keys(groups).sort().reverse()){
      const list=groups[key].slice().sort((a,b)=>(b.taken_on||'').localeCompare(a.taken_on||''));
      const used=new Set();
      const ordered=[];
      for(const pose of poseOrder){
        const p=list.find(x=>x.pose===pose&&!used.has(x.id));
        if(p){used.add(p.id);ordered.push(p)}
      }
      ordered.push(...list.filter(p=>!used.has(p.id)));

      for(const p of ordered){
        const card=cards[cardIndex++];
        if(!card)break;
        if(card.querySelector('.v120-photo-actions'))continue;
        const meta=card.querySelector('.photo-slot-meta,.pad')||card;
        meta.insertAdjacentHTML('beforeend',photoActionsV120(p));
      }
    }
  };

  window.__fjzPhotoManageV120={
    version:'12.0',
    replace:true,
    delete:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)
p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8")
sw=re.sub(r"team-fjz-v\d+(?:-\d+)+","team-fjz-v12-0",sw)
swp.write_text(sw,encoding="utf-8")

print("TEAM FJZ V12.0 progress photo replace/delete:",len(html),"bytes")
