import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V19.2 GENERAL STABILITY / REALTIME / VISUAL CONSOLIDATION
# =========================================================

def metrics(doc):
    return {
      "bytes":len(doc.encode("utf-8")),
      "scripts":len(re.findall(r"<script\b",doc,re.I)),
      "styles":len(re.findall(r"<style\b",doc,re.I)),
      "render_assignments":len(re.findall(r"(?:window\.)?render\s*=\s*function",doc)),
      "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
      "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
      "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
      "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
      "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
      "scroll_calls":len(re.findall(r"(?:scrollTo|scrollIntoView)\s*\(",doc)),
      "post_render_refs":len(re.findall(r"__fjzPostRenderV176",doc)),
      "channel_defs":len(re.findall(r"\.channel\s*\(",doc)),
    }

before=metrics(html)

def remove_tag(doc,tag,ident):
    pat=re.compile(r'\s*<'+tag+r' id=["\']'+re.escape(ident)+r'["\']>.*?</'+tag+r'>\s*',re.S|re.I)
    return pat.subn("\n",doc,count=1)

removed=[]
for tag,ident in [
  ("script","v186ExactFieldAlignmentRuntime"),
  ("style","v186ExactFieldAlignmentStyles"),
  ("script","v187PairedTrackingGridRuntime"),
  ("style","v187PairedTrackingGridStyles"),
  ("script","v188ScrollInteractionFixRuntime"),
  ("script","v191ActionGeometryAuditRuntime"),
  ("style","v191ActionGeometryAuditStyles"),
]:
    html,n=remove_tag(html,tag,ident)
    if n: removed.append(ident)

# ---------------------------------------------------------
# Single Realtime authority: V13.2 unified channel.
# Disable legacy V9.6 alert channel and V12.2 followup channel.
# Their cache invalidation is already handled by invalidateV132().
# ---------------------------------------------------------
v96_pat=re.compile(
    r"""\s*const oldSetupRealtimeV96=window\.setupRealtime;\s*
        if\(typeof oldSetupRealtimeV96==='function'\)\{\s*
        window\.setupRealtime=function\(\)\{.*?\n\s*\};\s*
        \}\s*
        (?=Object\.assign\(window,)""",
    re.S|re.X
)
html,n_v96=v96_pat.subn("\n  window.__fjzV96RealtimeDelegatedV192=true;\n\n  ",html,count=1)

v122_pat=re.compile(
    r"""\s*const baseSetupV122=window\.setupRealtime;\s*
        window\.setupRealtime=function\(\)\{.*?\n\};\s*
        (?=window\.__fjzFollowupsV122=)""",
    re.S|re.X
)
html,n_v122=v122_pat.subn("\nwindow.__fjzV122RealtimeDelegatedV192=true;\n\n",html,count=1)

if n_v96 not in (0,1):
    raise RuntimeError(f"V19.2 unexpected V96 realtime wrapper count: {n_v96}")
if n_v122 not in (0,1):
    raise RuntimeError(f"V19.2 unexpected V122 realtime wrapper count: {n_v122}")

# ---------------------------------------------------------
# Expand the unified Realtime view map so removing those old channels does
# not lose live updates where the data is actually visible.
# ---------------------------------------------------------
replacements={
"home:new Set(['athlete_schedule','athlete_reminders','student_notices','workout_sessions','workout_sets','progression_recommendations']),":
"home:new Set(['athlete_schedule','athlete_reminders','student_notices','weekly_checkins','nutrition_plans','exercise_feedback','workout_sessions','workout_sets','progression_recommendations']),",

"agenda:new Set(['athlete_schedule','athlete_reminders']),":
"agenda:new Set(['athlete_schedule','athlete_reminders','checkin_schedules','coach_payments']),",

"if(coachTab==='agenda')return ['athlete_schedule','athlete_reminders'].includes(table);":
"if(coachTab==='agenda')return ['athlete_schedule','athlete_reminders','checkin_schedules','coach_payments'].includes(table);",

"summary:new Set(['weekly_checkins','body_measurements','nutrition_plans','exercise_feedback','workout_sessions','workout_sets','progression_recommendations','progress_photos']),":
"summary:new Set(['weekly_checkins','body_measurements','nutrition_plans','exercise_feedback','student_notices','athlete_reminders','checkin_schedules','workout_sessions','workout_sets','progression_recommendations','progress_photos']),"
}
counts={}
for old,new in replacements.items():
    n=html.count(old)
    counts[old[:28]]=n
    html=html.replace(old,new)

if counts.get("home:new Set(['athlete_sche",0)!=1:
    raise RuntimeError("V19.2 student-home realtime map not found")
if counts.get("agenda:new Set(['athlete_sc",0)<2:
    raise RuntimeError("V19.2 agenda realtime maps not found")
if counts.get("if(coachTab==='agenda')retu",0)!=1:
    raise RuntimeError("V19.2 coach agenda realtime map not found")
if counts.get("summary:new Set(['weekly_che",0)!=1:
    raise RuntimeError("V19.2 coach summary realtime map not found")

