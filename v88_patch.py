
import pathlib

OUT = pathlib.Path("public")
p = OUT / "index.html"
html = p.read_text(encoding="utf-8")

html = html.replace("TEAM FJZ V8.7", "TEAM FJZ V8.8")

css = r"""
<style id="v88Fixes">
.v65-lib-shortcuts{display:none!important}
.v88-version{font-size:9px;color:var(--muted);opacity:.65;margin-top:3px}
</style>
"""

js = r"""
<script id="v88Runtime">
(function(){
  function ensureMotivationV88(){
    if(currentProfile?.role!=='student'||studentTab!=='tracking')return;
    if(document.getElementById('ciMotivation'))return;
    var grid=document.querySelector('.tracking-grid');
    if(!grid)return;
    var card=document.createElement('div');
    card.className='track-score';
    card.innerHTML='<label>Motivación</label><input id="ciMotivation" class="input" type="number" min="1" max="10" value="7">';
    var recovery=document.getElementById('ciRecovery')?.closest('.track-score');
    if(recovery)grid.insertBefore(card,recovery); else grid.appendChild(card);
  }

  function cleanupLibraryShortcutsV88(){
    document.querySelectorAll('.v65-lib-shortcuts').forEach(function(n){n.remove();});
  }

  var oldRenderV88=window.render;
  window.render=function(){
    oldRenderV88();
    setTimeout(function(){ensureMotivationV88();cleanupLibraryShortcutsV88();},20);
    setTimeout(function(){ensureMotivationV88();cleanupLibraryShortcutsV88();},250);
  };

  var oldTrackingV88=window.renderTrackingStudent;
  if(typeof oldTrackingV88==='function'){
    window.renderTrackingStudent=function(){
      oldTrackingV88();
      setTimeout(ensureMotivationV88,0);
    };
  }

  var oldOpenLibraryV88=window.openLibrary;
  if(typeof oldOpenLibraryV88==='function'){
    window.openLibrary=function(dayIndex){
      oldOpenLibraryV88(dayIndex);
      setTimeout(cleanupLibraryShortcutsV88,0);
    };
  }

  setTimeout(function(){
    var brand=document.querySelector('.brand');
    if(brand&&!document.getElementById('v88Version')){
      var v=document.createElement('div');v.id='v88Version';v.className='v88-version';v.textContent='V8.8';brand.appendChild(v);
    }
  },100);
})();
</script>
"""

html = html.replace("</head>", css + "\n</head>", 1)
html = html.replace("</body>", js + "\n</body>", 1)
p.write_text(html, encoding="utf-8")

swp = OUT / "sw.js"
sw = swp.read_text(encoding="utf-8")
for old in ("team-fjz-v8-4","team-fjz-v8-5","team-fjz-v8-6","team-fjz-v8-7"):
    sw = sw.replace(old, "team-fjz-v8-8")
sw = sw.replace(
    "fetch(req).then(res=>{",
    "fetch(new Request(req,{cache:'no-store'})).then(res=>{"
)
swp.write_text(sw, encoding="utf-8")

print("TEAM FJZ V8.8 fixes aplicado:", len(html), "bytes")


# V8.9 · objetivos múltiples + perfil 360 simplificado
import re
html = p.read_text(encoding="utf-8")
html = html.replace("TEAM FJZ V8.8","TEAM FJZ V8.9")

