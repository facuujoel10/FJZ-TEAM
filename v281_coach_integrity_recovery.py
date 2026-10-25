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
    'meta name="fjz-priority-calendar-recovery" content="20.80"',
    'meta name="fjz-final-stability-polish" content="20.79"',
    'id="v280OperationalRecoveryRuntime"',
    'id="v175ProfileAgendaCoachCenterRuntime"',
]:
    if marker not in html:
        raise RuntimeError("V20.81 prerequisite missing "+marker)

runtime=r"""
<script id="v281CoachIntegrityRuntime">
(function(){
  let filterV281='all';
  let sortV281='priority';

  const studentsV281=()=>Array.isArray(state?.students)?state.students:[];
  const daysSinceV281=v=>{
    const t=Date.parse(v||0);
    return t?Math.max(0,Math.floor((Date.now()-t)/86400000)):999;
  };
  const athleteV281=s=>{
    try{return cloudAthletes?.get?.(s?.id)||null}catch(_e){return null}
  };
  const feedV281=s=>{
    try{
      const a=athleteV281(s);
      const f=(typeof coachFeedV235!=='undefined'&&Array.isArray(coachFeedV235))?coachFeedV235:[];
      return a?f.filter(x=>x?.athlete_id===a.id):[];
    }catch(_e){return []}
  };
  const adherenceV281=s=>{
    try{return Number(adherence?.(s)||0)}catch(_e){return 0}
  };
  const statusV281=s=>{
    try{return statusFor?.(s)||'Seguimiento'}catch(_e){return 'Seguimiento'}
  };
  const pendingFeedbackV281=s=>{
    try{return Number(window.__fjzPendingSessionFeedbackCountV242?.(s)||0)}
    catch(_e){return 0}
  };
  const cadenceV281=s=>{
    const n=Number(s?.coachReviewSettingsV240?.cadenceDays||7);
    return [7,14,30].includes(n)?n:7;
  };
  const dueV281=s=>{
    const days=cadenceV281(s),reviewed=s?.coachReviewV237?.reviewedAt||null;
    if(!reviewed)return {due:true,days,cadenceDays:days,ageDays:999,remaining:0,label:'Sin revisión previa'};
    const age=daysSinceV281(reviewed),remaining=Math.max(0,days-age);
    return {due:age>=days,days,cadenceDays:days,ageDays:age,remaining,label:age>=days?'Revisión vencida · '+age+' días':'Próxima revisión en '+remaining+' días'};
  };
  const pendingV281=s=>feedV281(s).length;
  const criticalV281=s=>feedV281(s).filter(x=>x?.severity==='critical').length;

  function reviewStateV281(s){
    const prev=s?.coachReviewV237||null;
    const currentAdh=adherenceV281(s);
    const sessionsCount=Array.isArray(s?.sessions)?s.sessions.length:0;
    const currentStatus=statusV281(s);
    const pending=pendingV281(s);
    const sessionPending=pendingFeedbackV281(s);
    const due=dueV281(s);
    if(!prev)return {hasBaseline:false,changed:true,reviewDue:true,reviewDueLabel:due.label,reason:'Sin revisión previa',newSessions:sessionsCount,adherenceDelta:null,pending,sessionPending};
    const newSessions=Math.max(0,sessionsCount-Number(prev.sessionsCount||0));
    const adherenceDelta=currentAdh-Number(prev.adherence||0);
    const statusChanged=currentStatus!==prev.status;
    const lastWorkoutChanged=!!(s?.lastWorkout&&s.lastWorkout!==prev.lastWorkout);
    const changed=newSessions>0||pending>0||sessionPending>0||statusChanged||Math.abs(adherenceDelta)>=10||lastWorkoutChanged;
    const bits=[];
    if(sessionPending)bits.push(sessionPending+' feedback pendiente');
    if(newSessions)bits.push(newSessions+' entreno'+(newSessions===1?' nuevo':'s nuevos'));
    if(pending)bits.push(pending+' alerta'+(pending===1?'':'s'));
    if(statusChanged)bits.push('estado '+String(currentStatus).toLowerCase());
    if(Math.abs(adherenceDelta)>=10)bits.push('adherencia '+(adherenceDelta>0?'+':'')+Math.round(adherenceDelta)+'%');
    if(lastWorkoutChanged&&!newSessions)bits.push('actividad nueva');
    return {hasBaseline:true,changed,reviewDue:due.due,reviewDueLabel:due.label,reason:bits.slice(0,2).join(' · ')||(changed?'Cambios nuevos':'Al día'),newSessions,adherenceDelta,pending,sessionPending};
  }

  function scoreV281(s){
    const r=reviewStateV281(s),adh=adherenceV281(s),days=daysSinceV281(s?.lastWorkout);
    return criticalV281(s)*8+pendingV281(s)*3+pendingFeedbackV281(s)*7+
      (statusV281(s)==='Revisar'?5:0)+(adh<70?3:0)+(days>=7?2:0)+
      (r.changed?4:0)+(r.reviewDue?3:0)+(!r.hasBaseline?2:0);
  }
  function bestTabV281(s){
    if(pendingFeedbackV281(s)>0)return 'summary';
    const f=feedV281(s).slice();
    const rank={critical:4,warning:3,info:2,success:1};
    f.sort((a,b)=>(rank[b?.severity]||0)-(rank[a?.severity]||0));
    const top=f[0];
    if(top?.kind==='exercise_feedback'||top?.kind==='training')return 'routine';
    if(top?.kind==='checkin'||top?.kind==='wellness')return 'tracking';
    if(top?.kind==='nutrition')return 'nutrition';
    if(top?.kind==='progression')return 'progress';
    return 'summary';
  }
  function openStudentV281(id,tab){
    state.selectedStudentId=id;
    try{saveState?.()}catch(_e){}
    coachTab='student';coachStudentTab=tab||'summary';
    render?.();
  }
  function filteredV281(){
    const q=(()=>{
      try{return normalizeTextV70?.(el('studentSearch')?.value||'')||''}
      catch(_e){return String(el('studentSearch')?.value||'').toLowerCase()}
    })();
    let rows=studentsV281().filter(s=>{
      const name=(()=>{
        try{return normalizeTextV70?.(s?.name||'')||''}
        catch(_e){return String(s?.name||'').toLowerCase()}
      })();
      if(q&&!name.includes(q))return false;
      const adh=adherenceV281(s),days=daysSinceV281(s?.lastWorkout),r=reviewStateV281(s);
      if(filterV281==='review')return statusV281(s)==='Revisar';
      if(filterV281==='low')return adh<70;
      if(filterV281==='inactive')return days>=7;
      if(filterV281==='changes')return r.changed;
      if(filterV281==='unreviewed')return !r.hasBaseline;
      if(filterV281==='due')return r.reviewDue;
      if(filterV281==='session_feedback')return pendingFeedbackV281(s)>0;
      return true;
    });
    rows.sort((a,b)=>{
      if(sortV281==='adherence')return adherenceV281(a)-adherenceV281(b);
      if(sortV281==='last')return daysSinceV281(b?.lastWorkout)-daysSinceV281(a?.lastWorkout);
      if(sortV281==='name')return String(a?.name||'').localeCompare(String(b?.name||''));
      return scoreV281(b)-scoreV281(a)||adherenceV281(a)-adherenceV281(b);
    });
    return rows;
  }
  function decorateReviewV281(){
    document.querySelectorAll('.student-row[data-client-id]').forEach(row=>{
      row.querySelector('.v238-review-badge')?.remove();
      const s=studentsV281().find(x=>String(x.id)===String(row.dataset.clientId));
      if(!s)return;
      const r=reviewStateV281(s),main=row.querySelector('.student-main');if(!main)return;
      const cls=!r.hasBaseline?'unreviewed':r.reviewDue?'due':r.changed?'changed':'current';
      const label=!r.hasBaseline?'Sin revisión':r.reviewDue?'Revisión vencida':r.changed?'Nuevo desde revisión':'Revisado';
      main.insertAdjacentHTML('beforeend','<span class="v238-review-badge '+cls+'">'+label+'</span>');
    });
    const all=studentsV281(),changed=all.filter(s=>reviewStateV281(s).changed).length,unreviewed=all.filter(s=>!reviewStateV281(s).hasBaseline).length,due=all.filter(s=>reviewStateV281(s).reviewDue).length;
    if(el('v238ChangedCount'))el('v238ChangedCount').textContent=String(changed);
    if(el('v238UnreviewedCount'))el('v238UnreviewedCount').textContent=String(unreviewed);
    if(el('v240DueCount'))el('v240DueCount').textContent=String(due);
    if(el('v243SessionFeedbackCount'))el('v243SessionFeedbackCount').textContent=String(all.filter(s=>pendingFeedbackV281(s)>0).length);
    if(el('v238CurrentCount'))el('v238CurrentCount').textContent=String(all.filter(s=>{const r=reviewStateV281(s);return r.hasBaseline&&!r.changed&&!r.reviewDue}).length);
  }
  function renderStudentsV281(){
    const host=el('studentList');if(!host)return;
    const rows=filteredV281();
    host.innerHTML=rows.length?(typeof studentRows==='function'?studentRows(rows):rows.map(s=>'<div>'+esc(s.name||'Alumno')+'</div>').join('')):'<div class="empty">No hay alumnos en este filtro.</div>';
    document.querySelectorAll('[data-v235-filter]').forEach(b=>b.classList.toggle('active',b.dataset.v235Filter===filterV281));
    const n=el('v235StudentCount');if(n)n.textContent=rows.length;
    try{if(typeof decorateCoachAlertsV235==='function')decorateCoachAlertsV235()}catch(_e){}
    decorateReviewV281();
  }
  function renderFocusV281(){
    const h=el('v235CoachFocus');if(!h)return;
    const rows=studentsV281().map(s=>({s,score:scoreV281(s)})).filter(x=>x.score>0).sort((a,b)=>b.score-a.score).slice(0,5);
    h.innerHTML=rows.length?rows.map(({s,score})=>{
      const r=reviewStateV281(s),bits=[];
      if(pendingFeedbackV281(s))bits.push(pendingFeedbackV281(s)+' feedback pendiente');
      if(criticalV281(s))bits.push(criticalV281(s)+' prioridad alta');
      else if(pendingV281(s))bits.push(pendingV281(s)+' pendientes');
      if(r.reviewDue)bits.push(r.reviewDueLabel);
      else if(r.changed)bits.push(r.reason);
      if(adherenceV281(s)<70)bits.push('adherencia '+adherenceV281(s)+'%');
      return '<div class="v235-focus-item"><div><strong>'+esc(s.name||'Alumno')+'</strong><span>'+esc(bits.slice(0,2).join(' · ')||'Seguimiento')+'</span></div><b>'+score+'</b><div class="v235-focus-actions"><button class="btn small primary" onclick="openCoachStudentTabV235(\''+esc(s.id)+'\',\'summary\')">Resumen</button><button class="btn small" onclick="openCoachStudentTabV235(\''+esc(s.id)+'\',\'routine\')">Rutina</button><button class="btn small" onclick="openCoachStudentTabV235(\''+esc(s.id)+'\',\'tracking\')">Check-in</button><button class="btn small" onclick="openCoachStudentTabV235(\''+esc(s.id)+'\',\'progress\')">Progreso</button></div></div>';
    }).join(''):'<div class="empty">No hay alumnos con señales prioritarias.</div>';
  }

  window.coachDaysSinceV235=daysSinceV281;
  window.coachReviewCadenceDaysV240=cadenceV281;
  window.coachReviewDueV240=dueV281;
  window.coachReviewLoopStateV238=reviewStateV281;
  window.coachReviewCountsV238=function(){const s=studentsV281();return {changed:s.filter(x=>reviewStateV281(x).changed).length,unreviewed:s.filter(x=>!reviewStateV281(x).hasBaseline).length,current:s.filter(x=>{const r=reviewStateV281(x);return r.hasBaseline&&!r.changed&&!r.reviewDue}).length,due:s.filter(x=>reviewStateV281(x).reviewDue).length}};
  window.decorateCoachReviewStateV238=decorateReviewV281;
  window.pendingSessionFeedbackCountV243=pendingFeedbackV281;
  window.openCoachStudentTabV235=openStudentV281;
  window.renderCoachStudentsV235=renderStudentsV281;
  window.renderCoachFocusV235=renderFocusV281;
  window.setCoachStudentFilterV235=function(k){filterV281=k||'all';renderStudentsV281()};
  window.setCoachStudentSortV236=function(k){sortV281=['priority','adherence','last','name'].includes(k)?k:'priority';renderStudentsV281()};
  window.openNextCoachPriorityV236=function(){
    const ranked=studentsV281().map(s=>({s,score:scoreV281(s)})).filter(x=>x.score>0).sort((a,b)=>b.score-a.score||adherenceV281(a.s)-adherenceV281(b.s));
    if(!ranked.length){toast?.('No hay prioridades pendientes ahora');return}
    openStudentV281(ranked[0].s.id,bestTabV281(ranked[0].s));
  };
  window.setCoachReviewCadenceV240=function(days){
    const s=student?.();if(!s)return;
    const n=Number(days);
    s.coachReviewSettingsV240={...(s.coachReviewSettingsV240||{}),cadenceDays:[7,14,30].includes(n)?n:7};
    saveState?.();
    try{if(typeof renderReviewHubV237==='function'&&typeof reviewCurrentV237!=='undefined'&&reviewCurrentV237)renderReviewHubV237(reviewCurrentV237)}catch(_e){}
    if(typeof showSaveSuccessV264==='function')showSaveSuccessV264('Frecuencia de revisión actualizada');
  };
  window.coachPriorityStateV252=function(s){
    const r=reviewStateV281(s),adh=adherenceV281(s),days=daysSinceV281(s?.lastWorkout),critical=criticalV281(s),sf=pendingFeedbackV281(s),feed=pendingV281(s);
    if(critical||sf)return {bucket:'urgent',score:100+critical*20+sf*12+feed*2,label:sf?sf+' feedback pendiente':critical+' señal crítica'};
    if(r.reviewDue||r.changed||statusV281(s)==='Revisar'||adh<70||days>=7||feed)return {bucket:'today',score:50+scoreV281(s),label:r.reviewDue?r.reviewDueLabel:r.changed?r.reason:adh<70?'adherencia '+adh+'%':days>=7&&days<999?days+' días sin entrenar':feed+' pendientes'};
    return {bucket:'watch',score:scoreV281(s),label:'Seguimiento al día'};
  };
  window.coachPriorityActionV259=function(s){
    const tab=bestTabV281(s),r=reviewStateV281(s);
    if(pendingFeedbackV281(s)>0)return {tab:'summary',label:'Responder feedback',status:'Pendiente'};
    if(r.reviewDue)return {tab:'summary',label:'Hacer chequeo',status:'Vencido'};
    if(tab==='tracking')return {tab,label:'Revisar check-in',status:'Pendiente'};
    if(tab==='nutrition')return {tab,label:'Revisar nutrición',status:'Pendiente'};
    if(tab==='routine')return {tab,label:'Revisar entrenamiento',status:'Pendiente'};
    if(r.changed)return {tab:'summary',label:'Revisar cambios',status:'Revisar'};
    return {tab:'progress',label:'Ver evolución',status:'Al día'};
  };

  // Compatibility no-op only: UI/routes for Music remain removed, but any
  // historical stale call cannot throw at runtime.
  if(typeof window.loadSpotifyRowV68!=='function')window.loadSpotifyRowV68=async function(){return null};

  // Make bare global identifiers resolve even if historical declarations were
  // removed by the V20.68 block cleanup.
  try{coachDaysSinceV235=window.coachDaysSinceV235}catch(_e){}
  try{coachReviewCadenceDaysV240=window.coachReviewCadenceDaysV240}catch(_e){}
  try{coachReviewDueV240=window.coachReviewDueV240}catch(_e){}
  try{coachReviewLoopStateV238=window.coachReviewLoopStateV238}catch(_e){}
  try{coachReviewCountsV238=window.coachReviewCountsV238}catch(_e){}
  try{decorateCoachReviewStateV238=window.decorateCoachReviewStateV238}catch(_e){}
  try{pendingSessionFeedbackCountV243=window.pendingSessionFeedbackCountV243}catch(_e){}
  try{openCoachStudentTabV235=window.openCoachStudentTabV235}catch(_e){}
  try{renderCoachStudentsV235=window.renderCoachStudentsV235}catch(_e){}
  try{renderCoachFocusV235=window.renderCoachFocusV235}catch(_e){}
  try{setCoachStudentFilterV235=window.setCoachStudentFilterV235}catch(_e){}
  try{setCoachStudentSortV236=window.setCoachStudentSortV236}catch(_e){}
  try{openNextCoachPriorityV236=window.openNextCoachPriorityV236}catch(_e){}
  try{setCoachReviewCadenceV240=window.setCoachReviewCadenceV240}catch(_e){}
  try{coachPriorityStateV252=window.coachPriorityStateV252}catch(_e){}
  try{coachPriorityActionV259=window.coachPriorityActionV259}catch(_e){}
  try{loadSpotifyRowV68=window.loadSpotifyRowV68}catch(_e){}

  // Refresh the operational surfaces if the dashboard is already mounted.
  if(mode==='coach'&&coachTab==='dashboard'){
    try{renderStudentsV281()}catch(e){console.warn('TEAM FJZ V20.81 students recovery',e)}
    try{renderFocusV281()}catch(e){console.warn('TEAM FJZ V20.81 focus recovery',e)}
    try{window.__fjzOperationalDashboardV280?.()}catch(e){console.warn('TEAM FJZ V20.81 operational recovery',e)}
  }

  window.__fjzV281={
    version:'20.81',
    coachIntegrityRecovery:true,
    filtersRestored:true,
    sortingRestored:true,
    nextPriorityRestored:true,
    reviewCadenceRestored:true,
    reviewLoopRestored:true,
    focusPanelRestored:true,
    studentNavigationRestored:true,
    legacyMusicCallNeutralized:true,
    noExtraTimers:true,
    noExtraListeners:true,
    noExtraObservers:true,
    productionUntouched:true
  };
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-coach-integrity-recovery" content="20.81">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.81 topology changed "+key+": "+repr({"before":before,"after":after}))

required=[
    'meta name="fjz-coach-integrity-recovery" content="20.81"',
    "coachIntegrityRecovery:true","filtersRestored:true","sortingRestored:true",
    "nextPriorityRestored:true","reviewCadenceRestored:true","reviewLoopRestored:true",
    "focusPanelRestored:true","studentNavigationRestored:true","legacyMusicCallNeutralized:true",
    "window.openCoachStudentTabV235=openStudentV281",
    "window.renderCoachStudentsV235=renderStudentsV281",
    "window.renderCoachFocusV235=renderFocusV281",
    "window.setCoachStudentFilterV235=function",
    "window.setCoachStudentSortV236=function",
    "window.openNextCoachPriorityV236=function",
    "window.setCoachReviewCadenceV240=function",
]
for marker in required:
    if marker not in html: raise RuntimeError("V20.81 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.81 coach integrity recovery")
print("V20.81 BEFORE:",before)
print("V20.81 AFTER:",after)
print("V20.81 restored coach filters/sort/focus/review/navigation authorities after historical cleanup")
