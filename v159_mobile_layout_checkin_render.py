import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# Coalesce old zero-delay visual aftershocks into the shared frame scheduler.
replacements=0
patterns=[
    (
        r"""setTimeout\(\(\)=>\{\s*injectStudentProfileV70\(\);\s*injectCoachStudentAvatarV70\(\);\s*loadCoachAvatarsV70\(\);\s*\},0\)""",
        """fjzPostRenderV125('v159-profile-hydrate',()=>{injectStudentProfileV70();injectCoachStudentAvatarV70();loadCoachAvatarsV70()})"""
    ),
    (
        r"""setTimeout\(\(\)=>\{\s*injectStudent360V80\(\);\s*hydrateExerciseVideosV80\(\);\s*\},0\)""",
        """fjzPostRenderV125('v159-student360-video',()=>{injectStudent360V80();hydrateExerciseVideosV80()})"""
    ),
    (
        r"""setTimeout\(\(\)=>injectStudentAgendaHomeV81\(\),0\)""",
        """fjzPostRenderV125('v159-agenda-home',injectStudentAgendaHomeV81)"""
    ),
    (
        r"""setTimeout\(\(\)=>\{\s*removeLegacyMusicDuplicateV82\(\);\s*syncWatermarkLogoV82\(\);\s*injectInstallButtonV82\(\);\s*if\(currentProfile\?\.role==='student'\)scheduleAgendaNoticeV82\(\)\s*\},0\)""",
        """fjzPostRenderV125('v159-pwa-polish',()=>{removeLegacyMusicDuplicateV82();syncWatermarkLogoV82();injectInstallButtonV82();if(currentProfile?.role==='student')scheduleAgendaNoticeV82()})"""
    ),
    (
        r"""setTimeout\(dedupeMusicControlsV821,0\)""",
        """fjzPostRenderV125('v159-music-dedupe',dedupeMusicControlsV821)"""
    )
]
for pat,repl in patterns:
    html,n=re.subn(pat,repl,html,count=1,flags=re.S)
    replacements+=n

