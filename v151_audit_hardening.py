import pathlib

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

css=r"""
<style id="v151AuditHardeningStyles">
.v151-inc-caption{display:block}
.v151-audit-note{
  margin-top:12px;padding:10px 12px;border:1px solid var(--border);
  border-radius:12px;background:rgba(255,255,255,.025)
}
.v151-audit-grid{
  display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:8px
}
.v151-audit-grid>div{
  min-width:0;padding:8px 9px;border:1px solid var(--border);
  border-radius:10px;background:rgba(255,255,255,.018)
}
.v151-audit-grid strong{display:block;font-size:11px}
.v151-audit-grid span{display:block;margin-top:2px;font-size:9px;color:var(--muted)}
@media(max-width:520px){.v151-audit-grid{grid-template-columns:1fr}}
</style>
"""

js=r"""
<script id="v151AuditHardeningRuntime">
(function(){
  const VERSION='15.1';
  let savingExerciseV151=false;

  function clampV151(n,min,max,fallback){
    n=Number(n);
    if(!Number.isFinite(n))return fallback;
    return Math.min(max,Math.max(min,n));
  }

  function selectedLoadModeV151(old,name,equipment){
    const fromForm=el('fLoadModeV150')?.value;
    if(['external','bodyweight','weighted','assisted'].includes(fromForm))return fromForm;
    if(['external','bodyweight','weighted','assisted'].includes(old?.loadMode))return old.loadMode;
    if(typeof window.fjzLoadModeV150==='function'){
      return window.fjzLoadModeV150({name:name||old?.name||'',equipment:equipment||old?.equipment||''});
    }
    return 'external';
  }

  // Preserve the actual input node/value when changing load modes.
  // V15.0 rebuilt the increment input with innerHTML, which could restore its old value.
  window.updateLoadModeUIV150=function(){
    const mode=el('fLoadModeV150')?.value||'external';
    const help=el('fLoadHelpV150');
    const inc=el('fInc');
    const incLabel=inc?.closest('label');

    if(help){
      help.textContent=
        mode==='bodyweight'
          ? 'El alumno carga solo repeticiones y RIR. No necesita escribir kilos.'
          : mode==='weighted'
          ? 'El alumno escribe únicamente los kilos agregados como lastre.'
          : mode==='assisted'
          ? 'El alumno escribe los kilos de ayuda. Menos asistencia se interpreta como progreso.'
          : 'Usá este modo para máquinas, barras, mancuernas, poleas y otras cargas externas.';
    }

    if(incLabel&&inc){
      let caption=incLabel.querySelector('.v151-inc-caption');
      if(!caption){
        [...incLabel.childNodes].forEach(node=>{
          if(node.nodeType===Node.TEXT_NODE)node.remove();
        });
        caption=document.createElement('span');
        caption.className='v151-inc-caption';
        incLabel.insertBefore(caption,inc);
      }
      caption.textContent=
        mode==='assisted'?'Paso de asistencia (kg)':
        mode==='weighted'?'Incremento de lastre (kg)':
        'Incremento kg';
      incLabel.style.display=mode==='bodyweight'?'none':'';
    }
  };

  // Canonical one-pass exercise save.
  // Keeps every field from exact reps, training methods and load modes,
  // but performs only one state write + one render.
  window.saveExercise=function(di,ei,exUid,libId,muscle,equipment){
    if(savingExerciseV151)return;
    const s=student?.(),day=s?.days?.[Number(di)];
    if(!day){toast('No encuentro el día de entrenamiento');return}

    const old=ei==null?null:day.exercises?.[Number(ei)];
    const repMode=el('fRepMode')?.value||old?.repMode||'range';
    let exact=repMode==='exact'&&typeof window.parseExactRepsV104==='function'
      ? window.parseExactRepsV104(el('fExactReps')?.value||'')
      : [];

    if(repMode==='exact'&&!exact.length){
      toast('Escribí las repeticiones exactas, por ejemplo 12-10-8-8');
      return;
    }

    let sets=clampV151(el('fSets')?.value,1,10,old?.sets||3);
    let min=clampV151(el('fMin')?.value,1,100,old?.min||8);
    let max=clampV151(el('fMax')?.value,1,100,old?.max||12);
    if(repMode==='exact'){
      sets=exact.length;
      min=Math.min(...exact);
      max=Math.max(...exact);
    }else if(min>max){
      [min,max]=[max,min];
    }

    let rirMin=clampV151(el('fRMin')?.value,0,10,old?.rirMin??1);
    let rirMax=clampV151(el('fRMax')?.value,0,10,old?.rirMax??2);
    if(rirMin>rirMax)[rirMin,rirMax]=[rirMax,rirMin];

    const name=(el('fName')?.value||'').trim()||'Ejercicio';
    const loadMode=selectedLoadModeV151(old,name,equipment);
    const method=el('fMethodV137')?.value||el('fMethod')?.value||old?.method||'normal';
    const methodNote=String(
      el('fMethodNoteV137')?.value ??
      el('fMethodNote')?.value ??
      old?.methodNote ??
      ''
    ).trim();
    const methodApply=el('fMethodApplyV137')?.value||old?.methodApply||'last';

    const data={
      ...(old||{}),
      uid:old?.uid||exUid||uid('e'),
      libId:libId||old?.libId||'custom',
      name,
      muscle:muscle||old?.muscle||'Personalizado',
      equipment:equipment||old?.equipment||'Otro',
      sets,min,max,rirMin,rirMax,
      rest:clampV151(el('fRest')?.value,15,900,old?.rest||120),
      cue:(el('fCue')?.value||'').trim(),
      increment:(()=>{const raw=Number(el('fInc')?.value);if(Number.isFinite(raw))return Math.max(0,raw);const prev=Number(old?.increment);return Number.isFinite(prev)?Math.max(0,prev):2.5})(),
      method,
      methodNote,
      methodApply,
      repMode,
      repsExact:repMode==='exact'?exact:[],
      loadMode,
      history:old?.history||[],
      override:old?.override||null
    };

    savingExerciseV151=true;
    try{
      if(ei==null)day.exercises.push(data);
      else day.exercises[Number(ei)]=data;
      saveState();
      closeModal();
      render();
      toast('Rutina actualizada');
    }finally{
      queueMicrotask(()=>{savingExerciseV151=false});
    }
  };

  window.__fjzAuditV151={
    version:VERSION,
    singleExerciseSave:true,
    loadModeInputPreserved:true,
    rlsOptimized:true,
    getStatus(){
      const qa=window.__fjzInteractionQA||{};
      const rt=window.__fjzRealtimeV132||{};
      const rs=window.__fjzRenderStabilityV146||{};
      return {
        release:window.__FJZ_RELEASE__||VERSION,
        runtimeErrors:Number(qa.errors)||0,
        rejectedPromises:Number(qa.rejections)||0,
        realtime:rt.status||'unknown',
        pendingSync:!!localStorage.getItem('fjz_v112_pending_sync'),
        channels:typeof supabaseClient?.getChannels==='function'?supabaseClient.getChannels().length:null,
        lastRenderMs:rs.lastRenderMs??null,
        renderCount:rs.renderCount??null
      };
    }
  };

  // Add runtime health to the existing system modal without changing its flow.
  if(typeof window.showSystemStatusV80==='function'){
    const baseShowSystemStatusV151=window.showSystemStatusV80;
    window.showSystemStatusV80=async function(){
      const out=await baseShowSystemStatusV151.apply(this,arguments);
      const body=el('v80SystemBody');
      if(body&&!el('v151RuntimeAudit')){
        const st=window.__fjzAuditV151.getStatus();
        const box=document.createElement('div');
        box.id='v151RuntimeAudit';
        box.className='v151-audit-note';
        box.innerHTML=
          '<strong>Salud de la app</strong>'+
          '<div class="v151-audit-grid">'+
          '<div><strong>'+esc(String(st.runtimeErrors))+'</strong><span>Errores JS capturados</span></div>'+
          '<div><strong>'+esc(String(st.rejectedPromises))+'</strong><span>Promesas rechazadas</span></div>'+
          '<div><strong>'+esc(String(st.realtime))+'</strong><span>Realtime</span></div>'+
          '<div><strong>'+(st.pendingSync?'Sí':'No')+'</strong><span>Sync pendiente</span></div>'+
          '</div>';
        body.appendChild(box);
      }
      return out;
    };
  }
})();
</script>
"""

html=html.replace("</head>",css+"\n</head>",1)
html=html.replace("</body>",js+"\n</body>",1)

for marker in [
  "__fjzAuditV151",
  "singleExerciseSave:true",
  "loadModeInputPreserved:true",
  "rlsOptimized:true",
  "v151RuntimeAudit"
]:
    if marker not in html:
        raise RuntimeError("V15.1 missing audit marker: "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V15.1 audit hardening enabled")
