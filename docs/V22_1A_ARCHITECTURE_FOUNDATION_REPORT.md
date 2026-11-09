# TEAM FJZ V22 — Etapa 1A · Architecture Foundation Report

Fecha: 2026-11-09  
Rama: `dev/team-fjz-v22`  
Producción: `main`  
Baseline productivo protegido: `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`  
Commit de implementación 1A certificado antes de este informe: `b42e31e13d4788c470ce592646505350ae98bf77`

## 1. Certificación final de 0C

La Etapa 1A sólo comenzó después de certificar formalmente 0C en el commit documental:

`8ef81a48b9454c1e9e310c5c096962fd5901ca93`

Ejecuciones de ese mismo SHA:

- V22 local Supabase integration — run **42560798414** — **SUCCESS**.
- V22 browser baseline — run **42560798457** — **SUCCESS**.
- Mobile 390×844 — PASS.
- Desktop 1440×900 — PASS.
- JavaScript syntax audit — PASS.
- Explicit project preflight — PASS.
- aislamiento productivo — PASS.
- cero `pageerror` no controlados — PASS.
- `main` intacto — PASS.

Informe 0C: `docs/V22_0C_STABILIZATION_CERTIFICATION_REPORT.md`.

## 2. Estado del commit utilizado

Implementación 1A:

`b42e31e13d4788c470ce592646505350ae98bf77`

GitHub Actions del mismo SHA:

- V22 local Supabase integration — run **42561638532** — **SUCCESS**.
- V22 browser baseline — run **42561638483** — **SUCCESS**.

Outcomes reales del browser gate:

- `MOBILE_OUTCOME: success`
- `DESKTOP_OUTCOME: success`
- `SYNTAX_OUTCOME: success`

Los cuatro recorridos 0C permanecieron verdes tanto en mobile como desktop:

- student-navigation
- workout-comment-coach
- nutrition
- coach-workspace

El commit que contiene este informe es documental. Debe volver a superar la misma línea base antes de declarar 1A cerrada definitivamente.

## 3. Mapa de arquitectura heredada

### 3.1 Entrada y build efectivo

La aplicación parte de:

`base/team-fjz-source-v20.7.html`

y `build.py` actúa como orquestador secuencial de transformaciones.

El inventario automático de 1A detectó:

- **228 transforms/patches Python** en el orden efectivo del build.
- Primeras capas: V8.6/V8.7/V8.8 y V9.x.
- Últimas capas funcionales: V332, V335, V336, V337, V338, V339, V340, V341, V342 y V343.
- `staging_local_guard.py` y `v127_release_system.py` siguen teniendo ejecución tardía por compatibilidad.

El orden de ejecución es parte del comportamiento actual: cambiarlo sin pruebas puede cambiar la autoridad final de funciones globales.

### 3.2 Autoridades principales

| Dominio | Autoridad/cadena actual | Clasificación |
|---|---|---|
| Auth y sesión | base + V194/V263/V294 | Legacy compatible; alto riesgo |
| Render global | base + consolidaciones V125/V178/V180 y consumidores posteriores | Duplicado pero necesario |
| Realtime | V132/V192 + delegaciones V210–V218 | Dirección canónica con consumidores legacy |
| Guardado de workout | V205 → V207 → V340/V341 | Autoridad actual canónica |
| Rutinas | V200/V209 + editores históricos | Persistencia canónica + UI legacy |
| Comentarios | V73 → V287 → V325 → V328/V329/V336 | Cadena funcional canónica actual |
| Alertas/revisiones | V299/V301/V302 + V331/V338/V339 | Varias generaciones aún activas |
| Dashboard Coach | V170 visible + compatibilidad posterior | Autoridad final legacy-compatible |
| Agenda | V310–V314 + V342 | Candidata a migración |
| Nutrición | base/V94 + V153/V216/V229 y posteriores | Alto riesgo |
| Progreso/check-ins | snapshots históricos + V246–V260/V303–V309 | Alto riesgo |
| Release/PWA | V127 | Autoridad actual de release |

