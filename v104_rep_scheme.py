import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")
html=html.replace("TEAM FJZ V10.2","TEAM FJZ V10.4").replace("TEAM FJZ V10.1","TEAM FJZ V10.4").replace("TEAM FJZ V10.0","TEAM FJZ V10.4")

css=r"""
<style id="v104ExactRepsStyles">
.v104-rep-box{grid-column:1/-1;border:1px solid var(--border);background:#0d0d10;border-radius:12px;padding:11px;margin-top:2px}
.v104-rep-grid{display:grid;grid-template-columns:180px minmax(0,1fr);gap:10px;align-items:end}
.v104-rep-preview{margin-top:8px;display:flex;gap:6px;flex-wrap:wrap}
.v104-rep-chip{display:inline-flex;align-items:center;justify-content:center;min-width:44px;padding:5px 8px;border:1px solid rgba(90,167,255,.30);background:rgba(90,167,255,.07);border-radius:999px;font-size:10px;font-weight:850;color:#a8d0ff}
.v104-target{display:inline-flex;margin-top:5px;padding:4px 7px;border-radius:999px;border:1px solid rgba(90,167,255,.28);background:rgba(90,167,255,.06);font-size:10px;font-weight:850;color:#a8d0ff}
.v104-set-target{font-size:9px;color:#9ec8ff;font-weight:850;margin-top:3px}
@media(max-width:620px){.v104-rep-grid{grid-template-columns:1fr}}
</style>
"""

