import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# V20.35 COACH WORKFLOW PRO
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
if before["styles"]!=1: raise RuntimeError("V20.35 stylesheet mismatch")

anchor="async function hydrateCoachDashboardV80(){"
if html.count(anchor)!=1: raise RuntimeError("V20.35 hydrate anchor mismatch")
helpers=r"""
let coachFeedV235=[];
let coachStudentFilterV235='all';

function coachDaysSinceV235(v){
  if(!v)return 999;
  const d=new Date(v);if(Number.isNaN(d.getTime()))return 999;
  return Math.max(0,Math.floor((Date.now()-d.getTime())/86400000));
}
function coachStateV235(s){
  const a=Number(adherence(s)||0),days=coachDaysSinceV235(s?.lastWorkout);
  return {a,days,review:statusFor(s)==='Revisar',low:a<70,inactive:days>=7};
}
function coachAthleteV235(s){try{return cloudAthletes?.get?.(s?.id)||null}catch(_e){return null}}
function coachPendingV235(s){
  const a=coachAthleteV235(s);if(!a)return 0;
  return coachFeedV235.filter(x=>x?.athlete_id===a.id).length;
}
function coachCriticalV235(s){
  const a=coachAthleteV235(s);if(!a)return 0;
  return coachFeedV235.filter(x=>x?.athlete_id===a.id&&x?.severity==='critical').length;
}
function coachFocusScoreV235(s){
  const o=coachStateV235(s);
  return coachCriticalV235(s)*8+coachPendingV235(s)*3+(o.review?5:0)+(o.low?3:0)+(o.inactive?2:0);
}
function coachFilteredStudentsV235(){
  const q=normalizeTextV70(el('studentSearch')?.value||'');
  return (state.students||[]).filter(s=>{
    if(q&&!normalizeTextV70(s.name||'').includes(q))return false;
    const o=coachStateV235(s);
    if(coachStudentFilterV235==='review')return o.review;
    if(coachStudentFilterV235==='low')return o.low;
    if(coachStudentFilterV235==='inactive')return o.inactive;
    return true;
  });
}
function decorateCoachAlertsV235(){
  const by=new Map();coachFeedV235.forEach(x=>by.set(x.athlete_id,(by.get(x.athlete_id)||0)+1));
  document.querySelectorAll('.student-row[data-client-id]').forEach(row=>{
    row.querySelector('.v80-student-alert-count')?.remove();
    const a=cloudAthletes?.get?.(row.dataset.clientId),n=a?by.get(a.id)||0:0;
    if(n)row.querySelector('.student-main')?.insertAdjacentHTML('beforeend','<span class="v73-alert-badge v80-student-alert-count">'+n+'</span>');
  });
}
function renderCoachStudentsV235(){
  const h=el('studentList');if(!h)return;
  const rows=coachFilteredStudentsV235();
  h.innerHTML=rows.length?studentRows(rows):'<div class="empty">No hay alumnos en este filtro.</div>';
  document.querySelectorAll('[data-v235-filter]').forEach(b=>b.classList.toggle('active',b.dataset.v235Filter===coachStudentFilterV235));
  const n=el('v235StudentCount');if(n)n.textContent=rows.length;
  decorateCoachAlertsV235();
}
window.setCoachStudentFilterV235=function(k){coachStudentFilterV235=k||'all';renderCoachStudentsV235()};
window.openCoachStudentTabV235=function(id,tab){
  state.selectedStudentId=id;saveState();coachTab='student';coachStudentTab=tab||'summary';render();
};
function renderCoachFocusV235(){
  const h=el('v235CoachFocus');if(!h)return;
  const rows=(state.students||[]).map(s=>({s,score:coachFocusScoreV235(s)}))
    .filter(x=>x.score>0).sort((a,b)=>b.score-a.score).slice(0,5);
  h.innerHTML=rows.length?rows.map(({s,score})=>{
    const o=coachStateV235(s),bits=[];
    if(coachCriticalV235(s))bits.push(coachCriticalV235(s)+' prioridad alta');
    else if(coachPendingV235(s))bits.push(coachPendingV235(s)+' pendientes');
    if(o.review)bits.push('revisar');
    if(o.low)bits.push('adherencia '+o.a+'%');
    if(o.inactive&&o.days<999)bits.push(o.days+' días sin entrenar');
    return '<div class="v235-focus-item"><div><strong>'+esc(s.name)+'</strong><span>'+esc(bits.slice(0,2).join(' · ')||'Seguimiento')+'</span></div>'+
      '<b>'+score+'</b><div class="v235-focus-actions">'+
      '<button class="btn small primary" onclick="openCoachStudentTabV235(\''+s.id+'\',\'summary\')">Resumen</button>'+
      '<button class="btn small" onclick="openCoachStudentTabV235(\''+s.id+'\',\'routine\')">Rutina</button>'+
      '<button class="btn small" onclick="openCoachStudentTabV235(\''+s.id+'\',\'tracking\')">Check-in</button>'+
      '<button class="btn small" onclick="openCoachStudentTabV235(\''+s.id+'\',\'progress\')">Progreso</button></div></div>';
  }).join(''):'<div class="empty">No hay alumnos con señales prioritarias.</div>';
}
"""
html=html.replace(anchor,helpers+"\n"+anchor,1)

