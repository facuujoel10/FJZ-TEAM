import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# V20.36 COACH WORK QUEUE
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

for x in [
    'meta name="fjz-coach-workflow" content="20.35"',
    "coachFilteredStudentsV235","coachFocusScoreV235",
    "openCoachStudentTabV235","v235CoachFocus"
]:
    if x not in html:
        raise RuntimeError("V20.36 missing V20.35 authority: "+x)

state_anchor="let coachStudentFilterV235='all';"
if html.count(state_anchor)!=1:
    raise RuntimeError("V20.36 state anchor mismatch")
html=html.replace(state_anchor,state_anchor+"\nlet coachStudentSortV236='priority';",1)

old_filter="""function coachFilteredStudentsV235(){
  const q=normalizeTextV70(el('studentSearch')?.value||'');
  return (state.students||[]).filter(s=>{
    if(q&&!normalizeTextV70(s.name||'').includes(q))return false;
    const o=coachStateV235(s);
    if(coachStudentFilterV235==='review')return o.review;
    if(coachStudentFilterV235==='low')return o.low;
    if(coachStudentFilterV235==='inactive')return o.inactive;
    return true;
  });
}"""

new_filter="""function coachFilteredStudentsV235(){
  const q=normalizeTextV70(el('studentSearch')?.value||'');
  const rows=(state.students||[]).filter(s=>{
    if(q&&!normalizeTextV70(s.name||'').includes(q))return false;
    const o=coachStateV235(s);
    if(coachStudentFilterV235==='review')return o.review;
    if(coachStudentFilterV235==='low')return o.low;
    if(coachStudentFilterV235==='inactive')return o.inactive;
    return true;
  });
  rows.sort((a,b)=>{
    if(coachStudentSortV236==='adherence'){
      return Number(adherence(a)||0)-Number(adherence(b)||0)||
        String(a.name||'').localeCompare(String(b.name||''));
    }
    if(coachStudentSortV236==='last'){
      return coachDaysSinceV235(b?.lastWorkout)-coachDaysSinceV235(a?.lastWorkout)||
        String(a.name||'').localeCompare(String(b.name||''));
    }
    if(coachStudentSortV236==='name'){
      return String(a.name||'').localeCompare(String(b.name||''));
    }
    return coachFocusScoreV235(b)-coachFocusScoreV235(a)||
      Number(adherence(a)||0)-Number(adherence(b)||0)||
      String(a.name||'').localeCompare(String(b.name||''));
  });
  return rows;
}"""

if html.count(old_filter)!=1:
    raise RuntimeError("V20.36 filter function mismatch")
html=html.replace(old_filter,new_filter,1)

filter_action="window.setCoachStudentFilterV235=function(k){coachStudentFilterV235=k||'all';renderCoachStudentsV235()};"
if html.count(filter_action)!=1:
    raise RuntimeError("V20.36 filter action mismatch")

queue_logic="""
window.setCoachStudentSortV236=function(k){
  coachStudentSortV236=['priority','adherence','last','name'].includes(k)?k:'priority';
  renderCoachStudentsV235();
};

function coachBestTabV236(s){
  const ath=coachAthleteV235(s);
  if(!ath)return 'summary';
  const feed=(coachFeedV235||[]).filter(x=>x?.athlete_id===ath.id);
  if(!feed.length)return 'summary';
  const rank={critical:4,warning:3,info:2,success:1};
  feed.sort((a,b)=>(rank[b?.severity]||0)-(rank[a?.severity]||0));
  const top=feed[0];
  if(top?.kind==='exercise_feedback'||top?.kind==='training')return 'routine';
  if(top?.kind==='checkin'||top?.kind==='wellness')return 'tracking';
  if(top?.kind==='nutrition')return 'nutrition';
  if(top?.kind==='progression')return 'progress';
  return 'summary';
}

window.openNextCoachPriorityV236=function(){
  const ranked=(state.students||[])
    .map(s=>({s,score:coachFocusScoreV235(s)}))
    .filter(x=>x.score>0)
    .sort((a,b)=>b.score-a.score||
      Number(adherence(a.s)||0)-Number(adherence(b.s)||0));
  if(!ranked.length){
    toast?.('No hay prioridades pendientes ahora');
    return;
  }
  const s=ranked[0].s;
  openCoachStudentTabV235(s.id,coachBestTabV236(s));
};
"""
html=html.replace(filter_action,filter_action+"\n"+queue_logic,1)

