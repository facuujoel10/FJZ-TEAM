from __future__ import annotations
import base64, json, urllib.parse
from dev_common import TEST_PASSWORD,http_bytes,http_json,local_status

USERS=[
  ("coach@test.local","TEST COACH","coach"),
  ("alumno01@test.local","TEST ALUMNO 01","student"),
  ("alumno02@test.local","TEST ALUMNO 02","student"),
  ("outsider-coach@test.local","TEST COACH OUTSIDER","coach"),
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
             "dayName":"Día QA A","cloudConfirmed":True,"summary":{"up":1,"hold":1,"review":0,"totalSets":6},
             "exerciseResults":[
               {"exerciseUid":"dev_ex_press","name":"Press QA","sets":[[20,10,2],[20,9,2],[20,8,1]],
                "recommendation":{"type":"hold","title":"Mantener","copy":"Fixture QA"}}
             ]}
    history2={"id":"dev_session_history_02","date":"2026-11-10T15:00:00.000Z","dayId":"dev_day_01",
              "dayName":"Día QA A","cloudConfirmed":True,"summary":{"up":1,"hold":0,"review":0,"totalSets":6},
              "exerciseResults":[
                {"exerciseUid":"dev_ex_press","exerciseName":"Press QA","name":"Press QA","sets":[[22.5,10,2],[22.5,9,2],[22.5,8,1]],
                 "recommendation":{"type":"up","title":"Progresión QA","copy":"Fixture QA 3B"}},
                {"exerciseUid":"dev_ex_row","exerciseName":"Remo QA","name":"Remo QA","sets":[[30,12,2],[30,11,2],[30,10,1]],
                 "recommendation":{"type":"hold","title":"Mantener","copy":"Fixture QA 3B"}}
              ]}
    snap1={"id":"dev_student_01","name":"TEST ALUMNO 01","goal":"QA ficticio: hipertrofia",
           "plannedPerWeek":2,"lastWorkout":history2["date"],"days":[day1],"sessions":[history,history2],
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
       "session_id":None,"exercise_uid":"dev_ex_press","exercise_name":"Press QA","workout_day_id":"dev_day_01",
       "workout_day_name":"Día QA A","feedback_type":"comment","message":"Comentario ficticio pendiente para QA",
       "status":"pending"}
