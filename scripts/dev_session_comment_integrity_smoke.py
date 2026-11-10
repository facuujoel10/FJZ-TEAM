from __future__ import annotations
from dev_common import TEST_PASSWORD,http_json,local_status
A1="10000000-0000-4000-8000-000000000001";A2="10000000-0000-4000-8000-000000000002"
def login(api,pub,email):
    d=http_json("POST",api+"/auth/v1/token?grant_type=password",pub,None,{"email":email,"password":TEST_PASSWORD})
    if not isinstance(d,dict) or not d.get("access_token"): raise RuntimeError("auth failed "+email)
    return d["access_token"]
def rest(api,pub,tok,method,path,payload=None,prefer=None):
    return http_json(method,api+"/rest/v1/"+path,pub,tok,payload,prefer=prefer)
def expect_denied(fn,label):
    try: fn()
    except Exception: return
    raise AssertionError(label+" unexpectedly allowed")
def main():
    st=local_status();api=st["api"];pub=st["publishable"]
    coach=login(api,pub,"coach@test.local");s1=login(api,pub,"alumno01@test.local");s2=login(api,pub,"alumno02@test.local")
    athlete=rest(api,pub,s1,"GET","athletes?select=user_id&id=eq."+A1)[0];uid1=athlete["user_id"]
    uid2=rest(api,pub,s2,"GET","athletes?select=user_id&id=eq."+A2)[0]["user_id"]
    sid="ss_v22_2b_preconfirm_001"
    created=rest(api,pub,s1,"POST","exercise_feedback",{
      "athlete_id":A1,"student_id":uid1,"session_id":sid,"exercise_uid":"press-qa",
      "exercise_name":"Press QA","workout_day_id":"day-qa-a","workout_day_name":"Día QA A",
      "feedback_type":"comment","message":"2B exacto pre-finalización","status":"pending"
    },prefer="return=representation")
    assert created and created[0]["session_id"]==sid,created
    fid=created[0]["id"]
    exact=rest(api,pub,s1,"GET","exercise_feedback?select=id,session_id,student_id,exercise_uid,status&session_id=eq."+sid)
    assert len(exact)==1 and exact[0]["id"]==fid,exact

    rest(api,pub,s1,"POST","workout_sessions",{
      "student_id":uid1,"started_at":"2026-11-09T20:00:00Z","completed_at":"2026-11-09T20:30:00Z",
      "status":"completed","notes":"Día QA A","source_session_id":sid
    },prefer="return=representation")
    linked=rest(api,pub,s1,"GET","workout_sessions?select=student_id,source_session_id,status&source_session_id=eq."+sid)
    assert len(linked)==1 and linked[0]["student_id"]==uid1 and linked[0]["status"]=="completed",linked

    expect_denied(lambda:rest(api,pub,s2,"POST","workout_sessions",{
      "student_id":uid2,"status":"completed","source_session_id":sid
    },prefer="return=representation"),"cross-owner source_session_id")

    expect_denied(lambda:rest(api,pub,s2,"POST","exercise_feedback",{
      "athlete_id":A1,"student_id":uid2,"session_id":sid,"exercise_uid":"press-qa",
      "exercise_name":"Press QA","feedback_type":"comment","message":"cross","status":"pending"
    },prefer="return=representation"),"cross-student feedback")

    expect_denied(lambda:rest(api,pub,coach,"PATCH","exercise_feedback?id=eq."+fid,{"session_id":"ss_changed"},prefer="return=representation"),"session id mutation by authorized updater")

    reviewed=rest(api,pub,coach,"PATCH","exercise_feedback?id=eq."+fid,{"status":"reviewed"},prefer="return=representation")
    assert reviewed and reviewed[0]["status"]=="reviewed",reviewed
    reread=rest(api,pub,coach,"GET","exercise_feedback?select=id,session_id,status,reviewed_at&id=eq."+fid)
    assert reread and reread[0]["session_id"]==sid and reread[0]["status"]=="reviewed",reread

    sid2="ss_v22_2b_same_day_002"
    rest(api,pub,s1,"POST","workout_sessions",{
      "student_id":uid1,"started_at":"2026-11-09T21:00:00Z","completed_at":"2026-11-09T21:25:00Z",
      "status":"completed","notes":"Día QA A","source_session_id":sid2
    },prefer="return=representation")
    second=rest(api,pub,s1,"POST","exercise_feedback",{
      "athlete_id":A1,"student_id":uid1,"session_id":sid2,"exercise_uid":"press-qa",
      "exercise_name":"Press QA","workout_day_id":"day-qa-a","workout_day_name":"Día QA A",
      "feedback_type":"comment","message":"2B misma fecha segunda sesión","status":"pending"
    },prefer="return=representation")
    first_exact=rest(api,pub,s1,"GET","exercise_feedback?select=id,session_id,exercise_uid,message&session_id=eq."+sid+"&exercise_uid=eq.press-qa")
    second_exact=rest(api,pub,s1,"GET","exercise_feedback?select=id,session_id,exercise_uid,message&session_id=eq."+sid2+"&exercise_uid=eq.press-qa")
    assert len(first_exact)==1 and first_exact[0]["session_id"]==sid,first_exact
    assert len(second_exact)==1 and second_exact[0]["session_id"]==sid2 and second_exact[0]["id"]==second[0]["id"],second_exact

    post_confirm=rest(api,pub,s1,"POST","exercise_feedback",{
      "athlete_id":A1,"student_id":uid1,"session_id":sid,"exercise_uid":"row-qa",
      "exercise_name":"Remo QA","workout_day_id":"day-qa-a","workout_day_name":"Día QA A",
      "feedback_type":"comment","message":"2B comentario post-finalización","status":"pending"
    },prefer="return=representation")
    assert post_confirm and post_confirm[0]["session_id"]==sid,post_confirm

    legacy=rest(api,pub,s1,"POST","exercise_feedback",{
      "athlete_id":A1,"student_id":uid1,"exercise_uid":"row-qa","exercise_name":"Remo QA",
      "workout_day_id":"day-qa-a","workout_day_name":"Día QA A","feedback_type":"comment",
      "message":"2B histórico compatible","status":"pending"
    },prefer="return=representation")
    assert legacy and legacy[0].get("session_id") is None,legacy
    print("TEAM FJZ V22 2B SESSION/COMMENT INTEGRITY SMOKE OK")
    print("Pre-confirmation exact comment: OK")
    print("Canonical workout session reconciliation: OK")
    print("Cross-student session collision blocked: OK")
    print("session_id immutable: OK")
    print("Coach review persistence: OK")
    print("Historical NULL session compatibility: OK")
    print("Two same-day sessions isolated by exact session_id: OK")
    print("Post-confirmation exact comment: OK")
if __name__=="__main__": main()
