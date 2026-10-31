import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "intervals":len(re.findall(r"setInterval\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

before=metrics(html)

for marker in [
    'meta name="fjz-comments-pending-inbox" content="21.30"',
    'id="v278SmartAlertsProgressRuntime"',
    'id="v302ReviewResolutionAuthorityRuntime"',
    "specificProgressAlerts:true",
    "firstReviewCardsDisabledV327:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.31 prerequisite missing "+marker)

css=r"""
/* =========================================================
   TEAM FJZ · V21.31 PROFESSIONAL GROUPED ALERTS
   ========================================================= */
.v331-alert-groups{
  display:grid;
  gap:10px;
}
.v331-alert-group{
  min-width:0;
  overflow:hidden;
  border:1px solid #2b2f36;
  border-radius:14px;
  background:
    linear-gradient(180deg,rgba(255,255,255,.018),transparent 35%),
    #0c0d11;
}
.v331-alert-group.critical{border-left:3px solid #ff5262}
.v331-alert-group.warning{border-left:3px solid #f2bd55}
.v331-alert-group.success{border-left:3px solid #3bd58a}
.v331-alert-group.info{border-left:3px solid #67adff}
.v331-alert-group-head{
  display:flex;
  justify-content:space-between;
  gap:12px;
  align-items:flex-start;
  padding:12px 13px 10px;
  border-bottom:1px solid rgba(255,255,255,.055);
  background:rgba(255,255,255,.012);
}
.v331-alert-group-head.v333-alert-group-toggle{
  width:100%;
  margin:0;
  border-top:0;
  border-left:0;
  border-right:0;
  border-radius:0;
  font:inherit;
  color:inherit;
  text-align:left;
  cursor:pointer;
  appearance:none;
  -webkit-appearance:none;
}
.v331-alert-group-head.v333-alert-group-toggle:hover{
  background:rgba(255,255,255,.026);
}
.v331-alert-group-head.v333-alert-group-toggle:focus-visible{
  outline:2px solid rgba(103,173,255,.48);
  outline-offset:-2px;
}
.v331-alert-list[hidden]{display:none!important}
.v333-alert-chevron{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  width:22px;
  height:22px;
  border:1px solid #30353d;
  border-radius:999px;
  color:#b8bec7;
  background:#11141a;
  font-size:13px;
  line-height:1;
  transition:transform .16s ease;
}
.v331-alert-group.v333-open .v333-alert-chevron{transform:rotate(180deg)}
.v331-alert-student{
  min-width:0;
}
.v331-alert-student>strong{
  display:block;
  color:#f3f4f6;
  font-size:12px;
  line-height:1.25;
  overflow-wrap:anywhere;
}
.v331-alert-student>span{
  display:block;
  margin-top:4px;
  color:#7f8792;
  font-size:8px;
  line-height:1.35;
}
.v331-alert-group-badges{
  display:flex;
  flex-wrap:wrap;
  justify-content:flex-end;
  gap:5px;
  flex:0 0 auto;
}
.v331-alert-count,
.v331-alert-positive,
.v331-alert-review{
  display:inline-flex;
  align-items:center;
  min-height:22px;
  padding:3px 7px;
  border:1px solid #30353d;
  border-radius:999px;
  font-size:7px;
  font-weight:900;
  white-space:nowrap;
}
.v331-alert-count{color:#c6cad1;background:#12151a}
.v331-alert-positive{color:#79dfa7;border-color:rgba(59,213,138,.25);background:rgba(59,213,138,.05)}
.v331-alert-review{color:#f0c96c;border-color:rgba(242,189,85,.25);background:rgba(242,189,85,.05)}
.v331-alert-list{
  display:grid;
}
.v331-alert-row{
  min-width:0;
  display:grid;
  grid-template-columns:minmax(0,1fr) auto;
  gap:10px;
  align-items:center;
  padding:11px 13px;
  border-top:1px solid rgba(255,255,255,.045);
}
.v331-alert-row:first-child{border-top:0}
.v331-alert-row:hover{background:rgba(255,255,255,.016)}
.v331-alert-copy{
  min-width:0;
}
.v331-alert-label{
  display:flex;
  flex-wrap:wrap;
  gap:6px;
  align-items:center;
  color:#9aa2ad;
  font-size:7px;
  font-weight:900;
  letter-spacing:.055em;
  text-transform:uppercase;
}
.v331-alert-dot{
  width:6px;
  height:6px;
  border-radius:50%;
  background:#67adff;
}
.v331-alert-row.success .v331-alert-dot{background:#3bd58a}
.v331-alert-row.warning .v331-alert-dot{background:#f2bd55}
.v331-alert-row.critical .v331-alert-dot{background:#ff5262}
.v331-alert-main{
  display:flex;
  flex-wrap:wrap;
  gap:7px;
  align-items:baseline;
  margin-top:5px;
}
.v331-alert-main strong{
  min-width:0;
  color:#f1f3f5;
  font-size:11px;
  line-height:1.3;
  overflow-wrap:anywhere;
}
.v331-alert-main b{
  color:#d9dde3;
  font-size:11px;
  font-variant-numeric:tabular-nums;
}
.v331-alert-compare{
  margin-top:5px;
  color:#8f97a2;
  font-size:8px;
  line-height:1.45;
  overflow-wrap:anywhere;
}
.v331-alert-note{
  margin-top:4px;
  color:#747c87;
  font-size:7.5px;
  line-height:1.4;
}
.v331-alert-actions{
  display:flex;
  gap:6px;
  align-items:center;
}
.v331-alert-actions .btn{
  min-width:58px;
}
.v331-smart-dashboard .v331-alert-row{
  grid-template-columns:minmax(0,1fr) auto;
}
.v331-smart-dashboard .v331-alert-note{
  display:none;
}
.v331-empty{
  padding:16px 12px;
  border:1px dashed #2d323a;
  border-radius:12px;
  color:#848c97;
  font-size:9px;
  text-align:center;
}
@media(max-width:640px){
  .v331-alert-group-head{
    display:grid;
    grid-template-columns:minmax(0,1fr);
  }
  .v331-alert-group-badges{
    justify-content:flex-start;
  }
  .v331-alert-row,
  .v331-smart-dashboard .v331-alert-row{
    grid-template-columns:minmax(0,1fr);
  }
  .v331-alert-actions{
    width:100%;
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
  }
  .v331-alert-actions .btn{
    width:100%;
    min-width:0;
  }
}
@media(max-width:390px){
  .v331-alert-main{
    display:grid;
    grid-template-columns:1fr;
    gap:3px;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V21.31 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

runtime=r"""
<script id="v331ProfessionalAlertGroupingRuntime">
(function(){
  const VERSION='21.31';
  const rank={critical:4,warning:3,success:2,info:1};

  function safe(v){
    try{return typeof esc==='function'?esc(String(v??'')):String(v??'')
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/"/g,'&quot;').replace(/'/g,'&#39;')}catch(_e){return ''}
  }
  function js(v){
    return String(v??'').replace(/\\/g,'\\\\').replace(/'/g,"\\'");
  }
  function ms(v){
    const n=Date.parse(v||0);return Number.isFinite(n)?n:0;
  }
  function athleteKey(x){
    return String(x?.athlete_id||x?.client_id||x?.student_id||x?.athlete_name||x?.event_key||'unknown-alert');
  }
  function isWeight(x){
    const sm=x?.smart_meta||{};
    return /:weight:/i.test(String(x?.event_key||''))||/^peso\b/i.test(String(sm.type_label||''))||/^peso\b/i.test(String(x?.title||''));
  }
  function category(x){
    const sm=x?.smart_meta||{},metric=String(sm.metric||'').toLowerCase();
    if(isWeight(x))return 'PESO CORPORAL';
    if(sm.exercise){
      if(metric==='load')return 'CARGA';
      if(metric==='reps')return 'REPETICIONES';
      if(metric.includes('volume'))return 'VOLUMEN';
      if(metric.includes('rir')||metric==='fatigue')return 'RIR';
      return 'RENDIMIENTO';
    }
    if(x?.kind==='training'||/^adherencia/i.test(String(sm.type_label||'')))return 'ADHERENCIA';
    if(x?.kind==='nutrition')return 'NUTRICIÓN';
    if(x?.kind==='checkin'||x?.kind==='wellness')return 'CHECK-IN';
    if(x?.kind==='exercise_feedback')return 'COMENTARIO';
    const fallback=(typeof attentionKindLabelV80==='function'?attentionKindLabelV80(x?.kind):'ALERTA');
    return String(sm.type_label||fallback||'ALERTA').toUpperCase();
  }
  function title(x){
    const sm=x?.smart_meta||{},metric=String(sm.metric||'').toLowerCase();
    if(isWeight(x))return 'Peso corporal';
    if(sm.exercise){
      const labels={load:'Carga',reps:'Repeticiones',volume:'Volumen','volume-down':'Volumen','high-rir':'RIR alto',fatigue:'Posible fatiga','rir-reserve':'RIR','rir-demand':'RIR'};
      return sm.exercise+(labels[metric]?' · '+labels[metric]:'');
    }
    if(x?.kind==='training'&&/^adherencia/i.test(String(sm.type_label||'')))return 'Adherencia semanal';
    if(x?.kind==='nutrition')return 'Registro nutricional';
    return x?.title||'Alerta';
  }
  function mainMetric(x){
    const sm=x?.smart_meta||{};
    if(isWeight(x))return sm.current||'';
    if(x?.kind==='training'&&/^adherencia/i.test(String(sm.type_label||'')))return sm.current||'';
    if(x?.kind==='nutrition')return sm.current||'';
    return sm.current||sm.delta||'';
  }
  function comparison(x){
    const sm=x?.smart_meta||{};
    const prev=sm.previous,current=sm.current,delta=sm.delta,period=sm.period;
    if(isWeight(x)){
      const parts=[];
      if(prev&&current)parts.push(prev+' → '+current);
      if(delta)parts.push(delta);
      if(period)parts.push(period);
      return parts.join(' · ');
    }
    if(x?.kind==='training'&&/^adherencia/i.test(String(sm.type_label||''))){
      const parts=[];
      if(prev)parts.push('Plan: '+prev);
      if(current)parts.push('Realizado: '+current);
      if(period)parts.push(period);
      return parts.join(' · ');
    }
    if(x?.kind==='nutrition'){
      const parts=[];
      if(current)parts.push(current);
      if(period)parts.push(period);
      return parts.join(' · ');
    }
    const parts=[];
    if(prev&&current)parts.push(prev+' → '+current);
    if(delta&&delta!==current)parts.push(delta);
    if(period)parts.push(period);
    return parts.join(' · ')||String(x?.body||'');
  }
  function groupRows(rows){
    const map=new Map();
    (rows||[]).filter(Boolean).forEach(x=>{
      const key=athleteKey(x);
      if(!map.has(key))map.set(key,{key,name:x.athlete_name||'Alumno',athleteId:x.athlete_id||'',rows:[]});
      map.get(key).rows.push(x);
    });
    const groups=[...map.values()];
    groups.forEach(g=>{
      g.rows.sort((a,b)=>(rank[b?.severity]||0)-(rank[a?.severity]||0)||ms(b?.occurred_at)-ms(a?.occurred_at));
      g.severity=g.rows.reduce((best,x)=>(rank[x?.severity]||0)>(rank[best]||0)?x.severity:best,'info');
      g.positive=g.rows.filter(x=>x?.severity==='success').length;
      g.review=g.rows.filter(x=>x?.severity==='critical'||x?.severity==='warning').length;
      g.latest=Math.max(0,...g.rows.map(x=>ms(x?.occurred_at)));
    });
    groups.sort((a,b)=>(rank[b.severity]||0)-(rank[a.severity]||0)||b.latest-a.latest||a.name.localeCompare(b.name,'es'));
    return groups;
  }
  function rowHtml(x,{dismiss=false}={}){
    const sm=x?.smart_meta||{};
    const metric=mainMetric(x),compare=comparison(x),note=sm.suggestion||x?.body||'';
    return '<div class="v331-alert-row '+safe(x?.severity||'info')+'">'+
      '<div class="v331-alert-copy">'+
        '<div class="v331-alert-label"><i class="v331-alert-dot"></i><span>'+safe(category(x))+'</span></div>'+
        '<div class="v331-alert-main"><strong>'+safe(title(x))+'</strong>'+(metric?'<b>'+safe(metric)+'</b>':'')+'</div>'+
        (compare?'<div class="v331-alert-compare">'+safe(compare)+'</div>':'')+
        (note?'<div class="v331-alert-note">'+safe(note)+'</div>':'')+
      '</div>'+
      '<div class="v331-alert-actions">'+
        '<button class="btn small" onclick="window.__fjzOpenGroupedAlertV331(\''+js(x?.athlete_id)+'\',\''+js(x?.event_key)+'\',\''+js(x?.kind)+'\')">Ver</button>'+
        (dismiss?'<button class="btn ghost small" onclick="window.__fjzDismissGroupedAlertV331(\''+js(x?.event_key)+'\')">Ocultar</button>':'')+
      '</div>'+
    '</div>';
  }
  const alertGroupsOpenV333=window.__fjzAlertGroupsOpenV333 instanceof Set
    ?window.__fjzAlertGroupsOpenV333
    :new Set();
  window.__fjzAlertGroupsOpenV333=alertGroupsOpenV333;

  window.__fjzToggleAlertGroupV333=function(key){
    const k=String(key||'');
    if(!k)return;
    if(alertGroupsOpenV333.has(k))alertGroupsOpenV333.delete(k);
    else alertGroupsOpenV333.add(k);

    document.querySelectorAll('.v331-alert-group[data-v333-key]').forEach(node=>{
      if(String(node.dataset.v333Key||'')!==k)return;
      const open=alertGroupsOpenV333.has(k);
      node.classList.toggle('v333-open',open);
      const list=node.querySelector('.v331-alert-list');
      if(list)list.hidden=!open;
      const btn=node.querySelector('.v333-alert-group-toggle');
      if(btn)btn.setAttribute('aria-expanded',open?'true':'false');
    });
  };

  function groupHtml(g,{dismiss=false,limit=5}={}){
    const visible=g.rows.slice(0,limit),extra=Math.max(0,g.rows.length-visible.length);
    const open=alertGroupsOpenV333.has(String(g.key||''));
    return '<section class="v331-alert-group '+safe(g.severity)+' '+(open?'v333-open':'')+'" data-v333-key="'+safe(g.key)+'">'+
      '<button type="button" class="v331-alert-group-head v333-alert-group-toggle" aria-expanded="'+(open?'true':'false')+'" onclick="window.__fjzToggleAlertGroupV333(\''+js(g.key)+'\')">'+
        '<span class="v331-alert-student"><strong>'+safe(g.name)+'</strong><span>'+g.rows.length+' alerta'+(g.rows.length===1?'':'s')+' · Tocá para '+(open?'cerrar':'ver el detalle')+'</span></span>'+
        '<span class="v331-alert-group-badges">'+
          '<span class="v331-alert-count">'+g.rows.length+' cambio'+(g.rows.length===1?'':'s')+'</span>'+
          (g.positive?'<span class="v331-alert-positive">+'+g.positive+' mejora'+(g.positive===1?'':'s')+'</span>':'')+
          (g.review?'<span class="v331-alert-review">'+g.review+' revisar</span>':'')+
          '<span class="v333-alert-chevron" aria-hidden="true">⌄</span>'+
        '</span>'+
      '</button>'+
      '<div class="v331-alert-list" '+(open?'':'hidden')+'>'+visible.map(x=>rowHtml(x,{dismiss})).join('')+
        (extra?'<div class="v331-alert-row info"><div class="v331-alert-copy"><div class="v331-alert-main"><strong>+'+extra+' señal'+(extra===1?'':'es')+' adicional'+(extra===1?'':'es')+'</strong></div><div class="v331-alert-compare">Abrí el alumno para ver todo el contexto.</div></div></div>':'')+
      '</div>'+
    '</section>';
  }

  window.__fjzOpenGroupedAlertV331=function(athleteId,eventKey,kind){
    if(typeof openAttentionV80==='function')return openAttentionV80(athleteId,eventKey,kind);
    if(typeof openCoachAlertV96==='function')return openCoachAlertV96(athleteId,eventKey,kind);
  };
  window.__fjzDismissGroupedAlertV331=async function(eventKey){
    if(typeof dismissFeed==='function')return dismissFeed(eventKey);
    if(typeof dismissCoachAlertV96==='function')return dismissCoachAlertV96(eventKey);
  };

  const groupedAttention=function(feed){
    const rows=typeof filteredAttentionV80==='function'?filteredAttentionV80(feed):(feed||[]);
    if(!rows.length)return '<div class="feed-empty">No hay elementos en este filtro.</div>';
    const groups=groupRows(rows);
    return '<div class="v331-alert-groups">'+groups.map(g=>groupHtml(g,{dismiss:true,limit:6})).join('')+'</div>';
  };
  window.renderAttentionItemsV80=groupedAttention;
  try{renderAttentionItemsV80=groupedAttention}catch(_e){}

  function ensureSmartHost(){
    let host=typeof el==='function'?el('v278DashboardSmartAlerts'):document.getElementById('v278DashboardSmartAlerts');
    if(host)return host;
    const section=document.createElement('section');
    section.id='v278DashboardSmartCard';
    section.className='card v278-dashboard-card';
    section.innerHTML=
      '<div class="section-title"><div><div class="v225-section-kicker">ALERTAS INTELIGENTES</div><h3>Resumen por alumno</h3>'+
      '<div class="muted tiny">Los cambios del mismo alumno aparecen juntos y con el dato concreto que cambió.</div></div><span class="badge blue">Smart</span></div>'+
      '<div id="v278DashboardSmartAlerts" class="v278-dashboard-smart v331-smart-dashboard"><div class="v331-empty">Analizando cambios específicos…</div></div>';
    const priority=typeof el==='function'?el('v252PriorityCenter'):document.getElementById('v252PriorityCenter');
    const view=typeof el==='function'?el('view'):document.getElementById('view');
    if(priority?.parentNode)priority.parentNode.insertBefore(section,priority);
    else if(view)view.prepend(section);
    return document.getElementById('v278DashboardSmartAlerts');
  }

  window.__fjzRenderPrioritySmartV278=async function(){
    if(!(currentProfile?.role==='coach'&&coachTab==='dashboard'))return;
    const host=ensureSmartHost();if(!host)return;
    try{
      const feed=await window.loadCoachFeed(false);
      const smart=(feed||[]).filter(x=>x?.smart_meta);
      if(!smart.length){
        host.innerHTML='<div class="v278-dashboard-smart-head"><strong>Resumen por alumno</strong><span>Sin cambios nuevos con datos suficientes</span></div>';
        return;
      }
      const groups=groupRows(smart).slice(0,6);
      const total=groups.reduce((n,g)=>n+g.rows.length,0);
      host.classList.add('v331-smart-dashboard');
      host.innerHTML='<div class="v278-dashboard-smart-head"><strong>'+groups.length+' alumno'+(groups.length===1?'':'s')+' con cambios</strong><span>'+total+' señal'+(total===1?'':'es')+' agrupada'+(total===1?'':'s')+'</span></div>'+
        '<div class="v331-alert-groups">'+groups.map(g=>groupHtml(g,{dismiss:false,limit:5})).join('')+'</div>';
    }catch(e){
      console.warn('TEAM FJZ V21.31 grouped smart alerts',e);
    }
  };

  window.__fjzV331={
    version:VERSION,
    professionalGroupedAlerts:true,
    alertsGroupedByAthlete:true,
    weightAlertShowsCurrentKg:true,
    weightAlertShowsPreviousToCurrent:true,
    weightAlertAvoidsPercentAsPrimaryMetric:true,
    adherenceShowsCompletedVsPlanned:true,
    nutritionShowsDaysNotPercentPrimary:true,
    exerciseAlertShowsConcreteMetric:true,
    dashboardSmartGrouped:true,
    attentionCenterGrouped:true,
    groupSeverityPrioritized:true,
    noExtraTimers:true,
    noExtraListeners:true,
    noExtraObservers:true,
    athleteAccordionAlertsV333:true,
    alertsCollapsedByDefaultV333:true,
    alertGroupToggleWithoutRerenderV333:true
  };
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-professional-grouped-alerts" content="21.31">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V21.31 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-professional-grouped-alerts" content="21.31"',
    'id="v331ProfessionalAlertGroupingRuntime"',
    "professionalGroupedAlerts:true",
    "alertsGroupedByAthlete:true",
    "weightAlertShowsCurrentKg:true",
    "weightAlertShowsPreviousToCurrent:true",
    "weightAlertAvoidsPercentAsPrimaryMetric:true",
    "adherenceShowsCompletedVsPlanned:true",
    "dashboardSmartGrouped:true",
    "attentionCenterGrouped:true",
    "groupSeverityPrioritized:true",
    "firstReviewCardsDisabledV327:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.31 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.31 professional grouped alerts")
print("V21.31 BEFORE:",before)
print("V21.31 AFTER:",after)
