(function(root,factory){
  const nodeErrors=typeof module==='object'&&module.exports?require('./read-errors.js'):null;
  const api=factory((root&&root.TeamFJZReadErrors)||nodeErrors);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.TeamFJZAgendaRepository=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(ReadErrors){
  'use strict';
  if(!ReadErrors)throw new Error('AgendaRepository requires TeamFJZReadErrors');
  const {KINDS,RepositoryReadError,classifyReadError,cancelled}=ReadErrors;
  const SOURCE='agenda-repository-v22',DEFAULT_TTL_MS=15000;
  const SCHEDULE_FIELDS='id,athlete_id,coach_id,weekday,workout_day_id,workout_day_name,start_time,reminder_enabled,reminder_minutes_before,notes,active,created_at,updated_at';
  const REMINDER_FIELDS='id,athlete_id,coach_id,title,body,category,schedule_type,reminder_date,weekday,remind_time,active,created_at,updated_at';

  class AgendaRepositoryError extends RepositoryReadError{constructor(kind,operation,cause,options){super(kind,operation,cause,options);this.name='AgendaRepositoryError'}}
  function wrap(error,operation){
    if(error instanceof AgendaRepositoryError)return error;
    if(error instanceof RepositoryReadError)return new AgendaRepositoryError(error.kind,operation,error.cause||error,{publicMessage:error.publicMessage});
    return new AgendaRepositoryError(classifyReadError(error),operation,error);
  }
  function idValue(value,label){const out=String(value||'').trim();if(!out)throw new TypeError(label+' is required');return out}
  function freezeRows(rows){return Object.freeze((Array.isArray(rows)?rows:[]).map(row=>Object.freeze({...row})))}
  function defaultIdentityResolver(supabase){return async()=>{
    if(!supabase.auth||typeof supabase.auth.getSession!=='function')throw new AgendaRepositoryError(KINDS.AUTHORIZATION,'identity',new Error('Authenticated session unavailable'));
    const res=await supabase.auth.getSession();if(res?.error)throw wrap(res.error,'identity');
    const session=res?.data?.session||null,userId=String(session?.user?.id||'').trim();
    if(!userId)throw new AgendaRepositoryError(KINDS.AUTHORIZATION,'identity',new Error('No authenticated user'));
    return Object.freeze({userId,sessionKey:userId+'|'+String(session?.access_token||'')});
  }}

  function createAgendaRepository({supabase,ttlMs=DEFAULT_TTL_MS,clock=()=>Date.now(),identityResolver}={}){
    if(!supabase||typeof supabase.from!=='function')throw new TypeError('AgendaRepository requires a Supabase client');
    const resolveIdentity=typeof identityResolver==='function'?identityResolver:defaultIdentityResolver(supabase),ttl=Math.max(0,Number(ttlMs)||0),cache=new Map(),inflight=new Map();
    let ownerKey=null,generation=0,disposed=false,authSubscription=null;
    function resetOwnership(nextKey=null){generation++;ownerKey=nextKey;cache.clear();inflight.clear()}
    if(supabase.auth&&typeof supabase.auth.onAuthStateChange==='function'){
      try{
        const reg=supabase.auth.onAuthStateChange((_event,session)=>{
          const uid=String(session?.user?.id||'').trim(),key=uid?uid+'|'+String(session?.access_token||''):null;
          if(key!==ownerKey)resetOwnership(key);
        });
        authSubscription=reg?.data?.subscription||reg?.subscription||null;
      }catch(_e){}
    }
    async function identity(operation){
      if(disposed)throw new AgendaRepositoryError(KINDS.SESSION_CANCELLED,operation,new Error('Repository disposed'));
      let id;try{id=await resolveIdentity()}catch(error){throw wrap(error,operation+':identity')}
      const key=String(id?.sessionKey||id?.userId||'').trim();
      if(!key)throw new AgendaRepositoryError(KINDS.AUTHORIZATION,operation,new Error('Missing identity key'));
      if(ownerKey!==key)resetOwnership(key);
      return Object.freeze({userId:String(id.userId||''),key,generation});
    }
    async function assertSameIdentity(guard,operation){
      const current=await identity(operation);
      if(current.key!==guard.key||current.generation!==guard.generation)throw new AgendaRepositoryError(KINDS.SESSION_CANCELLED,operation,cancelled(operation));
    }
    async function executeList(athleteId,guard){
      let scheduleRes,reminderRes;
      try{[scheduleRes,reminderRes]=await Promise.all([
        supabase.from('athlete_schedule').select(SCHEDULE_FIELDS).eq('athlete_id',athleteId).eq('active',true).order('weekday',{ascending:true}),
        supabase.from('athlete_reminders').select(REMINDER_FIELDS).eq('athlete_id',athleteId).eq('active',true).order('reminder_date',{ascending:true}).order('created_at',{ascending:false})
      ])}catch(error){throw wrap(error,'listForAthlete')}
      if(scheduleRes?.error)throw wrap(scheduleRes.error,'listForAthlete:schedule');
      if(reminderRes?.error)throw wrap(reminderRes.error,'listForAthlete:reminders');
      await assertSameIdentity(guard,'listForAthlete');
      return Object.freeze({source:SOURCE,athleteId,ownerUserId:guard.userId,schedule:freezeRows(scheduleRes?.data),reminders:freezeRows(reminderRes?.data),loadedAt:Number(clock())});
    }
    async function listForAthlete(athleteId,{force=false}={}){
      const aid=idValue(athleteId,'athleteId'),guard=await identity('listForAthlete'),key=guard.key+'|'+aid,hit=cache.get(key),now=Number(clock());
      if(!force&&hit&&now-hit.loadedAt<ttl)return hit;
      if(inflight.has(key))return inflight.get(key);
      const pending=executeList(aid,guard).then(data=>{if(ownerKey!==guard.key||generation!==guard.generation)throw new AgendaRepositoryError(KINDS.SESSION_CANCELLED,'listForAthlete',null);cache.set(key,data);return data});
      inflight.set(key,pending);pending.finally(()=>{if(inflight.get(key)===pending)inflight.delete(key)}).catch(()=>{});
      return pending;
    }
    function cachedById(eventId,guard){
      const prefix=guard.key+'|';
      for(const [key,data] of cache.entries()){if(!key.startsWith(prefix))continue;
        const schedule=data.schedule.find(row=>String(row.id)===eventId);if(schedule)return Object.freeze({source:SOURCE,kind:'schedule',athleteId:String(schedule.athlete_id),ownerUserId:guard.userId,row:schedule});
        const reminder=data.reminders.find(row=>String(row.id)===eventId);if(reminder)return Object.freeze({source:SOURCE,kind:'reminder',athleteId:String(reminder.athlete_id),ownerUserId:guard.userId,row:reminder});
      }return null;
    }
    async function readOne(table,fields,id){try{const res=await supabase.from(table).select(fields).eq('id',id).maybeSingle();if(res?.error)throw wrap(res.error,'getById:'+table);return res?.data?Object.freeze({...res.data}):null}catch(error){throw wrap(error,'getById:'+table)}}
    async function getById(id){
      const eventId=idValue(id,'eventId'),guard=await identity('getById'),cached=cachedById(eventId,guard);if(cached)return cached;
      const [schedule,reminder]=await Promise.all([readOne('athlete_schedule',SCHEDULE_FIELDS,eventId),readOne('athlete_reminders',REMINDER_FIELDS,eventId)]);
      await assertSameIdentity(guard,'getById');
      if(schedule&&reminder)throw new AgendaRepositoryError(KINDS.INTEGRITY,'getById',new Error('Event id exists in both agenda tables'));
      if(!schedule&&!reminder)return null;const row=schedule||reminder;
      return Object.freeze({source:SOURCE,kind:schedule?'schedule':'reminder',athleteId:String(row.athlete_id),ownerUserId:guard.userId,row});
    }
    function clear(athleteId=null){generation++;inflight.clear();if(athleteId==null){cache.clear();return}const suffix='|'+String(athleteId);for(const key of [...cache.keys()])if(key.endsWith(suffix))cache.delete(key)}
    function invalidateSession(){resetOwnership(null)}
    function dispose(){disposed=true;resetOwnership(null);try{authSubscription?.unsubscribe?.()}catch(_e){}authSubscription=null}
    return Object.freeze({listForAthlete,getById,clear,invalidateSession,dispose});
  }
  return Object.freeze({SOURCE,DEFAULT_TTL_MS,AgendaRepositoryError,classifyError:classifyReadError,createAgendaRepository});
});
