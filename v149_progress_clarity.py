import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

js=r"""
<script id="v149ProgressClarityRuntime">
(function(){
  const VERSION='14.9';

  function safeSetsV149(entry){
    return Array.isArray(entry?.sets)?entry.sets.filter(x=>Array.isArray(x)):[];
  }

  function totalRepsV149(entry){
    return safeSetsV149(entry).reduce((a,x)=>a+(Number(x[1])||0),0);
  }

  function avgRirV149(entry){
    const vals=safeSetsV149(entry).map(x=>Number(x[2])).filter(Number.isFinite);
    if(!vals.length)return null;
    return vals.reduce((a,x)=>a+x,0)/vals.length;
  }

  window.progressChart=function(e,metric){
    metric=metric==='reps'?'reps':'load';
    const hist=e?.history||[];
    const vals=hist.map(x=>{
      const sets=safeSetsV149(x);
      if(metric==='reps')return totalRepsV149(x);
      return sets.length?Math.max(...sets.map(s=>Number(s[0])||0)):0;
    });
    if(!vals.length)return '<div class="empty">Todavía no hay datos suficientes para graficar.</div>';

    const w=700,hg=220,pad=30,min=Math.min(...vals),max=Math.max(...vals),span=Math.max(1,max-min);
    const pts=vals.map((v,i)=>({
      x:pad+(vals.length===1?(w-2*pad)/2:i*(w-2*pad)/(vals.length-1)),
      y:hg-pad-(v-min)/span*(hg-2*pad),
      v
    }));
    return '<div class="chart-wrap"><svg viewBox="0 0 '+w+' '+hg+'" preserveAspectRatio="none">'+
      '<line x1="'+pad+'" y1="'+(hg-pad)+'" x2="'+(w-pad)+'" y2="'+(hg-pad)+'" class="chart-axis"/>'+
      '<line x1="'+pad+'" y1="'+pad+'" x2="'+pad+'" y2="'+(hg-pad)+'" class="chart-axis"/>'+
      '<polyline class="chart-line" points="'+pts.map(q=>q.x+','+q.y).join(' ')+'"/>'+
      pts.map((q,i)=>'<circle class="chart-point" cx="'+q.x+'" cy="'+q.y+'" r="4"/><text class="chart-text" x="'+q.x+'" y="'+Math.max(12,q.y-9)+'" text-anchor="middle">'+(Math.round(q.v*10)/10)+'</text><text class="chart-text" x="'+q.x+'" y="'+(hg-7)+'" text-anchor="middle">'+(i+1)+'</text>').join('')+
      '</svg><div class="muted micro">Eje X: sesiones registradas · Métrica: '+(metric==='load'?'carga máxima (kg)':'repeticiones totales')+'</div></div>';
  };

  window.renderProgress=function(isCoach,targetId){
    const s=student();
    const target=targetId||(isCoach?'coachStudentBody':'studentSubBody');
    const b=el(target);
    if(!b)return;

    const items=allExercises(s).filter(x=>x.e.history?.length);
    if(!items.length){
      b.innerHTML='<div class="empty">Todavía no hay historial suficiente para mostrar progreso.</div>';
      return;
    }

    if(progressMetric==='volume')progressMetric='reps';
    if(progressMetric!=='load'&&progressMetric!=='reps')progressMetric='load';

    if(!selectedProgressExercise||!items.some(x=>x.e.uid===selectedProgressExercise)){
      selectedProgressExercise=items[0].e.uid;
    }

    const ex=items.find(x=>x.e.uid===selectedProgressExercise).e;
    const hist=ex.history||[];
    const latest=hist[hist.length-1];
    const first=hist[0];
    const latestSets=safeSetsV149(latest);
    const firstSets=safeSetsV149(first);
    const latestLoad=latestSets.length?Math.max(...latestSets.map(x=>Number(x[0])||0)):0;
    const firstLoad=firstSets.length?Math.max(...firstSets.map(x=>Number(x[0])||0)):0;
    const latestReps=totalRepsV149(latest);
    const avgRir=avgRirV149(latest);

    b.innerHTML=
      '<div class="grid two"><div class="card">'+
      '<div class="section-title"><h3>Progreso por ejercicio</h3><select id="progressExercise" class="input" style="max-width:310px">'+
      items.map(x=>'<option value="'+x.e.uid+'" '+(x.e.uid===ex.uid?'selected':'')+'>'+esc(x.e.name)+'</option>').join('')+
      '</select></div>'+
      '<div class="segmented" style="width:max-content;margin-bottom:12px">'+
      '<button class="'+(progressMetric==='load'?'active':'')+'" onclick="progressMetric=\'load\';render()">Carga</button>'+
      '<button class="'+(progressMetric==='reps'?'active':'')+'" onclick="progressMetric=\'reps\';render()">Reps</button>'+
      '</div>'+
      progressChart(ex,progressMetric)+
      '<div class="metric-grid" style="margin-top:12px">'+
      '<div class="metric"><strong>'+round1(latestLoad)+' kg</strong><span class="muted tiny">Carga máxima</span></div>'+
      '<div class="metric"><strong>'+latestReps+'</strong><span class="muted tiny">Reps última sesión</span></div>'+
      '<div class="metric"><strong>'+(avgRir==null?'—':round1(avgRir))+'</strong><span class="muted tiny">RIR promedio</span></div>'+
      '<div class="metric"><strong>'+(round1(latestLoad-firstLoad)>0?'+':'')+round1(latestLoad-firstLoad)+' kg</strong><span class="muted tiny">Cambio desde inicio</span></div>'+
      '</div></div>'+
      '<aside class="card"><h3 style="margin-top:0">Recomendación actual</h3>'+
      recommendationHtml(ex,autoRecommendation(ex,latestSets))+
      (isCoach?'<button class="btn primary" style="width:100%;margin-top:12px" onclick="setCoachOverride(\''+ex.uid+'\')">'+(ex.override?.active?'Editar indicación':'Sobrescribir recomendación')+'</button>'+(ex.override?.active?'<button class="btn" style="width:100%;margin-top:8px" onclick="clearCoachOverride(\''+ex.uid+'\')">Quitar indicación manual</button>':''):'')+
      '<hr style="border:0;border-top:1px solid var(--border);margin:16px 0"><h4>Últimas sesiones</h4>'+
      hist.slice(-4).reverse().map(x=>'<div class="history-item"><div><strong>'+fmtDate(x.date)+'</strong><div class="muted tiny">'+safeSetsV149(x).map(s=>s[0]+'×'+s[1]).join(' · ')+'</div></div><span class="badge amber">RIR '+(avgRirV149(x)==null?'—':round1(avgRirV149(x)))+'</span></div>').join('')+
      '</aside></div>';

    const picker=el('progressExercise');
    if(picker)picker.onchange=e=>{selectedProgressExercise=e.target.value;render()};
  };

  window.__fjzProgressClarityV149={
    version:VERSION,
    volumeMetricRemoved:true,
    loadChart:true,
    repsChart:true,
    latestReps:true,
    averageRir:true
  };
})();
</script>
"""

html=html.replace("</body>",js+"\n</body>",1)

for marker in [
    "__fjzProgressClarityV149",
    "volumeMetricRemoved:true",
    "latestReps:true",
    "averageRir:true"
]:
    if marker not in html:
        raise RuntimeError("V14.9 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V14.9 progress clarity enabled")