### 3.3 Globals compartidos

Continúan siendo críticos:

- `state`
- `mode`
- `coachTab`
- `coachStudentTab`
- `currentUser`
- `currentProfile`
- `supabaseClient`
- `cloudAthletes`
- `render`
- `saveState`

Esto confirma que una migración segura debe crear límites antes de retirar globals.

### 3.4 Topología runtime final observada

Inventario automático sobre el artefacto generado:

- render assignments: **18**
- Realtime channels: **2**
- timeouts: **56**
- intervals: **0**
- listeners: **51**
- MutationObservers: **3**
- canonical date core: **presente**
- date pilot integrado: **presente**

V343 compara la topología antes/después de la integración del módulo de fechas y falla si agrega render assignments, channels, timers, listeners u observers.

### 3.5 Supabase detectado

El scanner encontró **27 tablas referenciadas literalmente**:

`athlete_habits`, `athlete_reminders`, `athlete_schedule`, `athlete_snapshots`, `athletes`, `body_measurements`, `checkin_schedules`, `coach_feed_state`, `coach_media_settings`, `coach_payments`, `exercise_feedback`, `exercise_library`, `exercise_media`, `fitness_recipes`, `food_library`, `nutrition_habit_logs`, `nutrition_logs`, `nutrition_plan_revisions`, `nutrition_plans`, `nutrition_templates`, `profiles`, `progress_photos`, `student_alert_state`, `student_notices`, `supplement_library`, `weekly_checkins`, `workout_sessions`.

RPCs detectadas:

- `claim_athlete_invite`
- `commit_workout_session_v202`
- `delete_my_athlete`
- `delete_workout_session_v214`
- `get_coach_feed`
- `get_student_alerts`
- `reorder_athlete_exercises`
- `update_my_athlete_profile`
- `update_my_athlete_profile_v2`

Este inventario es evidencia de referencias literales en código, no una afirmación de que todas se ejecuten en cada recorrido.

## 4. Dependencias críticas

Las dependencias más sensibles son:

1. **Snapshot del atleta**: múltiples módulos dependen de IDs y formas históricas de `athlete_snapshots`.
2. **Sesiones confirmadas**: workout save y readback no deben separarse de la protección V207/V340/V341 sin cobertura equivalente.
3. **Render global**: todavía existen múltiples generaciones y handlers inline.
4. **Realtime**: sólo hay dos canales finales auditados, pero muchos consumidores dependen de la autoridad consolidada.
5. **Auth/RLS**: permisos Coach/Alumno y recuperación de sesión son de alto riesgo.
6. **Comentarios**: dependen tanto de `exercise_feedback` como de snapshots de sesión y estado revisado.
7. **Nutrición/progreso/check-ins**: fuerte dependencia de modelos históricos y UI.
8. **Fechas**: existen usos distribuidos con semánticas distintas entre “día calendario” e “instante exacto”.

No se eliminó ninguna pieza legacy en 1A.

## 5. Arquitectura modular propuesta

Se creó la base:

```
src/
  core/
  data/
  modules/
  ui/
  legacy/
```

### core
Primitivas transversales sin dependencia de Supabase/UI.

### data
Contratos de repositorio y futuros adapters. La UI deberá migrar progresivamente para dejar de repetir consultas Supabase.

### modules
Orquestación por dominio una vez que los límites estén probados. 1A no movió ningún dominio completo.

### ui
Futuros componentes reutilizables y criterios visuales consolidados.

### legacy
Compatibilidad explícita mientras existan consumidores históricos.

La estrategia es **strangler/progressive migration**, no reescritura: una autoridad nueva se introduce, se prueba, convive con legacy, se migran consumidores y sólo después se retira código viejo.

## 6. Primer módulo canónico implementado: fechas

Archivo:

`src/core/date.js`

