import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# Remove the two superseded nutrition-learning runtimes. V13.6 patches the real
# final functions directly instead of adding another wrapper on top.
html=re.sub(r'<script id="v134NutritionLearnRuntime">.*?</script>','',html,flags=re.S)
html=re.sub(r'<script id="v135NutritionLearnFixRuntime">.*?</script>','',html,flags=re.S)

# Replace the REAL lexical nutrition sub-navigation used by the app.
nav_re=r"""function nutritionRecipesNavV70\(active\)\{.*?\n\}"""
nav_fn=r"""function nutritionRecipesNavV70(active){
  return '<div class="v70-recipe-tabs v136-nutrition-tabs" id="v136NutritionTabs">'+
    '<button class="btn '+(active==='plan'?'primary':'')+'" onclick="switchNutritionViewV70(\'plan\')">Mi plan</button>'+
    '<button class="btn '+(active==='recipes'?'primary':'')+'" onclick="switchNutritionViewV70(\'recipes\')">Recetas</button>'+
    '<button class="btn '+(active==='learn'?'primary':'')+'" onclick="switchNutritionViewV70(\'learn\')">Aprender</button>'+
  '</div>'
}"""
html,n_nav=re.subn(nav_re,nav_fn,html,count=1,flags=re.S)
if n_nav!=1:
    raise RuntimeError(f"V13.6 expected 1 nutritionRecipesNavV70 replacement, got {n_nav}")

# Replace the REAL student nutrition dispatcher so Learn is a first-class view.
dispatch_re=r"""const _renderNutritionStudentV70Base=renderNutritionStudent;\s*renderNutritionStudent=function\(\)\{\s*if\(nutritionStudentViewV70==='recipes'\)return renderRecipesStudentV70\(\);\s*return _renderNutritionStudentV70Base\(\)\s*\};"""
dispatch_fn=r"""const _renderNutritionStudentV70Base=renderNutritionStudent;
renderNutritionStudent=function(){
  if(nutritionStudentViewV70==='recipes')return renderRecipesStudentV70();
  if(nutritionStudentViewV70==='learn')return renderNutritionLearnV136();
  return _renderNutritionStudentV70Base()
};"""
html,n_dispatch=re.subn(dispatch_re,dispatch_fn,html,count=1,flags=re.S)
if n_dispatch!=1:
    raise RuntimeError(f"V13.6 expected 1 nutrition student dispatcher replacement, got {n_dispatch}")

