# TEAM FJZ V22 — ETAPA 2A: PREMIUM WORKOUT EXPERIENCE REPORT

Fecha de cierre técnico: 2026-11-09 / 2026-11-10 UTC  
Rama exclusiva: `dev/team-fjz-v22`

## 1. SHA inicial y SHA final técnico

- Base certificada 1C: `94eec5a884b5bcfe7bb2a933fc1502be10a3c532`
- SHA técnico certificado de 2A: `dedf05fc96ab0a6f9993326e05f21733a5bff382`
- La rama quedó 11 commits por delante de 1C y 0 por detrás.
- `main` se mantuvo en `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`.

Al comenzar esta revisión se detectó que la rama ya había avanzado 10 commits respecto del SHA autorizado de 1C. Esos commits correspondían íntegramente a implementación 2A (módulo Premium Workout, UI, bridge de build, pruebas y documentación futura). Se auditaron antes de continuar. No se detectaron cambios productivos ni de otra etapa.

Este informe se añade después de certificar el SHA técnico. El commit documental que lo contiene debe volver a superar Integración y Browser antes del cierre formal definitivo.

## 2. Funciones implementadas

### 2A.1 — Experiencia visual de entrenamiento

Se incorporó una capa visual Premium sobre el entrenamiento actual, sin crear un segundo sistema:

- encabezado de entrenamiento activo;
- jerarquía Día → Ejercicio → Series → Registro → Comentario → Finalización;
- tarjetas de ejercicio diferenciadas;
- numeración visual de ejercicios;
- separación entre técnica, última sesión y recomendaciones;
- estado visible del progreso de series registradas;
- CTA de comentario dentro de cada ejercicio;
- CTA de finalización optimizado para mobile;
- estado visible de guardado/borrador;
- acceso al historial desde el modal de éxito confirmado.

Identidad preservada: negro, rojo y gris TEAM FJZ.

### 2A.2 — Registro profesional de series

Se incorporaron contratos explícitos para los campos:

- peso: teclado decimal, soporte `17.5` y `17,5`;
- RIR: decimal, paso 0.5;
- repeticiones: teclado numérico entero;
- touch targets de al menos 44/48 px en las pantallas Premium;
- etiquetas accesibles por ejercicio y serie;
- foco preservado durante escritura;
- sin render global nuevo al editar;
- carga anterior visualmente separada de la carga actual;
- recomendación/indicación del coach diferenciada;
- el peso anterior continúa siendo referencia y no se transforma automáticamente en registro confirmado.

No se reemplazó la lógica histórica de intensificaciones, peso corporal, sets incompletos ni progresión.

### 2A.3 — Comentarios contextuales

Se mantuvo `exercise_feedback` y el flujo actual.

Mejoras:

- botón Comentario destacado dentro del ejercicio;
- modal contextual sigue mostrando el ejercicio objetivo;
- borrador de comentario se conserva al cerrar y reabrir durante la sesión;
- enviar comentario tiene protección contra doble submit accidental;
- fallo de envío libera el bloqueo para reintento;
- éxito real limpia el borrador;
- confirmación visible después del guardado real;
- pesos/reps/RIR no se pierden al abrir o cerrar comentario;
- centro Coach, deeplinks, OK e históricos permanecen operativos.

No se agregó `session_id` ni se inventó asociación exacta de sesión.

Se agregó:

`docs/V22_COMMENT_SESSION_LINK_MIGRATION_PLAN.md`

con el diseño aditivo y retrocompatible propuesto para una subetapa posterior.

### 2A.4 — Guardado y finalización

La UI Premium interpreta únicamente señales reales del mecanismo existente.

Estados visibles:

- entrenamiento en curso;
- cambios pendientes;
- borrador protegido;
- guardando sesión;
- guardado confirmado;
- guardado pendiente/error recuperable.

El éxito final continúa dependiendo de la confirmación cloud de V207. No se sustituyó el mecanismo crítico por el save tracker nuevo.

Se verificó:

- recuperación tras refresh;
- borrador incompleto;
- finalización;
- readback;
- reintento;
- fallo de red;
- mismo `sessionId` durante retry;
- cero duplicado por segundo intento de finalización;
- historial posterior;
- lectura Coach y comentarios existentes.

## 3. Mejoras visuales verificables

Mobile:

- inputs grandes de 48 px;
- controles preparados para uso táctil;
- tarjetas de ejercicio compactas y legibles;
- carga anterior encima del registro actual;
- recomendación del sistema / indicación del Coach en bloques distintos;
- finalización disponible sin buscar el botón al final de una sesión larga;
- foco rojo de alto contraste;
- textarea de comentario de 16 px para evitar zoom incómodo;
- cero overflow horizontal certificado.

Desktop:

- ancho útil ampliado y centrado;
- tarjetas con separación visual clara;
- columnas peso/reps/RIR alineadas;
- referencias y recomendaciones con mayor jerarquía;
- botón de finalización visible y consistente.

Capturas generadas por CI en el artefacto:

`v22-2a-premium-workout-screens`

Incluye:

- `premium-draft-mobile-390.png`
- `premium-complete-mobile-390.png`
- `responsive-mobile-360.png`
- `responsive-mobile-390.png`
- `responsive-mobile-430.png`
- equivalentes desktop 1440.

Artefacto técnico certificado: ID `13726006123`.

## 4. Archivos realmente modificados

Desde 1C hasta el SHA técnico 2A:

- `.github/workflows/v22-browser-baseline.yml`
- `.github/workflows/v22-local-integration.yml`
- `build.py`
- `docs/V22_COMMENT_SESSION_LINK_MIGRATION_PLAN.md`
- `playwright.config.js`
- `scripts/v22_architecture_inventory.py`
- `src/modules/workouts/premium-workout.js`
- `src/ui/premium-workout.css`
- `tests/e2e/v22-baseline.spec.js`
- `tests/unit/v22-premium-workout.test.js`
- `v344_v22_2a_premium_workout.py`

No se modificó `main`, Supabase producción ni Render.

## 5. Comparación antes / después

### Antes 1C

La pantalla de entrenamiento utilizaba principalmente la presentación histórica: inputs y referencias existentes, pero sin una jerarquía Premium unificada ni estados de guardado explícitos integrados visualmente.

### Después 2A

El mismo flujo histórico queda presentado mediante una capa modular:

- tarjetas Premium;
- input contract por campo;
- referencias anteriores diferenciadas;
- feedback contextual;
- estado de borrador/guardado;
- progreso de series;
- finalización mobile-first;
- acceso directo al historial después de confirmación.

La autoridad de datos y guardado sigue siendo la existente.

## 6. Resultados mobile y desktop

Run Browser técnico certificado:

https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42732630697

SHA:

`dedf05fc96ab0a6f9993326e05f21733a5bff382`

### 390 × 844

10/10 PASS:

1. navegación Alumno;
2. entrenamiento + comentario + Coach;
3. Premium draft/recovery;
4. Premium finish/history/idempotency;
5. Premium network failure/retry;
6. Premium responsive;
7. nutrición;
8. AgendaRepository;
9. Coach workspace;
10. Coach Agenda.

### 360 × 800

Premium responsive: PASS.

### 430 × 932

Premium responsive: PASS.

### 1440 × 900

10/10 PASS con los mismos recorridos principales.

Resultados finales:

- `mobile=success`
- `desktop=success`
- `syntax=success`

## 7. Pruebas de guardado, recuperación y duplicados

PASS:

- peso decimal `17.5`;
- reps;
- RIR decimal `1.5`;
- foco conservado después de input;
- carga anterior visible;
- recomendación visible;
- draft local visible;
- refresh y recuperación del draft;
- finalización con confirmación cloud;
- `__fjzSessionSaveStateV207().state === 'success'`;
- `cloudConfirmed === true`;
- incremento de una sola sesión;
- segundo intento de `finishWorkout()` no agrega otra sesión;
- error de red produce estado `failed`;
- sesión pendiente conserva el mismo ID;
- reintento finaliza con éxito;
- cantidad de sesiones no aumenta durante el retry.

