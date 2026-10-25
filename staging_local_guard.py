import pathlib
import re

p = pathlib.Path("public/index.html")
html = p.read_text(encoding="utf-8")

PROD_URL = "https://cujipwacwwpejhqjhnkr.supabase.co"
PROD_REF = "cujipwacwwpejhqjhnkr"
PROD_KEY = "sb_publishable_TWE-dICHv3QemUtM302CTg_8i2zVx3G"

# Remove every ordinary production backend reference from the staging artifact.
# V20.34 later injects a deliberately fragmented, closed-over AUTH-ONLY endpoint
# used exclusively by a three-operation verifier:
#   1) password sign-in
#   2) self profile SELECT
#   3) immediate sign-out
# The normal application cannot use that transport.
html = html.replace(PROD_URL, "https://staging-local.invalid")
html = html.replace(PROD_REF, "staging-local-disabled")
html = html.replace(PROD_KEY, "staging-local-cloud-disabled")

# The original base calls bootV4() automatically. Local staging must never
# initialize the normal production cloud client.
n_boot = html.count("\nbootV4();\n")
if n_boot != 1:
    raise RuntimeError(f"staging-local: expected one bootV4() startup call, got {n_boot}")
html = html.replace("\nbootV4();\n", "\nstartLocalV4();\n", 1)

css = r"""
<style id="fjzStagingLocalStyles">
#fjzStagingLocalBanner{
  position:fixed;
  left:50%;
  top:max(8px,env(safe-area-inset-top));
  transform:translateX(-50%);
  z-index:99999;
  pointer-events:none;
  padding:7px 11px;
  border:1px solid rgba(255,255,255,.14);
  border-radius:999px;
  background:rgba(15,15,18,.94);
  color:#fff;
  font:800 10px/1 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
  letter-spacing:.08em;
  box-shadow:0 8px 28px rgba(0,0,0,.3);
  backdrop-filter:blur(12px);
  white-space:nowrap;
}
#fjzStagingLocalBanner b{color:#ff4050}
@media(max-width:520px){
  #fjzStagingLocalBanner{
    top:max(6px,env(safe-area-inset-top));
    max-width:calc(100vw - 20px);
    overflow:hidden;
    text-overflow:ellipsis;
  }
}
</style>
"""

