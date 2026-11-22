create table public.step_targets(athlete_id uuid primary key references public.athletes on delete cascade, target integer not null check(target between 1 and 150000));
create table public.daily_steps(athlete_id uuid references public.athletes on delete cascade, day date not null, steps integer not null check(steps between 0 and 150000), primary key(athlete_id,day));
alter table public.step_targets enable row level security;
alter table public.daily_steps enable row level security;
create policy target_read on public.step_targets for select to authenticated using(exists(select 1 from public.athletes a where a.id=athlete_id and auth.uid() in(a.coach_id,a.user_id)));
create policy target_write on public.step_targets for all to authenticated using(exists(select 1 from public.athletes a where a.id=athlete_id and a.coach_id=auth.uid())) with check(exists(select 1 from public.athletes a where a.id=athlete_id and a.coach_id=auth.uid()));
create policy steps_read on public.daily_steps for select to authenticated using(exists(select 1 from public.athletes a where a.id=athlete_id and auth.uid() in(a.coach_id,a.user_id)));
create policy steps_write on public.daily_steps for all to authenticated using(exists(select 1 from public.athletes a where a.id=athlete_id and a.user_id=auth.uid())) with check(exists(select 1 from public.athletes a where a.id=athlete_id and a.user_id=auth.uid()));
grant select,insert,update on public.step_targets,public.daily_steps to authenticated;
