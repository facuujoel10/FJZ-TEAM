import pathlib,re

p=pathlib.Path("public/index.html")
html=p.read_text(encoding="utf-8")

def metrics(doc):
    return {
        "styles":len(re.findall(r"<style\b",doc,re.I)),
        "renders":len(re.findall(r"(?:window\.)?render\s*=",doc)),
        "channels":len(re.findall(r"\.channel\s*\(",doc)),
        "timeouts":len(re.findall(r"setTimeout\s*\(",doc)),
        "intervals":len(re.findall(r"setInterval\s*\(",doc)),
        "rafs":len(re.findall(r"requestAnimationFrame\s*\(",doc)),
        "listeners":len(re.findall(r"addEventListener\s*\(",doc)),
        "mutation_observers":len(re.findall(r"new\s+MutationObserver",doc)),
    }

def edit_script(doc,script_id,transform):
    pat=re.compile(r"(<script[^>]*\bid=[\"']"+re.escape(script_id)+r"[\"'][^>]*>)(.*?)(</script>)",re.S|re.I)
    m=pat.search(doc)
    if not m: raise RuntimeError("V20.90 missing script "+script_id)
    body=m.group(2)
    new=transform(body)
    if new==body: raise RuntimeError("V20.90 no changes in "+script_id)
    return doc[:m.start(2)]+new+doc[m.end(2):]

before=metrics(html)

for marker in [
    'meta name="fjz-legacy-runtime-cleanup" content="20.89"',
    "function postRenderV175(){",
    "trackingCache",
    "specificProgressAlerts:true",
]:
    if marker not in html:
        raise RuntimeError("V20.90 prerequisite missing "+marker)

