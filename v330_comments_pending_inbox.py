import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":doc.lower().count("<style"),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":doc.count(".channel("),
        "timeouts":doc.count("setTimeout("),
        "intervals":doc.count("setInterval("),
        "listeners":doc.count("addEventListener("),
        "mutation_observers":doc.count("new MutationObserver"),
        "performance_observers":doc.count("new PerformanceObserver"),
    }

def edit_script(doc,sid,fn):
    mid=-1
    for marker in ('id="'+sid+'"',"id='"+sid+"'"):
        mid=doc.find(marker)
        if mid>=0: break
    if mid<0: raise RuntimeError("V21.30 missing script "+sid)
    a=doc.find(">",mid); b=doc.find("</script>",a)
    if a<0 or b<0: raise RuntimeError("V21.30 malformed script "+sid)
    body=doc[a+1:b]
    body=fn(body)
    return doc[:a+1]+body+doc[b:]

before=metrics(html)

for marker in [
    'meta name="fjz-comment-ok-exercise-focus" content="21.29"',
    'id="v302ReviewResolutionAuthorityRuntime"',
    'id="v175ProfileAgendaCoachCenterRuntime"',
    "trainingCommentOkV329:true",
    "trainingCommentOkIn360V329:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.30 prerequisite missing "+marker)

def patch_v302(body):
    old="""    const rows=allTrainingCommentsV325();
    const pending=rows.filter(x=>x.status==='pending').length;
    const visible=rows.slice(0,8);"""
    new="""    const rows=allTrainingCommentsV325();
    const pendingRows=rows.filter(x=>x.status==='pending');
    const pending=pendingRows.length;
    const visible=pendingRows.slice(0,8);"""
    if body.count(old)!=1:
        raise RuntimeError("V21.30 dashboard pending-only anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""      '<div class="v301-empty"><strong>Sin comentarios recientes</strong><span>Cuando un alumno escriba algo en su entrenamiento va a aparecer acá.</span></div>');"""
    new="""      '<div class="v301-empty"><strong>Sin comentarios pendientes</strong><span>Los comentarios que marques con OK desaparecen de este panel y siguen disponibles dentro del historial de la sesión.</span></div>');"""
    if body.count(old)!=1:
        raise RuntimeError("V21.30 dashboard empty-state anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    flag="""    trainingCommentCarriesExerciseIdentityV329:true,"""
    if body.count(flag)!=1:
        raise RuntimeError("V21.30 dashboard flag anchor mismatch")
    body=body.replace(flag,flag+"""
    trainingCommentsInboxPendingOnlyV330:true,
    reviewedCommentsLeaveDashboardV330:true,""",1)
    return body

html=edit_script(html,"v302ReviewResolutionAuthorityRuntime",patch_v302)

def patch_v175(body):
    old="""    const rows=trainingCommentsForStudentV325();
    const pending=rows.filter(x=>x.status==='pending').length;"""
    new="""    const rows=trainingCommentsForStudentV325();
    const pendingRows=rows.filter(x=>x.status==='pending');
    const pending=pendingRows.length;"""
    if body.count(old)!=1:
        raise RuntimeError("V21.30 360 pending-only count anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    old="""      (rows.length?'<div class="v325-student-comments-list">'+rows.slice(0,10).map(trainingCommentStudentCardV325).join('')+'</div>':
      '<div class="empty">Este alumno todavía no dejó comentarios en sus entrenamientos.</div>');"""
    new="""      (pendingRows.length?'<div class="v325-student-comments-list">'+pendingRows.slice(0,10).map(trainingCommentStudentCardV325).join('')+'</div>':
      '<div class="empty">No hay comentarios pendientes de este alumno. Los revisados siguen visibles dentro del historial de cada sesión.</div>');"""
    if body.count(old)!=1:
        raise RuntimeError("V21.30 360 pending-only list anchor mismatch: "+str(body.count(old)))
    body=body.replace(old,new,1)

    flag="""    trainingCommentOkIn360V329:true"""
    if body.count(flag)!=1:
        raise RuntimeError("V21.30 360 flag anchor mismatch")
    body=body.replace(flag,flag+""",
    reviewedCommentsLeave360PanelV330:true""",1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

html=html.replace("</head>",'<meta name="fjz-comments-pending-inbox" content="21.30">\n</head>',1)

after=metrics(html)
for key in before:
    if after[key]!=before[key]:
        raise RuntimeError("V21.30 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-comments-pending-inbox" content="21.30"',
    "const pendingRows=rows.filter(x=>x.status==='pending')",
    "const visible=pendingRows.slice(0,8)",
    "Sin comentarios pendientes",
    "reviewedCommentsLeaveDashboardV330:true",
    "reviewedCommentsLeave360PanelV330:true",
    "globalSaveIntegrity:true",
    "sessionSuccessRequiresDoubleVerification:true",
]:
    if marker not in html:
        raise RuntimeError("V21.30 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V21.30 pending-only comments inbox")
print("V21.30 BEFORE:",before)
print("V21.30 AFTER:",after)
