# data

Repository ports live here. 1A declared the domain boundaries. 1B adds the first real read adapter, `agenda-repository.js`, against the existing `athlete_schedule` and `athlete_reminders` tables.

The repository never bypasses RLS and never owns UI rendering. `agenda-read-policy.js` makes legacy compatibility fail-closed: legacy is used only when the V22 feature flag is disabled, never when the canonical repository returns empty or raises a permission/network error.
