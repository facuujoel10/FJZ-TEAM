import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\\.)?render\\s*=",doc)),
        "channels":len(re.findall(r"\\.channel\\s*\\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\\s*\\(",doc)),
        "intervals":len(re.findall(r"setInterval\\s*\\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\\s*\\(",doc)),
        "listeners":len(re.findall(r"addEventListener\\s*\\(",doc)),
        "mutation_observers":len(re.findall(r"new\\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\\s+PerformanceObserver",doc)),
    }

def edit_script(doc,script_id,transform):
    pat=re.compile(r'(<script[^>]*\\bid=["\\\']'+re.escape(script_id)+r'["\\\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.76 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.76 no changes in "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

required=[
    'meta name="fjz-mobile-hud-progress" content="20.75"',
    'id="v275MobileHudProgressRuntime"',
    'id="v272PreparationNutritionCalculatorRuntime"',
    "premiumMobileHud:true",
    "coachMacroCalculator:true",
    "renderNutritionCoachLoaded",
    "renderNutritionStudentLoaded",
    "addNutritionMeal",
    "nutritionOptionTotals",
]
missing=[x for x in required if x not in html]
if missing:
    raise RuntimeError("V20.76 prerequisites missing: "+repr(missing))

def harden_macro_calculator(body):
    body=body.replace("rawMeals<3||rawMeals>6","rawMeals<3||rawMeals>8")
    body=body.replace("Elegí entre 3 y 6 comidas","Elegí entre 3 y 8 comidas")
    body=body.replace('max="6" step="1" value="4"','max="8" step="1" value="4"')

    anchor="""      '<div class="v272-split"><strong>Promedio por '+r.meals+' comidas</strong><span>'+fmtV272(r.target/r.meals)+' kcal · P '+fmtV272(r.protein/r.meals,1)+' g · C '+fmtV272(r.carbs/r.meals,1)+' g · G '+fmtV272(r.fat/r.meals,1)+' g</span></div>'+"""
    if anchor not in body:
        raise RuntimeError("V20.76 calculator result anchor missing")
    extra=anchor+"""
      '<div class="v276-calc-check '+(Math.abs((r.macroEnergy||0)-r.target)<=2?'ok':'warn')+'"><strong>Chequeo energético</strong><span>Macros = '+fmtV272(r.macroEnergy||0)+' kcal · objetivo = '+fmtV272(r.target)+' kcal · diferencia '+fmtV272(Math.abs((r.macroEnergy||0)-r.target),0)+' kcal</span></div>'+"""
    body=body.replace(anchor,extra,1)

    old="""    macroEnergyReconciled:true"""
    if old not in body:
        raise RuntimeError("V20.76 macro audit flag anchor missing")
    body=body.replace(old,old+""",
    mealCountUpToEightV276:true,
    visibleEnergyReconciliationV276:true""",1)
    return body

html=edit_script(html,"v272PreparationNutritionCalculatorRuntime",harden_macro_calculator)

css=r"""
/* =========================================================
   TEAM FJZ · V20.76 COACH HUD + NUTRITION DETAIL
   ========================================================= */
@media(max-width:900px){
  .bottom-nav.v276-coach-hud{
    display:grid!important;
    grid-template-columns:repeat(4,minmax(0,1fr))!important;
    position:fixed!important;
    left:50%!important;
    right:auto!important;
    bottom:calc(10px + env(safe-area-inset-bottom))!important;
    width:min(calc(100% - 22px),470px)!important;
    min-width:0!important;
    transform:translateX(-50%)!important;
    gap:5px!important;
    padding:6px!important;
    overflow:visible!important;
    border:1px solid rgba(255,255,255,.11)!important;
    border-radius:22px!important;
    background:rgba(13,14,18,.95)!important;
    box-shadow:0 14px 38px rgba(0,0,0,.48),0 0 0 1px rgba(255,34,54,.025) inset!important;
    backdrop-filter:blur(18px)!important;
    -webkit-backdrop-filter:blur(18px)!important;
    z-index:92!important;
  }
  .bottom-nav.v276-coach-hud button{
    display:grid!important;
    grid-template-rows:23px auto!important;
    place-items:center!important;
    gap:3px!important;
    width:100%!important;
    min-width:0!important;
    min-height:56px!important;
    margin:0!important;
    padding:6px 3px 5px!important;
    border:0!important;
    border-radius:16px!important;
    background:transparent!important;
    color:#777d87!important;
    font-size:9px!important;
    line-height:1!important;
    font-weight:820!important;
    white-space:nowrap!important;
    transition:background-color .14s ease,color .14s ease,border-color .14s ease!important;
  }
  .bottom-nav.v276-coach-hud button svg{
    width:22px!important;
    height:22px!important;
    fill:none!important;
    stroke:currentColor!important;
    stroke-width:1.8!important;
    stroke-linecap:round!important;
    stroke-linejoin:round!important;
  }
  .bottom-nav.v276-coach-hud button.active{
    color:#fff!important;
    background:linear-gradient(180deg,rgba(255,55,72,.16),rgba(255,35,52,.075))!important;
    box-shadow:0 0 0 1px rgba(255,65,82,.22) inset!important;
  }
  .bottom-nav.v276-coach-hud button.active svg{color:#ff4658!important}

  #coachStudentTabs{
    position:sticky!important;
    top:6px!important;
    z-index:22!important;
    padding:5px!important;
    border:1px solid rgba(255,255,255,.08)!important;
    border-radius:15px!important;
    background:rgba(13,14,18,.91)!important;
    backdrop-filter:blur(14px)!important;
    -webkit-backdrop-filter:blur(14px)!important;
  }
}
@media(max-width:390px){
  .bottom-nav.v276-coach-hud{
    width:calc(100% - 14px)!important;
    bottom:calc(7px + env(safe-area-inset-bottom))!important;
    border-radius:20px!important;
  }
  .bottom-nav.v276-coach-hud button{min-height:54px!important;font-size:8px!important}
}

/* Daily nutrition status inspired by the provided reference. */
.v276-nutrition-status{
  margin-bottom:12px!important;
  border-color:rgba(255,70,87,.18)!important;
  background:
    radial-gradient(circle at 92% 0,rgba(255,40,58,.07),transparent 31%),
    #101116!important;
}
.v276-status-head{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:12px;
}
.v276-status-head h3{margin:0}
.v276-status-head p{margin:4px 0 0}
.v276-kcal-line{
  display:flex;
  align-items:baseline;
  justify-content:space-between;
  gap:10px;
  margin-top:13px;
}
.v276-kcal-line strong{
  color:#f5f6f7;
  font-size:28px;
  font-variant-numeric:tabular-nums;
}
.v276-kcal-line span{color:#8e949d;font-size:10px}
.v276-status-bar,
.v276-macro-bar{
  overflow:hidden;
  border-radius:99px;
  background:#272a31;
}
.v276-status-bar{height:8px;margin-top:8px}
.v276-macro-bar{height:5px;margin-top:8px}
.v276-status-bar>span,
.v276-macro-bar>span{
  display:block;
  height:100%;
  border-radius:99px;
  background:linear-gradient(90deg,#b91f30,#ff4658);
}
.v276-macro-cards{
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:8px;
  margin-top:12px;
}
.v276-macro-card{
  min-width:0;
  padding:11px;
  border:1px solid #292d34;
  border-radius:12px;
  background:#0d0e12;
}
.v276-macro-card>span{
  display:block;
  color:#858b95;
  font-size:7px;
  font-weight:900;
  letter-spacing:.07em;
  text-transform:uppercase;
}
.v276-macro-card strong{
  display:block;
  margin-top:5px;
  color:#f3f4f6;
  font-size:17px;
  font-variant-numeric:tabular-nums;
}
.v276-macro-card small{
  display:block;
  margin-top:4px;
  color:#7d838d;
  font-size:8px;
}
.v276-meal-target{
  display:flex;
  flex-wrap:wrap;
  gap:5px;
  margin-top:6px;
}
.v276-meal-target span{
  padding:3px 6px;
  border:1px solid #2b2f36;
  border-radius:999px;
  background:#0d0e12;
  color:#8f959f;
  font-size:7px;
}
.v276-meal-range{
  margin-top:5px;
  color:#777e88;
  font-size:7px;
  line-height:1.35;
}
.v276-preset-grid{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:7px;
}
.v276-preset-grid .btn{
  width:100%;
  min-width:0;
  text-align:left;
}
.v276-calc-check{
  display:flex;
  justify-content:space-between;
  gap:10px;
  margin-top:7px;
  padding:9px 10px;
  border:1px solid #292d34;
  border-radius:10px;
  background:#0d0e12;
}
.v276-calc-check strong{font-size:8px;color:#dfe2e6}
.v276-calc-check span{font-size:8px;color:#8a919b;text-align:right}
.v276-calc-check.ok{border-color:rgba(59,213,138,.22)}
.v276-calc-check.warn{border-color:rgba(255,173,76,.28)}
@media(max-width:520px){
  .v276-macro-cards{grid-template-columns:1fr 1fr}
  .v276-macro-card:last-child{grid-column:1/-1}
  .v276-kcal-line{display:grid;grid-template-columns:1fr}
  .v276-preset-grid{grid-template-columns:1fr}
  .v276-calc-check{display:grid;grid-template-columns:1fr}
  .v276-calc-check span{text-align:left}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.76 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

runtime=r"""
<script id="v276CoachHudNutritionRuntime">
(function(){
  const VERSION='20.76';
  const mealPresetsV276=['Desayuno','Media mañana','Almuerzo','Merienda','Pre entreno','Post entreno','Cena','Colación nocturna'];

  function iconV276(type){
    const m={
      panel:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z"/></svg>',
      agenda:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5h14v15H5zM8 3v4M16 3v4M5 9h14"/><path d="M8.5 13h2M13.5 13h2M8.5 16.5h2M13.5 16.5h2"/></svg>',
      athlete:'<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="3.2"/><path d="M5.5 20c.7-4.2 3-6.3 6.5-6.3s5.8 2.1 6.5 6.3"/></svg>',
      add:'<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="9" cy="8" r="3"/><path d="M3.8 19c.6-3.8 2.3-5.7 5.2-5.7 1.5 0 2.7.5 3.6 1.5M18 9v8M14 13h8"/></svg>'
    };
    return m[type]||m.panel;
  }

  function coachHudV276(nav){
    nav.classList.remove('v275-student-hud');
    nav.classList.add('v276-coach-hud');
    nav.setAttribute('aria-label','Navegación Coach');
    const athleteActive=coachTab==='student';
    nav.innerHTML=
      '<button class="'+(coachTab==='dashboard'?'active':'')+'" onclick="coachTab=\'dashboard\';render()" aria-label="Panel">'+iconV276('panel')+'<span>Panel</span></button>'+
      '<button class="'+(coachTab==='agenda'?'active':'')+'" onclick="coachTab=\'agenda\';render()" aria-label="Agenda">'+iconV276('agenda')+'<span>Agenda</span></button>'+
      '<button class="'+(athleteActive?'active':'')+'" onclick="coachTab=\'student\';coachStudentTab=\'summary\';render()" aria-label="Alumno">'+iconV276('athlete')+'<span>Alumno</span></button>'+
      '<button onclick="newStudent()" aria-label="Nuevo alumno">'+iconV276('add')+'<span>Nuevo</span></button>';
  }

  const baseBottomNavV276=window.renderBottomNav||renderBottomNav;
  window.renderBottomNav=function(){
    const nav=el('bottomNav');
    if(mode==='coach'&&nav){
      coachHudV276(nav);
      return;
    }
    nav?.classList.remove('v276-coach-hud');
    return baseBottomNavV276.apply(this,arguments);
  };
  try{renderBottomNav=window.renderBottomNav}catch(_e){}

  function v276Num(v){
    const n=Number(v);
    return Number.isFinite(n)?n:0;
  }
  function v276Pct(consumed,target){
    if(!(Number(target)>0))return 0;
    return Math.max(0,Math.min(100,Math.round(Number(consumed||0)/Number(target)*100)));
  }
  function v276Remaining(consumed,target){
    if(!(Number(target)>0))return null;
    return Math.max(0,Number(target)-Number(consumed||0));
  }
  function macroCardV276(label,consumed,target,unit){
    const pct=v276Pct(consumed,target),remaining=v276Remaining(consumed,target);
    return '<div class="v276-macro-card"><span>'+esc(label)+'</span><strong>'+nFmt(consumed,0)+' / '+(Number(target)>0?nFmt(target,0):'—')+unit+'</strong>'+
      '<div class="v276-macro-bar"><span style="width:'+pct+'%"></span></div>'+
      '<small>'+(remaining==null?'Sin objetivo cargado':nFmt(remaining,0)+unit+' restantes · '+pct+'%')+'</small></div>';
  }
  function nutritionStatusV276(){
    const p=nutritionCache?.plan||{};
    const totals=nutritionLogTotals();
    const target=Number(p.target_kcal)||0;
    const pct=v276Pct(totals.kcal,target);
    const remaining=v276Remaining(totals.kcal,target);
    return '<div class="card v276-nutrition-status" id="v276NutritionStatus">'+
      '<div class="v276-status-head"><div><h3>Estado de hoy</h3><p class="muted tiny">'+esc(nutritionCache?.date||dateInputToday())+' · registro nutricional</p></div><span class="badge red">'+pct+'%</span></div>'+
      '<div class="v276-kcal-line"><strong>'+nFmt(totals.kcal,0)+' / '+(target?nFmt(target,0):'—')+' kcal</strong><span>'+(remaining==null?'Cargá una referencia diaria':nFmt(remaining,0)+' kcal restantes')+'</span></div>'+
      '<div class="v276-status-bar"><span style="width:'+pct+'%"></span></div>'+
      '<div class="v276-macro-cards">'+
        macroCardV276('Proteína',totals.protein_g,p.target_protein_g,' g')+
        macroCardV276('Carbohidratos',totals.carbs_g,p.target_carbs_g,' g')+
        macroCardV276('Grasas',totals.fat_g,p.target_fat_g,' g')+
      '</div>'+
      '<div class="nutrition-note" style="margin-top:10px"><strong>Referencia diaria</strong><div class="muted tiny" style="margin-top:4px">Los valores registrados dependen de porciones, marcas y preparación. Se interpretan junto con el plan definido por el coach.</div></div>'+
    '</div>';
  }

  function mealRangeV276(meal){
    const opts=(meal?.options||[]).map(o=>nutritionOptionTotals(o)).filter(x=>x.kcal||x.protein_g||x.carbs_g||x.fat_g);
    if(!opts.length)return '';
    const range=(key,d=0)=>{
      const xs=opts.map(x=>v276Num(x[key]));
      const lo=Math.min(...xs),hi=Math.max(...xs);
      return Math.abs(hi-lo)<0.05?nFmt(lo,d):nFmt(lo,d)+'–'+nFmt(hi,d);
    };
    return '<div class="v276-meal-range">Opciones: '+range('kcal',0)+' kcal · P '+range('protein_g',1)+' g · C '+range('carbs_g',1)+' g · G '+range('fat_g',1)+' g</div>';
  }
  function mealTargetsV276(meal){
    const vals=[
      ['kcal',meal?.target_kcal,''],
      ['P',meal?.target_protein_g,' g'],
      ['C',meal?.target_carbs_g,' g'],
      ['G',meal?.target_fat_g,' g']
    ].filter(x=>Number(x[1])>0);
    if(!vals.length)return '<div class="v276-meal-target"><span>Sin objetivo específico por comida</span></div>'+mealRangeV276(meal);
    return '<div class="v276-meal-target">'+vals.map(x=>'<span>'+x[0]+' '+nFmt(x[1],0)+x[2]+'</span>').join('')+'</div>'+mealRangeV276(meal);
  }

  window.openMealMacroTargetV276=function(mealId){
    const m=findNutritionMeal(mealId);if(!m)return;
    showModal('<div class="modal-head"><div><h3>Macros · '+esc(m.name||'Comida')+'</h3><div class="muted tiny">Referencia específica de esta comida. Es opcional.</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="form-grid">'+
        '<label class="tiny muted">kcal<input id="v276MealKcal" class="input" type="number" min="0" step="1" value="'+(m.target_kcal??'')+'"></label>'+
        '<label class="tiny muted">Proteína (g)<input id="v276MealP" class="input" type="number" min="0" step="1" value="'+(m.target_protein_g??'')+'"></label>'+
        '<label class="tiny muted">Carbos (g)<input id="v276MealC" class="input" type="number" min="0" step="1" value="'+(m.target_carbs_g??'')+'"></label>'+
        '<label class="tiny muted">Grasas (g)<input id="v276MealF" class="input" type="number" min="0" step="1" value="'+(m.target_fat_g??'')+'"></label>'+
      '</div>'+
      '<div class="nutrition-note" style="margin-top:10px"><strong>Control de coherencia</strong><div class="muted tiny">La app muestra estos objetivos junto a los macros reales de cada opción. Después guardá el plan para publicarlos.</div></div>'+
      '<div class="nutrition-builder-actions" style="margin-top:12px"><button class="btn primary" onclick="saveMealMacroTargetV276(\''+mealId+'\')">Aplicar</button><button class="btn ghost" onclick="clearMealMacroTargetV276(\''+mealId+'\')">Limpiar</button></div>');
  };
  window.saveMealMacroTargetV276=function(mealId){
    const m=findNutritionMeal(mealId);if(!m)return;
    const val=id=>{const raw=el(id)?.value;return raw===''||raw==null?null:Math.max(0,Number(raw)||0)};
    m.target_kcal=val('v276MealKcal');
    m.target_protein_g=val('v276MealP');
    m.target_carbs_g=val('v276MealC');
    m.target_fat_g=val('v276MealF');
    closeModal();renderNutritionCoachLoaded();toast('Referencia de la comida actualizada · guardá el plan');
  };
  window.clearMealMacroTargetV276=function(mealId){
    const m=findNutritionMeal(mealId);if(!m)return;
    m.target_kcal=null;m.target_protein_g=null;m.target_carbs_g=null;m.target_fat_g=null;
    closeModal();renderNutritionCoachLoaded();toast('Referencia por comida eliminada · guardá el plan');
  };

  function decorateMealsV276(coach){
    const pd=nutritionPlanData();
    const meals=pd?.meals||[];
    const blocks=[...document.querySelectorAll((coach?'#coachStudentBody ':'#studentSubBody ')+'.meal-block')];
    blocks.forEach((block,i)=>{
      const meal=meals[i];if(!meal)return;
      const info=block.querySelector('.meal-head>div:first-child');
      if(info&&!info.querySelector('.v276-meal-target')){
        info.insertAdjacentHTML('beforeend',mealTargetsV276(meal));
      }
      if(coach){
        const actions=block.querySelector('.meal-head .nutrition-builder-actions');
        if(actions&&!actions.querySelector('[data-v276-meal-target]')){
          actions.insertAdjacentHTML('afterbegin','<button class="btn small" data-v276-meal-target onclick="openMealMacroTargetV276(\''+meal.id+'\')">Macros</button>');
        }
      }
    });
  }

  function injectNutritionStatusV276(coach){
    const host=coach?el('coachStudentBody'):el('studentSubBody');
    if(!host)return;
    el('v276NutritionStatus')?.remove();
    host.insertAdjacentHTML('afterbegin',nutritionStatusV276());
    decorateMealsV276(coach);
    ensureMealSelectV276();
  }

  function mealOptionsV276(selected=''){
    const values=[...mealPresetsV276,'Colación','Otra'];
    return values.map(x=>'<option '+(x===selected?'selected':'')+'>'+esc(x)+'</option>').join('');
  }
  function ensureMealSelectV276(){
    const s=el('macroMeal');if(s){
      const current=s.value;
      s.innerHTML=mealOptionsV276(current);
      if([...s.options].some(o=>o.value===current))s.value=current;
    }
  }

  const baseStudentNutritionV276=window.renderNutritionStudentLoaded||renderNutritionStudentLoaded;
  window.renderNutritionStudentLoaded=function(){
    const out=baseStudentNutritionV276.apply(this,arguments);
    injectNutritionStatusV276(false);
    return out;
  };
  try{renderNutritionStudentLoaded=window.renderNutritionStudentLoaded}catch(_e){}

  const baseCoachNutritionV276=window.renderNutritionCoachLoaded||renderNutritionCoachLoaded;
  window.renderNutritionCoachLoaded=function(){
    const out=baseCoachNutritionV276.apply(this,arguments);
    injectNutritionStatusV276(true);
    return out;
  };
  try{renderNutritionCoachLoaded=window.renderNutritionCoachLoaded}catch(_e){}

  const baseCustomLogV276=window.openCustomMacroLog||openCustomMacroLog;
  window.openCustomMacroLog=function(){
    const out=baseCustomLogV276.apply(this,arguments);
    const s=el('cmMeal');if(s){
      const current=s.value;
      s.innerHTML=mealOptionsV276(current);
      if([...s.options].some(o=>o.value===current))s.value=current;
    }
    return out;
  };
  try{openCustomMacroLog=window.openCustomMacroLog}catch(_e){}

  window.addPresetNutritionMealV276=function(name){
    const pd=nutritionPlanData();if(!pd)return;
    const normalized=String(name||'').trim().toLowerCase();
    if((pd.meals||[]).some(x=>String(x.name||'').trim().toLowerCase()===normalized)){
      toast('Esa comida ya está en el plan');return;
    }
    pd.meals.push({id:uid('meal'),name:String(name||'Comida'),options:[],target_kcal:null,target_protein_g:null,target_carbs_g:null,target_fat_g:null});
    closeModal();renderNutritionCoachLoaded();toast('Comida agregada · guardá el plan');
  };

  window.addNutritionMeal=function(){
    showModal('<div class="modal-head"><div><h3>Agregar comida</h3><div class="muted tiny">Elegí una estructura habitual o creá una personalizada.</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="v276-preset-grid">'+mealPresetsV276.map(x=>'<button class="btn" onclick="addPresetNutritionMealV276(\''+x.replace(/'/g,"\\'")+'\')">'+esc(x)+'</button>').join('')+'</div>'+
      '<div style="height:12px"></div><label class="tiny muted">Otra comida<input id="newMealName" class="input" placeholder="Ej: Colación de tarde"></label>'+
      '<button class="btn primary" style="width:100%;margin-top:10px" onclick="confirmNutritionMeal()">Agregar personalizada</button>');
  };
  try{addNutritionMeal=window.addNutritionMeal}catch(_e){}

  window.confirmNutritionMeal=function(){
    const n=el('newMealName')?.value.trim();if(!n){toast('Escribí el nombre de la comida');return}
    return window.addPresetNutritionMealV276(n);
  };
  try{confirmNutritionMeal=window.confirmNutritionMeal}catch(_e){}

  window.__fjzV276={
    version:VERSION,
    premiumCoachMobileHud:true,
    coachHudFourPrimaryActions:true,
    coachStudentTabsMobilePolished:true,
    dailyNutritionStatus:true,
    macroConsumedTargetRemaining:true,
    perMealMacroTargets:true,
    mealOptionMacroRanges:true,
    expandedMealPresets:true,
    calculatorMealsUpToEight:true,
    calculatorEnergyCheckVisible:true,
    noExtraTimers:true,
    noExtraListeners:true
  };
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-coach-hud-nutrition-detail" content="20.76">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.76 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-coach-hud-nutrition-detail" content="20.76"',
    "premiumCoachMobileHud:true",
    "dailyNutritionStatus:true",
    "macroConsumedTargetRemaining:true",
    "perMealMacroTargets:true",
    "mealOptionMacroRanges:true",
    "expandedMealPresets:true",
    "calculatorMealsUpToEight:true",
    "calculatorEnergyCheckVisible:true",
    "v276-coach-hud",
    "v276NutritionStatus",
    "openMealMacroTargetV276",
    "Media mañana",
    "Colación nocturna",
]:
    if marker not in html:
        raise RuntimeError("V20.76 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.76 coach HUD + nutrition detail")
print("V20.76 BEFORE:",before)
print("V20.76 AFTER:",after)
print("V20.76 coach mobile HUD + daily macro dashboard + per-meal targets + calculator audit UI")
