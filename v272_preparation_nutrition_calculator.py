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

before=metrics(html)

required=[
    'meta name="fjz-routine-library-preparation" content="20.69"',
    'meta name="fjz-nutrition-ui" content="20.29"',
    "__fjzWarmupLibraryV269",
    "__fjzStretchLibraryV269",
    "renderNutritionCoachLoaded",
    "renderNutritionStudentLoaded",
    "nutritionCache",
    "nutKcal",
    "nutProtein",
    "nutCarbs",
    "nutFat",
]
missing=[x for x in required if x not in html]
if missing:
    raise RuntimeError("V20.72 prerequisites missing: "+repr(missing))

runtime=r"""
<script id="v272PreparationNutritionCalculatorRuntime">
(function(){
  const VERSION='20.72';

  /* =========================================================
     1) PREPARATION CANONICALIZATION
     - warm-up only before training
     - stretching only after training
     - migrate any old preparation exercise rows out of exercises
     ========================================================= */
  const warmSourceV272=Array.isArray(window.__fjzWarmupLibraryV269)?window.__fjzWarmupLibraryV269:[];
  const stretchSourceV272=Array.isArray(window.__fjzStretchLibraryV269)?window.__fjzStretchLibraryV269:[];
  const warmIdsV272=new Set(warmSourceV272.map(x=>String(x.id||'')));
  const stretchIdsV272=new Set(stretchSourceV272.map(x=>String(x.id||'')));
  const warmNamesV272=new Set(warmSourceV272.map(x=>String(x.name||'').trim().toLowerCase()));
  const stretchNamesV272=new Set(stretchSourceV272.map(x=>String(x.name||'').trim().toLowerCase()));

  function prepKeyV272(x){
    const id=String(x?.id||x?.libId||'').trim();
    if(id)return 'id:'+id;
    return 'name:'+String(x?.name||'').trim().toLowerCase();
  }

  function prepItemV272(x){
    return {
      id:String(x?.id||x?.libId||x?.uid||('prep-'+Math.random().toString(36).slice(2))).trim(),
      name:String(x?.name||'Opción').trim(),
      equipment:String(x?.equipment||'').trim(),
      cue:String(x?.cue||'').trim()
    };
  }

  function uniquePrepV272(arr){
    const seen=new Set(),out=[];
    (Array.isArray(arr)?arr:[]).forEach(x=>{
      const k=prepKeyV272(x);
      if(!k||seen.has(k))return;
      seen.add(k);out.push(x);
    });
    return out;
  }

  function belongsWarmV272(x){
    const id=String(x?.id||x?.libId||'');
    const name=String(x?.name||'').trim().toLowerCase();
    return warmIdsV272.has(id)||warmNamesV272.has(name)||x?.muscle==='Calentamiento / Activación';
  }

  function belongsStretchV272(x){
    const id=String(x?.id||x?.libId||'');
    const name=String(x?.name||'').trim().toLowerCase();
    return stretchIdsV272.has(id)||stretchNamesV272.has(name)||x?.muscle==='Estiramientos / Movilidad';
  }

  function canonicalizeDayPrepV272(day){
    if(!day)return false;
    let changed=false;
    let warm=uniquePrepV272(day.warmupItems||[]);
    let cool=uniquePrepV272(day.cooldownItems||[]);

    const keepExercises=[];
    (Array.isArray(day.exercises)?day.exercises:[]).forEach(ex=>{
      if(belongsWarmV272(ex)){
        const item=prepItemV272(ex),key=prepKeyV272(item);
        if(!warm.some(x=>prepKeyV272(x)===key))warm.push(item);
        changed=true;
      }else if(belongsStretchV272(ex)){
        const item=prepItemV272(ex),key=prepKeyV272(item);
        if(!cool.some(x=>prepKeyV272(x)===key))cool.push(item);
        changed=true;
      }else{
        keepExercises.push(ex);
      }
    });

    const stretchKeys=new Set(cool.filter(belongsStretchV272).map(prepKeyV272));
    const beforeWarm=warm.length;
    warm=warm.filter(x=>!belongsStretchV272(x)&&!stretchKeys.has(prepKeyV272(x)));
    if(warm.length!==beforeWarm)changed=true;

    const beforeCool=cool.length;
    cool=cool.filter(x=>!belongsWarmV272(x));
    if(cool.length!==beforeCool)changed=true;

    warm=uniquePrepV272(warm);
    cool=uniquePrepV272(cool);

    if(day.exercises?.length!==keepExercises.length)changed=true;
    day.exercises=keepExercises;
    day.warmupItems=warm;
    day.cooldownItems=cool;
    return changed;
  }

  window.canonicalizePreparationV272=function(){
    let changed=false;
    (student()?.days||[]).forEach(d=>{if(canonicalizeDayPrepV272(d))changed=true});
    return changed;
  };

  const baseDayEditorV272=dayEditor;
  dayEditor=function(d,i){
    canonicalizeDayPrepV272(d);
    return baseDayEditorV272.apply(this,arguments);
  };
  try{window.dayEditor=dayEditor}catch(_e){}

  const baseRenderWorkoutV272=window.renderWorkout||renderWorkout;
  window.renderWorkout=function(){
    canonicalizeDayPrepV272(student()?.days?.[currentDay]);
    return baseRenderWorkoutV272.apply(this,arguments);
  };
  try{renderWorkout=window.renderWorkout}catch(_e){}

  /* =========================================================
     2) COACH MACRO TARGET CALCULATOR
     Adult estimation tool; does not auto-save a plan.
     ========================================================= */
  let lastMacroResultV272=null;

  function clampV272(v,min,max){return Math.min(max,Math.max(min,v))}
  function numV272(id,fallback=NaN){
    const raw=el(id)?.value;
    if(raw===undefined||raw===null||String(raw).trim()==='')return fallback;
    const n=Number(String(raw).replace(',','.'));
    return Number.isFinite(n)?n:fallback;
  }
  function ageFromBirthV272(date){
    if(!date)return null;
    const d=new Date(String(date)+'T12:00:00');
    if(Number.isNaN(d.getTime()))return null;
    const now=new Date();
    let age=now.getFullYear()-d.getFullYear();
    const m=now.getMonth()-d.getMonth();
    if(m<0||(m===0&&now.getDate()<d.getDate()))age--;
    return age>0&&age<120?age:null;
  }
  function sexForFormulaV272(v){
    const s=String(v||'').toLowerCase();
    if(/fem|mujer|female/.test(s))return 'female';
    if(/masc|hombre|male/.test(s))return 'male';
    return '';
  }
  function latestWeightV272(){
    const aid=typeof nutritionAthleteId==='function'?nutritionAthleteId():null;
    const tc=(typeof trackingCache!=='undefined'&&typeof trackingLoadedFor!=='undefined'&&trackingLoadedFor===aid)?trackingCache:null;
    const candidates=[
      tc?.measurements?.[0]?.weight_kg,
      tc?.checkins?.[0]?.weight_kg,
      student()?.profile?.weight_kg,
      student()?.weightKg,
      student()?.weight
    ];
    for(const x of candidates){
      const n=Number(x);
      if(Number.isFinite(n)&&n>20&&n<400)return n;
    }
    return '';
  }
  function goalFromStudentV272(){
    const g=String(student()?.goal||'').toLowerCase();
    if(/recomp/.test(g))return 'recomp';
    if(/volumen|masa|ganar|aument/.test(g))return 'gain';
    if(/defin|grasa|bajar|descen|perder/.test(g))return 'loss';
    return 'maintain';
  }
  function goalDefaultsV272(goal){
    if(goal==='loss')return{adjust:-15,protein:2.0,fat:.8};
    if(goal==='recomp')return{adjust:-5,protein:1.9,fat:.8};
    if(goal==='gain')return{adjust:8,protein:1.8,fat:.9};
    return{adjust:0,protein:1.7,fat:.9};
  }
  function suggestedFactorV272(){
    const work=el('v272Work')?.value||'sedentary';
    const workBase={sedentary:1.20,mixed:1.30,active:1.40,physical:1.50}[work]||1.20;
    const steps=Math.max(0,numV272('v272Steps',0));
    const sessions=Math.max(0,numV272('v272Strength',0))+Math.max(0,numV272('v272Cardio',0));
    const stepAdj=steps<4000?0:steps<7000?0.03:steps<10000?0.06:steps<13000?0.10:0.13;
    const trainAdj=Math.min(.12,sessions*.018);
    return clampV272(workBase+stepAdj+trainAdj,1.20,1.90);
  }
  function fmtV272(v,d=0){
    return Number(v).toLocaleString('es-AR',{minimumFractionDigits:d,maximumFractionDigits:d});
  }

  window.syncMacroGoalDefaultsV272=function(){
    const d=goalDefaultsV272(el('v272Goal')?.value||'maintain');
    if(el('v272Adjust'))el('v272Adjust').value=d.adjust;
    if(el('v272ProteinKg'))el('v272ProteinKg').value=d.protein;
    if(el('v272FatKg'))el('v272FatKg').value=d.fat;
  };

  function renderMacroResultV272(r){
    const h=el('v272MacroResult');if(!h)return;
    if(!r){h.innerHTML='';return}
    if(r.blocked){
      h.innerHTML='<div class="v272-warning"><strong>No se genera un objetivo automático</strong><span>'+esc(r.message)+'</span></div>';
      return;
    }
    const warn=r.warnings.length
      ?'<div class="v272-warning"><strong>Revisar antes de aplicar</strong><span>'+r.warnings.map(esc).join(' · ')+'</span></div>'
      :'';
    h.innerHTML=
      '<div class="v272-result-grid">'+
        '<div class="v272-result-card"><span>TMB estimada</span><strong>'+fmtV272(r.bmr)+' kcal</strong><small>'+esc(r.formula)+'</small></div>'+
        '<div class="v272-result-card"><span>Factor actividad</span><strong>'+fmtV272(r.factor,2)+'</strong><small>Sugerido/seleccionado</small></div>'+
        '<div class="v272-result-card"><span>Mantenimiento</span><strong>'+fmtV272(r.tdee)+' kcal</strong><small>Rango aprox. '+fmtV272(r.tdee*.92)+'–'+fmtV272(r.tdee*1.08)+'</small></div>'+
        '<div class="v272-result-card emphasis"><span>Objetivo diario</span><strong>'+fmtV272(r.target)+' kcal</strong><small>Ajuste '+(r.adjust>0?'+':'')+fmtV272(r.adjust,0)+'%</small></div>'+
      '</div>'+
      '<div class="v272-macro-grid">'+
        '<div><span>Proteína</span><strong>'+fmtV272(r.protein)+' g</strong><small>'+fmtV272(r.protein/r.weight,2)+' g/kg · '+fmtV272(r.proteinKcal/r.target*100,0)+'%</small></div>'+
        '<div><span>Carbohidratos</span><strong>'+fmtV272(r.carbs)+' g</strong><small>'+fmtV272(r.carbs/r.weight,2)+' g/kg · '+fmtV272(r.carbKcal/r.target*100,0)+'%</small></div>'+
        '<div><span>Grasas</span><strong>'+fmtV272(r.fat)+' g</strong><small>'+fmtV272(r.fat/r.weight,2)+' g/kg · '+fmtV272(r.fatKcal/r.target*100,0)+'%</small></div>'+
        '<div><span>Fibra orientativa</span><strong>'+fmtV272(r.fiber)+' g</strong><small>≈14 g / 1000 kcal</small></div>'+
      '</div>'+
      '<div class="v272-split"><strong>Promedio por '+r.meals+' comidas</strong><span>'+fmtV272(r.target/r.meals)+' kcal · P '+fmtV272(r.protein/r.meals,1)+' g · C '+fmtV272(r.carbs/r.meals,1)+' g · G '+fmtV272(r.fat/r.meals,1)+' g</span></div>'+
      warn+
      '<div class="nutrition-builder-actions v272-result-actions">'+
        '<button class="btn primary" onclick="applyMacroTargetsV272()">Copiar al plan del alumno</button>'+
        '<button class="btn" onclick="calcMacroTargetsV272()">Recalcular</button>'+
      '</div>';
  }

  window.calcMacroTargetsV272=function(){
    const weight=numV272('v272Weight'),height=numV272('v272Height'),age=numV272('v272Age');
    const sex=el('v272Sex')?.value||'';
    const bf=numV272('v272BodyFat',NaN);
    const meals=clampV272(Math.round(numV272('v272Meals',4)),3,6);
    const proteinKg=clampV272(numV272('v272ProteinKg',1.8),1.2,2.4);
    const fatKg=clampV272(numV272('v272FatKg',.8),.6,1.2);
    let adjust=clampV272(numV272('v272Adjust',0),-20,15);

    if(!Number.isFinite(age)||age<18){
      lastMacroResultV272={blocked:true,message:'Para menores de 18 años, los requerimientos energéticos y de crecimiento necesitan evaluación individual por un profesional de salud/nutrición. La app no calcula déficit, superávit ni macros automáticos.'};
      renderMacroResultV272(lastMacroResultV272);return;
    }
    if(!Number.isFinite(weight)||weight<35||weight>300||!Number.isFinite(height)||height<120||height>230||age>100){
      toast('Revisá edad, peso y altura');return;
    }

    let bmr=0,formula='';
    if(Number.isFinite(bf)&&bf>=5&&bf<=60){
      const lean=weight*(1-bf/100);
      bmr=370+21.6*lean;
      formula='Katch-McArdle · '+fmtV272(bf,1)+'% grasa';
    }else{
      if(!sex){toast('Elegí el sexo usado por la fórmula metabólica');return}
      bmr=10*weight+6.25*height-5*age+(sex==='male'?5:-161);
      formula='Mifflin-St Jeor';
    }

    const suggested=suggestedFactorV272();
    const manual=numV272('v272Factor',NaN);
    const factor=Number.isFinite(manual)?clampV272(manual,1.20,1.90):suggested;
    const tdee=bmr*factor;
    const target=tdee*(1+adjust/100);
    const protein=proteinKg*weight;
    const fat=fatKg*weight;
    const proteinKcal=protein*4,fatKcal=fat*9;
    const carbKcal=target-proteinKcal-fatKcal;
    const warnings=[];
    if(carbKcal<0)warnings.push('El objetivo calórico no alcanza para cubrir la proteína y grasas configuradas');
    if(adjust<=-18)warnings.push('Déficit alto: revisar adherencia, rendimiento y evolución antes de aplicarlo');
    if(target<bmr*.95)warnings.push('El objetivo queda muy cerca o por debajo de la TMB estimada; revisar el planteo');
    const carbs=Math.max(0,carbKcal/4);
    const fiber=target/1000*14;

    lastMacroResultV272={
      blocked:false,weight,height,age,bmr,factor,suggested,tdee,target,adjust,
      protein,carbs,fat,proteinKcal,carbKcal:Math.max(0,carbKcal),fatKcal,
      fiber,meals,formula,warnings
    };
    renderMacroResultV272(lastMacroResultV272);
  };

  window.applyMacroTargetsV272=function(){
    const r=lastMacroResultV272;
    if(!r||r.blocked){toast('Primero calculá un objetivo válido');return}
    if(r.warnings.some(x=>x.includes('no alcanza'))){toast('Revisá el cálculo antes de aplicarlo');return}
    const map=[['nutKcal',r.target],['nutProtein',r.protein],['nutCarbs',r.carbs],['nutFat',r.fat]];
    let found=0;
    map.forEach(([id,v])=>{const x=el(id);if(x){x.value=Math.round(v);found++}});
    if(!found){toast('Abrí el plan nutricional del alumno para aplicar los macros');return}
    closeModal();
    toast('Macros copiados al plan · revisalos y tocá Guardar plan');
  };

  window.openMacroTargetCalculatorV272=function(){
    if(currentProfile?.role!=='coach'){toast('Esta herramienta es para el Coach');return}
    const s=student()||{},p=s.profile||{};
    const age=ageFromBirthV272(p.birth_date)||'';
    const height=Number(p.height_cm||s.heightCm)||'';
    const weight=latestWeightV272();
    const sex=sexForFormulaV272(p.sex);
    const goal=goalFromStudentV272();
    const def=goalDefaultsV272(goal);
    const goalOptions=[
      ['maintain','Mantenimiento'],
      ['recomp','Recomposición'],
      ['loss','Pérdida de grasa'],
      ['gain','Ganancia muscular']
    ];
    showModal(
      '<div class="v272-calc-shell">'+
      '<div class="modal-head v269-modal-head"><div class="v269-title-block"><span class="v269-eyebrow">NUTRICIÓN · COACH</span><h3>Calculadora avanzada de macros</h3>'+
      '<small>Estimación adulta para definir una referencia inicial. No reemplaza evaluación clínica.</small></div>'+
      '<button class="btn small v269-close" onclick="closeModal()">✕</button></div>'+
      '<div class="v272-context"><strong>'+esc(s.name||'Alumno')+'</strong><span>Completá o corregí los datos antes de calcular.</span></div>'+
      '<div class="v272-section"><h4>1. Datos corporales</h4><div class="form-grid">'+
        '<label class="tiny muted">Edad<input id="v272Age" class="input" type="number" min="1" max="100" value="'+esc(String(age))+'"></label>'+
        '<label class="tiny muted">Sexo para fórmula<select id="v272Sex" class="input"><option value="">Elegir</option><option value="male" '+(sex==='male'?'selected':'')+'>Masculino</option><option value="female" '+(sex==='female'?'selected':'')+'>Femenino</option></select></label>'+
        '<label class="tiny muted">Peso actual (kg)<input id="v272Weight" class="input" type="number" min="35" max="300" step="0.1" value="'+esc(String(weight))+'"></label>'+
        '<label class="tiny muted">Altura (cm)<input id="v272Height" class="input" type="number" min="120" max="230" step="0.1" value="'+esc(String(height))+'"></label>'+
        '<label class="tiny muted span2">% grasa corporal (opcional)<input id="v272BodyFat" class="input" type="number" min="5" max="60" step="0.1" placeholder="Si lo cargás, usa Katch-McArdle"></label>'+
      '</div></div>'+
      '<div class="v272-section"><h4>2. Actividad</h4><div class="form-grid">'+
        '<label class="tiny muted">Trabajo / día<select id="v272Work" class="input"><option value="sedentary">Mayormente sentado</option><option value="mixed">Mixto / caminatas frecuentes</option><option value="active">Activo gran parte del día</option><option value="physical">Trabajo físico</option></select></label>'+
        '<label class="tiny muted">Pasos promedio/día<input id="v272Steps" class="input" type="number" min="0" max="50000" step="500" value="8000"></label>'+
        '<label class="tiny muted">Fuerza/semana<input id="v272Strength" class="input" type="number" min="0" max="14" step="1" value="'+esc(String(s.plannedPerWeek||3))+'"></label>'+
        '<label class="tiny muted">Cardio/deporte/semana<input id="v272Cardio" class="input" type="number" min="0" max="14" step="1" value="0"></label>'+
        '<label class="tiny muted span2">Factor de actividad manual (opcional)<input id="v272Factor" class="input" type="number" min="1.20" max="1.90" step="0.01" placeholder="Vacío = estimación por actividad, pasos y sesiones"></label>'+
      '</div></div>'+
      '<div class="v272-section"><h4>3. Objetivo y distribución</h4><div class="form-grid">'+
        '<label class="tiny muted">Objetivo<select id="v272Goal" class="input" onchange="syncMacroGoalDefaultsV272()">'+goalOptions.map(x=>'<option value="'+x[0]+'" '+(x[0]===goal?'selected':'')+'>'+x[1]+'</option>').join('')+'</select></label>'+
        '<label class="tiny muted">Ajuste energético (%)<input id="v272Adjust" class="input" type="number" min="-20" max="15" step="1" value="'+def.adjust+'"></label>'+
        '<label class="tiny muted">Proteína (g/kg)<input id="v272ProteinKg" class="input" type="number" min="1.2" max="2.4" step="0.1" value="'+def.protein+'"></label>'+
        '<label class="tiny muted">Grasas (g/kg)<input id="v272FatKg" class="input" type="number" min="0.6" max="1.2" step="0.1" value="'+def.fat+'"></label>'+
        '<label class="tiny muted span2">Comidas por día<input id="v272Meals" class="input" type="number" min="3" max="6" step="1" value="4"></label>'+
      '</div></div>'+
      '<div class="v272-calc-note"><strong>Cómo calcula</strong><span>Mifflin-St Jeor por defecto; si cargás % de grasa usa Katch-McArdle. El gasto diario es una estimación y debe ajustarse con evolución real, rendimiento, hambre, recuperación y adherencia.</span></div>'+
      '<button class="btn primary" style="width:100%;margin-top:12px" onclick="calcMacroTargetsV272()">Calcular objetivos</button>'+
      '<div id="v272MacroResult"></div>'+
      '</div>'
    );
  };

  function coachPlannerCardV272(){
    const p=nutritionCache?.plan;
    if(!p)return '';
    return '<div class="card v272-coach-planner" id="v272CoachMacroPlanner">'+
      '<div class="section-title"><div><h3>Calculadora avanzada de macros</h3><div class="muted tiny">Estimá TMB, mantenimiento y macros con datos del alumno. Después podés copiar el resultado al plan y revisarlo antes de guardar.</div></div><span class="badge blue">Coach</span></div>'+
      '<div class="v272-current-targets">'+
        '<span>Actual</span><strong>'+(p.target_kcal!=null?Math.round(Number(p.target_kcal))+' kcal':'Sin kcal')+'</strong>'+
        '<small>P '+(p.target_protein_g!=null?Math.round(Number(p.target_protein_g)):'—')+' · C '+(p.target_carbs_g!=null?Math.round(Number(p.target_carbs_g)):'—')+' · G '+(p.target_fat_g!=null?Math.round(Number(p.target_fat_g)):'—')+'</small>'+
      '</div>'+
      '<button class="btn primary" style="width:100%;margin-top:10px" onclick="openMacroTargetCalculatorV272()">Abrir calculadora</button>'+
    '</div>';
  }

  function ensureCoachNutritionV272(){
    if(!(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='nutrition'))return;
    const host=el('coachStudentBody');if(!host||el('v272CoachMacroPlanner')||!nutritionCache?.plan)return;
    const first=host.querySelector('.card');
    if(first)first.insertAdjacentHTML('afterend',coachPlannerCardV272());
    else host.insertAdjacentHTML('afterbegin',coachPlannerCardV272());
  }

  function enhanceStudentFoodCalculatorV272(){
    if(!(currentProfile?.role==='student'&&studentTab==='nutrition'))return;
    const host=el('studentSubBody');if(!host)return;
    const title=[...host.querySelectorAll('h3')].find(x=>(x.textContent||'').trim()==='Calculadora de macros'||(x.textContent||'').trim()==='Calculadora de alimentos y comidas');
    const card=title?.closest('.card');if(!card)return;
    title.textContent='Calculadora de alimentos y comidas';
    const sub=card.querySelector('.section-title .muted.tiny');
    if(sub)sub.textContent='Calculá la porción real de un alimento o armá una comida completa para registrarla.';
    const badge=card.querySelector('.section-title .badge');
    if(badge)badge.textContent='Porción';
    if(!card.querySelector('#v272FoodCalcHelp')){
      const note=document.createElement('div');
      note.id='v272FoodCalcHelp';
      note.className='v272-food-help';
      note.innerHTML='<strong>Esto calcula alimentos, no tus calorías objetivo.</strong><span>Los objetivos diarios los define tu coach dentro del plan. Acá podés ajustar cantidades y registrar lo que realmente comiste.</span>';
      const preview=card.querySelector('#macroPreview');
      if(preview)preview.insertAdjacentElement('afterend',note);else card.appendChild(note);
    }
  }

  const baseCoachNutritionLoadedV272=window.renderNutritionCoachLoaded||renderNutritionCoachLoaded;
  window.renderNutritionCoachLoaded=function(){
    const out=baseCoachNutritionLoadedV272.apply(this,arguments);
    ensureCoachNutritionV272();
    return out;
  };
  try{renderNutritionCoachLoaded=window.renderNutritionCoachLoaded}catch(_e){}

  const baseStudentNutritionLoadedV272=window.renderNutritionStudentLoaded||renderNutritionStudentLoaded;
  window.renderNutritionStudentLoaded=function(){
    const out=baseStudentNutritionLoadedV272.apply(this,arguments);
    enhanceStudentFoodCalculatorV272();
    return out;
  };
  try{renderNutritionStudentLoaded=window.renderNutritionStudentLoaded}catch(_e){}

  window.__fjzV272={
    version:VERSION,
    singlePreparationAuthority:true,
    legacyPrepExercisesMigrated:true,
    warmupBeforeOnly:true,
    stretchingAfterOnly:true,
    coachMacroCalculator:true,
    mifflinStJeor:true,
    katchMcArdleOptional:true,
    activityContext:true,
    goalAdjustmentGuarded:true,
    under18AutoTargetsBlocked:true,
    applyTargetsRequiresCoachReview:true,
    studentFoodCalculatorClarified:true
  };
})();
</script>
"""