css=r"""
<style id="v136StabilityAndNutritionStyles">
/* V13.6 · one stable box model across coach + student */
#view,#coachStudentBody,#studentSubBody{min-width:0;width:100%}
.card,.hero,.option-card,.student-row,.exercise-row,.metric,
.v114-profile-field,.v115-profile-item,.v122-event,.v122-kpi,
.v132-step,.v70-recipe-card,.v136-learn-card{
  box-sizing:border-box;min-width:0;max-width:100%
}
.grid,.grid.two,.metric-grid,.form-grid,.v114-profile-grid,.v115-profile-grid,
.v122-grid,.v132-assistant-top,.v136-learn-grid{
  min-width:0;align-items:stretch
}
.grid>*,
.grid.two>*,
.metric-grid>*,
.form-grid>*,
.v114-profile-grid>*,
.v115-profile-grid>*,
.v122-grid>*,
.v132-assistant-top>*,
.v136-learn-grid>*{min-width:0}
.form-grid label{min-width:0}
.input,select,textarea{box-sizing:border-box;max-width:100%}
.section-title{align-items:flex-start}
.section-title>div,.section-title>span,.section-title>.pill-row{min-width:0}
.section-title h3,.section-title p,.card strong,.card p,.card span{overflow-wrap:anywhere}
.pill-row,.day-actions,.exercise-actions,.nutrition-builder-actions{flex-wrap:wrap}
.tabs,.v70-recipe-tabs{overflow-x:auto;overflow-y:hidden;-webkit-overflow-scrolling:touch}
.tabs .tab,.v70-recipe-tabs .btn{flex:0 0 auto}
.v136-nutrition-tabs{
  display:flex;gap:8px;align-items:center;margin:0 0 14px;padding:4px;
  border:1px solid var(--border);border-radius:14px;background:rgba(255,255,255,.02)
}
.v136-nutrition-tabs .btn{margin:0;min-height:38px}
.v136-learn-hero{
  border:1px solid rgba(255,31,47,.22);
  background:linear-gradient(180deg,rgba(255,31,47,.055),rgba(255,255,255,.015))
}
.v136-learn-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:12px}
.v136-learn-card{border:1px solid var(--border);border-radius:14px;background:var(--card);overflow:hidden}
.v136-learn-btn{width:100%;display:flex;justify-content:space-between;gap:12px;align-items:center;padding:14px;border:0;background:transparent;color:var(--text);text-align:left;cursor:pointer}
.v136-learn-head{display:flex;gap:10px;align-items:center;min-width:0}
.v136-learn-icon{width:38px;height:38px;border-radius:11px;display:grid;place-items:center;border:1px solid var(--border);background:rgba(255,255,255,.025);font-size:14px;font-weight:900;flex:0 0 auto}
.v136-learn-btn strong{display:block;font-size:14px}
.v136-learn-btn span{display:block;margin-top:3px;font-size:10px;color:var(--muted)}
.v136-learn-body{display:none;padding:0 14px 14px}
.v136-learn-card.open .v136-learn-body{display:block}
.v136-learn-card.open .v136-arrow{transform:rotate(180deg)}
.v136-arrow{transition:.15s ease;font-size:11px;color:var(--muted)}
.v136-learn-section{border-top:1px solid var(--border);padding-top:10px;margin-top:10px}
.v136-learn-section:first-child{border-top:0;padding-top:0;margin-top:0}
.v136-learn-section strong{font-size:11px}
.v136-learn-section p{font-size:11px;line-height:1.55;color:var(--muted);margin:5px 0 0}
.v136-chip-row{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.v136-chip{border:1px solid var(--border);border-radius:999px;padding:5px 8px;font-size:9px;color:var(--muted)}
.v136-practical{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:12px}
.v136-practical>div{border:1px solid var(--border);border-radius:12px;padding:10px;background:rgba(255,255,255,.02)}
.v136-practical strong{display:block;font-size:11px;margin-bottom:4px}
.v136-practical span{font-size:10px;color:var(--muted);line-height:1.45}
.v136-note{margin-top:12px;border:1px dashed var(--border);border-radius:11px;padding:10px;font-size:10px;color:var(--muted);line-height:1.5}
.v136-coach-learn-link{margin-bottom:14px}
@media(max-width:760px){
  .grid.two,.v136-learn-grid,.v136-practical{grid-template-columns:1fr!important}
  .card{padding-left:12px!important;padding-right:12px!important}
  .section-title{gap:10px}
}
</style>
"""

