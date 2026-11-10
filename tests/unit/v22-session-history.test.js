const test=require('node:test');
const assert=require('node:assert/strict');
const h=require('../../src/modules/workouts/session-history.js');

test('2B same draft restores same session id and new same-day instance gets another id',()=>{
  h.clear();
  const first=h.ensureSessionId({studentId:'s1',dayId:'d1'});
  assert.ok(h.validSessionId(first));
  const restored=h.ensureSessionId({studentId:'s1',dayId:'d1',priorSessionId:first});
  assert.equal(restored,first);
  h.clear(first);
  const second=h.ensureSessionId({studentId:'s1',dayId:'d1'});
  assert.notEqual(second,first);
});
test('2B active identity is isolated by student/day',()=>{
  h.clear(); const a=h.ensureSessionId({studentId:'a',dayId:'day'});
  const b=h.ensureSessionId({studentId:'b',dayId:'day'});
  assert.notEqual(a,b);assert.equal(h.current().studentId,'b');
});
test('2B exact comments win; historical compatibility ignores linked rows from other sessions',()=>{
  const session={id:'ss-current',date:'2026-11-09T10:00:00Z',dayId:'day-a'};
  const rows=[
    {id:'c1',session_id:'ss-current',exercise_uid:'press',message:'exacto'},
    {id:'c2',session_id:'ss-other',exercise_uid:'press',message:'otro'},
    {id:'c3',session_id:null,exercise_uid:'press',workout_day_id:'day-a',created_at:'2026-11-09T10:01:00Z',message:'legacy'}
  ];
  const exact=h.feedbackForSession(rows,session,'press');
  assert.deepEqual(exact.map(x=>x.id),['c1']);
  const legacy=h.feedbackForSession(rows,{...session,id:'ss-no-exact'},'press');
  assert.deepEqual(legacy.map(x=>x.id),['c3']);
  assert.equal(legacy[0].linkMode,'historical-compatible');
});
test('2B comparison uses concrete best load and reps without percentages',()=>{
  const sessions=[
    {id:'a',date:'2026-11-08T10:00:00Z',exerciseResults:[{exerciseUid:'press',sets:[[20,10,2],[22.5,8,2]]}]},
    {id:'b',date:'2026-11-09T10:00:00Z',exerciseResults:[{exerciseUid:'press',sets:[[22.5,10,2],[25,8,2]]}]}
  ];
  const d=h.compareExercise(sessions,'b','press');
  assert.equal(d.previous.load,22.5);assert.equal(d.current.load,25);assert.equal(d.loadDelta,2.5);
});
