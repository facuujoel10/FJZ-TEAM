# TEAM FJZ V22 — 3C-UX Final Coach Experience Polish

## Estado
Candidato de cierre UX sobre la base certificada 3C. La certificación técnica requiere Integración y Browser SUCCESS sobre el mismo SHA final. La aprobación estética continúa reservada al Product Owner.

## Base
- Rama: `dev/team-fjz-v22`
- SHA inicial 3C: `db0f7e5bd3703c73ebc9a0b0e1abe8ad3b080002`
- Producción esperada: `main = 3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`

## Problemas visuales detectados
- microtipografía de 7–10 px en contexto, KPIs y navegación;
- navegación mobile en grilla densa;
- demasiados gráficos secundarios simultáneos en check-ins;
- fechas de mediciones/check-ins no visibles junto al dato analítico;
- prioridades visuales con peso similar a contenido informativo;
- controles secundarios por debajo del objetivo táctil recomendado;
- desktop correcto pero con jerarquía de superficies todavía demasiado homogénea.

## Correcciones
- capa final `src/ui/coach-ux-final-polish.css`, exclusivamente de presentación;
- tipografía contextual elevada y jerarquizada;
- navegación mobile horizontal, táctil y sticky, sin duplicar navegación;
- decisión y pendientes con prioridad visual explícita;
- cards secundarias compactadas sin eliminar métricas;
- un gráfico principal visible en check-ins mobile y métricas secundarias sin decoración redundante;
- fechas visibles en progreso y check-ins usando los mismos registros observados;
- botones de evidencia y acciones con objetivos táctiles >= 44 px;
- Command Center armonizado sin reabrir alertas ni lifecycle.

## Preservación funcional
No se modifican cálculos, comparabilidad, PR, confirmación de sesiones, repositories, Auth/RLS, OK, agenda, nutrición, progreso ni check-ins. No se agregan listeners, Realtime channels, timers, intervals ni observers.

## QA
Se conserva la suite heredada 3C y se añade `tests/e2e/v22-coach-ux-final.spec.js` para jerarquía inicial, pendientes, navegación única, touch targets, valores exactos, fechas, gráficos, overflow, comentario exacto, cambio A/B y refresh.

Viewports obligatorios: 360×800, 390×844, 430×932 y 1440×900.

## Capturas
El workflow crea `artifacts/3c-ux-comparison` comparando el SHA 3C certificado con 3C-UX. Cada estado principal genera captura viewport y full-page, además de metadata JSON con viewport efectivo, DPR y scrollWidth.

Estados: Inicio Coach, Athlete 360 Resumen, Rendimiento, Progreso, Check-ins, comentario exacto, alumno con baja/sin prioridad y error recuperable.

Artifact esperado: `v22-3c-ux-final-polish-screens`.

## Topología
La capa 3C-UX es CSS + metadatos de presentación. El guard de arquitectura debe mantener exactamente la misma topología runtime certificada por 3C.

## Certificación final
Este documento se actualizará únicamente con el SHA final y los enlaces de los dos workflows que certifiquen ese mismo SHA. No implica aprobación estética automática.
