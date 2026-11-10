# TEAM FJZ V22 — ETAPA 2B-V: REDISEÑO VISUAL PREMIUM REAL

Fecha: 2026-11-10  
Rama: `dev/team-fjz-v22`

## 1. SHA inicial y SHA técnico certificado

- Base 2B certificada: `58134a4671c7ca67e79a4e1c32e07eca03e5a511`
- SHA técnico 2B-V certificado: `e2d8357a731560c26025e6d698f14db37a7298ea`
- `main`: `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807` — intacto.
- Diferencia respecto de 2B: 19 commits por delante, 0 por detrás.

Este documento se incorpora después de la certificación técnica. El commit documental final debe volver a superar Integración y Browser sobre exactamente el mismo SHA antes del cierre formal.

## 2. Problemas visuales encontrados

La revisión de V21.41 y del 2B certificado confirmó que 2B había mejorado funcionalidad e información, pero conservaba demasiado de la composición legacy:

- hero superior demasiado parecido a V21.41;
- finalización con demasiado protagonismo temprano;
- tarjetas de ejercicios con jerarquía débil entre nombre, contexto y series;
- demasiados contenedores secuenciales;
- navegación contextual duplicada con navegación global;
- historial esencialmente listado;
- detalle de sesión demasiado vertical y documental;
- desktop basado en expansión del layout móvil;
- estados de guardado y contexto repartidos en la misma columna;
- tipografía operativa de 8–11 px en distintos componentes legacy/2B;
- comparación anterior/actual funcional pero visualmente secundaria;
- comentarios correctos pero con poca separación semántica.

## 3. Concepto visual

La dirección adoptada es **Performance Console TEAM FJZ**.

No copia Hevy, Trainerize ni Everfit. Conserva negro, rojo y grises TEAM FJZ, pero cambia la estructura:

- comando de sesión compacto;
- progreso cuantificado visible al entrar;
- numeración visual de ejercicios;
- cards con zonas de título, contexto y registro;
- series tratadas como una tabla operativa;
- técnica desplegable, no permanentemente invasiva;
- rail de contexto/guardado/finalización en desktop;
- dock de finalización separado de los inputs en mobile;
- historial como timeline de sesiones;
- detalle de sesión como revisión de performance;
- comentarios como bloques contextuales ligados al ejercicio.

El objetivo es que la interfaz se sienta construida para entrenar, no como un formulario largo.

## 4. Cambios de composición reales

### Entrenamiento

Antes:
- hero + guardado + tabs + cards legacy;
- botón finalizar dominaba el encabezado;
- inputs y referencias vivían dentro de una tarjeta extensa;
- técnica visible consumía altura;
- desktop era una versión ancha del mismo flujo.

2B-V:
- cockpit superior con progreso de sesión;
- KPIs `Ejercicios` y `Series listas`;
- progreso porcentual con barra integrada;
- ejercicio numerado `01 / 02 / ...`;
- nombre del ejercicio como elemento principal;
- estado de series por ejercicio;
- acción Comentario dentro del header del ejercicio;
- técnica convertida a disclosure `Técnica y ejecución`;
- última sesión / recomendación movidas a una zona de contexto;
- cabecera explícita `Serie | Carga | Reps | RIR`;
- inputs de carga/reps/RIR a 16–17 px y altura táctil;
- finalización movida a un dock de acción;
- desktop con feed principal + rail lateral de estado.

### Historial

Antes:
- lista de cards casi idénticas;
- poco resumen global;
- navegación secundaria duplicada.

2B-V:
- encabezado de historial con resumen;
- KPIs `Sesiones` y `Con feedback`;
- sesiones numeradas;
- badges y señales agrupados;
- CTA de apertura claramente separado;
- navegación contextual sin duplicar Inicio/Nutrición/Progreso/Entrenar.

### Detalle de sesión

Antes:
- modal largo con KPIs + ejercicios apilados.

