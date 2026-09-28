import base64
import pathlib
import re
import urllib.request

SOURCE = "https://cujipwacwwpejhqjhnkr.supabase.co/functions/v1/team-fjz-source"
OUT = pathlib.Path("public")
OUT.mkdir(parents=True, exist_ok=True)

req = urllib.request.Request(SOURCE, headers={"User-Agent": "TEAM-FJZ-Render-Build/1.0"})
with urllib.request.urlopen(req, timeout=60) as response:
    html = response.read().decode("utf-8")

if "<!doctype html" not in html.lower() or "TEAM FJZ" not in html:
    raise RuntimeError("La fuente de TEAM FJZ no devolvió la aplicación esperada.")

# V8.4: misma aplicación V8.3, con ajustes finales de publicación/PWA.
html = html.replace("TEAM FJZ V8.3", "TEAM FJZ V8.4")
html = html.replace("// ===== TEAM FJZ V8.3", "// ===== TEAM FJZ V8.4")
html = html.replace("/* TEAM FJZ V8.3", "/* TEAM FJZ V8.4")
html = html.replace(
    "<link rel=\"manifest\" href=\"./manifest.json\">",
    "<link rel=\"manifest\" href=\"./manifest.json\">\n"
    "<link rel=\"apple-touch-icon\" href=\"./icon-v84.webp\">\n"
    "<meta name=\"format-detection\" content=\"telephone=no\">"
)

# Ajustes finales de producción.
# Elimina el registro antiguo duplicado del service worker; se conserva registerPwaV82().
html = html.replace(
    "if('serviceWorker' in navigator && location.protocol.startsWith('http'))window.addEventListener('load',()=>navigator.serviceWorker.register('./sw.js').catch(()=>{}));",
    ""
)

# Todos los iconos/runtime apuntan al asset versionado para evitar caché vieja.
html = html.replace("icon.webp", "icon-v84.webp")

# El alta pública es únicamente para alumnos. El perfil Coach existente se mantiene.
html = html.replace(
    '<label class="tiny muted">Tipo de cuenta<select id="authRole" class="input"><option value="coach">Coach</option><option value="student">Alumno</option></select></label>',
    '<input id="authRole" type="hidden" value="student"><div class="card" style="padding:10px 12px"><strong>Cuenta de alumno</strong><div class="muted tiny">El acceso Coach se administra de forma privada.</div></div>'
)
html = html.replace(
    "const full_name=el('authName').value.trim(),role=el('authRole').value,email=el('authEmail').value.trim(),password=el('authPass').value;",
    "const full_name=el('authName').value.trim(),role='student',email=el('authEmail').value.trim(),password=el('authPass').value;"
)

# Extrae el logo WebP embebido para usarlo como icono PWA.
icons = re.findall(r"data:image/webp;base64,([A-Za-z0-9+/=]+)", html)
if icons:
    logo_b64 = max(icons, key=len)
    icon_bytes = base64.b64decode(logo_b64)
    if len(icon_bytes) < 1000:
        raise RuntimeError("El icono TEAM FJZ encontrado es demasiado pequeño.")
    (OUT / "icon-v84.webp").write_bytes(icon_bytes)
else:
    raise RuntimeError("No se encontró el icono TEAM FJZ embebido.")

(OUT / "index.html").write_text(html, encoding="utf-8")

manifest = """{
  "name": "TEAM FJZ",
  "short_name": "TEAM FJZ",
  "description": "Coaching de entrenamiento, seguimiento, nutrición y progreso.",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "background_color": "#08080a",
  "theme_color": "#0a0a0c",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "./icon-v84.webp",
      "sizes": "any",
      "type": "image/webp",
      "purpose": "any maskable"
    }
  ]
}
"""
(OUT / "manifest.json").write_text(manifest, encoding="utf-8")

sw = """const CACHE='team-fjz-v8-4';
const ASSETS=['./','./index.html','./manifest.json','./icon-v84.webp'];

self.addEventListener('install',event=>{
  event.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).catch(()=>{}));
  self.skipWaiting();
});

self.addEventListener('activate',event=>{
  event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener('fetch',event=>{
  const req=event.request;
  if(req.method!=='GET') return;
  const url=new URL(req.url);
  if(url.origin!==self.location.origin) return;
  if(req.mode==='navigate'){
    event.respondWith(
      fetch(req).then(res=>{
        if(res.ok){
          const copy=res.clone();
          caches.open(CACHE).then(c=>c.put('./index.html',copy)).catch(()=>{});
        }
        return res;
      }).catch(()=>caches.match('./index.html'))
    );
    return;
  }
  event.respondWith(caches.match(req).then(hit=>hit||fetch(req)));
});
"""
(OUT / "sw.js").write_text(sw, encoding="utf-8")

