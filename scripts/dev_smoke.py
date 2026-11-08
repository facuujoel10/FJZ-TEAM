from __future__ import annotations
import datetime as dt
import urllib.parse
import uuid

from dev_common import TEST_PASSWORD,http_bytes,http_json,local_status

def login(api,pub,email):
    x=http_json(
        "POST",api+"/auth/v1/token?grant_type=password",pub,None,
        {"email":email,"password":TEST_PASSWORD}
    )
    if not x.get("access_token"):
        raise RuntimeError("Auth local no devolvió token para la cuenta de prueba.")
    return x["access_token"]

def rest(api,pub,token,method,path,payload=None,prefer=None,ok=(200,201,204)):
    return http_json(method,api+"/rest/v1/"+path,pub,token,payload,prefer,ok)

def expect_error(fn,label,codes=("400","401","403","409","42501","23505")):
    try:
        fn()
    except RuntimeError as e:
        if any(x in str(e) for x in codes):
            return
        raise
    raise RuntimeError("Se esperaba rechazo: "+label)

def profile_id(api,pub,token,email):
    rows=rest(api,pub,token,"GET","profiles?select=id,email")
    return next(x["id"] for x in rows if x["email"]==email)

def storage_object_url(api,bucket,path):
    safe=urllib.parse.quote(path,safe="/")
    return api+"/storage/v1/object/"+bucket+"/"+safe

