import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# V20.26 PROFILE / 360 PRO — visual only
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
if before["styles"]!=1: raise RuntimeError("V20.26 expected one stylesheet: "+repr(before))

required=[
    'id="v175Coach360"',"window.renderCoachSummary=function()","single360:true",
    "richer360:true","stableCoachIdentity:true","assistantExecutiveSummary:true",
    "assistantMaxPriorities:3","cacheFirst:true","v175-coach-profile-hero",
    "v175-360-grid","v175-executive","v175-message"
]
missing=[x for x in required if x not in html]
if missing: raise RuntimeError("V20.26 canonical 360 authority missing: "+repr(missing))

css=r"""
/* TEAM FJZ · V20.26 PROFILE 360 PRO */
.v175-coach-profile-hero{
  position:relative;padding:18px!important;border:1px solid #2e3139;border-radius:20px;
  background:linear-gradient(145deg,rgba(255,38,57,.085),transparent 42%),
             linear-gradient(180deg,rgba(255,255,255,.02),transparent 46%),#101116;
  box-shadow:var(--shadow-card);overflow:hidden
}
.v175-coach-profile-hero::after{
  content:"";position:absolute;right:-60px;bottom:-90px;width:180px;height:180px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,38,57,.08),transparent 68%);pointer-events:none
}
#v175CoachAvatarSlot{
  width:82px;height:82px;flex-basis:82px;border-radius:18px;background:#0b0c0f;
  border:1px solid #393d46;box-shadow:inset 0 1px 0 rgba(255,255,255,.035),0 12px 30px rgba(0,0,0,.24);
  overflow:hidden
}
#v175CoachAvatarSlot .v70-avatar.big{
  width:82px!important;height:82px!important;border-radius:17px!important;border:0!important
}
.v175-coach-profile-info{position:relative;z-index:1;min-width:0!important}
.v175-coach-profile-info h2{
  margin:2px 0 5px!important;color:#fff;font-size:26px;font-weight:920;letter-spacing:-.035em
}
.v175-coach-profile-info p{color:var(--muted);font-size:12px;line-height:1.5}
.v175-coach-profile-actions{position:relative;z-index:1;gap:7px!important;flex-wrap:wrap}
.v175-coach-profile-actions .btn{min-height:34px;padding-left:11px;padding-right:11px}
#studentMainTabs,#coachStudentTabs,.v175-coach-profile-hero + .tabs{margin-top:12px}

#v175Coach360{
  gap:15px;padding:18px;border:1px solid #2e3139;border-radius:20px;
  background:linear-gradient(180deg,rgba(255,255,255,.018),transparent 22%),#0f1014;
  box-shadow:var(--shadow-card)
}
.v175-360-head{padding-bottom:3px}
.v175-360-head h3{
  position:relative;margin:0;padding-left:12px;color:#fff;font-size:20px;line-height:1.15;
  font-weight:920;letter-spacing:-.028em
}
.v175-360-head h3::before{
  content:"";position:absolute;left:0;top:3px;bottom:2px;width:3px;border-radius:99px;
  background:linear-gradient(180deg,var(--red),var(--red2))
}
.v175-360-head p{margin:6px 0 0;color:var(--muted);font-size:11px;line-height:1.5;max-width:760px}
#v175SummaryState{
  flex:0 0 auto;min-height:26px;display:inline-flex;align-items:center;padding:4px 8px;
  border:1px solid var(--border);border-radius:999px;background:#0b0c0f;color:#9296a1
}
.v175-360-grid{gap:9px}
.v175-360-metric{
  min-height:92px;display:flex;flex-direction:column;justify-content:center;padding:12px;
  border-color:#2c3038;border-radius:14px;
  background:linear-gradient(160deg,rgba(255,38,57,.03),transparent 48%),#121318;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.018)
}
.v175-360-metric strong{color:#fff;font-size:20px;line-height:1.05;font-weight:920;letter-spacing:-.035em}
.v175-360-metric span{
  margin-top:7px;color:#999da8;font-size:9px;line-height:1.35;font-weight:800;
  letter-spacing:.055em;text-transform:uppercase
}

.v175-360-section{
  padding:14px;border:1px solid var(--border-soft);border-radius:15px;background:#101116
}
.v175-360-section-head{margin-bottom:11px}
.v175-360-section-head h4{color:#f6f7f9;font-size:13px;font-weight:880;letter-spacing:-.012em}
.v175-360-section-head p{margin-top:4px;color:var(--muted);font-size:10px;line-height:1.45}
.v175-status-row{gap:7px}
.v175-status-chip{
  min-height:30px;padding:6px 9px;border-color:#30333c;background:#0d0e12;
  color:#b0b3bc;font-size:9px;font-weight:760
}
.v175-status-chip.warn{color:#ffbdc3;border-color:rgba(255,38,57,.30);background:rgba(255,38,57,.075)}
.v175-status-chip.good{color:#b9f3d3;border-color:rgba(59,213,138,.25);background:rgba(59,213,138,.055)}

.v175-executive{
  margin-bottom:10px;padding:12px 13px;border-color:rgba(103,173,255,.22);
  border-left:3px solid var(--blue);border-radius:0 13px 13px 0;
  background:linear-gradient(90deg,rgba(103,173,255,.075),rgba(103,173,255,.018));
  color:#e1e9f4;font-size:11px;line-height:1.55
}
.v175-assistant-list{gap:9px}
.v175-advice{padding:12px 13px;border-color:#2d3038;border-radius:13px;background:#0d0e12}
.v175-advice.review{
  border-color:rgba(255,38,57,.28);
  background:linear-gradient(90deg,rgba(255,38,57,.06),transparent 48%),#0e0f12
}
.v175-advice.good{
  border-color:rgba(59,213,138,.22);
  background:linear-gradient(90deg,rgba(59,213,138,.045),transparent 48%),#0e0f12
}
.v175-advice h5{color:#f4f5f7;font-size:12px;font-weight:860}
.v175-advice p{margin-top:6px;font-size:10px;line-height:1.5}
.v175-evidence{margin-top:9px;padding-top:9px;border-top-color:#282b32;font-size:9px;line-height:1.45}
.v175-advice-actions{gap:7px;margin-top:10px}
.v175-advice-actions .btn{min-height:32px}
.v175-message{
  min-height:54px;padding:12px 13px;border-color:rgba(255,38,57,.17);border-radius:13px;
  background:linear-gradient(145deg,rgba(255,38,57,.045),transparent 58%),#0d0e12;
  color:#dedfe4;font-size:11px;line-height:1.55
}
#v175AgendaBanner{border-radius:15px;box-shadow:none}
.v175-agenda-item{border-color:#2c2f37;background:#0d0e12}

@media(max-width:980px){
  .v175-360-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
}
@media(max-width:760px){
  .v175-coach-profile-hero{padding:15px!important;grid-template-columns:64px minmax(0,1fr)!important;gap:11px!important}
  #v175CoachAvatarSlot{width:64px;height:64px;flex-basis:64px;border-radius:15px}
  #v175CoachAvatarSlot .v70-avatar.big{width:64px!important;height:64px!important;border-radius:14px!important}
  .v175-coach-profile-info h2{font-size:22px}
  .v175-coach-profile-actions{grid-column:1/-1!important;justify-content:flex-start!important;width:100%!important}
  #v175Coach360{padding:14px;border-radius:17px}
  .v175-360-head,.v175-360-section-head{display:block}
  #v175SummaryState,.v175-360-head>.muted,.v175-360-section-head>.muted{margin-top:7px}
  .v175-360-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media(max-width:480px){
  .v175-coach-profile-info h2{font-size:20px}
  .v175-360-metric{min-height:82px;padding:10px}
  .v175-360-metric strong{font-size:18px}
  .v175-360-section{padding:12px}
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V20.26 stylesheet surface changed: "+str(len(styles)))
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

marker='<meta name="fjz-profile-360" content="20.26">'
if re.search(r'<meta\s+name=["\']fjz-profile-360["\']',html,re.I):
    html=re.sub(r'<meta\s+name=["\']fjz-profile-360["\']\s+content=["\'][^"\']*["\']\s*/?>',marker,html,count=1,flags=re.I)
else:
    html=html.replace("</head>",marker+"\n</head>",1)

after=metrics(html)
for key in ("styles","render_assignments","channels","mutation_observers","performance_observers","timeouts","rafs","listeners"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.26 runtime topology changed for "+key+": "+repr({"before":before,"after":after}))

critical=[
    'meta name="fjz-profile-360" content="20.26"',"TEAM FJZ · V20.26 PROFILE 360 PRO",
    "v175-coach-profile-hero","v175CoachAvatarSlot","v175Coach360","v175-360-grid",
    "v175-status-chip","v175-executive","v175-assistant-list","v175-message",
    "single360:true","assistantExecutiveSummary:true",
    'meta name="fjz-coach-dashboard" content="20.25"',
    'meta name="fjz-student-dashboard" content="20.24"'
]
missing=[x for x in critical if x not in html]
if missing: raise RuntimeError("V20.26 missing profile/stability marker: "+repr(missing))

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.26 profile 360 pro")
print("V20.26 BEFORE:",before)
print("V20.26 AFTER:",after)
print("V20.26 canonical V17.5 profile/360 polished; runtime topology unchanged")
