(()=>{
 const launch=document.createElement('button');
 launch.className='btn small'; launch.textContent='Recordatorios'; launch.type='button';
 document.querySelector('.top-actions')?.append(launch);
 launch.onclick=async()=>{
   const athlete=trackingAthleteId(), coach=currentProfile?.role==='coach' && mode==='coach';
   if(!athlete || (!coach && currentProfile?.role!=='student'))return toast('Abrí una ficha desde tu panel.');
   showModal('<div class="modal-head"><h3>Recordatorios de check-in</h3><button class="btn" onclick="closeModal()" aria-label="Cerrar">×</button></div><section id="fjzReminders">Cargando…</section>');
   const host=document.getElementById('fjzReminders');
   const labels={weekly:'Semanal · Sueño y estrés',monthly:'Mensual · Peso y medidas'};
   try{
     const {data,error}=await supabaseClient.from('checkin_reminder_rules').select('*').eq('athlete_id',athlete);
     if(error)throw error;
     host.replaceChildren();
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
 const kind=new URL(location.href).searchParams.get('checkin');
 if(['weekly','monthly'].includes(kind)){
   let remaining=40;
   const open=()=>{
     if(typeof currentProfile==='undefined'||!currentProfile||!trackingAthleteId()){
       if(--remaining>0)setTimeout(open,500);
       return;
     }
     if(currentProfile.role!=='student')return;
     studentTab='tracking';render();
     const url=new URL(location.href);url.searchParams.delete('checkin');history.replaceState(null,'',url);
   };
   open();
 }
})();
