-- TEAM FJZ V22 local-only baseline.
-- Schema only: no production records, emails, photos or credentials are copied.

create extension if not exists pgcrypto;

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  full_name text not null default '',
  role text not null default 'student' check (role in ('coach','student')),
  avatar_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  avatar_position_x numeric not null default 50,
  avatar_position_y numeric not null default 50,
  avatar_zoom numeric not null default 1
);

create table if not exists public.coach_students (
  id uuid primary key default gen_random_uuid(),
  coach_id uuid not null references auth.users(id) on delete cascade,
  student_id uuid not null references auth.users(id) on delete cascade,
  status text not null default 'active' check (status in ('active','inactive')),
  linked_at timestamptz not null default now(),
  unique(coach_id,student_id)
);

create table if not exists public.athletes (
  id uuid primary key default gen_random_uuid(),
  coach_id uuid not null references auth.users(id) on delete cascade,
  user_id uuid unique references auth.users(id) on delete set null,
  client_id text not null unique,
  name text not null,
  goal text not null default '',
  invite_code text not null unique default upper(substr(replace(gen_random_uuid()::text,'-',''),1,8)),
  created_at timestamptz not null default now(),
  spotify_url text,
  spotify_title text,
  sex text,
  birth_date date,
  occupation_study text,
  start_date date,
  height_cm numeric(5,2)
);

