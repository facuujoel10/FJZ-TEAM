# TEAM FJZ V22 — ETAPA 4C · Agenda Premium y Seguimiento Inteligente

## Estado
Etapa implementada exclusivamente en `dev/team-fjz-v22`. Base certificada de entrada: `374bfff596a79ba36debbec490989bbaa20c12dc`. Producción debe permanecer en `main@3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`.

La implementación funcional quedó validada sobre `91c006a542d81e283d18be99ebc9d5cead794190` con Integración SUCCESS y Browser SUCCESS. Este informe y la corrección del capturador visual forman el commit documental/evidencial final; por política de certificación, ese nuevo SHA también debe completar Integración + Browser en SUCCESS antes del cierre externo.

## Diagnóstico técnico de 4C
La agenda heredada combinaba Agenda V8.1/V16.x, superficies de inicio V21.10/V21.12 y el calendario operativo del Coach V20.59/V20.80. La persistencia real ya estaba endurecida por V21.04 y la lectura canónica por AgendaRepository V22. El trabajo de 4C fue de composición, navegación, lectura coherente y experiencia premium, sin crear un segundo motor de agenda.

### Incidente responsive 360×800
El run Browser `44331289560` sobre `83ec6acef2c442729b2c1503cf2012c0330a0420` terminó FAILURE. La evidencia del log mostró:

- Bloque: `Premium responsive — mobile 360x800`.
- Test que falló: `V22 4A-UX Coach: editor principal entra en primer viewport y no duplica cabeceras`.
- Archivo: `tests/e2e/v22-nutrition-ux-final-polish.spec.js`.
- Error: `TypeError: Cannot read properties of null (reading 'top')`.
- Aserción afectada: `expect(geo.meal.top).toBeLessThan(geo.h)`.
- Causa raíz: carrera de hidratación E2E; `.fjz4a-meal-editor` todavía no existía cuando el test midió geometría.
- Supabase local, fixtures, Auth/RLS y la Agenda 4C no fueron la causa. En ese mismo run, 390×844 y desktop completaron sus pruebas, y los tests de Agenda 4C ya habían pasado.

La corrección mínima fue `0a6b16c2103c0de1dcc5897a006cefac9a19b97c`: esperar explícitamente que `.fjz4a-meal-editor` sea visible antes de medir, sin eliminar pruebas, sin relajar la aserción geométrica y sin aumentar timeouts arbitrariamente.

## Ajuste final de Athlete 360
El commit `91c006a542d81e283d18be99ebc9d5cead794190` estabilizó el frame de identidad de Athlete 360:

- conserva/crea el slot de avatar canónico;
- identifica correctamente el bloque `.v175-coach-profile-info`;
- evita el colapso del nombre del alumno;
- mantiene acciones heredadas ocultas;
- añade una aserción geométrica real en Agenda 4C: nombre >120 px, altura <90 px y avatar >=50 px;
- no crea navegación duplicada ni wrappers globales nuevos.

La revisión manual de las capturas de ese SHA confirmó nombre completo, avatar y composición correcta en 390×844 y 1440×900.

## Incidente del capturador visual final
El Browser `44347514473` sobre `e821fac6b19e90599cc8984b576c7379caeaff4b` completó SUCCESS en 390×844, 360×800, 430×932 y 1440×900, además del gate final de aislamiento. El único fallo fue el paso de captura 4C.

Evidencia exacta:
- script: `scripts/capture_4c_agenda.js`;
- línea afectada: espera posterior a `closeModal()`;
- locator: `#v165Title`;
- error: timeout esperando `state:'detached'`;
- estado real: el input permanecía en DOM pero oculto, que es el comportamiento válido del modal legacy.

Causa raíz: condición incorrecta del capturador visual, no defecto del producto ni de Agenda 4C. La corrección mínima cambia sólo la espera de `detached` a `hidden`; no modifica lógica de producto, fixtures, timeouts funcionales ni aserciones E2E.

## Corrección de evidencia visual
El artifact `14445433480` del Browser SUCCESS `44340225926` expuso que las imágenes etiquetadas `v224c-*-student-agenda` mostraban Home. El producto no estaba fallando: los E2E de Agenda Alumno usan navegación real por el botón `Agenda` y pasaron en 360/390/430/1440.

La causa estaba exclusivamente en `scripts/capture_4c_agenda.js`: para V22 4C cambiaba `studentTab` y llamaba al refresh interno, que actualiza datos pero no garantiza navegación de UI. La corrección final hace click en el botón real `Agenda` y espera `.fjz4c-student` visible antes de capturar. No altera código de producto.

## Autoridades verificadas
- `AgendaRepository`: lectura canónica por atleta, caché ligada a identidad, cancelación de resultados de sesión anterior y `getById`.
- `athlete_schedule`: programación semanal.
- `athlete_reminders`: recordatorios únicos o semanales.
- `saveStudentScheduleV81`: escritura semanal existente con read-back exacto.
- `saveReminderV81` / `deleteReminderV81`: recordatorios existentes y verificados.
- `America/Argentina/Buenos_Aires`: zona de presentación y fecha pura.
- Athlete 360: navegación individual al tab Agenda.
- Command Center: entrada y regreso del Coach.

No se creó tabla, columna, RPC, migración, repositorio paralelo, canal Realtime, timer u observer.

