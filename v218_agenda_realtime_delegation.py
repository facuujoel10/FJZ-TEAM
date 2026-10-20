import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.18 AGENDA REALTIME DELEGATION
# =========================================================
# V13.2 unified realtime owns athlete_schedule + athlete_reminders and
# invalidates agendaLoadedV81. V14.6 view-scoped rendering covers student home,
# student agenda, coach agenda and coach-student agenda. Remove only V8.1's
# duplicate channel; preserve all agenda/reminder/password-recovery UX.

def metrics(doc):
    return {
        "channel_defs":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

before=metrics(html)
if before["channel_defs"]!=3:
    raise RuntimeError("V20.18 unexpected channel baseline: "+repr(before))
if html.count("fjz-v81-agenda")!=1:
    raise RuntimeError("V20.18 expected exactly one V81 agenda channel")
if "fjz-v132-unified" not in html:
    raise RuntimeError("V20.18 unified realtime authority missing")

start_marker="const _setupRealtimeV81Base=setupRealtime;"
end_marker="Object.assign(window,{"
if html.count(start_marker)!=1:
    raise RuntimeError("V20.18 agenda start marker mismatch: "+str(html.count(start_marker)))

start=html.index(start_marker)
end=html.index(end_marker,start)
block=html[start:end]

required=[
    "fjz-v81-agenda",
    "table:'athlete_schedule'",
    "table:'athlete_reminders'",
    "agendaLoadedV81=false",
]
missing=[x for x in required if x not in block]
if missing:
    raise RuntimeError("V20.18 agenda channel shape changed: "+repr(missing))
if block.count(".channel(")!=1:
    raise RuntimeError("V20.18 expected one channel in V81 wrapper")

html=html[:start]+"window.__fjzV81RealtimeDelegatedV218=true;\n\n"+html[end:]

after=metrics(html)
if after["channel_defs"]!=2:
    raise RuntimeError("V20.18 expected channel defs 3 -> 2: "+repr({"before":before,"after":after}))
if "fjz-v81-agenda" in html:
    raise RuntimeError("V20.18 legacy agenda channel still present")

critical=[
    "fjz-v132-unified",
    "agendaLoadedV81=false",
    "athlete_schedule",
    "athlete_reminders",
    "home:new Set(['athlete_schedule','athlete_reminders'",
    "agenda:new Set(['athlete_schedule','athlete_reminders'])",
    "renderCoachAgendaV81",
    "openStudentAgendaV81",
    "saveStudentScheduleV81",
    "openAddReminderV81",
    "saveReminderV81",
    "deleteReminderV81",
    "requestPasswordResetV81",
    "saveRecoveredPasswordV81",
    "singleRealtimeAuthority:true",
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.18 missing agenda behavior: "+repr(missing))

runtime=r"""
<script id="v218AgendaRealtimeDelegationRuntime">
(function(){
  window.__fjzV218={
    version:'20.18',
    agendaRealtimeDelegated:true,
    agendaUiPreserved:true,
    reminderUiPreserved:true,
    passwordRecoveryPreserved:true,
    agendaCacheInvalidationPreserved:true,
    viewScopedAgendaRefreshPreserved:true,
    paymentRealtimeUntouched:true,
    behaviorChange:false
  };
})();
</script>
"""
html=html.replace("</body>",runtime+"\n</body>",1)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.18 agenda realtime delegation")
print("V20.18 BEFORE:",before)
print("V20.18 AFTER:",after)
print("V20.18 duplicate agenda channel removed; agenda/reminders UX preserved")
