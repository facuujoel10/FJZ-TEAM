import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
    }

def edit_script(doc,script_id,transform):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.57 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.57 no script change "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-consolidation-gate" content="20.56"',
    'meta name="fjz-checkin-review" content="20.47"',
    'meta name="fjz-checkin-reply-loop" content="20.48"',
    "checkinCoachReviewCardV247",
    "parseCheckinFeedbackV248"
]:
    if marker not in html:
        raise RuntimeError("V20.57 missing prerequisite: "+marker)

def patch_v170(body):
    start=body.find("  function parseCheckinFeedbackV247(text){")
    end=body.find("  function checkinCoachReviewCardV247(c){",start)
    if start<0 or end<0:
        raise RuntimeError("V20.57 V247 parser block missing")

    replacement=r"""  function parseCheckinFeedbackV247(text){
    const raw=String(text||'').trim();
    const decisionMatch=raw.match(/^Decisión:\s*(.+?)(?:\n|$)/i);
    const nextMatch=raw.match(/(?:^|\n)Cómo seguimos:\s*([\s\S]*?)(?=\nPrioridad semanal:\s*|$)/i);
    const focusMatch=raw.match(/(?:^|\n)Prioridad semanal:\s*([\s\S]*)$/i);
    if(!decisionMatch&&!nextMatch&&!focusMatch){
      return {decision:'observe',nextStep:raw,weeklyFocus:''};
    }
    const label=String(decisionMatch?.[1]||'').trim();
    const map={
      'Mantener plan':'maintain',
      'Progresar':'progress',
      'Ajustar entrenamiento':'adjust_training',
      'Ajustar nutrición':'adjust_nutrition',
      'Priorizar recuperación':'recovery',
      'Contactar alumno':'contact',
      'Seguir observando':'observe'
    };
    return {
      decision:map[label]||'observe',
      nextStep:String(nextMatch?.[1]||'').trim(),
      weeklyFocus:String(focusMatch?.[1]||'').trim()
    };
  }

  function formatCheckinFeedbackV247(decision,nextStep,weeklyFocus){
    const base='Decisión: '+checkinDecisionLabelV247(decision)+'\nCómo seguimos: '+String(nextStep||'').trim();
    const focus=String(weeklyFocus||'').trim();
    return focus?base+'\nPrioridad semanal: '+focus:base;
  }

"""
    body=body[:start]+replacement+body[end:]

    card_anchor="""        (reviewed&&parsed.nextStep?'<p>'+esc(parsed.nextStep)+'</p>':'')+
"""
    card_repl="""        (reviewed&&parsed.weeklyFocus?'<div class="v257-focus-inline"><span>PRIORIDAD SEMANAL</span><strong>'+esc(parsed.weeklyFocus)+'</strong></div>':'')+
        (reviewed&&parsed.nextStep?'<p>'+esc(parsed.nextStep)+'</p>':'')+
"""
    if body.count(card_anchor)!=1:
        raise RuntimeError("V20.57 coach review card anchor mismatch: "+str(body.count(card_anchor)))
    body=body.replace(card_anchor,card_repl,1)

    modal_anchor="""        '</label>'+
        '<label class="tiny muted">Cómo seguimos · visible para el alumno'+
"""
    modal_repl="""        '</label>'+
        '<label class="tiny muted">Prioridad de la semana · visible para el alumno'+
          '<input id="v257WeeklyFocus" class="input" maxlength="180" placeholder="Ej: dormir 7 h, completar 3 sesiones y sostener pasos." value="'+esc(parsed.weeklyFocus||'')+'">'+
        '</label>'+
        '<label class="tiny muted">Cómo seguimos · visible para el alumno'+
"""
    if body.count(modal_anchor)!=1:
        raise RuntimeError("V20.57 review modal anchor mismatch: "+str(body.count(modal_anchor)))
    body=body.replace(modal_anchor,modal_repl,1)

    save_anchor="""    const decision=String(el('v247Decision')?.value||'observe');
    const nextStep=String(el('v247NextStep')?.value||'').trim().slice(0,800);
"""
    save_repl="""    const decision=String(el('v247Decision')?.value||'observe');
    const weeklyFocus=String(el('v257WeeklyFocus')?.value||'').trim().slice(0,180);
    const nextStep=String(el('v247NextStep')?.value||'').trim().slice(0,800);
"""
    if body.count(save_anchor)!=1:
        raise RuntimeError("V20.57 save fields anchor mismatch")
    body=body.replace(save_anchor,save_repl,1)

    value_anchor="    const value=formatCheckinFeedbackV247(decision,nextStep);"
    value_repl="    const value=formatCheckinFeedbackV247(decision,nextStep,weeklyFocus);"
    if body.count(value_anchor)!=1:
        raise RuntimeError("V20.57 format save anchor mismatch")
    body=body.replace(value_anchor,value_repl,1)

    student_anchor="""              '<p>'+esc(parsed.nextStep||c.coach_feedback)+'</p></div><span class="badge green">Revisado</span></div>'
"""
    student_repl="""              (parsed.weeklyFocus?'<div class="v257-student-focus"><span>PRIORIDAD DE LA SEMANA</span><strong>'+esc(parsed.weeklyFocus)+'</strong></div>':'')+
              '<p>'+esc(parsed.nextStep||c.coach_feedback)+'</p></div><span class="badge green">Revisado</span></div>'
"""
    if body.count(student_anchor)!=1:
        raise RuntimeError("V20.57 student history anchor mismatch")
    body=body.replace(student_anchor,student_repl,1)

    return body