Responsabilidades:

- obtener fecha calendario correcta en una zona horaria explícita;
- usar por defecto `America/Argentina/Buenos_Aires`;
- separar día calendario de timestamp exacto;
- formatear timestamps visibles;
- validar timestamps y zonas horarias;
- conservar cadenas históricas `YYYY-MM-DD` sin reinterpretarlas como UTC.

API:

- `calendarDate()`
- `exactTimestamp()`
- `formatTimestamp()`
- `describe()`
- `DEFAULT_TIME_ZONE`

### Integración limitada

Sólo se migró `dateInputToday()`.

Antes de 1A, 0C ya había eliminado el bug UTC usando componentes locales del navegador. En 1A esa función ahora usa el módulo canónico con timezone explícita y mantiene la lógica anterior como fallback.

No se migraron masivamente otras funciones de fecha.

### Casos unitarios obligatorios

Se probaron:

- 20:59 Argentina
- 21:00 Argentina
- 23:59 Argentina
- 00:01 Argentina
- preservación de fecha histórica date-only
- diferencia entre calendar date y exact timestamp
- timestamp inválido

Todos pasaron.

## 7. Contratos definidos

### 7.1 Guardado y errores

`src/core/save-contract.js`

Estados:

- `pending`
- `saving`
- `confirmed`
- `recoverable_error`
- `fatal_error`
- `retry_pending`

El contrato exige evidencia `serverConfirmedAt` para construir un receipt confirmado.

No reemplaza todavía los guardados actuales.

### 7.2 Repositorios

`src/data/repository-contracts.js`

Puertos declarados:

- WorkoutRepository
- CommentRepository
- NutritionRepository
- ProgressRepository
- CheckinRepository
- AgendaRepository
- CoachRepository

### 7.3 Piloto de bajo riesgo

Se implementó únicamente un wrapper read-only `AgendaRepository` que valida y delega:

- `listForAthlete`
- `getById`

No está conectado a UI ni a Supabase runtime. Su objetivo es demostrar el límite de arquitectura sin cambiar comportamiento visible.

### 7.4 Compatibilidad preservada

Los contratos futuros deberán conservar:

- IDs históricos
- snapshots
- sesiones
- rutinas
- comentarios
- nutrición
- check-ins
- fotografías
- estados de revisión
- permisos Coach/Alumno

## 8. Archivos realmente modificados

Commit 1A.1:

- `build.py`
- `.github/workflows/v22-browser-baseline.yml`
- `.github/workflows/v22-local-integration.yml`
- `src/core/date.js`
- `src/core/save-contract.js`
- `src/data/repository-contracts.js`
- `src/core/README.md`
- `src/data/README.md`
- `src/modules/README.md`
- `src/ui/README.md`
- `src/legacy/README.md`
- `v343_v22_1a_architecture_foundation.py`
- `tests/unit/v22-date.test.js`
- `tests/unit/v22-contracts.test.js`
- `scripts/v22_architecture_inventory.py`
- `docs/V22_1A_ARCHITECTURE_MAP.md`

Este informe agrega únicamente:

- `docs/V22_1A_ARCHITECTURE_FOUNDATION_REPORT.md`

## 9. Pruebas ejecutadas

### Tests específicos 1A

`node --test tests/unit/v22-date.test.js tests/unit/v22-contracts.test.js`

Ejecutados en los dos workflows y **PASS**.

Cubren:

- timezone Argentina;
- boundary times;
- preservación histórica;
- separación calendar/instant;
- save-state transitions;
- confirmación de servidor obligatoria;
- siete contratos de repositorio;
- AgendaRepository pilot.

### Línea base heredada de 0C

Sin reducción:

- JavaScript syntax audit
- preflight
- Supabase local integration
- recreate DB
- isolation guards
- Playwright 390×844
- Playwright 1440×900
- student-navigation
- workout-comment-coach
- nutrition
- coach-workspace

### RLS