2B-V:
- cabecera de sesión y estado confirmado jerarquizados;
- KPIs compactos de series, ejercicios, progresión y revisión;
- sección `Registro de la sesión`;
- ejercicios numerados;
- comparación previa/actual incorporada al bloque del ejercicio;
- comentarios diferenciados visualmente;
- estado pendiente/revisado y vínculo exacto legibles.

### Comentarios

- compose convertido a sheet/panel específico;
- textarea con altura operativa;
- acción principal táctil;
- Comentario y Molestia diferenciados;
- timestamp y vínculo de sesión visibles;
- comentarios continúan viviendo en el sistema existente, no se creó otra bandeja.

## 5. Componentes y tokens reutilizables

### `src/ui/design-system.css`

Tokens globales V22 reutilizables:

- surfaces;
- líneas;
- texto primario/secundario/terciario;
- rojo TEAM FJZ;
- verde/amber/blue semánticos;
- radios;
- spacing;
- altura táctil;
- escala tipográfica;
- focus ring;
- content max;
- rail desktop.

### `src/modules/workouts/visual-redesign.js`

Responsabilidades de composición:

- cockpit/overview;
- ejercicio;
- meta y acciones;
- series;
- contexto;
- técnica desplegable;
- finalización;
- layout desktop;
- comentario;
- historial;
- detalle de sesión;
- eliminación de navegación contextual duplicada.

Este módulo no cambia persistencia ni modelo de datos.

## 6. Comparaciones visuales reproducibles

CI genera automáticamente referencias aisladas de:

1. **V21.41** — `main@3ffcf3e...`
2. **V22 2B certificado** — `58134a46...`
3. **V22 2B-V actual**

Las tres versiones:

- se construyen contra Supabase local;
- bloquean el proyecto Supabase productivo;
- utilizan el mismo usuario ficticio;
- utilizan el mismo fixture;
- capturan los mismos estados;
- usan 390×844 y 1440×900.

Estados comparados:

- workout;
- registro de series;
- historial;
- detalle de sesión;
- comentarios;
- compose de comentario.

Se generan contact sheets `compare-*.png` con las tres versiones lado a lado.

La comparación confirma cambios estructurales y no únicamente cosméticos.

## 7. Mobile y desktop

### Mobile 360 × 800

PASS:

- workout visual;
- navegación/contexto/a11y;
- comentario táctil;
- historial/detalle;
- sin overflow horizontal;
- inputs conservan foco;
- tipografía operacional mínima 12 px en superficies rediseñadas;
- inputs numéricos >= 16 px;
- controles críticos >= 44 px.

### Mobile 390 × 844

16/16 E2E PASS, incluyendo:

- 2A draft/retry/idempotencia;
- 2B sesión/comentario exacto;
- 4 recorridos específicos 2B-V;
- nutrición;
- agenda;
- Coach workspace.

### Mobile 430 × 932

5/5 responsive visual PASS.

### Desktop 1440 × 900

16/16 E2E PASS.

Desktop no estira simplemente el layout mobile: usa feed de entrenamiento más rail lateral para estado, cambios pendientes y finalización.

## 8. Accesibilidad y legibilidad

Controles añadidos/reforzados:

- focus-visible;
- inputs de registro >= 16 px;
- target táctil >= 44 px;
- dock principal >= 48 px;
- textarea de comentario >= 120 px;
- nombres de ejercicio >= 18 px;
- comentarios >= 12 px;
- KPI labels >= 12 px;
- contextual copy >= 12 px;
- no quedan reglas nuevas de 8, 9 o 10 px en los CSS de 2B-V;
- el piso final de etiquetas operativas se elevó de 11 a 12 px;
- ausencia de scroll horizontal involuntario en 360/390/430/1440;
- navegación contextual duplicada oculta y retirada del tab order;
- inputs mantienen foco después de escribir.

## 9. Integración y Playwright

Certificación técnica sobre:

`e2d8357a731560c26025e6d698f14db37a7298ea`

Integración:

https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42867231551

Browser:

