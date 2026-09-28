import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v152DayDeleteStyles">
.v152-day-delete{
  border-color:rgba(255,82,95,.32)!important;
  color:#ff8a94!important;
  background:rgba(255,82,95,.055)!important
}
.v152-day-delete:hover{background:rgba(255,82,95,.11)!important}
.v152-delete-warning{
  margin-top:12px;padding:12px;border-radius:12px;
  border:1px solid rgba(255,82,95,.22);
  background:rgba(255,82,95,.045)
}
.v152-edit-actions{display:grid;grid-template-columns:1fr;gap:8px;margin-top:14px}
</style>
"""

js=r"""
<script id="v152DayDeleteRuntime">
(function(){
  const VERSION='15.2';

  function canDeleteDayV152(){
    return Array.isArray(student()?.days)&&student().days.length>1;
  }

  window.confirmDeleteDayV152=function(i){
    const s=student(),d=s?.days?.[Number(i)];
    if(!d)return;

    if(!canDeleteDayV152()){
      toast('La rutina debe conservar al menos un día');
      return;
    }

    const exerciseCount=Array.isArray(d.exercises)?d.exercises.length:0;
    showModal(
      '<div class="modal-head"><div><h3>Eliminar día</h3>'+
      '<div class="muted tiny">'+esc(d.name)+'</div></div>'+
      '<button class="btn small" onclick="closeModal()">✕</button></div>'+
      '<div class="v152-delete-warning"><strong>¿Eliminar este día de la rutina?</strong>'+
      '<div class="muted tiny" style="margin-top:6px">'+
      'Se quitarán este día y sus '+exerciseCount+' ejercicio'+(exerciseCount===1?'':'s')+
      ' de la rutina activa. Las sesiones ya guardadas en el historial no se borran.'+
      '</div></div>'+
      '<div class="pill-row" style="justify-content:flex-end;margin-top:14px">'+
      '<button class="btn" onclick="closeModal()">Cancelar</button>'+
      '<button id="v152DeleteDayBtn" class="btn v152-day-delete" onclick="deleteDayV152('+Number(i)+')">Eliminar día</button>'+
      '</div>'
    );
  };

  window.deleteDayV152=function(i){
    const s=student(),idx=Number(i);
    if(!Array.isArray(s?.days)||!s.days[idx]){closeModal();return}
    if(s.days.length<=1){
      toast('La rutina debe conservar al menos un día');
      return;
    }

    const removed=s.days[idx];
    s.days.splice(idx,1);

    if(typeof currentDay!=='undefined'){
      if(currentDay>idx)currentDay--;
      if(currentDay>=s.days.length)currentDay=Math.max(0,s.days.length-1);
    }

    // Historical sessions are intentionally preserved.
    saveState();
    closeModal();
    render();
    toast('Día eliminado: '+removed.name);
  };

  const baseDayEditorV152=dayEditor;
  dayEditor=function(d,i){
    let out=baseDayEditorV152.apply(this,arguments);
    const temp=document.createElement('div');
    temp.innerHTML=out;
    const card=temp.firstElementChild;
    const actions=card?.querySelector('.day-actions');
    if(actions&&!actions.querySelector('.v152-day-delete')){
      const btn=document.createElement('button');
      btn.className='btn small v152-day-delete';
      btn.type='button';
      btn.textContent='Eliminar';
      btn.setAttribute('onclick','confirmDeleteDayV152('+Number(i)+')');
      if(!canDeleteDayV152()){
        btn.disabled=true;
        btn.title='La rutina debe conservar al menos un día';
      }
      actions.appendChild(btn);
    }
    return card?card.outerHTML:out;
  };

  const baseEditDayV152=editDay;
  editDay=function(i){
    const out=baseEditDayV152.apply(this,arguments);
    const modal=el('modal');
    if(!modal||modal.querySelector('#v152EditDeleteDay'))return out;

    const saveBtn=[...modal.querySelectorAll('button')].find(b=>/guardar/i.test(b.textContent||''));
    if(saveBtn){
      const wrap=document.createElement('div');
      wrap.className='v152-edit-actions';
      const del=document.createElement('button');
      del.id='v152EditDeleteDay';
      del.type='button';
      del.className='btn v152-day-delete';
      del.textContent='Eliminar este día';
      del.disabled=!canDeleteDayV152();
      if(del.disabled)del.title='La rutina debe conservar al menos un día';
      del.onclick=()=>confirmDeleteDayV152(Number(i));
      saveBtn.parentNode.insertBefore(wrap,saveBtn);
      wrap.appendChild(saveBtn);
      wrap.appendChild(del);
    }
    return out;
  };

  window.__fjzDayDeleteV152={
    version:VERSION,
    coachOnly:true,
    confirmation:true,
    preservesSessionHistory:true,
    preventsEmptyRoutine:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzDayDeleteV152",
  "confirmDeleteDayV152",
  "deleteDayV152",
  "preservesSessionHistory:true",
  "preventsEmptyRoutine:true"
]:
    if marker not in html:
        raise RuntimeError("V15.2 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V15.2 routine day deletion enabled")
