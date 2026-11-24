const fjzNoticeCopy = {
 weekly:['Check-in semanal','Ya podés registrar cómo dormiste y cómo venís de estrés y energía.'],
 monthly:['Chequeo mensual','Hoy toca actualizar tu peso y tus medidas.'],
 message:['Mensaje de Facu','Tenés un mensaje de tu coach. Tocá para leerlo.']
};
self.addEventListener('push',event=>{
 let notice;
 try { notice=event.data.json(); } catch { return; }
 if(!notice || !Object.hasOwn(fjzNoticeCopy,notice.kind))return;
 const [title,body]=fjzNoticeCopy[notice.kind];
 event.waitUntil(self.registration.showNotification('TEAM FJZ · '+title,{
   body,tag:'fjz-'+notice.kind+'-'+notice.period,silent:true,
   icon:'./icon-192-v133.png',data:{kind:notice.kind}
 }));
});
self.addEventListener('notificationclick',event=>{
 event.notification.close();
 const kind=event.notification.data?.kind;
 if(Object.hasOwn(fjzNoticeCopy,kind))event.waitUntil(clients.openWindow('./?checkin='+kind));
});
