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
    student_review_attempt=rest(
        api,pub,s1,"PATCH","exercise_feedback?id=eq."+feedback_id,
        {"status":"reviewed"},"return=representation"
    )
    assert student_review_attempt==[],student_review_attempt
    still_pending=rest(
        api,pub,s1,"GET",
        "exercise_feedback?select=id,status,reviewed_by,reviewed_at&id=eq."+feedback_id
    )
    assert still_pending and still_pending[0]["status"]=="pending",still_pending
    assert still_pending[0]["reviewed_by"] is None and still_pending[0]["reviewed_at"] is None

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
    # 0C.3 schema parity: current application modules use real local
    # tables with Coach/Alumno/cross-student RLS, not 404 stubs.
    # ------------------------------------------------------------
    parity_tables=[
        "athlete_schedule","athlete_reminders","body_measurements","weekly_checkins",
        "coach_media_settings","exercise_media","fitness_recipes",
        "nutrition_habit_logs","nutrition_plan_revisions","nutrition_templates",
        "progress_photos","checkin_schedules","coach_payments","student_notices",
        "athlete_habits","student_alert_state"
    ]
    for table in parity_tables:
        coach_rows=rest(api,pub,coach,"GET",table+"?select=*&limit=20")
        assert isinstance(coach_rows,list),(table,coach_rows)

    own_schedule=rest(api,pub,s1,"GET","athlete_schedule?select=athlete_id,weekday,workout_day_name")
    assert len(own_schedule)==1 and own_schedule[0]["athlete_id"]==a1,own_schedule
    cross_schedule=rest(api,pub,s1,"GET","athlete_schedule?select=athlete_id&athlete_id=eq."+a2)
    assert cross_schedule==[],cross_schedule

    own_measurements=rest(api,pub,s1,"GET","body_measurements?select=athlete_id,weight_kg")
    assert len(own_measurements)>=2 and all(x["athlete_id"]==a1 for x in own_measurements),own_measurements
    cross_measurements=rest(api,pub,s1,"GET","body_measurements?select=id&athlete_id=eq."+a2)
    assert cross_measurements==[],cross_measurements

    own_checkins=rest(api,pub,s1,"GET","weekly_checkins?select=id,athlete_id,notes")
    assert len(own_checkins)>=2 and all(x["athlete_id"]==a1 for x in own_checkins),own_checkins
    cross_checkins=rest(api,pub,s1,"GET","weekly_checkins?select=id&athlete_id=eq."+a2)
    assert cross_checkins==[],cross_checkins

    schedule_attempt=rest(
        api,pub,s1,"PATCH",
        "athlete_schedule?athlete_id=eq."+a1,
        {"notes":"Alumno no debe editar agenda Coach"},"return=representation"
    )
    assert schedule_attempt==[],schedule_attempt
    schedule_after=rest(api,pub,s1,"GET","athlete_schedule?select=notes&athlete_id=eq."+a1)
    assert schedule_after[0]["notes"]=="Agenda ficticia QA",schedule_after

    coach_schedule_update=rest(
        api,pub,coach,"PATCH",
        "athlete_schedule?athlete_id=eq."+a1,
        {"notes":"Agenda QA verificada"},"return=representation"
    )
    assert coach_schedule_update and coach_schedule_update[0]["notes"]=="Agenda QA verificada"

    new_checkin_id=str(uuid.uuid4())
    new_checkin={
        "id":new_checkin_id,"athlete_id":a1,"student_id":s1_id,
        "week_start":"2026-01-12","weight_kg":72.2,
        "sleep_quality":8,"stress_level":3,"energy_level":8,
        "adherence_level":9,"mood_level":8,"hunger_level":4,
        "recovery_level":8,"motivation_level":9,"notes":"Check-in 0C smoke"
    }
    created_checkin=rest(api,pub,s1,"POST","weekly_checkins",new_checkin,"return=representation")
    assert created_checkin and created_checkin[0]["id"]==new_checkin_id
    reviewed_checkin=rest(
        api,pub,coach,"PATCH","weekly_checkins?id=eq."+new_checkin_id,
        {"coach_feedback":"Revisado QA","reviewed_at":"2026-01-13T12:00:00Z"},
        "return=representation"
    )
    assert reviewed_checkin and reviewed_checkin[0]["coach_feedback"]=="Revisado QA"

    forbidden_cross_checkin=dict(new_checkin)
    forbidden_cross_checkin["id"]=str(uuid.uuid4())
    forbidden_cross_checkin["athlete_id"]=a2
    forbidden_cross_checkin["student_id"]=s2_id
    forbidden_cross_checkin["week_start"]="2026-01-19"
    expect_error(
        lambda: rest(api,pub,s1,"POST","weekly_checkins",forbidden_cross_checkin,"return=representation"),
        "student cannot write another athlete checkin"
    )

    # Media/recipes are linked by coach; unrelated student data stays hidden.
    media_s1=rest(api,pub,s1,"GET","exercise_media?select=exercise_key,title,is_active")
    assert media_s1 and media_s1[0]["exercise_key"]=="dev_ex_press",media_s1
    recipes_s1=rest(api,pub,s1,"GET","fitness_recipes?select=title,category,kcal_per_serving")
    recipe_qa=next((x for x in recipes_s1 if x["title"]=="Receta QA local"),None)
    assert recipe_qa and float(recipe_qa["kcal_per_serving"])==300,recipes_s1
    templates_s1=rest(api,pub,s1,"GET","nutrition_templates?select=id")
    assert templates_s1==[],templates_s1

    photos_s1=rest(api,pub,s1,"GET","progress_photos?select=athlete_id,taken_on,pose,storage_path")
    assert photos_s1 and photos_s1[0]["athlete_id"]==a1,photos_s1
    photos_s2_cross=rest(api,pub,s2,"GET","progress_photos?select=id&athlete_id=eq."+a1)
    assert photos_s2_cross==[],photos_s2_cross

    habits_s1=rest(api,pub,s1,"GET","athlete_habits?select=id,athlete_id,name,category&order=sort_order.asc")
    assert len(habits_s1)==1 and habits_s1[0]["athlete_id"]==a1,habits_s1
    habits_cross=rest(api,pub,s1,"GET","athlete_habits?select=id&athlete_id=eq."+a2)
    assert habits_cross==[],habits_cross
    forbidden_habit={
        "id":str(uuid.uuid4()),"athlete_id":a1,"coach_id":coach_id,
        "name":"QA alumno no debe crear hábito","category":"general","active":True,"sort_order":9
    }
    expect_error(
        lambda: rest(api,pub,s1,"POST","athlete_habits",forbidden_habit,"return=representation"),
        "student cannot create coach habit"
    )

    student_alerts=rest(api,pub,s1,"POST","rpc/get_student_alerts",{},None,(200,201))
    assert isinstance(student_alerts,list),student_alerts
    if student_alerts:
        alert_keys={"event_key","category","severity","title","body","occurred_at","action_target","action_label","is_read"}
        assert alert_keys.issubset(student_alerts[0].keys()),student_alerts[0]
        first_key=student_alerts[0]["event_key"]
        state_row={
            "student_id":s1_id,"event_key":first_key,
            "read_at":"2026-11-08T12:00:00Z","dismissed_at":None
        }
        saved_state=rest(api,pub,s1,"POST","student_alert_state",state_row,"return=representation")
        assert saved_state and saved_state[0]["event_key"]==first_key,saved_state
        after_alerts=rest(api,pub,s1,"POST","rpc/get_student_alerts",{},None,(200,201))
        assert all(x["event_key"]!=first_key for x in after_alerts),after_alerts
        cross_state=rest(api,pub,s2,"GET","student_alert_state?select=event_key&student_id=eq."+s1_id)
        assert cross_state==[],cross_state

    # get_coach_feed has the production return contract and real local sources.
    feed=rest(
        api,pub,coach,"POST","rpc/get_coach_feed",{},
        None,(200,201)
    )
    assert isinstance(feed,list) and feed,feed
    required_feed={"event_key","athlete_id","athlete_name","kind","severity","title","body","occurred_at","is_read"}
    assert required_feed.issubset(feed[0].keys()),feed[0]
    assert any(x["kind"]=="exercise_feedback" for x in feed),feed
    student_feed=rest(api,pub,s1,"POST","rpc/get_coach_feed",{},None,(200,201))
    assert student_feed==[],student_feed

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

    video_path=coach_id+"/qa-smoke-exercise.txt"
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
    print("0C schema parity + Coach/Alumno RLS + coach/student alert RPCs: OK")
    print("Storage local + access policies: OK")

if __name__=="__main__":
    main()
