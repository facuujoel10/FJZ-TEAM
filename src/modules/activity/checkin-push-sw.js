self.addEventListener('push', event => {
  let data;
  try { data=event.data.json(); } catch { return; }
  if(!['weekly','monthly'].includes(data.kind))return;
  const weekly=data.kind==='weekly';
  event.waitUntil(self.registration.showNotification('TEAM FJZ', {
    body:weekly?'Ya podés completar tu check-in semanal de sueño y estrés.':'Tenés programado tu chequeo mensual de medidas.',
    tag:'fjz-'+data.kind+'-'+data.period, silent:true,
    icon:'./icon-192-v133.png',data:{kind:data.kind}
  }));
});
self.addEventListener('notificationclick',event=>{
  event.notification.close();
  const kind=event.notification.data?.kind;
  if(['weekly','monthly'].includes(kind))event.waitUntil(clients.openWindow('./?checkin='+kind));
});
