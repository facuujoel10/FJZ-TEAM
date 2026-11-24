create table public.checkin_reminder_rules (
  athlete_id uuid references public.athletes on delete cascade,
  kind text check (kind in ('weekly','monthly')),
  first_day date not null,
  local_time time not null check (local_time between time '08:00' and time '20:00'),
  enabled boolean not null default false,
  primary key (athlete_id, kind)
);
create table public.checkin_push_devices (
  athlete_id uuid primary key references public.athletes on delete cascade,
  owner_id uuid not null default auth.uid(),
  endpoint text unique not null check(length(endpoint) <= 2048),
  p256dh text not null check(length(p256dh) between 80 and 100),
  auth_key text not null check(length(auth_key) between 20 and 30)
);
create table public.checkin_push_attempts (
  athlete_id uuid references public.athletes on delete cascade,
  kind text not null, period date not null, attempted_at timestamptz default now(),
  primary key (athlete_id,kind,period)
);
alter table public.checkin_reminder_rules enable row level security;
alter table public.checkin_push_devices enable row level security;
alter table public.checkin_push_attempts enable row level security;
revoke all on public.checkin_reminder_rules,public.checkin_push_devices,public.checkin_push_attempts from anon,authenticated;
grant select,insert,update on public.checkin_reminder_rules to authenticated;
grant select,insert,update,delete on public.checkin_push_devices to authenticated;
create policy coach_programs on public.checkin_reminder_rules for all to authenticated
 using(exists(select 1 from public.athletes a where a.id=athlete_id and a.coach_id=auth.uid()))
 with check(exists(select 1 from public.athletes a where a.id=athlete_id and a.coach_id=auth.uid()));
create policy student_reads_plan on public.checkin_reminder_rules for select to authenticated
 using(exists(select 1 from public.athletes a where a.id=athlete_id and a.user_id=auth.uid()));
create policy own_push_device on public.checkin_push_devices for all to authenticated
 using(owner_id=auth.uid() and exists(select 1 from public.athletes a where a.id=athlete_id and a.user_id=auth.uid()))
 with check(owner_id=auth.uid() and exists(select 1 from public.athletes a where a.id=athlete_id and a.user_id=auth.uid()));