def main():
    st=local_status()
    api=st["api"]
    pub=st["publishable"]
    secret=st["secret"]

    coach=login(api,pub,"coach@test.local")
    s1=login(api,pub,"alumno01@test.local")
    s2=login(api,pub,"alumno02@test.local")
    coach_id=profile_id(api,pub,coach,"coach@test.local")
    s1_id=profile_id(api,pub,s1,"alumno01@test.local")
    s2_id=profile_id(api,pub,s2,"alumno02@test.local")

    # ------------------------------------------------------------
    # RLS: Coach sees both synthetic athletes; students only their own.
    # ------------------------------------------------------------
    coach_athletes=rest(api,pub,coach,"GET","athletes?select=id,client_id&order=client_id.asc")
    assert [x["client_id"] for x in coach_athletes]==["dev_student_01","dev_student_02"],coach_athletes

    a1_rows=rest(api,pub,s1,"GET","athletes?select=id,client_id")
    assert len(a1_rows)==1 and a1_rows[0]["client_id"]=="dev_student_01",a1_rows
    a1=a1_rows[0]["id"]

    a2_rows=rest(api,pub,s2,"GET","athletes?select=id,client_id")
    assert len(a2_rows)==1 and a2_rows[0]["client_id"]=="dev_student_02",a2_rows
    a2=a2_rows[0]["id"]

    cross=rest(api,pub,s1,"GET","athletes?select=id&client_id=eq.dev_student_02")
    assert cross==[],cross

    # ------------------------------------------------------------
    # Training: use the real local RPC, then read back snapshot and
    # projected workout_sessions. Calling it twice must not duplicate.
    # ------------------------------------------------------------
    snaps=rest(api,pub,s1,"GET","athlete_snapshots?select=athlete_id,data&athlete_id=eq."+a1)
    assert snaps and snaps[0]["data"]["name"]=="TEST ALUMNO 01"
    snapshot=snaps[0]["data"]
    day=snapshot["days"][0]
    session_id="qa_action_session_01"
    session={
        "id":session_id,
        "date":"2026-01-12T15:00:00.000Z",
        "dayId":day["id"],
        "dayName":day["name"],
        "summary":{"up":1,"hold":0,"review":0,"totalSets":3},
        "exerciseResults":[{
            "exerciseUid":"dev_ex_press",
            "name":"Press QA",
            "sets":[[22.5,10,2],[22.5,9,2],[22.5,8,1]],
            "completed":True,
            "recommendation":{"type":"hold","title":"Mantener","copy":"Smoke local"}
        }]
    }
    rpc_payload={"p_athlete_id":a1,"p_day_id":day["id"],"p_day":day,"p_session":session}
    for _ in range(2):
        rest(api,pub,s1,"POST","rpc/commit_workout_session_v202",rpc_payload,None,(200,201))

    snap_after=rest(api,pub,s1,"GET","athlete_snapshots?select=data&athlete_id=eq."+a1)
    ids=[x.get("id") for x in snap_after[0]["data"].get("sessions",[])]
    assert ids.count(session_id)==1,ids

    projected=rest(
        api,pub,s1,"GET",
        "workout_sessions?select=id,source_session_id,status&source_session_id=eq."+session_id
    )
    assert len(projected)==1 and projected[0]["status"]=="completed",projected

    # ------------------------------------------------------------
    # Exercise comments: student creates, duplicate client UUID is
    # rejected, student cannot mark reviewed, coach can.
    # ------------------------------------------------------------
    feedback_id=str(uuid.uuid4())
    comment={
        "id":feedback_id,
        "athlete_id":a1,
        "student_id":s1_id,
        "exercise_uid":"dev_ex_press",
        "exercise_name":"Press QA",
        "workout_day_id":"dev_day_01",
        "workout_day_name":"Día QA A",
        "feedback_type":"comment",
        "message":"Smoke QA local",
        "status":"pending"
    }
    created=rest(api,pub,s1,"POST","exercise_feedback",comment,"return=representation")
    assert created and created[0]["id"]==feedback_id

    expect_error(
        lambda: rest(api,pub,s1,"POST","exercise_feedback",comment,"return=representation"),
        "duplicate feedback id",
        codes=("409","23505")
    )
    expect_error(
        lambda: rest(
            api,pub,s1,"PATCH","exercise_feedback?id=eq."+feedback_id,
            {"status":"reviewed"},"return=representation"
        ),
        "student cannot review own exercise feedback"
    )

    reviewed_at=dt.datetime.now(dt.timezone.utc).isoformat()
    reviewed=rest(
        api,pub,coach,"PATCH","exercise_feedback?id=eq."+feedback_id,
        {"status":"reviewed","reviewed_by":coach_id,"reviewed_at":reviewed_at},
        "return=representation"
    )
    assert reviewed and reviewed[0]["status"]=="reviewed"
    assert reviewed[0]["reviewed_by"]==coach_id

    # ------------------------------------------------------------
    # Nutrition: enabled student can create/edit/delete. Disabled
    # student is blocked by database RLS, not only by UI.
    # ------------------------------------------------------------
    plan2=rest(api,pub,s2,"GET","nutrition_plans?select=athlete_id,student_logging_enabled")
    assert plan2 and plan2[0]["student_logging_enabled"] is False

    log_id=str(uuid.uuid4())
    log={
        "id":log_id,"athlete_id":a1,"student_id":s1_id,"logged_on":"2026-01-12",
        "meal_label":"Almuerzo","food_name":"QA Arroz cocido","grams":100,
        "kcal":130,"protein_g":2.7,"carbs_g":28,"fat_g":0.3,"source":"plan"
    }
    ins=rest(api,pub,s1,"POST","nutrition_logs",log,"return=representation")
    assert ins and ins[0]["id"]==log_id
    edited=rest(
        api,pub,s1,"PATCH","nutrition_logs?id=eq."+log_id,
        {"grams":150,"kcal":195,"protein_g":4.05,"carbs_g":42,"fat_g":0.45},
        "return=representation"
    )
    assert edited and float(edited[0]["grams"])==150
    deleted=rest(api,pub,s1,"DELETE","nutrition_logs?id=eq."+log_id,None,"return=representation")
    assert deleted and deleted[0]["id"]==log_id

    blocked={
        "athlete_id":a2,"student_id":s2_id,"logged_on":"2026-01-12",
        "meal_label":"Almuerzo","food_name":"QA bloqueado","grams":100,
        "kcal":1,"protein_g":0,"carbs_g":0,"fat_g":0,"source":"custom"
    }
    expect_error(
        lambda: rest(api,pub,s2,"POST","nutrition_logs",blocked,"return=representation"),
        "nutrition logging disabled"
    )

    # ------------------------------------------------------------
    # Storage: real local Storage service + RLS.
    # Student can upload/read own profile object, sibling student cannot,
    # linked coach can. Progress photo is athlete-scoped. Coach exercise
    # video is readable by linked student.
    # ------------------------------------------------------------
    buckets=http_json("GET",api+"/storage/v1/bucket",secret,secret)
    names={x.get("name") or x.get("id") for x in (buckets or [])}
    assert {"progress-photos","profile-photos","exercise-videos"}.issubset(names),names

    profile_path=s1_id+"/qa-profile.txt"
    profile_url=storage_object_url(api,"profile-photos",profile_path)
    http_bytes("POST",profile_url,pub,s1,b"TEAM FJZ LOCAL QA",content_type="text/plain")
    assert http_bytes("GET",profile_url,pub,s1)==b"TEAM FJZ LOCAL QA"
    assert http_bytes("GET",profile_url,pub,coach)==b"TEAM FJZ LOCAL QA"
    expect_error(lambda: http_bytes("GET",profile_url,pub,s2),"cross-student profile storage read")

    progress_path=a1+"/2026-01-12/qa-progress.txt"
    progress_url=storage_object_url(api,"progress-photos",progress_path)
    http_bytes("POST",progress_url,pub,s1,b"LOCAL PROGRESS QA",content_type="text/plain")
    assert http_bytes("GET",progress_url,pub,s1)==b"LOCAL PROGRESS QA"
    expect_error(lambda: http_bytes("GET",progress_url,pub,s2),"cross-athlete progress storage read")

    video_path=coach_id+"/qa-exercise.txt"
    video_url=storage_object_url(api,"exercise-videos",video_path)
    http_bytes("POST",video_url,pub,coach,b"LOCAL VIDEO PLACEHOLDER",content_type="text/plain")
    assert http_bytes("GET",video_url,pub,s1)==b"LOCAL VIDEO PLACEHOLDER"
    expect_error(lambda: http_bytes("POST",video_url+"-student",pub,s1,b"NO",content_type="text/plain"),
                 "student cannot upload coach exercise video")

    print("TEAM FJZ V22 LOCAL SMOKE OK")
    print("Auth local: OK")
    print("RLS Coach/Alumno: OK")
    print("Workout RPC + idempotent projection: OK")
    print("Exercise feedback create/review restrictions: OK")
    print("Nutrition create/edit/delete + disabled permission: OK")
    print("Storage local + access policies: OK")

if __name__=="__main__":
    main()
