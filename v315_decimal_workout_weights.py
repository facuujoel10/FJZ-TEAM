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
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

before=metrics(html)

for marker in [
    'meta name="fjz-operational-integrity-ux" content="21.14"',
    'id="v267InputContractsRuntime"',
    "function setWorkout(",
    "function renderWorkout(",
    '.session-card',
]:
    if marker not in html:
        raise RuntimeError("V21.15 prerequisite missing "+marker)

runtime=r"""
<script id="v315DecimalWorkoutWeightsRuntime">
(function(){
  const VERSION='21.15';

  function normalizeDecimalV315(value){
    let s=String(value??'').replace(',','.');
    s=s.replace(/[^0-9.]/g,'');
    const dot=s.indexOf('.');
    if(dot>=0)s=s.slice(0,dot+1)+s.slice(dot+1).replace(/\./g,'');
    return s;
  }

  function isWeightFieldV315(input){
    if(!input||input.tagName!=='INPUT')return false;
    const label=input.closest('label');
    const text=String(label?.textContent||'').toLowerCase();
    if(/\brir\b|rep(?:s|eticiones)?/.test(text))return false;
    return /\bkg\b|peso|carga|lastre|asistencia/.test(text);
  }

  function decimalizeV315(input){
    if(!isWeightFieldV315(input)||input.dataset.v315DecimalWeight==='1')return;
    const current=input.value;
    try{input.type='text'}catch(_e){}
    input.inputMode='decimal';
    input.autocomplete='off';
    input.setAttribute('pattern','[0-9]*[.,]?[0-9]*');
    input.dataset.v315DecimalWeight='1';
    if(current!=null&&current!=='')input.value=normalizeDecimalV315(current);

    const previousInput=input.oninput;
    input.oninput=function(e){
      const raw=String(this.value??'');
      const clean=normalizeDecimalV315(raw);
      if(raw!==clean)this.value=clean;
      if(typeof previousInput==='function')return previousInput.call(this,e);
    };
  }

  function applyDecimalWeightsV315(){
    document.querySelectorAll(
      '.session-card .set-grid input,'+
      '.v137-method-step input,'+
      '.session-card [class*="method"] input,'+
      '.session-card [class*="drop"] input,'+
      '.session-card [class*="super"] input,'+
      '.session-card [class*="biserie"] input'
    ).forEach(decimalizeV315);
  }

  const baseSetWorkoutV315=window.setWorkout||globalThis.setWorkout;
  if(typeof baseSetWorkoutV315==='function'){
    window.setWorkout=function(uidv,si,field,val){
      if(Number(field)===0)val=normalizeDecimalV315(val);
      return baseSetWorkoutV315.call(this,uidv,si,field,val);
    };
    try{setWorkout=window.setWorkout}catch(_e){}
  }

  const baseRenderWorkoutV315=window.renderWorkout||globalThis.renderWorkout;
  if(typeof baseRenderWorkoutV315==='function'){
    window.renderWorkout=function(){
      const out=baseRenderWorkoutV315.apply(this,arguments);
      applyDecimalWeightsV315();
      return out;
    };
    try{renderWorkout=window.renderWorkout}catch(_e){}
  }

  const baseShowModalV315=window.showModal;
  if(typeof baseShowModalV315==='function'){
    window.showModal=function(){
      const out=baseShowModalV315.apply(this,arguments);
      applyDecimalWeightsV315();
      return out;
    };
    try{showModal=window.showModal}catch(_e){}
  }

  window.__fjzApplyDecimalWeightsV315=applyDecimalWeightsV315;
  applyDecimalWeightsV315();

  window.__fjzV315={
    version:VERSION,
    workoutWeightDotDecimal:true,
    workoutWeightCommaDecimal:true,
    decimalNormalizedToDot:true,
    repsRemainInteger:true,
    rirRemainInteger:true,
    mobileLocaleSafeWeightInput:true,
    numericStoragePreserved:true,
    noSchemaChange:true,
    noExtraTimers:true,
    noExtraListeners:true,
    noExtraObservers:true
  };
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-decimal-workout-weights" content="21.15">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V21.15 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-decimal-workout-weights" content="21.15"',
    'id="v315DecimalWorkoutWeightsRuntime"',
    "replace(',','.')",
    "input.type='text'",
    "input.inputMode='decimal'",
    "Number(field)===0",
    "workoutWeightDotDecimal:true",
    "workoutWeightCommaDecimal:true",
    "decimalNormalizedToDot:true",
    "repsRemainInteger:true",
    "rirRemainInteger:true",
    "numericStoragePreserved:true",
]:
    if marker not in html:
        raise RuntimeError("V21.15 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.15 decimal workout weights")
print("V21.15 BEFORE:",before)
print("V21.15 AFTER:",after)
