import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

before={
  "timeouts":len(re.findall(r"setTimeout\s*\(",html)),
  "observers":len(re.findall(r"new MutationObserver",html)),
  "render_wrappers":len(re.findall(r"(?:window\.)?render\s*=\s*function",html)),
}

# ---------- 1) Make athlete bootstrap richer so opening a profile doesn't need another request ----------
old_coach="select('id,coach_id,user_id,client_id,name,goal,invite_code,spotify_url,spotify_title,created_at')"
new_coach="select('id,coach_id,user_id,client_id,name,goal,sex,birth_date,occupation_study,start_date,height_cm,invite_code,spotify_url,spotify_title,created_at')"
html=html.replace(old_coach,new_coach)

old_student="select('id,coach_id,user_id,client_id,name,goal,invite_code,spotify_url,spotify_title')"
new_student="select('id,coach_id,user_id,client_id,name,goal,sex,birth_date,occupation_study,start_date,height_cm,invite_code,spotify_url,spotify_title')"
html=html.replace(old_student,new_student)

# ---------- 2) Shared render scheduler: one visual pass per frame ----------
head=r"""
<script id="v125RenderSchedulerHead">
(function(){
  let postTasks=new Map();
  let postRaf=0;
  let renderRaf=0;

  window.fjzPostRenderV125=function(key,fn){
    if(typeof fn!=='function')return;
    postTasks.set(String(key||'task'),fn);
    if(postRaf)return;
    postRaf=requestAnimationFrame(()=>{
      postRaf=0;
      const batch=[...postTasks.values()];
      postTasks.clear();
      for(const task of batch){
        try{task()}catch(e){console.warn('TEAM FJZ post-render',e)}
      }
    });
  };

  window.fjzScheduleRenderV125=function(){
    if(renderRaf)return;
    renderRaf=requestAnimationFrame(()=>{
      renderRaf=0;
      try{if(typeof render==='function')render()}catch(e){console.error('TEAM FJZ render',e)}
    });
  };
})();
</script>
"""
html=html.replace("</head>",head+"\n</head>",1)

def edit_script(doc, script_id, transform):
    pat=re.compile(r'(<script id="'+re.escape(script_id)+r'">)(.*?)(</script>)',re.S)
    m=pat.search(doc)
    if not m:
        return doc,0
    body=transform(m.group(2))
    return doc[:m.start()]+m.group(1)+body+m.group(3)+doc[m.end():],1

edited=[]

# V9.6 alerts: 3 delayed passes -> 1 frame
def t96(b):
    old="""  const oldRenderV96=window.render;
  window.render=function(){
    oldRenderV96();
    setTimeout(injectAlertsV96,80);
    setTimeout(injectAlertsV96,500);
    setTimeout(injectAlertsV96,1100);
  };"""
    new="""  const oldRenderV96=window.render;
  window.render=function(){
    const out=oldRenderV96.apply(this,arguments);
    fjzPostRenderV125('alerts-v96',injectAlertsV96);
    return out;
  };"""
    return b.replace(old,new).replace("setTimeout(injectAlertsV96,250);","fjzPostRenderV125('alerts-v96-init',injectAlertsV96);")
html,n=edit_script(html,"v96AlertCenterRuntime",t96);edited.append(("v96",n))

# V9.8 precision: coalesce polishing
def t98(b):
    b=b.replace("""  const oldRenderV98=window.render;
  window.render=function(){
    oldRenderV98();
    setTimeout(polishV98,40);
    setTimeout(polishV98,250);
    setTimeout(polishV98,850);
  };""","""  const oldRenderV98=window.render;
  window.render=function(){
    const out=oldRenderV98.apply(this,arguments);
    fjzPostRenderV125('polish-v98',polishV98);
    return out;
  };""")
    b=b.replace("""  const observerV98=new MutationObserver(function(){
    clearTimeout(window.__v98PolishTimer);
    window.__v98PolishTimer=setTimeout(polishV98,35);
  });""","""  const observerV98=new MutationObserver(function(){
    fjzPostRenderV125('polish-v98',polishV98);
  });""")
    b=b.replace("""  setTimeout(function(){
    const view=document.getElementById('view');
    if(view)observerV98.observe(view,{childList:true,subtree:true});
    polishV98();
  },200);""","""  fjzPostRenderV125('polish-v98-init',function(){
    const view=document.getElementById('view');
    if(view)observerV98.observe(view,{childList:true,subtree:true});
    polishV98();
  });""")
    return b
