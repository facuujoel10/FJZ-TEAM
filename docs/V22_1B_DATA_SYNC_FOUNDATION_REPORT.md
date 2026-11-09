# TEAM FJZ V22 — Etapa 1B · Data & Sync Foundation Report

Fecha: 2026-11-09  
Rama: `dev/team-fjz-v22`  
Producción: `main`  
Baseline productivo protegido: `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`

## 1. Commit inicial y final

Base 1A aprobada:

`bf534358fe87d740136eb4c7e5dd16eada750202`

Antes de implementar 1B se actualizó únicamente la evidencia final de 1A:

`2f2a273887638683d01652ae3c904dc4f2317573`

Commit final certificado de 1B:

`b100ca9203abfbddabb9ca18b4d7d9ee00521163`

El cierre documental y los dos workflows finales fueron certificados sobre ese mismo SHA.

## 2. Estado de producción

Producción permaneció intacta durante toda 1B:

- `main`: `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`
- Deploys de Render: **0**
- Migraciones productivas: **0**
- Cambios en Supabase producción: **0**
- Cambios en Auth/RLS producción: **0**
- Datos reales de alumnos utilizados: **0**
- Servicios pagos agregados: **0**
- Referencias productivas permitidas en el artefacto V22 de desarrollo: **0**

Los workflows siguieron ejecutando los guards fail-closed de entorno y reportaron `production data copied: 0`, `production references: blocked`, `Production/staging isolation guards: OK` y `forbidden_present: []`.

## 3. Archivos modificados

Cambios de 1B respecto de la base 1A:

- `.github/workflows/v22-browser-baseline.yml`
- `.github/workflows/v22-local-integration.yml`
- `docs/V22_1A_ARCHITECTURE_FOUNDATION_REPORT.md` — actualización documental de la certificación final de 1A.
- `scripts/dev_agenda_repository_smoke.py`
- `scripts/v22_architecture_inventory.py`
- `src/core/save-contract.js`
- `src/data/README.md`
- `src/data/agenda-read-policy.js`
- `src/data/agenda-repository.js`
- `tests/e2e/v22-baseline.spec.js`
- `tests/unit/v22-agenda-repository.test.js`
- `tests/unit/v22-save-sync.test.js`
- `v343_v22_1a_architecture_foundation.py`

No se creó otro patch Python V344/V345. La integración continuó dentro del integrador fuente V343 existente.

## 4. Repositorio real implementado

Se implementó `src/data/agenda-repository.js` como primer repositorio real de TEAM FJZ V22.

### Responsabilidad

Es una capa canónica de lectura sobre las tablas ya existentes:

- `athlete_schedule`
- `athlete_reminders`

No renderiza UI, no modifica Auth, no posee una service/admin key y no escribe datos.

### API real

`createAgendaRepository({ supabase, ttlMs, clock })`

Expone:

- `listForAthlete(athleteId, options)`
- `getById(eventId)`
- `clear(athleteId?)`

### Propiedades implementadas

- filtros explícitos por `athlete_id`;
- sólo registros activos en la lectura de agenda;
- usa el cliente Supabase autenticado normal;
- RLS sigue siendo la autoridad final;
- coalescing de lecturas concurrentes;
- cache corto de 15 segundos;
- resultado vacío controlado;
- `getById` controlado para inexistentes/RLS-hidden;
- clasificación de error de red, permiso, query e integridad;
- preservación de strings históricas de fecha/hora;
- objetos de resultado congelados para evitar mutaciones accidentales.

No se creó una “segunda Agenda”: el repositorio reemplaza únicamente la fuente de datos de un recorrido existente.

## 5. Contratos de lectura

### listForAthlete

Devuelve un objeto con:

- `source: "agenda-repository-v22"`
- `athleteId`
- `schedule[]`
- `reminders[]`
- `loadedAt`

Una respuesta vacía es un resultado válido y autoritativo.

### getById

Devuelve:

- evento de `schedule`, o
- evento de `reminder`, o
- `null` si el evento no existe o RLS no lo hace visible para ese usuario.

No existe un camino de elevación de permisos.

### Compatibilidad fail-closed

`src/data/agenda-read-policy.js` define la regla de convivencia con legacy:

- feature flag desactivado → puede usarse legacy;
- feature flag activado → canonical es autoritativo;
- canonical vacío → **no fallback**;
- error de red → **no fallback**;
- error de permiso → **no fallback**.

