# TEAM FJZ V22 — Etapa 0B
## Auditoría funcional integral, QA de navegador y roadmap de transformación profesional

**Estado:** auditoría completada; baseline E2E bloqueada por defectos heredados de runtime.  
**Rama:** `dev/team-fjz-v22`  
**Commit de QA navegador:** `01364a84a012ac720efe82a54150f6ec6b11b060`  
**Producción de referencia:** V21.41 — `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`  
**GitHub Actions browser run:** https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42527765777  
**GitHub Actions integration run (mismo commit):** https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42527765649

---

# 1. Resumen ejecutivo

TEAM FJZ ya posee una cantidad importante de capacidades propias de una plataforma de coaching moderna: rutinas personalizadas, registro de entrenamiento, RIR, intensificaciones, historial, recuperación de sesiones, comentarios, check-ins, progreso, nutrición, agenda, alertas, fotos, videos, pagos y un workspace Coach.

El problema principal actual no es falta de funciones. El problema es que muchas de esas funciones se incorporaron mediante una larga cadena de parches que envuelven y vuelven a definir funciones globales.

La auditoría actual contabiliza aproximadamente:

- 225 parches versionados ejecutados por `build.py`.
- 76 scripts de auditoría ejecutados desde `preflight.py`.
- ~2 MB de HTML/JS generado.
- 117 bloques `<script>` en el artifact.
- 18 asignaciones de `render`.
- 11 asignaciones de `renderWorkout`.
- 9 asignaciones del editor de día.
- 2 canales Realtime.
- 56 `setTimeout`.
- 24 `requestAnimationFrame`.
- 51 listeners.
- 3 MutationObservers.

Esto ha permitido evolucionar la aplicación sin una reescritura, pero alcanzó un punto en el que la **integridad del artifact generado debe pasar a ser la prioridad número uno**.

La prueba de navegador real encontró cinco runtimes JavaScript inválidos en el artifact V22. El auditor histórico no los detectaba porque verificaba marcadores, conteos y contratos estáticos, pero no parseaba cada bloque JavaScript.

Por eso la primera fase de V22 no debe ser “agregar más funciones”. Debe ser:

1. recuperar integridad de runtime;
2. completar paridad del schema QA;
3. convertir Playwright en gate;
4. después modernizar los dominios de uno en uno.

No se recomienda una reescritura total.

---

# 2. Evidencia de aislamiento y seguridad

La auditoría se ejecutó únicamente sobre `dev/team-fjz-v22`.

Producción continuó en:

`3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`

No se realizó:

- merge a `main`;
- commit a `main`;
- deploy Render;
- restart de Render;
- modificación de Supabase producción;
- modificación de Auth/RLS producción;
- lectura de registros reales para los tests;
- creación de servicios pagos.

El workflow de navegador utilizó:

- GitHub Actions `ubuntu-latest`;
- Docker del runner;
- Supabase CLI fijada;
- Supabase local;
- Chromium real con Playwright;
- cuentas `@test.local`;
- fixtures TEST/QA;
- permisos GitHub `contents: read`;
- cero secretos productivos;
- cero artifacts subidos.

El listener Playwright bloquea conceptualmente cualquier solicitud a `*.supabase.co` o al project ref productivo. En las ejecuciones E2E no se detectó una solicitud a Supabase producción.

---

# 3. Resultado real de QA de navegador

## Configuración

Playwright:

- Chromium real.
- Mobile: 390 × 844.
- Desktop: 1440 × 900.
- Timezone: America/Argentina/Buenos_Aires.
- Locale: es-AR.
- 1 worker.
- 0 retries.
- base URL local: `http://127.0.0.1:8000`.
- Supabase API local: `http://127.0.0.1:54321`.
- Postgres local: `127.0.0.1:54322`.

La primera versión de Playwright utilizada no soportaba Ubuntu 26.04 del runner actual. Se actualizó únicamente la infraestructura QA a Playwright 1.65.0.

## Resultado final

Se intentaron 8 recorridos E2E:

- 4 mobile.
- 4 desktop.

Resultado:

- **0 aprobados.**
- **8 fallidos.**

Esto no significa que ocho funcionalidades distintas estén rotas. Los tests comparten un blocker de runtime global y algunos supuestos de automatización que también se identificaron.

La suite mantuvo el gate rojo. No se modificaron criterios para obtener un falso verde.

## Recorridos intentados

### Alumno — navegación / responsive

Intentaba comprobar:

- login real;
- Inicio;
- Entrenar;
- Nutrición;
- Progreso;
- Check-in si está visible;
- Historial visible;
- overflow horizontal.

Fallo de automatización confirmado:

el locator de `TEST ALUMNO 01` resolvía primero un `<option>` oculto. Este punto no debe contarse como bug funcional.

Además, el test registró errores JavaScript globales, por lo que el flujo no puede certificarse.

### Entrenamiento + comentario + Coach

Intentaba comprobar:

- inicio real;
- registro Kg/Reps/RIR;
- foco de inputs;
- `+ Comentario`;
- guardado;
- finalización;
- refresh;
- historial;
- Coach;
- comentario pendiente;
- deeplink;
- OK persistente.

El test quedó esperando el CTA de inicio del entrenamiento y agotó timeout.

El código estático contiene el CTA esperado, por lo que esta ausencia es compatible con la cadena de runtime parcialmente rota. Hasta corregir la integridad JavaScript no se puede certificar este recorrido.

### Nutrición

Intentaba comprobar:

- plan;
- opción del plan;
- `Registrar hoy`;
- alimentos;
- macros;
- consumido/objetivo/restante;
- fecha local;
- refresh;
- calculadora;
- personalizado;
- eliminación;
- preservación del plan.

La opción pudo ser localizada y clickeada, pero el toast de éxito quedó vacío.

Dado que también existían errores JavaScript globales, no se debe clasificar todavía como defecto aislado de `logPlanOption`. Debe repetirse después del bloque P0.

### Coach — dashboard / workspace

Intentaba comprobar:

- dashboard;
- alumno;
- workspace 360;
- Resumen;
- Rutina;
- Progreso;
- Historial;
- Seguimiento;
- Nutrición;
- Agenda;
- pagos si son visibles;
- overflow.

El locator inicial del nombre del alumno sufría el mismo problema del `<option>` oculto. Es un problema de automatización.

El workspace tampoco puede certificarse por los errores runtime globales.

---

# 4. Defectos confirmados de runtime — P0

El nuevo auditor de JavaScript encontró cinco runtimes inválidos.

## v170ConsolidatedRuntime

Error:

`missing ) after argument list`

La línea afectada construye un botón `Ver progreso` con quoting incorrecto dentro de `onclick`.

## v175ProfileAgendaCoachCenterRuntime

Error:

`Invalid or unexpected token`

Existe quoting inválido en un botón que intenta navegar a Check-in.

## v244UnifiedSessionHistoryRuntime

Error:

`Unexpected token 'function'`

El artifact contiene:

`function exerciseHtmlV244  function exerciseHtmlV244(...)`

Es una duplicación sintáctica directa.

## v309GeneralBodyMeasurementsRuntime

Error:

`Unexpected token '*'`

Una condición destinada a reconocer brazo/muslo derecho contiene una expresión incompleta/no delimitada correctamente.

## v331ProfessionalAlertGroupingRuntime

Error:

`Unexpected string`

La construcción del botón OK individual contiene comillas inválidas alrededor de la llamada a `__fjzResolveGroupedAlertV336`.

## Error runtime adicional

Chromium reporta:

`ReferenceError: injectCoachAdminCardV124 is not defined`

con stack dentro del artifact local.

Los cinco archivos fuente correspondientes a esos runtimes son iguales entre `main` y V22. Por lo tanto, 0B no introdujo esos defectos.

No se ejecutó Playwright contra producción y, por seguridad, no debe hacerse. Por eso no se afirma que la experiencia productiva reproduzca exactamente todos estos errores; sí se confirma que el código fuente heredado contiene esos puntos.

---