html = re.sub(
    r"function newStudent\(\)\{.*?\}\nfunction createStudent\(\)\{.*?\}\n\nfunction renderStudent\(",
    """function newStudent(){const goals=['Ganar masa muscular','Bajar grasa','Recomposición corporal','Mejorar fuerza','Mejorar rendimiento','Mejorar hábitos','Volver a entrenar','Otro'];showModal(`<div class="modal-head"><div><h3>Nuevo alumno</h3><div class="muted tiny">Podés elegir uno o varios objetivos.</div></div><button class="btn small" onclick="closeModal()">✕</button></div><label class="tiny muted">Nombre<input id="nName" class="input"></label><div style="margin-top:12px"><div class="tiny muted">Objetivos</div><div class="v89-goals">${goals.map((g,i)=>`<label class="v89-goal"><input type="checkbox" class="v89-goal-check" value="${esc(g)}" ${g==='Otro'?'onchange="toggleOtherGoalV89(this.checked)"':''}><span>${esc(g)}</span></label>`).join('')}</div><div id="v89OtherWrap" style="display:none;margin-top:8px"><label class="tiny muted">Otro objetivo<input id="v89OtherText" class="input" placeholder="Escribí el objetivo personalizado"></label></div></div><label class="tiny muted" style="display:block;margin-top:12px">Entrenamientos por semana<input id="nFreq" class="input" type="number" min="1" max="7" value="4"></label><button class="btn primary" style="width:100%;margin-top:14px" onclick="createStudent()">Crear alumno</button>`)}
function toggleOtherGoalV89(on){const w=el('v89OtherWrap');if(w)w.style.display=on?'block':'none'}
function createStudent(){const name=el('nName').value.trim();if(!name){toast('Escribí el nombre del alumno');return}let goals=[...document.querySelectorAll('.v89-goal-check:checked')].map(x=>x.value).filter(x=>x!=='Otro');if(document.querySelector('.v89-goal-check[value="Otro"]')?.checked){const x=el('v89OtherText')?.value.trim();if(x)goals.push(x)}if(!goals.length){toast('Elegí al menos un objetivo');return}const s={id:uid('s'),name,goal:goals.join(' · '),coachMessage:'Respetá la técnica y el RIR indicado.',checkin:'Pendiente',plannedPerWeek:+el('nFreq').value||4,lastWorkout:null,days:[{id:uid('d'),name:'Día 1',muscles:'A definir',exercises:[]}],sessions:[],checkins:[]};state.students.push(s);state.selectedStudentId=s.id;saveState();closeModal();coachTab='student';coachStudentTab='routine';render();toast('Alumno creado')}

function renderStudent(""",
    html, count=1, flags=re.S
)

html = re.sub(
    r"async function buildStudent360V80\(\)\{.*?\n\}\nasync function injectStudent360V80",
    """async function buildStudent360V80(){const s=student();let latest=null,nutrition=null;try{await Promise.all([loadTracking(true),loadNutrition(true),loadExerciseFeedbackV73(true)]);latest=trackingCache.checkins?.[0]||null;nutrition=nutritionCache.plan||null}catch(e){}const pending=pendingFeedbackV73?.().length||0;const sessions30=progressSessionsInDaysV72?.(s,30)?.length||0;return `<div class="card v80-360" id="v80Student360"><div class="section-title"><div><h3>Resumen 360°</h3><div class="muted tiny">Datos clave del seguimiento.</div></div>${pending?`<span class="v73-alert-badge pulse">${pending} comentario${pending>1?'s':''}</span>`:''}</div><div class="v80-360-grid"><div class="v80-360-metric"><strong>${adherence(s)}%</strong><span>Adherencia 7 días</span></div><div class="v80-360-metric"><strong>${sessions30}</strong><span>Sesiones 30 días</span></div><div class="v80-360-metric"><strong>${latest?latest.energy_level+'/10':'—'}</strong><span>Energía</span></div><div class="v80-360-metric"><strong>${latest?(latest.motivation_level??'—')+'/10':'—'}</strong><span>Motivación</span></div><div class="v80-360-metric"><strong>${latest?latest.recovery_level+'/10':'—'}</strong><span>Recuperación</span></div><div class="v80-360-metric"><strong>${nutrition?'Activo':'—'}</strong><span>Nutrición</span></div></div></div>`}
async function injectStudent360V80""",
    html, count=1, flags=re.S
)

