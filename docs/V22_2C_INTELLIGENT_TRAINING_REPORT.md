# TEAM FJZ V22 — ETAPA 2C · INTELLIGENT TRAINING REPORT

## 1. Alcance y trazabilidad

Etapa: 2C — Entrenamiento inteligente, descansos, récords y progresión.

Rama exclusiva: `dev/team-fjz-v22`.

Base técnica aprobada 2B-V2: `586fedd08b81b1599b649c0becf76af44ee8f115`.

SHA recibido al iniciar el cierre/estabilización: `dd98c9031d77df4ac6f2d37c52c7c7cd92e88884`.

SHA de implementación funcional congelada antes del cierre documental: `c1924563dc965521075cfadaef0f332d151ac06c`.

El SHA final de certificación es el commit que contiene este informe y debe coincidir exactamente con los runs finales de **V22 local Supabase integration** y **V22 browser baseline**. Su valor y los enlaces directos a los runs se publican en la entrega de certificación asociada a este documento.

No se autorizó ni se realizó merge, deploy, migración productiva ni inicio de Etapa 3.

## 2. Problemas encontrados durante el cierre

### 2.1 Infraestructura de GitHub Actions

El Browser run `43052001623` no llegó a ejecutar Playwright funcional. El runner falló durante `npx playwright install --with-deps chromium` por errores DNS al resolver mirrors de Ubuntu.

La causa se confirmó como externa/transitoria: ejecuciones posteriores instalaron Chromium y dependencias correctamente sin retirar `--with-deps`, sin ocultar errores y sin reducir cobertura.

### 2.2 Historial y Coach sin `.v22c-performance-note`

El run funcional anterior `43007674834` mostró que los recorridos de QA podían abrir una sesión distinta de la fixture comparable porque seleccionaban la primera tarjeta del historial.

Se corrigió la identidad del recorrido:
- cada fila V2C de historial expone `data-session-id` con el ID real de la sesión;
- QA abre exactamente `qa-2c-history-b` y `qa-2c-coach-b`;
- V345 calcula el análisis a partir del alumno actualmente seleccionado y de `student().sessions`;
- `exerciseUid` debe coincidir exactamente;
- la modalidad debe ser compatible;
- la sesión actual y la referencia histórica deben ser confirmables;
- si existe referencia válida se presenta `Progreso verificable`;
- si no existe, se presenta `Sin referencia comparable` con la razón calculada por el motor.

La comparación visual heredada de 2B sólo se muestra si su `previousSessionId` coincide con la referencia confirmada seleccionada por 2C. Así se evita que dos motores muestren referencias diferentes.

### 2.3 Patcher V345

Durante el cierre se detectó un fallo fail-fast del build: una edición había alterado el texto que V345 utiliza como anclaje antes de insertar la lógica 2C. También faltaba aplicar una sustitución ya validada para colocar `intelligentHtmlV2C`.

Se corrigió el patcher conservando sus guards de cardinalidad. En una segunda pasada, el auditor de JavaScript detectó que una sustitución parcial había dejado el cuerpo de la ternaria legacy duplicado (`Unexpected token '?'`). V345 pasó a sustituir atómicamente la asignación completa `comparisonHtmlV2B`; el build y el syntax audit validan el resultado generado. Si el HTML upstream deja de coincidir, el build vuelve a fallar explícitamente en lugar de producir una interfaz parcialmente integrada.

### 2.4 Modalidad bodyweight-added

Una prueba negativa descubrió que la cadena literal `bodyweight-added` podía clasificarse como peso corporal simple.

El normalizador ahora diferencia explícitamente:
- `external`;
- `bodyweight`;
- `bodyweight-added`;
- `assisted`.

Un set con lastre requiere carga positiva. Un ejercicio de peso corporal puro puede usar carga cero sin convertirse en ejercicio con lastre.

### 2.5 Valores vacíos

La normalización numérica anterior podía convertir una cadena vacía en cero.

Ahora:
- vacío => dato ausente;
- repeticiones vacías o <= 0 => set inválido;
- carga vacía => inválida para carga externa, asistencia y lastre;
- sólo peso corporal explícito puede normalizar carga vacía a 0.

### 2.6 KPIs de detalle en Historial/Coach

La revisión visual final detectó una incompatibilidad histórica adicional: algunas sesiones con `exerciseResults` válidos no conservan `session.summary.totalSets` ni `completedExercises`. V244 mostraba por eso `0 series / 0 ejercicios` aunque el registro detallado inferior sí tuviera datos.

Se corrigió sin crear una nueva fuente de verdad:
- si el resumen histórico contiene contadores positivos, se conservan;
- si esos contadores no existen o llegan vacíos, la UI deriva exclusivamente los KPIs de presentación desde `exerciseResults`;
- la analítica 2C de récords/progresión sigue usando `workSets()` y sus reglas estrictas, no estos contadores visuales;
- Playwright exige ahora coherencia entre el detalle y los KPIs tanto en Historial Alumno como en Coach.