# 5. Gaps del entorno local — no son bugs de la aplicación

El schema V22 de 0A cubre correctamente el núcleo necesario para entrenamiento, comentarios, nutrición base, Auth, RLS y Storage.

Sin embargo, el HTML productivo utiliza además tablas que todavía no existen en el schema local.

Faltan:

- `athlete_reminders`
- `athlete_schedule`
- `body_measurements`
- `coach_media_settings`
- `exercise_media`
- `fitness_recipes`
- `nutrition_habit_logs`
- `nutrition_plan_revisions`
- `nutrition_templates`
- `progress_photos`
- `weekly_checkins`

También falta en QA local la implementación equivalente de algunos RPC utilizados por módulos heredados, principalmente `get_coach_feed`.

Durante Playwright se observaron 404 locales sobre:

- `athlete_schedule`
- `athlete_reminders`
- `weekly_checkins`
- `body_measurements`
- `rpc/get_coach_feed`

Estos son **gaps del fixture/schema QA**, no defectos productivos confirmados.

La ampliación futura del schema local debe ser schema-only + datos sintéticos, nunca copia de datos reales.

---

# 6. Inventario funcional actual

| Dominio | Capacidades existentes | Estado 0B |
|---|---|---|
| Auth | login, roles Coach/Alumno, sesión persistente, perfiles vinculados | Integración API verde; browser bloqueado por runtime global |
| Entrenamiento Alumno | días, ejercicios, Kg/Reps/RIR, autosave, recuperación, finalización | Integración de sesión verde; E2E no certificada |
| Historial | sesiones, ejercicios, sets, recomendaciones, comentarios | Existe; runtime V244 inválido |
| Comentarios | comentario/molestia, inbox Coach, deeplink, ejercicio, OK | API/RLS verde; E2E no certificada |
| Rutinas | builder, ejercicios, series, repeticiones, RIR, intensificaciones | Existe; E2E profunda pendiente |
| Biblioteca | grupos, ejercicios, técnica, videos, custom exercises | Existe; schema local de media incompleto |
| Progreso | peso, medidas, fotos, comparaciones, charts | Existe; schema QA incompleto y runtime V309 inválido |
| Check-ins | sueño, estrés, energía, hambre, recuperación, adherencia, feedback | Existe; schema QA incompleto |
| Nutrición | planes, opciones, macros, calculadora, custom foods, logs | Integración API verde; E2E no certificada |
| Recetas | biblioteca de recetas | Existe; schema QA incompleto |
| Hábitos | registros nutricionales/hábitos | Existe; schema QA incompleto |
| Agenda | agenda Coach/Alumno, schedule/reminders | Existe; schema QA incompleto y V175 inválido |
| Alertas | feed, revisión, agrupación, OK, progreso real | Existe; V331 inválido y RPC QA faltante |
| Coach workspace | resumen, rutina, progreso, historial, seguimiento, nutrición | Existe; E2E no certificada |
| Pagos/admin | seguimiento administrativo/cobranzas | Existe parcialmente en capas posteriores; cobertura QA pendiente |
| Fotos/avatar | perfil y progreso | Storage base local verde; metadata progreso QA incompleta |
| Media técnica | videos por ejercicio | Storage base verde; tabla exercise_media QA pendiente |
| Realtime | snapshots/feed/media | Arquitectura presente; cobertura E2E específica pendiente |

---

# 7. Funciones que deben preservarse

V22 debe conservar como contratos de compatibilidad:

- IDs históricos de sesiones.
- Rutinas y días existentes.
- Historial de ejercicio.
- Sets y RIR históricos.
- snapshots actuales.
- recuperación de borradores.
- protección contra sesiones duplicadas.
- confirmación doble de sesión.
- comentarios ya existentes.
- estados reviewed/OK.
- planes nutricionales históricos.
- nutrition logs históricos.
- check-ins.
- medidas.
- fotos.
- agenda.
- alertas.
- datos administrativos.

La migración V22 debe ser aditiva y reversible.

No se deben renombrar/eliminar columnas o estructuras históricas en el mismo release en que se migra la UI.

