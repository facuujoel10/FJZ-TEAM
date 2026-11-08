from __future__ import annotations
import json, os, re, shutil, subprocess, urllib.error, urllib.parse, urllib.request

PROD_REF="cujipwacwwpejhqjhnkr"
PROD_URL="https://"+PROD_REF+".supabase.co"
PROD_KEY="sb_publishable_TWE-dICHv3QemUtM302CTg_8i2zVx3G"
LOCAL_HOSTS={"127.0.0.1","localhost"}
TEST_PASSWORD="TEAMFJZ-Local-Only!22"

SUPABASE_CLI_VERSION="3.0.0"

def supabase_cmd():
    # Exact version: avoids a future CLI major changing local/remote semantics.
    npx=shutil.which("npx")
    if npx: return [npx,"--yes","supabase@"+SUPABASE_CLI_VERSION]
    cli=shutil.which("supabase")
    if cli: return [cli]
    raise RuntimeError("Supabase CLI/NPM no disponible. Instalalo antes de continuar.")

def run(cmd,*,env=None,capture=False):
    return subprocess.run(cmd,check=True,text=True,env=env,
        capture_output=capture)

def parse_env_lines(text):
    out={}
    for raw in text.splitlines():
        line=raw.strip()
        if not line or "=" not in line: continue
        k,v=line.split("=",1)
        v=v.strip().strip('"').strip("'")
        out[k.strip()]=v
    return out

def local_status():
    p=run(supabase_cmd()+["status","-o","env"],capture=True)
    env=parse_env_lines(p.stdout)
    api=env.get("API_URL") or env.get("SUPABASE_URL") or env.get("PROJECT_URL")
    publishable=env.get("PUBLISHABLE_KEY") or env.get("ANON_KEY")
    secret=env.get("SERVICE_ROLE_KEY") or env.get("SECRET_KEY")
    if not api or not publishable or not secret:
        raise RuntimeError("No pude obtener URL/keys del Supabase local.")
    assert_local_url(api)
    for value in (api,publishable,secret):
        reject_production(value)
    return {"api":api.rstrip("/"),"publishable":publishable,"secret":secret,"raw":env}

def reject_production(value):
    value=str(value or "")
    low=value.lower()
    if PROD_REF in low or PROD_URL.lower() in low or PROD_KEY in value or ".supabase.co" in low:
        raise RuntimeError("Configuración productiva detectada y bloqueada.")

def assert_local_url(url):
    reject_production(url)
    p=urllib.parse.urlparse(str(url))
    if p.hostname not in LOCAL_HOSTS:
        raise RuntimeError("Solo se permite Supabase local en 127.0.0.1/localhost.")
    if p.scheme not in {"http","https"}:
        raise RuntimeError("Esquema de URL local inválido.")

def http_json(method,url,apikey,token=None,payload=None,prefer=None,ok=(200,201,204)):
    assert_local_url(url)
    body=None if payload is None else json.dumps(payload).encode()
    headers={"apikey":apikey,"Accept":"application/json"}
    if token: headers["Authorization"]="Bearer "+token
    if body is not None: headers["Content-Type"]="application/json"
    if prefer: headers["Prefer"]=prefer
    req=urllib.request.Request(url,data=body,headers=headers,method=method)
    try:
        with urllib.request.urlopen(req,timeout=15) as r:
            raw=r.read().decode()
            if r.status not in ok:
                raise RuntimeError(f"HTTP {r.status}: {raw}")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raw=e.read().decode()
        if e.code in ok:
            return json.loads(raw) if raw else None
        raise RuntimeError(f"HTTP {e.code}: {raw}") from e

def http_bytes(method,url,apikey,token=None,payload=None,content_type="application/octet-stream",ok=(200,201,204)):
    assert_local_url(url)
    headers={"apikey":apikey}
    if token: headers["Authorization"]="Bearer "+token
    if payload is not None: headers["Content-Type"]=content_type
    req=urllib.request.Request(url,data=payload,headers=headers,method=method)
    try:
        with urllib.request.urlopen(req,timeout=15) as r:
            raw=r.read()
            if r.status not in ok:
                raise RuntimeError(f"HTTP {r.status}")
            return raw
    except urllib.error.HTTPError as e:
        _=e.read()
        if e.code in ok:
            return b""
        raise RuntimeError(f"HTTP {e.code}") from e
