# TEAM FJZ V22 — entorno de desarrollo aislado

## Baseline inmutable de esta rama
- Rama: `dev/team-fjz-v22`
- Release de origen: **V21.41**
- Commit de origen: `3ffcf3efb1889dc3f915d063ffdf67d6c2ae5807`
- Producción Render: NO se usa para desarrollo.
- Supabase producción: NO se usa para desarrollo.

## Regla de aislamiento
El desarrollo V22 solo acepta Supabase en `127.0.0.1` o `localhost`.
El archivo `.team-fjz-development` obliga a indicar `TEAM_FJZ_ENV=development`
o `test`; un build productivo falla mientras ese sentinel esté presente.

No ejecutar en esta rama:
- `supabase login`
- `supabase link`
- `supabase db push --remote`
- `supabase db reset --remote`
- deploys de Render
- merges a `main`

## Requisitos gratuitos
Supabase local requiere Supabase CLI y un runtime compatible con Docker.
En Windows: Docker Desktop + Node 20 o superior. Los scripts usan `npx --yes supabase@3.0.0` para fijar exactamente la versión de la CLI y evitar cambios de targeting entre versiones. También puede instalarse la CLI por Scoop, pero el flujo automatizado usa la versión fijada por npx.

El stack local usa:
- API/Auth/Realtime/Storage: `http://127.0.0.1:54321`
- Postgres: puerto local 54322
- Studio: puerto local 54323
- Mailpit: puerto local 54324

El script crea una red Docker ligada a `127.0.0.1` para evitar exposición pública.

## Datos ficticios
Cuentas locales:
- `coach@test.local`
- `alumno01@test.local`
- `alumno02@test.local`

Contraseña local compartida: `TEAMFJZ-Local-Only!22`

Los nombres de fixtures comienzan con `TEST` o `QA`.
No se importa ninguna fila, foto, sesión, email ni credencial de producción.

## Inicializar / reiniciar
Desde la raíz de la rama:

```bash
python scripts/dev_reset.py
```

Ese comando:
1. ejecuta el guard;
2. comprueba Docker;
3. arranca Supabase local en red localhost;
4. ejecuta `supabase db reset`;
5. aplica migraciones y `seed.sql`;
6. crea las tres cuentas Auth locales;
7. carga fixtures ficticios;
8. ejecuta smoke tests de Auth, RLS, comentarios, nutrición y Storage.

## Generar la app local
```bash
python scripts/dev_build.py
python -m http.server 8000 -d public
```

`dev_build.py` obtiene URL/key exclusivamente de `supabase status -o env`.
No acepta una URL hospedada en `*.supabase.co`.

## QA de Etapa 0A
Debe quedar verde:
- `python scripts/dev_guard.py`
- `python scripts/dev_reset.py`
- `python scripts/dev_build.py`
- preflight existente, ejecutado por `build.py`
- `python scripts/dev_guard.py --artifact`

Una Etapa 0A no está validada si no puede ejecutarse `dev_reset.py` contra
Postgres/Auth/Storage reales del stack local. No se reemplaza por mocks.

## Diseño local relevante
La migración V22 crea solo el subconjunto necesario para la próxima fase:
profiles, coach_students, athletes, athlete_snapshots, workout_sessions,
exercise_feedback, food_library, nutrition_plans, nutrition_logs y
coach_feed_state. Incluye RLS Coach/Alumno, un RPC local compatible con el
guardado final de sesión y una proyección mínima de sesiones para QA.

Los buckets locales son:
- progress-photos
- profile-photos
- exercise-videos

## Recuperación
El entorno local es descartable. `supabase db reset` reconstruye esquema y
seed. `dev_bootstrap.py` vuelve a crear Auth y fixtures ficticios.

Esto no es un procedimiento de rollback productivo y no ejecuta ninguna
operación contra producción.
