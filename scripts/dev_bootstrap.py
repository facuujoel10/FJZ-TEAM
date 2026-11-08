from __future__ import annotations
import json, urllib.parse
from dev_common import TEST_PASSWORD,http_json,local_status

USERS=[
  ("coach@test.local","TEST COACH","coach"),
  ("alumno01@test.local","TEST ALUMNO 01","student"),
  ("alumno02@test.local","TEST ALUMNO 02","student"),
]

def admin_users(api,secret):
    data=http_json("GET",api+"/auth/v1/admin/users?page=1&per_page=1000",secret,secret)
    return data.get("users",[]) if isinstance(data,dict) else []

def ensure_user(api,secret,email,name,role):
    found=next((u for u in admin_users(api,secret) if u.get("email")==email),None)
    payload={"email":email,"password":TEST_PASSWORD,"email_confirm":True,
             "user_metadata":{"full_name":name,"role":role}}
    if found:
        return http_json("PUT",api+"/auth/v1/admin/users/"+found["id"],secret,secret,payload)
    return http_json("POST",api+"/auth/v1/admin/users",secret,secret,payload)

def upsert(api,secret,table,rows,conflict):
    return http_json(
      "POST",api+"/rest/v1/"+table+"?on_conflict="+urllib.parse.quote(conflict),
      secret,secret,rows,"resolution=merge-duplicates,return=representation"
    )

def ensure_bucket(api,secret,bucket):
    try:
        http_json("POST",api+"/storage/v1/bucket",secret,secret,
                  {"id":bucket,"name":bucket,"public":False},ok=(200,201))
    except RuntimeError as e:
        if "409" not in str(e) and "already exists" not in str(e).lower():
            raise

