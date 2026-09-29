import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v166ExplicitDateReminderStyles">
.v166-type-switch{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:8px;
  margin-bottom:12px
}
.v166-type-btn{
  min-height:42px;
  border:1px solid var(--border);
  border-radius:11px;
  background:rgba(255,255,255,.025);
  color:var(--text);
  font-weight:800;
  cursor:pointer
}
.v166-type-btn.active{
  border-color:rgba(255,31,47,.5);
  background:rgba(255,31,47,.08);
  color:#fff
}
.v166-date-panel,
.v166-weekly-panel{
  padding:11px;
  border:1px solid var(--border);
  border-radius:12px;
  background:rgba(255,255,255,.02);
  margin-bottom:10px
}
.v166-date-panel label,
.v166-weekly-panel label{
  display:block
}
.v166-date-panel input,
.v166-weekly-panel select{
  width:100%!important
}
.v166-date-hint{
  margin-top:5px;
  font-size:9px;
  color:var(--muted)
}
@media(max-width:520px){
  .v166-type-switch{grid-template-columns:1fr}
}
</style>
"""

js=r"""
<script id="v166ExplicitDateReminderRuntime">
(function(){
  const VERSION='16.6';
  let modeV166='once';

  function setModeV166(mode){
    modeV166=mode==='weekly'?'weekly':'once';
    document.querySelectorAll('.v166-type-btn').forEach(b=>{
      b.classList.toggle('active',b.dataset.mode===modeV166);
    });
    const datePanel=el('v166DatePanel');
    const weeklyPanel=el('v166WeeklyPanel');
    if(datePanel)datePanel.style.display=modeV166==='once'?'block':'none';
    if(weeklyPanel)weeklyPanel.style.display=modeV166==='weekly'?'block':'none';
    const hidden=el('v165Type');
    if(hidden)hidden.value=modeV166;
  }

  function openReminderModalV166(){
    modeV166='once';
    showModal(
      '<div class="modal-head"><div><h3>Nuevo recordatorio</h3>'+
      '<div class="muted tiny">'+esc(student()?.name||'Alumno')+'</div></div>'+
      '<button class="btn small" type="button" onclick="closeModal()">✕</button></div>'+
      '<div class="v166-type-switch">'+
        '<button type="button" class="v166-type-btn active" data-mode="once">Por fecha</button>'+
        '<button type="button" class="v166-type-btn" data-mode="weekly">Semanal</button>'+
      '</div>'+
      '<input id="v165Type" type="hidden" value="once">'+
      '<div class="form-grid">'+
        '<label class="tiny muted span2">Título *<input id="v165Title" class="input" maxlength="80" placeholder="Ej: Completar check-in"></label>'+
        '<label class="tiny muted span2">Mensaje<textarea id="v165Body" class="input" rows="3" maxlength="400" placeholder="Mensaje breve"></textarea></label>'+
        '<div id="v166DatePanel" class="v166-date-panel span2">'+
          '<label class="tiny muted">Fecha del recordatorio *<input id="v165Date" class="input" type="date" min="'+dateInputToday()+'" value="'+dateInputToday()+'"></label>'+
          '<div class="v166-date-hint">Elegí el día exacto en que querés que aparezca.</div>'+
        '</div>'+
        '<div id="v166WeeklyPanel" class="v166-weekly-panel span2" style="display:none">'+
          '<label class="tiny muted">Día de la semana *<select id="v165Weekday" class="input">'+
            WEEK_NAMES_V81.map((x,i)=>'<option value="'+i+'">'+esc(x)+'</option>').join('')+
          '</select></label>'+
          '<div class="v166-date-hint">Se repetirá todas las semanas ese día.</div>'+
        '</div>'+
        '<label class="tiny muted span2">Hora opcional<input id="v165Time" class="input" type="time"></label>'+
      '</div>'+
      '<div id="v165Error" class="v165-form-error"></div>'+
      '<button class="btn primary" type="button" style="width:100%;margin-top:12px" data-v165-action="save-reminder">Guardar recordatorio</button>'+
      '<div id="v165ReminderState" class="v165-save-state"></div>'
    );

    document.querySelectorAll('.v166-type-btn').forEach(btn=>{
      btn.addEventListener('click',()=>{
        setModeV166(btn.dataset.mode);
      });
    });
    setModeV166('once');
    setTimeout(()=>el('v165Title')?.focus(),50);
  }

  // Preserve the verified V16.5 save path; only make the selected mode explicit.
  const baseSaveReminderV166=window.saveReminderV81;
  async function saveReminderV166(){
    const hidden=el('v165Type');
    if(hidden)hidden.value=modeV166;
    return baseSaveReminderV166.apply(this,arguments);
  }

  window.openAddReminderV81=openReminderModalV166;
  window.saveReminderV81=saveReminderV166;

  // V16.5 uses delegated actions that close over its local functions.
  // Capture those clicks first so the visible V16.6 controls always use V16.6.
  if(!window.__fjzAgendaV166Delegated){
    window.__fjzAgendaV166Delegated=true;
    document.addEventListener('click',e=>{
      const btn=e.target?.closest?.('[data-v165-action]');
      if(!btn)return;
      const action=btn.getAttribute('data-v165-action');
      if(action==='add-reminder'){
        e.preventDefault();e.stopImmediatePropagation();
        openReminderModalV166();
      }else if(action==='save-reminder'){
        e.preventDefault();e.stopImmediatePropagation();
        saveReminderV166();
      }
    },true);
  }

  window.__fjzAgendaV166={
    version:VERSION,
    dateModeVisibleByDefault:true,
    explicitDatePicker:true,
    weeklyAsSecondMode:true,
    verifiedSavePathPreserved:true
  };
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzAgendaV166",
  "dateModeVisibleByDefault:true",
  "explicitDatePicker:true",
  "weeklyAsSecondMode:true",
  "verifiedSavePathPreserved:true"
]:
    if marker not in html:
        raise RuntimeError("V16.6 missing marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V16.6 explicit date reminder mode enabled")
