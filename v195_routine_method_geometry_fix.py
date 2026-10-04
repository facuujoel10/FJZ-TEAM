import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V19.5 ROUTINE METHOD DEDUP + WORKOUT FIELD GEOMETRY
# =========================================================

# 1) Disable the legacy V8.6 method editor. V13.7 is the canonical method UI.
legacy_pat=re.compile(
    r"""  var showExerciseFormV86Base=window\.showExerciseForm;\s*
        window\.showExerciseForm=function\(dayIndex,exIndex,e\)\{.*?\n  \};\s*
        (?=\n  window\.saveExercise=function)""",
    re.S|re.X
)
legacy_repl="""  var showExerciseFormV86Base=window.showExerciseForm;
  window.showExerciseForm=function(dayIndex,exIndex,e){
    return showExerciseFormV86Base.apply(this,arguments);
  };
"""
html,n_legacy=legacy_pat.subn(legacy_repl,html,count=1)
if n_legacy not in (0,1):
    raise RuntimeError(f"V19.5 unexpected legacy V86 editor count: {n_legacy}")

# 2) Harden the canonical V13.7 exercise editor: if any stale legacy method
#    control is produced by an older cached/runtime layer, remove it before
#    inserting the canonical method box.
old_v137="""    const grid=el('modal')?.querySelector('.form-grid');
    if(grid&&!el('v137MethodCoachBox')){
      grid.insertAdjacentHTML('beforeend',methodCoachHtmlV137(e));
      syncMethodFormV137();
    }"""
new_v137="""    const grid=el('modal')?.querySelector('.form-grid');
    const legacyMethod=el('fMethod');
    if(legacyMethod){
      const legacyHost=legacyMethod.closest('.span4')||legacyMethod.closest('.card');
      if(legacyHost&&legacyHost!==grid)legacyHost.remove();
      else legacyMethod.closest('label')?.remove();
      el('fMethodNote')?.closest('label')?.remove();
    }
    if(grid&&!el('v137MethodCoachBox')){
      grid.insertAdjacentHTML('beforeend',methodCoachHtmlV137(e));
      syncMethodFormV137();
    }"""
if html.count(old_v137)!=1:
    raise RuntimeError(f"V19.5 expected canonical V137 editor block once, got {html.count(old_v137)}")
html=html.replace(old_v137,new_v137,1)

css=r"""
<style id="v195RoutineGeometryStyles">
/* =========================================================
   V19.5 · ROUTINE / WORKOUT INPUT GEOMETRY
   ========================================================= */

/* Coach exercise editor: roomy fields again. */
.modal.v155-exercise-modal .form-grid{
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:11px!important;
}
.modal.v155-exercise-modal .form-grid>label{
  min-width:0!important;
  width:100%!important;
}
.modal.v155-exercise-modal #fSets,
.modal.v155-exercise-modal #fMin,
.modal.v155-exercise-modal #fMax,
.modal.v155-exercise-modal #fRMin,
.modal.v155-exercise-modal #fRMax,
.modal.v155-exercise-modal #fRest,
.modal.v155-exercise-modal #fInc,
.modal.v155-exercise-modal #fName,
.modal.v155-exercise-modal #fCue,
.modal.v155-exercise-modal #fRepMode,
.modal.v155-exercise-modal #fExactReps,
.modal.v155-exercise-modal #fMethodV137,
.modal.v155-exercise-modal #fMethodApplyV137,
.modal.v155-exercise-modal #fMethodNoteV137{
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  min-height:46px!important;
  height:46px!important;
  padding-left:12px!important;
  padding-right:12px!important;
  box-sizing:border-box!important;
}

/* These are sections, not tiny grid cells. */
.modal.v155-exercise-modal .v104-rep-box,
.modal.v155-exercise-modal .v137-method-coach{
  grid-column:1/-1!important;
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  box-sizing:border-box!important;
}
.modal.v155-exercise-modal .v104-rep-grid,
.modal.v155-exercise-modal .v137-method-coach-grid{
  display:grid!important;
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:10px!important;
  width:100%!important;
  min-width:0!important;
}
.modal.v155-exercise-modal .v137-method-note{
  display:flex!important;
  flex-direction:column!important;
  gap:5px!important;
  width:100%!important;
  min-width:0!important;
}

/* Student workout: Set number + 3 equally useful input columns.
   Avoid the Kg/Reps/RIR controls becoming tiny after global symmetry rules. */
.session-card .set-grid{
  display:grid!important;
  grid-template-columns:minmax(34px,42px) repeat(3,minmax(72px,1fr))!important;
  gap:8px!important;
  align-items:end!important;
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  box-sizing:border-box!important;
}
.session-card .set-grid>.set-n{
  min-width:34px!important;
  align-self:center!important;
  text-align:center!important;
}
.session-card .set-grid>label{
  display:flex!important;
  flex-direction:column!important;
  gap:5px!important;
  min-width:0!important;
  width:100%!important;
  margin:0!important;
  overflow:visible!important;
}
.session-card .set-grid>label>.input,
.session-card .set-grid>label>input{
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  height:46px!important;
  min-height:46px!important;
  max-height:46px!important;
  padding:0 9px!important;
  box-sizing:border-box!important;
  text-align:center!important;
  font-size:16px!important;
  line-height:46px!important;
  font-variant-numeric:tabular-nums!important;
}

/* Intensification sub-series also remain comfortable. */
.v137-method-step{
  min-width:0!important;
}
.v137-method-step .input{
  min-height:44px!important;
  height:44px!important;
  padding:0 9px!important;
  font-size:16px!important;
  text-align:center!important;
  box-sizing:border-box!important;
}

@media(max-width:520px){
  .session-card .set-grid{
    grid-template-columns:32px repeat(3,minmax(0,1fr))!important;
    gap:7px!important;
  }
  .session-card .set-grid>label>.input,
  .session-card .set-grid>label>input{
    height:46px!important;
    min-height:46px!important;
    max-height:46px!important;
    padding:0 6px!important;
  }
  .modal.v155-exercise-modal .form-grid{
    gap:9px!important;
  }
}
@media(max-width:360px){
  .session-card .set-grid{
    grid-template-columns:28px repeat(3,minmax(0,1fr))!important;
    gap:6px!important;
  }
}
</style>
"""

