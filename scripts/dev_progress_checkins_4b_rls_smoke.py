from __future__ import annotations
from dev_common import local_status
from dev_comment_repository_smoke import login,rest
A1="10000000-0000-4000-8000-000000000001";A2="10000000-0000-4000-8000-000000000002";DATE="2026-11-13";WEEK="2026-12-28"
def main():
    st=local_status();api=st["api"];pub=st["publishable"]
    coach=login(api,pub,"coach@test.local");s1=login(api,pub,"alumno01@test.local");s2=login(api,pub,"alumno02@test.local");out=login(api,pub,"outsider-coach@test.local")
    uid=rest(api,pub,s1,"GET","athletes?select=user_id&id=eq."+A1)[0]["user_id"]
    m={"athlete_id":A1,"student_id":uid,"measured_on":DATE,"weight_kg":73.4,"waist_cm":81.2,"arm_left_cm":33.2,"thigh_left_cm":58.1}
    rest(api,pub,s1,"POST","body_measurements",m,prefer="resolution=merge-duplicates,return=representation")
    own=rest(api,pub,s1,"GET","body_measurements?select=*&athlete_id=eq."+A1+"&measured_on=eq."+DATE);assert len(own)==1 and float(own[0]["arm_left_cm"])==33.2,own
    assert rest(api,pub,s2,"GET","body_measurements?select=id&athlete_id=eq."+A1+"&measured_on=eq."+DATE)==[]
    assert rest(api,pub,out,"GET","body_measurements?select=id&athlete_id=eq."+A1+"&measured_on=eq."+DATE)==[]
    c={"athlete_id":A1,"student_id":uid,"week_start":WEEK,"weight_kg":73.4,"sleep_quality":8,"stress_level":4,"energy_level":8,"adherence_level":9,"mood_level":8,"hunger_level":5,"recovery_level":8,"motivation_level":9,"notes":"QA 4B local"}
    rest(api,pub,s1,"POST","weekly_checkins",c,prefer="resolution=merge-duplicates,return=representation")
    chk=rest(api,pub,coach,"GET","weekly_checkins?select=*&athlete_id=eq."+A1+"&week_start=eq."+WEEK);assert len(chk)==1 and chk[0]["notes"]=="QA 4B local",chk
    assert rest(api,pub,s2,"GET","weekly_checkins?select=id&athlete_id=eq."+A1+"&week_start=eq."+WEEK)==[]
    photo={"athlete_id":A1,"student_id":uid,"taken_on":DATE,"pose":"front","storage_path":A1+"/"+DATE+"/front_qa.jpg"}
    rest(api,pub,s1,"POST","progress_photos",photo,prefer="resolution=merge-duplicates,return=representation")
    assert len(rest(api,pub,coach,"GET","progress_photos?select=id,storage_path&athlete_id=eq."+A1+"&taken_on=eq."+DATE))==1
    assert rest(api,pub,s2,"GET","progress_photos?select=id&athlete_id=eq."+A1+"&taken_on=eq."+DATE)==[]
    rest(api,pub,coach,"DELETE","progress_photos?athlete_id=eq."+A1+"&taken_on=eq."+DATE);rest(api,pub,coach,"DELETE","weekly_checkins?athlete_id=eq."+A1+"&week_start=eq."+WEEK);rest(api,pub,coach,"DELETE","body_measurements?athlete_id=eq."+A1+"&measured_on=eq."+DATE)
    print("TEAM FJZ V22 4B PROGRESS/CHECKINS AUTH/RLS SMOKE OK");print("Measurement isolation: OK");print("Check-in isolation: OK");print("Progress-photo metadata isolation: OK");print("Production data copied: 0")
if __name__=="__main__":main()