1A no modificó tablas, políticas, schema ni adapters Supabase runtime. Por lo tanto no creó una superficie RLS nueva. La integración local existente y sus checks continuaron verdes.

## 10. Resultados de GitHub Actions

Sobre `b42e31e13d4788c470ce592646505350ae98bf77`:

### Integration — 42561638532

**SUCCESS**

Pasaron:

- branch/main baseline guard
- static development guard
- 1A unit tests
- negative isolation tests
- local Supabase smoke
- build
- architecture inventory guard
- explicit preflight
- recreate DB + repeated smoke
- final generated-artifact isolation

### Browser — 42561638483

**SUCCESS**

Pasaron:

- branch/main baseline guard
- 1A unit tests
- local build
- architecture inventory guard
- JS syntax audit
- mobile E2E
- reset
- desktop E2E
- final isolation + QA gate

Evidencia de aislamiento:

- `production references: blocked`
- `production data copied: 0`
- `Production/staging isolation guards: OK`
- `forbidden_present: []`

## 11. Comparación antes / después

| Área | Antes de 1A | Después de 1A |
|---|---|---|
| Arquitectura | orden acumulativo conocido sólo implícitamente | inventario automático + mapa documentado |
| Estructura `src/` | inexistente | core/data/modules/ui/legacy preparados |
| Fechas | helpers distribuidos | primer core canónico + integración acotada |
| Argentina 21:00 | bug corregido puntualmente en 0C | contrato reusable y tests de frontera |
| Guardados | estados distribuidos por dominio | contrato común definido, no impuesto |
| Data access | Supabase mezclado con UI | siete puertos definidos |
| Repositorio piloto | ninguno | Agenda read-only, sin wiring runtime |
| Diseño | estilos acumulados | criterios de consolidación documentados |
| QA arquitectura | sólo audits históricos | unit tests + inventory guard en ambos workflows |
| Runtime topology | legado acumulativo | 1A garantiza cero crecimiento por el date pilot |
| Producción | protegida | sigue intacta |

## 12. Riesgos pendientes

1. 228 transforms indican alta deuda acumulativa.
2. 18 asignaciones de render siguen siendo demasiadas para una arquitectura final.
3. 56 timeouts y 51 listeners requieren análisis por ownership antes de reducirlos.
4. Los contratos de repositorio todavía no tienen adapters reales.
5. El save contract no está conectado a dominios existentes.
6. Quedan más helpers de fecha por clasificar y migrar uno por uno.
7. Auth, Realtime, workout save, nutrition, progress/photos y RLS continúan siendo zonas de alto riesgo.
8. Los snapshots históricos siguen siendo un contrato de compatibilidad central.
9. No debe borrarse legacy hasta mapear consumidores y tener pruebas del reemplazo.

## 13. Confirmación de producción intacta

Al finalizar la implementación 1A.1:

- `main` continúa en `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`.
- no hubo deploy de Render;
- no se ejecutaron migraciones productivas;
- no se modificó Supabase producción;
- no se utilizaron datos reales;
- los builds de desarrollo bloquearon referencias productivas;
- `production data copied: 0`.

## 14. Recomendación para el siguiente bloque

No avanzar automáticamente.

Tras aprobar este informe, el siguiente bloque debería continuar la modernización progresiva, no una refactorización masiva. La secuencia recomendada es:

1. ampliar el inventario de consumidores de helpers de fecha y migrar sólo otro uso de bajo riesgo;
2. implementar un adapter real read-only para AgendaRepository **únicamente en entorno V22**, manteniendo fallback legacy;
3. agregar contract tests contra Supabase local para ese adapter antes de conectar UI;
4. comenzar a usar el save contract en un flujo no crítico o en una capa de observación antes de tocar workout/session save;
5. mantener Nutrition, Auth y confirmed workout save fuera del primer reemplazo de data layer.

No iniciar 1B ni funcionalidades nuevas sin aprobación explícita.