https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42867231574

### Integración

SUCCESS:

- unit/contract tests;
- negative isolation;
- Supabase local real;
- AgendaRepository;
- CommentRepository;
- contrato 2B session/comment;
- build;
- architecture inventory;
- preflight;
- recreate DB;
- repetición de contratos;
- cross-student isolation;
- same-day session isolation;
- post-confirmation exact comment;
- project-scoped shutdown.

### Browser

- mobile 390: 16 PASS;
- mobile 360: 6 PASS;
- mobile 430: 5 PASS;
- desktop 1440: 16 PASS;
- syntax: SUCCESS;
- final isolation gate: SUCCESS;
- visual references: SUCCESS;
- contact sheets: SUCCESS.

## 10. Regresiones encontradas y corregidas durante 2B-V

Los 19 commits 2B-V incluyen correcciones graduales encontradas por screenshots y QA:

- integridad visual del header;
- geometría accesible de inputs;
- referencias visuales V21.41/2B reproducibles;
- validación de URLs Supabase locales;
- composición de performance console;
- detalle de sesión;
- técnica real del ejercicio;
- copy contextual demasiado pequeño;
- desktop composition;
- navegación global/contextual duplicada;
- labels operativas de 10 px;
- overflow específico en 360 px;
- cockpit mobile;
- persistencia de deduplicación después de rerenders legacy;
- rail desktop de sesión;
- piso tipográfico final 12 px.

No se debilitó ningún gate para obtener verde.

## 11. Topología y arquitectura

La topología runtime crítica permanece estable:

- render assignments: 18;
- channels: 2;
- timeouts: 56;
- listeners: 51;
- MutationObservers: 3.

No se añadió:

- canal Realtime;
- timer;
- observer;
- listener global;
- sistema de persistencia paralelo;
- nueva cadena de monkey patches;
- nueva etapa funcional.

El rediseño se conecta a través del bridge V22 existente y de módulos fuente.

## 12. Archivos principales

- `src/modules/workouts/visual-redesign.js`
- `src/modules/workouts/premium-workout.js`
- `src/ui/design-system.css`
- `src/ui/premium-workout.css`
- `src/ui/premium-history.css`
- `v344_v22_2a_premium_workout.py`
- `tests/e2e/v22-baseline.spec.js`
- `scripts/dev_build_visual_reference.py`
- `scripts/capture_visual_reference.js`
- `scripts/build_visual_contact_sheets.js`
- `.github/workflows/v22-browser-baseline.yml`

## 13. Funcionalidad preservada

PASS y sin sustitución de autoridades:

- V207 guardado confirmado;
- V340/V341 recovery;
- identidad estable de sesión;
- `exercise_feedback.session_id`;
- CommentRepository;
- AgendaRepository;
- comentarios históricos;
- OK/revisión Coach;
- valores decimales;
- input focus;
- sesiones incompletas;
- retry;
- doble finalización;
- idempotencia;
- RLS;
- Auth;
- historial exacto.

## 14. Producción intacta

Durante 2B-V:

- no se modificó `main`;
- no hubo deploy Render;
- no hubo migración productiva;
- no se modificó Supabase producción;
- no se utilizaron alumnos reales;
- no se agregaron servicios pagos;
- no se inició Etapa 2C;
- no se rediseñaron Nutrición, Progreso, Check-ins, Agenda o Biblioteca.

## 15. Estado de aprobación visual

**Estado técnico de 2B-V: CERTIFICADO.**

**Estado visual: PENDIENTE DE APROBACIÓN DEL COACH/PRODUCT OWNER.**

La existencia de CI verde no se considera aprobación estética.

Los contact sheets y screenshots son la evidencia para la revisión humana final.

Si la dirección visual es aprobada, estos tokens y componentes podrán convertirse en la base del futuro rediseño de otros módulos. Si no es aprobada, 2B-V permanece como una iteración visual revisable sin afectar producción.

**Etapa 2C: NO INICIADA.**
