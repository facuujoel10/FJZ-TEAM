import base64
import pathlib
import re
import urllib.request
import os

PINNED_SOURCE = pathlib.Path("base/team-fjz-source-v20.7.html")
PRODUCTION_SUPABASE_URL = "https://cujipwacwwpejhqjhnkr.supabase.co"
APP_ENV = os.environ.get("TEAM_FJZ_ENV", "production").strip().lower()

if APP_ENV not in {"production", "staging", "staging-local", "development", "test"}:
    raise RuntimeError(f"TEAM FJZ safety guard: unknown TEAM_FJZ_ENV={APP_ENV!r}")

if not PINNED_SOURCE.exists():
    raise RuntimeError(
        "TEAM FJZ reproducible-build guard: pinned base source is missing: "
        f"{PINNED_SOURCE}"
    )

# Reproducible baseline: builds start from the exact V20.7 base stored in Git.
# We no longer fetch a mutable Edge Function during the build.
html = PINNED_SOURCE.read_text(encoding="utf-8")

if APP_ENV == "staging-local":
    # Safe zero-cost staging: cloud access is deliberately disabled.
    # The final staging guard patch forces local synthetic/demo state.
    url_pattern = r"const DEFAULT_SUPABASE_URL='[^']+';"
    key_pattern = r"const DEFAULT_SUPABASE_KEY='[^']+';"
    html, url_count = re.subn(
        url_pattern,
        "const DEFAULT_SUPABASE_URL='https://staging-local.invalid';",
        html,
        count=1,
    )
    html, key_count = re.subn(
        key_pattern,
        "const DEFAULT_SUPABASE_KEY='staging-local-cloud-disabled';",
        html,
        count=1,
    )
    if url_count != 1 or key_count != 1:
        raise RuntimeError(
            "TEAM FJZ staging-local guard: expected exactly one Supabase URL/key constant."
        )
elif APP_ENV != "production":
    staging_url = os.environ.get("TEAM_FJZ_SUPABASE_URL", "").strip().rstrip("/")
    staging_key = os.environ.get("TEAM_FJZ_SUPABASE_PUBLISHABLE_KEY", "").strip()

    if not staging_url or not staging_key:
        raise RuntimeError(
            "TEAM FJZ staging guard: non-production cloud builds require "
            "TEAM_FJZ_SUPABASE_URL and TEAM_FJZ_SUPABASE_PUBLISHABLE_KEY."
        )
    if staging_url == PRODUCTION_SUPABASE_URL:
        raise RuntimeError(
            "TEAM FJZ staging guard: non-production build is pointing at the "
            "production Supabase URL."
        )

    url_pattern = r"const DEFAULT_SUPABASE_URL='[^']+';"
    key_pattern = r"const DEFAULT_SUPABASE_KEY='[^']+';"
    html, url_count = re.subn(
        url_pattern,
        "const DEFAULT_SUPABASE_URL=" + repr(staging_url) + ";",
        html,
        count=1,
    )
    html, key_count = re.subn(
        key_pattern,
        "const DEFAULT_SUPABASE_KEY=" + repr(staging_key) + ";",
        html,
        count=1,
    )
    if url_count != 1 or key_count != 1:
        raise RuntimeError(
            "TEAM FJZ staging guard: expected exactly one Supabase URL/key "
            "constant in the pinned base."
        )

OUT = pathlib.Path("public")
OUT.mkdir(parents=True, exist_ok=True)

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

# V13.6 final nutrition + render/data stability
exec(compile(open("v136_final_stability.py", encoding="utf-8").read(), "v136_final_stability.py", "exec"))

# V13.7 method tracking + desktop stability
exec(compile(open("v137_method_tracking_stability.py", encoding="utf-8").read(), "v137_method_tracking_stability.py", "exec"))

# V13.8 stable nutrition habits guide
exec(compile(open("v138_nutrition_habits_guide.py", encoding="utf-8").read(), "v138_nutrition_habits_guide.py", "exec"))

# V14.0 consolidated runtime / final optimization
exec(compile(open("v140_consolidated_runtime.py", encoding="utf-8").read(), "v140_consolidated_runtime.py", "exec"))

# V14.3 final interaction QA
exec(compile(open("v143_interaction_qa.py", encoding="utf-8").read(), "v143_interaction_qa.py", "exec"))

# V14.4 stretching / mobility library
exec(compile(open("v144_stretching_library.py", encoding="utf-8").read(), "v144_stretching_library.py", "exec"))

