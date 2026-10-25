# TEAM FJZ — Architecture Baseline V20.7

This document describes the **effective authorities** in the current V20.7 artifact.
It is a map for consolidation. It does **not** authorize deleting historical patches yet.

## Environment boundaries

- Production branch: `main`
- Production recovery branch: `baseline/v20.7-production`
- Development branch: `develop`
- Production Render: `team-fjz`
- Zero-cost staging Render: `team-fjz-staging-local`
- Staging-local cloud: deliberately disabled
- Production Supabase must never be used from staging-local

## Build authority

1. Pinned source: `base/team-fjz-source-v20.7.html`
2. Historical transformation pipeline in `build.py`
3. Optional `staging_local_guard.py` for staging-local
4. **`v127_release_system.py` must remain final**

The build must stay reproducible from Git. Do not restore the mutable Edge Function fetch as a build dependency.

## Effective runtime authorities

### Release / PWA
**Authority:** `v127_release_system.py`

Responsibilities:
- RELEASE is the version authority.
- PWA/cache version normalization.
- service-worker update authority.

### Realtime
**Authority:** `v192_general_stability_audit.py`

Protection layer:
- `v193_interaction_persistence.py` blocks disruptive renders while editing/modals are active.
- `v200_state_save_routine_stability.py` protects routine mutations from stale realtime refreshes.

Do not introduce a second independent realtime channel system.

### Authentication freshness
**Authority:** `v194_final_ui_functional_audit.py`

Responsibilities:
- refresh session when JWT is near expiry;
- coalesce auth refresh;
- preflight cloud operations.

### Workout drafts
Base mechanism:
- `v145_workout_autosave.py`

Final corrections:
- `v196_fresh_workout_routine_flow.py`: stale draft automatic-resume limits.
- `v205_canonical_workout_progress.py`: rejects drafts older than an already-saved session.
- Supabase `commit_workout_session_v202`: deletes the finished day's cloud draft atomically.

### Workout inputs / previous load
Final behavior:
- `v201_definitive_workout_save.py`
- `v205_canonical_workout_progress.py`

Contract:
- fresh Kg input is empty;
- previous Kg is reference only;
- previous value must never count as current input.

### Workout completion / save
**Final authority:** `v207_confirmed_session_commit.py`

State machine:
`idle -> saving -> success | failed`

Contract:
- success is shown only after cloud confirmation;
- save button locks while saving;
- retry reuses the same session ID;
- failed save remains retryable;
- successful session cannot be saved twice.

Historical patches V19.0/V20.0/V20.1/V20.3/V20.4/V20.5 may prepare/transform primitives, but must not become a competing final `finishWorkout` authority after V20.7.

### Partial-session draft construction
Primitive source:
- `v106_partial_sessions.py`

V20.5 exports the final session-draft/save primitives for V20.7.

### Method tracking (dropset / superset)
Data/entry foundation:
- `v137_method_tracking_stability.py`

Final UI corrections:
- `v195_routine_method_geometry_fix.py`
- `v198_method_panel_persistence.py`
- `v205_canonical_workout_progress.py`

Contract:
- current method fields remain empty until entered;
- previous method loads are shown as reference;
- method panel survives card rebuilds.

### Routine editor
Flow stabilization:
- `v196_fresh_workout_routine_flow.py`

Method editor:
- V13.7 canonical method controls, deduped by V19.5.

### Exercise reorder
**Final modal-reorder authority:** `v204_terminal_save_scroll_stability.py`

Backend authority:
- Supabase RPC `reorder_athlete_exercises`

Contract:
- local reorder is immediate;
- exact scroll position is preserved;
- server update is atomic;
- stale realtime refresh cannot undo the move.

### Progress charts
**Authority:** `v205_canonical_workout_progress.py`

Includes:
- exercise load/volume/reps charts;
- measurement charts;
- TEAM FJZ professional visual treatment.

### Alerts
Frontend reviewed/archive behavior:
- `v197_alert_archive_behavior.py`

Backend authority:
- `get_coach_feed()`
- `get_student_alerts()`
- state tables `coach_feed_state`, `student_alert_state`

Contract:
- active feed contains pending alerts only;
- read/dismissed event keys remain as internal tombstones to prevent regeneration.

### Mobile fluidity
Primary optimization:
- `v185_production_runtime_optimization.py`
- `v192_general_stability_audit.py`
- `v206_fluidity_runtime_audit.py`

Known V20.6 baseline:
- one consolidated stylesheet;
- 3 MutationObservers;
- 0 PerformanceObservers;
- ~62 timeout call sites;
- ~24 RAF call sites;
- ~49 listener call sites;
- ~27 render assignments;
- ~10 channel definitions.

These are regression ceilings/indicators, not proof that every call is simultaneously active.

## Data authority map

### Compatibility/state document
`athlete_snapshots`
- still contains broad app state and compatibility data;
- should not silently become the source of truth for new domains.

### Normalized workout data
- `workout_sessions`
- `workout_sets`
- `progression_recommendations`

Snapshot session commits are normalized by trigger. Future consolidation should move toward one clear authority per domain rather than reading/writing both representations indiscriminately.

### Tracking
- `weekly_checkins`
- `body_measurements`
- `progress_photos`
- `checkin_schedules`

### Nutrition
- `nutrition_plans`
- `nutrition_plan_revisions`
- `nutrition_logs`
- `food_library`
- `fitness_recipes`

### Coach/admin
- `coach_students`
- `coach_feed_state`
- `coach_payments`
- `student_notices`
- `student_alert_state`

## Consolidation order

Do not consolidate everything at once.

1. **Workout save/draft stack**
   - preserve V20.7 behavior exactly;
   - create characterization tests first;
   - collapse historical wrappers into one canonical module only after parity is proven.

2. **Routine/reorder stack**
   - preserve atomic RPC;
   - preserve scroll and modal behavior.

3. **Realtime/render stack**
   - one channel authority;
   - one render scheduling policy;
   - interaction guard.

4. **Tracking/progress**
   - consolidate visual and input geometry layers.

5. **Nutrition**
   - consolidate only after workout/routine paths are stable.

## Non-negotiable release rules

- Never develop directly on `main`.
- Never point staging-local to production Supabase.
- Never use real student data in staging.
- Never delete historical patches merely because a later authority exists; first prove behavioral parity.
- Never merge a schema-destructive migration without backup/rollback.
- Every release must pass `preflight.py` and `smoke_static.py`.
- Cloud/RLS integration tests remain blocked until an isolated Supabase staging environment exists.
