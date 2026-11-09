(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.TeamFJZAgendaReadPolicy=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  async function readAgendaWithCompatibility({enabled,canonicalRead,legacyRead}={}){
    if(typeof canonicalRead!=='function')throw new TypeError('canonicalRead is required');
    if(typeof legacyRead!=='function')throw new TypeError('legacyRead is required');
    if(!enabled)return legacyRead();
    // Fail closed: once the canonical path is enabled, empty data and errors
    // are authoritative. Never escape an RLS/network denial through legacy.
    return canonicalRead();
  }

  return Object.freeze({readAgendaWithCompatibility});
});
