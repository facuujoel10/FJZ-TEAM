import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.5 CANONICAL WORKOUT COMPLETION + PROGRESS VISUALS
# =========================================================

# 1) A draft is invalid if that day already has a completed session newer
#    than the draft. This prevents stale local/cloud drafts from restoring
#    old weights after a successful save.
restore_pat=re.compile(
r"""  function restoreDraftV145\(i\)\{
    const s=student\?\.\(\),d=s\?\.days\?\.\[i\];
    if\(!s\|\|!d\)return null;
    let p=freshestV145\(readLocalV145\(s,d\),readCloudV145\(s,d\)\);
    if\(!validForDayV145\(p,s,d\)\)return null;
    p=pruneForDayV145\(p,d\);
    if\(!meaningfulV145\(p\)\)return null;
    return p;
  \}"""
)
restore_repl=r"""  function restoreDraftV145(i){
    const s=student?.(),d=s?.days?.[i];
    if(!s||!d)return null;
    let p=freshestV145(readLocalV145(s,d),readCloudV145(s,d));
    if(!validForDayV145(p,s,d))return null;

    const draftAt=Date.parse(p.updatedAt||0)||0;
    const lastSaved=(s.sessions||[])
      .filter(x=>x?.dayId===d.id&&x?.date)
      .reduce((m,x)=>Math.max(m,Date.parse(x.date)||0),0);

    if(lastSaved&&draftAt&&lastSaved>=draftAt){
      try{localStorage.removeItem(localKeyV145(s,d))}catch(_e){}
      if(s.workoutDrafts?.[d.id]){
        delete s.workoutDrafts[d.id];
        if(!Object.keys(s.workoutDrafts).length)delete s.workoutDrafts;
      }
      return null;
    }

    p=pruneForDayV145(p,d);
    if(!meaningfulV145(p))return null;
    return p;
  }"""
html,n_restore=restore_pat.subn(restore_repl,html,count=1)
if n_restore!=1:
    raise RuntimeError(f"V20.5 restoreDraftV145 replacement mismatch: {n_restore}")

# Export the canonical draft clear helper from V14.5.
needle="  window.resumeWorkoutDraftV145=function(dayId){"
if html.count(needle)!=1:
    raise RuntimeError("V20.5 resume draft anchor missing")
html=html.replace(
    needle,
    "  window.__fjzClearWorkoutDraftV205=clearDraftV145;\n\n"+needle,
    1
)

# Export the FINAL V10.6/V20.2 save primitives from inside their closure.
start=html.find('<script id="v106PartialSessionsRuntime">')
end=html.find('</script>',start)
if start<0 or end<0:
    raise RuntimeError("V20.5 V106 runtime not found")
block=html[start:end]
close_at=block.rfind('})();')
if close_at<0:
    raise RuntimeError("V20.5 V106 closure end not found")
exports=r"""
  window.__fjzSessionDraftV205=sessionDraftV106;
  window.__fjzSaveSessionV205=saveSessionV106;
"""
block=block[:close_at]+exports+block[close_at:]
html=html[:start]+block+html[end:]

