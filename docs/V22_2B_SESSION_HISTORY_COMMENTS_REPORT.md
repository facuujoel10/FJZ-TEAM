# TEAM FJZ V22 — ETAPA 2B: SESSION HISTORY & EXACT COMMENTS REPORT

Fecha de cierre técnico: 2026-11-09 (America/Argentina/Buenos_Aires)  
Rama exclusiva: `dev/team-fjz-v22`

## 1. SHA inicial y SHA final técnico

- Base certificada 2A: `c6b6ba8d1aca3da4fc6fcc29f761a59d1e7f8900`
- SHA técnico certificado 2B: `e1b414a68dbd1e56eb8c6be6d996a9661351769f`
- Diferencia: 8 commits por delante de 2A, 0 por detrás.
- `main` se mantuvo intacto en `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`.

Este informe se incorpora después de la certificación técnica. El commit documental que lo contiene debe volver a superar Integración y Browser sobre el mismo SHA antes del cierre formal definitivo de 2B.

## 2. Funciones reales implementadas

2B profesionaliza el ciclo:

**Iniciar entrenamiento → registrar series → comentar → guardar/finalizar → consultar historial → revisar como Coach.**

Se implementó:

- identidad estable de instancia de entrenamiento desde el inicio;
- persistencia de esa identidad dentro del draft;
- reutilización de la misma identidad tras refresh;
- reutilización del mismo ID durante retry;
- reconciliación del mismo ID con `workout_sessions.source_session_id`;
- vínculo exacto nullable de comentarios nuevos mediante `exercise_feedback.session_id`;
- lectura de comentarios por sesión en `CommentRepository`;
- historial Premium Alumno/Coach;
- comentario debajo del ejercicio exacto;
- fecha, tipo, estado y modo de vínculo del comentario;
- comparación concreta entre sesión anterior y actual;
- compatibilidad explícita con históricos sin `session_id`.

No se creó un segundo sistema de entrenamientos ni una segunda bandeja de comentarios.

## 3. Cambios visuales verificables

### Historial Premium

La lista de historial ahora:

- destaca sesiones confirmadas;
- muestra nombre del día y fecha;
- mantiene series, dificultad y badges útiles;
- presenta CTA `Ver sesión` legible y táctil;
- utiliza jerarquía negra/roja/gris TEAM FJZ;
- mantiene tamaños cómodos en 360, 390 y 430 px.

### Detalle de sesión

El detalle de una sesión muestra:

- estado `Sesión confirmada`;
- cantidad de series;
- cantidad de ejercicios;
- indicadores de progresión/revisión;
- series reales con kg, reps y RIR;
- comparación `Sesión anterior → Esta sesión`;
- comentarios debajo del ejercicio correcto;
- tipo Comentario/Molestia;
- estado pendiente/revisado;
- timestamp;
- etiqueta `Vinculado a esta sesión` para vínculos exactos;
- etiqueta `Histórico compatible` cuando el registro legacy no tiene vínculo exacto.

No se presentan inferencias ambiguas como vínculos exactos.

## 4. Identidad de sesión adoptada

No se creó un segundo identificador.

La identidad canónica es el mismo `session.id` que V207/V205 ya utilizaban y que la proyección Supabase almacena como:

`workout_sessions.source_session_id`

2B adelanta la creación de esa misma identidad al inicio del entrenamiento.

### Ciclo

1. Al iniciar un entrenamiento se genera una identidad `ss_...`.
2. V145 la persiste dentro del draft.
3. Un refresh recupera el mismo `sessionId`.
4. Un comentario durante la sesión utiliza ese ID.
5. V106/V207 construyen la sesión final con exactamente el mismo ID.
6. El RPC confirmado proyecta ese ID como `source_session_id`.
7. Un retry reutiliza el mismo objeto pendiente y el mismo ID.
8. Una nueva instancia del mismo día obtiene un ID diferente.

V207 continúa siendo la autoridad de confirmación final. Un draft con ID no se considera sesión confirmada.

## 5. Estrategia de vínculo exacto Comentario ↔ Sesión

Se utiliza:

`exercise_feedback.session_id`

nullable.

Para comentarios nuevos durante una sesión activa:

`exercise_feedback.session_id === session.id === workout_sessions.source_session_id`

La relación exacta se interpreta junto con `student_id`.

### Comentario antes de finalizar

Está permitido. No existe FK inmediata hacia `workout_sessions`, porque la fila canónica todavía puede no existir.

El comentario queda vinculado al ID estable de la instancia. Al confirmar la sesión, la proyección se crea con ese mismo `source_session_id`.

### Comentario después de finalizar

También está permitido para la sesión autorizada y se mantiene el mismo vínculo exacto.

### Integridad

Dos triggers locales garantizan:

