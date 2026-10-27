-- TEAM FJZ V21.22 · server review authority
-- Canonical coach feed must not recycle the legacy 14-day weekly repeated-review aggregate.
-- Applied to production through Supabase execute_sql and retained here for repository history.

do $$
declare
  fn_oid oid;
  def text;
  patched text;
begin
  select p.oid into fn_oid
  from pg_proc p
  join pg_namespace n on n.oid=p.pronamespace
  where n.nspname='public'
    and p.proname='get_coach_feed'
    and pg_get_function_identity_arguments(p.oid)='';

  if fn_oid is null then
    raise exception 'get_coach_feed() not found';
  end if;

  def:=pg_get_functiondef(fn_oid);
  if position('event_key not like ''repeated-review:%''' in def)>0 then
    return;
  end if;

  patched:=replace(
    def,
    E'where event_key not like ''pending-checkin:%''',
    E'where event_key not like ''pending-checkin:%''\\n    and event_key not like ''repeated-review:%'''
  );

  if patched=def then
    raise exception 'get_coach_feed legacy filter anchor not found';
  end if;

  execute patched;
end $$;

update public.coach_feed_state
set read_at=coalesce(read_at,now()),
    dismissed_at=coalesce(dismissed_at,now())
where event_key like 'repeated-review:%'
  and dismissed_at is null;
