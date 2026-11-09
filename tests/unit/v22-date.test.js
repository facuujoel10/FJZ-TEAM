const test=require('node:test');
const assert=require('node:assert/strict');
const dates=require('../../src/core/date.js');
const TZ='America/Argentina/Buenos_Aires';
test('Argentina local date at 20:59',()=>assert.equal(dates.calendarDate('2026-11-09T23:59:00Z',TZ),'2026-11-09'));
test('Argentina does not roll at 21:00 because UTC changed day',()=>assert.equal(dates.calendarDate('2026-11-10T00:00:00Z',TZ),'2026-11-09'));
test('Argentina local date at 23:59',()=>assert.equal(dates.calendarDate('2026-11-10T02:59:00Z',TZ),'2026-11-09'));
test('Argentina advances after local midnight at 00:01',()=>assert.equal(dates.calendarDate('2026-11-10T03:01:00Z',TZ),'2026-11-10'));
test('historical date-only records stay unchanged',()=>assert.equal(dates.calendarDate('2025-03-01',TZ),'2025-03-01'));
test('calendar date and exact timestamp are distinct',()=>{
  const d=dates.describe('2026-11-10T00:00:00Z',TZ);
  assert.equal(d.calendarDate,'2026-11-09');
  assert.equal(d.exactTimestamp,'2026-11-10T00:00:00.000Z');
});
test('invalid timestamps fail explicitly',()=>assert.throws(()=>dates.calendarDate('not-a-date',TZ),/Invalid timestamp/));
