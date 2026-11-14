import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")
required=[
 'meta name="fjz-coach-ux-final-polish" content="22.3C-UX"',
 'meta name="fjz-athlete-360-workspace" content="22.3B"',
 'meta name="fjz-nutrition-mobile-macro-geometry" content="21.32"',
 'meta name="fjz-confirmed-save-feedback" content="20.64"',
 'student_logging_enabled',
 "from('nutrition_logs')",
 "from('nutrition_plans')",
 'function nutritionOptionTotals',
 'function nutritionAmountText',
 'window.openMacroTargetCalculatorV272',
 'function renderRecipesStudentV70',
]
for marker in required:
    if marker not in html: raise RuntimeError("V22 4A prerequisite missing: "+marker)
js=pathlib.Path("src/modules/nutrition/premium.js").read_text(encoding="utf-8")
css=pathlib.Path("src/ui/nutrition-premium.css").read_text(encoding="utf-8")
if "</script" in js.lower(): raise RuntimeError("V22 4A module contains closing script markup")
if re.search(r'\b(?:window\.)?render\s*=\s*function|const\s+_render\w*\s*=\s*render\b',js):
    raise RuntimeError("V22 4A must not wrap global render")
if re.search(r'addEventListener\s*\(|setTimeout\s*\(|setInterval\s*\(|new\s+MutationObserver|\.channel\s*\(',js):
    raise RuntimeError("V22 4A module must not add global listeners, timers, observers or realtime channels")
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V22 4A expected one consolidated stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]
html=html.replace("</head>",'<meta name="fjz-v22-4a-nutrition-premium" content="22.4A">\n</head>',1)
bridge=r'''<script id="v22NutritionPremiumAuthorityBridge">
(function(){
  window.__fjzNutritionContextV22=function(){
    let s=null,aid=null;try{s=student()}catch(_e){}
    try{aid=nutritionAthleteId()}catch(_e){}
    return {
      profile:typeof currentProfile!=='undefined'?currentProfile:null,
      userId:typeof currentUser!=='undefined'?currentUser?.id:null,
      coachTab:typeof coachTab!=='undefined'?coachTab:null,
      coachStudentTab:typeof coachStudentTab!=='undefined'?coachStudentTab:null,
      studentTab:typeof studentTab!=='undefined'?studentTab:null,
      nutritionStudentView:typeof nutritionStudentViewV70!=='undefined'?nutritionStudentViewV70:'plan',
      student:s,
      athleteId:aid,
      cache:typeof nutritionCache!=='undefined'?nutritionCache:null,
      supabase:typeof supabaseClient!=='undefined'?supabaseClient:null
    };
  };
  window.__fjzNutritionActionsV22={
    load:(force,date)=>loadNutrition(force,date),
    optionTotals:o=>nutritionOptionTotals(o),
    amountText:i=>nutritionAmountText(i),
    createPlan:()=>createNutritionPlan(),
    savePlan:()=>saveNutritionPlan(),
    addMeal:()=>addNutritionMeal(),
    renameMeal:id=>renameNutritionMeal(id),
    deleteMeal:id=>deleteNutritionMeal(id),
    addOption:id=>addNutritionOption(id),
    deleteOption:(m,o)=>deleteNutritionOption(m,o),
    openFood:(m,o)=>openNutritionFoodPicker(m,o),
    editAmount:(m,o,i)=>editNutritionItemMeasure(m,o,i),
    removeFood:(m,o,i)=>removeNutritionItem(m,o,i),
    mealMacros:id=>typeof openMealMacroTargetV276==='function'?openMealMacroTargetV276(id):false,
    coachCalculator:()=>typeof openMacroTargetCalculatorV272==='function'?openMacroTargetCalculatorV272():false,
    recipes:()=>typeof switchNutritionViewV70==='function'?switchNutritionViewV70('recipes'):false,
    renderRecipesStudent:()=>typeof renderRecipesStudentV70==='function'?renderRecipesStudentV70():false,
    coachRecipes:()=>typeof openCoachRecipesV70==='function'?openCoachRecipesV70():false,
    templates:()=>typeof openNutritionTemplatesV63==='function'?openNutritionTemplatesV63():false,
    saveTemplate:()=>typeof openSaveNutritionTemplateV63==='function'?openSaveNutritionTemplateV63():false,
    historyHtml:()=>typeof nutritionHistoryCardV63==='function'?nutritionHistoryCardV63():'',
    addSupplement:()=>typeof openSupplementPickerV94==='function'?openSupplementPickerV94():false,
    editSupplement:i=>typeof editSupplementV94==='function'?editSupplementV94(i):false,
    removeSupplement:i=>typeof removeSupplementV94==='function'?removeSupplementV94(i):false,
    addHabit:()=>typeof openAddNutritionHabitV66==='function'?openAddNutritionHabitV66():false,
    toggleHabit:(id,on)=>typeof toggleCoachHabitV66==='function'?toggleCoachHabitV66(id,on):false,
    deleteHabit:id=>typeof deleteCustomHabitV66==='function'?deleteCustomHabitV66(id):false,
    calculatorAdd:()=>typeof addCalculatorLog==='function'?addCalculatorLog():false,
    customLog:()=>typeof openCustomMacroLog==='function'?openCustomMacroLog():false,
    previewMacro:()=>typeof updateMacroPreview==='function'?updateMacroPreview():false,
    showModal:body=>showModal(body),
    formatDate:v=>typeof fmtDate==='function'?fmtDate(v):String(v||''),
    today:()=>typeof dateInputToday==='function'?dateInputToday():new Date().toISOString().slice(0,10),
    uuid:()=>typeof crypto!=='undefined'&&crypto.randomUUID?crypto.randomUUID():null,
    cloudError:e=>typeof cloudErr==='function'?cloudErr(e):String(e?.message||e||'Error')
  };
})();
</script>
'''
runtime=bridge+'<script id="v22NutritionPremiumRuntime">\n'+js+'\n</script>\n'+r'''<script id="v22NutritionPremiumInstall">
(function(){
  if(!window.TeamFJZNutritionPremium?.install?.())throw new Error("TEAM FJZ V22 4A install failed");
  window.__fjzRenderNutritionStudentLegacyV22=renderNutritionStudent;
  window.__fjzRenderNutritionCoachLegacyV22=renderNutritionCoach;
  window.__fjzRenderNutritionStudentLoadedLegacyV22=renderNutritionStudentLoaded;
  window.__fjzRenderNutritionCoachLoadedLegacyV22=renderNutritionCoachLoaded;
  renderNutritionStudent=function(){return window.TeamFJZNutritionPremium.startStudent(false)};
  renderNutritionCoach=function(){return window.TeamFJZNutritionPremium.startCoach(false)};
  renderNutritionStudentLoaded=function(){return window.TeamFJZNutritionPremium.renderStudent()};
  renderNutritionCoachLoaded=function(){return window.TeamFJZNutritionPremium.renderCoach()};
  window.renderNutritionStudent=renderNutritionStudent;
  window.renderNutritionCoach=renderNutritionCoach;
  window.renderNutritionStudentLoaded=renderNutritionStudentLoaded;
  window.renderNutritionCoachLoaded=renderNutritionCoachLoaded;
})();
</script>
'''
html=html.replace("</body>",runtime+"</body>",1)
markers=[
 'meta name="fjz-v22-4a-nutrition-premium" content="22.4A"',
 'id="v22NutritionPremiumAuthorityBridge"','id="v22NutritionPremiumRuntime"','id="v22NutritionPremiumInstall"',
 "VERSION='22.4A'","FJZ4A_OPTION:","meal_group_id","student_logging_enabled",
 "TeamFJZNutritionPremium.renderStudent","TeamFJZNutritionPremium.renderCoach",
 'meta name="fjz-coach-ux-final-polish" content="22.3C-UX"',
 'cloudConfirmationBeforeSuccess:true'
]
for marker in markers:
    if marker not in html: raise RuntimeError("V22 4A output marker missing: "+marker)
p.write_text(html,encoding="utf-8")
print("TEAM FJZ V22 4A Nutrition Premium injected",len(html))
