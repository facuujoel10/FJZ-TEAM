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
    'meta name="fjz-final-runtime-stability" content="20.74"',
    "preparationPersistenceIntegratedV274:true",
    "renderBottomNav",
    "renderStudent",
    "renderProgress",
    "studentTab==='nutrition'",
    "trackingCache",
]:
    if marker not in html:
        raise RuntimeError("V20.75 prerequisite missing: "+marker)

css=r"""
/* =========================================================
   TEAM FJZ · V20.75 MOBILE HUD + PROGRESS OVERVIEW
   ========================================================= */
@media(max-width:900px){
  body{
    padding-bottom:calc(112px + env(safe-area-inset-bottom))!important;
  }
  .shell{
    padding-bottom:calc(124px + env(safe-area-inset-bottom))!important;
  }

  .bottom-nav.v275-student-hud{
    display:grid!important;
    grid-template-columns:repeat(4,minmax(0,1fr))!important;
    position:fixed!important;
    left:50%!important;
    right:auto!important;
    bottom:calc(10px + env(safe-area-inset-bottom))!important;
    width:min(calc(100% - 22px),470px)!important;
    min-width:0!important;
    transform:translateX(-50%)!important;
    gap:5px!important;
    padding:6px!important;
    overflow:visible!important;
    border:1px solid rgba(255,255,255,.11)!important;
    border-radius:22px!important;
    background:rgba(13,14,18,.94)!important;
    box-shadow:0 14px 38px rgba(0,0,0,.46),0 0 0 1px rgba(255,34,54,.025) inset!important;
    backdrop-filter:blur(18px)!important;
    -webkit-backdrop-filter:blur(18px)!important;
    isolation:isolate;
    z-index:92!important;
  }
  .bottom-nav.v275-student-hud button{
    display:grid!important;
    grid-template-rows:23px auto!important;
    place-items:center!important;
    gap:3px!important;
    min-width:0!important;
    min-height:56px!important;
    width:100%!important;
    padding:6px 3px 5px!important;
    margin:0!important;
    border:0!important;
    border-radius:16px!important;
    background:transparent!important;
    color:#777d87!important;
    font-size:9px!important;
    line-height:1!important;
    font-weight:820!important;
    letter-spacing:.01em!important;
    white-space:nowrap!important;
    transition:background-color .14s ease,color .14s ease,border-color .14s ease!important;
  }
  .bottom-nav.v275-student-hud button svg{
    width:22px!important;
    height:22px!important;
    display:block!important;
    fill:none!important;
    stroke:currentColor!important;
    stroke-width:1.8!important;
    stroke-linecap:round!important;
    stroke-linejoin:round!important;
  }
  .bottom-nav.v275-student-hud button.active{
    color:#fff!important;
    background:
      linear-gradient(180deg,rgba(255,55,72,.16),rgba(255,35,52,.075))!important;
    box-shadow:0 0 0 1px rgba(255,65,82,.22) inset!important;
  }
  .bottom-nav.v275-student-hud button.active svg{
    color:#ff4658!important;
  }
  .bottom-nav.v275-student-hud button:active{
    transform:none!important;
    background-color:rgba(255,255,255,.055)!important;
  }
}
@media(max-width:390px){
  .bottom-nav.v275-student-hud{
    width:calc(100% - 14px)!important;
    bottom:calc(7px + env(safe-area-inset-bottom))!important;
    border-radius:20px!important;
  }
  .bottom-nav.v275-student-hud button{
    min-height:54px!important;
    font-size:8px!important;
  }
}

/* Training hub */
.v275-training-head{
  display:flex;
  align-items:flex-end;
  justify-content:space-between;
  gap:12px;
  margin-bottom:12px;
}
.v275-training-head h3{margin:0}
.v275-training-head p{margin:4px 0 0}
.v275-training-grid{
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:10px;
}
.v275-training-day{
  display:grid;
  gap:11px;
  min-width:0;
  padding:14px;
  border:1px solid #2a2d34;
  border-radius:15px;
  background:
    linear-gradient(150deg,rgba(255,38,57,.035),transparent 58%),
    #101116;
}
.v275-training-day-top{
  display:flex;
  justify-content:space-between;
  gap:10px;
  align-items:flex-start;
}
.v275-training-day h4{margin:0;font-size:15px}
.v275-training-day p{margin:4px 0 0}
.v275-training-number{
  display:grid;
  place-items:center;
  width:29px;
  height:29px;
  flex:0 0 29px;
  border-radius:10px;
  color:#ff5363;
  background:rgba(255,45,62,.08);
  border:1px solid rgba(255,55,72,.18);
  font-size:10px;
  font-weight:900;
}
.v275-training-summary{
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:7px;
  margin-bottom:10px;
}
.v275-training-summary>div{
  min-width:0;
  padding:10px;
  border:1px solid #292d34;
  border-radius:12px;
  background:#0e0f13;
}
.v275-training-summary span,
.v275-training-summary small{
  display:block;
  color:#7f858f;
  font-size:8px;
}
.v275-training-summary strong{
  display:block;
  margin-top:3px;
  color:#f4f5f7;
  font-size:16px;
  font-variant-numeric:tabular-nums;
}

/* Progress overview inspired by the supplied reference, adapted to TEAM FJZ. */
.v275-progress-overview{
  margin-bottom:12px!important;
  border-color:rgba(255,67,83,.18)!important;
  background:
    radial-gradient(circle at 92% 0,rgba(255,41,58,.07),transparent 31%),
    #101116!important;
}
.v275-progress-head{
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  gap:12px;
  margin-bottom:11px;
}
.v275-progress-head h3{margin:0}
.v275-progress-head p{margin:4px 0 0}
.v275-progress-grid{
  display:grid;
  grid-template-columns:1.45fr .8fr .8fr;
  gap:8px;
}
.v275-progress-panel{
  min-width:0;
  padding:12px;
  border:1px solid #2a2e35;
  border-radius:13px;
  background:#0d0e12;
}
.v275-progress-panel .v275-label{
  display:block;
  color:#7d838e;
  font-size:7px;
  font-weight:900;
  letter-spacing:.08em;
  text-transform:uppercase;
}
.v275-progress-panel strong.v275-value{
  display:block;
  margin-top:5px;
  color:#f5f6f7;
  font-size:22px;
  line-height:1.05;
  font-variant-numeric:tabular-nums;
}
.v275-progress-panel small{
  display:block;
  margin-top:5px;
  color:#858c96;
  font-size:8px;
  line-height:1.35;
}
.v275-weight-top{
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:6px;
  margin-bottom:8px;
}
.v275-weight-top>div{
  min-width:0;
}
.v275-weight-top strong{
  display:block;
  margin-top:3px;
  color:#eceef1;
  font-size:12px;
  font-variant-numeric:tabular-nums;
}
.v275-spark{
  width:100%;
  height:82px;
  display:block;
  overflow:visible;
}
.v275-spark-axis{
  stroke:#2b2e35;
  stroke-width:1;
}
.v275-spark-line{
  fill:none;
  stroke:#ff4052;
  stroke-width:2.4;
  vector-effect:non-scaling-stroke;
}
.v275-spark-point{
  fill:#ff4052;
  stroke:#101116;
  stroke-width:1.6;
  vector-effect:non-scaling-stroke;
}
.v275-progress-track{
  height:7px;
  overflow:hidden;
  margin-top:9px;
  border-radius:99px;
  background:#252830;
}
.v275-progress-track>span{
  display:block;
  height:100%;
  border-radius:99px;
  background:linear-gradient(90deg,#b91f30,#ff4658);
}
.v275-goal-copy{
  display:-webkit-box;
  -webkit-line-clamp:4;
  -webkit-box-orient:vertical;
  overflow:hidden;
}
.v275-progress-empty{
  display:grid;
  gap:4px;
  min-height:82px;
  align-content:center;
  color:#7f858e;
  font-size:9px;
}
@media(max-width:720px){
  .v275-progress-grid{
    grid-template-columns:1fr 1fr!important;
  }
  .v275-progress-panel.v275-weight{
    grid-column:1/-1;
  }
  .v275-training-grid{
    grid-template-columns:1fr;
  }
}
@media(max-width:390px){
  .v275-progress-grid{
    grid-template-columns:1fr!important;
  }
  .v275-progress-panel.v275-weight{
    grid-column:auto;
  }
  .v275-training-summary{
    grid-template-columns:1fr 1fr;
  }
  .v275-training-summary>div:last-child{
    grid-column:1/-1;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.75 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

runtime=r"""
<script id="v275MobileHudProgressRuntime">
(function(){
  const VERSION='20.75';

  function navIconV275(type){
    const icons={
      home:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 10.5 12 3.8l8.5 6.7"/><path d="M5.5 9.4V20h13V9.4"/><path d="M9.4 20v-6.2h5.2V20"/></svg>',
      train:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 8v8M3.5 9.5v5M18 8v8M20.5 9.5v5M6 12h12"/></svg>',
      nutrition:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.2 3v7.2M3.8 3v4.8c0 1.5 1 2.4 2.4 2.4s2.4-.9 2.4-2.4V3M6.2 10.2V21M15.4 3v18M15.4 3c3.2 1.4 4.8 4 4.8 7.2h-4.8"/></svg>',
      progress:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19V9M10 19V5M16 19v-7M3 19h18"/><path d="m4 8 6-4 6 6 5-5"/></svg>'
    };
    return icons[type]||icons.home;
  }

  function studentHudV275(nav){
    const trainingActive=studentTab==='training'||studentTab==='workout';
    nav.classList.add('v275-student-hud');
    nav.setAttribute('aria-label','Navegación principal');
    nav.innerHTML=
      '<button class="'+(studentTab==='home'?'active':'')+'" onclick="studentTab=\'home\';render()" aria-label="Inicio">'+navIconV275('home')+'<span>Inicio</span></button>'+
      '<button class="'+(trainingActive?'active':'')+'" onclick="studentTab=\'training\';render()" aria-label="Entrenar">'+navIconV275('train')+'<span>Entrenar</span></button>'+
      '<button class="'+(studentTab==='nutrition'?'active':'')+'" onclick="studentTab=\'nutrition\';render()" aria-label="Nutrición">'+navIconV275('nutrition')+'<span>Nutrición</span></button>'+
      '<button class="'+(studentTab==='progress'?'active':'')+'" onclick="studentTab=\'progress\';render()" aria-label="Progreso">'+navIconV275('progress')+'<span>Progreso</span></button>';
  }

  const baseBottomNavV275=window.renderBottomNav||renderBottomNav;
  window.renderBottomNav=function(){
    const nav=el('bottomNav');
    if(mode==='student'&&nav){
      studentHudV275(nav);
      return;
    }
    nav?.classList.remove('v275-student-hud');
    return baseBottomNavV275.apply(this,arguments);
  };
  try{renderBottomNav=window.renderBottomNav}catch(_e){}

  function recentSessionCountV275(days=7){
    const since=Date.now()-days*86400000;
    return (student()?.sessions||[]).filter(x=>{
      const t=new Date(x?.date||0).getTime();
      return Number.isFinite(t)&&t>=since;
    }).length;
  }

  window.renderTrainingHubV275=function(){
    const s=student(),v=el('view');
    if(!v)return;
    const done7=recentSessionCountV275(7);
    const planned=Math.max(1,Number(s?.plannedPerWeek)||s?.days?.length||1);
    const pct=Math.min(100,Math.round(done7/planned*100));
    const last=(s?.sessions||[]).slice().sort((a,b)=>new Date(b?.date||0)-new Date(a?.date||0))[0];

    v.innerHTML=
      '<section class="hero"><div><h2>Entrenar</h2><p>Elegí tu sesión y registrá cargas, repeticiones y RIR.</p></div><span class="badge '+(done7>=planned?'green':'blue')+'">'+done7+'/'+planned+' esta semana</span></section>'+
      '<div class="v275-training-summary">'+
        '<div><span>Sesiones 7 días</span><strong>'+done7+'</strong><small>de '+planned+' planificadas</small></div>'+
        '<div><span>Progreso semanal</span><strong>'+pct+'%</strong><small>constancia del plan</small></div>'+
        '<div><span>Última sesión</span><strong>'+(last?esc(fmtDate(last.date)):'—')+'</strong><small>'+(last?esc(last.dayName||'Entrenamiento'):'Sin registros')+'</small></div>'+
      '</div>'+
      '<div class="card"><div class="v275-training-head"><div><h3>Tu rutina</h3><p class="muted tiny">Seleccioná el día que vas a entrenar.</p></div><span class="badge blue">'+(s?.days?.length||0)+' días</span></div>'+
      '<div class="v275-training-grid">'+
      ((s?.days||[]).length?(s.days||[]).map((d,i)=>
        '<div class="v275-training-day">'+
          '<div class="v275-training-day-top"><div><h4>'+esc(d.name||('Día '+(i+1)))+'</h4><p class="muted tiny">'+esc(d.muscles||'Rutina')+' · '+(d.exercises?.length||0)+' ejercicios</p></div><span class="v275-training-number">'+(i+1)+'</span></div>'+
          '<button class="btn primary" style="width:100%" onclick="startWorkout('+i+')">Comenzar entrenamiento</button>'+
        '</div>'
      ).join(''):'<div class="empty">Tu coach todavía no cargó días de entrenamiento.</div>')+
      '</div></div>';
  };

  const baseRenderStudentV275=window.renderStudent||renderStudent;
  window.renderStudent=function(){
    if(studentTab==='training')return window.renderTrainingHubV275();
    return baseRenderStudentV275.apply(this,arguments);
  };
  try{renderStudent=window.renderStudent}catch(_e){}

  function trackingRowsV275(){
    const rows=[];
    const ms=Array.isArray(trackingCache?.measurements)?trackingCache.measurements:[];
    const cs=Array.isArray(trackingCache?.checkins)?trackingCache.checkins:[];
    ms.forEach(x=>{
      const w=Number(x?.weight_kg);
      if(Number.isFinite(w)&&w>20&&w<400)rows.push({date:String(x?.measured_on||''),weight:w,source:'measurement'});
    });
    cs.forEach(x=>{
      const w=Number(x?.weight_kg);
      if(Number.isFinite(w)&&w>20&&w<400)rows.push({date:String(x?.week_start||''),weight:w,source:'checkin'});
    });
    const byDate=new Map();
    rows.forEach(x=>{
      if(!x.date)return;
      const prev=byDate.get(x.date);
      if(!prev||x.source==='measurement')byDate.set(x.date,x);
    });
    return [...byDate.values()].sort((a,b)=>a.date.localeCompare(b.date)).slice(-12);
  }

  function sparkV275(rows){
    if(!rows.length)return '<div class="v275-progress-empty"><strong>Sin registros de peso todavía</strong><span>Podés cargarlo desde Check-in / Seguimiento.</span></div>';
    const vals=rows.map(x=>x.weight);
    const w=420,h=82,p=8,min=Math.min(...vals),max=Math.max(...vals),span=Math.max(.5,max-min);
    const pts=vals.map((v,i)=>({
      x:p+(vals.length===1?(w-2*p)/2:i*(w-2*p)/(vals.length-1)),
      y:h-p-(v-min)/span*(h-2*p)
    }));
    return '<svg class="v275-spark" viewBox="0 0 '+w+' '+h+'" preserveAspectRatio="none" aria-label="Tendencia de peso">'+
      '<line class="v275-spark-axis" x1="'+p+'" y1="'+(h-p)+'" x2="'+(w-p)+'" y2="'+(h-p)+'"/>'+
      '<polyline class="v275-spark-line" points="'+pts.map(q=>q.x+','+q.y).join(' ')+'"/>'+
      pts.map(q=>'<circle class="v275-spark-point" cx="'+q.x+'" cy="'+q.y+'" r="3"/>').join('')+
      '</svg>';
  }

  function latestCheckinV275(){
    const cs=Array.isArray(trackingCache?.checkins)?trackingCache.checkins:[];
    return cs.slice().sort((a,b)=>String(b?.week_start||'').localeCompare(String(a?.week_start||'')))[0]||null;
  }

  function progressOverviewHtmlV275(){
    const s=student();
    const rows=trackingRowsV275();
    const first=rows[0],latest=rows[rows.length-1];
    const delta=first&&latest?latest.weight-first.weight:null;
    const done7=recentSessionCountV275(7);
    const planned=Math.max(1,Number(s?.plannedPerWeek)||s?.days?.length||1);
    const pct=Math.min(100,Math.round(done7/planned*100));
    const ci=latestCheckinV275();
    const adherence=Number(ci?.adherence_level);
    return '<div class="card v275-progress-overview" id="v275ProgressOverview">'+
      '<div class="v275-progress-head"><div><h3>Tu progreso</h3><p class="muted tiny">Evolución física, constancia y objetivo en una sola vista.</p></div><span class="badge red">Resumen</span></div>'+
      '<div class="v275-progress-grid">'+
        '<div class="v275-progress-panel v275-weight">'+
          '<span class="v275-label">Evolución del peso</span>'+
          '<div class="v275-weight-top">'+
            '<div><span class="v275-label">Actual</span><strong>'+(latest?latest.weight.toFixed(1)+' kg':'—')+'</strong></div>'+
            '<div><span class="v275-label">Inicio</span><strong>'+(first?first.weight.toFixed(1)+' kg':'—')+'</strong></div>'+
            '<div><span class="v275-label">Cambio</span><strong>'+(delta==null?'—':(delta>0?'+':'')+delta.toFixed(1)+' kg')+'</strong></div>'+
          '</div>'+sparkV275(rows)+
        '</div>'+
        '<div class="v275-progress-panel">'+
          '<span class="v275-label">Entrenamiento</span>'+
          '<strong class="v275-value">'+done7+'/'+planned+'</strong>'+
          '<small>sesiones en los últimos 7 días</small>'+
          '<div class="v275-progress-track"><span style="width:'+pct+'%"></span></div>'+
          '<small>'+pct+'% de la frecuencia semanal</small>'+
        '</div>'+
        '<div class="v275-progress-panel">'+
          '<span class="v275-label">Objetivo actual</span>'+
          '<strong class="v275-value" style="font-size:15px;line-height:1.2">'+esc(s?.goal||'Plan personalizado')+'</strong>'+
          '<small class="v275-goal-copy">'+(Number.isFinite(adherence)?'Última adherencia reportada: '+adherence+'/10. ':'')+'El progreso se interpreta junto con rendimiento, medidas y check-ins.</small>'+
        '</div>'+
      '</div>'+
    '</div>';
  }

  function injectProgressOverviewV275(){
    const coachView=mode==='coach'&&coachTab==='student'&&coachStudentTab==='progress';
    const studentView=mode==='student'&&studentTab==='progress';
    if(!coachView&&!studentView)return;
    const host=coachView?el('coachStudentBody'):el('studentSubBody');
    if(!host)return;
    el('v275ProgressOverview')?.remove();
    host.insertAdjacentHTML('afterbegin',progressOverviewHtmlV275());
  }

  let hydrateProgressV275=null;
  function hydrateProgressOverviewV275(){
    injectProgressOverviewV275();
    const aid=typeof trackingAthleteId==='function'?trackingAthleteId():null;
    if(!aid||typeof loadTracking!=='function'||!cloudEnabled)return;
    if(typeof trackingLoadedFor!=='undefined'&&trackingLoadedFor===aid){
      injectProgressOverviewV275();
      return;
    }
    if(hydrateProgressV275)return;
    hydrateProgressV275=Promise.resolve(loadTracking(false)).then(()=>{
      hydrateProgressV275=null;
      const stillCoach=mode==='coach'&&coachTab==='student'&&coachStudentTab==='progress';
      const stillStudent=mode==='student'&&studentTab==='progress';
      if(stillCoach||stillStudent)injectProgressOverviewV275();
    }).catch(()=>{hydrateProgressV275=null});
  }

  const baseRenderProgressV275=window.renderProgress||renderProgress;
  window.renderProgress=function(){
    const out=baseRenderProgressV275.apply(this,arguments);
    hydrateProgressOverviewV275();
    return out;
  };
  try{renderProgress=window.renderProgress}catch(_e){}

  window.__fjzV275={
    version:VERSION,
    premiumMobileHud:true,
    hudFourPrimaryActions:true,
    dedicatedTrainingHub:true,
    progressOverview:true,
    weightTrendOverview:true,
    weeklyTrainingProgress:true,
    goalContextWithoutBodyJudgement:true,
    noExtraTimers:true,
    noExtraListeners:true
  };
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-mobile-hud-progress" content="20.75">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.75 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-mobile-hud-progress" content="20.75"',
    "premiumMobileHud:true",
    "hudFourPrimaryActions:true",
    "dedicatedTrainingHub:true",
    "progressOverview:true",
    "weightTrendOverview:true",
    "weeklyTrainingProgress:true",
    "goalContextWithoutBodyJudgement:true",
    "v275-student-hud",
    "renderTrainingHubV275",
    "v275ProgressOverview",
    "Nutrición",
]:
    if marker not in html:
        raise RuntimeError("V20.75 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.75 mobile HUD + progress overview")
print("V20.75 BEFORE:",before)
print("V20.75 AFTER:",after)
print("V20.75 premium student HUD + training hub + visual progress overview; zero runtime topology growth")
