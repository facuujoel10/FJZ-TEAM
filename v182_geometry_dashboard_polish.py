import pathlib
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v182GeometryCoachDashboardStyles">
/* ========================================================
   V18.2 · GEOMETRY / SPACING PASS
   Keep the app visually compact but give each block air.
   ======================================================== */
#view,
#coachStudentBody,
#studentSubBody,
.card,
.hero,
.student-row,
.form-grid,
.grid{
  min-width:0!important;
  box-sizing:border-box!important;
}

.card,
.hero,
.student-row{
  max-width:100%!important;
}

.student-list{
  display:grid!important;
  gap:9px!important;
}

.student-row{
  border-radius:13px!important;
}

.student-main{
  min-width:0!important;
}

.student-main .v182-student-copy{
  min-width:0!important;
}

.student-main .v182-student-name{
  display:block!important;
  margin:0 0 5px!important;
  font-size:13px!important;
  line-height:1.25!important;
  font-weight:850!important;
  letter-spacing:-.01em;
  overflow-wrap:normal!important;
  word-break:normal!important;
}

.student-main .v182-student-goal{
  display:-webkit-box!important;
  -webkit-box-orient:vertical;
  -webkit-line-clamp:2;
  overflow:hidden!important;
  margin:0!important;
  font-size:10px!important;
  line-height:1.4!important;
  color:var(--muted)!important;
  overflow-wrap:break-word!important;
  word-break:normal!important;
}

.v182-student-actions{
  min-width:0!important;
}

@media(min-width:901px){
  .student-main{
    display:flex!important;
    align-items:center!important;
    gap:12px!important;
  }
  .student-main>.v70-student-avatar-slot,
  .student-main>.avatar{
    flex:0 0 auto!important;
  }
}

/* Mobile dashboard rows: identity gets real space; actions get their own
   column instead of squeezing the name/goal against the avatar. */
@media(max-width:900px){
  .shell{
    padding-left:11px!important;
    padding-right:11px!important;
  }

  .card,
  .hero{
    border-radius:14px!important;
  }

  .grid,
  .metric-grid,
  .form-grid{
    column-gap:9px!important;
    row-gap:9px!important;
  }

  .student-row{
    display:grid!important;
    grid-template-columns:minmax(0,1fr) 92px!important;
    gap:12px!important;
    align-items:center!important;
    padding:12px!important;
    min-height:76px!important;
  }

  .student-row>div:nth-child(2),
  .student-row>div:nth-child(3),
  .student-row>div:nth-child(4){
    display:none!important;
  }

  .student-main{
    display:grid!important;
    grid-template-columns:50px minmax(0,1fr)!important;
    grid-template-rows:auto auto!important;
    column-gap:14px!important;
    row-gap:0!important;
    align-items:center!important;
    width:100%!important;
  }

  .student-main>.v70-student-avatar-slot,
  .student-main>.avatar{
    grid-column:1!important;
    grid-row:1 / span 2!important;
    width:50px!important;
    min-width:50px!important;
    height:50px!important;
    align-self:center!important;
  }

  .student-main>.v70-student-avatar-slot>.v70-avatar,
  .student-main>.avatar,
  .student-main>.v70-student-avatar-slot img{
    width:50px!important;
    height:50px!important;
    min-width:50px!important;
    max-width:50px!important;
    border-radius:13px!important;
    object-fit:cover!important;
  }

  .student-main>.v182-student-copy,
  .student-main>div:nth-child(2){
    grid-column:2!important;
    grid-row:1!important;
    min-width:0!important;
    align-self:center!important;
    padding-left:0!important;
    margin-left:0!important;
  }

  .student-main>.v80-student-alert-count{
    grid-column:2!important;
    grid-row:2!important;
    justify-self:start!important;
    margin:6px 0 0!important;
  }

  .student-main .v182-student-name{
    font-size:13.5px!important;
    margin-bottom:5px!important;
  }

  .student-main .v182-student-goal{
    font-size:10px!important;
    line-height:1.38!important;
  }

  .student-row>.v182-student-actions,
  .student-row>.pill-row:last-child{
    display:grid!important;
    grid-template-columns:1fr!important;
    gap:6px!important;
    width:92px!important;
    min-width:92px!important;
    max-width:92px!important;
    justify-self:end!important;
    align-self:center!important;
    margin:0!important;
  }

  .student-row>.v182-student-actions .btn,
  .student-row>.pill-row:last-child .btn{
    width:100%!important;
    min-width:0!important;
    height:32px!important;
    min-height:32px!important;
    padding:6px 7px!important;
    margin:0!important;
    font-size:9.5px!important;
    line-height:1!important;
    justify-content:center!important;
  }

  .v170-students-card>.section-title{
    margin-bottom:11px!important;
  }

  #studentSearch{
    min-height:40px!important;
    height:40px!important;
  }
}

