import pathlib,re
p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

# =========================================================
# V17.9 COMPACT MOBILE LAYOUT + CHECK-IN TIME + MEASURE EDIT
# =========================================================

# Put the measurement editor directly on the legacy Evolution card used in
# Progress/Summary, not only on the newer Tracking history.
old_head="""'<div class="muted tiny">'+esc(first.measured_on)+' → '+esc(last.measured_on)+'</div></div>'+"""
new_head="""'<div class="v179-measure-head-actions"><div class="muted tiny">'+esc(first.measured_on)+' → '+esc(last.measured_on)+'</div><button type="button" class="btn small" onclick="openMeasurementManagerV179()">Editar medidas</button></div></div>'+"""
head_count=html.count(old_head)
if head_count!=1:
    raise RuntimeError(f"V17.9 expected one legacy measurement header, got {head_count}")
html=html.replace(old_head,new_head,1)

css=r"""
<style id="v179CompactMobileFixStyles">
/* Undo V17.8 rules that made mobile screens look vertically inflated. */
@media(max-width:900px){
  #coachStudentBody,#studentSubBody{
    min-height:0!important;
  }

  .card,.hero{
    width:auto!important;
  }

  .form-grid,
  .tracking-form .form-grid{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:9px!important;
  }

  .form-grid .span2,
  .tracking-form .span2{
    grid-column:1/-1!important;
  }

  .section-title{
    flex-direction:row!important;
    flex-wrap:wrap!important;
    align-items:flex-start!important;
    gap:8px!important;
  }

  .section-title>div:first-child{
    flex:1 1 170px!important;
    width:auto!important;
  }

  .section-title>.btn,
  .section-title>button,
  .section-title>input,
  .section-title>select{
    width:auto!important;
    max-width:100%!important;
    flex:0 0 auto!important;
  }

  .pill-row{
    gap:6px!important;
  }
}

@media(max-width:390px){
  .form-grid,
  .tracking-form .form-grid{
    grid-template-columns:1fr!important;
  }
  .form-grid .span2,
  .tracking-form .span2{
    grid-column:auto!important;
  }
}

/* Native mobile time controls can keep an intrinsic width larger than the
   CSS box. A clipping wrapper guarantees they never escape the card. */
.v179-time-clip{
  display:block!important;
  width:100%!important;
  max-width:100%!important;
  min-width:0!important;
  overflow:hidden!important;
  box-sizing:border-box!important;
}

#v122CheckTime,
#v165Time,
.v165-week-row input[type="time"],
input[data-v165-time]{
  display:block!important;
  -webkit-appearance:none!important;
  appearance:none!important;
  inline-size:100%!important;
  width:100%!important;
  max-inline-size:100%!important;
  max-width:100%!important;
  min-inline-size:0!important;
  min-width:0!important;
  box-sizing:border-box!important;
  overflow:hidden!important;
  font-size:16px!important;
  line-height:1.2!important;
  padding:9px 7px!important;
}

#v122CheckTime::-webkit-date-and-time-value,
#v165Time::-webkit-date-and-time-value,
.v165-week-row input[type="time"]::-webkit-date-and-time-value,
input[data-v165-time]::-webkit-date-and-time-value{
  display:block!important;
  width:100%!important;
  min-width:0!important;
  margin:0!important;
  padding:0!important;
  text-align:left!important;
}

.v179-measure-head-actions{
  display:flex;
  align-items:center;
  justify-content:flex-end;
  gap:7px;
  flex-wrap:wrap;
}

.v179-measure-manager{
  display:grid;
  gap:8px;
  margin-top:10px;
}

.v179-measure-manager-row{
  display:grid;
  grid-template-columns:minmax(0,1fr) auto;
  gap:9px;
  align-items:center;
  padding:10px;
  border:1px solid var(--border);
  border-radius:11px;
  background:rgba(255,255,255,.02);
  min-width:0;
}

.v179-measure-manager-row strong{
  display:block;
  font-size:11px;
}

.v179-measure-manager-values{
  display:flex;
  flex-wrap:wrap;
  gap:5px;
  margin-top:5px;
}

.v179-measure-pill{
  font-size:9px;
  color:var(--muted);
  border:1px solid var(--border);
  border-radius:999px;
  padding:3px 6px;
}

@media(max-width:520px){
  .v179-measure-head-actions{
    width:100%;
    justify-content:space-between;
  }
  .v179-measure-manager-row{
    grid-template-columns:1fr;
  }
  .v179-measure-manager-row>.btn{
    width:100%!important;
  }
}
</style>
"""

