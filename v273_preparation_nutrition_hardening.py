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
        raise RuntimeError("V20.73 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.73 transform made no changes in "+script_id)
    return doc[:m.start()]+m.group(1)+new+m.group(3)+doc[m.end():]

before=metrics(html)

required=[
    'meta name="fjz-preparation-nutrition-calculator" content="20.72"',
    'id="v272PreparationNutritionCalculatorRuntime"',
    "window.canonicalizePreparationV272=function()",
    "window.calcMacroTargetsV272=function()",
    "window.applyMacroTargetsV272=function()",
    "window.openMacroTargetCalculatorV272=function()",
]
missing=[x for x in required if x not in html]
if missing:
    raise RuntimeError("V20.73 prerequisites missing: "+repr(missing))

def harden_v272(body):
    old_goal="""  function goalFromStudentV272(){
    const g=String(student()?.goal||'').toLowerCase();
    if(/recomp/.test(g))return 'recomp';
    if(/volumen|masa|ganar|aument/.test(g))return 'gain';
    if(/defin|grasa|bajar|descen|perder/.test(g))return 'loss';
    return 'maintain';
  }"""
    new_goal="""  function goalFromStudentV272(){
    const g=String(student()?.goal||'').toLowerCase();
    const wantsLoss=/defin|grasa|bajar|descen|perder/.test(g);
    const wantsGain=/volumen|masa|ganar|aument|músculo|musculo/.test(g);
    if(/recomp/.test(g)||(wantsLoss&&wantsGain))return 'recomp';
    if(wantsGain)return 'gain';
    if(wantsLoss)return 'loss';
    return 'maintain';
  }"""
    if old_goal not in body: raise RuntimeError("V20.73 goal anchor missing")
    body=body.replace(old_goal,new_goal,1)

    weight_anchor="""  function goalFromStudentV272(){"""
    weight_helper="""  async function latestWeightForCalculatorV273(){
    const local=latestWeightV272();
    if(local!==''&&local!=null)return local;
    if(!cloudEnabled||!supabaseClient||typeof nutritionAthleteId!=='function')return '';
    const aid=nutritionAthleteId();
    if(!aid)return '';
    try{
      const [mRes,cRes]=await Promise.all([
        supabaseClient.from('body_measurements').select('weight_kg,measured_on').eq('athlete_id',aid).not('weight_kg','is',null).order('measured_on',{ascending:false}).limit(1),
        supabaseClient.from('weekly_checkins').select('weight_kg,week_start').eq('athlete_id',aid).not('weight_kg','is',null).order('week_start',{ascending:false}).limit(1)
      ]);
      const rows=[];
      if(!mRes.error&&mRes.data?.[0]?.weight_kg)rows.push({w:Number(mRes.data[0].weight_kg),d:String(mRes.data[0].measured_on||'')});
      if(!cRes.error&&cRes.data?.[0]?.weight_kg)rows.push({w:Number(cRes.data[0].weight_kg),d:String(cRes.data[0].week_start||'')});
      rows.sort((a,b)=>b.d.localeCompare(a.d));
      const n=rows[0]?.w;
      return Number.isFinite(n)&&n>20&&n<400?n:'';
    }catch(_e){return ''}
  }

"""
    if weight_anchor not in body: raise RuntimeError("V20.73 weight helper anchor missing")
    body=body.replace(weight_anchor,weight_helper+weight_anchor,1)

    old_start="""  window.calcMacroTargetsV272=function(){
    const weight=numV272('v272Weight'),height=numV272('v272Height'),age=numV272('v272Age');
    const sex=el('v272Sex')?.value||'';
    const bf=numV272('v272BodyFat',NaN);
    const meals=clampV272(Math.round(numV272('v272Meals',4)),3,6);
    const proteinKg=clampV272(numV272('v272ProteinKg',1.8),1.2,2.4);
    const fatKg=clampV272(numV272('v272FatKg',.8),.6,1.2);
    let adjust=clampV272(numV272('v272Adjust',0),-20,15);

    if(!Number.isFinite(age)||age<18){"""
    new_start="""  window.calcMacroTargetsV272=function(){
    const weight=numV272('v272Weight'),height=numV272('v272Height'),age=numV272('v272Age');
    const sex=el('v272Sex')?.value||'';
    const bf=numV272('v272BodyFat',NaN);
    const rawMeals=numV272('v272Meals',4);
    const rawProteinKg=numV272('v272ProteinKg',1.8);
    const rawFatKg=numV272('v272FatKg',.8);
    const rawAdjust=numV272('v272Adjust',0);
    const manualFactor=numV272('v272Factor',NaN);

    if(!Number.isFinite(age)||age<18){"""
    if old_start not in body: raise RuntimeError("V20.73 calculator start anchor missing")
    body=body.replace(old_start,new_start,1)

    old_validation="""    if(!Number.isFinite(weight)||weight<35||weight>300||!Number.isFinite(height)||height<120||height>230||age>100){
      toast('Revisá edad, peso y altura');return;
    }

    let bmr=0,formula='';"""
    new_validation="""    if(!Number.isFinite(weight)||weight<35||weight>300||!Number.isFinite(height)||height<120||height>230||age>100){
      toast('Revisá edad, peso y altura');return;
    }
    if(Number.isFinite(bf)&&(bf<5||bf>60)){toast('El % de grasa debe quedar entre 5 y 60');return}
    if(!Number.isFinite(rawMeals)||rawMeals<3||rawMeals>6){toast('Elegí entre 3 y 6 comidas');return}
    if(!Number.isFinite(rawProteinKg)||rawProteinKg<1.2||rawProteinKg>2.4){toast('La proteína debe quedar entre 1,2 y 2,4 g/kg');return}
    if(!Number.isFinite(rawFatKg)||rawFatKg<0.6||rawFatKg>1.2){toast('Las grasas deben quedar entre 0,6 y 1,2 g/kg');return}
    if(!Number.isFinite(rawAdjust)||rawAdjust<-20||rawAdjust>15){toast('El ajuste energético debe quedar entre -20% y +15%');return}
    if(Number.isFinite(manualFactor)&&(manualFactor<1.20||manualFactor>1.90)){toast('El factor manual debe quedar entre 1,20 y 1,90');return}

    const meals=Math.round(rawMeals);
    const proteinKg=rawProteinKg;
    const fatKg=rawFatKg;
    const adjust=rawAdjust;

    let bmr=0,formula='';"""
    if old_validation not in body: raise RuntimeError("V20.73 validation anchor missing")
    body=body.replace(old_validation,new_validation,1)

    old_factor="""    const suggested=suggestedFactorV272();
    const manual=numV272('v272Factor',NaN);
    const factor=Number.isFinite(manual)?clampV272(manual,1.20,1.90):suggested;"""
    new_factor="""    const suggested=suggestedFactorV272();
    const factor=Number.isFinite(manualFactor)?manualFactor:suggested;"""
    if old_factor not in body: raise RuntimeError("V20.73 factor anchor missing")
    body=body.replace(old_factor,new_factor,1)

    old_warnings="""    const warnings=[];
    if(carbKcal<0)warnings.push('El objetivo calórico no alcanza para cubrir la proteína y grasas configuradas');
    if(adjust<=-18)warnings.push('Déficit alto: revisar adherencia, rendimiento y evolución antes de aplicarlo');
    if(target<bmr*.95)warnings.push('El objetivo queda muy cerca o por debajo de la TMB estimada; revisar el planteo');
    const carbs=Math.max(0,carbKcal/4);
    const fiber=target/1000*14;

    lastMacroResultV272={
      blocked:false,weight,height,age,bmr,factor,suggested,tdee,target,adjust,
      protein,carbs,fat,proteinKcal,carbKcal:Math.max(0,carbKcal),fatKcal,
      fiber,meals,formula,warnings
    };"""
    new_warnings="""    const warnings=[];
    if(carbKcal<0)warnings.push('El objetivo calórico no alcanza para cubrir la proteína y grasas configuradas');
    if(adjust<=-18)warnings.push('Déficit alto: revisar adherencia, rendimiento y evolución antes de aplicarlo');
    if(target<bmr*.95)warnings.push('El objetivo queda muy cerca o por debajo de la TMB estimada; revisar el planteo');
    const carbs=Math.max(0,carbKcal/4);
    const fiber=target/1000*14;
    const currentTarget=Number(nutritionCache?.plan?.target_kcal);
    const currentDelta=Number.isFinite(currentTarget)&&currentTarget>0?target-currentTarget:null;
    const hardBlockApply=carbKcal<0||target<bmr*.95;
    const macroEnergy=proteinKcal+Math.max(0,carbKcal)+fatKcal;

    lastMacroResultV272={
      blocked:false,weight,height,age,bmr,factor,suggested,tdee,target,adjust,
      protein,carbs,fat,proteinKcal,carbKcal:Math.max(0,carbKcal),fatKcal,
      fiber,meals,formula,warnings,currentTarget,currentDelta,hardBlockApply,macroEnergy
    };"""
    if old_warnings not in body: raise RuntimeError("V20.73 warnings anchor missing")
    body=body.replace(old_warnings,new_warnings,1)

    old_target="""        '<div class="v272-result-card emphasis"><span>Objetivo diario</span><strong>'+fmtV272(r.target)+' kcal</strong><small>Ajuste '+(r.adjust>0?'+':'')+fmtV272(r.adjust,0)+'%</small></div>'+"""
    new_target="""        '<div class="v272-result-card emphasis"><span>Objetivo diario</span><strong>'+fmtV272(r.target)+' kcal</strong><small>Ajuste '+(r.adjust>0?'+':'')+fmtV272(r.adjust,0)+'%'+(r.currentDelta!=null?' · vs plan '+(r.currentDelta>0?'+':'')+fmtV272(r.currentDelta)+' kcal':'')+'</small></div>'+"""
    if old_target not in body: raise RuntimeError("V20.73 result target anchor missing")
    body=body.replace(old_target,new_target,1)

    old_apply="""    if(r.warnings.some(x=>x.includes('no alcanza'))){toast('Revisá el cálculo antes de aplicarlo');return}"""
    new_apply="""    if(r.hardBlockApply){toast('Revisá el cálculo: hay una advertencia que bloquea la aplicación automática');return}"""
    if old_apply not in body: raise RuntimeError("V20.73 apply guard anchor missing")
    body=body.replace(old_apply,new_apply,1)

    old_open="""  window.openMacroTargetCalculatorV272=function(){"""
    new_open="""  window.openMacroTargetCalculatorV272=async function(){"""
    if old_open not in body: raise RuntimeError("V20.73 open calculator anchor missing")
    body=body.replace(old_open,new_open,1)

    old_weight="""    const weight=latestWeightV272();"""
    new_weight="""    const weight=await latestWeightForCalculatorV273();"""
    if old_weight not in body: raise RuntimeError("V20.73 async weight anchor missing")
    body=body.replace(old_weight,new_weight,1)

    return body

