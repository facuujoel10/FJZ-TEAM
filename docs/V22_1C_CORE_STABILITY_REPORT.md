# TEAM FJZ V22 — ETAPA 1C: CORE STABILITY REPORT

Fecha de cierre técnico: 2026-11-09  
Rama exclusiva: `dev/team-fjz-v22`

## 1. SHA inicial y SHA final técnico certificado

- SHA inicial 1C: `b100ca9203abfbddabb9ca18b4d7d9ee00521163`
- SHA final técnico certificado de 1C: `e2a7f4f01cb613cce41c7f5a891721a8d1eb384a`
- Comparación: 2 commits por delante de la base 1B, 0 commits por detrás.
- `main` verificado e intacto durante el cierre: `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`

Este informe se incorpora después de la certificación técnica. El commit documental que lo contiene se recertifica con los mismos workflows antes de considerar 1C formalmente cerrada; por definición un archivo no puede predecir el SHA criptográfico del commit que lo contiene.

## 2. Diagnóstico de caché y ciclo de sesión de AgendaRepository

### Riesgo confirmado en 1B

La caché de AgendaRepository estaba limitada por `athleteId`, con agrupación de lecturas concurrentes, pero no tenía ownership explícito por identidad autenticada. El TTL corto reducía la ventana temporal pero no garantizaba aislamiento cuando:

- se cerraba sesión y se iniciaba otra en el mismo navegador;
- cambiaba la identidad autenticada;
- quedaba una solicitud de red pendiente mientras cambiaba la sesión;
- `getById` encontraba un registro previamente cacheado bajo otra identidad.

RLS seguía siendo la autoridad del backend, pero una caché cliente no debe depender de RLS para corregir datos que ya fueron leídos bajo una sesión anterior.

### Solución 1C

AgendaRepository ahora liga cada caché y lectura en vuelo a:

- `userId` autenticado;
- token/sesión actual como parte de la clave de ownership;
- una generación interna de sesión.

Al cambiar la identidad:

- se invalida la caché;
- se desacoplan lecturas en vuelo anteriores;
- una respuesta iniciada bajo una generación anterior se clasifica como `session_cancelled`;
- esa respuesta no puede repoblar la caché nueva;
- `getById` sólo inspecciona caché perteneciente al owner actual.

Se mantiene TTL corto, deduplicación de lecturas concurrentes y comportamiento fail-closed. La caché no sustituye RLS ni autorización.

## 3. Problemas confirmados y riesgos descartados

### Confirmados

1. Ownership de caché de Agenda insuficientemente explícito en 1B.
2. Riesgo de respuesta tardía después de cambio de sesión.
3. `getById` necesitaba aislamiento de caché por identidad.
4. El script QA de recuperación de puertos tenía una rama CI demasiado amplia: podía eliminar contenedores `supabase_*` ajenos si ocupaban puertos locales fijos.
5. El primer Browser run de 1C mostró un timeout acumulativo en el recorrido Coach desktop, aunque los recorridos funcionales previos ya habían pasado.

### Descartados o no reproducidos como regresión funcional

- No se detectó fuga cross-student en RLS.
- No se detectó contacto con Supabase producción.
- No se detectó cambio en `main`.
- No se detectó regresión de guardado crítico de sesiones.
- No se detectó necesidad de agregar `session_id` a comentarios.
- No se justificó caché para CommentRepository en esta etapa.
- No se justificó reemplazar la UI histórica de comentarios.
- No aumentaron renders, timers, listeners, observers, intervalos o canales Realtime en el inventario final.

## 4. Cambios implementados

### Seguridad y datos

- Nuevo `src/data/read-errors.js` con clasificación compartida de errores de lectura.
- AgendaRepository endurecido con ownership de sesión y generación.
- Invalidación explícita de caché por sesión y por atleta.
- Protección de respuestas tardías.
- `getById` protegido ante cambio de owner.
- Nuevo `src/data/comment-repository.js` exclusivamente de lectura.
- Contrato CommentRepository actualizado sin operaciones de escritura.

### QA

