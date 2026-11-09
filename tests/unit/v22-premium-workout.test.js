const test=require('node:test');
const assert=require('node:assert/strict');
const premium=require('../../src/modules/workouts/premium-workout.js');

test('2A decimal normalization preserves dot and comma decimals',()=>{
  assert.equal(premium.normalizeDecimal('17.5'),'17.5');
  assert.equal(premium.normalizeDecimal('17,5'),'17.5');
  assert.equal(premium.normalizeDecimal('17..5'),'17.5');
});
test('2A field contracts use mobile-safe keyboards',()=>{
  assert.deepEqual(premium.fieldContract('weight'),{inputMode:'decimal',step:'0.5',min:'0',label:'Carga actual'});
  assert.deepEqual(premium.fieldContract('rir'),{inputMode:'decimal',step:'0.5',min:'0',max:'10',label:'RIR'});
  assert.deepEqual(premium.fieldContract('reps'),{inputMode:'numeric',step:'1',min:'0',label:'Repeticiones'});
});
test('2A comment duplicate gate preserves retry semantics',()=>{
  assert.equal(premium.beginCommentSubmit('exercise-a','texto','comment'),true);
  assert.equal(premium.beginCommentSubmit('exercise-a','texto','comment'),false);
  assert.equal(premium.endCommentSubmit('exercise-a',false),false);
  assert.equal(premium.beginCommentSubmit('exercise-a','texto','comment'),true);
  assert.equal(premium.endCommentSubmit('exercise-a',true),true);
  assert.equal(premium.commentDraft('exercise-a'),null);
});
