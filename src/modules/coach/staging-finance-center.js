
(function(root){
  'use strict';
  const nowLocal=()=>new Intl.DateTimeFormat('sv-SE',{timeZone:'America/Argentina/Buenos_Aires',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
  const ui={month:nowLocal().slice(0,7),tab:'overview',scope:'all',entries:[],budgets:[],payments:[],athletes:[],loading:false,loaded:false,error:'',busy:false,owner:'',editId:''};
  const q=(v)=>String(v??'').trim();
  const esc=(v)=>q(v).replace(/[&<>"']/g,(ch)=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const n=(v)=>Number(v)||0;
  const ar=(v)=>new Intl.NumberFormat('es-AR',{style:'currency',currency:'ARS',maximumFractionDigits:0}).format(n(v));
  const dateAR=(v)=>{const p=q(v).slice(0,10).split('-');return p.length===3?p.reverse().join('/'):q(v)||'—'};
  function ctx(){try{return root.__fjzCoachContextV22?.()||null}catch(_e){return null}}
  function allowed(){const c=ctx();return c?.profile?.role==='coach'&&c?.mode==='coach'&&c?.coachTab==='payments'}
  function opt(value,label,selected){return '<option value="'+esc(value)+'"'+(q(value)===q(selected)?' selected':'')+'>'+esc(label)+'</option>'}
  const within=(date)=>q(date).startsWith(ui.month);
  const entriesMonth=()=>ui.entries.filter(x=>within(x.occurred_on));
  const paidMonth=()=>ui.payments.filter(x=>x.status==='paid'&&within(x.paid_on));
  const openDues=()=>ui.payments.filter(x=>x.status==='pending');
  const by=(items,fn)=>items.reduce((sum,x)=>sum+n(fn(x)),0);
  function totals(){
    const e=entriesMonth(),income=(scope)=>by(e.filter(x=>x.scope===scope&&x.kind==='income'),x=>x.amount),expense=(scope)=>by(e.filter(x=>x.scope===scope&&x.kind==='expense'),x=>x.amount);
    const tuition=by(paidMonth(),x=>x.amount);
    return {tuition,unpaid:by(openDues(),x=>x.amount),personalIncome:income('personal'),personalExpense:expense('personal'),businessIncome:income('business'),businessExpense:expense('business'),paid:paidMonth().length,pending:openDues().length};
  }
  function moneyStat(label,value,description,kind){
    return '<div class="fjzfin-stat '+(kind||'')+'"><span>'+esc(label)+'</span><strong>'+ar(value)+'</strong><small>'+esc(description)+'</small></div>';
  }
  function pill(label,value){
    return '<span class="fjzfin-pill"><strong>'+esc(label)+'</strong> '+esc(value)+'</span>';
  }
  function monthTitle(){
    const parts=ui.month.split('-');return new Intl.DateTimeFormat('es-AR',{month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(Number(parts[0]),Number(parts[1])-1,1));
  }
  function empty(title,desc){
    return '<div class="fjzfin-empty"><strong>'+esc(title)+'</strong><p>'+esc(desc)+'</p></div>';
  }
  function paymentRow(x){
    const athlete=ui.athletes.find(a=>a.id===x.athlete_id),paid=x.status==='paid',overdue=!paid&&q(x.due_date)<nowLocal(),status=paid?'Cobrado':overdue?'Vencido':'Pendiente';
    return '<tr><td><strong>'+esc(athlete?.name||'Alumno')+'</strong><small>'+esc(x.note||'Cuota de alumno')+'</small></td><td>'+dateAR(x.due_date)+'</td><td>'+ar(x.amount)+'</td><td><span class="fjzfin-status '+(paid?'paid':overdue?'late':'pending')+'">'+status+'</span></td><td>'+
      (paid?'<small>'+dateAR(x.paid_on)+'</small>':'<div class="fjzfin-inline"><select aria-label="Método de cobro" data-fin-method="'+esc(x.id)+'">'+opt('transfer','Transferencia','transfer')+opt('cash','Efectivo','transfer')+opt('other','Otro','transfer')+'</select><button type="button" data-fin-action="paid" data-id="'+esc(x.id)+'">Marcar cobrado</button></div>')+'</td></tr>';
  }
  function duePanel(){
    const students=ui.athletes.map(a=>opt(a.id,a.name,'')).join('');
    const sorted=[...ui.payments].sort((a,b)=>q(b.due_date).localeCompare(q(a.due_date)));
    return '<div class="fjzfin-two"><section class="fjzfin-card"><div class="fjzfin-head"><div><span class="fjzfin-kicker">CUOTAS</span><h3>Nueva cobranza</h3><p>Vinculada al alumno; no se duplica en movimientos.</p></div></div>'+
      '<form class="fjzfin-form" data-fin-form="due"><label>Alumno<select name="athlete_id" required><option value="">Seleccionar alumno</option>'+students+'</select></label><label>Importe (ARS)<input name="amount" type="number" min="0.01" step="0.01" required placeholder="Ej: 60000"></label><label>Vencimiento<input type="date" name="due_date" required value="'+nowLocal()+'"></label><label>Concepto<input name="note" maxlength="200" placeholder="Ej: mensualidad noviembre"></label><button class="fjzfin-primary" type="submit"'+(ui.busy?' disabled':'')+'>Guardar cuota</button></form></section>'+
      '<section class="fjzfin-card"><div class="fjzfin-head"><div><span class="fjzfin-kicker">SEGUIMIENTO</span><h3>Estado de cobros</h3><p>Marcá los pagos confirmados cuando recibas el dinero.</p></div></div><div class="fjzfin-mini">'+pill('Pendientes',openDues().length)+pill('Cobradas este mes',paidMonth().length)+'</div>'+empty('Sin conexión bancaria','Los cobros se confirman manualmente y quedan asociados a la ficha del alumno.')+'</section></div>'+
      '<section class="fjzfin-card"><div class="fjzfin-head"><div><span class="fjzfin-kicker">HISTORIAL</span><h3>Cuotas y vencimientos</h3></div></div>'+table('<th>Alumno</th><th>Vencimiento</th><th>Importe</th><th>Estado</th><th>Acción</th>',sorted.map(paymentRow).join(''),5)+'</section>';
  }
  function table(head,rows,colspan){
    return rows?'<div class="fjzfin-table-wrap"><table class="fjzfin-table"><thead><tr>'+head+'</tr></thead><tbody>'+rows+'</tbody></table></div>':empty('Sin registros','Todavía no hay movimientos guardados para mostrar.');
  }
  function entryRow(x){
    const pos=x.kind==='income',sign=pos?'+':'−';
    return '<tr><td><strong>'+dateAR(x.occurred_on)+'</strong><small>'+esc(x.description||'Sin descripción')+'</small></td><td>'+esc(x.scope==='personal'?'Personal':'Negocio')+'</td><td>'+esc(x.category)+'</td><td>'+esc(x.account)+'</td><td class="'+(pos?'fjzfin-positive':'fjzfin-negative')+'">'+sign+' '+ar(x.amount)+'</td><td><div class="fjzfin-inline"><button type="button" data-fin-action="edit" data-id="'+esc(x.id)+'">Editar</button><button type="button" class="fjzfin-danger" data-fin-action="delete" data-id="'+esc(x.id)+'">Eliminar</button></div></td></tr>';
  }
  function movements(){
    const current=ui.entries.find(x=>x.id===ui.editId)||{},date=current.occurred_on||nowLocal(),sc=current.scope||'personal',kind=current.kind||'expense';
    const records=entriesMonth().filter(x=>ui.scope==='all'||x.scope===ui.scope).sort((a,b)=>q(b.occurred_on).localeCompare(q(a.occurred_on)));
    return '<div class="fjzfin-two"><section class="fjzfin-card"><div class="fjzfin-head"><div><span class="fjzfin-kicker">REGISTRO PRIVADO</span><h3>'+(ui.editId?'Editar movimiento':'Nuevo movimiento')+'</h3><p>Ingresos y gastos personales o del negocio, separados de las cuotas.</p></div></div>'+
      '<form class="fjzfin-form" data-fin-form="entry"><label>Ámbito<select name="scope">'+opt('personal','Personal',sc)+opt('business','Negocio',sc)+'</select></label><label>Tipo<select name="kind">'+opt('expense','Gasto',kind)+opt('income','Ingreso',kind)+'</select></label><label>Categoría<input name="category" required maxlength="80" list="fjzfinCategories" value="'+esc(current.category||'')+'" placeholder="Ej: Comida, gimnasio, alquiler"></label>'+
      '<datalist id="fjzfinCategories"><option value="Alimentación"><option value="Vivienda"><option value="Transporte"><option value="Salud"><option value="Servicios"><option value="Marketing"><option value="Equipamiento"><option value="Formación"><option value="Otros"></datalist>'+
      '<label>Importe (ARS)<input name="amount" type="number" min="0.01" step="0.01" required value="'+esc(current.amount??'')+'"></label><label>Fecha<input type="date" name="occurred_on" required value="'+esc(date)+'"></label><label>Cuenta / medio<input name="account" maxlength="80" required value="'+esc(current.account||'Efectivo')+'" placeholder="Ej: Efectivo o banco"></label><label class="full">Descripción<input name="description" maxlength="500" value="'+esc(current.description||'')+'" placeholder="Detalle del movimiento"></label>'+
      '<div class="fjzfin-form-actions"><button type="submit" class="fjzfin-primary"'+(ui.busy?' disabled':'')+'>'+(ui.editId?'Guardar edición':'Guardar movimiento')+'</button>'+(ui.editId?'<button type="button" data-fin-action="cancel-edit">Cancelar</button>':'')+'</div></form></section>'+
      '<section class="fjzfin-card"><div class="fjzfin-head"><div><span class="fjzfin-kicker">BUENA PRÁCTICA</span><h3>Separación de cuentas</h3><p>Las cuotas cobradas aparecen automáticamente en los ingresos del negocio. No las vuelvas a cargar como ingresos manuales.</p></div></div>'+
      '<div class="fjzfin-note">Este registro no está conectado a tu banco. Los saldos reflejan los movimientos que cargues y no saldos bancarios verificados.</div></section></div>'+
      '<section class="fjzfin-card"><div class="fjzfin-head"><div><span class="fjzfin-kicker">MOVIMIENTOS</span><h3>'+esc(monthTitle())+'</h3></div><select id="fjzfinScope" aria-label="Filtrar ámbito">'+opt('all','Todo',ui.scope)+opt('personal','Personal',ui.scope)+opt('business','Negocio',ui.scope)+'</select></div>'+
      table('<th>Fecha / detalle</th><th>Ámbito</th><th>Categoría</th><th>Cuenta</th><th>Importe</th><th>Acciones</th>',records.map(entryRow).join(''),6)+'</section>';
  }
  function budgetView(){
    const existing=ui.budgets.filter(x=>within(x.month+'')).sort((a,b)=>q(a.scope+a.category).localeCompare(q(b.scope+b.category)));
    return '<div class="fjzfin-two"><section class="fjzfin-card"><div class="fjzfin-head"><div><span class="fjzfin-kicker">PLANIFICACIÓN</span><h3>Presupuesto mensual</h3><p>Definí topes por categoría para los gastos personales o del negocio.</p></div></div><form class="fjzfin-form" data-fin-form="budget"><label>Ámbito<select name="scope">'+opt('personal','Personal','personal')+opt('business','Negocio','personal')+'</select></label><label>Categoría<input name="category" maxlength="80" required placeholder="Ej: Alimentación"></label><label>Presupuesto (ARS)<input name="limit_amount" type="number" min="0.01" step="0.01" required></label><button class="fjzfin-primary" type="submit"'+(ui.busy?' disabled':'')+'>Guardar presupuesto</button></form></section>'+
      '<section class="fjzfin-card"><span class="fjzfin-kicker">CONTROL</span><h3>Gasto real versus previsto</h3><p>Las comparaciones usan únicamente los gastos registrados este mes. No incluyen pagos pendientes de alumnos.</p></section></div>'+
      '<section class="fjzfin-card"><h3>Presupuestos de '+esc(monthTitle())+'</h3>'+(existing.length?existing.map(b=>{const used=by(entriesMonth().filter(e=>e.kind==='expense'&&e.scope===b.scope&&e.category.toLowerCase()===b.category.toLowerCase()),e=>e.amount),pct=Math.min(100,Math.round(100*used/n(b.limit_amount)));return '<div class="fjzfin-budget"><div><strong>'+esc(b.category)+' · '+(b.scope==='personal'?'Personal':'Negocio')+'</strong><small>'+ar(used)+' de '+ar(b.limit_amount)+'</small></div><div class="fjzfin-progress"><i style="width:'+pct+'%;background:'+(used>n(b.limit_amount)?'#fa6677':'#f23b54')+'"></i></div><button type="button" data-fin-action="delete-budget" data-id="'+esc(b.id)+'">Quitar</button></div>'}).join(''):empty('Sin presupuestos','Agregá un objetivo mensual de gastos para empezar.'))+'</section>';
  }
  function overview(){
    const t=totals(),latest=entriesMonth().slice().sort((a,b)=>q(b.occurred_on).localeCompare(q(a.occurred_on))).slice(0,5);
    const late=openDues().filter(x=>q(x.due_date)<nowLocal()).length;
    return '<div class="fjzfin-section-title"><span class="fjzfin-kicker">RESUMEN DEL MES</span><h3>Tu dinero, bien organizado</h3><p>Separá tus finanzas personales de los ingresos y gastos de TEAM FJZ.</p></div>'+
      '<div class="fjzfin-stats">'+moneyStat('Cobrado a alumnos',t.tuition,'Cuotas confirmadas en el mes','accent')+moneyStat('Cuotas por cobrar',t.unpaid,t.pending+' pendientes · '+late+' vencidas','warning')+moneyStat('Resultado del negocio',t.tuition+t.businessIncome-t.businessExpense,'Cobrado + otros ingresos − gastos','')+moneyStat('Resultado personal',t.personalIncome-t.personalExpense,'Ingresos personales − gastos','')+'</div>'+
      '<div class="fjzfin-two"><section class="fjzfin-card"><div class="fjzfin-head"><div><span class="fjzfin-kicker">NEGOCIO</span><h3>TEAM FJZ</h3></div><button type="button" data-fin-action="tab" data-tab="dues">Ver cuotas</button></div><div class="fjzfin-pairs"><div><span>Cuotas cobradas</span><strong>'+ar(t.tuition)+'</strong></div><div><span>Otros ingresos</span><strong>'+ar(t.businessIncome)+'</strong></div><div><span>Gastos del negocio</span><strong>'+ar(t.businessExpense)+'</strong></div></div></section>'+
      '<section class="fjzfin-card"><div class="fjzfin-head"><div><span class="fjzfin-kicker">PERSONAL</span><h3>Mis finanzas</h3></div><button type="button" data-fin-action="tab" data-tab="movements">Registrar</button></div><div class="fjzfin-pairs"><div><span>Ingresos personales</span><strong>'+ar(t.personalIncome)+'</strong></div><div><span>Gastos personales</span><strong>'+ar(t.personalExpense)+'</strong></div><div><span>Balance registrado</span><strong>'+ar(t.personalIncome-t.personalExpense)+'</strong></div></div></section></div>'+
      '<section class="fjzfin-card"><div class="fjzfin-head"><div><span class="fjzfin-kicker">ÚLTIMOS MOVIMIENTOS</span><h3>Actividad registrada</h3></div><button type="button" data-fin-action="tab" data-tab="movements">Ver todos</button></div>'+
      (latest.length?table('<th>Fecha</th><th>Ámbito</th><th>Categoría</th><th>Cuenta</th><th>Importe</th><th>Acciones</th>',latest.map(entryRow).join(''),6):empty('Todavía sin movimientos','Registrá ingresos o gastos para comenzar a construir tu historial.'))+'</section>';
  }
  function paint(){
    if(!allowed())return false;
    const view=document.getElementById('view');if(!view)return false;
    const tabs=[['overview','Resumen'],['dues','Cuotas de alumnos'],['movements','Movimientos'],['budgets','Presupuestos']];
    view.innerHTML='<div class="fjzfin-root" id="fjzFinanceRoot"><header class="fjzfin-hero"><div><span class="fjzfin-kicker">GESTIÓN ECONÓMICA · TEAM FJZ</span><h1>Finanzas</h1><p>Cuotas de alumnos, ingresos, gastos y presupuestos. Todo en ARS y sin mezclar lo personal con el negocio.</p></div><div class="fjzfin-period"><label>Período <input type="month" id="fjzFinanceMonth" value="'+esc(ui.month)+'"></label><button type="button" data-fin-action="refresh">Actualizar</button><button type="button" data-fin-action="export">Exportar CSV</button></div></header>'+
      '<nav class="fjzfin-tabs" aria-label="Secciones de Finanzas">'+tabs.map(x=>'<button type="button" data-fin-action="tab" data-tab="'+x[0]+'" class="'+(ui.tab===x[0]?'active':'')+'" aria-current="'+(ui.tab===x[0]?'page':'false')+'">'+x[1]+'</button>').join('')+'</nav>'+
      (ui.loading?'<div class="fjzfin-card fjzfin-loading">Cargando registros privados...</div>':ui.error?'<section class="fjzfin-card fjzfin-error"><strong>No se pudieron cargar tus finanzas</strong><p>'+esc(ui.error)+'</p><button type="button" data-fin-action="refresh">Reintentar</button></section>':!ui.loaded?'<div class="fjzfin-card fjzfin-loading">Preparando el módulo...</div>':ui.tab==='dues'?duePanel():ui.tab==='movements'?movements():ui.tab==='budgets'?budgetView():overview())+
      '<footer class="fjzfin-footer">Finanzas V22 · staging · Sin conexión automática a bancos. Los datos que registres aquí se guardan únicamente en el entorno de prueba.</footer></div>';
    const host=view.querySelector('#fjzFinanceRoot');if(!host)return true;
    host.onclick=async function(event){const b=event.target.closest('[data-fin-action]');if(!b||ui.busy)return;const action=b.dataset.finAction,id=b.dataset.id;
      if(action==='tab'){ui.tab=b.dataset.tab;ui.editId='';paint();return}
      if(action==='refresh'){ui.loaded=false;await load();return}
      if(action==='export'){exportCsv();return}
      if(action==='cancel-edit'){ui.editId='';paint();return}
      if(action==='edit'){ui.editId=id;ui.tab='movements';paint();view.querySelector('[data-fin-form="entry"]')?.scrollIntoView({block:'start'});return}
      if(action==='delete'){if(root.confirm('¿Eliminar este movimiento?'))await removeEntry(id);return}
      if(action==='delete-budget'){if(root.confirm('¿Quitar este presupuesto?'))await removeBudget(id);return}
      if(action==='paid'){if(root.confirm('¿Confirmás que recibiste esta cuota?'))await markPaid(id);return}
    };
    host.onchange=function(event){
      if(event.target.id==='fjzFinanceMonth'){
        if(/^\d{4}-\d{2}$/.test(event.target.value)){ui.month=event.target.value;paint()}
      }else if(event.target.id==='fjzfinScope'){ui.scope=event.target.value;paint()}
    };
    host.onsubmit=async function(event){const form=event.target.closest('[data-fin-form]');if(!form)return;event.preventDefault();if(ui.busy)return;const values=Object.fromEntries(new FormData(form).entries());const kind=form.dataset.finForm;if(kind==='due')await addDue(values);if(kind==='entry')await saveEntry(values);if(kind==='budget')await saveBudget(values)};
    return true;
  }
  async function load(){
    if(ui.loading||!allowed())return;
    ui.loading=true;ui.error='';paint();
    try{
      const c=ctx(),sb=c?.supabase||root.supabaseClient;if(!sb)throw Error('No hay conexión segura con staging.');
      const user=await sb.auth.getUser(),uid=user.data?.user?.id;if(user.error||!uid)throw Error('Iniciá sesión como Coach.');
      if(ui.owner&&ui.owner!==uid){ui.entries=[];ui.budgets=[];ui.payments=[];ui.athletes=[]}
      ui.owner=uid;
      const queries=await Promise.all([
        sb.from('coach_finance_entries').select('id,scope,kind,category,amount,occurred_on,account,description').eq('coach_id',uid).order('occurred_on',{ascending:false}).limit(1000),
        sb.from('coach_finance_budgets').select('id,month,scope,category,limit_amount').eq('coach_id',uid).limit(1000),
        sb.from('coach_payments').select('id,athlete_id,due_date,amount,status,paid_on,payment_method,note').eq('coach_id',uid).order('due_date',{ascending:false}).limit(1000),
        sb.from('athletes').select('id,name').eq('coach_id',uid).order('name').limit(1000)
      ]);
      for(const x of queries)if(x.error)throw Error(x.error.message||'Error de lectura');
      ui.entries=queries[0].data||[];ui.budgets=queries[1].data||[];ui.payments=queries[2].data||[];ui.athletes=queries[3].data||[];ui.loaded=true;
    }catch(err){ui.error=q(err?.message)||'No fue posible leer los registros';ui.loaded=false}
    finally{ui.loading=false;paint()}
  }
  async function mutate(task){
    const c=ctx();if(!allowed()||ui.busy||!c?.supabase)return;
    ui.busy=true;paint();
    try{const r=await task(c.supabase,ui.owner);if(r?.error)throw Error(r.error.message);ui.editId='';ui.loaded=false;ui.busy=false;await load();return true}
    catch(err){ui.busy=false;ui.error=q(err?.message)||'No se confirmó el guardado';paint();return false}
  }
  async function addDue(f){
    if(!ui.athletes.some(a=>a.id===f.athlete_id)||!(n(f.amount)>0)||!/^\d{4}-\d{2}-\d{2}$/.test(q(f.due_date)))return;
    await mutate((sb,uid)=>sb.from('coach_payments').insert({coach_id:uid,athlete_id:f.athlete_id,due_date:f.due_date,amount:Number(f.amount),status:'pending',note:q(f.note).slice(0,200)}).select('id').single());
  }
  async function markPaid(id){
    if(!ui.payments.some(x=>x.id===id&&x.status==='pending'))return;
    const method=document.querySelector('select[data-fin-method="'+id+'"]')?.value||'transfer';
    await mutate((sb,uid)=>sb.from('coach_payments').update({status:'paid',paid_on:nowLocal(),payment_method:method}).eq('coach_id',uid).eq('id',id).select('id').single());
  }
  async function saveEntry(f){
    const amount=n(f.amount),cat=q(f.category),account=q(f.account);
    if(!(amount>0)||!cat||!account||!/^\d{4}-\d{2}-\d{2}$/.test(q(f.occurred_on)))return;
    const payload={scope:f.scope,kind:f.kind,amount,category:cat.slice(0,80),account:account.slice(0,80),description:q(f.description).slice(0,500),occurred_on:f.occurred_on,updated_at:new Date().toISOString()};
    if(!['personal','business'].includes(payload.scope)||!['income','expense'].includes(payload.kind))return;
    const id=ui.editId;
    await mutate((sb,uid)=>id?sb.from('coach_finance_entries').update(payload).eq('coach_id',uid).eq('id',id).select('id').single():sb.from('coach_finance_entries').insert({...payload,coach_id:uid}).select('id').single());
  }
  async function saveBudget(f){
    const amount=n(f.limit_amount),category=q(f.category);
    if(!(amount>0)||!category||!['personal','business'].includes(f.scope))return;
    await mutate((sb,uid)=>sb.from('coach_finance_budgets').upsert({coach_id:uid,month:ui.month+'-01',scope:f.scope,category:category.slice(0,80),limit_amount:amount},{onConflict:'coach_id,month,scope,category'}).select('id').single());
  }
  async function removeEntry(id){
    if(!ui.entries.some(x=>x.id===id))return;
    await mutate((sb,uid)=>sb.from('coach_finance_entries').delete().eq('coach_id',uid).eq('id',id).select('id').single());
  }
  async function removeBudget(id){
    if(!ui.budgets.some(x=>x.id===id))return;
    await mutate((sb,uid)=>sb.from('coach_finance_budgets').delete().eq('coach_id',uid).eq('id',id).select('id').single());
  }
  function exportCsv(){
    if(!ui.loaded||ui.error)return;
    const safe=(v)=>{let s=String(v??'');if(/^[\s]*[=+@-]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"'};
    const rows=[['fecha','ambito','tipo','categoria','importe_ars','cuenta','descripcion']];
    entriesMonth().forEach(e=>rows.push([e.occurred_on,e.scope,e.kind,e.category,e.amount,e.account,e.description]));
    const csv='\uFEFF'+rows.map(row=>row.map(safe).join(';')).join('\r\n');
    const blob=new Blob([csv],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');
    a.href=url;a.download='team-fjz-finanzas-'+ui.month+'.csv';a.click();URL.revokeObjectURL(url);
  }
  function enter(){
    if(!allowed())return false;
    if(!ui.owner)ui.loaded=false;
    paint();
    if(!ui.loaded&&!ui.loading)load();
    root.__fjzSyncCoachWorkspaceNavV22?.();
    return true;
  }
  root.__fjzRenderCoachFinancesV22=enter;
})(window);