html = html.replace("</head>", "<style id=\"v89Styles\">.v89-goals{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:8px}.v89-goal{display:flex;gap:8px;align-items:flex-start;border:1px solid var(--border);background:var(--card);border-radius:11px;padding:10px}.v89-goal input{width:17px;height:17px;accent-color:var(--red)}@media(max-width:620px){.v89-goals{grid-template-columns:1fr}}</style>\n</head>",1)
p.write_text(html,encoding="utf-8")
sw=swp.read_text(encoding="utf-8").replace("team-fjz-v8-8","team-fjz-v8-9")
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V8.9 mejoras:",len(html),"bytes")


# V9.0 · motivación garantizada en Check-in
html = p.read_text(encoding="utf-8")
html = html.replace("TEAM FJZ V8.9","TEAM FJZ V9.0")

v90_js = r"""
<script id="v90MotivationFix">
(function(){
  function injectMotivationV90(){
    var grid=document.querySelector('#studentSubBody .tracking-grid, #studentSubBody .v701-checkin-scores');
    if(!grid)return false;
    if(document.getElementById('ciMotivation'))return true;
    var card=document.createElement('div');
    card.className='track-score';
    card.setAttribute('data-v90-motivation','1');
    card.innerHTML='<label>Motivación</label><input id="ciMotivation" class="input" type="number" min="1" max="10" value="7">';
    var recovery=document.getElementById('ciRecovery');
    var recoveryCard=recovery&&recovery.closest('.track-score');
    if(recoveryCard)grid.insertBefore(card,recoveryCard);else grid.appendChild(card);
    return true;
  }

  function watchCheckinV90(){
    injectMotivationV90();
    var host=document.getElementById('studentSubBody')||document.getElementById('view');
    if(!host)return;
    if(window.__v90CheckinObserver)window.__v90CheckinObserver.disconnect();
    window.__v90CheckinObserver=new MutationObserver(function(){injectMotivationV90();});
    window.__v90CheckinObserver.observe(host,{childList:true,subtree:true});
    setTimeout(injectMotivationV90,50);
    setTimeout(injectMotivationV90,250);
    setTimeout(injectMotivationV90,800);
  }

  var oldRenderV90=window.render;
  window.render=function(){
    oldRenderV90();
    setTimeout(watchCheckinV90,20);
  };

  var oldTrackingV90=window.renderTrackingStudent;
  if(typeof oldTrackingV90==='function'){
    window.renderTrackingStudent=function(){
      oldTrackingV90();
      setTimeout(watchCheckinV90,0);
    };
  }

  var oldSubmitV90=window.submitWeeklyCheckin;
  if(typeof oldSubmitV90==='function'){
    window.submitWeeklyCheckin=async function(){
      injectMotivationV90();
      return oldSubmitV90();
    };
  }

  setTimeout(watchCheckinV90,100);
})();
</script>
"""
html = html.replace("</body>", v90_js + "\n</body>", 1)
p.write_text(html,encoding="utf-8")

sw=swp.read_text(encoding="utf-8").replace("team-fjz-v8-9","team-fjz-v9-0")
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V9.0 motivacion garantizada:",len(html),"bytes")


# V9.1 · check-in simétrico + validación estricta 1-10
html = p.read_text(encoding="utf-8")
html = html.replace("TEAM FJZ V9.0","TEAM FJZ V9.1")

