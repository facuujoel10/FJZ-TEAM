# TEAM FJZ V22 — Etapa 3B · Athlete 360 Workspace

## Estado
Implementación en curso sobre `dev/team-fjz-v22`. Este informe se completa únicamente con resultados certificados del SHA final.

## 1. SHA inicial y final
- Base certificada 3A: `b24236d70b6bde281397fead3c20546a50c2ae3c`
- SHA final 3B: **PENDIENTE DE CERTIFICACIÓN**

## 2. Diagnóstico anterior
El perfil Coach heredado combinaba navegación V17.x/V20.x, un strip V266 y un resumen con señales genéricas. 3B conserva sus autoridades funcionales, pero reemplaza su composición visible por un workspace único, evitando métricas inferidas sin denominador confiable.

## 3. Concepto UX/UI
TEAM FJZ Athlete 360 Workspace: encabezado compacto, una navegación adaptativa, resumen centrado en decisiones y composición distinta para mobile y desktop.

## 4. Funciones y secciones
Resumen; Entrenamiento (Rutina, Historial, Rendimiento); Nutrición; Progreso físico; Check-ins; Agenda; Información y administración existente.

## 5. Arquitectura
`src/modules/coach/athlete-360.js`, `src/ui/athlete-360.css` y puente acotado `v347_v22_3b_athlete_360_workspace.py`. No se agrega wrapper global de `render`.

## 6. Datos y autoridades reutilizadas
TeamFJZIntelligentTraining, TeamFJZSessionHistory, CommentRepository, AgendaRepository, caches/autorizaciones existentes de tracking y nutrición, V207, V328/V329, V340/V341.

## 7. Compatibilidad histórica
Se preservan sesión canónica, historial, feedback histórico, edición nutricional, check-ins, medidas, fotografías, agenda y administración existentes.

## 8. Seguridad y aislamiento por alumno
Las respuestas asíncronas se aceptan sólo si coinciden studentId + athleteId + token de consulta actual. No se conserva una segunda copia permanente del alumno.

## 9. Pruebas RLS
**PENDIENTE DE RESULTADO FINAL.**

## 10. Playwright
**PENDIENTE DE RESULTADO FINAL.**

## 11. Comparaciones visuales
V21.41 vs 3A/pre-3B vs 3B: **PENDIENTE DE ARTIFACT FINAL.**

## 12. Capturas
360×800, 390×844, 430×932 y 1440×900: **PENDIENTE DE ARTIFACT FINAL.**

## 13. Rendimiento y topología
Sin Realtime nuevo, sin timers nuevos, sin MutationObserver nuevo. AgendaRepository se instancia una sola vez y conserva su TTL/inflight. Las lecturas legacy reutilizan sus caches.

## 14. Regresiones corregidas
- Progreso físico separado de Check-ins.
- Navegación heredada duplicada retirada de la superficie visible.
- Macros contenidos en geometría mobile.
- Fechas pasadas excluidas de “próxima fecha”.
- Adherencia genérica retirada del resumen 360.
- Comentarios exactos priorizados por identidad session_id + exercise_uid.

## 15. Riesgos pendientes
Se documentarán sólo después de CI y revisión de capturas.

## 16. GitHub Actions
- Integración: **PENDIENTE**
- Browser: **PENDIENTE**

## 17. Producción
`main` debe permanecer en `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`. Sin deploy Render, sin migración productiva y sin datos reales.

## 18. Recomendación para 3C
No iniciar 3C. Detenerse después de la certificación técnica 3B y esperar aprobación visual explícita del Product Owner.
