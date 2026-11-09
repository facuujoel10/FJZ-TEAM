(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.TeamFJZAgendaRepository=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const SOURCE='agenda-repository-v22';
  const DEFAULT_TTL_MS=15000;
  const SCHEDULE_FIELDS='id,athlete_id,coach_id,weekday,workout_day_id,workout_day_name,start_time,reminder_enabled,reminder_minutes_before,notes,active,created_at,updated_at';
  const REMINDER_FIELDS='id,athlete_id,coach_id,title,body,category,schedule_type,reminder_date,weekday,remind_time,active,created_at,updated_at';

  class AgendaRepositoryError extends Error{
    constructor(kind,operation,cause){
      super('AgendaRepository '+operation+' failed: '+String(cause?.message||cause||kind));
      this.name='AgendaRepositoryError';
      this.kind=kind;
      this.operation=operation;
      this.code=cause?.code||null;
      this.status=Number(cause?.status||cause?.statusCode||0)||null;
      this.cause=cause||null;
    }
  }

  function classifyError(error){
    const status=Number(error?.status||error?.statusCode||0);
    const code=String(error?.code||'');
    const msg=String(error?.message||error||'').toLowerCase();
    if(status===401||status===403||code==='42501'||/permission|not authorized|unauthorized|forbidden/.test(msg))return 'permission';
    if(error instanceof TypeError||status===0||/network|failed to fetch|fetch failed|connection|econn|timeout/.test(msg))return 'network';
    return 'query';
  }

  function wrapError(error,operation){
    if(error instanceof AgendaRepositoryError)return error;
    return new AgendaRepositoryError(classifyError(error),operation,error);
  }

  function idValue(value,label){
    const out=String(value||'').trim();
    if(!out)throw new TypeError(label+' is required');
    return out;
  }

  function freezeRows(rows){
    return Object.freeze((Array.isArray(rows)?rows:[]).map(row=>Object.freeze({...row})));
  }

  function createAgendaRepository({supabase,ttlMs=DEFAULT_TTL_MS,clock=()=>Date.now()}={}){
    if(!supabase||typeof supabase.from!=='function')throw new TypeError('AgendaRepository requires a Supabase client');
    const ttl=Math.max(0,Number(ttlMs)||0);
    const cache=new Map();
    const inflight=new Map();

    async function executeList(athleteId){
      let scheduleRes,reminderRes;
      try{
        [scheduleRes,reminderRes]=await Promise.all([
          supabase.from('athlete_schedule')
            .select(SCHEDULE_FIELDS)
            .eq('athlete_id',athleteId)
            .eq('active',true)
            .order('weekday',{ascending:true}),
          supabase.from('athlete_reminders')
            .select(REMINDER_FIELDS)
            .eq('athlete_id',athleteId)
            .eq('active',true)
            .order('reminder_date',{ascending:true})
            .order('created_at',{ascending:false})
        ]);
      }catch(error){
        throw wrapError(error,'listForAthlete');
      }
      if(scheduleRes?.error)throw wrapError(scheduleRes.error,'listForAthlete:schedule');
      if(reminderRes?.error)throw wrapError(reminderRes.error,'listForAthlete:reminders');

      const data=Object.freeze({
        source:SOURCE,
        athleteId,
        schedule:freezeRows(scheduleRes?.data),
        reminders:freezeRows(reminderRes?.data),
        loadedAt:Number(clock())
      });
      return data;
    }

    async function listForAthlete(athleteId,{force=false}={}){
      const aid=idValue(athleteId,'athleteId');
      const hit=cache.get(aid);
      const now=Number(clock());
      if(!force&&hit&&now-hit.loadedAt<ttl)return hit;
      if(inflight.has(aid))return inflight.get(aid);
      const pending=executeList(aid)
        .then(data=>{cache.set(aid,data);return data})
        .finally(()=>inflight.delete(aid));
      inflight.set(aid,pending);
      return pending;
    }

    function cachedById(id){
      for(const data of cache.values()){
        const schedule=data.schedule.find(row=>String(row.id)===id);
        if(schedule)return Object.freeze({source:SOURCE,kind:'schedule',athleteId:String(schedule.athlete_id),row:schedule});
        const reminder=data.reminders.find(row=>String(row.id)===id);
        if(reminder)return Object.freeze({source:SOURCE,kind:'reminder',athleteId:String(reminder.athlete_id),row:reminder});
      }
      return null;
    }

    async function readOne(table,fields,id){
      try{
        const res=await supabase.from(table).select(fields).eq('id',id).maybeSingle();
        if(res?.error)throw wrapError(res.error,'getById:'+table);
        return res?.data?Object.freeze({...res.data}):null;
      }catch(error){
        throw wrapError(error,'getById:'+table);
      }
    }

    async function getById(id){
      const eventId=idValue(id,'eventId');
      const cached=cachedById(eventId);
      if(cached)return cached;
      const [schedule,reminder]=await Promise.all([
        readOne('athlete_schedule',SCHEDULE_FIELDS,eventId),
        readOne('athlete_reminders',REMINDER_FIELDS,eventId)
      ]);
      if(schedule&&reminder)throw new AgendaRepositoryError('integrity','getById',new Error('Event id exists in both agenda tables'));
      if(!schedule&&!reminder)return null;
      const row=schedule||reminder;
      return Object.freeze({
        source:SOURCE,
        kind:schedule?'schedule':'reminder',
        athleteId:String(row.athlete_id),
        row
      });
    }

    function clear(athleteId=null){
      if(athleteId==null){cache.clear();return}
      cache.delete(String(athleteId));
    }

    return Object.freeze({listForAthlete,getById,clear});
  }

  return Object.freeze({
    SOURCE,
    DEFAULT_TTL_MS,
    AgendaRepositoryError,
    classifyError,
    createAgendaRepository
  });
});
