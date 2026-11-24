"""Run every five minutes with the staging database and dedicated VAPID credentials."""
import json
import os
from urllib.parse import urlsplit

DUE = """
with clock as (select current_timestamp at time zone 'America/Argentina/Buenos_Aires' as t),
scheduled as (
 select r.*,t,t::date as day,
 case when kind='weekly' then date_trunc('week',t)::date else date_trunc('month',t)::date end as period
 from public.checkin_reminder_rules r cross join clock
 where enabled and first_day<=t::date
 and t >= t::date + local_time and t < t::date + local_time + interval '30 minutes'
 and case when kind='weekly' then (t::date-first_day)%7=0 else
 extract(day from t)=least(extract(day from first_day),extract(day from date_trunc('month',t)+interval '1 month - 1 day')) end
)
select s.athlete_id,s.kind,s.period,d.endpoint,d.p256dh,d.auth_key
from scheduled s join public.athletes a on a.id=s.athlete_id
join public.checkin_push_devices d on d.athlete_id=a.id and d.owner_id=a.user_id
where not exists (select 1 from public.checkin_push_attempts p where (p.athlete_id,p.kind,p.period)=(s.athlete_id,s.kind,s.period))
and case when s.kind='weekly' then not exists(select 1 from public.weekly_checkins w where w.athlete_id=s.athlete_id and w.week_start=s.period)
else not exists(select 1 from public.body_measurements m where m.athlete_id=s.athlete_id and m.measured_on between s.period and s.day) end
"""

def supported(endpoint):
    url = urlsplit(endpoint)
    return (url.scheme == 'https' and url.netloc in
            {'fcm.googleapis.com', 'web.push.apple.com', 'updates.push.services.mozilla.com'}
            and url.path.startswith('/') and len(url.path)>1 and not url.fragment)

def main():
    import psycopg
    from pywebpush import webpush, WebPushException
    key, subject = os.environ['FJZ_VAPID_PRIVATE_KEY'], os.environ['FJZ_VAPID_SUBJECT']
    with psycopg.connect(os.environ['FJZ_STAGING_DATABASE_URL'], autocommit=True) as db:
        # Claim only rows still eligible, in one transaction. Overlapping ticks
        # cannot dispatch the same athlete, reminder and period twice.
        claim = """with due as (""" + DUE + """), claimed as (
            insert into public.checkin_push_attempts(athlete_id,kind,period)
            select athlete_id,kind,period from due on conflict do nothing
            returning athlete_id,kind,period)
            select due.* from due join claimed using(athlete_id,kind,period)"""
        messages = """with pending as (
            update public.coach_messages m set push_claimed_at=now()
            from public.checkin_push_devices d, public.athletes a
            where a.id=m.athlete_id and d.athlete_id=a.id and d.owner_id=a.user_id
              and m.recipient_id=a.user_id and m.sender_id=a.coach_id
              and m.push_claimed_at is null and m.created_at>now()-interval '15 minutes'
            returning m.athlete_id,'message',m.id,d.endpoint,d.p256dh,d.auth_key)
            select * from pending"""
        deliveries=db.execute(claim).fetchall()+db.execute(messages).fetchall()
        for athlete,kind,period,endpoint,p256dh,auth in deliveries:
            if not supported(endpoint):
                continue
            try:
                webpush(subscription_info={'endpoint':endpoint,'keys':{'auth':auth,'p256dh':p256dh}},
                        data=json.dumps({'kind':kind,'period':str(period)}),vapid_private_key=key,
                        vapid_claims={'sub':subject},ttl=900,timeout=10)
            except WebPushException as error:
                status=getattr(error.response,'status_code',None)
                if status in (404,410):
                    db.execute("delete from public.checkin_push_devices where athlete_id=%s and endpoint=%s",(athlete,endpoint))
                print('Check-in push not confirmed:', status or 'network')
if __name__=='__main__':
    main()