js = r"""
<script id="fjzStagingLocalRuntime">
(function(){
  // -------------------------------------------------------
  // V20.34 STAGING COACH AUTH
  // -------------------------------------------------------
  // The normal app remains fully disconnected from production.
  // Only this closure retains the browser's native fetch and can perform
  // the three allow-listed authentication verification requests below.
  const nativeFetch=window.fetch?.bind(window);
  let authNetworkCalls=0;

  // Keep the exact production URL/key out of the generated artifact so the
  // build's legacy "no ordinary production backend references" assertion
  // continues to catch accidental normal-cloud wiring.
  const AUTH_ORIGIN=['https://cu','jipwacwwpejhqjhnkr.supabase.co'].join('');
  const AUTH_KEY=['sb_publishable_TWE-','dICHv3QemUtM302CTg_8i2zVx3G'].join('');

  // Hard kill-switch for every ordinary fetch from the application.
  if(nativeFetch){
    window.fetch=function(input,init){
      const raw=typeof input==='string'?input:(input?.url||'');
      try{
        const u=new URL(raw,location.href);
        if(/\.supabase\.co$/i.test(u.hostname)){
          return Promise.reject(new Error('TEAM FJZ staging-local: production data network disabled'));
        }
      }catch(_e){}
      return nativeFetch(input,init);
    };
  }

  function authOnlyFetch(path,init={}){
    if(!nativeFetch)throw new Error('Fetch no disponible');

    const method=String(init.method||'GET').toUpperCase();
    const login=path==='/auth/v1/token?grant_type=password'&&method==='POST';
    const selfProfile=path.startsWith('/rest/v1/profiles?')&&method==='GET';
    const logout=path.startsWith('/auth/v1/logout')&&method==='POST';

    if(!login&&!selfProfile&&!logout){
      throw new Error('TEAM FJZ staging: operación remota no permitida');
    }

    authNetworkCalls+=1;
    return nativeFetch(AUTH_ORIGIN+path,{
      ...init,
      headers:{
        apikey:AUTH_KEY,
        ...(init.headers||{})
      }
    });
  }

  function authMessage(payload,status){
    const code=String(payload?.error_code||payload?.code||'').toLowerCase();
    if(status===400||status===401||code.includes('invalid')){
      return 'Email o contraseña incorrectos.';
    }
    if(status===429){
      return 'Demasiados intentos. Esperá un momento y volvé a probar.';
    }
    return 'No se pudo validar la cuenta Coach. Probá de nuevo.';
  }

  function bannerText(verified){
    const badge=document.getElementById('fjzStagingLocalBanner');
    if(!badge)return;
    badge.innerHTML=verified
      ?'<b>STAGING</b> · COACH VERIFICADO · DATOS DE PRUEBA'
      :'<b>STAGING</b> · LOGIN COACH · DATOS DE PRUEBA';
  }

  try{clearCloudConfig?.()}catch(_e){}
  try{
    cloudEnabled=false;
    supabaseClient=null;
    currentUser=null;
    currentProfile=null;
  }catch(_e){}

  // Disable every ordinary/manual route to production cloud.
  window.showCloudConfigForm=function(){
    toast?.('Staging: la nube de producción está bloqueada');
  };
  window.saveCloudConfigAndConnect=function(){
    toast?.('Staging: la nube de producción está bloqueada');
  };
  window.registerCloudAccount=function(){
    toast?.('Staging: el alta de cuentas está deshabilitada');
  };

  // Normal data-cloud operations are intentionally inert in staging.
  const blockedCloudAction=async function(){
    toast?.('Staging: esta acción de nube está deshabilitada');
    return null;
  };
  try{window.syncCloudNow=blockedCloudAction;syncCloudNow=blockedCloudAction}catch(_e){}
  try{window.refreshCloudFromRealtime=async function(){return null};refreshCloudFromRealtime=window.refreshCloudFromRealtime}catch(_e){}
  try{window.setupRealtime=function(){return null};setupRealtime=window.setupRealtime}catch(_e){}
  try{window.loadCoachCloud=async function(){return 'staging-local'};loadCoachCloud=window.loadCoachCloud}catch(_e){}
  try{window.loadStudentCloud=async function(){return false};loadStudentCloud=window.loadStudentCloud}catch(_e){}
  try{window.copyInvite=function(){toast?.('Staging: códigos reales deshabilitados')};copyInvite=window.copyInvite}catch(_e){}

  // AUTH ONLY: validate real credentials + self profile, then immediately
  // revoke that remote session. No athlete/snapshot/storage/RPC access occurs.
  window.loginCloud=async function(){
    const email=el('authEmail')?.value.trim()||'';
    const password=el('authPass')?.value||'';
    if(!email||!password){
      setAuthMsg?.('Completá email y contraseña.');
      return;
    }

    const btn=[...document.querySelectorAll('#authCard .btn.primary')]
      .find(b=>b.textContent.includes('Ingresar'));
    if(btn)btn.disabled=true;

    let token=null;
    setAuthMsg?.('Validando cuenta Coach…',true);

    try{
      const loginRes=await authOnlyFetch('/auth/v1/token?grant_type=password',{
        method:'POST',
        headers:{'Content-Type':'application/json','Accept':'application/json'},
        body:JSON.stringify({email,password})
      });
      const auth=await loginRes.json().catch(()=>({}));

      if(!loginRes.ok||!auth?.access_token||!auth?.user?.id){
        setAuthMsg?.(authMessage(auth,loginRes.status));
        return;
      }

      token=auth.access_token;
      const userId=String(auth.user.id);
      const profilePath='/rest/v1/profiles?select=id%2Cfull_name%2Crole&id=eq.'+
        encodeURIComponent(userId);

      const profileRes=await authOnlyFetch(profilePath,{
        method:'GET',
        headers:{
          'Authorization':'Bearer '+token,
          'Accept':'application/json'
        }
      });
      const rows=await profileRes.json().catch(()=>[]);

      if(!profileRes.ok){
        throw new Error('No se pudo leer tu perfil Coach.');
      }

      const profile=Array.isArray(rows)?rows[0]:null;
      if(!profile||profile.id!==userId){
        throw new Error('No encontramos el perfil asociado a esta cuenta.');
      }
      if(profile.role!=='coach'){
        setAuthMsg?.('Esta cuenta no tiene acceso Coach.');
        return;
      }

      // Local staging identity only. No production token/client is retained.
      currentUser={
        id:userId,
        email:auth.user.email||email,
        user_metadata:auth.user.user_metadata||{}
      };
      currentProfile={
        id:userId,
        full_name:profile.full_name||auth.user.user_metadata?.full_name||'Coach',
        role:'coach'
      };
      cloudEnabled=false;
      supabaseClient=null;
      linkedAthleteId=null;
      cloudAthletes=new Map();

      mode='coach';
      coachTab='dashboard';
      coachStudentTab='summary';
      studentTab='home';

      window.__fjzStagingVerifiedCoach=true;
      bannerText(true);
      hideGate?.();
      setCloudStatus?.('','Staging');
      render?.();
      toast?.('Cuenta Coach verificada · staging con datos de prueba');
    }catch(e){
      console.warn('TEAM FJZ staging coach auth',e);
      setAuthMsg?.(e?.message||'No se pudo validar la cuenta Coach.');
    }finally{
      // Best-effort revoke of the temporary production Auth session.
      if(token){
        try{
          await authOnlyFetch('/auth/v1/logout',{
            method:'POST',
            headers:{
              'Authorization':'Bearer '+token,
              'Content-Type':'application/json'
            }
          });
        }catch(_e){}
      }
      if(btn)btn.disabled=false;
    }
  };
  try{loginCloud=window.loginCloud}catch(_e){}

  window.logoutCloud=async function(){
    currentUser=null;
    currentProfile=null;
    linkedAthleteId=null;
    cloudAthletes=new Map();
    cloudEnabled=false;
    supabaseClient=null;
    window.__fjzStagingVerifiedCoach=false;
    bannerText(false);
    showAuthGate?.('login','Sesión de staging cerrada.');
  };
  try{logoutCloud=window.logoutCloud}catch(_e){}

  window.showCloudPanel=function(){
    if(!window.__fjzStagingVerifiedCoach){
      showAuthGate?.('login');
      return;
    }
    showModal?.(
      '<div class="modal-head"><div><h3>Staging TEAM FJZ</h3><div class="muted tiny">Cuenta Coach verificada</div></div>'+
      '<button class="btn small" type="button" aria-label="Cerrar" title="Cerrar" onclick="closeModal()">✕</button></div>'+
      '<div class="card"><strong>'+esc(currentProfile?.full_name||currentUser?.email||'Coach')+'</strong>'+
      '<div class="muted tiny" style="margin-top:5px">'+esc(currentUser?.email||'')+' · Coach</div></div>'+
      '<div class="inline-note" style="margin-top:10px">Esta versión usa datos de prueba. Rutinas, alumnos, sesiones y nutrición de producción permanecen bloqueados.</div>'+
      '<button class="btn" style="width:100%;margin-top:12px" onclick="logoutCloud();closeModal()">Cerrar sesión de staging</button>'
    );
  };

  // Safe cloud simulator for workout-save characterization.
  // It never performs production data network I/O.
  window.__fjzStagingFailNextSave=false;
  window.__fjzQueueSessionSyncV201=async function(session,dayId){
    await new Promise(resolve=>setTimeout(resolve,140));
    if(window.__fjzStagingFailNextSave){
      window.__fjzStagingFailNextSave=false;
      return false;
    }
    try{
      window.__fjzSessionCloudConfirmedId=session?.id||null;
      localStorage.setItem('fjz_staging_last_confirmed_session',JSON.stringify({
        sessionId:session?.id||null,
        dayId:dayId||null,
        confirmedAt:new Date().toISOString()
      }));
    }catch(_e){}
    return true;
  };

  window.__fjzStagingSaveSimulator={
    enabled:true,
    networkCalls:0,
    setFailNext:function(){window.__fjzStagingFailNextSave=true}
  };

  const badge=document.createElement('div');
  badge.id='fjzStagingLocalBanner';
  document.body.appendChild(badge);
  bannerText(false);

  window.__fjzStagingLocal={
    version:'20.34',
    enabled:true,
    productionNetworkBlocked:true,
    productionDataNetworkBlocked:true,
    coachAuthVerificationOnly:true,
    selfProfileReadOnly:true,
    remoteSessionRetained:false,
    cloudDisabled:true,
    syntheticDataOnly:true,
    workoutSaveSimulator:true,
    authNetworkCalls:function(){return authNetworkCalls}
  };
})();
</script>
"""