html=edit_script(html,"v272PreparationNutritionCalculatorRuntime",harden_v272)

persist_runtime=r"""
<script id="v273PreparationPersistenceRuntime">
(function(){
  let persistingV273=false;

  window.ensurePreparationPersistedV273=function(){
    if(persistingV273||typeof window.canonicalizePreparationV272!=='function')return false;
    const changed=window.canonicalizePreparationV272();
    if(!changed)return false;
    persistingV273=true;
    try{
      saveState();
    }finally{
      persistingV273=false;
    }
    return true;
  };

  const baseDayEditorV273=window.dayEditor||dayEditor;
  window.dayEditor=function(){
    window.ensurePreparationPersistedV273();
    return baseDayEditorV273.apply(this,arguments);
  };
  try{dayEditor=window.dayEditor}catch(_e){}

  const baseRenderWorkoutV273=window.renderWorkout||renderWorkout;
  window.renderWorkout=function(){
    window.ensurePreparationPersistedV273();
    return baseRenderWorkoutV273.apply(this,arguments);
  };
  try{renderWorkout=window.renderWorkout}catch(_e){}

  window.__fjzV273={
    version:'20.73',
    preparationMigrationPersisted:true,
    mixedGoalDetectsRecomposition:true,
    latestWeightCloudFallback:true,
    calculatorStrictBounds:true,
    currentPlanDelta:true,
    unsafeAutoApplyBlocked:true,
    macroEnergyReconciled:true
  };
})();
</script>
"""
html=html.replace("</body>",persist_runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-preparation-nutrition-hardening" content="20.73">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.73 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-preparation-nutrition-hardening" content="20.73"',
    "preparationMigrationPersisted:true",
    "mixedGoalDetectsRecomposition:true",
    "latestWeightCloudFallback:true",
    "calculatorStrictBounds:true",
    "currentPlanDelta:true",
    "unsafeAutoApplyBlocked:true",
    "macroEnergyReconciled:true",
    "saveState();",
    "latestWeightForCalculatorV273",
    "currentDelta",
    "hardBlockApply",
]:
    if marker not in html:
        raise RuntimeError("V20.73 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.73 preparation/nutrition hardening")
print("V20.73 BEFORE:",before)
print("V20.73 AFTER:",after)
print("V20.73 preparation migration now persists; macro calculator bounds/comparison hardened")
