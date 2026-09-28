import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# 1) Active workout protection must depend on the actual app mode, not account role.
old_guard="if(currentProfile?.role==='student'&&studentTab==='workout')return true;"
new_guard="if(mode==='student'&&studentTab==='workout')return true;"
count_guard=html.count(old_guard)
html=html.replace(old_guard,new_guard)

old_flush="if(!(currentProfile?.role==='student'&&studentTab==='workout'))"
new_flush="if(!(mode==='student'&&studentTab==='workout'))"
count_flush=html.count(old_flush)
html=html.replace(old_flush,new_flush)

# 2) Coach accounts using Student mode should get the same workout autosave UI/protection.
repls=[
 ("if(currentProfile?.role!=='student'||studentTab!=='home')return;","if(mode!=='student'||studentTab!=='home')return;"),
 ("if(currentProfile?.role!=='student'||studentTab!=='workout')return;","if(mode!=='student'||studentTab!=='workout')return;")
]
autosave_repls=0
for a,b in repls:
    n=html.count(a); autosave_repls+=n; html=html.replace(a,b)

# 3) V13.2 already invalidates caches before rendering. Stop there when current
#    screen does not need a redraw.
needle="""    tables.forEach(invalidateV132);

    const core=tables.some(t=>['athlete_snapshots','athletes'].includes(t));"""
replacement="""    tables.forEach(invalidateV132);

    if(window.__fjzShouldRenderRealtimeV146?.(tables)===false){
      window.__fjzDeferredRealtimeV146={
        tables:[...tables],
        at:new Date().toISOString()
      };
      return;
    }

    const core=tables.some(t=>['athlete_snapshots','athletes'].includes(t));"""
if needle not in html:
    raise RuntimeError("V14.6 could not locate realtime flush")
html=html.replace(needle,replacement,1)

css=r"""
<style id="v146RenderStabilityStyles">
/* Active workout DOM should not animate/reflow from background state changes. */
body.v146-workout-stable #view,
body.v146-workout-stable .session-card,
body.v146-workout-stable .set-grid{
  transition:none!important;
  animation:none!important;
}
body.v146-workout-stable #view{overflow-anchor:none}
</style>
"""

js=r"""
<script id="v146RenderStabilityRuntime">
(function(){
  const VERSION='14.6';
  const LEGACY_CHANNEL_KEYS=[
    '__fjzV63NutritionChannel',
    '__fjzV66HabitChannel',
    '__fjzV69MediaChannel',
    '__fjzV73FeedbackChannel',
    '__fjzV80Channel',
    '__fjzV81AgendaChannel'
  ];

  function activeWorkoutV146(){
    return mode==='student'&&studentTab==='workout';
  }

  function activeInputV146(){
    const a=document.activeElement;
    return !!(a&&a.matches?.('input,select,textarea,[contenteditable="true"]'));
  }

  function tableMatchesViewV146(table){
    if(activeWorkoutV146())return false;
    if(activeInputV146())return false;

    if(mode==='student'){
      const map={
        home:new Set(['athlete_schedule','athlete_reminders','student_notices','workout_sessions','workout_sets','progression_recommendations']),
        tracking:new Set(['weekly_checkins','body_measurements','progress_photos']),
        nutrition:new Set(['nutrition_logs','nutrition_plans','nutrition_habit_logs','nutrition_plan_revisions','nutrition_templates']),
        agenda:new Set(['athlete_schedule','athlete_reminders']),
        music:new Set(['coach_media_settings']),
        progress:new Set(['workout_sessions','workout_sets','progression_recommendations']),
        history:new Set(['workout_sessions','workout_sets'])
      };
      return map[studentTab]?.has(table)??false;
    }

    if(mode==='coach'){
      if(coachTab==='music')return table==='coach_media_settings';
      if(coachTab==='agenda')return ['athlete_schedule','athlete_reminders'].includes(table);
      if(coachTab==='dashboard'){
        return ['exercise_feedback','checkin_schedules','coach_payments','weekly_checkins','body_measurements','student_notices','workout_sessions','workout_sets','progression_recommendations'].includes(table);
      }
      if(coachTab==='student'){
        const map={
          summary:new Set(['weekly_checkins','body_measurements','nutrition_plans','exercise_feedback','workout_sessions','workout_sets','progression_recommendations','progress_photos']),
          routine:new Set(['exercise_feedback','exercise_media']),
          tracking:new Set(['weekly_checkins','body_measurements','progress_photos']),
          nutrition:new Set(['nutrition_logs','nutrition_plans','nutrition_habit_logs','nutrition_plan_revisions','nutrition_templates']),
          agenda:new Set(['athlete_schedule','athlete_reminders']),
          progress:new Set(['workout_sessions','workout_sets','progression_recommendations']),
          history:new Set(['workout_sessions','workout_sets'])
        };
        return map[coachStudentTab]?.has(table)??false;
      }
    }

    return false;
  }

  window.__fjzShouldRenderRealtimeV146=function(tables){
    if(activeWorkoutV146())return false;
    if(window.__fjzShouldDeferRefreshV137?.())return false;
    return (tables||[]).some(tableMatchesViewV146);
  };

  function cleanupLegacyRealtimeV146(){
    if(!supabaseClient)return 0;
    let removed=0;
    LEGACY_CHANNEL_KEYS.forEach(key=>{
      const ch=window[key];
      if(!ch)return;
      try{
        supabaseClient.removeChannel(ch);
        window[key]=null;
        removed++;
      }catch(e){}
    });
    window.__fjzRenderStabilityV146.legacyChannelsRemoved=
      Math.max(window.__fjzRenderStabilityV146.legacyChannelsRemoved||0,removed);
    return removed;
  }

  const baseSetupRealtimeV146=setupRealtime;
  setupRealtime=function(){
    const out=baseSetupRealtimeV146.apply(this,arguments);
    Promise.resolve().then(cleanupLegacyRealtimeV146);
    return out;
  };

  function syncWorkoutBodyClassV146(){
    document.body?.classList.toggle('v146-workout-stable',activeWorkoutV146());
  }

  const baseRenderV146=render;
  render=function(){
    const before=performance.now();
    const out=baseRenderV146.apply(this,arguments);
    syncWorkoutBodyClassV146();
    const now=performance.now();
    const q=window.__fjzRenderStabilityV146;
    q.renderCount++;
    q.lastRenderMs=Math.round((now-before)*10)/10;
    q.lastRenderAt=new Date().toISOString();
    return out;
  };

  // Initial cleanup in case Realtime was already initialized before this script loaded.
  Promise.resolve().then(()=>{
    cleanupLegacyRealtimeV146();
    syncWorkoutBodyClassV146();
  });

  window.__fjzRenderStabilityV146={
    version:VERSION,
    activeWorkoutFreeze:true,
    viewScopedRealtime:true,
    legacyChannelsRemoved:0,
    renderCount:0,
    lastRenderMs:0,
    lastRenderAt:null
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzShouldRenderRealtimeV146",
  "activeWorkoutFreeze:true",
  "viewScopedRealtime:true",
  "v146-workout-stable"
]:
    if marker not in html:
        raise RuntimeError("V14.6 missing marker: "+marker)

if count_guard<1:
    raise RuntimeError("V14.6 did not update active workout refresh guard")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V14.6 render stability:",{
  "workout_guard_replacements":count_guard,
  "flush_guard_replacements":count_flush,
  "autosave_mode_replacements":autosave_repls,
  "legacy_channel_keys":6
})