css=r"""
/* =========================================================
   TEAM FJZ · V20.72 PREPARATION + NUTRITION CALCULATOR
   ========================================================= */
.v272-coach-planner{
  margin-top:12px!important;
  border-color:rgba(255,70,87,.24)!important;
  background:
    linear-gradient(155deg,rgba(255,38,57,.045),transparent 58%),
    #101116!important;
}
.v272-current-targets{
  display:grid;
  grid-template-columns:auto minmax(0,1fr);
  gap:3px 9px;
  align-items:baseline;
  margin-top:10px;
  padding:10px 11px;
  border:1px solid #2b2f36;
  border-radius:11px;
  background:#0d0e12;
}
.v272-current-targets>span{
  grid-row:1/3;
  color:#777d87;
  font-size:7px;
  font-weight:900;
  letter-spacing:.1em;
  text-transform:uppercase;
}
.v272-current-targets strong{font-size:16px;color:#f5f6f8}
.v272-current-targets small{color:#8c929c;font-size:8px}
.v272-calc-shell{min-width:0;max-width:100%}
.v272-context{
  display:flex;
  justify-content:space-between;
  gap:10px;
  align-items:center;
  margin-bottom:10px;
  padding:9px 10px;
  border:1px solid #2a2e35;
  border-radius:11px;
  background:#0d0e12;
}
.v272-context strong{color:#f3f4f6;font-size:11px}
.v272-context span{color:#858b95;font-size:8px;text-align:right}
.v272-section{
  margin-top:9px;
  padding:11px;
  border:1px solid #292d34;
  border-radius:12px;
  background:#0e0f13;
}
.v272-section h4{
  margin:0 0 9px;
  color:#f0f2f4;
  font-size:10px;
  letter-spacing:.01em;
}
.v272-section .form-grid{gap:8px!important}
.v272-section .input,
.v272-section input,
.v272-section select{
  max-width:100%!important;
  min-width:0!important;
  box-sizing:border-box!important;
}
.v272-calc-note,
.v272-warning,
.v272-food-help{
  display:grid;
  gap:4px;
  margin-top:10px;
  padding:10px 11px;
  border:1px solid rgba(103,173,255,.22);
  border-radius:11px;
  background:rgba(103,173,255,.045);
}
.v272-calc-note strong,.v272-food-help strong{font-size:9px;color:#dce9f7}
.v272-calc-note span,.v272-food-help span{font-size:8px;line-height:1.45;color:#9eabb9}
.v272-warning{
  border-color:rgba(255,173,76,.28);
  background:rgba(255,173,76,.055);
}
.v272-warning strong{font-size:9px;color:#ffd096}
.v272-warning span{font-size:8px;line-height:1.45;color:#b9a68f}
.v272-result-grid{
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:7px;
  margin-top:12px;
}
.v272-result-card{
  min-width:0;
  padding:10px;
  border:1px solid #2b2f36;
  border-radius:11px;
  background:#101116;
}
.v272-result-card.emphasis{
  border-color:rgba(255,70,87,.30);
  background:rgba(255,38,57,.045);
}
.v272-result-card span,.v272-macro-grid span{
  display:block;
  color:#818792;
  font-size:7px;
  font-weight:850;
  text-transform:uppercase;
  letter-spacing:.06em;
}
.v272-result-card strong{
  display:block;
  margin-top:4px;
  color:#f6f7f8;
  font-size:14px;
  font-variant-numeric:tabular-nums;
}
.v272-result-card small,.v272-macro-grid small{
  display:block;
  margin-top:4px;
  color:#777e88;
  font-size:7px;
  line-height:1.35;
}
.v272-macro-grid{
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:7px;
  margin-top:7px;
}
.v272-macro-grid>div{
  min-width:0;
  padding:9px 10px;
  border:1px solid #2a2d34;
  border-radius:11px;
  background:#0d0e12;
}
.v272-macro-grid strong{
  display:block;
  margin-top:4px;
  color:#f4f5f7;
  font-size:13px;
  font-variant-numeric:tabular-nums;
}
.v272-split{
  display:flex;
  justify-content:space-between;
  gap:10px;
  margin-top:7px;
  padding:9px 10px;
  border:1px solid #292d34;
  border-radius:10px;
  background:#101116;
}
.v272-split strong{font-size:8px;color:#dadde2}
.v272-split span{font-size:8px;color:#8b919b;text-align:right}
.v272-result-actions{margin-top:10px!important}
.v272-food-help{margin-top:9px}
@media(max-width:760px){
  .v272-result-grid,.v272-macro-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .v272-context,.v272-split{display:grid;grid-template-columns:1fr}
  .v272-context span,.v272-split span{text-align:left}
}
@media(max-width:430px){
  .v272-section{padding:9px}
  .v272-result-grid,.v272-macro-grid{grid-template-columns:1fr}
  .v272-result-actions{display:grid!important;grid-template-columns:1fr!important}
  .v272-result-actions .btn{width:100%!important}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.72 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-preparation-nutrition-calculator" content="20.72">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.72 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-preparation-nutrition-calculator" content="20.72"',
    "singlePreparationAuthority:true",
    "legacyPrepExercisesMigrated:true",
    "warmupBeforeOnly:true",
    "stretchingAfterOnly:true",
    "coachMacroCalculator:true",
    "mifflinStJeor:true",
    "katchMcArdleOptional:true",
    "under18AutoTargetsBlocked:true",
    "applyTargetsRequiresCoachReview:true",
    "Calculadora avanzada de macros",
    "Calculadora de alimentos y comidas",
]:
    if marker not in html:
        raise RuntimeError("V20.72 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.72 preparation + nutrition calculator")
print("V20.72 BEFORE:",before)
print("V20.72 AFTER:",after)
print("V20.72 duplicate preparation paths consolidated; adult coach macro estimator added")