Esto evita que una lectura denegada por RLS sea “rescatada” accidentalmente por una ruta legacy.

## 6. Pruebas Auth/RLS

Se agregó `scripts/dev_agenda_repository_smoke.py`, ejecutado contra Supabase local con fixtures ficticios y usuarios autenticados normales.

Pruebas verificadas:

1. Coach autorizado consulta agenda de su alumno — PASS.
2. Alumno consulta sus propios eventos — PASS.
3. Alumno A consulta eventos de Alumno B — resultado vacío por RLS — PASS.
4. Evento propio por ID — PASS.
5. Evento cruzado por ID — no visible — PASS.
6. Evento inexistente — resultado controlado — PASS.
7. Alumno sin eventos — resultado vacío controlado — PASS.
8. Reminder propio — PASS.
9. Reminder de otro alumno — no visible — PASS.
10. Fecha `2026-01-20` conservada como date-only — PASS.
11. Service/admin key expuesta al navegador — **0**.

El mismo contrato se ejecutó nuevamente después de recrear la base local desde cero y volvió a pasar.

No se agregó ni modificó una política RLS en 1B: se validaron las políticas locales existentes, basadas en `can_access_athlete(athlete_id)`.

## 7. Integración controlada con Agenda

Se eligió un único recorrido existente y de bajo riesgo:

`loadOwnAppointmentsV312()`

Ese recorrido ya alimentaba las fechas visibles del alumno y la integración V312/V313/V314.

En desarrollo/test:

- V343 inyecta los módulos fuente;
- activa `fjz-v22-agenda-repository-read=enabled`;
- V312 utiliza `TeamFJZAgendaRepository`;
- el resultado se identifica con `source: "agenda-repository-v22"`.

En producción, el flag queda desactivado y el comportamiento publicado permanece legacy.

No se modificaron:

- creación de eventos;
- edición de eventos;
- eliminación de eventos;
- render global;
- navegación global;
- Realtime;
- Auth;
- RLS.

## 8. Segundo uso de fechas migrado

Se mantuvo `src/core/date.js` como fuente canónica.

El segundo uso de bajo riesgo migrado fue:

`isoV310(d)`

Ahora intenta:

`TeamFJZDate.calendarDate(d, "America/Argentina/Buenos_Aires")`

y mantiene la construcción local histórica como fallback.

No se modificaron timestamps históricos ni se reinterpretaron registros anteriores.

Los tests de Argentina de 1A —20:59, 21:00, 23:59 y 00:01— permanecieron activos y verdes.

## 9. Avances del contrato de guardado y sincronización

Se extendió `src/core/save-contract.js` con una implementación de referencia pura:

`createSaveTracker()`

Estados soportados:

- `pending`
- `saving`
- `confirmed`
- `recoverable_error`
- `retry_pending`
- `fatal_error`

El tracker mantiene snapshot + history y exige un `serverConfirmedAt` explícito antes de permitir `confirmed`.

Se agregaron tests que prueban:

- no se puede confirmar antes de evidencia del servidor;
- error recuperable y retry son estados diferentes;
- retry vuelve a `saving`;
- confirmación durable conserva timestamp;
- error fatal es terminal.

Este tracker **no está conectado** a workout, nutrición, check-ins ni Agenda writes. V207/V340/V341 permanecen sin cambios como autoridad de guardado de sesiones.

## 10. Arquitectura antes / después

| Indicador | Antes 1B | Después 1B |
|---|---:|---:|
| Python transforms | 228 | **228** |
| Render assignments | 18 | **18** |
| Realtime channels | 2 | **2** |
| Timeouts final artifact | 56 | **56** |
| Intervals | 0 | **0** |
| Listeners | 51 | **51** |
| MutationObservers | 3 | **3** |
| Repositorios Supabase reales en `src/data` | 0 | **1** |
| Agenda read fail-closed policy | no | **sí** |
| Agenda RLS contract dedicado | no | **sí** |
| Save state reference tracker | no | **sí** |

V343 compara la topología antes/después del piloto y falla si la integración local agrega runtime topology.

El inventory guard final además exige exactamente la topología certificada de 1A y que el número de transforms siga siendo 228.

## 11. Resultados de Playwright

Run de implementación:

https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42621466469

