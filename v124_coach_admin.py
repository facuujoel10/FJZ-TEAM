import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# Remove the old runtime that actively rewrites every version label back to 12.1.
html,n_old=re.subn(
    r'<script id="v121ReleaseRuntime">.*?</script>',
    '',
    html,
    count=1,
    flags=re.S
)

# Normalize all visible/static version labels to the current release.
html=re.sub(r'TEAM FJZ V\d+(?:\.\d+)+','TEAM FJZ V12.4',html)
html=re.sub(r'(?i)(versi[oó]n\s*[:·-]?\s*)V?\d+(?:\.\d+)+',r'\1V12.4',html)

# Keep one machine-readable release marker.
html=re.sub(
    r'<meta\s+name=["\']fjz-release["\']\s+content=["\'][^"\']*["\']\s*/?>',
    '<meta name="fjz-release" content="12.4">',
    html,
    count=1,
    flags=re.I
)

css=r"""
<style id="v124CoachAdminStyles">
.v124-admin-card{margin:14px 0}
.v124-admin-actions{display:flex;gap:8px;flex-wrap:wrap}
.v124-admin-actions .btn{min-width:150px}
.v124-empty{padding:18px;border:1px dashed var(--border);border-radius:12px;text-align:center;color:var(--muted)}
.v124-payments-head{display:flex;justify-content:space-between;gap:10px;align-items:flex-start;flex-wrap:wrap}
@media(max-width:520px){.v124-admin-actions .btn{width:100%}}
</style>
"""