# V14.5 workout draft autosave / resume
exec(compile(open("v145_workout_autosave.py", encoding="utf-8").read(), "v145_workout_autosave.py", "exec"))

# V14.6 render stability / background refresh guard
exec(compile(open("v146_render_stability.py", encoding="utf-8").read(), "v146_render_stability.py", "exec"))

# V14.7 coach-programmed routine authority
exec(compile(open("v147_program_authority.py", encoding="utf-8").read(), "v147_program_authority.py", "exec"))

# V14.8 coach/student session deletion
exec(compile(open("v148_session_delete.py", encoding="utf-8").read(), "v148_session_delete.py", "exec"))

# V14.9 clearer progress metrics / audited release
exec(compile(open("v149_progress_clarity.py", encoding="utf-8").read(), "v149_progress_clarity.py", "exec"))

# V15.1 bodyweight / weighted / assisted load modes + mixed-exercise hardening
exec(compile(open("v150_bodyweight_load_modes.py", encoding="utf-8").read(), "v150_bodyweight_load_modes.py", "exec"))

# V15.1 full audit hardening / single-save editor
exec(compile(open("v151_audit_hardening.py", encoding="utf-8").read(), "v151_audit_hardening.py", "exec"))

# V15.2 routine day deletion
exec(compile(open("v152_day_delete.py", encoding="utf-8").read(), "v152_day_delete.py", "exec"))

# V15.3 nutrition calculator / logging reliability
exec(compile(open("v153_nutrition_logging.py", encoding="utf-8").read(), "v153_nutrition_logging.py", "exec"))

# V15.4 interactive weekly check-in scores
exec(compile(open("v154_checkin_scores.py", encoding="utf-8").read(), "v154_checkin_scores.py", "exec"))

# V15.5 mobile modal / exercise editor scroll fix
exec(compile(open("v155_modal_scroll_fix.py", encoding="utf-8").read(), "v155_modal_scroll_fix.py", "exec"))

# V15.6 tab interaction audit + calculator hardening
exec(compile(open("v156_interaction_calculator_audit.py", encoding="utf-8").read(), "v156_interaction_calculator_audit.py", "exec"))

# V15.7 compact check-in inputs
exec(compile(open("v157_compact_checkin.py", encoding="utf-8").read(), "v157_compact_checkin.py", "exec"))

# V15.8 fluid navigation / render stability
exec(compile(open("v158_fluid_navigation.py", encoding="utf-8").read(), "v158_fluid_navigation.py", "exec"))

# V15.9 mobile layout + check-in + render polish
exec(compile(open("v159_mobile_layout_checkin_render.py", encoding="utf-8").read(), "v159_mobile_layout_checkin_render.py", "exec"))

# V16.0 final simple check-in numeric inputs
exec(compile(open("v160_simple_checkin_inputs.py", encoding="utf-8").read(), "v160_simple_checkin_inputs.py", "exec"))

# V16.1 unified coach summary 360
exec(compile(open("v161_unified_coach_summary.py", encoding="utf-8").read(), "v161_unified_coach_summary.py", "exec"))

# V16.2 coach panel dedup + smart integrated guidance
exec(compile(open("v162_coach_panel_dedup_guidance.py", encoding="utf-8").read(), "v162_coach_panel_dedup_guidance.py", "exec"))

# V16.3 streamline coach summary identity
exec(compile(open("v163_summary_identity_cleanup.py", encoding="utf-8").read(), "v163_summary_identity_cleanup.py", "exec"))

# V16.4 agenda reliability + performance
exec(compile(open("v164_agenda_reliability.py", encoding="utf-8").read(), "v164_agenda_reliability.py", "exec"))

# V16.5 agenda hard reset / direct handlers
exec(compile(open("v165_agenda_hard_reset.py", encoding="utf-8").read(), "v165_agenda_hard_reset.py", "exec"))

# V16.6 explicit date reminders
exec(compile(open("v166_explicit_date_reminders.py", encoding="utf-8").read(), "v166_explicit_date_reminders.py", "exec"))

# V16.7 clean submitted check-in + full coach view
exec(compile(open("v167_checkin_cleanup_full_coach.py", encoding="utf-8").read(), "v167_checkin_cleanup_full_coach.py", "exec"))

# V17.0 consolidated coach/check-in runtime + dashboard polish
exec(compile(open("v170_consolidated_runtime.py", encoding="utf-8").read(), "v170_consolidated_runtime.py", "exec"))