js=r"""
<script id="v179CompactMobileFixRuntime">
(function(){
  const VERSION='17.9';

  function wrapTimeV179(input){
    if(!input||input.closest('.v179-time-clip'))return;
    const parent=input.parentElement;
    if(!parent)return;
    parent.style.minWidth='0';
    parent.style.maxWidth='100%';
    parent.style.overflow='hidden';

    const wrap=document.createElement('span');
    wrap.className='v179-time-clip';
    parent.insertBefore(wrap,input);
    wrap.appendChild(input);
  }

  function fixTimeFieldsV179(){
    document.querySelectorAll(
      '#v122CheckTime,#v165Time,.v165-week-row input[type="time"],input[data-v165-time]'
    ).forEach(wrapTimeV179);
  }

  function measureValuesV179(m){
    const specs=[
      ['Peso',m.weight_kg,'kg'],
      ['Cintura',m.waist_cm,'cm'],
      ['Cadera',m.hip_cm,'cm'],
      ['Pecho',m.chest_cm,'cm'],
      ['Brazo',m.arm_left_cm,'cm'],
      ['Muslo',m.thigh_left_cm,'cm']
    ];
    return specs.filter(x=>x[1]!=null&&Number.isFinite(Number(x[1]))).map(x=>
      '<span class="v179-measure-pill">'+esc(x[0])+' '+esc(Number(x[1]).toLocaleString('es-AR',{maximumFractionDigits:1}))+' '+x[2]+'</span>'
    ).join('');
  }

  window.openMeasurementManagerV179=function(){
    const rows=(trackingCache?.measurements||[])
      .slice()
      .filter(x=>x?.id)
      .sort((a,b)=>String(b.measured_on||'').localeCompare(String(a.measured_on||'')));

    if(!rows.length){
      toast('Todavía no hay medidas cargadas');
      return;
    }

    showModal(
      '<div class="modal-head"><div><h3>Editar medidas</h3>'+
      '<div class="muted tiny">Elegí cualquier registro, incluido el inicial, para corregirlo.</div></div>'+
      '<button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="v179-measure-manager">'+
      rows.map(m=>
        '<div class="v179-measure-manager-row"><div><strong>'+esc(fmtDate(m.measured_on))+'</strong>'+
        '<div class="v179-measure-manager-values">'+measureValuesV179(m)+'</div></div>'+
        '<button type="button" class="btn small" onclick="openEditMeasurementV176(\''+esc(m.id)+'\')">Editar</button></div>'
      ).join('')+
      '</div>'
    );
  };

  function enhanceMeasurementCardsV179(){
    document.querySelectorAll('#v93MeasureCompare .v93-compare-head').forEach(head=>{
      if(head.querySelector('.v179-measure-head-actions'))return;
      const date=[...head.children].find(x=>x.classList?.contains('muted'));
      const actions=document.createElement('div');
      actions.className='v179-measure-head-actions';
      if(date)actions.appendChild(date);
      const b=document.createElement('button');
      b.type='button';
      b.className='btn small';
      b.textContent='Editar medidas';
      b.onclick=()=>window.openMeasurementManagerV179();
      actions.appendChild(b);
      head.appendChild(actions);
    });

    const history=document.getElementById('v176MeasurementHistory');
    const title=history?.querySelector('.section-title');
    if(title&&!title.querySelector('.v179-manage-measures')){
      const b=document.createElement('button');
      b.type='button';
      b.className='btn small v179-manage-measures';
      b.textContent='Editar medidas';
      b.onclick=()=>window.openMeasurementManagerV179();
      title.appendChild(b);
    }
  }

  function polishV179(){
    fixTimeFieldsV179();
    enhanceMeasurementCardsV179();
  }

  // Reuse the already-consolidated final render pass instead of adding
  // another render() wrapper.
  const basePostV176=window.__fjzPostRenderV176;
  window.__fjzPostRenderV176=function(){
    const out=basePostV176?.apply(this,arguments);
    polishV179();
    return out;
  };

  // Async tracking history can finish after the main render pass.
  if(typeof window.renderStudentTrackingHistory==='function'){
    const baseStudentHistoryV179=window.renderStudentTrackingHistory;
    window.renderStudentTrackingHistory=function(){
      const out=baseStudentHistoryV179.apply(this,arguments);
      requestAnimationFrame(polishV179);
      return out;
    };
    try{renderStudentTrackingHistory=window.renderStudentTrackingHistory}catch(_e){}
  }

  if(typeof window.renderTrackingCoachLoaded==='function'){
    const baseCoachTrackingV179=window.renderTrackingCoachLoaded;
    window.renderTrackingCoachLoaded=function(){
      const out=baseCoachTrackingV179.apply(this,arguments);
      requestAnimationFrame(polishV179);
      return out;
    };
    try{renderTrackingCoachLoaded=window.renderTrackingCoachLoaded}catch(_e){}
  }

  // When a historical measurement is edited from Progress/Summary, refresh
  // the current screen after the cloud confirms the update.
  if(typeof window.saveMeasurementV176==='function'){
    const baseSaveMeasurementV179=window.saveMeasurementV176;
    window.saveMeasurementV176=async function(){
      const out=await baseSaveMeasurementV179.apply(this,arguments);
      if(out){
        const coachNeedsRefresh=currentProfile?.role==='coach'&&coachTab==='student'&&
          ['progress','summary'].includes(coachStudentTab);
        const studentNeedsRefresh=mode==='student'&&['progress','home'].includes(studentTab);
        if(coachNeedsRefresh||studentNeedsRefresh){
          window.fjzScheduleRenderV125?.();
        }
      }
      return out;
    };
  }

  requestAnimationFrame(polishV179);

  window.__fjzV179={
    version:VERSION,
    compactMobileLayout:true,
    checkinTimeClipped:true,
    legacyEvolutionEditable:true,
    allMeasurementRecordsEditable:true,
    noExtraRenderWrapper:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "v179CompactMobileFixStyles",
  "openMeasurementManagerV179",
  "#v122CheckTime",
  "legacyEvolutionEditable:true",
  "noExtraRenderWrapper:true"
]:
    if marker not in html:
        raise RuntimeError("V17.9 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V17.9 compact mobile/time/measurement editing enabled")