pat=re.compile(r"(async function hydrateCoachDashboardV80\(\)\{.*?)(\n\})\nfunction renderCoachDashboardV80",re.S)
m=pat.search(html)
if not m: raise RuntimeError("V20.35 hydrate block missing")
body=m.group(1)
if body.count("const feed=await loadCoachFeed(true);")!=1: raise RuntimeError("V20.35 feed call mismatch")
body=body.replace("const feed=await loadCoachFeed(true);","const feed=await loadCoachFeed(true);coachFeedV235=Array.isArray(feed)?feed:[];",1)
body=body.replace("    const byAthlete=new Map();","    renderCoachFocusV235();\n    const byAthlete=new Map();",1)
body=body.replace("  }catch(e){","  }catch(e){coachFeedV235=[];renderCoachFocusV235();",1)
html=html[:m.start(1)]+body+m.group(2)+"\nfunction renderCoachDashboardV80"+html[m.end():]

list_marker='<div class="student-list v225-student-list" id="studentList">${studentRows(students)}</div>'
if html.count(list_marker)!=1: raise RuntimeError("V20.35 student list marker mismatch")
filters=r"""<div class="v235-student-filters">
  <button class="btn small active" data-v235-filter="all" onclick="setCoachStudentFilterV235('all')">Todos</button>
  <button class="btn small" data-v235-filter="review" onclick="setCoachStudentFilterV235('review')">Revisar</button>
  <button class="btn small" data-v235-filter="low" onclick="setCoachStudentFilterV235('low')">Adherencia &lt;70</button>
  <button class="btn small" data-v235-filter="inactive" onclick="setCoachStudentFilterV235('inactive')">7+ días sin entrenar</button>
  <span class="badge blue" id="v235StudentCount">${students.length}</span>
</div>"""
html=html.replace(list_marker,filters+"\n        "+list_marker,1)

flow_pat=re.compile(r'<section class="card v225-flow-card">.*?</section>',re.S)
fm=list(flow_pat.finditer(html))
if len(fm)!=1: raise RuntimeError("V20.35 flow card mismatch: "+str(len(fm)))
focus=r"""<section class="card v235-focus-card">
  <div class="v225-section-kicker">ALUMNOS EN FOCO</div>
  <div class="section-title"><div><h3>Qué revisar primero</h3><div class="muted tiny">Ordenado por alertas, adherencia, revisión e inactividad.</div></div></div>
  <div id="v235CoachFocus"><div class="empty">Preparando prioridades…</div></div>
</section>"""
html=html[:fm[0].start()]+focus+html[fm[0].end():]

old_search="""  if(search)search.oninput=e=>{
    const q=normalizeTextV70(e.target.value);
    el('studentList').innerHTML=studentRows(students.filter(s=>normalizeTextV70(s.name).includes(q)));
    hydrateCoachDashboardV80()
  };
  hydrateCoachDashboardV80();"""
new_search="""  if(search)search.oninput=()=>renderCoachStudentsV235();
  renderCoachStudentsV235();
  renderCoachFocusV235();
  hydrateCoachDashboardV80();"""
if html.count(old_search)!=1: raise RuntimeError("V20.35 search block mismatch")
html=html.replace(old_search,new_search,1)

css=r"""
/* TEAM FJZ · V20.35 COACH WORKFLOW PRO */
.v235-student-filters{display:flex;gap:7px;flex-wrap:wrap;align-items:center;margin:10px 0 13px}
.v235-student-filters .btn.active{color:#fff;border-color:var(--red-border);background:var(--red-soft)}
.v235-focus-card{border-color:#30343a;background:linear-gradient(145deg,rgba(255,38,57,.055),transparent 48%),var(--card)}
#v235CoachFocus{display:grid;gap:8px}
.v235-focus-item{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;padding:11px;border:1px solid #2d3038;border-left:3px solid #f2bd55;border-radius:13px;background:#0d0e12}
.v235-focus-item strong{display:block;color:#f5f6f8;font-size:12px}
.v235-focus-item span{display:block;margin-top:4px;color:#969aa5;font-size:9px;line-height:1.4}
.v235-focus-item>b{color:#ff7985;font-size:11px}
.v235-focus-actions{grid-column:1/-1;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:5px}
.v235-focus-actions .btn{min-width:0;min-height:29px;padding:5px 4px;font-size:9px}
.v235-student-list .v80-student-alert-count{animation:none!important}
@media(max-width:560px){
  .v235-student-filters{display:grid;grid-template-columns:1fr 1fr}
  .v235-student-filters .badge{grid-column:1/-1;justify-self:start}
  .v235-focus-actions{grid-template-columns:1fr 1fr}
}
"""
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V20.35 stylesheet surface changed")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-coach-workflow" content="20.35">\n</head>',1)

after=metrics(html)
for k in ("styles","renders","channels","timeouts","rafs","listeners"):
    if after[k]!=before[k]: raise RuntimeError("V20.35 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-coach-workflow" content="20.35"',
    "setCoachStudentFilterV235","renderCoachStudentsV235","renderCoachFocusV235",
    "openCoachStudentTabV235","v235CoachFocus","v235-student-filters",
    "loadCoachFeed(true)","openAttentionV80","v122FollowupPaymentsRuntime"
]:
    if marker not in html: raise RuntimeError("V20.35 missing "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.35 coach workflow pro")
print("V20.35 BEFORE:",before)
print("V20.35 AFTER:",after)
print("V20.35 coach filters/focus/direct shortcuts added; runtime topology unchanged")
