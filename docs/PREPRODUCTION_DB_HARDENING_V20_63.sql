-- TEAM FJZ V20.63 — PREPRODUCTION DATABASE HARDENING
-- PREPARED ONLY. Do not auto-apply from build.py.
-- Apply during the production release window after a final staging check.

-- Limit the SECURITY DEFINER helper so an authenticated caller can only ask
-- whether THEY are linked to the other supplied profile. This preserves the
-- current profiles RLS call: are_linked(auth.uid(), id).
create or replace function public.are_linked(a uuid, b uuid)
returns boolean
language sql
stable
security definer
set search_path = public, pg_temp
as $$
  select
    auth.uid() is not null
    and (a = auth.uid() or b = auth.uid())
    and exists (
      select 1
      from public.coach_students cs
      where cs.status = 'active'
        and (
          (cs.coach_id = a and cs.student_id = b)
          or
          (cs.coach_id = b and cs.student_id = a)
        )
    );
$$;

-- Keep direct anonymous RPC access disabled.
revoke execute on function public.are_linked(uuid,uuid) from public, anon;
grant execute on function public.are_linked(uuid,uuid) to authenticated;

-- Verification query after applying:
-- select public.are_linked(auth.uid(), auth.uid());
