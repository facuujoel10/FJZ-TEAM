# V22 — futuro vínculo exacto Comentario ↔ Sesión

Este documento prepara una subetapa posterior. **2A no cambia el esquema.**

## Diseño aditivo propuesto

1. Agregar en una migración futura una columna nullable `session_id` (o identificador estable equivalente) sólo después de certificar la autoridad definitiva de la instancia de sesión.
2. Mantener `athlete_id`, `student_id`, `exercise_uid`, `workout_day_id` y timestamps actuales.
3. Comentarios históricos continúan válidos con `session_id = null`.
4. Sólo escribir el vínculo exacto cuando el cliente tenga una instancia de sesión estable y autorizada.
5. RLS deberá comprobar acceso al comentario y pertenencia de la sesión al mismo alumno/Coach.
6. Historial y Centro de Comentarios priorizarán el vínculo exacto; históricos sin vínculo conservarán el fallback compatible actual.
7. La migración será aditiva, primero en Supabase local, con retrocompatibilidad.

## Fuera de 2A

2A no agrega la columna, no infiere asociaciones exactas retroactivas, no modifica comentarios históricos y no reemplaza el snapshot compatible V287.