print("TEAM FJZ V8.4 lista para publicar:", len(html), "bytes")


# Producción cerrada: un alumno registrado no accede a la app hasta vincular el código del coach.
html = html.replace(
    "function startLocalV4(){cloudEnabled=false;currentUser=null;currentProfile=null;hideGate();setCloudStatus('', 'Local');render()}",
    "function startLocalV4(){showAuthGate('login','El modo local está deshabilitado. Ingresá con tu cuenta TEAM FJZ.');}"
)

html = html.replace(
    "if(!data){data={id:currentUser.id,full_name:currentUser.user_metadata?.full_name||'',role:currentUser.user_metadata?.role==='coach'?'coach':'student'}}",
    "if(!data){data={id:currentUser.id,full_name:currentUser.user_metadata?.full_name||'',role:'student'}}"
)

html = html.replace(
    "if(!linked){showClaimGate();return}",
    "if(!linked){linkedAthleteId=null;cloudAthletes=new Map();cloudApplying=true;window.__fjzCloudApplying=true;state={version:5,selectedStudentId:'',templates:state.templates?.length?state.templates:clone(initialState.templates),students:[]};localStorage.setItem('fjz_v4_state',JSON.stringify(state));cloudApplying=false;window.__fjzCloudApplying=false;showClaimGate();return}"
)

html = html.replace(
    '<div style="display:flex;justify-content:space-between;gap:8px;margin-top:14px"><button class="btn ghost small" onclick="showCloudConfigForm()">Configurar nube</button><button class="btn ghost small" onclick="startLocalV4()">Modo local</button></div>',
    '<div class="muted micro" style="margin-top:14px;text-align:center">Acceso privado TEAM FJZ · Los alumnos necesitan un código de vinculación del coach.</div>'
)

html = html.replace(
    "<p>Pedile a tu coach el código de invitación que aparece dentro de tu ficha de TEAM FJZ.</p>",
    "<p>Tu cuenta fue creada correctamente. Para entrar a TEAM FJZ necesitás el código de vinculación que te entrega tu coach.</p><div class=\"card\" style=\"padding:10px 12px;margin:10px 0\"><strong>Acceso bloqueado hasta vincular</strong><div class=\"muted tiny\">Sin un código válido no se cargan rutinas, nutrición, progreso, agenda ni datos de alumnos.</div></div>"
)


# V8.5: eliminación de alumnos desde Coach + realtime más estable para reducir parpadeos/lag.
html = html.replace(
    "if(Date.now()-cloudLastWrite<1200)return;",
    "if(Date.now()-cloudLastWrite<3000)return;"
)
html = html.replace(
    "cloudRefreshTimer=setTimeout(refreshCloudFromRealtime,500)",
    "cloudRefreshTimer=setTimeout(refreshCloudFromRealtime,900)"
)

html = re.sub(
    r"function studentRows\(arr\)\{return arr\.map\(s=>`.*?`\)\.join\(''\)\}",
    """function studentRows(arr){return arr.map(s=>`<div class="student-row"><div class="student-main"><div class="avatar">${esc(s.name.slice(0,2).toUpperCase())}</div><div><strong>${esc(s.name)}</strong><div class="muted tiny">${esc(s.goal)}</div></div></div><div><strong>${adherence(s)}%</strong><div class="muted tiny">Adherencia</div></div><div><strong>${fmtDate(s.lastWorkout)}</strong><div class="muted tiny">Último entreno</div></div><div>${badge(statusFor(s))}</div><div class="pill-row" style="justify-content:flex-end"><button class="btn small" onclick="openStudent('${s.id}')">Abrir</button><button class="btn small" style="border-color:rgba(255,31,47,.55);color:#ff7a84" onclick="deleteStudentCloud('${s.id}')">Eliminar</button></div></div>`).join('')}""",
    html,
    count=1,
    flags=re.S
)

delete_fn = r"""
async function deleteStudentCloud(id){
  const s=state.students.find(x=>x.id===id);
  const row=cloudAthletes.get(id);
  if(!s||!row){toast('No se encontró el alumno en la nube');return}
  if(!confirm('¿Eliminar a '+s.name+' de TEAM FJZ? Se borrarán su ficha, rutina, registros, nutrición, check-ins y acceso.'))return;
  if(!confirm('Esta acción es definitiva. ¿Confirmás eliminar al alumno?'))return;
  try{
    setCloudStatus('syncing','Eliminando');
    const {error}=await supabaseClient.rpc('delete_my_athlete',{p_athlete:row.id});
    if(error)throw error;
    cloudAthletes.delete(id);
    state.students=state.students.filter(x=>x.id!==id);
    state.selectedStudentId=state.students[0]?.id||'';
    localStorage.setItem('fjz_v4_state',JSON.stringify(state));
    coachTab='dashboard';
    coachStudentTab='summary';
    render();
    setCloudStatus('online','En nube');
    toast('Alumno eliminado');
  }catch(e){
    console.error(e);
    setCloudStatus('error','Error');
    alert('No se pudo eliminar el alumno. Probá de nuevo.');
  }
}
"""
html = html.replace("function openStudent(id){", delete_fn + "\nfunction openStudent(id){", 1)

