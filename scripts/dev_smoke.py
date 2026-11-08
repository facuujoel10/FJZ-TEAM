from __future__ import annotations
import uuid, urllib.parse
from dev_common import TEST_PASSWORD,http_json,local_status

def login(api,pub,email):
    x=http_json("POST",api+"/auth/v1/token?grant_type=password",pub,None,
                {"email":email,"password":TEST_PASSWORD})
    if not x.get("access_token"): raise RuntimeError("Auth local no devolvió token para "+email)
    return x["access_token"]

def rest(api,pub,token,method,path,payload=None,prefer=None,ok=(200,201,204)):
    return http_json(method,api+"/rest/v1/"+path,pub,token,payload,prefer,ok)

def expect_forbidden(fn,label):
    try: fn()
    except RuntimeError as e:
        if any(x in str(e) for x in ("401","403","42501")): return
        raise
    raise RuntimeError("Se esperaba bloqueo RLS: "+label)

def main():
    st=local_status();api=st["api"];pub=st["publishable"];secret=st["secret"]
    coach=login(api,pub,"coach@test.local")
    s1=login(api,pub,"alumno01@test.local")
    s2=login(api,pub,"alumno02@test.local")

    c=rest(api,pub,coach,"GET","athletes?select=client_id&order=client_id.asc")
    assert [x["client_id"] for x in c]==["dev_student_01","dev_student_02"],c
    a=rest(api,pub,s1,"GET","athletes?select=id,client_id")
    assert len(a)==1 and a[0]["client_id"]=="dev_student_01",a
    cross=rest(api,pub,s1,"GET","athletes?select=id&client_id=eq.dev_student_02")
    assert cross==[],cross

    own=a[0]["id"]
    snap=rest(api,pub,s1,"GET","athlete_snapshots?select=athlete_id,data&athlete_id=eq."+own)
    assert snap and snap[0]["data"]["name"]=="TEST ALUMNO 01"

    plan2=rest(api,pub,s2,"GET","nutrition_plans?select=athlete_id,student_logging_enabled")
    assert plan2 and plan2[0]["student_logging_enabled"] is False

    fid=str(uuid.uuid4())
    comment={"id":fid,"athlete_id":own,"student_id":snap[0]["data"].get("_never","") or None,
             "exercise_uid":"dev_ex_press","exercise_name":"Press QA","workout_day_id":"dev_day_01",
             "workout_day_name":"Día QA A","feedback_type":"comment","message":"Smoke QA","status":"pending"}
    # Resolve student id from own profile rather than embedding any real identity.
    me=rest(api,pub,s1,"GET","profiles?select=id,email&id=eq."+urllib.parse.quote("",safe=""))
    # profiles RLS returns the caller row; use it for student_id.
    me=rest(api,pub,s1,"GET","profiles?select=id,email")
    sid=next(x["id"] for x in me if x["email"]=="alumno01@test.local")
    comment["student_id"]=sid
    row=rest(api,pub,s1,"POST","exercise_feedback",comment,"return=representation")
    assert row and row[0]["id"]==fid

    # Same client-generated id cannot be inserted twice.
    expect_forbidden(lambda: rest(api,pub,s1,"POST","exercise_feedback",comment,"return=representation"),
                     "duplicate feedback id")

    reviewed=rest(api,pub,coach,"PATCH","exercise_feedback?id=eq."+fid,
                  {"status":"reviewed"},"return=representation")
    assert reviewed and reviewed[0]["status"]=="reviewed"

    log_id=str(uuid.uuid4())
    log={"id":log_id,"athlete_id":own,"student_id":sid,"logged_on":"2026-01-12",
         "meal_label":"Almuerzo","food_name":"QA Arroz cocido","grams":100,
         "kcal":130,"protein_g":2.7,"carbs_g":28,"fat_g":0.3,"source":"plan"}
    ins=rest(api,pub,s1,"POST","nutrition_logs",log,"return=representation")
    assert ins and ins[0]["id"]==log_id
    rest(api,pub,s1,"DELETE","nutrition_logs?id=eq."+log_id,None,"return=representation")

    a2=rest(api,pub,s2,"GET","athletes?select=id")
    p2=rest(api,pub,s2,"GET","profiles?select=id,email")
    sid2=next(x["id"] for x in p2 if x["email"]=="alumno02@test.local")
    blocked={"athlete_id":a2[0]["id"],"student_id":sid2,"logged_on":"2026-01-12",
             "meal_label":"Almuerzo","food_name":"QA bloqueado","grams":100,
             "kcal":1,"protein_g":0,"carbs_g":0,"fat_g":0,"source":"custom"}
    expect_forbidden(lambda: rest(api,pub,s2,"POST","nutrition_logs",blocked,"return=representation"),
                     "nutrition logging disabled")

    buckets=http_json("GET",api+"/storage/v1/bucket",secret,secret)
    names={x.get("name") or x.get("id") for x in (buckets or [])}
    assert {"progress-photos","profile-photos","exercise-videos"}.issubset(names),names

    print("TEAM FJZ V22 LOCAL SMOKE OK")
    print("Auth local: OK")
    print("RLS Coach/Alumno: OK")
    print("Exercise feedback: OK")
    print("Nutrition permission: OK")
    print("Storage buckets: OK")

if __name__=="__main__":
    main()
