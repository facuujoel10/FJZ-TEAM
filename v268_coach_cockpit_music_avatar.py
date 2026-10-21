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
        raise RuntimeError("V20.68 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.68 no script change "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-coach-profile-input-contracts" content="20.67"',
    "coachFourWeekSnapshot:true",
    "coachWeeklyBrief:true",
    "function ensureCoachHeroFrameV175()",
    "window.renderCoachSummary=function()",
]:
    if marker not in html:
        raise RuntimeError("V20.68 missing prerequisite: "+marker)

# ================================================================
# 1) REMOVE MUSIC/SPOTIFY FEATURE FROM ACTIVE APP CODE
# ================================================================
# V6.7 per-athlete Spotify block.
start="// ===== TEAM FJZ V8.3 · SPOTIFY / MÚSICA ====="
end="// ===== TEAM FJZ V8.3 · CONSEJOS SIN CHECKLIST + MÚSICA VISIBLE ====="
pat=re.compile(re.escape(start)+r".*?(?="+re.escape(end)+r")",re.S)
html,n=pat.subn("",html,count=1)
if n not in (0,1):
    raise RuntimeError("V20.68 legacy Spotify block removal mismatch: "+str(n))

# V6.8 Spotify subsection + all music navigation overrides.
start2="// --- Spotify: búsqueda robusta de la ficha y pestaña propia ---"
end2="// ===== TEAM FJZ V8.3 · MÚSICA GLOBAL DEL COACH ====="
pat2=re.compile(re.escape(start2)+r".*?(?="+re.escape(end2)+r")",re.S)
html,n=pat2.subn("",html,count=1)
if n not in (0,1):
    raise RuntimeError("V20.68 V6.8 music subsection removal mismatch: "+str(n))

# V6.9 global music / coach_media_settings.
start3="// ===== TEAM FJZ V8.3 · MÚSICA GLOBAL DEL COACH ====="
end3="// ===== TEAM FJZ V8.3 · FOTO DE PERFIL + RECETAS ====="
pat3=re.compile(re.escape(start3)+r".*?(?="+re.escape(end3)+r")",re.S)
html,n=pat3.subn("",html,count=1)
if n not in (0,1):
    raise RuntimeError("V20.68 global music block removal mismatch: "+str(n))

# V20.14 delegation marker is obsolete after feature removal.
html,n=re.subn(r'<script[^>]*\bid=["\']v214GlobalMusicRealtimeDelegationRuntime["\'][^>]*>.*?</script>\s*','',html,count=1,flags=re.S|re.I)
if n not in (0,1):
    raise RuntimeError("V20.68 V20.14 marker removal mismatch: "+str(n))

# Remove coach_media_settings from unified realtime and its invalidation.
def patch_v132(body):
    old="""    if(table==='coach_media_settings'){
      try{coachMediaV69=null}catch(e){}
    }
"""
    if body.count(old)!=1:
        raise RuntimeError("V20.68 music invalidation mismatch")
    body=body.replace(old,"",1)
    old_list="'athlete_schedule','athlete_reminders','coach_media_settings','exercise_media'"
    new_list="'athlete_schedule','athlete_reminders','exercise_media'"
    if body.count(old_list)!=1:
        raise RuntimeError("V20.68 unified realtime music table mismatch")
    return body.replace(old_list,new_list,1)

html=edit_script(html,"v132CoachAssistantRealtime",patch_v132)

