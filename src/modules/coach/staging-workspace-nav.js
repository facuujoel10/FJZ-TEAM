(function(){
  'use strict';
  const ID='fjzCoachGlobalNav';
  let raf=0,lastDashboard='operations';
  const doc=document;
  function context(){
    try{return typeof window.__fjzCoachContextV22==='function' ? window.__fjzCoachContextV22() : null}
    catch(_e){return null}
  }
  function isCoach(){
    const c=context();
    return (c?.profile?.role==='coach'&&c.mode==='coach') || (c?.mode!=='student'&&!!doc.querySelector('#view > .fjz3a-command-center'));
  }
  function activeDestination(){
    const tab=context()?.coachTab||'dashboard';
    if(tab==='agenda')return 'agenda';
    if(tab==='payments')return 'payments';
    if(tab==='student')return 'students';
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
      bar.innerHTML='<div class="fjz-coach-nav-brand"><span class="fjz-coach-nav-logo">FZ</span><span class="fjz-coach-nav-label"><strong>TEAM FJZ</strong><small>COACH · STAGING</small></span></div><div class="fjz-coach-nav-links">'+
        '<button type="button" data-coach-dest="operations">Operaciones</button>'+
        '<button type="button" data-coach-dest="students">Alumnos</button>'+
        '<button type="button" data-coach-dest="agenda">Agenda</button>'+
        '<button type="button" data-coach-dest="templates">Plantillas</button>'+
        '<button type="button" data-coach-dest="payments">Finanzas</button>'+
        '<button type="button" data-coach-dest="notice">Avisos</button>'+
      '</div>'+
      '<details class="fjz-coach-more"><summary aria-label="Más herramientas del Coach">Más</summary><div class="fjz-coach-more-menu"><button type="button" data-coach-dest="templates">Plantillas</button><button type="button" data-coach-dest="payments">Finanzas</button><button type="button" data-coach-dest="notice">Avisos</button></div></details>'+
      '<div class="fjz-coach-mobile-links" aria-label="Navegación móvil Coach">'+
        '<button type="button" data-coach-dest="operations"><svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.9"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg><span>Panel</span></button>'+
        '<button type="button" data-coach-dest="agenda"><svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.9"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4m10-4v4M3 10h18m-13 4h3m3 0h3m-9 4h3"/></svg><span>Agenda</span></button>'+
        '<button type="button" data-coach-dest="students"><svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.9"><circle cx="12" cy="8" r="4"/><path d="M4.5 21c.5-5 3-7.5 7.5-7.5s7 2.5 7.5 7.5"/></svg><span>Alumno</span></button>'+
        '<button type="button" data-coach-dest="new-student"><svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.9"><circle cx="10" cy="8" r="4"/><path d="M2.5 21c.5-5 3-7.5 7.5-7.5m8-3v9m-4.5-4.5h9"/></svg><span>Nuevo</span></button>'+
      '</div>';
      bar.onclick=function(event){
        const btn=event.target.closest('[data-coach-dest]');
        if(!btn||!isCoach())return;
        const dest=btn.dataset.coachDest;
        if(dest==='new-student'){window.newStudent?.();return}
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
          synchronize();
          schedule();
          const id=dest==='students'?'fjz3a-students':'fjz3a-reviews';
          requestAnimationFrame(function(){doc.getElementById(id)?.scrollIntoView?.({block:'start',behavior:'auto'})});
        }
      };
    }
    if(bar.parentElement!==view.parentElement||bar.nextElementSibling!==view)
      view.parentElement.insertBefore(bar,view);
    const brandLogo=doc.querySelector('.topbar .brand img');
    const logoSlot=bar.querySelector('.fjz-coach-nav-logo');
    if(brandLogo&&logoSlot&&!logoSlot.querySelector('img')){
      const image=brandLogo.cloneNode(true);
      image.removeAttribute('id');
      image.alt='Logo TEAM FJZ';
      logoSlot.replaceChildren(image);
    }
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
    if(tab!=='payments')bar.querySelector('.fjz-coach-more')?.removeAttribute('open');
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
    if(!doc.getElementById('view'))return;
    synchronize();
  }
  window.__fjzSyncCoachWorkspaceNavV22=synchronize;
  initialize();
})();