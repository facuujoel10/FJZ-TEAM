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

def edit_script(doc,sid,fn):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(sid)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m: raise RuntimeError("V21.13 missing script "+sid)
    body=fn(m.group(2))
    return doc[:m.start(2)]+body+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-review-agenda-authority" content="21.12"',
    'id="v280OperationalRecoveryRuntime"',
    'id="v312ReviewAgendaAuthorityRuntime"',
    "__fjzProfileReviewedAthleteV311",
    "__fjzProfileReviewStateLoadedV311",
    "function reviewEvent(s)",
    "Primer chequeo",
]:
    if marker not in html:
        raise RuntimeError("V21.13 prerequisite missing "+marker)

def patch_v280(body):
    old="""  function cadenceDays(s){try{if(typeof coachReviewCadenceDaysV240==='function'){const n=Number(coachReviewCadenceDaysV240(s));if(Number.isFinite(n)&&n>0)return n}}catch(_e){}return 14}
  function reviewEvent(s){const today=startDay(new Date()),reviewed=s?.coachReviewV237?.reviewedAt||null;let due=today;if(reviewed){const d=new Date(reviewed);if(!Number.isNaN(d.getTime()))due=startDay(addDays(d,cadenceDays(s)))}return {date:key(due),raw:due,student:s,kind:'review',title:reviewed?'Chequeo / revisión':'Primer chequeo',overdue:due<today,tab:'summary'}}
  function studentByAthlete(aid){"""
    new="""  function cadenceDays(s){try{if(typeof coachReviewCadenceDaysV240==='function'){const n=Number(coachReviewCadenceDaysV240(s));if(Number.isFinite(n)&&n>0)return n}}catch(_e){}return 14}
  function cloudProfileReviewedV313(s){
    try{
      const a=athleteFor(s),id=String(a?.id||'');
      return !!id&&!!window.__fjzProfileReviewedAthleteV311?.(id);
    }catch(_e){return false}
  }
  function reviewStateReadyV313(){
    try{return !!window.__fjzProfileReviewStateLoadedV311?.()}catch(_e){return false}
  }
  function reviewEvent(s){
    // Never fabricate "Primer chequeo" before cloud review state is known.
    // This was the source of the 15 recurring profile reviews after reload.
    if(cloudEnabled&&supabaseClient&&!window.__fjzStagingLocal?.enabled&&!reviewStateReadyV313())return null;
    const today=startDay(new Date()),reviewed=s?.coachReviewV237?.reviewedAt||null;
    if(!reviewed&&cloudProfileReviewedV313(s))return null;
    let due=today;
    if(reviewed){
      const d=new Date(reviewed);
      if(!Number.isNaN(d.getTime()))due=startDay(addDays(d,cadenceDays(s)));
    }
    return {date:key(due),raw:due,student:s,kind:'review',title:reviewed?'Chequeo / revisión':'Primer chequeo',overdue:due<today,tab:'summary'};
  }
  function reviewEventsV313(){return students().map(reviewEvent).filter(Boolean)}
  function studentByAthlete(aid){"""
    if body.count(old)!=1:
        raise RuntimeError("V21.13 reviewEvent anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    body=body.replace(
        "const events=(month=monthV280)=>[...students().map(reviewEvent),...remoteEvents(month)];",
        "const events=(month=monthV280)=>[...reviewEventsV313(),...remoteEvents(month)];",
        1
    )
    body=body.replace(
        "all=[...students().map(reviewEvent),...remoteEvents(new Date(today.getFullYear(),today.getMonth(),1)),...remoteEvents(new Date(today.getFullYear(),today.getMonth()+1,1))],upcoming=all.filter(e=>e.kind==='review'?e.raw<=limit:(e.raw>=today&&e.raw<=limit)).sort((a,b)=>(a.overdue===b.overdue?0:a.overdue?-1:1)||a.raw-b.raw).slice(0,8),overdue=students().map(reviewEvent).filter(e=>e.overdue).length,week=students().map(reviewEvent).filter(e=>!e.overdue&&e.raw>=today&&e.raw<=addDays(today,7)).length;",
        "all=[...reviewEventsV313(),...remoteEvents(new Date(today.getFullYear(),today.getMonth(),1)),...remoteEvents(new Date(today.getFullYear(),today.getMonth()+1,1))],upcoming=all.filter(e=>e.kind==='review'?e.raw<=limit:(e.raw>=today&&e.raw<=limit)).sort((a,b)=>(a.overdue===b.overdue?0:a.overdue?-1:1)||a.raw-b.raw).slice(0,8),overdue=reviewEventsV313().filter(e=>e.overdue).length,week=reviewEventsV313().filter(e=>!e.overdue&&e.raw>=today&&e.raw<=addDays(today,7)).length;",
        1
    )
    if "students().map(reviewEvent)" in body:
        raise RuntimeError("V21.13 stale direct reviewEvent map remains")

    old_marker="""  window.__fjzV280={version:'20.80',priorityCalendarRecovery:true,restoredPriorityAuthorityAfterMusicRemoval:true,restoredCalendarAuthorityAfterMusicRemoval:true,staleCalendarCallsRemoved:true,priorityPerStudentIsolation:true,calendarIndependentFromPriority:true,stagingCalendarFallbackSafe:true,explicitDashboardOperationalHydration:true,productionUntouched:true,noExtraTimers:true,noExtraListeners:true,noExtraObservers:true};"""
    new_marker="""  window.__fjzV280={version:'21.13',priorityCalendarRecovery:true,restoredPriorityAuthorityAfterMusicRemoval:true,restoredCalendarAuthorityAfterMusicRemoval:true,staleCalendarCallsRemoved:true,priorityPerStudentIsolation:true,calendarIndependentFromPriority:true,stagingCalendarFallbackSafe:true,explicitDashboardOperationalHydration:true,cloudReviewAwareCalendar:true,noSyntheticFirstCheckBeforeReviewSync:true,closedProfilesExcludedFromCalendar:true,productionUntouched:true,noExtraTimers:true,noExtraListeners:true,noExtraObservers:true};"""
    if body.count(old_marker)!=1:
        raise RuntimeError("V21.13 V280 marker anchor mismatch")
    body=body.replace(old_marker,new_marker,1)
    return body