## 8. Pruebas de comentarios

PASS:

- comentario abre desde ejercicio;
- modal conserva contexto;
- borrador sobrevive cierre/reapertura;
- envío real confirma guardado;
- no pierde el registro `17.5`;
- protección contra submit duplicado en unit test;
- fallo permite reintento;
- flujo Coach histórico sigue mostrando comentario;
- OK continúa persistiendo;
- comentario revisado continúa fuera del panel después de refresh.

## 9. Rendimiento y topología

Inventario final:

- render assignments: **18**
- Realtime channels: **2**
- timeouts: **56**
- intervals: **0**
- listeners: **51**
- MutationObservers: **3**

No hubo crecimiento de topología runtime respecto de 1C.

Integración 2A utiliza un único bridge adicional:

`v344_v22_2a_premium_workout.py`

El módulo funcional reside en:

`src/modules/workouts/premium-workout.js`

y los estilos fuente en:

`src/ui/premium-workout.css`.

No se agregaron nuevos timers, listeners, observers o canales para la experiencia Premium.

## 10. Compatibilidad histórica

Se preservaron:

- IDs existentes;
- snapshots;
- sesiones;
- formatos de rutina;
- V207;
- V340;
- V341;
- V73;
- V287;
- V325;
- V328;
- V329;
- V336;
- `exercise_feedback`;
- comentarios históricos sin `session_id`;
- sesiones incompletas;
- historial Coach/Alumno;
- lógica existente de recomendación y carga anterior.

2A no introduce una inferencia retroactiva de sesión para comentarios.

## 11. GitHub Actions

### Certificación técnica 2A

Integración:

https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42732630731

Browser:

https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42732630697

Ambas terminaron SUCCESS sobre:

`dedf05fc96ab0a6f9993326e05f21733a5bff382`

Integración incluye:

- Auth/RLS;
- AgendaRepository;
- CommentRepository;
- unit/contract tests;
- build;
- preflight;
- inventario 2A;
- reconstrucción completa de DB;
- segundo smoke;
- aislamiento;
- shutdown project-scoped.

## 12. Problemas encontrados y corregidos

### Rama avanzada al iniciar

La rama ya estaba 10 commits por delante del SHA 1C. Se comprobó que todos correspondían a 2A y que `main` seguía intacto antes de continuar.

### Browser intermedio rojo

Run intermedio:

https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42720187040

El guardado, idempotencia y estado cloud habían pasado, pero el test intentaba clicar un botón “Ver historial” situado detrás del modal de éxito. El overlay interceptaba el puntero.

Corrección:

- se mantuvo el modal;
- se mantuvo el CTA nuevo de 2A dentro del modal;
- el E2E pasó a validar específicamente `#modal .v22-history-after-save`;
- se comprueba cierre del modal y llegada real al historial.

No se usó force-click ni se debilitó la aserción.

### Fallo de red intencional

El test de resiliencia genera un `net::ERR_FAILED` deliberado al abortar el RPC de commit. La prueba exige estado failed, conservación del ID, retry y ausencia de duplicado. Luego termina PASS.

## 13. Funciones diferidas a 2B o subetapa posterior

Deliberadamente fuera de 2A:

- asociación exacta comentario ↔ sesión mediante `session_id`;
- progresión inteligente avanzada;
- PRs/récords y comparativas Premium avanzadas;
- rediseño completo del Coach;
- constructor avanzado de rutinas;
- refactor masivo del runtime histórico;
- cambios estructurales de nutrición.

El plan de vínculo de comentarios queda preparado de forma aditiva y retrocompatible.

## 14. Producción intacta

Durante toda 2A:

- rama exclusiva `dev/team-fjz-v22`;
- `main` permanece en `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`;
- fixtures únicamente ficticios;
- bloqueos de producción activos;
- cero deploy Render;
- cero migraciones Supabase producción;
- cero modificación Auth productiva;
- cero datos reales;
- cero servicios pagos.

**Estado técnico 2A: CERTIFICADO.**  
**2B: NO INICIADA.**  
**Producción: INTACTA.**
