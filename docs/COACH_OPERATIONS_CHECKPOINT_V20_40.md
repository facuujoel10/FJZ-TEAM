# TEAM FJZ — Coach Operations Checkpoint V20.40

Fecha: 2026-10-21
Branch de respaldo: `checkpoint-v20.40-coach-operations`
Trabajo activo: `develop`
Producción: `main` sin modificar

## Bloque funcional Coach V20.35–V20.40

### V20.35 — Coach Workflow Pro
- filtros operativos de alumnos;
- Alumnos en foco;
- accesos directos a Resumen / Rutina / Check-in / Progreso;
- búsqueda sin recargar el feed en cada tecla.

### V20.36 — Coach Work Queue
- ordenar por prioridad;
- menor adherencia;
- más días sin entrenar;
- nombre;
- botón Siguiente prioridad con apertura automática de la pestaña relevante.

### V20.37 — Coach Review Hub
- Desde tu última revisión;
- cambios detectados;
- decisiones pendientes;
- marcar revisión completada;
- baseline persistido dentro del snapshot del alumno.

### V20.38 — Review Loop
- el dashboard distingue cambios nuevos, sin revisión y revisado;
- cambios desde la revisión influyen en la prioridad;
- filtro Cambios nuevos;
- filtro Sin revisión.

### V20.39 — Decision Log
- decisión principal por revisión;
- nota opcional;
- historial limitado a 12 revisiones;
- última decisión visible en Resumen 360.

### V20.40 — Review Cadence
- frecuencia semanal / quincenal / mensual;
- revisión vencida;
- filtro de revisiones vencidas;
- vencimiento integrado en Siguiente prioridad.

## QA staging
- stylesheets: 1
- renders: 20
- realtime channels: 2
- timeouts: 55
- RAF refs: 24
- listeners: 49
- MutationObservers: 3
- PerformanceObservers: 0
- Preflight: OK
- Smoke: OK
- Consolidation audit: OK
- Production/staging isolation: OK

## Fuera de alcance
- pagos/cobranzas;
- Supabase producción;
- merge a main.
