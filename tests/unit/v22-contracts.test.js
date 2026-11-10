const test=require('node:test');
const assert=require('node:assert/strict');
const save=require('../../src/core/save-contract.js');
const repos=require('../../src/data/repository-contracts.js');
test('save states are explicit',()=>assert.deepEqual(Object.values(save.SAVE_STATES).sort(),['confirmed','fatal_error','pending','recoverable_error','retry_pending','saving']));
test('confirmed save requires server evidence',()=>assert.throws(()=>save.createSaveReceipt({state:save.SAVE_STATES.CONFIRMED}),/serverConfirmedAt/));
test('recoverable save has explicit retry path',()=>{
  let s=save.transitionSaveState(save.SAVE_STATES.PENDING,save.SAVE_EVENTS.START);
  s=save.transitionSaveState(s,save.SAVE_EVENTS.FAIL_RECOVERABLE);
  s=save.transitionSaveState(s,save.SAVE_EVENTS.QUEUE_RETRY);
  s=save.transitionSaveState(s,save.SAVE_EVENTS.RETRY);
  assert.equal(s,save.SAVE_STATES.SAVING);
});
test('all repository boundaries are declared',()=>assert.deepEqual(Object.keys(repos.REPOSITORY_CONTRACTS).sort(),['AgendaRepository','CheckinRepository','CoachRepository','CommentRepository','NutritionRepository','ProgressRepository','WorkoutRepository']));
test('Agenda pilot delegates without UI or Supabase coupling',async()=>{
  const adapter={async listForAthlete(){return [{id:'a1'}]},async getById(id){return {id}}};
  const repo=repos.createAgendaRepositoryPilot(adapter);
  assert.deepEqual(await repo.listForAthlete('s1',{}),[{id:'a1'}]);
  assert.deepEqual(await repo.getById('a1'),{id:'a1'});
  assert.ok(Object.isFrozen(repo));
});
test('Agenda pilot rejects incomplete adapters',()=>assert.throws(()=>repos.createAgendaRepositoryPilot({listForAthlete(){}}),/getById/));

test('Comment read pilot delegates without exposing write operations',async()=>{
  const adapter={async listForAthlete(){return {rows:[]}},async listForSession(){return {rows:[{id:'c1'}]}},async listPending(){return {rows:[]}},async getById(){return null}};
  const repo=repos.createCommentRepositoryPilot(adapter);
  assert.deepEqual(await repo.listForAthlete('a1',{}),{rows:[]});
  assert.deepEqual(await repo.listForSession('ss-a',{}),{rows:[{id:'c1'}]});
  assert.deepEqual(await repo.listPending({}),{rows:[]});
  assert.equal(await repo.getById('c1'),null);
  assert.equal(typeof repo.markReviewed,'undefined');
  assert.ok(Object.isFrozen(repo));
});
test('Comment read pilot rejects incomplete adapters',()=>assert.throws(()=>repos.createCommentRepositoryPilot({listForAthlete(){},listForSession(){},listPending(){}}),/getById/));