html,n=edit_script(html,"v98PrecisionPolishRuntime",t98);edited.append(("v98",n))

# V9.9 audit: same
def t99(b):
    b=b.replace("""  const oldRenderV99=window.render;
  window.render=function(){
    oldRenderV99();
    setTimeout(auditPolishV99,30);
    setTimeout(auditPolishV99,220);
    setTimeout(auditPolishV99,800);
  };""","""  const oldRenderV99=window.render;
  window.render=function(){
    const out=oldRenderV99.apply(this,arguments);
    fjzPostRenderV125('audit-v99',auditPolishV99);
    return out;
  };""")
    b=b.replace("""  const obsV99=new MutationObserver(function(){
    clearTimeout(window.__v99AuditTimer);
    window.__v99AuditTimer=setTimeout(auditPolishV99,45);
  });""","""  const obsV99=new MutationObserver(function(){
    fjzPostRenderV125('audit-v99',auditPolishV99);
  });""")
    b=b.replace("""  setTimeout(function(){
    const view=document.getElementById('view');
    if(view)obsV99.observe(view,{childList:true,subtree:true});
    auditPolishV99();
  },180);""","""  fjzPostRenderV125('audit-v99-init',function(){
    const view=document.getElementById('view');
    if(view)obsV99.observe(view,{childList:true,subtree:true});
    auditPolishV99();
  });""")
    return b
html,n=edit_script(html,"v99AuditRuntime",t99);edited.append(("v99",n))

# V10 core cleanup
def t100(b):
    b=b.replace("""  const previousRender=window.render;
  window.render=function(){
    const out=previousRender.apply(this,arguments);
    setTimeout(polish,40);
    setTimeout(polish,300);
    return out;
  };""","""  const previousRender=window.render;
  window.render=function(){
    const out=previousRender.apply(this,arguments);
    fjzPostRenderV125('core-polish-v100',polish);
    return out;
  };""")
    b=b.replace("""  const observer=new MutationObserver(()=>{
    clearTimeout(polishTimer);
    polishTimer=setTimeout(polish,45);
  });""","""  const observer=new MutationObserver(()=>{
    fjzPostRenderV125('core-polish-v100',polish);
  });""")
    b=b.replace("""  setTimeout(()=>{
    const view=document.getElementById('view');
    if(view)observer.observe(view,{childList:true,subtree:true});
    polish();
  },180);""","""  fjzPostRenderV125('core-polish-v100-init',()=>{
    const view=document.getElementById('view');
    if(view)observer.observe(view,{childList:true,subtree:true});
    polish();
  });""")
    return b
html,n=edit_script(html,"v100CoreRuntime",t100);edited.append(("v100",n))

# V10.1 avatar adjust
def t101(b):
    b=b.replace("""  const oldRender=window.render;
  window.render=function(){const out=oldRender.apply(this,arguments);setTimeout(inject,120);setTimeout(inject,600);return out};""","""  const oldRender=window.render;
  window.render=function(){const out=oldRender.apply(this,arguments);fjzPostRenderV125('avatar-adjust-v101',inject);return out};""")
    b=b.replace("  setTimeout(inject,250);","  fjzPostRenderV125('avatar-adjust-v101-init',inject);")
    return b
html,n=edit_script(html,"v101AvatarAdjustRuntime",t101);edited.append(("v101",n))

# V11 alerts polish
def t110(b):
    return b.replace("""  const baseRenderV110=window.render;
  window.render=function(){
    const out=baseRenderV110.apply(this,arguments);
    setTimeout(polishCoachAlertsV110,0);
    setTimeout(polishCoachAlertsV110,500);
    return out;
  };""","""  const baseRenderV110=window.render;
  window.render=function(){
    const out=baseRenderV110.apply(this,arguments);
    fjzPostRenderV125('alerts-polish-v110',polishCoachAlertsV110);
    return out;
  };""")
html,n=edit_script(html,"v110FinalRuntime",t110);edited.append(("v110",n))