- Nuevos unit tests para cambio de identidad, lectura en vuelo, `getById`, invalidación y clasificación de errores.
- Nuevos unit tests de CommentRepository.
- Nuevo smoke local Auth/RLS para `exercise_feedback`.
- Repetición de contratos tras reconstrucción completa de base.
- Nuevo apagado project-scoped del stack Supabase local.
- Limpieza de Docker restringida a `team-fjz-v22-local`.
- El test Coach E2E se separó en dos recorridos con las mismas comprobaciones: workspace 360 y acceso visible a Agenda. No se eliminó cobertura ni se aumentó el timeout global.

### Documentación 1B

Se actualizó `docs/V22_1B_DATA_SYNC_FOUNDATION_REPORT.md` con el SHA y los runs certificados reales de 1B.

## 5. Contrato CommentRepository

Piloto canónico read-only:

- `listForAthlete(athleteId, options)`
- `listPending(options)`
- `getById(commentId)`

Campos preservados:

- atleta y alumno;
- `exercise_uid` y `exercise_name`;
- `workout_day_id` y `workout_day_name` cuando existen;
- tipo;
- mensaje;
- estado `pending/reviewed`;
- revisión y timestamps.

Decisiones deliberadas de 1C:

- no agrega `session_id`;
- no modifica esquema productivo;
- no modifica botón + Comentario;
- no modifica OK;
- no modifica deeplinks;
- no sustituye V73, V287, V325, V328, V329 o V336;
- no se conecta a la UI como nueva autoridad todavía;
- no incorpora caché porque no aportaba valor suficiente para este piloto.

## 6. Clasificación compartida de errores

Las lecturas canónicas distinguen:

- `network`
- `authorization`
- `not_found`
- `query`
- `integrity`
- `session_cancelled`

Un error de permisos no se transforma en una consulta vacía mediante un fallback inseguro. Los errores contienen mensaje público seguro y conservan la causa técnica sólo para capas internas.

## 7. Pruebas Auth/RLS y aislamiento entre usuarios

Con cuentas totalmente ficticias del entorno local se verificó:

1. Coach autorizado lee comentarios de alumno vinculado: PASS.
2. Alumno consulta sus comentarios permitidos: PASS.
3. Alumno A no puede leer comentarios de Alumno B: PASS.
4. Cambio de usuario invalida caché de Agenda anterior: PASS.
5. Respuesta pendiente de sesión anterior no contamina nueva sesión: PASS.
6. Comentario `reviewed` conserva estado tras refresco: PASS.
7. Comentario inexistente/RLS-hidden produce resultado controlado: PASS.
8. Permisos no activan fallback inseguro: PASS.
9. Datos históricos conservan ejercicio/día/status, incluyendo nulls históricos: PASS.
10. Recorrido actual comentario + sesión + OK Coach continúa funcionando en Playwright: PASS.

## 8. Conflictos de puertos y resiliencia QA

Supabase local usa el proyecto `team-fjz-v22-local` y puertos locales fijos, incluyendo 54322.

El análisis descartó conflicto entre jobs paralelos de GitHub Actions como causa directa, porque cada job corre en un runner aislado. El mecanismo relevante dentro de un runner es un arranque/paro parcial que deje recursos Supabase locales reteniendo puertos durante un reset posterior.

Antes de 1C existía además una recuperación CI demasiado amplia que podía borrar cualquier contenedor con prefijo `supabase_` si ocupaba esos puertos.

1C cambia el contrato:

- sólo se eliminan contenedores cuyo nombre pertenece a `team-fjz-v22-local`;
- si otro proyecto posee un puerto, el gate falla cerrado e informa el owner en vez de eliminarlo;
- al final de ambos workflows se ejecuta un shutdown project-scoped;
- la certificación final registró `Project containers running: 0`;
- reconstrucción completa y segundo smoke pasaron.

No se usa limpieza Docker global.

## 9. Comparación arquitectónica antes/después

El inventario final conserva:

- build patches: **228**
- render assignments: **18**
- Realtime channels: **2**
- timeouts: **56**
- intervals: **0**
- listeners: **51**
- MutationObservers: **3**

