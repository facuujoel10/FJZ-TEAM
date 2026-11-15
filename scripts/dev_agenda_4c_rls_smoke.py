from __future__ import annotations
from dev_common import local_status
from dev_comment_repository_smoke import login,rest
A1="10000000-0000-4000-8000-000000000001"
A2="10000000-0000-4000-8000-000000000002"
DATE="2026-12-31"
def main():
    st=local_status();api=st["api"];pub=st["publishable"]
    coach=login(api,pub,"coach@test.local");s1=login(api,pub,"alumno01@test.local");s2=login(api,pub,"alumno02@test.local");out=login(api,pub,"outsider-coach@test.local")
    # Existing weekly schedule must be visible to owner + coach and isolated from another student.
    own=rest(api,pub,s1,"GET","athlete_schedule?select=id,athlete_id,weekday,start_time&athlete_id=eq."+A1)
    assert own and own[0]["athlete_id"]==A1,own
    assert rest(api,pub,s2,"GET","athlete_schedule?select=id&athlete_id=eq."+A1)==[]
    # Create a real one-off agenda event through the same table used by the app.
    payload={"athlete_id":A1,"title":"QA 4C seguimiento","body":"Evento local ficticio","category":"custom","schedule_type":"once","reminder_date":DATE,"remind_time":"17:00","active":True}
    created=rest(api,pub,coach,"POST","athlete_reminders",payload,prefer="return=representation")
    assert len(created)==1,created
    rid=created[0]["id"]
    # Coach and intended student recover the same event; other identities cannot.
    cr=rest(api,pub,coach,"GET","athlete_reminders?select=id,athlete_id,title,reminder_date,remind_time&id=eq."+rid)
    sr=rest(api,pub,s1,"GET","athlete_reminders?select=id,athlete_id,title,reminder_date,remind_time&id=eq."+rid)
    assert len(cr)==1 and len(sr)==1 and sr[0]["reminder_date"]==DATE and str(sr[0]["remind_time"]).startswith("17:00"),(cr,sr)
    assert rest(api,pub,s2,"GET","athlete_reminders?select=id&id=eq."+rid)==[]
    assert rest(api,pub,out,"GET","athlete_reminders?select=id&id=eq."+rid)==[]
    # Edit must be visible after a new read and must keep date-only semantics.
    updated=rest(api,pub,coach,"PATCH","athlete_reminders?id=eq."+rid,{"title":"QA 4C seguimiento editado","remind_time":"18:15"},prefer="return=representation")
    assert len(updated)==1 and updated[0]["title"].endswith("editado"),updated
    sr2=rest(api,pub,s1,"GET","athlete_reminders?select=id,title,reminder_date,remind_time&id=eq."+rid)
    assert len(sr2)==1 and sr2[0]["reminder_date"]==DATE and str(sr2[0]["remind_time"]).startswith("18:15"),sr2
    # Delete must be durable and disappear for both roles.
    rest(api,pub,coach,"DELETE","athlete_reminders?id=eq."+rid,prefer="return=representation")
    assert rest(api,pub,coach,"GET","athlete_reminders?select=id&id=eq."+rid)==[]
    assert rest(api,pub,s1,"GET","athlete_reminders?select=id&id=eq."+rid)==[]
    print("TEAM FJZ V22 4C AGENDA AUTH/RLS + SYNC SMOKE OK")
    print("Coach -> student visibility: OK")
    print("Cross-student isolation: OK")
    print("Unauthorized coach isolation: OK")
    print("Date-only + local time preservation: OK")
    print("Edit rehydration + durable delete: OK")
    print("Production data copied: 0")
if __name__=="__main__":main()