## 3. Temporizador profesional de descanso

El temporizador es una única autoridad de módulo.

Propiedades:
- inicio explícito mediante `data-rest-action="start"`;
- pausa;
- reanudación;
- reinicio;
- omisión;
- duración del Coach cuando existe;
- duración personal configurable cuando no existe prescripción;
- no se infiere “serie completada” sólo porque exista un peso;
- no emite sonidos ni notificaciones externas.

### Reloj

No acumula segundos mediante intervalos.

Al iniciar:
`targetAt = Date.now() + durationMs`

Tiempo restante:
`remainingMs = max(0, targetAt - Date.now())`

Esto permite recalcular el estado al regresar de background o después de una demora del navegador.

Topología:
- 0 `setInterval`;
- un único `setTimeout` autocancelable del motor 2C;
- `timerCount()` verifica que no existan tickers duplicados.

El estado se guarda por `sessionId` en localStorage. Al cambiar de sesión, la autoridad en memoria se descarta antes de restaurar la nueva sesión, impidiendo que un descanso de otro entrenamiento continúe gobernando la UI actual.

Se respeta `prefers-reduced-motion`.

## 4. Autoridad de confirmación

2C no considera un simple `status: "completed"` como evidencia suficiente de confirmación en servidor.

`sessionConfirmed()` acepta una sesión únicamente cuando existe evidencia verificable mediante alguna de estas autoridades:
- el `confirmedSessionId` exacto entregado por el flujo V207;
- un ID marcado en la autoridad de ejecución después de confirmación V207;
- `cloudConfirmed === true`;
- `confirmed === true`;
- identidad de sesión de origen persistida (`source_session_id` / `sourceSessionId`) cuando está disponible.

V207 sigue siendo la autoridad de éxito terminal. El resumen 2C se construye únicamente después de que V207 recibe confirmación de nube.

## 5. Series comparables

`workSets()` excluye datos no aptos para récords/progresión:
- sets incompletos;
- reps ausentes o <= 0;
- carga inválida para la modalidad;
- calentamientos cuando el modelo los identifica;
- dropsets;
- rest-pause;
- intensificaciones no comparables;
- sets marcados explícitamente como incompletos.

No se persisten métricas derivadas nuevas. Los resultados se calculan a partir de sesiones y `exerciseResults`.

## 6. Identidad y modalidad

La comparación requiere:
1. mismo `exerciseUid`;
2. sesión actual confirmada;
3. sesión previa confirmada;
4. modalidad compatible;
5. al menos un work set válido en ambas.

No se mezclan:
- carga externa;
- peso corporal;
- peso corporal con lastre;
- asistencia.

Las sesiones del mismo día se ordenan por timestamp completo y mantienen identidad independiente.

## 7. Récords personales

Los récords son independientes de la valoración de progreso frente a la sesión anterior.

### Carga externa / peso corporal con lastre
PR de carga = mayor carga válida histórica del mismo ejercicio y modalidad.

PR de repeticiones = más repeticiones que el mejor registro histórico con exactamente la misma carga.

### Peso corporal
PR de repeticiones = máximo de repeticiones válido frente al histórico comparable.

### Asistido
PR = menor asistencia válida histórica, respetando la semántica inversa de la carga de asistencia.

No se calcula ni presenta 1RM estimado como récord real.

Un nuevo máximo de carga con una caída fuerte de repeticiones puede ser un **récord de carga** y, al mismo tiempo, NO ser clasificado como mejora global de rendimiento.

## 8. Comparación con la sesión anterior

`analyzeExercise()` devuelve:
- comparabilidad;
- razón si no existe referencia;
- modalidad;
- `previousSessionId`;
- set representativo anterior y actual;
- récords;
- comparación textual;
- tendencia.

Tendencias relevantes:
- `improved`: mejora verificable según modalidad;
- `lower`: rendimiento claramente inferior;
- `mixed`: cambio que no permite afirmar mejora global;
- `stable`;
- `higher-effort`;
- `no-reference`;
- `unconfirmed`;
- `invalid`.

Sólo una tendencia realmente positiva entra en `improvements`.

No se generan porcentajes de mejora.

## 9. Progresión y sugerencias

La prescripción del Coach nunca se modifica automáticamente.

La interfaz separa:
- prescripción del Coach;
- referencia histórica;
- resultado real;
- `Sugerencia calculada`.

Reglas principales:
- sin RIR no se justifica un aumento de dificultad;
- RIR < 1 bloquea recomendaciones de aumento automático;
- más reps con la misma carga y RIR >= 2 permite sugerir que el Coach valore progresión;
- peso corporal nunca se convierte automáticamente en recomendación de añadir lastre;
- asistencia se expresa en términos de asistencia, no de “subir carga”;
- una carga mayor con reps inferiores no se describe automáticamente como progreso.

## 10. Resumen Premium confirmado

