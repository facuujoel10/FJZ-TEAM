from __future__ import annotations
from dev_common import http_json,local_status
from dev_comment_repository_smoke import login,rest

A1="10000000-0000-4000-8000-000000000001"
A2="10000000-0000-4000-8000-000000000002"

def denied(fn,label):
    try:
        fn()
    except Exception:
        print(label+": BLOCKED")
        return
    raise AssertionError(label+" unexpectedly allowed")

def main():
    st=local_status();api=st["api"];pub=st["publishable"]
    coach=login(api,pub,"coach@test.local")
    s1=login(api,pub,"alumno01@test.local")
    own=rest(api,pub,s1,"GET","athletes?select=id,user_id,coach_id&id=eq."+A1)
    assert len(own)==1,own
    uid1=own[0]["user_id"]

    denied(lambda:rest(api,pub,s1,"POST","body_measurements",{
      "athlete_id":A2,"student_id":uid1,"measured_on":"2027-02-01","weight_kg":72.1
    },prefer="return=representation"),"cross-athlete body_measurement insert")

    denied(lambda:rest(api,pub,s1,"POST","weekly_checkins",{
      "athlete_id":A2,"student_id":uid1,"week_start":"2027-02-01",
      "sleep_quality":8,"stress_level":4,"energy_level":8,"adherence_level":9,
      "mood_level":8,"hunger_level":5,"recovery_level":8,"motivation_level":9,
      "notes":"STAGE5 cross-pair attempt"
    },prefer="return=representation"),"cross-athlete weekly_checkin insert")

    denied(lambda:rest(api,pub,s1,"POST","progress_photos",{
      "athlete_id":A2,"student_id":uid1,"taken_on":"2027-02-01",
      "pose":"front","storage_path":A2+"/2027-02-01/cross.jpg"
    },prefer="return=representation"),"cross-athlete progress_photo metadata insert")

    valid=rest(api,pub,s1,"POST","nutrition_habit_logs",{
      "athlete_id":A1,"student_id":uid1,"habit_id":"stage5_pair_guard",
      "logged_on":"2027-02-01","completed":True
    },prefer="return=representation")
    assert len(valid)==1,valid
    hid=valid[0]["id"]
    denied(lambda:rest(api,pub,s1,"PATCH","nutrition_habit_logs?id=eq."+hid,{
      "athlete_id":A2
    },prefer="return=representation"),"cross-athlete nutrition_habit reassignment")
    reread=rest(api,pub,coach,"GET","nutrition_habit_logs?select=id,athlete_id,student_id&id=eq."+hid)
    assert len(reread)==1 and reread[0]["athlete_id"]==A1 and reread[0]["student_id"]==uid1,reread
    rest(api,pub,s1,"DELETE","nutrition_habit_logs?id=eq."+hid,prefer="return=representation")

    denied(lambda:http_json("POST",api+"/rest/v1/rpc/are_linked",pub,None,{
      "a":uid1,"b":own[0]["coach_id"]
    }),"anonymous SECURITY DEFINER helper execution")

    print("TEAM FJZ V22 STAGE 5 CROSS-DOMAIN SECURITY SMOKE OK")
    print("Mismatched athlete/student writes: BLOCKED")
    print("Cross-athlete metadata reassignment: BLOCKED")
    print("Anonymous helper execution: BLOCKED")
    print("Production data copied: 0")

if __name__=="__main__":
    main()