def patch_v175(body):
    anchor="  function postRenderV175(){"
    if body.count(anchor)!=1:
        raise RuntimeError("V20.90 postRender anchor mismatch")

    helpers=r"""
  /* ---------- Final product layer V20.90 ---------- */
  const habitCacheV290=new Map();
  const habitInflightV290=new Map();
  const HABIT_LOCAL_PREFIX_V290='fjz-v290-habits-';

  function isoTodayV290(){
    const d=new Date(),y=d.getFullYear(),m=String(d.getMonth()+1).padStart(2,'0'),day=String(d.getDate()).padStart(2,'0');
    return y+'-'+m+'-'+day;
  }
  function isoDaysAgoV290(days){
    const d=new Date();d.setDate(d.getDate()-days);
    return d.toISOString().slice(0,10);
  }
  function selectedAthleteV290(){
    const s=student?.();
    return s?.id?cloudAthletes?.get?.(s.id)||null:null;
  }
  function localHabitStateV290(s){
    const key=HABIT_LOCAL_PREFIX_V290+String(s?.id||'demo');
    let data=null;
    try{data=JSON.parse(localStorage.getItem(key)||'null')}catch(_e){}
    if(!data||!Array.isArray(data.assignments)){
      data={
        assignments:[
          {id:'demo-water',name:'Hidratación',category:'nutrition',active:true,sort_order:0},
          {id:'demo-steps',name:'Movimiento diario',category:'movement',active:true,sort_order:1},
          {id:'demo-sleep',name:'Rutina de sueño',category:'recovery',active:true,sort_order:2}
        ],
        logs:[]
      };
      try{localStorage.setItem(key,JSON.stringify(data))}catch(_e){}
    }
    return {key,data};
  }
  function saveLocalHabitStateV290(s,data){
    try{localStorage.setItem(HABIT_LOCAL_PREFIX_V290+String(s?.id||'demo'),JSON.stringify(data))}catch(_e){}
  }
  async function loadHabitsV290(force=false){
    const s=student?.();if(!s)return {assignments:[],logs:[]};
    const ath=selectedAthleteV290();
    const key=ath?.id||('local:'+String(s.id));
    const hit=habitCacheV290.get(key);
    if(!force&&hit&&Date.now()-hit.at<30000)return hit.data;
    if(habitInflightV290.has(key))return habitInflightV290.get(key);

    const job=(async()=>{
      if(!cloudEnabled||!supabaseClient||!ath?.id){
        const local=localHabitStateV290(s).data;
        const data={assignments:(local.assignments||[]).filter(x=>x.active!==false),logs:local.logs||[]};
        habitCacheV290.set(key,{at:Date.now(),data});return data;
      }
      const [a,l]=await Promise.all([
        supabaseClient.from('athlete_habits')
          .select('id,athlete_id,coach_id,name,category,active,sort_order,created_at,updated_at')
          .eq('athlete_id',ath.id).eq('active',true).order('sort_order').order('created_at'),
        supabaseClient.from('nutrition_habit_logs')
          .select('id,athlete_id,student_id,habit_id,logged_on,completed,created_at,updated_at')
          .eq('athlete_id',ath.id).gte('logged_on',isoDaysAgoV290(42)).order('logged_on',{ascending:false})
      ]);
      if(a.error)throw a.error;if(l.error)throw l.error;
      const data={assignments:a.data||[],logs:l.data||[]};
      habitCacheV290.set(key,{at:Date.now(),data});return data;
    })().finally(()=>habitInflightV290.delete(key));
    habitInflightV290.set(key,job);return job;
  }
  function completedHabitSetV290(data,date=isoTodayV290()){
    return new Set((data?.logs||[]).filter(x=>x.completed&&String(x.logged_on)===date).map(x=>String(x.habit_id)));
  }
  function habitEligibleOnV291(h,day){
    const created=String(h?.created_at||'').slice(0,10);
    return !created||created<=day;
  }
  function habitWeekAdherenceV290(data){
    const active=(data?.assignments||[]).filter(x=>x.active!==false);
    if(!active.length)return null;
    let done=0,total=0;
    for(let i=0;i<7;i++){
      const d=new Date();d.setDate(d.getDate()-i);
      const day=d.toISOString().slice(0,10);
      const eligible=active.filter(h=>habitEligibleOnV291(h,day));
      const keys=new Set(eligible.map(x=>String(x.id)));
      total+=eligible.length;
      done+=(data?.logs||[]).filter(x=>x.completed&&String(x.logged_on)===day&&keys.has(String(x.habit_id))).length;
    }
    return total?Math.round(done/total*100):null;
  }
  function habitStreakV290(data){
    const active=(data?.assignments||[]).filter(x=>x.active!==false);
    if(!active.length)return 0;
    let streak=0;
    for(let i=0;i<42;i++){
      const d=new Date();d.setDate(d.getDate()-i);
      const day=d.toISOString().slice(0,10);
      const eligible=active.filter(h=>habitEligibleOnV291(h,day));
      if(!eligible.length)break;
      const ids=new Set(eligible.map(x=>String(x.id)));
      const done=new Set((data?.logs||[]).filter(x=>x.completed&&String(x.logged_on)===day&&ids.has(String(x.habit_id))).map(x=>String(x.habit_id)));
      if(done.size===eligible.length)streak++;
      else if(i===0)continue;
      else break;
    }
    return streak;
  }
  function habitCategoryLabelV290(cat){
    return ({movement:'Movimiento',recovery:'Recuperación',nutrition:'Nutrición',cardio:'Cardio',general:'General'})[cat]||'General';
  }

  window.toggleHabitV290=async function(id){
    const s=student?.();if(!s)return;
    const ath=selectedAthleteV290(),today=isoTodayV290();
    try{
      if(!cloudEnabled||!supabaseClient||!ath?.id){
        const local=localHabitStateV290(s);const logs=local.data.logs||[];
        const idx=logs.findIndex(x=>String(x.habit_id)===String(id)&&String(x.logged_on)===today);
        if(idx>=0)logs[idx].completed=!logs[idx].completed;
        else logs.push({id:'local-'+Date.now(),habit_id:String(id),logged_on:today,completed:true});
        local.data.logs=logs;saveLocalHabitStateV290(s,local.data);
      }else{
        const existing=await supabaseClient.from('nutrition_habit_logs')
          .select('id,completed').eq('athlete_id',ath.id).eq('habit_id',String(id)).eq('logged_on',today).maybeSingle();
        if(existing.error)throw existing.error;
        if(existing.data?.id){
          const r=await supabaseClient.from('nutrition_habit_logs')
            .update({completed:!existing.data.completed,updated_at:new Date().toISOString()}).eq('id',existing.data.id);
          if(r.error)throw r.error;
        }else{
          const r=await supabaseClient.from('nutrition_habit_logs').insert({
            athlete_id:ath.id,student_id:currentUser?.id||s.id,habit_id:String(id),logged_on:today,completed:true
          });
          if(r.error)throw r.error;
        }
      }
      habitCacheV290.clear();
      await injectFinalProductV290(true);
      window.__fjzQuickSavedV264?.('Hábito actualizado');
    }catch(e){console.error(e);toast?.('No se pudo actualizar el hábito')}
  };

  window.addHabitV290=async function(){
    if(!(currentProfile?.role==='coach'))return;
    const s=student?.(),ath=selectedAthleteV290(),input=el('v290HabitName'),cat=el('v290HabitCategory');
    const name=String(input?.value||'').trim();
    if(!s||!name)return toast?.('Escribí un hábito');
    try{
      if(!cloudEnabled||!supabaseClient||!ath?.id){
        const local=localHabitStateV290(s);
        local.data.assignments.push({id:'local-'+Date.now(),name,category:cat?.value||'general',active:true,sort_order:local.data.assignments.length});
        saveLocalHabitStateV290(s,local.data);
      }else{
        const r=await supabaseClient.from('athlete_habits').insert({
          athlete_id:ath.id,coach_id:currentUser.id,name,category:cat?.value||'general',active:true,
          sort_order:(habitCacheV290.get(ath.id)?.data?.assignments||[]).length
        });
        if(r.error)throw r.error;
      }
      if(input)input.value='';
      habitCacheV290.clear();await injectFinalProductV290(true);window.__fjzQuickSavedV264?.('Hábito agregado');
    }catch(e){console.error(e);toast?.('No se pudo agregar el hábito')}
  };

  window.removeHabitV290=async function(id){
    if(!(currentProfile?.role==='coach'))return;
    const s=student?.(),ath=selectedAthleteV290();if(!s)return;
    try{
      if(!cloudEnabled||!supabaseClient||!ath?.id){
        const local=localHabitStateV290(s);
        const row=local.data.assignments.find(x=>String(x.id)===String(id));if(row)row.active=false;
        saveLocalHabitStateV290(s,local.data);
      }else{
        const r=await supabaseClient.from('athlete_habits')
          .update({active:false,updated_at:new Date().toISOString()}).eq('id',id).eq('athlete_id',ath.id);
        if(r.error)throw r.error;
      }
      habitCacheV290.clear();await injectFinalProductV290(true);window.__fjzQuickSavedV264?.('Hábito retirado');
    }catch(e){console.error(e);toast?.('No se pudo retirar el hábito')}
  };

  function isTodaySessionV290(x){
    return String(x?.date||x?.completedAt||'').slice(0,10)===isoTodayV290();
  }
  function latestCheckinV290(){
    return (trackingCache?.checkins||[]).slice().sort((a,b)=>String(b?.week_start||'').localeCompare(String(a?.week_start||'')))[0]||null;
  }
  function todayWorkoutNameV290(s){
    const todays=(s?.sessions||[]).filter(isTodaySessionV290);
    if(todays.length)return todays[0]?.dayName||'Sesión completada';
    return 'Entrenamiento del día';
  }
  function todayProgressV290(s,data){
    const habits=(data?.assignments||[]).filter(x=>x.active!==false);
    const doneHabits=completedHabitSetV290(data).size;
    const workoutDone=(s?.sessions||[]).some(isTodaySessionV290);
    const check=latestCheckinV290();
    const checkDone=!!check&&Date.now()-Date.parse(check.submitted_at||check.created_at||check.week_start||0)<7*86400000;
    const total=(habits.length?1:0)+1+1;
    const done=(habits.length&&doneHabits===habits.length?1:0)+(workoutDone?1:0)+(checkDone?1:0);
    return {done,total,workoutDone,checkDone,doneHabits,habitTotal:habits.length};
  }

  function numericV291(v){
    if(typeof v==='number')return Number.isFinite(v)?v:NaN;
    const s=String(v??'').trim().replace(',','.').replace(/[^0-9.+-]/g,'');
    const n=Number(s);return Number.isFinite(n)?n:NaN;
  }
  function exerciseKeyV291(name){
    const raw=String(name||'').trim();
    try{return typeof normalizeTextV70==='function'?normalizeTextV70(raw):raw.toLocaleLowerCase('es-AR')}catch(_e){return raw.toLowerCase()}
  }
  function setStatsV290(result){
    const raw=Array.isArray(result?.sets)?result.sets:[];
    const sets=raw.map(x=>{
      if(Array.isArray(x))return {kg:numericV291(x?.[0]),reps:numericV291(x?.[1])};
      if(x&&typeof x==='object'){
        const kg=numericV291(x.kg??x.weight??x.load??x.peso??x.value);
        const reps=numericV291(x.reps??x.rep??x.repetitions??x.repeticiones);
        return {kg,reps};
      }
      return null;
    }).filter(x=>x&&Number.isFinite(x.reps)&&x.reps>0);
    if(!sets.length)return null;
    const weighted=sets.filter(x=>Number.isFinite(x.kg)&&x.kg>0);
    return {
      bestLoad:weighted.length?Math.max(...weighted.map(x=>x.kg)):null,
      bestReps:Math.max(...sets.map(x=>x.reps)),
      volume:weighted.reduce((a,x)=>a+x.kg*x.reps,0)
    };
  }
  function achievementsV290(s){
    const sessions=(s?.sessions||[]).slice().sort((a,b)=>Date.parse(a?.date||0)-Date.parse(b?.date||0));
    const out=[];
    const count=sessions.length;
    [10,25,50,100].forEach(n=>{if(count>=n)out.push({tone:'milestone',title:n+' entrenamientos registrados',meta:'Hito de constancia'})});
    const by=new Map();
    sessions.forEach(ss=>{
      const perSession=new Map();
      (ss?.exerciseResults||[]).forEach(r=>{
        const name=String(r?.name||'').trim();if(!name)return;
        const st=setStatsV290(r);if(!st)return;
        const key=exerciseKeyV291(name);if(!key)return;
        const prev=perSession.get(key);
        perSession.set(key,{
          name,
          bestLoad:Math.max(Number(prev?.bestLoad)||0,Number(st.bestLoad)||0)||null,
          bestReps:Math.max(Number(prev?.bestReps)||0,Number(st.bestReps)||0),
          volume:(Number(prev?.volume)||0)+(Number(st.volume)||0)
        });
      });
      perSession.forEach((st,key)=>{
        if(!by.has(key))by.set(key,{name:st.name,items:[]});
        const bucket=by.get(key);bucket.name=st.name;
        bucket.items.push({date:ss.date,sessionId:ss.id||'',bestLoad:st.bestLoad,bestReps:st.bestReps,volume:st.volume});
      });
    });
    by.forEach((bucket)=>{
      const name=bucket.name,items=bucket.items;
      if(items.length<2)return;
      const last=items[items.length-1],prev=items.slice(0,-1);
      const prevLoad=Math.max(...prev.map(x=>Number(x.bestLoad)||0));
      const prevVol=Math.max(...prev.map(x=>Number(x.volume)||0));
      const parsed=Date.parse(last.date||'');const recent=Number.isFinite(parsed)&&Date.now()-parsed>=0&&Date.now()-parsed<=14*86400000;
      if(recent&&Number(last.bestLoad)>prevLoad&&Number(last.bestLoad)>0)
        out.unshift({tone:'pr',kind:'load',exercise:name,title:'Nuevo PR · '+name,meta:last.bestLoad+' kg',value:last.bestLoad,date:last.date,sessionId:last.sessionId});
      else if(recent&&Number(last.volume)>prevVol&&Number(last.volume)>0)
        out.push({tone:'pr',kind:'volume',exercise:name,title:'Mejor volumen · '+name,meta:Math.round(last.volume)+' kg·rep',value:Math.round(last.volume),date:last.date,sessionId:last.sessionId});
    });
    return out.slice(0,4);
  }

  function checkinInsightV290(){
    const rows=(trackingCache?.checkins||[]).slice().sort((a,b)=>String(b?.week_start||'').localeCompare(String(a?.week_start||''))).slice(0,3);
    if(!rows.length)return {title:'Todavía no hay check-ins para comparar',body:'Cuando haya datos, este panel va a resumir tendencias y posibles puntos de revisión.',draft:''};
    const latest=rows[0],older=rows[rows.length-1];
    const vals=(key)=>rows.map(x=>Number(x?.[key])).filter(Number.isFinite);
    const avg=(key)=>{const xs=vals(key);return xs.length?xs.reduce((a,b)=>a+b,0)/xs.length:null};
    const changes=[];
    const delta=(key,label,reverse=false)=>{
      const a=Number(latest?.[key]),b=Number(older?.[key]);if(!Number.isFinite(a)||!Number.isFinite(b)||rows.length<2)return;
      const d=a-b;if(Math.abs(d)>=2)changes.push(label+' '+(d>0?'subió':'bajó')+' '+Math.abs(d)+' puntos'+(reverse?' (más alto requiere contexto)':''));
    };
    delta('energy_level','Energía');delta('sleep_quality','Sueño');delta('recovery_level','Recuperación');delta('adherence_level','Adherencia');delta('stress_level','Estrés',true);
    const flags=[];
    if(avg('energy_level')!=null&&avg('energy_level')<=5)flags.push('energía media baja');
    if(avg('recovery_level')!=null&&avg('recovery_level')<=5)flags.push('recuperación media baja');
    if(avg('adherence_level')!=null&&avg('adherence_level')<=6)flags.push('adherencia para revisar');
    if(avg('stress_level')!=null&&avg('stress_level')>=7)flags.push('estrés elevado');
    const title=flags.length?'Hay señales para revisar antes de ajustar':'Tendencia general estable';
    const body=(changes.length?changes.join(' · ')+'. ':'')+(flags.length?'Puntos principales: '+flags.join(', ')+'.':'No aparecen caídas fuertes en los últimos check-ins.');
    const draft='Revisé tus últimos check-ins. '+body+' Antes de hacer cambios grandes, quiero confirmar cómo venís llevando el plan esta semana y qué fue lo más difícil de sostener.';
    return {title,body,draft};
  }
  window.copyCheckinDraftV290=async function(){
    const text=checkinInsightV290().draft;if(!text)return;
    try{await navigator.clipboard.writeText(text);toast?.('Borrador copiado')}catch(_e){toast?.('No se pudo copiar')}
  };

  function engagementRiskV290(s){
    let score=0,reasons=[];
    const days=typeof daysSince==='function'?daysSince(s?.lastWorkout):null;
    const adh=Number(typeof adherence==='function'?adherence(s):NaN);
    if(Number.isFinite(days)&&days>=10){score+=45;reasons.push(days+' días sin entrenamiento registrado')}
    else if(Number.isFinite(days)&&days>=6){score+=28;reasons.push(days+' días sin entrenamiento registrado')}
    if(Number.isFinite(adh)&&adh<45){score+=35;reasons.push('adherencia 7 días '+Math.round(adh)+'%')}
    else if(Number.isFinite(adh)&&adh<70){score+=18;reasons.push('adherencia 7 días '+Math.round(adh)+'%')}
    if((s?.checkin||'')==='Pendiente'){score+=14;reasons.push('check-in pendiente')}
    const level=score>=55?'high':score>=25?'mid':'low';
    return {score:Math.min(100,score),level,reasons};
  }

  function renderStudentTodayV290(s,data){
    const view=el('view');if(!view)return;
    el('v290Today')?.remove();
    const p=todayProgressV290(s,data),streak=habitStreakV290(data),adh=habitWeekAdherenceV290(data);
    const card=document.createElement('section');card.id='v290Today';card.className='card v290-today';
    card.innerHTML=
      '<div class="v290-head"><div><div class="v225-section-kicker">HOY</div><h3>Tu día en TEAM FJZ</h3><p>'+p.done+' de '+p.total+' áreas completas</p></div>'+
      '<div class="v290-ring"><strong>'+Math.round(p.done/Math.max(1,p.total)*100)+'%</strong><span>hoy</span></div></div>'+
      '<div class="v290-today-grid">'+
        '<button class="v290-action '+(p.workoutDone?'done':'')+'" onclick="studentTab=\\'workout\\';render()"><span>Entrenamiento</span><strong>'+esc(p.workoutDone?'Completado':todayWorkoutNameV290(s))+'</strong></button>'+
        '<button class="v290-action '+(p.checkDone?'done':'')+'" onclick="studentTab=\\'tracking\\';render()"><span>Check-in</span><strong>'+esc(p.checkDone?'Al día':'Revisar')+'</strong></button>'+
        '<button class="v290-action '+(p.habitTotal&&p.doneHabits===p.habitTotal?'done':'')+'" onclick="document.getElementById(\\'v290Habits\\')?.scrollIntoView({block:\\'center\\'})"><span>Hábitos</span><strong>'+p.doneHabits+'/'+p.habitTotal+' · 🔥 '+streak+'</strong></button>'+
        '<button class="v290-action" onclick="studentTab=\\'progress\\';render()"><span>Progreso</span><strong>'+(adh==null?'Sin datos':adh+'% hábitos')+'</strong></button>'+
      '</div>';
    const anchor=el('v253StudentWeekFlow')||el('v245StudentActionHub')||view.querySelector('.hero');
    if(anchor)anchor.insertAdjacentElement('afterend',card);else view.prepend(card);
  }

  function prKeyV291(x){
    const raw=['fjz-pr-v291',String(student()?.id||''),String(x?.sessionId||x?.date||''),exerciseKeyV291(x?.exercise||x?.title||''),String(x?.kind||''),String(x?.value||'')].join('|');
    return encodeURIComponent(raw);
  }
  function latestUnseenPrV291(s){
    const rows=achievementsV290(s).filter(x=>x.tone==='pr');
    for(const x of rows){
      const key=prKeyV291(x);
      try{if(localStorage.getItem(key)!=='1')return {...x,_key:key}}catch(_e){return {...x,_key:key}}
    }
    return null;
  }
  window.dismissPrBannerV291=function(key){
    try{localStorage.setItem(String(key||''),'1')}catch(_e){}
    el('v291PrBanner')?.remove();
  };
  function renderPrBannerV291(s){
    if(!(mode==='student'&&studentTab==='home'))return;
    el('v291PrBanner')?.remove();
    const pr=latestUnseenPrV291(s);if(!pr)return;
    const view=el('view');if(!view)return;
    const card=document.createElement('section');
    card.id='v291PrBanner';card.className='v291-pr-banner';
    const headline=pr.kind==='load'?'NUEVO PESO · NUEVO PR':'NUEVO RÉCORD DE VOLUMEN';
    card.innerHTML='<button class="v291-pr-close" aria-label="Cerrar" onclick="dismissPrBannerV291(\''+esc(pr._key)+'\')">×</button>'+
      '<div class="v291-pr-icon">🏆</div><div class="v291-pr-copy"><span>'+headline+'</span><strong>'+esc(pr.exercise||pr.title)+'</strong><b>'+esc(pr.meta)+'</b><small>Tu progreso quedó registrado en Logros.</small></div>';
    const anchor=el('v290Today')||view.querySelector('.hero');
    if(anchor)anchor.insertAdjacentElement('afterend',card);else view.prepend(card);
  }

  function renderStudentHabitsV290(data){
    if(!(mode==='student'&&studentTab==='home'))return;
    const view=el('view');if(!view)return;
    el('v290Habits')?.remove();
    const rows=(data?.assignments||[]).filter(x=>x.active!==false),done=completedHabitSetV290(data);
    const card=document.createElement('section');card.id='v290Habits';card.className='card v290-habits';
    card.innerHTML='<div class="section-title"><div><div class="v225-section-kicker">HÁBITOS</div><h3>Constancia diaria</h3><div class="muted tiny">Marcá solo lo que realmente cumpliste hoy.</div></div>'+
      '<span class="badge blue">🔥 '+habitStreakV290(data)+' días</span></div>'+
      (rows.length?'<div class="v290-habit-list">'+rows.map(h=>{
        const yes=done.has(String(h.id));
        return '<button class="v290-habit '+(yes?'done':'')+'" onclick="toggleHabitV290(\\''+esc(String(h.id))+'\\')"><span class="v290-check">'+(yes?'✓':'')+'</span><div><strong>'+esc(h.name)+'</strong><small>'+esc(habitCategoryLabelV290(h.category))+'</small></div></button>';
      }).join('')+'</div>':'<div class="v290-empty">Tu coach todavía no asignó hábitos.</div>');
    const anchor=el('v290Today')||el('v253StudentWeekFlow')||view.querySelector('.hero');
    if(anchor)anchor.insertAdjacentElement('afterend',card);else view.prepend(card);
  }

  function renderAchievementsV290(s){
    if(!(mode==='student'&&studentTab==='home'))return;
    const view=el('view');if(!view)return;
    el('v290Achievements')?.remove();
    const rows=achievementsV290(s);
    const card=document.createElement('section');card.id='v290Achievements';card.className='card v290-achievements';
    card.innerHTML='<div class="section-title"><div><div class="v225-section-kicker">LOGROS</div><h3>Récords y constancia</h3><div class="muted tiny">Progreso visible sin cambiar tu rutina automáticamente.</div></div></div>'+
      (rows.length?'<div class="v290-achievement-grid">'+rows.map(x=>'<div class="v290-achievement '+x.tone+'"><span>'+(x.tone==='pr'?'🏆':'✓')+'</span><div><strong>'+esc(x.title)+'</strong><small>'+esc(x.meta)+'</small></div></div>').join('')+'</div>':'<div class="v290-empty">Los logros aparecen a medida que acumulás sesiones y progresos.</div>');
    const anchor=el('v290Habits')||el('v253StudentWeekFlow');
    if(anchor)anchor.insertAdjacentElement('afterend',card);else view.append(card);
  }

  function renderCoachHabitManagerV290(data){
    if(!(mode==='coach'&&coachTab==='student'&&coachStudentTab==='summary'))return;
    const host=el('coachStudentBody');if(!host)return;
    el('v290CoachHabits')?.remove();
    const rows=(data?.assignments||[]).filter(x=>x.active!==false),done=completedHabitSetV290(data);
    const card=document.createElement('section');card.id='v290CoachHabits';card.className='card v290-coach-habits';
    card.innerHTML='<div class="section-title"><div><div class="v225-section-kicker">HÁBITOS</div><h3>Hábitos asignados</h3><div class="muted tiny">Seguimiento simple, sin mensajes automáticos.</div></div>'+
      '<span class="badge blue">'+(habitWeekAdherenceV290(data)??0)+'% · 7 días</span></div>'+
      '<div class="v290-coach-habit-list">'+(rows.length?rows.map(h=>'<div class="v290-coach-habit"><div><strong>'+esc(h.name)+'</strong><small>'+esc(habitCategoryLabelV290(h.category))+' · '+(done.has(String(h.id))?'Hecho hoy':'Pendiente hoy')+'</small></div><button class="btn ghost small" onclick="removeHabitV290(\\''+esc(String(h.id))+'\\')">Retirar</button></div>').join(''):'<div class="v290-empty">Sin hábitos asignados.</div>')+'</div>'+
      '<div class="v290-habit-create"><input id="v290HabitName" placeholder="Ej: movilidad 10 min" maxlength="80"><select id="v290HabitCategory"><option value="general">General</option><option value="movement">Movimiento</option><option value="recovery">Recuperación</option><option value="nutrition">Nutrición</option><option value="cardio">Cardio</option></select><button class="btn primary" onclick="addHabitV290()">Agregar</button></div>';
    const anchor=el('v175Coach360')||host.firstElementChild;
    if(anchor)anchor.insertAdjacentElement('afterend',card);else host.prepend(card);
  }

  function renderCheckinAssistantV290(){
    if(!(mode==='coach'&&coachTab==='student'&&coachStudentTab==='summary'))return;
    const host=el('coachStudentBody');if(!host)return;
    el('v290CheckinAssistant')?.remove();
    const i=checkinInsightV290();
    const card=document.createElement('section');card.id='v290CheckinAssistant';card.className='card v290-checkin-assistant';
    card.innerHTML='<div class="section-title"><div><div class="v225-section-kicker">ASISTENTE DE CHECK-IN</div><h3>'+esc(i.title)+'</h3><div class="muted tiny">'+esc(i.body)+'</div></div><span class="badge blue">Últimos 3</span></div>'+
      (i.draft?'<div class="v290-draft"><strong>Borrador de devolución</strong><p>'+esc(i.draft)+'</p><div class="v290-draft-actions"><button class="btn small" onclick="copyCheckinDraftV290()">Copiar borrador</button><button class="btn primary small" onclick="coachStudentTab=\\'tracking\\';render()">Abrir seguimiento</button></div></div>':'');
    const anchor=el('v290CoachHabits')||el('v175Coach360')||host.firstElementChild;
    if(anchor)anchor.insertAdjacentElement('afterend',card);else host.prepend(card);
  }

  function renderCoachRiskV290(){
    if(!(mode==='coach'&&coachTab==='dashboard'))return;
    const view=el('view');if(!view)return;
    el('v290Risk')?.remove();
    const rows=(Array.isArray(state?.students)?state.students:[]).map(s=>({s,r:engagementRiskV290(s)}))
      .sort((a,b)=>b.r.score-a.r.score).slice(0,5);
    const card=document.createElement('section');card.id='v290Risk';card.className='card v290-risk';
    card.innerHTML='<div class="section-title"><div><div class="v225-section-kicker">ADHERENCIA</div><h3>Riesgo de desconexión</h3><div class="muted tiny">Prioriza a quién revisar primero según actividad, adherencia y check-in. Es una señal operativa, no un diagnóstico.</div></div></div>'+
      '<div class="v290-risk-list">'+rows.map(x=>{
        const label=x.r.level==='high'?'Prioridad':x.r.level==='mid'?'Atención':'Bien';
        return '<button class="v290-risk-row '+x.r.level+'" onclick="openStudent(\\''+esc(String(x.s.id))+'\\');coachStudentTab=\\'summary\\';render()"><div><strong>'+esc(x.s.name||'Alumno')+'</strong><small>'+esc(x.r.reasons.join(' · ')||'Sin señales principales')+'</small></div><span>'+label+' · '+x.r.score+'</span></button>';
      }).join('')+'</div>';
    const anchor=el('v252CoachPriorityCenter')||el('v225CoachDashboard')||view.querySelector('.hero');
    if(anchor)anchor.insertAdjacentElement('afterend',card);else view.prepend(card);
  }

  async function injectFinalProductV290(force=false){
    const s=student?.();
    if(mode==='coach'&&coachTab==='dashboard')renderCoachRiskV290();
    if(!s)return;
    const needsHabits=(mode==='student'&&studentTab==='home')||(mode==='coach'&&coachTab==='student'&&coachStudentTab==='summary');
    let data={assignments:[],logs:[]};
    if(needsHabits){
      try{data=await loadHabitsV290(force)}catch(e){console.warn('V20.90 habits',e)}
      const same=String(student()?.id||'')===String(s.id||'');if(!same)return;
    }
    if(mode==='student'&&studentTab==='home'){
      renderStudentTodayV290(s,data);renderPrBannerV291(s);renderStudentHabitsV290(data);renderAchievementsV290(s);
    }
    if(mode==='coach'&&coachTab==='student'&&coachStudentTab==='summary'){
      renderCoachHabitManagerV290(data);
      if(typeof loadTracking==='function'){
        const aid=typeof trackingAthleteId==='function'?trackingAthleteId():null;
        if(aid&&trackingLoadedFor!==aid)try{await loadTracking(false)}catch(_e){}
      }
      if(mode==='coach'&&coachTab==='student'&&coachStudentTab==='summary'&&String(student()?.id||'')===String(s.id||''))renderCheckinAssistantV290();
    }
  }

"""
    body=body.replace(anchor,helpers+anchor,1)
    body=body.replace(anchor,anchor+"\n    injectFinalProductV290(false);",1)

    marker="window.__fjzV175={"
    if marker not in body:
        raise RuntimeError("V20.90 V175 marker object missing")
    body=body.replace(marker,"window.__fjzV175={finalProductLayerV290:true,todayDashboardV290:true,habitStreaksV290:true,prAchievementsV290:true,engagementRiskV290:true,checkinAssistantV290:true,prBannerV291:true,robustPrDetectionV291:true,localizedWeightParsingV291:true,normalizedExercisePrKeyV291:true,habitAssignmentDateAwareV291:true,prSessionDedupV291:true,prSafeStorageKeyV291:true,",1)
    return body