js=r"""
<script id="v195RoutineGeometryRuntime">
(function(){
  const VERSION='19.5';

  function cleanupLegacyMethodV195(){
    const modal=document.getElementById('modal');
    if(!modal)return;

    // Remove legacy controls by ID, regardless of which historical wrapper
    // created them.
    modal.querySelectorAll('#fMethod,#fMethodNote').forEach(old=>{
      const host=old.closest('.span4')||old.closest('.card');
      if(host&&host!==modal&&!host.querySelector('#v137MethodCoachBox'))host.remove();
      else old.closest('label')?.remove();
    });

    // Extra safety for an old card whose controls were already transformed.
    [...modal.querySelectorAll('.card,.span4')].forEach(node=>{
      if(node.querySelector('#v137MethodCoachBox'))return;
      if(/Método de intensificación/i.test(node.textContent||''))node.remove();
    });

    // Canonical editor must never be duplicated.
    const canonical=[...modal.querySelectorAll('#v137MethodCoachBox')];
    canonical.slice(1).forEach(x=>x.remove());
  }

  const baseShowV195=window.showExerciseForm;
  if(typeof baseShowV195==='function'){
    window.showExerciseForm=function(){
      const out=baseShowV195.apply(this,arguments);
      cleanupLegacyMethodV195();
      return out;
    };
    try{showExerciseForm=window.showExerciseForm}catch(_e){}
  }

  window.__fjzV195={
    version:VERSION,
    singleCanonicalMethodEditor:true,
    legacyMethodEditorRemoved:true,
    workoutSetFieldsRestored:true,
    coachExerciseFieldsRestored:true,
    exactRepsFullWidth:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

# Final style consolidation after V19.5.
styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
mergeable=[]
for m in styles:
    attrs=m.group("attrs") or ""
    if re.search(r"\b(media|nonce)\s*=",attrs,re.I):continue
    mergeable.append(m)
if len(mergeable)>1:
    chunks=[]
    for m in mergeable:
        ident=re.search(r'id=["\']([^"\']+)["\']',m.group("attrs") or "",re.I)
        name=ident.group(1) if ident else "anonymous"
        chunks.append("\n/* --- "+name+" --- */\n"+m.group("body").strip())
    for m in reversed(mergeable):
        html=html[:m.start()]+html[m.end():]
    html=html.replace("</head>",'<style id="fjzProductionStylesV195">'+''.join(chunks)+'\n</style>\n</head>',1)

# Hard assertions.
legacy_text_refs=html.count("Método de intensificación")
if html.count("id=\"v137MethodCoachBox\"")<1:
    raise RuntimeError("V19.5 canonical method editor missing")
if "singleCanonicalMethodEditor:true" not in html:
    raise RuntimeError("V19.5 runtime marker missing")
if len(re.findall(r"<style\b",html,re.I))!=1:
    raise RuntimeError("V19.5 expected one final stylesheet")

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V19.5 routine method dedup + field geometry enabled")
print("TEAM FJZ V19.5 legacy V86 method editor removed:",n_legacy)
print("TEAM FJZ V19.5 legacy method text refs retained only in source/runtime:",legacy_text_refs)