create table if not exists public.athlete_snapshots (
  athlete_id uuid primary key references public.athletes(id) on delete cascade,
  data jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create table if not exists public.workout_sessions (
  id uuid primary key default gen_random_uuid(),
  student_id uuid not null references auth.users(id) on delete cascade,
  routine_id uuid,
  routine_day_id uuid,
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  status text not null default 'in_progress' check (status in ('in_progress','completed','cancelled')),
  notes text not null default '',
  adherence_score numeric,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  source_session_id text
);
create index if not exists workout_sessions_student_date_idx on public.workout_sessions(student_id,started_at desc);
create unique index if not exists workout_sessions_student_source_uidx
  on public.workout_sessions(student_id,source_session_id)
  where source_session_id is not null;

create table if not exists public.exercise_feedback (
  id uuid primary key default gen_random_uuid(),
  athlete_id uuid not null references public.athletes(id) on delete cascade,
  student_id uuid not null references auth.users(id) on delete cascade,
  exercise_uid text not null,
  exercise_name text not null,
  workout_day_id text,
  workout_day_name text,
  feedback_type text not null default 'comment' check (feedback_type in ('comment','discomfort')),
  message text not null,
  status text not null default 'pending' check (status in ('pending','reviewed')),
  reviewed_by uuid references auth.users(id) on delete set null,
  reviewed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists exercise_feedback_athlete_status_idx on public.exercise_feedback(athlete_id,status,created_at desc);
create index if not exists exercise_feedback_student_idx on public.exercise_feedback(student_id,created_at desc);

create table if not exists public.food_library (
  id uuid primary key default gen_random_uuid(),
  created_by uuid references auth.users(id) on delete cascade,
  is_global boolean not null default false,
  name text not null,
  category text not null default 'Otros',
  kcal_100g numeric(7,2) not null check (kcal_100g>=0),
  protein_100g numeric(6,2) not null check (protein_100g>=0),
  carbs_100g numeric(6,2) not null check (carbs_100g>=0),
  fat_100g numeric(6,2) not null check (fat_100g>=0),
  default_portion_g numeric(7,2) not null default 100 check (default_portion_g>0),
  notes text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unit_name text,
  grams_per_unit numeric(8,2),
  reference_source text not null default '',
  reference_note text not null default ''
);
create index if not exists food_library_name_idx on public.food_library(lower(name));
create unique index if not exists food_library_global_name_uidx on public.food_library(lower(name)) where is_global=true;

create table if not exists public.nutrition_plans (
  id uuid primary key default gen_random_uuid(),
  athlete_id uuid not null unique references public.athletes(id) on delete cascade,
  coach_id uuid not null references auth.users(id) on delete cascade,
  title text not null default 'Plan nutricional',
  notes text not null default '',
  target_kcal numeric,
  target_protein_g numeric,
  target_carbs_g numeric,
  target_fat_g numeric,
  plan jsonb not null default '{"meals":[]}'::jsonb,
  revision integer not null default 1,
  active boolean not null default true,
  published_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  student_logging_enabled boolean not null default true
);

create table if not exists public.nutrition_logs (
  id uuid primary key default gen_random_uuid(),
  athlete_id uuid not null references public.athletes(id) on delete cascade,
  student_id uuid references auth.users(id) on delete cascade,
  logged_on date not null default current_date,
  meal_label text not null default 'Comida',
  food_id uuid references public.food_library(id) on delete set null,
  food_name text not null,
  grams numeric not null check (grams>0),
  kcal numeric not null check (kcal>=0),
  protein_g numeric not null check (protein_g>=0),
  carbs_g numeric not null check (carbs_g>=0),
  fat_g numeric not null check (fat_g>=0),
  source text not null default 'calculator' check (source in ('calculator','custom','plan')),
  note text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  measure_type text not null default 'grams' check (measure_type in ('grams','units')),
  quantity numeric,
  unit_name text,
  meal_group_id uuid
);
create index if not exists nutrition_logs_athlete_date_idx on public.nutrition_logs(athlete_id,logged_on desc);
create index if not exists nutrition_logs_student_idx on public.nutrition_logs(student_id);

create table if not exists public.coach_feed_state (
  coach_id uuid not null references auth.users(id) on delete cascade,
  event_key text not null,
  read_at timestamptz,
  dismissed_at timestamptz,
  created_at timestamptz not null default now(),
  primary key(coach_id,event_key)
);

create or replace function public.current_profile_role()
returns text
language sql
stable
security definer
set search_path to 'public','pg_temp'
as $$
  select role from public.profiles where id=auth.uid();
$$;

create or replace function public.are_linked(a uuid,b uuid)
returns boolean
language sql
stable
security definer
set search_path to 'public','pg_temp'
as $$
  select exists(
    select 1 from public.coach_students cs
    where cs.status='active'
      and ((cs.coach_id=a and cs.student_id=b)
        or (cs.coach_id=b and cs.student_id=a))
  );
$$;

create or replace function public.is_coach_of(p_student uuid)
returns boolean
language sql
stable
security definer
set search_path to 'public','pg_temp'
as $$
  select exists(
    select 1 from public.coach_students cs
    where cs.coach_id=auth.uid()
      and cs.student_id=p_student
      and cs.status='active'
  );
$$;

create or replace function public.can_access_athlete(p_athlete uuid)
returns boolean
language sql
stable
security definer
set search_path to 'public','pg_temp'
as $$
  select exists(
    select 1 from public.athletes a
    where a.id=p_athlete
      and (a.coach_id=auth.uid() or a.user_id=auth.uid())
  );
$$;

create or replace function public.can_edit_athlete_as_coach(p_athlete uuid)
returns boolean
language sql
stable
security definer
set search_path to 'public','pg_temp'
as $$
  select exists(
    select 1 from public.athletes a
    where a.id=p_athlete and a.coach_id=auth.uid()
  );
$$;

create or replace function public.commit_workout_session_v202(
  p_athlete_id uuid,p_day_id text,p_day jsonb,p_session jsonb
)
returns timestamptz
language plpgsql
set search_path to 'public','pg_temp'
as $$
declare
  v_updated timestamptz;
  v_uid uuid:=auth.uid();
  v_days jsonb;
  v_sessions jsonb;
  v_drafts jsonb;
begin
  if v_uid is null then raise exception 'not authenticated'; end if;
  if p_session is null or nullif(p_session->>'id','') is null then raise exception 'invalid session'; end if;
  if not exists(
    select 1 from public.athletes a
    where a.id=p_athlete_id and (a.coach_id=v_uid or a.user_id=v_uid)
  ) then raise exception 'not allowed'; end if;

  select coalesce(jsonb_agg(
    case when d.day->>'id'=p_day_id then p_day else d.day end order by d.ord
  ),'[]'::jsonb)
  into v_days
  from public.athlete_snapshots s
  cross join lateral jsonb_array_elements(
    case when jsonb_typeof(coalesce(s.data->'days','[]'::jsonb))='array'
      then coalesce(s.data->'days','[]'::jsonb) else '[]'::jsonb end
  ) with ordinality d(day,ord)
  where s.athlete_id=p_athlete_id;

  select coalesce(jsonb_agg(x.sess order by x.ord)
    filter(where nullif(x.sess->>'id','')<>nullif(p_session->>'id','')),'[]'::jsonb)
    || jsonb_build_array(p_session)
  into v_sessions
  from public.athlete_snapshots s
  left join lateral jsonb_array_elements(
    case when jsonb_typeof(coalesce(s.data->'sessions','[]'::jsonb))='array'
      then coalesce(s.data->'sessions','[]'::jsonb) else '[]'::jsonb end
  ) with ordinality x(sess,ord) on true
  where s.athlete_id=p_athlete_id;

  select coalesce(s.data->'workoutDrafts','{}'::jsonb)-p_day_id
  into v_drafts
  from public.athlete_snapshots s where s.athlete_id=p_athlete_id;

  update public.athlete_snapshots s
  set data=jsonb_set(
      jsonb_set(
        jsonb_set(
          jsonb_set(s.data,'{days}',coalesce(v_days,'[]'::jsonb),true),
          '{sessions}',coalesce(v_sessions,jsonb_build_array(p_session)),true
        ),
        '{workoutDrafts}',coalesce(v_drafts,'{}'::jsonb),true
      ),
      '{lastWorkout}',to_jsonb(coalesce(p_session->>'date','')),true
    ),
    updated_at=now()
  where s.athlete_id=p_athlete_id
  returning s.updated_at into v_updated;

  if v_updated is null then raise exception 'snapshot not found'; end if;
  return v_updated;
end;
$$;

create or replace function public.sync_snapshot_sessions_dev()
returns trigger
language plpgsql
security definer
set search_path to 'public','pg_temp'
as $$
declare
  a public.athletes%rowtype;
  sess jsonb;
  sid text;
  sdate timestamptz;
begin
  select * into a from public.athletes where id=new.athlete_id;
  if not found or a.user_id is null then return new; end if;

  for sess in select value from jsonb_array_elements(
    case when jsonb_typeof(coalesce(new.data->'sessions','[]'::jsonb))='array'
      then coalesce(new.data->'sessions','[]'::jsonb) else '[]'::jsonb end
  )
  loop
    sid:=nullif(sess->>'id','');
    if sid is null then continue; end if;
    begin sdate:=coalesce((sess->>'date')::timestamptz,now());
    exception when others then sdate:=now(); end;

    insert into public.workout_sessions(
      student_id,started_at,completed_at,status,notes,source_session_id
    ) values(
      a.user_id,sdate,sdate,'completed',
      coalesce(sess->>'dayName','Entrenamiento'),sid
    )
    on conflict(student_id,source_session_id) where source_session_id is not null
    do update set completed_at=excluded.completed_at,status='completed',
      notes=excluded.notes,updated_at=now();
  end loop;

  delete from public.workout_sessions ws
  where ws.student_id=a.user_id and ws.source_session_id is not null
    and not exists(
      select 1 from jsonb_array_elements(
        case when jsonb_typeof(coalesce(new.data->'sessions','[]'::jsonb))='array'
          then coalesce(new.data->'sessions','[]'::jsonb) else '[]'::jsonb end
      ) x
      where nullif(x->>'id','')=ws.source_session_id
    );
  return new;
end;
$$;

drop trigger if exists athlete_snapshots_sync_sessions_dev on public.athlete_snapshots;
create trigger athlete_snapshots_sync_sessions_dev
after insert or update of data on public.athlete_snapshots
for each row execute function public.sync_snapshot_sessions_dev();

alter table public.profiles enable row level security;
alter table public.coach_students enable row level security;
alter table public.athletes enable row level security;
alter table public.athlete_snapshots enable row level security;
alter table public.workout_sessions enable row level security;
alter table public.exercise_feedback enable row level security;
alter table public.food_library enable row level security;
alter table public.nutrition_plans enable row level security;
alter table public.nutrition_logs enable row level security;
alter table public.coach_feed_state enable row level security;

create policy profiles_select_linked on public.profiles for select to authenticated
using (id=(select auth.uid()) or public.are_linked((select auth.uid()),id));
create policy profiles_update_self on public.profiles for update to authenticated
using (id=(select auth.uid())) with check (id=(select auth.uid()));

create policy coach_students_select_self on public.coach_students for select to authenticated
using (coach_id=(select auth.uid()) or student_id=(select auth.uid()));

create policy athletes_select_access on public.athletes for select to authenticated
using (coach_id=(select auth.uid()) or user_id=(select auth.uid()));
create policy athletes_insert_coach on public.athletes for insert to authenticated
with check (coach_id=(select auth.uid()) and public.current_profile_role()='coach');
create policy athletes_update_coach on public.athletes for update to authenticated
using (coach_id=(select auth.uid()) and public.current_profile_role()='coach')
with check (coach_id=(select auth.uid()) and public.current_profile_role()='coach');

create policy snapshots_select_access on public.athlete_snapshots for select to authenticated
using (public.can_access_athlete(athlete_id));
create policy snapshots_insert_access on public.athlete_snapshots for insert to authenticated
with check (public.can_access_athlete(athlete_id));
create policy snapshots_update_access on public.athlete_snapshots for update to authenticated
using (public.can_access_athlete(athlete_id)) with check (public.can_access_athlete(athlete_id));

create policy workout_sessions_select_access on public.workout_sessions for select to authenticated
using (student_id=(select auth.uid()) or public.is_coach_of(student_id));
create policy workout_sessions_insert_access on public.workout_sessions for insert to authenticated
with check (student_id=(select auth.uid()) or public.is_coach_of(student_id));
create policy workout_sessions_update_access on public.workout_sessions for update to authenticated
using (student_id=(select auth.uid()) or public.is_coach_of(student_id))
with check (student_id=(select auth.uid()) or public.is_coach_of(student_id));

create policy exercise_feedback_select_access on public.exercise_feedback for select to authenticated
using (public.can_access_athlete(athlete_id));
create policy exercise_feedback_insert_student on public.exercise_feedback for insert to authenticated
with check (
  student_id=(select auth.uid())
  and exists(select 1 from public.athletes a where a.id=athlete_id and a.user_id=(select auth.uid()))
);
create policy exercise_feedback_update_coach on public.exercise_feedback for update to authenticated
using (public.can_edit_athlete_as_coach(athlete_id))
with check (public.can_edit_athlete_as_coach(athlete_id));

create policy food_library_select_access on public.food_library for select to authenticated
using (
  is_global=true or created_by=(select auth.uid()) or exists(
    select 1 from public.coach_students cs
    where cs.student_id=(select auth.uid())
      and cs.coach_id=food_library.created_by and cs.status='active'
  )
);
create policy food_library_insert_coach on public.food_library for insert to authenticated
with check (created_by=(select auth.uid()) and is_global=false and public.current_profile_role()='coach');

create policy nutrition_plans_select_access on public.nutrition_plans for select to authenticated
using (public.can_access_athlete(athlete_id));
create policy nutrition_plans_insert_coach on public.nutrition_plans for insert to authenticated
with check (coach_id=(select auth.uid()) and public.can_edit_athlete_as_coach(athlete_id));
create policy nutrition_plans_update_coach on public.nutrition_plans for update to authenticated
using (coach_id=(select auth.uid()) and public.can_edit_athlete_as_coach(athlete_id))
with check (coach_id=(select auth.uid()) and public.can_edit_athlete_as_coach(athlete_id));

create policy nutrition_logs_select_access on public.nutrition_logs for select to authenticated
using (public.can_access_athlete(athlete_id));
create policy nutrition_logs_insert_access on public.nutrition_logs for insert to authenticated
with check (
  public.can_access_athlete(athlete_id) and (
    (public.current_profile_role()='student'
      and student_id=(select auth.uid())
      and exists(select 1 from public.nutrition_plans np
        where np.athlete_id=nutrition_logs.athlete_id
          and np.active=true and np.student_logging_enabled=true))
    or
    (public.current_profile_role()='coach' and public.can_edit_athlete_as_coach(athlete_id))
  )
);
create policy nutrition_logs_update_access on public.nutrition_logs for update to authenticated
using (
  public.can_access_athlete(athlete_id) and (
    (student_id=(select auth.uid()) and exists(
      select 1 from public.nutrition_plans np
      where np.athlete_id=nutrition_logs.athlete_id
        and np.active=true and np.student_logging_enabled=true
    )) or public.can_edit_athlete_as_coach(athlete_id)
  )
)
with check (
  public.can_access_athlete(athlete_id) and (
    (student_id=(select auth.uid()) and exists(
      select 1 from public.nutrition_plans np
      where np.athlete_id=nutrition_logs.athlete_id
        and np.active=true and np.student_logging_enabled=true
    )) or public.can_edit_athlete_as_coach(athlete_id)
  )
);
create policy nutrition_logs_delete_access on public.nutrition_logs for delete to authenticated
using (
  (student_id=(select auth.uid()) and exists(
    select 1 from public.nutrition_plans np
    where np.athlete_id=nutrition_logs.athlete_id
      and np.active=true and np.student_logging_enabled=true
  )) or public.can_edit_athlete_as_coach(athlete_id)
);

create policy coach_feed_state_select_self on public.coach_feed_state for select to authenticated
using (coach_id=(select auth.uid()));
create policy coach_feed_state_insert_self on public.coach_feed_state for insert to authenticated
with check (coach_id=(select auth.uid()) and public.current_profile_role()='coach');
create policy coach_feed_state_update_self on public.coach_feed_state for update to authenticated
using (coach_id=(select auth.uid())) with check (coach_id=(select auth.uid()));

grant usage on schema public to authenticated;
grant select,insert,update,delete on
  public.profiles,public.coach_students,public.athletes,public.athlete_snapshots,
  public.workout_sessions,public.exercise_feedback,public.food_library,
  public.nutrition_plans,public.nutrition_logs,public.coach_feed_state
to authenticated;
grant execute on function public.current_profile_role() to authenticated;
grant execute on function public.are_linked(uuid,uuid) to authenticated;
grant execute on function public.is_coach_of(uuid) to authenticated;
grant execute on function public.can_access_athlete(uuid) to authenticated;
grant execute on function public.can_edit_athlete_as_coach(uuid) to authenticated;
grant execute on function public.commit_workout_session_v202(uuid,text,jsonb,jsonb) to authenticated;

-- Local Storage policies mirror TEAM FJZ ownership concepts without using
-- any production objects.
create policy profile_photos_insert_self on storage.objects for insert to authenticated
with check (bucket_id='profile-photos' and (storage.foldername(name))[1]=(select auth.uid())::text);
create policy profile_photos_select_access on storage.objects for select to authenticated
using (
  bucket_id='profile-photos' and (
    (storage.foldername(name))[1]=(select auth.uid())::text or
    ((storage.foldername(name))[1] ~* '^[0-9a-f-]{36}$'
      and public.are_linked((select auth.uid()),((storage.foldername(name))[1])::uuid))
  )
);
create policy progress_photos_insert_access on storage.objects for insert to authenticated
with check (
  bucket_id='progress-photos'
  and coalesce((storage.foldername(name))[1],'') ~* '^[0-9a-f-]{36}$'
  and public.can_access_athlete(((storage.foldername(name))[1])::uuid)
);
create policy progress_photos_select_access on storage.objects for select to authenticated
using (
  bucket_id='progress-photos'
  and coalesce((storage.foldername(name))[1],'') ~* '^[0-9a-f-]{36}$'
  and public.can_access_athlete(((storage.foldername(name))[1])::uuid)
);
create policy exercise_videos_insert_coach on storage.objects for insert to authenticated
with check (
  bucket_id='exercise-videos'
  and (storage.foldername(name))[1]=(select auth.uid())::text
  and public.current_profile_role()='coach'
);
create policy exercise_videos_select_access on storage.objects for select to authenticated
using (
  bucket_id='exercise-videos' and (
    (storage.foldername(name))[1]=(select auth.uid())::text or exists(
      select 1 from public.coach_students cs
      where cs.coach_id::text=(storage.foldername(name))[1]
        and cs.student_id=(select auth.uid()) and cs.status='active'
    )
  )
);

do $$ begin
  alter publication supabase_realtime add table public.athletes;
exception when duplicate_object then null; end $$;
do $$ begin
  alter publication supabase_realtime add table public.athlete_snapshots;
exception when duplicate_object then null; end $$;
do $$ begin
  alter publication supabase_realtime add table public.exercise_feedback;
exception when duplicate_object then null; end $$;
do $$ begin
  alter publication supabase_realtime add table public.nutrition_plans;
exception when duplicate_object then null; end $$;
do $$ begin
  alter publication supabase_realtime add table public.nutrition_logs;
exception when duplicate_object then null; end $$;


-- ================================================================
-- TEAM FJZ V22 0C.3 SCHEMA PARITY
-- Local-only contracts mirrored from production metadata.
-- No production rows or credentials are used.
-- ================================================================

create table if not exists public.athlete_schedule (
  id uuid primary key default gen_random_uuid(),
  athlete_id uuid not null references public.athletes(id) on delete cascade,
  coach_id uuid not null references public.profiles(id) on delete cascade,
  weekday smallint not null check (weekday between 0 and 6),
  workout_day_id text,
  workout_day_name text,
  start_time time,
  reminder_enabled boolean not null default true,
  reminder_minutes_before integer not null default 60 check (reminder_minutes_before between 0 and 1440),
  notes text not null default '',
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(athlete_id,weekday)
);

create table if not exists public.athlete_reminders (
  id uuid primary key default gen_random_uuid(),
  athlete_id uuid not null references public.athletes(id) on delete cascade,
  coach_id uuid not null references public.profiles(id) on delete cascade,
  title text not null,
  body text not null default '',
  category text not null default 'custom',
  schedule_type text not null default 'once' check (schedule_type in ('once','weekly')),
  reminder_date date,
  weekday smallint check (weekday between 0 and 6),
  remind_time time,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (
    (schedule_type='once' and reminder_date is not null)
    or (schedule_type='weekly' and weekday is not null)
  )
);

create table if not exists public.body_measurements (
  id uuid primary key default gen_random_uuid(),
  student_id uuid references public.profiles(id) on delete cascade,
  measured_on date not null default current_date,
  weight_kg numeric check (weight_kg is null or weight_kg between 20 and 400),
  waist_cm numeric check (waist_cm is null or waist_cm between 20 and 300),
  abdomen_cm numeric check (abdomen_cm is null or abdomen_cm between 20 and 300),
  hip_cm numeric check (hip_cm is null or hip_cm between 20 and 300),
  chest_cm numeric check (chest_cm is null or chest_cm between 20 and 300),
  arm_left_cm numeric check (arm_left_cm is null or arm_left_cm between 10 and 100),
  arm_right_cm numeric check (arm_right_cm is null or arm_right_cm between 10 and 100),
  thigh_left_cm numeric check (thigh_left_cm is null or thigh_left_cm between 15 and 150),
  thigh_right_cm numeric check (thigh_right_cm is null or thigh_right_cm between 15 and 150),
  notes text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  athlete_id uuid references public.athletes(id) on delete cascade,
  unique(student_id,measured_on),
  unique(athlete_id,measured_on)
);

create table if not exists public.weekly_checkins (
  id uuid primary key default gen_random_uuid(),
  student_id uuid references public.profiles(id) on delete cascade,
  week_start date not null default (date_trunc('week',current_date)::date),
  weight_kg numeric check (weight_kg is null or weight_kg between 20 and 400),
  sleep_quality smallint not null check (sleep_quality between 1 and 10),
  stress_level smallint not null check (stress_level between 1 and 10),
  energy_level smallint not null check (energy_level between 1 and 10),
  adherence_level smallint not null check (adherence_level between 1 and 10),
  mood_level smallint not null check (mood_level between 1 and 10),
  hunger_level smallint check (hunger_level is null or hunger_level between 1 and 10),
  recovery_level smallint check (recovery_level is null or recovery_level between 1 and 10),
  motivation_level smallint check (motivation_level is null or motivation_level between 1 and 10),
  notes text not null default '',
  coach_feedback text not null default '',
  submitted_at timestamptz not null default now(),
  reviewed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  athlete_id uuid references public.athletes(id) on delete cascade,
  unique(student_id,week_start),
  unique(athlete_id,week_start)
);

create table if not exists public.coach_media_settings (
  coach_id uuid primary key references public.profiles(id) on delete cascade,
  spotify_url text,
  spotify_title text,
  updated_at timestamptz not null default now()
);

create table if not exists public.exercise_media (
  id uuid primary key default gen_random_uuid(),
  coach_id uuid not null references public.profiles(id) on delete cascade,
  exercise_key text not null,
  title text not null default 'Video técnico',
  video_url text,
  storage_path text,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(coach_id,exercise_key)
);

create table if not exists public.fitness_recipes (
  id uuid primary key default gen_random_uuid(),
  coach_id uuid references public.profiles(id) on delete cascade,
  is_global boolean not null default false,
  title text not null,
  category text not null,
  description text not null default '',
  prep_minutes integer,
  servings integer not null default 1,
  ingredients jsonb not null default '[]'::jsonb,
  steps jsonb not null default '[]'::jsonb,
  kcal numeric,
  protein_g numeric,
  carbs_g numeric,
  fat_g numeric,
  tags text[] not null default '{}'::text[],
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.nutrition_habit_logs (
  id uuid primary key default gen_random_uuid(),
  athlete_id uuid not null references public.athletes(id) on delete cascade,
  student_id uuid references public.profiles(id) on delete set null,
  habit_id text not null,
  logged_on date not null default current_date,
  completed boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(athlete_id,habit_id,logged_on)
);

create table if not exists public.nutrition_plan_revisions (
  id uuid primary key default gen_random_uuid(),
  plan_id uuid not null references public.nutrition_plans(id) on delete cascade,
  athlete_id uuid not null references public.athletes(id) on delete cascade,
  coach_id uuid not null references public.profiles(id) on delete cascade,
  revision integer not null,
  title text not null,
  notes text not null default '',
  target_kcal numeric,
  target_protein_g numeric,
  target_carbs_g numeric,
  target_fat_g numeric,
  plan jsonb not null,
  created_at timestamptz not null default now(),
  student_logging_enabled boolean not null default true,
  unique(plan_id,revision)
);

create table if not exists public.nutrition_templates (
  id uuid primary key default gen_random_uuid(),
  coach_id uuid not null references public.profiles(id) on delete cascade,
  name text not null,
  description text not null default '',
  title text not null default 'Plan nutricional',
  notes text not null default '',
  target_kcal numeric,
  target_protein_g numeric,
  target_carbs_g numeric,
  target_fat_g numeric,
  plan jsonb not null default '{"meals":[]}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(coach_id,name)
);

create table if not exists public.progress_photos (
  id uuid primary key default gen_random_uuid(),
  student_id uuid references public.profiles(id) on delete cascade,
  taken_on date not null default current_date,
  pose text not null check (pose in ('front','side','back','other')),
  storage_path text not null,
  notes text not null default '',
  created_at timestamptz not null default now(),
  athlete_id uuid references public.athletes(id) on delete cascade,
  unique(student_id,taken_on,pose),
  unique(athlete_id,taken_on,pose)
);

create table if not exists public.checkin_schedules (
  id uuid primary key default gen_random_uuid(),
  athlete_id uuid not null unique references public.athletes(id) on delete cascade,
  coach_id uuid not null references public.profiles(id) on delete cascade,
  cadence text not null check (cadence in ('once','weekly','biweekly','monthly')),
  next_due date not null,
  remind_time time,
  active boolean not null default true,
  notes text not null default '',
  last_completed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.coach_payments (
  id uuid primary key default gen_random_uuid(),
  athlete_id uuid not null references public.athletes(id) on delete cascade,
  coach_id uuid not null references public.profiles(id) on delete cascade,
  due_date date not null,
  amount numeric,
  status text not null default 'pending' check (status in ('pending','paid','cancelled')),
  paid_on date,
  payment_method text check (payment_method is null or payment_method in ('cash','transfer','other')),
  note text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.student_notices (
  id uuid primary key default gen_random_uuid(),
  athlete_id uuid not null references public.athletes(id) on delete cascade,
  coach_id uuid not null references public.profiles(id) on delete cascade,
  title text not null,
  body text not null default '',
  priority text not null default 'info' check (priority in ('info','important')),
  active boolean not null default true,
  expires_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Useful local parity indexes.
create index if not exists athlete_schedule_athlete_idx on public.athlete_schedule(athlete_id,weekday);
create index if not exists athlete_reminders_athlete_idx on public.athlete_reminders(athlete_id,active);
create index if not exists body_measurements_athlete_date_idx on public.body_measurements(athlete_id,measured_on desc);
create index if not exists weekly_checkins_athlete_week_idx on public.weekly_checkins(athlete_id,week_start desc);
create index if not exists nutrition_habit_logs_athlete_date_idx on public.nutrition_habit_logs(athlete_id,logged_on desc);
create index if not exists progress_photos_athlete_date_idx on public.progress_photos(athlete_id,taken_on desc);
create index if not exists coach_payments_coach_due_idx on public.coach_payments(coach_id,due_date);
create index if not exists student_notices_athlete_active_idx on public.student_notices(athlete_id,active,created_at desc);

-- RLS parity helpers.
alter table public.athlete_schedule enable row level security;
alter table public.athlete_reminders enable row level security;
alter table public.body_measurements enable row level security;
alter table public.weekly_checkins enable row level security;
alter table public.coach_media_settings enable row level security;
alter table public.exercise_media enable row level security;
alter table public.fitness_recipes enable row level security;
alter table public.nutrition_habit_logs enable row level security;
alter table public.nutrition_plan_revisions enable row level security;
alter table public.nutrition_templates enable row level security;
alter table public.progress_photos enable row level security;
alter table public.checkin_schedules enable row level security;
alter table public.coach_payments enable row level security;
alter table public.student_notices enable row level security;

create policy athlete_schedule_select_access on public.athlete_schedule for select to authenticated
using (public.can_access_athlete(athlete_id));
create policy athlete_schedule_insert_coach on public.athlete_schedule for insert to authenticated
with check (coach_id=(select auth.uid()) and public.can_edit_athlete_as_coach(athlete_id));
create policy athlete_schedule_update_coach on public.athlete_schedule for update to authenticated
using (coach_id=(select auth.uid()) and public.can_edit_athlete_as_coach(athlete_id))
with check (coach_id=(select auth.uid()) and public.can_edit_athlete_as_coach(athlete_id));
create policy athlete_schedule_delete_coach on public.athlete_schedule for delete to authenticated
using (coach_id=(select auth.uid()) and public.can_edit_athlete_as_coach(athlete_id));

create policy athlete_reminders_select_access on public.athlete_reminders for select to authenticated
using (public.can_access_athlete(athlete_id));
create policy athlete_reminders_insert_coach on public.athlete_reminders for insert to authenticated
with check (coach_id=(select auth.uid()) and public.can_edit_athlete_as_coach(athlete_id));
create policy athlete_reminders_update_coach on public.athlete_reminders for update to authenticated
using (coach_id=(select auth.uid()) and public.can_edit_athlete_as_coach(athlete_id))
with check (coach_id=(select auth.uid()) and public.can_edit_athlete_as_coach(athlete_id));
create policy athlete_reminders_delete_coach on public.athlete_reminders for delete to authenticated
using (coach_id=(select auth.uid()) and public.can_edit_athlete_as_coach(athlete_id));

create policy body_measurements_select_access on public.body_measurements for select to authenticated
using (
  student_id=(select auth.uid())
  or (student_id is not null and public.is_coach_of(student_id))
  or (athlete_id is not null and public.can_access_athlete(athlete_id))
);
create policy body_measurements_insert_access on public.body_measurements for insert to authenticated
with check (
  student_id=(select auth.uid())
  or (athlete_id is not null and public.can_edit_athlete_as_coach(athlete_id))
);
create policy body_measurements_update_access on public.body_measurements for update to authenticated
using (
  student_id=(select auth.uid())
  or (athlete_id is not null and public.can_edit_athlete_as_coach(athlete_id))
)
with check (
  student_id=(select auth.uid())
  or (athlete_id is not null and public.can_edit_athlete_as_coach(athlete_id))
);
create policy body_measurements_delete_coach on public.body_measurements for delete to authenticated
using (athlete_id is not null and public.can_edit_athlete_as_coach(athlete_id));

create policy weekly_checkins_select_access on public.weekly_checkins for select to authenticated
using (
  student_id=(select auth.uid())
  or (student_id is not null and public.is_coach_of(student_id))
  or (athlete_id is not null and public.can_access_athlete(athlete_id))
);
create policy weekly_checkins_insert_student on public.weekly_checkins for insert to authenticated
with check (student_id=(select auth.uid()) and public.can_access_athlete(athlete_id));
create policy weekly_checkins_update_access on public.weekly_checkins for update to authenticated
using (
  student_id=(select auth.uid())
  or (athlete_id is not null and public.can_edit_athlete_as_coach(athlete_id))
)
with check (
  student_id=(select auth.uid())
  or (athlete_id is not null and public.can_edit_athlete_as_coach(athlete_id))
);

create policy coach_media_settings_select_linked on public.coach_media_settings for select to authenticated
using (
  coach_id=(select auth.uid())
  or exists(
    select 1 from public.coach_students cs
    where cs.coach_id=coach_media_settings.coach_id
      and cs.student_id=(select auth.uid()) and cs.status='active'
  )
);
create policy coach_media_settings_write_self on public.coach_media_settings for all to authenticated
using (coach_id=(select auth.uid()) and public.current_profile_role()='coach')
with check (coach_id=(select auth.uid()) and public.current_profile_role()='coach');

create policy exercise_media_select_linked on public.exercise_media for select to authenticated
using (
  coach_id=(select auth.uid())
  or exists(
    select 1 from public.coach_students cs
    where cs.coach_id=exercise_media.coach_id
      and cs.student_id=(select auth.uid()) and cs.status='active'
  )
);
create policy exercise_media_write_coach on public.exercise_media for all to authenticated
using (coach_id=(select auth.uid()) and public.current_profile_role()='coach')
with check (coach_id=(select auth.uid()) and public.current_profile_role()='coach');

create policy fitness_recipes_select_access on public.fitness_recipes for select to authenticated
using (
  is_global=true or coach_id=(select auth.uid())
  or exists(
    select 1 from public.coach_students cs
    where cs.coach_id=fitness_recipes.coach_id
      and cs.student_id=(select auth.uid()) and cs.status='active'
  )
);
create policy fitness_recipes_write_coach on public.fitness_recipes for all to authenticated
using (coach_id=(select auth.uid()) and is_global=false and public.current_profile_role()='coach')
with check (coach_id=(select auth.uid()) and is_global=false and public.current_profile_role()='coach');

create policy nutrition_habit_logs_select_access on public.nutrition_habit_logs for select to authenticated
using (public.can_access_athlete(athlete_id));
create policy nutrition_habit_logs_insert_access on public.nutrition_habit_logs for insert to authenticated
with check (
  (student_id=(select auth.uid()) and public.can_access_athlete(athlete_id))
  or public.can_edit_athlete_as_coach(athlete_id)
);
create policy nutrition_habit_logs_update_access on public.nutrition_habit_logs for update to authenticated
using (
  student_id=(select auth.uid()) or public.can_edit_athlete_as_coach(athlete_id)
)
with check (
  student_id=(select auth.uid()) or public.can_edit_athlete_as_coach(athlete_id)
);
create policy nutrition_habit_logs_delete_access on public.nutrition_habit_logs for delete to authenticated
using (student_id=(select auth.uid()) or public.can_edit_athlete_as_coach(athlete_id));

create policy nutrition_plan_revisions_select_access on public.nutrition_plan_revisions for select to authenticated
using (public.can_access_athlete(athlete_id));

create policy nutrition_templates_select_coach on public.nutrition_templates for select to authenticated
using (coach_id=(select auth.uid()) and public.current_profile_role()='coach');
create policy nutrition_templates_write_coach on public.nutrition_templates for all to authenticated
using (coach_id=(select auth.uid()) and public.current_profile_role()='coach')
with check (coach_id=(select auth.uid()) and public.current_profile_role()='coach');

create policy progress_photos_select_access on public.progress_photos for select to authenticated
using (
  student_id=(select auth.uid())
  or (student_id is not null and public.is_coach_of(student_id))
  or (athlete_id is not null and public.can_access_athlete(athlete_id))
);
create policy progress_photos_insert_access on public.progress_photos for insert to authenticated
with check (
  student_id=(select auth.uid())
  or (athlete_id is not null and public.can_edit_athlete_as_coach(athlete_id))
);
create policy progress_photos_update_access on public.progress_photos for update to authenticated
using (
  student_id=(select auth.uid())
  or (athlete_id is not null and public.can_edit_athlete_as_coach(athlete_id))
)
with check (
  student_id=(select auth.uid())
  or (athlete_id is not null and public.can_edit_athlete_as_coach(athlete_id))
);
create policy progress_photos_delete_access on public.progress_photos for delete to authenticated
using (
  student_id=(select auth.uid())
  or (athlete_id is not null and public.can_edit_athlete_as_coach(athlete_id))
);

create policy checkin_schedules_select_access on public.checkin_schedules for select to authenticated
using (public.can_access_athlete(athlete_id));
create policy checkin_schedules_write_coach on public.checkin_schedules for all to authenticated
using (coach_id=(select auth.uid()) and public.can_edit_athlete_as_coach(athlete_id))
with check (coach_id=(select auth.uid()) and public.can_edit_athlete_as_coach(athlete_id));

create policy coach_payments_select_access on public.coach_payments for select to authenticated
using (public.can_access_athlete(athlete_id));
create policy coach_payments_write_coach on public.coach_payments for all to authenticated
using (coach_id=(select auth.uid()) and public.can_edit_athlete_as_coach(athlete_id))
with check (coach_id=(select auth.uid()) and public.can_edit_athlete_as_coach(athlete_id));

create policy student_notices_select_access on public.student_notices for select to authenticated
using (
  coach_id=(select auth.uid())
  or exists(
    select 1 from public.athletes a
    where a.id=student_notices.athlete_id and a.user_id=(select auth.uid())
  )
);
create policy student_notices_write_coach on public.student_notices for all to authenticated
using (coach_id=(select auth.uid()) and public.can_edit_athlete_as_coach(athlete_id))
with check (coach_id=(select auth.uid()) and public.can_edit_athlete_as_coach(athlete_id));

grant select,insert,update,delete on
  public.athlete_schedule,public.athlete_reminders,public.body_measurements,
  public.weekly_checkins,public.coach_media_settings,public.exercise_media,
  public.fitness_recipes,public.nutrition_habit_logs,public.nutrition_plan_revisions,
  public.nutrition_templates,public.progress_photos,public.checkin_schedules,
  public.coach_payments,public.student_notices
to authenticated;

-- Same public RPC contract as production. Local sources are genuine local
-- tables/fixtures; no hosted project is queried.
create or replace function public.get_coach_feed()
returns table(
  event_key text,
  athlete_id uuid,
  athlete_name text,
  kind text,
  severity text,
  title text,
  body text,
  occurred_at timestamptz,
  is_read boolean
)
language sql
stable
security definer
set search_path to 'public','pg_temp'
as $$
  with me as (
    select auth.uid() as uid
  ),
  allowed as (
    select a.id,a.name
    from public.athletes a,me
    where me.uid is not null and a.coach_id=me.uid
      and public.current_profile_role()='coach'
  ),
  raw as (
    select
      'feedback:'||ef.id::text as event_key,
      ef.athlete_id,
      a.name as athlete_name,
      'exercise_feedback'::text as kind,
      case when ef.feedback_type='discomfort' then 'important' else 'info' end as severity,
      case when ef.feedback_type='discomfort' then 'Molestia en ejercicio' else 'Comentario de ejercicio' end as title,
      ef.exercise_name||' · '||ef.message as body,
      ef.created_at as occurred_at
    from public.exercise_feedback ef
    join allowed a on a.id=ef.athlete_id
    where ef.status='pending'

    union all
    select
      'checkin:'||wc.id::text,
      wc.athlete_id,a.name,'weekly_checkin','info',
      'Check-in semanal',
      coalesce(nullif(wc.notes,''),'Nuevo check-in para revisar'),
      wc.submitted_at
    from public.weekly_checkins wc
    join allowed a on a.id=wc.athlete_id
    where wc.reviewed_at is null

    union all
    select
      'reminder:'||ar.id::text,
      ar.athlete_id,a.name,'reminder','info',
      ar.title,coalesce(nullif(ar.body,''),'Recordatorio activo'),ar.updated_at
    from public.athlete_reminders ar
    join allowed a on a.id=ar.athlete_id
    where ar.active=true

    union all
    select
      'payment:'||cp.id::text,
      cp.athlete_id,a.name,'payment',
      case when cp.due_date<current_date then 'important' else 'info' end,
      'Cobranza',
      'Vence '||cp.due_date::text||' · '||cp.status,
      cp.updated_at
    from public.coach_payments cp
    join allowed a on a.id=cp.athlete_id
    where cp.status='pending'
  )
  select
    r.event_key,r.athlete_id,r.athlete_name,r.kind,r.severity,r.title,r.body,r.occurred_at,
    (cfs.read_at is not null) as is_read
  from raw r
  left join public.coach_feed_state cfs
    on cfs.coach_id=(select uid from me) and cfs.event_key=r.event_key
  where cfs.dismissed_at is null
  order by r.occurred_at desc
  limit 100;
$$;

revoke all on function public.get_coach_feed() from public;
grant execute on function public.get_coach_feed() to authenticated;

do $$ begin
  alter publication supabase_realtime add table public.athlete_schedule;
exception when duplicate_object then null; end $$;
do $$ begin
  alter publication supabase_realtime add table public.athlete_reminders;
exception when duplicate_object then null; end $$;
do $$ begin
  alter publication supabase_realtime add table public.weekly_checkins;
exception when duplicate_object then null; end $$;
do $$ begin
  alter publication supabase_realtime add table public.body_measurements;
exception when duplicate_object then null; end $$;