html=edit_script(html,"v175ProfileAgendaCoachCenterRuntime",patch_v175)

css=r"""
/* TEAM FJZ · V20.90 FINAL PRODUCT LAYER */
.v290-head{display:flex;justify-content:space-between;gap:14px;align-items:flex-start}
.v290-head h3{margin:2px 0 0;font-size:20px}
.v290-head p{margin:5px 0 0;color:var(--muted);font-size:12px}
.v290-ring{width:64px;height:64px;border:1px solid #3c424c;border-radius:18px;background:#111318;display:grid;place-items:center;align-content:center}
.v290-ring strong{font-size:16px}.v290-ring span{font-size:8px;color:var(--muted);text-transform:uppercase}
.v290-today-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-top:12px}
.v290-action{appearance:none;text-align:left;padding:12px;border:1px solid #30343c;border-radius:12px;background:#0d0f13;color:#eef0f3;cursor:pointer}
.v290-action span{display:block;color:#8e949e;font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:.05em}
.v290-action strong{display:block;margin-top:5px;font-size:12px;line-height:1.35}.v290-action.done{border-color:rgba(59,213,138,.42);background:rgba(59,213,138,.045)}
.v290-habit-list,.v290-coach-habit-list,.v290-risk-list{display:grid;gap:7px}
.v290-habit{appearance:none;width:100%;display:grid;grid-template-columns:34px minmax(0,1fr);gap:10px;align-items:center;text-align:left;padding:10px;border:1px solid #2f343c;border-radius:12px;background:#0d0f13;color:#eef0f3;cursor:pointer}
.v290-habit.done{border-color:rgba(59,213,138,.45);background:rgba(59,213,138,.045)}
.v290-check{width:30px;height:30px;border:1px solid #3a404a;border-radius:9px;display:grid;place-items:center;font-weight:900}.v290-habit.done .v290-check{color:#9ce4bb}
.v290-habit strong,.v290-coach-habit strong{display:block;font-size:12px}.v290-habit small,.v290-coach-habit small{display:block;margin-top:3px;color:#8e949e;font-size:9px}
.v290-achievement-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.v290-achievement{display:grid;grid-template-columns:32px minmax(0,1fr);gap:9px;padding:10px;border:1px solid #30343c;border-radius:12px;background:#0d0f13}.v290-achievement.pr{border-color:rgba(242,189,85,.38)}.v290-achievement strong{display:block;font-size:11px}.v290-achievement small{display:block;color:#8e949e;font-size:9px;margin-top:3px}
.v290-coach-habit{display:flex;justify-content:space-between;gap:8px;align-items:center;padding:9px 10px;border:1px solid #2f343c;border-radius:11px;background:#0d0f13}.v290-habit-create{display:grid;grid-template-columns:minmax(0,1fr) 150px auto;gap:7px;margin-top:10px}.v290-habit-create input,.v290-habit-create select{min-width:0}
.v290-draft{padding:11px;border:1px solid #30343c;border-radius:12px;background:#0d0f13}.v290-draft strong{font-size:10px;text-transform:uppercase;color:#aab0ba}.v290-draft p{font-size:11px;line-height:1.5;color:#e5e7eb}.v290-draft-actions{display:flex;gap:7px;flex-wrap:wrap}
.v290-risk-row{appearance:none;width:100%;display:flex;justify-content:space-between;gap:10px;align-items:center;text-align:left;padding:11px;border:1px solid #30343c;border-radius:12px;background:#0d0f13;color:#eef0f3;cursor:pointer}.v290-risk-row.high{border-left:3px solid #ff5261}.v290-risk-row.mid{border-left:3px solid #f2bd55}.v290-risk-row.low{border-left:3px solid #3bd58a}.v290-risk-row strong{display:block;font-size:13px}.v290-risk-row small{display:block;margin-top:4px;color:#8e949e;font-size:10px;line-height:1.4}.v290-risk-row>span{font-size:10px;font-weight:900;white-space:nowrap}
.v291-pr-banner{position:relative;display:grid;grid-template-columns:52px minmax(0,1fr);gap:12px;align-items:center;padding:15px 44px 15px 15px;border:1px solid rgba(242,189,85,.42);border-radius:16px;background:linear-gradient(135deg,rgba(242,189,85,.10),rgba(15,17,22,.98));box-shadow:0 14px 34px rgba(0,0,0,.22)}
.v291-pr-icon{width:46px;height:46px;display:grid;place-items:center;border-radius:14px;background:rgba(242,189,85,.12);font-size:24px}
.v291-pr-copy span{display:block;color:#f2bd55;font-size:9px;font-weight:950;letter-spacing:.08em}.v291-pr-copy strong{display:block;margin-top:3px;font-size:16px}.v291-pr-copy b{display:block;margin-top:2px;font-size:20px}.v291-pr-copy small{display:block;margin-top:4px;color:#9aa0aa;font-size:10px}
.v291-pr-close{position:absolute;top:8px;right:9px;width:28px;height:28px;border:0;border-radius:8px;background:transparent;color:#a8aeb8;font-size:20px;cursor:pointer}
.v290-empty{padding:14px;text-align:center;color:#858b95;font-size:10px}
@media(max-width:760px){.v290-today-grid{grid-template-columns:1fr 1fr}.v290-habit-create{grid-template-columns:1fr 1fr}.v290-habit-create .btn{grid-column:1/-1}.v290-achievement-grid{grid-template-columns:1fr}}
@media(max-width:430px){.v290-head{align-items:center}.v290-ring{width:56px;height:56px}.v290-today-grid{grid-template-columns:1fr}.v290-risk-row{align-items:flex-start}.v290-risk-row>span{font-size:9px}}
@media(min-width:1000px){.v290-action strong,.v290-habit strong,.v290-coach-habit strong{font-size:14px}.v290-action span,.v290-habit small,.v290-coach-habit small{font-size:11px}.v290-risk-row strong{font-size:15px}.v290-risk-row small{font-size:12px}.v290-draft p{font-size:13px}}
"""