html = re.sub(
    r"async function refreshCloudFromRealtime\(\)\{.*?\}\nfunction setupRealtime\(\)",
    r"""async function refreshCloudFromRealtime(){
  if(!cloudEnabled||!currentProfile)return;
  if(window.__fjzRtBusy){window.__fjzRtQueued=true;return}
  window.__fjzRtBusy=true;
  try{
    cloudApplying=true;window.__fjzCloudApplying=true;
    if(currentProfile.role==='coach'){
      await loadCoachCloud();
    }else{
      const linked=await loadStudentCloud();
      if(!linked){
        linkedAthleteId=null;
        cloudAthletes=new Map();
        state={version:5,selectedStudentId:'',templates:state.templates?.length?state.templates:clone(initialState.templates),students:[]};
        localStorage.setItem('fjz_v4_state',JSON.stringify(state));
        cloudApplying=false;window.__fjzCloudApplying=false;
        showClaimGate('Tu acceso no está vinculado. Pedile un nuevo código a tu coach.');
        setCloudStatus('online','En nube');
        return;
      }
    }
    cloudApplying=false;window.__fjzCloudApplying=false;
    render();
    setCloudStatus('online','Actualizado');
  }catch(e){
    cloudApplying=false;window.__fjzCloudApplying=false;
    console.error(e);
  }finally{
    window.__fjzRtBusy=false;
    if(window.__fjzRtQueued){
      window.__fjzRtQueued=false;
      clearTimeout(window.__fjzRtQueueTimer);
      window.__fjzRtQueueTimer=setTimeout(()=>refreshCloudFromRealtime(),900);
    }
  }
}
function setupRealtime()""",
    html,
    count=1,
    flags=re.S
)


# FINAL_REWRITE_V85: las transformaciones añadidas arriba deben persistirse después de aplicarse.
(OUT / "index.html").write_text(html, encoding="utf-8")
print("TEAM FJZ V8.5 final:", len(html), "bytes")


# V8.6 final patch
exec(compile(open("v86_patch.py", encoding="utf-8").read(), "v86_patch.py", "exec"))


# V8.7 final UI polish
exec(compile(open("v87_patch.py", encoding="utf-8").read(), "v87_patch.py", "exec"))


# V8.8 final fixes
exec(compile(open("v88_patch.py", encoding="utf-8").read(), "v88_patch.py", "exec"))


# V9.4 nutrition + tracking
exec(compile(open("v94_nutrition_tracking.py", encoding="utf-8").read(), "v94_nutrition_tracking.py", "exec"))

# V9.4 training guidance
exec(compile(open("v94_training.py", encoding="utf-8").read(), "v94_training.py", "exec"))

# V9.6 professional alerts
exec(compile(open("v96_alerts.py", encoding="utf-8").read(), "v96_alerts.py", "exec"))

# V9.7 migrated profile metadata
exec(compile(open("v97_migration_profiles.py", encoding="utf-8").read(), "v97_migration_profiles.py", "exec"))

# V9.8 precision UI polish
exec(compile(open("v98_ui_precision.py", encoding="utf-8").read(), "v98_ui_precision.py", "exec"))

# V9.9 full audit
exec(compile(open("v99_full_audit.py", encoding="utf-8").read(), "v99_full_audit.py", "exec"))

# V10.0 consolidated core cleanup
exec(compile(open("v100_core_cleanup.py", encoding="utf-8").read(), "v100_core_cleanup.py", "exec"))

# V10.0 remove superseded legacy layers
exec(compile(open("v100_post_cleanup.py", encoding="utf-8").read(), "v100_post_cleanup.py", "exec"))

# V10.4 exact repetition schemes
exec(compile(open("v104_rep_scheme.py", encoding="utf-8").read(), "v104_rep_scheme.py", "exec"))

# V10.5 Ariel historical routine import
exec(compile(open("v105_ariel_routine.py", encoding="utf-8").read(), "v105_ariel_routine.py", "exec"))

# V10.6 allow partial workout session saves
exec(compile(open("v106_partial_sessions.py", encoding="utf-8").read(), "v106_partial_sessions.py", "exec"))

# V11.0 method loads + coach intelligence + final polish
exec(compile(open("v110_final_polish.py", encoding="utf-8").read(), "v110_final_polish.py", "exec"))


