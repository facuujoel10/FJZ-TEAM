const test=require('node:test');const assert=require('node:assert/strict');const mod=require('../../src/modules/tracking/progress-checkins-premium.js');
test('V22 4B neutral progress and missing values',()=>{assert.equal(mod.VERSION,'22.4B');assert.equal(mod.neutralDelta(70,72,'kg'),'+2.0 kg');assert.equal(mod.neutralDelta(72,70,'kg'),'-2.0 kg');assert.equal(mod.measurementValue({weight_kg:null},'weight_kg'),null);assert.equal(mod.measurementValue({weight_kg:0},'weight_kg'),0)});
test('V22 4B review state uses persisted timestamps',()=>{assert.equal(mod.reviewState(null),'none');assert.equal(mod.reviewState({submitted_at:'2026-11-15T10:00:00Z',reviewed_at:null}),'pending');assert.equal(mod.reviewState({submitted_at:'2026-11-15T10:00:00Z',reviewed_at:'2026-11-15T09:00:00Z'}),'pending');assert.equal(mod.reviewState({submitted_at:'2026-11-15T10:00:00Z',reviewed_at:'2026-11-15T11:00:00Z'}),'reviewed')});
test('V22 4B preserves existing independent check-in scales',()=>{const keys=mod.CHECKS.map(x=>x[1]);assert.deepEqual(keys,['sleep_quality','recovery_level','hunger_level','stress_level','energy_level','mood_level','motivation_level','adherence_level']);assert.equal(keys.includes('score'),false);assert.equal(keys.includes('difficulty'),false)});
test('V22 4B markup is structurally new without invented score',()=>{const p=mod.progressView(false),c=mod.checkinsView(false);assert.match(p,/PROGRESO FÍSICO/);assert.match(p,/Tu evolución, sin ruido/);assert.match(p,/FOTOGRAFÍAS/);assert.match(c,/Estado físico/);assert.match(c,/Sensaciones/);assert.match(c,/Adherencia y evolución/);assert.match(c,/Comentarios/);assert.doesNotMatch(c,/readiness|score global|promedio general/i)});
test('Last weight and variation skip later measurements without weight',t=>{
  const original=globalThis.__fjzProgressCheckinsContextV22; t.after(()=>{if(original)globalThis.__fjzProgressCheckinsContextV22=original;else delete globalThis.__fjzProgressCheckinsContextV22});
  globalThis.__fjzProgressCheckinsContextV22=()=>({tracking:{measurements:[
    {measured_on:'2026-11-23',weight_kg:70},
    {measured_on:'2026-11-24',weight_kg:71},
    {measured_on:'2026-11-25',waist_cm:80}
  ]}});
  const html=mod.progressView(false);
  assert.match(html,/Último peso<\/small><strong>71 <i>kg/);
  assert.match(html,/\+1\.0 kg/);
});
