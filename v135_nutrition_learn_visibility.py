import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

js=r"""
<script id="v135NutritionLearnFixRuntime">
(function(){
  function navV135(active){
    return '<div class="v70-recipe-tabs" id="v135NutritionSubnav">'+
      '<button class="btn '+(active==='plan'?'primary':'')+'" onclick="switchNutritionViewV70(\'plan\')">Mi plan</button>'+
      '<button class="btn '+(active==='recipes'?'primary':'')+'" onclick="switchNutritionViewV70(\'recipes\')">Recetas</button>'+
      '<button class="btn '+(active==='learn'?'primary':'')+'" onclick="switchNutritionViewV70(\'learn\')">Aprender</button>'+
    '</div>';
  }

  // Override the actual lexical binding used by the app, not only window.*
  nutritionRecipesNavV70=navV135;

  const baseSwitchV135=switchNutritionViewV70;
  switchNutritionViewV70=function(view){
    nutritionStudentViewV70=view;
    if(view==='learn'){
      render();
      return;
    }
    return baseSwitchV135.apply(this,arguments);
  };

  // Re-wrap the real lexical render function after all previous nutrition layers.
  const baseRenderNutritionV135=renderNutritionStudent;
  renderNutritionStudent=function(){
    if(nutritionStudentViewV70==='learn'){
      return renderNutritionLearnV134();
    }
    return baseRenderNutritionV135.apply(this,arguments);
  };

  function ensureLearnNavV135(){
    if(currentProfile?.role!=='student'||studentTab!=='nutrition')return;
    const host=el('studentSubBody');
    if(!host)return;

    let nav=host.querySelector('.v70-recipe-tabs');
    if(!nav){
      host.insertAdjacentHTML('afterbegin',navV135(nutritionStudentViewV70||'plan'));
      nav=host.querySelector('.v70-recipe-tabs');
    }
    if(nav && ![...nav.querySelectorAll('button')].some(b=>/Aprender/i.test(b.textContent||''))){
      nav.outerHTML=navV135(nutritionStudentViewV70||'plan');
    }
  }

  const baseRenderV135=render;
  render=function(){
    const out=baseRenderV135.apply(this,arguments);
    fjzPostRenderV125('nutrition-learn-v135',ensureLearnNavV135);
    return out;
  };

  fjzPostRenderV125('nutrition-learn-v135-init',ensureLearnNavV135);

  window.__fjzNutritionLearnV135={version:'13.5',lexicalOverride:true};
})();
</script>
"""

html=html.replace("</body>",js+"\n</body>",1)

# Build-time proof that direct lexical overrides exist.
for marker in [
    "nutritionRecipesNavV70=navV135",
    "renderNutritionStudent=function()",
    "Aprender</button>",
    "renderNutritionLearnV134()"
]:
    if marker not in html:
        raise RuntimeError("V13.5 missing nutrition learn marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V13.5 nutrition learn visibility fix:",len(html),"bytes")