styles=list(re.finditer(r"<style(?P<attrs>[^>]*)>(?P<body>.*?)</style>",html,re.S|re.I))
if len(styles)!=1: raise RuntimeError("V20.90 expected one stylesheet")
sm=styles[0]
html=html[:sm.start("body")]+sm.group("body").rstrip()+"\n"+css+"\n"+html[sm.end("body"):]

html=html.replace("</head>",'<meta name="fjz-final-product-layer" content="20.90">\n</head>',1)

after=metrics(html)
for key in ("styles","renders","channels","timeouts","intervals","rafs","listeners","mutation_observers"):
    if after[key]!=before[key]:
        raise RuntimeError("V20.90 runtime topology changed "+key+": "+repr({"before":before,"after":after}))

required=[
    'meta name="fjz-final-product-layer" content="20.90"',
    "athlete_habits","nutrition_habit_logs",
    "injectFinalProductV290","toggleHabitV290","addHabitV290","removeHabitV290",
    "achievementsV290","engagementRiskV290","checkinInsightV290",
    "HOY","HÁBITOS","LOGROS","Riesgo de desconexión","ASISTENTE DE CHECK-IN",
    "Seguimiento simple, sin mensajes automáticos.",
    "finalProductLayerV290:true"
]
for marker in required:
    if marker not in html: raise RuntimeError("V20.90 missing marker "+marker)

p.write_text(html,encoding="utf-8")
print("TEAM FJZ V20.90 final product layer")
print("V20.90 BEFORE:",before)
print("V20.90 AFTER:",after)
print("V20.90 Today + habits/streaks + PR/achievements + adherence risk + check-in assistant")
