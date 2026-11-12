# TEAM FJZ V22 — Etapa 3A Coach Command Center

## 1. Base, alcance y certificación

- Rama exclusiva: `dev/team-fjz-v22`.
- SHA base certificada solicitada: `5ad73468ba958620c2e69a7ede4c0a7fde2628ea`.
- Al iniciar la auditoría la rama ya estaba 9 commits por delante, en `5f0b1de7843a37860ee9f99a88b68ea6470dae4a`; esos commits correspondían a trabajo 3A ya iniciado y fueron preservados/auditados, no sobrescritos.
- Producción: `main` permanece fijado en `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`.
- El SHA final técnico es el HEAD que contiene este informe y debe coincidir con los dos runs SUCCESS indicados en la certificación final entregada al usuario.
- No se realizó deploy de Render, merge a `main`, migración productiva, cambio de Auth/RLS productivo, ni uso de datos reales.

## 2. Diagnóstico del Panel Coach anterior

El Panel Coach previo reunía capacidades maduras pero dispersas: feed operativo, Review Center, comentarios, agenda, prioridades y agrupación por alumno coexistían en varias capas históricas. El principal problema era de composición y semántica: demasiadas superficies competían por la atención, el escritorio heredaba una estructura lineal y el Coach debía recorrer contenedores diferentes para responder una pregunta simple: “¿quién necesita mi atención y por qué?”.

3A no elimina esas autoridades. Las consolida en una superficie operativa nueva y acotada.

## 3. Diseño y navegación nuevos

### Desktop
- Sidebar Coach persistente dentro del dashboard.
- Área principal dedicada a actividad/revisiones.
- Resumen operativo reducido a señales accionables.
- Rail de próximos seguimientos.
- Lista de alumnos con búsqueda y estado pendiente.
- Uso real del ancho de 1440 px, evitando una columna móvil estirada.

### Mobile
- Sidebar desktop retirada.
- Navegación inferior específica del Command Center.
- Filtros desplazables.
- Grupos compactos por alumno.
- Acciones táctiles de 44 px o más.
- Sin tablas ni overflow horizontal.
- Breakpoints verificados en 360×800, 390×844 y 430×932.

## 4. Funciones implementadas

- Bandeja operativa unificada por alumno.
- Categorías: Entrenamientos, Comentarios, Check-ins, Progreso físico, Agenda y otras revisiones legítimas.
- Deduplicación por identidad canónica del evento y agrupación estable por `studentId` canónico cuando existe mapeo.
- Apertura de perfil/alumno y origen exacto cuando existe vínculo confiable.
- Búsqueda operativa de alumnos.
- Próximas fechas mediante `AgendaRepository`.
- Comentarios mediante `CommentRepository`.
- Deep-link a sesión/ejercicio usando las autoridades V328/V329 existentes.
- Reutilización del motor 2C para comparaciones de rendimiento.
- Estados de carga, vacío, error/reintento y sincronización visible.

## 5. Arquitectura de eventos y estados

`src/modules/coach/command-center.js` es una capa de presentación/coordination. Consume las autoridades existentes y publica únicamente `__fjzRenderCoachCommandCenterV22` como autoridad visual de 3A. El bridge `v346_v22_3a_coach_command_center.py` expone de forma acotada el contexto léxico que la app base mantiene privado (`currentProfile`, `coachTab`, `state`, `cloudAthletes` y `supabaseClient`) y modifica sólo el dispatcher Coach activo de V170: cuando `coachTab==='dashboard'` delega en 3A y, fuera de ese caso, conserva `renderCoachDashboardV170` / `baseRenderCoachV170`. No se agrega un wrapper global de `render` ni se duplica estado. Mientras `.fjz3a-command-center` está montado, CSS oculta únicamente los hijos directos legacy que V324–V339 puedan volver a insertar en `#view`; no se eliminan esas autoridades y vuelven a estar disponibles fuera del dashboard 3A.

No agrega:
- otro feed persistente;
- otro sistema de alertas;
- nuevos listeners globales;
- nuevas suscripciones Realtime;
- nuevos MutationObservers;
- wrappers globales de `render`.

Topología certificada esperada del artefacto V22:
- render assignments: 18
- Realtime channels: 2
- timeouts: 57
- intervals: 0
- listeners: 51
- MutationObservers: 3

El guard `scripts/v22_architecture_inventory.py --check` exige que 3A mantenga exactamente esos valores y un único bridge adicional `v346_v22_3a_coach_command_center.py`.

### Estados
La UI diferencia:
- Nuevo.
- Visto/informativo.
- Pendiente de acción.
- Revisado/OK confirmado.

Abrir una novedad no equivale a resolverla.

## 6. Persistencia y semántica de OK

El Command Center no inventa persistencia nueva. El OK delega en las autoridades existentes:
- `__fjzResolveGroupedAlertV336` para alertas/eventos.
- `__fjzAckTrainingCommentV329` para comentarios exactos.

Flujo:
1. Identifica la identidad exacta.
2. Deshabilita temporalmente el control.
3. Ejecuta la escritura existente.
4. Exige confirmación.
5. Rehidrata desde servidor.
6. Sólo entonces el elemento deja pendientes.

Si la escritura devuelve `false`, `null` o lanza error, no se retira el evento ni se muestra un éxito falso.

Los reintentos conservan la identidad canónica y dependen de las escrituras idempotentes ya endurecidas en V336/V329.

