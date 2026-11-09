import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def topology(doc):
    return {
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "intervals":len(re.findall(r"setInterval\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
    }

def edit_script(doc,script_id,fn):
    pattern=re.compile(r"(<script[^>]*id=[\\\"']"+re.escape(script_id)+r"[\\\"'][^>]*>)(.*?)(</script>)",re.S|re.I)
    matches=list(pattern.finditer(doc))
    if len(matches)!=1:
        raise RuntimeError("V22 foundation script authority mismatch "+script_id+": "+str(len(matches)))
    m=matches[0]
    return doc[:m.start(2)]+fn(m.group(2))+doc[m.end(2):]

before=topology(html)
for marker in [
    'meta name="fjz-v22-0c-final-ui-authority"',
    "sessionSuccessRequiresDoubleVerification:true",
    "function dateInputToday(){const d=new Date();",
    'id="v310SharedStudentAgendaRuntime"',
    'id="v312ReviewAgendaAuthorityRuntime"',
]:
    if marker not in html:
        raise RuntimeError("V22 foundation prerequisite missing "+marker)

modules=[
    ("v22CanonicalDateCore","src/core/date.js"),
    ("v22AgendaRepositoryCore","src/data/agenda-repository.js"),
    ("v22AgendaReadPolicyCore","src/data/agenda-read-policy.js"),
]
scripts=[]
for sid,path in modules:
    code=pathlib.Path(path).read_text(encoding="utf-8").strip()
    if "</script" in code.lower():
        raise RuntimeError("V22 source module cannot contain closing script markup: "+path)
    scripts.append('<script id="'+sid+'">\\n'+code+'\\n</script>')

agenda_flag="enabled" if globals().get("APP_ENV") in {"development","test"} else "disabled"
head_payload="\\n".join(scripts)+(
    '\\n<meta name="fjz-v22-1a-architecture-foundation" content="date-pilot">'
    '\\n<meta name="fjz-v22-agenda-repository-read" content="'+agenda_flag+'">'
    '\\n<meta name="fjz-v22-1b-data-sync-foundation" content="agenda-read-pilot">\\n'
)
if html.count("</head>")!=1:
    raise RuntimeError("V22 foundation head anchor mismatch")
html=html.replace("</head>",head_payload+"</head>",1)

old="function dateInputToday(){const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')}"
new="function dateInputToday(){try{return globalThis.TeamFJZDate.calendarDate(new Date(),'America/Argentina/Buenos_Aires')}catch(_e){const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')}}"
if html.count(old)!=1:
    raise RuntimeError("V22 1A dateInputToday authority mismatch: "+str(html.count(old)))
html=html.replace(old,new,1)

def patch_v310(body):
    old="""  function isoV310(d){
    return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
  }"""
    new="""  function isoV310(d){
    try{return globalThis.TeamFJZDate.calendarDate(d,'America/Argentina/Buenos_Aires')}
    catch(_e){return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')}
  }"""
    if body.count(old)!=1:
        raise RuntimeError("V22 1B V310 second date pilot mismatch: "+str(body.count(old)))
    return body.replace(old,new,1)

html=edit_script(html,"v310SharedStudentAgendaRuntime",patch_v310)

def patch_v312(body):
    cache_anchor="  let appointmentCacheV312={userId:null,at:0,data:null,inflight:null};"
    if body.count(cache_anchor)!=1:
        raise RuntimeError("V22 1B V312 cache anchor mismatch")
    body=body.replace(cache_anchor,cache_anchor+"\\n  let agendaRepositoryV22=null;",1)

    old="""      const [rr,ss]=await Promise.all([
        supabaseClient.from('athlete_reminders')
          .select('id,title,body,category,schedule_type,reminder_date,weekday,remind_time,active')
          .eq('athlete_id',athlete.id).eq('active',true),
        supabaseClient.from('athlete_schedule')
          .select('id,weekday,workout_day_name,start_time,notes,active')
          .eq('athlete_id',athlete.id).eq('active',true)
      ]);
      if(rr.error)throw rr.error;if(ss.error)throw ss.error;"""
    new="""      const readRows=await globalThis.TeamFJZAgendaReadPolicy.readAgendaWithCompatibility({
        enabled:document.querySelector('meta[name="fjz-v22-agenda-repository-read"]')?.content==='enabled',
        canonicalRead:async()=>{
          if(!agendaRepositoryV22){
            agendaRepositoryV22=globalThis.TeamFJZAgendaRepository.createAgendaRepository({
              supabase:supabaseClient,
              ttlMs:15000
            });
          }
          // The canonical repository owns de-duplication/cache even when legacy
          // callers request force=true. Explicit repository clear() is the only
          // way to bypass that cache in this bounded 1B pilot.
          return agendaRepositoryV22.listForAthlete(athlete.id,{force:false});
        },
        legacyRead:async()=>{
          const [scheduleRes,reminderRes]=await Promise.all([
            supabaseClient.from('athlete_schedule')
              .select('*').eq('athlete_id',athlete.id).eq('active',true).order('weekday',{ascending:true}),
            supabaseClient.from('athlete_reminders')
              .select('*').eq('athlete_id',athlete.id).eq('active',true)
          ]);
          if(scheduleRes.error)throw scheduleRes.error;
          if(reminderRes.error)throw reminderRes.error;
          return {
            source:'legacy-v312',
            athleteId:athlete.id,
            schedule:scheduleRes.data||[],
            reminders:reminderRes.data||[]
          };
        }
      });
      const rr={data:readRows.reminders||[],error:null};
      const ss={data:readRows.schedule||[],error:null};"""
    if body.count(old)!=1:
        raise RuntimeError("V22 1B V312 Agenda read anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    data_old="      const data={athlete,items};"
    data_new="      const data={athlete,items,source:readRows.source||'legacy-v312'};"
    if body.count(data_old)!=1:
        raise RuntimeError("V22 1B V312 data source anchor mismatch")
    body=body.replace(data_old,data_new,1)
    return body

html=edit_script(html,"v312ReviewAgendaAuthorityRuntime",patch_v312)

after=topology(html)
if after!=before:
    raise RuntimeError("V22 1B pilot changed runtime topology: "+repr({"before":before,"after":after}))

for marker in [
    'id="v22CanonicalDateCore"',
    'id="v22AgendaRepositoryCore"',
    'id="v22AgendaReadPolicyCore"',
    'meta name="fjz-v22-1a-architecture-foundation" content="date-pilot"',
    'meta name="fjz-v22-1b-data-sync-foundation" content="agenda-read-pilot"',
    'meta name="fjz-v22-agenda-repository-read" content="'+agenda_flag+'"',
    "globalThis.TeamFJZDate.calendarDate",
    "TeamFJZAgendaReadPolicy.readAgendaWithCompatibility",
    "TeamFJZAgendaRepository.createAgendaRepository",
    "source:readRows.source||'legacy-v312'",
]:
    if marker not in html:
        raise RuntimeError("V22 foundation missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V22 1A/1B architecture + data sync foundation")
print("V22 1B Agenda repository flag:",agenda_flag)
print("V22 1B topology:",after)
