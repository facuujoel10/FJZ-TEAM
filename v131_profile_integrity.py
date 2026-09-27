import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# Coach profile save: profile writes must be isolated from the global snapshot sync.
old = """    s.name=data.name;
    s.goal=data.goal;
    s.profile={
      ...(s.profile||{}),
      sex:data.sex||null,
      birth_date:data.birth_date||null,
      occupation_study:data.occupation_study||null,
      start_date:data.start_date||null,
      height_cm:data.height_cm??null
    };
    s.heightCm=data.height_cm??null;
    s.startDate=data.start_date||null;
    cloudAthletes.set(s.id,{...row,...data});
    profileCacheV114.set(s.id,data);
    saveState();
    try{await syncCloudNow()}catch(e){console.warn('profile sync V11.4',e)}
    closeModal();
    render();
    toast('Perfil actualizado');"""

new = """    s.name=data.name;
    s.goal=data.goal;
    s.profile={
      ...(s.profile||{}),
      sex:data.sex??null,
      birth_date:data.birth_date??null,
      occupation_study:data.occupation_study??null,
      start_date:data.start_date??null,
      height_cm:data.height_cm??null
    };
    s.heightCm=data.height_cm??null;
    s.startDate=data.start_date??null;

    const canonical={...row,...data};
    cloudAthletes.set(s.id,canonical);
    profileCacheV114.set(s.id,canonical);

    // Persist the local view quietly. Do NOT schedule the global routine/history
    // sync for a profile-only edit.
    try{
      window.__fjzCloudApplying=true;
      localStorage.setItem('fjz_v4_state',JSON.stringify(state));
    }finally{
      window.__fjzCloudApplying=false;
    }

    // Ignore the Realtime echo from our own canonical athlete update.
    cloudLastWrite=Date.now();

    closeModal();
    render();
    toast('Perfil actualizado y guardado');"""

if old not in html:
    raise RuntimeError("V13.1 could not locate coach profile save block")
html=html.replace(old,new,1)

# Student profile save: immediately mirror returned canonical data into both
# cloudAthletes and local state. Realtime can then refresh without a visible gap.
old2 = """    if(error){toast(cloudErr(error));return}
    myAthleteV115=data||null;
    closeModal();
    render();
    toast('Datos actualizados');"""
new2 = """    if(error){toast(cloudErr(error));return}
    myAthleteV115=data||null;

    if(data){
      const s=student();
      const existing=cloudAthletes.get(s.id)||{};
      cloudAthletes.set(s.id,{...existing,...data});
      s.profile={
        ...(s.profile||{}),
        sex:data.sex??null,
        birth_date:data.birth_date??null,
        occupation_study:data.occupation_study??null,
        start_date:data.start_date??s.profile?.start_date??null,
        height_cm:data.height_cm??null
      };
      s.heightCm=data.height_cm??null;
      try{
        window.__fjzCloudApplying=true;
        localStorage.setItem('fjz_v4_state',JSON.stringify(state));
      }finally{
        window.__fjzCloudApplying=false;
      }
      cloudLastWrite=Date.now();
    }

    closeModal();
    render();
    toast('Datos actualizados y guardados');"""
if old2 not in html:
    raise RuntimeError("V13.1 could not locate student profile save block")
html=html.replace(old2,new2,1)

# Final integrity assertions.
if "try{await syncCloudNow()}catch(e){console.warn('profile sync V11.4'" in html:
    raise RuntimeError("Legacy global sync still attached to profile save")
for required in [
    "sex,birth_date,occupation_study,start_date,height_cm",
    "Perfil actualizado y guardado",
    "Datos actualizados y guardados",
]:
    if required not in html:
        raise RuntimeError("Missing V13.1 integrity marker: "+required)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V13.1 profile integrity:",len(html),"bytes")
