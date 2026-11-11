const test=require('node:test');
const assert=require('node:assert/strict');
const engine=require('../../src/modules/workouts/intelligent-training.js');

function session(id,date,exerciseUid,sets,extra={}){
  return {id,date,status:'completed',confirmed:true,cloudConfirmed:true,exerciseResults:[{exerciseUid,sets,...extra}]};
}

test('2C timer uses absolute target time and prevents duplicate ticker semantics',()=>{
  const s=engine.startRest({sessionId:'ss-a',exerciseUid:'press',durationSeconds:90});
  assert.equal(s.state,'running');assert.equal(engine.timerCount(),1);
  const firstTarget=s.targetAt;
  const again=engine.startRest({sessionId:'ss-a',exerciseUid:'press',durationSeconds:60});
  assert.equal(engine.timerCount(),1);assert.notEqual(again.targetAt,firstTarget);
  const paused=engine.pauseRest();assert.equal(paused.state,'paused');assert.equal(engine.timerCount(),0);
  const resumed=engine.resumeRest();assert.equal(resumed.state,'running');assert.equal(engine.timerCount(),1);
  const reset=engine.resetRest();assert.equal(reset.state,'paused');assert.equal(reset.remainingMs,reset.durationMs);
  engine.skipRest();assert.equal(engine.timerCount(),0);assert.equal(engine.timerSnapshot(),null);
});

test('2C timer start checkpoints workout identity through certified V145 autosave',()=>{
  let calls=0;
  global.__fjzPersistWorkoutDraftV145=()=>{calls++};
  engine.startRest({sessionId:'timer-checkpoint',exerciseUid:'press',durationSeconds:30});
  assert.equal(calls,1);
  engine.skipRest();
  delete global.__fjzPersistWorkoutDraftV145;
});

test('2C timer recalculates from absolute time and clears authority on session change',()=>{
  const s=engine.startRest({sessionId:'timer-a',exerciseUid:'press',durationSeconds:30});
  const future=engine.advance(s.startedAt+45000);
  assert.equal(future.state,'finished');assert.equal(future.remainingMs,0);
  engine.startRest({sessionId:'timer-a',exerciseUid:'press',durationSeconds:30});
  assert.equal(engine.timerCount(),1);
  const switched=engine.restoreTimer('timer-b');
  assert.equal(switched,null);assert.equal(engine.timerSnapshot(),null);assert.equal(engine.timerCount(),0);
});

test('2C comparison detects real load and same-load rep improvements without percentages',()=>{
  const a=session('a','2026-11-09T10:00:00Z','press',[[80,10,2]]);
  const b=session('b','2026-11-10T10:00:00Z','press',[[82.5,10,2]]);
  const load=engine.analyzeExercise({sessions:[a,b],currentSession:b,exerciseUid:'press',confirmedSessionId:'b'});
  assert.equal(load.comparable,true);
  assert.equal(load.records[0].type,'load');
  assert.equal(load.records[0].message,'80 kg × 10 → 82.5 kg × 10');
  assert.ok(!load.records[0].message.includes('%'));

  const c=session('c','2026-11-11T10:00:00Z','press',[[82.5,12,2]]);
  const reps=engine.analyzeExercise({sessions:[a,b,c],currentSession:c,exerciseUid:'press',confirmedSessionId:'c'});
  assert.equal(reps.records[0].type,'reps_same_load');
  assert.equal(reps.records[0].message,'82.5 kg × 10 → 82.5 kg × 12');
});

test('2C comparisons preserve exercise identity and modality compatibility',()=>{
  const a=session('a','2026-11-09T10:00:00Z','pullup',[[10,8,2]],{loadMode:'bodyweight-added'});
  const b=session('b','2026-11-10T10:00:00Z','pullup',[[30,10,2]],{loadMode:'assisted'});
  const x=engine.analyzeExercise({sessions:[a,b],currentSession:b,exerciseUid:'pullup',confirmedSessionId:'b'});
  assert.equal(x.comparable,false);
  assert.match(x.reason,/referencia comparable/i);

  const wrong=session('c','2026-11-09T11:00:00Z','row',[[100,10,2]]);
  const d=session('d','2026-11-11T10:00:00Z','press',[[50,10,2]]);
  const y=engine.analyzeExercise({sessions:[wrong,d],currentSession:d,exerciseUid:'press',confirmedSessionId:'d'});
  assert.equal(y.comparable,false);
});

