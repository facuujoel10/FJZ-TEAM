const test=require('node:test');const assert=require('node:assert/strict');
const analytics=require('../../src/modules/coach/analytics-followup.js');
const engine=require('../../src/modules/workouts/intelligent-training.js');
const sessions=[
 {id:'s1',date:'2026-11-01T10:00:00Z',cloudConfirmed:true,dayName:'A',exerciseResults:[{exerciseUid:'press',exerciseName:'Press QA',sets:[[15,10,2],[15,9,2]]}]},
 {id:'s2',date:'2026-11-08T10:00:00Z',cloudConfirmed:true,dayName:'A',exerciseResults:[{exerciseUid:'press',exerciseName:'Press QA',sets:[[17.5,10,2],[17.5,9,2]]}]},
 {id:'draft',date:'2026-11-09T10:00:00Z',cloudConfirmed:false,dayName:'A',exerciseResults:[{exerciseUid:'press',exerciseName:'Press QA',sets:[[99,10,2]]}]}
];
test('3C exercise series uses confirmed sessions and TeamFJZIntelligentTraining comparison authority',()=>{
 const rows=analytics.exerciseSeries({sessions},engine);assert.equal(rows.length,1);assert.equal(rows[0].points.length,2);
 const last=rows[0].points.at(-1);assert.equal(last.load,17.5);assert.equal(last.analysis.trend,'improved');assert.match(last.analysis.comparison,/15 kg/);assert.doesNotMatch(last.analysis.comparison,/99/);
});
test('3C measurement timeline is chronological and neutral',()=>{
 const rows=analytics.measurementTimeline([{id:'a',measured_on:'2026-11-01',weight_kg:72.5,waist_cm:80},{id:'b',measured_on:'2026-11-08',weight_kg:71.8,waist_cm:79}]);
 const w=rows.find(x=>x.key==='weight_kg'),waist=rows.find(x=>x.key==='waist_cm');assert.equal(w.latest.value,71.8);assert.ok(Math.abs(w.delta+0.7)<1e-9);assert.equal(waist.delta,-1);
});
test('3C check-in timeline never invents a combined score',()=>{
 const rows=analytics.checkinTimeline([{id:'a',week_start:'2026-11-01',sleep_quality:7,recovery_level:6},{id:'b',week_start:'2026-11-08',sleep_quality:8,recovery_level:8}]);
 assert.equal(rows.find(x=>x.key==='sleep_quality').delta,1);assert.equal(rows.find(x=>x.key==='recovery_level').delta,2);assert.equal(rows.some(x=>x.key==='score'),false);
});
test('3C priorities are evidence-backed and discomfort precedes generic comment/check-in',()=>{
 const rows=analytics.priorityReasons({comments:[{id:'c1',status:'pending',feedback_type:'comment',exercise_name:'Remo'},{id:'c2',status:'pending',feedback_type:'discomfort',exercise_name:'Press'}],checkins:[{id:'k1',week_start:'2026-11-08',reviewed_at:null}],sessions,engine});
 assert.equal(rows[0].kind,'comment');assert.equal(rows[0].evidenceId,'c2');assert.match(rows[0].title,/Molestia/);assert.ok(rows.every(x=>x.evidenceId));
});
test('3C sparse data yields observations only, never fabricated trends',()=>{
 assert.deepEqual(analytics.exerciseSeries({sessions:[sessions[0]]},engine)[0].points[0].analysis.trend,'no-reference');
 const m=analytics.measurementTimeline([{id:'a',measured_on:'2026-11-01',weight_kg:72.5}])[0];assert.equal(m.delta,null);
});