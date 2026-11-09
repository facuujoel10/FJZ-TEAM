'use strict';
const SAVE_STATES=Object.freeze({
  PENDING:'pending',SAVING:'saving',CONFIRMED:'confirmed',
  RECOVERABLE_ERROR:'recoverable_error',FATAL_ERROR:'fatal_error',RETRY_PENDING:'retry_pending'
});
const SAVE_EVENTS=Object.freeze({
  START:'start',CONFIRM:'confirm',FAIL_RECOVERABLE:'fail_recoverable',
  FAIL_FATAL:'fail_fatal',QUEUE_RETRY:'queue_retry',RETRY:'retry'
});
const TRANSITIONS=Object.freeze({
  [SAVE_STATES.PENDING]:Object.freeze({[SAVE_EVENTS.START]:SAVE_STATES.SAVING}),
  [SAVE_STATES.SAVING]:Object.freeze({
    [SAVE_EVENTS.CONFIRM]:SAVE_STATES.CONFIRMED,
    [SAVE_EVENTS.FAIL_RECOVERABLE]:SAVE_STATES.RECOVERABLE_ERROR,
    [SAVE_EVENTS.FAIL_FATAL]:SAVE_STATES.FATAL_ERROR
  }),
  [SAVE_STATES.RECOVERABLE_ERROR]:Object.freeze({[SAVE_EVENTS.QUEUE_RETRY]:SAVE_STATES.RETRY_PENDING}),
  [SAVE_STATES.RETRY_PENDING]:Object.freeze({[SAVE_EVENTS.RETRY]:SAVE_STATES.SAVING}),
  [SAVE_STATES.CONFIRMED]:Object.freeze({}),
  [SAVE_STATES.FATAL_ERROR]:Object.freeze({})
});
function transitionSaveState(current,event){
  const next=TRANSITIONS[current]?.[event];
  if(!next)throw new Error('Invalid save transition: '+current+' -> '+event);
  return next;
}
function createSaveReceipt({state=SAVE_STATES.PENDING,operationId=null,serverConfirmedAt=null,error=null}={}){
  if(!Object.values(SAVE_STATES).includes(state))throw new Error('Unknown save state: '+state);
  if(state===SAVE_STATES.CONFIRMED&&!serverConfirmedAt)throw new Error('Confirmed save requires serverConfirmedAt');
  return Object.freeze({state,operationId,serverConfirmedAt,error});
}
module.exports=Object.freeze({SAVE_STATES,SAVE_EVENTS,TRANSITIONS,transitionSaveState,createSaveReceipt});
