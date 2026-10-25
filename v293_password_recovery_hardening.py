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
    'meta name="fjz-single-coach-athlete-nav" content="20.92"',
    "resetPasswordForEmail",
    "PASSWORD_RECOVERY",
    "saveRecoveredPasswordV81",
    "detectSessionInUrl:true",
]:
    if marker not in html:
        raise RuntimeError("V20.93 prerequisite missing "+marker)

# Capture recovery in the first auth listener and stop normal session routing.
old="async function initSupabase(){const c=cloudConfig();if(!c?.url||!c?.key)throw new Error('Falta configurar Supabase.');const mod=await import('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm');supabaseClient=mod.createClient(c.url,c.key,{auth:{persistSession:true,autoRefreshToken:true,detectSessionInUrl:true}});cloudEnabled=true;supabaseClient.auth.onAuthStateChange((event,session)=>{if(event==='SIGNED_OUT'){currentUser=null;currentProfile=null;showAuthGate()}else if(event==='SIGNED_IN'&&session?.user&&!currentUser){setTimeout(()=>handleSession(session),0)}})}"
new="async function initSupabase(){const c=cloudConfig();if(!c?.url||!c?.key)throw new Error('Falta configurar Supabase.');let recovery=false,recoveryError='';try{const u=new URL(location.href),h=new URLSearchParams((location.hash||'').replace(/^#/,''));const type=u.searchParams.get('type')||h.get('type')||'';recovery=type==='recovery';recoveryError=u.searchParams.get('error_description')||h.get('error_description')||''}catch(_e){}window.__fjzRecoveryModeV293=recovery;window.__fjzRecoveryUrlErrorV293=recoveryError;const mod=await import('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm');supabaseClient=mod.createClient(c.url,c.key,{auth:{persistSession:true,autoRefreshToken:true,detectSessionInUrl:true}});cloudEnabled=true;supabaseClient.auth.onAuthStateChange((event,session)=>{if(event==='PASSWORD_RECOVERY'){window.__fjzRecoveryModeV293=true;if(session?.user)currentUser=session.user;setTimeout(()=>{try{showPasswordUpdateV81()}catch(_e){}},0);return}if(event==='SIGNED_OUT'){currentUser=null;currentProfile=null;if(!window.__fjzRecoveryModeV293)showAuthGate()}else if(event==='SIGNED_IN'&&session?.user&&!currentUser&&!window.__fjzRecoveryModeV293){setTimeout(()=>handleSession(session),0)}})}"
if html.count(old)!=1:
    raise RuntimeError("V20.93 initSupabase anchor mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

# Harden reset request.
pat=re.compile(r"async function requestPasswordResetV81\(\)\{.*?\n\}",re.S)
m=pat.search(html)
if not m:
    raise RuntimeError("V20.93 requestPasswordResetV81 not found")
replacement="""async function requestPasswordResetV81(){
  if(window.__fjzRecoverySendBusyV293)return;
  const input=el('authEmail');
  const email=String(input?.value||'').trim().toLowerCase();
  if(!email){setAuthMsg('Escribí tu email y después tocá recuperar contraseña.');return}
  if(input&&typeof input.checkValidity==='function'&&!input.checkValidity()){setAuthMsg('Revisá que el email esté bien escrito.');return}
  if(!supabaseClient){setAuthMsg('No se pudo conectar con el sistema de acceso.');return}
  const btn=el('v81ForgotPass');
  window.__fjzRecoverySendBusyV293=true;
  if(btn){btn.disabled=true;btn.textContent='Enviando...'}
  try{
    const options={};
    if(location.protocol==='http:'||location.protocol==='https:')options.redirectTo=location.origin+location.pathname;
    const {error}=await supabaseClient.auth.resetPasswordForEmail(email,options);
    if(error)throw error;
    setAuthMsg('Si ese email corresponde a una cuenta, te va a llegar un enlace para crear una nueva contraseña. Revisá también spam.',true)
  }catch(e){setAuthMsg(cloudErr(e))}
  finally{
    window.__fjzRecoverySendBusyV293=false;
    if(btn){btn.disabled=false;btn.textContent='¿Olvidaste tu contraseña?'}
  }
}"""
html=html[:m.start()]+replacement+html[m.end():]

# Strengthen password form without changing layout.
html=html.replace('id="v81NewPass" class="input" type="password" minlength="6"',
                  'id="v81NewPass" class="input" type="password" minlength="8" autocomplete="new-password" placeholder="Mínimo 8 caracteres"',1)
html=html.replace('id="v81NewPass2" class="input" type="password" minlength="6"',
                  'id="v81NewPass2" class="input" type="password" minlength="8" autocomplete="new-password" placeholder="Repetí la contraseña"',1)
html=html.replace('<button class="btn primary" onclick="saveRecoveredPasswordV81()">Guardar contraseña</button>',
                  '<button id="v293SaveRecoveredPass" class="btn primary" onclick="saveRecoveredPasswordV81()">Guardar contraseña</button>',1)

# Harden update and cleanup URL.
pat2=re.compile(r"async function saveRecoveredPasswordV81\(\)\{.*?\n\}",re.S)
m2=pat2.search(html)
if not m2:
    raise RuntimeError("V20.93 saveRecoveredPasswordV81 not found")
replacement2="""async function saveRecoveredPasswordV81(){
  if(window.__fjzRecoverySaveBusyV293)return;
  const a=el('v81NewPass')?.value||'',b=el('v81NewPass2')?.value||'';
  if(a.length<8){setAuthMsg('Usá al menos 8 caracteres.');return}
  if(a!==b){setAuthMsg('Las contraseñas no coinciden.');return}
  if(!supabaseClient){setAuthMsg('No se pudo conectar con el sistema de acceso.');return}
  const btn=el('v293SaveRecoveredPass');
  window.__fjzRecoverySaveBusyV293=true;
  if(btn){btn.disabled=true;btn.textContent='Guardando...'}
  try{
    const {error}=await supabaseClient.auth.updateUser({password:a});
    if(error)throw error;
    setAuthMsg('Contraseña actualizada correctamente. Entrando a tu cuenta...',true);
    window.__fjzRecoveryModeV293=false;
    window.__fjzRecoveryUrlErrorV293='';
    try{history.replaceState(null,'',location.origin+location.pathname)}catch(_e){}
    const {data}=await supabaseClient.auth.getSession();
    if(data?.session)setTimeout(()=>handleSession(data.session),450);
    else setTimeout(()=>showAuthGate('login','Contraseña actualizada. Ingresá con tu nueva contraseña.'),450)
  }catch(e){setAuthMsg(cloudErr(e))}
  finally{
    window.__fjzRecoverySaveBusyV293=false;
    if(btn){btn.disabled=false;btn.textContent='Guardar contraseña'}
  }
}"""
html=html[:m2.start()]+replacement2+html[m2.end():]

# Remove the late duplicate recovery listener; keep a deterministic fallback.
old_wrap="""const _initSupabaseV81Base=initSupabase;
initSupabase=async function(){
  await _initSupabaseV81Base();
  if(!window.__fjzV81RecoveryListener&&supabaseClient){
    window.__fjzV81RecoveryListener=true;
    supabaseClient.auth.onAuthStateChange((event)=>{
      if(event==='PASSWORD_RECOVERY')setTimeout(showPasswordUpdateV81,0)
    })
  }
};"""
new_wrap="""const _initSupabaseV81Base=initSupabase;
initSupabase=async function(){
  await _initSupabaseV81Base();
  if(window.__fjzRecoveryUrlErrorV293){
    window.__fjzRecoveryModeV293=false;
    setTimeout(()=>showAuthGate('login','El enlace de recuperación venció, ya fue usado o no es válido. Pedí uno nuevo.'),0);
    return
  }
  if(window.__fjzRecoveryModeV293)setTimeout(showPasswordUpdateV81,0)
};"""
if html.count(old_wrap)!=1:
    raise RuntimeError("V20.93 V81 recovery wrapper mismatch: "+str(html.count(old_wrap)))
html=html.replace(old_wrap,new_wrap,1)

css="""
/* TEAM FJZ · V20.93 PASSWORD RECOVERY HARDENING */
#v81ForgotPass:disabled,
#v293SaveRecoveredPass:disabled{
  opacity:.62!important;
  pointer-events:none!important;
}
"""
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.93 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-password-recovery-hardening" content="20.93">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V20.93 topology changed "+key+": "+repr({"before":before,"after":after}))

required=[
    'meta name="fjz-password-recovery-hardening" content="20.93"',
    "window.__fjzRecoveryModeV293",
    "event==='PASSWORD_RECOVERY'",
    "window.__fjzRecoverySendBusyV293",
    "window.__fjzRecoverySaveBusyV293",
    'minlength="8"',
    'autocomplete="new-password"',
    "El enlace de recuperación venció",
    "history.replaceState",
    "Si ese email corresponde a una cuenta",
]
for marker in required:
    if marker not in html:
        raise RuntimeError("V20.93 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.93 password recovery hardening")
print("V20.93 BEFORE:",before)
print("V20.93 AFTER:",after)
