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

def edit_script(doc,script_id,transform):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.78 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.78 no changes in "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-final-save-geometry" content="20.77"',
    'id="v96AlertCenterRuntime"',
    'id="v175ProfileAgendaCoachCenterRuntime"',
    "exercisePerformanceProgress:true",
    "progressPulseFourWeeks:true",
    "premiumCoachMobileHud:true",
]:
    if marker not in html:
        raise RuntimeError("V20.78 prerequisite missing "+marker)

# Make the existing alert center understand rich smart-alert metadata while
# preserving its read/dismiss/feed-state authority.
def patch_v96(body):
    card_pat=re.compile(
        r"  function coachAlertCardV96\(x\)\{.*?\n  \}\n  function renderCoachAlertsV96",
        re.S
    )
    m=card_pat.search(body)
    if not m:
        raise RuntimeError("V20.78 coachAlertCardV96 anchor missing")

    replacement=r"""  function coachAlertCardV96(x){
    const sm=x?.smart_meta||null;
    const detail=sm
      ?'<div class="v278-alert-detail">'+
        (sm.exercise?'<div class="v278-alert-exercise">'+esc(sm.exercise)+'</div>':'')+
        ((sm.previous!=null||sm.current!=null||sm.delta!=null)
          ?'<div class="v278-alert-delta">'+
            '<div><span>Anterior</span><strong>'+esc(sm.previous??'—')+'</strong></div>'+
            '<div><span>Actual</span><strong>'+esc(sm.current??'—')+'</strong></div>'+
            '<div><span>Cambio</span><strong>'+esc(sm.delta??'—')+'</strong></div>'+
           '</div>'
          :'')+
        (sm.period?'<div class="v278-alert-period">'+esc(sm.period)+'</div>':'')+
        (sm.suggestion?'<div class="v278-alert-suggestion"><strong>Sugerencia</strong><span>'+esc(sm.suggestion)+'</span></div>':'')+
       '</div>'
      :'';
    const actionLabel=sm?.action_label||'Abrir';
    return '<div class="v96-alert-card '+esc(x.severity||'info')+' '+(x.is_read?'':'unread')+' '+(sm?'v278-smart-alert':'')+'">'+
      '<div class="v96-alert-icon">'+esc(iconV96(x.kind))+'</div>'+
      '<div><div class="v96-alert-title">'+(!x.is_read?'<span class="unread-dot"></span>':'')+esc(x.athlete_name||'Alumno')+' · '+esc(x.title||'Aviso')+'</div>'+
      '<div class="v96-alert-meta">'+esc(sm?.type_label||labelV96(x.kind))+' · '+esc(relativeV96(x.occurred_at))+'</div>'+
      '<div class="v96-alert-body">'+esc(x.body||'')+'</div>'+detail+'</div>'+
      '<div class="v96-alert-actions"><button class="btn small" onclick="openCoachAlertV96(\''+x.athlete_id+'\',\''+escAttrV96(x.event_key)+'\',\''+escAttrV96(x.kind)+'\')">'+esc(actionLabel)+'</button>'+
      (!x.is_read?'<button class="btn ghost small" onclick="readCoachAlertV96(\''+escAttrV96(x.event_key)+'\')">Leído</button>':'')+
      '<button class="btn ghost small" onclick="dismissCoachAlertV96(\''+escAttrV96(x.event_key)+'\')">Ocultar</button></div></div>';
  }
  function renderCoachAlertsV96"""
    body=body[:m.start()]+replacement+body[m.end():]

    old_filters="[['all','Todas'],['priority','Prioridad'],['checkin','Check-ins'],['training','Entrenamiento'],['nutrition','Nutrición'],['exercise_feedback','Ejercicios']]"
    new_filters="[['all','Todas'],['priority','Prioridad'],['progression','Progreso'],['checkin','Check-ins'],['training','Entrenamiento'],['nutrition','Nutrición'],['exercise_feedback','Ejercicios']]"
    if old_filters in body:
        body=body.replace(old_filters,new_filters,1)

    body=body.replace(
        "<h3>Centro de alertas</h3><div class=\"muted tiny\">Lo que requiere tu atención, ordenado por prioridad.</div>",
        "<h3>Alertas inteligentes</h3><div class=\"muted tiny\">Cambios específicos de rendimiento, RIR, peso, adherencia y seguimiento.</div>",
        1
    )
    return body

html=edit_script(html,"v96AlertCenterRuntime",patch_v96)

# The current Coach dashboard uses the newer V8 attention center. Enrich that
# surface too so the Coach sees the same structured smart alert everywhere.
v80_pat=re.compile(
    r"function renderAttentionItemsV80\(feed\)\{.*?\n\}\nasync function hydrateCoachDashboardV80",
    re.S
)
v80_match=v80_pat.search(html)
if not v80_match:
    raise RuntimeError("V20.78 V80 attention renderer anchor missing")
v80_replacement=r"""function renderAttentionItemsV80(feed){
  const rows=filteredAttentionV80(feed);
  if(!rows.length)return '<div class="feed-empty">No hay elementos en este filtro.</div>';
  return '<div class="v80-attention">'+rows.slice(0,18).map(x=>{
    const sm=x?.smart_meta||null;
    const detail=sm
      ?'<div class="v278-alert-detail">'+
        (sm.exercise?'<div class="v278-alert-exercise">'+esc(sm.exercise)+'</div>':'')+
        ((sm.previous!=null||sm.current!=null||sm.delta!=null)
          ?'<div class="v278-alert-delta">'+
            '<div><span>Anterior</span><strong>'+esc(sm.previous??'—')+'</strong></div>'+
            '<div><span>Actual</span><strong>'+esc(sm.current??'—')+'</strong></div>'+
            '<div><span>Cambio</span><strong>'+esc(sm.delta??'—')+'</strong></div>'+
           '</div>'
          :'')+
        (sm.period?'<div class="v278-alert-period">'+esc(sm.period)+'</div>':'')+
        (sm.suggestion?'<div class="v278-alert-suggestion"><strong>Sugerencia</strong><span>'+esc(sm.suggestion)+'</span></div>':'')+
       '</div>'
      :'';
    return '<div class="v80-attention-item '+esc(x.severity||'info')+' '+(sm?'v278-smart-alert':'')+'">'+
      '<div class="v80-attention-head"><div><h4>'+esc(x.athlete_name)+' · '+esc(x.title)+'</h4>'+
      '<p class="muted tiny">'+esc(x.body||'')+'</p>'+detail+'</div>'+
      '<span class="badge '+(x.severity==='critical'?'red':x.severity==='warning'?'amber':x.severity==='success'?'green':'blue')+'">'+
      esc(sm?.type_label||attentionKindLabelV80(x.kind))+'</span></div>'+
      '<div class="v80-attention-actions">'+
      '<button class="btn small" onclick="openAttentionV80(\''+x.athlete_id+'\',\''+esc(x.event_key)+'\',\''+esc(x.kind)+'\')">'+esc(sm?.action_label||'Revisar')+'</button>'+
      '<button class="btn ghost small" onclick="dismissFeed(\''+esc(x.event_key)+'\')">Ocultar</button>'+
      '</div></div>';
  }).join('')+'</div>';
}
async function hydrateCoachDashboardV80"""
html=html[:v80_match.start()]+v80_replacement+html[v80_match.end():]

html=html.replace(
    "<div><h3>Centro de atención</h3><div class=\"muted tiny\">Ordena lo que requiere una decisión o revisión tuya.</div></div>",
    "<div><h3>Alertas inteligentes</h3><div class=\"muted tiny\">Cambios específicos de rendimiento, RIR, peso, adherencia y seguimiento.</div></div>",
    1
)
v80_filters_old="""      ['critical','Prioridad',critical],
      ['exercise_feedback','Comentarios',comments],"""
v80_filters_new="""      ['critical','Prioridad',critical],
      ['progression','Progreso',feed.filter(x=>x.kind==='progression').length],
      ['exercise_feedback','Comentarios',comments],"""
if v80_filters_old not in html:
    raise RuntimeError("V20.78 V80 filter anchor missing")
html=html.replace(v80_filters_old,v80_filters_new,1)

