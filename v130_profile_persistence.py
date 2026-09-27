import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# Always request canonical profile fields in athlete bootstrap queries.
html=html.replace(
    "select('id,coach_id,user_id,client_id,name,goal,invite_code,spotify_url,spotify_title,created_at')",
    "select('id,coach_id,user_id,client_id,name,goal,sex,birth_date,occupation_study,start_date,height_cm,invite_code,spotify_url,spotify_title,created_at')"
)
html=html.replace(
    "select('id,coach_id,user_id,client_id,name,goal,invite_code,spotify_url,spotify_title')",
    "select('id,coach_id,user_id,client_id,name,goal,sex,birth_date,occupation_study,start_date,height_cm,invite_code,spotify_url,spotify_title')"
)

# New athletes created by sync should immediately return the full canonical profile shape.
html=html.replace(
    ".select('id,coach_id,user_id,client_id,name,goal,invite_code,spotify_url,spotify_title,created_at').single()",
    ".select('id,coach_id,user_id,client_id,name,goal,sex,birth_date,occupation_study,start_date,height_cm,invite_code,spotify_url,spotify_title,created_at').single()"
)

# Persist top-level compatibility fields locally after coach profile edit.
html=html.replace(
"""      height_cm:data.height_cm??null
    };
    cloudAthletes.set(s.id,{...row,...data});""",
"""      height_cm:data.height_cm??null
    };
    s.heightCm=data.height_cm??null;
    s.startDate=data.start_date||null;
    cloudAthletes.set(s.id,{...row,...data});"""
)

# V12.6 profile-first renderer: merge canonical cloud row with snapshot fallback,
# so an incomplete cache can never visually erase already-saved profile data.
html=html.replace(
"""    const row=cloudAthletes?.get?.(s.id)||null;
    let profile=el('v114ProfileCard');""",
"""    const cloudRow=cloudAthletes?.get?.(s.id)||null;
    const localProfile=s.profile||{};
    const row={
      ...localProfile,
      ...(cloudRow||{}),
      name:cloudRow?.name||s.name,
      goal:cloudRow?.goal||s.goal,
      sex:cloudRow?.sex??localProfile.sex??null,
      birth_date:cloudRow?.birth_date??localProfile.birth_date??null,
      occupation_study:cloudRow?.occupation_study??localProfile.occupation_study??null,
      start_date:cloudRow?.start_date??localProfile.start_date??s.startDate??null,
      height_cm:cloudRow?.height_cm??localProfile.height_cm??s.heightCm??null
    };
    let profile=el('v114ProfileCard');"""
)

# When cloud bootstrap maps rows + snapshots, inject canonical profile into local state too.
old_coach_map="""const students=rows.map(r=>{const s=clone(by.get(r.id)||defaultStudent(r.client_id,r.name,r.goal));s.id=r.client_id;s.name=r.name||s.name;s.goal=r.goal||s.goal;return s});"""
new_coach_map="""const students=rows.map(r=>{const s=clone(by.get(r.id)||defaultStudent(r.client_id,r.name,r.goal));s.id=r.client_id;s.name=r.name||s.name;s.goal=r.goal||s.goal;s.profile={...(s.profile||{}),sex:r.sex??s.profile?.sex??null,birth_date:r.birth_date??s.profile?.birth_date??null,occupation_study:r.occupation_study??s.profile?.occupation_study??null,start_date:r.start_date??s.profile?.start_date??null,height_cm:r.height_cm??s.profile?.height_cm??null};s.heightCm=r.height_cm??s.heightCm??null;s.startDate=r.start_date??s.startDate??null;return s});"""
html=html.replace(old_coach_map,new_coach_map)

old_student_map="""const s=clone(snap?.data||defaultStudent(ath.client_id,ath.name,ath.goal));s.id=ath.client_id;s.name=ath.name||s.name;s.goal=ath.goal||s.goal;"""
new_student_map="""const s=clone(snap?.data||defaultStudent(ath.client_id,ath.name,ath.goal));s.id=ath.client_id;s.name=ath.name||s.name;s.goal=ath.goal||s.goal;s.profile={...(s.profile||{}),sex:ath.sex??s.profile?.sex??null,birth_date:ath.birth_date??s.profile?.birth_date??null,occupation_study:ath.occupation_study??s.profile?.occupation_study??null,start_date:ath.start_date??s.profile?.start_date??null,height_cm:ath.height_cm??s.profile?.height_cm??null};s.heightCm=ath.height_cm??s.heightCm??null;s.startDate=ath.start_date??s.startDate??null;"""
html=html.replace(old_student_map,new_student_map)

# Build-time verification: these fields must exist in both bootstrap queries.
required="sex,birth_date,occupation_study,start_date,height_cm"
if html.count(required) < 2:
    raise RuntimeError("Profile persistence bootstrap fields missing")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V13.0 profile persistence frontend:",len(html),"bytes")