El resumen se renderiza después de la confirmación V207.

Incluye sólo información verificada:
- día/entrenamiento;
- fecha;
- work sets válidos;
- ejercicios registrados;
- récords reales;
- mejoras verificables;
- comentarios vinculados a la sesión exacta cuando existen;
- acceso a historial.

La pantalla conserva el significado de guardado exitoso mediante “Sesión guardada con éxito”.

Los estados de fallo/reintento siguen bajo V207 y reutilizan el mismo ID de sesión, preservando idempotencia.

## 11. Alumno y Coach

Historial Alumno y Coach consultan la misma sesión exacta.

El Coach recibe:
- comparación verificable;
- sugerencia calculada diferenciada;
- comentarios/molestias ya vinculados por sesión;
- estados existentes de revisión/OK.

No se inició el rediseño global del Dashboard Coach.

## 12. QA agregado y heredado

La certificación final exige en el mismo SHA:

### Unit/contract
- date core;
- repository contracts;
- AgendaRepository;
- CommentRepository;
- Premium workout;
- session history;
- save sync;
- intelligent training.

Pruebas negativas 2C cubren además:
- `completed` local no equivale a confirmación;
- referencia histórica sin confirmar queda excluida;
- rendimiento inferior no se etiqueta como mejora;
- PR de carga con menos reps no equivale a mejora global;
- vacío no se convierte en cero accidental;
- modalidades incompatibles;
- calentamientos/intensificaciones/incompletos;
- sesiones del mismo día;
- RIR;
- timer absoluto y cambio de sesión.

### Supabase local
- Auth/RLS;
- integración smoke;
- AgendaRepository;
- CommentRepository;
- integridad sesión/comentario;
- reconstrucción completa de DB;
- repetición de contratos después de reconstrucción;
- aislamiento del artefacto.

### Browser
- 390x844 completo;
- 360x800 responsive;
- 430x932 responsive;
- 1440x900 completo;
- guardado confirmado;
- fallo/reintento;
- idempotencia;
- recovery;
- comentarios exactos;
- historial Alumno;
- historial Coach;
- temporizador;
- récords;
- progresión;
- no-reference;
- resumen confirmado;
- ausencia de overflow y regresiones V2.

## 13. Evidencia visual

Los Browser E2E generan fixtures ficticios y capturas en `artifacts/2c/`:

- `rest-active-<viewport>.png`;
- `record-valid-<viewport>.png`;
- `progression-<viewport>.png`;
- `no-reference-<viewport>.png`;
- `summary-<viewport>.png`;
- `student-history-<viewport>.png`;
- `coach-session-<viewport>.png`.

Estas capturas son evidencia de QA, no aprobación estética automática.

## 14. Topología y rendimiento

El inventory guard mantiene como contrato del artefacto:
- render assignments: 18;
- realtime channels: 2;
- timeouts: 57;
- intervals: 0;
- listeners: 51;
- MutationObservers: 3.

2C añade un único timeout acotado para el ticker de descanso y no añade intervalos, realtime channels ni una nueva fuente de verdad de sesiones.

## 15. Compatibilidad histórica

Se conserva:
- V207;
- recovery V340/V341;
- identidad estable de sesión;
- CommentRepository;
- AgendaRepository;
- comentarios exactos;
- historial V2;
- Auth/RLS.

Decisión conservadora: una sesión histórica que no conserve ninguna evidencia verificable de confirmación puede mostrarse en el historial legado, pero queda excluida de récords y progresión 2C. Es preferible no declarar un PR a partir de evidencia ambigua.

## 16. Producción y seguridad

Los workflows validan que `main` permanezca exactamente en:
`3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`.

Todo 2C se prueba con Supabase local y usuarios `test.local`.

No se modificó:
- `main`;
- Render producción;
- Supabase productivo;
- Auth/RLS productivo;
- datos reales.

No hubo deploy, merge ni migración productiva.

## 17. GitHub Actions de certificación

Los runs de certificación deben corresponder al commit que contiene este informe y estar ambos en SUCCESS:
- V22 local Supabase integration: https://github.com/facuujoel10/FJZ-TEAM/actions/workflows/v22-local-integration.yml?query=branch%3Adev%2Fteam-fjz-v22
- V22 browser baseline: https://github.com/facuujoel10/FJZ-TEAM/actions/workflows/v22-browser-baseline.yml?query=branch%3Adev%2Fteam-fjz-v22

Los enlaces directos a los dos runs exactos se incluyen en la entrega final, junto con el SHA final.

## 18. Riesgos pendientes

- Históricos sin evidencia persistida de confirmación quedan deliberadamente fuera de analytics 2C.
- Las etiquetas de set dependen de que el modelo histórico permita identificar calentamientos/intensificaciones; cuando no existe esa metadata, 2C no inventa una clasificación.
- La aprobación visual del temporizador, indicadores y resumen final corresponde al Product Owner después de revisar las capturas.

Etapa 3 no iniciada.
