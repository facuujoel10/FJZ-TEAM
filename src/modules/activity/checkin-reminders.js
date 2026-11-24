(()=>{
 const launch=document.createElement('button');
 launch.id='fjzNoticeCenter';launch.className='btn small'; launch.textContent='Avisos'; launch.type='button';
 document.querySelector('.top-actions')?.append(launch);
 launch.onclick=async()=>{
   const athlete=trackingAthleteId(), coach=currentProfile?.role==='coach' && mode==='coach';
   if(!athlete || (!coach && currentProfile?.role!=='student'))return toast('Abrí una ficha desde tu panel.');
   showModal('<div class="modal-head"><h3>Avisos y recordatorios</h3><button class="btn" onclick="closeModal()" aria-label="Cerrar">×</button></div><section id="fjzReminders">Cargando…</section>');
   const host=document.getElementById('fjzReminders');
   const labels={weekly:'Semanal · Sueño y estrés',monthly:'Mensual · Peso y medidas'};
   try{
     const {data,error}=await supabaseClient.from('checkin_reminder_rules').select('*').eq('athlete_id',athlete);
     if(error)throw error;
     host.replaceChildren();
     const inbox=document.createElement('section');inbox.className='card';
     host.append(inbox);
     const history=document.createElement('div');
     const heading=document.createElement('h4');heading.textContent=coach?'Mensajes al alumno':'Mensajes de Facu';inbox.append(heading,history);
     const columns='id,body,created_at';
     const draw=async()=>{
       const rows=await supabaseClient.from('coach_messages').select(columns).eq('athlete_id',athlete).order('created_at',{ascending:false}).limit(30);
       if(rows.error){history.textContent='No se pudieron cargar los mensajes.';return}
       history.replaceChildren();
       if(!rows.data.length)history.textContent='Todavía no hay mensajes.';
       for(const row of rows.data){
         const article=document.createElement('article'),when=document.createElement('small'),body=document.createElement('p');
         when.textContent=new Date(row.created_at).toLocaleString('es-AR');body.textContent=row.body;
         article.append(when,body);history.append(article);
       }
     };
     if(coach){
       const recipient=await supabaseClient.from('athletes').select('user_id').eq('id',athlete).single();
       if(recipient.error)throw recipient.error;
       const form=document.createElement('form');
       form.innerHTML='<label>Mensaje privado<textarea class="input" maxlength="1500" required></textarea></label><button class="btn primary">Enviar mensaje</button><p role="status"></p>';
       inbox.insertBefore(form,history);
       const field=form.querySelector('textarea'),button=form.querySelector('button'),status=form.querySelector('p');
       let id=crypto.randomUUID();
       if(!recipient.data.user_id){button.disabled=true;status.textContent='El alumno necesita una cuenta vinculada.'}
       form.onsubmit=async e=>{
         e.preventDefault();const body=field.value.trim();if(!body)return;
         button.disabled=true;field.disabled=true;
         try{
           const saved=await supabaseClient.from('coach_messages').insert({id,athlete_id:athlete,recipient_id:recipient.data.user_id,body}).select(columns).single();
           if(saved.error){
             const prior=await supabaseClient.from('coach_messages').select(columns).eq('id',id).maybeSingle();
             if(prior.data?.body!==body)throw saved.error;
           }
           id=crypto.randomUUID();field.value='';status.textContent='Mensaje guardado en la bandeja del alumno.';await draw();
         }catch{status.textContent='No se pudo confirmar el envío.'}
         finally{button.disabled=false;field.disabled=false}
       };
     }
     await draw();
     for(const [kind,title] of Object.entries(labels)){
       const rule=data.find(r=>r.kind===kind);
       const form=document.createElement('form');form.className='card';
       form.innerHTML='<h4>'+title+'</h4>';
       host.append(form);
       if(!coach){form.append(rule?.enabled?'Programado · '+rule.local_time.slice(0,5)+' (Argentina)':'Apagado');continue}
       form.insertAdjacentHTML('beforeend','<label><input type="checkbox"> Enviar recordatorio</label><div class="form-grid"><label>Primera fecha<input class="input" type="date" required></label><label>Hora argentina<input class="input" type="time" min="08:00" max="20:00" required></label></div><button class="btn">Guardar</button> <small role="status"></small>');
       const [on,date,time]=form.querySelectorAll('input');
       on.checked=Boolean(rule?.enabled);date.value=rule?.first_day||new Intl.DateTimeFormat('sv-SE',{timeZone:'America/Argentina/Buenos_Aires'}).format(new Date());
       time.value=rule?.local_time?.slice(0,5)||'10:00';
       form.onsubmit=async e=>{
         e.preventDefault();const b=form.querySelector('button'),status=form.querySelector('small');b.disabled=true;
         try{const res=await supabaseClient.from('checkin_reminder_rules').upsert({athlete_id:athlete,kind,first_day:date.value,local_time:time.value,enabled:on.checked}).select().single();if(res.error)throw res.error;
           status.textContent=on.checked?'Programado':'Apagado';
         }catch{status.textContent='No se pudo guardar.'}finally{b.disabled=false}
       };
     }
     if(coach)return;
     if(!('PushManager' in window)||!('serviceWorker' in navigator)||!window.Notification){host.append('En iPhone, abrí TEAM FJZ desde la pantalla de inicio.');return}
     const registration=await navigator.serviceWorker.getRegistration();
     if(!registration?.active || !fjzPushPublicKey){host.append('Las notificaciones todavía no están disponibles.');return}
     const existing=await registration.pushManager.getSubscription();
     const device=await supabaseClient.from('checkin_push_devices').select('endpoint').eq('athlete_id',athlete).maybeSingle();
     if(device.error)throw device.error;
     const active=Boolean(existing && device.data?.endpoint===existing.endpoint);
     const toggle=document.createElement('button');toggle.className='btn';host.append(toggle);
     toggle.textContent=active?'Desactivar en este celular':'Activar en este celular';
     const status=document.createElement('p');status.setAttribute('role','status');host.append(status);
     toggle.onclick=async()=>{
       toggle.disabled=true;
       try{
         if(active){
           const result=await supabaseClient.from('checkin_push_devices').delete().eq('athlete_id',athlete).eq('endpoint',existing.endpoint);
           if(result.error)throw result.error;
           await existing.unsubscribe();
         }else{
           if(await Notification.requestPermission()!=='granted'){status.textContent='Los avisos siguen apagados.';return}
           const sub=existing||await registration.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:fjzPushPublicKey});
           const {endpoint,keys}=sub.toJSON();
           const result=await supabaseClient.from('checkin_push_devices').upsert({athlete_id:athlete,endpoint,p256dh:keys.p256dh,auth_key:keys.auth}).select('athlete_id').single();
           if(result.error)throw result.error;
         }
         await launch.onclick();
       }catch{status.textContent='No se pudo confirmar el cambio.'}finally{toggle.disabled=false}
     };
   }catch{host.textContent='No se pudieron cargar los recordatorios.'}
 };
})();