# V17.3 safe summary dedup + payments navigation
exec(compile(open("v173_safe_summary_payments.py", encoding="utf-8").read(), "v173_safe_summary_payments.py", "exec"))

# V17.4 single canonical 360 + integrated coach assistant
exec(compile(open("v174_single_360_assistant.py", encoding="utf-8").read(), "v174_single_360_assistant.py", "exec"))

# V17.5 profile/layout + agenda attention + unified coach center
exec(compile(open("v175_profile_agenda_coach_center.py", encoding="utf-8").read(), "v175_profile_agenda_coach_center.py", "exec"))

# V17.6 mobile UX + measurement editing + grouped meals + nutrition cleanup
exec(compile(open("v176_mobile_tracking_meals_cleanup.py", encoding="utf-8").read(), "v176_mobile_tracking_meals_cleanup.py", "exec"))

# V17.7 mobile stability + reliable measurement editing
exec(compile(open("v177_mobile_stability_measurements.py", encoding="utf-8").read(), "v177_mobile_stability_measurements.py", "exec"))

# V17.8 final mobile/render audit + post-render consolidation
exec(compile(open("v178_final_mobile_render_audit.py", encoding="utf-8").read(), "v178_final_mobile_render_audit.py", "exec"))

# V17.9 compact mobile layout + check-in time + measurement editing
exec(compile(open("v179_compact_mobile_time_measure_edit.py", encoding="utf-8").read(), "v179_compact_mobile_time_measure_edit.py", "exec"))

# V18.0 visual stability + canonical navigation scroll
exec(compile(open("v180_visual_stability_navigation.py", encoding="utf-8").read(), "v180_visual_stability_navigation.py", "exec"))

# V18.1 tracking date-field symmetry
exec(compile(open("v181_tracking_date_symmetry.py", encoding="utf-8").read(), "v181_tracking_date_symmetry.py", "exec"))

# V18.2 geometry + coach dashboard polish
exec(compile(open("v182_geometry_dashboard_polish.py", encoding="utf-8").read(), "v182_geometry_dashboard_polish.py", "exec"))

# V18.3 student measurement scope + input alignment
exec(compile(open("v183_student_scope_input_alignment.py", encoding="utf-8").read(), "v183_student_scope_input_alignment.py", "exec"))

# V18.4 hard measurement isolation + exact date geometry
exec(compile(open("v184_hard_measure_isolation_date_geometry.py", encoding="utf-8").read(), "v184_hard_measure_isolation_date_geometry.py", "exec"))

# V18.5 production rendering/runtime optimization
exec(compile(open("v185_production_runtime_optimization.py", encoding="utf-8").read(), "v185_production_runtime_optimization.py", "exec"))

# V18.6 exact tracking field alignment
exec(compile(open("v186_exact_tracking_field_alignment.py", encoding="utf-8").read(), "v186_exact_tracking_field_alignment.py", "exec"))

# V18.7 strict 2-by-2 tracking geometry
exec(compile(open("v187_strict_paired_tracking_geometry.py", encoding="utf-8").read(), "v187_strict_paired_tracking_geometry.py", "exec"))

# V18.8 panel click scroll fix
exec(compile(open("v188_panel_click_scroll_fix.py", encoding="utf-8").read(), "v188_panel_click_scroll_fix.py", "exec"))

# V19.0 session save confirmation + alert badge geometry
exec(compile(open("v190_session_save_alert_badge_hardening.py", encoding="utf-8").read(), "v190_session_save_alert_badge_hardening.py", "exec"))

# V19.1 action geometry + overflow audit
exec(compile(open("v191_action_geometry_audit.py", encoding="utf-8").read(), "v191_action_geometry_audit.py", "exec"))

# V19.2 general stability / realtime / visual audit
exec(compile(open("v192_general_stability_audit.py", encoding="utf-8").read(), "v192_general_stability_audit.py", "exec"))

# V19.3 interaction persistence / modal protection
exec(compile(open("v193_interaction_persistence.py", encoding="utf-8").read(), "v193_interaction_persistence.py", "exec"))

# V19.4 final UI symmetry + functional audit
exec(compile(open("v194_final_ui_functional_audit.py", encoding="utf-8").read(), "v194_final_ui_functional_audit.py", "exec"))

