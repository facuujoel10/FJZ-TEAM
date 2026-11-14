# TEAM FJZ V22 — 4A Nutrition Premium

## Estado de certificación

- Rama autorizada: `dev/team-fjz-v22`.
- SHA inicial certificado: `8664d12d78a1c26b35989e2e4afec2177e458ab7`.
- Producción protegida: `main` debe permanecer en `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`.
- SHA final: el commit que contiene este informe; el hash literal se entrega junto con los dos runs finales porque un commit no puede contener su propio SHA de forma autorreferencial.
- Integración final: workflow `V22 local Supabase integration`, run final entregado con la certificación.
- Browser final: workflow `V22 browser baseline`, run final entregado con la certificación.
- Alcance: exclusivamente Etapa 4A. No se inicia 4B.

## Diagnóstico de la experiencia anterior

La Nutrición anterior acumulaba varias capas históricas sobre una misma pantalla extensa. El plan, la calculadora, el registro, adherencia, recetas, hábitos, suplementos, plantillas e historial coexistían mediante wrappers e inyecciones sucesivas. El resultado conservaba funciones valiosas, pero visualmente seguía siendo una sucesión de cards y formularios con poca jerarquía entre prescripción, alternativa visible y consumo real.

La auditoría confirmó que módulos como `v229_nutrition_pro.py` y `v332_nutrition_mobile_macro_geometry.py` son principalmente de presentación/geometría; `v272_preparation_nutrition_calculator.py` y `v273_preparation_nutrition_hardening.py` endurecen la calculadora; y la persistencia real no debe inferirse de esos nombres históricos. La autoridad efectiva vive en el runtime consolidado y en las tablas ya existentes.

Un problema conceptual relevante era que ciertas capas mostraban consumo frente a objetivos mediante porcentajes/barras. En 4A esas visualizaciones no se usan para presentar el plan: objetivo prescrito, macros de una opción y consumo registrado son tres conceptos separados.

## Autoridades y arquitectura vigentes

### Plan prescrito

`nutrition_plans` sigue siendo la única fuente de verdad del plan. Su JSON `plan` mantiene `meals[] -> options[] -> items[]`, además de objetivos diarios, revisión, estado activo y `student_logging_enabled`. 4A no crea otra copia persistente del plan.

La edición Coach reutiliza el mismo objeto en memoria que ya utiliza el runtime histórico. Las mutaciones de comidas, opciones, alimentos, cantidades, suplementos, hábitos/guías, plantillas y herramientas existentes continúan delegándose a sus funciones consolidadas. El nuevo módulo sólo organiza la experiencia y mantiene estado efímero de navegación/selección.

### Macros y cantidades

Los macros de una alternativa se obtienen de la autoridad existente `nutritionOptionTotals`, que suma exclusivamente los items de esa alternativa. 4A nunca suma varias opciones de una misma comida como si debieran consumirse juntas.

Las cantidades respetan `measure_type`, `quantity`, `unit_name`, `grams_per_unit` y `grams` existentes. Una unidad no se transforma visualmente en “peso cocido” ni se inventa una convención no guardada. Los valores históricos almacenados de kcal, proteína, carbohidratos y grasas no se recalculan silenciosamente.

### Consumo real

`nutrition_logs` sigue siendo la única fuente de verdad del consumo. Los registros de calculadora y alimentos personalizados reutilizan las funciones existentes.

Para una opción completa, 4A usa columnas ya existentes y cubiertas por RLS:

- `meal_group_id`: agrupa los alimentos que pertenecen al mismo acto de registro.
- `note`: guarda el marcador `FJZ4A_OPTION:{mealId,optionId}`.

Así se puede identificar de forma inequívoca alumno, fecha, comida y opción sin migraciones. Los registros históricos que no tienen ese marcador se muestran como “Registro histórico · opción no identificada”; jamás se adivina una opción.

El insert requiere confirmación de Supabase y valida que todas las filas regresen con el mismo `meal_group_id` y la identidad esperada antes de mostrar éxito. Si el plan está inactivo o `student_logging_enabled=false`, el alumno no puede generar registros desde 4A.

### Recetas y recursos

`fitness_recipes` y sus políticas existentes siguen siendo la autoridad de recetas. La vista 4A enlaza con el flujo `Plan / Recetas` existente y no crea otra biblioteca.

Suplementos y hábitos/guías permanecen dentro del JSON del plan y reutilizan los editores históricos autorizados. 4A no reactiva el antiguo sistema de “adherencia de hábitos” eliminado por las capas de consolidación posteriores.

### Integración Athlete 360

4A se monta dentro de la sección Nutrición de Athlete 360. Mantiene la cabecera, identidad, navegación y regreso del workspace 3B/3C. Antes de mostrar un plan Coach se compara `plan.athlete_id` con el atleta activo; un mismatch muestra carga y fuerza una lectura del alumno correcto en vez de exponer temporalmente datos del alumno anterior.

## Transformación visual

### Alumno

La nueva composición abandona el formulario largo:

1. Encabezado compacto “Mi alimentación”.
2. Contexto del plan y revisión.
3. Objetivos diarios prescritos, explícitamente rotulados como referencia y no consumo.
4. Comidas con identidad visual propia.
5. Selector horizontal de alternativas por comida.
6. Una sola alternativa visible por vez, con macros e ingredientes.
7. Acción de registro separada de la simple selección visual.
8. Recursos (recetas, calculadora, suplementos y hábitos/guías existentes).
9. Consumo realmente registrado en un bloque separado.

No se usan barras de progreso para aparentar adherencia. “Sin registrar” nunca se convierte en “No cumplió”.

### Coach

Desktop usa un workspace específico:

- Rail lateral de comidas.
- Área principal de configuración y edición.
- Una comida seleccionada por vez.
- Opciones editables con macros visibles.
- Ingredientes y cantidades con los editores existentes.
- Estado explícito `Cambios pendientes / Guardando / Guardado / Error al guardar`.
- Acceso a Vista Alumno, calculadora, recetas, plantillas, suplementos y recursos existentes.

En mobile, el rail pasa a navegación horizontal táctil; el editor usa controles de al menos 44 px cuando corresponde y la acción de guardado se mantiene accesible sin tapar inputs.

## Guardado Coach y compatibilidad histórica

El guardado continúa delegándose a `saveNutritionPlan`, que actualiza `nutrition_plans` y solicita la fila confirmada al servidor. 4A agrega una verificación posterior: el mismo `id` debe volver con una revisión superior a la previa. Sólo entonces el estado pasa a `Guardado` y aparece la confirmación verde.

Si falla la red/escritura o no aumenta la revisión, se muestra `Error al guardar`; no existe un éxito visual falso.

Los planes históricos permanecen en el mismo JSON. Si un registro antiguo carece de identidad de opción, se conserva y se presenta de forma neutral sin modificarlo.

## Carga, errores y recuperación

4A también toma control de la entrada específica a Nutrición (no del `render` global). Alumno y Coach reciben estado de carga propio y un error recuperable con `Reintentar`. No se añaden listeners globales, timers, observers, canales Realtime ni wrappers del render principal.

## Auth / RLS

No se modifica ninguna política productiva. La suite usa exclusivamente Supabase local y fixtures ficticios.

Contratos reutilizados:

- `nutrition_plans`: lectura por acceso al atleta; escritura Coach.
- `nutrition_logs`: lectura por acceso; escritura del alumno sólo sobre su identidad y con un plan activo que habilite logging, o Coach autorizado.
- `fitness_recipes`: lectura de globales/recetas del Coach vinculado; escritura Coach.

No se agregan tablas, columnas, RPCs ni migraciones.

## QA 4A

La suite nueva cubre:

- Plan del alumno y estado sin plan.
- Múltiples alternativas y cambio visual sin escritura.
- Macros por opción y cantidades/unidades.
- Registro de opción con `meal_group_id` + identidad exacta.
- Registro deshabilitado sin consumo inventado.
- Recetas y calculadora existentes.
- Editor Coach.
- Guardado confirmado y error sin falso éxito.
- Refresh/rehidratación.
- Aislamiento Alumno A/B dentro de Athlete 360.
- Bloqueo del editor Coach para rol alumno.
- Ausencia de overflow en macros y documento.
- Mobile 360×800, 390×844, 430×932 y desktop 1440×900.
- Suite heredada 2A–3C-UX sin debilitar pruebas certificadas.

La integración añade además tests unitarios de reglas 4A: suma de una alternativa, marcador de identidad, agrupación de consumo y compatibilidad con registros históricos.

## Evidencia visual

El workflow genera `v22-4a-nutrition-premium-screens` con:

- V21.41 Alumno y Coach.
- V22 inmediatamente anterior a 4A.
- V22 4A Alumno y Coach.
- Comparación mobile 390 y desktop 1440.
- Evidencia 360 / 390 / 430 de comida, alternativas, calculadora, consumo, estado vacío y error recuperable.
- Capturas viewport y full-page.

Cada captura verifica antes de aceptarse:

- `innerWidth/innerHeight` contra el viewport Playwright.
- `devicePixelRatio` real.
- ancho/alto PNG a partir del header binario.
- ancho esperado `CSS × DPR`.
- ausencia de overflow horizontal.

## Topología y rendimiento

4A agrega un módulo JavaScript y una hoja CSS integrados al build V22. No añade:

- `render` global wrappers.
- `addEventListener` globales.
- timers.
- intervals.
- Mutation/Performance Observers.
- canales Realtime.

El inventario V22 conserva los límites de topología certificados y suma únicamente el marker/contrato de Nutrition Premium.

## Riesgos pendientes

- Los registros históricos anteriores a 4A no siempre permiten determinar qué alternativa fue elegida; se muestran sin inferencia.
- Las recetas y algunos recursos proceden de UI histórica reutilizada, aunque el acceso queda integrado visualmente desde 4A.
- La certificación técnica no implica aprobación estética; las capturas se entregan para revisión del Product Owner.

## Producción

4A no despliega Render, no ejecuta migraciones productivas, no toca Auth/RLS productivo y no usa alumnos reales. El workflow final vuelve a comprobar que `main` permanezca exactamente en `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`.
