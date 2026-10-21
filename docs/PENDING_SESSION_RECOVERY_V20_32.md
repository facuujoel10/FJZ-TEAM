# TEAM FJZ — V20.32 Pending Session Recovery Checkpoint

Fecha: 2026-10-21
Branch de respaldo: `checkpoint-v20.32-pending-recovery`
Línea de trabajo: `develop`
Producción: `main` sin modificar

## Problema cerrado

Una sesión finalizada podía quedar guardada localmente pero pendiente de confirmación en nube. Tras una recarga, V20.7 pierde su estado en memoria y V20.2 podía borrar el marcador si no encontraba la sesión en el estado local.

## V20.32

- El marcador `fjz_v201_pending_session` nunca se borra solo porque falte la copia local.
- Antes de iniciar otra sesión, V20.5 consulta el pendiente.
- Si existe, se bloquea el nuevo entrenamiento y se abre recuperación.
- La recuperación utiliza `__fjzQueueSessionSyncV201` y el mismo `session.id`.
- Si la sesión local falta, el usuario puede actualizar datos y reintentar; no existe ruta de descarte automático.
- V20.7 solo delega a esta protección cuando su propio state machine está `idle`.
- Durante recuperación manual se activa `__fjzManualSessionCommitV207` para no competir con reintentos automáticos.
- Sin cambios de esquema ni Supabase.

## QA staging

- Stylesheets: 1
- Render assignments: 20
- startWorkout assignments: 12
- finishWorkout assignments: 5
- Realtime channels: 2
- MutationObservers: 3
- PerformanceObservers: 0
- Timeouts: 55
- RAF: 24
- Listeners: 49
- Preflight: OK
- Smoke test: OK
- Consolidation audit: OK
- Staging-local guard: OK

## Producción

- `main`: sin cambios.
- Supabase producción: sin cambios.
- Pagos/cobranzas: sin cambios.