Resultado: **SUCCESS**

### Mobile 390×844

- `E2E_FLOW_OK student-navigation mobile-390`
- `E2E_FLOW_OK workout-comment-coach mobile-390`
- `E2E_FLOW_OK nutrition mobile-390`
- `E2E_FLOW_OK agenda-repository mobile-390`
- `E2E_FLOW_OK coach-workspace mobile-390`

### Desktop 1440×900

- `E2E_FLOW_OK student-navigation desktop-1440`
- `E2E_FLOW_OK workout-comment-coach desktop-1440`
- `E2E_FLOW_OK nutrition desktop-1440`
- `E2E_FLOW_OK agenda-repository desktop-1440`
- `E2E_FLOW_OK coach-workspace desktop-1440`

Gate real:

- `MOBILE_OUTCOME: success`
- `DESKTOP_OUTCOME: success`
- `SYNTAX_OUTCOME: success`

Los ocho recorridos heredados permanecieron sin eliminación; se agregaron dos ejecuciones del nuevo recorrido Agenda, una por viewport.

## 12. Resultados de Supabase local

Run de implementación:

https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42621466408

Resultado: **SUCCESS**

Pasaron:

- branch/main isolation guard;
- static development guard;
- unit + contract tests;
- negative isolation tests;
- Supabase local integration smoke;
- AgendaRepository Auth/RLS smoke;
- build V22;
- architecture inventory guard;
- preflight;
- recreate DB desde cero;
- repeat AgendaRepository Auth/RLS smoke;
- final artifact isolation.

Evidencia del segundo smoke:

- `TEAM FJZ V22 1B AGENDA REPOSITORY/RLS SMOKE OK`
- `Coach authorized read: OK`
- `Student own read: OK`
- `Cross-student isolation: OK`
- `Event by id + missing/empty results: OK`
- `Date-only preservation: OK`
- `Service/admin key exposed to browser: 0`

## 13. GitHub Actions

Cierre 1B certificado sobre el mismo SHA `b100ca9203abfbddabb9ca18b4d7d9ee00521163`:

- Integración local: https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42622258794
- Browser E2E: https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42622258858

Ambas ejecuciones finalizaron SUCCESS.

## 14. Fallos y limitaciones pendientes

### Fallos encontrados durante 1B y resueltos

Se encontraron tres problemas exclusivamente en el integrador V343 antes de llegar a la aplicación:

1. `ab1ec37...`: SyntaxError Python por quoting de la regex de script.
2. `e385559...`: regex de topología sobre-escapada.
3. `d15c424...`: newlines emitidos como texto literal `\n`, detectados por el JS syntax audit.

Los tres fallos fueron detectados por QA, corregidos sin relajar pruebas y recertificados desde cero.

### Limitaciones deliberadas

- sólo se migró una lectura de Agenda;
- V165/V310 y otras lecturas legacy no se migraron masivamente;
- no hay writes en AgendaRepository todavía;
- no se modificó Realtime;
- el cache es local al repositorio, sin invalidación Realtime todavía;
- RLS-hidden y evento inexistente retornan ambos “no visible” a nivel de lectura, como corresponde a una política de filtrado;
- el save tracker es una referencia, no autoridad productiva;
- no se migraron Nutrition/Progress/Checkin repositories.

## 15. Costo adicional

Costo adicional de 1B: **cero**.

No se incorporaron:

- servicios pagos;
- proveedores nuevos;
- infraestructura adicional;
- bases externas;
- herramientas premium;
- claves administrativas en frontend.

Se utilizaron GitHub Actions existentes y Supabase local.

## 16. Recomendación concreta para el siguiente bloque

No avanzar automáticamente.

Después de aprobar 1B, el siguiente bloque debería profundizar la capa de datos de forma controlada:

1. convertir el piloto AgendaRepository en un adapter con ownership explícito de invalidación/cache;
2. migrar una segunda lectura de Agenda o CommentRepository, no ambos a la vez;
3. agregar contract tests de la nueva capa antes de conectar más UI;
4. definir una estrategia de errores de repositorio común;
5. empezar a observar el save tracker en un flujo no crítico antes de conectarlo a escrituras;
6. mantener workout confirmed-save, Auth, Nutrition y Progress fuera de la primera migración de writes.

No se inicia ninguna etapa posterior desde este informe.