# V19.5 routine method dedup + field geometry
exec(compile(open("v195_routine_method_geometry_fix.py", encoding="utf-8").read(), "v195_routine_method_geometry_fix.py", "exec"))

# V19.6 fresh workout loads + routine builder stability
exec(compile(open("v196_fresh_workout_routine_flow.py", encoding="utf-8").read(), "v196_fresh_workout_routine_flow.py", "exec"))

# V19.7 reviewed alert archival
exec(compile(open("v197_alert_archive_behavior.py", encoding="utf-8").read(), "v197_alert_archive_behavior.py", "exec"))

# V19.8 method panel persistence
exec(compile(open("v198_method_panel_persistence.py", encoding="utf-8").read(), "v198_method_panel_persistence.py", "exec"))

# V20.0 state/save/routine stability authority
exec(compile(open("v200_state_save_routine_stability.py", encoding="utf-8").read(), "v200_state_save_routine_stability.py", "exec"))

# V20.1 definitive workout save + empty load inputs
exec(compile(open("v201_definitive_workout_save.py", encoding="utf-8").read(), "v201_definitive_workout_save.py", "exec"))

# V20.3 terminal workout save flow
exec(compile(open("v203_terminal_workout_save.py", encoding="utf-8").read(), "v203_terminal_workout_save.py", "exec"))

# V20.4 terminal save + zero-jump reorder
exec(compile(open("v204_terminal_save_scroll_stability.py", encoding="utf-8").read(), "v204_terminal_save_scroll_stability.py", "exec"))

# V20.5 canonical workout completion + progress visuals
exec(compile(open("v205_canonical_workout_progress.py", encoding="utf-8").read(), "v205_canonical_workout_progress.py", "exec"))

# V20.6 fluidity/runtime audit
exec(compile(open("v206_fluidity_runtime_audit.py", encoding="utf-8").read(), "v206_fluidity_runtime_audit.py", "exec"))

# V20.7 confirmed session commit state machine
exec(compile(open("v207_confirmed_session_commit.py", encoding="utf-8").read(), "v207_confirmed_session_commit.py", "exec"))

# V20.8 consolidate superseded workout completion wrappers.
exec(compile(open("v208_workout_save_wrapper_consolidation.py", encoding="utf-8").read(), "v208_workout_save_wrapper_consolidation.py", "exec"))

# V20.9 consolidate superseded routine save/reorder authorities.
exec(compile(open("v209_routine_authority_consolidation.py", encoding="utf-8").read(), "v209_routine_authority_consolidation.py", "exec"))

# V20.10 consolidate duplicate alert realtime into the unified authority.
exec(compile(open("v210_alert_realtime_consolidation.py", encoding="utf-8").read(), "v210_alert_realtime_consolidation.py", "exec"))

# V20.11 delegate the original core realtime subscription to V13.2.
exec(compile(open("v211_core_realtime_delegation.py", encoding="utf-8").read(), "v211_core_realtime_delegation.py", "exec"))

# V20.12 delegate exercise feedback realtime to the unified authority.
exec(compile(open("v212_feedback_realtime_delegation.py", encoding="utf-8").read(), "v212_feedback_realtime_delegation.py", "exec"))

# V20.13 inventory the final realtime surface without behavior changes.
exec(compile(open("v213_nutrition_habit_realtime_delegation.py", encoding="utf-8").read(), "v213_nutrition_habit_realtime_delegation.py", "exec"))

# V20.14 delegate global music realtime to the unified authority.
exec(compile(open("v214_global_music_realtime_delegation.py", encoding="utf-8").read(), "v214_global_music_realtime_delegation.py", "exec"))

# V20.15 delegate V80 media/feedback realtime to the unified authority.
exec(compile(open("v215_v80_realtime_delegation.py", encoding="utf-8").read(), "v215_v80_realtime_delegation.py", "exec"))

# V20.16 delegate core nutrition realtime to the unified authority.
exec(compile(open("v216_core_nutrition_realtime_delegation.py", encoding="utf-8").read(), "v216_core_nutrition_realtime_delegation.py", "exec"))

# V20.17 delegate nutrition templates/revisions realtime to V13.2.
exec(compile(open("v217_nutrition_extra_realtime_delegation.py", encoding="utf-8").read(), "v217_nutrition_extra_realtime_delegation.py", "exec"))

# V20.18 delegate agenda realtime to the unified authority.
exec(compile(open("v218_agenda_realtime_delegation.py", encoding="utf-8").read(), "v218_agenda_realtime_delegation.py", "exec"))

