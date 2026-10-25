import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V20.26 COACH STUDENT PROFILE / 360 PRO
# =========================================================
# Visual-only polish of the canonical V17.5 coach profile + 360 summary.
# No new JS runtime work, queries, listeners, timers, RAFs or channels.

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

if before["styles"]!=1:
    raise RuntimeError("V20.26 expected one stylesheet: "+repr(before))

required_before=[
    "__fjzV175",
    "single360:true",
    "richer360:true",
    'id="v175Coach360"',
    "v175-360-head",
    "v175-360-grid",
    "v175-360-section",
    "v175-assistant-list",
    "v175-message",
    "v175-coach-profile-hero",
    'meta name="fjz-student-dashboard" content="20.24"',
    'meta name="fjz-coach-dashboard" content="20.25"',
]
missing=[x for x in required_before if x not in html]
if missing:
    raise RuntimeError("V20.26 canonical 360/dashboard baseline missing: "+repr(missing))

css=r"""
/* =========================================================
   TEAM FJZ · V20.26 COACH STUDENT PROFILE / 360 PRO
   ========================================================= */

/* ---------- Student profile hero as coach ---------- */
.v175-coach-profile-hero{
  display:grid!important;
  grid-template-columns:82px minmax(0,1fr) auto!important;
  gap:16px!important;
  align-items:center!important;
  padding:16px 18px!important;
  margin-bottom:13px!important;
  border:1px solid #2f323b;
  border-radius:18px;
  background:
    radial-gradient(circle at 0 0,rgba(255,38,57,.08),transparent 34%),
    linear-gradient(180deg,rgba(255,255,255,.018),transparent 45%),
    #0e0f13;
  box-shadow:0 16px 42px rgba(0,0,0,.21);
}

#v175CoachAvatarSlot{
  width:82px!important;
  height:82px!important;
  align-self:center;
}

#v175CoachAvatarSlot .v70-avatar,
#v175CoachAvatarSlot .v70-avatar.big,
#v175CoachAvatarSlot img{
  width:82px!important;
  height:82px!important;
  border-radius:18px!important;
  border:1px solid #3b3f49!important;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.06),
    0 10px 26px rgba(0,0,0,.25);
}

.v175-coach-profile-info{
  min-width:0!important;
}

.v175-coach-profile-info h2{
  margin:0 0 5px!important;
  font-size:26px!important;
  letter-spacing:-.035em!important;
}

.v175-coach-profile-info p{
  margin:0!important;
  color:#a7aab3!important;
  font-size:12px!important;
  line-height:1.45!important;
}

.v175-coach-profile-actions{
  display:flex!important;
  align-items:center!important;
  justify-content:flex-end!important;
  gap:7px!important;
  flex-wrap:wrap!important;
  min-width:0!important;
}

.v175-coach-profile-actions .badge{
  min-height:31px;
  display:inline-flex;
  align-items:center;
}

.v175-coach-profile-actions .btn{
  min-height:34px;
}

/* ---------- Profile tabs ---------- */
.v175-coach-profile-hero + .tabs,
#view>.tabs{
  margin:0 0 14px!important;
  padding:5px!important;
  gap:4px!important;
  border:1px solid var(--border)!important;
  border-radius:14px!important;
  background:#0d0e12!important;
  overflow-x:auto;
}

.v175-coach-profile-hero + .tabs .tab,
#view>.tabs .tab{
  min-height:35px;
  padding:7px 13px!important;
  border-radius:10px!important;
  border-color:transparent!important;
  background:transparent!important;
  white-space:nowrap;
}

.v175-coach-profile-hero + .tabs .tab.active,
#view>.tabs .tab.active{
  border-color:rgba(255,38,57,.30)!important;
  background:rgba(255,38,57,.10)!important;
  color:#fff!important;
}

/* ---------- Canonical 360 card ---------- */
#v175Coach360{
  gap:0!important;
  padding:0!important;
  overflow:hidden;
  border-color:#30333c!important;
  background:
    linear-gradient(180deg,rgba(255,255,255,.018),transparent 24%),
    #101116!important;
  box-shadow:0 16px 44px rgba(0,0,0,.22)!important;
}

.v175-360-head{
  min-height:82px;
  padding:17px 18px 15px;
  align-items:center!important;
  background:
    linear-gradient(90deg,rgba(255,38,57,.065),transparent 42%),
    rgba(255,255,255,.008);
  border-bottom:1px solid var(--border-soft);
}

.v175-360-head h3{
  font-size:19px!important;
  font-weight:920!important;
  letter-spacing:-.025em!important;
  color:#fff;
}

.v175-360-head p{
  max-width:650px;
  margin-top:5px!important;
  font-size:10px!important;
  color:#9fa2ab!important;
}

#v175SummaryState{
  display:inline-flex;
  align-items:center;
  min-height:27px;
  padding:5px 9px;
  border:1px solid rgba(59,213,138,.18);
  border-radius:999px;
  color:#baf2d1!important;
  background:rgba(59,213,138,.045);
  font-weight:800;
}

/* ---------- 360 metrics ---------- */
.v175-360-grid{
  grid-template-columns:repeat(6,minmax(0,1fr))!important;
  gap:0!important;
  padding:0 18px;
  border-bottom:1px solid var(--border-soft);
}

.v175-360-metric{
  min-height:90px;
  display:flex;
  flex-direction:column;
  justify-content:center;
  padding:15px 13px!important;
  border:0!important;
  border-right:1px solid var(--border-soft)!important;
  border-radius:0!important;
  background:transparent!important;
}

.v175-360-metric:last-child{
  border-right:0!important;
}

.v175-360-metric strong{
  font-size:20px!important;
  font-weight:920!important;
  letter-spacing:-.035em;
  color:#fff;
}

.v175-360-metric span{
  margin-top:6px!important;
  font-size:9px!important;
  font-weight:730;
  color:#8f929d!important;
}

/* ---------- Sections ---------- */
.v175-360-section{
  padding:16px 18px!important;
  border-top:0!important;
  border-bottom:1px solid var(--border-soft);
}

.v175-360-section:last-child{
  border-bottom:0;
}

.v175-360-section-head{
  margin-bottom:11px!important;
}

.v175-360-section-head h4{
  font-size:13px!important;
  font-weight:880!important;
  letter-spacing:-.012em;
  color:#f6f7f9;
}

.v175-360-section-head p{
  margin-top:4px!important;
  font-size:9px!important;
  color:#90949e!important;
}

#v175Coverage{
  display:inline-flex;
  align-items:center;
  padding:5px 8px;
  border:1px solid var(--border);
  border-radius:999px;
  background:#0d0e12;
  white-space:nowrap;
}

/* ---------- Connected status ---------- */
.v175-status-row{
  gap:7px!important;
}

.v175-status-chip{
  min-height:30px!important;
  padding:6px 9px!important;
  border-color:#30333c!important;
  background:#0d0f13!important;
  color:#b1b4bc!important;
  font-weight:760;
}

.v175-status-chip.good{
  color:#baf2d1!important;
  border-color:rgba(59,213,138,.22)!important;
  background:rgba(59,213,138,.045)!important;
}

.v175-status-chip.warn{
  color:#ffc4ca!important;
  border-color:rgba(255,38,57,.28)!important;
  background:rgba(255,38,57,.055)!important;
}

/* ---------- Assistant ---------- */
.v175-executive{
  position:relative;
  padding:13px 14px 13px 17px!important;
  border:1px solid rgba(103,173,255,.19)!important;
  border-radius:13px!important;
  background:
    linear-gradient(90deg,rgba(103,173,255,.065),transparent 60%),
    #0d0f13!important;
  color:#dfe8f5;
  font-size:10px!important;
  line-height:1.55!important;
  margin-bottom:10px!important;
}

.v175-executive::before{
  content:"";
  position:absolute;
  left:0;
  top:10px;
  bottom:10px;
  width:3px;
  border-radius:4px;
  background:#67adff;
}

.v175-assistant-list{
  gap:9px!important;
}

.v175-advice{
  padding:12px 13px!important;
  border-color:#2e313a!important;
  border-radius:13px!important;
  background:#0e0f13!important;
}

.v175-advice.review{
  border-color:rgba(255,38,57,.25)!important;
  background:rgba(255,38,57,.045)!important;
}

.v175-advice.good{
  border-color:rgba(59,213,138,.20)!important;
  background:rgba(59,213,138,.035)!important;
}

.v175-advice h5{
  font-size:11px!important;
  font-weight:880!important;
  color:#f3f4f6;
}

.v175-advice p{
  font-size:10px!important;
  line-height:1.5!important;
}

.v175-evidence{
  border-top-color:#292c34!important;
  color:#8e929c!important;
}

.v175-advice-actions .btn{
  min-height:31px;
}

/* ---------- Coach message ---------- */
.v175-message{
  min-height:66px;
  padding:13px 14px!important;
  border-color:rgba(255,38,57,.16)!important;
  border-radius:13px!important;
  background:
    linear-gradient(90deg,rgba(255,38,57,.045),transparent 50%),
    #0d0e12!important;
  color:#dcdee4;
  font-size:10px!important;
  line-height:1.55!important;
}

/* ---------- Coach student body spacing ---------- */
#coachStudentBody{
  min-width:0;
}

#coachStudentBody>.card,
#coachStudentBody>.grid,
#coachStudentBody>.section-title{
  scroll-margin-top:110px;
}

/* ---------- Responsive ---------- */
@media(max-width:980px){
  .v175-360-grid{
    grid-template-columns:repeat(3,minmax(0,1fr))!important;
  }
  .v175-360-metric:nth-child(3){
    border-right:0!important;
  }
  .v175-360-metric:nth-child(-n+3){
    border-bottom:1px solid var(--border-soft)!important;
  }
}

@media(max-width:760px){
  .v175-coach-profile-hero{
    grid-template-columns:64px minmax(0,1fr)!important;
    gap:11px!important;
    padding:14px!important;
  }

  #v175CoachAvatarSlot{
    width:64px!important;
    height:64px!important;
  }

  #v175CoachAvatarSlot .v70-avatar,
  #v175CoachAvatarSlot .v70-avatar.big,
  #v175CoachAvatarSlot img{
    width:64px!important;
    height:64px!important;
    border-radius:15px!important;
  }

  .v175-coach-profile-info h2{
    font-size:22px!important;
  }

  .v175-coach-profile-actions{
    grid-column:1/-1!important;
    width:100%!important;
    justify-content:flex-start!important;
  }

  .v175-coach-profile-hero + .tabs,
  #view>.tabs{
    border-radius:12px!important;
  }

  .v175-360-head{
    min-height:auto;
    padding:15px!important;
  }

  .v175-360-grid{
    padding:0 15px!important;
  }

  .v175-360-section{
    padding:15px!important;
  }
}

@media(max-width:520px){
  .v175-360-grid{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
  }

  .v175-360-metric{
    min-height:82px;
    border-bottom:1px solid var(--border-soft)!important;
  }

  .v175-360-metric:nth-child(2n){
    border-right:0!important;
  }

  .v175-360-metric:nth-last-child(-n+2){
    border-bottom:0!important;
  }

  .v175-360-head,
  .v175-360-section-head{
    display:block!important;
  }

  #v175SummaryState,
  #v175Coverage{
    margin-top:7px;
  }
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.26 stylesheet surface changed: "+str(len(styles)))

m=styles[0]
new_body=m.group("body").rstrip()+"\n"+css+"\n"
html=html[:m.start("body")]+new_body+html[m.end("body"):]

marker='<meta name="fjz-coach-student-profile" content="20.26">'
if re.search(r'<meta\s+name=["\']fjz-coach-student-profile["\']',html,re.I):
    html=re.sub(
        r'<meta\s+name=["\']fjz-coach-student-profile["\']\s+content=["\'][^"\']*["\']\s*/?>',
        marker,html,count=1,flags=re.I
    )
else:
    html=html.replace("</head>",marker+"\n</head>",1)

after=metrics(html)

for key in (
    "styles","render_assignments","channels","mutation_observers",
    "performance_observers","timeouts","rafs","listeners"
):
    if after[key]!=before[key]:
        raise RuntimeError("V20.26 runtime topology changed for "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-coach-student-profile" content="20.26"',
    "TEAM FJZ · V20.26 COACH STUDENT PROFILE / 360 PRO",
    ".v175-coach-profile-hero",
    "#v175Coach360",
    ".v175-360-grid",
    ".v175-executive",
    ".v175-assistant-list",
    ".v175-message",
    "__fjzV175",
    "single360:true",
    "richer360:true",
    'meta name="fjz-coach-dashboard" content="20.25"',
    'meta name="fjz-student-dashboard" content="20.24"',
]
missing=[x for x in critical if x not in html]
if missing:
    raise RuntimeError("V20.26 missing 360/stability marker: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.26 coach student profile / 360 pro")
print("V20.26 BEFORE:",before)
print("V20.26 AFTER:",after)
print("V20.26 canonical V17.5 360 visually upgraded; runtime topology unchanged")
