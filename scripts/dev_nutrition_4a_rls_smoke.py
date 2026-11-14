from __future__ import annotations
from dev_common import local_status
from dev_comment_repository_smoke import login,rest
A1="10000000-0000-4000-8000-000000000001"
A2="10000000-0000-4000-8000-000000000002"
GROUP="66000000-0000-4000-8000-000000000004"

def denied(fn,label):
    try:
        fn()
    except Exception:
        return
    raise AssertionError(label+" unexpectedly allowed")

def main():
    st=local_status();api=st["api"];pub=st["publishable"]
    coach=login(api,pub,"coach@test.local");outsider=login(api,pub,"outsider-coach@test.local")
    s1=login(api,pub,"alumno01@test.local");s2=login(api,pub,"alumno02@test.local")
    p1=rest(api,pub,s1,"GET","nutrition_plans?select=id,athlete_id,title,student_logging_enabled&athlete_id=eq."+A1)
    p2=rest(api,pub,s2,"GET","nutrition_plans?select=id,athlete_id,title,student_logging_enabled&athlete_id=eq."+A2)
    assert len(p1)==1 and p1[0]["title"]=="PLAN QA A" and p1[0]["student_logging_enabled"] is True,p1
    assert len(p2)==1 and p2[0]["title"]=="PLAN QA B" and p2[0]["student_logging_enabled"] is False,p2
    assert rest(api,pub,outsider,"GET","nutrition_plans?select=id&athlete_id=eq."+A1)==[]
    uid=rest(api,pub,s1,"GET","athletes?select=user_id&id=eq."+A1)[0]["user_id"]
    note='FJZ4A_OPTION:{"mealId":"meal_qa_lunch","optionId":"opt_qa_2"}'
    rows=[
      {"athlete_id":A1,"student_id":uid,"logged_on":"2026-11-14","meal_label":"Almuerzo","food_name":"QA 4A arroz","grams":100,"kcal":130,"protein_g":3,"carbs_g":28,"fat_g":0.3,"source":"plan","note":note,"meal_group_id":GROUP},
      {"athlete_id":A1,"student_id":uid,"logged_on":"2026-11-14","meal_label":"Almuerzo","food_name":"QA 4A proteína","grams":100,"kcal":165,"protein_g":31,"carbs_g":0,"fat_g":3.6,"source":"plan","note":note,"meal_group_id":GROUP}
    ]
    created=rest(api,pub,s1,"POST","nutrition_logs",rows,prefer="return=representation")
    assert len(created)==2 and all(x["meal_group_id"]==GROUP for x in created),created
    exact=rest(api,pub,coach,"GET","nutrition_logs?select=id,athlete_id,meal_group_id,note,food_name&meal_group_id=eq."+GROUP)
    assert len(exact)==2 and all(x["athlete_id"]==A1 and "opt_qa_2" in x["note"] for x in exact),exact
    denied(lambda:rest(api,pub,s1,"POST","nutrition_logs",{**rows[0],"athlete_id":A2,"meal_group_id":"66000000-0000-4000-8000-000000000005"},prefer="return=representation"),"cross-athlete student insert")
    uid2=rest(api,pub,s2,"GET","athletes?select=user_id&id=eq."+A2)[0]["user_id"]
    denied(lambda:rest(api,pub,s2,"POST","nutrition_logs",{**rows[0],"athlete_id":A2,"student_id":uid2,"meal_group_id":"66000000-0000-4000-8000-000000000006"},prefer="return=representation"),"disabled-plan student insert")
    recipe=rest(api,pub,s1,"GET","fitness_recipes?select=id,title&title=eq.Receta%20QA%20local")
    assert recipe and recipe[0]["title"]=="Receta QA local",recipe
    rest(api,pub,s1,"DELETE","nutrition_logs?meal_group_id=eq."+GROUP)
    assert rest(api,pub,coach,"GET","nutrition_logs?select=id&meal_group_id=eq."+GROUP)==[]
    print("TEAM FJZ V22 4A NUTRITION AUTH/RLS SMOKE OK")
    print("Plan isolation: OK")
    print("Exact option group persistence: OK")
    print("Disabled logging enforcement: OK")
    print("Recipe linked access: OK")
    print("Production data copied: 0")

if __name__=="__main__":
    main()
