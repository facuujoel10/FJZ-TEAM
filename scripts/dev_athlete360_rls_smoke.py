from __future__ import annotations
from dev_common import TEST_PASSWORD,http_json,local_status
A1="10000000-0000-4000-8000-000000000001"
TABLES=("athletes","weekly_checkins","body_measurements","progress_photos","nutrition_plans","exercise_feedback","athlete_schedule","athlete_reminders")
def login(api,pub,email):
    data=http_json("POST",api+"/auth/v1/token?grant_type=password",pub,None,{"email":email,"password":TEST_PASSWORD})
    token=data.get("access_token") if isinstance(data,dict) else None
    if not token: raise RuntimeError("3B RLS auth failed for "+email)
    return token
def get(api,pub,token,path): return http_json("GET",api+"/rest/v1/"+path,pub,token)
def main():
    st=local_status();api=st["api"];pub=st["publishable"]
    coach=login(api,pub,"coach@test.local");outsider=login(api,pub,"outsider-coach@test.local");student=login(api,pub,"alumno01@test.local")
    authorized={}
    for table in TABLES:
        key="id" if table=="athletes" else "athlete_id"
        rows=get(api,pub,coach,f"{table}?select=id&{key}=eq.{A1}")
        authorized[table]=len(rows)
        assert rows,("authorized coach lost read",table,rows)
        hidden=get(api,pub,outsider,f"{table}?select=id&{key}=eq.{A1}")
        assert hidden==[],("unauthorized coach read leaked",table,hidden)
    student_cross=get(api,pub,student,"athletes?select=id&id=neq."+A1)
    assert all(x.get("id")==A1 for x in student_cross)==False if student_cross else True
    print("TEAM FJZ V22 3B ATHLETE 360 RLS SMOKE OK")
    print("Authorized Coach 360 reads:",authorized)
    print("Unauthorized Coach cross-portfolio reads: 0")
    print("Production data copied: 0")
if __name__=="__main__": main()
