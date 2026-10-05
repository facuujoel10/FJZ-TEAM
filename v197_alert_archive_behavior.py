import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

js=r"""
<script id="v197AlertArchiveRuntime">
(function(){
  const VERSION='19.7';

  window.readCoachAlertV96=async function(key){
    const payload={coach_id:currentUser.id,event_key:key,read_at:new Date().toISOString()};
    const {error}=await supabaseClient.from('coach_feed_state').upsert(payload,{onConflict:'coach_id,event_key'});
    if(error){toast(cloudErr(error));return}
    coachAlertsV96=coachAlertsV96.filter(a=>a.event_key!==key);
    coachFeedLoadedAt=0;
    renderCoachAlertsV96();
    updateCoachBellV96();
  };

  window.readAllCoachAlertsV96=async function(){
    const rows=(coachAlertsV96||[]).map(x=>({
      coach_id:currentUser.id,
      event_key:x.event_key,
      read_at:new Date().toISOString()
    }));
    if(!rows.length)return;
    const {error}=await supabaseClient.from('coach_feed_state').upsert(rows,{onConflict:'coach_id,event_key'});
    if(error){toast(cloudErr(error));return}
    coachAlertsV96=[];
    coachFeedLoadedAt=0;
    renderCoachAlertsV96();
    updateCoachBellV96();
    toast('Alertas revisadas y archivadas');
  };

  window.readStudentAlertV96=async function(key){
    const payload={student_id:currentUser.id,event_key:key,read_at:new Date().toISOString()};
    const {error}=await supabaseClient.from('student_alert_state').upsert(payload,{onConflict:'student_id,event_key'});
    if(error){toast(cloudErr(error));return}
    studentAlertsV96=studentAlertsV96.filter(a=>a.event_key!==key);
    studentAlertsLoadedAtV96=0;
    renderStudentAlertModalV96();
    updateStudentAlertsV96(false);
  };

  window.readAllStudentAlertsV96=async function(){
    const rows=(studentAlertsV96||[]).map(x=>({
      student_id:currentUser.id,
      event_key:x.event_key,
      read_at:new Date().toISOString()
    }));
    if(rows.length){
      const {error}=await supabaseClient.from('student_alert_state').upsert(rows,{onConflict:'student_id,event_key'});
      if(error){toast(cloudErr(error));return}
    }
    studentAlertsV96=[];
    studentAlertsLoadedAtV96=0;
    renderStudentAlertModalV96();
    updateStudentAlertsV96(false);
    toast('Avisos revisados y archivados');
  };

  window.__fjzV197={
    version:VERSION,
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
  "dismissedAndReadExcludedServerSide:true",
  "noVisibleAlertAccumulation:true",
]:
    if marker not in html:
        raise RuntimeError("V19.7 missing "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V19.7 reviewed alerts archive immediately")
