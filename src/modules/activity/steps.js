(() => {
 const button=document.createElement('button');
 button.type='button';button.className='btn small';button.textContent='◉  Pasos';button.setAttribute('aria-label','Abrir actividad de pasos');
 document.querySelector('.top-actions')?.prepend(button);
 button.onclick=async()=>{
   const id=trackingAthleteId(),coach=currentProfile?.role==='coach'&&mode==='coach',studentRole=currentProfile?.role==='student';
   if(!id){toast('Seleccioná una ficha vinculada.');return}
   const day=new Intl.DateTimeFormat('sv-SE').format(new Date());
   showModal('<div class="modal-head"><h3>Pasos diarios</h3><button class="btn step-close" type="button" aria-label="Cerrar pasos" onclick="closeModal()">×</button></div><section id="stepPanel" aria-live="polite">Cargando…</section>');
   const panel=document.getElementById('stepPanel');
   const load=async()=>{
     const [target,logs]=await Promise.all([supabaseClient.from('step_targets').select('target').eq('athlete_id',id).maybeSingle(),supabaseClient.from('daily_steps').select('day,steps').eq('athlete_id',id).order('day',{ascending:false}).limit(7)]);
     if(target.error||logs.error){panel.textContent='No se pudieron cargar los pasos.';return}
     const today=logs.data.find(r=>r.day===day)?.steps;
     const goal=target.data?.target,format=value=>Number(value).toLocaleString('es-AR');
     const percent=goal && today!=null?Math.round(today/goal*100):null;
     const week=Array.from({length:7},(_,i)=>{
       const date=new Date();date.setDate(date.getDate()-6+i);
       const key=new Intl.DateTimeFormat('sv-SE').format(date);
       return {label:date.toLocaleDateString('es-AR',{weekday:'short'}),steps:logs.data.find(row=>row.day===key)?.steps};
     });
     const highest=Math.max(1,...week.map(row=>row.steps||0));
     panel.innerHTML='<div class="step-hero"><div class="step-ring" style="--angle:'+Math.min(percent||0,100)*3.6+'deg"><span>'+(percent==null?'—':format(percent)+'%')+'</span></div><div><small>Pasos de hoy</small><strong>'+(today==null?'Sin registro':format(today))+'</strong><span>'+(goal?'Meta · '+format(goal)+' pasos':'Sin meta asignada')+'</span></div></div>'+
       '<h4>Últimos 7 días</h4><div class="step-week">'+week.map(row=>'<div><small>'+(row.steps==null?'—':format(row.steps))+'</small><i style="--height:'+Math.round((row.steps||0)/highest*100)+'%"></i><span>'+row.label+'</span></div>').join('')+'</div>'+
       (coach||studentRole?'<form><label>'+(coach?'Objetivo de pasos diarios':'Pasos de hoy según tu celular o reloj')+'<input class="input" type="number" required step="1" min="'+(coach?1:0)+'" max="150000" value="'+(coach?target.data?.target??'':today??'')+'"></label><button class="btn primary">Guardar</button></form>':'')+
       '<p role="status"></p>';
     const form=panel.querySelector('form');
     if(form)form.onsubmit=async e=>{
       e.preventDefault();const save=form.querySelector('button');save.disabled=true;
       try{
         const value=form.querySelector('input').valueAsNumber;
         const result=await supabaseClient.from(coach?'step_targets':'daily_steps').upsert(coach?{athlete_id:id,target:value}:{athlete_id:id,day,steps:value},{onConflict:coach?'athlete_id':'athlete_id,day'}).select().single();
         if(result.error)throw result.error;await load();panel.querySelector('[role=status]').textContent='Guardado';
       }catch{panel.querySelector('[role=status]').textContent='No se pudo confirmar el guardado.';save.disabled=false}
     };
   };await load();
 };
})();
