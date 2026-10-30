const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const FITNESS_ROOT = path.resolve(__dirname, '../..');
const APP = fs.readFileSync(path.join(FITNESS_ROOT, 'android/app/src/main/assets/pulse/app.js'), 'utf8');
const HTML = fs.readFileSync(path.join(FITNESS_ROOT, 'android/app/src/main/assets/pulse/index.html'), 'utf8');
const PROGRAMS = JSON.parse(fs.readFileSync(path.join(FITNESS_ROOT, 'android/app/src/main/assets/pulse/data/programs.json'), 'utf8'));

function timedMinimumMinutes(session) {
  const seconds = (session.exercises || []).reduce((sum, reference) => {
    const duration = Number(reference.durationSeconds) || 0;
    if (duration <= 0) return sum;
    const sets = Math.max(1, Number(reference.sets) || 1);
    const rest = Math.max(0, Number(reference.restSeconds) || 0);
    return sum + duration * sets + Math.max(0, sets - 1) * rest;
  }, 0);
  return Math.ceil(seconds / 60);
}

test('program duration prescriptions use readable MM:SS instead of raw seconds', () => {
  assert.ok(APP.includes('function formatDuration(totalSeconds)'));
  assert.ok(APP.includes('formatDuration(reference.durationSeconds)'));
});

test('program detail discloses timed-work lower bounds above the stated estimate', () => {
  assert.ok(APP.includes('function timedMinimumMinutes(session)'));
  assert.ok(APP.includes('programTimeWarning'));
  const program = PROGRAMS.find(item => item.id === 'walk-run-foundation');
  const session = program.sessions.find(item => item.id === 'walk-run-foundation-session-1');
  assert.equal(timedMinimumMinutes(session), 126);
  assert.ok(timedMinimumMinutes(session) > session.estimatedMinutes);
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

test('timer and program-time warning copy is bilingual', () => {
  for (const key of ['time:', 'target:', 'startTimer:', 'pauseTimer:', 'timeReached:', 'durationReached:', 'programTimeWarning:']) {
    assert.ok(APP.includes(key), `missing Arabic/English copy key ${key}`);
  }
});