css=r"""
<style id="v205CanonicalWorkoutProgressStyles">
/* Clear distinction: previous load is reference, never an entered value. */
.v205-prev-load{
  display:block;
  margin:2px 0 5px;
  font-size:8px;
  line-height:1.2;
  font-weight:750;
  color:var(--muted);
  white-space:nowrap;
}
.v205-prev-load strong{color:rgba(255,255,255,.82);font-weight:850}
.v205-method-reference{
  margin:0 0 10px;
  padding:9px 10px;
  border:1px solid rgba(255,255,255,.08);
  border-left:3px solid rgba(255,45,58,.65);
  border-radius:10px;
  background:rgba(255,255,255,.018);
  font-size:9px;
  line-height:1.5;
  color:var(--muted);
}
.v205-method-reference strong{color:var(--text)}
.v205-method-reference .v205-ref-row{margin-top:3px}

/* Save is terminal once accepted. */
body.v205-workout-committing button[onclick*="finishWorkout"],
body.v205-workout-committing button[onclick*="confirmPartialSessionV106"]{
  pointer-events:none!important;
  opacity:.58!important;
}

/* Professional progress charts. */
.v205-chart{
  border:1px solid rgba(255,255,255,.075);
  border-radius:16px;
  background:linear-gradient(180deg,rgba(255,255,255,.025),rgba(255,255,255,.01));
  padding:14px;
  overflow:hidden;
}
.v205-chart-head{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:12px;
  margin-bottom:8px;
}
.v205-chart-title{font-size:11px;font-weight:850}
.v205-chart-sub{font-size:8px;color:var(--muted);margin-top:3px}
.v205-chart-kpis{
  display:flex;
  gap:6px;
  flex-wrap:wrap;
  justify-content:flex-end;
}
.v205-chart-kpi{
  min-width:74px;
  padding:6px 8px;
  border:1px solid rgba(255,255,255,.07);
  border-radius:9px;
  background:rgba(255,255,255,.02);
  text-align:right;
}
.v205-chart-kpi span{display:block;font-size:7px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.v205-chart-kpi strong{display:block;margin-top:2px;font-size:10px}
.v205-chart-svg{
  width:100%;
  height:auto;
  min-height:190px;
  display:block;
}
.v205-grid-line{stroke:rgba(255,255,255,.065);stroke-width:1}
.v205-axis-label{fill:rgba(255,255,255,.42);font-size:9px;font-weight:700}
.v205-line{
  fill:none;
  stroke:#ff3447;
  stroke-width:3.2;
  stroke-linecap:round;
  stroke-linejoin:round;
  vector-effect:non-scaling-stroke;
}
.v205-area{opacity:.16}
.v205-point{
  fill:#101014;
  stroke:#ff3447;
  stroke-width:3;
  vector-effect:non-scaling-stroke;
}
.v205-point-last{fill:#ff3447;stroke:#fff;stroke-width:2}
.v205-value-label{fill:rgba(255,255,255,.88);font-size:9px;font-weight:850}
.metric-grid .metric{
  border:1px solid rgba(255,255,255,.065);
  border-radius:11px;
  background:rgba(255,255,255,.018);
  padding:10px;
}
@media(max-width:560px){
  .v205-chart{padding:11px}
  .v205-chart-head{display:block}
  .v205-chart-kpis{justify-content:flex-start;margin-top:8px}
  .v205-chart-kpi{text-align:left}
  .v205-chart-svg{min-height:170px}
}
</style>
"""

