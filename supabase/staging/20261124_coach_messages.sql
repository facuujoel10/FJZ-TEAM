create table public.coach_messages (
 id uuid primary key, athlete_id uuid not null references public.athletes on delete cascade,
 recipient_id uuid not null, sender_id uuid not null default auth.uid(),
 body text not null check(length(trim(body)) between 1 and 1500),
 created_at timestamptz not null default now(), push_claimed_at timestamptz
);
create index coach_messages_inbox on public.coach_messages(athlete_id,created_at desc);
alter table public.coach_messages enable row level security;
revoke all on public.coach_messages from anon,authenticated;
grant select(id,athlete_id,recipient_id,sender_id,body,created_at),insert(id,athlete_id,recipient_id,body) on public.coach_messages to authenticated;
create policy write_own_message on public.coach_messages for insert to authenticated with check (
 sender_id=auth.uid() and exists(select 1 from public.athletes a where a.id=athlete_id and a.coach_id=auth.uid() and a.user_id=recipient_id));
create policy read_own_message on public.coach_messages for select to authenticated using (
 exists(select 1 from public.athletes a where a.id=athlete_id and a.user_id=recipient_id and
 (auth.uid()=recipient_id or (auth.uid()=sender_id and a.coach_id=sender_id))));
