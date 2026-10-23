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
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

def edit_script(doc,script_id,transform):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m: raise RuntimeError("V20.89 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body: raise RuntimeError("V20.89 no changes in "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-desktop-coach-readability" content="20.88"',
    'id="v122FollowupPaymentsRuntime"',
    'id="v173SafeSummaryPaymentsRuntime"',
    'id="v277SaveGeometryRuntime"',
    'meta name="fjz-payments-deferred" content="20.85"',
    "duplicateAsyncSaveGuard:true",
]:
    if marker not in html:
        raise RuntimeError("V20.89 prerequisite missing "+marker)

# ------------------------------------------------------------------
# 1) V12.2: keep check-in scheduling, retire all payment I/O/runtime work.
# ------------------------------------------------------------------
def patch_v122(body):
    old_load="""async function loadFollowupsV122(force=false){
 if(followupLoadedV122&&!force)return followupCacheV122;
 const [c,p]=await Promise.all([
   supabaseClient.from('checkin_schedules').select('*').order('next_due'),
   supabaseClient.from('coach_payments').select('*').order('due_date',{ascending:false})
 ]);
 if(c.error)throw c.error;if(p.error)throw p.error;
 followupCacheV122={checkins:c.data||[],payments:p.data||[]};followupLoadedV122=true;return followupCacheV122;
}"""
    new_load="""async function loadFollowupsV122(force=false){
 if(followupLoadedV122&&!force)return followupCacheV122;
 const c=await supabaseClient.from('checkin_schedules').select('*').order('next_due');
 if(c.error)throw c.error;
 followupCacheV122={checkins:c.data||[],payments:[]};followupLoadedV122=true;return followupCacheV122;
}"""
    if body.count(old_load)!=1:
        raise RuntimeError("V20.89 V122 followup load anchor mismatch")
    body=body.replace(old_load,new_load,1)

    # Replace all retired payment CRUD/render code with compatibility no-ops.
    start=body.find("window.openNewPaymentV122=function")
    end=body.find("async function upcomingEventsV122",start)
    if start<0 or end<0:
        raise RuntimeError("V20.89 V122 payment block bounds missing")
    stubs="""window.openNewPaymentV122=function(){return null};
window.saveNewPaymentV122=async function(){return null};
window.openMarkPaidV122=function(){return null};
window.markPaidV122=async function(){return null};
window.deletePaymentV122=async function(){return null};
window.renderCoachPaymentsV122=async function(){coachTab='dashboard';return render()};
window.openPaymentPickerV122=function(){return null};

"""
    body=body[:start]+stubs+body[end:]

    old_upcoming=re.search(r"async function upcomingEventsV122\(athleteId=null,days=30\)\{.*?\n\}",body,re.S)
    if not old_upcoming:
        raise RuntimeError("V20.89 V122 upcoming block missing")
    new_upcoming="""async function upcomingEventsV122(athleteId=null,days=30){
 await loadFollowupsV122(true);
 const start=todayISO122(),end=new Date();end.setDate(end.getDate()+days);const endIso=end.toISOString().slice(0,10);
 const cs=followupCacheV122.checkins.filter(x=>x.active&&(athleteId?x.athlete_id===athleteId:true)&&x.next_due>=start&&x.next_due<=endIso);
 return {cs,ps:[]};
}"""
    body=body[:old_upcoming.start()]+new_upcoming+body[old_upcoming.end():]

    # Old routing wrappers stay in the chain for compatibility but do no routing.
    route_start=body.find("const baseCoachRenderV122=window.renderCoach;")
    route_end=body.find("const baseSetupV122=window.setupRealtime;",route_start)
    if route_start<0 or route_end<0:
        raise RuntimeError("V20.89 V122 route wrapper bounds missing")
    route_clean="""const baseCoachRenderV122=window.renderCoach;
window.renderCoach=function(){return baseCoachRenderV122.apply(this,arguments)};
const baseBottomV122=window.renderBottomNav;
window.renderBottomNav=function(){return baseBottomV122.apply(this,arguments)};

"""
    body=body[:route_start]+route_clean+body[route_end:]

    rt_start=body.find("const baseSetupV122=window.setupRealtime;")
    rt_end=body.find("window.__fjzFollowupsV122=",rt_start)
    if rt_start<0 or rt_end<0:
        raise RuntimeError("V20.89 V122 realtime bounds missing")
    rt_clean="""const baseSetupV122=window.setupRealtime;
window.setupRealtime=function(){
 const r=baseSetupV122.apply(this,arguments);if(!supabaseClient)return r;
 try{
  if(window.__fjzV122Channel)supabaseClient.removeChannel(window.__fjzV122Channel);
  window.__fjzV122Channel=supabaseClient.channel('fjz-v122-followups')
   .on('postgres_changes',{event:'*',schema:'public',table:'checkin_schedules'},()=>{followupLoadedV122=false;setTimeout(()=>render(),250)})
   .subscribe();
 }catch(e){console.warn('V12.2 check-in realtime',e)}
 return r;
};

"""
    body=body[:rt_start]+rt_clean+body[rt_end:]

    old_marker="window.__fjzFollowupsV122={version:'12.2',checkins:true,payments:true};"
    new_marker="window.__fjzFollowupsV122={version:'12.2',checkins:true,payments:false,paymentsDeferredV289:true};"
    if body.count(old_marker)!=1:
        raise RuntimeError("V20.89 V122 marker mismatch")
    body=body.replace(old_marker,new_marker,1)
    return body