css=r"""
<style id="v159MobileLayoutCheckinRenderStyles">
html{scroll-behavior:auto!important}
#view,#coachStudentBody,#studentSubBody{overflow-anchor:none!important}
#view>.card,#coachStudentBody>.card,#studentSubBody>.card,
.student-row,.exercise-row,.day-card,.option-card,.track-row,.history-item,
.v80-kpi,.v80-360,.v81-day,.v81-coach-day{
  animation:none!important;
  transform:none!important
}
body.v158-rendering #view{min-height:calc(100dvh - 150px)!important}
#coachStudentBody,#studentSubBody{min-height:560px}
#cloudFeed,#v80AttentionBody{min-height:150px}
#v159Student360Slot{min-height:188px;margin-bottom:14px}
#v159AgendaHomeSlot{min-height:112px;margin-bottom:14px}

.section-title{flex-wrap:wrap!important}
.section-title>*{min-width:0!important}
.history-item,.track-row-head,.option-head,.meal-head,.photo-month-head,.alert,.feed-top{min-width:0}
.history-item>div:first-child,.track-row-head>div:first-child,.option-head>div:first-child,
.meal-head>div:first-child,.alert>div:first-child,.feed-top>div:first-child{min-width:0}

.student-row{min-width:0!important}
.student-main{min-width:0!important}
.student-main>div:nth-child(2){min-width:0!important}
.student-main>div:nth-child(2)>strong{
  display:block;line-height:1.2;overflow-wrap:anywhere
}
.student-main>div:nth-child(2)>.muted{
  display:block;margin-top:3px;line-height:1.25;overflow-wrap:anywhere
}

.v159-score-card{
  display:grid!important;
  grid-template-columns:minmax(0,1fr) 86px!important;
  align-items:center!important;
  gap:10px!important;
  padding:10px 12px!important;
  min-width:0!important
}
.v159-score-label{min-width:0}
.v159-score-label strong{display:block;font-size:12px;line-height:1.2}
.v159-score-label span{display:block;margin-top:2px;font-size:9px;color:var(--muted)}
.v159-score-control{
  display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:5px;min-width:0
}
.v159-score-input{
  width:100%!important;height:40px!important;padding:6px 8px!important;
  text-align:center!important;font-size:17px!important;font-weight:900!important;
  line-height:1!important;pointer-events:auto!important;touch-action:manipulation!important;
  user-select:text!important;-webkit-user-select:text!important
}
.v159-score-input.v159-invalid{
  border-color:#ff5261!important;box-shadow:0 0 0 2px rgba(255,82,97,.10)!important
}
.v159-score-suffix{color:var(--muted);font-size:10px;font-weight:800;white-space:nowrap}

@media(max-width:900px){
  #view{min-height:calc(100dvh - 128px)!important}
  body.v158-rendering #view{min-height:calc(100dvh - 128px)!important}
  #coachStudentBody,#studentSubBody{min-height:520px!important}

  .topbar,.bottom-nav{-webkit-backdrop-filter:none!important;backdrop-filter:none!important}

  .student-row{
    grid-template-columns:minmax(0,1fr) 64px!important;
    gap:9px!important;align-items:center!important;padding:11px!important
  }
  .student-row>div:nth-child(2),.student-row>div:nth-child(3),.student-row>div:nth-child(4){
    display:none!important
  }
  .student-row>.btn:last-child{
    width:64px!important;min-width:64px!important;padding:8px 6px!important;justify-self:end
  }
  .student-main{
    display:grid!important;grid-template-columns:44px minmax(0,1fr)!important;
    grid-auto-rows:auto;column-gap:10px!important;row-gap:5px!important;align-items:center!important
  }
  .student-main>.v70-student-avatar-slot,.student-main>.avatar{
    grid-column:1!important;grid-row:1 / span 2!important;align-self:center!important;
    width:44px!important;min-width:44px!important
  }
  .student-main>div:nth-child(2){grid-column:2!important;grid-row:1!important}
  .student-main>.v80-student-alert-count{
    display:inline-flex!important;grid-column:2!important;grid-row:2!important;
    justify-self:start!important;margin:0!important;max-width:100%!important
  }
  .student-main .v70-avatar,.student-main .avatar{width:42px!important;height:42px!important}

  .v80-dashboard-grid{grid-template-columns:1fr!important}
  .v80-dashboard-grid>aside{margin-top:14px}
  .v80-kpis{grid-template-columns:repeat(2,minmax(0,1fr))!important}

  .section-title{align-items:flex-start!important}
  .section-title>div:first-child{flex:1 1 180px;min-width:0!important}
  .section-title>input,.section-title>select,.section-title>.input{
    flex:1 1 180px!important;width:100%!important;max-width:none!important
  }

  .track-row-head,.option-head,.meal-head,.photo-month-head,.alert,.feed-top{flex-wrap:wrap!important}
  .history-item{grid-template-columns:minmax(0,1fr) auto!important}

  .v701-checkin-scores{grid-template-columns:1fr!important;gap:8px!important}
}

@media(max-width:520px){
  .shell{padding-left:10px!important;padding-right:10px!important}
  .card{padding:13px!important}
  .hero{gap:10px!important}
  .v80-kpis,.grid.kpi,.metric-grid,.summary-grid{
    grid-template-columns:1fr 1fr!important
  }
  .v80-kpi,.metric,.grid.kpi>.card{min-width:0!important}
  .v80-kpi strong,.metric strong,.grid.kpi>.card strong{overflow-wrap:anywhere}
  .section-title{gap:8px!important}
  .section-title>input,.section-title>select,.section-title>.input{flex-basis:100%!important}
  .v159-score-card{
    grid-template-columns:minmax(0,1fr) 82px!important;padding:9px 10px!important
  }
  .v159-score-input{height:38px!important}
  .history-item{gap:8px!important}
}
@media(max-width:380px){
  .v80-kpis,.grid.kpi,.metric-grid,.summary-grid{grid-template-columns:1fr!important}
}
</style>
"""

