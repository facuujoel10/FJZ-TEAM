import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

js=r"""
<script id="v144StretchingLibraryRuntime">
(function(){
  const stretches=[
    {id:'stretch_band_pec',name:'Estiramiento de pectoral con banda',muscle:'Estiramientos / Movilidad',equipment:'Banda elástica',cue:'Anclá la banda detrás, abrí el pecho y mantené 20–30 s sin rebotes.'},
    {id:'stretch_band_lat',name:'Estiramiento de dorsal con banda',muscle:'Estiramientos / Movilidad',equipment:'Banda elástica',cue:'Sujetá la banda por encima de la cabeza, llevá la cadera atrás y mantené 20–30 s por lado.'},
    {id:'stretch_band_triceps',name:'Estiramiento de tríceps con banda',muscle:'Estiramientos / Movilidad',equipment:'Banda elástica',cue:'Llevá el brazo por encima de la cabeza y usá la banda como asistencia suave. Mantené 20–30 s.'},
    {id:'stretch_band_shoulder',name:'Pasadas de hombro con banda',muscle:'Estiramientos / Movilidad',equipment:'Banda elástica',cue:'Usá un agarre amplio y pasá la banda por encima de la cabeza sin forzar el hombro.'},
    {id:'stretch_band_external',name:'Rotación externa suave con banda',muscle:'Estiramientos / Movilidad',equipment:'Banda elástica',cue:'Codo pegado al cuerpo y tensión suave. Mové dentro de un rango cómodo y controlado.'},
    {id:'stretch_band_hamstring',name:'Estiramiento de isquios con banda',muscle:'Estiramientos / Movilidad',equipment:'Banda elástica',cue:'Acostado, elevá una pierna asistida por la banda y mantené la rodilla cómoda. 20–30 s por lado.'},
    {id:'stretch_band_glute',name:'Estiramiento de glúteo con banda',muscle:'Estiramientos / Movilidad',equipment:'Banda elástica',cue:'Usá la banda para acercar suavemente la pierna sin despegar la pelvis. 20–30 s por lado.'},
    {id:'stretch_band_calf',name:'Estiramiento de gemelo con banda',muscle:'Estiramientos / Movilidad',equipment:'Banda elástica',cue:'Pierna extendida y banda en el antepié. Acercá suavemente los dedos hacia vos durante 20–30 s.'},

    {id:'stretch_pec_wall',name:'Estiramiento de pectoral en pared',muscle:'Estiramientos / Movilidad',equipment:'Pared',cue:'Apoyá antebrazo o mano y rotá el torso suavemente hasta sentir tensión cómoda. 20–30 s por lado.'},
    {id:'stretch_lat_bench',name:'Estiramiento de dorsal en banco',muscle:'Estiramientos / Movilidad',equipment:'Banco',cue:'Apoyá manos o codos en el banco, llevá la cadera atrás y bajá el pecho sin forzar la espalda.'},
    {id:'stretch_child_pose_lat',name:'Postura del niño con alcance lateral',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Sentate hacia talones, extendé brazos y desplazá las manos hacia un lado para enfatizar dorsal. 20–30 s.'},
    {id:'stretch_upper_trap',name:'Estiramiento de trapecio superior',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Incliná la cabeza suavemente hacia un lado sin tirar fuerte. Mantené 20–30 s.'},
    {id:'stretch_neck_rotation',name:'Movilidad cervical suave',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Realizá inclinaciones y rotaciones cortas, lentas y sin dolor. Evitá movimientos bruscos.'},

    {id:'stretch_hip_flexor',name:'Estiramiento de flexores de cadera',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'En media rodilla, contraé glúteo de la pierna atrasada y llevá la pelvis suavemente hacia adelante. 20–30 s.'},
    {id:'stretch_couch',name:'Couch stretch',muscle:'Estiramientos / Movilidad',equipment:'Banco / Pared',cue:'Rodilla cerca del apoyo y torso erguido. Ajustá la distancia para mantener una tensión tolerable.'},
    {id:'stretch_quad_standing',name:'Estiramiento de cuádriceps de pie',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Tomá el tobillo, mantené rodillas cerca y pelvis estable. 20–30 s por lado.'},
    {id:'stretch_hamstring_seated',name:'Estiramiento de isquios sentado',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Extendé una pierna y acercá el torso desde la cadera sin redondear de más. 20–30 s por lado.'},
    {id:'stretch_adductor_rockback',name:'Movilidad de aductores en rock back',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Una pierna extendida al costado, llevá la cadera atrás lentamente y volvé. Movimiento controlado.'},
    {id:'stretch_butterfly',name:'Estiramiento mariposa de aductores',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Juntá las plantas de los pies y dejá caer las rodillas suavemente. No rebotes.'},
    {id:'stretch_90_90',name:'Movilidad de cadera 90/90',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Colocá ambas piernas en 90° y rotá de un lado al otro con control, sin forzar el rango.'},
    {id:'stretch_figure4',name:'Estiramiento de glúteo en figura 4',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Cruzá un tobillo sobre la rodilla contraria y acercá la pierna hacia el torso. 20–30 s por lado.'},
    {id:'stretch_pigeon',name:'Estiramiento de glúteo tipo pigeon',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Adoptá una posición cómoda de cadera y avanzá el torso solo hasta una tensión tolerable.'},
    {id:'stretch_ankle_wall',name:'Movilidad de tobillo rodilla a pared',muscle:'Estiramientos / Movilidad',equipment:'Pared',cue:'Talón apoyado, llevá la rodilla hacia la pared siguiendo la línea del pie sin levantar el talón.'},
    {id:'stretch_calf_wall',name:'Estiramiento de gemelo en pared',muscle:'Estiramientos / Movilidad',equipment:'Pared',cue:'Pierna atrás extendida, talón apoyado y cuerpo inclinado hacia la pared. 20–30 s por lado.'},
    {id:'stretch_soleus_wall',name:'Estiramiento de sóleo en pared',muscle:'Estiramientos / Movilidad',equipment:'Pared',cue:'Mantené el talón apoyado y flexioná la rodilla de la pierna atrasada para enfatizar sóleo.'},
    {id:'stretch_thoracic_rotation',name:'Rotación torácica en cuadrupedia',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Desde cuadrupedia, rotá el torso llevando un brazo hacia arriba sin mover demasiado la pelvis.'},
    {id:'stretch_thread_needle',name:'Thread the needle',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Desde cuadrupedia, pasá un brazo por debajo del otro y rotá suavemente la parte alta de la espalda.'}
  ];

  const existing=new Set(exerciseLibrary.map(x=>x.id));
  stretches.forEach(x=>{if(!existing.has(x.id))exerciseLibrary.push(x)});

  window.__fjzStretchLibraryV144={
    version:'14.4',
    count:stretches.length,
    bandCount:stretches.filter(x=>x.equipment==='Banda elástica').length
  };
})();
</script>
"""

html=html.replace("</body>",js+"\n</body>",1)

# Add a quick filter button beside the existing library shortcuts when present.
old="""<button class=\"btn small\" onclick=\"el('muscleFilter').value='Cuádriceps';window.__v65LibraryRefresh()\">Cuádriceps</button>"""
new=old+"""\n      <button class=\"btn small\" onclick=\"el('muscleFilter').value='Estiramientos / Movilidad';window.__v65LibraryRefresh()\">Estiramientos</button>"""
if old in html:
    html=html.replace(old,new,1)

for marker in [
    "stretch_band_pec",
    "stretch_hip_flexor",
    "stretch_ankle_wall",
    "Estiramientos / Movilidad",
    "__fjzStretchLibraryV144"
]:
    if marker not in html:
        raise RuntimeError("V14.4 missing stretching library marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V14.4 stretching library: 27 exercises, 8 with elastic band")