test('2C incomplete, warm-up and intensification sets are excluded from comparable work sets',()=>{
  const r={sets:[[20,10,3],[40,8,2],[50,null,1],[45,8,1]],setTypes:['warmup','work','work','dropset']};
  const sets=engine.workSets(r);
  assert.deepEqual(sets.map(x=>[x.load,x.reps]),[[40,8]]);
});

test('2C same-day sessions remain distinct and previous comparable follows exact chronology',()=>{
  const a=session('a','2026-11-10T08:00:00Z','press',[[60,10,2]]);
  const b=session('b','2026-11-10T18:00:00Z','press',[[62.5,10,2]]);
  const d=engine.analyzeExercise({sessions:[a,b],currentSession:b,exerciseUid:'press',confirmedSessionId:'b'});
  assert.equal(d.previousSessionId,'a');assert.equal(d.previous.load,60);assert.equal(d.current.load,62.5);
});

test('2C suggestions are labeled, RIR-aware and never mutate coach prescription',()=>{
  const analysis={comparable:true,current:{load:60,reps:12,rir:2},previous:{load:60,reps:10,rir:2}};
  const prescription={load:60,reps:'8-12',rir:2};
  const before=JSON.stringify(prescription);
  const s=engine.progressionSuggestion(analysis);
  assert.equal(s.label,'Sugerencia calculada');
  assert.match(s.message,/Coach puede considerar/i);
  assert.equal(JSON.stringify(prescription),before);

  const hard=engine.progressionSuggestion({comparable:true,current:{load:60,reps:12,rir:0},previous:{load:60,reps:10,rir:1}});
  assert.match(hard.message,/No se sugiere aumentar/i);
});

test('2C summary only exists for confirmed session and counts valid data',()=>{
  const a=session('a','2026-11-09T10:00:00Z','press',[[80,10,2]]);
  const b={id:'b',date:'2026-11-10T10:00:00Z',dayName:'Pecho',exerciseResults:[{exerciseUid:'press',exerciseName:'Press banca',sets:[[82.5,10,2]]}]};
  assert.equal(engine.workoutSummary({sessions:[a,b],currentSession:b,confirmedSessionId:null}),null);
  const s=engine.workoutSummary({sessions:[a,b],currentSession:b,confirmedSessionId:'b',feedbackRows:[{session_id:'b',exercise_uid:'press'}]});
  assert.equal(s.dayName,'Pecho');assert.equal(s.totalSets,1);assert.equal(s.exercises.length,1);assert.equal(s.commentCount,1);
});

test('2C personal record requires prior comparable history and confirmed current session',()=>{
  const a=session('a','2026-11-09T10:00:00Z','press',[[80,10,2]]);
  const b=session('b','2026-11-10T10:00:00Z','press',[[82.5,10,2]]);
  const prs=engine.personalRecords({sessions:[a,b],currentSession:b,exerciseUid:'press',confirmedSessionId:'b'});
  assert.equal(prs[0].type,'all_time_load');
  const unconfirmed={...b,status:undefined,confirmed:false,cloudConfirmed:false};
  assert.deepEqual(engine.personalRecords({sessions:[a,unconfirmed],currentSession:unconfirmed,exerciseUid:'press'}),[]);
});


test('2C assisted and bodyweight modes use mode-correct progression semantics',()=>{
  const a=session('a','2026-11-09T10:00:00Z','pullup',[[30,8,2]],{loadMode:'assisted'});
  const b=session('b','2026-11-10T10:00:00Z','pullup',[[25,8,2]],{loadMode:'assisted'});
  const assisted=engine.analyzeExercise({sessions:[a,b],currentSession:b,exerciseUid:'pullup',confirmedSessionId:'b'});
  assert.equal(assisted.records[0].type,'less_assistance');

  const c1=session('c1','2026-11-09T10:00:00Z','pullup-bw',[[0,8,2]],{loadMode:'bodyweight'});
  const c2=session('c2','2026-11-10T10:00:00Z','pullup-bw',[[0,10,2]],{loadMode:'bodyweight'});
  const bw=engine.analyzeExercise({sessions:[c1,c2],currentSession:c2,exerciseUid:'pullup-bw',confirmedSessionId:'c2'});
  assert.equal(bw.records[0].type,'bodyweight_reps');
});