js=r"""
<script id="v159MobileLayoutCheckinRenderRuntime">
(function(){
  const VERSION='15.9';
  const SPECS=[
    ['Sueño','ciSleep'],['Hambre','ciHunger'],['Estrés','ciStress'],['Energía','ciEnergy'],
    ['Adherencia','ciAdh'],['Ánimo','ciMood'],['Motivación','ciMotivation'],['Recuperación','ciRecovery']
  ];

  function sanitizeScoreV159(input,finalize=false){
    if(!input)return;
    let raw=String(input.value||'').replace(/\D/g,'').slice(0,2);
    input.classList.remove('v159-invalid');
    if(raw===''){input.value='';return}
    let n=parseInt(raw,10);
    if(!Number.isFinite(n)){input.value='';return}
    if(n>10)n=10;
    input.value=String(n);
    if(finalize&&n<1){
      input.value='';
      input.classList.add('v159-invalid');
      return;
    }
    if(n<1||n>10)input.classList.add('v159-invalid');
  }

  window.checkinScoreInputV159=input=>sanitizeScoreV159(input,false);
  window.checkinScoreBlurV159=input=>sanitizeScoreV159(input,true);

  function scoreCardV159(label,id,value=''){
    const safe=/^(?:[1-9]|10)$/.test(String(value||''))?String(value):'';
    return '<div class="track-score v159-score-card" data-score-id="'+id+'">'+
      '<div class="v159-score-label"><strong>'+esc(label)+'</strong><span>Del 1 al 10</span></div>'+
      '<div class="v159-score-control">'+
        '<input id="'+id+'" class="input v157-score-input v159-score-input" '+
          'type="text" inputmode="numeric" pattern="[0-9]*" maxlength="2" autocomplete="off" '+
          'enterkeyhint="next" placeholder="—" value="'+safe+'" '+
          'oninput="checkinScoreInputV159(this)" onblur="checkinScoreBlurV159(this)">'+
        '<span class="v159-score-suffix">/10</span>'+
      '</div>'+
    '</div>';
  }

  function installCheckinFieldsV159(){
    const host=el('studentSubBody');
    const grid=host?.querySelector('.v701-checkin-scores');
    if(!grid)return;
    const values={};
    SPECS.forEach(([,id])=>{
      const x=el(id);
      if(x&&/^(?:[1-9]|10)$/.test(String(x.value||'')))values[id]=x.value;
    });
    grid.innerHTML=SPECS.map(([label,id])=>scoreCardV159(label,id,values[id]||'')).join('');
    const note=el('v154RequiredNote');
    if(note)note.textContent='Escribí un número del 1 al 10 en cada indicador. Máximo 10.';
  }

  const baseRenderTrackingStudentV159=renderTrackingStudent;
  renderTrackingStudent=function(){
    const out=baseRenderTrackingStudentV159.apply(this,arguments);
    installCheckinFieldsV159();
    return out;
  };

  const baseSetScoreV159=window.setCheckinScoreV154;
  window.setCheckinScoreV154=function(id,value){
    const input=el(id);
    if(input&&input.classList.contains('v159-score-input')){
      const n=Number(value);
      input.value=Number.isFinite(n)&&n>=1&&n<=10?String(Math.round(n)):'';
      return;
    }
    if(typeof baseSetScoreV159==='function')return baseSetScoreV159.apply(this,arguments);
  };

  if(typeof renderCoachSummary==='function'){
    const baseCoachSummaryV159=renderCoachSummary;
    renderCoachSummary=function(){
      const out=baseCoachSummaryV159.apply(this,arguments);
      if(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'){
        const host=el('coachStudentBody');
        if(host&&!el('v80Student360')&&!el('v159Student360Slot')){
          const slot=document.createElement('div');
          slot.id='v159Student360Slot';
          slot.innerHTML='<div class="card"><div class="empty">Cargando resumen del alumno…</div></div>';
          host.insertBefore(slot,host.firstChild);
        }
      }
      return out;
    };
  }

  if(typeof buildStudent360V80==='function'){
    injectStudent360V80=async function(){
      if(currentProfile?.role!=='coach'||coachTab!=='student'||coachStudentTab!=='summary')return;
      const host=el('coachStudentBody');
      if(!host||el('v80Student360'))return;

      let slot=el('v159Student360Slot');
      if(!slot){
        slot=document.createElement('div');
        slot.id='v159Student360Slot';
        slot.innerHTML='<div class="card"><div class="empty">Cargando resumen del alumno…</div></div>';
        host.insertBefore(slot,host.firstChild);
      }
      if(slot.dataset.loading==='1')return;
      slot.dataset.loading='1';
      try{
        const built=await buildStudent360V80();
        if(!slot.isConnected)return;
        if(!(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'))return;
        slot.outerHTML=built;
      }catch(e){
        if(slot.isConnected)slot.remove();
      }
    };
  }

  if(typeof renderStudent==='function'){
    const baseRenderStudentV159=renderStudent;
    renderStudent=function(){
      const out=baseRenderStudentV159.apply(this,arguments);
      if(mode==='student'&&studentTab==='home'){
        const v=el('view'),hero=v?.querySelector('.hero');
        if(v&&hero&&!el('v81HomeAgenda')&&!el('v159AgendaHomeSlot')){
          const slot=document.createElement('div');
          slot.id='v159AgendaHomeSlot';
          slot.innerHTML='<div class="card"><div class="empty">Cargando agenda de hoy…</div></div>';
          hero.insertAdjacentElement('afterend',slot);
        }
      }
      return out;
    };
  }

  if(typeof loadAgendaV81==='function'&&typeof weekdayLocalV81==='function'){
    injectStudentAgendaHomeV81=async function(){
      if(currentProfile?.role!=='student'||mode!=='student'||studentTab!=='home')return;
      const v=el('view');
      if(!v||el('v81HomeAgenda'))return;
      let slot=el('v159AgendaHomeSlot');
      try{
        await loadAgendaV81();
        if(!(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'))return;
        const ath=currentAthleteRowV73?.();
        if(!ath){slot?.remove();return}
        const row=scheduleForV81(ath.id).find(x=>Number(x.weekday)===weekdayLocalV81());
        const reminders=remindersForV81(ath.id).filter(r=>reminderOccursV81(r,new Date()));
        if(!row&&!reminders.length){slot?.remove();return}

        const s=student(),done=row?completedTodayV81(s,row,new Date()):false,idx=row?findRoutineIndexV81(s,row):-1;
        const card=document.createElement('div');
        card.id='v81HomeAgenda';
        card.className='card v81-today';
        card.style.marginBottom='14px';
        card.innerHTML='<div class="section-title"><div><h3>Agenda de hoy</h3><div class="muted tiny">Tu planificación y recordatorios.</div></div>'+
          '<button class="btn small" onclick="studentTab=\'agenda\';render()">Ver semana</button></div>'+
          (row?'<div class="v81-today-item"><div><strong>'+esc(row.workout_day_name)+'</strong><div class="muted micro">'+fmtTimeV81(row.start_time)+'</div></div>'+
            (done?'<span class="badge green">Registrado</span>':idx>=0?'<button class="btn primary small" onclick="startWorkout('+idx+')">Entrenar</button>':'')+
          '</div>':'')+
          reminders.map(r=>'<div class="v81-today-item" style="margin-top:7px"><div><strong>'+esc(r.title)+'</strong><div class="muted micro">'+esc(r.body||'')+'</div></div></div>').join('');

        slot=el('v159AgendaHomeSlot');
        if(slot?.isConnected)slot.replaceWith(card);
        else{
          const hero=v.querySelector('.hero');
          if(hero)hero.insertAdjacentElement('afterend',card);
        }
      }catch(e){
        slot?.remove();
      }
    };
  }

  function rectOverlapV159(a,b){
    const A=a.getBoundingClientRect(),B=b.getBoundingClientRect();
    return Math.max(0,Math.min(A.right,B.right)-Math.max(A.left,B.left))>2 &&
           Math.max(0,Math.min(A.bottom,B.bottom)-Math.max(A.top,B.top))>2;
  }

  function auditVisibleLayoutV159(){
    const root=el('view');
    if(!root)return {ok:true,overlaps:[]};
    const overlaps=[];
    root.querySelectorAll('.student-row').forEach((row,ri)=>{
      const main=row.querySelector('.student-main');
      const btn=row.querySelector(':scope > button:last-child');
      if(main&&btn&&rectOverlapV159(main,btn))overlaps.push('student-row-'+ri);
    });
    return {ok:overlaps.length===0,overlaps:[...new Set(overlaps)]};
  }

  window.__fjzLayoutV159={
    version:VERSION,
    manualCheckinInput:true,
    maxScore:10,
    coachMobileRowFixed:true,
    stableAsyncSlots:true,
    animationsDisabled:true,
    coalescedLegacyAftershocks:true,
    audit:auditVisibleLayoutV159
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzLayoutV159","manualCheckinInput:true","maxScore:10",
  "coachMobileRowFixed:true","stableAsyncSlots:true","animationsDisabled:true","v159-score-input"
]:
    if marker not in html:
        raise RuntimeError("V15.9 missing marker: "+marker)

if re.search(r'(?:html|body)\s*\{[^}]*overflow-y\s*:\s*hidden',html,re.I|re.S):
    raise RuntimeError("V15.9 root vertical scroll hidden")
if re.search(r'addEventListener\s*\(\s*[\'"]touchmove[\'"].*?preventDefault\s*\(',html,re.I|re.S):
    raise RuntimeError("V15.9 touchmove blocker detected")

print("TEAM FJZ V15.9 legacy aftershocks coalesced:",replacements)
print("TEAM FJZ V15.9 remaining zero-delay timers:",len(re.findall(r"setTimeout\s*\([^,]+,\s*0\s*\)",html,re.S)))
p.write_text(html,encoding="utf-8")
print("TEAM FJZ V15.9 mobile layout/check-in/render polish enabled")