## Transformación visual
4C agrega:
- Agenda Alumno con hero compacto, próximo evento y calendario mensual.
- Lista contextual por fecha y detalle del evento.
- Agenda global del Coach con calendario, próximos seguimientos y acceso exacto al alumno.
- Agenda dentro de Athlete 360 usando la misma autoridad.
- Acciones Coach para crear recordatorios y editar programación semanal mediante flujos existentes.
- Responsive específico para 360×800, 390×844, 430×932 y 1440×900.

## Fechas, persistencia y sincronización
Las fechas `YYYY-MM-DD` se tratan como fechas de calendario, no como instantes UTC. Los eventos semanales siguen la convención local de weekday y la hora se conserva como `HH:mm`.

El smoke 4C con Supabase local y usuarios ficticios verifica:
- creación por Coach;
- lectura por Coach y alumno autorizado;
- aislamiento frente a otro alumno y Coach no autorizado;
- edición y relectura;
- conservación de fecha pura/hora;
- eliminación durable.

Los wrappers existentes mantienen:
- read-back exacto de agenda semanal;
- confirmación de recordatorio recuperable antes de éxito;
- confirmación de ausencia tras borrado;
- locks existentes para escrituras críticas.

## Auth/RLS
No se modificó Auth ni RLS productivo. Todo QA usa Supabase local y fixtures ficticios. No se copiaron datos productivos.

## QA ejecutado
Cobertura 4C:
- `tests/unit/v22-agenda-premium.test.js`
- `tests/e2e/v22-agenda-premium.spec.js`
- `scripts/dev_agenda_4c_rls_smoke.py`
- `scripts/capture_4c_agenda.js`

Además se conservaron los tests heredados de 2A a 4B.

Validaciones confirmadas en `91c006a542d81e283d18be99ebc9d5cead794190`:
- 390×844: SUCCESS.
- 360×800: SUCCESS.
- 430×932: SUCCESS.
- 1440×900: SUCCESS.
- Agenda Alumno: PASS.
- Agenda Coach: PASS.
- Agenda Athlete 360: PASS.
- Entrenamiento/historial/comentarios: PASS.
- Nutrición: PASS.
- Progreso/Check-ins: PASS.
- Unit + contracts + architecture guard: PASS.
- Final isolation gate: PASS.

## GitHub Actions de verificación de implementación
- Integración SUCCESS: https://github.com/facuujoel10/FJZ-TEAM/actions/runs/44340225843
- Browser SUCCESS: https://github.com/facuujoel10/FJZ-TEAM/actions/runs/44340225926
- Mismo SHA: `91c006a542d81e283d18be99ebc9d5cead794190`
- Artifact 4C: `v22-4c-agenda-premium-screens`, ID `14445433480`.

El cierre externo debe usar los runs SUCCESS del SHA final que contiene este informe y el capturador corregido.

## Comparación visual
La evidencia compara:
1. V21.41.
2. V22 pre-4C exacta: `374bfff596a79ba36debbec490989bbaa20c12dc`.
3. V22 4C final.

Se revisan viewport y full-page en mobile y desktop para Alumno, Coach y Athlete 360. La aprobación estética definitiva corresponde al Product Owner.

## Rendimiento y topología
4C no añade polling, Realtime, `setTimeout`, `setInterval`, MutationObserver ni PerformanceObserver. Reutiliza TTL e invalidación por identidad de AgendaRepository.

## Producción
`main`, Render y Supabase productivo permanecen fuera del alcance. `main` debe conservar `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`.

## Riesgos pendientes
No se identificó un bloqueo funcional pendiente de 4C. El riesgo residual es visual/productivo: aprobación final del Product Owner sobre las capturas del SHA final certificado.

## Propuesta técnica — Etapa 5 (NO iniciada)
Objetivo: auditoría integral y estabilización de TEAM FJZ V22 sin agregar funcionalidades.

Criterios de certificación propuestos:
1. Auth/sesiones: login, refresh, logout, reentrada y roles sin cierre inesperado.
2. Seguridad: aislamiento Coach/Alumno, RLS A/B, ausencia de accesos cruzados y sin cambios productivos.
3. Command Center + Athlete 360: navegación única, identidad estable, estados de error/recuperación.
4. Entrenamiento: sesiones, historial, PRs, temporizador, comentarios exactos, autoguardado y refresh.
5. Alertas/revisiones: agrupación, OK durable, navegación al contexto correcto y ausencia de “primera revisión” espuria.
6. Nutrición: plan, macros, consumo, editor Coach, historial, errores y aislamiento.
7. Progreso/fotos/check-ins: persistencia, reintento idempotente, revisión y responsive.
8. Agenda: CRUD, sincronización, fecha pura, programación semanal, Coach global y Athlete 360.
9. Responsive: 360×800, 390×844, 430×932 y 1440×900 sin overflow ni navegación duplicada.
10. Accesibilidad: foco, nombres accesibles, contraste y objetivos táctiles.
11. Rendimiento/topología: inventario de listeners/timers/observers, ausencia de duplicaciones y regresiones.
12. Evidencia final: Integration + Browser SUCCESS sobre el mismo SHA, artifacts visuales y comparación global V21.41→V22.

La Etapa 5 no debe iniciarse sin autorización explícita del Product Owner.