js=r"""
<script id="v104ExactRepsRuntime">
(function(){
  function parseExactV104(raw){
    raw=String(raw||'').trim().toLowerCase().replace(/×/g,'x');
    const mult=raw.match(/^\s*(\d+)\s*x\s*(\d+)\s*$/);
    if(mult){
      const count=Math.max(1,Math.min(10,Number(mult[1])));
      const reps=Math.max(1,Math.min(100,Number(mult[2])));
      return Array.from({length:count},()=>reps);
    }
    return raw.replace(/[^0-9,;\-\/\s]/g,' ')
      .split(/[\s,;\-\/]+/)
      .map(Number)
      .filter(n=>Number.isFinite(n)&&n>0&&n<=100)
      .slice(0,10);
  }
  function exactTextV104(e){
    const a=Array.isArray(e?.repsExact)?e.repsExact.filter(n=>Number(n)>0):[];
    return a.length?a.join('-'):'';
  }
  function targetRepV104(e,i){
    if(e?.repMode==='exact'&&Array.isArray(e.repsExact)&&e.repsExact.length){
      return Number(e.repsExact[i]??e.repsExact[e.repsExact.length-1])||e.min||1;
    }
    return e?.min||1;
  }
  function targetLabelV104(e){
    return e?.repMode==='exact'&&Array.isArray(e.repsExact)&&e.repsExact.length
      ? e.repsExact.join('-')
      : ((e?.min??'—')+'–'+(e?.max??'—'));
  }
  window.parseExactRepsV104=parseExactV104;

  const baseShow=window.showExerciseForm;
  window.showExerciseForm=function(dayIndex,exIndex,e){
    baseShow.apply(this,arguments);
    const grid=document.querySelector('.modal .form-grid');
    if(!grid||document.getElementById('fRepMode'))return;
    const box=document.createElement('div');
    box.className='v104-rep-box';
    const mode=e?.repMode==='exact'?'exact':'range';
    box.innerHTML='<div class="v104-rep-grid">'+
      '<label class="tiny muted">Tipo de repeticiones<select id="fRepMode" class="input" onchange="toggleRepModeV104()"><option value="range">Rango</option><option value="exact">Exactas por serie</option></select></label>'+
      '<label class="tiny muted" id="fExactWrap">Reps exactas<input id="fExactReps" class="input" placeholder="Ej: 12-10-8-8 o 3x12" value="'+esc(exactTextV104(e))+'" oninput="previewExactRepsV104()"></label>'+
      '</div><div id="fExactPreview" class="v104-rep-preview"></div>';
    const cue=document.getElementById('fCue')?.closest('label');
    cue?grid.insertBefore(box,cue):grid.appendChild(box);
    document.getElementById('fRepMode').value=mode;
    toggleRepModeV104();
  };

  window.toggleRepModeV104=function(){
    const mode=document.getElementById('fRepMode')?.value||'range';
    const wrap=document.getElementById('fExactWrap');
    if(wrap)wrap.style.display=mode==='exact'?'block':'none';
    const ids=['fSets','fMin','fMax'];
    ids.forEach(id=>{
      const l=document.getElementById(id)?.closest('label');
      if(l)l.style.opacity=mode==='exact'?'0.48':'1';
    });
    previewExactRepsV104();
  };
  window.previewExactRepsV104=function(){
    const h=document.getElementById('fExactPreview');if(!h)return;
    if((document.getElementById('fRepMode')?.value||'range')!=='exact'){h.innerHTML='';return}
    const a=parseExactV104(document.getElementById('fExactReps')?.value);
    h.innerHTML=a.length?a.map((n,i)=>'<span class="v104-rep-chip">S'+(i+1)+' · '+n+'</span>').join(''):'<span class="muted tiny">Escribí un esquema como 12-10-8-8.</span>';
  };

  window.saveExercise=function(di,ei,exUid,libId,muscle,equipment){
    const old=ei==null?null:student().days[di].exercises[ei];
    const mode=document.getElementById('fRepMode')?.value||old?.repMode||'range';
    let exact=mode==='exact'?parseExactV104(document.getElementById('fExactReps')?.value):[];
    if(mode==='exact'&&!exact.length){toast('Escribí las repeticiones exactas, por ejemplo 12-10-8-8');return}
    let sets=+el('fSets').value,min=+el('fMin').value,max=+el('fMax').value;
    if(mode==='exact'){
      sets=exact.length;min=Math.min(...exact);max=Math.max(...exact);
    }
    const data={
      uid:old?.uid||exUid||uid('e'),libId,
      name:el('fName').value.trim()||'Ejercicio',muscle,equipment,
      sets,min,max,rirMin:+el('fRMin').value,rirMax:+el('fRMax').value,
      rest:+el('fRest').value,cue:el('fCue').value.trim(),increment:+el('fInc').value,
      method:(el('fMethod')&&el('fMethod').value)||old?.method||'normal',
      methodNote:(el('fMethodNote')&&el('fMethodNote').value.trim())||'',
      repMode:mode,repsExact:mode==='exact'?exact:[],
      history:old?.history||[],override:old?.override||null
    };
    if(ei==null)student().days[di].exercises.push(data);else student().days[di].exercises[ei]=data;
    saveState();closeModal();render();toast('Rutina actualizada');
  };

  const baseDay=window.dayEditor;
  if(typeof baseDay==='function')window.dayEditor=function(d,i){
    let out=baseDay.apply(this,arguments);
    (d.exercises||[]).forEach(e=>{
      if(e.repMode!=='exact'||!Array.isArray(e.repsExact)||!e.repsExact.length)return;
      const old=e.sets+' series · '+e.min+'–'+e.max+' reps';
      const neu=e.sets+' series · reps '+e.repsExact.join('-');
      out=out.replace(old,neu);
    });
    return out;
  };

  window.workoutExercise=function(e,i){
    const prev=baselineSets(e),rec=currentRecommendation(e);
    const header=e.repMode==='exact'&&e.repsExact?.length
      ? e.sets+' series · '+e.repsExact.join('-')+' reps · RIR '+e.rirMin+'–'+e.rirMax+' · descanso '+e.rest+'s'
      : e.sets+' series · '+e.min+'–'+e.max+' reps · RIR '+e.rirMin+'–'+e.rirMax+' · descanso '+e.rest+'s';
    let method='';
    if(e&&e.method&&e.method!=='normal'){
      const labels={dropset:'Dropset',rest_pause:'Rest-pause',myo_reps:'Myo-reps',cluster:'Cluster',superserie:'Superserie'};
      method='<div style="margin:0 0 10px"><span class="v86-method-badge">'+esc(labels[e.method]||e.method)+'</span>';
      if(e.methodNote)method+='<div class="v86-method-note">'+esc(e.methodNote)+'</div>';
      method+='</div>';
    }
    return '<div class="card session-card">'+method+
      '<div class="day-head"><div><strong>'+(i+1)+'. '+esc(e.name)+'</strong><div class="muted tiny">'+header+'</div>'+
      (e.repMode==='exact'?'<div class="v104-target">Objetivo: '+esc(e.repsExact.join('-'))+'</div>':'')+
      '</div><span class="badge amber">Objetivo</span></div>'+
      '<p class="muted tiny">'+esc(e.cue||'')+'</p>'+
      (prev.length?'<div class="coach-note tiny"><strong>Última sesión:</strong> '+prev.map((x,j)=>'S'+(j+1)+' '+x[0]+'kg × '+x[1]+' · RIR '+x[2]).join(' · ')+'</div>':'<div class="coach-note tiny"><strong>Primera sesión:</strong> esta carga va a crear tu referencia inicial.</div>')+
      '<div style="height:10px"></div>'+
      Array.from({length:e.sets},(_,si)=>{
        const target=targetRepV104(e,si);
        const p=prev[si]||prev[prev.length-1]||[0,target,e.rirMax];
        const draft=(workoutDraft[e.uid]||[])[si],vals=draft||p;
        return '<div class="set-grid"><div class="set-n">'+(si+1)+(e.repMode==='exact'?'<div class="v104-set-target">Meta '+target+'</div>':'')+'</div>'+
          '<label class="tiny muted">Kg<input class="input" type="number" step="0.5" value="'+(vals[0]||'')+'" oninput="setWorkout(\''+e.uid+'\','+si+',0,this.value)"></label>'+
          '<label class="tiny muted">Reps<input class="input" type="number" value="'+(vals[1]||target)+'" oninput="setWorkout(\''+e.uid+'\','+si+',1,this.value)"></label>'+
          '<label class="tiny muted">RIR<input class="input" type="number" min="0" max="10" value="'+(vals[2]??e.rirMax)+'" oninput="setWorkout(\''+e.uid+'\','+si+',2,this.value)"></label></div>';
      }).join('')+
      '<div id="rec_'+e.uid+'">'+recommendationHtml(e,rec)+'</div></div>';
  };

  const baseAuto=window.autoRecommendation;
  window.autoRecommendation=function(e,sets){
    if(e?.repMode!=='exact'||!Array.isArray(e.repsExact)||!e.repsExact.length){
      return baseAuto.apply(this,arguments);
    }
    const targets=e.repsExact;
    const valid=sets.length===e.sets&&sets.every(x=>x[0]>0&&x[1]>0&&x[2]>=0);
    if(!valid)return{type:'none',title:'Completá todas las series',copy:'Necesito carga, repeticiones y RIR válidos para analizar la sesión.'};
    const last=latestHistory(e),hist=e.history||[],sig=targetSig(e)+'|'+targets.join('-');
    if(last&&last.target&&last.target!==sig)return{type:'reset',title:'Nueva referencia',copy:'Cambió el objetivo de este ejercicio. Esta sesión servirá como nueva base.'};
    const hit=sets.every((x,i)=>x[1]>=Number(targets[i]??targets[targets.length-1])&&x[2]>=e.rirMin&&x[2]<=e.rirMax);
    const tooHard=sets.filter((x,i)=>x[1]<Number(targets[i]??targets[targets.length-1])||x[2]<e.rirMin).length>=Math.ceil(e.sets/2);
    const sameWeight=sets.every(x=>Math.abs(x[0]-sets[0][0])<.001);
    if(!last)return{type:'first',title:'Primera referencia',copy:'Guardá esta sesión. La próxima vez podremos comparar y recomendar progresión.'};
    if(hit&&sameWeight)return{type:'up',title:'Objetivo exacto completado',copy:'Completaste todas las repeticiones indicadas dentro del RIR objetivo. Podés evaluar una suba de carga en la próxima sesión.'};
    if(tooHard)return{type:'down',title:'Mantené o bajá levemente la carga',copy:'Varias series quedaron por debajo del objetivo exacto o demasiado cerca del fallo.'};
    const prev=last.sets||[];
    const reps=sets.reduce((a,x)=>a+x[1],0),prevReps=prev.reduce((a,x)=>a+(x[1]||0),0);
    if(reps>prevReps)return{type:'rep',title:'Mejoraste las repeticiones totales',copy:'Mantené la carga hasta completar el esquema exacto respetando el RIR.'};
    return{type:'hold',title:'Mantené la carga',copy:'Buscá completar el esquema exacto con buena técnica y el RIR indicado.'};
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)
p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8").replace("team-fjz-v10-2","team-fjz-v10-4").replace("team-fjz-v10-1","team-fjz-v10-4").replace("team-fjz-v10-0","team-fjz-v10-4")
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V10.4 exact reps:",len(html),"bytes")
