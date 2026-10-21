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

def edit_script(doc,script_id,transform):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m: raise RuntimeError("V20.54 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body: raise RuntimeError("V20.54 no script change")
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-student-week-flow" content="20.53"',
    "progressPulseFourWeeks:true",
    "function postRenderV175()",
    "normalizeExerciseTextV65"
]:
    if marker not in html:
        raise RuntimeError("V20.54 missing prerequisite: "+marker)

def patch_v175(body):
    anchor="  function postRenderV175(){"
    if body.count(anchor)!=1:
        raise RuntimeError("V20.54 postRender anchor mismatch")

    helpers=r"""
  /* ---------- Exercise Performance Progress V20.54 ---------- */
  function exerciseSetStatsV254(r){
    const sets=(r?.sets||[]).filter(x=>Array.isArray(x));
    const valid=sets.map(x=>({
      kg:Number(x?.[0]),
      reps:Number(x?.[1]),
      rir:Number(x?.[2])
    })).filter(x=>Number.isFinite(x.reps)&&x.reps>0);

    const weighted=valid.filter(x=>Number.isFinite(x.kg)&&x.kg>0);
    const best=weighted.slice().sort((a,b)=>b.kg-a.kg||b.reps-a.reps)[0]||null;
    return {
      setCount:valid.length,
      totalReps:valid.reduce((a,x)=>a+x.reps,0),
      volume:weighted.reduce((a,x)=>a+x.kg*x.reps,0),
      bestLoad:best?.kg??null,
      bestReps:best?.reps??null,
      weighted:weighted.length>0
    };
  }

  function exerciseProgressRowsV254(s=student()){
    const map=new Map();
    const sessions=(s?.sessions||[]).slice().sort(
      (a,b)=>(Date.parse(a?.date||0)||0)-(Date.parse(b?.date||0)||0)
    );

    sessions.forEach(ss=>{
      (ss?.exerciseResults||[]).forEach(r=>{
        if(!r?.name||!(r?.sets||[]).length)return;
        const key=typeof normalizeExerciseTextV65==='function'
          ?normalizeExerciseTextV65(r.name)
          :String(r.name).trim().toLowerCase();
        const stats=exerciseSetStatsV254(r);
        if(!stats.setCount)return;
        if(!map.has(key))map.set(key,{key,name:r.name,items:[]});
        map.get(key).items.push({
          date:ss.date,
          sessionId:ss.id,
          dayName:ss.dayName,
          loadMode:r.loadMode||'external',
          ...stats
        });
      });
    });

    return [...map.values()].map(row=>{
      const items=row.items;
      const latest=items[items.length-1];
      const recent=items.slice(-2);
      const previous=items.slice(-4,-2);
      const metric=(x)=>latest?.weighted?Number(x.volume||0):Number(x.totalReps||0);
      const avg=(arr)=>arr.length?arr.reduce((a,x)=>a+metric(x),0)/arr.length:null;
      const a=avg(recent),b=avg(previous);
      const pct=(a!=null&&b>0)?((a-b)/b*100):null;
      let trend='stable';
      if(pct!=null&&pct>=7)trend='up';
      else if(pct!=null&&pct<=-12)trend='down';

      return {
        ...row,
        latest,
        occurrences:items.length,
        trend,
        trendPct:pct,
        weighted:!!latest?.weighted,
        lastDate:latest?.date||null
      };
    }).sort((a,b)=>
      b.occurrences-a.occurrences||
      (Date.parse(b.lastDate||0)||0)-(Date.parse(a.lastDate||0)||0)
    );
  }

  function exerciseTrendLabelV254(row){
    if(row.trend==='up')return {cls:'good',label:'En progreso'};
    if(row.trend==='down')return {cls:'warn',label:'Revisar tendencia'};
    return {cls:'info',label:row.occurrences<3?'Pocos datos':'Estable'};
  }

  function exerciseMetricCopyV254(row){
    const x=row.latest||{};
    if(row.weighted&&x.bestLoad!=null){
      return {
        primary:round1(x.bestLoad)+' kg × '+Math.round(x.bestReps||0),
        secondary:'Volumen sesión '+Math.round(x.volume||0)+' kg·rep'
      };
    }
    return {
      primary:Math.round(x.totalReps||0)+' reps',
      secondary:Math.round(x.setCount||0)+' series registradas'
    };
  }

  function exerciseProgressCardV254(row){
    const t=exerciseTrendLabelV254(row),m=exerciseMetricCopyV254(row);
    const delta=row.trendPct==null?'':((row.trendPct>0?'+':'')+Math.round(row.trendPct)+'%');
    return '<button class="v254-exercise-card" onclick="showExerciseProgressV254(\''+esc(row.key)+'\')">'+
      '<div class="v254-exercise-head"><div><strong>'+esc(row.name)+'</strong>'+
      '<span>'+esc(fmtDate(row.lastDate))+' · '+row.occurrences+' registro'+(row.occurrences===1?'':'s')+'</span></div>'+
      '<span class="badge '+(t.cls==='good'?'green':t.cls==='warn'?'amber':'blue')+'">'+esc(t.label)+'</span></div>'+
      '<div class="v254-exercise-main"><strong>'+esc(m.primary)+'</strong>'+
      (delta?'<span class="'+esc(t.cls)+'">'+esc(delta)+' vs. bloque previo</span>':'<span>Comparación en construcción</span>')+'</div>'+
      '<div class="v254-exercise-foot">'+esc(m.secondary)+'</div>'+
    '</button>';
  }

  window.showExerciseProgressV254=function(key){
    const row=exerciseProgressRowsV254().find(x=>x.key===key);
    if(!row)return;
    const t=exerciseTrendLabelV254(row);
    const items=row.items.slice(-8).reverse();

    showModal(
      '<div class="modal-head"><div><h3>'+esc(row.name)+'</h3><div class="muted tiny">Historial de rendimiento · últimas '+items.length+' apariciones</div></div>'+
      '<button class="btn small" type="button" aria-label="Cerrar" title="Cerrar" onclick="closeModal()">✕</button></div>'+
      '<div class="v254-detail-head"><span class="badge '+(t.cls==='good'?'green':t.cls==='warn'?'amber':'blue')+'">'+esc(t.label)+'</span>'+
      '<p>La tendencia compara rendimiento reciente con registros anteriores del mismo ejercicio. Es una señal de seguimiento, no una obligación de subir carga.</p></div>'+
      '<div class="v254-detail-list">'+items.map(x=>{
        const metric=row.weighted
          ?(x.bestLoad!=null?round1(x.bestLoad)+' kg × '+Math.round(x.bestReps||0):'—')
          :Math.round(x.totalReps||0)+' reps';
        const secondary=row.weighted
          ?Math.round(x.volume||0)+' kg·rep'
          :Math.round(x.setCount||0)+' series';
        return '<div class="v254-detail-row"><div><strong>'+esc(fmtDate(x.date))+'</strong><span>'+esc(x.dayName||'Sesión')+'</span></div>'+
          '<div><strong>'+esc(metric)+'</strong><span>'+esc(secondary)+'</span></div></div>';
      }).join('')+'</div>'
    );
  };

  function injectExerciseProgressV254(){
    const coachView=mode==='coach'&&coachTab==='student'&&coachStudentTab==='progress';
    const studentView=mode==='student'&&studentTab==='progress';
    if(!coachView&&!studentView)return;

    const host=el(coachView?'coachStudentBody':'studentSubBody');
    if(!host)return;
    el('v254ExerciseProgress')?.remove();

    const rows=exerciseProgressRowsV254().slice(0,8);
    const card=document.createElement('section');
    card.id='v254ExerciseProgress';
    card.className='card v254-exercise-progress';
    card.innerHTML=
      '<div class="section-title v254-title"><div><div class="v225-section-kicker">FUERZA · HIPERTROFIA</div>'+
      '<h3>Progreso por ejercicio</h3><div class="muted tiny">Carga, repeticiones y volumen a partir de tus sesiones registradas.</div></div>'+
      '<span class="badge blue">'+rows.length+' ejercicios</span></div>'+
      (rows.length
        ?'<div class="v254-exercise-grid">'+rows.map(exerciseProgressCardV254).join('')+'</div>'
        :'<div class="empty">Todavía no hay suficientes sesiones para analizar ejercicios.</div>')+
      '<div class="v254-note">Las tendencias sirven para detectar evolución o necesidad de revisión. No modifican automáticamente la rutina ni las cargas programadas.</div>';

    const pulse=el('v249ProgressPulse');
    if(pulse)pulse.insertAdjacentElement('afterend',card);
    else host.prepend(card);
  }

"""
    body=body.replace(anchor,helpers+anchor,1)

    post_old="""    hydrateProgressPulseV249();"""
    post_new="""    hydrateProgressPulseV249();
    injectExerciseProgressV254();"""
    if body.count(post_old)!=1:
        raise RuntimeError("V20.54 progress postRender anchor mismatch: "+str(body.count(post_old)))
    body=body.replace(post_old,post_new,1)

    marker_old="""    studentFollowupUnified:true
  };"""
    marker_new="""    studentFollowupUnified:true,
    exercisePerformanceProgress:true,
    exerciseProgressReadOnly:true
  };"""
    if body.count(marker_old)!=1:
        raise RuntimeError("V20.54 marker mismatch")
    body=body.replace(marker_old,marker_new,1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

css=r"""
/* TEAM FJZ · V20.54 EXERCISE PERFORMANCE PROGRESS */
.v254-exercise-progress{
  margin-bottom:14px;
  border-color:#30343c;
}
.v254-title{align-items:flex-start}
.v254-exercise-grid{
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:8px;
}
.v254-exercise-card{
  appearance:none;
  width:100%;
  min-width:0;
  padding:11px;
  border:1px solid #2c3038;
  border-radius:12px;
  background:#0d0e12;
  color:inherit;
  text-align:left;
  cursor:pointer;
}
.v254-exercise-card:hover{border-color:#414650;background:#111318}
.v254-exercise-head{
  display:flex;
  justify-content:space-between;
  gap:8px;
  align-items:flex-start;
}
.v254-exercise-head>div{min-width:0}
.v254-exercise-head strong{
  display:block;color:#f2f3f5;font-size:11px;font-weight:880;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis
}
.v254-exercise-head>div>span{
  display:block;margin-top:3px;color:#858a95;font-size:8px
}
.v254-exercise-main{
  display:flex;
  justify-content:space-between;
  gap:8px;
  align-items:end;
  margin-top:10px;
}
.v254-exercise-main>strong{color:#fff;font-size:17px;font-weight:920}
.v254-exercise-main>span{color:#8e939d;font-size:8px;text-align:right}
.v254-exercise-main>span.good{color:#8fdcaf}
.v254-exercise-main>span.warn{color:#e7c274}
.v254-exercise-foot{
  margin-top:6px;color:#979ba5;font-size:8px;line-height:1.35
}
.v254-note{
  margin-top:9px;color:#7f848f;font-size:8px;line-height:1.45
}
.v254-detail-head{
  padding:10px;border:1px solid #2c3038;border-radius:10px;background:#0d0e12
}
.v254-detail-head p{margin:7px 0 0;color:#9499a3;font-size:9px;line-height:1.45}
.v254-detail-list{display:grid;gap:6px;margin-top:9px}
.v254-detail-row{
  display:grid;grid-template-columns:1fr 1fr;gap:8px;
  padding:9px 10px;border:1px solid #292d34;border-radius:9px;background:#101116
}
.v254-detail-row>div:last-child{text-align:right}
.v254-detail-row strong{display:block;color:#eef0f3;font-size:10px}
.v254-detail-row span{display:block;margin-top:3px;color:#858a95;font-size:8px}
@media(max-width:650px){
  .v254-exercise-grid{grid-template-columns:1fr}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V20.54 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-exercise-performance-progress" content="20.54">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.54 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-exercise-performance-progress" content="20.54"',
    "exerciseProgressRowsV254","injectExerciseProgressV254",
    "showExerciseProgressV254","FUERZA · HIPERTROFIA",
    "Progreso por ejercicio","exercisePerformanceProgress:true",
    "exerciseProgressReadOnly:true"
]:
    if marker not in html:
        raise RuntimeError("V20.54 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.54 exercise performance progress")
print("V20.54 BEFORE:",before)
print("V20.54 AFTER:",after)
print("V20.54 per-exercise load/reps/volume trends added; program authority unchanged")
