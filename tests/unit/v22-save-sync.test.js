const test=require('node:test');
const assert=require('node:assert/strict');
const save=require('../../src/core/save-contract.js');

test('reference tracker cannot report confirmed before server evidence',()=>{
  const tracker=save.createSaveTracker({operationId:'agenda-ref-1'});
  assert.equal(tracker.snapshot().state,save.SAVE_STATES.PENDING);
  tracker.start();
  assert.equal(tracker.snapshot().state,save.SAVE_STATES.SAVING);
  assert.throws(()=>tracker.confirm(),/serverConfirmedAt/);
  assert.equal(tracker.snapshot().state,save.SAVE_STATES.SAVING);
});

test('reference tracker separates recoverable error, retry pending and retry',()=>{
  const tracker=save.createSaveTracker({operationId:'agenda-ref-2'});
  tracker.start();
  tracker.failRecoverable({message:'offline'});
  assert.equal(tracker.snapshot().state,save.SAVE_STATES.RECOVERABLE_ERROR);
  tracker.queueRetry();
  assert.equal(tracker.snapshot().state,save.SAVE_STATES.RETRY_PENDING);
  tracker.retry();
  assert.equal(tracker.snapshot().state,save.SAVE_STATES.SAVING);
});

test('reference tracker records durable confirmation only after explicit server timestamp',()=>{
  const tracker=save.createSaveTracker({operationId:'agenda-ref-3'});
  tracker.start();
  tracker.confirm('2026-11-09T12:00:00.000Z');
  const receipt=tracker.snapshot();
  assert.equal(receipt.state,save.SAVE_STATES.CONFIRMED);
  assert.equal(receipt.serverConfirmedAt,'2026-11-09T12:00:00.000Z');
  assert.equal(tracker.history().length,3);
});

test('fatal error is terminal in the reference tracker',()=>{
  const tracker=save.createSaveTracker({operationId:'agenda-ref-4'});
  tracker.start();
  tracker.failFatal({message:'invalid payload'});
  assert.equal(tracker.snapshot().state,save.SAVE_STATES.FATAL_ERROR);
  assert.throws(()=>tracker.retry(),/Invalid save transition/);
});
