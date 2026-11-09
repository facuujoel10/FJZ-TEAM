# TEAM FJZ V22 — 1A Architecture Map

## Entry points and effective execution

- `build.py` is the build orchestrator.
- Reproducible base: `base/team-fjz-source-v20.7.html`.
- Historical Python transforms execute sequentially; order is behaviorally significant.
- 0C authority ends at `v342_v22_0c_ui_authority.py`.
- 1A adds `v343_v22_1a_architecture_foundation.py`.
- `v127_release_system.py` remains a late compatibility/release authority.
- Development/test output is sanitized against hosted/productive Supabase and finishes through `preflight.py`.
- `scripts/v22_architecture_inventory.py` extracts the complete ordered patch list, literal Supabase tables/RPCs and runtime topology on CI.

## Real authority map

| Domain | Effective chain | Classification |
|---|---|---|
| Auth/session | base auth + V194/V263/V294 hardening | Legacy compatible; dangerous |
| Global render | base + consolidation layers including V125/V178/V180 | Duplicated, still necessary |
| Realtime | V132/V192 plus V210–V218 delegation | Canonical direction + legacy consumers |
| Workout save | V205 → V207 → V340/V341 | Current canonical authority |
| Routine save | V200/V209 + historical editor consumers | Canonical persistence + legacy UI |
| Exercise comments | V73 → V287 → V325 → V328/V329/V336 | Current canonical functional chain |
| Review/alerts | V299/V301/V302 + V331/V338/V339 | Multiple generations; compatibility required |
| Coach dashboard | V170 visible dashboard + later compatibility layers | Legacy-compatible final surface |
| Agenda | historical data + V310–V314 + V342 visibility | Candidate for first repository migration |
| Nutrition | base/V94 + V153/V216/V229 + later UI | High-risk |
| Progress/check-ins | historical snapshots + V246–V260/V303–V309 | High-risk |
| Release/PWA | V127 late release authority | Current canonical release authority |

## Shared globals and historical coupling

Important shared globals include `state`, `mode`, `coachTab`, `coachStudentTab`, `currentUser`, `currentProfile`, `supabaseClient`, `cloudAthletes`, `render` and `saveState`.

Historical athlete/session snapshots are compatibility contracts. IDs, routines, sessions, comments, nutrition, check-ins, photos and review state must remain backward compatible during migration.

## Persistence, synchronization and Supabase

Persistence is still mixed between in-memory/local state and Supabase calls embedded in UI/runtime functions. Current confirmed-save/readback work is valuable but not yet a single cross-domain contract.

Known critical examples include `athlete_snapshots`, `exercise_feedback` and `coach_feed_state`. CI inventory scans source for all literal `.from(...)` and `.rpc(...)` calls so the map remains evidence-based.

## Dates

Date logic is distributed historically. 1A introduces `src/core/date.js` as the first canonical module and integrates only `dateInputToday()` with a safe legacy fallback. Date-only historical strings are preserved and are not reinterpreted as UTC instants.

## Target progressive structure

```
src/
  core/    cross-domain primitives
  data/    repository contracts and future adapters
  modules/ future domain orchestration
  ui/      shared design/UI criteria
  legacy/  compatibility adapters/notes
```

## Classification

**Canonical/reusable:** new date core; dev isolation guards; E2E safety barrier; V207 confirmed-session authority; readback pattern for critical writes.

**Legacy requiring compatibility:** global state model, base render/auth, historical snapshot shapes, V170 dashboard consumers, historical nutrition/progress/check-in models.

**Duplicated but still necessary:** remaining render generations, alert/review presentation layers and inline-handler targets still consumed by current screens.

**Migration candidates:** date helpers, Agenda data access, Comment data access, save-status UI.

**Dangerous without more tests:** auth/session recovery, global render authority, Realtime ownership, confirmed workout save, athlete snapshot schema, nutrition persistence, progress photos and RLS-sensitive Coach/Alumno permissions.

## Save/error contract

Future saves distinguish:
`pending → saving → confirmed`,
`saving → recoverable_error → retry_pending → saving`,
or `saving → fatal_error`.

A confirmed receipt requires server confirmation evidence. 1A does not replace existing save systems globally.

## Data contracts

Declared future ports:
WorkoutRepository, CommentRepository, NutritionRepository, ProgressRepository, CheckinRepository, AgendaRepository and CoachRepository.

Only a read-only `AgendaRepository` pilot is implemented and tested. It is not connected to current UI or Supabase runtime.

## Design-system foundation

TEAM FJZ retains black/red/gray. Future work must consolidate existing variables/components instead of introducing a parallel theme. Priorities: mobile-first Student, desktop-first Coach, readable typography, consistent spacing/actions, explicit loading/success/error states, accessible labels/focus and responsive controls.

No screen redesign is performed in 1A.
