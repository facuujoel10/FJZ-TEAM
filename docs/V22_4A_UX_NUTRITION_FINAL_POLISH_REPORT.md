# TEAM FJZ V22 — 4A-UX Nutrition Final Polish

## Certificación
- Rama: `dev/team-fjz-v22`
- SHA inicial obligatorio: `812423a2a7eace1b9c817137f17bf9ca7c167204`
- SHA final: se entrega con la certificación del commit final.
- Producción protegida: `main` debe continuar en `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`.
- Alcance: exclusivamente 4A-UX. No se inicia 4B.

## Diagnóstico visual
La evidencia certificada de 4A mostró dos problemas de jerarquía. En Alumno mobile, la cabecera legacy, la navegación superior, la cabecera propia de Nutrición y los objetivos consumían casi todo 390×844 antes de que apareciera la primera comida. En Coach, el header Athlete 360, dos bloques de contexto y la cabecera de Nutrición repetían identidad/plan, dejando el editor principal por debajo del primer viewport.

## Cambios 4A-UX
- La pantalla Alumno conserva back/avisos, pero la cabecera premium pasa a ser la autoridad visual del título.
- En mobile se elimina la navegación superior duplicada y se conserva la barra inferior existente.
- Objetivos diarios pasan a una geometría compacta de cuatro columnas, sin ocultar valores ni cambiar cálculos.
- Las indicaciones del Coach se compactan sin eliminarse.
- La sección de comidas comienza inmediatamente después del resumen prescrito.
- Tabs de alternativas y acción de registro mantienen objetivos táctiles.
- En Coach Nutrición se ocultan únicamente contexto repetido de Athlete 360 y el bloque de contexto nutricional duplicado; navegación e identidad permanecen.
- La cabecera Coach de 4A deja de repetir el nombre del alumno y se convierte en toolbar del plan + guardado.
- La comida seleccionada precede a la configuración general en el DOM.
- Desktop usa comida seleccionada como superficie principal y Prescripción como inspector lateral.
- Mobile muestra navegación por comidas y editor antes de la prescripción general.
- El guardado mobile deja de ser sticky para no superponerse a inputs.

## Preservación funcional
No se cambian `nutrition_plans`, `nutrition_logs`, `fitness_recipes`, `nutritionOptionTotals`, `saveNutritionPlan`, `meal_group_id`, identidad de opciones, calculadora, recetas, hábitos, suplementos, Athlete 360, CommentRepository, AgendaRepository, sesiones, Auth/RLS ni migraciones.

La capa 4A-UX no agrega listeners globales, timers, observers ni canales Realtime. `v349_v22_4a_ux_nutrition_final_polish.py` verifica que la topología runtime sea idéntica antes y después de inyectar CSS.

## QA
Se mantiene toda la suite 4A y se agregan contratos 4A-UX para:
- primera comida dentro del primer viewport mobile;
- jerarquía de cabecera y objetivos;
- macros sin overflow;
- alternativa visual sin escritura;
- controles táctiles;
- editor Coach desktop y mobile;
- ausencia de cabeceras/contextos duplicados;
- guardado confirmado, error recuperable y refresh;
- aislamiento A/B;
- ausencia de scroll horizontal.

Viewports obligatorios: 360×800, 390×844, 430×932 y 1440×900. Supabase local y fixtures ficticios exclusivamente.

## Evidencia visual
El workflow crea `v22-4a-ux-nutrition-final-polish-screens` comparando el SHA certificado 4A con 4A-UX. Incluye Alumno inicio/primera comida/alternativas/macros/consumo, Coach desktop/mobile, guardado exitoso, error y estado sin plan; viewport y full-page con verificación CSS/DPR/PNG y overflow.

Además, el script registra posiciones reales de primera comida y editor Coach y falla si 4A-UX no mejora perceptiblemente respecto de 4A.

## Riesgos pendientes
- La aprobación técnica no implica aprobación estética.
- Las recetas y herramientas históricas conservan su UI interna; 4A-UX optimiza su acceso y contexto, no las rediseña funcionalmente.
- La barra inferior del Alumno continúa siendo la navegación mobile canónica y se respeta su safe area.

## GitHub Actions
Los enlaces de los runs finales SUCCESS se incorporan/entregan con la certificación final del mismo SHA.

## Producción
Sin Render, sin Supabase productivo, sin Auth/RLS productivo, sin alumnos reales, sin servicios pagos y sin 4B.