# V11.4 coach profile: reuse cloudAthletes row and dedupe both injection paths to same frame/key
def t114(b):
    b=b.replace("""    const mapRow=cloudAthletes?.get?.(s.id);
    if(!supabaseClient||!mapRow?.id){
      const fallback={client_id:s.id,name:s.name,goal:s.goal};
      profileCacheV114.set(s.id,fallback);
      return fallback;
    }
    const {data,error}=await supabaseClient.from('athletes')
      .select('id,coach_id,user_id,client_id,name,goal,sex,birth_date,occupation_study,start_date,height_cm,invite_code,created_at')
      .eq('id',mapRow.id).single();""","""    const mapRow=cloudAthletes?.get?.(s.id);
    if(mapRow?.id && ('height_cm' in mapRow || 'birth_date' in mapRow || 'sex' in mapRow)){
      profileCacheV114.set(s.id,mapRow);
      return mapRow;
    }
    if(!supabaseClient||!mapRow?.id){
      const fallback={client_id:s.id,name:s.name,goal:s.goal};
      profileCacheV114.set(s.id,fallback);
      return fallback;
    }
    const {data,error}=await supabaseClient.from('athletes')
      .select('id,coach_id,user_id,client_id,name,goal,sex,birth_date,occupation_study,start_date,height_cm,invite_code,created_at')
      .eq('id',mapRow.id).single();""")
    b=b.replace("      setTimeout(injectProfileV114,50);","      fjzPostRenderV125('coach-profile-v114',injectProfileV114);")
    b=b.replace("      setTimeout(injectProfileV114,80);","      fjzPostRenderV125('coach-profile-v114',injectProfileV114);")
    return b
html,n=edit_script(html,"v114CoachProfileRuntime",t114);edited.append(("v114",n))

# V11.5 student profile: reuse loaded athlete row
def t115(b):
    b=b.replace("""    if(myAthleteV115&&!force)return myAthleteV115;
    const {data,error}=await supabaseClient.from('athletes')
      .select('id,name,goal,sex,birth_date,occupation_study,height_cm,start_date,user_id')
      .eq('user_id',currentUser.id).maybeSingle();""","""    if(myAthleteV115&&!force)return myAthleteV115;
    const mapRow=[...cloudAthletes.values()].find(x=>x.user_id===currentUser.id);
    if(!force&&mapRow?.id&&('height_cm' in mapRow||'birth_date' in mapRow||'sex' in mapRow)){
      myAthleteV115=mapRow;
      return myAthleteV115;
    }
    const {data,error}=await supabaseClient.from('athletes')
      .select('id,name,goal,sex,birth_date,occupation_study,height_cm,start_date,user_id')
      .eq('user_id',currentUser.id).maybeSingle();""")
    b=b.replace("      setTimeout(injectMyProfileV115,80);","      fjzPostRenderV125('student-profile-v115',injectMyProfileV115);")
    return b
html,n=edit_script(html,"v115StudentProfileFieldsRuntime",t115);edited.append(("v115",n))

# V11.6 avatar
def t116(b):
    return b.replace("      setTimeout(injectAvatarV116,120);","      fjzPostRenderV125('student-avatar-v116',injectAvatarV116);").replace("      setTimeout(()=>render(),350);","      fjzScheduleRenderV125();")
html,n=edit_script(html,"v116StudentAvatarFixRuntime",t116);edited.append(("v116",n))

# Cleanup guards: one frame, no long visual aftershocks
def t117(b):
    b=re.sub(r"""    if\(currentProfile\?\.role==='student'&&mode==='student'&&studentTab==='home'\)\{\s*
      setTimeout\(cleanupStudentProfileV117,20\);\s*
      setTimeout\(cleanupStudentProfileV117,180\);\s*
      setTimeout\(cleanupStudentProfileV117,800\);\s*
    \}""","""    if(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'){
      fjzPostRenderV125('profile-clean-v117',cleanupStudentProfileV117);
    }""",b)
    return b.replace("  setTimeout(cleanupStudentProfileV117,200);","  fjzPostRenderV125('profile-clean-v117-init',cleanupStudentProfileV117);")
html,n=edit_script(html,"v117ProfileDedupRuntime",t117);edited.append(("v117",n))

def t118(b):
    b=b.replace("""    setTimeout(enforceSingleStudentProfileV118,50);
    setTimeout(enforceSingleStudentProfileV118,400);""","""    fjzPostRenderV125('profile-single-v118',enforceSingleStudentProfileV118);""")
    return b.replace("  setTimeout(enforceSingleStudentProfileV118,250);","  fjzPostRenderV125('profile-single-v118-init',enforceSingleStudentProfileV118);")
