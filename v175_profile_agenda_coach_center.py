import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v175ProfileAgendaCoachCenterStyles">
/* ===== Coach/student identity: stable first frame ===== */
.v175-coach-profile-hero{
  display:grid!important;
  grid-template-columns:auto minmax(0,1fr) auto!important;
  align-items:center!important;
  gap:14px!important
}
#v175CoachAvatarSlot{
  width:76px;
  height:76px;
  flex:0 0 76px;
  display:grid;
  place-items:center
}
#v175CoachAvatarSlot .v70-avatar.big{
  width:76px!important;
  height:76px!important;
  margin:0!important
}
.v175-coach-profile-info{
  min-width:0!important
}
.v175-coach-profile-info h2{
  margin:6px 0 3px!important;
  line-height:1.1
}
.v175-coach-profile-info p{
  margin:0!important;
  line-height:1.4
}
.v175-coach-profile-actions{
  justify-content:flex-end!important;
  align-items:center!important
}

/* Student own profile: identity stays above fields from the first visible frame. */
#v175StudentProfilePlaceholder,
#v115StudentProfileCard{
  scroll-margin-top:90px
}
.v175-student-identity{
  display:grid;
  grid-template-columns:68px minmax(0,1fr);
  gap:12px;
  align-items:center;
  margin:10px 0 12px;
  padding:11px;
  border:1px solid var(--border);
  border-radius:14px;
  background:rgba(255,255,255,.02)
}
.v175-student-identity .v116-avatar-preview{
  width:68px!important;
  height:68px!important;
  margin:0!important
}
.v175-student-identity-main{
  min-width:0
}
.v175-student-identity-main strong{
  display:block;
  font-size:15px;
  line-height:1.25;
  overflow-wrap:anywhere
}
.v175-student-identity-main .muted{
  margin-top:3px;
  line-height:1.35
}
.v175-student-profile-actions{
  display:flex;
  flex-wrap:wrap;
  gap:6px;
  margin-top:8px
}
#v175StudentProfilePlaceholder .v175-placeholder-grid{
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:8px;
  margin-top:11px
}
#v175StudentProfilePlaceholder .v175-placeholder-cell{
  min-height:55px;
  border-radius:11px;
  background:rgba(255,255,255,.025)
}

/* ===== Single 360 ===== */
#v175Coach360{
  display:grid;
  gap:12px;
  contain:layout style
}
.v175-360-head{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:12px
}
.v175-360-head h3{margin:0;font-size:17px}
.v175-360-head p{margin:4px 0 0;color:var(--muted);font-size:10px;line-height:1.4}
.v175-360-grid{
  display:grid;
  grid-template-columns:repeat(6,minmax(0,1fr));
  gap:8px
}
.v175-360-metric{
  min-width:0;
  padding:10px;
  border:1px solid var(--border);
  border-radius:12px;
  background:rgba(255,255,255,.02)
}
.v175-360-metric strong{
  display:block;
  font-size:16px;
  line-height:1.15;
  overflow-wrap:anywhere
}
.v175-360-metric span{
  display:block;
  margin-top:4px;
  color:var(--muted);
  font-size:9px;
  line-height:1.3
}
.v175-360-section{
  padding-top:12px;
  border-top:1px solid var(--border)
}
.v175-360-section-head{
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  gap:10px;
  margin-bottom:9px
}
.v175-360-section-head h4{margin:0;font-size:12px}
.v175-360-section-head p{margin:3px 0 0;color:var(--muted);font-size:9px;line-height:1.4}
.v175-status-row{
  display:flex;
  gap:6px;
  flex-wrap:wrap
}
.v175-status-chip{
  display:inline-flex;
  align-items:center;
  min-height:28px;
  padding:5px 8px;
  border:1px solid var(--border);
  border-radius:999px;
  background:rgba(255,255,255,.02);
  color:var(--muted);
  font-size:9px;
  line-height:1.2
}
.v175-status-chip.warn{
  color:#ffc5ca;
  border-color:rgba(255,82,97,.3);
  background:rgba(255,82,97,.055)
}
.v175-status-chip.good{
  color:#baf2d1;
  border-color:rgba(55,204,128,.25);
  background:rgba(55,204,128,.045)
}
.v175-executive{
  padding:10px 11px;
  border:1px solid rgba(90,167,255,.2);
  border-radius:12px;
  background:rgba(90,167,255,.04);
  font-size:10px;
  line-height:1.45;
  margin-bottom:8px
}
.v175-assistant-list{
  display:grid;
  gap:8px
}
.v175-advice{
  padding:10px 11px;
  border:1px solid var(--border);
  border-radius:12px;
  background:rgba(255,255,255,.02)
}
.v175-advice.review{
  border-color:rgba(255,82,97,.26);
  background:rgba(255,82,97,.045)
}
.v175-advice.good{
  border-color:rgba(55,204,128,.22);
  background:rgba(55,204,128,.035)
}
.v175-advice-top{
  display:flex;
  justify-content:space-between;
  gap:8px;
  align-items:flex-start
}
.v175-advice h5{margin:0;font-size:11px;line-height:1.3}
.v175-advice p{margin:5px 0 0;color:var(--muted);font-size:10px;line-height:1.4}
.v175-evidence{
  margin-top:7px;
  padding-top:7px;
  border-top:1px dashed rgba(255,255,255,.08);
  color:var(--muted);
  font-size:9px;
  line-height:1.4
}
.v175-advice-actions{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.v175-message{
  padding:10px 11px;
  border:1px solid var(--border);
  border-radius:11px;
  background:rgba(255,255,255,.02);
  font-size:10px;
  line-height:1.4
}

/* ===== Agenda attention ===== */
.v175-agenda-tab-badge,
.v175-agenda-row-badge{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  min-width:19px;
  min-height:19px;
  padding:2px 6px;
  margin-left:5px;
  border-radius:999px;
  background:rgba(255,31,47,.14);
  border:1px solid rgba(255,31,47,.38);
  color:#ffc5ca;
  font-size:9px;
  font-weight:900;
  line-height:1
}
.v175-agenda-row-badge{
  margin:4px 0 0!important;
  width:max-content
}
#v175AgendaBanner{
  margin-bottom:12px;
  border-color:rgba(255,159,67,.28);
  background:rgba(255,159,67,.035)
}
.v175-agenda-list{
  display:grid;
  gap:7px;
  margin-top:9px
}
.v175-agenda-item{
  display:flex;
  justify-content:space-between;
  gap:10px;
  align-items:flex-start;
  padding:8px 9px;
  border:1px solid var(--border);
  border-radius:10px;
  background:rgba(255,255,255,.02)
}
.v175-agenda-item strong{display:block;font-size:10px}
.v175-agenda-item .muted{margin-top:2px}
.v175-agenda-hero-btn{
  cursor:pointer
}

