# TEAM FJZ — Checkpoint V20.58 · Check-in Focus + Current Plan

Fecha: 2026-10-21  
Trabajo activo: `develop`  
Producción: `main` sin modificar

## V20.57 — Weekly Check-in Focus
- suma “Prioridad de la semana” al circuito profesional de revisión del check-in;
- mantiene “Decisión actual” y “Cómo seguimos”;
- la prioridad queda visible para el alumno;
- reutiliza `weekly_checkins.coach_feedback`, sin migraciones ni columnas nuevas;
- formato retrocompatible con devoluciones anteriores;
- el Action Hub del alumno puede destacar la prioridad semanal.

## V20.58 — Persistent Current Plan
- agrega bloque “PLAN ACTUAL” en Home del alumno;
- mantiene visible la última decisión revisada del coach aunque el alumno ya haya tocado “Entendido”;
- muestra:
  - decisión actual;
  - prioridad de la semana;
  - cómo seguimos;
  - estado Nuevo / Visto;
- acceso directo al seguimiento;
- conserva el circuito de acknowledgement existente.

## Seguridad / alcance
- no hay cambios de esquema Supabase;
- no hay cambios de datos de producción;
- no hay merge a `main`;
- `RELEASE` continúa en 20.7;
- V20.57 y V20.58 se ejecutan después del Consolidation Gate V20.56.

## Diferencia contra checkpoint V20.56
- `v257_checkin_weekly_focus.py`
- `v258_student_current_plan.py`
- `build.py` (wiring de ambos bloques)
- documentación de checkpoint.

## Estado
- desarrollo aislado en `develop`;
- producción preservada;
- listo para continuar con el próximo bloque o preparar QA funcional antes de promover a producción.
