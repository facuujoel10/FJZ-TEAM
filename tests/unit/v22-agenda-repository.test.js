const test=require('node:test');
const assert=require('node:assert/strict');
const {
  createAgendaRepository,
  AgendaRepositoryError
}=require('../../src/data/agenda-repository.js');
const {readAgendaWithCompatibility}=require('../../src/data/agenda-read-policy.js');

const A1='10000000-0000-4000-8000-000000000001';
const A2='10000000-0000-4000-8000-000000000002';
const S1='50000000-0000-4000-8000-000000000001';
const R1='51000000-0000-4000-8000-000000000001';

function fakeSupabase(seed,{throwNetwork=false,errorByTable={}}={}){
  let calls=0;
  function from(table){
    calls++;
    const filters=[];
    const builder={
      select(){return builder;},
      eq(column,value){filters.push([column,value]);return builder;},
      order(){return builder;},
      maybeSingle(){
        if(throwNetwork)return Promise.reject(new TypeError('Failed to fetch'));
        const error=errorByTable[table]||null;
        if(error)return Promise.resolve({data:null,error});
        let rows=(seed[table]||[]).filter(row=>filters.every(([k,v])=>row[k]===v));
        return Promise.resolve({data:rows[0]||null,error:null});
      },
      then(resolve,reject){
        if(throwNetwork)return Promise.reject(new TypeError('Failed to fetch')).then(resolve,reject);
        const error=errorByTable[table]||null;
        let rows=(seed[table]||[]).filter(row=>filters.every(([k,v])=>row[k]===v));
        return Promise.resolve({data:error?null:rows,error}).then(resolve,reject);
      }
    };
    return builder;
  }
  return {client:{from},calls:()=>calls};
}

function seed(){
  return {
    athlete_schedule:[
      {id:S1,athlete_id:A1,coach_id:'coach',weekday:1,workout_day_name:'Día QA A',start_time:'09:00:00',active:true},
      {id:'50000000-0000-4000-8000-000000000002',athlete_id:A2,coach_id:'coach',weekday:3,workout_day_name:'Día QA B',start_time:'18:00:00',active:true}
    ],
    athlete_reminders:[
      {id:R1,athlete_id:A1,coach_id:'coach',title:'QA weekly',schedule_type:'weekly',reminder_date:null,weekday:1,remind_time:'08:00:00',active:true},
      {id:'51000000-0000-4000-8000-000000000002',athlete_id:A2,coach_id:'coach',title:'QA once',schedule_type:'once',reminder_date:'2026-01-20',weekday:null,remind_time:null,active:true}
    ]
  };
}

test('AgendaRepository lists one athlete and preserves historical date/time strings',async()=>{
  const f=fakeSupabase(seed());
  const repo=createAgendaRepository({supabase:f.client,ttlMs:15000,clock:()=>1000});
  const data=await repo.listForAthlete(A1);
  assert.equal(data.athleteId,A1);
  assert.equal(data.schedule.length,1);
  assert.equal(data.schedule[0].start_time,'09:00:00');
  assert.equal(data.reminders[0].remind_time,'08:00:00');

  const a2=await repo.listForAthlete(A2);
  assert.equal(a2.reminders[0].reminder_date,'2026-01-20');
});

test('AgendaRepository coalesces inflight reads and uses short cache',async()=>{
  const f=fakeSupabase(seed());
  const repo=createAgendaRepository({supabase:f.client,ttlMs:15000,clock:()=>1000});
  const [a,b]=await Promise.all([repo.listForAthlete(A1),repo.listForAthlete(A1)]);
  assert.equal(a,b);
  assert.equal(f.calls(),2);
  await repo.listForAthlete(A1);
  assert.equal(f.calls(),2);
});

test('AgendaRepository getById uses cached rows and nonexistent ids are controlled',async()=>{
  const f=fakeSupabase(seed());
  const repo=createAgendaRepository({supabase:f.client,clock:()=>1000});
  await repo.listForAthlete(A1);
  const before=f.calls();
  const event=await repo.getById(S1);
  assert.equal(event.kind,'schedule');
  assert.equal(event.row.workout_day_name,'Día QA A');
  assert.equal(f.calls(),before);

  const missing=await repo.getById('59999999-0000-4000-8000-000000000099');
  assert.equal(missing,null);
});

test('empty agenda is a valid authoritative result',async()=>{
  const f=fakeSupabase(seed());
  const repo=createAgendaRepository({supabase:f.client,clock:()=>1000});
  const data=await repo.listForAthlete('10000000-0000-4000-8000-000000000099');
  assert.deepEqual(data.schedule,[]);
  assert.deepEqual(data.reminders,[]);
});

test('network errors are classified and never cached as data',async()=>{
  const f=fakeSupabase(seed(),{throwNetwork:true});
  const repo=createAgendaRepository({supabase:f.client});
  await assert.rejects(
    ()=>repo.listForAthlete(A1),
    err=>err instanceof AgendaRepositoryError&&err.kind==='network'
  );
});

test('permission errors remain permission errors',async()=>{
  const f=fakeSupabase(seed(),{errorByTable:{athlete_schedule:{code:'42501',message:'permission denied'}}});
  const repo=createAgendaRepository({supabase:f.client});
  await assert.rejects(
    ()=>repo.listForAthlete(A1),
    err=>err instanceof AgendaRepositoryError&&err.kind==='permission'
  );
});

test('enabled canonical empty result never falls back to legacy',async()=>{
  let legacyCalls=0;
  const result=await readAgendaWithCompatibility({
    enabled:true,
    canonicalRead:async()=>({source:'agenda-repository-v22',schedule:[],reminders:[]}),
    legacyRead:async()=>{legacyCalls++;return {source:'legacy'}}
  });
  assert.equal(result.source,'agenda-repository-v22');
  assert.equal(legacyCalls,0);
});

test('enabled canonical permission denial never falls back to legacy',async()=>{
  let legacyCalls=0;
  await assert.rejects(
    ()=>readAgendaWithCompatibility({
      enabled:true,
      canonicalRead:async()=>{throw new AgendaRepositoryError('permission','listForAthlete',{message:'denied'})},
      legacyRead:async()=>{legacyCalls++;return {source:'legacy'}}
    }),
    err=>err.kind==='permission'
  );
  assert.equal(legacyCalls,0);
});

test('legacy path is only used when feature is explicitly disabled',async()=>{
  let canonicalCalls=0;
  const result=await readAgendaWithCompatibility({
    enabled:false,
    canonicalRead:async()=>{canonicalCalls++;return {source:'canonical'}},
    legacyRead:async()=>({source:'legacy-v312',schedule:[],reminders:[]})
  });
  assert.equal(result.source,'legacy-v312');
  assert.equal(canonicalCalls,0);
});
