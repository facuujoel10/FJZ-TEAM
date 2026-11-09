from __future__ import annotations
from dev_common import TEST_PASSWORD,http_json,local_status
A1="10000000-0000-4000-8000-000000000001";A2="10000000-0000-4000-8000-000000000002";MISSING="69999999-0000-4000-8000-000000000099"
def login(api,pub,email):
    data=http_json("POST",api+"/auth/v1/token?grant_type=password",pub,None,{"email":email,"password":TEST_PASSWORD});token=data.get("access_token") if isinstance(data,dict) else None
    if not token: raise RuntimeError("Comment smoke auth failed for "+email)
    return token
def rest(api,pub,token,method,path,payload=None,prefer=None): return http_json(method,api+"/rest/v1/"+path,pub,token,payload,prefer=prefer)
def main():
    st=local_status();api=st["api"];pub=st["publishable"];coach=login(api,pub,"coach@test.local");s1=login(api,pub,"alumno01@test.local");s2=login(api,pub,"alumno02@test.local")
    athlete=rest(api,pub,s1,"GET","athletes?select=user_id&id=eq."+A1);uid=athlete[0]["user_id"];message="QA 1C comentario ficticio"
    created=rest(api,pub,s1,"POST","exercise_feedback",{"athlete_id":A1,"student_id":uid,"exercise_uid":"press-qa","exercise_name":"Press QA","workout_day_id":"day-qa-a","workout_day_name":"Día QA A","feedback_type":"comment","message":message,"status":"pending"},prefer="return=representation");cid=created[0]["id"]
    pending=rest(api,pub,coach,"GET","exercise_feedback?select=id,athlete_id,exercise_uid,exercise_name,workout_day_id,workout_day_name,message,status&athlete_id=eq."+A1+"&status=eq.pending");assert any(x["id"]==cid for x in pending),pending
    own=rest(api,pub,s1,"GET","exercise_feedback?select=id,athlete_id,message,status&id=eq."+cid);assert len(own)==1 and own[0]["athlete_id"]==A1,own
    assert rest(api,pub,s2,"GET","exercise_feedback?select=id,athlete_id&id=eq."+cid)==[]
    assert rest(api,pub,s1,"GET","exercise_feedback?select=id&athlete_id=eq."+A2)==[]
    assert rest(api,pub,s1,"GET","exercise_feedback?select=id&id=eq."+MISSING)==[]
    reviewed=rest(api,pub,coach,"PATCH","exercise_feedback?id=eq."+cid,{"status":"reviewed"},prefer="return=representation");assert reviewed and reviewed[0]["status"]=="reviewed",reviewed
    refreshed=rest(api,pub,coach,"GET","exercise_feedback?select=id,status,exercise_uid,exercise_name,workout_day_id,workout_day_name,reviewed_at,created_at,updated_at&id=eq."+cid);assert len(refreshed)==1 and refreshed[0]["status"]=="reviewed",refreshed;assert refreshed[0]["exercise_uid"]=="press-qa" and refreshed[0]["workout_day_id"]=="day-qa-a",refreshed
    historical=rest(api,pub,coach,"GET","exercise_feedback?select=id,exercise_uid,exercise_name,workout_day_id,workout_day_name,status&athlete_id=eq."+A1);assert all("exercise_uid" in x and "status" in x for x in historical),historical
    print("TEAM FJZ V22 1C COMMENT REPOSITORY/RLS SMOKE OK");print("Coach authorized pending read: OK");print("Student own read: OK");print("Cross-student isolation: OK");print("Reviewed persistence after refresh: OK");print("Missing/RLS-hidden controlled result: OK");print("Historical identity fields preserved: OK")
if __name__=="__main__": main()