---

# 8. Riesgos técnicos principales

## P0 — integridad del artifact

Hoy es posible que una auditoría estática diga OK mientras un bloque JavaScript no pueda parsearse.

La nueva regla V22 debe ser:

**ningún artifact se considera testeable ni publicable si un bloque JS falla parseo.**

## P0 — crecimiento por monkey patching

Muchas capas hacen:

- `const baseRender = render`;
- `render = function(){...}`;
- nuevas redefiniciones de `renderStudent`;
- nuevas redefiniciones de `setupRealtime`.

Esto genera orden implícito y dependencias difíciles de detectar.

## P1 — fecha UTC

`dateInputToday()` utiliza:

`new Date().toISOString().slice(0,10)`

Eso representa fecha UTC, no fecha Argentina.

Después de aproximadamente las 21:00 en Argentina puede seleccionar el día siguiente.

Es un riesgo confirmado por código y debe tener test horario específico. No fue reproducido como E2E en 0B porque el runtime quedó bloqueado antes.

## P1 — identidad exacta de comentario

`exercise_feedback` no tiene actualmente una referencia de sesión de primer nivel.

La asociación de comentarios históricos al historial utiliza ejercicio/día/proximidad temporal.

V22 debe introducir una referencia nullable/aditiva de sesión, preservando compatibilidad.

## P1 — idempotencia nutricional

`logPlanOption` protege guardados en curso, pero una segunda acción posterior puede representar un nuevo grupo de inserts.

Debe existir una identidad explícita del evento de consumo.

## P1 — carga/sincronización

La app ha necesitado varias capas de control sobre snapshots, Realtime y re-render.

V22 debe establecer una única política de sincronización por dominio.

---

# 9. Arquitectura objetivo V22

No se recomienda reemplazar toda la aplicación.

Se recomienda una migración tipo **strangler**:

la aplicación actual continúa siendo la capa de compatibilidad y, dominio por dominio, las responsabilidades se transfieren a módulos canónicos.

Estructura objetivo conceptual:

```
src/
  core/
    auth/
    router/
    state/
    sync/
    dates/
    errors/
  data/
    supabase/
    repositories/
    mappers/
  modules/
    workouts/
    programming/
    comments/
    coach/
    nutrition/
    progress/
    checkins/
    agenda/
    admin/
    media/
  ui/
    tokens/
    components/
    layouts/
    charts/
  legacy/
    compatibility/
  qa/
```

## Principios

### Un renderer canónico por dominio

No seguir envolviendo globalmente `render()`.

Cada módulo expone una función de render/controlador clara.

### Repositories de datos

La UI no debe construir consultas Supabase en decenas de lugares.

Ejemplo:

`WorkoutRepository`  
`NutritionRepository`  
`ProgressRepository`  
`AgendaRepository`

### Compatibilidad

Los repositories traducen los modelos modernos al formato histórico mientras sea necesario.

### Sync / Outbox

Cambios críticos:

1. persistencia local inmediata;
2. cola identificada;
3. envío;
4. readback;
5. confirmación;
6. retry idempotente.

### Fechas

Una única utilidad de fecha local.

Nunca usar UTC como “día del usuario”.

### Diseño

Sistema de tokens:

- colores;
- espaciado;
- radius;
- tipografía;
- alturas de controles;
- estados;
- focus;
- loading;
- success/error.

### Navegación

Una sola fuente de verdad para rutas/pestañas mobile y desktop.

---

# 10. Roadmap recomendado

## Bloque 0C — Runtime Integrity & QA Parity
**Prioridad P0**

Objetivo:

hacer que la app actual sea completamente parseable y E2E-testable antes de agregar funciones.

Trabajo autorizado futuro:

- corregir los 5 runtimes inválidos;
- resolver referencia `injectCoachAdminCardV124`;
- mantener auditor de sintaxis como gate;
- corregir únicamente selectores Playwright incorrectos;
- ampliar schema QA a schedule/reminders/checkins/measurements/photos/feed;
- fixtures sintéticos para todos esos módulos;
- repetir 8 E2E;
- agregar tests específicos para módulos restantes.

