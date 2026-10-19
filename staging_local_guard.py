import pathlib
import re

p = pathlib.Path("public/index.html")
html = p.read_text(encoding="utf-8")

PROD_URL = "https://cujipwacwwpejhqjhnkr.supabase.co"
PROD_REF = "cujipwacwwpejhqjhnkr"
PROD_KEY = "sb_publishable_TWE-dICHv3QemUtM302CTg_8i2zVx3G"

# Remove every known production backend reference from the staging artifact.
html = html.replace(PROD_URL, "https://staging-local.invalid")
html = html.replace(PROD_REF, "staging-local-disabled")
html = html.replace(PROD_KEY, "staging-local-cloud-disabled")

# The original base calls bootV4() automatically. Local staging must never
# attempt cloud initialization.
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
}
#fjzStagingLocalBanner b{color:#ff4050}
</style>
"""

js = r"""
<script id="fjzStagingLocalRuntime">
(function(){
  // Hard network kill-switch. A staging-local build may not contact production,
  // even if a historical handler is invoked manually.
  const nativeFetch=window.fetch?.bind(window);
  if(nativeFetch){
    window.fetch=function(input,init){
      const raw=typeof input==='string'?input:(input?.url||'');
      try{
        const u=new URL(raw,location.href);
        if(/\.supabase\.co$/i.test(u.hostname)){
          return Promise.reject(new Error('TEAM FJZ staging-local: cloud access disabled'));
        }
      }catch(_e){}
      return nativeFetch(input,init);
    };
  }

  try{clearCloudConfig?.()}catch(_e){}
  try{
    cloudEnabled=false;
    supabaseClient=null;
    currentUser=null;
    currentProfile=null;
  }catch(_e){}

  // Disable every visible/manual path that could try to configure cloud.
  window.showCloudConfigForm=function(){
    toast?.('Staging local: nube desactivada por seguridad');
  };
  window.saveCloudConfigAndConnect=function(){
    toast?.('Staging local: nube desactivada por seguridad');
  };
  window.loginCloud=function(){
    toast?.('Staging local: usá los datos sintéticos');
  };
  window.registerCloudAccount=function(){
    toast?.('Staging local: usá los datos sintéticos');
  };

  const badge=document.createElement('div');
  badge.id='fjzStagingLocalBanner';
  badge.innerHTML='<b>STAGING</b> · DATOS DE PRUEBA · SIN NUBE';
  document.body.appendChild(badge);

  window.__fjzStagingLocal={
    enabled:true,
    productionNetworkBlocked:true,
    cloudDisabled:true,
    syntheticDataOnly:true
  };
})();
</script>
"""

html = html.replace("</head>", css + "\n</head>", 1)
html = html.replace("</body>", js + "\n</body>", 1)

# Absolute safety assertions.
for forbidden in (PROD_URL, PROD_REF, PROD_KEY):
    if forbidden in html:
        raise RuntimeError("staging-local: production backend reference remains in output")

required = [
    "startLocalV4();",
    "productionNetworkBlocked:true",
    "cloudDisabled:true",
    "syntheticDataOnly:true",
    "STAGING</b> · DATOS DE PRUEBA"
]
missing = [x for x in required if x not in html]
if missing:
    raise RuntimeError("staging-local: missing safety markers: " + repr(missing))

p.write_text(html, encoding="utf-8")
print("TEAM FJZ STAGING-LOCAL safety guard enabled")
print("Cloud: disabled")
print("Production Supabase references: 0")
