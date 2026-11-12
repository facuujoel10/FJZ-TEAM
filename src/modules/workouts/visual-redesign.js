(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.TeamFJZVisualRedesign=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const VERSION='22.2B-V2';

function hasDOM(){return typeof document!=='undefined'&&!!document.querySelector}
function t(v){return String(v??'').trim()}
function num(v){const n=Number(String(v??'').replace(',','.'));return Number.isFinite(n)?n:null}
function make(tag,cls,html){const n=document.createElement(tag);if(cls)n.className=cls;if(html!=null)n.innerHTML=html;return n}
function complete(grid){const xs=[...grid.querySelectorAll('input')];return xs.length>=3&&xs.slice(0,3).every(x=>t(x.value)!==''&&num(x.value)!==null)}
function progress(card){const sets=[...card.querySelectorAll('.set-grid')];return{done:sets.filter(complete).length,total:sets.length}}
function allProgress(view){const cards=[...view.querySelectorAll('.session-card.v22-premium-exercise')];const data=cards.map(progress);return{exercises:cards.length,done:data.reduce((a,x)=>a+x.done,0),total:data.reduce((a,x)=>a+x.total,0)}}
function percent(p){return p.total?Math.round((p.done/p.total)*100):0}
function role(){try{return String(globalThis.currentProfile?.role||'')}catch(_e){return''}}
function findButton(root,re){return [...(root?.querySelectorAll?.('button')||[])].find(x=>re.test(t(x.textContent))||re.test(t(x.getAttribute('aria-label'))))}
function clickPrimaryNav(label){
  const buttons=[...document.querySelectorAll('#bottomNav button,.bottom-nav button')];
  const hit=buttons.find(x=>t(x.textContent).toLowerCase()===label.toLowerCase());
  if(hit){hit.click();return true}
  try{
    if(label.toLowerCase()==='inicio'){globalThis.currentDay=-1;globalThis.studentTab='home'}
    if(label.toLowerCase()==='historial'){globalThis.currentDay=-1;globalThis.studentTab='history'}
    globalThis.render?.();return true
  }catch(_e){return false}
}

function trimDuplicateNav(view){
  if(!view||role()==='coach'||view.querySelector('button.tab[onclick*="coachStudentTab"]'))return;
  const duplicate=new Set(['inicio','nutrición','nutricion','progreso','entrenar']);
  const groups=new Set();
  [...view.querySelectorAll('.tabs .tab,button.tab')].forEach(b=>{
    if(!duplicate.has(t(b.textContent).toLowerCase()))return;
    b.classList.add('v22v-duplicate-nav','v22v2-duplicate-nav');
    b.hidden=true;b.setAttribute('aria-hidden','true');b.tabIndex=-1;
    const group=b.closest('.tabs');if(group)groups.add(group);
  });
  groups.forEach(group=>{
    group.classList.add('v22v-context-nav','v22v2-context-nav');
    const visible=[...group.querySelectorAll('.tab')].filter(x=>!x.hidden);
    if(!visible.length){group.hidden=true;group.setAttribute('aria-hidden','true')}
  });
}

function hideWorkoutGlobalNav(view){
  if(!view||role()==='coach')return;
  const globalLabels=new Set(['inicio','agenda','check-in','checkin','nutrición','nutricion','progreso','entrenar','historial']);
  [...view.querySelectorAll('.tabs')].forEach(group=>{
    const buttons=[...group.querySelectorAll(':scope > .tab, :scope > button.tab')];
    if(!buttons.length)return;
    const labels=buttons.map(b=>t(b.textContent).toLowerCase()).filter(Boolean);
    const globalCount=labels.filter(x=>globalLabels.has(x)).length;
    if(globalCount<2)return;
    group.classList.add('v22v2-workout-global-nav');
    group.hidden=true;group.setAttribute('aria-hidden','true');
    buttons.forEach(b=>{b.hidden=true;b.setAttribute('aria-hidden','true');b.tabIndex=-1});
  });
}

function sessionHeader(view){
  const hero=view.querySelector('.v22-workout-hero,.hero');if(!hero)return null;
  hero.classList.add('v22v-command','v22v2-workout-header','fjz-appbar');
  hero.querySelector('.v22-workout-eyebrow')?.remove();
  hero.querySelector('.v22v-session-overview')?.remove();
  hero.querySelector('.v22v-progress-cluster')?.remove();

  let main=hero.querySelector('.v22v2-header-main');
  if(!main){
    main=make('div','v22v2-header-main');
    const back=make('button','v22v2-back fjz-icon-button','‹');
    back.type='button';back.setAttribute('aria-label','Salir del entrenamiento');
    back.onclick=()=>clickPrimaryNav('Inicio');
    const title=make('div','v22v2-header-copy');
    const h=hero.querySelector('h2');
    const subtitle=h?.parentElement?.querySelector('p,.muted');
    if(h){h.classList.add('v22v-workout-title','v22v2-workout-title');title.appendChild(h)}
    if(subtitle){subtitle.classList.add('v22v2-workout-subtitle');title.appendChild(subtitle)}
    const menu=make('details','v22v2-session-menu');
    const summary=make('summary','fjz-icon-button v22v2-menu-trigger','•••');
    summary.setAttribute('aria-label','Opciones del entrenamiento');
    const panel=make('div','v22v2-session-menu-panel');
    panel.innerHTML='<strong>Sesión en curso</strong><span>El guardado y las opciones de borrador se mantienen disponibles acá.</span>';
    menu.append(summary,panel);
    main.append(back,title,menu);
    hero.prepend(main);
  }

  const menuPanel=hero.querySelector('.v22v2-session-menu-panel');
  const direct=[...view.children];
  const discardButtons=[...view.querySelectorAll('button')].filter(x=>/Descartar borrador/i.test(t(x.textContent)||t(x.getAttribute('aria-label'))));
  const autosaveCandidates=[
    document.getElementById('v145AutosaveBox'),
    ...discardButtons.map(btn=>btn.closest?.('[id*="Autosave"],[class*="autosave"],.card,section')||btn.parentElement),
    direct.find(n=>n!==hero&&!n.querySelector?.('.session-card')&&/Autoguardado activo|Descartar borrador/i.test(t(n.textContent)))
  ].filter(Boolean).filter((node,i,arr)=>arr.indexOf(node)===i&&node!==hero&&!node.closest?.('.session-card'));
  const autosave=autosaveCandidates[0]||null;
  if(autosave&&menuPanel&&autosave.parentElement!==menuPanel){
    autosave.classList.add('v22v2-autosave-menu');
    menuPanel.appendChild(autosave);
  }
  autosaveCandidates.slice(1).forEach(node=>{
    if(node===menuPanel||node.contains?.(menuPanel))return;
    node.classList.add('v22v2-autosave-duplicate');
    node.setAttribute('aria-hidden','true');
  });
  discardButtons.forEach(btn=>{
    if(menuPanel&&!btn.closest('.v22v2-session-menu-panel')){
      btn.classList.add('v22v2-discard-menu-action');
      menuPanel.appendChild(btn);
    }
  });
  let menuDiscards=menuPanel?[...menuPanel.querySelectorAll('button')].filter(x=>/Descartar borrador/i.test(t(x.textContent)||t(x.getAttribute('aria-label')))):[];
  menuDiscards.slice(1).forEach(btn=>{btn.classList.add('v22v2-autosave-duplicate-action');btn.setAttribute('aria-hidden','true')});
  if(menuPanel&&!menuDiscards.length&&typeof globalThis.confirmDiscardWorkoutDraftV145==='function'){
    const action=make('button','btn v22v2-discard-menu-action','Descartar borrador');
    action.type='button';
    action.onclick=function(){
      try{
        const d=globalThis.student?.()?.days?.[globalThis.currentDay];
        if(d?.id)globalThis.confirmDiscardWorkoutDraftV145(d.id);
      }catch(_e){}
    };
    menuPanel.appendChild(action);
    menuDiscards=[action];
  }
  direct.filter(n=>n!==hero&&!n.querySelector?.('.session-card')&&/series con registro/i.test(t(n.textContent))).forEach(n=>n.classList.add('v22v2-legacy-progress'))

  let bar=hero.querySelector('.v22v2-progress');
  if(!bar){bar=make('div','v22v2-progress');bar.innerHTML='<div class="v22v2-progress-track"><i></i></div><div class="v22v2-progress-meta"><strong></strong><span></span></div>';hero.appendChild(bar)}
  const p=allProgress(view),pct=percent(p);
  bar.querySelector('i').style.width=pct+'%';
  bar.querySelector('strong').textContent=p.done+' / '+p.total+' series';
  bar.querySelector('span').textContent=pct+'%';

  const save=document.getElementById('v22WorkoutSaveState');
  if(save){
    save.classList.add('v22v-save-state','v22v2-save-state');
    let status=hero.querySelector('.v22v2-save-slot');
    if(!status){status=make('div','v22v2-save-slot');main.appendChild(status)}
    if(save.parentElement!==status)status.appendChild(save);
  }
  return hero;
}

function parsePrescription(head){
  if(!head)return '';
  const strings=[...head.querySelectorAll('.muted,.tiny,small,span')].map(x=>t(x.textContent)).filter(Boolean);
  return strings.find(x=>/serie|rep|rir|descanso/i.test(x))||'';
}
function ensureExerciseHeader(card,index){
  const head=card.querySelector('.day-head');if(!head)return null;
  head.classList.add('v22v-exercise-head','v22v2-exercise-head');
  let top=head.querySelector('.v22v2-exercise-top');
  if(!top){
    top=make('div','v22v2-exercise-top');
    const number=make('span','v22v-exercise-number v22v2-exercise-number',String(index+1).padStart(2,'0'));
    const copy=make('div','v22v-exercise-title v22v2-exercise-copy');
    const strong=head.querySelector('strong');
    if(strong){strong.classList.add('v22v2-exercise-name');copy.appendChild(strong)}
    const prescription=parsePrescription(head);
    const meta=make('div','v22v2-prescription');
    if(prescription)meta.textContent=prescription;
    copy.appendChild(meta);
    const action=findButton(card,/comentario/i);
    if(action){
      action.classList.add('v22-comment-action','v22v-icon-action','v22v2-comment-action');
      action.textContent='Comentar';
      action.setAttribute('aria-label','Comentario de '+t(strong?.textContent||'ejercicio'));
    }
    top.append(number,copy);
    if(action){const actions=make('div','v22v-exercise-actions v22v2-exercise-actions');actions.appendChild(action);top.appendChild(actions)}
    head.prepend(top);
  }
  [...head.children].forEach(x=>{if(x!==top)x.classList.add('v22v2-head-legacy')});
  const p=progress(card);
  let status=top.querySelector('.v22v-exercise-progress');
  if(!status){status=make('span','v22v-exercise-progress v22v2-exercise-progress');top.querySelector('.v22v2-exercise-copy')?.appendChild(status)}
  status.textContent=p.done+'/'+p.total+' series listas';
  status.dataset.complete=p.total>0&&p.done===p.total?'true':'false';
  return head;
}

function labelSeriesRows(block){
  [...block.querySelectorAll('.v22-premium-set')].forEach((row,i)=>{
    row.dataset.setState=complete(row)?'complete':'pending';
    const n=row.querySelector('.set-n');if(n){n.setAttribute('aria-label','Serie '+(i+1));n.textContent=String(i+1)}
  });
}
function buildSeries(card){
  const sets=[...card.querySelectorAll(':scope > .set-grid, :scope > .v22-premium-set')];if(!sets.length)return null;
  let block=card.querySelector(':scope > .v22v-series-block');
  if(!block){
    block=make('section','v22v-series-block v22v2-series-block');
    const h=make('div','v22v-series-header v22v2-series-header','<span>Serie</span><span>Carga</span><span>Reps</span><span>RIR</span>');
    block.appendChild(h);sets[0].before(block);
  }else block.classList.add('v22v2-series-block');
  sets.forEach(x=>{x.classList.add('v22v2-set-row');if(x.parentElement!==block)block.appendChild(x)});
  labelSeriesRows(block);
  return block;
}
function secondaryContext(card,seriesBlock){
  const previous=[...card.querySelectorAll(':scope > .v22-last-session-reference, :scope > .coach-note')];
  const recommendation=[...card.querySelectorAll(':scope > .v22-recommendation, :scope > .recommend')];
  let strip=card.querySelector(':scope > .v22v2-reference-strip');
  if(!strip){strip=make('div','v22v2-reference-strip');if(seriesBlock)seriesBlock.before(strip);else card.appendChild(strip)}
  const prevNodes=[...card.querySelectorAll('.v22-previous-load,.v205-prev-load')];
  const refText=t(previous[0]?.textContent);
  const m=refText.match(/(\d+(?:[.,]\d+)?)\s*kg\s*[×x]\s*(\d+).*?RIR\s*([0-9.,]+)/i);
  prevNodes.forEach((x,i)=>{
    x.classList.add('v22v2-previous-load');
    if(i===0){
      if(m)x.textContent='Anterior '+m[1].replace(',','.')+' kg × '+m[2]+' · RIR '+m[3].replace(',','.');
      if(x.parentElement!==strip)strip.appendChild(x);
    }else x.classList.add('v22v2-previous-load-duplicate');
  });

  let details=card.querySelector(':scope > .v22v2-guidance');
  if((previous.length||recommendation.length)&&!details){
    details=make('details','v22v2-guidance fjz-disclosure');
    const summary=make('summary','v22v2-guidance-summary','<span><b>Referencia de rendimiento</b><small>Recomendación y última sesión</small></span><i>Ver</i>');
    const body=make('div','v22v2-guidance-body');
    details.append(summary,body);
    if(seriesBlock)seriesBlock.after(details);else card.appendChild(details);
  }
  const body=details?.querySelector('.v22v2-guidance-body');
  [...previous,...recommendation].forEach(x=>{if(body&&x.parentElement!==body){x.classList.add('v22v2-guidance-item');body.appendChild(x)}});
}
function technique(card){
  const existing=card.querySelector(':scope > .v22v-disclosure');
  if(existing){existing.classList.add('v22v2-technique-disclosure','fjz-disclosure');existing.open=false;existing.removeAttribute('open');return}
  const layout=card.querySelector(':scope > .v72-tech-layout');
  let node=layout;
  if(!node)node=[...card.children].find(n=>{
    if(n.classList?.contains('v22v2-guidance')||n.classList?.contains('v22v2-series-block'))return false;
    const tx=t(n.textContent);
    return /técnica|tecnica/i.test(tx)&&/buscá|busca|evitá|evita|posición|posicion|ejecución|ejecucion/i.test(tx);
  });
  if(!node)node=[...card.querySelectorAll(':scope > p.muted')].find(p=>/técnica|tecnica|buscá|evitá|posición|posicion/i.test(t(p.textContent)));
  if(!node)return;
  const d=make('details','v22v-disclosure v22v2-technique-disclosure fjz-disclosure');
  const s=make('summary','v22v-disclosure-summary','<span>Técnica y ejecución</span><span class="v22v-disclosure-action">Abrir</span>');
  node.before(d);d.append(s,node);
  node.classList.add('v22v-technique');
  d.open=false;d.removeAttribute('open');
}
function compactFeedbackStatus(card){
  const statuses=[...card.querySelectorAll('.v73-student-feedback-status')];
  const rawBadges=[...card.querySelectorAll('.v73-comment-badge,.v73-alert-badge')];
  const entries=rawBadges.map(badge=>({
    text:t(badge.textContent).replace(/\s*·\s*\d+\s*$/,'').trim(),
    alert:badge.classList.contains('v73-alert-badge')||/molestia/i.test(t(badge.textContent))
  })).filter(x=>x.text);
  if(!entries.length){statuses.slice(1).forEach(x=>x.remove());return}
  let host=statuses[0];
  if(!host){
    host=make('div','v73-student-feedback-status v22v2-feedback-status');
    const header=card.querySelector('.v22v2-exercise-head,.v22v-exercise-head');
    if(header)header.after(host);else card.prepend(host);
  }
  host.classList.add('v22v2-feedback-status');
  statuses.filter(x=>x!==host).forEach(x=>x.remove());
  const unique=[];
  const seen=new Set();
  entries.forEach(entry=>{
    const key=entry.text.toLowerCase();
    if(seen.has(key))return;
    seen.add(key);unique.push(entry);
  });
  host.innerHTML='';
  unique.forEach(entry=>{
    host.appendChild(make('span',(entry.alert?'v73-alert-badge':'v73-comment-badge')+' v22v-feedback-summary',entry.text));
  });
}
function exercise(card,index){
  card.classList.add('v22v-exercise','v22v2-exercise','fjz-performance-section');
  card.dataset.exerciseIndex=String(index);
  ensureExerciseHeader(card,index);
  const seriesBlock=buildSeries(card);
  secondaryContext(card,seriesBlock);
  technique(card);
  compactFeedbackStatus(card);
  if(index===0)card.classList.add('is-active');
}

function sessionNavigator(feed,aside){
  let nav=aside.querySelector('.v22v2-exercise-map');
  if(!nav){nav=make('nav','v22v2-exercise-map');nav.setAttribute('aria-label','Ejercicios de la sesión');aside.prepend(nav)}
  nav.innerHTML='<div class="v22v2-aside-label">Ejercicios</div>';
  [...feed.querySelectorAll('.v22v2-exercise')].forEach((card,i)=>{
    const name=t(card.querySelector('.v22v2-exercise-name')?.textContent)||('Ejercicio '+(i+1));
    const p=progress(card),id='v22v2-exercise-'+(i+1);card.id=id;
    const b=make('a','v22v2-exercise-map-item');
    b.href='#'+id;b.innerHTML='<span>'+String(i+1).padStart(2,'0')+'</span><b>'+name+'</b><small>'+p.done+'/'+p.total+'</small>';
    nav.appendChild(b);
  });
}
function finishZone(view,feed,aside){
  const btn=view.querySelector('.v22-finish-workout');if(!btn)return null;
  btn.classList.add('v22v-primary-finish','v22v2-primary-finish');
  let zone=view.querySelector('.v22v2-finish-zone');
  if(!zone){
    zone=make('section','v22v-finish-dock v22v2-finish-zone fjz-surface');
    zone.innerHTML='<div><span>Fin de la sesión</span><strong>¿Terminaste tu entrenamiento?</strong><small>Se confirmará el guardado antes de cerrar.</small></div>';
    zone.appendChild(btn);
  }
  const target=window.matchMedia&&window.matchMedia('(min-width:1000px)').matches?aside:feed;
  if(target&&zone.parentElement!==target)target.appendChild(zone);
  const old=view.querySelector('.v22v-finish-dock');if(old&&old!==zone){while(old.firstChild)old.firstChild===btn?zone.appendChild(btn):old.firstChild.remove();old.remove()}
  return zone;
}
function workoutComposition(view){
  let layout=view.querySelector(':scope > .v22v2-workout-layout');
  if(!layout){layout=make('div','v22v-workout-layout v22v2-workout-layout');const first=view.querySelector(':scope > .v22v2-exercise');if(first)first.before(layout);else view.appendChild(layout)}
  let feed=layout.querySelector(':scope > .v22v2-workout-feed');
  if(!feed){feed=make('main','v22v-workout-feed v22v2-workout-feed');layout.appendChild(feed)}
  let aside=layout.querySelector(':scope > .v22v2-session-aside');
  if(!aside){aside=make('aside','v22v-session-rail v22v2-session-aside');aside.setAttribute('aria-label','Mapa de la sesión');layout.appendChild(aside)}
  [...view.querySelectorAll(':scope > .v22v2-exercise')].forEach(x=>feed.appendChild(x));
  sessionNavigator(feed,aside);
  finishZone(view,feed,aside);
  return {layout,feed,aside};
}
function updateWorkout(view){
  const p=allProgress(view),pct=percent(p);
  const bar=view.querySelector('.v22v2-progress');
  if(bar){bar.querySelector('i').style.width=pct+'%';bar.querySelector('strong').textContent=p.done+' / '+p.total+' series';bar.querySelector('span').textContent=pct+'%'}
  [...view.querySelectorAll('.v22v2-exercise')].forEach(card=>{
    const cp=progress(card),s=card.querySelector('.v22v-exercise-progress');
    if(s){s.textContent=cp.done+'/'+cp.total+' series listas';s.dataset.complete=cp.total>0&&cp.done===cp.total?'true':'false'}
    const block=card.querySelector('.v22v2-series-block');if(block)labelSeriesRows(block);
  });
}
function bindWorkoutProgress(view){
  if(view.dataset.v22v2ProgressBound)return;view.dataset.v22v2ProgressBound='1';
  const prior=view.oninput;
  view.oninput=function(e){if(typeof prior==='function')prior.call(this,e);if(e.target?.matches?.('.v22-set-field input,.set-grid input'))updateWorkout(view)};
}
function enhanceWorkout(root){
  if(!hasDOM())return false;const view=root||document.getElementById('view');
  if(!view||!view.classList.contains('v22-premium-workout'))return false;
  view.classList.add('v22v-performance-shell','v22v-workout-active','v22v2-workout-active');
  trimDuplicateNav(view);hideWorkoutGlobalNav(view);sessionHeader(view);
  [...view.querySelectorAll('.session-card.v22-premium-exercise')].forEach(exercise);
  const composition=workoutComposition(view);bindWorkoutProgress(view);updateWorkout(view);
  view.dataset.v22ProductExperience='performance-training-v2';
  if(typeof queueMicrotask==='function')queueMicrotask(()=>{
    if(!view.isConnected)return;
    [...view.querySelectorAll('.session-card.v22-premium-exercise,.v22v2-exercise')].forEach(compactFeedbackStatus);
  });
  return !!composition;
}

function enhanceCommentModal(modal){
  if(!modal)return false;
  modal.classList.add('v22v-comment-sheet','v22v2-comment-sheet');
  modal.querySelector('.modal-content')?.classList.add('v22v-comment-panel','v22v2-comment-panel');
  modal.querySelector('.modal-head')?.classList.add('v22v-comment-head','v22v2-comment-head');
  const types=modal.querySelector('.v73-feedback-type');types?.classList.add('v22v-comment-types','v22v2-comment-types');
  [...(types?.querySelectorAll('.v73-type-option')||[])].forEach(x=>x.classList.add('v22v2-comment-type'));
  const textarea=modal.querySelector('textarea');
  if(textarea){textarea.classList.add('v22v-comment-text','v22v2-comment-text');textarea.setAttribute('aria-label','Comentario para el coach')}
  const send=findButton(modal,/Enviar al coach/i);send?.classList.add('v22v-comment-submit','v22v2-comment-submit');
  const close=modal.querySelector('.modal-head button[onclick*="closeModal"]');if(close)close.classList.add('fjz-icon-button','v22v2-comment-close');
  let intro=modal.querySelector('.v22v2-comment-intro');
  if(!intro&&textarea){intro=make('div','v22v2-comment-intro','<span>Feedback contextual</span><strong>Dejalo ligado a este ejercicio y esta sesión.</strong>');types?.before(intro)}
  return true;
}

function historyMetrics(row){
  const copy=row.querySelector('.v244-history-copy');if(!copy)return;
  copy.classList.add('v22v-history-copy','v22v2-history-copy');
  copy.querySelector('.v244-history-badges')?.classList.add('v22v-history-signals','v22v2-history-signals');
  copy.querySelector('.muted')?.classList.add('v22v-history-subline','v22v2-history-subline');
}
function historyHeader(card){
  const title=card.querySelector('.section-title');if(!title)return;
  title.classList.add('v22v2-history-header','fjz-appbar');
  const h=title.querySelector('h3');if(h)h.textContent='Historial';
  const muted=title.querySelector('.muted');if(muted)muted.textContent='Sesiones, progreso verificable y comentarios en un solo registro.';
  let count=title.querySelector('.v22v2-history-count')||title.querySelector(':scope > .badge');
  if(!count){count=make('span','v22v2-history-count');title.appendChild(count)}
  count.classList.remove('badge','blue','amber','green','red');count.classList.add('v22v2-history-count');
  [...title.querySelectorAll(':scope > .badge')].filter(x=>x!==count).forEach(x=>x.remove());
  count.textContent=card.querySelectorAll('.v22-history-session').length+' sesiones';
}
function sessionDateBadge(row,index){
  if(row.querySelector('.v22v2-history-date'))return;
  const copy=row.querySelector('.v244-history-copy');
  const raw=t(copy?.querySelector('.muted')?.textContent);
  const badge=make('div','v22v-history-index v22v2-history-date');
  badge.innerHTML='<span>'+String(index+1).padStart(2,'0')+'</span><small>SES</small>';
  row.prepend(badge);
}
function restoreCoachNav(view){
  if(!view)return;
  [...view.querySelectorAll('button.tab[onclick*="coachStudentTab"]')].forEach(b=>{
    b.hidden=false;b.removeAttribute('hidden');b.removeAttribute('aria-hidden');b.removeAttribute('tabindex');b.classList.remove('v22v-duplicate-nav','v22v2-duplicate-nav');
    const group=b.closest('.tabs');if(group){group.hidden=false;group.removeAttribute('hidden');group.removeAttribute('aria-hidden');group.classList.remove('v22v-context-nav','v22v2-context-nav')}
  });
}
function enhanceHistory(host){
  if(!host)return false;const view=document.getElementById('view')||host,isCoach=role()==='coach'||!!view.querySelector('button.tab[onclick*="coachStudentTab"]');
  if(isCoach)restoreCoachNav(view);
  else{view.classList.add('v22v-history-active','v22v2-history-active');trimDuplicateNav(view)}
  const card=host.querySelector('.v22-premium-history');if(!card)return false;
  if(!isCoach){
    [...view.children].forEach(n=>{
      if(n===card||n.contains?.(card)||card.contains?.(n))return;
      const tx=t(n.textContent);
      if(/Historial/i.test(tx)&&(/Avisos/i.test(tx)||/ALUMNO/i.test(tx)||/←\s*Inicio/i.test(tx)))n.classList.add('v22v2-history-legacy-shell');
    });
  }
  card.classList.add('v22v-history','v22v2-history','fjz-surface');
  card.querySelector('.v244-history-list')?.classList.add('v22v-history-list','v22v2-history-list');
  historyHeader(card);
  [...card.querySelectorAll('.v22-history-session')].forEach((row,index)=>{
    row.classList.add('v22v-history-session','v22v2-history-session');
    row.querySelector('.v22v-history-index')?.remove();
    sessionDateBadge(row,index);historyMetrics(row);
    const b=row.querySelector(':scope > button');if(b){b.classList.add('v22v-history-open','v22v2-history-open');b.setAttribute('aria-label','Ver sesión')}
  });
  card.querySelector('.v22v-history-overview')?.remove();
  if(!isCoach)view.dataset.v22ProductExperience='performance-history-v2';else card.dataset.v22ProductExperience='performance-history-v2';
  return true;
}

function coachContext(modal){
  if(role()!=='coach')return;
  modal.classList.add('v22v2-coach-session');
  const layout=modal.querySelector('.v22v2-session-layout');if(!layout||layout.querySelector('.v22v2-coach-context'))return;
  const aside=make('aside','v22v2-coach-context');
  const title=t(modal.querySelector('.modal-head h3')?.textContent)||'Sesión';
  const comments=modal.querySelectorAll('.v287-exercise-comment').length;
  aside.innerHTML='<span class="v22v2-aside-label">Revisión Coach</span><strong>'+title+'</strong><p>'+comments+' comentario'+(comments===1?'':'s')+' vinculados a esta sesión.</p><small>Las acciones de revisión y estados OK conservan su autoridad existente.</small>';
  layout.prepend(aside);
}
function sessionLayout(modal){
  const content=modal.querySelector('.modal-content');if(!content)return;
  const k=modal.querySelector('.v244-summary-grid'),flow=modal.querySelector('.v244-timeline');if(!k||!flow)return;
  let layout=modal.querySelector('.v22v2-session-layout');
  if(!layout){layout=make('div','v22v-session-layout v22v2-session-layout');k.before(layout);layout.append(k,flow)}
  else{layout.classList.add('v22v-session-layout');if(k.parentElement!==layout)layout.appendChild(k);if(flow.parentElement!==layout)layout.appendChild(flow)}
}
function enhanceSessionDetail(modal){
  if(!modal)return false;
  modal.classList.add('v22v-session-modal','v22v2-session-modal');
  modal.querySelector('.modal-content')?.classList.add('v22v-session-panel','v22v2-session-panel');
  modal.querySelector('.modal-head')?.classList.add('v22v-session-head','v22v2-session-head');
  modal.querySelector('.v244-summary-grid')?.classList.add('v22v-session-kpis','v22v2-session-kpis');
  modal.querySelector('.v244-timeline')?.classList.add('v22v-session-flow','v22v2-session-flow');
  sessionLayout(modal);
  [...modal.querySelectorAll('.v244-exercise')].forEach((x,i)=>{
    x.classList.add('v22v-history-exercise','v22v2-history-exercise');
    let n=x.querySelector('.v22v-history-exercise-index');if(!n){n=make('span','v22v-history-exercise-index v22v2-history-exercise-index',String(i+1).padStart(2,'0'));x.prepend(n)}else n.classList.add('v22v2-history-exercise-index');
    [...x.querySelectorAll('.v22-history-compare-box')].forEach((box,bi)=>box.classList.add(bi===0?'v22v-compare-previous':'v22v-compare-current','v22v2-compare-box'));
  });
  [...modal.querySelectorAll('.v287-exercise-comment')].forEach(x=>x.classList.add('v22v-context-comment','v22v2-context-comment'));
  coachContext(modal);
  return true;
}

return Object.freeze({VERSION,enhanceWorkout,enhanceCommentModal,enhanceHistory,enhanceSessionDetail});
});