Criterio de salida:

- 0 errores de parseo;
- 0 page errors no controlados en recorridos base;
- 0 requests productivas;
- preflight verde;
- integración verde;
- E2E base verde o con fallos funcionales aislados/documentados.

## Bloque 1 — Architecture Kernel
**Prioridad P0/P1**

Sin rediseñar funciones todavía:

- introducir módulos fuente;
- repositorios;
- utilidades de fecha;
- error handling;
- sync contract;
- design tokens;
- compatibilidad legacy.

Criterio:

ninguna regresión visible y reducción medible de nuevas redefiniciones globales.

## Bloque 2 — Entrenamiento Premium
**Prioridad P1**

Secuencia:

1. flujo de sesión canónico;
2. exact session identity;
3. comentarios exactos;
4. autosave/outbox;
5. edición segura;
6. rest timer;
7. historial rápido;
8. PRs;
9. progresión;
10. supersets/dropsets/rest-pause visualmente consistentes;
11. resumen final;
12. métricas por grupo muscular.

No reemplazar historial existente.

## Bloque 3 — Coach Operations Center
**Prioridad P1**

- dashboard operativo;
- lista priorizada;
- perfil 360;
- adherencia;
- progresión;
- peso/medidas;
- comentarios;
- review center;
- agenda;
- administración;
- filtros;
- deeplinks;
- OK duradero.

Las alertas deben ser hechos verificables, no inferencias presentadas como certeza.

## Bloque 4 — Nutrición V22
**Prioridad P1**

- planned vs consumed separados;
- `Comí esta opción`;
- idempotency key;
- cantidades reales;
- edición;
- eliminación;
- macros consumidos/restantes;
- calculator/custom;
- historial;
- adherencia;
- fecha local correcta.

Nunca mutar automáticamente el plan Coach.

## Bloque 5 — Progress & Check-ins
**Prioridad P1/P2**

- peso;
- medidas;
- fotos;
- tendencias;
- períodos;
- wellness;
- dificultad;
- feedback Coach;
- historial de decisiones;
- comparador.

Todos los indicadores deben tener fuente y período explícito.

## Bloque 6 — Programming & Library
**Prioridad P2**

- ejercicios;
- técnica;
- videos;
- templates;
- duplicación;
- bloques/semanas;
- progresiones;
- swaps;
- calentamientos;
- estiramientos;
- historial de programación.

## Bloque 7 — Agenda, hábitos, comunicación y administración
**Prioridad P2**

- calendario bidireccional;
- home reminders;
- tareas;
- hábitos;
- pasos;
- comentarios;
- notificaciones internas;
- pagos.

Sin spam ni notificaciones automáticas innecesarias.

## Bloque 8 — Performance & Legacy Consolidation
**Prioridad continua**

A medida que cada dominio migra:

- retirar solo el wrapper que ya quedó reemplazado;
- comprobar referencias antes de eliminar;
- reducir scripts;
- reducir render wrappers;
- reducir queries;
- medir long tasks;
- controlar foco/scroll;
- mantener presupuestos de rendimiento.

No realizar una “limpieza masiva”.

## Bloque 9 — Release Hardening

Antes de cualquier promoción:

- integración;
- RLS;
- E2E mobile;
- E2E desktop;
- sintaxis;
- performance;
- snapshot backup;
- Storage backup;
- rollback;
- canary/staging;
- autorización explícita.

---

# 11. Matriz de calidad obligatoria por módulo

Cada bloque funcional deberá tener:

## Unit tests

Para:

- fechas;
- macros;
- progresión;
- alert rules;
- cálculos;
- mappers;
- deduplicación.

## Integration tests

Con Supabase local:

- inserts;
- updates;
- delete;
- RPC;
- idempotencia;
- readback.

## Permission tests

Coach / Alumno / Alumno ajeno.

## Browser E2E

Mobile y desktop.

## Persistence

Reload + nueva sesión del navegador donde corresponda.

## Negative tests

- doble click;
- offline/fallo;
- dato inválido;
- permiso denegado;
- registro duplicado.