css=r"""
<style id="v192GeneralStabilityStyles">
/* =========================================================
   V19.2 · One final geometry authority for dynamic tracking
   pairs and workout actions. No runtime layout measurements.
   ========================================================= */
.v192-pair-grid{
  display:grid!important;
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:9px!important;
  align-items:start!important;
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  box-sizing:border-box!important;
}
.v192-pair-grid>label{
  display:flex!important;
  flex-direction:column!important;
  justify-content:flex-start!important;
  gap:5px!important;
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  min-height:61px!important;
  margin:0!important;
  padding:0!important;
  line-height:14px!important;
  box-sizing:border-box!important;
  overflow:hidden!important;
}
.v192-pair-grid>label.span2{grid-column:1/-1!important}
.v192-pair-grid>label>.input,
.v192-pair-grid>label>input,
.v192-pair-grid>label>select,
.v192-pair-grid>label>.v181-date-clip{
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  height:42px!important;
  min-height:42px!important;
  max-height:42px!important;
  margin:0!important;
  box-sizing:border-box!important;
  flex:0 0 42px!important;
}
.v192-pair-grid .v181-date-clip{
  display:block!important;
  padding:0!important;
  border:0!important;
  overflow:hidden!important;
  line-height:0!important;
}
.v192-pair-grid .v181-date-clip>input[type="date"]{
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  height:42px!important;
  min-height:42px!important;
  max-height:42px!important;
  margin:0!important;
  box-sizing:border-box!important;
  position:static!important;
  transform:none!important;
}
.v192-pair-grid input[type="date"]::-webkit-date-and-time-value,
.v192-pair-grid input[type="date"]::-webkit-datetime-edit,
.v192-pair-grid input[type="date"]::-webkit-datetime-edit-fields-wrapper{
  display:flex!important;
  align-items:center!important;
  height:100%!important;
  min-height:0!important;
  margin:0!important;
  padding:0!important;
  line-height:normal!important;
}
.v192-pair-grid input[type="date"]::-webkit-calendar-picker-indicator{
  align-self:center!important;
  flex:0 0 auto!important;
  margin:0 0 0 6px!important;
  padding:0!important;
}

button.v192-session-finish,
.btn.v192-session-finish{
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  min-height:48px!important;
  height:auto!important;
  padding:12px 16px!important;
  margin-top:12px!important;
  box-sizing:border-box!important;
  border-radius:12px!important;
  font-size:12px!important;
  font-weight:850!important;
  line-height:1.2!important;
  text-align:center!important;
  white-space:normal!important;
  overflow:visible!important;
  overflow-wrap:break-word!important;
}
button.v192-session-save-confirm{
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
  min-height:42px!important;
  height:auto!important;
  padding:9px 13px!important;
  box-sizing:border-box!important;
  line-height:1.2!important;
  white-space:normal!important;
  text-align:center!important;
}

/* Stable mobile geometry: no transforms/animations while working in a
   workout, and no browser scroll anchoring fighting DOM updates. */
body.v146-workout-stable #view,
body.v146-workout-stable .session-card,
body.v146-workout-stable .set-grid{
  transform:none!important;
  transition:none!important;
  animation:none!important;
}
html,body,#view,#studentSubBody,#coachStudentBody{
  overflow-anchor:none;
}

@media(max-width:390px){
  .v192-pair-grid{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:8px!important;
  }
}
</style>
"""