- el `session_id` de un comentario es inmutable;
- atleta y alumno deben coincidir;
- un ID de sesión no puede reconciliarse con otro alumno;
- una sesión confirmada no puede adoptar un ID que ya tenga feedback de otro alumno.

Las funciones de trigger usan `SECURITY DEFINER` exclusivamente para comprobar conflictos que RLS oculta entre usuarios, con `search_path` fijo `public,pg_temp`. La aplicación continúa operando bajo sus políticas RLS normales.

## 6. Cambios de esquema exclusivamente local

Archivo:

`supabase/migrations/20261110012000_v22_2b_session_comment_link.sql`

Cambios:

- columna nullable `exercise_feedback.session_id text`;
- índice parcial por `student_id + session_id + created_at`;
- check de forma del identificador;
- trigger de integridad de feedback;
- trigger de reconciliación con `workout_sessions`.

No se ejecutó esta migración en Supabase producción.

No se agregó una FK que bloquee comentarios pre-finalización.

## 7. Compatibilidad con históricos

Los registros antiguos continúan válidos con:

`session_id = NULL`

Resolución del historial:

1. buscar comentario exacto por `session_id + exercise_uid`;
2. si no existe exacto, usar snapshot ya guardado en la sesión;
3. sólo para históricos sin `session_id`, mantener el fallback temporal/día compatible;
4. un comentario ya vinculado a otra sesión nunca entra por el fallback temporal.

Los históricos ambiguos se identifican como `Histórico compatible`, no como certeza exacta.

## 8. Archivos modificados

Desde 2A hasta el SHA técnico 2B:

- `.github/workflows/v22-browser-baseline.yml`
- `.github/workflows/v22-local-integration.yml`
- `scripts/dev_session_comment_integrity_smoke.py`
- `scripts/v22_architecture_inventory.py`
- `src/data/comment-repository.js`
- `src/data/repository-contracts.js`
- `src/modules/workouts/session-history.js`
- `src/ui/premium-history.css`
- `supabase/migrations/20261110012000_v22_2b_session_comment_link.sql`
- `tests/e2e/v22-baseline.spec.js`
- `tests/unit/v22-comment-repository.test.js`
- `tests/unit/v22-contracts.test.js`
- `tests/unit/v22-session-history.test.js`
- `v344_v22_2a_premium_workout.py`

No se agregó un nuevo transform V345. Se extendió el único bridge V22 de entrenamientos ya existente.

## 9. Resultados RLS e integridad

Con cuentas completamente ficticias en Supabase local:

- comentario exacto pre-finalización: PASS;
- reconciliación con sesión canónica: PASS;
- Alumno A / Alumno B aislados: PASS;
- colisión de `source_session_id` entre alumnos: BLOQUEADA;
- mutación posterior de `session_id`: BLOQUEADA;
- revisión Coach: PASS;
- refresh/readback del estado revisado: PASS;
- histórico con `NULL session_id`: PASS;
- dos sesiones del mismo ejercicio el mismo día: SEPARADAS;
- comentario exacto post-finalización: PASS.

El contrato completo se ejecutó antes y después de reconstruir la base desde cero.

## 10. Idempotencia y recuperación

Se preservan los gates 2A y se agrega identidad exacta.

PASS:

- draft con ID estable;
- refresh y recuperación;
- misma identidad después de refresh;
- retry con mismo `sessionId`;
- fallo de red y reintento;
- doble finalización sin duplicado;
- cloud success sólo después de confirmación;
- sesión visible en historial;
- comentario exacto visible tras finalización;
- kg, reps y RIR preservados;
- sesiones del mismo día no se mezclan.

La lógica crítica V207/V340/V341 no fue sustituida.

## 11. Resultados Playwright

Browser técnico:

https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42739297715

SHA:

`e1b414a68dbd1e56eb8c6be6d996a9661351769f`

### Mobile 390 × 844

12/12 PASS:

1. navegación Alumno;
2. comentario/Coach histórico;
3. draft recovery 2A;
4. finish/history/idempotency 2A;
5. network retry 2A;
6. Premium responsive 2A;
7. **session/comment/history exacto 2B**;
8. **history responsive 2B**;
9. nutrición;
10. AgendaRepository;
11. Coach workspace;
12. Coach Agenda.

### Mobile 360 × 800

- Premium responsive 2A: PASS
- History responsive 2B: PASS

### Mobile 430 × 932

- Premium responsive 2A: PASS
- History responsive 2B: PASS

### Desktop 1440 × 900

12/12 PASS, incluyendo ambos recorridos 2B.

Gate final:

- `mobile=success`
- `desktop=success`
- `syntax=success`

## 12. Comparación de rendimiento y topología

La topología runtime permanece congelada:

- render assignments: **18**
- Realtime channels: **2**
- timeouts: **56**
- intervals: **0**
- listeners: **51**
- MutationObservers: **3**
- build patches: **229**

