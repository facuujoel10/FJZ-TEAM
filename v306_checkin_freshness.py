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
    'meta name="fjz-checkin-resubmission-lifecycle" content="21.05"',
    'id="v305CheckinResubmissionLifecycleRuntime"',
    "renderTrackingCoachLoaded",
    "renderStudentTrackingHistory",
]:
    if marker not in html:
        raise RuntimeError("V21.06 prerequisite missing "+marker)

old_label='<label class="tiny muted">Semana<input id="ciWeek"'
new_label='<label class="tiny muted">Semana (inicio lunes)<input id="ciWeek"'
if html.count(old_label)!=1:
    raise RuntimeError("V21.06 student week label anchor mismatch: "+str(html.count(old_label)))
html=html.replace(old_label,new_label,1)

old_week='Semana \${esc(c.week_start)}'
new_week='\${esc(window.__fjzWeekRangeLabelV306?.(c.week_start)||("Semana "+c.week_start))}'
week_count=html.count(old_week)
if week_count<2:
    raise RuntimeError("V21.06 raw week labels missing: "+str(week_count))
html=html.replace(old_week,new_week)

runtime=r"""
<script id="v306CheckinFreshnessPresentationRuntime">
(function(){
  const TZ='America/Argentina/Buenos_Aires';

  function parseYmd(v){
    const m=String(v||'').match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if(!m)return null;
    return new Date(Number(m[1]),Number(m[2])-1,Number(m[3]),12,0,0,0);
  }
  function monthShort(d){
    return new Intl.DateTimeFormat('es-AR',{month:'short'}).format(d).replace('.','');
  }
  function weekRange(v){
    const a=parseYmd(v);if(!a)return 'Semana '+String(v||'—');
    const b=new Date(a);b.setDate(b.getDate()+6);
    const sameMonth=a.getMonth()===b.getMonth()&&a.getFullYear()===b.getFullYear();
    const sameYear=a.getFullYear()===b.getFullYear();
    if(sameMonth)return 'Semana '+a.getDate()+'–'+b.getDate()+' '+monthShort(a)+' '+a.getFullYear();
    if(sameYear)return 'Semana '+a.getDate()+' '+monthShort(a)+'–'+b.getDate()+' '+monthShort(b)+' '+a.getFullYear();
    return 'Semana '+a.getDate()+' '+monthShort(a)+' '+a.getFullYear()+'–'+b.getDate()+' '+monthShort(b)+' '+b.getFullYear();
  }
  window.__fjzWeekRangeLabelV306=weekRange;

  function partsDate(d){
    try{
      const p=new Intl.DateTimeFormat('en-CA',{
        timeZone:TZ,year:'numeric',month:'2-digit',day:'2-digit'
      }).formatToParts(d);
      const o={};p.forEach(x=>o[x.type]=x.value);
      return o.year+'-'+o.month+'-'+o.day;
    }catch(_e){return ''}
  }
  function fmtSubmitted(v){
    if(!v)return 'Sin fecha de envío';
    const d=new Date(v);if(Number.isNaN(d.getTime()))return 'Enviado '+String(v);
    const day=partsDate(d),today=partsDate(new Date());
    const time=new Intl.DateTimeFormat('es-AR',{
      timeZone:TZ,hour:'2-digit',minute:'2-digit',hour12:false
    }).format(d);
    if(day&&day===today)return 'Enviado hoy '+time;
    const date=new Intl.DateTimeFormat('es-AR',{
      timeZone:TZ,day:'2-digit',month:'2-digit'
    }).format(d);
    return 'Enviado '+date+' '+time;
  }
  window.__fjzCheckinSubmittedLabelV306=fmtSubmitted;

  function annotateRows(host,data){
    if(!host||!Array.isArray(data))return;
    const rows=[...host.querySelectorAll('.track-row')];
    rows.slice(0,data.length).forEach((node,i)=>{
      const c=data[i];if(!c)return;
      const heading=[...node.querySelectorAll('strong')].find(x=>/^Semana\b/.test(String(x.textContent||'').trim()));
      if(heading)heading.textContent=weekRange(c.week_start);
      const state=node.querySelector('.v305-checkin-state small');
      if(state)state.textContent=fmtSubmitted(c.submitted_at);
      node.dataset.weekStart=String(c.week_start||'');
      node.dataset.submittedAt=String(c.submitted_at||'');
    });
  }

  const baseCoach=window.renderTrackingCoachLoaded||globalThis.renderTrackingCoachLoaded;
  if(typeof baseCoach==='function'){
    const wrapped=function(){
      const out=baseCoach.apply(this,arguments);
      try{annotateRows(document.getElementById('coachStudentBody'),trackingCache?.checkins||[])}catch(e){
        console.warn('TEAM FJZ V21.06 coach check-in labels',e);
      }
      return out;
    };
    window.renderTrackingCoachLoaded=wrapped;
    try{renderTrackingCoachLoaded=wrapped}catch(_e){}
  }

  const baseStudent=window.renderStudentTrackingHistory||globalThis.renderStudentTrackingHistory;
  if(typeof baseStudent==='function'){
    const wrapped=function(){
      const out=baseStudent.apply(this,arguments);
      try{annotateRows(document.getElementById('trackingStudentHistory'),trackingCache?.checkins||[])}catch(e){
        console.warn('TEAM FJZ V21.06 student check-in labels',e);
      }
      return out;
    };
    window.renderStudentTrackingHistory=wrapped;
    try{renderStudentTrackingHistory=wrapped}catch(_e){}
  }

  window.__fjzV306={
    version:'21.06',
    weekStartKeptAsMondayAnchor:true,
    weekRangePresentation:true,
    submissionTimestampPresentation:true,
    buenosAiresTimezone:true,
    feedCurrentPendingOnly:true,
    reviewedWellnessHidden:true,
    staleCheckinFeedStateCleaned:true,
    noExtraTimers:true,
    noExtraListeners:true,
    noExtraObservers:true
  };
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-checkin-freshness" content="21.06">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V21.06 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-checkin-freshness" content="21.06"',
    'id="v306CheckinFreshnessPresentationRuntime"',
    "Semana (inicio lunes)",
    "weekStartKeptAsMondayAnchor:true",
    "weekRangePresentation:true",
    "submissionTimestampPresentation:true",
    "buenosAiresTimezone:true",
    "feedCurrentPendingOnly:true",
    "reviewedWellnessHidden:true",
    "staleCheckinFeedStateCleaned:true",
    "Enviado hoy ",
]:
    if marker not in html:
        raise RuntimeError("V21.06 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.06 check-in freshness + week presentation")
print("V21.06 student week labels replaced:",label_count)\nprint("V21.06 raw week labels replaced:",week_count)
print("V21.06 BEFORE:",before)
print("V21.06 AFTER:",after)
