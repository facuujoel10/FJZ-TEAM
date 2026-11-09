(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.TeamFJZReadErrors=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const KINDS=Object.freeze({NETWORK:'network',AUTHORIZATION:'authorization',NOT_FOUND:'not_found',QUERY:'query',INTEGRITY:'integrity',SESSION_CANCELLED:'session_cancelled'});
  class RepositoryReadError extends Error{
    constructor(kind,operation,cause,options={}){
      const publicMessage=options.publicMessage||(kind===KINDS.AUTHORIZATION?'No tenés permiso para consultar estos datos.':kind===KINDS.NOT_FOUND?'El registro solicitado no está disponible.':kind===KINDS.SESSION_CANCELLED?'La sesión cambió durante la consulta.':'No pudimos completar la consulta.');
      super(publicMessage);this.name='RepositoryReadError';this.kind=kind;this.operation=operation;this.code=cause?.code||null;this.status=Number(cause?.status||cause?.statusCode||0)||null;this.publicMessage=publicMessage;this.cause=cause||null;
    }
  }
  function classifyReadError(error){
    if(error instanceof RepositoryReadError)return error.kind;
    const status=Number(error?.status||error?.statusCode||0),code=String(error?.code||''),msg=String(error?.message||error||'').toLowerCase();
    if(status===401||status===403||code==='42501'||/permission|not authorized|unauthorized|forbidden|jwt/.test(msg))return KINDS.AUTHORIZATION;
    if(error instanceof TypeError||status===0||/network|failed to fetch|fetch failed|connection|econn|timeout/.test(msg))return KINDS.NETWORK;
    if(/integrity|duplicate|ambiguous/.test(msg))return KINDS.INTEGRITY;
    return KINDS.QUERY;
  }
  function wrapReadError(error,operation){return error instanceof RepositoryReadError?error:new RepositoryReadError(classifyReadError(error),operation,error)}
  function cancelled(operation){return new RepositoryReadError(KINDS.SESSION_CANCELLED,operation,null)}
  return Object.freeze({KINDS,RepositoryReadError,classifyReadError,wrapReadError,cancelled});
});