test('2C suggestions never treat bodyweight reps as automatic load progression',()=>{
  const s=engine.progressionSuggestion({comparable:true,mode:'bodyweight',current:{load:0,reps:12,rir:2},previous:{load:0,reps:10,rir:2}});
  assert.match(s.message,/sin asumir automáticamente que deba añadir lastre/i);
  assert.doesNotMatch(s.message,/progresar la carga/i);
});

test('2C assisted suggestion speaks in assistance, not external load',()=>{
  const s=engine.progressionSuggestion({comparable:true,mode:'assisted',current:{load:25,reps:10,rir:2},previous:{load:30,reps:10,rir:2}});
  assert.match(s.message,/menor asistencia/i);
  assert.doesNotMatch(s.message,/subida de carga/i);
});


test('2C completed local status alone is not server confirmation',()=>{
  const local={id:'local-only',date:'2026-11-10T10:00:00Z',status:'completed',exerciseResults:[{exerciseUid:'press',sets:[[80,10,2]]}]};
  assert.equal(engine.sessionConfirmed(local),false);
  assert.deepEqual(engine.personalRecords({sessions:[local],currentSession:local,exerciseUid:'press'}),[]);
});

test('2C local confirmed flag alone is not server-verifiable confirmation',()=>{
  const local={id:'local-confirmed-only',date:'2026-11-10T10:00:00Z',status:'completed',confirmed:true,cloudConfirmed:false,exerciseResults:[{exerciseUid:'press',sets:[[80,10,2]]}]};
  assert.equal(engine.sessionConfirmed(local),false);
  assert.deepEqual(engine.analyzeExercise({sessions:[local],currentSession:local,exerciseUid:'press'}).records,[]);
  const persisted={...local,id:'persisted',source_session_id:'server-source-session'};
  assert.equal(engine.sessionConfirmed(persisted),true);
});

test('2C unconfirmed prior sessions are excluded from comparisons and records',()=>{
  const draft={id:'draft',date:'2026-11-09T10:00:00Z',status:'completed',exerciseResults:[{exerciseUid:'press',sets:[[100,10,2]]}]};
  const current=session('confirmed','2026-11-10T10:00:00Z','press',[[80,10,2]]);
  const a=engine.analyzeExercise({sessions:[draft,current],currentSession:current,exerciseUid:'press'});
  assert.equal(a.comparable,false);
  assert.match(a.reason,/referencia comparable confirmada/i);
  assert.deepEqual(engine.personalRecords({sessions:[draft,current],currentSession:current,exerciseUid:'press'}),[]);
});

test('2C lower performance is comparison, not positive improvement',()=>{
  const a=session('a','2026-11-09T10:00:00Z','press',[[80,10,2]]);
  const b=session('b','2026-11-10T10:00:00Z','press',[[75,8,1]]);
  const x=engine.analyzeExercise({sessions:[a,b],currentSession:b,exerciseUid:'press'});
  assert.equal(x.comparable,true);
  assert.equal(x.trend,'lower');
  assert.equal(x.improvements.length,0);
  assert.match(x.comparison,/80 kg × 10/);
  assert.equal(engine.progressionSuggestion(x).kind,'maintain');
});

test('2C higher load with fewer reps can be a load record without being global improvement',()=>{
  const a=session('a','2026-11-09T10:00:00Z','press',[[80,10,2]]);
  const b=session('b','2026-11-10T10:00:00Z','press',[[82.5,5,1]]);
  const x=engine.analyzeExercise({sessions:[a,b],currentSession:b,exerciseUid:'press'});
  const prs=engine.personalRecords({sessions:[a,b],currentSession:b,exerciseUid:'press'});
  assert.equal(x.records[0].type,'load');
  assert.equal(x.improvements.length,0);
  assert.equal(x.trend,'mixed');
  assert.equal(prs[0].type,'all_time_load');
});

test('2C empty external load is invalid while explicit bodyweight can use zero load',()=>{
  assert.equal(engine.workSets({sets:[['',10,2]],loadMode:'external'}).length,0);
  assert.deepEqual(engine.workSets({sets:[['',10,2]],loadMode:'bodyweight'}).map(x=>[x.load,x.reps]),[[0,10]]);
  assert.equal(engine.workSets({sets:[[0,10,2]],loadMode:'bodyweight-added'}).length,0);
});