Nuevos contratos detectados:

- shared read errors: presente;
- AgendaRepository: presente;
- CommentRepository: presente;
- Agenda read policy: presente.

No se añadió otro patch Python al build y no creció la topología de runtime.

## 10. Resultados Playwright

### Run técnico final certificado

Browser E2E:  
https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42658668976

SHA: `e2a7f4f01cb613cce41c7f5a891721a8d1eb384a`

Mobile 390×844:

- 6/6 PASS
- student navigation
- workout + comment + Coach review
- nutrition
- AgendaRepository
- Coach workspace
- Coach Agenda

Desktop 1440×900:

- 6/6 PASS
- mismos seis recorridos
- `MOBILE_OUTCOME: success`
- `DESKTOP_OUTCOME: success`
- `SYNTAX_OUTCOME: success`

### Incidente intermedio

Run Browser anterior:  
https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42657536309

Mobile pasó. Desktop llegó a completar los recorridos funcionales principales, pero el test combinado Coach agotó el timeout de 45 s. Se mantuvieron todas las comprobaciones y se separó el recorrido Coach en workspace y Agenda, agregando checkpoints y límites explícitos de interacción. La nueva ejecución pasó 6/6 tanto mobile como desktop.

## 11. Resultados Supabase local

Integración final:  
https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42658669013

SHA: `e2a7f4f01cb613cce41c7f5a891721a8d1eb384a`

PASS:

- guard de rama/producción;
- tests unitarios y contractuales;
- negative isolation;
- Supabase local;
- Auth/RLS;
- Storage y smoke existentes;
- AgendaRepository;
- CommentRepository;
- build;
- inventario arquitectónico;
- preflight;
- reconstrucción completa de base;
- segundo smoke;
- repetición Agenda RLS;
- repetición Comment RLS;
- aislamiento final;
- shutdown project-scoped.

## 12. URLs de GitHub Actions correspondientes al SHA final técnico

- Integración: https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42658669013
- Browser: https://github.com/facuujoel10/FJZ-TEAM/actions/runs/42658668976

Ambas finalizaron SUCCESS sobre exactamente `e2a7f4f01cb613cce41c7f5a891721a8d1eb384a`.

## 13. Confirmación de producción intacta

Durante los workflows se exigió:

- rama exacta `dev/team-fjz-v22`;
- `main` en `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`;
- bloqueo de referencias productivas;
- fixtures exclusivamente ficticios;
- ninguna solicitud HTTP/WebSocket del navegador a Supabase productivo.

No hubo:

- deploy de Render;
- migración productiva;
- modificación de Supabase producción;
- merge a `main`;
- datos reales de alumnos.

## 14. Riesgos pendientes

- CommentRepository queda deliberadamente desacoplado de la UI hasta que una etapa funcional necesite migrar una lectura concreta con evidencia E2E.
- El esquema histórico de comentarios no tiene `session_id`; 1C preserva el contrato existente en lugar de inventar esa relación.
- El runtime heredado continúa siendo voluminoso aunque la topología quedó congelada; su reducción debe hacerse por dominios durante etapas funcionales, no como otra preparación indefinida.
- Los puertos locales de Supabase siguen siendo fijos; ahora el comportamiento ante colisión es project-scoped y fail-closed, no destructivo.

## 15. Recomendación de inicio para Entrenamientos Premium

El núcleo V22 queda técnicamente preparado para pasar a cambios funcionales visibles.

La siguiente etapa debería comenzar directamente por **Entrenamientos Premium**, manteniendo:

- repositorios como límites de datos;
- guardados críticos sin regresión;
- feedback/comentarios existentes funcionales;
- integración local + Auth/RLS;
- Playwright mobile y desktop en cada bloque.

Recomendación concreta de inicio: modernizar primero la experiencia visible de sesión del alumno —jerarquía del día, ejercicio, series, carga/reps/RIR, recomendado/anterior, comentario contextual y finalización— con cambios incrementales y E2E desde el primer commit.

**Estado técnico 1C: CERTIFICADO.**  
**Etapa 2: NO INICIADA.**  
**Producción: INTACTA.**
