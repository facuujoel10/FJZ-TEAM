-- TEAM FJZ V21.05
-- Check-in resubmission lifecycle authority.
-- Applied to production Supabase on 2026-10-25.
--
-- 1) Any genuine resubmission of the same weekly row becomes pending review again.
-- 2) Feed keys include submitted_at so a new submission cannot inherit old read/dismissed state.

create or replace function public.reset_weekly_checkin_review_on_resubmit()
returns trigger
language plpgsql
set search_path = public, pg_temp
as $$
begin
  if old.reviewed_at is not null
     and new.submitted_at is not null
     and (old.submitted_at is null or new.submitted_at > old.submitted_at) then
    new.reviewed_at := null;
  end if;
  return new;
end;
$$;

drop trigger if exists weekly_checkin_resubmit_pending on public.weekly_checkins;

create trigger weekly_checkin_resubmit_pending
before update of submitted_at on public.weekly_checkins
for each row
execute function public.reset_weekly_checkin_review_on_resubmit();

-- get_coach_feed_legacy_v121 was updated in production so these two event keys are versioned:
-- new-checkin:<checkin_id>:<submitted_at YYYYMMDDHH24MISSMS>
-- wellness:<checkin_id>:<submitted_at YYYYMMDDHH24MISSMS>
