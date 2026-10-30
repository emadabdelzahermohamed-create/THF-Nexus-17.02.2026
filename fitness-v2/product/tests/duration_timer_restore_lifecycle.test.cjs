const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const APP = fs.readFileSync(path.resolve(__dirname, '../../android/app/src/main/assets/pulse/app.js'), 'utf8');

function extractFunction(source, name) {
  const marker = `function ${name}(`;
  const start = source.indexOf(marker);
  assert.notEqual(start, -1, `missing ${name}`);
  const open = source.indexOf('{', start);
  let depth = 0;
  for (let i = open; i < source.length; i += 1) {
    if (source[i] === '{') depth += 1;
    else if (source[i] === '}') {
      depth -= 1;
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  throw new Error(`unterminated ${name}`);
}

function restore(savedSet, timerIndex = 0) {
  const active = { sets: [{ ...savedSet }], durationTimerSetIndex: timerIndex };
  let persists = 0;
  const context = {
    state: { active },
    persistActive() { persists += 1; },
    Date,
    Number,
    Math,
    Object,
  };
  vm.runInNewContext(`${extractFunction(APP, 'restoreDurationTimerState')}; globalThis.runRestore = restoreDurationTimerState;`, context);
  context.runRestore();
  return { active, set: active.sets[0], persists };
}

test('process restart preserves last persisted remaining time instead of counting background time', () => {
  const expiredDeadline = Date.now() - 5000;
  const result = restore({ durationSeconds: 30, durationRemainingMs: 17000, durationRunning: true, durationEndsAtMs: expiredDeadline, durationElapsed: false });
  assert.equal(result.set.durationRemainingMs, 17000);
  assert.equal(result.set.durationRunning, false);
  assert.equal(result.set.durationElapsed, false);
  assert.equal('durationEndsAtMs' in result.set, false);
  assert.equal(result.active.durationTimerSetIndex, null);
  assert.equal(result.persists, 1);
});

test('zero saved remaining time restores as elapsed and paused', () => {
  const result = restore({ durationSeconds: 30, durationRemainingMs: 0, durationRunning: true, durationEndsAtMs: Date.now() + 10000, durationElapsed: false });
  assert.equal(result.set.durationRemainingMs, 0);
  assert.equal(result.set.durationRunning, false);
  assert.equal(result.set.durationElapsed, true);
  assert.equal('durationEndsAtMs' in result.set, false);
});

test('missing saved remaining time restores the full target paused', () => {
  const result = restore({ durationSeconds: 45, durationRunning: true, durationEndsAtMs: Date.now() - 10000, durationElapsed: false });
  assert.equal(result.set.durationRemainingMs, 45000);
  assert.equal(result.set.durationRunning, false);
  assert.equal(result.set.durationElapsed, false);
});

test('null saved remaining time is treated as missing rather than zero', () => {
  const result = restore({ durationSeconds: 20, durationRemainingMs: null, durationRunning: true, durationElapsed: false });
  assert.equal(result.set.durationRemainingMs, 20000);
  assert.equal(result.set.durationRunning, false);
  assert.equal(result.set.durationElapsed, false);
});

test('paused timers discard stale deadlines without changing their remaining time', () => {
  const result = restore({ durationSeconds: 60, durationRemainingMs: 42000, durationRunning: false, durationEndsAtMs: Date.now() + 30000, durationElapsed: false });
  assert.equal(result.set.durationRemainingMs, 42000);
  assert.equal(result.set.durationRunning, false);
  assert.equal('durationEndsAtMs' in result.set, false);
});

test('corrupt remaining time is bounded by the prescribed target', () => {
  const result = restore({ durationSeconds: 25, durationRemainingMs: 90000, durationRunning: false, durationElapsed: false });
  assert.equal(result.set.durationRemainingMs, 25000);
});
