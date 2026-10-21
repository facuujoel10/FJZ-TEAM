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
        raise RuntimeError("V20.64 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.64 no script change "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-preproduction-hardening" content="20.63"',
    "cloudConfirmationBeforeSuccess:true",
    "confirmedCheckinSuccess:true",
    "__fjzRoutineSavingV200",
    "v207-save-state"
]:
    if marker not in html:
        raise RuntimeError("V20.64 missing prerequisite: "+marker)

# ---------------------------------------------------------
# 1) ROUTINE: green confirmation only after the routine sync
#    authority finishes successfully.
# ---------------------------------------------------------
def patch_v200(body):
    old="""  function finishRoutineMutationV200(){
    routineDirtyV200=false;
    window.__fjzRoutineSavingV200=false;
    try{cloudLastWrite=Date.now()}catch(_e){}
    if(deferredRefreshV200){
      deferredRefreshV200=false;
      setTimeout(()=>window.refreshCloudFromRealtime?.(),300);
    }
  }"""
    new="""  function finishRoutineMutationV200(){
    const wasDirty=routineDirtyV200;
    routineDirtyV200=false;
    window.__fjzRoutineSavingV200=false;
    try{cloudLastWrite=Date.now()}catch(_e){}
    if(wasDirty){
      try{window.__fjzQuickSavedV264?.('Rutina guardada')}catch(_e){}
    }
    if(deferredRefreshV200){
      deferredRefreshV200=false;
      setTimeout(()=>window.refreshCloudFromRealtime?.(),300);
    }
  }"""
    if body.count(old)!=1:
        raise RuntimeError("V20.64 routine finish anchor mismatch: "+str(body.count(old)))
    return body.replace(old,new,1)

html=edit_script(html,"v200StabilityAuthorityRuntime",patch_v200)

