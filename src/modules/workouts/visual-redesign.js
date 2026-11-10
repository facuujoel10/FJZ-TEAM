(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.TeamFJZVisualRedesign=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const VERSION='22.2B-V.5';
function hasDOM(){return typeof document!=='undefined'&&!!document.querySelector}
function t(v){return String(v??'').trim()}
function num(v){const n=Number(String(v??'').replace(',','.'));return Number.isFinite(n)?n:null}
function complete(grid){const xs=[...grid.querySelectorAll('input')];return xs.length>=3&&xs.slice(0,3).every(x=>t(x.value)!==''&&num(x.value)!==null)}
function progress(card){const sets=[...card.querySelectorAll('.set-grid')];return{done:sets.filter(complete).length,total:sets.length}}
function allProgress(view){const cards=[...view.querySelectorAll('.session-card.v22-premium-exercise')];const data=cards.map(progress);return{exercises:cards.length,done:data.reduce((a,x)=>a+x.done,0),total:data.reduce((a,x)=>a+x.total,0)}}
function make(tag,cls,html){const n=document.createElement(tag);n.className=cls;if(html!=null)n.innerHTML=html;return n}
function ensureOverview(view,hero){
  let o=hero.querySelector('.v22v-session-overview');if(!o){o=make('div','v22v-session-overview');hero.appendChild(o)}
  const p=allProgress(view),pct=p.total?Math.round(p.done/p.total*100):0;
  o.innerHTML='<div class="v22v-overview-primary"><span class="v22v-label">Progreso de sesión</span><strong>'+p.done+' / '+p.total+'</strong><span>'+pct+'% completado</span></div>'+
    '<div class="v22v-overview-stat"><span>Ejercicios</span><strong>'+p.exercises+'</strong></div>'+
    '<div class="v22v-overview-stat"><span>Series listas</span><strong>'+p.done+'</strong></div>';
  o.style.setProperty('--v22v-progress',pct+'%');
}
function command(view){
  const hero=view.querySelector('.v22-workout-hero,.hero');if(!hero)return;
  hero.classList.add('v22v-command');hero.querySelector('h2')?.classList.add('v22v-workout-title');
  const p=hero.querySelector('.session-progress')||view.querySelector('.session-progress'),l=document.getElementById('v22WorkoutProgressLabel');
  if(p){let c=hero.querySelector('.v22v-progress-cluster');if(!c){c=make('div','v22v-progress-cluster');hero.appendChild(c)}if(p.parentElement!==c)c.appendChild(p);if(l&&l.parentElement!==c)c.appendChild(l)}
  ensureOverview(view,hero);
}
function trimDuplicateNav(view){
  const duplicate=new Set(['inicio','nutrición','nutricion','progreso','entrenar']);
  [...view.querySelectorAll('.tabs .tab')].forEach(b=>{
    if(!duplicate.has(t(b.textContent).toLowerCase()))return;
    b.classList.add('v22v-duplicate-nav');
    b.closest('.tabs')?.classList.add('v22v-context-nav');
  });
}
function actions(card,head){let box=head.querySelector('.v22v-exercise-actions');if(!box){box=make('div','v22v-exercise-actions');head.appendChild(box)}
 const btn=[...card.querySelectorAll('button')].find(x=>/comentario/i.test(t(x.textContent)));if(btn&&btn.parentElement!==box){btn.classList.add('v22v-icon-action');btn.textContent='Comentario';box.appendChild(btn)}}
function meta(card,head,index){let m=head.querySelector('.v22v-exercise-meta');if(!m){m=make('div','v22v-exercise-meta');const strong=head.querySelector('strong');let host=strong?.parentElement;if(strong&&host===head){host=make('div','');head.insertBefore(host,strong);host.appendChild(strong)}if(host&&host!==head){host.classList.add('v22v-exercise-title');m.appendChild(host)}head.prepend(m)}
 if(!m.querySelector('.v22v-exercise-number')){const n=make('span','v22v-exercise-number',String(index+1).padStart(2,'0'));m.prepend(n)}
 const p=progress(card);let s=m.querySelector('.v22v-exercise-progress');if(!s){s=make('span','v22v-exercise-progress');m.appendChild(s)}s.textContent=p.done+'/'+p.total+' series';s.dataset.complete=p.total>0&&p.done===p.total?'true':'false'}
function labelSeriesRows(block){[...block.querySelectorAll('.v22-premium-set')].forEach((row,i)=>{row.dataset.setState=complete(row)?'complete':'pending';const n=row.querySelector('.set-n');if(n){n.setAttribute('aria-label','Serie '+(i+1));}})}
function series(card){const sets=[...card.querySelectorAll(':scope > .set-grid, :scope > .v22-premium-set')];if(!sets.length)return;let block=card.querySelector(':scope > .v22v-series-block');
 if(!block){block=make('section','v22v-series-block');const h=make('div','v22v-series-header','<span>Serie</span><span>Carga</span><span>Reps</span><span>RIR</span>');block.appendChild(h);sets[0].before(block)}
 sets.forEach(x=>{if(x.parentElement!==block)block.appendChild(x)});labelSeriesRows(block)}
function context(card){const xs=[...card.querySelectorAll(':scope > .v22-last-session-reference, :scope > .v22-recommendation, :scope > .coach-note, :scope > .recommend')];if(!xs.length)return;let rail=card.querySelector(':scope > .v22v-context-rail');
 if(!rail){rail=make('div','v22v-context-rail');const s=card.querySelector(':scope > .v22v-series-block');if(s)s.before(rail);else card.appendChild(rail)}xs.forEach(x=>{if(x.parentElement!==rail)rail.appendChild(x)})}
function technique(card){const layout=card.querySelector(':scope > .v72-tech-layout');if(layout){layout.classList.add('v22v-technique-layout');const tech=layout.querySelector('.v72-tech-card');if(tech)tech.classList.add('v22v-technique-card');[...layout.querySelectorAll('.v72-tech-step')].forEach((x,i)=>{x.classList.add('v22v-technique-step');x.dataset.step=String(i+1)});return}const ps=[...card.querySelectorAll(':scope > p.muted')];ps.forEach(p=>{if(/técnica|tecnica|buscá|evitá|posición|posicion/i.test(t(p.textContent)))p.classList.add('v22v-technique')})}
function exercise(card,index){card.classList.add('v22v-exercise');const h=card.querySelector('.day-head');if(h){h.classList.add('v22v-exercise-head');meta(card,h,index);actions(card,h)}technique(card);context(card);series(card)}
function finishDock(view){const btn=view.querySelector('.v22-finish-workout');if(!btn)return;btn.classList.add('v22v-primary-finish');let dock=view.querySelector('.v22v-finish-dock');if(!dock){dock=make('div','v22v-finish-dock');dock.innerHTML='<div class="v22v-finish-copy"><span>Cuando termines</span><strong>Confirmar entrenamiento</strong></div>';btn.before(dock);dock.appendChild(btn)}}
function enhanceWorkout(root){if(!hasDOM())return false;const view=root||document.getElementById('view');if(!view||!view.classList.contains('v22-premium-workout'))return false;view.classList.add('v22v-performance-shell');trimDuplicateNav(view);command(view);[...view.querySelectorAll('.session-card.v22-premium-exercise')].forEach(exercise);document.getElementById('v22WorkoutSaveState')?.classList.add('v22v-save-state');finishDock(view);return true}
function enhanceCommentModal(modal){if(!modal)return false;modal.classList.add('v22v-comment-sheet');modal.querySelector('.modal-content')?.classList.add('v22v-comment-panel');modal.querySelector('.modal-head')?.classList.add('v22v-comment-head');modal.querySelector('.v73-feedback-type')?.classList.add('v22v-comment-types');modal.querySelector('textarea')?.classList.add('v22v-comment-text');const send=[...modal.querySelectorAll('button')].find(x=>/Enviar al coach/i.test(t(x.textContent)));send?.classList.add('v22v-comment-submit');return true}
function historyMetrics(row){const copy=row.querySelector('.v244-history-copy');if(!copy)return;const badges=copy.querySelector('.v244-history-badges')||row.querySelector('.v244-history-badges');badges?.classList.add('v22v-history-signals');const muted=copy.querySelector('.muted');muted?.classList.add('v22v-history-subline')}
function enhanceHistory(host){if(!host)return false;trimDuplicateNav(document.getElementById('view')||host);const card=host.querySelector('.v22-premium-history');if(!card)return false;card.classList.add('v22v-history');card.querySelector('.v244-history-list')?.classList.add('v22v-history-list');
 [...card.querySelectorAll('.v22-history-session')].forEach((row,index)=>{row.classList.add('v22v-history-session');if(!row.querySelector('.v22v-history-index'))row.prepend(make('span','v22v-history-index',String(index+1).padStart(2,'0')));row.querySelector('.v244-history-copy')?.classList.add('v22v-history-copy');historyMetrics(row);const b=row.querySelector(':scope > button');if(b)b.classList.add('v22v-history-open')});return true}
function sessionLayout(modal){const content=modal.querySelector('.modal-content');if(!content)return;const k=modal.querySelector('.v244-summary-grid'),flow=modal.querySelector('.v244-timeline');if(!k||!flow)return;let layout=modal.querySelector('.v22v-session-layout');if(!layout){layout=make('div','v22v-session-layout');k.before(layout);layout.appendChild(k);layout.appendChild(flow)}}
function enhanceSessionDetail(modal){if(!modal)return false;modal.classList.add('v22v-session-modal');modal.querySelector('.modal-content')?.classList.add('v22v-session-panel');modal.querySelector('.modal-head')?.classList.add('v22v-session-head');modal.querySelector('.v244-summary-grid')?.classList.add('v22v-session-kpis');modal.querySelector('.v244-timeline')?.classList.add('v22v-session-flow');sessionLayout(modal);
 [...modal.querySelectorAll('.v244-exercise')].forEach((x,i)=>{x.classList.add('v22v-history-exercise');if(!x.querySelector('.v22v-history-exercise-index'))x.prepend(make('span','v22v-history-exercise-index',String(i+1).padStart(2,'0')))});[...modal.querySelectorAll('.v287-exercise-comment')].forEach(x=>x.classList.add('v22v-context-comment'));return true}
return Object.freeze({VERSION,enhanceWorkout,enhanceCommentModal,enhanceHistory,enhanceSessionDetail});
});
