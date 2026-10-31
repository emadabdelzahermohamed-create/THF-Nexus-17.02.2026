const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const summary = require(path.resolve(__dirname, '../../android/app/src/main/assets/pulse/workout-work-summary.js'));
const pulse = path.resolve(__dirname, '../../android/app/src/main/assets/pulse');
const app = fs.readFileSync(path.join(pulse, 'app.js'), 'utf8');
const html = fs.readFileSync(path.join(pulse, 'index.html'), 'utf8');
const formatDuration = seconds => String(Math.floor(seconds / 60)).padStart(2, '0') + ':' + String(seconds % 60).padStart(2, '0');
const elapsedMs = set => Number(set.durationSeconds) * 1000 - Number(set.durationRemainingMs);

test('repetition-based sessions retain completed kilogram volume', () => {
  const result = summary.summarize([], [
    { complete: true, load: 20, reps: 8 },
    { complete: false, load: 30, reps: 5 }
  ]);
  assert.deepEqual(result, { volumeKg: 160, timeSeconds: 0, timedSetCount: 0 });
  assert.equal(summary.format(result, 'Time', formatDuration), '160 kg');
});

test('timed active work reports elapsed time instead of a misleading zero-kilogram value', () => {
  const result = summary.summarize([], [
    { durationSeconds: 30, durationRemainingMs: 5000, complete: false }
  ], elapsedMs);
  assert.deepEqual(result, { volumeKg: 0, timeSeconds: 25, timedSetCount: 1 });
  assert.equal(summary.format(result, 'Time', formatDuration), 'Time: 00:25');
});

test('program history combines prior load volume with elapsed timed work', () => {
  const entries = [{ sets: [{ complete: true, load: 20, reps: 5 }] }];
  const current = [{ durationSeconds: 30, durationRemainingMs: 0, complete: true }];
  const result = summary.summarize(entries, current, elapsedMs);
  assert.deepEqual(result, { volumeKg: 100, timeSeconds: 30, timedSetCount: 1 });
  assert.equal(summary.format(result, 'الوقت', formatDuration), '100 kg · الوقت: 00:30');
});

test('completed legacy timed sets without a remaining-time field count their prescribed duration', () => {
  const result = summary.summarize([], [{ durationSeconds: 45, complete: true }], () => 0);
  assert.deepEqual(result, { volumeKg: 0, timeSeconds: 45, timedSetCount: 1 });
  assert.equal(summary.format(result, 'Time', formatDuration), 'Time: 00:45');
});

test('unstarted timed work and invalid durations do not inflate elapsed time', () => {
  const result = summary.summarize([], [
    { durationSeconds: 40, durationRemainingMs: 40000, complete: false },
    { durationSeconds: -5, durationRemainingMs: 0, complete: true }
  ], elapsedMs);
  assert.deepEqual(result, { volumeKg: 0, timeSeconds: 0, timedSetCount: 1 });
});

test('time-only summaries omit kilogram volume when no completed repetitions exist', () => {
  const result = summary.summarize([], [{ durationSeconds: 30, durationRemainingMs: 30000 }], elapsedMs);
  assert.equal(summary.format(result, 'الوقت', formatDuration), 'الوقت: 00:00');
});

test('the active workout loads and renders the bilingual work summary helper', () => {
  assert.ok(html.indexOf('./workout-work-summary.js') < html.indexOf('./app.js'));
  assert.match(app, /window\.THF_WORKOUT_WORK_SUMMARY\.summarize\(/);
  assert.match(app, /window\.THF_WORKOUT_WORK_SUMMARY\.format\(summary, t\('time'\), formatDuration\)/);
  assert.match(app, /\$\('sessionWorkSummary'\)\.textContent = sessionWorkSummaryText\(\)/);
  assert.match(html, /id="sessionWorkSummary"/);
  assert.doesNotMatch(app, /\$\('sessionVolume'\)\.textContent =/);
});

test('legacy timed sets with stale repetition fields do not inflate kilogram volume', () => {
  const result = summary.summarize([], [
    { complete: true, load: 20, reps: 10, durationSeconds: 30, durationRemainingMs: 0 },
    { complete: true, load: 10, reps: 5 }
  ], elapsedMs);
  assert.deepEqual(result, { volumeKg: 50, timeSeconds: 30, timedSetCount: 1 });
  assert.equal(summary.format(result, 'Time', formatDuration), '50 kg · Time: 00:30');

  const timedOnly = summary.summarize([], [
    { complete: true, load: 20, reps: 10, durationSeconds: 30, durationRemainingMs: 0 }
  ], elapsedMs);
  assert.equal(summary.format(timedOnly, 'Time', formatDuration), 'Time: 00:30');
});