,
      {"id":"40000000-0000-4000-8000-000000000002","athlete_id":a1,"student_id":s1,
       "session_id":"dev_session_history_02","exercise_uid":"dev_ex_press","exercise_name":"Press QA",
       "workout_day_id":"dev_day_01","workout_day_name":"Día QA A","feedback_type":"discomfort",
       "message":"Molestia ficticia exacta 3B","status":"pending"}
    ],"id")

    # ------------------------------------------------------------
    # 0C.3 synthetic parity fixtures. These exercise the current
    # production contracts without copying any production rows.
    # ------------------------------------------------------------
    upsert(api,secret,"athlete_schedule",[
      {"id":"50000000-0000-4000-8000-000000000001","athlete_id":a1,"coach_id":coach,
       "weekday":1,"workout_day_id":"dev_day_01","workout_day_name":"Día QA A",
       "start_time":"09:00:00","reminder_enabled":True,"reminder_minutes_before":60,
       "notes":"Agenda ficticia QA","active":True},
      {"id":"50000000-0000-4000-8000-000000000002","athlete_id":a2,"coach_id":coach,
       "weekday":3,"workout_day_id":"dev_day_01","workout_day_name":"Día QA B",
       "start_time":"18:00:00","reminder_enabled":True,"reminder_minutes_before":30,
       "notes":"Agenda ficticia QA 2","active":True}
    ],"id")

    upsert(api,secret,"athlete_reminders",[
      {"id":"51000000-0000-4000-8000-000000000001","athlete_id":a1,"coach_id":coach,
       "title":"QA recordatorio 01","body":"Recordatorio completamente ficticio",
       "category":"custom","schedule_type":"weekly","reminder_date":None,"weekday":1,
       "remind_time":"08:00:00","active":True},
      {"id":"51000000-0000-4000-8000-000000000002","athlete_id":a2,"coach_id":coach,
       "title":"QA recordatorio 02","body":"Recordatorio completamente ficticio",
       "category":"custom","schedule_type":"once","reminder_date":"2026-01-20","weekday":None,
       "remind_time":None,"active":True}
    ],"id")

    upsert(api,secret,"body_measurements",[
      {"id":"52000000-0000-4000-8000-000000000001","athlete_id":a1,"student_id":s1,
       "measured_on":"2026-01-10","weight_kg":72.5,"waist_cm":80,"abdomen_cm":82,
       "hip_cm":96,"chest_cm":101,"arm_left_cm":35,"arm_right_cm":35,
       "thigh_left_cm":57,"thigh_right_cm":57,"notes":"Medición QA"},
      {"id":"52000000-0000-4000-8000-000000000002","athlete_id":a2,"student_id":s2,
       "measured_on":"2026-01-10","weight_kg":65,"waist_cm":76,"abdomen_cm":78,
       "hip_cm":92,"chest_cm":94,"arm_left_cm":31,"arm_right_cm":31,
       "thigh_left_cm":53,"thigh_right_cm":53,"notes":"Medición QA 2"}
,
      {"id":"52000000-0000-4000-8000-000000000003","athlete_id":a1,"student_id":s1,
       "measured_on":"2026-11-08","weight_kg":71.8,"waist_cm":79,"abdomen_cm":81,
       "hip_cm":96,"chest_cm":102,"arm_left_cm":35.5,"arm_right_cm":35.5,
       "thigh_left_cm":57.5,"thigh_right_cm":57.5,"notes":"Medición QA 3B"},
      {"id":"52000000-0000-4000-8000-000000000004","athlete_id":a2,"student_id":s2,
       "measured_on":"2026-11-08","weight_kg":64.8,"waist_cm":75.5,"abdomen_cm":77.5,
       "hip_cm":92,"chest_cm":94,"arm_left_cm":31,"arm_right_cm":31,
       "thigh_left_cm":53,"thigh_right_cm":53,"notes":"Medición QA 3B alumno 02"}
    ],"id")

    upsert(api,secret,"weekly_checkins",[
      {"id":"53000000-0000-4000-8000-000000000001","athlete_id":a1,"student_id":s1,
       "week_start":"2026-01-05","weight_kg":72.5,"sleep_quality":8,"stress_level":3,
       "energy_level":8,"adherence_level":9,"mood_level":8,"hunger_level":4,
       "recovery_level":8,"motivation_level":9,"notes":"Check-in QA pendiente",
       "reviewed_at":None,"coach_feedback":""},
      {"id":"53000000-0000-4000-8000-000000000002","athlete_id":a2,"student_id":s2,
       "week_start":"2026-01-05","weight_kg":65,"sleep_quality":7,"stress_level":4,
       "energy_level":7,"adherence_level":8,"mood_level":7,"hunger_level":5,
       "recovery_level":7,"motivation_level":8,"notes":"Check-in QA alumno 02",
       "reviewed_at":"2026-01-08T12:00:00Z","coach_feedback":"Feedback QA"}
,
      {"id":"53000000-0000-4000-8000-000000000003","athlete_id":a1,"student_id":s1,
       "week_start":"2026-11-09","weight_kg":71.8,"sleep_quality":8,"stress_level":3,
       "energy_level":8,"adherence_level":9,"mood_level":8,"hunger_level":4,
       "recovery_level":8,"motivation_level":9,"notes":"Check-in QA 3B pendiente",
       "reviewed_at":None,"coach_feedback":""},
      {"id":"53000000-0000-4000-8000-000000000004","athlete_id":a2,"student_id":s2,
       "week_start":"2026-11-09","weight_kg":64.8,"sleep_quality":7,"stress_level":4,
       "energy_level":7,"adherence_level":8,"mood_level":7,"hunger_level":5,
       "recovery_level":7,"motivation_level":8,"notes":"Check-in QA 3B revisado",
       "reviewed_at":"2026-11-11T12:00:00Z","coach_feedback":"Decisión: Mantener plan\nCómo seguimos: QA 3B"}
    ],"id")

    upsert(api,secret,"coach_media_settings",[
      {"coach_id":coach,"spotify_url":"https://example.invalid/qa-playlist",
       "spotify_title":"Playlist QA local"}
    ],"coach_id")

    upsert(api,secret,"exercise_media",[
      {"id":"54000000-0000-4000-8000-000000000001","coach_id":coach,
       "exercise_key":"dev_ex_press","title":"Video QA Press","video_url":None,
       "storage_path":coach+"/qa-exercise.txt","is_active":True}
    ],"id")

    upsert(api,secret,"fitness_recipes",[
      {"id":"55000000-0000-4000-8000-000000000001","coach_id":coach,"is_global":False,
       "title":"Receta QA local","category":"Dulce","description":"Fixture ficticio",
       "prep_minutes":5,"servings":1,
       "ingredients":[{"name":"Ingrediente QA","amount":"100 g"}],
       "steps":["Paso QA 1"],"kcal_per_serving":300,"protein_g":20,"carbs_g":35,"fat_g":8,
       "tags":["qa","local"]}
    ],"id")

    upsert(api,secret,"athlete_habits",[
      {"id":"55500000-0000-4000-8000-000000000001","athlete_id":a1,"coach_id":coach,
       "name":"QA movimiento diario","category":"movement","active":True,"sort_order":1},
      {"id":"55500000-0000-4000-8000-000000000002","athlete_id":a2,"coach_id":coach,
       "name":"QA hábito nutricional","category":"nutrition","active":True,"sort_order":1}
    ],"id")

    upsert(api,secret,"nutrition_habit_logs",[
      {"id":"56000000-0000-4000-8000-000000000001","athlete_id":a1,"student_id":s1,
       "habit_id":"qa-water","logged_on":"2026-01-12","completed":True}
    ],"id")

    upsert(api,secret,"nutrition_plan_revisions",[
      {"id":"57000000-0000-4000-8000-000000000001",
       "plan_id":"30000000-0000-4000-8000-000000000001","athlete_id":a1,"coach_id":coach,
       "revision":1,"title":"PLAN QA A","notes":"Revisión QA sintética",
       "target_kcal":2200,"target_protein_g":160,"target_carbs_g":250,"target_fat_g":60,
       "plan":plan1,"student_logging_enabled":True}
    ],"id")

    upsert(api,secret,"nutrition_templates",[
      {"id":"58000000-0000-4000-8000-000000000001","coach_id":coach,
       "name":"Plantilla QA","description":"Plantilla solo QA","title":"Plan QA plantilla",
       "notes":"No es un plan real","target_kcal":2100,"target_protein_g":150,
       "target_carbs_g":230,"target_fat_g":60,"plan":plan1}
    ],"id")

    upsert(api,secret,"checkin_schedules",[
      {"id":"59000000-0000-4000-8000-000000000001","athlete_id":a1,"coach_id":coach,
       "cadence":"weekly","next_due":"2026-01-19","remind_time":"09:00:00","active":True,
       "notes":"Cadencia QA","last_completed_at":None},
      {"id":"59000000-0000-4000-8000-000000000002","athlete_id":a2,"coach_id":coach,
       "cadence":"biweekly","next_due":"2026-01-26","remind_time":None,"active":True,
       "notes":"Cadencia QA 2","last_completed_at":None}
    ],"id")

    upsert(api,secret,"coach_payments",[
      {"id":"5a000000-0000-4000-8000-000000000001","athlete_id":a1,"coach_id":coach,
       "due_date":"2026-01-15","amount":1000,"status":"pending","paid_on":None,
       "payment_method":None,"note":"Cobranza QA"},
      {"id":"5a000000-0000-4000-8000-000000000002","athlete_id":a2,"coach_id":coach,
       "due_date":"2026-01-15","amount":1000,"status":"paid","paid_on":"2026-01-14",
       "payment_method":"transfer","note":"Cobranza QA 2"}
    ],"id")

    upsert(api,secret,"student_notices",[
      {"id":"5b000000-0000-4000-8000-000000000001","athlete_id":a1,"coach_id":coach,
       "title":"Aviso QA","body":"Aviso interno ficticio","priority":"info","active":True}
    ],"id")

    for bucket in ("progress-photos","profile-photos","exercise-videos"):
        ensure_bucket(api,secret,bucket)

    # Real local Storage objects so metadata-driven UI does not point at
    # nonexistent files. Tiny valid PNG + text video placeholder.
    png=base64.b64decode(
      "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )
    progress_path=a1+"/2026-01-10/front.png"
    http_bytes("POST",api+"/storage/v1/object/progress-photos/"+progress_path,
               secret,secret,png,content_type="image/png",ok=(200,201))
    http_bytes("POST",api+"/storage/v1/object/exercise-videos/"+coach+"/qa-exercise.txt",
               secret,secret,b"TEAM FJZ LOCAL QA VIDEO PLACEHOLDER",
               content_type="text/plain",ok=(200,201))

    upsert(api,secret,"progress_photos",[
      {"id":"5c000000-0000-4000-8000-000000000001","athlete_id":a1,"student_id":s1,
       "taken_on":"2026-01-10","pose":"front","storage_path":progress_path,
       "notes":"Foto QA local"}
    ],"id")

    print("TEAM FJZ V22 LOCAL FIXTURES READY")
    print("coach@test.local / alumno01@test.local / alumno02@test.local")
    print("production data copied: 0")

if __name__=="__main__":
    main()
