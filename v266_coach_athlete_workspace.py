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
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

def edit_script(doc,script_id,transform):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.66 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.66 no script change "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-release-candidate-geometry" content="20.65"',
    'meta name="fjz-profile-360" content="20.26"',
    "function ensureCoachHeroFrameV175()",
    "window.renderCoachSummary=function()",
    "coachFourWeekSnapshot:true",
    "coachWeeklyBrief:true"
]:
    if marker not in html:
        raise RuntimeError("V20.66 missing prerequisite: "+marker)

def patch_v175(body):
    # Insert workspace helpers before the canonical coach hero function.
    anchor="""  function ensureCoachHeroFrameV175(){
"""
    helpers=r"""  /* ---------- Coach athlete workspace V20.66 ---------- */
  function coachDaysSinceV266(v){
    if(!v)return null;
    const t=new Date(v).getTime();
    if(!Number.isFinite(t))return null;
    return Math.max(0,Math.floor((Date.now()-t)/86400000));
  }

  function coachWorkspaceMetricV266(label,value,sub=''){
    return '<div class="v266-context-metric"><span>'+esc(label)+'</span><strong>'+esc(String(value??'—'))+'</strong>'+
      (sub?'<small>'+esc(sub)+'</small>':'')+'</div>';
  }

  function coachWorkspaceHtmlV266(s){
    const status=statusFor(s);
    const adh=Number(adherence(s)||0);
    const days=coachDaysSinceV266(s?.lastWorkout);
    const last=days==null?'Sin registro':days===0?'Hoy':days===1?'Ayer':days+' días';
    const planned=Math.max(0,Number(s?.plannedPerWeek)||s?.days?.length||0);
    const statusTone=status==='Revisar'?'warn':status==='Progresando'?'good':'info';

    return '<div class="v266-context-main">'+
      coachWorkspaceMetricV266('Estado',status,statusTone==='warn'?'Requiere revisión':'Seguimiento actual')+
      coachWorkspaceMetricV266('Adherencia',adh+'%','Últimos 7 días')+
      coachWorkspaceMetricV266('Último entreno',last,s?.lastWorkout?fmtDate(s.lastWorkout):'Sin sesión')+
      coachWorkspaceMetricV266('Frecuencia',planned?planned+'x / semana':'—','Planificada')+
    '</div>'+
    '<div class="v266-quick-actions">'+
      '<button class="btn small" onclick="openCoachProfileTabV266(\'routine\')">Rutina</button>'+
      '<button class="btn small" onclick="openCoachProfileTabV266(\'tracking\')">Seguimiento</button>'+
      '<button class="btn small" onclick="openCoachProfileTabV266(\'nutrition\')">Nutrición</button>'+
      '<button class="btn small" onclick="openCoachProfileTabV266(\'agenda\')">Agenda</button>'+
    '</div>';
  }

  window.openCoachProfileTabV266=function(tab){
    coachStudentTab=tab||'summary';
    render();
  };

  function ensureCoachWorkspaceV266(hero,s){
    const info=hero?.querySelector('.v175-coach-profile-info');
    if(info&&!info.querySelector('.v266-profile-kicker')){
      info.insertAdjacentHTML('afterbegin','<div class="v266-profile-kicker">ATHLETE WORKSPACE · TEAM FJZ</div>');
    }

    let stateChip=info?.querySelector('.v266-profile-state');
    if(info&&!stateChip){
      stateChip=document.createElement('div');
      stateChip.className='v266-profile-state';
      const p=info.querySelector('p');
      if(p)p.insertAdjacentElement('afterend',stateChip);else info.appendChild(stateChip);
    }
    if(stateChip){
      const status=statusFor(s);
      stateChip.className='v266-profile-state '+(status==='Revisar'?'warn':status==='Progresando'?'good':'info');
      stateChip.textContent=status||'Seguimiento';
    }

    let bar=el('v266CoachWorkspace');
    if(!bar){
      bar=document.createElement('section');
      bar.id='v266CoachWorkspace';
      bar.className='v266-coach-workspace';
      hero.insertAdjacentElement('afterend',bar);
    }
    bar.innerHTML=coachWorkspaceHtmlV266(s);

    const tabs=el('coachStudentTabs')||hero.parentElement?.querySelector('.tabs');
    if(tabs)tabs.classList.add('v266-coach-tabs');
  }

"""
    if body.count(anchor)!=1:
        raise RuntimeError("V20.66 hero helper anchor mismatch")
    body=body.replace(anchor,helpers+anchor,1)

    # Enhance the existing stable hero after its canonical structure is resolved.
    hero_anchor="""    if(actions)actions.classList.add('v175-coach-profile-actions');

    const old=el('v70CoachStudentAvatar');
"""
    hero_repl="""    if(actions)actions.classList.add('v175-coach-profile-actions');
    ensureCoachWorkspaceV266(hero,s);

    const old=el('v70CoachStudentAvatar');
"""
    if body.count(hero_anchor)!=1:
        raise RuntimeError("V20.66 hero enhancement anchor mismatch")
    body=body.replace(hero_anchor,hero_repl,1)

    # Make the summary feel like a coach command surface rather than the old long card.
    old_head="""'<div class="v175-360-head"><div><h3>Resumen 360</h3><p>Una sola lectura del alumno: rendimiento, seguimiento, agenda y prioridades del coach.</p></div><span id="v175SummaryState" class="muted micro">Actualizando…</span></div>'+"""
    new_head="""'<div class="v175-360-head v266-command-head"><div><div class="v266-command-kicker">CONTROL DEL ALUMNO</div><h3>Panel de seguimiento</h3><p>Estado actual, evolución reciente y decisiones del Coach en una sola pantalla.</p></div><span id="v175SummaryState" class="muted micro">Actualizando…</span></div>'+"""
    if body.count(old_head)!=1:
        raise RuntimeError("V20.66 summary head mismatch")
    body=body.replace(old_head,new_head,1)

    body=body.replace(
      "<h4>Asistente Coach</h4><p>Prioriza decisiones concretas cruzando tendencia, entrenamiento, recuperación, nutrición, feedback y Agenda.</p>",
      "<div class=\"v266-section-kicker\">DECISIONES DEL COACH</div><h4>Recomendaciones y contexto</h4><p>Prioridades concretas cruzando entrenamiento, recuperación, nutrición, feedback y Agenda.</p>",
      1
    )
    body=body.replace(
      "<h4>Estado conectado</h4><p>Señales rápidas del check-in, nutrición, feedback y Agenda.</p>",
      "<div class=\"v266-section-kicker\">LECTURA RÁPIDA</div><h4>Estado actual</h4><p>Señales del check-in, nutrición, feedback y Agenda.</p>",
      1
    )
    body=body.replace(
      "<h4>Mensaje para el alumno</h4><p>Tu indicación general visible para este alumno.</p>",
      "<div class=\"v266-section-kicker\">COMUNICACIÓN</div><h4>Mensaje para el alumno</h4><p>Tu indicación general visible para este alumno.</p>",
      1
    )

    marker="""    coachFourWeekUsesExistingTracking:true
  };"""
    repl="""    coachFourWeekUsesExistingTracking:true,
    coachAthleteWorkspaceV266:true,
    coachWorkspaceQuickActions:true,
    coachProfileCommandCenter:true
  };"""
    if body.count(marker)!=1:
        raise RuntimeError("V20.66 marker mismatch")
    body=body.replace(marker,repl,1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

css=r"""
/* =========================================================
   TEAM FJZ · V20.66 COACH ATHLETE WORKSPACE
   ========================================================= */

/* The athlete identity should feel like a coach workspace, not a generic hero. */
.v175-coach-profile-hero{
  padding:20px!important;
  border-radius:18px!important;
  border-color:#323640!important;
  background:
    linear-gradient(110deg,rgba(255,38,57,.105),transparent 34%),
    linear-gradient(180deg,rgba(255,255,255,.022),transparent 58%),
    #0e0f13!important;
}
.v266-profile-kicker,
.v266-command-kicker,
.v266-section-kicker{
  color:#ff6674;
  font-size:8px;
  line-height:1.2;
  font-weight:950;
  letter-spacing:.15em;
  text-transform:uppercase;
}
.v266-profile-kicker{margin-bottom:6px}
.v175-coach-profile-info h2{
  margin:0 0 5px!important;
  font-size:28px!important;
  letter-spacing:-.035em!important;
}
.v175-coach-profile-info p{
  max-width:680px;
  color:#a4a8b2!important;
  font-size:11px!important;
}
.v266-profile-state{
  display:inline-flex;
  align-items:center;
  min-height:24px;
  margin-top:8px;
  padding:4px 8px;
  border:1px solid #343943;
  border-radius:999px;
  background:#101217;
  color:#aeb3bd;
  font-size:8px;
  line-height:1;
  font-weight:900;
  letter-spacing:.04em;
}
.v266-profile-state.warn{
  color:#ffd0d4;
  border-color:rgba(255,70,87,.34);
  background:rgba(255,70,87,.075);
}
.v266-profile-state.good{
  color:#bef2d5;
  border-color:rgba(59,213,138,.28);
  background:rgba(59,213,138,.06);
}

.v175-coach-profile-actions{
  align-self:start!important;
  padding-top:4px;
}
.v175-coach-profile-actions .btn{
  min-height:36px!important;
  border-radius:10px!important;
}

/* New persistent coach context strip, visible on every athlete tab. */
#v266CoachWorkspace{
  display:grid;
  grid-template-columns:minmax(0,1fr) auto;
  gap:12px;
  align-items:stretch;
  margin:10px 0 9px;
  padding:10px;
  border:1px solid #2d3139;
  border-radius:14px;
  background:#0d0e12;
}
.v266-context-main{
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:7px;
  min-width:0;
}
.v266-context-metric{
  min-width:0;
  min-height:58px;
  padding:9px 10px;
  border:1px solid #272b32;
  border-radius:10px;
  background:#101116;
}
.v266-context-metric>span{
  display:block;
  color:#7f8590;
  font-size:7px;
  font-weight:900;
  letter-spacing:.08em;
  text-transform:uppercase;
}
.v266-context-metric>strong{
  display:block;
  margin-top:4px;
  color:#f2f4f7;
  font-size:13px;
  line-height:1.15;
  font-weight:920;
  font-variant-numeric:tabular-nums;
}
.v266-context-metric>small{
  display:block;
  margin-top:4px;
  color:#858b95;
  font-size:7px;
  line-height:1.25;
}
.v266-quick-actions{
  display:grid;
  grid-template-columns:repeat(2,minmax(76px,1fr));
  gap:6px;
  align-content:center;
}
.v266-quick-actions .btn{
  min-height:29px;
  padding:5px 8px;
  font-size:8px;
  border-radius:9px;
}

/* Tabs become a clear secondary navigation surface. */
.v266-coach-tabs,
#coachStudentTabs{
  position:relative;
  margin:0 0 12px!important;
  padding:5px!important;
  gap:4px!important;
  border:1px solid #2b2f37;
  border-radius:12px!important;
  background:#0c0d10;
}
.v266-coach-tabs .tab,
#coachStudentTabs .tab{
  min-height:34px;
  border-radius:9px!important;
  font-size:9px!important;
  font-weight:820!important;
}
.v266-coach-tabs .tab.active,
#coachStudentTabs .tab.active{
  background:linear-gradient(180deg,rgba(255,50,70,.16),rgba(255,50,70,.075))!important;
  border-color:rgba(255,65,82,.32)!important;
  color:#fff!important;
}

/* Summary = command center. */
#v175Coach360{
  grid-template-columns:repeat(12,minmax(0,1fr));
  gap:11px!important;
  padding:0!important;
  border:0!important;
  background:transparent!important;
  box-shadow:none!important;
  contain:layout style;
}
#v175Coach360>.v175-360-head,
#v175Coach360>#v175Metrics,
#v175Coach360>.v175-360-section{
  grid-column:1/-1;
}
#v175Coach360>.v175-360-head{
  padding:16px 17px;
  border:1px solid #30343c;
  border-radius:16px;
  background:
    linear-gradient(120deg,rgba(255,38,57,.065),transparent 36%),
    #101116;
}
.v266-command-head h3{
  margin-top:4px!important;
  font-size:22px!important;
}
.v266-command-head p{
  max-width:720px;
  font-size:10px!important;
}

/* Main metrics read like a dashboard rather than six generic boxes. */
#v175Metrics{
  gap:8px!important;
}
#v175Metrics .v175-360-metric{
  min-height:86px!important;
  padding:12px!important;
  border-radius:12px!important;
  background:#101116!important;
}
#v175Metrics .v175-360-metric:first-child{
  border-color:rgba(255,60,78,.30)!important;
  background:linear-gradient(145deg,rgba(255,38,57,.07),transparent 54%),#101116!important;
}
#v175Metrics .v175-360-metric:nth-child(2){
  border-color:rgba(103,173,255,.24)!important;
  background:linear-gradient(145deg,rgba(103,173,255,.055),transparent 54%),#101116!important;
}

/* 28-day snapshot + weekly brief become the first decision row. */
#v260CoachFourWeek{
  grid-column:span 7!important;
  margin:0!important;
}
#v250CoachWeeklyBrief{
  grid-column:span 5!important;
  margin:0!important;
}
#v260CoachFourWeek,
#v250CoachWeeklyBrief{
  padding:14px!important;
  border:1px solid #2e323a!important;
  border-radius:15px!important;
}

/* Other sections get proper card separation instead of one long stacked panel. */
#v175Coach360>.v175-360-section{
  padding:14px!important;
  border:1px solid #2a2e35!important;
  border-radius:15px!important;
  background:#0f1014!important;
}
#v175Coach360>.v175-360-section-head{
  border:0;
}
.v266-section-kicker{margin-bottom:4px}

.v237-review-section{
  border-color:rgba(255,70,87,.18)!important;
}
.v175-message{
  min-height:64px!important;
  padding:13px!important;
}

@media(max-width:980px){
  #v266CoachWorkspace{
    grid-template-columns:1fr;
  }
  .v266-quick-actions{
    grid-template-columns:repeat(4,minmax(0,1fr));
  }
  #v260CoachFourWeek,
  #v250CoachWeeklyBrief{
    grid-column:1/-1!important;
  }
}

@media(max-width:760px){
  .v175-coach-profile-hero{
    padding:15px!important;
  }
  .v175-coach-profile-info h2{
    font-size:23px!important;
  }
  #v266CoachWorkspace{
    padding:8px;
    border-radius:12px;
  }
  .v266-context-main{
    grid-template-columns:1fr 1fr;
  }
  .v266-quick-actions{
    grid-template-columns:1fr 1fr;
  }
  .v266-coach-tabs,
  #coachStudentTabs{
    overflow-x:auto;
    overscroll-behavior-x:contain;
    scrollbar-width:none;
    white-space:nowrap;
  }
  .v266-coach-tabs::-webkit-scrollbar,
  #coachStudentTabs::-webkit-scrollbar{display:none}
  .v266-coach-tabs .tab,
  #coachStudentTabs .tab{
    flex:0 0 auto;
  }
  #v175Coach360>.v175-360-head{
    padding:14px;
  }
}

@media(max-width:420px){
  .v175-coach-profile-hero{
    grid-template-columns:58px minmax(0,1fr)!important;
  }
  #v175CoachAvatarSlot,
  #v175CoachAvatarSlot .v70-avatar.big{
    width:58px!important;
    height:58px!important;
  }
  .v175-coach-profile-info h2{
    font-size:20px!important;
  }
  .v266-context-metric{
    min-height:54px;
    padding:8px;
  }
  .v266-context-metric>strong{font-size:12px}
  .v266-command-head h3{font-size:19px!important}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.66 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-coach-athlete-workspace" content="20.66">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.66 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-coach-athlete-workspace" content="20.66"',
    "coachAthleteWorkspaceV266:true",
    "coachWorkspaceQuickActions:true",
    "coachProfileCommandCenter:true",
    "ATHLETE WORKSPACE · TEAM FJZ",
    "CONTROL DEL ALUMNO",
    "v266CoachWorkspace",
    "openCoachProfileTabV266",
    "#v260CoachFourWeek",
    "#v250CoachWeeklyBrief"
]:
    if marker not in html:
        raise RuntimeError("V20.66 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.66 coach athlete workspace")
print("V20.66 BEFORE:",before)
print("V20.66 AFTER:",after)
print("V20.66 coach profile visibly redesigned with persistent context + command-center summary; runtime topology unchanged")
