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
    if not m: raise RuntimeError("V21.10 missing script "+sid)
    body=fn(m.group(2))
    return doc[:m.start(2)]+body+doc[m.end(2):]

before=metrics(html)

# -------------------------------------------------------------------
# 1) BODY MEASUREMENTS: fix the real legacy V93 compare authority.
#    Keep exactly one general Brazo and one general Muslo/Pierna row.
# -------------------------------------------------------------------
def patch_v94(body):
    pat=re.compile(
        r"  function cleanMeasureCompareV94\(\)\{.*?\n  \}\n\n  function normalizeMeasureFormV94\(\)\{",
        re.S
    )
    m=pat.search(body)
    if not m:
        raise RuntimeError("V21.10 V94 cleanMeasureCompareV94 anchor missing")

    new=r"""  function measureLabelV310(value){
    return String(value||'')
      .normalize('NFD').replace(/[\u0300-\u036f]/g,'')
      .toLowerCase().replace(/[._/-]+/g,' ').replace(/\s+/g,' ').trim();
  }

  function cleanMeasureCompareV94(){
    const nodes=[...document.querySelectorAll('.v93-compare,#v93MeasureCompare')];
    nodes.slice(1).forEach(n=>n.remove());
    const card=nodes[0];
    if(!card)return;

    let armKept=false,thighKept=false;
    card.querySelectorAll('.v93-measure-row').forEach(function(row){
      const strong=row.querySelector('strong');
      const raw=strong?.textContent||row.textContent||'';
      const label=measureLabelV310(raw);
      const arm=/^(brazo|arm)\b/.test(label);
      const thigh=/^(muslo|pierna|thigh)\b/.test(label);
      const right=/\b(der|derecho|derecha|d|right)\b/.test(label);
      const left=/\b(izq|izquierdo|izquierda|i|left)\b/.test(label);

      if(label==='abdomen'){row.remove();return}

      if(arm){
        if(right||armKept){row.remove();return}
        armKept=true;
        if(strong)strong.textContent='Brazo';
        return;
      }

      if(thigh){
        if(right||thighKept){row.remove();return}
        thighKept=true;
        if(strong)strong.textContent='Muslo';
        return;
      }
    });
  }

  function normalizeMeasureFormV94(){"""
    return body[:m.start()]+new+body[m.end():]

html=edit_script(html,"v94NutritionTrackingRuntime",patch_v94)

