import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

def edit_script(doc,script_id,transform):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.70 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.70 no script change "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-coach-cockpit-music-removal" content="20.68"',
    'meta name="fjz-routine-library-preparation" content="20.69"',
    "stableExerciseModalHeader:true",
    "mobileLibraryGeometry:true",
    "async function avatarResultV268(userId,name)",
]:
    if marker not in html:
        raise RuntimeError("V20.70 missing prerequisite: "+marker)

def patch_avatar(body):
    old=r"""  async function avatarResultV268(userId,name){
    if(window.__fjzStagingLocal?.syntheticDataOnly){
      return {demo:true,url:'',state:'demo'};
    }
    if(!userId)return {demo:false,url:'',state:'unlinked'};
    if(!supabaseClient)return {demo:false,url:'',state:'offline'};
    try{
      const {data,error}=await supabaseClient.from('profiles').select('id,avatar_url').eq('id',userId).maybeSingle();
      if(error)throw error;
      const path=data?.avatar_url||'';
      try{avatarPathCacheV70?.set?.(userId,path)}catch(_e){}
      if(!path)return {demo:false,url:'',state:'empty'};
      const {data:signed,error:signErr}=await supabaseClient.storage.from('profile-photos').createSignedUrl(path,3600);
      if(signErr)throw signErr;
      return {demo:false,url:signed?.signedUrl||'',state:signed?.signedUrl?'loaded':'empty'};
    }catch(e){
      console.warn('TEAM FJZ V20.68 avatar',e);
      return {demo:false,url:'',state:'error'};
    }
  }
"""
    new=r"""  function cachedAvatarPathV270(userId){
    try{return avatarPathCacheV70?.get?.(userId)||''}catch(_e){return ''}
  }

  async function signedAvatarV270(path,state='loaded'){
    if(!path)return {demo:false,url:'',state:'empty'};
    const {data:signed,error}=await supabaseClient.storage.from('profile-photos').createSignedUrl(path,3600);
    if(error)throw error;
    const url=signed?.signedUrl||'';
    return {demo:false,url,state:url?state:'empty'};
  }

  async function avatarResultV268(userId,name){
    if(window.__fjzStagingLocal?.syntheticDataOnly){
      return {demo:true,url:'',state:'demo'};
    }
    if(!userId)return {demo:false,url:'',state:'unlinked'};
    if(!supabaseClient)return {demo:false,url:'',state:'offline'};

    const cached=cachedAvatarPathV270(userId);
    try{
      const {data,error}=await supabaseClient.from('profiles').select('id,avatar_url').eq('id',userId).maybeSingle();
      if(error)throw error;
      const path=data?.avatar_url||cached||'';
      try{avatarPathCacheV70?.set?.(userId,path)}catch(_e){}
      if(!path)return {demo:false,url:'',state:'empty'};
      return await signedAvatarV270(path,'loaded');
    }catch(e){
      if(cached){
        try{
          const fallback=await signedAvatarV270(cached,'loaded-cache');
          if(fallback.url){
            console.warn('TEAM FJZ V20.70 avatar profile lookup fallback',e);
            return fallback;
          }
        }catch(_fallbackError){}
      }
      console.warn('TEAM FJZ V20.70 avatar',e);
      return {demo:false,url:'',state:'error'};
    }
  }
"""
    if body.count(old)!=1:
        raise RuntimeError("V20.70 avatar loader anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)
    body=body.replace(
        "if(result?.state==='loaded')return 'Foto sincronizada';",
        "if(result?.state==='loaded'||result?.state==='loaded-cache')return 'Foto sincronizada';",
        1
    )
    body=body.replace(
        "return 'Sin foto cargada';",
        "return 'Sin foto cargada · se muestran iniciales';",
        1
    )
    marker="""    studentAvatarProductionLinkedProfile:true,
    stagingAvatarClearlyDemo:true,
"""
    repl="""    studentAvatarProductionLinkedProfile:true,
    avatarCachedPathFallbackV270:true,
    avatarEmptyStateExplicitV270:true,
    stagingAvatarClearlyDemo:true,
"""
    if body.count(marker)!=1:
        raise RuntimeError("V20.70 avatar marker anchor mismatch")
    return body.replace(marker,repl,1)

html=edit_script(html,"v268CoachCockpitAvatarRuntime",patch_avatar)

css=r"""
/* =========================================================
   TEAM FJZ · V20.70 MOBILE EDGE GEOMETRY + AVATAR RESILIENCE
   360/390px authority for modal/library/preparation surfaces.
   ========================================================= */
.modal-wrap,
.modal,
.modal *,
.v269-library-shell,
.v269-library-shell *,
.v269-exercise-modal,
.v269-exercise-modal *{
  box-sizing:border-box;
}
.modal-wrap{
  width:100%;
  max-width:100%;
  overflow-x:hidden!important;
}
.v269-library-shell,
.v269-exercise-modal{
  width:100%;
  max-width:100%;
  overflow-x:hidden;
}
.v269-title-block,
.v269-library-copy,
.v269-form-head-left,
.v269-prep-col,
.v269-prep-head>div{
  min-width:0!important;
}
.v269-title-block h3,
.v269-title-block small,
.v269-library-copy h4,
.v269-library-copy p,
.v269-library-copy small,
.v269-back-btn,
.v269-prep-head strong{
  overflow-wrap:anywhere;
  word-break:normal;
}
.v269-library-shell input,
.v269-library-shell select,
.v269-exercise-modal input,
.v269-exercise-modal select,
.v269-exercise-modal textarea{
  min-width:0!important;
  max-width:100%!important;
  width:100%;
}

@media(max-width:430px){
  .modal-wrap{
    padding-left:max(6px,env(safe-area-inset-left))!important;
    padding-right:max(6px,env(safe-area-inset-right))!important;
    padding-top:max(6px,env(safe-area-inset-top))!important;
    padding-bottom:max(6px,env(safe-area-inset-bottom))!important;
  }
  .modal{
    width:100%!important;
    max-width:100%!important;
    max-height:calc(100dvh - 12px - env(safe-area-inset-top) - env(safe-area-inset-bottom))!important;
    margin:0!important;
    padding:12px!important;
    overflow-x:hidden!important;
  }
  .v269-modal-head,
  .v269-exercise-form-head{
    grid-template-columns:minmax(0,1fr) 34px!important;
    gap:8px!important;
    width:100%!important;
    max-width:100%!important;
    align-items:start!important;
  }
  .v269-close{
    width:34px!important;
    min-width:34px!important;
    height:34px!important;
    min-height:34px!important;
  }
  .v269-form-head-left{
    display:grid!important;
    grid-template-columns:minmax(0,1fr)!important;
    gap:7px!important;
    width:100%!important;
  }
  .v269-back-btn{
    width:100%!important;
    min-width:0!important;
    max-width:100%!important;
    min-height:36px!important;
    padding:8px 10px!important;
    display:flex!important;
    align-items:center!important;
    justify-content:flex-start!important;
    text-align:left!important;
    white-space:normal!important;
  }
  .v269-search-row,
  .v269-library-filters,
  .v269-library-grid,
  .v269-prep-editor{
    width:100%!important;
    max-width:100%!important;
    min-width:0!important;
    grid-template-columns:minmax(0,1fr)!important;
  }
  .v269-library-item{
    width:100%!important;
    max-width:100%!important;
    min-width:0!important;
    grid-template-columns:minmax(0,1fr)!important;
    align-items:stretch!important;
    padding:10px!important;
  }
  .v269-library-item>.btn,
  .v269-custom-btn{
    width:100%!important;
    min-width:0!important;
    max-width:100%!important;
  }
  .v269-prep-head{
    display:grid!important;
    grid-template-columns:minmax(0,1fr)!important;
    gap:8px!important;
  }
  .v269-prep-head>.btn{
    width:100%!important;
    min-width:0!important;
  }
  .v269-library-shell input,
  .v269-library-shell select,
  .v269-exercise-modal input,
  .v269-exercise-modal select,
  .v269-exercise-modal textarea{
    font-size:16px!important;
  }
}

@media(max-width:390px){
  .modal{padding:10px!important;border-radius:13px!important}
  .v269-title-block h3{font-size:15px!important;line-height:1.2!important}
  .v269-title-block small{font-size:7.5px!important}
  .v269-library-item{gap:8px!important;padding:9px!important}
  .v269-prep-col{padding:9px!important}
  .v269-prep-chip{max-width:100%!important}
}

@media(max-width:360px){
  .modal-wrap{
    padding-left:max(4px,env(safe-area-inset-left))!important;
    padding-right:max(4px,env(safe-area-inset-right))!important;
  }
  .modal{padding:9px!important}
  .v269-modal-head,
  .v269-exercise-form-head{gap:6px!important}
  .v269-title-block h3{font-size:14px!important}
  .v269-back-btn{padding:7px 9px!important}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.70 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-mobile-edge-avatar-resilience" content="20.70">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.70 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-mobile-edge-avatar-resilience" content="20.70"',
    "avatarCachedPathFallbackV270:true",
    "avatarEmptyStateExplicitV270:true",
    "TEAM FJZ · V20.70 MOBILE EDGE GEOMETRY + AVATAR RESILIENCE",
    "@media(max-width:390px)",
    "@media(max-width:360px)",
    ".v269-back-btn",
    "box-sizing:border-box",
]:
    if marker not in html:
        raise RuntimeError("V20.70 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.70 mobile edge geometry + avatar resilience")
print("V20.70 BEFORE:",before)
print("V20.70 AFTER:",after)
print("V20.70 360/390 modal geometry hardened; avatar loader now has cached-path fallback and explicit no-photo state")
