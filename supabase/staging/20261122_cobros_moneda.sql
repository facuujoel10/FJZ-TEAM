alter table public.coach_payments add column currency text not null default 'ARS'
  check (currency in ('ARS','EUR'));