def main():
    st=local_status();api=st["api"];secret=st["secret"]
    ids={}
    for email,name,role in USERS:
        u=ensure_user(api,secret,email,name,role)
        ids[email]=u["id"]

    coach=ids["coach@test.local"];s1=ids["alumno01@test.local"];s2=ids["alumno02@test.local"]
    a1="10000000-0000-4000-8000-000000000001"
    a2="10000000-0000-4000-8000-000000000002"

    upsert(api,secret,"profiles",[
      {"id":coach,"email":"coach@test.local","full_name":"TEST COACH","role":"coach"},
      {"id":s1,"email":"alumno01@test.local","full_name":"TEST ALUMNO 01","role":"student"},
      {"id":s2,"email":"alumno02@test.local","full_name":"TEST ALUMNO 02","role":"student"}
    ],"id")

    upsert(api,secret,"coach_students",[
      {"id":"11000000-0000-4000-8000-000000000001","coach_id":coach,"student_id":s1,"status":"active"},
      {"id":"11000000-0000-4000-8000-000000000002","coach_id":coach,"student_id":s2,"status":"active"}
    ],"id")

    upsert(api,secret,"athletes",[
      {"id":a1,"coach_id":coach,"user_id":s1,"client_id":"dev_student_01","name":"TEST ALUMNO 01",
       "goal":"QA ficticio: hipertrofia","invite_code":"DEVQA001","sex":"X","height_cm":170},
      {"id":a2,"coach_id":coach,"user_id":s2,"client_id":"dev_student_02","name":"TEST ALUMNO 02",
       "goal":"QA ficticio: recomposición","invite_code":"DEVQA002","sex":"X","height_cm":165}
    ],"id")

    day1={"id":"dev_day_01","name":"Día QA A","muscles":"General","warmup":[],"stretching":[],
          "cardio":{"enabled":False},"exercises":[
            {"uid":"dev_ex_press","libId":"custom","name":"Press QA","muscle":"Pecho","equipment":"Máquina",
             "sets":3,"min":8,"max":10,"rirMin":1,"rirMax":2,"rest":90,"cue":"Fixture QA","history":[],"override":None},
            {"uid":"dev_ex_row","libId":"custom","name":"Remo QA","muscle":"Espalda","equipment":"Polea",
             "sets":3,"min":10,"max":12,"rirMin":1,"rirMax":2,"rest":90,"cue":"Fixture QA","history":[],"override":None}
          ]}
    history={"id":"dev_session_history_01","date":"2026-01-10T15:00:00.000Z","dayId":"dev_day_01",
             "dayName":"Día QA A","summary":{"up":1,"hold":1,"review":0,"totalSets":6},
             "exerciseResults":[
               {"exerciseUid":"dev_ex_press","name":"Press QA","sets":[[20,10,2],[20,9,2],[20,8,1]],
                "recommendation":{"type":"hold","title":"Mantener","copy":"Fixture QA"}}
             ]}
    snap1={"id":"dev_student_01","name":"TEST ALUMNO 01","goal":"QA ficticio: hipertrofia",
           "plannedPerWeek":2,"lastWorkout":history["date"],"days":[day1],"sessions":[history],
           "checkins":[],"workoutDrafts":{}}
    snap2={"id":"dev_student_02","name":"TEST ALUMNO 02","goal":"QA ficticio: recomposición",
           "plannedPerWeek":2,"lastWorkout":None,"days":[day1],"sessions":[],"checkins":[],"workoutDrafts":{}}
    upsert(api,secret,"athlete_snapshots",[
      {"athlete_id":a1,"data":snap1},{"athlete_id":a2,"data":snap2}
    ],"athlete_id")

    plan1={"meals":[
      {"id":"meal_qa_breakfast","name":"Desayuno","options":[
        {"id":"opt_qa_1","name":"Opción QA 1","items":[
          {"food_id":"20000000-0000-4000-8000-000000000003","name":"QA Yogur ficticio",
           "grams":180,"kcal":135,"protein_g":14.4,"carbs_g":10.8,"fat_g":3.6}
        ]}
      ]},
      {"id":"meal_qa_lunch","name":"Almuerzo","options":[
        {"id":"opt_qa_2","name":"Opción QA 2","items":[
          {"food_id":"20000000-0000-4000-8000-000000000001","name":"QA Arroz cocido",
           "grams":150,"kcal":195,"protein_g":4.05,"carbs_g":42,"fat_g":0.45},
          {"food_id":"20000000-0000-4000-8000-000000000002","name":"QA Proteína ficticia",
           "grams":150,"kcal":247.5,"protein_g":46.5,"carbs_g":0,"fat_g":5.4}
        ]}
      ]}
    ]}
    upsert(api,secret,"nutrition_plans",[
      {"id":"30000000-0000-4000-8000-000000000001","athlete_id":a1,"coach_id":coach,
       "title":"PLAN QA A","notes":"Solo datos ficticios","target_kcal":2200,"target_protein_g":160,
       "target_carbs_g":250,"target_fat_g":60,"plan":plan1,"revision":1,"active":True,
       "student_logging_enabled":True,"published_at":"2026-01-01T12:00:00Z"},
      {"id":"30000000-0000-4000-8000-000000000002","athlete_id":a2,"coach_id":coach,
       "title":"PLAN QA B","notes":"Registro deshabilitado para probar permisos","target_kcal":2000,
       "target_protein_g":140,"target_carbs_g":220,"target_fat_g":60,"plan":plan1,"revision":1,
       "active":True,"student_logging_enabled":False,"published_at":"2026-01-01T12:00:00Z"}
    ],"id")

    upsert(api,secret,"exercise_feedback",[
      {"id":"40000000-0000-4000-8000-000000000001","athlete_id":a1,"student_id":s1,
       "exercise_uid":"dev_ex_press","exercise_name":"Press QA","workout_day_id":"dev_day_01",
       "workout_day_name":"Día QA A","feedback_type":"comment","message":"Comentario ficticio pendiente para QA",
       "status":"pending"}
    ],"id")

    for bucket in ("progress-photos","profile-photos","exercise-videos"):
        ensure_bucket(api,secret,bucket)

    print("TEAM FJZ V22 LOCAL FIXTURES READY")
    print("coach@test.local / alumno01@test.local / alumno02@test.local")
    print("production data copied: 0")

if __name__=="__main__":
    main()
