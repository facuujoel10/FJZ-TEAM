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
    }

before=metrics(html)

required=[
    "__fjzStretchLibraryV144",
    "Estiramientos / Movilidad",
    "openLibrary=function(dayIndex)",
    "__v65LibraryRefresh"
]
missing=[x for x in required if x not in html]
if missing:
    raise RuntimeError("V20.51 missing library authority: "+repr(missing))

js=r"""
<script id="v251WarmupMobilityLibraryRuntime">
(function(){
  const warmups=[
    {id:'warm_arm_circles',name:'Círculos de brazos',muscle:'Calentamiento / Activación',equipment:'Peso corporal',cue:'Realizá círculos progresivos hacia adelante y atrás con control, sin forzar el hombro.'},
    {id:'warm_band_pull_apart',name:'Band pull-apart',muscle:'Calentamiento / Activación',equipment:'Banda elástica',cue:'Brazos extendidos, separá la banda llevando escápulas atrás y abajo. Tensión suave y controlada.'},
    {id:'warm_band_face_pull',name:'Face pull liviano con banda',muscle:'Calentamiento / Activación',equipment:'Banda elástica',cue:'Tirá hacia la cara con codos altos y carga muy liviana. Buscá control escapular.'},
    {id:'warm_band_external_rotation',name:'Rotación externa con banda',muscle:'Calentamiento / Activación',equipment:'Banda elástica',cue:'Codo pegado al cuerpo, rotá hacia afuera con tensión baja y recorrido cómodo.'},
    {id:'warm_wall_slide',name:'Wall slides',muscle:'Calentamiento / Activación',equipment:'Pared',cue:'Espalda contra la pared, deslizá brazos arriba manteniendo control escapular y sin dolor.'},
    {id:'warm_scap_pushup',name:'Flexiones escapulares',muscle:'Calentamiento / Activación',equipment:'Peso corporal',cue:'Con codos extendidos, acercá y separá las escápulas sin perder la posición del tronco.'},
    {id:'warm_scap_pullup',name:'Dominada escapular',muscle:'Calentamiento / Activación',equipment:'Barra',cue:'Desde colgado cómodo, deprimí y elevá escápulas sin flexionar los codos.'},
    {id:'warm_thoracic_rotation',name:'Rotación torácica dinámica',muscle:'Calentamiento / Activación',equipment:'Peso corporal',cue:'Desde cuadrupedia o zancada, rotá la parte alta de la espalda con movimiento lento y controlado.'},
    {id:'warm_cat_cow',name:'Cat-cow',muscle:'Calentamiento / Activación',equipment:'Peso corporal',cue:'Alterná flexión y extensión suave de columna acompañando con la respiración.'},
    {id:'warm_dead_bug',name:'Dead bug de activación',muscle:'Calentamiento / Activación',equipment:'Peso corporal',cue:'Mantené zona media estable mientras alternás brazos y piernas sin despegar la zona lumbar.'},
    {id:'warm_bird_dog',name:'Bird dog',muscle:'Calentamiento / Activación',equipment:'Peso corporal',cue:'Extendé brazo y pierna contraria sin rotar la pelvis. Volvé con control.'},
    {id:'warm_glute_bridge',name:'Puente de glúteos',muscle:'Calentamiento / Activación',equipment:'Peso corporal',cue:'Empujá el piso, extendé cadera y contraé glúteos sin hiperextender la espalda.'},
    {id:'warm_miniband_lateral',name:'Caminata lateral con minibanda',muscle:'Calentamiento / Activación',equipment:'Minibanda',cue:'Pasos cortos, rodillas alineadas y tensión constante en la banda.'},
    {id:'warm_monster_walk',name:'Monster walk con minibanda',muscle:'Calentamiento / Activación',equipment:'Minibanda',cue:'Avanzá con pasos cortos manteniendo rodillas y pies alineados.'},
    {id:'warm_bodyweight_squat',name:'Sentadilla con peso corporal',muscle:'Calentamiento / Activación',equipment:'Peso corporal',cue:'Usá un rango cómodo y progresivo, manteniendo apoyo completo del pie y control de rodillas.'},
    {id:'warm_reverse_lunge',name:'Zancada atrás dinámica',muscle:'Calentamiento / Activación',equipment:'Peso corporal',cue:'Paso atrás controlado, tronco estable y apoyo firme antes de volver.'},
    {id:'warm_lateral_lunge',name:'Zancada lateral dinámica',muscle:'Calentamiento / Activación',equipment:'Peso corporal',cue:'Desplazá la cadera hacia un lado con el pie apoyado y regresá de forma controlada.'},
    {id:'warm_hip_90_90',name:'Transiciones 90/90 de cadera',muscle:'Calentamiento / Activación',equipment:'Peso corporal',cue:'Rotá ambas caderas de lado a lado dentro de un rango cómodo, sin rebotes.'},
    {id:'warm_hip_airplane_assisted',name:'Hip airplane asistido',muscle:'Calentamiento / Activación',equipment:'Apoyo / Pared',cue:'Usá un apoyo estable y rotá la pelvis sobre una pierna sin perder equilibrio.'},
    {id:'warm_adductor_rockback',name:'Rock back de aductores',muscle:'Calentamiento / Activación',equipment:'Peso corporal',cue:'Una pierna extendida al costado; llevá la cadera atrás y volvé lentamente.'},
    {id:'warm_ankle_rocks',name:'Movilidad dinámica de tobillo',muscle:'Calentamiento / Activación',equipment:'Peso corporal',cue:'Llevá la rodilla hacia adelante manteniendo el talón apoyado y el pie estable.'},
    {id:'warm_calf_raises',name:'Elevaciones de gemelos de activación',muscle:'Calentamiento / Activación',equipment:'Peso corporal',cue:'Subí y bajá con control para activar tobillo y pantorrilla antes del trabajo principal.'},
    {id:'warm_pogo_low',name:'Pogos suaves',muscle:'Calentamiento / Activación',equipment:'Peso corporal',cue:'Rebotes cortos y suaves desde tobillo, solo si forman parte del plan y no generan molestias.'},
    {id:'warm_high_knee_march',name:'Marcha con rodillas altas',muscle:'Calentamiento / Activación',equipment:'Peso corporal',cue:'Elevá rodilla alternada manteniendo postura alta, abdomen activo y movimiento controlado.'},
    {id:'warm_empty_bar_squat',name:'Sentadilla con barra vacía',muscle:'Calentamiento / Activación',equipment:'Barra',cue:'Usá carga mínima para practicar el patrón y aumentar gradualmente la preparación específica.'},
    {id:'warm_empty_bar_press',name:'Press con barra vacía',muscle:'Calentamiento / Activación',equipment:'Barra',cue:'Series livianas para preparar el patrón antes de agregar carga. Técnica prioritaria.'},
    {id:'warm_ramp_set',name:'Serie de aproximación progresiva',muscle:'Calentamiento / Activación',equipment:'Según ejercicio',cue:'Realizá una o más series progresivas por debajo de la carga de trabajo, sin acercarte al fallo.'}
  ];

  const extraMobility=[
    {id:'stretch_wrist_flexor',name:'Estiramiento de flexores de muñeca',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Brazo extendido, acompañá suavemente la mano hacia atrás sin forzar muñeca ni dedos.'},
    {id:'stretch_wrist_extensor',name:'Estiramiento de extensores de muñeca',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Brazo extendido, llevá suavemente la mano hacia abajo manteniendo el codo cómodo.'},
    {id:'stretch_forearm_prayer',name:'Movilidad de muñecas en posición de oración',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Palmas juntas, bajá las manos suavemente hasta una tensión cómoda.'},
    {id:'stretch_deep_squat_hold',name:'Sentadilla profunda asistida',muscle:'Estiramientos / Movilidad',equipment:'Apoyo / Peso corporal',cue:'Usá apoyo si hace falta y mantené una posición cómoda para trabajar cadera y tobillo.'},
    {id:'stretch_world_greatest',name:'World’s greatest stretch',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Zancada amplia con rotación torácica suave. Movete lento y sin forzar el rango.'},
    {id:'stretch_open_book',name:'Open book torácico',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Acostado de lado con rodillas flexionadas, abrí el brazo superior y rotá suavemente el torso.'},
    {id:'stretch_doorway_pec',name:'Estiramiento de pectoral en marco de puerta',muscle:'Estiramientos / Movilidad',equipment:'Marco / Pared',cue:'Apoyá el antebrazo y avanzá suavemente hasta una tensión tolerable en el pecho.'},
    {id:'stretch_triceps_overhead',name:'Estiramiento de tríceps por encima de la cabeza',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Flexioná el codo detrás de la cabeza y acompañá suavemente sin tirar fuerte.'},
    {id:'stretch_lats_bar',name:'Estiramiento de dorsal sujetando barra',muscle:'Estiramientos / Movilidad',equipment:'Barra / Apoyo',cue:'Sujetá un apoyo firme y llevá la cadera atrás para alargar el dorsal sin colgarte de forma brusca.'},
    {id:'stretch_frog',name:'Movilidad de aductores tipo frog',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Abrí rodillas solo hasta un rango cómodo y desplazá la cadera atrás lentamente.'},
    {id:'stretch_hip_internal',name:'Movilidad de rotación interna de cadera',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Trabajá la rotación interna con rango controlado, sin empujar la articulación.'},
    {id:'stretch_hip_external',name:'Movilidad de rotación externa de cadera',muscle:'Estiramientos / Movilidad',equipment:'Peso corporal',cue:'Buscá un rango cómodo y estable, sin rebotes ni dolor.'}
  ];

  const all=[...warmups,...extraMobility];
  const existingIds=new Set(exerciseLibrary.map(x=>x.id));
  const existingNames=new Set(exerciseLibrary.map(x=>String(x.name||'').trim().toLowerCase()));
  all.forEach(x=>{
    const key=String(x.name||'').trim().toLowerCase();
    if(!existingIds.has(x.id)&&!existingNames.has(key)){
      exerciseLibrary.push(x);
      existingIds.add(x.id);
      existingNames.add(key);
    }
  });

  window.__fjzWarmupMobilityV251={
    version:'20.51',
    warmupCount:warmups.length,
    extraMobilityCount:extraMobility.length,
    warmupCategory:'Calentamiento / Activación',
    stretchCategory:'Estiramientos / Movilidad'
  };
})();
</script>
"""
html=html.replace("</body>",js+"\n</body>",1)