js=r"""
<script id="v136NutritionAndStabilityRuntime">
(function(){
  const TOPICS=[
    ['P','Proteínas','Recuperación, tejidos y saciedad',
      'Las proteínas aportan aminoácidos que el cuerpo usa para construir y reparar tejidos y para muchas otras funciones.',
      'En personas que entrenan, una ingesta adecuada acompaña la recuperación y el desarrollo muscular junto con entrenamiento, energía suficiente y descanso.',
      ['Carnes, pollo y pescado','Huevos','Lácteos y yogures','Legumbres','Soja y derivados','Whey como opción práctica'],
      'Más proteína no significa automáticamente más músculo. Importa el plan completo.'],
    ['C','Carbohidratos','Energía para entrenar y para el día',
      'Los carbohidratos son una fuente importante de energía y aparecen en muchos alimentos diferentes.',
      'Pueden ser útiles especialmente alrededor del entrenamiento porque ayudan a llegar con energía y a reponer lo utilizado.',
      ['Arroz, papa y batata','Avena y cereales','Pan y pastas','Frutas','Legumbres'],
      'No hace falta demonizarlos. El contexto total y las cantidades importan más que un nutriente aislado.'],
    ['G','Grasas','Hormonas, células y vitaminas',
      'Las grasas son esenciales y forman parte de las células, participan en funciones hormonales y ayudan a absorber vitaminas.',
      'No conviene eliminarlas; se ajustan dentro del plan según necesidades y preferencias.',
      ['Aceite de oliva','Palta','Frutos secos','Semillas','Pasta de maní','Pescados grasos'],
      'La grasa que comés y la grasa corporal no son la misma cosa.'],
    ['F','Fibra y vegetales','Digestión, saciedad y variedad',
      'La fibra forma parte de alimentos vegetales y existen distintos tipos con funciones diferentes.',
      'Frutas, verduras, legumbres, cereales integrales y semillas aportan fibra y variedad de micronutrientes.',
      ['Verduras','Frutas enteras','Avena','Legumbres','Semillas','Cereales integrales'],
      'Si comés poca fibra, suele ser mejor aumentarla gradualmente y acompañarla con buena hidratación.'],
    ['H','Hidratación','Rendimiento y funcionamiento diario',
      'El agua participa en gran parte de los procesos del organismo.',
      'Llegar bien hidratado al entrenamiento puede ayudar al rendimiento y al bienestar.',
      ['Agua como base','Infusiones','Frutas y verduras también aportan agua'],
      'No existe una cantidad universal idéntica para todos: cambia con clima, actividad y sudoración.'],
    ['M','Vitaminas y minerales','Lo pequeño también importa',
      'Los micronutrientes se necesitan en cantidades menores, pero cumplen funciones importantes en todo el organismo.',
      'La variedad de alimentos suele ser más útil que perseguir un único “superalimento”.',
      ['Frutas y verduras variadas','Lácteos o alternativas fortificadas','Carnes, huevos y legumbres','Frutos secos y semillas'],
      'Los suplementos no reemplazan automáticamente una alimentación variada.'],
    ['PL','Cómo pensar una comida','Una estructura simple y flexible',
      'Podés pensar una comida como una combinación de proteína, fuente de energía, frutas/vegetales y grasas según el caso.',
      'No hace falta que cada plato sea perfecto; la consistencia a lo largo del tiempo importa más.',
      ['Proteína + arroz/papa + verduras','Huevos + pan/avena + fruta','Yogur + avena + fruta + frutos secos'],
      'Buscar comidas “perfectas” puede volver el plan más difícil de sostener.'],
    ['PRE','Antes y después de entrenar','Energía, tolerancia y recuperación',
      'La comida previa debería adaptarse al horario y a la tolerancia digestiva. Después, importa volver a una alimentación normal y suficiente.',
      'No hay una única comida obligatoria ni una combinación idéntica para todos.',
      ['Antes: fruta, tostadas, yogur o avena según tolerancia','Después: una comida completa','Hidratación según necesidad'],
      'No existe una ventana de pocos minutos que arruine el progreso si no tomás un batido enseguida.'],
    ['ET','Leer etiquetas','Qué mirar realmente',
      'La etiqueta sirve para entender porciones, ingredientes y composición nutricional.',
      'Es útil para comparar productos similares, no para juzgar un alimento por un único número.',
      ['Revisar la porción','Comparar productos de la misma categoría','Mirar ingredientes','Revisar proteína o fibra cuando tenga sentido'],
      '“Light”, “fit”, “natural” o “sin azúcar” no significa automáticamente que sea mejor para cualquier objetivo.'],
    ['S','Suplementos y mitos','Complementos, no atajos',
      'Los suplementos pueden facilitar necesidades concretas, pero no reemplazan una base organizada.',
      'La utilidad depende del producto y del contexto de cada persona.',
      ['Whey puede facilitar llegar a la proteína del plan','No todos necesitan suplementos','Una comida aislada no define tu progreso'],
      'Antes de buscar atajos, suele ser más útil ordenar alimentación, sueño, entrenamiento y constancia.']
  ];

  function topicV136(t,i){
    return '<div class="v136-learn-card" id="v136Topic'+i+'">'+
      '<button class="v136-learn-btn" onclick="toggleNutritionTopicV136('+i+')">'+
        '<div class="v136-learn-head"><div class="v136-learn-icon">'+esc(t[0])+'</div><div><strong>'+esc(t[1])+'</strong><span>'+esc(t[2])+'</span></div></div>'+
        '<div class="v136-arrow">⌄</div>'+
      '</button>'+
      '<div class="v136-learn-body">'+
        '<div class="v136-learn-section"><strong>Qué es</strong><p>'+esc(t[3])+'</p></div>'+
        '<div class="v136-learn-section"><strong>Por qué importa</strong><p>'+esc(t[4])+'</p></div>'+
        '<div class="v136-learn-section"><strong>Ejemplos</strong><div class="v136-chip-row">'+t[5].map(x=>'<span class="v136-chip">'+esc(x)+'</span>').join('')+'</div></div>'+
        '<div class="v136-learn-section"><strong>Error común</strong><p>'+esc(t[6])+'</p></div>'+
      '</div>'+
    '</div>';
  }

  window.toggleNutritionTopicV136=function(i){el('v136Topic'+i)?.classList.toggle('open')};

  function educationBodyV136(includeNav){
    return (includeNav?nutritionRecipesNavV70('learn'):'')+
      '<div class="card v136-learn-hero">'+
        '<div class="section-title"><div><h3>Aprender nutrición</h3><div class="muted tiny">Conceptos simples para entender mejor el plan y tomar decisiones con más criterio.</div></div><span class="badge blue">TEAM FJZ</span></div>'+
        '<div class="v136-practical">'+
          '<div><strong>Entendé el porqué</strong><span>No hace falta memorizar números; la idea es entender para qué sirve cada parte de la alimentación.</span></div>'+
          '<div><strong>Aplicalo al plan</strong><span>El plan personal sigue siendo la referencia. Esta sección explica conceptos generales.</span></div>'+
          '<div><strong>Mirá tendencias</strong><span>Una comida o un día aislado no define el progreso. Importa lo que se sostiene en el tiempo.</span></div>'+
        '</div>'+
      '</div>'+
      '<div class="v136-learn-grid">'+TOPICS.map(topicV136).join('')+'</div>'+
      '<div class="v136-note"><strong>Importante:</strong> contenido educativo general. Ante alergias, síntomas persistentes, condiciones médicas o indicaciones clínicas, corresponde seguir la orientación de un profesional de salud.</div>';
  }

  window.renderNutritionLearnV136=function(){
    const b=el('studentSubBody');if(!b)return;
    b.innerHTML=educationBodyV136(true);
  };

  window.openCoachNutritionLearnV136=function(){
    showModal('<div class="modal-head"><div><h3>Guía nutricional del alumno</h3><div class="muted tiny">Vista del contenido educativo disponible en Nutrición.</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+educationBodyV136(false));
  };

  function ensureStudentNutritionNavV136(){
    if(currentProfile?.role!=='student'||studentTab!=='nutrition')return;
    const b=el('studentSubBody');if(!b)return;
    if(nutritionStudentViewV70==='learn'){
      if(!b.querySelector('.v136-learn-hero'))renderNutritionLearnV136();
      return;
    }
    const current=nutritionStudentViewV70==='recipes'?'recipes':'plan';
    const old=[...b.querySelectorAll('.v70-recipe-tabs')];
    if(!old.length){
      b.insertAdjacentHTML('afterbegin',nutritionRecipesNavV70(current));
    }else{
      const first=old[0];
      if(![...first.querySelectorAll('button')].some(x=>(x.textContent||'').trim()==='Aprender')){
        first.outerHTML=nutritionRecipesNavV70(current);
      }
      old.slice(1).forEach(x=>x.remove());
    }
  }

  function ensureCoachNutritionLearnV136(){
    if(currentProfile?.role!=='coach'||coachTab!=='student'||coachStudentTab!=='nutrition')return;
    const b=el('coachStudentBody');if(!b||el('v136CoachLearnLink'))return;
    const wrap=document.createElement('div');
    wrap.id='v136CoachLearnLink';
    wrap.className='v136-coach-learn-link';
    wrap.innerHTML='<div class="v136-nutrition-tabs"><button class="btn primary">Plan del alumno</button><button class="btn" onclick="openCoachRecipesV70()">Recetas</button><button class="btn" onclick="openCoachNutritionLearnV136()">Aprender</button></div>';
    b.insertBefore(wrap,b.firstChild);
  }

  // Final render hook: one post-render frame, no delayed timeouts.
  const baseRenderV136=render;
  render=function(){
    const out=baseRenderV136.apply(this,arguments);
    fjzPostRenderV125('nutrition-final-v136',()=>{
      ensureStudentNutritionNavV136();
      ensureCoachNutritionLearnV136();
    });
    return out;
  };

  // Async nutrition loaders can replace the body after the main render.
  const baseStudentLoadedV136=renderNutritionStudentLoaded;
  renderNutritionStudentLoaded=function(){
    const out=baseStudentLoadedV136.apply(this,arguments);
    ensureStudentNutritionNavV136();
    return out;
  };

  const baseCoachLoadedV136=renderNutritionCoachLoaded;
  renderNutritionCoachLoaded=function(){
    const out=baseCoachLoadedV136.apply(this,arguments);
    ensureCoachNutritionLearnV136();
    return out;
  };

  window.__fjzV136={
    version:'13.6',
    nutritionLearnFinal:true,
    stableGrid:true,
    postRenderFrame:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

# Build-time validation: prove the real lexical function contains Aprender and
# old broken runtimes are gone.
if '<script id="v134NutritionLearnRuntime">' in html or '<script id="v135NutritionLearnFixRuntime">' in html:
    raise RuntimeError("Superseded nutrition runtimes still present")
if html.count("Aprender</button>") < 2:
    raise RuntimeError("Aprender is not present in both student and coach navigation")
if "if(nutritionStudentViewV70==='learn')return renderNutritionLearnV136();" not in html:
    raise RuntimeError("Learn dispatcher is not wired into real nutrition renderer")

print("TEAM FJZ V13.6 final nutrition/stability:",len(html),"bytes")
print("V13.6 Aprender button occurrences:",html.count("Aprender</button>"))
print("V13.6 observers:",html.count("new MutationObserver"),"timeouts:",html.count("setTimeout("))
