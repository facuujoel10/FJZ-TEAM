import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.25 COACH DASHBOARD PRO
# =========================================================
# Reorganize the existing V8.0/V20.x coach dashboard authority.
# Preserve all asynchronous attention-feed IDs/actions and student filtering.
# No new queries, listeners, timers, render wrappers, channels or payment work.

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
        "coach_dashboard_defs":len(re.findall(r"function\s+renderCoachDashboardV80\s*\(\s*\)",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

before=metrics(html)
if before["styles"]!=1:
    raise RuntimeError("V20.25 expected one stylesheet: "+repr(before))
if before["coach_dashboard_defs"]!=1:
    raise RuntimeError("V20.25 expected one coach dashboard authority: "+repr(before))

pat=re.compile(
    r"function\s+renderCoachDashboardV80\s*\(\s*\)\s*\{.*?\n(?=const\s+_renderCoachV80Base\s*=\s*renderCoach;)",
    re.S
)
matches=list(pat.finditer(html))
if len(matches)!=1:
    raise RuntimeError("V20.25 renderCoachDashboardV80 block mismatch: "+str(len(matches)))

old=matches[0].group(0)
for marker in [
    "v80AttentionCount","v80CriticalCount","v80CommentCount","v80CheckinCount",
    "v80AttentionFilters","v80AttentionBody","studentSearch","studentList",
    "hydrateCoachDashboardV80()","showSystemStatusV80()","showTemplates()",
    "coachTab='music';render()","newStudent()"
]:
    if marker not in old:
        raise RuntimeError("V20.25 missing coach dashboard marker: "+marker)

new=r"""function renderCoachDashboardV80(){
  const v=el('view');
  const students=Array.isArray(state.students)?state.students:[];
  const avg=Math.round(students.reduce((a,s)=>a+adherence(s),0)/Math.max(1,students.length));
  const reviewCount=students.filter(s=>statusFor(s)==='Revisar').length;
  const progressingCount=students.filter(s=>statusFor(s)==='Progresando').length;

  v.innerHTML=`<section class="hero v225-coach-hero">
    <div class="v225-hero-copy">
      <div class="v225-eyebrow">TEAM FJZ · COACH CONTROL</div>
      <h2>Panel Coach</h2>
      <p>Prioridades, seguimiento y alumnos en una vista pensada para decidir rápido qué necesita atención.</p>
    </div>
    <div class="v225-hero-actions">
      <button class="btn" onclick="showSystemStatusV80()">Estado</button>
      <button class="btn" onclick="showTemplates()">Plantillas</button>
      <button class="btn" onclick="coachTab='music';render()">Música</button>
      <button class="btn primary" onclick="newStudent()">+ Nuevo alumno</button>
    </div>
  </section>

  <div class="grid kpi v225-kpi-grid">
    <div class="card v225-kpi-card">
      <span class="v225-kpi-label">ALUMNOS</span>
      <strong>${students.length}</strong>
      <span>Activos en el panel</span>
    </div>
    <div class="card v225-kpi-card">
      <span class="v225-kpi-label">ADHERENCIA</span>
      <strong>${avg||0}%</strong>
      <span>Media de 7 días</span>
    </div>
    <div class="card v225-kpi-card ${reviewCount?'v225-kpi-attention':''}">
      <span class="v225-kpi-label">REVISIÓN</span>
      <strong>${reviewCount}</strong>
      <span>Alumnos a revisar</span>
    </div>
    <div class="card v225-kpi-card v225-kpi-attention">
      <span class="v225-kpi-label">ATENCIÓN HOY</span>
      <strong id="v80AttentionCount">—</strong>
      <span>Elementos pendientes</span>
    </div>
  </div>

  <div class="grid v225-dashboard-grid">
    <main class="v225-main-column">
      <section class="card v225-attention-card">
        <div class="section-title v225-card-head">
          <div>
            <div class="v225-section-kicker">PRIORIDADES</div>
            <h3>Atención hoy</h3>
            <div class="muted tiny">Comentarios, check-ins y señales que requieren una decisión tuya.</div>
          </div>
          <button class="btn small" onclick="hydrateCoachDashboardV80()">Actualizar</button>
        </div>
        <div class="v80-filter-row v225-filter-row" id="v80AttentionFilters"></div>
        <div id="v80AttentionBody"><div class="empty">Cargando prioridades…</div></div>
      </section>

      <section class="card v225-students-card">
        <div class="section-title v225-students-head">
          <div>
            <div class="v225-section-kicker">EQUIPO</div>
            <h3>Alumnos</h3>
            <div class="muted tiny">${progressingCount} progresando · ${reviewCount} requieren revisión</div>
          </div>
          <input id="studentSearch" class="input v225-search" placeholder="Buscar alumno...">
        </div>
        <div class="student-list v225-student-list" id="studentList">${studentRows(students)}</div>
      </section>
    </main>

    <aside class="v225-side-column">
      <section class="card v225-today-card">
        <div class="v225-section-kicker">RESUMEN</div>
        <div class="section-title"><h3>Señales de hoy</h3><span class="badge red" id="v80CriticalCount">—</span></div>
        <div class="v225-signal-grid">
          <button class="v225-signal" onclick="attentionFilterV80='exercise_feedback';hydrateCoachDashboardV80()">
            <strong id="v80CommentCount">—</strong>
            <span>Comentarios</span>
          </button>
          <button class="v225-signal" onclick="attentionFilterV80='wellness';hydrateCoachDashboardV80()">
            <strong id="v80CheckinCount">—</strong>
            <span>Check-ins / recuperación</span>
          </button>
        </div>
        <div class="v225-side-actions">
          <button class="btn" onclick="attentionFilterV80='critical';hydrateCoachDashboardV80()">Ver prioridad alta</button>
          <button class="btn" onclick="attentionFilterV80='nutrition';hydrateCoachDashboardV80()">Ver nutrición</button>
        </div>
      </section>

      <section class="card v225-flow-card">
        <div class="v225-section-kicker">FLUJO DE TRABAJO</div>
        <div class="section-title"><h3>Orden recomendado</h3></div>
        <div class="v225-flow-list">
          <div class="v225-flow-step">
            <span>01</span>
            <div><strong>Prioridad alta</strong><p>Molestias y recuperación comprometida primero.</p></div>
          </div>
          <div class="v225-flow-step">
            <span>02</span>
            <div><strong>Check-ins y adherencia</strong><p>Revisá cambios en sueño, estrés, energía y continuidad.</p></div>
          </div>
          <div class="v225-flow-step">
            <span>03</span>
            <div><strong>Progresión</strong><p>Decidí si mantener, progresar o ajustar el plan.</p></div>
          </div>
        </div>
      </section>
    </aside>
  </div>`;

  const search=el('studentSearch');
  if(search)search.oninput=e=>{
    const q=normalizeTextV70(e.target.value);
    el('studentList').innerHTML=studentRows(students.filter(s=>normalizeTextV70(s.name).includes(q)));
    hydrateCoachDashboardV80()
  };
  hydrateCoachDashboardV80();
}
"""
html=html[:matches[0].start()]+new+html[matches[0].end():]

css=r"""
/* =========================================================
   TEAM FJZ · V20.25 COACH DASHBOARD PRO
   ========================================================= */

.v225-coach-hero{align-items:center}
.v225-hero-copy{min-width:0}
.v225-eyebrow,.v225-section-kicker{color:#ff6674;font-size:10px;line-height:1.2;font-weight:900;letter-spacing:.16em}
.v225-eyebrow{margin-bottom:8px}
.v225-hero-actions{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
.v225-kpi-grid{margin-bottom:18px}
.v225-kpi-card{display:flex;flex-direction:column;justify-content:center;min-height:116px}
.v225-kpi-label{color:#ff7985!important;font-size:10px!important;font-weight:900!important;letter-spacing:.11em;margin-bottom:8px}
.v225-kpi-card>strong{margin-bottom:5px}
.v225-kpi-attention{border-color:rgba(255,38,57,.24);background:linear-gradient(145deg,rgba(255,38,57,.05),transparent 48%),var(--card)}
.v225-dashboard-grid{grid-template-columns:minmax(0,1.5fr) minmax(310px,.72fr);gap:16px;align-items:start}
.v225-main-column,.v225-side-column{display:grid;gap:16px;min-width:0}
.v225-card-head,.v225-students-head{align-items:flex-start;margin-top:0}
.v225-card-head h3,.v225-students-head h3,.v225-today-card h3,.v225-flow-card h3{margin-top:3px}
.v225-attention-card{border-color:#30333c}
.v225-filter-row{display:flex;gap:7px;flex-wrap:wrap;margin:12px 0}
.v225-filter-row .btn.active{background:var(--red-soft);border-color:var(--red-border);color:#fff}
.v225-search{max-width:270px!important}
.v225-student-list .student-row{box-shadow:none}
.v225-today-card{background:linear-gradient(145deg,rgba(255,38,57,.065),transparent 46%),var(--card)}
.v225-signal-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.v225-signal{appearance:none;border:1px solid var(--border);background:#0e0f13;color:var(--text);border-radius:13px;padding:14px;text-align:left;cursor:pointer}
.v225-signal strong{display:block;color:#fff;font-size:24px;line-height:1;font-weight:920;margin-bottom:7px}
.v225-signal span{color:var(--muted);font-size:11px;font-weight:700;line-height:1.35}
.v225-side-actions{display:grid;gap:8px;margin-top:10px}
.v225-flow-list{display:grid}
.v225-flow-step{display:grid;grid-template-columns:34px minmax(0,1fr);gap:10px;padding:12px 0;border-top:1px solid var(--border-soft)}
.v225-flow-step:first-child{border-top:0;padding-top:3px}
.v225-flow-step>span{color:#ff6674;font-size:10px;font-weight:900;letter-spacing:.08em;padding-top:3px}
.v225-flow-step strong{color:#f4f5f7;font-size:13px}
.v225-flow-step p{margin:4px 0 0;color:var(--muted);font-size:11px;line-height:1.45}

@media(hover:hover) and (pointer:fine){
  .v225-signal:hover{border-color:#3d414b;background:#13151a}
}

@media(max-width:900px){
  .v225-coach-hero{align-items:flex-start}
  .v225-hero-actions{width:100%;justify-content:flex-start}
  .v225-dashboard-grid{grid-template-columns:1fr}
  .v225-students-head{flex-direction:column}
  .v225-search{max-width:none!important;width:100%}
}

@media(max-width:520px){
  .v225-hero-actions{display:grid;grid-template-columns:1fr 1fr}
  .v225-hero-actions .btn{width:100%}
  .v225-kpi-card{min-height:106px}
  .v225-signal-grid{grid-template-columns:1fr 1fr}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.25 stylesheet surface changed: "+str(len(styles)))
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

marker='<meta name="fjz-coach-dashboard" content="20.25">'
if re.search(r'<meta\r+name=["\']fjz-coach-dashboard["\']',html,re.I):
    html=re.sub(
        r'<meta\s+name=["\']fjz-coach-dashboard["\']\s+content=["\'][^"\']*["\']\s*/?>',
        marker,html,count=1,flags=re.I
    )
else:
    html=html.replace("</head>",marker+"\n</head>",1)

after=metrics(html)
for key in (
    "styles","render_assignments","channels","mutation_observers",
    "performance_observers","timeouts","rafs","listeners","coach_dashboard_defs"
):
    if after[key]!=before[key]:
        raise RuntimeError("V20.25 runtime topology changed for "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-coach-dashboard" content="20.25"',
    "TEAM FJZ · V20.25 COACH DASHBOARD PRO",
    "v225-coach-hero","v225-dashboard-grid","v225-attention-card","v225-students-card",
    "v80AttentionCount","v80CriticalCount","v80CommentCount","v80CheckinCount",
    "v80AttentionFilters","v80AttentionBody","studentSearch","studentList",
    "hydrateCoachDashboardV80()","showSystemStatusV80()","showTemplates()",
    "coachTab='music';render()","newStudent()",
    "v122FollowupPaymentsRuntime",'meta name="fjz-student-dashboard" content="20.24"'
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.25 missing coach/stability marker: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.25 coach dashboard pro")
print("V20.25 BEFORE:",before)
print("V20.25 AFTER:",after)
print("V20.25 coach dashboard reorganized without new data/runtime work")