# V20.19 consolidate profile render work into the V14 authority.
exec(compile(open("v219_profile_render_wrapper_consolidation.py", encoding="utf-8").read(), "v219_profile_render_wrapper_consolidation.py", "exec"))

# V20.20 consolidate V17.7 tracking repair wrappers into V19.2.
exec(compile(open("v220_tracking_repair_wrapper_consolidation.py", encoding="utf-8").read(), "v220_tracking_repair_wrapper_consolidation.py", "exec"))

# V20.21 remove the duplicate V11.9 profile cleanup render wrapper.
exec(compile(open("v221_general_repair_render_consolidation.py", encoding="utf-8").read(), "v221_general_repair_render_consolidation.py", "exec"))

# V20.22 integrate the V15.8 fluid render transaction into V17.8.
exec(compile(open("v222_fluid_render_transaction_consolidation.py", encoding="utf-8").read(), "v222_fluid_render_transaction_consolidation.py", "exec"))

# V20.23 professional visual foundation; CSS-only/runtime-topology neutral.
exec(compile(open("v223_professional_ui_foundation.py", encoding="utf-8").read(), "v223_professional_ui_foundation.py", "exec"))

# V20.24 professional student home using existing data/actions only.
exec(compile(open("v224_student_dashboard_pro.py", encoding="utf-8").read(), "v224_student_dashboard_pro.py", "exec"))

# V20.25 professional coach dashboard preserving V80 attention/feed authority.
exec(compile(open("v225_coach_dashboard_pro.py", encoding="utf-8").read(), "v225_coach_dashboard_pro.py", "exec"))

# V20.26 professional canonical coach-student profile / Resumen 360.
exec(compile(open("v226_profile_360_pro.py", encoding="utf-8").read(), "v226_profile_360_pro.py", "exec"))

# V20.27 professional workout experience; visual-only.
exec(compile(open("v227_workout_experience_pro.py", encoding="utf-8").read(), "v227_workout_experience_pro.py", "exec"))

# V20.28 professional tracking/progress experience; visual-only.
exec(compile(open("v228_tracking_progress_pro.py", encoding="utf-8").read(), "v228_tracking_progress_pro.py", "exec"))

# V20.29 professional nutrition experience; visual-only.
exec(compile(open("v229_nutrition_pro.py", encoding="utf-8").read(), "v229_nutrition_pro.py", "exec"))

# V20.30 professional agenda/alerts experience; visual-only, payments untouched.
exec(compile(open("v230_agenda_alerts_pro.py", encoding="utf-8").read(), "v230_agenda_alerts_pro.py", "exec"))

# V20.31 professional routine builder/library experience; visual-only.
exec(compile(open("v231_routine_builder_pro.py", encoding="utf-8").read(), "v231_routine_builder_pro.py", "exec"))

# V20.32 reconcile any previously pending workout before another can start.
exec(compile(open("v232_pending_session_recovery.py", encoding="utf-8").read(), "v232_pending_session_recovery.py", "exec"))

# V20.33 static UX states/accessibility; no runtime topology changes.
exec(compile(open("v233_ux_states_accessibility.py", encoding="utf-8").read(), "v233_ux_states_accessibility.py", "exec"))

# V20.35 functional coach workflow upgrade using existing dashboard/feed data.
exec(compile(open("v235_coach_workflow_pro.py", encoding="utf-8").read(), "v235_coach_workflow_pro.py", "exec"))

# V20.36 coach work queue: sort + next priority using existing data.
exec(compile(open("v236_coach_work_queue.py", encoding="utf-8").read(), "v236_coach_work_queue.py", "exec"))

# V20.37 per-student coach review baseline + changes/decisions.
exec(compile(open("v237_coach_review_hub.py", encoding="utf-8").read(), "v237_coach_review_hub.py", "exec"))

# V20.38 dashboard review loop: new changes / unreviewed / current.
exec(compile(open("v238_coach_review_loop.py", encoding="utf-8").read(), "v238_coach_review_loop.py", "exec"))

# V20.39 bounded coach decision/review history inside student snapshot.
exec(compile(open("v239_coach_decision_log.py", encoding="utf-8").read(), "v239_coach_decision_log.py", "exec"))

# V20.40 per-student coach review cadence and overdue-review queue.
exec(compile(open("v240_coach_review_cadence.py", encoding="utf-8").read(), "v240_coach_review_cadence.py", "exec"))