html=edit_script(html,"v170ConsolidatedRuntime",patch_v170)

def patch_v175(body):
    start=body.find("  function parseCheckinFeedbackV248(text){")
    end=body.find("  function latestReviewedCheckinV248(){",start)
    if start<0 or end<0:
        raise RuntimeError("V20.57 V248 parser block missing")

    replacement=r"""  function parseCheckinFeedbackV248(text){
    const raw=String(text||'').trim();
    const decisionMatch=raw.match(/^Decisión:\s*(.+?)(?:\n|$)/i);
    const nextMatch=raw.match(/(?:^|\n)Cómo seguimos:\s*([\s\S]*?)(?=\nPrioridad semanal:\s*|$)/i);
    const focusMatch=raw.match(/(?:^|\n)Prioridad semanal:\s*([\s\S]*)$/i);
    if(!decisionMatch&&!nextMatch&&!focusMatch){
      return {decision:'observe',nextStep:raw,weeklyFocus:''};
    }
    const reverse={
      'Mantener plan':'maintain',
      'Progresar':'progress',
      'Ajustar entrenamiento':'adjust_training',
      'Ajustar nutrición':'adjust_nutrition',
      'Priorizar recuperación':'recovery',
      'Contactar alumno':'contact',
      'Seguir observando':'observe'
    };
    return {
      decision:reverse[String(decisionMatch?.[1]||'').trim()]||'observe',
      nextStep:String(nextMatch?.[1]||'').trim(),
      weeklyFocus:String(focusMatch?.[1]||'').trim()
    };
  }

"""
    body=body[:start]+replacement+body[end:]

    copy_anchor="        copy:parsed.nextStep||'Tu coach revisó el último check-in.',"
    copy_repl="        copy:parsed.weeklyFocus?('Prioridad de la semana: '+parsed.weeklyFocus):(parsed.nextStep||'Tu coach revisó el último check-in.'),"
    if body.count(copy_anchor)!=1:
        raise RuntimeError("V20.57 action hub copy anchor mismatch")
    body=body.replace(copy_anchor,copy_repl,1)

    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

css=r"""
/* TEAM FJZ · V20.57 WEEKLY CHECK-IN FOCUS */
.v257-focus-inline{
  display:grid;
  gap:3px;
  margin-top:7px;
  padding:7px 8px;
  border:1px solid rgba(103,173,255,.20);
  border-radius:9px;
  background:rgba(103,173,255,.055);
}
.v257-focus-inline span,
.v257-student-focus span{
  color:#7f8793;
  font-size:7px;
  font-weight:900;
  letter-spacing:.08em;
}
.v257-focus-inline strong{
  color:#dfe7f3;
  font-size:9px;
  line-height:1.4;
}
.v257-student-focus{
  display:grid;
  gap:4px;
  margin:8px 0 6px;
  padding:8px 9px;
  border-left:3px solid #67adff;
  border-radius:0 9px 9px 0;
  background:#10151d;
}
.v257-student-focus strong{
  color:#f0f3f7;
  font-size:10px;
  line-height:1.4;
}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1:
    raise RuntimeError("V20.57 stylesheet mismatch")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-checkin-weekly-focus" content="20.57">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","rafs","listeners","mutation_observers","performance_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.57 topology changed "+key+": "+repr({"before":before,"after":after}))

for marker in [
    'meta name="fjz-checkin-weekly-focus" content="20.57"',
    "v257WeeklyFocus",
    "Prioridad semanal:",
    "PRIORIDAD DE LA SEMANA",
    "parsed.weeklyFocus",
    "formatCheckinFeedbackV247(decision,nextStep,weeklyFocus)"
]:
    if marker not in html:
        raise RuntimeError("V20.57 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.57 weekly check-in focus")
print("V20.57 BEFORE:",before)
print("V20.57 AFTER:",after)
print("V20.57 coach review now stores a backward-compatible weekly priority in coach_feedback")
