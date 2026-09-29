import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v161UnifiedCoachSummaryStyles">
#v161CoachOverview{
  margin-bottom:14px
}
.v161-overview-head{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:14px;
  margin-bottom:14px
}
.v161-overview-person{
  display:flex;
  align-items:center;
  gap:12px;
  min-width:0
}
.v161-overview-person>div:last-child{
  min-width:0
}
.v161-overview-person h3{
  margin:0;
  overflow-wrap:anywhere
}
.v161-overview-person p{
  margin:3px 0 0;
  overflow-wrap:anywhere
}
.v161-overview-grid{
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:8px
}
.v161-overview-metric{
  min-width:0;
  padding:11px;
  border:1px solid var(--border);
  border-radius:12px;
  background:rgba(255,255,255,.025)
}
.v161-overview-metric strong{
  display:block;
  font-size:18px;
  line-height:1.15;
  overflow-wrap:anywhere
}
.v161-overview-metric span{
  display:block;
  margin-top:4px;
  font-size:9px;
  color:var(--muted);
  line-height:1.25
}
.v161-overview-section{
  margin-top:12px;
  padding-top:12px;
  border-top:1px solid var(--border)
}
.v161-overview-section-title{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:8px;
  margin-bottom:8px
}
.v161-overview-section-title strong{
  font-size:11px
}
.v161-signal-row{
  display:flex;
  gap:6px;
  flex-wrap:wrap
}
.v161-signal{
  display:inline-flex;
  align-items:center;
  min-height:28px;
  padding:5px 8px;
  border:1px solid var(--border);
  border-radius:999px;
  font-size:9px;
  color:var(--muted);
  background:rgba(255,255,255,.025)
}
.v161-signal.attention{
  color:#ffb4ba;
  border-color:rgba(255,82,97,.28);
  background:rgba(255,82,97,.06)
}
.v161-overview-actions{
  display:flex;
  gap:7px;
  flex-wrap:wrap;
  margin-top:12px
}
.v161-overview-loading{
  opacity:.7
}
@media(max-width:760px){
  .v161-overview-head{
    display:block
  }
  .v161-overview-head>.muted{
    margin-top:9px
  }
  .v161-overview-grid{
    grid-template-columns:repeat(2,minmax(0,1fr))
  }
  .v161-overview-actions{
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr))
  }
  .v161-overview-actions .btn{
    width:100%
  }
}
@media(max-width:380px){
  .v161-overview-grid{
    grid-template-columns:1fr 1fr
  }
}
</style>
"""

js=r"""
<script id="v161UnifiedCoachSummaryRuntime">
(function(){
  const VERSION='16.1';
  let inflightV161=null;
  let inflightKeyV161='';

  function studentKeyV161(){
    return String(student()?.id||'');
  }

  function overviewHostV161(){
    return el('coachStudentBody');
  }

  function sessions30V161(s){
    if(typeof progressSessionsInDaysV72==='function')return progressSessionsInDaysV72(s,30).length;
    const cut=Date.now()-30*86400000;
    return (s?.sessions||[]).filter(x=>{
      const t=new Date(x.date||x.completedAt||0).getTime();
      return Number.isFinite(t)&&t>=cut;
    }).length;
  }

  function recentWeightV161(latest,meas){
    const v=meas?.weight_kg??latest?.weight_kg;
    return v!=null&&v!==''?Number(v):null;
  }

  function metricV161(value,label,sub=''){
    return '<div class="v161-overview-metric">'+
      '<strong>'+esc(String(value??'—'))+'</strong>'+
      '<span>'+esc(label)+(sub?'<br>'+esc(sub):'')+'</span>'+
    '</div>';
  }

  function signalV161(text,attention=false){
    return '<span class="v161-signal '+(attention?'attention':'')+'">'+esc(text)+'</span>';
  }

  function localOverviewHtmlV161(){
    const s=student();
    const ath=currentAthleteRowV73?.()||cloudAthletes?.get?.(s?.id);
    const pending=typeof pendingFeedbackV73==='function'?pendingFeedbackV73().length:0;
    const days=typeof daysSince==='function'?daysSince(s?.lastWorkout):null;
    const status=statusFor(s);
    const avatar='<div id="v161AvatarSlot">'+
      '<div class="v70-avatar big">'+esc((s?.name||'AL').slice(0,2).toUpperCase())+'</div>'+
    '</div>';

    const quick=[];
    if(pending)quick.push(signalV161(pending+' comentario'+(pending===1?'':'s')+' pendiente'+(pending===1?'':'s'),true));
    if(Number.isFinite(days)&&days>=6)quick.push(signalV161(days+' días sin entrenar',true));
    if(!quick.length)quick.push(signalV161('Sin alertas críticas'));

    return '<div class="card" id="v161CoachOverview">'+
      '<div class="v161-overview-head">'+
        '<div class="v161-overview-person">'+avatar+
          '<div><h3>'+esc(s?.name||'Alumno')+'</h3>'+
          '<p class="muted tiny">'+esc(s?.goal||'Sin objetivo cargado')+'</p>'+
          '<div class="pill-row" style="margin-top:7px">'+badge(status)+'</div></div>'+
        '</div>'+
        '<div class="muted micro">Resumen 360 · una sola vista</div>'+
      '</div>'+
      '<div class="v161-overview-grid">'+
        metricV161(adherence(s)+'%','Adherencia 7 días')+
        metricV161(sessions30V161(s),'Entrenos 30 días')+
        metricV161(fmtDate(s?.lastWorkout),'Último entreno')+
        metricV161('—','Peso reciente')+
        metricV161('—','Energía')+
        metricV161('—','Recuperación')+
        metricV161('—','Sueño')+
        metricV161('—','Estrés')+
      '</div>'+
      '<div class="v161-overview-section">'+
        '<div class="v161-overview-section-title"><strong>Nutrición y seguimiento</strong><span class="muted micro v161-overview-loading">Actualizando…</span></div>'+
        '<div id="v161NutritionLine" class="v161-signal-row">'+signalV161('Cargando datos conectados…')+'</div>'+
      '</div>'+
      '<div class="v161-overview-section">'+
        '<div class="v161-overview-section-title"><strong>Atención rápida</strong></div>'+
        '<div id="v161SignalLine" class="v161-signal-row">'+quick.join('')+'</div>'+
      '</div>'+
      '<div class="v161-overview-actions">'+
        '<button class="btn small" onclick="coachStudentTab=\'routine\';render()">Rutina</button>'+
        '<button class="btn small" onclick="coachStudentTab=\'progress\';render()">Progreso</button>'+
        '<button class="btn small" onclick="coachStudentTab=\'tracking\';render()">Check-in</button>'+
        '<button class="btn small" onclick="coachStudentTab=\'nutrition\';render()">Nutrición</button>'+
        '<button class="btn small" onclick="coachStudentTab=\'history\';render()">Historial</button>'+
      '</div>'+
    '</div>';
  }

  function installShellV161(){
    if(currentProfile?.role!=='coach'||coachTab!=='student'||coachStudentTab!=='summary')return null;
    const host=overviewHostV161();
    if(!host)return null;

    const existing=el('v161CoachOverview');
    if(existing)return existing;

    ['v63UnifiedSummary','v80Student360','v80Student360Loading'].forEach(id=>el(id)?.remove());

    const slot=el('v159Student360Slot');
    const wrap=document.createElement('div');
    wrap.innerHTML=localOverviewHtmlV161();
    const card=wrap.firstElementChild;

    if(slot?.isConnected)slot.replaceWith(card);
    else host.insertBefore(card,host.firstChild);

    return card;
  }

  function updateOverviewV161(key){
    if(studentKeyV161()!==key)return;
    const card=el('v161CoachOverview');
    if(!card)return;

    const s=student();
    const latest=trackingCache?.checkins?.[0]||null;
    const meas=trackingCache?.measurements?.[0]||null;
    const nutrition=nutritionCache?.plan||null;
    const weight=recentWeightV161(latest,meas);
    const pending=typeof pendingFeedbackV73==='function'?pendingFeedbackV73().length:0;

    const values=[
      [adherence(s)+'%','Adherencia 7 días'],
      [sessions30V161(s),'Entrenos 30 días'],
      [fmtDate(s?.lastWorkout),'Último entreno'],
      [weight!=null?round1(weight)+' kg':'—','Peso reciente'],
      [latest?.energy_level!=null?latest.energy_level+'/10':'—','Energía'],
      [latest?.recovery_level!=null?latest.recovery_level+'/10':'—','Recuperación'],
      [latest?.sleep_quality!=null?latest.sleep_quality+'/10':'—','Sueño'],
      [latest?.stress_level!=null?latest.stress_level+'/10':'—','Estrés']
    ];

    const grid=card.querySelector('.v161-overview-grid');
    if(grid)grid.innerHTML=values.map(x=>metricV161(x[0],x[1])).join('');

    const nutritionLine=el('v161NutritionLine');
    if(nutritionLine){
      const parts=[];
      parts.push(signalV161(nutrition?'Plan nutricional activo':'Sin plan nutricional',!nutrition));
      if(nutrition){
        try{
          const a=nutritionAdherenceV63();
          parts.push(signalV161(a.expected?'Registro semanal '+a.pct+'%':'Registro semanal sin base'));
          parts.push(signalV161((a.completed||0)+'/'+(a.expected||0)+' comidas registradas'));
        }catch(e){}
      }
      if(latest?.week_start||latest?.submitted_at){
        parts.push(signalV161('Último check-in '+fmtDate(latest.week_start||latest.submitted_at)));
      }else{
        parts.push(signalV161('Sin check-in reciente',true));
      }
      nutritionLine.innerHTML=parts.join('');
    }

    const signals=[];
    const days=typeof daysSince==='function'?daysSince(s?.lastWorkout):null;
    if(pending)signals.push(signalV161(pending+' comentario'+(pending===1?'':'s')+' pendiente'+(pending===1?'':'s'),true));
    if(Number.isFinite(days)&&days>=6)signals.push(signalV161(days+' días sin entrenar',true));
    if(latest?.recovery_level!=null&&Number(latest.recovery_level)<=4)signals.push(signalV161('Recuperación baja',true));
    if(latest?.energy_level!=null&&Number(latest.energy_level)<=4)signals.push(signalV161('Energía baja',true));
    if(latest?.stress_level!=null&&Number(latest.stress_level)>=8)signals.push(signalV161('Estrés alto',true));
    if(!signals.length)signals.push(signalV161('Sin alertas críticas'));
    const signalLine=el('v161SignalLine');
    if(signalLine)signalLine.innerHTML=signals.join('');

    const loading=card.querySelector('.v161-overview-loading');
    if(loading){
      loading.textContent='Datos conectados';
      loading.classList.remove('v161-overview-loading');
    }
  }

  async function hydrateAvatarV161(key){
    try{
      const s=student(),ath=currentAthleteRowV73?.()||cloudAthletes?.get?.(s?.id);
      if(!ath?.user_id||typeof avatarHtmlV70!=='function')return;
      const html=await avatarHtmlV70(ath.user_id,s.name,'big');
      if(studentKeyV161()!==key)return;
      const slot=el('v161AvatarSlot');
      if(slot)slot.innerHTML=html;
    }catch(e){}
  }

  async function hydrateOverviewV161(){
    if(currentProfile?.role!=='coach'||coachTab!=='student'||coachStudentTab!=='summary')return;
    const key=studentKeyV161();
    if(!key)return;

    installShellV161();

    if(inflightV161&&inflightKeyV161===key)return inflightV161;
    inflightKeyV161=key;

    inflightV161=(async()=>{
      const athleteId=trackingAthleteId?.();
      const jobs=[];

      if(athleteId&&trackingLoadedFor!==athleteId&&typeof loadTracking==='function'){
        jobs.push(loadTracking(false));
      }

      const nutritionAthlete=nutritionAthleteId?.();
      const nutritionReady=!!nutritionAthlete&&
        nutritionLoadedAthlete===nutritionAthlete&&
        nutritionFoodsLoaded===true;
      if(nutritionAthlete&&!nutritionReady&&typeof loadNutrition==='function'){
        jobs.push(loadNutrition(false,nutritionCache?.date||dateInputToday()));
      }

      try{
        const feedbackKey=typeof feedbackKeyV73==='function'?feedbackKeyV73(currentAthleteIdV73?.()):null;
        const feedbackReady=feedbackKey&&exerciseFeedbackCacheV73?.has?.(feedbackKey);
        if(!feedbackReady&&typeof loadExerciseFeedbackV73==='function'){
          jobs.push(loadExerciseFeedbackV73(false));
        }
      }catch(e){}

      const results=await Promise.allSettled(jobs);
      if(studentKeyV161()!==key)return;
      updateOverviewV161(key);
      hydrateAvatarV161(key);
      return results;
    })().finally(()=>{
      if(inflightKeyV161===key){
        inflightV161=null;
        inflightKeyV161='';
      }
    });

    return inflightV161;
  }

  // Both legacy entry points now resolve to the same single overview.
  window.injectUnifiedStudentSummaryV63=function(){
    installShellV161();
    return hydrateOverviewV161();
  };
  window.injectStudent360V80=function(){
    installShellV161();
    return hydrateOverviewV161();
  };

  // Remove both legacy cards if an old cached render left them around.
  function cleanupLegacyV161(){
    if(!(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'))return;
    ['v63UnifiedSummary','v80Student360','v80Student360Loading'].forEach(id=>el(id)?.remove());
    installShellV161();
    hydrateOverviewV161();
  }

  if(typeof fjzPostRenderV125==='function'){
    const baseRenderV161=render;
    render=function(){
      const out=baseRenderV161.apply(this,arguments);
      if(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'){
        fjzPostRenderV125('v161-unified-overview',cleanupLegacyV161);
      }
      return out;
    };
  }

  window.__fjzUnifiedOverviewV161={
    version:VERSION,
    singleOverview:true,
    legacyIntegralMerged:true,
    legacy360Merged:true,
    cacheFirst:true,
    duplicateLoadsRemoved:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzUnifiedOverviewV161",
  "singleOverview:true",
  "legacyIntegralMerged:true",
  "legacy360Merged:true",
  "cacheFirst:true",
  "duplicateLoadsRemoved:true"
]:
    if marker not in html:
        raise RuntimeError("V16.1 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V16.1 unified coach summary 360 enabled")