v91_css = r"""
<style id="v91CheckinPolish">
#studentSubBody .tracking-grid,
#studentSubBody .v701-checkin-scores{
  display:grid!important;
  grid-template-columns:repeat(4,minmax(0,1fr))!important;
  gap:10px!important;
  align-items:stretch!important;
}
#studentSubBody .tracking-grid .track-score,
#studentSubBody .v701-checkin-scores .track-score{
  display:flex!important;
  flex-direction:column!important;
  justify-content:space-between!important;
  min-height:96px!important;
  height:100%!important;
  padding:12px!important;
  border-radius:13px!important;
  box-sizing:border-box!important;
}
#studentSubBody .tracking-grid .track-score label,
#studentSubBody .v701-checkin-scores .track-score label{
  display:block!important;
  min-height:30px!important;
  margin:0 0 8px!important;
  line-height:1.2!important;
}
#studentSubBody .tracking-grid .track-score input,
#studentSubBody .v701-checkin-scores .track-score input{
  width:100%!important;
  min-height:40px!important;
  text-align:center!important;
  font-weight:800!important;
  box-sizing:border-box!important;
}
#studentSubBody .section-title .badge.blue{
  min-width:52px!important;
  text-align:center!important;
  justify-content:center!important;
  padding:6px 9px!important;
  border-radius:999px!important;
  font-size:10px!important;
  letter-spacing:.2px!important;
  white-space:nowrap!important;
}
@media(max-width:900px){
  #studentSubBody .tracking-grid,
  #studentSubBody .v701-checkin-scores{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
  }
}
@media(max-width:430px){
  #studentSubBody .tracking-grid,
  #studentSubBody .v701-checkin-scores{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:8px!important;
  }
  #studentSubBody .tracking-grid .track-score,
  #studentSubBody .v701-checkin-scores .track-score{
    min-height:92px!important;
    padding:10px!important;
  }
}
</style>
"""

v91_js = r"""
<script id="v91CheckinClamp">
(function(){
  function clampScoreV91(input){
    if(!input)return;
    let raw=String(input.value||'').replace(/[^0-9]/g,'');
    if(raw===''){input.value='';return}
    let n=parseInt(raw,10);
    if(!Number.isFinite(n))n=1;
    if(n<1)n=1;
    if(n>10)n=10;
    input.value=String(n);
  }

  function setupScoresV91(){
    const ids=['ciSleep','ciStress','ciEnergy','ciAdh','ciMood','ciMotivation','ciRecovery'];
    ids.forEach(function(id){
      const input=document.getElementById(id);
      if(!input)return;
      input.setAttribute('min','1');
      input.setAttribute('max','10');
      input.setAttribute('step','1');
      input.setAttribute('inputmode','numeric');
      input.setAttribute('pattern','[0-9]*');
      input.oninput=function(){clampScoreV91(input)};
      input.onchange=function(){clampScoreV91(input)};
      input.onblur=function(){
        clampScoreV91(input);
        if(input.value==='')input.value='1';
      };
    });
    const badge=document.querySelector('#studentSubBody .section-title .badge.blue');
    if(badge)badge.textContent='1–10';
  }

  const oldRenderV91=window.render;
  window.render=function(){
    oldRenderV91();
    setTimeout(setupScoresV91,40);
    setTimeout(setupScoresV91,300);
  };

  const oldTrackingV91=window.renderTrackingStudent;
  if(typeof oldTrackingV91==='function'){
    window.renderTrackingStudent=function(){
      oldTrackingV91();
      setTimeout(setupScoresV91,0);
    };
  }

  const oldSubmitV91=window.submitWeeklyCheckin;
  if(typeof oldSubmitV91==='function'){
    window.submitWeeklyCheckin=async function(){
      setupScoresV91();
      const ids=['ciSleep','ciStress','ciEnergy','ciAdh','ciMood','ciMotivation','ciRecovery'];
      for(const id of ids){
        const input=document.getElementById(id);
        if(!input)continue;
        clampScoreV91(input);
        const n=Number(input.value);
        if(!Number.isFinite(n)||n<1||n>10){
          toast('Todos los valores del check-in deben estar entre 1 y 10');
          input.focus();
          return;
        }
      }
      return oldSubmitV91();
    };
  }

  setTimeout(setupScoresV91,100);
})();
</script>
"""

html = html.replace("</head>", v91_css + "\n</head>", 1)
html = html.replace("</body>", v91_js + "\n</body>", 1)
p.write_text(html,encoding="utf-8")

sw=swp.read_text(encoding="utf-8").replace("team-fjz-v9-0","team-fjz-v9-1")
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V9.1 checkin polish:",len(html),"bytes")
