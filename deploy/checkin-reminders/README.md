## Recordatorios opcionales en staging

Aplicar supabase/staging/20261124_checkin_reminders.sql a la base de staging. Instalar los requisitos del worker en su entorno virtual. Configurar FJZ_STAGING_DATABASE_URL para una cuenta de servicio con lectura de las fichas, reglas, dispositivos, controles semanales y medidas, inserción en checkin_push_attempts, eliminación de suscripciones vencidas y acceso por las políticas correspondientes.

Generar un par VAPID exclusivo para staging. Pasar FJZ_VAPID_PUBLIC_KEY (base64url) al build. Guardar FJZ_VAPID_PRIVATE_KEY y FJZ_VAPID_SUBJECT (mailto de contacto) sólo en el worker. Instalar staging.cron ajustando la ruta del checkout. Publicar sobre HTTPS.

La frecuencia semanal usa el día de la semana de la primera fecha. La mensual usa su día de mes o el último día si es más corto. Se usa hora argentina. Cada programación permite un intento por período, dentro de los primeros 30 minutos desde la hora elegida. Sólo se conserva un teléfono activo por alumno. El control mensual corresponde a las medidas corporales. Los chequeos y las medidas ya registrados en su período suprimen el aviso.

Validar con cuentas QA y teléfonos de prueba: permisos denegados, regla apagada, activación explícita de ambas partes, recepción con app cerrada, apertura, cancelación, doble ejecución del worker y supresión después de registrar el control. Revisar las excepciones de entrega sin registrar claves ni endpoints.