html=edit_script(html,"v280OperationalRecoveryRuntime",patch_v280)

def patch_v312(body):
    old="""  Promise.resolve(window.__fjzLoadReviewStatesV302?.(false)).finally(()=>{
    try{decorateCoachReviewStateV238?.()}catch(_e){}
    try{renderCoachStudentsV235?.()}catch(_e){}
    try{renderCoachFocusV235?.()}catch(_e){}
    try{renderCoachPriorityCenterV252?.()}catch(_e){}
    try{normalizeLegacyReviewHubV312()}catch(_e){}
  });"""
    new="""  Promise.resolve(window.__fjzLoadReviewStatesV302?.(false)).finally(()=>{
    try{decorateCoachReviewStateV238?.()}catch(_e){}
    try{renderCoachStudentsV235?.()}catch(_e){}
    try{renderCoachFocusV235?.()}catch(_e){}
    try{renderCoachPriorityCenterV252?.()}catch(_e){}
    try{normalizeLegacyReviewHubV312()}catch(_e){}
    // V20.80 used to keep synthetic "Primer chequeo" entries painted after
    // cloud state finished loading. V21.13 forces the operational calendar
    // to recalculate from the now-authoritative review state.
    try{window.refreshCoachOperationalV280?.()}catch(_e){}
  });"""
    if body.count(old)!=1:
        raise RuntimeError("V21.13 V312 review-load refresh anchor mismatch")
    body=body.replace(old,new,1)

    old_marker="""    appointmentScopedByAuthUser:true,
    noSchemaChange:true,"""
    new_marker="""    appointmentScopedByAuthUser:true,
    operationalCalendarRefreshAfterReviewSync:true,
    noSchemaChange:true,"""
    if body.count(old_marker)!=1:
        raise RuntimeError("V21.13 V312 marker anchor mismatch")
    body=body.replace(old_marker,new_marker,1)
    return body

html=edit_script(html,"v312ReviewAgendaAuthorityRuntime",patch_v312)

html=html.replace("</head>",'<meta name="fjz-review-calendar-authority" content="21.13">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V21.13 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-review-calendar-authority" content="21.13"',
    "cloudProfileReviewedV313",
    "reviewStateReadyV313",
    "reviewEventsV313",
    "noSyntheticFirstCheckBeforeReviewSync:true",
    "closedProfilesExcludedFromCalendar:true",
    "refreshCoachOperationalV280",
    "operationalCalendarRefreshAfterReviewSync:true",
]:
    if marker not in html:
        raise RuntimeError("V21.13 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.13 review calendar authority")
print("V21.13 BEFORE:",before)
print("V21.13 AFTER:",after)