js=r"""
<script id="v192GeneralStabilityRuntime">
(function(){
  const VERSION='19.2';
  const TRACK_IDS=['ciWeight','ciWeek','mDate','mWeight','mWaist','mAbd','mHip','mChest','progressPhotoDate','progressPhotoPose','progressPhotoFile'];

  function applyTrackingGeometryV192(){
    TRACK_IDS.forEach(id=>{
      document.querySelectorAll('#'+id).forEach(node=>{
        const grid=node.closest('.form-grid');
        if(grid)grid.classList.add('v192-pair-grid');
      });
    });
  }

  function markWorkoutActionsV192(){
    document.querySelectorAll('button[onclick*="finishWorkout"],.btn[onclick*="finishWorkout"]').forEach(btn=>{
      btn.classList.add('v192-session-finish');
    });
    document.querySelectorAll('button[onclick*="confirmPartialSessionV106"],.btn[onclick*="confirmPartialSessionV106"]').forEach(btn=>{
      btn.classList.add('v192-session-save-confirm');
    });
  }

  function polishV192(){
    applyTrackingGeometryV192();
    markWorkoutActionsV192();
  }

  const basePostV192=window.__fjzPostRenderV176;
  window.__fjzPostRenderV176=function(){
    const out=basePostV192?.apply(this,arguments);
    polishV192();
    return out;
  };

  ['renderTrackingCoachLoaded','renderStudentTrackingHistory'].forEach(name=>{
    const fn=window[name];
    if(typeof fn!=='function'||fn.__v192Wrapped)return;
    const wrapped=function(){
      const out=fn.apply(this,arguments);
      Promise.resolve(out).finally(polishV192);
      return out;
    };
    wrapped.__v192Wrapped=true;
    window[name]=wrapped;
    try{globalThis[name]=wrapped}catch(_e){}
  });

  ['renderStudentRoutine','renderStudentRoutineV94','renderWorkoutDay'].forEach(name=>{
    const fn=window[name];
    if(typeof fn!=='function'||fn.__v192Wrapped)return;
    const wrapped=function(){
      const out=fn.apply(this,arguments);
      queueMicrotask(polishV192);
      return out;
    };
    wrapped.__v192Wrapped=true;
    window[name]=wrapped;
    try{globalThis[name]=wrapped}catch(_e){}
  });

  function cleanupDuplicateRealtimeV192(){
    if(!supabaseClient)return;
    ['__fjzV96AlertChannel','__fjzV122Channel'].forEach(key=>{
      const ch=window[key];
      if(!ch)return;
      try{supabaseClient.removeChannel(ch)}catch(_e){}
      window[key]=null;
    });
  }

  const baseSetupRealtimeV192=window.setupRealtime;
  window.setupRealtime=function(){
    const out=baseSetupRealtimeV192?.apply(this,arguments);
    Promise.resolve().then(cleanupDuplicateRealtimeV192);
    return out;
  };

  Promise.resolve().then(()=>{
    cleanupDuplicateRealtimeV192();
    polishV192();
  });

  window.__fjzRuntimeHealthV192=function(){
    let channels=[];
    try{
      channels=(supabaseClient?.getChannels?.()||[]).map(x=>x.topic||x.state||'channel');
    }catch(_e){}
    return {
      version:VERSION,
      release:window.__FJZ_RELEASE__||null,
      channels,
      channelCount:channels.length,
      syncPending:!!localStorage.getItem('fjz_v112_pending_sync'),
      mode:window.mode||null,
      studentTab:window.studentTab||null,
      coachTab:window.coachTab||null,
      coachStudentTab:window.coachStudentTab||null,
      workoutStable:document.body?.classList.contains('v146-workout-stable')||false
    };
  };

  window.__fjzV192={
    version:VERSION,
    singleRealtimeAuthority:true,
    legacyAlertRealtimeRemoved:true,
    legacyFollowupRealtimeRemoved:true,
    noLayoutMeasurementScanner:true,
    recentGeometryWrappersConsolidated:true,
    runtimeHealthProbe:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

# ---------------------------------------------------------
# Final CSS consolidation after all recent releases. Preserve order.
# ---------------------------------------------------------
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
mergeable=[]
for m in styles:
    attrs=m.group("attrs") or ""
    if re.search(r"\b(media|nonce)\s*=",attrs,re.I):continue
    mergeable.append(m)

if len(mergeable)>1:
    chunks=[]
    for m in mergeable:
        ident=re.search(r'id=["\']([^"\']+)["\']',m.group("attrs") or "",re.I)
        name=ident.group(1) if ident else "anonymous"
        chunks.append("\n/* --- "+name+" --- */\n"+m.group("body").strip())
    for m in reversed(mergeable):
        html=html[:m.start()]+html[m.end():]
    html=html.replace("</head>",'<style id="fjzProductionStylesV192">'+''.join(chunks)+'\n</style>\n</head>',1)

after=metrics(html)

# ---------------------------------------------------------
# Safety assertions: functionality stays, expensive/duplicate paths go.
# ---------------------------------------------------------
critical=[
  "window.finishWorkout",
  "__fjzConfirmSessionSavedV190",
  "__fjzPersistWorkoutDraftV145",
  "window.submitWeeklyCheckin",
  "window.renderNutritionStudentLoaded",
  "window.renderTrackingCoachLoaded",
  "window.saveMeasurementV176",
  "deleteSessionV148",
  "deleteDayV152",
  "fjz-v132-unified",
  "__fjzShouldRenderRealtimeV146",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V19.2 critical functionality missing: "+repr(missing))

for ident in [
  "v186ExactFieldAlignmentRuntime","v187PairedTrackingGridRuntime",
  "v188ScrollInteractionFixRuntime","v191ActionGeometryAuditRuntime"
]:
    if f'id="{ident}"' in html:
        raise RuntimeError("V19.2 obsolete recent runtime still present: "+ident)

if after["styles"]!=1:
    raise RuntimeError("V19.2 expected one final stylesheet: "+str(after["styles"]))
if after["performance_observers"]!=0:
    raise RuntimeError("V19.2 production PerformanceObserver should be zero")
if after["mutation_observers"]>3:
    raise RuntimeError("V19.2 too many MutationObservers: "+str(after["mutation_observers"]))
if after["render_assignments"]>23:
    raise RuntimeError("V19.2 render wrapper regression: "+str(after["render_assignments"]))
if after["timeouts"]>46:
    raise RuntimeError("V19.2 timeout regression: "+str(after["timeouts"]))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V19.2 GENERAL AUDIT BEFORE:",before)
print("TEAM FJZ V19.2 GENERAL AUDIT AFTER:",after)
print("TEAM FJZ V19.2 removed recent runtimes/styles:",removed)
print("TEAM FJZ V19.2 realtime consolidation:",{"v96":n_v96,"v122":n_v122,"map_replacements":counts})
print("TEAM FJZ V19.2 general stability audit enabled")