# ================================================================
# 2) COACH COCKPIT: more information + action-oriented assistance
# ================================================================
def patch_v175(body):
    anchor="  async function hydrateSummaryV175(){"
    if body.count(anchor)!=1:
        raise RuntimeError("V20.68 coach cockpit helper anchor mismatch")

    helpers=r"""
  /* ---------- Coach Cockpit V20.68 ---------- */
  function daysSinceV268(value){
    if(!value)return 999;
    const t=Date.parse(value);
    if(!Number.isFinite(t))return 999;
    return Math.max(0,Math.floor((Date.now()-t)/86400000));
  }

  function avgV268(rows,key){
    const vals=(rows||[]).map(x=>Number(x?.[key])).filter(Number.isFinite);
    return vals.length?vals.reduce((a,b)=>a+b,0)/vals.length:null;
  }

  function deltaV268(a,b,suffix=''){
    const x=Number(a),y=Number(b);
    if(!Number.isFinite(x)||!Number.isFinite(y))return '—';
    const d=x-y;
    if(Math.abs(d)<.05)return '0'+suffix;
    const v=Math.abs(d)<10?round1(d):Math.round(d);
    return (d>0?'+':'')+v+suffix;
  }

  function coachCockpitStateV268(s,latest){
    const checks=trackingCache?.checkins||[];
    const prev=checks[1]||null;
    const ms=trackingCache?.measurements||[];
    const sessions7=recentSessionsV175(s,7);
    const sessions28=recentSessionsV175(s,28);
    const planned=Math.max(0,Number(s?.plannedPerWeek)||s?.days?.length||0);
    const planPct=planned?Math.min(150,Math.round(sessions7.length/planned*100)):null;
    const checkinAge=latest?daysSinceV268(latest.week_start||latest.submitted_at):999;
    const pendingExercise=pendingFeedbackV175()?.length||0;
    const pendingSession=Number(window.__fjzPendingSessionFeedbackCountV242?.(s)||0);
    const ath=coachAthleteV175?.()||{};
    const nutrition=nutritionSummaryV175?.()||{active:false};
    const agenda=agendaSummaryV175?.(ath?.id)||{total:0,overdue:0};

    const profileFields=[
      ['Altura',ath?.height_cm],
      ['Nacimiento',ath?.birth_date],
      ['Ocupación',ath?.occupation_study],
      ['Inicio del plan',ath?.start_date],
      ['Objetivo',ath?.goal||s?.goal]
    ];
    const missingProfile=profileFields.filter(([,v])=>v==null||String(v).trim()==='').map(([k])=>k);

    const coverageParts=[
      !!latest,
      sessions28.length>0,
      ms.length>0,
      !!nutrition.active,
      missingProfile.length<=1,
      !!(ath?.id)
    ];
    const coverage=Math.round(coverageParts.filter(Boolean).length/coverageParts.length*100);

    const signals=[];
    const add=(tone,title,copy,tab,label)=>signals.push({tone,title,copy,tab,label});

    if(pendingSession>0)add('warn','Feedback de sesión pendiente',
      pendingSession+' devolución'+(pendingSession===1?'':'es')+' esperan tu respuesta.','summary','Revisar feedback');
    if(pendingExercise>0)add('warn','Comentarios de ejercicios',
      pendingExercise+' comentario'+(pendingExercise===1?'':'s')+' pendiente'+(pendingExercise===1?'':'s')+' de revisión.','routine','Abrir rutina');
    if(latest&&!latest.reviewed_at)add('warn','Check-in sin revisar',
      'El último check-in todavía no tiene revisión del Coach.','tracking','Revisar check-in');
    if(checkinAge>10)add('info','Check-in desactualizado',
      'Pasaron '+checkinAge+' días desde el último check-in registrado.','tracking','Abrir seguimiento');
    if(latest?.recovery_level!=null&&Number(latest.recovery_level)<=4)add('warn','Recuperación baja',
      'Recuperación '+latest.recovery_level+'/10. Revisá contexto, descanso y carga antes de ajustar.','tracking','Ver contexto');
    if(latest?.energy_level!=null&&Number(latest.energy_level)<=4)add('info','Energía baja',
      'Energía '+latest.energy_level+'/10 en el último check-in.','tracking','Ver check-in');
    if(latest?.stress_level!=null&&Number(latest.stress_level)>=8)add('warn','Estrés alto',
      'Estrés '+latest.stress_level+'/10. Conviene observar tendencia antes de modificar el plan.','tracking','Ver tendencia');
    if(planned&&sessions7.length<Math.max(1,planned-1))add('info','Frecuencia debajo del plan',
      sessions7.length+' de '+planned+' sesiones planificadas en los últimos 7 días.','routine','Revisar semana');
    if(Number(agenda?.overdue||0)>0)add('warn','Agenda vencida',
      agenda.overdue+' elemento'+(agenda.overdue===1?'':'s')+' vencido'+(agenda.overdue===1?'':'s')+'.','agenda','Abrir agenda');
    if(!nutrition.active)add('info','Nutrición sin plan activo',
      'No figura un plan nutricional activo en la ficha.','nutrition','Abrir nutrición');
    if(missingProfile.length)add('neutral','Ficha incompleta',
      'Faltan: '+missingProfile.join(', ')+'.','summary','Completar ficha');
    if(!signals.length)add('good','Seguimiento estable',
      'No aparece una acción prioritaria con los datos disponibles.','progress','Ver evolución');

    const wellness={
      sleep:latest?.sleep_quality??null,
      energy:latest?.energy_level??null,
      recovery:latest?.recovery_level??null,
      stress:latest?.stress_level??null,
      adherence:latest?.adherence_level??null,
      avg4:avgV268(checks.slice(0,4),'adherence_level')
    };

    return {
      sessions7:sessions7.length,sessions28:sessions28.length,planned,planPct,
      checkinAge,pendingExercise,pendingSession,coverage,signals:signals.slice(0,4),
      latest,prev,wellness,missingProfile,nutrition,agenda
    };
  }

  function cockpitMetricV268(label,value,sub=''){
    return '<div class="v268-metric"><span>'+esc(label)+'</span><strong>'+esc(String(value??'—'))+'</strong>'+
      (sub?'<small>'+esc(sub)+'</small>':'')+'</div>';
  }

  function renderCoachCockpitV268(s,latest){
    const host=el('v268CoachCockpit');if(!host)return;
    const x=coachCockpitStateV268(s,latest);
    const checkin=x.checkinAge>=999?'Sin registro':x.checkinAge===0?'Hoy':x.checkinAge===1?'Ayer':x.checkinAge+' d';
    const plan=x.planPct==null?'—':x.planPct+'%';
    const rec=x.wellness.recovery!=null?x.wellness.recovery+'/10':'—';
    const stress=x.wellness.stress!=null?x.wellness.stress+'/10':'—';
    const first=x.signals[0];

    const changes=x.prev&&latest
      ?'<div class="v268-change-grid">'+
        cockpitMetricV268('Adherencia',deltaV268(latest.adherence_level,x.prev.adherence_level,' pts'),'vs anterior')+
        cockpitMetricV268('Energía',deltaV268(latest.energy_level,x.prev.energy_level,' pts'),'vs anterior')+
        cockpitMetricV268('Recuperación',deltaV268(latest.recovery_level,x.prev.recovery_level,' pts'),'vs anterior')+
       '</div>'
      :'<div class="v268-empty-note">Todavía no hay dos check-ins comparables.</div>';

    host.innerHTML=
      '<div class="v268-cockpit-head"><div><div class="v268-kicker">COACH COCKPIT</div><h4>Lectura operativa del alumno</h4>'+
      '<p>Lo importante de entrenamiento, check-in, adherencia y seguimiento antes de tomar una decisión.</p></div>'+
      '<span class="badge '+(first.tone==='warn'?'amber':first.tone==='good'?'green':'blue')+'">'+esc(first.title)+'</span></div>'+
      '<div class="v268-metrics">'+
        cockpitMetricV268('Entrenos 7 días',x.sessions7,x.planned?x.planned+' planificados':'Sin frecuencia')+
        cockpitMetricV268('Entrenos 28 días',x.sessions28,'Últimas 4 semanas')+
        cockpitMetricV268('Cumplimiento semanal',plan,'Sesiones registradas / plan')+
        cockpitMetricV268('Último check-in',checkin,'Actualización')+
        cockpitMetricV268('Recuperación',rec,'Último check-in')+
        cockpitMetricV268('Estrés',stress,'Último check-in')+
        cockpitMetricV268('Cobertura de datos',x.coverage+'%','Calidad de lectura')+
      '</div>'+
      '<div class="v268-cockpit-grid">'+
        '<section class="v268-panel v268-actions"><div class="v268-panel-head"><strong>Qué mirar ahora</strong><span>'+x.signals.length+' señal'+(x.signals.length===1?'':'es')+'</span></div>'+
          x.signals.map((a,i)=>'<div class="v268-signal '+esc(a.tone)+'"><div><span>'+(i+1)+'</span><strong>'+esc(a.title)+'</strong><p>'+esc(a.copy)+'</p></div>'+
          '<button class="btn small" onclick="openCoachCockpitV268(\''+esc(a.tab)+'\')">'+esc(a.label)+'</button></div>').join('')+
        '</section>'+
        '<section class="v268-panel"><div class="v268-panel-head"><strong>Cambios vs. check-in anterior</strong><span>Tendencia</span></div>'+changes+
          '<div class="v268-mini-context"><span>Sueño</span><b>'+(x.wellness.sleep!=null?esc(String(x.wellness.sleep))+'/10':'—')+'</b>'+
          '<span>Energía</span><b>'+(x.wellness.energy!=null?esc(String(x.wellness.energy))+'/10':'—')+'</b>'+
          '<span>Adherencia</span><b>'+(x.wellness.adherence!=null?esc(String(x.wellness.adherence))+'/10':'—')+'</b></div>'+
        '</section>'+
        '<section class="v268-panel"><div class="v268-panel-head"><strong>Calidad de la ficha</strong><span>'+x.coverage+'%</span></div>'+
          (x.missingProfile.length
            ?'<div class="v268-profile-missing"><p>Datos a completar</p><strong>'+esc(x.missingProfile.join(' · '))+'</strong><button class="btn small" onclick="openEditStudentProfileV114()">Completar ficha</button></div>'
            :'<div class="v268-profile-ok"><strong>Ficha principal completa</strong><p>Los datos básicos necesarios para contextualizar el seguimiento están cargados.</p></div>')+
        '</section>'+
      '</div>';
  }

  window.openCoachCockpitV268=function(tab){
    coachStudentTab=tab||'summary';
    render();
  };

"""
    body=body.replace(anchor,helpers+anchor,1)

    hydrate_anchor="""    renderCoachFourWeekV260(s,latest);
    renderCoachWeeklyBriefV250(s,latest,agenda,nutrition,pending);
"""
    hydrate_repl="""    renderCoachFourWeekV260(s,latest);
    renderCoachWeeklyBriefV250(s,latest,agenda,nutrition,pending);
    renderCoachCockpitV268(s,latest);
"""
    if body.count(hydrate_anchor)!=1:
        raise RuntimeError("V20.68 cockpit hydrate mismatch")
    body=body.replace(hydrate_anchor,hydrate_repl,1)

    section_anchor="""      '<div class="v175-360-section v260-four-week" id="v260CoachFourWeek"><div class="empty">Preparando estado de 4 semanas…</div></div>'+
"""
    section_new="""      '<div class="v175-360-section v268-cockpit" id="v268CoachCockpit"><div class="empty">Preparando lectura operativa…</div></div>'+
""" + section_anchor
    if body.count(section_anchor)!=1:
        raise RuntimeError("V20.68 cockpit section mismatch")
    body=body.replace(section_anchor,section_new,1)

    marker="""    coachProfileCommandCenter:true,
    coachAvatarDirectLinkedProfile:true,
"""
    repl="""    coachProfileCommandCenter:true,
    coachCockpitV268:true,
    coachDecisionSignals:true,
    coachDataCoverage:true,
    coachAvatarDirectLinkedProfile:true,
"""
    if body.count(marker)!=1:
        raise RuntimeError("V20.68 coach marker mismatch")
    return body.replace(marker,repl,1)

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

