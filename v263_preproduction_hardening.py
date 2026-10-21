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
        raise RuntimeError("V20.63 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.63 no script change "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-premium-polish" content="20.62"',
    "v194AuthFreshnessRuntime",
    "window.__fjzEnsureFreshAuthV194",
    "persistSession:true",
    "autoRefreshToken:true",
    "onAuthStateChange"
]:
    if marker not in html:
        raise RuntimeError("V20.63 missing prerequisite: "+marker)

def patch_auth(body):
    state_anchor="""  let refreshPromiseV194=null;
  let lastCheckV194=0;
"""
    helpers=r"""  let refreshPromiseV194=null;
  let lastCheckV194=0;

  function invalidRefreshV263(e){
    const msg=String(
      e?.message||
      e?.error_description||
      e?.error||
      e?.code||
      ''
    ).toLowerCase();
    return (
      msg.includes('refresh token not found')||
      msg.includes('invalid refresh token')||
      msg.includes('refresh_token_not_found')||
      msg.includes('refresh token already used')
    );
  }

  async function clearInvalidLocalSessionV263(e){
    if(!invalidRefreshV263(e))return false;
    if(window.__fjzInvalidRefreshClearingV263)return true;
    window.__fjzInvalidRefreshClearingV263=true;
    window.__fjzAuthInvalidatedV263={
      at:new Date().toISOString(),
      reason:'invalid_refresh_token'
    };
    try{
      // Supabase JS documented local scope: clear only this browser session.
      await supabaseClient.auth.signOut({scope:'local'});
    }catch(signOutErr){
      console.warn('TEAM FJZ V20.63 local auth cleanup',signOutErr);
    }finally{
      window.__fjzInvalidRefreshClearingV263=false;
    }
    return true;
  }
"""
    if body.count(state_anchor)!=1:
        raise RuntimeError("V20.63 auth state anchor mismatch")
    body=body.replace(state_anchor,helpers,1)

    old_refresh="""        })().catch(e=>{
          console.warn('TEAM FJZ V19.4 auth refresh',e);
          return false;
        }).finally(()=>{refreshPromiseV194=null});"""
    new_refresh="""        })().catch(async e=>{
          console.warn('TEAM FJZ V19.4 auth refresh',e);
          await clearInvalidLocalSessionV263(e);
          return false;
        }).finally(()=>{refreshPromiseV194=null});"""
    if body.count(old_refresh)!=1:
        raise RuntimeError("V20.63 refresh catch mismatch")
    body=body.replace(old_refresh,new_refresh,1)

    old_preflight="""    }catch(e){
      console.warn('TEAM FJZ V19.4 auth preflight',e);
      return false;
    }
  }"""
    new_preflight="""    }catch(e){
      console.warn('TEAM FJZ V19.4 auth preflight',e);
      await clearInvalidLocalSessionV263(e);
      return false;
    }
  }"""
    if body.count(old_preflight)!=1:
        raise RuntimeError("V20.63 preflight catch mismatch")
    body=body.replace(old_preflight,new_preflight,1)

    old_wrapper="""    const wrapped=async function(){
      await ensureFreshAuthV194(false);
      return fn.apply(this,arguments);
    };"""
    new_wrapper="""    const wrapped=async function(){
      const authOk=await ensureFreshAuthV194(false);
      if(!authOk){
        console.warn('TEAM FJZ V20.63 cloud task skipped without fresh auth',name);
        return null;
      }
      return fn.apply(this,arguments);
    };"""
    if body.count(old_wrapper)!=1:
        raise RuntimeError("V20.63 cloud task wrapper mismatch")
    body=body.replace(old_wrapper,new_wrapper,1)

    old_marker="""    authExpiryPreflight:true,
    wrappedCloudTasks:wrappedTasks
  };"""
    new_marker="""    authExpiryPreflight:true,
    wrappedCloudTasks:wrappedTasks,
    invalidRefreshLocalSignout:true,
    cloudTasksRequireFreshAuth:true,
    invalidRefreshLoopGuard:true
  };"""
    if body.count(old_marker)!=1:
        raise RuntimeError("V20.63 auth marker mismatch")
    body=body.replace(old_marker,new_marker,1)
    return body

html=edit_script(html,"v194AuthFreshnessRuntime",patch_auth)
html=html.replace("</head>",'<meta name="fjz-preproduction-hardening" content="20.63">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.63 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-preproduction-hardening" content="20.63"',
    "invalidRefreshV263","clearInvalidLocalSessionV263",
    "signOut({scope:'local'})",
    "invalidRefreshLocalSignout:true",
    "cloudTasksRequireFreshAuth:true",
    "invalidRefreshLoopGuard:true"
]:
    if marker not in html:
        raise RuntimeError("V20.63 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.63 preproduction auth hardening")
print("V20.63 BEFORE:",before)
print("V20.63 AFTER:",after)
print("V20.63 stale refresh sessions now clear locally and cloud tasks stop without fresh auth")