# V20.41 structured student feedback attached to confirmed workout session.
exec(compile(open("v241_student_session_feedback.py", encoding="utf-8").read(), "v241_student_session_feedback.py", "exec"))

# V20.42 coach response + visible next step for session feedback.
exec(compile(open("v242_coach_session_feedback_response.py", encoding="utf-8").read(), "v242_coach_session_feedback_response.py", "exec"))

# V20.43 student journey + session-feedback coach priority.
exec(compile(open("v243_student_journey_feedback_priority.py", encoding="utf-8").read(), "v243_student_journey_feedback_priority.py", "exec"))

# V20.44 unified workout/session feedback/coach response history.
exec(compile(open("v244_unified_session_history.py", encoding="utf-8").read(), "v244_unified_session_history.py", "exec"))

# V20.45 student smart action hub + coach-response acknowledgement.
exec(compile(open("v245_student_action_hub.py", encoding="utf-8").read(), "v245_student_action_hub.py", "exec"))

# V20.46 confirmed check-in success modal after cloud persistence.
exec(compile(open("v246_confirmed_checkin_success.py", encoding="utf-8").read(), "v246_confirmed_checkin_success.py", "exec"))

# V20.47 professional coach review + student reply for weekly check-ins.
exec(compile(open("v247_professional_checkin_review.py", encoding="utf-8").read(), "v247_professional_checkin_review.py", "exec"))

# V20.48 Student Home check-in reply + acknowledgement back to Coach.
exec(compile(open("v248_checkin_reply_loop.py", encoding="utf-8").read(), "v248_checkin_reply_loop.py", "exec"))

# V20.49 four-week performance/adherence/wellness progress pulse.
exec(compile(open("v249_progress_pulse.py", encoding="utf-8").read(), "v249_progress_pulse.py", "exec"))

# V20.50 selected-student operational weekly brief in Resumen 360.
exec(compile(open("v250_coach_weekly_brief.py", encoding="utf-8").read(), "v250_coach_weekly_brief.py", "exec"))

# V20.51 populated warm-up / activation / stretching library.
exec(compile(open("v251_warmup_mobility_library.py", encoding="utf-8").read(), "v251_warmup_mobility_library.py", "exec"))

# V20.52 consolidated coach priority center.
exec(compile(open("v252_coach_priority_center.py", encoding="utf-8").read(), "v252_coach_priority_center.py", "exec"))

# V20.53 unified Student Home workout/feedback/check-in/coach flow.
exec(compile(open("v253_student_week_flow.py", encoding="utf-8").read(), "v253_student_week_flow.py", "exec"))

# V20.54 per-exercise strength/hypertrophy performance progress.
exec(compile(open("v254_exercise_performance_progress.py", encoding="utf-8").read(), "v254_exercise_performance_progress.py", "exec"))

# V20.55 mobile geometry/input/modal stability hardening.
exec(compile(open("v255_mobile_stability_pass.py", encoding="utf-8").read(), "v255_mobile_stability_pass.py", "exec"))

# V20.56 final consolidation/authority gate; removes obsolete Home DOM pass.
exec(compile(open("v256_consolidation_gate.py", encoding="utf-8").read(), "v256_consolidation_gate.py", "exec"))

# V20.57 adds a dedicated weekly priority to the professional check-in review.
exec(compile(open("v257_checkin_weekly_focus.py", encoding="utf-8").read(), "v257_checkin_weekly_focus.py", "exec"))

# V20.58 keeps the latest reviewed coach plan visible on Student Home.
exec(compile(open("v258_student_current_plan.py", encoding="utf-8").read(), "v258_student_current_plan.py", "exec"))

# V20.59 coach action center 2.0 + operational calendar.
exec(compile(open("v259_coach_action_calendar.py", encoding="utf-8").read(), "v259_coach_action_calendar.py", "exec"))

# V20.60 fast four-week coach snapshot per athlete.
exec(compile(open("v260_coach_four_week_snapshot.py", encoding="utf-8").read(), "v260_coach_four_week_snapshot.py", "exec"))

# Safe zero-cost local staging: synthetic/demo data only, cloud hard-disabled.
if APP_ENV == "staging-local":
    exec(compile(open("staging_local_guard.py", encoding="utf-8").read(), "staging_local_guard.py", "exec"))

# V12.7 centralized release + PWA update system
exec(compile(open("v127_release_system.py", encoding="utf-8").read(), "v127_release_system.py", "exec"))