# Reuse the existing post-render authority instead of adding another render
# wrapper or MutationObserver.
def patch_v175(body):
    anchor="  function postRenderV175(){"
    if body.count(anchor)!=1:
        raise RuntimeError("V20.78 postRenderV175 anchor mismatch")
    body=body.replace(anchor,anchor+"\n    window.__fjzSmartPostRenderV278?.();",1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

css=r"""
/* =========================================================
   TEAM FJZ · V20.78 SMART ALERTS + PROFESSIONAL PROGRESS
   ========================================================= */
.v278-smart-alert{
  position:relative;
  overflow:hidden;
}
.v278-smart-alert.success{border-left-color:#3bd58a!important}
.v278-smart-alert.warning{border-left-color:#f2bd55!important}
.v278-smart-alert.critical{border-left-color:#ff5262!important}
.v278-smart-alert.info{border-left-color:#67adff!important}
.v278-alert-detail{
  display:grid;
  gap:7px;
  margin-top:8px;
  padding-top:8px;
  border-top:1px solid rgba(255,255,255,.055);
}
.v278-alert-exercise{
  color:#f3f5f7;
  font-size:10px;
  font-weight:900;
}
.v278-alert-delta{
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:6px;
}
.v278-alert-delta>div{
  min-width:0;
  padding:7px 8px;
  border:1px solid #292d34;
  border-radius:9px;
  background:#0b0c10;
}
.v278-alert-delta span{
  display:block;
  color:#777e89;
  font-size:6.5px;
  font-weight:900;
  letter-spacing:.07em;
  text-transform:uppercase;
}
.v278-alert-delta strong{
  display:block;
  margin-top:3px;
  color:#e9ebee;
  font-size:9px;
  font-variant-numeric:tabular-nums;
}
.v278-alert-period{
  color:#7f8791;
  font-size:7px;
}
.v278-alert-suggestion{
  display:flex;
  gap:7px;
  align-items:flex-start;
  padding:7px 8px;
  border:1px solid rgba(103,173,255,.14);
  border-radius:9px;
  background:rgba(103,173,255,.035);
}
.v278-alert-suggestion strong{
  flex:0 0 auto;
  color:#a9cdf9;
  font-size:7px;
  text-transform:uppercase;
  letter-spacing:.06em;
}
.v278-alert-suggestion span{
  color:#969da8;
  font-size:8px;
  line-height:1.35;
}

/* Selected-athlete intelligence summary. */
.v278-athlete-intel{
  margin-bottom:12px!important;
  border-color:rgba(255,70,87,.18)!important;
  background:
    radial-gradient(circle at 95% 0,rgba(255,46,64,.055),transparent 34%),
    #101116!important;
}
.v278-intel-grid{
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:7px;
  margin-top:10px;
}
.v278-intel-metric{
  min-width:0;
  padding:10px;
  border:1px solid #292d34;
  border-radius:11px;
  background:#0d0e12;
}
.v278-intel-metric span{
  display:block;
  color:#7e858f;
  font-size:7px;
  font-weight:900;
  letter-spacing:.07em;
  text-transform:uppercase;
}
.v278-intel-metric strong{
  display:block;
  margin-top:5px;
  color:#f3f5f7;
  font-size:16px;
  line-height:1.1;
  font-variant-numeric:tabular-nums;
}
.v278-intel-metric small{
  display:block;
  margin-top:4px;
  color:#858c96;
  font-size:7px;
  line-height:1.35;
}
.v278-mini-alerts{
  display:grid;
  gap:7px;
  margin-top:9px;
}
.v278-mini-alert{
  appearance:none;
  width:100%;
  min-width:0;
  display:grid;
  grid-template-columns:auto minmax(0,1fr) auto;
  gap:9px;
  align-items:center;
  padding:9px 10px;
  border:1px solid #292d34;
  border-radius:11px;
  background:#0d0e12;
  color:inherit;
  text-align:left;
  cursor:pointer;
}
.v278-mini-alert.success{border-left:3px solid #3bd58a}
.v278-mini-alert.warning{border-left:3px solid #f2bd55}
.v278-mini-alert.critical{border-left:3px solid #ff5262}
.v278-mini-alert.info{border-left:3px solid #67adff}
.v278-mini-alert>span:first-child{
  display:grid;
  place-items:center;
  width:27px;
  height:27px;
  border-radius:9px;
  background:#12141a;
  color:#b8bec8;
  font-size:12px;
}
.v278-mini-alert strong{display:block;font-size:9px;color:#f0f2f4}
.v278-mini-alert small{display:block;margin-top:3px;font-size:7.5px;color:#858c97;line-height:1.35}
.v278-mini-alert>span:last-child{color:#8f96a0;font-size:14px}

/* Professional progress workspace. */
.v278-progress{
  margin-bottom:13px!important;
  border-color:#30343c!important;
  background:
    linear-gradient(180deg,rgba(255,255,255,.014),transparent 30%),
    #0e0f13!important;
}
.v278-progress-head{
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  gap:12px;
}
.v278-progress-head h3{margin:0}
.v278-progress-head p{margin:4px 0 0}
.v278-weight-kpis,
.v278-perf-kpis{
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:7px;
  margin:11px 0 9px;
}
.v278-kpi{
  min-width:0;
  padding:9px 10px;
  border:1px solid #292d34;
  border-radius:10px;
  background:#0b0c10;
}
.v278-kpi span{
  display:block;
  color:#7d848f;
  font-size:6.5px;
  font-weight:900;
  letter-spacing:.07em;
  text-transform:uppercase;
}
.v278-kpi strong{
  display:block;
  margin-top:4px;
  color:#f4f5f7;
  font-size:14px;
  line-height:1.1;
  font-variant-numeric:tabular-nums;
}
.v278-kpi small{
  display:block;
  margin-top:4px;
  color:#7f8690;
  font-size:7px;
}
.v278-chart-shell{
  min-width:0;
  overflow:hidden;
  padding:10px;
  border:1px solid #292d34;
  border-radius:12px;
  background:#0a0b0e;
}
.v278-chart{
  display:block;
  width:100%;
  height:auto;
  min-height:190px;
  max-height:250px;
  overflow:visible;
}
.v278-gridline{stroke:rgba(255,255,255,.055);stroke-width:1}
.v278-axis-label{fill:#747b86;font-size:8px;font-family:system-ui,sans-serif}
.v278-line-main{
  fill:none;
  stroke:#ff4658;
  stroke-width:2.6;
  stroke-linecap:round;
  stroke-linejoin:round;
  vector-effect:non-scaling-stroke;
}
.v278-line-trend{
  fill:none;
  stroke:#a4aab4;
  stroke-width:1.5;
  stroke-dasharray:5 5;
  opacity:.72;
  vector-effect:non-scaling-stroke;
}
.v278-line-rir{
  fill:none;
  stroke:#67adff;
  stroke-width:2;
  stroke-linecap:round;
  stroke-linejoin:round;
  vector-effect:non-scaling-stroke;
}
.v278-point-main{
  fill:#ff4658;
  stroke:#0a0b0e;
  stroke-width:2;
  vector-effect:non-scaling-stroke;
}
.v278-point-rir{
  fill:#67adff;
  stroke:#0a0b0e;
  stroke-width:2;
  vector-effect:non-scaling-stroke;
}
.v278-target-line{
  stroke:#f2bd55;
  stroke-width:1.4;
  stroke-dasharray:7 5;
  opacity:.85;
  vector-effect:non-scaling-stroke;
}
.v278-chart-legend{
  display:flex;
  flex-wrap:wrap;
  gap:10px;
  margin-top:7px;
  color:#838a95;
  font-size:7.5px;
}
.v278-legend-dot{
  display:inline-block;
  width:8px;
  height:8px;
  margin-right:4px;
  border-radius:50%;
  background:#ff4658;
  vertical-align:-1px;
}
.v278-legend-dot.trend{background:#a4aab4}
.v278-legend-dot.rir{background:#67adff}
.v278-legend-dot.target{background:#f2bd55}

.v278-performance{
  margin-top:11px;
  padding-top:11px;
  border-top:1px solid #292d34;
}
.v278-controls{
  display:grid;
  grid-template-columns:minmax(0,1.3fr) minmax(120px,.7fr);
  gap:8px;
  margin:9px 0;
}
.v278-controls select{
  min-width:0;
  width:100%;
  max-width:100%;
}
.v278-dual{
  margin-top:9px;
  padding-top:9px;
  border-top:1px solid #252930;
}
.v278-dual-head{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:8px;
  margin-bottom:7px;
}
.v278-dual-head strong{font-size:9px;color:#e6e8eb}
.v278-dual-head span{font-size:7px;color:#838a95}

.v278-adherence{
  margin-top:11px;
  padding-top:11px;
  border-top:1px solid #292d34;
}
.v278-adherence-grid{
  display:grid;
  grid-template-columns:minmax(0,1.4fr) repeat(2,minmax(0,.8fr));
  gap:8px;
  margin-top:8px;
}
.v278-week-bars{
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:6px;
  align-items:end;
  min-height:90px;
  padding:9px;
  border:1px solid #292d34;
  border-radius:11px;
  background:#0b0c10;
}
.v278-week{
  display:grid;
  gap:5px;
  align-items:end;
  height:70px;
}
.v278-week-bar{
  align-self:end;
  min-height:4px;
  border-radius:6px 6px 3px 3px;
  background:linear-gradient(180deg,#ff5363,#a7192a);
}
.v278-week span{
  color:#747b86;
  font-size:6.5px;
  text-align:center;
}
.v278-adherence-card{
  padding:10px;
  border:1px solid #292d34;
  border-radius:11px;
  background:#0b0c10;
}
.v278-adherence-card span{
  display:block;
  color:#7d848f;
  font-size:7px;
  text-transform:uppercase;
  font-weight:900;
  letter-spacing:.06em;
}
.v278-adherence-card strong{
  display:block;
  margin-top:6px;
  color:#f1f3f5;
  font-size:16px;
}
.v278-adherence-card small{
  display:block;
  margin-top:4px;
  color:#818893;
  font-size:7px;
  line-height:1.35;
}
.v278-empty{
  padding:20px 10px;
  text-align:center;
  color:#7e858f;
  font-size:9px;
}

@media(max-width:760px){
  .v278-intel-grid,
  .v278-weight-kpis,
  .v278-perf-kpis{
    grid-template-columns:repeat(2,minmax(0,1fr));
  }
  .v278-adherence-grid{grid-template-columns:1fr 1fr}
  .v278-week-bars{grid-column:1/-1}
}
@media(max-width:520px){
  .v278-alert-delta{grid-template-columns:1fr 1fr}
  .v278-alert-delta>div:last-child{grid-column:1/-1}
  .v278-controls{grid-template-columns:1fr}
  .v278-progress-head,
  .v278-dual-head{display:grid;grid-template-columns:1fr}
  .v278-chart{min-height:165px}
}
@media(max-width:390px){
  .v278-intel-grid,
  .v278-weight-kpis,
  .v278-perf-kpis,
  .v278-adherence-grid{
    grid-template-columns:1fr!important;
  }
  .v278-week-bars{grid-column:auto}
  .v278-mini-alert{grid-template-columns:auto minmax(0,1fr)}
  .v278-mini-alert>span:last-child{display:none}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.78 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

runtime=r"""
<script id="v278SmartAlertsProgressRuntime">
(function(){
  const VERSION='20.78';
  const DAY=86400000;
  let smartCloudCacheV278={at:0,weights:new Map(),nutritionDays:new Map(),nutritionPlans:new Map(),states:new Map()};
  let smartTrackingPromiseV278=null;
  let selectedExerciseV278='';
  let selectedMetricV278='load';

  function numV278(v){
    const n=Number(v);
    return Number.isFinite(n)?n:null;
  }
  function r1V278(v){
    const n=Number(v);
    return Number.isFinite(n)?Math.round(n*10)/10:null;
  }
  function fmtV278(v,d=1){
    const n=Number(v);
    if(!Number.isFinite(n))return '—';
    return n.toLocaleString('es-AR',{minimumFractionDigits:d,maximumFractionDigits:d});
  }
  function isoDayV278(v){
    if(!v)return '';
    const s=String(v);
    return s.length>=10?s.slice(0,10):s;
  }
  function dateMsV278(v){
    const t=Date.parse(v||0);
    return Number.isFinite(t)?t:0;
  }
  function daysBetweenV278(a,b){
    const x=dateMsV278(a),y=dateMsV278(b);
    return x&&y?Math.max(0,Math.round(Math.abs(y-x)/DAY)):0;
  }
  function dateAgoV278(days){
    const d=new Date(Date.now()-days*DAY);
    return d.toISOString().slice(0,10);
  }
  function weekKeyV278(date=new Date()){
    const d=new Date(date);
    d.setHours(12,0,0,0);
    const dow=(d.getDay()+6)%7;
    d.setDate(d.getDate()-dow);
    return d.toISOString().slice(0,10);
  }
  function normExerciseV278(name){
    try{
      if(typeof normalizeExerciseTextV65==='function')return normalizeExerciseTextV65(name);
    }catch(_e){}
    return String(name||'').trim().toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g,'')
      .replace(/[^a-z0-9]+/g,' ').trim();
  }
  function avgV278(arr){
    const xs=(arr||[]).map(Number).filter(Number.isFinite);
    return xs.length?xs.reduce((a,b)=>a+b,0)/xs.length:null;
  }
  function pctV278(a,b){
    return Number.isFinite(a)&&Number.isFinite(b)&&b!==0?(a-b)/b*100:null;
  }
  function athleteForStudentV278(s){
    try{return cloudAthletes?.get?.(s?.id)||null}catch(_e){return null}
  }
  function allStudentsV278(){
    return Array.isArray(state?.students)?state.students:[];
  }

  function setStatsV278(result){
    const valid=(result?.sets||[]).filter(Array.isArray).map(x=>({
      kg:numV278(x?.[0]),
      reps:numV278(x?.[1]),
      rir:numV278(x?.[2])
    })).filter(x=>Number.isFinite(x.reps)&&x.reps>0);
    if(!valid.length)return null;
    const weighted=valid.filter(x=>Number.isFinite(x.kg)&&x.kg>0);
    const best=weighted.slice().sort((a,b)=>b.kg-a.kg||b.reps-a.reps)[0]||null;
    return {
      setCount:valid.length,
      bestLoad:best?.kg??null,
      bestReps:best?.reps??Math.max(...valid.map(x=>x.reps)),
      totalReps:valid.reduce((a,x)=>a+x.reps,0),
      volume:weighted.reduce((a,x)=>a+x.kg*x.reps,0),
      avgRir:avgV278(valid.map(x=>x.rir).filter(Number.isFinite)),
      weighted:weighted.length>0
    };
  }

  function exerciseSeriesV278(s){
    const map=new Map();
    const muscleByName=new Map();
    (s?.days||[]).forEach(d=>(d?.exercises||[]).forEach(e=>{
      muscleByName.set(normExerciseV278(e?.name),e?.muscle||d?.muscles||'');
    }));
    (s?.sessions||[]).slice().sort((a,b)=>dateMsV278(a?.date)-dateMsV278(b?.date)).forEach(ss=>{
      (ss?.exerciseResults||[]).forEach(r=>{
        if(!r?.name)return;
        const stats=setStatsV278(r);if(!stats)return;
        const key=normExerciseV278(r.name);if(!key)return;
        if(!map.has(key))map.set(key,{key,name:r.name,muscle:muscleByName.get(key)||'',items:[]});
        map.get(key).items.push({date:ss.date,sessionId:ss.id,dayName:ss.dayName,...stats});
      });
    });
    return [...map.values()];
  }

  function compareExerciseV278(row,athleteId,athleteName){
    const items=row.items||[];
    if(items.length<2)return [];
    const cur=items[items.length-1],prev=items[items.length-2];
    const alerts=[];
    const loadDiff=(Number.isFinite(cur.bestLoad)&&Number.isFinite(prev.bestLoad))?cur.bestLoad-prev.bestLoad:null;
    const repsDiff=(Number.isFinite(cur.bestReps)&&Number.isFinite(prev.bestReps))?cur.bestReps-prev.bestReps:null;
    const rirDiff=(Number.isFinite(cur.avgRir)&&Number.isFinite(prev.avgRir))?cur.avgRir-prev.avgRir:null;
    const volPct=pctV278(cur.volume,prev.volume);
    const loadSimilar=loadDiff!=null&&(Math.abs(loadDiff)<=1||Math.abs(loadDiff)/Math.max(1,prev.bestLoad)<=.02);
    const repsSimilar=repsDiff!=null&&Math.abs(repsDiff)<=1;
    const rirSimilar=rirDiff==null||Math.abs(rirDiff)<=.75;
    const date=isoDayV278(cur.date);
    const encoded=encodeURIComponent(row.key);

    const make=(metric,severity,title,body,previous,current,delta,suggestion,typeLabel='Rendimiento')=>({
      athlete_id:athleteId,
      athlete_name:athleteName,
      title,
      body,
      severity,
      kind:'progression',
      occurred_at:cur.date||new Date().toISOString(),
      event_key:'smart:v278:exercise:'+athleteId+':'+encoded+':'+metric+':'+date,
      is_read:false,
      smart_meta:{
        type_label:typeLabel,
        exercise:row.name,
        previous,current,delta,
        period:'Comparación con la sesión anterior · '+fmtDate(cur.date),
        suggestion,
        action_label:'Ver rendimiento',
        exercise_key:row.key,
        metric
      }
    });

    const last2=items.slice(-2);
    const lowRirRepeated=last2.length===2&&last2.every(x=>Number.isFinite(x.avgRir)&&x.avgRir<=.75);
    const repsFalling=repsDiff!=null&&repsDiff<=-2;
    const volumeFalling=volPct!=null&&volPct<=-12;
    if(lowRirRepeated&&(repsFalling||volumeFalling)){
      alerts.push(make(
        'fatigue','critical',
        row.name+' · posible fatiga',
        'RIR muy bajo repetido junto con una caída de rendimiento.',
        'RIR '+fmtV278(prev.avgRir,1),
        'RIR '+fmtV278(cur.avgRir,1),
        repsFalling?(fmtV278(repsDiff,0)+' reps'):(fmtV278(volPct,0)+'% volumen'),
        'Revisar recuperación, técnica y carga antes de progresar.',
        'RIR · Atención'
      ));
      return alerts;
    }

    const last3=items.slice(-3);
    if(last3.length===3&&last3.every(x=>Number.isFinite(x.avgRir)&&x.avgRir>=3.5)){
      alerts.push(make(
        'high-rir','warning',
        row.name+' · RIR alto sostenido',
        'Tres sesiones con margen alto. Puede haber espacio para progresar si la técnica se mantiene.',
        'RIR '+fmtV278(last3[0].avgRir,1),
        'RIR '+fmtV278(cur.avgRir,1),
        '3 sesiones',
        'Evaluar un aumento de carga o repeticiones según el plan.',
        'RIR · Revisar'
      ));
      return alerts;
    }

    if(loadDiff!=null&&loadDiff>=Math.max(2,prev.bestLoad*.025)&&repsDiff!=null&&repsDiff>=-2&&rirSimilar){
      alerts.push(make(
        'load','success',
        row.name+' · carga +'+fmtV278(loadDiff,1)+' kg',
        'Subió la carga manteniendo repeticiones y un esfuerzo comparable.',
        fmtV278(prev.bestLoad,1)+' kg × '+fmtV278(prev.bestReps,0)+' · RIR '+fmtV278(prev.avgRir,1),
        fmtV278(cur.bestLoad,1)+' kg × '+fmtV278(cur.bestReps,0)+' · RIR '+fmtV278(cur.avgRir,1),
        '+'+fmtV278(loadDiff,1)+' kg',
        'Continuar la progresión actual si la ejecución sigue sólida.'
      ));
      return alerts;
    }

    if(loadSimilar&&repsDiff!=null&&repsDiff>=2&&rirSimilar){
      alerts.push(make(
        'reps','success',
        row.name+' · +'+fmtV278(repsDiff,0)+' reps',
        'Más repeticiones con una carga y un RIR comparables.',
        fmtV278(prev.bestLoad,1)+' kg × '+fmtV278(prev.bestReps,0)+' · RIR '+fmtV278(prev.avgRir,1),
        fmtV278(cur.bestLoad,1)+' kg × '+fmtV278(cur.bestReps,0)+' · RIR '+fmtV278(cur.avgRir,1),
        '+'+fmtV278(repsDiff,0)+' reps',
        'Mantener el criterio de progresión del ejercicio.'
      ));
      return alerts;
    }

    if(loadSimilar&&repsSimilar&&rirDiff!=null&&rirDiff>=1){
      alerts.push(make(
        'rir-reserve','success',
        row.name+' · mayor reserva',
        'Misma carga y repeticiones con un RIR mayor: el trabajo resultó menos exigente.',
        'RIR '+fmtV278(prev.avgRir,1),
        'RIR '+fmtV278(cur.avgRir,1),
        '+'+fmtV278(rirDiff,1)+' RIR',
        'Valorar progresión si coincide con la técnica y el objetivo.',
        'RIR · Progreso'
      ));
      return alerts;
    }

    if(loadSimilar&&repsSimilar&&rirDiff!=null&&rirDiff<=-1){
      alerts.push(make(
        'rir-demand','info',
        row.name+' · sesión más exigente',
        'Misma carga y repeticiones, pero con menos RIR. No se interpreta automáticamente como progreso.',
        'RIR '+fmtV278(prev.avgRir,1),
        'RIR '+fmtV278(cur.avgRir,1),
        fmtV278(rirDiff,1)+' RIR',
        'Observar recuperación y la próxima sesión antes de ajustar.',
        'RIR · Contexto'
      ));
      return alerts;
    }

    if(items.length>=4){
      const rec=items.slice(-2),old=items.slice(-4,-2);
      const recVol=avgV278(rec.map(x=>x.volume).filter(x=>x>0));
      const oldVol=avgV278(old.map(x=>x.volume).filter(x=>x>0));
      const blockPct=pctV278(recVol,oldVol);
      if(blockPct!=null&&blockPct>=15){
        alerts.push(make(
          'volume','success',
          row.name+' · volumen +'+fmtV278(blockPct,0)+'%',
          'El volumen medio de las últimas dos sesiones superó al bloque anterior.',
          fmtV278(oldVol,0)+' kg·rep',
          fmtV278(recVol,0)+' kg·rep',
          '+'+fmtV278(blockPct,0)+'%',
          'Confirmar que la mejora también sea compatible con RIR y recuperación.',
          'Volumen · Progreso'
        ));
      }else if(blockPct!=null&&blockPct<=-15){
        alerts.push(make(
          'volume-down','warning',
          row.name+' · volumen '+fmtV278(blockPct,0)+'%',
          'El volumen medio reciente cayó frente al bloque anterior.',
          fmtV278(oldVol,0)+' kg·rep',
          fmtV278(recVol,0)+' kg·rep',
          fmtV278(blockPct,0)+'%',
          'Revisar contexto, RIR, técnica y recuperación antes de cambiar el plan.',
          'Volumen · Revisar'
        ));
      }
    }
    return alerts;
  }

  function exerciseAlertsV278(s,athleteId,athleteName){
    const rank={critical:4,warning:3,success:2,info:1};
    const alerts=exerciseSeriesV278(s).flatMap(r=>compareExerciseV278(r,athleteId,athleteName));
    alerts.sort((a,b)=>(rank[b.severity]||0)-(rank[a.severity]||0)||dateMsV278(b.occurred_at)-dateMsV278(a.occurred_at));
    return alerts.slice(0,5);
  }

  function sessionDateV278(s){
    const rows=(s?.sessions||[]).filter(x=>dateMsV278(x?.date)).slice().sort((a,b)=>dateMsV278(b.date)-dateMsV278(a.date));
    return rows[0]?.date||s?.lastWorkout||null;
  }
  function adherenceAlertsV278(s,athleteId,athleteName){
    const out=[];
    const planned=Math.max(1,Number(s?.plannedPerWeek)||s?.days?.length||1);
    const since=Date.now()-7*DAY;
    const done=(s?.sessions||[]).filter(x=>dateMsV278(x?.date)>=since).length;
    const last=sessionDateV278(s);
    const idle=last?Math.floor((Date.now()-dateMsV278(last))/DAY):999;
    const wk=weekKeyV278();

    if(idle>=10){
      out.push({
        athlete_id:athleteId,athlete_name:athleteName,
        title:'Sin entrenamiento hace '+idle+' días',
        body:'No hay una sesión registrada reciente.',
        severity:'critical',kind:'training',occurred_at:last||new Date().toISOString(),
        event_key:'smart:v278:adherence:'+athleteId+':inactive:'+wk,
        is_read:false,
        smart_meta:{type_label:'Adherencia · Atención',previous:null,current:idle+' días',delta:'Sin registro',period:'Últimos '+idle+' días',suggestion:'Revisar disponibilidad, adherencia y contexto del alumno.',action_label:'Ver resumen'}
      });
    }else if(idle>=6){
      out.push({
        athlete_id:athleteId,athlete_name:athleteName,
        title:'Adherencia · '+idle+' días sin entrenar',
        body:'Conviene revisar si hubo cambios de horarios, recuperación o adherencia.',
        severity:'warning',kind:'training',occurred_at:last||new Date().toISOString(),
        event_key:'smart:v278:adherence:'+athleteId+':idle:'+wk,
        is_read:false,
        smart_meta:{type_label:'Adherencia · Revisar',previous:null,current:idle+' días',delta:'',period:'Semana actual',suggestion:'Confirmar contexto antes de ajustar la rutina.',action_label:'Ver resumen'}
      });
    }else if(planned>=2&&done>=planned){
      out.push({
        athlete_id:athleteId,athlete_name:athleteName,
        title:'Adherencia · '+done+'/'+planned+' entrenamientos',
        body:'Completó la frecuencia semanal programada.',
        severity:'success',kind:'training',occurred_at:last||new Date().toISOString(),
        event_key:'smart:v278:adherence:'+athleteId+':complete:'+wk,
        is_read:false,
        smart_meta:{type_label:'Adherencia · Positivo',previous:planned+' planificados',current:done+' realizados',delta:Math.round(done/planned*100)+'%',period:'Últimos 7 días',suggestion:'Mantener la estructura si recuperación y rendimiento acompañan.',action_label:'Ver resumen'}
      });
    }
    return out;
  }

  function normalizeWeightsV278(rows){
    const byDate=new Map();
    (rows||[]).forEach(x=>{
      const w=numV278(x?.weight_kg),d=isoDayV278(x?.date||x?.measured_on||x?.week_start);
      if(!Number.isFinite(w)||w<20||w>400||!d)return;
      const priority=x?.source==='measurement'?2:1;
      const prev=byDate.get(d);
      if(!prev||priority>=prev.priority)byDate.set(d,{date:d,weight:w,priority});
    });
    return [...byDate.values()].sort((a,b)=>a.date.localeCompare(b.date));
  }

  function weightAlertV278(rows,athleteId,athleteName){
    const ws=normalizeWeightsV278(rows);
    if(ws.length<2)return [];
    const cur=ws[ws.length-1],prev=ws[ws.length-2];
    const recentDiff=cur.weight-prev.weight;
    const recentDays=daysBetweenV278(prev.date,cur.date);
    const rapidThreshold=Math.max(2,cur.weight*.025);
    const eventDate=cur.date;

    if(recentDays<=10&&Math.abs(recentDiff)>=rapidThreshold){
      return [{
        athlete_id:athleteId,athlete_name:athleteName,
        title:'Peso · cambio rápido '+(recentDiff>0?'+':'')+fmtV278(recentDiff,1)+' kg',
        body:'Cambio marcado entre los dos últimos registros. Se muestra como señal para revisar contexto, no como valoración positiva o negativa.',
        severity:'warning',kind:'progression',occurred_at:eventDate,
        event_key:'smart:v278:weight:'+athleteId+':rapid:'+eventDate,
        is_read:false,
        smart_meta:{type_label:'Peso · Revisar',previous:fmtV278(prev.weight,1)+' kg',current:fmtV278(cur.weight,1)+' kg',delta:(recentDiff>0?'+':'')+fmtV278(recentDiff,1)+' kg',period:recentDays+' días',suggestion:'Confirmar tendencia con más registros y revisar contexto.',action_label:'Ver peso'}
      }];
    }

    const cutoff=Date.now()-35*DAY;
    const recent=ws.filter(x=>dateMsV278(x.date)>=cutoff);
    if(recent.length<3)return [];
    const first=recent[0],span=daysBetweenV278(first.date,cur.date);
    if(span<14)return [];
    const delta=cur.weight-first.weight;
    const range=Math.max(...recent.map(x=>x.weight))-Math.min(...recent.map(x=>x.weight));

    if(span>=21&&range<=.3){
      return [{
        athlete_id:athleteId,athlete_name:athleteName,
        title:'Peso estable · variación '+fmtV278(range,1)+' kg',
        body:'Los registros se mantuvieron dentro de un rango estrecho durante varias semanas.',
        severity:'info',kind:'progression',occurred_at:eventDate,
        event_key:'smart:v278:weight:'+athleteId+':stable:'+eventDate,
        is_read:false,
        smart_meta:{type_label:'Peso · Tendencia',previous:fmtV278(first.weight,1)+' kg',current:fmtV278(cur.weight,1)+' kg',delta:'±'+fmtV278(range,1)+' kg',period:span+' días',suggestion:'Interpretar junto con objetivo, medidas, rendimiento y adherencia.',action_label:'Ver peso'}
      }];
    }
    if(Math.abs(delta)>=.8){
      return [{
        athlete_id:athleteId,athlete_name:athleteName,
        title:'Peso en '+(delta>0?'aumento':'descenso')+' · '+(delta>0?'+':'')+fmtV278(delta,1)+' kg',
        body:'Tendencia observada en varios registros; no se interpreta por sí sola como progreso o retroceso.',
        severity:'info',kind:'progression',occurred_at:eventDate,
        event_key:'smart:v278:weight:'+athleteId+':trend:'+eventDate,
        is_read:false,
        smart_meta:{type_label:'Peso · Tendencia',previous:fmtV278(first.weight,1)+' kg',current:fmtV278(cur.weight,1)+' kg',delta:(delta>0?'+':'')+fmtV278(delta,1)+' kg',period:span+' días',suggestion:'Cruzar la tendencia con el objetivo y el resto del seguimiento.',action_label:'Ver peso'}
      }];
    }
    return [];
  }

  function nutritionAlertV278(plan,days,athleteId,athleteName){
    if(!plan)return [];
    const published=dateMsV278(plan.published_at);
    const oldEnough=!published||Date.now()-published>=7*DAY;
    const wk=weekKeyV278();
    if(days>=6){
      return [{
        athlete_id:athleteId,athlete_name:athleteName,
        title:'Nutrición · '+days+'/7 días con registro',
        body:'Registro nutricional consistente durante la última semana.',
        severity:'success',kind:'nutrition',occurred_at:new Date().toISOString(),
        event_key:'smart:v278:nutrition:'+athleteId+':good:'+wk,
        is_read:false,
        smart_meta:{type_label:'Nutrición · Adherencia',previous:'7 días',current:days+' registrados',delta:Math.round(days/7*100)+'%',period:'Últimos 7 días',suggestion:'Usar el registro como contexto, sin depender de un único día.',action_label:'Ver nutrición'}
      }];
    }
    if(oldEnough&&days<=2){
      return [{
        athlete_id:athleteId,athlete_name:athleteName,
        title:'Nutrición · '+days+'/7 días con registro',
        body:'Hay pocos días registrados esta semana para interpretar adherencia nutricional.',
        severity:'warning',kind:'nutrition',occurred_at:new Date().toISOString(),
        event_key:'smart:v278:nutrition:'+athleteId+':low:'+wk,
        is_read:false,
        smart_meta:{type_label:'Nutrición · Revisar',previous:'7 días',current:days+' registrados',delta:Math.round(days/7*100)+'%',period:'Últimos 7 días',suggestion:'Confirmar si el alumno está usando el registro antes de sacar conclusiones.',action_label:'Ver nutrición'}
      }];
    }
    return [];
  }

  async function loadSmartCloudDataV278(force=false){
    if(!cloudEnabled||!supabaseClient||currentProfile?.role!=='coach'){
      return smartCloudCacheV278;
    }
    if(!force&&Date.now()-smartCloudCacheV278.at<60000)return smartCloudCacheV278;
    const athletes=[...cloudAthletes.values()].filter(x=>x?.id);
    const ids=[...new Set(athletes.map(x=>x.id))];
    if(!ids.length)return smartCloudCacheV278;
    const since35=dateAgoV278(35),since7=dateAgoV278(7);
    try{
      const [mr,cr,nr,pr,sr]=await Promise.all([
        supabaseClient.from('body_measurements').select('athlete_id,measured_on,weight_kg').in('athlete_id',ids).gte('measured_on',since35).not('weight_kg','is',null).order('measured_on',{ascending:true}).limit(700),
        supabaseClient.from('weekly_checkins').select('athlete_id,week_start,weight_kg').in('athlete_id',ids).gte('week_start',since35).not('weight_kg','is',null).order('week_start',{ascending:true}).limit(700),
        supabaseClient.from('nutrition_logs').select('athlete_id,logged_on').in('athlete_id',ids).gte('logged_on',since7).order('logged_on',{ascending:true}).limit(1400),
        supabaseClient.from('nutrition_plans').select('athlete_id,published_at').in('athlete_id',ids).limit(500),
        supabaseClient.from('coach_feed_state').select('event_key,read_at,dismissed_at').eq('coach_id',currentUser.id).like('event_key','smart:v278:%').limit(700)
      ]);
      const weights=new Map();
      const addWeight=(x,source,date)=>{
        if(!x?.athlete_id)return;
        if(!weights.has(x.athlete_id))weights.set(x.athlete_id,[]);
        weights.get(x.athlete_id).push({date,weight_kg:x.weight_kg,source});
      };
      if(!mr.error)(mr.data||[]).forEach(x=>addWeight(x,'measurement',x.measured_on));
      if(!cr.error)(cr.data||[]).forEach(x=>addWeight(x,'checkin',x.week_start));

      const daySets=new Map();
      if(!nr.error)(nr.data||[]).forEach(x=>{
        if(!x?.athlete_id||!x?.logged_on)return;
        if(!daySets.has(x.athlete_id))daySets.set(x.athlete_id,new Set());
        daySets.get(x.athlete_id).add(x.logged_on);
      });
      const nutritionDays=new Map([...daySets].map(([k,v])=>[k,v.size]));
      const nutritionPlans=new Map();
      if(!pr.error)(pr.data||[]).forEach(x=>nutritionPlans.set(x.athlete_id,x));
      const states=new Map();
      if(!sr.error)(sr.data||[]).forEach(x=>states.set(x.event_key,x));

      smartCloudCacheV278={at:Date.now(),weights,nutritionDays,nutritionPlans,states};
    }catch(e){
      console.warn('TEAM FJZ V20.78 smart cloud context',e);
      smartCloudCacheV278.at=Date.now();
    }
    return smartCloudCacheV278;
  }

  function buildSmartAlertsV278(cloud){
    const out=[],seen=new Set();
    allStudentsV278().forEach(s=>{
      const ath=athleteForStudentV278(s);
      if(!ath?.id)return;
      const rows=[
        ...exerciseAlertsV278(s,ath.id,s.name),
        ...adherenceAlertsV278(s,ath.id,s.name),
        ...weightAlertV278(cloud.weights.get(ath.id)||[],ath.id,s.name),
        ...nutritionAlertV278(cloud.nutritionPlans.get(ath.id),cloud.nutritionDays.get(ath.id)||0,ath.id,s.name)
      ];
      rows.forEach(x=>{
        if(seen.has(x.event_key))return;
        seen.add(x.event_key);
        const st=cloud.states.get(x.event_key);
        if(st?.dismissed_at)return;
        x.is_read=!!st?.read_at;
        out.push(x);
      });
    });
    const rank={critical:4,warning:3,success:2,info:1};
    out.sort((a,b)=>(rank[b.severity]||0)-(rank[a.severity]||0)||dateMsV278(b.occurred_at)-dateMsV278(a.occurred_at));
    return out;
  }

  const baseLoadCoachFeedV278=window.loadCoachFeed||loadCoachFeed;
  window.loadCoachFeed=async function(force=false){
    let base=[];
    try{base=await baseLoadCoachFeedV278(force)}catch(e){console.warn('TEAM FJZ V20.78 base coach feed',e)}
    const cloud=await loadSmartCloudDataV278(force);
    const smart=buildSmartAlertsV278(cloud);
    const specificAthletes=new Set(smart.filter(x=>x.kind==='progression').map(x=>x.athlete_id));
    const filtered=(base||[]).filter(x=>{
      const generic=/progreso detectado|progresi[oó]n detectada/i.test(String(x?.title||'')+' '+String(x?.body||''));
      return !(generic&&specificAthletes.has(x?.athlete_id));
    });
    const keys=new Set();
    const merged=[...smart,...filtered].filter(x=>{
      const k=x?.event_key||[x?.athlete_id,x?.title,x?.occurred_at].join(':');
      if(keys.has(k))return false;keys.add(k);return true;
    });
    const rank={critical:4,warning:3,success:2,info:1};
    merged.sort((a,b)=>(rank[b.severity]||0)-(rank[a.severity]||0)||dateMsV278(b.occurred_at)-dateMsV278(a.occurred_at));
    coachFeedCache=merged;coachFeedLoadedAt=Date.now();
    return merged;
  };
  try{loadCoachFeed=window.loadCoachFeed}catch(_e){}

  const baseOpenCoachAlertV278=window.openCoachAlertV96;
  window.openCoachAlertV96=async function(athleteId,key,kind){
    if(!String(key||'').startsWith('smart:v278:')){
      return baseOpenCoachAlertV278?.apply(this,arguments);
    }
    try{await window.readCoachAlertV96?.(key)}catch(_e){}
    const row=[...cloudAthletes.values()].find(x=>x.id===athleteId);
    if(row){
      state.selectedStudentId=row.client_id;
    }else if(!String(athleteId||'').startsWith('local-')){
      toast('No encuentro esa ficha');return;
    }
    saveState();coachTab='student';
    const parts=String(key).split(':'),type=parts[2];
    if(type==='exercise'){
      try{selectedExerciseV278=decodeURIComponent(parts[4]||'')}catch(_e){selectedExerciseV278=''}
      selectedMetricV278=['rir-reserve','rir-demand','high-rir','fatigue'].includes(parts[5])?'rir':parts[5]==='volume'||parts[5]==='volume-down'?'volume':parts[5]==='reps'?'reps':'load';
      coachStudentTab='progress';
    }else if(type==='weight'){
      coachStudentTab='progress';
    }else if(type==='nutrition'){
      coachStudentTab='nutrition';
    }else{
      coachStudentTab='summary';
    }
    render();
  };

  const baseOpenAttentionV278=window.openAttentionV80;
  window.openAttentionV80=async function(athleteId,key,kind){
    if(!String(key||'').startsWith('smart:v278:')){
      return baseOpenAttentionV278?.apply(this,arguments);
    }
    try{await markFeedRead?.(key)}catch(_e){}
    const row=[...cloudAthletes.values()].find(x=>x.id===athleteId);
    if(row){
      state.selectedStudentId=row.client_id;
    }else if(!String(athleteId||'').startsWith('local-')){
      toast('No encuentro esa ficha');return;
    }
    saveState();coachTab='student';
    const parts=String(key).split(':'),type=parts[2];
    if(type==='exercise'){
      try{selectedExerciseV278=decodeURIComponent(parts[4]||'')}catch(_e){selectedExerciseV278=''}
      selectedMetricV278=['rir-reserve','rir-demand','high-rir','fatigue'].includes(parts[5])?'rir':parts[5]==='volume'||parts[5]==='volume-down'?'volume':parts[5]==='reps'?'reps':'load';
      coachStudentTab='progress';
    }else if(type==='weight'){
      coachStudentTab='progress';
    }else if(type==='nutrition'){
      coachStudentTab='nutrition';
    }else{
      coachStudentTab='summary';
    }
    render();
  };

  function trackingWeightRowsV278(){
    const rows=[];
    (trackingCache?.measurements||[]).forEach(x=>rows.push({date:x.measured_on,weight_kg:x.weight_kg,source:'measurement'}));
    (trackingCache?.checkins||[]).forEach(x=>rows.push({date:x.week_start,weight_kg:x.weight_kg,source:'checkin'}));
    return normalizeWeightsV278(rows);
  }
  function explicitTargetWeightV278(s){
    const candidates=[
      s?.targetWeight,s?.target_weight_kg,s?.profile?.target_weight_kg,
      s?.profile?.goal_weight_kg,s?.profile?.targetWeight
    ];
    for(const v of candidates){
      const n=numV278(v);if(Number.isFinite(n)&&n>=20&&n<=400)return n;
    }
    return null;
  }
  function movingAverageV278(values){
    return values.map((_,i)=>{
      const xs=values.slice(Math.max(0,i-2),i+1);
      return avgV278(xs);
    });
  }
  function chartSvgV278(points,{target=null,unit='',trend=true}={}){
    if(!points?.length)return '<div class="v278-empty">Todavía no hay suficientes registros para graficar.</div>';
    const W=640,H=220,L=48,R=16,T=18,B=34;
    const vals=points.map(x=>Number(x.value)).filter(Number.isFinite);
    if(Number.isFinite(target))vals.push(target);
    let min=Math.min(...vals),max=Math.max(...vals);
    const pad=Math.max((max-min)*.16,unit==='kg'?1:.5);
    min-=pad;max+=pad;if(max<=min)max=min+1;
    const x=i=>L+(points.length===1?(W-L-R)/2:i*(W-L-R)/(points.length-1));
    const y=v=>T+(max-v)/(max-min)*(H-T-B);
    const path=points.map((p,i)=>(i?'L':'M')+x(i).toFixed(1)+' '+y(p.value).toFixed(1)).join(' ');
    const mav=trend&&points.length>=4?movingAverageV278(points.map(p=>p.value)):null;
    const trendPath=mav?mav.map((v,i)=>(i?'L':'M')+x(i).toFixed(1)+' '+y(v).toFixed(1)).join(' '):'';
    const grid=[0,.25,.5,.75,1].map(fr=>{
      const yy=T+fr*(H-T-B),vv=max-fr*(max-min);
      return '<line class="v278-gridline" x1="'+L+'" y1="'+yy+'" x2="'+(W-R)+'" y2="'+yy+'"/>'+
        '<text class="v278-axis-label" x="'+(L-7)+'" y="'+(yy+3)+'" text-anchor="end">'+fmtV278(vv,unit==='kg'?1:0)+'</text>';
    }).join('');
    const labelStep=Math.max(1,Math.ceil(points.length/5));
    const labels=points.map((p,i)=>(i%labelStep===0||i===points.length-1)
      ?'<text class="v278-axis-label" x="'+x(i)+'" y="'+(H-8)+'" text-anchor="middle">'+esc(fmtDate(p.date))+'</text>':'').join('');
    const targetLine=Number.isFinite(target)
      ?'<line class="v278-target-line" x1="'+L+'" y1="'+y(target)+'" x2="'+(W-R)+'" y2="'+y(target)+'"/>':'';
    return '<svg class="v278-chart" viewBox="0 0 '+W+' '+H+'" preserveAspectRatio="none" role="img">'+
      grid+targetLine+
      (trendPath?'<path class="v278-line-trend" d="'+trendPath+'"/>':'')+
      '<path class="v278-line-main" d="'+path+'"/>'+
      points.map((p,i)=>'<circle class="v278-point-main" cx="'+x(i)+'" cy="'+y(p.value)+'" r="4"/>').join('')+
      labels+'</svg>';
  }

  function dualChartSvgV278(items){
    const pts=(items||[]).filter(x=>Number.isFinite(x.bestLoad)&&Number.isFinite(x.avgRir));
    if(pts.length<2)return '<div class="v278-empty">Se necesitan al menos 2 sesiones con carga y RIR para comparar.</div>';
    const W=640,H=190,L=28,R=18,T=16,B=30;
    const loads=pts.map(x=>x.bestLoad),rirs=pts.map(x=>x.avgRir);
    let lmin=Math.min(...loads),lmax=Math.max(...loads),rmin=Math.min(...rirs),rmax=Math.max(...rirs);
    if(lmax===lmin){lmax+=1;lmin-=1}if(rmax===rmin){rmax+=.5;rmin-=.5}
    const x=i=>L+i*(W-L-R)/(pts.length-1);
    const yLoad=v=>T+(lmax-v)/(lmax-lmin)*(H-T-B);
    const yRir=v=>T+(rmax-v)/(rmax-rmin)*(H-T-B);
    const lp=pts.map((p,i)=>(i?'L':'M')+x(i).toFixed(1)+' '+yLoad(p.bestLoad).toFixed(1)).join(' ');
    const rp=pts.map((p,i)=>(i?'L':'M')+x(i).toFixed(1)+' '+yRir(p.avgRir).toFixed(1)).join(' ');
    return '<svg class="v278-chart" viewBox="0 0 '+W+' '+H+'" preserveAspectRatio="none">'+
      [0,.5,1].map(fr=>'<line class="v278-gridline" x1="'+L+'" y1="'+(T+fr*(H-T-B))+'" x2="'+(W-R)+'" y2="'+(T+fr*(H-T-B))+'"/>').join('')+
      '<path class="v278-line-main" d="'+lp+'"/><path class="v278-line-rir" d="'+rp+'"/>'+
      pts.map((p,i)=>'<circle class="v278-point-main" cx="'+x(i)+'" cy="'+yLoad(p.bestLoad)+'" r="3.5"/><circle class="v278-point-rir" cx="'+x(i)+'" cy="'+yRir(p.avgRir)+'" r="3.5"/>').join('')+
      '</svg>';
  }

  function weightSectionV278(s){
    const rows=trackingWeightRowsV278();
    if(!rows.length)return '<div class="v278-empty">Todavía no hay registros de peso para mostrar una tendencia.</div>';
    const first=rows[0],cur=rows[rows.length-1],total=cur.weight-first.weight;
    const cutoff=Date.now()-21*DAY;
    const recent=rows.filter(x=>dateMsV278(x.date)>=cutoff);
    const recentDelta=recent.length>=2?cur.weight-recent[0].weight:null;
    const target=explicitTargetWeightV278(s);
    let trend='Estable';
    if(recentDelta!=null&&recentDelta>=.4)trend='En aumento';
    else if(recentDelta!=null&&recentDelta<=-.4)trend='En descenso';
    const pts=rows.slice(-16).map(x=>({date:x.date,value:x.weight}));
    return '<div class="v278-weight-kpis">'+
      '<div class="v278-kpi"><span>Inicio visible</span><strong>'+fmtV278(first.weight,1)+' kg</strong><small>'+esc(fmtDate(first.date))+'</small></div>'+
      '<div class="v278-kpi"><span>Actual</span><strong>'+fmtV278(cur.weight,1)+' kg</strong><small>'+esc(fmtDate(cur.date))+'</small></div>'+
      '<div class="v278-kpi"><span>Cambio total</span><strong>'+(total>0?'+':'')+fmtV278(total,1)+' kg</strong><small>'+rows.length+' registros</small></div>'+
      '<div class="v278-kpi"><span>Tendencia 3 sem.</span><strong>'+esc(trend)+'</strong><small>'+(recentDelta==null?'Sin comparación':(recentDelta>0?'+':'')+fmtV278(recentDelta,1)+' kg')+'</small></div>'+
      '</div>'+
      '<div class="v278-chart-shell">'+chartSvgV278(pts,{target,unit:'kg',trend:true})+
      '<div class="v278-chart-legend"><span><i class="v278-legend-dot"></i>Peso</span><span><i class="v278-legend-dot trend"></i>Tendencia</span>'+
      (Number.isFinite(target)?'<span><i class="v278-legend-dot target"></i>Objetivo cargado: '+fmtV278(target,1)+' kg</span>':'')+
      '</div></div>';
  }

  function metricValueV278(item,metric){
    if(metric==='load')return item.bestLoad;
    if(metric==='reps')return item.totalReps;
    if(metric==='volume')return item.volume;
    if(metric==='rir')return item.avgRir;
    return null;
  }
  function metricLabelV278(metric){
    return {load:'Carga',reps:'Repeticiones',volume:'Volumen',rir:'RIR promedio'}[metric]||metric;
  }
  function metricUnitV278(metric){
    return metric==='load'?'kg':metric==='volume'?'kg·rep':metric==='reps'?'reps':'RIR';
  }

  window.updateSmartExerciseChartV278=function(){
    const select=el('v278ExerciseSelect'),metricSel=el('v278MetricSelect'),body=el('v278ExerciseChartBody');
    if(!body)return;
    if(select)selectedExerciseV278=select.value;
    if(metricSel)selectedMetricV278=metricSel.value;
    const rows=exerciseSeriesV278(student());
    const row=rows.find(x=>x.key===selectedExerciseV278)||rows[0];
    if(!row){body.innerHTML='<div class="v278-empty">Todavía no hay sesiones suficientes para analizar ejercicios.</div>';return}
    selectedExerciseV278=row.key;
    const items=row.items.slice(-10);
    const metric=selectedMetricV278;
    const pts=items.map(x=>({date:x.date,value:metricValueV278(x,metric)})).filter(x=>Number.isFinite(x.value));
    const cur=pts[pts.length-1],prev=pts[pts.length-2];
    const delta=cur&&prev?cur.value-prev.value:null;
    const dp=cur&&prev?pctV278(cur.value,prev.value):null;
    const last=row.items[row.items.length-1];
    body.innerHTML=
      '<div class="v278-perf-kpis">'+
        '<div class="v278-kpi"><span>'+esc(metricLabelV278(metric))+' actual</span><strong>'+fmtV278(cur?.value,metric==='rir'?1:metric==='load'?1:0)+' '+esc(metricUnitV278(metric))+'</strong><small>'+esc(fmtDate(cur?.date))+'</small></div>'+
        '<div class="v278-kpi"><span>Anterior</span><strong>'+fmtV278(prev?.value,metric==='rir'?1:metric==='load'?1:0)+' '+esc(metricUnitV278(metric))+'</strong><small>'+esc(fmtDate(prev?.date))+'</small></div>'+
        '<div class="v278-kpi"><span>Cambio</span><strong>'+(delta==null?'—':(delta>0?'+':'')+fmtV278(delta,metric==='rir'||metric==='load'?1:0))+'</strong><small>'+(dp==null?'Sin % comparable':(dp>0?'+':'')+fmtV278(dp,0)+'%')+'</small></div>'+
        '<div class="v278-kpi"><span>Último RIR</span><strong>'+fmtV278(last?.avgRir,1)+'</strong><small>'+fmtV278(last?.bestLoad,1)+' kg · '+fmtV278(last?.bestReps,0)+' reps</small></div>'+
      '</div>'+
      '<div class="v278-chart-shell">'+chartSvgV278(pts,{unit:metric==='load'?'kg':'',trend:true})+'</div>'+
      '<div class="v278-dual"><div class="v278-dual-head"><strong>Carga × RIR</strong><span>Relaciona rendimiento con esfuerzo percibido.</span></div>'+
      '<div class="v278-chart-shell">'+dualChartSvgV278(items)+
      '<div class="v278-chart-legend"><span><i class="v278-legend-dot"></i>Carga</span><span><i class="v278-legend-dot rir"></i>RIR promedio</span></div></div></div>';
  };

  function performanceSectionV278(s){
    const rows=exerciseSeriesV278(s).filter(x=>x.items.length>=1).sort((a,b)=>b.items.length-a.items.length);
    if(!rows.length)return '<div class="v278-empty">Todavía no hay resultados por ejercicio para graficar.</div>';
    if(!selectedExerciseV278||!rows.some(x=>x.key===selectedExerciseV278))selectedExerciseV278=rows[0].key;
    const options=rows.map(x=>'<option value="'+esc(x.key)+'" '+(x.key===selectedExerciseV278?'selected':'')+'>'+esc(x.name)+'</option>').join('');
    const metrics=[['load','Carga'],['reps','Reps'],['volume','Volumen'],['rir','RIR promedio']]
      .map(x=>'<option value="'+x[0]+'" '+(x[0]===selectedMetricV278?'selected':'')+'>'+x[1]+'</option>').join('');
    return '<div class="v278-controls"><label class="tiny muted">Ejercicio<select id="v278ExerciseSelect" class="input" onchange="updateSmartExerciseChartV278()">'+options+'</select></label>'+
      '<label class="tiny muted">Métrica<select id="v278MetricSelect" class="input" onchange="updateSmartExerciseChartV278()">'+metrics+'</select></label></div>'+
      '<div id="v278ExerciseChartBody"></div>';
  }

  function weekBucketsV278(s){
    const planned=Math.max(1,Number(s?.plannedPerWeek)||s?.days?.length||1);
    const now=Date.now();
    return [3,2,1,0].map(offset=>{
      const end=now-offset*7*DAY,start=end-7*DAY;
      const done=(s?.sessions||[]).filter(x=>{const t=dateMsV278(x?.date);return t>=start&&t<end}).length;
      return {done,planned,pct:Math.min(100,Math.round(done/planned*100)),label:offset===0?'Actual':'-'+offset+' sem'};
    });
  }
  function adherenceSectionV278(s){
    const weeks=weekBucketsV278(s),latest=weeks[weeks.length-1];
    const checks=(trackingCache?.checkins||[]).slice().sort((a,b)=>String(b?.week_start||'').localeCompare(String(a?.week_start||'')));
    const currentCheck=checks.find(x=>dateMsV278(x?.week_start)>=Date.now()-8*DAY);
    const ath=athleteForStudentV278(s);
    const nutritionActive=ath?.id&&smartCloudCacheV278.nutritionPlans.has(ath.id);
    const nutritionDays=ath?.id?(smartCloudCacheV278.nutritionDays.get(ath.id)||0):0;
    return '<div class="v278-adherence-grid">'+
      '<div class="v278-week-bars">'+weeks.map(w=>'<div class="v278-week"><div class="v278-week-bar" style="height:'+Math.max(5,w.pct*.6)+'px"></div><span>'+w.done+'/'+w.planned+'<br>'+esc(w.label)+'</span></div>').join('')+'</div>'+
      '<div class="v278-adherence-card"><span>Entrenamientos</span><strong>'+latest.done+' / '+latest.planned+'</strong><small>'+latest.pct+'% de la frecuencia de los últimos 7 días.</small></div>'+
      '<div class="v278-adherence-card"><span>Check-in</span><strong>'+(currentCheck?'Completado':'Pendiente')+'</strong><small>'+(currentCheck?esc(fmtDate(currentCheck.week_start)):'Sin check-in reciente')+'</small></div>'+
      (nutritionActive?'<div class="v278-adherence-card"><span>Nutrición</span><strong>'+nutritionDays+' / 7 días</strong><small>Días con algún registro nutricional.</small></div>':'')+
      '</div>';
  }

  function renderSmartProgressV278(){
    const coachView=mode==='coach'&&coachTab==='student'&&coachStudentTab==='progress';
    const studentView=mode==='student'&&studentTab==='progress';
    if(!coachView&&!studentView)return;
    const host=el(coachView?'coachStudentBody':'studentSubBody');
    if(!host)return;
    el('v278SmartProgress')?.remove();
    el('v275ProgressOverview')?.remove();
    const s=student();if(!s)return;

    const card=document.createElement('section');
    card.id='v278SmartProgress';card.className='card v278-progress';
    card.innerHTML=
      '<div class="v278-progress-head"><div><div class="v225-section-kicker">PROGRESO · TEAM FJZ</div><h3>Panel de evolución</h3>'+
      '<p class="muted tiny">Peso, rendimiento, RIR, volumen y adherencia con contexto.</p></div><span class="badge red">Pro</span></div>'+
      '<div class="v278-performance"><div class="section-title"><div><h4 style="margin:0">Peso corporal</h4><div class="muted tiny">Tendencia de varios registros; no se interpreta de forma aislada.</div></div></div>'+
      weightSectionV278(s)+'</div>'+
      '<div class="v278-performance"><div class="section-title"><div><h4 style="margin:0">Rendimiento por ejercicio</h4><div class="muted tiny">Carga, reps, volumen y RIR sin modificar automáticamente la rutina.</div></div></div>'+
      performanceSectionV278(s)+'</div>'+
      '<div class="v278-adherence"><div class="section-title"><div><h4 style="margin:0">Adherencia</h4><div class="muted tiny">Frecuencia semanal, check-in y nutrición cuando está activa.</div></div></div>'+
      adherenceSectionV278(s)+'</div>';
    host.prepend(card);
    window.updateSmartExerciseChartV278();
  }

  async function hydrateSmartProgressV278(){
    renderSmartProgressV278();
    const aid=typeof trackingAthleteId==='function'?trackingAthleteId():null;
    if(cloudEnabled&&supabaseClient&&aid&&trackingLoadedFor!==aid&&!smartTrackingPromiseV278){
      smartTrackingPromiseV278=Promise.resolve(loadTracking(false)).then(()=>{
        smartTrackingPromiseV278=null;
        return currentProfile?.role==='coach'?loadSmartCloudDataV278(false):null;
      }).then(()=>{
        const stillCoach=mode==='coach'&&coachTab==='student'&&coachStudentTab==='progress';
        const stillStudent=mode==='student'&&studentTab==='progress';
        if(stillCoach||stillStudent)renderSmartProgressV278();
      }).catch(()=>{smartTrackingPromiseV278=null});
    }else if(currentProfile?.role==='coach'&&cloudEnabled){
      loadSmartCloudDataV278(false).then(()=>renderSmartProgressV278()).catch(()=>{});
    }
  }

  function selectedStudentAlertsV278(s){
    const ath=athleteForStudentV278(s);
    const aid=ath?.id||'local-'+s.id;
    const weights=ath?.id?(smartCloudCacheV278.weights.get(ath.id)||[]):trackingWeightRowsV278();
    return [
      ...exerciseAlertsV278(s,aid,s.name),
      ...adherenceAlertsV278(s,aid,s.name),
      ...weightAlertV278(weights,aid,s.name),
      ...(ath?.id?nutritionAlertV278(smartCloudCacheV278.nutritionPlans.get(ath.id),smartCloudCacheV278.nutritionDays.get(ath.id)||0,aid,s.name):[])
    ];
  }

  function renderAthleteIntelV278(){
    if(!(mode==='coach'&&coachTab==='student'&&coachStudentTab==='summary'))return;
    const host=el('coachStudentBody');if(!host)return;
    el('v278AthleteIntel')?.remove();
    const s=student();if(!s)return;
    const alerts=selectedStudentAlertsV278(s);
    const success=alerts.filter(x=>x.severity==='success');
    const review=alerts.filter(x=>x.severity==='warning'||x.severity==='critical');
    const series=exerciseSeriesV278(s);
    const progressing=series.filter(r=>compareExerciseV278(r,'x',s.name).some(a=>a.severity==='success')).length;
    const stable=series.filter(r=>r.items.length>=4&&!compareExerciseV278(r,'x',s.name).length).length;
    const planned=Math.max(1,Number(s.plannedPerWeek)||s.days?.length||1);
    const done=(s.sessions||[]).filter(x=>dateMsV278(x?.date)>=Date.now()-7*DAY).length;
    const weights=trackingWeightRowsV278();
    let weightText='Sin datos',weightSub='';
    if(weights.length>=2){
      const a=weights[Math.max(0,weights.length-3)],b=weights[weights.length-1],d=b.weight-a.weight;
      weightText=(d>0?'+':'')+fmtV278(d,1)+' kg';
      weightSub='últimos '+daysBetweenV278(a.date,b.date)+' días';
    }
    const top=alerts.slice(0,3);
    const ath=athleteForStudentV278(s);
    const card=document.createElement('section');card.id='v278AthleteIntel';card.className='card v278-athlete-intel';
    card.innerHTML=
      '<div class="section-title"><div><div class="v225-section-kicker">INTELIGENCIA DE PROGRESO</div><h3>Lectura rápida</h3><div class="muted tiny">Cambios concretos detectados sin repetir señales genéricas.</div></div><span class="badge blue">'+alerts.length+' señales</span></div>'+
      '<div class="v278-intel-grid">'+
        '<div class="v278-intel-metric"><span>Mejoras</span><strong>'+success.length+'</strong><small>'+progressing+' ejercicios con señal positiva</small></div>'+
        '<div class="v278-intel-metric"><span>Revisar</span><strong>'+review.length+'</strong><small>'+stable+' ejercicios sin cambio relevante</small></div>'+
        '<div class="v278-intel-metric"><span>Peso reciente</span><strong>'+esc(weightText)+'</strong><small>'+esc(weightSub||'tendencia disponible en Progreso')+'</small></div>'+
        '<div class="v278-intel-metric"><span>Adherencia</span><strong>'+done+' / '+planned+'</strong><small>últimos 7 días</small></div>'+
      '</div>'+
      (top.length?'<div class="v278-mini-alerts">'+top.map(x=>
        '<button class="v278-mini-alert '+esc(x.severity)+'" onclick="openCoachAlertV96(\''+(ath?.id||x.athlete_id)+'\',\''+esc(x.event_key)+'\',\''+esc(x.kind)+'\')">'+
        '<span>'+(x.severity==='success'?'↗':x.severity==='critical'?'!':x.severity==='warning'?'△':'i')+'</span>'+
        '<span><strong>'+esc(x.title)+'</strong><small>'+esc(x.body)+'</small></span><span>›</span></button>'
      ).join('')+'</div>':'<div class="v278-empty">Sin señales nuevas con datos suficientes.</div>');
    host.prepend(card);
  }

  async function hydrateAthleteIntelV278(){
    renderAthleteIntelV278();
    if(!cloudEnabled||!supabaseClient)return;
    const aid=typeof trackingAthleteId==='function'?trackingAthleteId():null;
    const jobs=[loadSmartCloudDataV278(false)];
    if(aid&&trackingLoadedFor!==aid)jobs.push(loadTracking(false));
    Promise.allSettled(jobs).then(()=>{
      if(mode==='coach'&&coachTab==='student'&&coachStudentTab==='summary')renderAthleteIntelV278();
    });
  }

  window.__fjzSmartPostRenderV278=function(){
    if(mode==='coach'&&coachTab==='student'&&coachStudentTab==='summary'){
      hydrateAthleteIntelV278();
      return;
    }
    const progress=(mode==='coach'&&coachTab==='student'&&coachStudentTab==='progress')||(mode==='student'&&studentTab==='progress');
    if(progress)hydrateSmartProgressV278();
  };

  window.__fjzV278={
    version:VERSION,
    specificProgressAlerts:true,
    genericProgressAlertSuppressedWhenSpecific:true,
    smartAlertDedupByEventKey:true,
    smartAlertReadDismissState:true,
    weightTrendUsesMultipleRecords:true,
    weightDirectionNeutral:true,
    rirComparableExerciseLogic:true,
    repeatedHighRirAlert:true,
    repeatedLowRirFatigueSignal:true,
    loadRepsVolumeAlerts:true,
    clickableSmartAlerts:true,
    professionalWeightChart:true,
    targetWeightOnlyWhenExplicit:true,
    exerciseMetricSelector:true,
    loadRirCombinedChart:true,
    fourWeekAdherenceChart:true,
    athleteIntelligenceSummary:true,
    noExtraTimers:true,
    noExtraListeners:true,
    noExtraObservers:true
  };
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-smart-alerts-progress" content="20.78">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.78 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-smart-alerts-progress" content="20.78"',
    "specificProgressAlerts:true",
    "genericProgressAlertSuppressedWhenSpecific:true",
    "smartAlertDedupByEventKey:true",
    "weightTrendUsesMultipleRecords:true",
    "rirComparableExerciseLogic:true",
    "repeatedHighRirAlert:true",
    "repeatedLowRirFatigueSignal:true",
    "clickableSmartAlerts:true",
    "professionalWeightChart:true",
    "targetWeightOnlyWhenExplicit:true",
    "exerciseMetricSelector:true",
    "loadRirCombinedChart:true",
    "fourWeekAdherenceChart:true",
    "athleteIntelligenceSummary:true",
    "Alertas inteligentes",
    "Carga × RIR",
    "v278SmartProgress",
    "v278AthleteIntel",
]:
    if marker not in html:
        raise RuntimeError("V20.78 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.78 smart alerts + professional progress")
print("V20.78 BEFORE:",before)
print("V20.78 AFTER:",after)
print("V20.78 specific alerts, RIR/load/reps/volume logic, weight trends and pro charts added with zero topology growth")
