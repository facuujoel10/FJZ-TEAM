(function(root,factory){
  const nodeErrors=typeof module==='object'&&module.exports?require('./read-errors.js'):null;
  const api=factory((root&&root.TeamFJZReadErrors)||nodeErrors);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.TeamFJZCommentRepository=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(ReadErrors){
  'use strict';
  if(!ReadErrors)throw new Error('CommentRepository requires TeamFJZReadErrors');
  const {RepositoryReadError,classifyReadError}=ReadErrors,SOURCE='comment-repository-v22';
  const FIELDS='id,athlete_id,student_id,session_id,exercise_uid,exercise_name,workout_day_id,workout_day_name,feedback_type,message,status,reviewed_by,reviewed_at,created_at,updated_at';
  class CommentRepositoryError extends RepositoryReadError{constructor(kind,operation,cause,options){super(kind,operation,cause,options);this.name='CommentRepositoryError'}}
  function wrap(error,operation){if(error instanceof CommentRepositoryError)return error;if(error instanceof RepositoryReadError)return new CommentRepositoryError(error.kind,operation,error.cause||error,{publicMessage:error.publicMessage});return new CommentRepositoryError(classifyReadError(error),operation,error)}
  function idValue(value,label){const out=String(value||'').trim();if(!out)throw new TypeError(label+' is required');return out}
  function freezeRows(rows){return Object.freeze((Array.isArray(rows)?rows:[]).map(x=>Object.freeze({...x})))}
  async function run(builder,operation){try{const res=await builder;if(res?.error)throw wrap(res.error,operation);return res}catch(error){throw wrap(error,operation)}}
  function createCommentRepository({supabase}={}){
    if(!supabase||typeof supabase.from!=='function')throw new TypeError('CommentRepository requires a Supabase client');
    async function listForAthlete(athleteId,{status=null,limit=100}={}){
      const aid=idValue(athleteId,'athleteId');let q=supabase.from('exercise_feedback').select(FIELDS).eq('athlete_id',aid);if(status!=null)q=q.eq('status',String(status));q=q.order('created_at',{ascending:false}).limit(Math.max(1,Math.min(250,Number(limit)||100)));
      const res=await run(q,'listForAthlete');return Object.freeze({source:SOURCE,athleteId:aid,rows:freezeRows(res?.data)});
    }
    async function listForSession(sessionId,{athleteId=null,status=null,limit=100}={}){
      const sid=idValue(sessionId,'sessionId');
      let q=supabase.from('exercise_feedback').select(FIELDS).eq('session_id',sid);
      if(athleteId!=null)q=q.eq('athlete_id',idValue(athleteId,'athleteId'));
      if(status!=null)q=q.eq('status',String(status));
      q=q.order('created_at',{ascending:true}).limit(Math.max(1,Math.min(250,Number(limit)||100)));
      const res=await run(q,'listForSession');
      return Object.freeze({source:SOURCE,sessionId:sid,rows:freezeRows(res?.data)});
    }

    async function listPending({athleteId=null,limit=100}={}){
      let q=supabase.from('exercise_feedback').select(FIELDS).eq('status','pending');if(athleteId!=null)q=q.eq('athlete_id',idValue(athleteId,'athleteId'));q=q.order('created_at',{ascending:false}).limit(Math.max(1,Math.min(250,Number(limit)||100)));
      const res=await run(q,'listPending');return Object.freeze({source:SOURCE,status:'pending',rows:freezeRows(res?.data)});
    }
    async function getById(id){const cid=idValue(id,'commentId'),res=await run(supabase.from('exercise_feedback').select(FIELDS).eq('id',cid).maybeSingle(),'getById');return res?.data?Object.freeze({source:SOURCE,row:Object.freeze({...res.data})}):null}
    return Object.freeze({listForAthlete,listForSession,listPending,getById});
  }
  return Object.freeze({SOURCE,FIELDS,CommentRepositoryError,createCommentRepository});
});
