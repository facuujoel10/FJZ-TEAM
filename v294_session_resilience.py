import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "intervals":len(re.findall(r"setInterval\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

before=metrics(html)

for marker in [
    'meta name="fjz-password-recovery-hardening" content="20.93"',
    "persistSession:true",
    "autoRefreshToken:true",
    "detectSessionInUrl:true",
    "handleSessionV641",
    "async function logoutCloud()",
]:
    if marker not in html:
        raise RuntimeError("V20.94 prerequisite missing "+marker)

old_cdn="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm"
new_cdn="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.118.0/+esm"
if html.count(old_cdn)!=1:
    raise RuntimeError("V20.94 expected one unpinned Supabase import")
html=html.replace(old_cdn,new_cdn,1)

storage_old="mod.createClient(c.url,c.key,{auth:{persistSession:true,autoRefreshToken:true,detectSessionInUrl:true}})"
storage_new="mod.createClient(c.url,c.key,{auth:{persistSession:true,autoRefreshToken:true,detectSessionInUrl:true,storageKey:'sb-cujipwacwwpejhqjhnkr-auth-token'}})"
if html.count(storage_old)!=1:
    raise RuntimeError("V20.94 auth storage anchor mismatch: "+str(html.count(storage_old)))
html=html.replace(storage_old,storage_new,1)

old_logout="async function logoutCloud(){if(supabaseClient)await supabaseClient.auth.signOut();currentUser=null;currentProfile=null;linkedAthleteId=null;cloudAthletes=new Map();showAuthGate()}"
new_logout="async function logoutCloud(){window.__fjzIntentionalLogoutV294=true;try{if(supabaseClient)await supabaseClient.auth.signOut({scope:'local'})}catch(e){console.warn('TEAM FJZ local logout error',e)}currentUser=null;currentProfile=null;linkedAthleteId=null;cloudAthletes=new Map();window.__fjzIntentionalLogoutV294=false;showAuthGate()}"
if html.count(old_logout)!=1:
    raise RuntimeError("V20.94 logout anchor mismatch")
html=html.replace(old_logout,new_logout,1)

old_signedout="if(event==='SIGNED_OUT'){currentUser=null;currentProfile=null;if(!window.__fjzRecoveryModeV293)showAuthGate()}else if(event==='SIGNED_IN'&&session?.user&&!currentUser&&!window.__fjzRecoveryModeV293)"
new_signedout="if(event==='SIGNED_OUT'){if(window.__fjzIntentionalLogoutV294){currentUser=null;currentProfile=null;if(!window.__fjzRecoveryModeV293)showAuthGate();return}if(!window.__fjzRecoveryModeV293)queueMicrotask(()=>{if(typeof recoverUnexpectedSignedOutV294==='function')recoverUnexpectedSignedOutV294();else showAuthGate()});return}else if(event==='SIGNED_IN'&&session?.user&&!currentUser&&!window.__fjzRecoveryModeV293)"
if html.count(old_signedout)!=1:
    raise RuntimeError("V20.94 SIGNED_OUT anchor mismatch")
html=html.replace(old_signedout,new_signedout,1)

runtime=r"""
// ===== TEAM FJZ V20.94 · AUTH / SESSION RESILIENCE =====

const FJZ_AUTH_STORAGE_KEY_V298='sb-cujipwacwwpejhqjhnkr-auth-token';
function isStaleAuthErrorV298(e){
  const msg=String(e?.message||e?.error_description||e?.code||e||'').toLowerCase();
  return msg.includes('refresh token not found')||
    msg.includes('invalid refresh token')||
    msg.includes('refresh_token_not_found')||
    msg.includes('session_not_found')||
    msg.includes('authsessionmissing');
}
function clearStaleAuthStorageV298(){
  try{localStorage.removeItem(FJZ_AUTH_STORAGE_KEY_V298)}catch(_e){}
  currentUser=null;currentProfile=null;linkedAthleteId=null;
}
function showFreshLoginAfterStaleSessionV298(){
  clearStaleAuthStorageV298();
  setCloudStatus('','Nube');
  showAuthGate('login','La sesión de este dispositivo venció o quedó desactualizada. Ingresá nuevamente con tu email y contraseña. Tus datos siguen guardados.')
}
function showSessionRecoveryV294(message){
  message=message||'Tu sesión sigue activa, pero hubo un problema temporal al cargar los datos.';
  showGate();
  const card=authCard();
  if(!card)return;
  card.innerHTML='<div class="auth-brand"><img class="auth-logo" src="'+document.querySelector('.brand img').src+'" alt="TEAM FJZ"><div><h2>Reconectando</h2><div class="muted tiny">TEAM FJZ CLOUD</div></div></div>'+
    '<div class="auth-grid"><div class="card v294-session-note"><strong>Tu cuenta sigue conectada</strong><div class="muted tiny" style="margin-top:5px">'+esc(message)+'</div></div>'+
    '<button class="btn primary" onclick="retryActiveSessionV294()">Reintentar conexión</button>'+
    '<button class="btn ghost" onclick="logoutCloud()">Cerrar sesión en este dispositivo</button></div>';
}
async function retryActiveSessionV294(){
  if(!supabaseClient){bootV4(true);return}
  setCloudStatus('syncing','Reconectando');
  try{
    const {data,error}=await supabaseClient.auth.getSession();
    if(error)throw error;
    if(data&&data.session){await handleSessionV294(data.session);return}
    currentUser=null;currentProfile=null;
    showAuthGate('login','Tu sesión terminó. Ingresá nuevamente.')
  }catch(e){
    console.error('TEAM FJZ session retry error',e);
    if(isStaleAuthErrorV298(e)){showFreshLoginAfterStaleSessionV298();return}
    showSessionRecoveryV294('No pudimos verificar la sesión todavía. Revisá tu conexión y volvé a intentar.')
  }
}
async function recoverUnexpectedSignedOutV294(){
  if(window.__fjzRecoveryModeV293)return;
  let authError=null;
  try{
    const {data,error}=await supabaseClient.auth.getSession();
    authError=error||null;
    if(!error&&data&&data.session){
      currentUser=data.session.user;
      await handleSessionV294(data.session);
      return
    }
  }catch(e){
    authError=e;
    console.warn('TEAM FJZ auth state verification error',e)
  }
  if(isStaleAuthErrorV298(authError)){showFreshLoginAfterStaleSessionV298();return}
  currentUser=null;currentProfile=null;linkedAthleteId=null;
  showAuthGate('login','Tu sesión terminó. Ingresá nuevamente.')
}
async function handleSessionV294(session){
  if(!session||!session.user){showAuthGate();return}
  currentUser=session.user;
  setCloudStatus('syncing','Conectando');
  try{
    currentProfile=await fetchProfile();
    if(currentProfile.role==='coach'){
      mode='coach';
      const result=await loadCoachCloud();
      hideGate();
      try{render()}catch(uiErr){
        console.error('TEAM FJZ render error',uiErr);
        setCloudStatus('error','Vista con error');
        toast('La sesión inició, pero hubo un error al dibujar una sección.')
      }
      if(result==='empty')showCloudBootstrap()
    }else{
      mode='student';
      const linked=await loadStudentCloud();
      if(!linked){showClaimGate();return}
      hideGate();
      try{render()}catch(uiErr){
        console.error('TEAM FJZ render error',uiErr);
        setCloudStatus('error','Vista con error');
        toast('La sesión inició, pero hubo un error al dibujar una sección.')
      }
    }
  }catch(coreErr){
    console.error('TEAM FJZ session data load error',coreErr);
    setCloudStatus('error','Conexión inestable');
    let active=null;
    let probeError=null;
    try{
      const probe=await supabaseClient.auth.getSession();
      probeError=probe.error||null;
      if(!probe.error)active=probe.data&&probe.data.session?probe.data.session:null
    }catch(_e){probeError=_e}
    if(isStaleAuthErrorV298(probeError)){showFreshLoginAfterStaleSessionV298();return}
    if(active&&active.user){
      currentUser=active.user;
      showSessionRecoveryV294('La autenticación fue correcta, pero falló una carga de datos. No hace falta volver a escribir la contraseña.');
      return
    }
    currentUser=null;currentProfile=null;
    showAuthGate('login','Tu sesión terminó. Ingresá nuevamente.');
    return
  }
  try{setupRealtime()}catch(rtErr){console.error('TEAM FJZ realtime error',rtErr)}
  setCloudStatus('online','En nube')
}
handleSession=handleSessionV294;

loginCloud=async function(){
  const email=(el('authEmail')&&el('authEmail').value?el('authEmail').value:'').trim().toLowerCase();
  const password=el('authPass')?el('authPass').value:'';
  if(!email||!password){setAuthMsg('Completá email y contraseña.');return}
  const btn=[...document.querySelectorAll('#authCard .btn.primary')].find(b=>b.textContent.includes('Ingresar'));
  if(btn)btn.disabled=true;
  setAuthMsg('Ingresando...',true);
  try{
    const {data,error}=await supabaseClient.auth.signInWithPassword({email,password});
    if(error){setAuthMsg(cloudErr(error));return}
    if(!data||!data.session){setAuthMsg('No se pudo iniciar la sesión. Probá nuevamente.');return}
    await handleSessionV294(data.session)
  }catch(e){
    setAuthMsg(cloudErr(e))
  }finally{
    if(btn)btn.disabled=false
  }
};

bootV4=async function(force){
  const cfg=cloudConfig();
  if(!cfg){showSetupGate();setCloudStatus('', 'Local');return}
  showGate();
  authCard().innerHTML='<div class="auth-brand"><img class="auth-logo" src="'+document.querySelector('.brand img').src+'" alt="TEAM FJZ"><div><h2>TEAM FJZ</h2><div class="muted tiny">CONECTANDO CON LA NUBE</div></div></div><p>Cargando cuenta y sincronizando datos…</p>';
  try{
    await initSupabase();
    const {data,error}=await supabaseClient.auth.getSession();
    if(error)throw error;
    if(data&&data.session)await handleSessionV294(data.session);
    else showAuthGate()
  }catch(e){
    console.error('TEAM FJZ boot/session error',e);
    if(isStaleAuthErrorV298(e)){showFreshLoginAfterStaleSessionV298();return}
    setCloudStatus('error','Conexión inestable');
    showGate();
    authCard().innerHTML='<div class="auth-brand"><img class="auth-logo" src="'+document.querySelector('.brand img').src+'" alt="TEAM FJZ"><div><h2>No pudimos conectar</h2><div class="muted tiny">TEAM FJZ CLOUD</div></div></div>'+
      '<div class="auth-grid"><div class="card v294-session-note"><div class="muted tiny">No borramos tu sesión ni tus datos. Puede ser un problema temporal de conexión.</div></div>'+
      '<button class="btn primary" onclick="bootV4(true)">Reintentar</button>'+
      '<button class="btn ghost" onclick="showAuthGate(\'login\',\'Ingresá nuevamente si tu sesión necesita renovarse.\')">Ir al login</button></div>'
  }
};

Object.assign(window,{retryActiveSessionV294,recoverUnexpectedSignedOutV294});
"""

anchor="bootV4();"
if html.count(anchor)!=1:
    raise RuntimeError("V20.94 boot anchor mismatch")
html=html.replace(anchor,runtime+"\n"+anchor,1)

css=r"""
/* TEAM FJZ · V20.94 SESSION RESILIENCE */
.v294-session-note{
  padding:13px!important;
  border-color:rgba(90,167,255,.28)!important;
  background:rgba(90,167,255,.055)!important;
}
"""
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.94 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-session-resilience" content="20.94">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V20.94 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-session-resilience" content="20.94"',
    "@supabase/supabase-js@2.118.0/+esm",
    "signOut({scope:'local'})",
    "handleSessionV294",
    "retryActiveSessionV294",
    "recoverUnexpectedSignedOutV294",
    "La autenticación fue correcta, pero falló una carga de datos",
    "No borramos tu sesión ni tus datos",
    "FJZ_AUTH_STORAGE_KEY_V298",
    "showFreshLoginAfterStaleSessionV298",
    "refresh_token_not_found",
]:
    if marker not in html:
        raise RuntimeError("V20.94 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.94 auth/session resilience")
print("V20.94 BEFORE:",before)
print("V20.94 AFTER:",after)
