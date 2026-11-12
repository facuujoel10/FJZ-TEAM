# TEAM FJZ V22 — Etapa 3A Coach Command Center

## Estado
Implementación iniciada desde la base certificada `5ad73468ba958620c2e69a7ede4c0a7fde2628ea`. Este documento se completa con los SHAs y enlaces de GitHub Actions al cierre técnico.

## Base y límites
- Rama exclusiva: `dev/team-fjz-v22`.
- Producción: `main` permanece en `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`.
- Sin deploy de Render, migraciones productivas, cambios de Auth/RLS productivos ni datos reales.
- V207, V340/V341 e identidad canónica de sesiones permanecen intactos.
- No se introduce un sistema persistente paralelo de alertas.

## Diagnóstico anterior
El Panel Coach previo reunía capacidades maduras pero dispersas: feed operativo, Review Center, comentarios, agenda, prioridades y agrupación por alumno coexistían en varias capas históricas. El problema principal era de composición y semántica: demasiadas superficies competían por la atención y el dashboard de escritorio seguía heredando una estructura lineal.

## Diseño y navegación 3A
Desktop: sidebar operativa, área de revisiones, rail de agenda y lista de alumnos. Mobile: composición específica, filtros desplazables, botones táctiles y navegación compacta. La jerarquía pone primero qué requiere atención y por qué.

## Arquitectura de eventos y estados
`src/modules/coach/command-center.js` es una capa de presentación. Consume `loadCoachFeed`, `CommentRepository`, `AgendaRepository` y el motor 2C. Reemplaza únicamente `renderCoachDashboardV80`; no agrega wrappers globales de `render`, listeners Realtime ni nuevas suscripciones.

## Persistencia y semántica de OK
Abrir no equivale a resolver. El OK delega en las autoridades existentes (`__fjzResolveGroupedAlertV336` y `__fjzAckTrainingCommentV329`), espera confirmación y vuelve a hidratar. Ante error no elimina optimistamente la revisión.

## Comentarios y sesiones
Los comentarios se leen desde `CommentRepository`; mantienen `session_id`, `exercise_uid` e ID de feedback. La apertura reutiliza el deep-link V328 y el foco exacto V329.

## Agenda
Las fechas se leen mediante `AgendaRepository`, con zona `America/Argentina/Buenos_Aires`, deduplicación por ID y acceso al alumno/agenda existente.

## Primera revisión
Se mantiene V327: ausencia de baseline no genera `Primera revisión`. 3A no reintroduce esa señal.

## QA
Se agregaron pruebas unitarias de deduplicación/agrupación/categorías y E2E para dashboard, búsqueda, comentario exacto, motor 2C, RLS, loading y falso OK. Browser QA genera evidencia en `artifacts/3a/`.

## Pendiente de cierre
Completar SHA final, Actions de Integración/Browser, capturas comparativas, topología antes/después, limitaciones y confirmación final de producción intacta después de certificar ambos workflows sobre el mismo SHA.