# Harden V21.09's fallback cleanup too: include the actual V93 row class and
# treat "Pierna" as the same general thigh measurement.
def patch_v309(body):
    old="'.v94-chart,.v205-chart,.v93-measure-item,.v93-measure-card,.metric,label,.form-field,.field,.measure-field'"
    new="'.v94-chart,.v205-chart,.v93-measure-row,.v93-measure-item,.v93-measure-card,.metric,label,.form-field,.field,.measure-field'"
    if body.count(old)!=1:
        raise RuntimeError("V21.10 V309 selector anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old2="if(/^(brazo|muslo)\\s+(derecho|der\\.?)"
    new2="if(/^(brazo|muslo|pierna)\\s+(derecho|derecha|der\\.?)"
    if body.count(old2)!=1:
        raise RuntimeError("V21.10 V309 right-label anchor mismatch: "+str(body.count(old2)))
    body=body.replace(old2,new2,1)

    old3="if(/muslo\\s+(izquierdo|izq\\.?)"
    new3="if(/(muslo|pierna)\\s+(izquierdo|izquierda|izq\\.?)"
    if body.count(old3)!=1:
        raise RuntimeError("V21.10 V309 left-label anchor mismatch: "+str(body.count(old3)))
    body=body.replace(old3,new3,1)
    return body

html=edit_script(html,"v309GeneralBodyMeasurementsRuntime",patch_v309)

# -------------------------------------------------------------------
# 2) SHARED STUDENT AGENDA: resolve the athlete by auth user directly,
#    scope reads to that athlete, and surface future reminders in Home/Agenda.
# -------------------------------------------------------------------
css=r"""
/* TEAM FJZ · V21.10 SHARED STUDENT AGENDA */
.v310-student-agenda{
  margin:0 0 14px!important;
  border-color:rgba(255,69,86,.24)!important;
  background:
    radial-gradient(circle at 92% 0,rgba(255,48,67,.08),transparent 34%),
    #101116!important;
}
.v310-student-agenda .v310-head{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:12px;
  margin-bottom:10px;
}
.v310-student-agenda .v310-head h3{margin:0}
.v310-student-agenda .v310-head p{margin:4px 0 0}
.v310-agenda-list{display:grid;gap:8px}
.v310-agenda-item{
  display:grid;
  grid-template-columns:auto minmax(0,1fr);
  gap:10px;
  align-items:start;
  padding:11px;
  border:1px solid #2d3038;
  border-radius:12px;
  background:#0d0e12;
}
.v310-agenda-date{
  min-width:58px;
  padding:7px 8px;
  border:1px solid rgba(255,73,90,.2);
  border-radius:10px;
  background:rgba(255,48,67,.055);
  color:#ff6978;
  font-size:9px;
  line-height:1.25;
  font-weight:900;
  text-align:center;
  text-transform:uppercase;
}
.v310-agenda-copy{min-width:0}
.v310-agenda-copy strong{display:block;color:#f5f6f8;font-size:12px}
.v310-agenda-copy span{display:block;margin-top:4px;color:#9da2ac;font-size:9px;line-height:1.45}
.v310-agenda-copy small{display:block;margin-top:5px;color:#747b86;font-size:8px}
@media(max-width:520px){
  .v310-student-agenda .v310-head{display:grid}
  .v310-student-agenda .v310-head .btn{width:100%}
  .v310-agenda-item{grid-template-columns:52px minmax(0,1fr)}
}
"""
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V21.10 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

runtime=r"""
<script id="v310SharedStudentAgendaRuntime">
(function(){
  const VERSION='21.10';
  const DAY=86400000;
  let cache={athlete:null,athleteId:null,schedule:[],reminders:[],loadedAt:0,inflight:null};

  function startDayV310(v){
    const d=v instanceof Date?new Date(v):new Date(String(v||'')+'T00:00:00');
    if(Number.isNaN(d.getTime()))return null;
    d.setHours(0,0,0,0);
    return d;
  }
  function isoV310(d){
    return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
  }
  function localWeekdayV310(d){return (d.getDay()+6)%7}
  function dateLabelV310(d){
    return new Intl.DateTimeFormat('es-AR',{day:'2-digit',month:'short'}).format(d).replace('.','');
  }

  function knownStudentAthleteV310(){
    try{
      const a=typeof currentAthleteRowV73==='function'?currentAthleteRowV73():null;
      if(a?.id)return a;
    }catch(_e){}
    try{
      const vals=[...((cloudAthletes&&cloudAthletes.values)?cloudAthletes.values():[])];
      const a=vals.find(x=>String(x?.user_id||'')===String(currentUser?.id||''));
      if(a?.id)return a;
    }catch(_e){}
    return null;
  }

  async function resolveStudentAthleteV310(force=false){
    if(currentProfile?.role!=='student'||!currentUser?.id)return null;
    const known=knownStudentAthleteV310();
    if(known?.id&&!force){
      cache.athlete=known;cache.athleteId=known.id;
      return known;
    }
    if(!cloudEnabled||!supabaseClient)return known;

    const {data,error}=await supabaseClient.from('athletes')
      .select('id,client_id,user_id,coach_id,name,goal')
      .eq('user_id',currentUser.id)
      .maybeSingle();
    if(error)throw error;
    if(!data?.id)return known;

    cache.athlete=data;cache.athleteId=data.id;
    try{if(data.client_id&&cloudAthletes?.set)cloudAthletes.set(data.client_id,data)}catch(_e){}
    try{if(typeof linkedAthleteId!=='undefined')linkedAthleteId=data.id}catch(_e){}
    return data;
  }

  function syncLegacyV310(athleteId,schedule,reminders){
    try{
      agendaScheduleV81=[
        ...(Array.isArray(agendaScheduleV81)?agendaScheduleV81:[]).filter(x=>String(x?.athlete_id)!==String(athleteId)),
        ...schedule
      ];
      agendaRemindersV81=[
        ...(Array.isArray(agendaRemindersV81)?agendaRemindersV81:[]).filter(x=>String(x?.athlete_id)!==String(athleteId)),
        ...reminders
      ];
      agendaLoadedV81=true;
    }catch(_e){}
  }

  async function loadStudentAgendaV310(force=false){
    const athlete=await resolveStudentAthleteV310(force);
    if(!athlete?.id)return {athlete:null,schedule:[],reminders:[]};
    if(!cloudEnabled||!supabaseClient){
      const schedule=typeof scheduleForV81==='function'?scheduleForV81(athlete.id):[];
      const reminders=typeof remindersForV81==='function'?remindersForV81(athlete.id):[];
      return {athlete,schedule,reminders};
    }
    if(!force&&cache.athleteId===athlete.id&&cache.loadedAt&&Date.now()-cache.loadedAt<20000){
      return {athlete,schedule:cache.schedule,reminders:cache.reminders};
    }
    if(cache.inflight)return cache.inflight;

    cache.inflight=(async()=>{
      const [sRes,rRes]=await Promise.all([
        supabaseClient.from('athlete_schedule')
          .select('*').eq('athlete_id',athlete.id).eq('active',true).order('weekday',{ascending:true}),
        supabaseClient.from('athlete_reminders')
          .select('*').eq('athlete_id',athlete.id).eq('active',true).order('reminder_date',{ascending:true}).order('created_at',{ascending:false})
      ]);
      if(sRes.error)throw sRes.error;
      if(rRes.error)throw rRes.error;
      cache.athlete=athlete;cache.athleteId=athlete.id;
      cache.schedule=sRes.data||[];cache.reminders=rRes.data||[];cache.loadedAt=Date.now();
      syncLegacyV310(athlete.id,cache.schedule,cache.reminders);
      return {athlete,schedule:cache.schedule,reminders:cache.reminders};
    })().finally(()=>{cache.inflight=null});
    return cache.inflight;
  }

  function nextOccurrenceV310(r,from){
    if(r?.schedule_type==='once'){
      const d=startDayV310(r?.reminder_date);
      return d&&d>=from?d:null;
    }
    const wd=Number(r?.weekday);
    if(!Number.isInteger(wd)||wd<0||wd>6)return null;
    const d=new Date(from),delta=(wd-localWeekdayV310(from)+7)%7;
    d.setDate(d.getDate()+delta);return d;
  }

  function upcomingV310(data,days=30){
    const today=startDayV310(new Date()),limit=new Date(today);limit.setDate(limit.getDate()+days);
    const out=[];
    (data?.reminders||[]).forEach(r=>{
      const d=nextOccurrenceV310(r,today);
      if(!d||d>limit)return;
      out.push({
        kind:'reminder',date:d,time:r?.remind_time||null,
        title:r?.title||'Recordatorio',body:r?.body||'Recordatorio de tu coach',id:r?.id||''
      });
    });
    (data?.schedule||[]).forEach(s=>{
      const wd=Number(s?.weekday);if(!Number.isInteger(wd)||wd<0||wd>6)return;
      const d=new Date(today),delta=(wd-localWeekdayV310(today)+7)%7;d.setDate(d.getDate()+delta);
      out.push({
        kind:'training',date:d,time:s?.start_time||null,
        title:s?.workout_day_name||'Entrenamiento',body:'Entrenamiento programado por tu coach',id:s?.id||''
      });
    });
    const seen=new Set();
    return out.sort((a,b)=>a.date-b.date||String(a.time||'').localeCompare(String(b.time||''))).filter(x=>{
      const k=[x.kind,x.id,isoV310(x.date)].join(':');
      if(seen.has(k))return false;seen.add(k);return true;
    });
  }

  function agendaCardV310(items,home=false){
    if(!items.length)return '';
    const rows=items.slice(0,home?3:6).map(x=>
      '<div class="v310-agenda-item">'+
        '<div class="v310-agenda-date">'+esc(dateLabelV310(x.date))+'</div>'+
        '<div class="v310-agenda-copy"><strong>'+esc(x.title)+'</strong>'+
          '<span>'+esc(x.body||'')+'</span>'+
          '<small>'+esc((x.time?String(x.time).slice(0,5)+' · ':'')+(x.kind==='training'?'Entrenamiento':'Recordatorio'))+'</small>'+
        '</div>'+
      '</div>'
    ).join('');
    return '<section class="card v310-student-agenda" id="'+(home?'v310StudentAgendaHome':'v310StudentAgendaUpcoming')+'">'+
      '<div class="v310-head"><div><h3>'+(home?'Próximamente':'Próximos recordatorios')+'</h3>'+
      '<p class="muted tiny">'+(home?'Fechas y avisos cargados por tu coach.':'También muestra recordatorios de semanas siguientes.')+'</p></div>'+
      (home?'<button class="btn small" onclick="studentTab=\'agenda\';render()">Ver agenda</button>':'')+
      '</div><div class="v310-agenda-list">'+rows+'</div></section>';
  }

  async function injectStudentAgendaHomeV310(){
    if(!(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'))return;
    const data=await loadStudentAgendaV310(false);
    if(!(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'))return;
    const view=el('view');if(!view)return;
    el('v310StudentAgendaHome')?.remove();
    const items=upcomingV310(data,30);
    if(!items.length)return;
    const tmp=document.createElement('div');tmp.innerHTML=agendaCardV310(items,true);
    const card=tmp.firstElementChild;if(!card)return;
    const hero=view.querySelector('.hero');
    if(hero)hero.insertAdjacentElement('afterend',card);else view.prepend(card);
  }

  function injectStudentAgendaUpcomingV310(data){
    if(!(currentProfile?.role==='student'&&mode==='student'&&studentTab==='agenda'))return;
    const host=el('studentSubBody');if(!host)return;
    el('v310StudentAgendaUpcoming')?.remove();
    const items=upcomingV310(data,30).filter(x=>x.kind==='reminder');
    if(!items.length)return;
    const tmp=document.createElement('div');tmp.innerHTML=agendaCardV310(items,false);
    const card=tmp.firstElementChild;if(!card)return;
    const notify=el('v82NotifyCard');
    if(notify?.parentNode)notify.insertAdjacentElement('afterend',card);
    else host.prepend(card);
  }

  const baseStudentAgendaV310=window.renderStudentAgendaV81||renderStudentAgendaV81;
  window.renderStudentAgendaV81=async function(){
    let data=null;
    try{data=await loadStudentAgendaV310(true)}catch(e){console.warn('TEAM FJZ V21.10 student agenda load',e)}
    const out=await baseStudentAgendaV310.apply(this,arguments);
    try{
      if(!data)data=await loadStudentAgendaV310(false);
      injectStudentAgendaUpcomingV310(data);
    }catch(e){console.warn('TEAM FJZ V21.10 student agenda upcoming',e)}
    return out;
  };
  try{renderStudentAgendaV81=window.renderStudentAgendaV81}catch(_e){}

  const basePostV310=window.__fjzPostRenderV176;
  window.__fjzPostRenderV176=function(){
    const out=basePostV310?.apply(this,arguments);
    if(currentProfile?.role==='student'&&mode==='student'&&studentTab==='home'){
      Promise.resolve().then(()=>injectStudentAgendaHomeV310()).catch(e=>console.warn('TEAM FJZ V21.10 student home agenda',e));
    }
    return out;
  };

  window.__fjzV310={
    version:VERSION,
    generalArmSingleRow:true,
    generalThighSingleRow:true,
    studentAgendaDirectAuthLookup:true,
    studentAgendaScopedReads:true,
    upcomingReminderOnHome:true,
    futureReminderList:true,
    sharedCoachStudentAgenda:true,
    noSchemaChange:true,
    noExtraTimers:true,
    noExtraListeners:true,
    noExtraObservers:true
  };
})();
</script>
"""

html=html.replace("</body>",runtime+"\n</body>",1)
html=html.replace("</head>",'<meta name="fjz-shared-agenda-measure-fix" content="21.10">\n</head>',1)

after=metrics(html)
for k in before:
    if after[k]!=before[k]:
        raise RuntimeError("V21.10 topology changed "+k+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-shared-agenda-measure-fix" content="21.10"',
    'id="v310SharedStudentAgendaRuntime"',
    "generalArmSingleRow:true",
    "generalThighSingleRow:true",
    "studentAgendaDirectAuthLookup:true",
    "studentAgendaScopedReads:true",
    "upcomingReminderOnHome:true",
    "futureReminderList:true",
    "sharedCoachStudentAgenda:true",
    ".v93-measure-row",
    "armKept=false,thighKept=false",
    ".eq('user_id',currentUser.id)",
    ".eq('athlete_id',athlete.id)",
    "Próximos recordatorios",
]:
    if marker not in html:
        raise RuntimeError("V21.10 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.10 shared agenda + general measurements fix")
print("V21.10 BEFORE:",before)
print("V21.10 AFTER:",after)
