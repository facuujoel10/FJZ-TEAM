import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# V20.30 AGENDA & ALERTS PRO — visual only
def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "render_assignments":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "bytes":len(doc.encode("utf-8")),
    }

before=metrics(html)
if before["styles"]!=1: raise RuntimeError("V20.30 expected one stylesheet: "+repr(before))

required=[
    "v81-week","v81-coach-week","v81-agenda-kpis","v81-reminders","renderCoachAgendaV81",
    "v96-alert-panel","v96-alert-summary","v96-alert-card","v96-alert-tools","v96-bell",
    "injectCoachAlertPanelV96","readCoachAlertV96","dismissCoachAlertV96",
    "v122FollowupPaymentsRuntime",'meta name="fjz-nutrition-ui" content="20.29"'
]
missing=[x for x in required if x not in html]
if missing: raise RuntimeError("V20.30 agenda/alerts authority missing: "+repr(missing))

css=r"""
/* TEAM FJZ · V20.30 AGENDA & ALERTS PRO */

/* ---------- Agenda ---------- */
.v81-agenda-kpis{
  gap:9px;
  margin-bottom:16px;
}

.v81-agenda-kpi{
  min-width:0;
  min-height:94px;
  display:flex;
  flex-direction:column;
  justify-content:center;
  padding:13px;
  border-color:#2c3038;
  border-radius:14px;
  background:
    linear-gradient(155deg,rgba(255,38,57,.03),transparent 52%),
    #111217;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.018);
}

.v81-agenda-kpi strong{
  color:#fff;
  font-size:24px;
  line-height:1;
  font-weight:920;
  letter-spacing:-.035em;
  font-variant-numeric:tabular-nums;
}

.v81-agenda-kpi span{
  margin-top:7px;
  color:#979ba6;
  font-size:9px;
  line-height:1.35;
  font-weight:760;
  text-transform:uppercase;
  letter-spacing:.045em;
}

.v81-week,
.v81-coach-week{
  gap:9px;
}

.v81-day,
.v81-coach-day{
  min-width:0;
  padding:11px;
  border-color:#2c3038;
  border-radius:14px;
  background:#101116;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.014);
}

.v81-day.today,
.v81-coach-day.today{
  border-color:rgba(255,38,57,.42);
  background:
    linear-gradient(145deg,rgba(255,38,57,.07),transparent 56%),
    #101116;
}

.v81-day-head{
  padding-bottom:8px;
  margin-bottom:8px;
  border-bottom:1px solid #25282f;
}

.v81-day-name{
  color:#f3f4f6;
  font-size:10px;
  font-weight:900;
  letter-spacing:.075em;
}

.v81-day-date,
.v81-day-time{
  color:#9296a1;
}

.v81-day-title{
  color:#f2f3f5;
  font-weight:850;
}

.v81-coach-entry{
  padding:9px 0;
  border-top-color:#25282f;
}

.v81-coach-entry strong{
  color:#f4f5f7;
  font-size:11px;
}

.v81-coach-entry .btn{
  min-height:31px;
}

.v81-config-grid{
  gap:9px;
}

.v81-config-day{
  color:#f3f4f6;
  font-weight:900;
}

.v81-reminders{
  gap:9px;
}

.v81-reminder{
  padding:11px 12px;
  border-color:#2c3038;
  border-radius:13px;
  background:#0f1014;
}

.v81-reminder strong{
  color:#f3f4f6;
  font-size:12px;
  font-weight:860;
}

.v81-reminder p{
  color:#9b9faa;
}

.v81-today{
  border-color:rgba(255,38,57,.24);
  border-radius:15px;
  background:
    linear-gradient(145deg,rgba(255,38,57,.065),transparent 56%),
    #101116;
}

.v81-today-list{
  gap:8px;
}

.v81-today-item{
  padding:10px 11px;
  border-color:#2c3038;
  border-radius:12px;
  background:#0d0e12;
}

/* ---------- Alert center ---------- */
.v96-alert-panel{
  margin-bottom:16px;
  border-color:#2e3139;
  border-radius:18px;
  background:
    linear-gradient(180deg,rgba(255,255,255,.016),transparent 24%),
    #101116;
  box-shadow:var(--shadow-card);
}

.v96-alert-panel>.section-title{
  margin-top:0;
}

.v96-alert-summary{
  gap:8px;
  margin:13px 0;
}

.v96-alert-kpi{
  min-width:0;
  min-height:82px;
  display:flex;
  flex-direction:column;
  justify-content:center;
  padding:11px;
  border-color:#2c3038;
  border-radius:13px;
  background:#0d0e12;
}

.v96-alert-kpi strong{
  color:#fff;
  font-size:22px;
  font-weight:920;
  letter-spacing:-.03em;
  font-variant-numeric:tabular-nums;
}

.v96-alert-kpi span{
  margin-top:6px;
  color:#9296a1;
  font-size:8px;
  font-weight:800;
  letter-spacing:.07em;
}

.v96-alert-tools{
  gap:6px;
  margin-bottom:11px;
}

.v96-chip{
  min-height:30px;
  padding:6px 9px;
  border-color:#30333c;
  background:#0c0d10;
  color:#a0a4ae;
  font-weight:780;
}

.v96-chip.active{
  border-color:var(--red-border);
  background:var(--red-soft);
  color:#fff;
}

.v96-alert-list{
  gap:8px;
}

.v96-alert-card{
  padding:12px;
  border-color:#2c3038;
  border-radius:14px;
  background:#0d0e12;
  box-shadow:none;
}

.v96-alert-card.unread{
  border-color:#3a3e48;
  background:#121318;
}

.v96-alert-card.warning{border-left-color:#f2bd55}
.v96-alert-card.critical{border-left-color:#ff4657}
.v96-alert-card.success{border-left-color:#3bd58a}
.v96-alert-card.info{border-left-color:#67adff}

.v96-alert-icon{
  width:34px;
  height:34px;
  border-color:#30333c;
  border-radius:10px;
  background:#090a0d;
  color:#f6f7f9;
  font-weight:900;
}

.v96-alert-title{
  color:#f5f6f8;
  font-size:12px;
  font-weight:880;
  line-height:1.35;
}

.v96-alert-meta{
  margin-top:4px;
  color:#898e99;
  font-size:9px;
}

.v96-alert-body{
  margin-top:6px;
  color:#adb0b9;
  font-size:10px;
  line-height:1.5;
}

.v96-alert-actions{
  gap:6px;
}

.v96-alert-actions .btn{
  min-height:31px;
}

.v96-bell{
  position:relative;
  padding-right:12px;
}

.v96-bell-count{
  right:-6px;
  top:-8px;
  min-width:19px;
  height:19px;
  background:linear-gradient(180deg,#ff4657,var(--red2));
  border-color:#090a0d;
  box-shadow:0 5px 12px rgba(198,16,34,.28);
}

.v96-student-preview,
.v96-notice-card{
  border-color:#2e3139;
}

.v96-preview-row{
  border-top-color:#25282f;
}

.v96-notice-list{
  gap:8px;
}

.v96-notice-item{
  padding:10px 11px;
  border-color:#2c3038;
  border-radius:12px;
  background:#0d0e12;
}

.v96-center-head{
  margin-bottom:11px;
}

.v96-empty{
  padding:24px 10px;
  color:#898e99;
}

/* Never style or modify the postponed payments/followups runtime. */

@media(max-width:760px){
  .v81-agenda-kpis{
    grid-template-columns:repeat(2,minmax(0,1fr));
  }

  .v81-week,
  .v81-coach-week{
    grid-template-columns:repeat(2,minmax(0,1fr));
  }

  .v81-config-grid{
    gap:7px;
  }

  .v96-alert-summary{
    grid-template-columns:repeat(2,minmax(0,1fr));
  }

  .v96-alert-card{
    grid-template-columns:34px minmax(0,1fr);
  }

  .v96-alert-actions{
    padding-left:44px;
  }
}

@media(max-width:470px){
  .v81-week,
  .v81-coach-week{
    grid-template-columns:1fr;
  }

  .v81-agenda-kpis{
    grid-template-columns:1fr 1fr;
  }

  .v81-agenda-kpi{
    min-height:84px;
    padding:11px;
  }

  .v96-alert-card{
    padding:10px;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V20.30 stylesheet surface changed: "+str(len(styles)))
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

marker='<meta name="fjz-agenda-alerts-ui" content="20.30">'
if re.search(r'<meta\s+name=["\']fjz-agenda-alerts-ui["\']',html,re.I):
    html=re.sub(r'<meta\s+name=["\']fjz-agenda-alerts-ui["\']\s+content=["\'][^"\']*["\']\s*/?>',marker,html,count=1,flags=re.I)
else:
    html=html.replace("</head>",marker+"\n</head>",1)

after=metrics(html)
for key in ("styles","render_assignments","channels","mutation_observers","performance_observers","timeouts","rafs","listeners"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.30 runtime topology changed for "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-agenda-alerts-ui" content="20.30"',"TEAM FJZ · V20.30 AGENDA & ALERTS PRO",
    ".v81-agenda-kpi",".v81-coach-day",".v81-reminder",".v96-alert-panel",
    ".v96-alert-card",".v96-chip",".v96-bell-count",
    "readCoachAlertV96","dismissCoachAlertV96","v122FollowupPaymentsRuntime",
    'meta name="fjz-nutrition-ui" content="20.29"'
]
missing=[x for x in critical if x not in html]
if missing: raise RuntimeError("V20.30 missing agenda/alerts/stability marker: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.30 agenda alerts pro")
print("V20.30 BEFORE:",before)
print("V20.30 AFTER:",after)
print("V20.30 agenda/alerts visual hierarchy polished; payments/runtime unchanged")