js=r"""
<script id="v124CoachAdminRuntime">
(function(){
  const RELEASE='12.4';
  window.__FJZ_RELEASE__=RELEASE;

  function normalizeVersionV124(){
    document.querySelectorAll('body *').forEach(el=>{
      if(el.children.length)return;
      const t=el.textContent||'';
      if(/TEAM FJZ V\d+(?:\.\d+)+/i.test(t)){
        el.textContent=t.replace(/TEAM FJZ V\d+(?:\.\d+)+/gi,'TEAM FJZ V'+RELEASE);
      }else if(/versi[oó]n\s*[:·-]?\s*V?\d+(?:\.\d+)+/i.test(t)){
        el.textContent=t.replace(/(versi[oó]n\s*[:·-]?\s*)V?\d+(?:\.\d+)+/gi,'$1V'+RELEASE);
      }
    });
  }

  window.openPaymentsV124=function(){
    coachTab='payments';
    render();
  };

  window.openNoticePickerV124=function(){
    if(currentProfile?.role!=='coach')return;
    showModal(
      '<div class="modal-head"><div><h3>Enviar alerta a alumno</h3><div class="muted tiny">Elegí a quién querés avisar.</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="v81-reminders">'+
      state.students.map(s=>'<button class="btn" style="width:100%;justify-content:flex-start" onclick="openNoticeForStudentV124(\''+s.id+'\')">'+esc(s.name)+'</button>').join('')+
      '</div>'
    );
  };

  window.openNoticeForStudentV124=function(clientId){
    state.selectedStudentId=clientId;
    saveState();
    const s=state.students.find(x=>x.id===clientId);
    const ath=cloudAthletes.get(clientId);
    if(!s||!ath){toast('No encuentro la ficha del alumno');return}
    showModal(
      '<div class="modal-head"><div><h3>Nueva alerta</h3><div class="muted tiny">'+esc(s.name)+'</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="form-grid">'+
        '<label class="tiny muted span2">Título<input id="v124NoticeTitle" class="input" placeholder="Ej: Recordatorio importante"></label>'+
        '<label class="tiny muted span2">Mensaje<textarea id="v124NoticeBody" class="input" rows="4" placeholder="Escribí el mensaje que verá el alumno"></textarea></label>'+
        '<label class="tiny muted">Prioridad<select id="v124NoticePriority" class="input"><option value="info">Informativa</option><option value="important">Importante</option></select></label>'+
        '<label class="tiny muted">Visible por<select id="v124NoticeDays" class="input"><option value="7">7 días</option><option value="14">14 días</option><option value="30">30 días</option><option value="0">Sin vencimiento</option></select></label>'+
      '</div>'+
      '<button class="btn primary" style="width:100%;margin-top:12px" onclick="sendNoticeV124(\''+clientId+'\')">Enviar alerta</button>'
    );
  };

  window.sendNoticeV124=async function(clientId){
    const ath=cloudAthletes.get(clientId);
    if(!ath){toast('No encuentro la ficha del alumno');return}
    const title=(el('v124NoticeTitle')?.value||'').trim();
    const body=(el('v124NoticeBody')?.value||'').trim();
    if(!title||!body){toast('Completá título y mensaje');return}
    const days=Number(el('v124NoticeDays')?.value||0);
    const expires_at=days?new Date(Date.now()+days*86400000).toISOString():null;
    const {error}=await supabaseClient.from('student_notices').insert({
      athlete_id:ath.id,
      coach_id:currentUser.id,
      title,
      body,
      priority:el('v124NoticePriority')?.value||'info',
      expires_at,
      active:true
    });
    if(error){toast(cloudErr(error));return}
    closeModal();
    toast('Alerta enviada');
    coachFeedLoadedAt=0;
  };

  function injectCoachAdminCardV124(){
    if(currentProfile?.role!=='coach'||coachTab!=='dashboard')return;
    if(el('v124CoachAdminCard'))return;
    const view=el('view');
    if(!view)return;
    const hero=view.querySelector('.hero');
    if(!hero)return;

    const card=document.createElement('div');
    card.id='v124CoachAdminCard';
    card.className='card v124-admin-card';
    card.innerHTML=
      '<div class="section-title"><div><h3>Administración</h3><div class="muted tiny">Cobranzas y avisos manuales para tus alumnos.</div></div></div>'+
      '<div class="v124-admin-actions">'+
        '<button class="btn primary" onclick="openPaymentsV124()">Pagos y cobranzas</button>'+
        '<button class="btn" onclick="openNoticePickerV124()">Enviar alerta</button>'+
      '</div>';
    hero.insertAdjacentElement('afterend',card);
  }

  // Make Payments routing explicit using the real global binding.
  const previousRenderCoachV124=renderCoach;
  renderCoach=function(){
    if(coachTab==='payments'&&typeof window.renderCoachPaymentsV122==='function'){
      return window.renderCoachPaymentsV122();
    }
    return previousRenderCoachV124.apply(this,arguments);
  };

  // Make the Coach navigation explicit instead of relying on V12.2 winning the wrapper chain.
  const previousBottomV124=renderBottomNav;
  renderBottomNav=function(){
    if(mode==='coach'){
      const nav=el('bottomNav');
      if(nav){
        nav.innerHTML=
          '<button class="'+(coachTab==='dashboard'?'active':'')+'" onclick="coachTab=\'dashboard\';render()">Alumnos</button>'+
          '<button class="'+(coachTab==='agenda'?'active':'')+'" onclick="coachTab=\'agenda\';render()">Agenda</button>'+
          '<button class="'+(coachTab==='payments'?'active':'')+'" onclick="coachTab=\'payments\';render()">Pagos</button>'+
          '<button class="'+(coachTab==='music'?'active':'')+'" onclick="coachTab=\'music\';render()">Música</button>'+
          '<button onclick="newStudent()">+ Alumno</button>';
        return;
      }
    }
    return previousBottomV124.apply(this,arguments);
  };

  // Improve the payments empty state and guarantee admin actions in the section itself.
  const previousPaymentsV124=window.renderCoachPaymentsV122;
  if(typeof previousPaymentsV124==='function'){
    window.renderCoachPaymentsV122=async function(){
      await previousPaymentsV124.apply(this,arguments);
      const view=el('view');
      if(!view)return;
      const hero=view.querySelector('.hero');
      if(hero){
        const actions=hero.querySelector('.pill-row')||hero;
        if(!el('v124PayAlertBtn')){
          const btn=document.createElement('button');
          btn.id='v124PayAlertBtn';
          btn.className='btn';
          btn.textContent='Enviar alerta';
          btn.onclick=openNoticePickerV124;
          actions.appendChild(btn);
        }
      }
      const body=el('v122PaymentsBody');
      if(body&&!followupCacheV122?.payments?.length&&!body.querySelector('.v124-empty')){
        const empty=body.querySelector('.empty');
        if(empty){
          empty.className='v124-empty';
          empty.innerHTML='<strong>No hay cobranzas cargadas</strong><div style="margin-top:5px">Tocá “+ Cobranza” para elegir un alumno, fecha e importe.</div>';
        }
      }
    };
  }

  const previousRenderV124=render;
  render=function(){
    const out=previousRenderV124.apply(this,arguments);
    setTimeout(injectCoachAdminCardV124,60);
    setTimeout(normalizeVersionV124,100);
    return out;
  };

  document.addEventListener('DOMContentLoaded',normalizeVersionV124,{once:true});
  setTimeout(normalizeVersionV124,150);

  window.__fjzAdminV124={
    version:RELEASE,
    payments:true,
    manualStudentAlerts:true,
    oldReleaseRuntimeRemoved:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)
p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8")
sw=re.sub(r"team-fjz-v\d+(?:-\d+)+","team-fjz-v12-4",sw)
swp.write_text(sw,encoding="utf-8")

print("TEAM FJZ V12.4 coach admin:",len(html),"bytes","old121_removed",n_old)