# ================================================================
# 3) ROBUST AVATAR SURFACE: Coach + Student/View-as-student
# ================================================================
def patch_v176(body):
    old="""    window.__fjzApplyInputRulesV267?.();
    if(studentTrackingActiveV176()||coachTrackingActiveV176())injectMeasurementHistoryV176();
"""
    new="""    window.__fjzApplyInputRulesV267?.();
    window.__fjzApplyProfileUiV268?.();
    if(studentTrackingActiveV176()||coachTrackingActiveV176())injectMeasurementHistoryV176();
"""
    if body.count(old)!=1:
        raise RuntimeError("V20.68 post-render profile UI anchor mismatch")
    return body.replace(old,new,1)

html=edit_script(html,"v176MobileTrackingMealsCleanupRuntime",patch_v176)

runtime=r"""
<script id="v268CoachCockpitAvatarRuntime">
(function(){
  let avatarSeqV268=0;

  function initialsV268(name){
    return String(name||'AL').trim().split(/\s+/).slice(0,2).map(x=>x[0]||'').join('').toUpperCase()||'AL';
  }

  function demoAvatarV268(name){
    const initials=esc(initialsV268(name));
    return '<div class="v268-avatar-demo" aria-label="Avatar demo de '+esc(name||'alumno')+'">'+
      '<div class="v268-avatar-ring"></div><span>'+initials+'</span><small>STAGING</small></div>';
  }

  function fallbackAvatarV268(name){
    return '<div class="v268-avatar-fallback">'+esc(initialsV268(name))+'</div>';
  }

  async function avatarResultV268(userId,name){
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

  function avatarHtmlV268(result,name){
    if(result?.demo)return demoAvatarV268(name);
    if(result?.url)return '<img class="v268-avatar-img" src="'+result.url+'" alt="Foto de perfil de '+esc(name||'alumno')+'">';
    return fallbackAvatarV268(name);
  }

  function avatarStateLabelV268(result){
    if(result?.demo)return 'Foto demo · staging aislado';
    if(result?.state==='loaded')return 'Foto sincronizada';
    if(result?.state==='unlinked')return 'Cuenta sin vincular';
    if(result?.state==='offline')return 'Foto disponible con conexión';
    if(result?.state==='error')return 'No se pudo cargar la foto';
    return 'Sin foto cargada';
  }

  async function applyCoachAvatarV268(seq){
    if(!(currentProfile?.role==='coach'&&mode==='coach'&&coachTab==='student'))return;
    const s=student?.(),ath=cloudAthletes?.get?.(s?.id);
    const slot=el('v175CoachAvatarSlot'),hero=el('view')?.querySelector('.hero');
    if(!s||!slot||!hero)return;
    const result=await avatarResultV268(ath?.user_id,s.name);
    if(seq!==avatarSeqV268||!(currentProfile?.role==='coach'&&mode==='coach'&&coachTab==='student')||student()?.id!==s.id)return;
    slot.innerHTML=avatarHtmlV268(result,s.name);
    slot.dataset.avatarState=result.state;
    let meta=hero.querySelector('.v268-avatar-state');
    if(!meta){
      meta=document.createElement('div');
      meta.className='v268-avatar-state';
      const info=hero.querySelector('.v175-coach-profile-info');
      info?.appendChild(meta);
    }
    if(meta)meta.textContent=avatarStateLabelV268(result);
  }

  async function applyStudentAvatarV268(seq){
    if(!(mode==='student'&&studentTab==='home'))return;
    const s=student?.(),hero=el('view')?.querySelector('.hero');
    if(!s||!hero)return;

    const athlete=cloudAthletes?.get?.(s.id);
    const uid=currentProfile?.role==='student'?currentUser?.id:athlete?.user_id;
    const result=await avatarResultV268(uid,s.name);
    if(seq!==avatarSeqV268||!(mode==='student'&&studentTab==='home')||student()?.id!==s.id)return;

    let panel=el('v268StudentAvatarPanel');
    if(!panel){
      panel=document.createElement('div');
      panel.id='v268StudentAvatarPanel';
      panel.className='v268-student-avatar-panel';
      hero.insertAdjacentElement('afterbegin',panel);
    }
    panel.innerHTML='<div class="v268-student-avatar">'+avatarHtmlV268(result,s.name)+'</div>'+
      '<div><span>PERFIL</span><strong>'+esc(s.name||'Alumno')+'</strong><small>'+esc(avatarStateLabelV268(result))+'</small></div>';
    panel.dataset.avatarState=result.state;

    // Retire older duplicate avatar fragments after the canonical V20.68 panel exists.
    hero.querySelectorAll('#v70StudentProfile').forEach(x=>x.remove());
  }

  window.__fjzApplyProfileUiV268=function(){
    const seq=++avatarSeqV268;
    applyCoachAvatarV268(seq);
    applyStudentAvatarV268(seq);
  };

  window.__fjzApplyProfileUiV268();

  window.__fjzV268={
    version:'20.68',
    musicFeatureRemoved:true,
    coachMediaRealtimeRemoved:true,
    coachCockpitV268:true,
    coachAvatarProductionLinkedProfile:true,
    studentAvatarProductionLinkedProfile:true,
    stagingAvatarClearlyDemo:true,
    noProductionDataInStaging:true
  };
})();
</script>
"""

