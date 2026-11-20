(function(){
  'use strict';
  const ID='fjzCoachGlobalNav';
  let viewObserver=null,raf=0,lastDashboard='operations';
  const doc=document;
  function context(){
    try{return typeof window.__fjzCoachContextV22==='function' ? window.__fjzCoachContextV22() : null}
    catch(_e){return null}
  }
  function isCoach(){
    const c=context();
    return c?.profile?.role==='coach'&&c.mode==='coach';
  }
  function activeDestination(){
    const tab=context()?.coachTab||'dashboard';
    if(tab==='agenda')return 'agenda';
    if(tab==='payments')return 'payments';
    if(tab==='dashboard')return lastDashboard;
    return '';
  }
  function ensureBar(){
    const view=doc.getElementById('view');
    if(!view||!view.parentElement)return null;
    let bar=doc.getElementById(ID);
    if(!bar){
      bar=doc.createElement('nav');
      bar.id=ID;
      bar.hidden=true;
      bar.setAttribute('aria-label','Navegación principal del Coach');
      bar.innerHTML='<div class="fjz-coach-nav-brand"><span class="fjz-coach-nav-logo">FZ</span><span>TEAM FJZ · COACH</span></div><div class="fjz-coach-nav-links">'+
        '<button type="button" data-coach-dest="operations">Operaciones</button>'+
        '<button type="button" data-coach-dest="students">Alumnos</button>'+
        '<button type="button" data-coach-dest="agenda">Agenda</button>'+
        '<button type="button" data-coach-dest="templates">Plantillas</button>'+
        '<button type="button" data-coach-dest="payments">Finanzas</button>'+
        '<button type="button" data-coach-dest="notice">Avisos</button>'+
      '</div>';
      bar.addEventListener('click',function(event){
        const btn=event.target.closest('[data-coach-dest]');
        if(!btn||!isCoach())return;
        const dest=btn.dataset.coachDest;
        if(dest==='notice'){window.openNoticePickerV124?.();return}
        if(dest==='templates'){window.showTemplates?.();return}
        if(dest==='payments'){window.openPaymentsV124?.();schedule();return}
        if(dest==='agenda'){
          if(typeof window.__fjzCoachNavigateV22==='function')window.__fjzCoachNavigateV22('agenda');
          else{window.coachTab='agenda';window.render?.()}
          schedule();return;
        }
        if(dest==='operations'||dest==='students'){
          lastDashboard=dest;
          const c=context();
          if(c?.coachTab!=='dashboard'){
            if(typeof window.__fjzCoachNavigateV22==='function')window.__fjzCoachNavigateV22('dashboard');
            else{window.coachTab='dashboard';window.render?.()}
          }
          schedule();
          const id=dest==='students'?'fjz3a-students':'fjz3a-reviews';
          requestAnimationFrame(function(){doc.getElementById(id)?.scrollIntoView?.({block:'start',behavior:'auto'})});
        }
      });
    }
    if(bar.parentElement!==view.parentElement||bar.nextElementSibling!==view)
      view.parentElement.insertBefore(bar,view);
    return bar;
  }
  function synchronize(){
    const bar=ensureBar();
    if(!bar)return;
    const visible=isCoach();
    bar.hidden=!visible;
    if(!visible)return;
    const current=activeDestination();
    bar.querySelectorAll('button[data-coach-dest]').forEach(b=>{
      if(b.dataset.coachDest===current)b.setAttribute('aria-current','page');
      else b.removeAttribute('aria-current');
    });
    const tab=context()?.coachTab;
    if(tab==='payments'){
      const h=doc.querySelector('#view > .hero h2');
      if(h&&h.textContent.trim()==='Pagos y cobranzas')h.textContent='Finanzas';
    }
  }
  function schedule(){
    if(raf)return;
    raf=requestAnimationFrame(function(){raf=0;synchronize()});
  }
  function initialize(){
    const view=doc.getElementById('view');
    if(!view)return;
    synchronize();
    if(!viewObserver){
      viewObserver=new MutationObserver(schedule);
      viewObserver.observe(view,{childList:true});
    }
  }
  if(doc.readyState==='loading')doc.addEventListener('DOMContentLoaded',initialize,{once:true});
  else initialize();
  window.addEventListener('pageshow',schedule);
})();