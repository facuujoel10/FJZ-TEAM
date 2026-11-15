# TEAM FJZ V22 — ETAPA 4B · Progreso Físico y Check-ins Premium

## Estado
Etapa implementada exclusivamente en `dev/team-fjz-v22`. Base certificada: `e80cfff6de34aff6a52b4bdc9f60468c201e3eef`. Producción debe permanecer en `main@3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`.

El SHA final de certificación es el HEAD de esta rama que contiene este informe; el cierre externo de etapa registra el SHA exacto y los dos workflows correspondientes, ya que un documento no puede contener criptográficamente el SHA del propio commit que lo contiene.

## Diagnóstico previo
La experiencia heredada mezclaba check-in, medidas y fotos en una sucesión larga de tarjetas, con baja jerarquía mobile. El Coach veía seguimiento correcto pero visualmente denso. No era necesario crear nuevas autoridades: el runtime certificado ya tenía persistencia, aislamiento, edición y guardas de integridad.

## Autoridades de datos verificadas
- `weekly_checkins`: check-ins, escalas originales, comentario del alumno, `coach_feedback`, `submitted_at` y `reviewed_at`.
- `body_measurements`: peso, cintura, abdomen, cadera, pecho, brazos, muslos, notas y fecha.
- `progress_photos`: metadata de fecha/pose/storage.
- Storage privado: bucket `progress-photos`, sin cambio de rutas o políticas.
- `trackingCache` + `loadTracking`: autoridad de hidratación existente.
- `v303_save_integrity.py`: write/read-back del check-in y guard anti-doble toque.
- `v304_global_save_integrity.py`: confirmación de mediciones/fotos y compensación de carga de imágenes.
- `v305_checkin_resubmission_lifecycle.py`: semántica pendiente/revisado tras reenvío.
- Athlete 360 3B y Analytics 3C siguen leyendo estas mismas autoridades.

## Arquitectura 4B
Se agregó una capa acotada:
- `src/modules/tracking/progress-checkins-premium.js`
- `src/ui/progress-checkins-premium.css`
- `v350_v22_4b_progress_checkins_premium.py`

No existe nueva tabla, migración, fuente de verdad, canal Realtime, timer, observer ni wrapper global de `render`. El módulo reemplaza únicamente el render acotado de seguimiento del alumno y se integra a Progreso/Check-ins de Athlete 360 mediante el hook certificado de hidratación.

## Progreso Físico Premium
- Hero compacto con último peso y fecha.
- Variaciones neutrales, sin etiquetar subida/bajada como mejora.
- Gráfico de peso sólo con datos suficientes.
- Historial de medidas con ausencia representada como ausencia, nunca cero.
- Alta mobile de peso/cintura/abdomen/cadera/pecho/brazo/muslo con unidades explícitas.
- Read-back de la medición antes de confirmar guardado.
- Edición histórica existente preservada.
- Fotografías agrupadas por fecha y vista (frente/perfil/espalda), con faltantes explícitos y ampliación.
- Upload conserva `progress-photos` y la transacción/compensación existente.

## Check-ins Premium
- Formulario reestructurado en grupos lógicos: Estado físico, Sensaciones, Adherencia/Evolución y Comentarios.
- Conserva las escalas existentes: sueño, recuperación, hambre, estrés, energía, ánimo, motivación y adherencia.
- No se agrega dificultad clínica, score global ni promedio entre escalas.
- Mantiene semana, peso opcional y notas.
- El texto `Check-in guardado correctamente.` aparece sólo después del flujo confirmado del servidor.
- El anti-doble toque permanece delegado al `checkinPromise` certificado.
- Historial separa comentario del alumno de devolución del Coach y muestra estado de revisión persistente.

## Coach / Athlete 360 / 3C
Progreso y Check-ins se presentan dentro del mismo Athlete 360. No se agrega navegación global ni otro perfil. Las rutas de 3C siguen apuntando a los IDs fuente mediante `data-measurement` y `data-checkin`; el hook 4B encadena el hook anterior en vez de sustituirlo.

## Compatibilidad histórica
No se eliminan ni migran registros. Los campos históricos de brazo/muslo izquierdo/derecho siguen legibles; la presentación general reutiliza el valor disponible según el contrato heredado. Fotos históricas no se comprimen, mueven o transforman.

## Seguridad y RLS
No se modifica Auth/RLS. El smoke local `scripts/dev_progress_checkins_4b_rls_smoke.py` verifica aislamiento A/B para medidas, check-ins y metadata de fotos con usuarios sintéticos. Producción no participa en QA.

## QA
Se agregaron:
- `tests/unit/v22-progress-checkins-premium.test.js`
- `tests/e2e/v22-progress-checkins-premium.spec.js`
- `scripts/dev_progress_checkins_4b_rls_smoke.py`
- captura `scripts/capture_4b_progress_checkins.js`

El browser workflow ejecuta 4B en 360×800, 390×844, 430×932 y 1440×900, con control de overflow. La integración mantiene la suite heredada y añade el contrato RLS 4B.

## Evidencia visual
El workflow construye tres referencias aisladas contra Supabase local:
1. V21.41.
2. V22 pre-4B exacta: `e80cfff6de34aff6a52b4bdc9f60468c201e3eef`.
3. V22 4B.

Artifact esperado: `v22-4b-progress-checkins-premium-screens`, con viewport/full-page de Alumno y Coach.

## Rendimiento y topología
4B no añade polling, Realtime, MutationObserver, PerformanceObserver ni intervalos. Las imágenes siguen usando URLs firmadas y sólo se hidratan en la vista de progreso.

## Riesgos pendientes
La aprobación estética final está reservada al Product Owner sobre las capturas. No se inicia 4C.

## GitHub Actions
Los enlaces exactos de Integración y Browser se asocian al SHA final en el cierre de la etapa. Ambos deben terminar SUCCESS sobre el mismo HEAD antes de declarar 4B técnicamente cerrada.

## Producción
`main`, Render y Supabase productivo no deben modificarse durante 4B.
