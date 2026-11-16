# TEAM FJZ V22 — ETAPA 4C · Agenda Premium y Seguimiento Inteligente

## Estado
Etapa implementada exclusivamente en `dev/team-fjz-v22`. Base certificada: `374bfff596a79ba36debbec490989bbaa20c12dc`. Producción debe permanecer en `main@3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`.

El SHA final se declara en el cierre externo una vez que Integración y Browser terminen SUCCESS sobre el mismo HEAD.

## Diagnóstico técnico
La agenda heredada combinaba tres capas: Agenda V8.1/V16.x, superficies de inicio V21.10/V21.12 y el calendario operativo del Coach V20.59/V20.80. La persistencia real ya estaba endurecida por V21.04 y la lectura canónica por AgendaRepository V22. El problema de 4C era principalmente de composición, navegación y coherencia de lectura, no de esquema.

## Autoridades verificadas
- `AgendaRepository`: lectura canónica por atleta, caché ligada a identidad, cancelación de resultados de sesión anterior y `getById`.
- `athlete_schedule`: programación semanal.
- `athlete_reminders`: recordatorios únicos o semanales.
- `saveStudentScheduleV81`: escritura semanal existente, envuelta por V21.04 con read-back exacto.
- `saveReminderV81` / `deleteReminderV81`: recordatorios existentes, verificados por V21.04.
- `America/Argentina/Buenos_Aires`: zona de presentación y fecha pura.
- Athlete 360 3B: navegación individual al tab Agenda.
- Command Center 3A/3C: punto de regreso del Coach.

No se creó una segunda agenda, tabla, columna, RPC, migración, canal Realtime, timer u observer.

## Transformación visual
4C agrega:
- Agenda Alumno con hero compacto y próximo evento.
- Calendario mensual legible con días marcados.
- Lista contextual del día seleccionado.
- Detalle del evento sin navegación adicional.
- Próximos eventos en una superficie separada.
- Agenda global del Coach con calendario, próximos seguimientos y detalle por alumno.
- Agenda dentro de Athlete 360 usando la misma autoridad.
- Acciones Coach para crear recordatorios y editar la programación semanal mediante los flujos existentes.
- Responsive específico para 360×800, 390×844, 430×932 y 1440×900.

## Fechas y zona horaria
Las fechas `YYYY-MM-DD` se interpretan como fechas de calendario, no como instantes UTC. Los eventos semanales se derivan por weekday local lunes=0. La hora, cuando existe, se mantiene como HH:mm sin conversión arbitraria.

## Sincronización Coach ↔ Alumno
El smoke 4C utiliza Supabase local y usuarios ficticios para verificar:
- creación de recordatorio por Coach;
- recuperación por Coach y alumno autorizado;
- aislamiento frente a otro alumno y un Coach no autorizado;
- edición y relectura;
- conservación de fecha pura y hora;
- eliminación durable.

## Persistencia
4C no reemplaza los wrappers de V21.04:
- agenda semanal exige read-back exacto;
- recordatorio exige fila recuperable antes de éxito;
- borrado exige ausencia confirmada;
- los locks existentes evitan escrituras críticas concurrentes.

## Auth/RLS
No se modifica Auth ni RLS. El QA utiliza exclusivamente Supabase local. No se copian datos productivos.

## QA
Cobertura nueva:
- `tests/unit/v22-agenda-premium.test.js`
- `tests/e2e/v22-agenda-premium.spec.js`
- `scripts/dev_agenda_4c_rls_smoke.py`
- `scripts/capture_4c_agenda.js`

Incluye fecha pura, semanal, fin de año, ausencia de eventos vencidos como próximos, calendario, cambio de mes, refresh, no duplicados, Coach global, Athlete 360, RLS A/B y overflow.

## Capturas comparativas
El Browser workflow compara:
1. V21.41.
2. V22 pre-4C exacta: `374bfff596a79ba36debbec490989bbaa20c12dc`.
3. V22 4C final.

Artifact esperado: `v22-4c-agenda-premium-screens`, con viewport/full-page en mobile y desktop para Alumno, Coach y Athlete 360.

## Rendimiento y topología
El módulo 4C no añade polling, Realtime, `setTimeout`, `setInterval`, MutationObserver ni PerformanceObserver. Reutiliza el TTL y la invalidación por identidad de AgendaRepository.

## Compatibilidad histórica
No se eliminan eventos históricos ni se cambia la semántica de `athlete_schedule` / `athlete_reminders`. Los recordatorios únicos y semanales siguen siendo compatibles con las capas previas.

## Riesgos pendientes
La aprobación estética final corresponde al Product Owner sobre las capturas finales. No se inicia 4D ni Etapa 5 automáticamente.

## GitHub Actions
Los enlaces exactos de Integración y Browser se registran en el cierre de la etapa cuando ambos sean SUCCESS sobre el mismo SHA final.

## Producción
`main`, Render y Supabase productivo permanecen fuera del alcance de 4C.

## Nota de certificación

La certificación final debe considerar únicamente un par de workflows `Integración + Browser` completados sobre el mismo SHA. Runs cancelados por la política de concurrencia de GitHub Actions no se consideran fallos funcionales ni evidencia de cierre.


## Revalidación final

La certificación final incorpora montaje inmediato de las superficies Agenda Premium y lectura paralela de la cartera del Coach, preservando AgendaRepository, RLS y las autoridades de escritura existentes. No se añadieron tablas, migraciones, Realtime, polling ni cambios productivos.
