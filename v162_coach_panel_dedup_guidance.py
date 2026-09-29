import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v162CoachPanelDedupGuidanceStyles">
#v162CoachGuidance{
  margin-top:12px;
  padding-top:12px;
  border-top:1px solid var(--border)
}
.v162-guide-head{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:10px;
  margin-bottom:8px
}
.v162-guide-head strong{font-size:11px}
.v162-guide-list{
  display:grid;
  gap:7px
}
.v162-guide-item{
  padding:9px 10px;
  border:1px solid var(--border);
  border-radius:11px;
  background:rgba(255,255,255,.025)
}
.v162-guide-item.review{
  border-color:rgba(255,82,97,.25);
  background:rgba(255,82,97,.045)
}
.v162-guide-item.good{
  border-color:rgba(70,200,130,.2);
  background:rgba(70,200,130,.04)
}
.v162-guide-title{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:8px
}
.v162-guide-title h4{
  margin:0;
  font-size:11px;
  line-height:1.3
}
.v162-guide-copy{
  margin-top:5px;
  font-size:10px;
  line-height:1.4;
  color:var(--muted)
}
.v162-guide-why{
  margin-top:6px;
  font-size:9px;
  line-height:1.35;
  color:var(--muted)
}
.v162-guide-action{
  margin-top:7px
}
.v162-data-quality{
  font-size:9px;
  color:var(--muted);
  white-space:nowrap
}
#v71CoachHelp,
#v71CoachHelpLoading,
#v71CoachHelpTracking,
#v71CoachHelpTrackingCard{
  display:none!important
}
@media(max-width:700px){
  .v162-guide-head{display:block}
  .v162-data-quality{display:block;margin-top:4px}
}
</style>
"""

js=r"""
<script id="v162CoachPanelDedupGuidanceRuntime">
(function(){
  const VERSION='16.2';

  function uniqPhotosV162(rows){
    const seen=new Set();
    return (rows||[]).filter(p=>{
      const key=String(p?.storage_path||p?.id||'');
      if(!key||seen.has(key))return false;
      seen.add(key);
      return true;
    });
  }

  function cleanTrackingPhotosV162(){
    if(trackingCache&&Array.isArray(trackingCache.photos)){
      trackingCache.photos=uniqPhotosV162(trackingCache.photos);
    }
  }

  const baseLoadTrackingV162=window.loadTracking;
  if(typeof baseLoadTrackingV162==='function'){
    window.loadTracking=async function(){
      const out=await baseLoadTrackingV162.apply(this,arguments);
      cleanTrackingPhotosV162();
      return out;
    };
  }

  const baseRenderPhotoGridV162=window.renderPhotoGrid;
  if(typeof baseRenderPhotoGridV162==='function'){
    window.renderPhotoGrid=async function(){
      cleanTrackingPhotosV162();
      const out=await baseRenderPhotoGridV162.apply(this,arguments);
      cleanupPhotoDomV162(arguments[0]);
      return out;
    };
  }

  function cleanupPhotoDomV162(targetId){
    const root=el(targetId);
    if(!root)return;
    const seen=new Set();
    [...root.querySelectorAll('.photo-slot img,.photo-card img')].forEach(img=>{
      const src=String(img.getAttribute('src')||'').split('?')[0];
      if(!src)return;
      if(seen.has(src)){
        const card=img.closest('.photo-slot,.photo-card');
        if(card)card.remove();
      }else seen.add(src);
    });
    root.querySelectorAll('.photo-month').forEach(month=>{
      const grids=[...month.querySelectorAll('.photo-grid')];
      grids.forEach(g=>{
        if(!g.children.length)g.remove();
      });
    });
  }

  function removeLegacyAssistantV162(){
    ['v71CoachHelp','v71CoachHelpLoading','v71CoachHelpTracking','v71CoachHelpTrackingCard'].forEach(id=>el(id)?.remove());
  }

  // Stop legacy standalone assistant from performing another tracking/nutrition load.
  window.injectCoachHelpV71=function(){ removeLegacyAssistantV162(); return; };
  window.buildCoachHelpV71=async function(){ return []; };
  window.coachHelpHtmlV71=function(){ return ''; };
  window.refreshCoachAssistantV132=function(){
    if(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'){
      refreshGuidanceV162();
      toast('Resumen 360 actualizado');
    }
  };

  function recentSessionsV162(s,days){
    const cut=Date.now()-days*86400000;
    return (s?.sessions||[]).filter(x=>{
      const t=new Date(x.date||x.completedAt||0).getTime();
      return Number.isFinite(t)&&t>=cut;
    });
  }

  function addGuideV162(list,type,priority,title,copy,reason,tab){
    if(list.some(x=>x.title===title))return;
    list.push({type,priority,title,copy,reason,tab});
  }

  function tabNameV162(tab){
    return ({routine:'Rutina',progress:'Progreso',tracking:'Seguimiento',nutrition:'Nutrición',history:'Historial'})[tab]||'Abrir';
  }

  function buildGuidanceV162(){
    const s=student();
    const latest=trackingCache?.checkins?.[0]||null;
    const checks=trackingCache?.checkins||[];
    const measurements=trackingCache?.measurements||[];
    const pending=typeof pendingFeedbackV73==='function'?pendingFeedbackV73():[];
    const ss7=recentSessionsV162(s,7);
    const ss14=recentSessionsV162(s,14);
    const planned=Math.max(1,Number(s?.plannedPerWeek)||s?.days?.length||1);
    const list=[];

    if(!s?.days?.length){
      addGuideV162(list,'review',100,'Falta una rutina activa',
        'Sin una estructura semanal no hay una base clara para interpretar adherencia o progresión.',
        'No hay días programados.','routine');
    }

    if(pending.length){
      const names=[...new Set(pending.map(x=>x.exercise_name).filter(Boolean))].slice(0,3);
      addGuideV162(list,'review',98,'Revisar comentarios pendientes',
        'Conviene resolver primero los comentarios de ejercicios antes de cambiar cargas o volumen.',
        pending.length+' pendiente'+(pending.length===1?'':'s')+(names.length?' · '+names.join(' · '):''), 'routine');
    }

    const daysSinceLast=typeof daysSince==='function'?daysSince(s?.lastWorkout):null;
    if(Number.isFinite(daysSinceLast)&&daysSinceLast>=7){
      addGuideV162(list,'review',94,'Revisar continuidad',
        'Hay varios días sin una sesión registrada. Primero conviene confirmar si entrenó y si el registro está actualizado.',
        'Último entrenamiento: '+fmtDate(s?.lastWorkout)+'.','history');
    }

    if(latest){
      const low=[];
      if(Number(latest.sleep_quality)<=4)low.push('sueño '+latest.sleep_quality+'/10');
      if(Number(latest.energy_level)<=4)low.push('energía '+latest.energy_level+'/10');
      if(Number(latest.recovery_level)<=4)low.push('recuperación '+latest.recovery_level+'/10');
      if(Number(latest.stress_level)>=8)low.push('estrés '+latest.stress_level+'/10');
      if(low.length>=2){
        addGuideV162(list,'review',92,'No sumaría exigencia todavía',
          'Hay varias señales de recuperación para revisar antes de aumentar trabajo.',
          low.join(' · ')+'.','tracking');
      }
      if(Number(latest.adherence_level)<=5){
        addGuideV162(list,'review',86,'Simplificar antes de agregar',
          'La adherencia reportada está baja. Es más útil encontrar la barrera principal que sumar tareas.',
          'Adherencia '+latest.adherence_level+'/10.','tracking');
      }
    }else{
      addGuideV162(list,'info',82,'Falta un check-in reciente',
        'Sin sueño, energía, estrés y recuperación actualizados hay menos contexto para interpretar el entrenamiento.',
        'Todavía no hay check-ins disponibles.','tracking');
    }

    const incomplete=ss14.filter(x=>(Number(x.summary?.skippedExercises)||0)>0||(Number(x.summary?.partial)||0)>0);
    if(incomplete.length>=2){
      addGuideV162(list,'review',84,'La rutina puede estar costando completarse',
        'Se repiten sesiones parciales. Revisaría duración, orden y qué ejercicios quedan afuera.',
        incomplete.length+' sesiones incompletas en 14 días.','history');
    }

    const expected=Math.max(1,planned);
    if(ss7.length<Math.ceil(expected*.6)){
      addGuideV162(list,'info',72,'Frecuencia por debajo de lo planificado',
        'La cantidad de sesiones registradas esta semana está por debajo de la estructura prevista.',
        ss7.length+' de '+planned+' sesiones registradas.','routine');
    }

    const results=ss14.flatMap(x=>x.exerciseResults||[]);
    const review=results.filter(x=>['down','plateau'].includes(x.recommendation?.type));
    const progress=results.filter(x=>['up','rep','load'].includes(x.recommendation?.type));
    if(review.length>=2){
      const names=[...new Set(review.map(x=>x.name).filter(Boolean))].slice(0,3);
      addGuideV162(list,'review',78,'Revisar progresiones puntuales',
        'Hay ejercicios que conviene revisar uno por uno en vez de cambiar toda la rutina.',
        review.length+' señales'+(names.length?' · '+names.join(' · '):''), 'progress');
    }else if(progress.length>=2&&latest&&Number(latest.energy_level)>=6&&Number(latest.recovery_level)>=6&&Number(latest.stress_level)<=6){
      addGuideV162(list,'good',48,'Hay margen para progresión selectiva',
        'El rendimiento reciente y el último check-in acompañan. Progresaría solo donde se cumplió el objetivo.',
        progress.length+' mejoras recientes registradas.','progress');
    }

    try{
      if(nutritionCache?.plan&&typeof nutritionAdherenceV63==='function'){
        const a=nutritionAdherenceV63();
        if(a.expected>=4&&a.pct<50){
          addGuideV162(list,'info',68,'Confirmar el registro nutricional',
            'Hay pocos registros del plan; antes de cambiar cantidades conviene saber si faltó cumplirlo o solo registrarlo.',
            a.completed+' de '+a.expected+' registros esperados · '+a.pct+'%.','nutrition');
        }
      }
    }catch(e){}

    if(!list.length){
      addGuideV162(list,'good',20,'Mantener la base',
        'No aparece una señal fuerte para cambiar el plan ahora. Seguiría observando la tendencia.',
        'Sin banderas principales con los datos actuales.','progress');
    }

    list.sort((a,b)=>b.priority-a.priority);

    let quality=0;
    if(checks.length>=2)quality+=2; else if(checks.length===1)quality+=1;
    if(ss14.length>=2)quality+=2; else if(ss14.length===1)quality+=1;
    if(measurements.length>=2)quality+=1;
    if(pending!==null)quality+=1;
    const confidence=quality>=5?'Alta':quality>=3?'Media':'Baja';

    return {items:list.slice(0,3),confidence,sessions14:ss14.length,checkins:checks.length};
  }

  function guideBadgeV162(type){
    if(type==='review')return '<span class="badge warn">Revisar</span>';
    if(type==='good')return '<span class="badge green">Bien</span>';
    return '<span class="badge blue">Sugerencia</span>';
  }

  function ensureGuidanceV162(){
    const card=el('v161CoachOverview');
    if(!card)return null;
    let box=el('v162CoachGuidance');
    if(box)return box;
    box=document.createElement('div');
    box.id='v162CoachGuidance';
    const actions=card.querySelector('.v161-overview-actions');
    if(actions)card.insertBefore(box,actions);
    else card.appendChild(box);
    return box;
  }

  function refreshGuidanceV162(){
    if(!(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'))return;
    removeLegacyAssistantV162();
    const box=ensureGuidanceV162();
    if(!box)return;
    const data=buildGuidanceV162();
    box.innerHTML=
      '<div class="v162-guide-head"><div><strong>Sugerencias del coach</strong>'+
      '<div class="muted micro" style="margin-top:2px">Cruza entrenamiento, check-in, nutrición y comentarios sin modificar el plan.</div></div>'+
      '<span class="v162-data-quality">Datos '+esc(data.confidence)+' · '+data.sessions14+' sesiones / '+data.checkins+' check-ins</span></div>'+
      '<div class="v162-guide-list">'+data.items.map(x=>
        '<div class="v162-guide-item '+esc(x.type)+'">'+
          '<div class="v162-guide-title"><h4>'+esc(x.title)+'</h4>'+guideBadgeV162(x.type)+'</div>'+
          '<div class="v162-guide-copy">'+esc(x.copy)+'</div>'+
          '<div class="v162-guide-why"><strong>Por qué:</strong> '+esc(x.reason)+'</div>'+
          '<div class="v162-guide-action"><button class="btn small" onclick="coachStudentTab=\''+esc(x.tab)+'\';render()">Abrir '+esc(tabNameV162(x.tab))+'</button></div>'+
        '</div>'
      ).join('')+'</div>';
  }

  // Tracking: gallery stays here, but comparison + old assistant do not.
  const baseTrackingCoachLoadedV162=window.renderTrackingCoachLoaded;
  if(typeof baseTrackingCoachLoadedV162==='function'){
    window.renderTrackingCoachLoaded=function(){
      const out=baseTrackingCoachLoadedV162.apply(this,arguments);
      cleanTrackingPhotosV162();
      el('monthlyCompareCard')?.remove();
      removeLegacyAssistantV162();
      cleanupPhotoDomV162('coachPhotoGrid');
      return out;
    };
  }

  // Progress: the monthly comparator belongs here instead of duplicating gallery content in Tracking.
  const baseRenderProgressV162=window.renderProgress;
  if(typeof baseRenderProgressV162==='function'){
    window.renderProgress=function(isCoach,targetId){
      const out=baseRenderProgressV162.apply(this,arguments);
      if(isCoach&&currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='progress'){
        const athleteId=typeof trackingAthleteId==='function'?trackingAthleteId():null;
        const add=()=> {
          if(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='progress'&&typeof injectMonthlyComparisonV53==='function'){
            injectMonthlyComparisonV53();
          }
        };
        if(athleteId&&trackingLoadedFor===athleteId)add();
        else if(typeof loadTracking==='function')loadTracking(false).then(add).catch(()=>{});
      }
      return out;
    };
  }

  function cleanupCoachStudentV162(){
    if(!(currentProfile?.role==='coach'&&coachTab==='student'))return;
    removeLegacyAssistantV162();

    const body=el('coachStudentBody');
    if(!body)return;

    const uniqueIds=[
      'v161CoachOverview','v114ProfileCard','monthlyCompareCard','coachPhotoGrid',
      'v73RoutineFeedbackTop','v159Student360Slot'
    ];
    uniqueIds.forEach(id=>{
      const nodes=[...document.querySelectorAll('#'+id)];
      nodes.slice(1).forEach(n=>n.remove());
    });

    if(coachStudentTab!=='summary'){
      el('v161CoachOverview')?.remove();
      el('v159Student360Slot')?.remove();
    }
    if(coachStudentTab!=='progress'){
      el('monthlyCompareCard')?.remove();
    }
    if(coachStudentTab==='summary'){
      refreshGuidanceV162();
    }
    if(coachStudentTab==='tracking'){
      cleanTrackingPhotosV162();
      cleanupPhotoDomV162('coachPhotoGrid');
    }
  }

  const baseLoadNutritionV162=window.loadNutrition;
  if(typeof baseLoadNutritionV162==='function'){
    window.loadNutrition=async function(){
      const out=await baseLoadNutritionV162.apply(this,arguments);
      if(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'){
        queueMicrotask(refreshGuidanceV162);
      }
      return out;
    };
  }

  const baseLoadFeedbackV162=window.loadExerciseFeedbackV73;
  if(typeof baseLoadFeedbackV162==='function'){
    window.loadExerciseFeedbackV73=async function(){
      const out=await baseLoadFeedbackV162.apply(this,arguments);
      if(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'){
        queueMicrotask(refreshGuidanceV162);
      }
      return out;
    };
  }

  const finalLoadTrackingV162=window.loadTracking;
  if(typeof finalLoadTrackingV162==='function'){
    window.loadTracking=async function(){
      const out=await finalLoadTrackingV162.apply(this,arguments);
      cleanTrackingPhotosV162();
      if(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'){
        queueMicrotask(refreshGuidanceV162);
      }
      return out;
    };
  }

  const baseRenderV162=window.render;
  window.render=function(){
    const out=baseRenderV162.apply(this,arguments);
    if(typeof fjzPostRenderV125==='function'){
      fjzPostRenderV125('v162-coach-panel-cleanup',cleanupCoachStudentV162);
    }else{
      queueMicrotask(cleanupCoachStudentV162);
    }
    return out;
  };

  window.__fjzCoachPanelV162={
    version:VERSION,
    standaloneAssistantRemoved:true,
    assistantIntegratedInSummary:true,
    assistantMaxSuggestions:3,
    assistantCacheFirst:true,
    photosDeduped:true,
    photoComparisonMovedToProgress:true,
    coachPanelUniqueBlocks:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzCoachPanelV162",
  "standaloneAssistantRemoved:true",
  "assistantIntegratedInSummary:true",
  "assistantMaxSuggestions:3",
  "assistantCacheFirst:true",
  "photosDeduped:true",
  "photoComparisonMovedToProgress:true",
  "coachPanelUniqueBlocks:true"
]:
    if marker not in html:
        raise RuntimeError("V16.2 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V16.2 coach panel dedup + smart guidance enabled")
