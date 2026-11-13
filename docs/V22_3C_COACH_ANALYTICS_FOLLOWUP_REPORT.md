# TEAM FJZ V22 — Etapa 3C · Seguimiento Inteligente y Analítica Profesional del Coach

## Estado
Etapa 3C implementada en la rama aislada `dev/team-fjz-v22`. Este informe forma parte del candidato final. La certificación técnica sólo se considera cerrada cuando Integración y Browser terminan en SUCCESS sobre el mismo SHA que contiene este documento. La aprobación estética permanece reservada al Product Owner.

## 1. Base certificada
- Etapa 3B: `d3eba2b3398ae9e53c353be08295bd487d0a037b`
- Producción `main`: `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`
- Rama exclusiva: `dev/team-fjz-v22`

## 2. Alcance implementado
3C transforma datos existentes en superficies de seguimiento trazables dentro del Command Center y Athlete 360:
- evolución por ejercicio con carga, repeticiones, RIR, comparación y PR;
- historial de peso y mediciones con deltas neutrales;
- comparación cronológica de sueño, hambre, estrés, motivación, recuperación, energía, ánimo y adherencia registrada;
- priorización de pendientes verificables;
- navegación desde indicadores hacia la sesión, comentario o área histórica que contiene la evidencia;
- estados vacíos/no comparables explícitos;
- composición responsive para mobile y desktop.

## 3. Autoridades y separación de responsabilidades
No se creó un motor paralelo de rendimiento.
- `TeamFJZIntelligentTraining` conserva autoridad de sesión confirmada, series válidas, modos comparables, comparación, tendencias y PR.
- `CommentRepository` conserva autoridad del feedback canónico y del OK persistido.
- `AgendaRepository` permanece como autoridad de agenda.
- tracking existente conserva mediciones, fotografías y check-ins.
- 3C únicamente ordena cronología, presenta observaciones y enlaza evidencia.

No existe score compuesto de recuperación ni interpretación automática de peso/medidas.

## 4. Datos observados, sugerencias y decisiones
La UI diferencia:
- observación: valor fechado proveniente del registro;
- comparación: únicamente cuando la autoridad existente declara comparabilidad;
- PR: únicamente cuando `TeamFJZIntelligentTraining.personalRecords()` lo confirma;
- decisión del Coach: permanece fuera de cualquier automatismo 3C.

Los cambios corporales se describen como variaciones neutrales. No se etiqueta bajar/subir peso o medidas como progreso positivo sin contexto.

## 5. Rendimiento por ejercicio
`src/modules/coach/analytics-followup.js` construye cronologías sólo desde sesiones confirmadas. Para cada ejercicio reutiliza:
- `bestLoad()`;
- `analyzeExercise()`;
- `personalRecords()`;
- `modeOf()`.

Sesiones draft/no confirmadas quedan excluidas. Cuando falta referencia comparable aparece “Sin referencia comparable” en lugar de inferir tendencia.

## 6. Seguimiento corporal
Las mediciones se ordenan por `measured_on/created_at`. Cada métrica conserva valor, fecha y delta contra el registro anterior únicamente cuando existen dos observaciones válidas. Los gráficos se muestran sólo con dos o más puntos.

## 7. Check-ins y recuperación
Cada escala se compara por separado. No se promedian dimensiones heterogéneas y no se inventa un “readiness score”. El Coach puede leer la evolución cronológica manteniendo el significado original de cada campo.

## 8. Priorización
La prioridad del Athlete 360 se apoya en evidencia verificable:
1. molestias pendientes;
2. comentarios pendientes;
3. check-ins pendientes de revisión;
4. contexto de sesión confirmada cuando corresponde.

No se crea urgencia artificial por falta de datos.

## 9. Navegación a evidencia
- Rendimiento → sesión confirmada fuente.
- Comentario/molestia → comentario y ejercicio exactos mediante el flujo heredado 3B/V328.
- Check-in → sección histórica de check-ins.
- Medición → sección histórica de progreso.
- Command Center 3A mantiene sus deep-links de eventos y comentarios.

## 10. UX/UI
Nueva capa `src/ui/coach-analytics.css`:
- paneles compactos;
- sparklines sólo con datos suficientes;
- jerarquía visual compatible con 3A/3B;
- responsive 360/390/430 y desktop 1440;
- sin sobrecarga de KPIs ni porcentajes sin denominador.

## 11. Arquitectura/runtime
Archivos 3C:
- `src/modules/coach/analytics-followup.js`
- `src/ui/coach-analytics.css`
- `tests/unit/v22-coach-analytics.test.js`
- `tests/e2e/v22-coach-analytics.spec.js`
- `scripts/capture_3c_coach_analytics.js`
- `docs/V22_3C_COACH_ANALYTICS_FOLLOWUP_REPORT.md`

3C se conecta únicamente a hooks acotados de 3A/3B. No reemplaza `window.render`, no crea Realtime, timers, intervals ni MutationObservers nuevos. Las acciones se enlazan a hosts 3C, no a un listener global permanente.

## 12. QA
Cobertura añadida:
- sesiones confirmadas vs draft;
- comparabilidad y PR;
- peso/medidas cronológicos;
- check-ins por dimensión sin score compuesto;
- prioridad por motivo verificable;
- perfiles A/B;
- refresh con identidad preservada;
- rol alumno sin superficies Coach;
- overflow responsive;
- navegación a sesión fuente;
- regresión heredada 3B;
- Auth/RLS local heredado de Athlete 360, AgendaRepository y CommentRepository.

Los workflows ejecutan los tests 3C junto con la suite heredada.

## 13. Capturas
El Browser workflow genera `artifacts/3c-comparison` usando los mismos fixtures sintéticos y compara:
- 3B mobile 390;
- 3C mobile 390;
- 3B desktop 1440;
- 3C desktop 1440;
- Command Center;
- resumen Athlete 360;
- entrenamiento;
- progreso;
- check-ins.

Artifact esperado: `v22-3c-coach-analytics-screens`.

## 14. Seguridad
- sin datos reales;
- sin migraciones productivas;
- sin cambios Auth/RLS productivos;
- sin Render deploy;
- sin servicios pagos;
- sin merge a `main`.

## 15. Producción
El workflow conserva el guard obligatorio que exige:
`main == 3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`.

## 16. Certificación final
El SHA final es el commit que contiene este informe. Para declarar cierre técnico:
- V22 local Supabase integration: SUCCESS.
- V22 browser baseline: SUCCESS.
- ambos sobre exactamente el mismo SHA.
- artifact visual 3C generado.
- `main` sin cambios.

No se declara aprobación estética automática.
