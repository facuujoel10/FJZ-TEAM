(() => {
 const button=document.createElement('button');
 button.type='button';button.className='btn fjz-activity-launch';
 button.innerHTML='<svg viewBox="0 0 28 28" width="25" height="25" aria-hidden="true" fill="none" stroke-width="3" stroke-linecap="round"><circle cx="14" cy="14" r="10" stroke="#56313d"/><circle cx="14" cy="14" r="10" stroke="#ff4668" stroke-dasharray="49 64" transform="rotate(-90 14 14)"/><circle cx="14" cy="14" r="5" stroke="#f4b865" stroke-dasharray="23 32" transform="rotate(-90 14 14)"/></svg><span>Pasos</span>';button.setAttribute('aria-label','Abrir actividad de pasos');
 document.querySelector('.top-actions')?.prepend(button);
 button.onclick=async()=>{
   const id=trackingAthleteId(),coach=currentProfile?.role==='coach'&&mode==='coach',studentRole=currentProfile?.role==='student';
   if(!id){toast('Seleccioná una ficha vinculada.');return}
   const day=new Intl.DateTimeFormat('sv-SE').format(new Date());
   showModal('<div class="modal-head"><h3>Pasos diarios</h3><button class="btn step-close" type="button" aria-label="Cerrar pasos" onclick="closeModal()">×</button></div><section id="stepPanel" aria-live="polite">Cargando…</section>');
   const panel=document.getElementById('stepPanel');
   const load=async()=>{
     const [target,logs,measurement]=await Promise.all([supabaseClient.from('step_targets').select('target').eq('athlete_id',id).maybeSingle(),supabaseClient.from('daily_steps').select('day,steps').eq('athlete_id',id).order('day',{ascending:false}).limit(7),supabaseClient.from('body_measurements').select('weight_kg').eq('athlete_id',id).lte('measured_on',day).not('weight_kg','is',null).order('measured_on',{ascending:false}).limit(1)]);
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
     const estimate=document.createElement('section');
     estimate.className='step-estimate';
     estimate.innerHTML='<h4>Calorías activas de hoy</h4><p>Estimación para caminata en terreno llano. Medí diez pasos y dividí la distancia por diez.</p><div class="form-grid"><label>Peso (kg)<input class="input" type="number" min="1" step="0.1"></label><label>Longitud de un paso (cm)<input class="input" type="number" min="1" max="200" step="0.1" placeholder="Ej. 70"></label></div><output aria-live="polite"></output>';
     panel.querySelector('.step-hero').after(estimate);
     const [weight,length]=estimate.querySelectorAll('input');
     weight.value=measurement.data?.[0]?.weight_kg||'';
     const lengthKey='fjz-step-length:'+id;
     try{length.value=localStorage.getItem(lengthKey)||''}catch{}
     const output=estimate.querySelector('output');
     const refreshEstimate=()=>{
       const input=studentRole?panel.querySelector('form input'):null;
       const steps=input?.value!=='' && input?input.valueAsNumber:today;
       const kg=weight.valueAsNumber,cm=length.valueAsNumber;
       output.textContent=steps==null?'Sin pasos registrados hoy.':!Number.isFinite(steps)||steps<0?'Revisá los pasos.':
         !(kg>0 && cm>0 && cm<=200)?'Ingresá peso y longitud de paso para estimar.':
         '≈ '+Math.round(0.5*kg*steps*cm/100000).toLocaleString('es-AR')+' kcal activas';
     };
     weight.oninput=refreshEstimate;
     length.oninput=()=>{try{if(length.validity.valid)localStorage.setItem(lengthKey,length.value)}catch{}refreshEstimate()};
     if(studentRole && panel.querySelector('form input'))panel.querySelector('form input').oninput=refreshEstimate;
     refreshEstimate();
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