# Ensure the canonical V65 shortcut row exposes both populated categories.
shortcut_anchor="""      <button class="btn small" onclick="el('muscleFilter').value='Cuádriceps';window.__v65LibraryRefresh()">Cuádriceps</button>"""
if shortcut_anchor not in html:
    raise RuntimeError("V20.51 canonical library shortcut anchor missing")
addon="""
      <button class="btn small" onclick="el('muscleFilter').value='Calentamiento / Activación';window.__v65LibraryRefresh()">Calentamiento</button>
      <button class="btn small" onclick="el('muscleFilter').value='Estiramientos / Movilidad';window.__v65LibraryRefresh()">Estiramientos</button>"""
# Avoid duplicate stretching shortcut if V14.4 already inserted one.
if "value='Calentamiento / Activación'" not in html:
    html=html.replace(shortcut_anchor,shortcut_anchor+addon,1)
elif "value='Estiramientos / Movilidad'" not in html:
    html=html.replace(shortcut_anchor,shortcut_anchor+"\n"+addon.splitlines()[-1],1)

html=html.replace("</head>",'<meta name="fjz-warmup-mobility-library" content="20.51">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.51 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-warmup-mobility-library" content="20.51"',
    "__fjzWarmupMobilityV251",
    "warm_ramp_set","warm_band_pull_apart","warm_bodyweight_squat",
    "stretch_world_greatest","stretch_open_book",
    "Calentamiento / Activación","Estiramientos / Movilidad",
    ">Calentamiento</button>",">Estiramientos</button>"
]:
    if marker not in html:
        raise RuntimeError("V20.51 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.51 warm-up & mobility library")
print("V20.51 BEFORE:",before)
print("V20.51 AFTER:",after)
print("V20.51 added 27 warm-ups + 12 mobility/stretch exercises; canonical filters exposed")
