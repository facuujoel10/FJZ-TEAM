# TEAM FJZ V22 — ETAPA 2B-V2: PRODUCT EXPERIENCE REDESIGN

Fecha: 2026-11-10  
Rama: `dev/team-fjz-v22`  
Base certificada: `6a7eb038d2920f384bb0fd73ccaaca3d9febd31c`

## 1. Diagnóstico del diseño anterior

2B-V y 2B-V.1 mejoraron legibilidad, geometría, feedback de guardado, comentarios e historial, pero conservaron demasiado de la composición histórica: hero grande, múltiples bloques de estado antes del primer ejercicio, tarjetas contenedoras anidadas, navegación visible durante la sesión y un dock de finalización que competía con la carga de series.

La consecuencia era una UI técnicamente moderna pero todavía reconocible como evolución de V21.41, no como una experiencia de entrenamiento mobile-first.

## 2. Nueva estructura

### Entrenamiento

- modo concentración durante una sesión activa;
- header compacto con nombre, progreso real, guardado y opciones;
- topbar/footer globales retirados del foco mobile durante la carga;
- primer ejercicio accesible de inmediato;
- ejercicios presentados como secciones de rendimiento, no como tarjetas de dashboard;
- prescripción, carga previa y series priorizadas;
- recomendación, última sesión y técnica movidas a disclosures contextuales;
- comentario como acción propia del ejercicio;
- finalización estática al final del recorrido, sin overlay permanente;
- mapa de ejercicios y panel de finalización en rail únicamente en desktop.

### Historial

- estructura de performance log;
- filas compactas con jerarquía fecha/sesión/señales;
- detalle en sheet de revisión;
- KPIs compactos;
- comparación anterior/actual priorizada;
- comentarios ligados al ejercicio visibles dentro del flujo;
- composición Coach ampliada en desktop con contexto de revisión.

### Comentarios

- bottom sheet mobile;
- única acción de cierre;
- selector comentario/molestia;
- textarea con foco estable;
- envío adherido al flujo del ejercicio;
- preservación de session_id, permisos, estados y compatibilidad histórica.

## 3. Componentes reutilizables

Se agregaron primitivas reutilizables en `src/ui/design-system.css`:

- `.fjz-appbar`
- `.fjz-surface`
- `.fjz-icon-button`
- `.fjz-disclosure`
- `.fjz-performance-section`

La intención es extender la misma gramática visual a Nutrición, Progreso, Check-ins, Agenda y Coach sin crear una segunda aplicación ni incorporar un framework completo.

## 4. Archivos modificados

- `src/modules/workouts/visual-redesign.js`
- `src/modules/workouts/premium-workout.js`
- `src/ui/design-system.css`
- `src/ui/premium-workout.css`
- `src/ui/premium-history.css`
- `tests/e2e/v22-baseline.spec.js`
- `.github/workflows/v22-browser-baseline.yml`

Archivos QA nuevos:

- `scripts/capture_product_experience_v2.js`
- `scripts/build_product_experience_contact_sheets.js`

## 5. Contratos preservados

No se modifica la autoridad de:

- V207 guardado confirmado;
- V340/V341 recovery;
- idempotencia;
- identidad exacta de sesión;
- `exercise_feedback.session_id`;
- Auth/RLS;
- repositorios V22;
- modelo de comentarios;
- sesiones históricas.

La recomposición visual reutiliza los mismos inputs, botones, handlers y nodos funcionales existentes.

## 6. QA de experiencia agregado

Playwright exige ahora:

- header de entrenamiento compacto;
- primer ejercicio visible en viewport inicial;
- primera serie editable sin pasos intermedios;
- navegación primaria duplicada ausente dentro del workout;
- bottom navigation fuera del modo concentración;
- finalización no fija;
- input activo sin superposición;
- comentario contextual con retorno inmediato al ejercicio;
- historial compacto;
- detalle exacto preservado;
- 360, 390, 430 y 1440 px;
- ausencia de overflow horizontal.

Los contratos certificados de 2B-V.1 siguen ejecutándose además de estos nuevos gates.

## 7. Comparación visual

La automatización genera exactamente los mismos estados para:

1. V21.41.
2. V22 2B-V.1.
3. V22 2B-V2.

Viewports:

- 360 × 800
- 390 × 844
- 430 × 932
- 1440 × 900

Estados:

- workout-initial;
- workout;
- series;
- history;
- session-detail;
- comments;
- comment-compose.

El estado `workout-initial` es captura sin scroll posterior al ingreso a Entrenar y es el principal criterio para evaluar tiempo hasta primera acción.

## 8. Producción y aislamiento

- `main` no se modifica.
- No se realiza deploy.
- No se ejecutan migraciones productivas.
- No se usa Supabase productivo.
- No se inicia 2C.
- Toda validación se realiza con Supabase local y usuarios `test.local`.

## 9. Limitaciones pendientes

- La modernización integral del Dashboard Coach queda fuera de esta etapa.
- Nutrición, Progreso, Check-ins, Agenda y Administración todavía conservan la dirección visual anterior.
- La aceptación estética de 2B-V2 no se considera automática por un resultado CI verde; queda reservada a revisión humana de capturas y recorrido.

## 10. Recomendación de extensión

Si la dirección V2 es aprobada visualmente, los próximos módulos deberían reutilizar el mismo patrón:

- appbar compacta;
- una sola autoridad de navegación;
- contenido primario antes que métricas;
- superficies planas y disclosures para contexto secundario;
- sheets mobile para acciones enfocadas;
- railes desktop sólo cuando agreguen contexto real;
- componentes táctiles de al menos 44–48 px;
- densidad y jerarquía ajustadas por viewport, no desktop reducido.