css=r"""
/* TEAM FJZ · V20.68 COACH COCKPIT + AVATAR SURFACE */
#v175CoachAvatarSlot{
  width:104px!important;height:104px!important;flex-basis:104px!important;border-radius:22px!important;
  display:grid!important;place-items:center!important;background:#0a0b0e!important;overflow:hidden!important
}
#v175CoachAvatarSlot .v268-avatar-img,
.v268-student-avatar .v268-avatar-img{
  width:100%!important;height:100%!important;object-fit:cover!important;object-position:center!important;display:block!important
}
.v268-avatar-fallback,.v268-avatar-demo{
  position:relative;width:100%;height:100%;display:grid;place-items:center;overflow:hidden;
  background:radial-gradient(circle at 30% 20%,rgba(255,62,79,.28),transparent 36%),linear-gradient(145deg,#191b22,#0b0c10);
  color:#fff;font-weight:950;letter-spacing:-.04em
}
.v268-avatar-fallback{font-size:24px}
.v268-avatar-demo span{position:relative;z-index:2;font-size:24px}
.v268-avatar-demo small{
  position:absolute;left:0;right:0;bottom:8px;z-index:2;text-align:center;color:#aab0bb;
  font-size:6px;font-weight:900;letter-spacing:.16em
}
.v268-avatar-ring{
  position:absolute;inset:11px;border:1px solid rgba(255,65,82,.40);border-radius:18px;
  box-shadow:inset 0 0 24px rgba(255,38,57,.08)
}
.v268-avatar-state{
  margin-top:7px;color:#8e949f;font-size:8px;font-weight:760;line-height:1.35
}

.v268-student-avatar-panel{
  display:grid;grid-template-columns:72px minmax(0,1fr);gap:12px;align-items:center;
  min-width:255px;padding:10px 12px;border:1px solid #30343c;border-radius:15px;background:#0e0f13
}
.v268-student-avatar{width:72px;height:72px;border-radius:15px;overflow:hidden}
.v268-student-avatar-panel>div:last-child>span{
  display:block;color:#7f8590;font-size:7px;font-weight:900;letter-spacing:.12em
}
.v268-student-avatar-panel strong{display:block;margin-top:4px;color:#fff;font-size:14px;font-weight:920}
.v268-student-avatar-panel small{display:block;margin-top:5px;color:#9298a3;font-size:8px;line-height:1.35}

.v268-cockpit{
  border-color:rgba(255,54,72,.24)!important;
  background:
    radial-gradient(circle at 100% 0,rgba(255,38,57,.06),transparent 30%),
    linear-gradient(145deg,rgba(255,38,57,.035),transparent 48%),#101116!important
}
.v268-cockpit-head{
  display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:12px
}
.v268-kicker{
  color:#ff6b79;font-size:7px;font-weight:950;letter-spacing:.14em
}
.v268-cockpit-head h4{margin:4px 0 0;color:#f6f7f9;font-size:17px;font-weight:930;letter-spacing:-.02em}
.v268-cockpit-head p{margin:5px 0 0;color:#969ba6;font-size:9px;line-height:1.5;max-width:650px}
.v268-metrics{
  display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:7px
}
.v268-metric{
  min-width:0;padding:10px;border:1px solid #2a2e36;border-radius:11px;background:#0d0e12
}
.v268-metric span{
  display:block;color:#7f8590;font-size:6.5px;font-weight:900;letter-spacing:.065em;text-transform:uppercase
}
.v268-metric strong{
  display:block;margin-top:5px;color:#f4f6f8;font-size:15px;line-height:1.05;font-weight:930;overflow-wrap:anywhere
}
.v268-metric small{display:block;margin-top:5px;color:#858b96;font-size:7px;line-height:1.35}
.v268-cockpit-grid{
  display:grid;grid-template-columns:1.35fr .85fr .8fr;gap:8px;margin-top:9px
}
.v268-panel{
  min-width:0;padding:11px;border:1px solid #2a2e35;border-radius:12px;background:#0d0e12
}
.v268-panel-head{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:9px}
.v268-panel-head strong{color:#f2f4f6;font-size:10px;font-weight:900}
.v268-panel-head span{color:#777e89;font-size:7px;font-weight:850;text-transform:uppercase;letter-spacing:.06em}
.v268-signal{
  display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:center;
  padding:9px 0;border-top:1px solid #252930
}
.v268-signal:first-of-type{border-top:0;padding-top:0}
.v268-signal>div{display:grid;grid-template-columns:22px minmax(0,1fr);column-gap:7px}
.v268-signal>div>span{
  grid-row:1 / span 2;width:22px;height:22px;display:grid;place-items:center;border-radius:7px;
  background:#17191f;color:#9298a3;font-size:8px;font-weight:950
}
.v268-signal strong{color:#eef0f3;font-size:9px;font-weight:900}
.v268-signal p{grid-column:2;margin:3px 0 0;color:#8f95a0;font-size:7.5px;line-height:1.4}
.v268-signal.warn>div>span{background:rgba(242,189,85,.10);color:#f2bd55}
.v268-signal.good>div>span{background:rgba(59,213,138,.09);color:#55de98}
.v268-change-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px}
.v268-change-grid .v268-metric{padding:8px}
.v268-change-grid .v268-metric strong{font-size:13px}
.v268-mini-context{
  display:grid;grid-template-columns:1fr auto;gap:6px 10px;margin-top:9px;padding-top:9px;border-top:1px solid #262a31
}
.v268-mini-context span{color:#818793;font-size:8px}
.v268-mini-context b{color:#edf0f3;font-size:9px;font-weight:900}
.v268-empty-note,.v268-profile-ok,.v268-profile-missing{
  color:#9197a1;font-size:8px;line-height:1.45
}
.v268-profile-ok strong,.v268-profile-missing strong{display:block;color:#eef0f3;font-size:10px}
.v268-profile-ok p,.v268-profile-missing p{margin:5px 0 0}
.v268-profile-missing .btn{width:100%;margin-top:9px}

@media(max-width:1100px){
  .v268-metrics{grid-template-columns:repeat(4,minmax(0,1fr))}
  .v268-cockpit-grid{grid-template-columns:1fr 1fr}
  .v268-actions{grid-column:1/-1}
}
@media(max-width:760px){
  #v175CoachAvatarSlot{width:82px!important;height:82px!important;flex-basis:82px!important;border-radius:18px!important}
  .v268-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}
  .v268-cockpit-grid{grid-template-columns:1fr}
  .v268-actions{grid-column:auto}
  .v268-student-avatar-panel{width:100%;min-width:0}
}
@media(max-width:520px){
  .v268-cockpit-head{display:block}
  .v268-cockpit-head>.badge{margin-top:8px}
  .v268-signal{grid-template-columns:1fr}
  .v268-signal .btn{width:100%}
  .v268-change-grid{grid-template-columns:1fr 1fr 1fr}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.68 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-coach-cockpit-music-removal" content="20.68">\n</head>',1)

after=metrics(html)

# Feature removal should reduce obsolete render wrappers, but must never add
# timers/channels/observers/listeners/RAFs.
for key in ("channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]>before[key]:
        raise RuntimeError("V20.68 runtime topology grew "+key+": "+repr({"before":before,"after":after}))
if after["styles"]!=1:
    raise RuntimeError("V20.68 stylesheet count changed")

for forbidden in [
    "coach_media_settings",
    "renderGlobalMusicCoachV69",
    "saveGlobalSpotifyV69",
    "renderSpotifyStudentV69",
    "saveSpotifyV68",
    "spotify_url",
    "coachTab==='music'",
    "studentTab==='music'",
    "coachStudentTab==='music'",
]:
    if forbidden in html:
        raise RuntimeError("V20.68 music feature still active: "+forbidden)

for marker in [
    'meta name="fjz-coach-cockpit-music-removal" content="20.68"',
    "musicFeatureRemoved:true",
    "coachMediaRealtimeRemoved:true",
    "coachCockpitV268:true",
    "coachDecisionSignals:true",
    "coachDataCoverage:true",
    "coachAvatarProductionLinkedProfile:true",
    "studentAvatarProductionLinkedProfile:true",
    "stagingAvatarClearlyDemo:true",
    "noProductionDataInStaging:true",
    "COACH COCKPIT",
]:
    if marker not in html:
        raise RuntimeError("V20.68 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.68 coach cockpit + avatar + music removal")
print("V20.68 BEFORE:",before)
print("V20.68 AFTER:",after)
print("V20.68 music removed from runtime/realtime/navigation; coach cockpit and robust avatar surface enabled")
