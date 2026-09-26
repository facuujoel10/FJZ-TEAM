import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")
html=html.replace("TEAM FJZ V10.4","TEAM FJZ V10.5")

js=r"""
<script id="v105ArielRoutineImport">
(function(){
  const CLIENT='s_muh19cy1_0ez0t';
  const TAG='Ariel Semana 1 · planilla histórica';

  function e(uid,name,muscle,equipment,reps,cue,method='normal',methodNote=''){
    const exact=reps.slice();
    return {
      uid,libId:'custom',name,muscle,equipment,
      sets:exact.length,min:Math.min(...exact),max:Math.max(...exact),
      repMode:'exact',repsExact:exact,
      rirMin:1,rirMax:2,rest:120,increment:equipment.includes('Mancuernas')?2:2.5,
      cue,method,methodNote,history:[],override:null
    };
  }
  function d(id,name,muscles,exercises){
    return {id,name,muscles,warmup:[],stretching:[],
      cardio:{enabled:false,type:'',minutes:'',steps:'',intensity:'',timing:'Después del entrenamiento',notes:''},
      exercises};
  }
  function routine(){
    return [
      d('d_ariel_1','Día 1','Cuádriceps · Femorales · Aductores',[
        e('a11','Prensa inclinada','Cuádriceps','Prensa',[12,10,8,8],'Bajar controlado. No despegar la cadera del respaldo.'),
        e('a12','Sentadilla sumo con mancuerna','Glúteos / Aductores','Mancuernas',[12,12,12],'Bajar controlado y buscar profundidad.'),
        e('a13','Extensión en sillón de cuádriceps','Cuádriceps','Máquina',[12,10,8,8],'Control en la concéntrica 1,5 s y bajar controlado.','dropset','Última serie con dropset.'),
        e('a14','Sillón de femorales','Femorales','Máquina',[12,12,12],'Trabajo pesado. Controlar 2 s al contraer.'),
        e('a15','Aductores en máquina','Aductores','Máquina',[12,12,12],'Control tanto en la concéntrica como en la excéntrica.','dropset','Última serie con dropset.')
      ]),
      d('d_ariel_2','Día 2','Pecho · Hombros · Tríceps',[
        e('a21','Press inclinado en Smith','Pecho','Smith',[12,10,8,8],'Controlar el peso al bajar y apretar el pecho.'),
        e('a22','Press plano en Smith + aperturas con mancuernas','Pecho','Smith + Mancuernas',[12,10,10],'Press 12-10-10. Aperturas 3x10. Controlar el peso al bajar y apretar el pecho.','superserie','Biserie con aperturas con mancuernas 3x10.'),
        e('a23','Apertura en peck deck','Pecho','Peck deck',[12,12,12],'Intentar juntar bíceps al cerrar los brazos y apretar el pecho.'),
        e('a24','Press de hombros en máquina','Hombros','Máquina',[10,8,8],'Controlar el peso al bajar y no bajar más del hombro.'),
        e('a25','Vuelos laterales con mancuernas','Hombros','Mancuernas',[12,10,10],'Buscar alejar las mancuernas del cuerpo y controlar al bajar.'),
        e('a26','Trasnuca en polea agarre V','Tríceps','Polea',[10,10,10],'Codos cerrados y controlar el peso al bajar.'),
        e('a27','Extensión de tríceps en polea con agarre V','Tríceps','Polea',[10,10,10],'Trabajo pesado. Codos pegados al cuerpo; tirar hacia abajo y no hacia el cuerpo.')
      ]),
      d('d_ariel_3','Día 3','Femorales · Cuádriceps · Aductores',[
        e('a31','Peso muerto rumano con mancuernas','Femorales','Mancuernas',[12,10,8,8],'Controlar al bajar y estirar bien el femoral.'),
        e('a32','Sillón de femorales','Femorales','Máquina',[10,8,8],'Apretar bien el femoral y controlar la excéntrica.'),
        e('a33','Camilla de femorales','Femorales','Máquina',[12,10,8,8],'Controlar el peso al bajar y evitar levantar la cadera.','dropset','Última serie con dropset.'),
        e('a34','Extensión en sillón de cuádriceps','Cuádriceps','Máquina',[12,12,12],'Control en la concéntrica 1,5 s y bajar controlado.'),
        e('a35','Aductores en máquina','Aductores','Máquina',[12,12,12],'Control tanto en la concéntrica como en la excéntrica.')
      ]),
      d('d_ariel_4','Día 4','Espalda · Bíceps',[
        e('a41','Jalón al pecho agarre abierto (prono)','Espalda','Polea',[12,10,8,8],'Al bajar contraer dorsal y controlar la excéntrica en la subida.'),
        e('a42','Remo bajo en polea (neutro)','Espalda','Polea',[12,10,8,8],'Al contraer apretar dorsal y controlar la vuelta.'),
        e('a43','Remo con barra (prono)','Espalda','Barra',[10,10,10],'Codos abiertos; buscar apretar la espalda media.'),
        e('a44','Pull over en polea con soga + face pull con soga','Espalda / Hombro posterior','Polea',[12,12,12],'Pull over 3x12. Face pull 3x10. Pull over: 2 s en la concéntrica y controlar la excéntrica. Face pull: tirar hacia los ojos y controlar el peso.','superserie','Superserie con face pull 3x10.'),
        e('a45','Curl de bíceps en polea con barra','Bíceps','Polea',[12,10,10],'Sacar pecho, hombros hacia atrás, codos pegados al cuerpo y controlar la excéntrica.'),
        e('a46','Curl martillo con mancuernas','Bíceps','Mancuernas',[10,10,10],'Controlar el peso en la excéntrica al bajar.')
      ])
    ];
  }

  async function importAriel(){
    if(currentProfile?.role!=='coach')return false;
    const s=state.students.find(x=>x.id===CLIENT);
    if(!s||s.routineSource===TAG)return false;
    s.days=routine();
    s.plannedPerWeek=4;
    s.routineSource=TAG;
    saveState();
    try{
      await syncCloudNow();
      toast('Rutina histórica de Ariel cargada');
      return true;
    }catch(err){
      console.error('Ariel routine import',err);
      return false;
    }
  }

  const baseLoad=window.loadCoachCloud;
  if(typeof baseLoad==='function'){
    window.loadCoachCloud=async function(){
      const out=await baseLoad.apply(this,arguments);
      await importAriel();
      return out;
    };
  }
  setTimeout(importAriel,700);
})();
</script>
"""

html=html.replace("</body>",js+"\n</body>",1)
p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8").replace("team-fjz-v10-4","team-fjz-v10-5")
swp.write_text(sw,encoding="utf-8")
print("TEAM FJZ V10.5 Ariel routine import:",len(html),"bytes")
