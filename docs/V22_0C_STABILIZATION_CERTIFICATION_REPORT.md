# TEAM FJZ V22 — Etapa 0C · Informe final de estabilización y certificación

Fecha: 2026-11-09  
Rama: `dev/team-fjz-v22`  
Producción: `main`  
Baseline productivo protegido: `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`  
SHA de implementación certificado: `4ae69ea5e32290fc96cd7c831be3f21f0108237a`

## 1. Certificación

La implementación de 0C quedó verde en el mismo SHA:

- V22 local Supabase integration — run **42560126528** — **SUCCESS**.
- V22 browser baseline — run **42560126465** — **SUCCESS**.
- Mobile 390×844 — **PASS**.
- Desktop 1440×900 — **PASS**.
- Auditoría de JavaScript generado — **PASS**.
- Explicit project preflight — **PASS**.
- Recreate DB + segundo integration smoke — **PASS**.
- Final isolation and QA gate — **PASS**.
- Cero conexiones productivas — **PASS**.
- Cero `pageerror` JavaScript no controlados — **PASS**.
- Producción modificada — **NO**.

El commit que contiene este informe es documental y debe volver a superar los mismos workflows antes de habilitar 1A.

## 2. Aislamiento

Los guards confirmaron `production references: blocked`, rechazo de `TEAM_FJZ_ENV=production`, rechazo de URL Supabase productiva, `production data copied: 0`, `Production/staging isolation guards: OK` y `forbidden_present: []`.

No hubo deploy de Render, cambios en Supabase producción ni uso de datos reales.

## 3. Bloqueos resueltos

- Se restauró la acción `Comentario` que el renderer V104 había perdido respecto de V73.
- Se corrigió un uso acotado de fecha calendario basado en UTC para evitar rollover nocturno en Argentina sin modificar timestamps históricos.
- `scripts/dev_reset.py` quedó endurecido para limpiar stacks locales, reintentar cold start, recrear la DB y repetir el smoke.
- El snapshot de `exerciseFeedback` se mueve después de aplicar la hora real del entrenamiento para no perder comentarios cerca del cambio de día.
- Se identificó V170 como dashboard Coach final visible y se estabilizaron centro de comentarios + Agenda reutilizando autoridades existentes.
- El deep-link del comentario conserva `feedbackId` y `exerciseUid`, abre la sesión exacta y enfoca el comentario del ejercicio exacto.
- El OK del comentario exige readback durable. Al confirmarse, el comentario del modal muestra **Revisado** y el OK desaparece para evitar doble confirmación.
- El E2E cierra el modal mediante su control visible y verifica que el comentario revisado no reaparezca tras refresh.

## 4. Browser E2E

Mobile:

- `E2E_FLOW_OK student-navigation mobile-390`
- `E2E_FLOW_OK workout-comment-coach mobile-390`
- `E2E_FLOW_OK nutrition mobile-390`
- `E2E_FLOW_OK coach-workspace mobile-390`

Desktop:

- `E2E_FLOW_OK student-navigation desktop-1440`
- `E2E_FLOW_OK workout-comment-coach desktop-1440`
- `E2E_FLOW_OK nutrition desktop-1440`
- `E2E_FLOW_OK coach-workspace desktop-1440`

Gate final:

- `MOBILE_OUTCOME: success`
- `DESKTOP_OUTCOME: success`
- `SYNTAX_OUTCOME: success`

La suite bloque HTTP/WebSocket productivo y exige cero 404 locales y cero `pageerror`.

## 5. Integración Supabase local

Run **42560126528**:

1. Checkout exacto V22 — PASS.
2. Baseline productivo sin cambios — PASS.
3. Docker + Supabase CLI pinneado — PASS.
4. Static development guard — PASS.
5. Negative isolation tests — PASS.
6. Supabase local + integration smoke — PASS.
7. Build contra Supabase local — PASS.
8. Explicit project preflight — PASS.
9. Recreate DB + segundo smoke — PASS.
10. Final generated-artifact isolation check — PASS.

## 6. Pruebas no reducidas

Comparando `2000957ec75324afc0aed5574b211d0c44adb376` con `4ae69ea5e32290fc96cd7c831be3f21f0108237a`:

- los workflows de browser e integración no fueron reducidos;
- `tests/e2e/v22-baseline.spec.js` quedó en **+57 / -2 líneas**;
- se agregaron aserciones para origen exacto, contenedor exacto, OK exacto, estado **Revisado**, desaparición del OK y persistencia.

No se aumentó el timeout ni se eliminó un recorrido para obtener verde.

## 7. Topología

Los audits finales se mantuvieron dentro de hard limits: 1 stylesheet consolidado, 2 canales Realtime auditados, 0 intervals y límites de listeners/observers sin nuevas violaciones. Las correcciones finales no agregaron un nuevo observer, interval ni wrapper global para resolver dashboard/Agenda.

## 8. Archivos relevantes modificados

Entre otros:

- `v104_rep_scheme.py`
- `v320_runtime_flow_cleanup.py`
- `v340_session_input_recovery.py`
- `v324_review_dashboard_hydration.py`
- `v325_training_comments_center.py`
- `v339_review_center_curtain.py`
- `v342_v22_0c_ui_authority.py`
- `v336_review_comment_hardening.py`
- `scripts/dev_reset.py`
- `tests/e2e/v22-baseline.spec.js`

No se eliminó legacy sólo por parecer antiguo.

## 9. Antes / después

| Área | Antes | Cierre 0C |
|---|---|---|
| Browser E2E | múltiples bloqueos | móvil + desktop verdes |
| Supabase local | cold start/estado heredado interferían | reset/retry/recreate certificados |
| Comentarios | renderer/snapshot/deep-link con fallos | flujo completo certificado |
| Fecha calendario | riesgo UTC nocturno | caso acotado local |
| Dashboard Coach | autoridad final ambigua | V170 identificado |
| Agenda desktop | podía desaparecer | visible y certificada |
| OK comentario | stale/bloqueaba navegación | durable + Revisado visible |
| Producción | debía quedar aislada | intacta |

## 10. Riesgos pendientes

Persisten la deuda arquitectónica de 0B: redefiniciones globales, generaciones históricas de renderers, lógica Supabase mezclada con UI, contratos de guardado distribuidos, utilidades de fecha duplicadas y dependencia de snapshots históricos. Deben migrarse progresivamente; no justifican una reescritura masiva.

## 11. Criterio de salida

0C sólo queda formalmente cerrada cuando el commit documental que contiene este informe también tenga integración SUCCESS, browser SUCCESS, mobile PASS, desktop PASS, syntax PASS, preflight PASS, aislamiento PASS, cero `pageerror` y `main` sin cambios.

Hasta entonces, **1A permanece bloqueada**.

## 12. Recomendación

Una vez certificado este commit documental, comenzar solamente **Etapa 1A — Architecture Foundation**. No avanzar automáticamente a 1B ni iniciar funcionalidades nuevas.
