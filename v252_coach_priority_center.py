import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
    }

before=metrics(html)

for marker in [
    'meta name="fjz-warmup-mobility-library" content="20.51"',
    "coachFocusScoreV235","coachReviewLoopStateV238",
    "pendingSessionFeedbackCountV243","openCoachStudentTabV235",
    "renderCoachFocusV235","coachFeedV235"
]:
    if marker not in html:
        raise RuntimeError("V20.52 missing prerequisite: "+marker)

anchor="function renderCoachFocusV235(){"
if html.count(anchor)!=1:
    raise RuntimeError("V20.52 focus authority mismatch")

helpers=r"""
function coachPriorityStateV252(s){
  const o=coachStateV235(s);
  const review=coachReviewLoopStateV238(s);
  const critical=coachCriticalV235(s);
  const sessionFeedback=pendingSessionFeedbackCountV243(s);
  const feed=coachPendingV235(s);

  if(critical>0||sessionFeedback>0){
    return {
      bucket:'urgent',
      score:100+critical*20+sessionFeedback*12+feed*2,
      label:sessionFeedback>0
        ?sessionFeedback+' feedback de sesión pendiente'+(sessionFeedback===1?'':'s')
        :critical+' señal'+(critical===1?' crítica':'es críticas')
    };
  }

  if(review.reviewDue||o.review||o.low||o.inactive||feed>0){
    const reasons=[];
    if(review.reviewDue)reasons.push('revisión vencida');
    if(o.review)reasons.push('requiere revisión');
    if(o.low)reasons.push('adherencia '+o.a+'%');
    if(o.inactive&&o.days<999)reasons.push(o.days+' días sin entrenar');
    if(feed>0)reasons.push(feed+' pendiente'+(feed===1?'':'s'));
    return {
      bucket:'today',
      score:50+coachFocusScoreV235(s),
      label:reasons.slice(0,2).join(' · ')
    };
  }

  return {
    bucket:'watch',
    score:coachFocusScoreV235(s),
    label:review.hasBaseline&&!review.changed?'Seguimiento al día':'Monitorear evolución'
  };
}

function coachPriorityTabV252(s){
  if(pendingSessionFeedbackCountV243(s)>0)return 'summary';
  const a=coachAthleteV235(s);
  const feed=a?(coachFeedV235||[]).filter(x=>x?.athlete_id===a.id):[];
  const critical=feed.find(x=>x?.severity==='critical')||feed[0];
  if(critical?.kind==='checkin'||critical?.kind==='wellness')return 'tracking';
  if(critical?.kind==='nutrition')return 'nutrition';
  if(critical?.kind==='exercise_feedback'||critical?.kind==='training')return 'routine';
  const o=coachStateV235(s);
  if(o.inactive||o.low)return 'summary';
  return 'summary';
}

function coachPriorityRowsV252(bucket){
  return (state.students||[])
    .map(s=>({s,...coachPriorityStateV252(s)}))
    .filter(x=>x.bucket===bucket)
    .sort((a,b)=>b.score-a.score||String(a.s.name||'').localeCompare(String(b.s.name||'')));
}

function priorityPersonV252(item){
  const s=item.s;
  return '<button class="v252-person" onclick="openCoachStudentTabV235(\''+esc(s.id)+'\',\''+esc(coachPriorityTabV252(s))+'\')">'+
    '<span class="v252-avatar">'+esc((s.name||'A').slice(0,2).toUpperCase())+'</span>'+
    '<span class="v252-copy"><strong>'+esc(s.name||'Alumno')+'</strong><small>'+esc(item.label||'Seguimiento')+'</small></span>'+
    '<span class="v252-arrow">›</span>'+
  '</button>';
}

function renderCoachPriorityCenterV252(){
  const host=el('v252PriorityCenter');if(!host)return;
  const urgent=coachPriorityRowsV252('urgent');
  const today=coachPriorityRowsV252('today');
  const watch=coachPriorityRowsV252('watch');

  const column=(title,cls,rows,empty)=>
    '<div class="v252-column '+cls+'">'+
      '<div class="v252-column-head"><strong>'+esc(title)+'</strong><span>'+rows.length+'</span></div>'+
      '<div class="v252-column-body">'+
        (rows.length?rows.slice(0,4).map(priorityPersonV252).join(''):'<div class="v252-empty">'+esc(empty)+'</div>')+
      '</div>'+
    '</div>';

  host.innerHTML=
    '<div class="v252-priority-head">'+
      '<div><div class="v225-section-kicker">CENTRO DE PRIORIDADES</div><h3>Qué necesita atención ahora</h3>'+
      '<p>La app agrupa señales para que no tengas que revisar alumno por alumno.</p></div>'+
      '<button class="btn small primary" onclick="openNextCoachPriorityV236()">Siguiente prioridad</button>'+
    '</div>'+
    '<div class="v252-columns">'+
      column('Urgente','urgent',urgent,'Sin urgencias ahora')+
      column('Hoy','today',today,'Nada pendiente para hoy')+
      column('Seguimiento','watch',watch,'Sin alumnos en seguimiento')+
    '</div>';
}

"""
html=html.replace(anchor,helpers+anchor,1)

