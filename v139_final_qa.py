import pathlib,re
from html.parser import HTMLParser
from collections import Counter

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# Remove layout containment that can create surprising fixed/scroll/layout behavior.
html=re.sub(r"#view\s*\{\s*contain\s*:\s*layout\s+style\s*;?\s*\}","#view{contain:none}",html)

# The base realtime channel already listens to these four core tables. V13.2's
# unified safety net should cover the rest, not duplicate the same core events.
old_tables="""        'athlete_snapshots','athletes','weekly_checkins','body_measurements','progress_photos',"""
new_tables="""        'progress_photos',"""
if old_tables in html:
    html=html.replace(old_tables,new_tables,1)

# Align own-write ignore window across realtime layers.
html=html.replace("Date.now()-(Number(cloudLastWrite)||0)>700","Date.now()-(Number(cloudLastWrite)||0)>1500")

css=r"""
<style id="v139FinalQAStyles">
/* TEAM FJZ V13.9 · final layout contract */
*,*::before,*::after{box-sizing:border-box}
html{scrollbar-gutter:stable}
body{overflow-x:hidden}
#view,#coachStudentBody,#studentSubBody,.app-shell,.main,.content{min-width:0;max-width:100%}
.card,.hero,.metric,.option-card,.student-row,.exercise-row,.day-card,.invite-card,
.v114-profile-card,.v115-profile-card,.v122-row,.v132-step,.v136-learn-card,.v138-habit-card{
  min-width:0;max-width:100%;box-sizing:border-box;transform:none!important
}
.card,.hero,.metric,.option-card,.student-row,.exercise-row,.day-card{
  transition:border-color .12s ease,box-shadow .12s ease,background-color .12s ease!important
}
.grid,.grid.two,.metric-grid,.form-grid,.v114-profile-grid,.v115-profile-grid,
.v122-grid,.v132-assistant-top,.v136-learn-grid,.v138-habit-grid,.v138-general-list{
  min-width:0;align-items:stretch
}
.grid>*,.grid.two>*,.metric-grid>*,.form-grid>*,.v114-profile-grid>*,
.v115-profile-grid>*,.v122-grid>*,.v132-assistant-top>*,.v136-learn-grid>*,
.v138-habit-grid>*,.v138-general-list>*{min-width:0}
.input,input,select,textarea,button{max-width:100%}
.input,input,select,textarea{min-width:0}
img,video,svg,canvas{max-width:100%}
.section-title{min-width:0;align-items:flex-start}
.section-title>*{min-width:0}
.section-title h1,.section-title h2,.section-title h3,.section-title p,
.card h1,.card h2,.card h3,.card p,.card strong,.card span{overflow-wrap:anywhere}
.tabs,.v70-recipe-tabs,.v136-nutrition-tabs{
  min-width:0;overflow-x:auto;overflow-y:hidden;-webkit-overflow-scrolling:touch;scrollbar-width:thin
}
.pill-row,.day-actions,.exercise-actions,.nutrition-builder-actions,.modal-actions{flex-wrap:wrap}
.modal,.modal-card,.modal-content{max-width:min(94vw,760px)}
@media(min-width:900px){
  html{overflow-y:scroll}
  #coachStudentBody,#studentSubBody{min-height:620px}
}
@media(max-width:760px){
  .grid.two,.v114-profile-grid,.v115-profile-grid,.v132-assistant-top,
  .v136-learn-grid,.v138-habit-grid,.v138-general-list{grid-template-columns:1fr!important}
}
</style>
"""