html,n=edit_script(html,"v118AuditCleanupRuntime",t118);edited.append(("v118",n))

def t119(b):
    b=b.replace("""  const obs=new MutationObserver(muts=>{
    if(currentProfile?.role!=='student')return;
    let relevant=false;
    for(const m of muts){
      if(m.addedNodes?.length){relevant=true;break}
    }
    if(relevant)removeLegacyProfileV119();
  });""","""  const obs=new MutationObserver(muts=>{
    if(currentProfile?.role!=='student')return;
    if(muts.some(m=>m.addedNodes?.length))fjzPostRenderV125('profile-guard-v119',removeLegacyProfileV119);
  });""")
    b=b.replace("""    removeLegacyProfileV119();
    queueMicrotask(removeLegacyProfileV119);""","""    fjzPostRenderV125('profile-guard-v119',removeLegacyProfileV119);""")
    return b
html,n=edit_script(html,"v119LegacyProfileHardGuard",t119);edited.append(("v119",n))

# V12.3 dashboard cleanup observer + delayed work -> one coalesced pass
def t123(b):
    b=b.replace("""    setTimeout(removeLegacyAttentionV123,20);
    setTimeout(injectDashboardGuideV123,120);
    setTimeout(removeLegacyAttentionV123,450);""","""    fjzPostRenderV125('dashboard-clean-v123',()=>{
      removeLegacyAttentionV123();
      injectDashboardGuideV123();
    });""")
    b=b.replace("""      removeLegacyAttentionV123();
      injectDashboardGuideV123();""","""      fjzPostRenderV125('dashboard-clean-v123',()=>{
        removeLegacyAttentionV123();
        injectDashboardGuideV123();
      });""")
    return b
html,n=edit_script(html,"v123AlertCenterCleanupRuntime",t123);edited.append(("v123",n))

# V12.4 admin/version post work -> one frame
def t124(b):
    b=b.replace("""    setTimeout(injectCoachAdminCardV124,60);
    setTimeout(normalizeVersionV124,100);""","""    fjzPostRenderV125('coach-admin-v124',injectCoachAdminCardV124);
    fjzPostRenderV125('version-v124',normalizeVersionV124);""")
    return b.replace("  setTimeout(normalizeVersionV124,150);","  fjzPostRenderV125('version-v124-init',normalizeVersionV124);")
html,n=edit_script(html,"v124CoachAdminRuntime",t124);edited.append(("v124",n))

# ---------- 3) Realtime UI refreshes: coalesce bursts into one render frame ----------
html=re.sub(r"setTimeout\(\(\)=>render\(\),\s*(250|350|400)\)", "fjzScheduleRenderV125()", html)

# ---------- 4) Smoother visual commit ----------
css=r"""
<style id="v125RenderPerformanceStyles">
#view{contain:layout style}
#view>.hero,#coachStudentBody,#studentSubBody{overflow-anchor:none}
@media (prefers-reduced-motion:no-preference){
  #coachStudentBody>.card,#studentSubBody>.card,#view>.card{animation:v125In .11s ease-out both}
  @keyframes v125In{from{opacity:.82;transform:translateY(2px)}to{opacity:1;transform:none}}
}
</style>
"""
html=html.replace("</head>",css+"\n</head>",1)

# Current release
html=re.sub(r"TEAM FJZ V\d+(?:\.\d+)+","TEAM FJZ V12.5",html)
html=re.sub(r'(<meta\s+name=["\']fjz-release["\']\s+content=["\'])[^"\']*(["\'])',r'\g<1>12.5\g<2>',html,flags=re.I)

after={
  "timeouts":len(re.findall(r"setTimeout\s*\(",html)),
  "observers":len(re.findall(r"new MutationObserver",html)),
  "render_wrappers":len(re.findall(r"(?:window\.)?render\s*=\s*function",html)),
}

p.write_text(html,encoding="utf-8")

swp=pathlib.Path("public/sw.js")
sw=swp.read_text(encoding="utf-8")
sw=re.sub(r"team-fjz-v\d+(?:-\d+)+","team-fjz-v12-5",sw)
swp.write_text(sw,encoding="utf-8")

print("TEAM FJZ V12.5 render optimization:",len(html),"bytes")
print("V12.5 scripts edited:",edited)
print("V12.5 render metrics before:",before)
print("V12.5 render metrics after:",after)