# ---------------------------------------------------------
# 2) COACH local snapshot writes: wait for the snapshot cloud
#    sync before showing a green success state.
# ---------------------------------------------------------
def patch_v175(body):
    sig1="  window.saveCoachReviewDecisionV239=function(){"
    if body.count(sig1)!=1:
        raise RuntimeError("V20.64 coach decision signature mismatch")
    body=body.replace(sig1,"  window.saveCoachReviewDecisionV239=async function(){",1)

    tail1="""    saveState();
    closeModal?.();
    renderReviewHubV237(reviewCurrentV237);
    toast?.('Revisión y decisión guardadas');
  };"""
    repl1="""    saveState();
    let cloudOkV264=true;
    if(cloudEnabled&&supabaseClient){
      try{
        const authOk=await window.__fjzEnsureFreshAuthV194?.(false);
        if(authOk===false)throw new Error('auth_not_fresh');
        await window.syncCloudNow?.();
      }catch(e){
        cloudOkV264=false;
        console.warn('TEAM FJZ V20.64 coach review sync pending',e);
      }
    }
    closeModal?.();
    renderReviewHubV237(reviewCurrentV237);
    if(cloudOkV264)window.__fjzConfirmSavedV264?.('Revisión guardada','La decisión y la revisión quedaron confirmadas.');
    else toast?.('Revisión guardada localmente · sincronización pendiente');
  };"""
    if body.count(tail1)!=1:
        raise RuntimeError("V20.64 coach decision tail mismatch")
    body=body.replace(tail1,repl1,1)

    sig2="  window.saveSessionFeedbackCoachV242=function(sessionId){"
    if body.count(sig2)!=1:
        raise RuntimeError("V20.64 session feedback signature mismatch")
    body=body.replace(sig2,"  window.saveSessionFeedbackCoachV242=async function(sessionId){",1)

    tail2="""    saveState();
    closeModal?.();
    renderSessionFeedbackCoachV242();
    toast?.('Feedback revisado y devolución guardada');
  };"""
    repl2="""    saveState();
    let cloudOkV264=true;
    if(cloudEnabled&&supabaseClient){
      try{
        const authOk=await window.__fjzEnsureFreshAuthV194?.(false);
        if(authOk===false)throw new Error('auth_not_fresh');
        await window.syncCloudNow?.();
      }catch(e){
        cloudOkV264=false;
        console.warn('TEAM FJZ V20.64 session feedback sync pending',e);
      }
    }
    closeModal?.();
    renderSessionFeedbackCoachV242();
    if(cloudOkV264)window.__fjzConfirmSavedV264?.('Feedback guardado','La devolución quedó confirmada y disponible para el alumno.');
    else toast?.('Feedback guardado localmente · sincronización pendiente');
  };"""
    if body.count(tail2)!=1:
        raise RuntimeError("V20.64 session feedback tail mismatch")
    body=body.replace(tail2,repl2,1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

# ---------------------------------------------------------
# 3) Day delete was historically local-first and outside the
#    V20.0 routine wrapper. Confirm cloud sync before green.
# ---------------------------------------------------------
def patch_v152(body):
    sig="  window.deleteDayV152=function(i){"
    if body.count(sig)!=1:
        raise RuntimeError("V20.64 delete day signature mismatch")
    body=body.replace(sig,"  window.deleteDayV152=async function(i){",1)

    old="""    // Historical sessions are intentionally preserved.
    saveState();
    closeModal();
    render();
    toast('Día eliminado: '+removed.name);
  };"""
    new="""    // Historical sessions are intentionally preserved.
    saveState();
    let cloudOkV264=true;
    if(cloudEnabled&&supabaseClient){
      try{
        const authOk=await window.__fjzEnsureFreshAuthV194?.(false);
        if(authOk===false)throw new Error('auth_not_fresh');
        await window.syncCloudNow?.();
      }catch(e){
        cloudOkV264=false;
        console.warn('TEAM FJZ V20.64 day delete sync pending',e);
      }
    }
    closeModal();
    render();
    if(cloudOkV264)window.__fjzQuickSavedV264?.('Rutina guardada');
    else toast('Día eliminado localmente · sincronización pendiente');
  };"""
    if body.count(old)!=1:
        raise RuntimeError("V20.64 delete day tail mismatch")
    return body.replace(old,new,1)

html=edit_script(html,"v152DayDeleteRuntime",patch_v152)

# ---------------------------------------------------------
# 4) Existing cloud-confirmed success toasts -> consistent
#    TEAM FJZ green confirmation surfaces.
# ---------------------------------------------------------
def replace_toast_literal(doc,msg,replacement):
    pat=re.compile(r"toast(?:\?\.)?\(\s*(['\"])" + re.escape(msg) + r"\1\s*\)")
    new,n=pat.subn(replacement,doc)
    return new,n

major={
    "Medición guardada":("Medición guardada","Tus medidas quedaron confirmadas en la nube."),
    "Medición actualizada":("Medición actualizada","Los cambios quedaron confirmados en la nube."),
    "Perfil actualizado":("Perfil actualizado","Los datos del alumno quedaron confirmados en la nube."),
    "Datos actualizados":("Datos guardados","Tus datos quedaron confirmados en la nube."),
    "Feedback guardado":("Feedback guardado","La devolución quedó confirmada en la nube."),
    "Plan creado":("Plan creado","El plan nutricional quedó confirmado en la nube."),
    "Plan nutricional guardado":("Plan nutricional guardado","Los cambios del plan quedaron confirmados en la nube."),
    "Plantilla guardada":("Plantilla guardada","La plantilla quedó confirmada en la nube."),
    "Foto guardada":("Foto guardada","La foto quedó confirmada en tu progreso."),
    "Foto reemplazada":("Foto actualizada","La nueva foto quedó confirmada en la nube."),
    "Foto de perfil actualizada":("Foto de perfil guardada","La nueva foto quedó confirmada en la nube."),
    "Video técnico guardado":("Video guardado","El video técnico quedó confirmado en la nube."),
    "Agenda semanal guardada":("Agenda guardada","La agenda semanal quedó confirmada en la nube."),
    "Recordatorio guardado":("Recordatorio guardado","El recordatorio quedó confirmado en la nube."),
    "Alerta enviada":("Alerta enviada","La alerta quedó guardada y disponible para el alumno."),
    "Receta agregada":("Receta guardada","La receta quedó confirmada en la nube."),
    "Datos importados a la nube":("Datos guardados","La importación quedó confirmada en la nube."),
}

replacement_counts={}
for msg,(title,copy) in major.items():
    expr="window.__fjzConfirmSavedV264?.("+repr(title)+","+repr(copy)+")"
    html,n=replace_toast_literal(html,msg,expr)
    replacement_counts[msg]=n

quick={
    "Agregado al registro":"Registro guardado",
    "Opción registrada":"Comida guardada",
    "Comida completa registrada":"Comida guardada",
    "Registro eliminado":"Cambio guardado",
    "Comida eliminada":"Cambio guardado",
    "Recordatorio eliminado":"Cambio guardado",
    "Foto eliminada":"Cambio guardado",
    "Video eliminado":"Cambio guardado",
    "Plantilla eliminada":"Cambio guardado",
}
for msg,title in quick.items():
    expr="window.__fjzQuickSavedV264?.("+repr(title)+")"
    html,n=replace_toast_literal(html,msg,expr)
    replacement_counts[msg]=n

dynamic=[
    ("toast(checked?'Hábito marcado':'Hábito desmarcado')",
     "window.__fjzQuickSavedV264?.(checked?'Hábito guardado':'Hábito actualizado')"),
    ("toast(enabled?'Plan guardado · registro activado':'Plan guardado · registro desactivado')",
     "window.__fjzConfirmSavedV264?.('Plan guardado',enabled?'Registro de comidas activado.':'Registro de comidas desactivado.')"),
    ("toast(url?'Spotify guardado':'Spotify eliminado')",
     "window.__fjzConfirmSavedV264?.(url?'Spotify guardado':'Spotify eliminado','La configuración quedó confirmada en la nube.')"),
    ("toast(url?'Música guardada':'Música eliminada')",
     "window.__fjzConfirmSavedV264?.(url?'Música guardada':'Música eliminada','La configuración quedó confirmada en la nube.')"),
    ("toast(url?'Música general guardada para todos':'Música general eliminada')",
     "window.__fjzConfirmSavedV264?.(url?'Música general guardada':'Música general eliminada','La configuración quedó confirmada en la nube.')"),
]
for old,new in dynamic:
    if old in html:
        html=html.replace(old,new)

# ---------------------------------------------------------
# 5) Shared confirmation UI: full modal for deliberate saves,
#    compact green notice for rapid logging/routine operations.
#    CSS animation avoids adding timers/listeners.
# ---------------------------------------------------------
css=r"""
/* TEAM FJZ · V20.64 CONFIRMED SAVE FEEDBACK */
.v264-confirmed-save .v207-save-icon.success{
  box-shadow:0 0 0 7px rgba(59,213,138,.07),0 10px 28px rgba(0,0,0,.18);
}
.v264-quick-save{
  position:fixed;
  left:50%;
  bottom:max(82px,calc(68px + env(safe-area-inset-bottom)));
  z-index:9999;
  display:flex;
  align-items:center;
  gap:9px;
  max-width:min(92vw,440px);
  padding:10px 14px;
  border:1px solid rgba(59,213,138,.34);
  border-radius:12px;
  background:#101814;
  box-shadow:0 12px 30px rgba(0,0,0,.24);
  color:#eefbf4;
  opacity:0;
  transform:translate(-50%,10px);
  pointer-events:none;
}
.v264-quick-save>span{
  display:grid;
  place-items:center;
  width:24px;height:24px;
  flex:0 0 24px;
  border-radius:50%;
  background:rgba(59,213,138,.15);
  color:#63e7a5;
  font-size:14px;
  font-weight:950;
}
.v264-quick-save>b{
  font-size:10px;
  line-height:1.25;
  letter-spacing:.01em;
}
.v264-quick-save.show{
  animation:v264SaveConfirmation 2.15s ease both;
}
@keyframes v264SaveConfirmation{
  0%{opacity:0;transform:translate(-50%,10px)}
  12%,78%{opacity:1;transform:translate(-50%,0)}
  100%{opacity:0;transform:translate(-50%,-4px)}
}
@media(prefers-reduced-motion:reduce){
  .v264-quick-save.show{animation-duration:1.7s!important}
}
"""
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.64 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

runtime=r"""
<script id="v264ConfirmedSaveFeedbackRuntime">
(function(){
  function safeV264(v){
    return String(v??'')
      .replace(/&/g,'&amp;')
      .replace(/</g,'&lt;')
      .replace(/>/g,'&gt;')
      .replace(/"/g,'&quot;')
      .replace(/'/g,'&#39;');
  }

  window.__fjzConfirmSavedV264=function(title,copy){
    const t=safeV264(title||'Guardado con éxito');
    const c=safeV264(copy||'Los cambios quedaron guardados correctamente.');
    try{
      showModal(
        '<div class="v207-save-state v264-confirmed-save">'+
          '<div class="v207-save-icon success">✓</div>'+
          '<div class="v207-save-title">'+t+'</div>'+
          '<div class="v207-save-copy">'+c+'</div>'+
          '<div class="v207-save-actions"><button class="btn primary" onclick="closeModal()">Listo</button></div>'+
        '</div>'
      );
      return true;
    }catch(e){
      try{toast?.('✓ '+String(title||'Guardado con éxito'))}catch(_e){}
      return false;
    }
  };

  window.__fjzQuickSavedV264=function(title){
    let n=document.getElementById('v264QuickSaved');
    if(!n){
      n=document.createElement('div');
      n.id='v264QuickSaved';
      n.className='v264-quick-save';
      n.setAttribute('role','status');
      n.setAttribute('aria-live','polite');
      document.body.appendChild(n);
    }
    n.innerHTML='<span>✓</span><b>'+safeV264(title||'Guardado con éxito')+'</b>';
    n.classList.remove('show');
    void n.offsetWidth;
    n.classList.add('show');
    return true;
  };

  window.__fjzV264={
    version:'20.64',
    greenConfirmedSaveFeedback:true,
    workoutUsesExistingConfirmedSuccess:true,
    checkinUsesExistingConfirmedSuccess:true,
    routineSuccessAfterCloudSync:true,
    majorSaveModal:true,
    quickSaveGreenNotice:true,
    noFalseGreenOnPendingSync:true
  };
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-confirmed-save-feedback" content="20.64">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.64 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-confirmed-save-feedback" content="20.64"',
    "v264ConfirmedSaveFeedbackRuntime",
    "__fjzConfirmSavedV264","__fjzQuickSavedV264",
    "greenConfirmedSaveFeedback:true",
    "routineSuccessAfterCloudSync:true",
    "noFalseGreenOnPendingSync:true",
    "Rutina guardada",
    "Revisión guardada",
    "Feedback guardado"
]:
    if marker not in html:
        raise RuntimeError("V20.64 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.64 confirmed save feedback")
print("V20.64 BEFORE:",before)
print("V20.64 AFTER:",after)
print("V20.64 REPLACEMENTS:",replacement_counts)
print("V20.64 major saves use green check modal; quick saves use green compact confirmation")
