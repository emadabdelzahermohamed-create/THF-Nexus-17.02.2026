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
  assert.match(APP, /function formatDuration\(totalSeconds\)/);
  assert.match(APP, /reference\.sets \\u00d7 \${formatDuration\(reference\.durationSeconds\)}/);
});

test('program detail discloses timed-work lower bounds above the stated estimate', () => {
  assert.match(APP, /function timedMinimumMinutes\(session\)/);
  assert.match(APP, /programTimeWarning/);
  const program = PROGRAMS.find(item => item.id === 'walk-run-foundation');
  const session = program.sessions.find(item => item.id === 'walk-run-foundation-session-1');
  assert.equal(timedMinimumMinutes(session), 126);
  assert.ok(timedMinimumMinutes(session) > session.estimatedMinutes);
});

test('program timed sets seed independent remaining-time state', () => {
  assert.match(APP, /durationRemainingMs:durationSeconds\*1000/);
  assert.match(APP, /durationRunning:false,durationElapsed:false/);
});

test('active workout renders a timer control instead of a zero-reps field for timed sets', () => {
  assert.match(APP, /data-duration-toggle/);
  assert.match(APP, /hasTimedSets\?t\('time'\):t\('reps'\)/);
  assert.match(APP, /durationSeconds\?t\('time'\):t\('reps'\)/);
  assert.match(HTML, /id="setRepsHeader"/);
  assert.match(HTML, /id="durationAnnouncement" class="sr-only" aria-live="polite" aria-atomic="true"/);
});

test('duration timer supports start, pause, persisted restore and background pause', () => {
  for (const name of ['startDurationTimer','pauseDurationTimer','tickDurationTimer','restoreDurationTimerState']) {
    assert.ok(APP.includes(`function ${name}(`), `missing ${name}`);
  }
  assert.match(APP, /if\(document\.hidden\)\{pauseActiveDurationTimer\(\);video\.pause\(\);\}/);
  assert.match(APP, /window\.addEventListener\('pagehide',pauseActiveDurationTimer\)/);
  assert.match(APP, /if \(id !== 'activeWorkoutScreen'\) pauseActiveDurationTimer\(\)/);
});

test('reaching the target announces completion but does not auto-complete the set', () => {
  assert.match(APP, /set\.durationElapsed=true/);
  assert.match(APP, /durationAnnouncement/);
  assert.doesNotMatch(APP, /set\.complete=true/);
});

test('timer and program-time warning copy is bilingual', () => {
  for (const key of ['time:', 'target:', 'startTimer:', 'pauseTimer:', 'timeReached:', 'durationReached:', 'programTimeWarning:']) {
    assert.ok(APP.includes(key), `missing Arabic/English copy key ${key}`);
  }
});