@media(max-width:420px){
  .student-row{
    grid-template-columns:1fr!important;
    gap:10px!important;
  }

  .student-row>.v182-student-actions,
  .student-row>.pill-row:last-child{
    grid-template-columns:1fr 1fr!important;
    width:100%!important;
    min-width:0!important;
    max-width:none!important;
    justify-self:stretch!important;
  }
}

@media(max-width:360px){
  .student-main{
    grid-template-columns:46px minmax(0,1fr)!important;
    column-gap:12px!important;
  }
  .student-main>.v70-student-avatar-slot,
  .student-main>.avatar,
  .student-main>.v70-student-avatar-slot>.v70-avatar,
  .student-main>.v70-student-avatar-slot img{
    width:46px!important;
    min-width:46px!important;
    max-width:46px!important;
    height:46px!important;
  }
}
</style>
"""

js=r"""
<script id="v182GeometryCoachDashboardRuntime">
(function(){
  const VERSION='18.2';

  function renderStudentRowsV182(arr){
    return (arr||[]).map(function(s){
      const goal=(s.goal||'Sin objetivo cargado').trim?.()||'Sin objetivo cargado';
      return '<div class="student-row v182-student-row" data-client-id="'+esc(s.id)+'">'+
        '<div class="student-main">'+
          '<div class="v70-student-avatar-slot"><div class="v70-avatar">'+esc((s.name||'?').slice(0,2).toUpperCase())+'</div></div>'+
          '<div class="v182-student-copy"><strong class="v182-student-name">'+esc(s.name||'Alumno')+'</strong>'+
          '<div class="muted tiny v182-student-goal">'+esc(goal)+'</div></div>'+
        '</div>'+
        '<div><strong>'+adherence(s)+'%</strong><div class="muted tiny">Adherencia</div></div>'+
        '<div><strong>'+fmtDate(s.lastWorkout)+'</strong><div class="muted tiny">Último entreno</div></div>'+
        '<div>'+badge(statusFor(s))+'</div>'+
        '<div class="pill-row v182-student-actions">'+
          '<button class="btn small" onclick="openStudent(\''+s.id+'\')">Abrir</button>'+
          '<button class="btn small" style="border-color:rgba(255,31,47,.55);color:#ff7a84" onclick="deleteStudentCloud(\''+s.id+'\')">Eliminar</button>'+
        '</div>'+
      '</div>';
    }).join('');
  }

  // studentRows is used by the dashboard and by its live search.
  window.studentRows=renderStudentRowsV182;
  try{studentRows=window.studentRows}catch(_e){}

  function decorateRowsV182(){
    document.querySelectorAll('.student-row[data-client-id]').forEach(row=>{
      row.classList.add('v182-student-row');
      const main=row.querySelector('.student-main');
      if(!main)return;

      const copy=main.querySelector('.v182-student-copy')||
        [...main.children].find(x=>!x.classList.contains('v70-student-avatar-slot')&&!x.classList.contains('avatar')&&!x.classList.contains('v80-student-alert-count'));

      if(copy){
        copy.classList.add('v182-student-copy');
        const name=copy.querySelector('strong');
        const goal=copy.querySelector('.muted');
        name?.classList.add('v182-student-name');
        goal?.classList.add('v182-student-goal');
      }

      const actions=row.querySelector(':scope > .pill-row:last-child');
      actions?.classList.add('v182-student-actions');
    });
  }

  // Reuse the consolidated post-render path; no additional render wrapper.
  const basePostV182=window.__fjzPostRenderV176;
  window.__fjzPostRenderV176=function(){
    const out=basePostV182?.apply(this,arguments);
    decorateRowsV182();
    return out;
  };

  requestAnimationFrame(decorateRowsV182);

  window.__fjzV182={
    version:VERSION,
    dashboardStudentGeometry:true,
    avatarIdentitySpacing:true,
    dedicatedActionColumn:true,
    compactGlobalGeometry:true,
    noExtraRenderWrapper:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "v182GeometryCoachDashboardStyles",
  "renderStudentRowsV182",
  "avatarIdentitySpacing:true",
  "dedicatedActionColumn:true",
  "compactGlobalGeometry:true"
]:
  if marker not in html:
    raise RuntimeError("V18.2 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V18.2 geometry/dashboard polish enabled")
