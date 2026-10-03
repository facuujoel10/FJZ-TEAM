import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v191ActionGeometryAuditStyles">
/* =========================================================
   V19.1 · ACTION / BADGE GEOMETRY HARDENING
   ========================================================= */

/* Canonical workout final action. */
button.v191-session-finish,
.btn.v191-session-finish{
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  min-height:46px!important;
  height:auto!important;
  padding:11px 16px!important;
  margin-top:12px!important;
  box-sizing:border-box!important;
  border-radius:12px!important;
  font-size:12px!important;
  font-weight:850!important;
  line-height:1.2!important;
  text-align:center!important;
  white-space:normal!important;
  overflow:visible!important;
  text-overflow:clip!important;
  word-break:normal!important;
  overflow-wrap:break-word!important;
}

/* Partial-session confirmation uses the same geometry when it is the
   definitive save action. */
button.v191-session-save-confirm{
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
  min-height:42px!important;
  height:auto!important;
  padding:9px 13px!important;
  box-sizing:border-box!important;
  line-height:1.2!important;
  white-space:normal!important;
  text-align:center!important;
}

/* Only elements proven to overflow at runtime receive this class. */
.btn.v191-auto-fit,
button.v191-auto-fit{
  min-width:max-content!important;
  min-height:36px!important;
  height:auto!important;
  padding:8px 11px!important;
  box-sizing:border-box!important;
  line-height:1.15!important;
  white-space:normal!important;
  overflow:visible!important;
  text-overflow:clip!important;
}

.badge.v191-auto-fit,
.v175-agenda-row-badge.v191-auto-fit,
.v175-agenda-tab-badge.v191-auto-fit,
.v73-alert-badge.v191-auto-fit{
  display:inline-flex!important;
  align-items:center!important;
  justify-content:center!important;
  width:auto!important;
  min-width:max-content!important;
  max-width:100%!important;
  min-height:24px!important;
  height:auto!important;
  padding:5px 9px!important;
  box-sizing:border-box!important;
  line-height:1.1!important;
  white-space:nowrap!important;
  overflow:visible!important;
  text-overflow:clip!important;
}

/* Buttons inside full-width form/card actions should never look visually
   shorter than neighboring inputs. */
.tracking-form>.btn,
.card>button.btn[style*="width:100%"],
.card>.btn[style*="width:100%"]{
  min-height:42px;
  box-sizing:border-box;
}

@media(max-width:520px){
  button.v191-session-finish,
  .btn.v191-session-finish{
    min-height:48px!important;
    padding:12px 14px!important;
    font-size:12px!important;
  }

  .btn.v191-auto-fit,
  button.v191-auto-fit{
    max-width:100%!important;
    min-width:0!important;
  }
}
</style>
"""

js=r"""
<script id="v191ActionGeometryAuditRuntime">
(function(){
  const VERSION='19.1';

  function visibleV191(el){
    if(!el||!el.isConnected)return false;
    const cs=getComputedStyle(el);
    return cs.display!=='none'&&cs.visibility!=='hidden';
  }

  function markSessionActionsV191(){
    document.querySelectorAll('button,.btn').forEach(btn=>{
      if(!visibleV191(btn))return;
      const txt=(btn.textContent||'').trim().toLowerCase();
      const onclick=btn.getAttribute?.('onclick')||'';

      if(
        onclick.includes('finishWorkout')||
        /finalizar\s+(sesión|sesion|entrenamiento)/i.test(txt)
      ){
        btn.classList.add('v191-session-finish');
      }

      if(
        onclick.includes('confirmPartialSessionV106')||
        /guardar\s+sesión\s+igual/i.test(txt)
      ){
        btn.classList.add('v191-session-save-confirm');
      }
    });
  }

  function actualOverflowV191(el){
    if(!visibleV191(el))return false;
    const sw=Math.ceil(el.scrollWidth||0);
    const cw=Math.ceil(el.clientWidth||0);
    const sh=Math.ceil(el.scrollHeight||0);
    const ch=Math.ceil(el.clientHeight||0);
    return (cw>0&&sw>cw+2)||(ch>0&&sh>ch+2);
  }

  function repairActualOverflowV191(){
    document.querySelectorAll(
      '.btn,.badge,.v175-agenda-row-badge,.v175-agenda-tab-badge,.v73-alert-badge'
    ).forEach(el=>{
      el.classList.remove('v191-auto-fit');
      if(actualOverflowV191(el))el.classList.add('v191-auto-fit');
    });
  }

  function polishV191(){
    markSessionActionsV191();
    repairActualOverflowV191();
  }

  /* Use the consolidated render transaction; no new render() wrapper. */
  const basePostV191=window.__fjzPostRenderV176;
  window.__fjzPostRenderV176=function(){
    const out=basePostV191?.apply(this,arguments);
    requestAnimationFrame(polishV191);
    return out;
  };

  /* Workout body can be rendered by nested routine functions. */
  const workoutCandidates=['renderStudentRoutine','renderStudentRoutineV94','renderWorkoutDay'];
  workoutCandidates.forEach(name=>{
    const fn=window[name];
    if(typeof fn!=='function'||fn.__v191Wrapped)return;
    const wrapped=function(){
      const out=fn.apply(this,arguments);
      requestAnimationFrame(polishV191);
      return out;
    };
    wrapped.__v191Wrapped=true;
    window[name]=wrapped;
    try{globalThis[name]=wrapped}catch(_e){}
  });

  requestAnimationFrame(polishV191);

  window.__fjzV191={
    version:VERSION,
    sessionFinishGeometry:true,
    overflowOnlyAutoRepair:true,
    badgeOverflowAudit:true,
    noGeneralLayoutRewrite:true,
    noRenderWrapper:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "v191ActionGeometryAuditStyles",
  "sessionFinishGeometry:true",
  "overflowOnlyAutoRepair:true",
  "badgeOverflowAudit:true",
  "noGeneralLayoutRewrite:true",
]:
    if marker not in html:
        raise RuntimeError("V19.1 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V19.1 action geometry/overflow audit enabled")
