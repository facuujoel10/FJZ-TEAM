import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v138NutritionHabitsGuideStyles">
#v66StudentHabits{display:none!important}
.v138-habits-hero{border:1px solid rgba(90,167,255,.22);background:linear-gradient(180deg,rgba(90,167,255,.055),rgba(255,255,255,.015))}
.v138-habit-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:12px}
.v138-habit-card{border:1px solid var(--border);border-radius:14px;padding:12px;background:var(--card);min-width:0}
.v138-habit-card strong{font-size:12px}
.v138-habit-card p{font-size:10px;line-height:1.55;color:var(--muted);margin:5px 0 0}
.v138-habit-tag{display:inline-flex;margin-bottom:7px;padding:3px 7px;border-radius:999px;border:1px solid rgba(90,167,255,.22);font-size:8px;color:var(--muted)}
.v138-general{margin-top:14px}
.v138-general-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;margin-top:10px}
.v138-tip{border:1px solid var(--border);border-radius:12px;padding:10px;background:rgba(255,255,255,.018)}
.v138-tip strong{display:block;font-size:11px}
.v138-tip span{display:block;margin-top:4px;font-size:10px;line-height:1.5;color:var(--muted)}
.v138-note{margin-top:12px;padding:10px 11px;border:1px dashed var(--border);border-radius:11px;font-size:10px;line-height:1.5;color:var(--muted)}
@media(max-width:760px){.v138-habit-grid,.v138-general-list{grid-template-columns:1fr}}
</style>
"""

js=r"""
<script id="v138NutritionHabitsGuideRuntime">
(function(){
  const GENERAL_V138=[
    ['Hidratación','Tomá agua de forma regular durante el día. La necesidad cambia con actividad, clima y sudoración.'],
    ['Proteína','Distribuí las fuentes de proteína a lo largo del día según tu plan, sin necesidad de concentrar todo en una sola comida.'],
    ['Frutas y verduras','Buscá variedad de colores y alimentos durante la semana para sumar fibra, vitaminas y minerales.'],
    ['Preparaciones','Priorizá la mayor parte del tiempo preparaciones simples como horno, plancha, vapor o hervido.'],
    ['Planificación','Si sabés que vas a tener un día complicado, dejar una comida o colación preparada puede facilitar mucho la adherencia.'],
    ['Sueño y rutina','Dormir y mantener horarios relativamente ordenados puede ayudar a la recuperación, el hambre y el rendimiento.'],
    ['Comer con calma','Comer más despacio puede ayudarte a registrar mejor hambre, saciedad y tolerancia digestiva.'],
    ['Flexibilidad','Una comida diferente no define tu progreso. Lo importante es la tendencia general y la constancia.'],
    ['Etiquetas','Usá la etiqueta para comparar productos similares; no hace falta juzgar un alimento por un solo número.'],
    ['Alcohol','No es necesario para una alimentación saludable ni para el rendimiento. Evitarlo o limitarlo según edad, contexto e indicación profesional.']
  ];

  function navV138(active){
    return '<div class="v70-recipe-tabs v136-nutrition-tabs" id="v138NutritionTabs">'+
      '<button class="btn '+(active==='plan'?'primary':'')+'" onclick="switchNutritionViewV70(\'plan\')">Mi plan</button>'+
      '<button class="btn '+(active==='recipes'?'primary':'')+'" onclick="switchNutritionViewV70(\'recipes\')">Recetas</button>'+
      '<button class="btn '+(active==='learn'?'primary':'')+'" onclick="switchNutritionViewV70(\'learn\')">Aprender</button>'+
      '<button class="btn '+(active==='habits'?'primary':'')+'" onclick="switchNutritionViewV70(\'habits\')">Hábitos</button>'+
    '</div>';
  }

  nutritionRecipesNavV70=navV138;

  function activeCoachHabitsV138(){
    try{
      const arr=activeNutritionHabitsV66?.()||[];
      return arr.filter(x=>x&&x.title&&x.text);
    }catch(e){return []}
  }

  function habitCardsV138(){
    const habits=activeCoachHabitsV138();
    if(!habits.length)return '<div class="empty">Tu coach todavía no cargó consejos específicos para esta etapa.</div>';
    return '<div class="v138-habit-grid">'+habits.map(h=>
      '<div class="v138-habit-card">'+
        '<span class="v138-habit-tag">'+(h.custom?'Personalizado':'Consejo del plan')+'</span>'+
        '<strong>'+esc(h.title)+'</strong>'+
        '<p>'+esc(h.text)+'</p>'+
      '</div>'
    ).join('')+'</div>';
  }

  function generalTipsV138(){
    return '<div class="card v138-general">'+
      '<div class="section-title"><div><h3>Guía general de hábitos</h3><div class="muted tiny">Ideas simples para acompañar el plan sin convertirlo en una lista rígida.</div></div><span class="badge blue">Guía</span></div>'+
      '<div class="v138-general-list">'+GENERAL_V138.map(x=>
        '<div class="v138-tip"><strong>'+esc(x[0])+'</strong><span>'+esc(x[1])+'</span></div>'
      ).join('')+'</div>'+
    '</div>';
  }

  function habitsBodyV138(includeNav){
    return (includeNav?navV138('habits'):'')+
      '<div class="card v138-habits-hero">'+
        '<div class="section-title"><div><h3>Hábitos y consejos</h3><div class="muted tiny">Recomendaciones para acompañar tu alimentación y hacerla más fácil de sostener.</div></div><span class="badge green">TEAM FJZ</span></div>'+
        '<div class="v138-note" style="margin-top:10px">No hace falta “cumplir perfecto”. Usá estos consejos como referencia práctica y priorizá lo que tu coach marcó para tu etapa.</div>'+
      '</div>'+
      '<div class="card" style="margin-top:12px">'+
        '<div class="section-title"><div><h3>Consejos de tu plan</h3><div class="muted tiny">Estos son los hábitos que tu coach dejó activos para vos.</div></div></div>'+
        habitCardsV138()+
      '</div>'+
      generalTipsV138()+
      '<div class="v138-note"><strong>Importante:</strong> esta sección es educativa. Si tenés una condición médica, alergia, síntomas persistentes o una indicación clínica específica, seguí la recomendación de un profesional de salud.</div>';
  }

  window.renderNutritionHabitsGuideV138=function(){
    const b=el('studentSubBody');if(!b)return;
    b.innerHTML=habitsBodyV138(true);
  };

  window.openCoachNutritionHabitsV138=function(){
    showModal(
      '<div class="modal-head"><div><h3>Hábitos y consejos del alumno</h3><div class="muted tiny">Vista del contenido que recibe el alumno.</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
      habitsBodyV138(false)
    );
  };

  const baseSwitchV138=switchNutritionViewV70;
  switchNutritionViewV70=function(view){
    nutritionStudentViewV70=view;
    if(view==='habits'){render();return}
    return baseSwitchV138.apply(this,arguments);
  };

  const baseNutritionStudentV138=renderNutritionStudent;
  renderNutritionStudent=function(){
    if(nutritionStudentViewV70==='habits')return renderNutritionHabitsGuideV138();
    return baseNutritionStudentV138.apply(this,arguments);
  };

  function ensureHabitsTabsV138(){
    if(currentProfile?.role==='student'&&studentTab==='nutrition'){
      const host=el('studentSubBody');
      if(!host)return;
      if(nutritionStudentViewV70==='habits'){
        if(!host.querySelector('.v138-habits-hero'))renderNutritionHabitsGuideV138();
        return;
      }
      const nav=host.querySelector('.v70-recipe-tabs');
      if(nav&&![...nav.querySelectorAll('button')].some(b=>(b.textContent||'').trim()==='Hábitos')){
        nav.outerHTML=navV138(nutritionStudentViewV70||'plan');
      }
    }
    if(currentProfile?.role==='coach'&&coachTab==='student'&&coachStudentTab==='nutrition'){
      const nav=el('coachStudentBody')?.querySelector('.v136-nutrition-tabs');
      if(nav&&![...nav.querySelectorAll('button')].some(b=>(b.textContent||'').trim()==='Hábitos')){
        nav.insertAdjacentHTML('beforeend','<button class="btn" onclick="openCoachNutritionHabitsV138()">Hábitos</button>');
      }
    }
  }

  const baseRenderV138=render;
  render=function(){
    const out=baseRenderV138.apply(this,arguments);
    fjzPostRenderV125('nutrition-habits-v138',ensureHabitsTabsV138);
    return out;
  };

  const baseStudentLoadedV138=renderNutritionStudentLoaded;
  renderNutritionStudentLoaded=function(){
    const out=baseStudentLoadedV138.apply(this,arguments);
    if(nutritionStudentViewV70==='habits')renderNutritionHabitsGuideV138();
    else ensureHabitsTabsV138();
    return out;
  };

  window.__fjzV138={version:'13.8',habitsGuide:true,textOnlyStudentHabits:true,nutritionSubtab:true};
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in ["Hábitos</button>","renderNutritionHabitsGuideV138","textOnlyStudentHabits:true","Consejos de tu plan","Guía general de hábitos"]:
    if marker not in html:
        raise RuntimeError("V13.8 missing habits marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V13.8 nutrition habits guide:",len(html),"bytes")
print("V13.8 runtime nav: Mi plan / Recetas / Aprender / Hábitos")
