import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.24 STUDENT DASHBOARD PRO
# =========================================================
# Build-time replacement of the base student HOME view only.
# No new data queries, listeners, timers, render wrappers or channels.
# Existing student subviews/workout logic remain untouched.

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "render_assignments":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "render_student_defs":len(re.findall(r"function\s+renderStudent\s*\(\s*\)",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

before=metrics(html)
if before["styles"]!=1:
    raise RuntimeError("V20.24 expected one stylesheet: "+repr(before))
if before["render_student_defs"]!=1:
    raise RuntimeError("V20.24 expected one base renderStudent definition: "+repr(before))

pat=re.compile(
    r"function\s+renderStudent\s*\(\s*\)\s*\{.*?\n(?=function\s+renderStudentShell\s*\()",
    re.S
)
matches=list(pat.finditer(html))
if len(matches)!=1:
    raise RuntimeError("V20.24 renderStudent block mismatch: "+str(len(matches)))

old=matches[0].group(0)
for marker in [
    "studentTab==='workout'",
    "studentTab==='tracking'",
    "studentTab==='progress'",
    "studentTab==='history'",
    "renderWorkout()",
    "renderTrackingStudent()",
    "renderProgress(false)",
    "renderHistory(false)",
]:
    if marker not in old:
        raise RuntimeError("V20.24 missing student route marker: "+marker)

new=r"""function renderStudent(){
  if(studentTab==='workout')return renderWorkout();
  if(studentTab==='tracking')return renderStudentShell('Check-in y seguimiento',()=>renderTrackingStudent());
  if(studentTab==='progress')return renderStudentShell('Progreso',()=>renderProgress(false));
  if(studentTab==='history')return renderStudentShell('Historial',()=>renderHistory(false));

  const s=student(),v=el('view');
  const days=Array.isArray(s.days)?s.days:[];
  const sessions=Array.isArray(s.sessions)?s.sessions:[];
  const totalExercises=days.reduce((sum,d)=>sum+(Array.isArray(d.exercises)?d.exercises.length:0),0);
  const recent=sessions.slice(-3).reverse();
  const goal=String(s.goal||'Plan personalizado').trim()||'Plan personalizado';

  v.innerHTML=`
    <section class="hero v224-student-hero">
      <div class="v224-hero-copy">
        <div class="v224-eyebrow">TEAM FJZ · TU PLAN</div>
        <h2>Hola, ${esc(s.name)}</h2>
        <p>Entrená, registrá y seguí tu progreso desde un solo lugar.</p>
        <div class="v224-goal"><span>Objetivo</span><strong>${esc(goal)}</strong></div>
      </div>
      <div class="v224-hero-side">
        ${badge(statusFor(s))}
        <div class="v224-quick-actions">
          <button class="btn small" onclick="studentTab='tracking';render()">Check-in</button>
          <button class="btn small" onclick="studentTab='progress';render()">Progreso</button>
          <button class="btn small" onclick="studentTab='history';render()">Historial</button>
        </div>
      </div>
    </section>

    <div class="grid kpi v224-kpi-grid">
      <div class="card v224-kpi-card">
        <span class="v224-kpi-label">Adherencia · 7 días</span>
        <strong>${adherence(s)}%</strong>
        <span>Consistencia reciente</span>
      </div>
      <div class="card v224-kpi-card">
        <span class="v224-kpi-label">Plan</span>
        <strong>${days.length}</strong>
        <span>Días programados</span>
      </div>
      <div class="card v224-kpi-card">
        <span class="v224-kpi-label">Rutina</span>
        <strong>${totalExercises}</strong>
        <span>Ejercicios programados</span>
      </div>
      <div class="card v224-kpi-card">
        <span class="v224-kpi-label">Historial</span>
        <strong>${sessions.length}</strong>
        <span>Sesiones guardadas</span>
      </div>
    </div>

    <div class="grid v224-dashboard-grid">
      <section class="card v224-plan-card">
        <div class="section-title v224-plan-head">
          <div>
            <div class="v224-section-kicker">ENTRENAMIENTO</div>
            <h3>Tu plan</h3>
            <div class="muted tiny">Elegí el día que vas a entrenar y registrá la sesión.</div>
          </div>
          <span class="badge blue">Rutina del coach</span>
        </div>

        <div class="v224-day-list">
          ${days.length?days.map((d,i)=>`
            <div class="v224-day-row">
              <div class="v224-day-index">${String(i+1).padStart(2,'0')}</div>
              <div class="v224-day-copy">
                <strong>${esc(d.name)}</strong>
                <div class="muted tiny">${esc(d.muscles||'A definir')} · ${(d.exercises||[]).length} ejercicios</div>
              </div>
              <button class="btn primary small v224-day-action" onclick="startWorkout(${i})">Entrenar</button>
            </div>
          `).join(''):'<div class="empty">Tu coach todavía no cargó días de entrenamiento.</div>'}
        </div>
      </section>

      <aside class="v224-side-stack">
        <section class="card v224-coach-card">
          <div class="v224-section-kicker">COACH</div>
          <div class="section-title">
            <h3>Mensaje del coach</h3>
            <span class="badge red">FJZ</span>
          </div>
          <div class="coach-note v224-coach-message">${esc(s.coachMessage||'Sin mensaje nuevo.')}</div>
          <button class="btn primary v224-checkin-cta" onclick="studentTab='tracking';render()">Completar check-in</button>
        </section>

        <section class="card v224-recent-card">
          <div class="section-title">
            <div>
              <div class="v224-section-kicker">ACTIVIDAD</div>
              <h3>Últimas sesiones</h3>
            </div>
            ${sessions.length?`<span class="badge green">${sessions.length}</span>`:''}
          </div>
          <div class="v224-recent-list">
            ${recent.length?recent.map(x=>`
              <div class="history-item v224-history-item">
                <div>
                  <strong>${esc(x.dayName)}</strong>
                  <div class="muted tiny">${fmtDate(x.date)} · ${x.summary?.totalSets||0} series</div>
                </div>
                <span class="badge ${x.summary?.review?'red':'green'}">${x.summary?.review?'Revisar':'OK'}</span>
              </div>
            `).join(''):'<div class="empty">Todavía no hay sesiones guardadas.</div>'}
          </div>
          ${sessions.length?`<button class="btn ghost v224-history-cta" onclick="studentTab='history';render()">Ver historial completo</button>`:''}
        </section>
      </aside>
    </div>`;
}
"""
html=html[:matches[0].start()]+new+html[matches[0].end():]

css=r"""
/* =========================================================
   TEAM FJZ · V20.24 STUDENT DASHBOARD PRO
   ========================================================= */

.v224-student-hero{align-items:center;padding:4px 0 2px}
.v224-hero-copy{min-width:0}
.v224-eyebrow,.v224-section-kicker{color:#ff6674;font-size:10px;line-height:1.2;font-weight:900;letter-spacing:.16em}
.v224-eyebrow{margin-bottom:8px}
.v224-student-hero h2{margin-bottom:7px}
.v224-goal{display:flex;align-items:center;gap:9px;margin-top:12px;min-width:0}
.v224-goal span{flex:0 0 auto;color:var(--muted);font-size:11px;font-weight:750;text-transform:uppercase;letter-spacing:.08em}
.v224-goal strong{min-width:0;color:#e9eaee;font-size:13px;font-weight:780;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.v224-hero-side{display:flex;align-items:flex-end;flex-direction:column;gap:10px;min-width:0}
.v224-quick-actions{display:flex;gap:7px;flex-wrap:wrap;justify-content:flex-end}
.v224-kpi-grid{margin-bottom:18px}
.v224-kpi-card{display:flex;flex-direction:column;justify-content:center;min-height:116px}
.v224-kpi-label{color:#ff7985!important;font-size:10px!important;font-weight:900!important;text-transform:uppercase;letter-spacing:.11em;margin-bottom:8px}
.v224-kpi-card>strong{margin-bottom:5px}
.v224-dashboard-grid{grid-template-columns:minmax(0,1.45fr) minmax(310px,.82fr);gap:16px;align-items:start}
.v224-plan-card{min-width:0}
.v224-plan-head{align-items:flex-start;margin-top:0;margin-bottom:7px}
.v224-plan-head h3,.v224-recent-card h3{margin-top:3px}
.v224-day-list{display:grid;margin-top:5px}
.v224-day-row{display:grid;grid-template-columns:42px minmax(0,1fr) auto;gap:12px;align-items:center;min-width:0;padding:14px 0;border-top:1px solid var(--border-soft)}
.v224-day-row:first-child{border-top:0}
.v224-day-index{width:38px;height:38px;display:grid;place-items:center;border:1px solid #30343d;border-radius:11px;background:#0e0f13;color:#ff6674;font-size:11px;font-weight:900;letter-spacing:.04em}
.v224-day-copy{min-width:0}
.v224-day-copy strong{display:block;color:#f7f7f9;font-size:14px;font-weight:860;margin-bottom:4px}
.v224-day-copy .tiny{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.v224-side-stack{display:grid;gap:16px;min-width:0}
.v224-coach-card{background:linear-gradient(145deg,rgba(255,38,57,.075),transparent 44%),var(--card)}
.v224-coach-card>.section-title{margin-top:5px}
.v224-coach-message{min-height:74px;line-height:1.55;color:#dedfe4;border-color:rgba(255,38,57,.17);background:rgba(5,5,7,.34)}
.v224-checkin-cta,.v224-history-cta{width:100%;margin-top:12px}
.v224-recent-list{display:grid;gap:8px}
.v224-history-item{box-shadow:none;background:#101116;padding:11px}

@media(max-width:900px){
  .v224-student-hero{align-items:flex-start}
  .v224-hero-side{width:100%;align-items:flex-start}
  .v224-quick-actions{width:100%;justify-content:flex-start}
  .v224-dashboard-grid{grid-template-columns:1fr}
  .v224-side-stack{grid-template-columns:1fr}
}

@media(max-width:520px){
  .v224-goal{align-items:flex-start;flex-direction:column;gap:4px}
  .v224-goal strong{white-space:normal}
  .v224-quick-actions{display:grid;grid-template-columns:repeat(3,minmax(0,1fr))}
  .v224-quick-actions .btn{width:100%;padding-left:7px;padding-right:7px}
  .v224-kpi-card{min-height:106px}
  .v224-day-row{grid-template-columns:36px minmax(0,1fr) auto;gap:9px;padding:13px 0}
  .v224-day-index{width:34px;height:34px;border-radius:10px}
  .v224-day-action{min-width:76px}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.24 stylesheet surface changed: "+str(len(styles)))
sm=styles[0]
new_style=sm.group("body").rstrip()+"\n"+css+"\n"
html=html[:sm.start("body")]+new_style+html[sm.end("body"):]

marker='<meta name="fjz-student-dashboard" content="20.24">'
if re.search(r'<meta\s+name=["\']fjz-student-dashboard["\']',html,re.I):
    html=re.sub(
        r'<meta\s+name=["\']fjz-student-dashboard["\']\s+content=["\'][^"\']*["\']\s*/?>',
        marker,html,count=1,flags=re.I
    )
else:
    html=html.replace("</head>",marker+"\n</head>",1)

after=metrics(html)
for key in (
    "styles","render_assignments","channels","mutation_observers",
    "performance_observers","timeouts","rafs","listeners","render_student_defs"
):
    if after[key]!=before[key]:
        raise RuntimeError("V20.24 runtime topology changed for "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-student-dashboard" content="20.24"',
    "TEAM FJZ · V20.24 STUDENT DASHBOARD PRO",
    "v224-student-hero",
    "v224-dashboard-grid",
    "v224-day-row",
    "v224-coach-card",
    "v224-recent-card",
    "startWorkout(${i})",
    "studentTab='tracking';render()",
    "studentTab='progress';render()",
    "studentTab='history';render()",
    "function renderStudentShell",
    "__fjzV222",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.24 missing dashboard/stability marker: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.24 student dashboard pro")
print("V20.24 BEFORE:",before)
print("V20.24 AFTER:",after)
print("V20.24 student home reorganized with existing data/actions only")
