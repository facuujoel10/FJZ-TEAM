import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v160SimpleCheckinInputStyles">
#v160CheckinScores{
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:8px
}
.v160-score-row{
  display:grid;
  grid-template-columns:minmax(0,1fr) 78px;
  align-items:center;
  gap:10px;
  padding:10px 12px;
  border:1px solid var(--border);
  border-radius:12px;
  background:var(--card);
  min-width:0;
  position:relative;
  z-index:1
}
.v160-score-row>div:first-child{
  min-width:0
}
.v160-score-row strong{
  display:block;
  font-size:12px;
  line-height:1.2
}
.v160-score-row small{
  display:block;
  margin-top:2px;
  color:var(--muted);
  font-size:9px
}
.v160-score-box{
  display:grid;
  grid-template-columns:minmax(0,1fr) auto;
  gap:5px;
  align-items:center;
  min-width:0;
  position:relative;
  z-index:20
}
.v160-score-input{
  display:block!important;
  position:relative!important;
  z-index:30!important;
  width:100%!important;
  height:40px!important;
  min-width:0!important;
  padding:6px 8px!important;
  margin:0!important;
  border:1px solid var(--border)!important;
  border-radius:10px!important;
  background:#0d0d0f!important;
  color:#fff!important;
  text-align:center!important;
  font-size:17px!important;
  font-weight:900!important;
  line-height:1!important;
  pointer-events:auto!important;
  touch-action:manipulation!important;
  user-select:text!important;
  -webkit-user-select:text!important;
  opacity:1!important
}
.v160-score-input:focus{
  outline:none!important;
  border-color:var(--red)!important;
  box-shadow:0 0 0 2px rgba(255,31,47,.10)!important
}
.v160-score-input.v160-invalid{
  border-color:#ff5261!important
}
.v160-score-box span{
  font-size:10px;
  font-weight:800;
  color:var(--muted);
  white-space:nowrap
}
#v160CheckinHelp{
  margin-top:8px;
  padding:8px 10px;
  border:1px solid rgba(90,167,255,.22);
  border-radius:10px;
  background:rgba(90,167,255,.04);
  font-size:10px;
  color:var(--muted)
}
@media(max-width:700px){
  #v160CheckinScores{grid-template-columns:1fr}
  .v160-score-row{grid-template-columns:minmax(0,1fr) 76px}
  .v160-score-input{height:38px!important}
}
</style>
"""

js=r"""
<script id="v160SimpleCheckinInputRuntime">
(function(){
  const VERSION='16.0';
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

  function cleanV160(input,finalize=false){
    if(!input)return;
    let raw=String(input.value||'').replace(/[^0-9]/g,'').slice(0,2);
    input.classList.remove('v160-invalid');

    if(raw===''){
      input.value='';
      return;
    }

    let n=parseInt(raw,10);
    if(!Number.isFinite(n)){
      input.value='';
      return;
    }

    if(n>10)n=10;
    input.value=String(n);

    if(finalize&&n<1){
      input.value='';
      input.classList.add('v160-invalid');
    }
  }

  function rowV160(label,id,value=''){
    const safe=/^(?:[1-9]|10)$/.test(String(value||''))?String(value):'';
    return '<div class="v160-score-row">'+
      '<div><strong>'+esc(label)+'</strong><small>Escribí un número del 1 al 10</small></div>'+
      '<div class="v160-score-box">'+
        '<input id="'+id+'" class="v160-score-input" type="tel" inputmode="numeric" pattern="[0-9]*" '+
          'maxlength="2" autocomplete="off" placeholder="—" value="'+safe+'" aria-label="'+esc(label)+' del 1 al 10">'+
        '<span>/10</span>'+
      '</div>'+
    '</div>';
  }

  function installV160(){
    const host=el('studentSubBody');
    if(!host)return;

    const old=host.querySelector('.v701-checkin-scores,#v160CheckinScores');
    if(!old)return;

    const existing={};
    SPECS.forEach(([,id])=>{
      const node=el(id);
      if(node&&/^(?:[1-9]|10)$/.test(String(node.value||'')))existing[id]=node.value;
    });

    const wrap=document.createElement('div');
    wrap.id='v160CheckinScores';
    wrap.innerHTML=SPECS.map(([label,id])=>rowV160(label,id,existing[id]||'')).join('');

    old.replaceWith(wrap);

    const priorHelp=el('v160CheckinHelp')||el('v154RequiredNote');
    if(priorHelp)priorHelp.remove();

    const help=document.createElement('div');
    help.id='v160CheckinHelp';
    help.textContent='Tocá cada caja y escribí con el teclado del celular. Solo se aceptan valores del 1 al 10.';
    wrap.insertAdjacentElement('afterend',help);

    SPECS.forEach(([,id])=>{
      const input=el(id);
      if(!input)return;

      input.addEventListener('input',()=>cleanV160(input,false));
      input.addEventListener('blur',()=>cleanV160(input,true));
      input.addEventListener('focus',()=>input.classList.remove('v160-invalid'));
    });
  }

  const previousRenderV160=renderTrackingStudent;
  renderTrackingStudent=function(){
    const out=previousRenderV160.apply(this,arguments);
    installV160();
    return out;
  };

  const previousSetScoreV160=window.setCheckinScoreV154;
  window.setCheckinScoreV154=function(id,value){
    const input=el(id);
    if(input&&input.classList.contains('v160-score-input')){
      const n=Number(value);
      input.value=Number.isFinite(n)&&n>=1&&n<=10?String(Math.round(n)):'';
      return;
    }
    if(typeof previousSetScoreV160==='function')return previousSetScoreV160.apply(this,arguments);
  };

  window.__fjzSimpleCheckinV160={
    version:VERSION,
    plainKeyboardInput:true,
    inputType:'tel',
    min:1,
    max:10,
    legacyScoreGridRemoved:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzSimpleCheckinV160",
  "plainKeyboardInput:true",
  "inputType:'tel'",
  "legacyScoreGridRemoved:true",
  "v160-score-input"
]:
    if marker not in html:
        raise RuntimeError("V16.0 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V16.0 simple check-in keyboard inputs enabled")