html=edit_script(html,"v122FollowupPaymentsRuntime",patch_v122)

# ------------------------------------------------------------------
# 2) V17.3: retain the useful legacy-summary cleanup, retire payment enhancer.
# ------------------------------------------------------------------
def patch_v173(body):
    start=body.find("  function enhancePaymentsV173(){")
    end=body.find("  // Existing render chain can call the legacy V6.3 hook",start)
    if start<0 or end<0:
        raise RuntimeError("V20.89 V173 payment enhancer bounds missing")
    body=body[:start]+"  // Payments are deferred; V17.3 now only protects the canonical summary.\n\n"+body[end:]

    old_render="""  const baseRenderV173=window.render;
  window.render=function(){
    const out=baseRenderV173.apply(this,arguments);
    removeLegacySummaryV173();
    if(currentProfile?.role==='coach'&&coachTab==='payments')enhancePaymentsV173();
    return out;
  };"""
    new_render="""  const baseRenderV173=window.render;
  window.render=function(){
    const out=baseRenderV173.apply(this,arguments);
    removeLegacySummaryV173();
    return out;
  };"""
    if body.count(old_render)!=1:
        raise RuntimeError("V20.89 V173 render wrapper mismatch")
    body=body.replace(old_render,new_render,1)
    body=body.replace("paymentsBackNavigation:true,","paymentsDeferredV289:true,",1)
    return body

html=edit_script(html,"v173SafeSummaryPaymentsRuntime",patch_v173)

# ------------------------------------------------------------------
# 3) Put V12.2's active check-in save under the canonical V20.77 lock.
# ------------------------------------------------------------------
def patch_v277(body):
    anchor="""    'submitWeeklyCheckin'
  ];"""
    repl="""    'submitWeeklyCheckin',
    'saveCheckinScheduleV122'
  ];"""
    if body.count(anchor)!=1:
        raise RuntimeError("V20.89 V277 guard list anchor mismatch")
    body=body.replace(anchor,repl,1)
    body=body.replace("    guardedActions:guardedNow","    checkinScheduleV122GuardedV289:true,\n    guardedActions:guardedNow",1)
    return body

html=edit_script(html,"v277SaveGeometryRuntime",patch_v277)

