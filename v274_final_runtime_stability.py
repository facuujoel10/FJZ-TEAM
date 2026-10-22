import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "day_editors":len(re.findall(r"(?:window\.)?dayEditor\s*=",doc)),
        "render_workout":len(re.findall(r"(?:window\.)?renderWorkout\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "intervals":len(re.findall(r"setInterval\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
        "performance_observers":len(re.findall(r"new\s+PerformanceObserver",doc)),
        "scroll_calls":len(re.findall(r"(?:scrollTo|scrollIntoView)\s*\(",doc)),
    }

def edit_script(doc,script_id,transform):
    pat=re.compile(r'(<script[^>]*\bid=["\']'+re.escape(script_id)+r'["\'][^>]*>)(.*?)(</script>)',re.S|re.I)
    m=pat.search(doc)
    if not m:
        raise RuntimeError("V20.74 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body:
        raise RuntimeError("V20.74 no change in "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'id="v272PreparationNutritionCalculatorRuntime"',
    'id="v273PreparationPersistenceRuntime"',
    'meta name="fjz-preparation-nutrition-hardening" content="20.73"',
    "preparationMigrationPersisted:true",
]:
    if marker not in html:
        raise RuntimeError("V20.74 prerequisite missing "+marker)

def consolidate_v272(body):
    anchor="""  window.canonicalizePreparationV272=function(){
    let changed=false;
    (student()?.days||[]).forEach(d=>{if(canonicalizeDayPrepV272(d))changed=true});
    return changed;
  };

  const baseDayEditorV272=dayEditor;"""
    replacement="""  window.canonicalizePreparationV272=function(){
    let changed=false;
    (student()?.days||[]).forEach(d=>{if(canonicalizeDayPrepV272(d))changed=true});
    return changed;
  };

  let prepPersistQueuedV274=false;
  function persistPrepMigrationV274(changed){
    if(!changed||prepPersistQueuedV274)return;
    prepPersistQueuedV274=true;
    queueMicrotask(()=>{
      prepPersistQueuedV274=false;
      saveState();
    });
  }

  const baseDayEditorV272=dayEditor;"""
    if anchor not in body:
        raise RuntimeError("V20.74 canonicalization anchor missing")
    body=body.replace(anchor,replacement,1)

    old_day="""  dayEditor=function(d,i){
    canonicalizeDayPrepV272(d);
    return baseDayEditorV272.apply(this,arguments);
  };"""
    new_day="""  dayEditor=function(d,i){
    const changed=canonicalizeDayPrepV272(d);
    persistPrepMigrationV274(changed);
    return baseDayEditorV272.apply(this,arguments);
  };"""
    if old_day not in body:
        raise RuntimeError("V20.74 dayEditor anchor missing")
    body=body.replace(old_day,new_day,1)

    old_workout="""  window.renderWorkout=function(){
    canonicalizeDayPrepV272(student()?.days?.[currentDay]);
    return baseRenderWorkoutV272.apply(this,arguments);
  };"""
    new_workout="""  window.renderWorkout=function(){
    const changed=canonicalizeDayPrepV272(student()?.days?.[currentDay]);
    persistPrepMigrationV274(changed);
    return baseRenderWorkoutV272.apply(this,arguments);
  };"""
    if old_workout not in body:
        raise RuntimeError("V20.74 renderWorkout anchor missing")
    body=body.replace(old_workout,new_workout,1)

    old_flags="""    studentFoodCalculatorClarified:true
  };"""
    new_flags="""    studentFoodCalculatorClarified:true,
    preparationPersistenceIntegratedV274:true,
    preparationSaveCoalescedV274:true
  };"""
    if old_flags not in body:
        raise RuntimeError("V20.74 V272 flags anchor missing")
    body=body.replace(old_flags,new_flags,1)
    return body

html=edit_script(html,"v272PreparationNutritionCalculatorRuntime",consolidate_v272)

# V20.73's second wrapper is now redundant. Remove it completely after
# integrating persistence into the V20.72 canonical preparation authority.
pat_v273=re.compile(r'\n?<script[^>]*\bid=["\']v273PreparationPersistenceRuntime["\'][^>]*>.*?</script>\n?',re.S|re.I)
html,n_removed=pat_v273.subn("\n",html,count=1)
if n_removed!=1:
    raise RuntimeError("V20.74 could not remove duplicate V20.73 preparation wrapper")

html=html.replace("</head>",'<meta name="fjz-final-runtime-stability" content="20.74">\n</head>',1)

after=metrics(html)

# This pass intentionally removes one nested dayEditor/renderWorkout wrapper;
# it must not add any timers, listeners, observers, RAFs, channels or renders.
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers","performance_observers","scroll_calls"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.74 unexpected topology change "+key+": "+repr({"before":before,"after":after}))

if after["day_editors"]>=before["day_editors"]:
    raise RuntimeError("V20.74 did not reduce dayEditor wrapper depth")
if after["render_workout"]>=before["render_workout"]:
    raise RuntimeError("V20.74 did not reduce renderWorkout wrapper depth")

for marker in [
    'meta name="fjz-final-runtime-stability" content="20.74"',
    "preparationPersistenceIntegratedV274:true",
    "preparationSaveCoalescedV274:true",
    "persistPrepMigrationV274",
    "prepPersistQueuedV274",
]:
    if marker not in html:
        raise RuntimeError("V20.74 missing marker "+marker)

if 'id="v273PreparationPersistenceRuntime"' in html:
    raise RuntimeError("V20.74 duplicate V20.73 runtime still present")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.74 final runtime stability")
print("V20.74 BEFORE:",before)
print("V20.74 AFTER:",after)
print("V20.74 removed redundant preparation wrapper and coalesced migration persistence")
