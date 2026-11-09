(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.TeamFJZDate=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const DEFAULT_TIME_ZONE='America/Argentina/Buenos_Aires';
  const DATE_ONLY=/^\d{4}-\d{2}-\d{2}$/;
  function assertTimeZone(timeZone){
    const tz=String(timeZone||DEFAULT_TIME_ZONE);
    try{new Intl.DateTimeFormat('en-US',{timeZone:tz}).format(new Date(0));}
    catch(_e){throw new RangeError('Invalid time zone: '+tz);}
    return tz;
  }
  function asInstant(value){
    const d=value instanceof Date?new Date(value.getTime()):new Date(value);
    if(Number.isNaN(d.getTime()))throw new RangeError('Invalid timestamp');
    return d;
  }
  function parts(value,timeZone=DEFAULT_TIME_ZONE){
    const d=asInstant(value),tz=assertTimeZone(timeZone);
    const rows=new Intl.DateTimeFormat('en-US',{
      timeZone:tz,year:'numeric',month:'2-digit',day:'2-digit',
      hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23'
    }).formatToParts(d);
    return Object.fromEntries(rows.filter(x=>x.type!=='literal').map(x=>[x.type,x.value]));
  }
  function calendarDate(value=new Date(),timeZone=DEFAULT_TIME_ZONE){
    if(typeof value==='string'&&DATE_ONLY.test(value))return value;
    const p=parts(value,timeZone);
    return p.year+'-'+p.month+'-'+p.day;
  }
  function exactTimestamp(value=new Date()){return asInstant(value).toISOString();}
  function formatTimestamp(value,options={}){
    const d=asInstant(value);
    const locale=options.locale||'es-AR';
    const timeZone=assertTimeZone(options.timeZone||DEFAULT_TIME_ZONE);
    const formatOptions=Object.assign({
      year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'
    },options.format||{});
    return new Intl.DateTimeFormat(locale,Object.assign({timeZone},formatOptions)).format(d);
  }
  function describe(value=new Date(),timeZone=DEFAULT_TIME_ZONE){
    const d=asInstant(value);
    return Object.freeze({
      calendarDate:calendarDate(d,timeZone),
      exactTimestamp:d.toISOString(),
      timeZone:assertTimeZone(timeZone)
    });
  }
  return Object.freeze({DEFAULT_TIME_ZONE,calendarDate,exactTimestamp,formatTimestamp,describe});
});
