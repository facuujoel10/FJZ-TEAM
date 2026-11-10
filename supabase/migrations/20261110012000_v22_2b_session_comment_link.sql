-- TEAM FJZ V22 · ETAPA 2B
-- Additive local-only migration. Production application requires separate authorization.
alter table public.exercise_feedback
  add column if not exists session_id text;

create index if not exists exercise_feedback_session_id_idx
  on public.exercise_feedback(student_id,session_id,created_at desc)
  where session_id is not null;

do $$
begin
  if not exists (
    select 1 from pg_constraint
    where conname='exercise_feedback_session_id_shape_v22_2b'
      and conrelid='public.exercise_feedback'::regclass
  ) then
    alter table public.exercise_feedback
      add constraint exercise_feedback_session_id_shape_v22_2b
      check (session_id is null or (char_length(session_id) between 3 and 160 and session_id !~ '\\s'));
  end if;
end $$;

create or replace function public.guard_feedback_session_link_v22_2b()
returns trigger
language plpgsql
set search_path to 'public','pg_temp'
as $$
declare
  v_owner uuid;
begin
  if tg_op='UPDATE' and new.session_id is distinct from old.session_id then
    raise exception 'session_id is immutable';
  end if;
  if new.session_id is null then return new; end if;

  select a.user_id into v_owner from public.athletes a where a.id=new.athlete_id;
  if v_owner is null or v_owner<>new.student_id then
    raise exception 'feedback athlete/student mismatch';
  end if;

  if exists(
    select 1 from public.workout_sessions ws
    where ws.source_session_id=new.session_id
      and ws.student_id<>new.student_id
  ) then
    raise exception 'feedback session belongs to another student';
  end if;

  return new;
end;
$$;

drop trigger if exists exercise_feedback_session_link_guard_v22_2b on public.exercise_feedback;
create trigger exercise_feedback_session_link_guard_v22_2b
before insert or update on public.exercise_feedback
for each row execute function public.guard_feedback_session_link_v22_2b();

create or replace function public.guard_workout_session_feedback_owner_v22_2b()
returns trigger
language plpgsql
set search_path to 'public','pg_temp'
as $$
begin
  if new.source_session_id is null then return new; end if;
  if exists(
    select 1
    from public.exercise_feedback f
    join public.athletes a on a.id=f.athlete_id
    where f.session_id=new.source_session_id
      and (f.student_id<>new.student_id or a.user_id<>new.student_id)
  ) then
    raise exception 'session id conflicts with feedback owner';
  end if;
  return new;
end;
$$;

drop trigger if exists workout_session_feedback_owner_guard_v22_2b on public.workout_sessions;
create trigger workout_session_feedback_owner_guard_v22_2b
before insert or update of student_id,source_session_id on public.workout_sessions
for each row execute function public.guard_workout_session_feedback_owner_v22_2b();

comment on column public.exercise_feedback.session_id is
  'V22 2B stable workout instance id. Nullable for historical feedback; exact link uses student_id + session_id.';
