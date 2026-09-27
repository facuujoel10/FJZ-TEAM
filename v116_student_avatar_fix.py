import pathlib, re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v116StudentAvatarFixStyles">
.v116-avatar-box{display:flex;align-items:center;gap:12px;margin:10px 0 14px;padding:12px;border:1px solid var(--border);border-radius:14px;background:rgba(255,255,255,.02)}
.v116-avatar-preview{width:64px;height:64px;border-radius:50%;overflow:hidden;border:2px solid rgba(255,255,255,.12);background:#17171b;display:grid;place-items:center;font-weight:900;flex:0 0 auto}
.v116-avatar-preview img{width:100%;height:100%;object-fit:cover;display:block}
.v116-avatar-actions{display:flex;gap:7px;flex-wrap:wrap;margin-top:7px}
.v116-file{display:none}
</style>
"""

js=r"""
<script id="v116StudentAvatarFixRuntime">
(function(){
  let avatarBusyV116=false;

  async function myAvatarPathV116(){
    if(!currentUser||!supabaseClient)return '';
    const {data,error}=await supabaseClient.from('profiles')
      .select('avatar_url')
      .eq('id',currentUser.id)
      .maybeSingle();
    if(error)throw error;
    return data?.avatar_url||'';
  }

  async function myAvatarUrlV116(path){
    if(!path||!supabaseClient)return '';
    const {data,error}=await supabaseClient.storage.from('profile-photos').createSignedUrl(path,3600);
    if(error)return '';
    return data?.signedUrl||'';
  }

  async function avatarHtmlV116(){
    let path='',url='';
    try{
      path=await myAvatarPathV116();
      url=await myAvatarUrlV116(path);
    }catch(e){console.warn('avatar V11.6 load',e)}
    const initials=esc((student()?.name||'?').slice(0,2).toUpperCase());
    return '<div class="v116-avatar-box" id="v116AvatarBox">'+
      '<div class="v116-avatar-preview" id="v116AvatarPreview">'+(url?'<img src="'+url+'" alt="Foto de perfil">':initials)+'</div>'+
      '<div style="min-width:0"><strong>Foto de perfil</strong><div class="muted tiny">La vas a ver vos y también tu coach.</div>'+
      '<div class="v116-avatar-actions">'+
        '<button class="btn small" type="button" onclick="document.getElementById(\'v116AvatarInput\').click()">Elegir foto</button>'+
        (path?'<button class="btn ghost small" type="button" onclick="removeMyAvatarV116()">Quitar foto</button>':'')+
        '<input id="v116AvatarInput" class="v116-file" type="file" accept="image/jpeg,image/png,image/webp,image/heic,image/heif,image/*" onchange="uploadMyAvatarV116(this)">'+
      '</div><div id="v116AvatarStatus" class="muted micro" style="margin-top:6px"></div></div></div>';
  }

  async function injectAvatarV116(){
    if(currentProfile?.role!=='student'||mode!=='student'||studentTab!=='home')return;
    const card=el('v115StudentProfileCard');
    if(!card||el('v116AvatarBox'))return;
    const holder=document.createElement('div');
    holder.innerHTML=await avatarHtmlV116();
    const node=holder.firstElementChild;
    if(node)card.insertBefore(node,card.children[1]||null);
  }

  window.uploadMyAvatarV116=async function(input){
    if(avatarBusyV116)return;
    const file=input?.files?.[0];
    if(!file)return;

    if(file.size>5*1024*1024){
      toast('La foto debe pesar menos de 5 MB');
      input.value='';
      return;
    }
    if(file.type&&!['image/jpeg','image/png','image/webp','image/heic','image/heif'].includes(file.type)){
      toast('Formato no compatible. Usá JPG, PNG, WebP o HEIC.');
      input.value='';
      return;
    }

    avatarBusyV116=true;
    const status=el('v116AvatarStatus');
    if(status)status.textContent='Subiendo foto…';

    try{
      const oldPath=await myAvatarPathV116();
      const rawExt=(file.name.split('.').pop()||'jpg').toLowerCase().replace(/[^a-z0-9]/g,'');
      const ext=['jpg','jpeg','png','webp','heic','heif'].includes(rawExt)?rawExt:'jpg';
      const path=currentUser.id+'/avatar-'+Date.now()+'.'+ext;

      const {error:uploadError}=await supabaseClient.storage
        .from('profile-photos')
        .upload(path,file,{upsert:false,contentType:file.type||'image/jpeg',cacheControl:'3600'});
      if(uploadError)throw uploadError;

      const {data:profile,error:profileError}=await supabaseClient.from('profiles')
        .update({avatar_url:path})
        .eq('id',currentUser.id)
        .select('id,full_name,role,avatar_url')
        .single();
      if(profileError){
        try{await supabaseClient.storage.from('profile-photos').remove([path])}catch(_e){}
        throw profileError;
      }

      currentProfile={...(currentProfile||{}),...profile};
      try{
        if(typeof avatarPathCacheV70!=='undefined')avatarPathCacheV70.set(currentUser.id,path);
        if(typeof avatarSignedCacheV70!=='undefined')avatarSignedCacheV70.clear();
      }catch(_e){}

      if(oldPath&&oldPath!==path){
        try{await supabaseClient.storage.from('profile-photos').remove([oldPath])}catch(_e){}
      }

      const url=await myAvatarUrlV116(path);
      const preview=el('v116AvatarPreview');
      if(preview)preview.innerHTML=url?'<img src="'+url+'" alt="Foto de perfil">':esc((student()?.name||'?').slice(0,2).toUpperCase());
      if(status)status.textContent='Foto actualizada correctamente.';
      input.value='';
      toast('Foto de perfil actualizada');

      setTimeout(()=>render(),350);
    }catch(e){
      console.error('V11.6 avatar upload',e);
      if(status)status.textContent='No se pudo subir la foto.';
      toast(cloudErr(e));
      input.value='';
    }finally{
      avatarBusyV116=false;
    }
  };

  window.removeMyAvatarV116=async function(){
    if(avatarBusyV116)return;
    avatarBusyV116=true;
    const status=el('v116AvatarStatus');
    if(status)status.textContent='Quitando foto…';
    try{
      const oldPath=await myAvatarPathV116();
      const {data:profile,error}=await supabaseClient.from('profiles')
        .update({avatar_url:null})
        .eq('id',currentUser.id)
        .select('id,full_name,role,avatar_url')
        .single();
      if(error)throw error;
      currentProfile={...(currentProfile||{}),...profile};
      if(oldPath){try{await supabaseClient.storage.from('profile-photos').remove([oldPath])}catch(_e){}}
      try{
        if(typeof avatarPathCacheV70!=='undefined')avatarPathCacheV70.set(currentUser.id,'');
        if(typeof avatarSignedCacheV70!=='undefined')avatarSignedCacheV70.clear();
      }catch(_e){}
      toast('Foto eliminada');
      render();
    }catch(e){
      if(status)status.textContent='No se pudo quitar la foto.';
      toast(cloudErr(e));
    }finally{
      avatarBusyV116=false;
    }
  };

  const baseRenderV116=window.render;
  window.render=function(){
    const out=baseRenderV116.apply(this,arguments);
    if(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'){
      setTimeout(injectAvatarV116,120);
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
sw=re.sub(r"team-fjz-v\d+(?:-\d+)+","team-fjz-v11-6",sw)
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V11.6 student avatar fix:",len(html),"bytes")