# ------------------------------------------------------------------
# 4) Desktop typography: increase the actual activity/athlete text one more step.
# ------------------------------------------------------------------
css=r"""
/* TEAM FJZ · V20.89 DESKTOP READABILITY SCALE */
@media(min-width:1000px){
  .v225-section-kicker,
  .v225-eyebrow{
    font-size:12px!important;
  }

  .v225-student-list .student-main>div>strong{
    font-size:17px!important;
    line-height:1.25!important;
  }
  .v225-student-list .student-main>div>.muted.tiny{
    font-size:14px!important;
    line-height:1.4!important;
  }
  .v225-student-list .student-row>div:not(.student-main)>strong{
    font-size:15.5px!important;
  }
  .v225-student-list .student-row>div:not(.student-main)>.muted.tiny{
    font-size:12.5px!important;
  }
  .v225-student-list .badge{
    font-size:12px!important;
  }
  .v225-student-list .btn.small{
    font-size:12px!important;
  }

  .v225-card-head h3,
  .v225-students-head h3,
  .v225-attention-card .section-title h3{
    font-size:20px!important;
  }
  .v225-card-head .muted.tiny,
  .v225-students-head .muted.tiny,
  .v225-attention-card .section-title .muted.tiny{
    font-size:13.5px!important;
    line-height:1.5!important;
  }

  .v80-attention-item h4{
    font-size:15.5px!important;
    line-height:1.4!important;
  }
  .v80-attention-item p,
  .v80-attention-item .muted.tiny{
    font-size:13px!important;
    line-height:1.52!important;
  }
  .v80-attention-item .badge{
    font-size:12px!important;
  }
  .v225-filter-row .btn,
  .v80-attention-actions .btn.small{
    font-size:12px!important;
  }

  .v278-dashboard-smart-head strong{
    font-size:14px!important;
  }
  .v278-dashboard-smart-head span{
    font-size:11px!important;
  }
  .v278-dashboard-alert-top strong{
    font-size:14px!important;
    line-height:1.35!important;
  }
  .v278-dashboard-alert-top span{
    font-size:11px!important;
  }
  .v278-dashboard-alert p{
    font-size:12.5px!important;
    line-height:1.5!important;
  }
  .v278-dashboard-alert-stats span{
    font-size:10px!important;
  }
  .v278-dashboard-alert-stats b{
    font-size:12px!important;
  }
  .v278-alert-exercise{
    font-size:12.5px!important;
  }
  .v278-alert-delta span,
  .v278-alert-period,
  .v278-alert-suggestion strong{
    font-size:10.5px!important;
  }
  .v278-alert-delta strong{
    font-size:12px!important;
  }
  .v278-alert-suggestion span{
    font-size:12px!important;
    line-height:1.45!important;
  }
  .v278-mini-alert strong{
    font-size:12px!important;
  }
  .v278-mini-alert small{
    font-size:10.5px!important;
    line-height:1.4!important;
  }

  .v225-flow-step p,
  .v225-signal span,
  .v225-today-card .muted.tiny,
  .v225-flow-card .muted.tiny{
    font-size:13px!important;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.89 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-legacy-runtime-cleanup" content="20.89">\n<meta name="fjz-desktop-readability-scale" content="20.89">\n</head>',1)

after=metrics(html)

# No new runtime topology. Removing a retired payment timeout is allowed.
for key in ("styles","renders","channels","intervals","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.89 unexpected topology change "+key+": "+repr({"before":before,"after":after}))
if after["timeouts"]>before["timeouts"]:
    raise RuntimeError("V20.89 timeout growth")
if "coach_payments" in html:
    raise RuntimeError("V20.89 retired coach_payments reference survived")

required=[
    'meta name="fjz-legacy-runtime-cleanup" content="20.89"',
    'meta name="fjz-desktop-readability-scale" content="20.89"',
    "paymentsDeferredV289:true",
    "checkinScheduleV122GuardedV289:true",
    "payments:false",
    "font-size:17px!important",
    ".v278-dashboard-alert-top strong",
    "font-size:14px!important",
]
for marker in required:
    if marker not in html:
        raise RuntimeError("V20.89 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.89 legacy cleanup + desktop readability")
print("V20.89 BEFORE:",before)
print("V20.89 AFTER:",after)
print("V20.89 payments runtime quarantined; V12.2 check-in save uses canonical duplicate-submit guard")