# V11.1 production release cleanup
exec(compile(open("v111_release_cleanup.py", encoding="utf-8").read(), "v111_release_cleanup.py", "exec"))


# V11.2 synchronization hardening
exec(compile(open("v112_sync_hardening.py", encoding="utf-8").read(), "v112_sync_hardening.py", "exec"))


# V11.3 exercise ordering and descriptions
exec(compile(open("v113_exercise_order_descriptions.py", encoding="utf-8").read(), "v113_exercise_order_descriptions.py", "exec"))


# V11.4 editable student profiles
exec(compile(open("v114_editable_student_profiles.py", encoding="utf-8").read(), "v114_editable_student_profiles.py", "exec"))


# V11.5 student profile height editing
exec(compile(open("v115_student_profile_height.py", encoding="utf-8").read(), "v115_student_profile_height.py", "exec"))


# V11.6 student avatar fix
exec(compile(open("v116_student_avatar_fix.py", encoding="utf-8").read(), "v116_student_avatar_fix.py", "exec"))


# V11.7 remove duplicate student profile UI
exec(compile(open("v117_profile_dedup.py", encoding="utf-8").read(), "v117_profile_dedup.py", "exec"))


# V11.8 audit cleanup
exec(compile(open("v118_audit_cleanup.py", encoding="utf-8").read(), "v118_audit_cleanup.py", "exec"))


# V11.9 hard profile dedup + PWA refresh
exec(compile(open("v119_profile_hard_dedup.py", encoding="utf-8").read(), "v119_profile_hard_dedup.py", "exec"))


# V12.0 progress photo replace/delete
exec(compile(open("v120_progress_photo_manage.py", encoding="utf-8").read(), "v120_progress_photo_manage.py", "exec"))


# V12.1 normalize visible release label
exec(compile(open("v121_release_label.py", encoding="utf-8").read(), "v121_release_label.py", "exec"))


# V12.2 scheduled check-ins and payment tracking
exec(compile(open("v122_followups_payments.py", encoding="utf-8").read(), "v122_followups_payments.py", "exec"))


# V12.3 consolidate coach alert center
exec(compile(open("v123_alert_center_cleanup.py", encoding="utf-8").read(), "v123_alert_center_cleanup.py", "exec"))


# V12.4 coach admin visibility + manual alerts + release fix
exec(compile(open("v124_coach_admin.py", encoding="utf-8").read(), "v124_coach_admin.py", "exec"))


# V12.5 render/performance consolidation
exec(compile(open("v125_render_optimization.py", encoding="utf-8").read(), "v125_render_optimization.py", "exec"))


# V12.6 stable layout + profile first
exec(compile(open("v126_stable_layout.py", encoding="utf-8").read(), "v126_stable_layout.py", "exec"))


# V13.0 canonical profile persistence
exec(compile(open("v130_profile_persistence.py", encoding="utf-8").read(), "v130_profile_persistence.py", "exec"))

# V13.1 profile integrity
exec(compile(open("v131_profile_integrity.py", encoding="utf-8").read(), "v131_profile_integrity.py", "exec"))

# V13.2 Coach Assistant 360 + realtime batching
exec(compile(open("v132_assistant_realtime_audit.py", encoding="utf-8").read(), "v132_assistant_realtime_audit.py", "exec"))

# V13.3 platform-standard PWA icons
exec(compile(open("v133_pwa_icons.py", encoding="utf-8").read(), "v133_pwa_icons.py", "exec"))

# V13.4 nutrition education
exec(compile(open("v134_nutrition_education.py", encoding="utf-8").read(), "v134_nutrition_education.py", "exec"))

# V13.5 nutrition learn visibility fix
exec(compile(open("v135_nutrition_learn_visibility.py", encoding="utf-8").read(), "v135_nutrition_learn_visibility.py", "exec"))

# V13.6 final nutrition + render/data stability
exec(compile(open("v136_final_stability.py", encoding="utf-8").read(), "v136_final_stability.py", "exec"))

# V13.7 method tracking + desktop stability
exec(compile(open("v137_method_tracking_stability.py", encoding="utf-8").read(), "v137_method_tracking_stability.py", "exec"))

# V13.8 stable nutrition habits guide
exec(compile(open("v138_nutrition_habits_guide.py", encoding="utf-8").read(), "v138_nutrition_habits_guide.py", "exec"))

# V13.9 final QA / consolidation
exec(compile(open("v139_final_qa.py", encoding="utf-8").read(), "v139_final_qa.py", "exec"))

# V12.7 centralized release + PWA update system
exec(compile(open("v127_release_system.py", encoding="utf-8").read(), "v127_release_system.py", "exec"))