## Performance

- no pérdida de foco;
- no scroll jumps;
- no loops;
- no canales duplicados;
- no render storms.

---

# 12. Criterios de UX V22

## Mobile first

El entrenamiento debe optimizarse para pulgar:

- controles grandes;
- inputs numéricos claros;
- teclado correcto;
- acciones fijas cuando sea útil;
- no cajas fuera del viewport;
- feedback de guardado inmediato;
- navegación mínima.

## Desktop Coach

Más densidad informativa sin letras diminutas:

- jerarquía;
- paneles;
- filtros;
- tablas cuando aporten;
- drill-down claro;
- acciones no ambiguas.

## Accesibilidad

- focus visible;
- labels;
- contraste;
- aria donde corresponda;
- botones semánticos;
- no depender solo de color.

---

# 13. Funciones nuevas recomendadas

Estas funciones aportan valor, pero deben implementarse solo después de estabilizar el núcleo.

## Alumno

- rest timer integrado;
- PRs claros;
- historial rápido inline;
- comparación con última sesión;
- resumen de entrenamiento;
- micro-feedback de progreso;
- estados offline/sync comprensibles.

## Coach

- “Inbox operativo” diario;
- búsqueda global;
- filtros por necesidad;
- timeline de alumno;
- comparación 7/30/90 días;
- decisiones Coach auditables;
- agenda accionable.

## Nutrición

- consumos agrupados por comida;
- idempotency key;
- adherencia simple;
- favoritos;
- últimas comidas;
- copia segura de una comida previa.

## Programación

- templates;
- copiar semana;
- mesociclos/bloques;
- cambios programados;
- swaps equivalentes;
- historial de programa.

---

# 14. Qué se puede hacer sin costo adicional

El plan V22 puede continuar con:

- GitHub;
- GitHub Actions estándar;
- Playwright;
- Chromium;
- Supabase local;
- PostgreSQL local;
- Auth local;
- Storage local;
- Realtime local;
- Python/Node tooling open source;
- infraestructura productiva existente.

No es necesario contratar:

- un segundo Supabase;
- un segundo Render;
- servicio E2E pago;
- observabilidad paga;
- plataforma de diseño paga.

Las funciones que aumenten almacenamiento/egress en producción deberán revisarse respecto de la cuota actual antes de habilitarlas masivamente, pero no requieren por diseño un proveedor nuevo.

---

# 15. Orden de desarrollo recomendado

Orden final:

1. **0C — Integridad runtime + paridad QA.**
2. **Kernel arquitectónico y sistema de diseño.**
3. **Entrenamiento + comentarios exactos.**
4. **Coach Operations Center.**
5. **Nutrición V22.**
6. **Progreso + Check-ins.**
7. **Programación + Biblioteca.**
8. **Agenda + Hábitos + Comunicación + Admin.**
9. **Consolidación de legacy y performance continua.**
10. **Release hardening y promoción controlada.**

El orden se basa en riesgo y dependencia, no solo en impacto visual.

Entrenamiento y Coach dependen del runtime y del modelo de datos central. Nutrición tiene un dominio bastante delimitado pero comparte sincronización/fechas. Progreso/agenda dependen de completar primero el schema QA.

---

# 16. Decisión de Etapa 0B

## Completado

- inventario arquitectónico;
- inventario funcional;
- Playwright configurado;
- Chromium real;
- mobile/desktop;
- Supabase local;
- detección de conexiones productivas;
- sintaxis JS auditada;
- E2E intentados;
- gaps de schema identificados;
- defectos runtime identificados;
- roadmap V22 definido.

## No aprobado como baseline verde

La línea base E2E no puede marcarse verde porque existen errores runtime heredados.

Esto es exactamente el tipo de defecto que 0B debía descubrir antes de comenzar V22.

La recomendación es autorizar un bloque **0C exclusivamente de estabilización**, sin agregar features, cuyo objetivo sea conseguir la primera baseline de navegador verde y completar el schema QA.

Solo después conviene comenzar la primera mejora funcional.
