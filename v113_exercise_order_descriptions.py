import pathlib, re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v113ExerciseOrderStyles">
.v113-move-preview{display:grid;gap:7px;margin:12px 0}
.v113-move-row{display:grid;grid-template-columns:34px 1fr;gap:9px;align-items:center;padding:9px 10px;border:1px solid var(--border);border-radius:10px;background:rgba(255,255,255,.02)}
.v113-move-row.active{border-color:rgba(255,31,47,.55);background:rgba(255,31,47,.07)}
.v113-move-n{font-weight:900;text-align:center;color:var(--muted)}
.v113-tech{margin-top:8px;padding:9px 10px;border-left:2px solid rgba(90,167,255,.6);background:rgba(90,167,255,.055);border-radius:0 10px 10px 0}
.v113-tech strong{display:block;font-size:11px;margin-bottom:3px;color:#dcecff}
.v113-tech div{font-size:11px;line-height:1.45;color:var(--muted)}
@media(max-width:520px){.v113-move-row{grid-template-columns:28px 1fr}}
</style>
"""

js=r"""
<script id="v113ExerciseOrderRuntime">
(function(){
  function normV113(v){
    return String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  }

  function techniqueV113(e){
    const name=normV113(e?.name), muscle=normV113(e?.muscle), equipment=normV113(e?.equipment);
    const current=String(e?.cue||'').trim();

    let prep='',exec='',avoid='';

    if(/sentadilla|squat|hack|prensa|pendulo|belt/.test(name)){
      prep='Pies firmes y abdomen activo antes de iniciar.';
      exec='Bajá con control, mantené rodillas alineadas con los pies y empujá sin perder el apoyo.';
      avoid='Evitá rebotes, despegar la pelvis o perder estabilidad.';
    }else if(/peso muerto|rumano|rdl|buenos dias|bisagra/.test(name)){
      prep='Fijá el tronco y llevá la cadera hacia atrás antes de bajar.';
      exec='Mantené la carga cerca del cuerpo y volvé extendiendo la cadera con control.';
      avoid='Evitá redondear la espalda o convertir el movimiento en una sentadilla.';
    }else if(/hip thrust|hip trust|puente/.test(name)){
      prep='Apoyá bien espalda y pies, con abdomen firme.';
      exec='Extendé la cadera hasta alinear tronco y muslos, apretando glúteos arriba.';
      avoid='Evitá terminar el movimiento arqueando la zona lumbar.';
    }else if(/curl femoral|femoral/.test(name)){
      prep='Ajustá la máquina para que la rodilla quede alineada y la cadera estable.';
      exec='Flexioná la rodilla con control y frená la vuelta.';
      avoid='Evitá levantar la cadera o soltar la carga en la excéntrica.';
    }else if(/extension.*cuad|cuadriceps/.test(name)){
      prep='Alineá la rodilla con el eje de la máquina y fijá la cadera.';
      exec='Extendé la rodilla de forma controlada y bajá sin dejar caer el peso.';
      avoid='Evitá despegar la cadera o usar impulso.';
    }else if(/bulgar|estocada|zancada|split/.test(name)){
      prep='Buscá una base estable y apoyá todo el pie delantero.';
      exec='Descendé verticalmente con control y empujá manteniendo rodilla y pie alineados.';
      avoid='Evitá perder equilibrio o impulsarte con la pierna trasera.';
    }else if(/press banca|press de pecho|press inclinado|press declinado|fondos/.test(name)){
      prep='Fijá escápulas y apoyos antes de empezar.';
      exec='Bajá con control y empujá manteniendo hombros estables y trayectoria repetible.';
      avoid='Evitá rebotar, despegar hombros o perder posición al final de la serie.';
    }else if(/apertura|peck deck|pec deck/.test(name)){
      prep='Pecho estable y codos levemente flexionados.';
      exec='Abrí hasta un rango cómodo y cerrá llevando los brazos hacia el centro sin acelerar.';
      avoid='Evitá adelantar hombros o convertirlo en un press.';
    }else if(/press militar|press de hombro/.test(name)){
      prep='Glúteos y abdomen firmes, hombros colocados antes de empujar.';
      exec='Empujá sobre la cabeza con recorrido controlado y bajá hasta un rango cómodo.';
      avoid='Evitá hiperextender la zona lumbar o usar impulso.';
    }else if(/elevacion lateral|laterales/.test(name)){
      prep='Torso firme y hombros lejos de las orejas.';
      exec='Elevá guiando con el codo y controlá especialmente la bajada.';
      avoid='Evitá balancearte o encoger los hombros.';
    }else if(/pajaro|posterior|reverse pec|peck deck inverso|face pull/.test(name)){
      prep='Torso estable y escápulas controladas.';
      exec='Abrí los brazos/codos sin perder la posición del hombro y frená la vuelta.';
      avoid='Evitá usar impulso o encoger los hombros.';
    }else if(/jalon|dominada|pull.?up/.test(name)){
      prep='Pecho estable y hombros colocados antes de tirar.';
      exec='Llevá los codos hacia abajo mientras mantenés el torso controlado.';
      avoid='Evitá balancearte o tirar solo con brazos.';
    }else if(/remo/.test(name)){
      prep='Fijá tronco y hombros antes de iniciar.';
      exec='Llevá el codo hacia atrás/cadera y controlá el regreso sin perder tensión.';
      avoid='Evitá balancear el torso o encoger los hombros.';
    }else if(/pullover/.test(name)){
      prep='Costillas controladas y brazos casi extendidos.';
      exec='Llevá los brazos hacia el cuerpo usando dorsales y frená la vuelta.';
      avoid='Evitá compensar con la zona lumbar o flexionar demasiado los codos.';
    }else if(/curl/.test(name)){
      prep='Hombros quietos y codos colocados antes de empezar.';
      exec='Flexioná el codo sin mover el hombro y controlá la bajada completa.';
      avoid='Evitá balancear el torso o adelantar los codos.';
    }else if(/triceps|extension.*polea|press frances|skull/.test(name)){
      prep='Fijá hombros y codos antes de iniciar.';
      exec='Extendé el codo manteniendo estable el brazo y controlá la vuelta.';
      avoid='Evitá abrir los codos o usar el torso para mover la carga.';
    }else if(/abduccion|patada.*glute|gluteo.*polea/.test(name)){
      prep='Pelvis y torso estables antes de mover la pierna.';
      exec='Mové desde la cadera con control y mantené tensión durante todo el recorrido.';
      avoid='Evitá girar el cuerpo o generar impulso.';
    }else if(/adduccion/.test(name)){
      prep='Sentate/parate estable y colocá la cadera en una posición cómoda.';
      exec='Llevá la pierna hacia la línea media y controlá la apertura.';
      avoid='Evitá rebotes o compensaciones del tronco.';
    }else if(/gemelo|pantorrilla|calf/.test(name)){
      prep='Apoyá bien el antepié y buscá un rango cómodo de tobillo.';
      exec='Subí el talón, pausá arriba y bajá de forma controlada.';
      avoid='Evitá rebotes o acortar el recorrido por apuro.';
    }else if(/crunch|abdominal|elevacion de piernas|elevacion de rodillas/.test(name)||/abdomen|core/.test(muscle)){
      prep='Estabilizá pelvis y caja torácica antes de empezar.';
      exec=current || 'Mové el tronco o la pelvis con control, manteniendo tensión abdominal.';
      avoid='Evitá balancearte, tirar del cuello o perder la posición lumbar.';
    }else if(/muneca|antebrazo|farmer|pinza|dead hang/.test(name)){
      prep='Fijá hombro/codo y asegurá un agarre estable.';
      exec=current || 'Realizá el recorrido o sostén con control y tensión continua.';
      avoid='Evitá impulso innecesario y soltá la carga de forma controlada.';
    }else{
      prep='Buscá una posición estable y cómoda antes de empezar.';
      exec=current || ('Realizá el movimiento con control y un recorrido repetible'+(equipment?' usando '+e.equipment:'')+'.');
      avoid='Evitá impulso y frená si perdés la técnica.';
    }

    if(current && !exec.includes(current) && current.length>12){
      exec=current+' '+exec;
    }
    return {prep,exec,avoid};
  }

  window.exerciseTechniqueV113=techniqueV113;

  window.openMoveExerciseV113=function(di,ei){
    const d=student().days[di], e=d?.exercises?.[ei];
    if(!d||!e)return;
    const rows=d.exercises.map((x,i)=>
      '<div class="v113-move-row '+(i===ei?'active':'')+'"><div class="v113-move-n">'+(i+1)+'</div><div><strong>'+esc(x.name)+'</strong>'+(i===ei?'<div class="muted micro">Posición actual</div>':'')+'</div></div>'
    ).join('');
    showModal(
      '<div class="modal-head"><div><h3>Mover ejercicio</h3><div class="muted tiny">'+esc(e.name)+'</div></div><button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<label class="tiny muted">Nueva posición<select id="v113MovePos" class="input">'+
      d.exercises.map((x,i)=>'<option value="'+i+'" '+(i===ei?'selected':'')+'>'+(i+1)+' · '+esc(x.name)+'</option>').join('')+
      '</select></label>'+
      '<div class="v113-move-preview">'+rows+'</div>'+
      '<button class="btn primary" style="width:100%" onclick="confirmMoveExerciseV113('+di+','+ei+')">Mover ejercicio</button>'
    );
  };

  window.confirmMoveExerciseV113=function(di,ei){
    const d=student().days[di], a=d?.exercises;
    if(!a||!a[ei])return;
    let target=Number(el('v113MovePos')?.value);
    if(!Number.isInteger(target)||target<0||target>=a.length)return;
    if(target===ei){closeModal();return}
    const [item]=a.splice(ei,1);
    a.splice(target,0,item);
    saveState();
    closeModal();
    render();
    toast('Ejercicio movido a la posición '+(target+1));
  };

  const baseDayV113=window.dayEditor;
  if(typeof baseDayV113==='function'){
    window.dayEditor=function(d,i){
      let out=baseDayV113.apply(this,arguments);
      (d.exercises||[]).forEach((e,j)=>{
        const edit='<button class="btn small" onclick="editExercise('+i+','+j+')">Editar</button>';
        const move='<button class="btn small" onclick="openMoveExerciseV113('+i+','+j+')">Mover</button>';
        if(out.includes(edit) && !out.includes('openMoveExerciseV113('+i+','+j+')')){
          out=out.replace(edit,move+edit);
        }
        const t=techniqueV113(e);
        const old='<p>'+esc(e.cue||'')+'</p>';
        const richer='<div class="v113-tech"><strong>Cómo hacerlo</strong><div>'+esc(t.prep)+' '+esc(t.exec)+' <span style="opacity:.9">Evitá: '+esc(t.avoid)+'</span></div></div>';
        if(e.cue&&out.includes(old))out=out.replace(old,richer);
      });
      return out;
    };
  }

  const baseWorkoutExerciseV113=window.workoutExercise;
  if(typeof baseWorkoutExerciseV113==='function'){
    window.workoutExercise=function(e,i){
      let out=baseWorkoutExerciseV113.apply(this,arguments);
      const t=techniqueV113(e);
      const cue='<p class="muted tiny">'+esc(e.cue||'')+'</p>';
      const richer='<div class="v113-tech"><strong>Técnica</strong><div>'+esc(t.prep)+' '+esc(t.exec)+' <span style="opacity:.9">Evitá: '+esc(t.avoid)+'</span></div></div>';
      if(e.cue&&out.includes(cue))out=out.replace(cue,richer);
      else{
        const marker='<div style="height:10px"></div>';
        if(out.includes(marker))out=out.replace(marker,richer+marker);
      }
      return out;
    };
  }

  const baseLibraryItemsV113=window.libraryItems;
  if(typeof baseLibraryItemsV113==='function'){
    window.libraryItems=function(dayIndex,arr){
      return arr.map(x=>{
        const t=techniqueV113(x);
        return '<div class="library-item"><h4>'+esc(x.name)+'</h4><p>'+esc(x.muscle)+' · '+esc(x.equipment)+'</p>'+
          '<div class="muted micro" style="line-height:1.4;margin:7px 0 9px">'+esc(t.exec)+'</div>'+
          '<button class="btn primary small" onclick="configureExercise('+dayIndex+',\''+x.id+'\')">Agregar</button></div>';
      }).join('')||'<div class="empty">No encontré ejercicios con esos filtros.</div>';
    };
  }
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)
p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8")
sw=re.sub(r"team-fjz-v\d+(?:-\d+)+","team-fjz-v11-3",sw)
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V11.3 exercise ordering/descriptions:",len(html),"bytes")
