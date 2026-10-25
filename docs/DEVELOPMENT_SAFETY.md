# TEAM FJZ — Development & Release Safety Policy

Baseline de producción al iniciar la nueva etapa: **V20.7**  
Commit LIVE: `f6480c4cbd35cf8035e77680ed87423b1e22f1c6`

## Ramas

- `baseline/v20.7-production`: punto de recuperación de la producción actual. No desarrollar aquí.
- `main`: producción. No trabajar directamente.
- `develop`: integración de cambios antes de staging.

## Regla principal

Ningún cambio nuevo debe llegar a `main` sin pasar primero por:

1. `develop`.
2. Preflight.
3. Staging con backend separado.
4. Checklist funcional.
5. Verificación de integridad de datos.
6. Aprobación para release.
7. Procedimiento de rollback identificado.

## Staging

El build de staging debe usar:

- `TEAM_FJZ_ENV=staging`
- `TEAM_FJZ_SUPABASE_URL=<URL del proyecto/branch de staging>`
- `TEAM_FJZ_SUPABASE_PUBLISHABLE_KEY=<publishable key de staging>`

El build debe fallar si un entorno no productivo apunta al Supabase de producción.

## Datos

- No usar datos personales reales para pruebas.
- Crear usuarios Coach Test / Alumno Test.
- Usar datos sintéticos.
- No copiar fotos reales a staging.
- No ejecutar migraciones destructivas.
- Toda migración futura debe tener rollback o estrategia reversible.

## Validación automática\n\nCada build de staging debe ejecutar:\n\n```bash\npython preflight.py\npython smoke_static.py\n```\n\nUn fallo en cualquiera bloquea la publicación.\n\n## Release checklist mínima

### Auth y aislamiento
- Coach Test inicia sesión.
- Alumno Test inicia sesión.
- Alumno Test no puede leer/modificar otro alumno.
- Coach Test solo accede a alumnos vinculados.

### Entrenamiento
- Abrir rutina.
- Cargar kg / reps / RIR.
- Peso anterior se muestra solo como referencia.
- Dropset/superserie conserva referencia anterior y slots nuevos vacíos.
- Guardado parcial.
- Recuperación de borrador.
- Finalización completa.
- Doble toque en Guardar no duplica.
- Fallo de red permite reintentar la misma sesión.
- Tras éxito confirmado desaparece el flujo de Guardar.
- Recargar conserva la sesión.
- 1 sesión final = 1 ID.

### Rutinas
- Editar ejercicio.
- Mover ejercicio sin salto de scroll.
- Guardar orden.
- Agregar/eliminar ejercicio.
- Agregar/eliminar día.

### Seguimiento
- Check-in.
- Medidas.
- Editar medida.
- Fotos.
- Gráficos.

### Nutrición
- Ver dieta.
- Alternativas.
- Registro si está habilitado.
- Recetas.

### Regresión
- Alertas.
- Agenda.
- Pagos.
- Perfil.
- PWA móvil.
- Desktop.

## Rollback

Antes de publicar:

- Anotar commit de producción anterior.
- Confirmar deploy anterior disponible.
- Confirmar backup/restore de base de datos.
- No publicar cambios de schema irreversibles.
- Mantener la rama baseline.

Si una prueba crítica falla, **no promover a producción**.
