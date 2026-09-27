import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v134NutritionLearnStyles">
.v134-learn-hero{border:1px solid rgba(255,31,47,.22);background:linear-gradient(180deg,rgba(255,31,47,.055),rgba(255,255,255,.015));}
.v134-learn-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:12px}
.v134-learn-card{border:1px solid var(--border);border-radius:14px;background:var(--card);overflow:hidden}
.v134-learn-btn{width:100%;display:flex;justify-content:space-between;gap:12px;align-items:center;padding:14px;border:0;background:transparent;color:var(--text);text-align:left;cursor:pointer}
.v134-learn-btn strong{display:block;font-size:14px}
.v134-learn-btn span{display:block;margin-top:3px;font-size:10px;color:var(--muted)}
.v134-learn-icon{width:38px;height:38px;border-radius:11px;display:grid;place-items:center;border:1px solid var(--border);background:rgba(255,255,255,.025);font-size:18px;flex:0 0 auto}
.v134-learn-head{display:flex;gap:10px;align-items:center;min-width:0}
.v134-learn-body{display:none;padding:0 14px 14px}
.v134-learn-card.open .v134-learn-body{display:block}
.v134-learn-card.open .v134-arrow{transform:rotate(180deg)}
.v134-arrow{transition:.15s ease;font-size:11px;color:var(--muted)}
.v134-learn-section{border-top:1px solid var(--border);padding-top:10px;margin-top:10px}
.v134-learn-section:first-child{border-top:0;padding-top:0;margin-top:0}
.v134-learn-section strong{font-size:11px}
.v134-learn-section p,.v134-learn-section ul{font-size:11px;line-height:1.55;color:var(--muted);margin:5px 0 0}
.v134-learn-section ul{padding-left:17px}
.v134-chip-row{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.v134-chip{border:1px solid var(--border);border-radius:999px;padding:5px 8px;font-size:9px;color:var(--muted)}
.v134-practical{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:12px}
.v134-practical>div{border:1px solid var(--border);border-radius:12px;padding:10px;background:rgba(255,255,255,.02)}
.v134-practical strong{display:block;font-size:11px;margin-bottom:4px}
.v134-practical span{font-size:10px;color:var(--muted);line-height:1.45}
.v134-note{margin-top:12px;border:1px dashed var(--border);border-radius:11px;padding:10px;font-size:10px;color:var(--muted);line-height:1.5}
@media(max-width:760px){.v134-learn-grid{grid-template-columns:1fr}.v134-practical{grid-template-columns:1fr}}
</style>
"""

js=r"""
<script id="v134NutritionLearnRuntime">
(function(){
  const TOPICS=[
    {
      id:'protein',icon:'P',title:'Proteínas',sub:'Recuperación, tejidos y saciedad',
      what:'Las proteínas están formadas por aminoácidos. El cuerpo las usa para construir y reparar tejidos, además de participar en enzimas, defensas y otras funciones.',
      why:'En personas que entrenan, una ingesta adecuada ayuda a sostener la recuperación y el desarrollo muscular junto con entrenamiento, energía suficiente y descanso.',
      examples:['Carnes, pollo y pescado','Huevos','Lácteos y yogures','Legumbres','Soja y derivados','Whey como opción práctica, no obligatoria'],
      mistake:'Pensar que “más proteína” siempre significa “más músculo”. El resultado depende del plan completo, del entrenamiento y de la recuperación.'
    },
    {
      id:'carbs',icon:'C',title:'Carbohidratos',sub:'Energía para entrenar y para el día',
      what:'Los carbohidratos son una fuente importante de energía. Se encuentran tanto en alimentos naturales como en productos procesados, y no todos aportan la misma calidad nutricional.',
      why:'Pueden ser especialmente útiles alrededor del entrenamiento porque ayudan a llegar con energía y a reponer lo utilizado durante la actividad.',
      examples:['Arroz, papa y batata','Avena y cereales','Pan y pastas','Frutas','Legumbres','Tortillas y otros alimentos según el plan'],
      mistake:'Creer que los carbohidratos “engordan por sí solos”. El contexto total de alimentación, actividad y cantidades importa más que demonizar un nutriente.'
    },
    {
      id:'fats',icon:'G',title:'Grasas',sub:'Hormonas, células y vitaminas',
      what:'Las grasas son un nutriente esencial. Forman parte de las membranas celulares, participan en funciones hormonales y ayudan a absorber vitaminas liposolubles.',
      why:'No conviene eliminarlas. Lo importante es incluir fuentes variadas y ajustar cantidades al plan individual.',
      examples:['Aceite de oliva','Palta','Frutos secos','Semillas','Pasta de maní','Pescados grasos'],
      mistake:'Pensar que “grasa de la comida = grasa corporal” de forma directa. Son conceptos distintos.'
    },
    {
      id:'fiber',icon:'F',title:'Fibra y vegetales',sub:'Digestión, saciedad y variedad',
      what:'La fibra es una parte de los alimentos vegetales que el cuerpo no digiere completamente. Hay distintos tipos y cada uno cumple funciones diferentes.',
      why:'Una alimentación con frutas, verduras, legumbres, cereales integrales y semillas suele aportar fibra, micronutrientes y variedad.',
      examples:['Verduras de distintos colores','Frutas enteras','Avena','Legumbres','Semillas','Cereales integrales'],
      mistake:'Subir la fibra de golpe. Si alguien come muy poca, suele ser mejor aumentar gradualmente y acompañar con buena hidratación.'
    },
    {
      id:'hydration',icon:'H',title:'Hidratación',sub:'Rendimiento y funcionamiento diario',
      what:'El agua participa en prácticamente todos los procesos del organismo. Las necesidades cambian según clima, actividad, alimentación y sudoración.',
      why:'Llegar bien hidratado al entrenamiento puede ayudar al rendimiento y al bienestar general.',
      examples:['Agua como base','Infusiones sin exceso de azúcar','Frutas y verduras también aportan agua'],
      mistake:'Esperar a tener mucha sed para recién tomar líquido o copiar una cantidad fija que no considera actividad y clima.'
    },
    {
      id:'micros',icon:'M',title:'Vitaminas y minerales',sub:'Lo pequeño también importa',
      what:'Los micronutrientes se necesitan en cantidades menores que los macronutrientes, pero son fundamentales para funciones como metabolismo, sistema inmune, sangre, huesos y sistema nervioso.',
      why:'La variedad de alimentos suele ser más importante que perseguir un único “superalimento”.',
      examples:['Frutas y verduras variadas','Lácteos o alternativas fortificadas','Carnes, huevos y legumbres','Frutos secos y semillas'],
      mistake:'Usar suplementos como reemplazo automático de una alimentación variada. Si hay una necesidad específica, conviene evaluarla con un profesional de salud.'
    },
    {
      id:'plate',icon:'🍽',title:'Cómo pensar una comida',sub:'Una estructura simple y flexible',
      what:'Una comida puede pensarse como una combinación de fuente de proteína, fuente de energía, vegetales/frutas y alguna fuente de grasa según el caso.',
      why:'No hace falta que cada plato sea perfecto. La consistencia a lo largo de los días importa más que una sola comida.',
      examples:['Proteína + arroz/papa + verduras','Huevos + pan/avena + fruta','Yogur + avena + fruta + frutos secos'],
      mistake:'Buscar comidas “perfectas” y después abandonar porque son difíciles de sostener.'
    },
    {
      id:'training',icon:'⚡',title:'Antes y después de entrenar',sub:'Energía, tolerancia y recuperación',
      what:'La comida previa debería ser fácil de tolerar y compatible con el horario. Después de entrenar, lo importante es volver a comer dentro de una rutina normal que cubra energía y nutrientes.',
      why:'No existe una única comida obligatoria. El mejor esquema es el que se adapta a horarios, digestión y plan.',
      examples:['Antes: fruta, tostadas, yogur, avena según tolerancia','Después: comida completa con proteína y carbohidratos','Hidratación antes, durante y después según necesidad'],
      mistake:'Creer que existe una “ventana” de pocos minutos en la que todo se pierde si no se toma un batido.'
    },
    {
      id:'labels',icon:'🔎',title:'Leer etiquetas sin complicarse',sub:'Qué mirar realmente',
      what:'La etiqueta ayuda a entender ingredientes, porción y composición nutricional. No hace falta juzgar un alimento por un solo número.',
      why:'Sirve para comparar productos similares y saber qué estamos consumiendo.',
      examples:['Revisar porción declarada','Comparar proteína/fibra cuando tenga sentido','Mirar ingredientes','Comparar productos de la misma categoría'],
      mistake:'Pensar que “light”, “fit”, “natural” o “sin azúcar” automáticamente significa que un producto es mejor para cualquier objetivo.'
    },
    {
      id:'supplements',icon:'S',title:'Suplementos',sub:'Complemento, no base',
      what:'Un suplemento puede ser útil cuando facilita cubrir una necesidad concreta, pero no reemplaza una alimentación organizada.',
      why:'La utilidad depende del producto, de la persona y del contexto. No todo lo que se vende como deportivo es necesario.',
      examples:['Whey puede ser una forma práctica de sumar proteína','Otros suplementos deben evaluarse caso por caso'],
      mistake:'Comprar suplementos antes de ordenar sueño, alimentación, entrenamiento y constancia.'
    },
    {
      id:'myths',icon:'?',title:'Mitos rápidos',sub:'Ideas comunes que conviene revisar',
      what:'La nutrición suele simplificarse demasiado en redes. Una regla aislada casi nunca explica por sí sola el resultado de una persona.',
      why:'Aprender a mirar contexto ayuda a evitar cambios extremos o innecesarios.',
      examples:['No hay un alimento que por sí solo “queme grasa”','No hace falta eliminar grupos enteros sin motivo','Una comida fuera del plan no arruina semanas de constancia','El peso puede variar por muchos factores además de grasa corporal'],
      mistake:'Cambiar el plan cada pocos días por una tendencia, video o número aislado.'
    }
  ];

  window.nutritionRecipesNavV70=function(active){
    return '<div class="v70-recipe-tabs">'+
      '<button class="btn '+(active==='plan'?'primary':'')+'" onclick="switchNutritionViewV70(\'plan\')">Mi plan</button>'+
      '<button class="btn '+(active==='recipes'?'primary':'')+'" onclick="switchNutritionViewV70(\'recipes\')">Recetas</button>'+
      '<button class="btn '+(active==='learn'?'primary':'')+'" onclick="switchNutritionViewV70(\'learn\')">Aprender</button>'+
    '</div>';
  };

  function topicCardV134(t){
    return '<div class="v134-learn-card" id="v134-'+t.id+'">'+
      '<button class="v134-learn-btn" onclick="toggleNutritionTopicV134(\''+t.id+'\')">'+
        '<div class="v134-learn-head"><div class="v134-learn-icon">'+esc(t.icon)+'</div><div><strong>'+esc(t.title)+'</strong><span>'+esc(t.sub)+'</span></div></div>'+
        '<div class="v134-arrow">⌄</div>'+
      '</button>'+
      '<div class="v134-learn-body">'+
        '<div class="v134-learn-section"><strong>Qué es</strong><p>'+esc(t.what)+'</p></div>'+
        '<div class="v134-learn-section"><strong>Por qué importa</strong><p>'+esc(t.why)+'</p></div>'+
        '<div class="v134-learn-section"><strong>Ejemplos</strong><div class="v134-chip-row">'+t.examples.map(x=>'<span class="v134-chip">'+esc(x)+'</span>').join('')+'</div></div>'+
        '<div class="v134-learn-section"><strong>Error común</strong><p>'+esc(t.mistake)+'</p></div>'+
      '</div>'+
    '</div>';
  }

  window.toggleNutritionTopicV134=function(id){
    el('v134-'+id)?.classList.toggle('open');
  };

  window.renderNutritionLearnV134=function(){
    const b=el('studentSubBody');if(!b)return;
    b.innerHTML=
      nutritionRecipesNavV70('learn')+
      '<div class="card v134-learn-hero">'+
        '<div class="section-title"><div><h3>Aprender nutrición</h3><div class="muted tiny">Conceptos simples para entender mejor tu plan y tomar decisiones con más criterio.</div></div><span class="badge blue">TEAM FJZ</span></div>'+
        '<div class="v134-practical">'+
          '<div><strong>1. Entendé el porqué</strong><span>La idea no es memorizar números: es entender qué función cumple cada parte de tu alimentación.</span></div>'+
          '<div><strong>2. Aplicalo a tu rutina</strong><span>Tu plan personal sigue siendo la referencia. Esta guía explica conceptos generales.</span></div>'+
          '<div><strong>3. Mirá tendencias</strong><span>Una comida o un día aislado no define tu progreso. Importa lo que sostenés en el tiempo.</span></div>'+
        '</div>'+
      '</div>'+
      '<div class="v134-learn-grid">'+TOPICS.map(topicCardV134).join('')+'</div>'+
      '<div class="v134-note"><strong>Importante:</strong> este contenido es educativo y general. Si tenés una condición médica, alergia, síntomas digestivos persistentes o una indicación clínica específica, seguí la recomendación de un profesional de salud.</div>';
  };

  const baseNutritionStudentV134=renderNutritionStudent;
  renderNutritionStudent=function(){
    if(nutritionStudentViewV70==='learn')return renderNutritionLearnV134();
    return baseNutritionStudentV134.apply(this,arguments);
  };

  window.__fjzNutritionLearnV134={version:'13.4',topics:TOPICS.length};
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

if "Aprender nutrición" not in html or "nutritionStudentViewV70==='learn'" not in html:
    raise RuntimeError("V13.4 nutrition education module missing")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V13.4 nutrition education:",len(html),"bytes","topics",10)
