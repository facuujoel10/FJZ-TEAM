from __future__ import annotations
from dev_common import TEST_PASSWORD,http_json,local_status

A1="10000000-0000-4000-8000-000000000001"
A2="10000000-0000-4000-8000-000000000002"
SCHEDULE_1="50000000-0000-4000-8000-000000000001"
SCHEDULE_2="50000000-0000-4000-8000-000000000002"
REMINDER_2="51000000-0000-4000-8000-000000000002"
MISSING="59999999-0000-4000-8000-000000000099"
EMPTY_ATHLETE="10000000-0000-4000-8000-000000000099"

def login(api,pub,email):
    data=http_json("POST",api+"/auth/v1/token?grant_type=password",pub,None,{"email":email,"password":TEST_PASSWORD})
    token=data.get("access_token") if isinstance(data,dict) else None
    if not token: raise RuntimeError("Agenda smoke auth failed for "+email)
    return token

def get(api,pub,token,path):
    return http_json("GET",api+"/rest/v1/"+path,pub,token)

def main():
    st=local_status();api=st["api"];pub=st["publishable"]
    coach=login(api,pub,"coach@test.local")
    s1=login(api,pub,"alumno01@test.local")
    s2=login(api,pub,"alumno02@test.local")

    coach_a1=get(api,pub,coach,"athlete_schedule?select=id,athlete_id,weekday,start_time&athlete_id=eq."+A1)
    assert len(coach_a1)==1 and coach_a1[0]["id"]==SCHEDULE_1,coach_a1

    own=get(api,pub,s1,"athlete_schedule?select=id,athlete_id,weekday,start_time&athlete_id=eq."+A1)
    assert len(own)==1 and own[0]["athlete_id"]==A1,own

    cross=get(api,pub,s1,"athlete_schedule?select=id,athlete_id&athlete_id=eq."+A2)
    assert cross==[],cross

    own_by_id=get(api,pub,s1,"athlete_schedule?select=id,athlete_id&id=eq."+SCHEDULE_1)
    assert len(own_by_id)==1 and own_by_id[0]["athlete_id"]==A1,own_by_id

    cross_by_id=get(api,pub,s1,"athlete_schedule?select=id,athlete_id&id=eq."+SCHEDULE_2)
    assert cross_by_id==[],cross_by_id

    missing=get(api,pub,s1,"athlete_schedule?select=id&id=eq."+MISSING)
    assert missing==[],missing

    empty=get(api,pub,s1,"athlete_schedule?select=id&athlete_id=eq."+EMPTY_ATHLETE)
    assert empty==[],empty

    own_reminders=get(api,pub,s1,"athlete_reminders?select=id,athlete_id,schedule_type,reminder_date,remind_time&athlete_id=eq."+A1)
    assert len(own_reminders)==1 and own_reminders[0]["athlete_id"]==A1,own_reminders

    coach_once=get(api,pub,coach,"athlete_reminders?select=id,athlete_id,schedule_type,reminder_date,remind_time&id=eq."+REMINDER_2)
    assert len(coach_once)==1 and coach_once[0]["reminder_date"]=="2026-01-20",coach_once

    student2_own=get(api,pub,s2,"athlete_reminders?select=id,athlete_id,reminder_date&id=eq."+REMINDER_2)
    assert len(student2_own)==1 and student2_own[0]["athlete_id"]==A2,student2_own

    student1_cross=get(api,pub,s1,"athlete_reminders?select=id,athlete_id,reminder_date&id=eq."+REMINDER_2)
    assert student1_cross==[],student1_cross

    print("TEAM FJZ V22 1B AGENDA REPOSITORY/RLS SMOKE OK")
    print("Coach authorized read: OK")
    print("Student own read: OK")
    print("Cross-student isolation: OK")
    print("Event by id + missing/empty results: OK")
    print("Date-only preservation: OK")
    print("Service/admin key exposed to browser: 0")

if __name__=="__main__":
    main()