No se agregó:

- render wrapper global nuevo;
- listener;
- timer;
- observer;
- canal Realtime;
- nuevo transform Python de etapa.

La lógica fuente nueva vive en `src/modules/workouts/session-history.js` y `src/ui/premium-history.css`.

## 13. Capturas con fixtures ficticios

Artefacto CI:

`v22-2b-session-history-screens`

Artifact ID técnico: `13728601493`

Incluye:

- `2b/exact-history-mobile-390.png`
- `2b/exact-history-desktop-1440.png`
- `2b/history-responsive-mobile-360.png`
- `2b/history-responsive-mobile-390.png`
- `2b/history-responsive-mobile-430.png`
- `2b/history-responsive-desktop-1440.png`
- capturas 2A de regresión.

La revisión visual confirma legibilidad, ausencia de overflow horizontal y jerarquía clara en mobile/desktop.

## 14. GitHub Actions

Certificación técnica 2B:

- Integración: https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42739297785
- Browser: https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42739297715

Ambas finalizaron SUCCESS sobre exactamente:

`e1b414a68dbd1e56eb8c6be6d996a9661351769f`

Integración incluyó:

- unit/contract tests;
- negative isolation;
- Supabase local;
- AgendaRepository;
- CommentRepository;
- contrato 2B de sesión/comentario;
- build;
- inventario;
- preflight;
- reconstrucción completa;
- repetición de los contratos;
- aislamiento final;
- shutdown project-scoped.

## 15. Problemas encontrados y corregidos

### 15.1 Integridad cross-user invisible bajo RLS

El primer trigger corría con permisos del caller. RLS ocultaba filas del otro alumno y no podía detectar una colisión de ID.

Corrección:

- funciones de trigger `SECURITY DEFINER`;
- `search_path` fijo;
- alcance exclusivo de validación de integridad;
- RLS de aplicación intacta.

### 15.2 Delimitadores SQL durante edición

Una sustitución JavaScript interpretó `$$` como sintaxis especial de replacement y produjo `AS $`.

Corrección:

- edición literal sin replacement expansion;
- reconstrucción desde cero exitosa.

### 15.3 Test de inmutabilidad bajo RLS

El alumno no tiene UPDATE sobre feedback. PostgREST devolvía 0 filas afectadas en lugar de una excepción, por lo que no era una prueba válida del trigger.

Corrección:

- la inmutabilidad se prueba con Coach, que sí posee UPDATE autorizado;
- el trigger rechaza correctamente cambiar `session_id`.

### 15.4 Anchor de inicio de entrenamiento

El primer anchor asumía la forma histórica de V145, pero V340/V341 ya habían transformado ese recorrido.

Corrección:

- helper estable exportado desde V145;
- llamada desde la autoridad final de `startWorkout`.

### 15.5 Wrapper V207 preparado pero no aplicado

Durante auditoría se detectó que faltaba ejecutar el `body.replace` del wrapper de inicio.

Corrección:

- reemplazo obligatorio con guard de count;
- identidad creada desde el inicio, incluso antes de cargar una serie.

### 15.6 Payload V73 sin vínculo real

El guard de build detectó que el marcador `session_id` no estaba realmente en los payloads V73 cloud/local.

Corrección:

- inserción exacta en ambos payloads;
- anchor obligatorio;
- build posterior PASS.

### 15.7 Generación de migración por CLI

La generación automática mediante CLI no pudo autenticarse contra el repositorio privado en este entorno.

No se usó un workaround que tocara Supabase remoto. La migración se versionó manualmente siguiendo la convención del proyecto y fue aplicada, reconstruida y certificada exclusivamente contra Supabase local.

## 16. Riesgos pendientes de publicación

La migración existe únicamente en V22 local/repo. Antes de publicación requiere autorización separada.

Orden recomendado:

1. respaldo verificable de producción;
2. revisar/aplicar migración aditiva;
3. comprobar compatibilidad con V21.41;
4. verificar RLS y triggers en staging/controlado;
5. desplegar código compatible con `session_id NULL`;
6. activar gradualmente V22;
7. comprobar comentarios, sesiones e historial;
8. mantener plan de reversión de código y plan independiente para DB.

Un rollback de código **no** revierte automáticamente la migración de base.

Los históricos permanecen compatibles, por lo que no se requiere backfill masivo.

## 17. Producción intacta

Durante 2B:

- `main` permaneció en `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`;
- no se desplegó Render;
- no se modificó Supabase producción;
- no se ejecutó migración productiva;
- no se utilizaron alumnos reales;
- no se cambió Auth productivo;
- no se iniciaron servicios pagos;
- no se inició 2C.

**Estado técnico 2B: CERTIFICADO.**  
**Etapa siguiente: NO INICIADA.**  
**Producción: INTACTA.**
