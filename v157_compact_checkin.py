import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v157CompactCheckinStyles">
.v701-checkin-scores{
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:8px!important
}
.v157-score-card{
  display:grid!important;
  grid-template-columns:minmax(0,1fr) 92px!important;
  align-items:center!important;
  gap:10px!important;
  padding:10px 12px!important;
  min-width:0!important
}
.v157-score-label{
  display:block;
  font-size:12px;
  font-weight:800;
  color:var(--text)
}
.v157-score-help{
  display:block;
  margin-top:2px;
  font-size:9px;
  color:var(--muted)
}
.v157-score-input-wrap{
  display:grid;
  grid-template-columns:minmax(0,1fr) auto;
  align-items:center;
  gap:5px;
  min-width:0
}
.v157-score-input{
  width:100%!important;
  min-width:0!important;
  height:40px!important;
  text-align:center!important;
  font-size:16px!important;
  font-weight:900!important;
  padding:6px 8px!important
}
.v157-score-suffix{
  color:var(--muted);
  font-size:11px;
  font-weight:800;
  white-space:nowrap
}
.v157-score-input:focus{
  border-color:rgba(255,31,47,.62)!important;
  box-shadow:0 0 0 2px rgba(255,31,47,.10)
}
.v157-score-input.v157-invalid{
  border-color:#ff5261!important
}
.v154-score-grid,.v154-score-value{display:none!important}
.v154-required-note{
  margin-top:8px!important;
  padding:8px 10px!important
}
@media(max-width:700px){
  .v701-checkin-scores{grid-template-columns:1fr!important}
  .v157-score-card{
    grid-template-columns:minmax(0,1fr) 88px!important;
    padding:9px 10px!important
  }
  .v157-score-input{height:38px!important}
}
</style>
"""

js=r"""
<script id="v157CompactCheckinRuntime">
(function(){
  const VERSION='15.7';
  const SPECS=[
    ['Sueño','ciSleep'],
    ['Hambre','ciHunger'],
    ['Estrés','ciStress'],
    ['Energía','ciEnergy'],
    ['Adherencia','ciAdh'],
    ['Ánimo','ciMood'],
    ['Motivación','ciMotivation'],
    ['Recuperación','ciRecovery']
  ];

  function normalizeScoreV157(input,hard=false){
    if(!input)return;
    const raw=String(input.value||'').trim();
    input.classList.remove('v157-invalid');
    if(raw==='')return;
    const n=Number(raw);
    if(!Number.isFinite(n)){
      input.classList.add('v157-invalid');
      if(hard)input.value='';
      return;
    }
    if(n<1||n>10){
      input.classList.add('v157-invalid');
      if(hard)input.value=String(Math.max(1,Math.min(10,Math.round(n))));
      return;
    }
    if(hard)input.value=String(Math.round(n));
  }

  function compactCardV157(label,id){
    return '<div class="track-score v157-score-card" data-score-id="'+id+'">'+
      '<div><span class="v157-score-label">'+esc(label)+'</span>'+
      '<span class="v157-score-help">Valor del 1 al 10</span></div>'+
      '<div class="v157-score-input-wrap">'+
      '<input id="'+id+'" class="input v157-score-input" type="number" min="1" max="10" step="1" inputmode="numeric" placeholder="—" '+
      'oninput="normalizeCheckinScoreV157(this,false)" onchange="normalizeCheckinScoreV157(this,true)">'+
      '<span class="v157-score-suffix">/10</span></div>'+
      '</div>';
  }

  window.normalizeCheckinScoreV157=normalizeScoreV157;

  function simplifyCheckinV157(){
    const host=el('studentSubBody');
    const grid=host?.querySelector('.v701-checkin-scores');
    if(!grid)return;

    const current={};
    SPECS.forEach(([,id])=>{
      const old=el(id);
      if(old&&old.value!=='')current[id]=old.value;
    });

    grid.innerHTML=SPECS.map(([label,id])=>compactCardV157(label,id)).join('');

    SPECS.forEach(([,id])=>{
      if(current[id]!==undefined){
        const input=el(id);
        if(input)input.value=current[id];
      }
    });

    const note=el('v154RequiredNote');
    if(note)note.textContent='Ingresá un valor del 1 al 10 en cada indicador.';
  }

  const baseRenderTrackingStudentV157=renderTrackingStudent;
  renderTrackingStudent=function(){
    const out=baseRenderTrackingStudentV157.apply(this,arguments);
    simplifyCheckinV157();
    return out;
  };

  // V15.4 uses this function when loading an already-saved week.
  const baseSetScoreV157=window.setCheckinScoreV154;
  window.setCheckinScoreV154=function(id,value){
    const input=el(id);
    if(input&&input.classList.contains('v157-score-input')){
      const v=Math.max(1,Math.min(10,Number(value)||0));
      if(v)input.value=String(v);
      return;
    }
    if(typeof baseSetScoreV157==='function')return baseSetScoreV157.apply(this,arguments);
  };

  window.__fjzCompactCheckinV157={
    version:VERSION,
    oneCompactFieldPerMetric:true,
    noTenButtonGrid:true,
    mobileSingleColumn:true,
    numericValidation:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzCompactCheckinV157",
  "oneCompactFieldPerMetric:true",
  "noTenButtonGrid:true",
  "mobileSingleColumn:true",
  "numericValidation:true"
]:
    if marker not in html:
        raise RuntimeError("V15.7 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V15.7 compact check-in inputs enabled")