# Hydration: refresh center after feed data arrives.
hydrate_anchor="""    renderCoachFocusV235();
    decorateCoachReviewStateV238();"""
hydrate_repl="""    renderCoachFocusV235();
    renderCoachPriorityCenterV252();
    decorateCoachReviewStateV238();"""
if html.count(hydrate_anchor)!=1:
    raise RuntimeError("V20.52 hydrate anchor mismatch")
html=html.replace(hydrate_anchor,hydrate_repl,1)

# Dashboard: insert the new priority center immediately before the canonical dashboard grid.
grid_anchor='  <div class="grid v225-dashboard-grid">'
priority_section="""  <section class="card v252-priority-card" id="v252PriorityCenter">
    <div class="empty">Preparando prioridades…</div>
  </section>

  <div class="grid v225-dashboard-grid">"""
if html.count(grid_anchor)!=1:
    raise RuntimeError("V20.52 dashboard insertion mismatch: "+str(html.count(grid_anchor)))
html=html.replace(grid_anchor,priority_section,1)

# Initial render before async feed comes back.
initial_anchor="""  renderCoachStudentsV235();
  renderCoachFocusV235();
  hydrateCoachDashboardV80();"""
initial_repl="""  renderCoachStudentsV235();
  renderCoachFocusV235();
  renderCoachPriorityCenterV252();
  hydrateCoachDashboardV80();"""
if html.count(initial_anchor)!=1:
    raise RuntimeError("V20.52 initial render anchor mismatch")
html=html.replace(initial_anchor,initial_repl,1)

css=r"""
/* TEAM FJZ · V20.52 COACH PRIORITY CENTER */
.v252-priority-card{
  margin:0 0 14px;
  border-color:#30343c;
  background:
    linear-gradient(145deg,rgba(255,38,57,.035),transparent 42%),
    var(--card);
}
.v252-priority-head{
  display:flex;
  justify-content:space-between;
  gap:14px;
  align-items:flex-start;
  margin-bottom:12px;
}
.v252-priority-head h3{
  margin:4px 0 0;
  color:#f5f6f8;
  font-size:16px;
  font-weight:920;
  letter-spacing:-.02em;
}
.v252-priority-head p{
  margin:5px 0 0;
  color:#959aa4;
  font-size:9px;
  line-height:1.45;
}
.v252-columns{
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:9px;
}
.v252-column{
  min-width:0;
  border:1px solid #2c3038;
  border-top:3px solid #6f7580;
  border-radius:0 12px 12px 12px;
  background:#0d0e12;
  overflow:hidden;
}
.v252-column.urgent{border-top-color:#ff4657}
.v252-column.today{border-top-color:#f2bd55}
.v252-column.watch{border-top-color:#67adff}
.v252-column-head{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:9px 10px;
  border-bottom:1px solid #262931;
}
.v252-column-head strong{
  color:#f0f1f3;
  font-size:10px;
  font-weight:900;
}
.v252-column-head span{
  min-width:22px;
  height:22px;
  display:grid;
  place-items:center;
  border:1px solid #343842;
  border-radius:999px;
  color:#b7bbc4;
  font-size:8px;
  font-weight:900;
}
.v252-column-body{
  display:grid;
}
.v252-person{
  appearance:none;
  width:100%;
  display:grid;
  grid-template-columns:32px minmax(0,1fr) auto;
  gap:8px;
  align-items:center;
  padding:9px 10px;
  border:0;
  border-bottom:1px solid #24272e;
  background:transparent;
  color:inherit;
  text-align:left;
  cursor:pointer;
}
.v252-person:last-child{border-bottom:0}
.v252-person:hover{background:#121419}
.v252-avatar{
  width:32px;height:32px;display:grid;place-items:center;
  border:1px solid #333741;border-radius:9px;
  background:#15171c;color:#f2f3f5;font-size:9px;font-weight:900
}
.v252-copy{min-width:0}
.v252-copy strong{
  display:block;color:#f0f1f3;font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis
}
.v252-copy small{
  display:block;margin-top:3px;color:#8f949e;font-size:8px;line-height:1.35;overflow-wrap:anywhere
}
.v252-arrow{color:#666c77;font-size:18px}
.v252-empty{
  padding:15px 10px;color:#747984;font-size:9px;line-height:1.4;text-align:center
}
@media(max-width:820px){
  .v252-columns{grid-template-columns:1fr}
}
@media(max-width:560px){
  .v252-priority-head{display:grid}
  .v252-priority-head>.btn{width:100%}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V20.52 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-coach-priority-center" content="20.52">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.52 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-coach-priority-center" content="20.52"',
    "coachPriorityStateV252","renderCoachPriorityCenterV252",
    "CENTRO DE PRIORIDADES","Qué necesita atención ahora",
    "Urgente","Seguimiento","openNextCoachPriorityV236"
]:
    if marker not in html:
        raise RuntimeError("V20.52 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.52 coach priority center")
print("V20.52 BEFORE:",before)
print("V20.52 AFTER:",after)
print("V20.52 urgent/today/watch operational queue added without new runtime topology")
