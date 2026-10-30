const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const FITNESS_ROOT = path.resolve(__dirname, '../..');
const APP = fs.readFileSync(path.join(FITNESS_ROOT, 'android/app/src/main/assets/pulse/app.js'), 'utf8');
const HTML = fs.readFileSync(path.join(FITNESS_ROOT, 'android/app/src/main/assets/pulse/index.html'), 'utf8');
const CSS = fs.readFileSync(path.join(FITNESS_ROOT, 'android/app/src/main/assets/pulse/styles.css'), 'utf8');
const PROGRAMS_SOURCE = fs.readFileSync(path.join(FITNESS_ROOT, 'android/app/src/main/assets/pulse/data/programs.js'), 'utf8');
const PROGRAMS = JSON.parse(PROGRAMS_SOURCE.slice(PROGRAMS_SOURCE.indexOf('=') + 1).trim().replace(/;$/, ''));

test('program duration prescriptions use readable MM:SS instead of raw seconds', () => {
  assert.ok(APP.includes('function formatDuration(totalSeconds)'));
  assert.ok(APP.includes('formatDuration(reference.durationSeconds)'));
  const timedReference = PROGRAMS.flatMap(program => program.sessions.flatMap(session => session.exercises))
    .find(reference => Number(reference.durationSeconds) > 0);
  assert.ok(timedReference, 'the offline program library must retain at least one timed prescription');
});

test('program timed sets seed independent remaining-time state', () => {
  assert.ok(APP.includes('durationRemainingMs:durationSeconds*1000'));
  assert.ok(APP.includes('durationRunning:false,durationElapsed:false'));
});

test('active workout renders a timer control instead of a zero-reps field for timed sets', () => {
  assert.ok(APP.includes('data-duration-toggle'));
  assert.ok(APP.includes("hasTimedSets?t('time'):t('reps')"));
  assert.ok(APP.includes("durationSeconds?t('time'):t('reps')"));
  assert.ok(HTML.includes('id="setRepsHeader"'));
  assert.ok(HTML.includes('id="durationAnnouncement" class="sr-only" aria-live="polite" aria-atomic="true"'));
  assert.ok(CSS.includes('.sr-only{position:absolute!important'));
});

test('duration timer supports start, pause, persisted restore and background pause', () => {
  for (const name of ['startDurationTimer','pauseDurationTimer','tickDurationTimer','restoreDurationTimerState']) {
    assert.ok(APP.includes(`function ${name}(`), `missing ${name}`);
  }
  assert.ok(APP.includes('if(document.hidden){pauseActiveDurationTimer();video.pause();}'));
  assert.ok(APP.includes("window.addEventListener('pagehide',pauseActiveDurationTimer)"));
  assert.ok(APP.includes("if (id !== 'activeWorkoutScreen') pauseActiveDurationTimer()"));
});

test('reaching the target announces completion but does not auto-complete the set', () => {
  assert.ok(APP.includes('set.durationElapsed=true'));
  assert.ok(APP.includes('durationAnnouncement'));
  assert.equal(APP.includes('set.complete=true'), false);
});

test('undoing a completed timed set resets its timer to the full target', () => {
  assert.ok(APP.includes('if(Number(set.durationSeconds)>0&&!set.complete)resetDurationTimer(index)'));
  assert.ok(APP.includes('set.durationRemainingMs=Number(set.durationSeconds)*1000'));
  assert.ok(APP.includes('set.durationElapsed=false'));
});

test('timer copy is bilingual', () => {
  for (const key of ['time:', 'target:', 'startTimer:', 'pauseTimer:', 'timeReached:', 'durationReached:']) {
    assert.ok(APP.includes(key), `missing Arabic/English copy key ${key}`);
  }
});
