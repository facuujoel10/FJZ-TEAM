# TEAM FJZ — Manual QA · Release Candidate V20.65

Fecha: 2026-10-21  
Objetivo: validar manualmente `develop/staging` antes de cualquier merge a `main`.

## Regla de release
No mergear a `main` hasta completar este checklist manual y resolver cualquier anomalía observada.

## 1. Acceso y navegación
- Entrar a staging como Coach.
- Cambiar entre Dashboard, alumno, Resumen, Rutina, Progreso, Historial, Seguimiento y Nutrición.
- Verificar que ninguna pestaña scrollee sola a mitad de pantalla.
- Volver atrás y confirmar que no haya saltos o warpeos.
- Repetir en móvil.
- Confirmar que botones, cards y headers no se muevan al tocar fuera de modales.

## 2. Dashboard Coach
- Revisar Centro de Prioridades.
- Revisar Calendario del Coach.
- Cambiar mes hacia atrás y adelante.
- Confirmar que nombres, botones y badges no se salgan de los boxes.
- Confirmar que los cuatro KPIs del calendario estén alineados.
- Abrir eventos y verificar navegación correcta al alumno.
- Revisar Estado 4 semanas de varios alumnos.
- Confirmar que las cards tengan misma separación, radios y jerarquía visual.

## 3. Rutina — Coach
- Crear ejercicio.
- Editar ejercicio.
- Cambiar series/repeticiones/RIR.
- Mover ejercicio arriba/abajo.
- Mover ejercicio con modal.
- Crear/eliminar/mover día.
- Probar principal 12-10-8-8 y accesorio 3x10.
- Probar dropset, rest-pause, superserie y biserie.
- Verificar slot de peso adicional para dropset/métodos.
- Confirmar que cada guardado válido muestra ✓ verde.
- Si la sincronización queda pendiente, confirmar que NO aparezca éxito verde falso.
- Confirmar que mover ejercicios no produzca scroll involuntario.

## 4. Entrenamiento — Alumno
- Iniciar sesión.
- Cargar algunos ejercicios y dejar otros vacíos.
- Salir/cerrar y volver a entrar: confirmar recuperación/autosave.
- Guardar sesión incompleta.
- Guardar y finalizar sesión completa.
- Confirmar que después de finalizar:
  - aparece ✓ verde;
  - el botón de guardar/finalizar deja de invitar a guardar otra vez;
  - no se duplica la sesión;
  - el historial muestra una sola sesión.
- Iniciar la siguiente sesión del mismo día y confirmar que reps/estructura programada no cambien solas.
- Confirmar que pesos anteriores aparezcan como referencia y no se autocompleten incorrectamente.

## 5. Check-in
- Completar todos los campos.
- Enviar.
- Confirmar ✓ verde sólo después del guardado.
- Confirmar que campos 1–10 respeten límites.
- Verificar boxes de semana/fecha en móvil.
- Coach: abrir check-in, escribir decisión, cómo seguimos y prioridad semanal.
- Guardar devolución y confirmar ✓ verde.
- Alumno: confirmar que Plan actual y respuesta del Coach aparezcan.
- Marcar Entendido y comprobar que el estado cambia sin desaparecer incorrectamente.

## 6. Progreso / medidas / fotos
- Cargar medición.
- Editar medición.
- Confirmar ✓ verde.
- Revisar que fecha/peso/medidas estén alineados en móvil.
- Cargar foto frente/perfil/espalda.
- Reemplazar y eliminar foto.
- Confirmar que Progreso no aparezca superpuesto en otras pestañas.
- Revisar gráficos y tarjetas en desktop y móvil.

## 7. Agenda y calendario
- Configurar agenda semanal.
- Crear recordatorio semanal.
- Crear recordatorio de fecha única.
- Confirmar ✓ verde en guardado.
- Verificar que calendario Coach refleje próximo check-in / revisión.
- Verificar vencidos y próximos 7/14 días.
- Confirmar que no haya recordatorios duplicados después de recargar.

## 8. Feedback
- Alumno: enviar comentario general + dificultad de sesión.
- Coach: responder feedback y marcar revisión.
- Confirmar ✓ verde.
- Alumno: visualizar devolución.
- Confirmar que no reaparezca como pendiente después de revisada.

## 9. Nutrición
- Abrir plan.
- Guardar cambios.
- Registrar comida completa.
- Registrar opción del plan.
- Editar/activar opciones disponibles.
- Confirmar ✓ verde o confirmación verde compacta según la acción.
- Verificar que ningún box de macros se salga en móvil.

## 10. Perfil
- Editar nombre/objetivo como Coach.
- Editar datos personales como Alumno.
- Cambiar foto.
- Confirmar ✓ verde.
- Revisar avatar, nombre y objetivo en dashboard y perfil.
- Confirmar que no haya duplicados visuales.

## 11. Estabilidad / warpeo
Repetir durante varios minutos:
- cambiar pestañas rápido;
- abrir/cerrar modales;
- editar inputs;
- abrir teclado móvil;
- hacer scroll largo;
- mover ejercicios;
- guardar y volver al dashboard;
- rotar entre vistas.

Debe cumplirse:
- sin scroll involuntario;
- sin boxes que cambien de ancho solos;
- sin cards que aparezcan en otra pestaña;
- sin parpadeos grandes;
- sin doble render visible;
- sin botones duplicados;
- sin elementos que se salgan horizontalmente;
- sin lag notable al escribir.

## 12. Resoluciones recomendadas
- Desktop ancho.
- Laptop 1366×768 aproximado.
- Tablet / 768 px.
- Móvil ~430 px.
- Móvil ~390 px.
- Móvil pequeño ~360 px.

## Estado de release
- [ ] QA manual Coach completa
- [ ] QA manual Alumno completa
- [ ] QA móvil completa
- [ ] Guardados ✓ completos
- [ ] Calendario completo
- [ ] Rutinas completas
- [ ] Check-in completo
- [ ] Sin warpeo/scroll involuntario
- [ ] Seguridad pendiente de release revisada
- [ ] Autorización explícita del Coach para merge a `main`

Hasta que estas casillas estén completas, `main` queda intacta.