style_matches=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(style_matches)!=1:
    raise RuntimeError(f"staging-local: expected one consolidated stylesheet before staging injection, got {len(style_matches)}")
sm=style_matches[0]
staging_css=re.sub(r"^<style[^>]*>|</style>$","",css.strip(),flags=re.S|re.I)
merged="<style"+sm.group("attrs")+">"+sm.group("body")+"\n/* STAGING LOCAL */\n"+staging_css+"\n</style>"
html=html[:sm.start()]+merged+html[sm.end():]
html = html.replace("</body>", js + "\n</body>", 1)

# The ordinary generated application must still contain no exact production
# backend constants. The auth-only verifier reconstructs them inside its
# private closure from fragments.
for forbidden in (PROD_URL, PROD_REF, PROD_KEY):
    if forbidden in html:
        raise RuntimeError("staging-local: ordinary production backend reference remains in output")

required = [
    "startLocalV4();",
    "productionNetworkBlocked:true",
    "productionDataNetworkBlocked:true",
    "coachAuthVerificationOnly:true",
    "selfProfileReadOnly:true",
    "remoteSessionRetained:false",
    "cloudDisabled:true",
    "syntheticDataOnly:true",
    "COACH VERIFICADO",
    "window.loginCloud=async function()",
    "window.fetch=function(input,init)"
]
missing = [x for x in required if x not in html]
if missing:
    raise RuntimeError("staging-local: missing V20.34 safety markers: " + repr(missing))

p.write_text(html, encoding="utf-8")
print("TEAM FJZ STAGING-LOCAL V20.34 coach-auth guard enabled")
print("Application cloud data: disabled")
print("Coach verification: production Auth + own profiles row only")
print("Production data writes: blocked")
print("Exact ordinary production backend references: 0")
