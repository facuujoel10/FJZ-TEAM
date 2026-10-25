import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "intervals":len(re.findall(r"setInterval\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

before=metrics(html)
for marker in [
    'meta name="fjz-global-save-integrity" content="21.04"',
    'id="v303SaveIntegrityRuntime"',
    'id="v304GlobalSaveIntegrityRuntime"',
    "window.submitWeeklyCheckin=async function()",
    "renderTrackingCoachLoaded",
]:
    if marker not in html:
        raise RuntimeError("V21.05 prerequisite missing "+marker)

old_payload="""        notes:(document.getElementById('ciNotes')?.value||'').trim(),
        submitted_at:nowIso()"""
new_payload="""        notes:(document.getElementById('ciNotes')?.value||'').trim(),
        reviewed_at:null,
        submitted_at:nowIso()"""
if html.count(old_payload)!=1:
    raise RuntimeError("V21.05 check-in payload anchor mismatch: "+str(html.count(old_payload)))
html=html.replace(old_payload,new_payload,1)

old_cols="id,athlete_id,student_id,week_start,weight_kg,sleep_quality,stress_level,energy_level,adherence_level,mood_level,hunger_level,recovery_level,motivation_level,notes,submitted_at,created_at,updated_at"
new_cols="id,athlete_id,student_id,week_start,weight_kg,sleep_quality,stress_level,energy_level,adherence_level,mood_level,hunger_level,recovery_level,motivation_level,notes,coach_feedback,reviewed_at,submitted_at,created_at,updated_at"
if html.count(old_cols)<2:
    raise RuntimeError("V21.05 check-in select columns anchors missing: "+str(html.count(old_cols)))
html=html.replace(old_cols,new_cols)

runtime=r"""
<script id="v305CheckinResubmissionLifecycleRuntime">
(function(){
  function staleReview(c){
    if(!c?.reviewed_at)return true;
    const reviewed=Date.parse(c.reviewed_at||0),submitted=Date.parse(c.submitted_at||0);
    return Number.isFinite(submitted)&&(!Number.isFinite(reviewed)||reviewed<submitted);
  }
  window.__fjzCheckinNeedsReviewV305=staleReview;

  function fmtSubmitted(v){
    if(!v)return 'Sin hora';
    const d=new Date(v);
    if(Number.isNaN(d.getTime()))return String(v);
    try{
      return new Intl.DateTimeFormat('es-AR',{
        day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'
      }).format(d);
    }catch(_e){return d.toLocaleString()}
  }

  function annotateCoachCheckins(){
    if(currentProfile?.role!=='coach'||coachTab!=='student'||coachStudentTab!=='tracking')return;
    const host=document.getElementById('coachStudentBody');
    if(!host)return;
    const rows=[...host.querySelectorAll('.track-row')];
    const data=Array.isArray(trackingCache?.checkins)?trackingCache.checkins:[];
    rows.slice(0,data.length).forEach((node,i)=>{
      const c=data[i];
      if(!c)return;
      node.querySelector('.v305-checkin-state')?.remove();
      const pending=staleReview(c);
      const meta=document.createElement('div');
      meta.className='v305-checkin-state '+(pending?'pending':'reviewed');
      meta.innerHTML=
        '<span class="v305-checkin-dot"></span>'+
        '<strong>'+(pending?'Pendiente de revisión':'Revisado')+'</strong>'+
        '<small>Último envío '+fmtSubmitted(c.submitted_at)+'</small>';
      const head=node.querySelector('.track-row-head');
      if(head)head.insertAdjacentElement('afterend',meta);
      else node.insertAdjacentElement('afterbegin',meta);
    });
  }

  const baseCoachTracking=window.renderTrackingCoachLoaded||globalThis.renderTrackingCoachLoaded;
  if(typeof baseCoachTracking==='function'){
    const wrapped=function(){
      const out=baseCoachTracking.apply(this,arguments);
      try{annotateCoachCheckins()}catch(e){console.warn('TEAM FJZ V21.05 annotate check-in',e)}
      return out;
    };
    window.renderTrackingCoachLoaded=wrapped;
    try{renderTrackingCoachLoaded=wrapped}catch(_e){}
  }

  const baseOpenStudent=window.openCoachStudentTabV235||globalThis.openCoachStudentTabV235;
  if(typeof baseOpenStudent==='function'){
    const wrapped=function(id,tab){
      if(tab==='tracking'){
        try{trackingLoadedFor=null}catch(_e){}
        try{coachFeedLoadedAt=0}catch(_e){}
      }
      return baseOpenStudent.apply(this,arguments);
    };
    window.openCoachStudentTabV235=wrapped;
    try{openCoachStudentTabV235=wrapped}catch(_e){}
  }

  const baseRefreshFeed=window.refreshCoachFeed||globalThis.refreshCoachFeed;
  if(typeof baseRefreshFeed==='function'){
    const wrapped=async function(){
      try{coachFeedLoadedAt=0}catch(_e){}
      return baseRefreshFeed.apply(this,arguments);
    };
    window.refreshCoachFeed=wrapped;
    try{refreshCoachFeed=wrapped}catch(_e){}
  }

  window.__fjzV305={
    version:'21.05',
    resubmissionResetsReview:true,
    coachTrackingShowsReviewState:true,
    coachTrackingShowsSubmittedAt:true,
    trackingAlwaysReloadsOnOpen:true,
    feedRefreshBypassesCache:true,
    dbTriggerBackstop:true,
    versionedCheckinFeedKeys:true,
    noExtraTimers:true,
    noExtraListeners:true,
    noExtraObservers:true
  };
})();
</script>
"""

css=r"""
/* TEAM FJZ · V21.05 CHECK-IN RESUBMISSION LIFECYCLE */
.v305-checkin-state{
  display:flex;
  align-items:center;
  flex-wrap:wrap;
  gap:6px;
  margin:8px 0 0;
  padding:7px 9px;
  border-radius:9px;
  border:1px solid #30343b;
  background:#111318;
}
.v305-checkin-state .v305-checkin-dot{
  width:7px;height:7px;border-radius:50%;flex:0 0 7px;
}
.v305-checkin-state strong{font-size:9px;line-height:1.2}
.v305-checkin-state small{font-size:8px;color:#9097a2;line-height:1.2}
.v305-checkin-state.pending{
  border-color:rgba(242,189,85,.28);
  background:rgba(242,189,85,.055);
}
.v305-checkin-state.pending .v305-checkin-dot{background:#f2bd55}
.v305-checkin-state.pending strong{color:#f5cc79}
.v305-checkin-state.reviewed{
  border-color:rgba(89,219,146,.24);
  background:rgba(89,219,146,.045);
}
.v305-checkin-state.reviewed .v305-checkin-dot{background:#59db92}
.v305-checkin-state.reviewed strong{color:#7ee6aa}
@media(min-width:1000px){
  .v305-checkin-state strong{font-size:10.5px}
  .v305-checkin-state small{font-size:9.5px}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V21.05 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-checkin-resubmission-lifecycle" content="21.05">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V21.05 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-checkin-resubmission-lifecycle" content="21.05"',
    'id="v305CheckinResubmissionLifecycleRuntime"',
    "reviewed_at:null",
    "resubmissionResetsReview:true",
    "coachTrackingShowsReviewState:true",
    "coachTrackingShowsSubmittedAt:true",
    "trackingAlwaysReloadsOnOpen:true",
    "feedRefreshBypassesCache:true",
    "dbTriggerBackstop:true",
    "versionedCheckinFeedKeys:true",
    "Pendiente de revisión",
    "Último envío ",
]:
    if marker not in html:
        raise RuntimeError("V21.05 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.05 check-in resubmission lifecycle")
print("V21.05 BEFORE:",before)
print("V21.05 AFTER:",after)