js=r"""
<script id="v205CanonicalWorkoutProgressRuntime">
(function(){
  const VERSION='20.5';
  const CLOSED_PREFIX='fjz_v205_closed:';
  let commitBusyV205=false;

  function cloneV205(x){
    try{return JSON.parse(JSON.stringify(x))}catch(_e){return x}
  }
  function escV205(v){return esc(String(v??''))}
  function closedKeyV205(sid,dayId){return CLOSED_PREFIX+String(sid||'student')+':'+String(dayId||'day')}

  function readClosedV205(sid,dayId){
    try{return JSON.parse(localStorage.getItem(closedKeyV205(sid,dayId))||'null')}catch(_e){return null}
  }
  function setClosedV205(s,dayId,session){
    if(!s||!dayId)return;
    const marker={studentId:s.id,dayId,sessionId:session?.id||null,at:new Date().toISOString()};
    try{localStorage.setItem(closedKeyV205(s.id,dayId),JSON.stringify(marker))}catch(_e){}
    window.__fjzClosedWorkoutV205=marker;
  }
  function clearClosedV205(s,dayId){
    if(!s||!dayId)return;
    try{localStorage.removeItem(closedKeyV205(s.id,dayId))}catch(_e){}
    window.__fjzClosedWorkoutV205=null;
  }
  function isClosedV205(s,d){
    if(!s||!d)return false;
    const m=readClosedV205(s.id,d.id);
    if(!m)return false;
    if(m.sessionId&&(s.sessions||[]).some(x=>x?.id===m.sessionId))return true;
    const age=Date.now()-(Date.parse(m.at||0)||0);
    return age>=0&&age<6*60*60*1000;
  }

  function compactMethodLogV205(e){
    const x=window.__fjzMethodDraftV110?.[e?.uid];
    if(!x||!e?.method||e.method==='normal')return null;
    const sets={};
    Object.entries(x.sets||{}).forEach(([si,row])=>{
      const clean={};
      Object.entries(row||{}).forEach(([k,v])=>{
        const n=Number(v);
        if(Number.isFinite(n)&&n>=0)clean[k]=n;
      });
      if(Object.keys(clean).length)sets[si]=clean;
    });
    const note=String(x.note||'').trim();
    if(!Object.keys(sets).length&&!note)return null;
    return {type:e.method,methodNote:e.methodNote||'',sets,note};
  }

  function attachMethodHistoryV205(pack,session){
    if(!pack||!session)return;
    (session.exerciseResults||[]).forEach(r=>{
      const e=(pack.d?.exercises||[]).find(x=>x.uid===r.exerciseUid);
      if(!e)return;
      const log=compactMethodLogV205(e);
      if(!log)return;
      r.methodLog=cloneV205(log);
      if(r.completed&&e.history?.length){
        e.history[e.history.length-1].methodLog=cloneV205(log);
      }
    });
    try{saveState()}catch(_e){}
  }

  function terminalCloseV205(pack,session){
    const s=pack?.s||student?.();
    const d=pack?.d;
    if(!s||!d)return;

    setClosedV205(s,d.id,session);
    window.__v106PendingSession=null;
    window.__fjzPendingSavedSessionV190=null;
    window.__fjzPendingDraftClearV190=null;

    try{
      window.__fjzClearWorkoutDraftV205?.(d.id,false);
      workoutDraft={};
      window.__fjzMethodDraftV110={};
      saveState();
    }catch(_e){}

    try{closeModal?.()}catch(_e){}
    studentTab='home';
    currentDay=-1;
    render();
    toast('Sesión guardada');
    commitBusyV205=false;
    document.body?.classList.remove('v205-workout-committing');
  }

  function commitPackV205(pack){
    if(commitBusyV205||!pack)return;
    commitBusyV205=true;
    document.body?.classList.add('v205-workout-committing');
    try{
      const session=window.__fjzSaveSessionV205?.(pack);
      if(!session)throw new Error('No se pudo crear la sesión');
      attachMethodHistoryV205(pack,session);
      terminalCloseV205(pack,session);
    }catch(e){
      console.error('TEAM FJZ V20.5 save error',e);
      commitBusyV205=false;
      document.body?.classList.remove('v205-workout-committing');
      toast('No se pudo guardar la sesión');
    }
  }

  // Canonical final save flow. It bypasses every historical finish wrapper.
  window.finishWorkout=function(){
    if(commitBusyV205)return;
    const pack=window.__fjzSessionDraftV205?.();
    if(!pack?.d)return;
    if(!pack.d.exercises?.length){
      studentTab='home';currentDay=-1;render();return;
    }
    if(!pack.registered?.length){
      toast('Cargá al menos una serie para guardar la sesión');
      return;
    }

    const partial=(pack.registered||[]).filter(x=>!x.complete);
    const missing=(pack.skipped||[]).length+partial.length;
    if(!missing){
      commitPackV205(pack);
      return;
    }

    window.__v106PendingSession=pack;
    const parts=[];
    if(pack.skipped?.length)parts.push(pack.skipped.length+' ejercicio'+(pack.skipped.length===1?'':'s')+' sin cargar');
    if(partial.length)parts.push(partial.length+' ejercicio'+(partial.length===1?'':'s')+' incompleto'+(partial.length===1?'':'s'));

    showModal(
      '<div class="modal-head"><div><h3>Finalizar entrenamiento</h3><div class="muted tiny">Podés guardar lo que completaste y cerrar esta sesión.</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="card"><strong>'+escV205(parts.join(' · '))+'</strong><div class="muted tiny" style="margin-top:6px">Solo se guardan las series con datos válidos.</div></div>'+
      '<div class="pill-row" style="justify-content:flex-end;margin-top:12px"><button class="btn" onclick="closeModal()">Seguir entrenando</button><button class="btn primary" onclick="confirmPartialSessionV106()">Guardar y finalizar</button></div>'
    );
  };
  try{finishWorkout=window.finishWorkout}catch(_e){}

  window.confirmPartialSessionV106=function(){
    if(commitBusyV205)return;
    const pack=window.__v106PendingSession;
    window.__v106PendingSession=null;
    if(!pack){closeModal?.();return}
    commitPackV205(pack);
  };
  try{confirmPartialSessionV106=window.confirmPartialSessionV106}catch(_e){}

  // Explicitly starting a new workout re-arms that day.
  const baseStartV205=window.startWorkout||globalThis.startWorkout;
  if(typeof baseStartV205==='function'){
    const wrapped=function(i){
      const s=student?.(),d=s?.days?.[i];
      if(s&&d)clearClosedV205(s,d.id);
      commitBusyV205=false;
      document.body?.classList.remove('v205-workout-committing');
      window.__v106PendingSession=null;
      return baseStartV205.apply(this,arguments);
    };
    window.startWorkout=wrapped;
    try{startWorkout=wrapped}catch(_e){}
  }

  // Absolute guard against a late realtime/render reopening a completed workout.
  const baseRenderWorkoutV205=window.renderWorkout||globalThis.renderWorkout;
  if(typeof baseRenderWorkoutV205==='function'){
    const wrapped=function(){
      const s=student?.(),d=s?.days?.[currentDay];
      if(s&&d&&isClosedV205(s,d)){
        studentTab='home';currentDay=-1;
        return (window.renderStudent||globalThis.renderStudent)?.();
      }
      return baseRenderWorkoutV205.apply(this,arguments);
    };
    window.renderWorkout=wrapped;
    try{renderWorkout=wrapped}catch(_e){}
  }

  // -------------------------------------------------------
  // Workout UI: force historical weights to REFERENCE ONLY.
  // -------------------------------------------------------
  function methodReferenceV205(e){
    const log=latestHistory(e)?.methodLog;
    if(!log)return '';
    const labels={
      d1:'Descenso 1',d2:'Descenso 2',d3:'Descenso 3',
      rp1:'RP 1',rp2:'RP 2',b:'Ejercicio B',
      myo1:'Miniset 1',myo2:'Miniset 2',myo3:'Miniset 3',
      cl1:'Bloque 1',cl2:'Bloque 2',cl3:'Bloque 3'
    };
    const rows=[];
    Object.entries(log.sets||{}).forEach(([si,vals])=>{
      const bits=[];
      Object.entries(labels).forEach(([key,label])=>{
        const kg=vals?.[key+'kg'],reps=vals?.[key+'reps'];
        if(kg!==undefined||reps!==undefined){
          bits.push(label+': '+(kg!==undefined?kg+' kg':'—')+(reps!==undefined?' × '+reps:''));
        }
      });
      if(bits.length)rows.push('<div class="v205-ref-row">S'+(Number(si)+1)+' · '+escV205(bits.join(' · '))+'</div>');
    });
    if(!rows.length)return '';
    return '<div class="v205-method-reference"><strong>Referencia método anterior</strong>'+rows.join('')+'</div>';
  }

  const baseExerciseV205=window.workoutExercise||globalThis.workoutExercise;
  if(typeof baseExerciseV205==='function'){
    const wrapped=function(e,i){
      const out=baseExerciseV205.apply(this,arguments);
      const tpl=document.createElement('template');
      tpl.innerHTML=String(out||'');

      const prev=latestHistory(e)?.sets||[];
      const activeDraft=workoutDraft?.[e.uid]||null;
      const card=tpl.content.querySelector('.session-card');

      card?.querySelectorAll('.set-grid').forEach((grid,si)=>{
        const label=grid.querySelector('label');
        const input=label?.querySelector('input');
        if(!label||!input)return;

        // A fresh workout must NEVER visually inherit the previous Kg.
        const entered=activeDraft?.[si]?.[0];
        if(!(Number.isFinite(Number(entered))&&Number(entered)!==0)){
          input.value='';
          input.setAttribute('value','');
        }

        if(!label.querySelector('.v205-prev-load')){
          const kg=Number(prev?.[si]?.[0]??prev?.[prev.length-1]?.[0]);
          const ref=document.createElement('span');
          ref.className='v205-prev-load';
          ref.innerHTML=Number.isFinite(kg)&&kg>0
            ? 'Anterior: <strong>'+escV205(kg)+' kg</strong>'
            : (Number.isFinite(kg)&&kg===0?'Anterior: <strong>peso corporal</strong>':'Sin carga anterior');
          label.insertBefore(ref,input);
        }
        input.placeholder='Ingresá kg';
      });

      const methodPanel=tpl.content.querySelector('.v137-method-panel');
      if(methodPanel){
        methodPanel.querySelectorAll('.v137-method-prev').forEach(n=>n.remove());
        const refHtml=methodReferenceV205(e);
        if(refHtml){
          const head=methodPanel.querySelector('.v137-method-head');
          head?.insertAdjacentHTML('afterend',refHtml);
        }
        methodPanel.querySelectorAll('input[type="number"]').forEach(inp=>{
          if(!inp.value)inp.placeholder=inp.closest('label')?.textContent?.includes('Reps')?'Reps':'Kg';
        });
      }

      return tpl.innerHTML;
    };
    window.workoutExercise=wrapped;
    try{workoutExercise=wrapped}catch(_e){}
  }

  // -------------------------------------------------------
  // Professional progress charts.
  // -------------------------------------------------------
  function n1V205(v){return Math.round(Number(v)*10)/10}
  function dateV205(v){
    if(!v)return '';
    const d=new Date(v);
    if(Number.isNaN(d.getTime()))return String(v).slice(5,10);
    return d.toLocaleDateString('es-AR',{day:'2-digit',month:'2-digit'});
  }
  function deltaTextV205(d,unit){
    if(!Number.isFinite(d))return '—';
    return (d>0?'+':'')+n1V205(d)+(unit?' '+unit:'');
  }

  function proChartV205(values,dates,label,unit,id){
    if(values.length<2)return '<div class="empty">Necesitamos al menos 2 registros para mostrar la tendencia.</div>';
    const w=720,h=250,l=44,r=18,t=28,b=38;
    const min0=Math.min(...values),max0=Math.max(...values);
    const margin=Math.max((max0-min0)*.16,unit==='kg'?.5:1);
    const min=min0-margin,max=max0+margin,span=Math.max(.001,max-min);
    const pts=values.map((v,i)=>({
      x:l+(w-l-r)*(i/Math.max(1,values.length-1)),
      y:t+(h-t-b)*(1-(v-min)/span),
      v
    }));
    const line=pts.map(p=>p.x+','+p.y).join(' ');
    const area=l+','+(h-b)+' '+line+' '+(w-r)+','+(h-b);
    const change=values[values.length-1]-values[0];
    const best=Math.max(...values);
    const grad='v205grad_'+String(id||label).replace(/[^a-z0-9]/gi,'_');
    const grid=[0,.25,.5,.75,1].map(q=>{
      const y=t+(h-t-b)*q;
      const val=max-(span*q);
      return '<line class="v205-grid-line" x1="'+l+'" y1="'+y+'" x2="'+(w-r)+'" y2="'+y+'"/>'+
        '<text class="v205-axis-label" x="'+(l-7)+'" y="'+(y+3)+'" text-anchor="end">'+n1V205(val)+'</text>';
    }).join('');
    const labelIndexes=[0,Math.floor((values.length-1)/2),values.length-1].filter((v,i,a)=>a.indexOf(v)===i);
    const xlabels=labelIndexes.map(i=>'<text class="v205-axis-label" x="'+pts[i].x+'" y="'+(h-10)+'" text-anchor="middle">'+escV205(dates[i]||String(i+1))+'</text>').join('');
    const points=pts.map((p,i)=>'<circle class="v205-point '+(i===pts.length-1?'v205-point-last':'')+'" cx="'+p.x+'" cy="'+p.y+'" r="'+(i===pts.length-1?5:3.5)+'"/>'+
      (i===pts.length-1?'<text class="v205-value-label" x="'+p.x+'" y="'+Math.max(14,p.y-11)+'" text-anchor="middle">'+n1V205(p.v)+(unit?' '+unit:'')+'</text>':'')).join('');

    return '<div class="v205-chart">'+
      '<div class="v205-chart-head"><div><div class="v205-chart-title">'+escV205(label)+'</div><div class="v205-chart-sub">'+values.length+' registros · evolución cronológica</div></div>'+
      '<div class="v205-chart-kpis">'+
        '<div class="v205-chart-kpi"><span>Actual</span><strong>'+n1V205(values.at(-1))+(unit?' '+unit:'')+'</strong></div>'+
        '<div class="v205-chart-kpi"><span>Cambio</span><strong>'+deltaTextV205(change,unit)+'</strong></div>'+
        '<div class="v205-chart-kpi"><span>Máximo</span><strong>'+n1V205(best)+(unit?' '+unit:'')+'</strong></div>'+
      '</div></div>'+
      '<svg class="v205-chart-svg" viewBox="0 0 '+w+' '+h+'" preserveAspectRatio="xMidYMid meet">'+
        '<defs><linearGradient id="'+grad+'" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#ff3447" stop-opacity=".58"/><stop offset="100%" stop-color="#ff3447" stop-opacity="0"/></linearGradient></defs>'+
        grid+'<polygon class="v205-area" points="'+area+'" fill="url(#'+grad+')"/><polyline class="v205-line" points="'+line+'"/>'+points+xlabels+
      '</svg></div>';
  }

  window.progressChart=function(e,metric){
    const rows=(e?.history||[]).slice(-12);
    const vals=rows.map(x=>{
      if(metric==='volume')return x.sets.reduce((a,s)=>a+Number(s[0]||0)*Number(s[1]||0),0);
      if(metric==='reps')return x.sets.reduce((a,s)=>a+Number(s[1]||0),0);
      return Math.max(...x.sets.map(s=>Number(s[0]||0)));
    });
    const dates=rows.map(x=>dateV205(x.date));
    const label=metric==='load'?'Carga máxima':metric==='volume'?'Volumen total':'Repeticiones totales';
    const unit=metric==='load'?'kg':metric==='volume'?'kg':'reps';
    return proChartV205(vals,dates,label,unit,'exercise_'+metric);
  };
  try{progressChart=window.progressChart}catch(_e){}

  window.simpleLineChart=function(rows,key,label){
    const pts=(rows||[]).filter(x=>x?.[key]!=null).slice(0,12).reverse();
    if(pts.length<2)return '<div class="empty">Necesitamos al menos 2 registros para mostrar la tendencia.</div>';
    const vals=pts.map(x=>Number(x[key]));
    const dates=pts.map(x=>dateV205(x.measured_on||x.week_start||x.submitted_at||x.created_at));
    const unit=/weight|kg/i.test(key)?'kg':/cm|waist|hip|chest|abd/i.test(key)?'cm':'';
    return proChartV205(vals,dates,label,unit,'simple_'+key);
  };
  try{simpleLineChart=window.simpleLineChart}catch(_e){}

  window.__fjzV205={
    version:VERSION,
    canonicalSaveFlow:true,
    staleDraftRejectedAfterSavedSession:true,
    cloudDraftRemovedAtomically:true,
    previousWeightReferenceOnly:true,
    methodPreviousReference:true,
    professionalProgressCharts:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

# Consolidate styles.
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
mergeable=[]
for m in styles:
    attrs=m.group("attrs") or ""
    if re.search(r"\b(media|nonce)\s*=",attrs,re.I):continue
    mergeable.append(m)
if len(mergeable)>1:
    chunks=[]
    for m in mergeable:
        ident=re.search(r'id=["\']([^"\']+)["\']',m.group("attrs") or "",re.I)
        name=ident.group(1) if ident else "anonymous"
        chunks.append("\n/* --- "+name+" --- */\n"+m.group("body").strip())
    for m in reversed(mergeable):
        html=html[:m.start()]+html[m.end():]
    html=html.replace("</head>",'<style id="fjzProductionStylesV205">'+''.join(chunks)+'\n</style>\n</head>',1)

critical=[
  "__fjzSessionDraftV205",
  "__fjzSaveSessionV205",
  "__fjzClearWorkoutDraftV205",
  "canonicalSaveFlow:true",
  "staleDraftRejectedAfterSavedSession:true",
  "previousWeightReferenceOnly:true",
  "methodPreviousReference:true",
  "professionalProgressCharts:true"
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.5 missing critical markers: "+repr(missing))

if len(re.findall(r"<style\b",html,re.I))!=1:
    raise RuntimeError("V20.5 expected one final stylesheet")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.5 canonical workout completion + progress visuals enabled")
print("TEAM FJZ V20.5 stale draft restore patched:",n_restore)
