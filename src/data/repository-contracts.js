'use strict';
const REPOSITORY_CONTRACTS=Object.freeze({
  WorkoutRepository:Object.freeze(['getRoutine','getSession','saveSession']),
  CommentRepository:Object.freeze(['listPending','getById','markReviewed']),
  NutritionRepository:Object.freeze(['getPlan','listLogs','saveLog']),
  ProgressRepository:Object.freeze(['listMeasurements','saveMeasurement','listPhotos']),
  CheckinRepository:Object.freeze(['list','save','review']),
  AgendaRepository:Object.freeze(['listForAthlete','getById']),
  CoachRepository:Object.freeze(['listAthletes','getAthleteSnapshot'])
});
function assertRepositoryShape(name,candidate){
  const methods=REPOSITORY_CONTRACTS[name];
  if(!methods)throw new Error('Unknown repository contract: '+name);
  if(!candidate||typeof candidate!=='object')throw new TypeError(name+' adapter must be an object');
  const missing=methods.filter(method=>typeof candidate[method]!=='function');
  if(missing.length)throw new TypeError(name+' missing methods: '+missing.join(', '));
  return true;
}
function createAgendaRepositoryPilot(adapter){
  assertRepositoryShape('AgendaRepository',adapter);
  return Object.freeze({
    listForAthlete:(athleteId,range)=>adapter.listForAthlete(athleteId,range),
    getById:id=>adapter.getById(id)
  });
}
module.exports=Object.freeze({REPOSITORY_CONTRACTS,assertRepositoryShape,createAgendaRepositoryPilot});