student_expr="$"+"{students.length}"
filter_old='  <span class="badge blue" id="v235StudentCount">'+student_expr+'</span>\n</div>'
filter_new='  <span class="badge blue" id="v235StudentCount">'+student_expr+'</span>\n'+"""  <label class="v236-sort">
    <span>Ordenar</span>
    <select class="input" onchange="setCoachStudentSortV236(this.value)">
      <option value="priority">Prioridad</option>
      <option value="adherence">Menor adherencia</option>
      <option value="last">Más días sin entrenar</option>
      <option value="name">Nombre</option>
    </select>
  </label>
</div>"""
if html.count(filter_old)!=1:
    raise RuntimeError("V20.36 filter bar mismatch: "+str(html.count(filter_old)))
html=html.replace(filter_old,filter_new,1)

focus_old="""  <div class="section-title"><div><h3>Qué revisar primero</h3><div class="muted tiny">Ordenado por alertas, adherencia, revisión e inactividad.</div></div></div>
  <div id="v235CoachFocus">"""
focus_new="""  <div class="section-title v236-focus-head">
    <div><h3>Qué revisar primero</h3><div class="muted tiny">Ordenado por alertas, adherencia, revisión e inactividad.</div></div>
    <button class="btn small primary" onclick="openNextCoachPriorityV236()">Siguiente prioridad</button>
  </div>
  <div id="v235CoachFocus">"""
if html.count(focus_old)!=1:
    raise RuntimeError("V20.36 focus head mismatch")
html=html.replace(focus_old,focus_new,1)

css="""
/* TEAM FJZ · V20.36 COACH WORK QUEUE */
.v236-sort{display:flex;align-items:center;gap:7px;margin-left:auto;color:#8f939e;font-size:9px;font-weight:800;letter-spacing:.04em;text-transform:uppercase}
.v236-sort .input{width:auto;min-width:145px;min-height:31px;padding:5px 28px 5px 9px;font-size:10px;text-transform:none;letter-spacing:0}
.v236-focus-head{align-items:flex-start}
.v236-focus-head>.btn{flex:0 0 auto;min-height:32px}
@media(max-width:650px){
  .v236-sort{grid-column:1/-1;width:100%;margin-left:0;justify-content:space-between}
  .v236-sort .input{flex:1;max-width:210px}
  .v236-focus-head{display:grid;gap:9px}
  .v236-focus-head>.btn{width:100%}
}
"""
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.36 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-coach-work-queue" content="20.36">\n</head>',1)

after=metrics(html)
for k in ("styles","renders","channels","timeouts","rafs","listeners"):
    if after[k]!=before[k]:
        raise RuntimeError("V20.36 topology changed "+k+": "+repr({"before":before,"after":after}))

for x in [
    'meta name="fjz-coach-work-queue" content="20.36"',
    "coachStudentSortV236","setCoachStudentSortV236","coachBestTabV236",
    "openNextCoachPriorityV236","Siguiente prioridad",
    "Menor adherencia","Más días sin entrenar","v122FollowupPaymentsRuntime"
]:
    if x not in html:
        raise RuntimeError("V20.36 missing marker: "+x)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.36 coach work queue")
print("V20.36 BEFORE:",before)
print("V20.36 AFTER:",after)
print("V20.36 sort + next-priority workflow added; topology unchanged")