js=r"""
<script id="v139FinalQARuntime">
(function(){
  const RELEASE='13.9';

  // ----- Core cloud refresh coalescing -----
  const baseRefreshV139=refreshCloudFromRealtime;
  let refreshInFlightV139=false;
  let refreshQueuedV139=false;
  let refreshTimerV139=null;
  let lastRefreshV139=0;

  refreshCloudFromRealtime=async function(){
    if(window.__fjzShouldDeferRefreshV137?.()){
      window.__fjzDeferredCloudRefreshV137=true;
      return;
    }

    const now=Date.now();
    const minGap=1200;

    if(refreshInFlightV139){
      refreshQueuedV139=true;
      return;
    }

    if(now-lastRefreshV139<minGap){
      refreshQueuedV139=true;
      clearTimeout(refreshTimerV139);
      refreshTimerV139=setTimeout(()=>{
        refreshTimerV139=null;
        refreshCloudFromRealtime();
      },Math.max(80,minGap-(now-lastRefreshV139)));
      return;
    }

    refreshInFlightV139=true;
    try{
      await baseRefreshV139.apply(this,arguments);
      lastRefreshV139=Date.now();
    }finally{
      refreshInFlightV139=false;
      if(refreshQueuedV139){
        refreshQueuedV139=false;
        clearTimeout(refreshTimerV139);
        refreshTimerV139=setTimeout(()=>{
          refreshTimerV139=null;
          refreshCloudFromRealtime();
        },650);
      }
    }
  };

  // ----- Known duplicate cleanup, no MutationObserver -----
  const UNIQUE_IDS_V139=[
    'cloudInviteCard','v114ProfileCard','v115StudentProfileCard','v71CoachHelp',
    'v96CoachAlerts','v122PaymentsBody','v136NutritionTabs','v138NutritionTabs',
    'v94SuppStudent','v94SuppCoach','v66CoachHabits','v66StudentHabits',
    'v136CoachLearnLink','v137MethodCoachBox'
  ];

  function dedupeKnownV139(){
    UNIQUE_IDS_V139.forEach(id=>{
      const nodes=[...document.querySelectorAll('#'+CSS.escape(id))];
      nodes.slice(1).forEach(n=>n.remove());
    });

    // Never let old hidden student habit card coexist visually with the new guide.
    if(window.__fjzV138?.textOnlyStudentHabits){
      document.querySelectorAll('#v66StudentHabits').forEach(n=>{n.style.display='none'});
    }
  }

  function normalizeLayoutV139(){
    document.querySelectorAll('.grid,.grid.two,.metric-grid,.form-grid').forEach(g=>{
      g.style.minWidth='0';
    });
    document.querySelectorAll('.card,.hero,.exercise-row,.student-row,.day-card').forEach(n=>{
      n.style.minWidth='0';
      n.style.maxWidth='100%';
    });
  }

  // One final post-render pass in the existing scheduler.
  const baseRenderV139=render;
  render=function(){
    const out=baseRenderV139.apply(this,arguments);
    fjzPostRenderV125('final-qa-v139',()=>{
      dedupeKnownV139();
      normalizeLayoutV139();
    });
    return out;
  };

  // ----- lightweight diagnostics -----
  window.__fjzFinalQA={
    version:RELEASE,
    duplicateCleanup:true,
    cloudRefreshMinGapMs:1200,
    duplicatedCoreRealtimeSubscriptionsRemoved:true,
    observersAdded:0,
    layoutContract:true,
    getStatus(){
      return {
        version:window.__FJZ_RELEASE__||RELEASE,
        realtime:window.__fjzRealtimeV132?.status||'unknown',
        channels:typeof supabaseClient?.getChannels==='function'?supabaseClient.getChannels().length:null,
        pendingSync:!!localStorage.getItem('fjz_v112_pending_sync'),
        deferredRefresh:!!window.__fjzDeferredCloudRefreshV137
      };
    }
  };

  fjzPostRenderV125('final-qa-v139-init',()=>{
    dedupeKnownV139();
    normalizeLayoutV139();
  });
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

# ----- Build-time audit of the final static document -----
class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
        self.scripts=0
        self.styles=0
    def handle_starttag(self,tag,attrs):
        if tag=='script': self.scripts+=1
        if tag=='style': self.styles+=1
        for k,v in attrs:
            if k=='id' and v: self.ids.append(v)

parser=AuditParser()
parser.feed(html)
id_counts=Counter(parser.ids)
dupes={k:v for k,v in id_counts.items() if v>1}

metrics={
    'bytes':len(html.encode('utf-8')),
    'static_ids':len(parser.ids),
    'static_duplicate_ids':len(dupes),
    'scripts':parser.scripts,
    'styles':parser.styles,
    'mutation_observers':html.count('new MutationObserver'),
    'timeouts':html.count('setTimeout('),
    'render_assignments':html.count('render=function'),
    'channels':html.count('.channel('),
}

critical=['cloudInviteCard','v114ProfileCard','v115StudentProfileCard','v71CoachHelp','v96CoachAlerts']
critical_dupes={k:v for k,v in dupes.items() if k in critical}
if critical_dupes:
    raise RuntimeError("V13.9 critical static duplicate ids: "+repr(critical_dupes))

for marker in [
    "__fjzFinalQA",
    "cloudRefreshMinGapMs:1200",
    "duplicatedCoreRealtimeSubscriptionsRemoved:true",
    "layoutContract:true"
]:
    if marker not in html:
        raise RuntimeError("V13.9 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V13.9 FINAL QA:",metrics)
print("V13.9 static duplicate ids:",dupes)