/* ===== One unified coach center ===== */
#v96CoachAlerts.v175-coach-center{
  display:block!important
}
#v96CoachAlerts .v96-alert-summary{
  display:none!important
}
#v96CoachAlerts .v170-kpis.v175-center-stats{
  display:grid!important;
  grid-template-columns:repeat(5,minmax(0,1fr))!important;
  gap:8px!important;
  margin:10px 0 12px!important
}
#v96CoachAlerts .v170-kpis.v175-center-stats .v170-kpi{
  padding:10px!important;
  min-width:0!important
}
#v96CoachAlerts .v170-kpis.v175-center-stats .v170-kpi strong{
  font-size:20px!important
}
#v96CoachAlerts .v170-kpis.v175-center-stats .v170-kpi span{
  font-size:9px!important
}
.v175-center-agenda strong{
  color:#ffd09a
}

@media(max-width:980px){
  .v175-360-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
  #v96CoachAlerts .v170-kpis.v175-center-stats{
    grid-template-columns:repeat(3,minmax(0,1fr))!important
  }
}
@media(max-width:760px){
  .v175-coach-profile-hero{
    grid-template-columns:64px minmax(0,1fr)!important;
    gap:10px!important;
    align-items:start!important
  }
  #v175CoachAvatarSlot{
    width:64px;height:64px
  }
  #v175CoachAvatarSlot .v70-avatar.big{
    width:64px!important;height:64px!important
  }
  .v175-coach-profile-actions{
    grid-column:1/-1!important;
    justify-content:flex-start!important;
    width:100%!important
  }
  .v175-360-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .v175-360-head,.v175-360-section-head{display:block}
  .v175-360-head>.muted,.v175-360-section-head>.muted{display:block;margin-top:5px}
  #v96CoachAlerts .v170-kpis.v175-center-stats{
    grid-template-columns:repeat(2,minmax(0,1fr))!important
  }
  .v175-student-identity{grid-template-columns:60px minmax(0,1fr)}
  .v175-student-identity .v116-avatar-preview{width:60px!important;height:60px!important}
  #v175StudentProfilePlaceholder .v175-placeholder-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .v175-agenda-item{display:block}
  .v175-agenda-item .badge{margin-top:5px}
}
@media(max-width:480px){
  #v96CoachAlerts .v170-kpis.v175-center-stats{
    grid-template-columns:1fr 1fr!important
  }
}
</style>
"""

js=r"""
<script id="v175ProfileAgendaCoachCenterRuntime">
(function(){
  const VERSION='17.5';
  let summarySeqV175=0;
  const agendaCacheV175={loadedAt:0,reminders:[],checks:[],inflight:null};
  const AGENDA_CACHE_MS=30000;

  function todayKeyV175(){
    const d=new Date(),y=d.getFullYear(),m=String(d.getMonth()+1).padStart(2,'0'),day=String(d.getDate()).padStart(2,'0');
    return y+'-'+m+'-'+day;
  }
  function parseLocalDateV175(s){
    if(!s)return null;
    const p=String(s).slice(0,10).split('-').map(Number);
    if(p.length!==3||p.some(x=>!Number.isFinite(x)))return null;
    return new Date(p[0],p[1]-1,p[2],12,0,0,0);
  }
  function dayDiffV175(s){
    const a=parseLocalDateV175(s),b=parseLocalDateV175(todayKeyV175());
    if(!a||!b)return null;
    return Math.round((a-b)/86400000);
  }
  function weekdayMondayV175(){
    return (new Date().getDay()+6)%7;
  }
  function agendaDateLabelV175(s){
    const d=dayDiffV175(s);
    if(d===null)return s||'Sin fecha';
    if(d<0)return 'Vencido · '+fmtDate(s);
    if(d===0)return 'Hoy';
    if(d===1)return 'Mañana';
    return 'En '+d+' días · '+fmtDate(s);
  }

  async function loadAgendaAttentionV175(force=false){
    if(!cloudEnabled||!supabaseClient)return agendaCacheV175;
    if(!force&&agendaCacheV175.loadedAt&&Date.now()-agendaCacheV175.loadedAt<AGENDA_CACHE_MS)return agendaCacheV175;
    if(agendaCacheV175.inflight)return agendaCacheV175.inflight;
    agendaCacheV175.inflight=(async()=>{
      const [r,c]=await Promise.all([
        supabaseClient.from('athlete_reminders')
          .select('id,athlete_id,title,body,category,schedule_type,reminder_date,weekday,remind_time,active')
          .eq('active',true),
        supabaseClient.from('checkin_schedules')
          .select('id,athlete_id,cadence,next_due,remind_time,notes,active,last_completed_at')
          .eq('active',true)
      ]);
      if(r.error)throw r.error;
      if(c.error)throw c.error;
      agendaCacheV175.reminders=r.data||[];
      agendaCacheV175.checks=c.data||[];
      agendaCacheV175.loadedAt=Date.now();
      return agendaCacheV175;
    })().finally(()=>{agendaCacheV175.inflight=null});
    return agendaCacheV175.inflight;
  }

  function agendaItemsV175(athleteId){
    if(!athleteId)return [];
    const out=[],todayWd=weekdayMondayV175();
    (agendaCacheV175.reminders||[]).filter(x=>x.athlete_id===athleteId).forEach(x=>{
      if(x.schedule_type==='once'){
        const diff=dayDiffV175(x.reminder_date);
        if(diff!==null&&diff<=7){
          out.push({kind:'reminder',id:x.id,title:x.title||'Recordatorio',date:x.reminder_date,diff,meta:agendaDateLabelV175(x.reminder_date)});
        }
      }else if(x.schedule_type==='weekly'&&Number(x.weekday)===todayWd){
        out.push({kind:'reminder',id:x.id,title:x.title||'Recordatorio semanal',date:todayKeyV175(),diff:0,meta:'Hoy · semanal'});
      }
    });
    (agendaCacheV175.checks||[]).filter(x=>x.athlete_id===athleteId).forEach(x=>{
      const diff=dayDiffV175(x.next_due);
      if(diff!==null&&diff<=7){
        out.push({kind:'checkin',id:x.id,title:x.notes||'Check-in programado',date:x.next_due,diff,meta:agendaDateLabelV175(x.next_due)});
      }
    });
    return out.sort((a,b)=>(a.diff??999)-(b.diff??999));
  }
  function agendaSummaryV175(athleteId){
    const items=agendaItemsV175(athleteId);
    return {
      items,
      total:items.length,
      overdue:items.filter(x=>x.diff<0).length,
      today:items.filter(x=>x.diff===0).length,
      upcoming:items.filter(x=>x.diff>0).length
    };
  }

  /* ---------- Stable coach profile identity ---------- */
  function coachAthleteV175(){
    const s=student?.();
    return s?.id?cloudAthletes?.get?.(s.id)||null:null;
  }
  function ensureCoachHeroFrameV175(){
    if(!(currentProfile?.role==='coach'&&coachTab==='student'))return;
    const hero=el('view')?.querySelector('.hero');
    const s=student?.();
    if(!hero||!s)return;

    hero.classList.add('v175-coach-profile-hero');

    let slot=el('v175CoachAvatarSlot');
    if(!slot){
      slot=document.createElement('div');
      slot.id='v175CoachAvatarSlot';
      slot.innerHTML='<div class="v70-avatar big">'+esc((s.name||'AL').slice(0,2).toUpperCase())+'</div>';
      hero.insertBefore(slot,hero.firstChild);
    }

    const children=[...hero.children];
    const info=children.find(x=>x!==slot&&!x.classList.contains('pill-row')&&x.id!=='v70CoachStudentAvatar');
    const actions=hero.querySelector('.pill-row');
    if(info)info.classList.add('v175-coach-profile-info');
    if(actions)actions.classList.add('v175-coach-profile-actions');

    const old=el('v70CoachStudentAvatar');
    if(old){
      const visual=old.querySelector('.v70-avatar')||old.firstElementChild;
      if(visual)slot.innerHTML=visual.outerHTML;
      old.remove();
    }
  }
  async function hydrateCoachAvatarV175(){
    ensureCoachHeroFrameV175();
    if(!(currentProfile?.role==='coach'&&coachTab==='student'))return;
    const hero=el('view')?.querySelector('.hero'),slot=el('v175CoachAvatarSlot'),s=student?.(),ath=coachAthleteV175();
    if(!hero||!slot||!s||!ath?.user_id||typeof avatarHtmlV70!=='function')return;
    const key=String(s.id);
    try{
      const avatar=await avatarHtmlV70(ath.user_id,s.name,'big');
      if(!(currentProfile?.role==='coach'&&coachTab==='student'&&String(student()?.id)===key))return;
      if(el('v175CoachAvatarSlot'))el('v175CoachAvatarSlot').innerHTML=avatar;
    }catch(e){}
  }
  const coachAvatarV175=async function(){await hydrateCoachAvatarV175();return null};
  try{injectCoachStudentAvatarV70=coachAvatarV175}catch(e){}
  try{window.injectCoachStudentAvatarV70=coachAvatarV175}catch(e){}

  /* ---------- Stable student own identity ---------- */
  function studentProfileAnchorV175(view){
    return el('studentMainTabs')||view?.querySelector('.hero')||null;
  }
  function studentIdentityShellV175(){
    const s=student?.()||{};
    return '<div class="v175-student-identity">'+
      '<div class="v116-avatar-preview" id="v116AvatarPreview">'+esc((s.name||'?').slice(0,2).toUpperCase())+'</div>'+
      '<div class="v175-student-identity-main"><strong>'+esc(s.name||'Alumno')+'</strong>'+
      '<div class="muted tiny">'+esc(s.goal||'Plan personalizado')+'</div>'+
      '<div class="v175-student-profile-actions">'+
        '<button class="btn small" type="button" onclick="document.getElementById(\'v116AvatarInput\')?.click()">Cambiar foto</button>'+
        (currentProfile?.avatar_url?'<button class="btn ghost small" type="button" onclick="removeMyAvatarV116()">Quitar</button>':'')+
        '<input id="v116AvatarInput" class="v116-file" type="file" accept="image/jpeg,image/png,image/webp,image/heic,image/heif,image/*" onchange="uploadMyAvatarV116(this)">'+
      '</div><div id="v116AvatarStatus" class="muted micro" style="margin-top:6px"></div></div></div>';
  }
  function ensureStudentProfilePlaceholderV175(){
    if(!(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'))return;
    const view=el('view');if(!view)return;
    const card=el('v115StudentProfileCard');
    if(card){finalizeStudentProfileV175();return}
    if(el('v175StudentProfilePlaceholder'))return;
    const ph=document.createElement('div');
    ph.id='v175StudentProfilePlaceholder';
    ph.className='card';
    ph.innerHTML='<div class="section-title"><div><h3>Mi perfil</h3><div class="muted tiny">Foto y datos personales.</div></div></div>'+
      studentIdentityShellV175()+
      '<div class="v175-placeholder-grid">'+Array.from({length:4},()=>'<div class="v175-placeholder-cell"></div>').join('')+'</div>';
    const anchor=studentProfileAnchorV175(view);
    if(anchor)anchor.insertAdjacentElement('afterend',ph);else view.prepend(ph);
  }
  async function fillStudentAvatarV175(){
    const preview=el('v116AvatarPreview');
    if(!preview||!currentUser?.id||!supabaseClient)return;
    try{
      let path=currentProfile?.avatar_url||'';
      if(!path&&typeof profilePathV70==='function')path=await profilePathV70(currentUser.id);
      if(!path)return;
      let url='';
      if(typeof signedAvatarV70==='function')url=await signedAvatarV70(path);
      else{
        const r=await supabaseClient.storage.from('profile-photos').createSignedUrl(path,3600);
        url=r.data?.signedUrl||'';
      }
      if(url&&el('v116AvatarPreview'))el('v116AvatarPreview').innerHTML='<img src="'+url+'" alt="Foto de perfil">';
    }catch(e){}
  }
  function finalizeStudentProfileV175(){
    if(!(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'))return;
    const view=el('view'),card=el('v115StudentProfileCard');
    if(!view||!card)return;
    const anchor=studentProfileAnchorV175(view);
    if(anchor&&anchor.nextElementSibling!==card)anchor.insertAdjacentElement('afterend',card);
    el('v175StudentProfilePlaceholder')?.remove();

    const title=card.querySelector('.section-title h3');
    const desc=card.querySelector('.section-title .muted');
    if(title)title.textContent='Mi perfil';
    if(desc)desc.textContent='Foto y datos personales.';

    let old=el('v116AvatarBox');
    if(old)old.remove();
    let identity=card.querySelector('.v175-student-identity');
    if(!identity){
      const grid=card.querySelector('.v115-profile-grid');
      if(grid)grid.insertAdjacentHTML('beforebegin',studentIdentityShellV175());
      else card.insertAdjacentHTML('beforeend',studentIdentityShellV175());
    }
    fillStudentAvatarV175();
  }
  const studentAvatarV175=async function(){finalizeStudentProfileV175();await fillStudentAvatarV175();return null};
  try{injectAvatarV116=studentAvatarV175}catch(e){}
  try{window.injectAvatarV116=studentAvatarV175}catch(e){}

  /* ---------- 360 + pro assistant ---------- */
  function metricV175(value,label){
    return '<div class="v175-360-metric"><strong>'+esc(String(value??'—'))+'</strong><span>'+esc(label)+'</span></div>';
  }
  function chipV175(text,type=''){
    return '<span class="v175-status-chip '+esc(type)+'">'+esc(text)+'</span>';
  }
  function recentSessionsV175(s,days){
    const cut=Date.now()-days*86400000;
    return (s?.sessions||[]).filter(x=>{
      const t=new Date(x.date||x.completedAt||0).getTime();
      return Number.isFinite(t)&&t>=cut
    });
  }
  function nutritionSummaryV175(){
    try{
      if(!nutritionCache?.plan)return {active:false,logging:false,pct:null,expected:0,completed:0};
      const logging=typeof nutritionLoggingEnabledV64==='function'?nutritionLoggingEnabledV64():true;
      if(!logging)return {active:true,logging:false,pct:null,expected:0,completed:0};
      if(typeof nutritionAdherenceV63==='function'){
        const a=nutritionAdherenceV63();
        return {active:true,logging:true,pct:Number(a.pct),expected:Number(a.expected)||0,completed:Number(a.completed)||0};
      }
      return {active:true,logging:true,pct:null,expected:0,completed:0};
    }catch(e){return {active:!!nutritionCache?.plan,logging:false,pct:null,expected:0,completed:0}}
  }
  function pendingFeedbackV175(){
    try{return typeof pendingFeedbackV73==='function'?(pendingFeedbackV73()||[]):[]}catch(e){return []}
  }
  function assistantV175(agenda){
    const s=student(),checks=trackingCache?.checkins||[],latest=checks[0]||null,prev=checks[1]||null;
    const pending=pendingFeedbackV175(),nutrition=nutritionSummaryV175();
    const s7=recentSessionsV175(s,7),s14=recentSessionsV175(s,14);
    const planned=Math.max(1,Number(s?.plannedPerWeek)||s?.days?.length||1);
    const list=[];
    const add=(type,priority,title,action,evidence,tab)=>list.push({type,priority,title,action,evidence,tab});

    if(pending.length){
      const names=[...new Set(pending.map(x=>x.exercise_name).filter(Boolean))].slice(0,3);
      add('review',100,'Resolver feedback técnico primero',
        'Revisaría estos comentarios antes de tocar volumen, cargas o progresiones.',
        pending.length+' pendiente'+(pending.length===1?'':'s')+(names.length?' · '+names.join(' · '):''),
        'routine');
    }

    if(!latest){
      add('review',96,'Completar contexto de recuperación',
        'Pediría un check-in antes de hacer un ajuste importante. Falta contexto de sueño, energía, estrés, recuperación y adherencia.',
        'No hay un check-in reciente disponible.',
        'tracking');
    }else{
      const red=[];
      if(Number(latest.sleep_quality)<=4)red.push('sueño '+latest.sleep_quality+'/10');
      if(Number(latest.energy_level)<=4)red.push('energía '+latest.energy_level+'/10');
      if(Number(latest.recovery_level)<=4)red.push('recuperación '+latest.recovery_level+'/10');
      if(Number(latest.stress_level)>=8)red.push('estrés '+latest.stress_level+'/10');
      if(red.length>=2){
        add('review',94,'No aumentaría exigencia todavía',
          'Primero revisaría descanso, estrés, horarios y tolerancia de la rutina. Hay varias señales que apuntan en la misma dirección.',
          red.join(' · '),
          'tracking');
      }
      if(Number(latest.adherence_level)<=5){
        add('review',90,'Encontrar la barrera de adherencia',
          'Antes de sumar tareas o complejidad, buscaría qué parte del plan está costando sostener y simplificaría ahí.',
          'Adherencia '+latest.adherence_level+'/10.',
          'tracking');
      }
      if(prev){
        const changes=[];
        if(Number(latest.energy_level)-Number(prev.energy_level)<=-2)changes.push('energía '+prev.energy_level+'→'+latest.energy_level);
        if(Number(latest.recovery_level)-Number(prev.recovery_level)<=-2)changes.push('recuperación '+prev.recovery_level+'→'+latest.recovery_level);
        if(Number(latest.stress_level)-Number(prev.stress_level)>=2)changes.push('estrés '+prev.stress_level+'→'+latest.stress_level);
        if(changes.length>=2){
          add('review',88,'La tendencia semanal merece revisión',
            'No es un valor aislado: cambiaron varias señales respecto del check-in anterior. Confirmaría qué cambió esta semana.',
            changes.join(' · '),
            'tracking');
        }
      }
    }

    if(agenda?.total){
      const first=agenda.items[0];
      add(first?.diff<0?'review':'info',92,'Hay una tarea de Agenda próxima',
        'La revisaría antes de cerrar el seguimiento de este alumno para no dejar pasar un chequeo o recordatorio.',
        agenda.total+' pendiente'+(agenda.total===1?'':'s')+' · '+(first?.title||'Agenda')+' · '+(first?.meta||''),
        'agenda');
    }

    const days=typeof daysSince==='function'?daysSince(s?.lastWorkout):null;
    if(Number.isFinite(days)&&days>=7){
      add('review',91,'Confirmar continuidad de entrenamiento',
        'Verificaría si realmente no entrenó, si faltó registrar sesiones o si hubo un problema de adherencia antes de cambiar la rutina.',
        'Último entrenamiento registrado hace '+days+' días.',
        'history');
    }else if(s7.length<Math.ceil(planned*.6)){
      add('info',76,'Frecuencia semanal por debajo de lo previsto',
        'Confirmaría adherencia y disponibilidad antes de agregar o quitar trabajo.',
        s7.length+' de '+planned+' sesiones previstas esta semana.',
        'routine');
    }

    const incomplete=s14.filter(x=>(Number(x.summary?.skippedExercises)||0)>0||(Number(x.summary?.partial)||0)>0);
    if(incomplete.length>=2){
      add('review',84,'La sesión puede estar siendo demasiado difícil de completar',
        'Revisaría duración, orden de ejercicios y qué bloques suelen quedar afuera antes de sumar volumen.',
        incomplete.length+' sesiones parciales en 14 días.',
        'history');
    }

    const results=s14.flatMap(x=>x.exerciseResults||[]);
    const needsReview=results.filter(x=>['down','plateau','review'].includes(x.recommendation?.type));
    const progress=results.filter(x=>['up','rep','load'].includes(x.recommendation?.type));
    if(needsReview.length>=2){
      const names=[...new Set(needsReview.map(x=>x.name).filter(Boolean))].slice(0,3);
      add('info',80,'Revisar ejercicios puntuales, no toda la rutina',
        'Concentraría el ajuste en los ejercicios que muestran señales de estancamiento o revisión.',
        needsReview.length+' señales'+(names.length?' · '+names.join(' · '):''),
        'progress');
    }

    if(nutrition.active&&nutrition.logging&&nutrition.expected>=4&&Number.isFinite(nutrition.pct)&&nutrition.pct<50){
      add('info',70,'Confirmar el registro nutricional antes de ajustar',
        'Primero distinguiría si faltó cumplir el plan o si simplemente faltó registrarlo.',
        nutrition.completed+' de '+nutrition.expected+' registros · '+Math.round(nutrition.pct)+'%.',
        'nutrition');
    }

    if(latest&&progress.length>=2&&Number(latest.energy_level)>=6&&Number(latest.recovery_level)>=6&&Number(latest.stress_level)<=6){
      add('good',48,'Hay margen para progresión selectiva',
        'Progresaría solo donde cumplió el objetivo técnico y de repeticiones, no de forma automática en toda la rutina.',
        progress.length+' señales de progresión con recuperación favorable.',
        'progress');
    }

    if(!list.length){
      add('good',20,'Mantener la estructura y seguir observando',
        'No aparece una señal fuerte para cambiar el plan hoy. Mantendría la base y revisaría tendencia, técnica y adherencia.',
        'Sin banderas principales con los datos disponibles.',
        'progress');
    }

    const dataPoints=[
      latest?'check-in':null,
      prev?'tendencia':null,
      s14.length?'entrenamiento':null,
      nutrition.active?'nutrición':null,
      pending?'feedback':null,
      agenda?'agenda':null
    ].filter(Boolean);
    const confidence=dataPoints.length>=5?'Alta':dataPoints.length>=3?'Media':'Baja';
    const executive=list[0]?.type==='review'
      ?'La prioridad principal es '+list[0].title.toLowerCase()+'. Conviene resolver eso antes de hacer cambios amplios.'
      :list[0]?.type==='good'
        ?'El panorama actual es estable. La mejor decisión parece ser mantener la base y progresar solo donde haya evidencia.'
        :'Hay información útil para revisar, pero no una razón fuerte para cambiar todo el plan.';

    return {items:list.sort((a,b)=>b.priority-a.priority).slice(0,3),confidence,dataPoints,executive};
  }
  function adviceHtmlV175(x,i){
    const badge=x.type==='review'
      ?'<span class="badge red">Prioridad '+(i+1)+'</span>'
      :x.type==='good'
        ?'<span class="badge green">Oportunidad</span>'
        :'<span class="badge blue">Revisar</span>';
    const labels={routine:'Rutina',tracking:'Seguimiento',history:'Historial',progress:'Progreso',nutrition:'Nutrición',agenda:'Agenda'};
    return '<div class="v175-advice '+esc(x.type)+'">'+
      '<div class="v175-advice-top"><h5>'+esc(x.title)+'</h5>'+badge+'</div>'+
      '<p><strong>Qué haría:</strong> '+esc(x.action)+'</p>'+
      '<div class="v175-evidence"><strong>Evidencia:</strong> '+esc(x.evidence)+'</div>'+
      '<div class="v175-advice-actions"><button class="btn small" onclick="coachStudentTab=\''+esc(x.tab)+'\';render()">Abrir '+esc(labels[x.tab]||'sección')+'</button></div>'+
    '</div>';
  }

  async function hydrateSummaryV175(){
    const run=++summarySeqV175,jobs=[];
    const aid=typeof trackingAthleteId==='function'?trackingAthleteId():null;
    if(aid&&trackingLoadedFor!==aid&&typeof loadTracking==='function')jobs.push(loadTracking(false));

    const nAid=typeof nutritionAthleteId==='function'?nutritionAthleteId():null;
    const nutritionReady=nAid&&nutritionLoadedAthlete===nAid&&nutritionFoodsLoaded===true;
    if(nAid&&!nutritionReady&&typeof loadNutrition==='function')jobs.push(loadNutrition(false,nutritionCache?.date||dateInputToday()));

    try{if(typeof loadExerciseFeedbackV73==='function')jobs.push(loadExerciseFeedbackV73(false))}catch(e){}
    jobs.push(loadAgendaAttentionV175(false));

    await Promise.allSettled(jobs);
    if(run!==summarySeqV175||!(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='summary'))return;
    const s=student(),latest=trackingCache?.checkins?.[0]||null,measurement=trackingCache?.measurements?.[0]||null;
    const sessions30=recentSessionsV175(s,30).length;
    const weight=measurement?.weight_kg??latest?.weight_kg??null;
    const ath=coachAthleteV175();
    const agenda=agendaSummaryV175(ath?.id);
    const nutrition=nutritionSummaryV175();
    const pending=pendingFeedbackV175();

    if(el('v175Metrics'))el('v175Metrics').innerHTML=
      metricV175(adherence(s)+'%','Adherencia 7 días')+
      metricV175(sessions30,'Entrenos 30 días')+
      metricV175(fmtDate(s.lastWorkout),'Último entreno')+
      metricV175(weight!=null?round1(weight)+' kg':'—','Peso reciente')+
      metricV175(latest?.energy_level!=null?latest.energy_level+'/10':'—','Energía')+
      metricV175(latest?.recovery_level!=null?latest.recovery_level+'/10':'—','Recuperación');

    const chips=[];
    chips.push(latest?chipV175('Check-in '+fmtDate(latest.week_start),'good'):chipV175('Sin check-in reciente','warn'));
    if(latest?.sleep_quality!=null)chips.push(chipV175('Sueño '+latest.sleep_quality+'/10',Number(latest.sleep_quality)<=4?'warn':''));
    if(latest?.stress_level!=null)chips.push(chipV175('Estrés '+latest.stress_level+'/10',Number(latest.stress_level)>=8?'warn':''));
    chips.push(nutrition.active?chipV175('Nutrición activa','good'):chipV175('Sin plan nutricional','warn'));
    if(pending.length)chips.push(chipV175(pending.length+' comentario'+(pending.length===1?'':'s')+' pendiente'+(pending.length===1?'':'s'),'warn'));
    if(agenda.total)chips.push(chipV175('Agenda · '+agenda.total,agenda.overdue?'warn':''));
    if(el('v175Status'))el('v175Status').innerHTML=chips.join('');

    const a=assistantV175(agenda);
    if(el('v175Executive'))el('v175Executive').textContent=a.executive;
    if(el('v175Coverage'))el('v175Coverage').textContent='Cobertura '+a.confidence+' · '+(a.dataPoints.join(' · ')||'pocos datos');
    if(el('v175Assistant'))el('v175Assistant').innerHTML=a.items.map(adviceHtmlV175).join('');
    if(el('v175SummaryState'))el('v175SummaryState').textContent='Actualizado';
    enhanceAgendaIndicatorsV175();
  }

  window.renderCoachSummary=function(){
    const s=student(),b=el('coachStudentBody');if(!b)return;
    b.innerHTML='<div class="card" id="v175Coach360">'+
      '<div class="v175-360-head"><div><h3>Resumen 360</h3><p>Una sola lectura del alumno: rendimiento, seguimiento, agenda y prioridades del coach.</p></div><span id="v175SummaryState" class="muted micro">Actualizando…</span></div>'+
      '<div id="v175Metrics" class="v175-360-grid">'+
        metricV175(adherence(s)+'%','Adherencia 7 días')+metricV175('—','Entrenos 30 días')+metricV175(fmtDate(s.lastWorkout),'Último entreno')+
        metricV175('—','Peso reciente')+metricV175('—','Energía')+metricV175('—','Recuperación')+
      '</div>'+
      '<div class="v175-360-section"><div class="v175-360-section-head"><div><h4>Estado conectado</h4><p>Señales rápidas del check-in, nutrición, feedback y Agenda.</p></div></div><div id="v175Status" class="v175-status-row">'+chipV175('Cargando datos…')+'</div></div>'+
      '<div class="v175-360-section"><div class="v175-360-section-head"><div><h4>Asistente Coach</h4><p>Prioriza decisiones concretas cruzando tendencia, entrenamiento, recuperación, nutrición, feedback y Agenda.</p></div><span id="v175Coverage" class="muted micro">Evaluando datos…</span></div>'+
        '<div id="v175Executive" class="v175-executive">Analizando información disponible…</div><div id="v175Assistant" class="v175-assistant-list"></div></div>'+
      '<div class="v175-360-section"><div class="v175-360-section-head"><div><h4>Mensaje para el alumno</h4><p>Tu indicación general visible para este alumno.</p></div><button class="btn small" onclick="editCoachMessage()">Editar</button></div>'+
        '<div class="v175-message">'+esc(s?.coachMessage||'Sin mensaje cargado.')+'</div></div>'+
    '</div>';
    hydrateSummaryV175();
  };

  /* ---------- Agenda badges/banner ---------- */
  function agendaTabButtonV175(){
    return [...document.querySelectorAll('.tabs .tab')].find(b=>{
      const on=b.getAttribute('onclick')||'';
      return on.includes("coachStudentTab='agenda'")||/^Agenda\b/i.test((b.textContent||'').trim());
    })||null;
  }
  function addAgendaTabBadgeV175(total){
    const btn=agendaTabButtonV175();if(!btn)return;
    btn.querySelector('.v175-agenda-tab-badge')?.remove();
    if(total){
      btn.insertAdjacentHTML('beforeend','<span class="v175-agenda-tab-badge">'+total+'</span>');
    }
  }
  function agendaBannerHtmlV175(sum){
    if(!sum.total)return '';
    const rows=sum.items.slice(0,5).map(x=>
      '<div class="v175-agenda-item"><div><strong>'+esc(x.title)+'</strong><div class="muted tiny">'+esc(x.kind==='checkin'?'Chequeo programado':'Recordatorio')+'</div></div>'+
      '<span class="badge '+(x.diff<0?'red':x.diff===0?'amber':'blue')+'">'+esc(x.meta)+'</span></div>'
    ).join('');
    return '<div class="card" id="v175AgendaBanner"><div class="section-title"><div><h3>Para revisar en Agenda</h3><div class="muted tiny">Fechas próximas, vencidas y chequeos programados.</div></div><span class="badge '+(sum.overdue?'red':'amber')+'">'+sum.total+' pendiente'+(sum.total===1?'':'s')+'</span></div><div class="v175-agenda-list">'+rows+'</div></div>';
  }
  function injectAgendaBannerV175(){
    if(!(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='agenda'))return;
    const host=el('coachStudentBody'),ath=coachAthleteV175();
    if(!host||!ath)return;
    el('v175AgendaBanner')?.remove();
    const sum=agendaSummaryV175(ath.id);
    const html=agendaBannerHtmlV175(sum);
    if(html)host.insertAdjacentHTML('afterbegin',html);
  }
  function watchAgendaShellOnceV175(){
    if(!(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='agenda'))return;
    const host=el('coachStudentBody');if(!host)return;
    const ready=()=>host.querySelector('.v165-agenda-shell,.card');
    if(ready()){injectAgendaBannerV175();return}
    const ob=new MutationObserver(()=>{
      if(ready()){
        ob.disconnect();
        injectAgendaBannerV175();
      }
    });
    ob.observe(host,{childList:true,subtree:false});
    setTimeout(()=>ob.disconnect(),3500);
  }

  function enhanceAgendaIndicatorsV175(){
    if(currentProfile?.role!=='coach')return;
    if(coachTab==='student'){
      const ath=coachAthleteV175(),sum=agendaSummaryV175(ath?.id);
      addAgendaTabBadgeV175(sum.total);
      const hero=el('view')?.querySelector('.hero');
      const actions=hero?.querySelector('.pill-row');
      actions?.querySelector('.v175-agenda-hero-btn')?.remove();
      if(sum.total&&actions){
        const b=document.createElement('button');
        b.type='button';
        b.className='btn ghost small v175-agenda-hero-btn';
        b.textContent='Agenda · '+sum.total;
        b.onclick=()=>{coachStudentTab='agenda';render()};
        actions.prepend(b);
      }
      if(coachStudentTab==='agenda')watchAgendaShellOnceV175();
    }

    if(coachTab==='dashboard'){
      let total=0;
      document.querySelectorAll('.student-row[data-client-id]').forEach(row=>{
        row.querySelector('.v175-agenda-row-badge')?.remove();
        const cid=row.getAttribute('data-client-id'),ath=cloudAthletes?.get?.(cid);
        const sum=agendaSummaryV175(ath?.id);
        total+=sum.total;
        if(sum.total){
          const main=row.querySelector('.student-main');
          if(main)main.insertAdjacentHTML('beforeend','<span class="v175-agenda-row-badge">Agenda · '+sum.total+'</span>');
        }
      });
      const target=el('v175DashboardAgendaCount');
      if(target)target.textContent=String(total);
    }
  }

  /* ---------- Merge dashboard KPIs into alert center ---------- */
  function unifyCoachCenterV175(){
    if(!(currentProfile?.role==='coach'&&coachTab==='dashboard'))return;
    const center=el('v96CoachAlerts'),stats=document.querySelector('.v170-kpis');
    if(!center||!stats)return;
    center.classList.add('v175-coach-center');
    stats.classList.add('v175-center-stats');

    const head=center.querySelector('.v170-section-head,.section-title');
    if(head&&stats.parentElement!==center){
      head.insertAdjacentElement('afterend',stats);
    }

    if(!el('v175DashboardAgendaCount')){
      stats.insertAdjacentHTML('beforeend','<div class="v170-kpi v175-center-agenda"><strong id="v175DashboardAgendaCount">—</strong><span>Agenda próxima</span></div>');
    }

    const h3=head?.querySelector('h3');
    const p=head?.querySelector('p');
    if(h3)h3.textContent='Centro de seguimiento';
    if(p)p.textContent='Estado general, prioridades y alertas en una sola vista.';

    const dashboard=stats.closest('.v170-dashboard');
    if(dashboard)dashboard.classList.add('v175-dashboard-unified');
  }

  async function hydrateDashboardV175(){
    try{await loadAgendaAttentionV175(false)}catch(e){}
    if(!(currentProfile?.role==='coach'&&coachTab==='dashboard'))return;
    unifyCoachCenterV175();
    enhanceAgendaIndicatorsV175();
  }

  /* ---------- Final UI pass ---------- */
  function postRenderV175(){
    ensureCoachHeroFrameV175();
    ensureStudentProfilePlaceholderV175();
    finalizeStudentProfileV175();
    unifyCoachCenterV175();

    if(currentProfile?.role==='coach'){
      loadAgendaAttentionV175(false).then(()=>{
        enhanceAgendaIndicatorsV175();
        if(coachTab==='dashboard')unifyCoachCenterV175();
      }).catch(()=>{});
    }

    hydrateCoachAvatarV175();
    if(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'){
      try{
        const fn=typeof injectMyProfileV115==='function'?injectMyProfileV115:null;
        Promise.resolve(fn?.()).then(()=>{finalizeStudentProfileV175();fillStudentAvatarV175()}).catch(()=>{});
      }catch(e){}
    }
  }

  const baseRenderV175=window.render;
  window.render=function(){
    const out=baseRenderV175.apply(this,arguments);
    ensureCoachHeroFrameV175();
    ensureStudentProfilePlaceholderV175();
    if(typeof fjzPostRenderV125==='function')fjzPostRenderV125('v175-final-ui',postRenderV175);
    else requestAnimationFrame(postRenderV175);
    return out;
  };

  /* Existing old 360/help symbols remain no-op from V17.4. Re-assert defensively. */
  const noopV175=async function(){
    ['v80Student360','v80Student360Loading','v71CoachHelp','v71CoachHelpLoading','v71CoachHelpTracking','v71CoachHelpTrackingCard','v63UnifiedSummary']
      .forEach(id=>el(id)?.remove());
    return null;
  };
  try{injectStudent360V80=noopV175}catch(e){}
  try{window.injectStudent360V80=noopV175}catch(e){}
  try{injectCoachHelpV71=noopV175}catch(e){}
  try{window.injectCoachHelpV71=noopV175}catch(e){}
  try{injectUnifiedStudentSummaryV63=noopV175}catch(e){}
  try{window.injectUnifiedStudentSummaryV63=noopV175}catch(e){}

  window.__fjzV175={
    version:VERSION,
    single360:true,
    richer360:true,
    stableCoachIdentity:true,
    stableStudentIdentity:true,
    agendaAttention:true,
    agendaUsesRemindersAndCheckinSchedule:true,
    unifiedCoachCenter:true,
    duplicateAlertSummaryHidden:true,
    assistantExecutiveSummary:true,
    assistantMaxPriorities:3,
    cacheFirst:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

required=[
  "__fjzV175","single360:true","richer360:true","stableCoachIdentity:true","stableStudentIdentity:true",
  "agendaAttention:true","agendaUsesRemindersAndCheckinSchedule:true","unifiedCoachCenter:true",
  "duplicateAlertSummaryHidden:true","assistantExecutiveSummary:true","assistantMaxPriorities:3","cacheFirst:true"
]
for marker in required:
    if marker not in html:
        raise RuntimeError("V17.5 missing marker: "+marker)

# Static audit: no duplicate new IDs and no accidental new always-on observer.
ids=re.findall(r'id="(v175[^"]+)"',html)
dupes=sorted({x for x in ids if ids.count(x)>1})
if dupes:
    raise RuntimeError("V17.5 duplicate static ids: "+", ".join(dupes))

print("TEAM FJZ V17.5 profile/agenda/coach-center enabled")
print("V17.5 audit:",{
    "bytes":len(html),
    "scripts":len(re.findall(r"<script\\b",html)),
    "styles":len(re.findall(r"<style\\b",html)),
    "render_assignments":len(re.findall(r"(?:window\\.)?render\\s*=\\s*function",html)),
    "mutation_observers":len(re.findall(r"new\\s+MutationObserver",html)),
    "timeouts":len(re.findall(r"setTimeout\\s*\\(",html)),
    "new_id_duplicates":len(dupes)
})

p.write_text(html,encoding="utf-8")
