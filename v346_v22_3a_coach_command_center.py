import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")
required=[
 'meta name="fjz-athlete-alert-curtain" content="21.38"',
 'meta name="fjz-review-center-curtain" content="21.39"',
 'meta name="fjz-no-first-review-alerts" content="21.27"',
 'meta name="fjz-v22-agenda-repository-read" content="enabled"',
 'meta name="fjz-v22-2c-intelligent-training" content="enabled"',
]
for marker in required:
    if marker not in html: raise RuntimeError("V22 3A prerequisite missing: "+marker)
comment_repo=pathlib.Path("src/data/comment-repository.js").read_text(encoding="utf-8").strip()
if "</script" in comment_repo.lower(): raise RuntimeError("V22 3A CommentRepository source contains closing script markup")
if 'id="v22ReadErrorsCore"' not in html: raise RuntimeError("V22 3A read-error authority missing")
if 'id="v22CommentRepositoryCore"' not in html:
    html=html.replace("</head>",'<script id="v22CommentRepositoryCore">\\n'+comment_repo+'\\n</script>\\n<meta name="fjz-v22-comment-repository-read" content="enabled">\\n</head>',1)
js=pathlib.Path("src/modules/coach/command-center.js").read_text(encoding="utf-8")
css=pathlib.Path("src/ui/coach-command-center.css").read_text(encoding="utf-8")
if "TeamFJZCoachCommandCenter" in html or "fjz-coach-command-center" in html:
    raise RuntimeError("V22 3A duplicate command center injection")
html=html.replace("</head>",'<style id="v22CoachCommandCenterStyles">\\n'+css+'\\n</style>\\n<meta name="fjz-coach-command-center" content="22.3A">\\n</head>',1)
runtime='<script id="v22CoachCommandCenterRuntime">\\n'+js+'\\n</script>\\n<script id="v22CoachCommandCenterInstall">\\nif(!window.TeamFJZCoachCommandCenter?.install?.())throw new Error("TEAM FJZ V22 3A install failed");\\n</script>\\n'
if "</body>" not in html: raise RuntimeError("V22 3A body anchor missing")
html=html.replace("</body>",runtime+"</body>",1)
for marker in ['meta name="fjz-coach-command-center" content="22.3A"','id="v22CoachCommandCenterRuntime"','id="v22CoachCommandCenterInstall"','id="v22CommentRepositoryCore"','meta name="fjz-v22-comment-repository-read" content="enabled"',"VERSION='22.3A'","root.renderCoachDashboardV80=render","__fjzHydrateCoachCommandCenterV22","Abrir no equivale a resolver","firstReviewCardsDisabledV327:true"]:
    if marker not in html: raise RuntimeError("V22 3A output marker missing: "+marker)
runtime_body=re.search(r'<script id="v22CoachCommandCenterRuntime">(.*?)</script>',html,re.S)
if not runtime_body: raise RuntimeError("V22 3A runtime missing after injection")
if re.search(r'\\brender\\s*=\\s*function|const\\s+_render\\w*\\s*=\\s*render\\b',runtime_body.group(1)):
    raise RuntimeError("V22 3A must not add a global render wrapper")
if "Primera revisión" in runtime_body.group(1):
    raise RuntimeError("V22 3A may not reintroduce first-review copy")
p.write_text(html,encoding="utf-8")
print("TEAM FJZ V22 3A Coach Command Center injected",len(html))
