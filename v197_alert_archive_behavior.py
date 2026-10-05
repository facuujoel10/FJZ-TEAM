import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

old_coach="""  window.readCoachAlertV96=async function(key){
    const payload={coach_id:currentUser.id,event_key:key,read_at:new Date().toISOString(),dismissed_at:null};
    const {error}=await supabaseClient.from('coach_feed_state').upsert(payload,{onConflict:'coach_id,event_key'});
    if(error){toast(cloudErr(error));return}
    const x=coachAlertsV96.find(a=>a.event_key===key);if(x)x.is_read=true;
    coachFeedLoadedAt=0;renderCoachAlertsV96();updateCoachBellV96();
  };"""
new_coach="""  window.readCoachAlertV96=async function(key){
    const payload={coach_id:currentUser.id,event_key:key,read_at:new Date().toISOString()};
    const {error}=await supabaseClient.from('coach_feed_state').upsert(payload,{onConflict:'coach_id,event_key'});
    if(error){toast(cloudErr(error));return}
    coachAlertsV96=coachAlertsV96.filter(a=>a.event_key!==key);
    coachFeedLoadedAt=0;renderCoachAlertsV96();updateCoachBellV96();
  };"""
if html.count(old_coach)!=1:
    raise RuntimeError(f"V19.7 coach read handler count {html.count(old_coach)}")
html=html.replace(old_coach,new_coach,1)

old_all="""  window.readAllCoachAlertsV96=async function(){
    const rows=coachAlertsV96.filter(x=>!x.is_read).map(x=>({coach_id:currentUser.id,event_key:x.event_key,read_at:new Date().toISOString(),dismissed_at:null}));
    if(!rows.length)return;
    const {error}=await supabaseClient.from('coach_feed_state').upsert(rows,{onConflict:'coach_id,event_key'});
    if(error){toast(cloudErr(error));return}
    coachAlertsV96.forEach(x=>x.is_read=true);coachFeedLoadedAt=0;renderCoachAlertsV96();updateCoachBellV96();toast('Alertas marcadas como leídas');
  };"""
new_all="""  window.readAllCoachAlertsV96=async function(){
    const rows=coachAlertsV96.map(x=>({coach_id:currentUser.id,event_key:x.event_key,read_at:new Date().toISOString()}));
    if(!rows.length)return;
    const {error}=await supabaseClient.from('coach_feed_state').upsert(rows,{onConflict:'coach_id,event_key'});
    if(error){toast(cloudErr(error));return}
    coachAlertsV96=[];coachFeedLoadedAt=0;renderCoachAlertsV96();updateCoachBellV96();toast('Alertas revisadas y archivadas');
  };"""
if html.count(old_all)!=1:
    raise RuntimeError(f"V19.7 coach read-all handler count {html.count(old_all)}")
html=html.replace(old_all,new_all,1)

old_student="""  window.readStudentAlertV96=async function(key){
    const payload={student_id:currentUser.id,event_key:key,read_at:new Date().toISOString(),dismissed_at:null};
    const {error}=await supabaseClient.from('student_alert_state').upsert(payload,{onConflict:'student_id,event_key'});
    if(error){toast(cloudErr(error));return}
    const x=studentAlertsV96.find(a=>a.event_key===key);if(x)x.is_read=true;
    studentAlertsLoadedAtV96=0;renderStudentAlertModalV96();updateStudentAlertsV96(false);
  };"""
new_student="""  window.readStudentAlertV96=async function(key){
    const payload={student_id:currentUser.id,event_key:key,read_at:new Date().toISOString()};
    const {error}=await supabaseClient.from('student_alert_state').upsert(payload,{onConflict:'student_id,event_key'});
    if(error){toast(cloudErr(error));return}
    studentAlertsV96=studentAlertsV96.filter(a=>a.event_key!==key);
    studentAlertsLoadedAtV96=0;renderStudentAlertModalV96();updateStudentAlertsV96(false);
  };"""
if html.count(old_student)!=1:
    raise RuntimeError(f"V19.7 student read handler count {html.count(old_student)}")
html=html.replace(old_student,new_student,1)

old_student_all="""  window.readAllStudentAlertsV96=async function(){
    const rows=studentAlertsV96.filter(x=>!x.is_read).map(x=>({student_id:currentUser.id,event_key:x.event_key,read_at:new Date().toISOString(),dismissed_at:null}));
    if(!rows.length)return;
    const {error}=await supabaseClient.from('student_alert_state').upsert(rows,{onConflict:'student_id,event_key'});
    if(error){toast(cloudErr(error));return}
    studentAlertsV96.forEach(x=>x.is_read=true);studentAlertsLoadedAtV96=0;renderStudentAlertModalV96();updateStudentAlertsV96(false);toast('Avisos marcados como leídos');
  };"""
new_student_all="""  window.readAllStudentAlertsV96=async function(){
    const rows=studentAlertsV96.map(x=>({student_id:currentUser.id,event_key:x.event_key,read_at:new Date().toISOString()}));
    if(!rows.length)return;
    const {error}=await supabaseClient.from('student_alert_state').upsert(rows,{onConflict:'student_id,event_key'});
    if(error){toast(cloudErr(error));return}
    studentAlertsV96=[];studentAlertsLoadedAtV96=0;renderStudentAlertModalV96();updateStudentAlertsV96(false);toast('Avisos revisados y archivados');
  };"""
if html.count(old_student_all)!=1:
    raise RuntimeError(f"V19.7 student read-all handler count {html.count(old_student_all)}")
html=html.replace(old_student_all,new_student_all,1)

html=html.replace(">Marcar todo leído</button>",">Archivar revisadas</button>")

js=r"""
<script id="v197AlertArchiveRuntime">
(function(){
  window.__fjzV197={
    version:'19.7',
    readMeansArchived:true,
    immediateLocalRemoval:true,
    dismissedAndReadExcludedServerSide:true,
    noVisibleAlertAccumulation:true
  };
})();
</script>
"""
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "readMeansArchived:true",
  "immediateLocalRemoval:true",
  "noVisibleAlertAccumulation:true",
]:
    if marker not in html:
        raise RuntimeError("V19.7 missing "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V19.7 reviewed alerts archive immediately")