## 7. Integración con comentarios y sesiones

Los comentarios se leen mediante `CommentRepository` y conservan:
- `athlete_id`;
- `student_id` cuando existe mapeo;
- `session_id`;
- `exercise_uid`;
- ID exacto de feedback;
- tipo comentario/molestia.

Cuando esos vínculos existen, la apertura reutiliza el deep-link V328 y el foco exacto V329. No se infieren asociaciones exactas para históricos ambiguos.

Si el feed heredado y `CommentRepository` describen el mismo comentario pendiente, 3A prioriza el registro exacto del repositorio (mensaje, `session_id`, `exercise_uid` e ID de feedback) y descarta sólo el duplicado del feed. De esta forma un repaint posterior no puede reemplazar el comentario exacto por una señal genérica.

## 8. Rendimiento inteligente

3A no recalcula récords. Reutiliza `TeamFJZIntelligentTraining` de 2C y muestra comparaciones concretas sólo cuando la fuente trae metadatos comparables. Se evita introducir porcentajes fabricados o reinterpretar una caída de volumen como mejora.

La suite mantiene un caso real de comparación 80 kg × 10 → 82.5 kg × 10 y exige que 2C siga siendo la autoridad.

## 9. Primera revisión

La autoridad V327 permanece intacta: la ausencia de baseline no genera por sí sola “Primera revisión”. El bridge 3A contiene un guard que impide reintroducir esa copia y no crea un disparador alternativo.

## 10. Agenda

Las próximas fechas se cargan mediante `AgendaRepository` para los atletas accesibles al Coach actual.

Reglas:
- zona `America/Argentina/Buenos_Aires`;
- recordatorios pasados excluidos;
- horarios compactos;
- deduplicación por ID;
- acceso al alumno/agenda existente;
- errores parciales no inventan eventos.

No se reconstruyó Agenda ni se agregó una sincronización global.

## 11. Pruebas Auth/RLS y QA

Se preservan las suites certificadas previas y se agregan:
- unit tests de identidad/deduplicación;
- agrupación que nunca mezcla alumnos;
- categorías operativas;
- E2E de dashboard responsive;
- búsqueda de alumnos;
- vínculo comentario → sesión/ejercicio;
- autoridad 2C;
- restricción de Command Center para alumno;
- lectura RLS acotada;
- ausencia de loading permanente;
- ausencia de falso OK.

La suite base ya cubre adicionalmente persistencia real del comentario revisado tras refresh y navegación con Supabase local. El baseline heredado fue adaptado para validar la representación agrupada de comentarios de 3A y la nueva acción de Agenda sin eliminar la compatibilidad con las rutas previas; no se relajó la comprobación del comentario exacto ni de la navegación real. Los E2E 3A verifican además que, una vez montado el Command Center, no quede visible ningún panel legacy hermano dentro de `#view`.

Todos los datos son fixtures `test.local` / nombres `TEST ...`.

## 12. Capturas comparativas y evidencia

El workflow Browser conserva las capturas históricas ya certificadas y agrega evidencia específica 3A en:
- `artifacts/3a/`
- `artifacts/3a-comparison/`

La comparación específica usa:
- V21.41: `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`;
- V22 inmediatamente anterior a 3A: `5ad73468ba958620c2e69a7ede4c0a7fde2628ea`;
- V22 3A: HEAD certificado.

Se capturan:
- dashboard desktop;
- Centro de Actividades con grupo abierto;
- lista de alumnos;
- próximas fechas;
- estado vacío;
- error/reintento;
- mobile 390×844.

Los E2E adicionales cubren 360×800, 430×932 y desktop 1440×900.

## 13. Rendimiento y topología antes/después

3A agrega una sola autoridad de dashboard acotada, sin aumentar canales, listeners, intervalos ni observers respecto de la línea base V22 certificada. El inventario bloquea cualquier regresión de topología en CI.

La hidratación se realiza con `Promise.allSettled` para feed, comentarios y agenda; el feed principal es fail-closed y la UI tiene estado recuperable de error. Un token de hidratación evita que una respuesta anterior pise una lectura posterior.

## 14. Limitaciones y riesgos

- 3A moderniza el acceso a perfiles, pero no rediseña el Perfil 360; eso queda reservado para 3B.
- Agenda se presenta de forma compacta; su rediseño completo queda fuera de alcance.
- Eventos históricos sin IDs exactos conservan comportamiento compatible y no se “adivinan”.
- La capa actual todavía depende de autoridades históricas V325–V339 para persistencia/deep-link; se preservan deliberadamente para evitar una migración funcional dentro de 3A.

## 15. GitHub Actions

Los enlaces definitivos de Integración y Browser deben corresponder al mismo HEAD que contiene este informe. Se consignan en la entrega/certificación final después de que ambos concluyan SUCCESS.

## 16. Confirmación de producción intacta

Cada workflow verifica explícitamente que `main` continúe en:

`3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`

Los guards V22 bloquean referencias a Supabase productivo en el artefacto de desarrollo. No se ejecutó ningún deploy.

## 17. Alcance recomendado para 3B

3B puede abordar el Perfil 360 Coach:
- jerarquía y navegación del alumno;
- vista integrada de entrenamiento, nutrición, progreso, check-ins y agenda;
- contexto persistente al volver;
- diseño desktop/mobile coherente con 3A.

No debe iniciarse hasta aprobación visual explícita de 3A.
