
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
