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

function harness({ withPerformance = true, monotonic = 1000, wall = 100000, saved = {} } = {}) {
  const monotonicNow = { value: monotonic };
  const wallNow = { value: wall };
  const set = {
    durationSeconds: 30,
    durationRemainingMs: 30000,
    durationRunning: false,
    durationElapsed: false,
    ...saved,
  };
  const active = { sets: [set], durationTimerSetIndex: null };
  const intervals = new Map();
  const announcement = { textContent: '' };
  let nextInterval = 1;
  let persists = 0;
  const window = {};
  if (withPerformance) window.performance = { now: () => monotonicNow.value };
  const context = {
    window,
    Date: { now: () => wallNow.value },
    Number,
    Math,
    Object,
    state: { active, durationTick: null },
    setInterval(callback, delay) {
      const id = nextInterval++;
      intervals.set(id, { callback, delay });
      return id;
    },
    clearInterval(id) { intervals.delete(id); },
    persistActive() { persists += 1; },
    renderDurationControls() {},
    $(id) { return id === 'durationAnnouncement' ? announcement : null; },
    t(key) { return key; },
  };
  const names = [
    'durationClockNow',
    'remainingDurationMs',
    'pauseDurationTimer',
    'startDurationTimer',
    'tickDurationTimer',
    'restoreDurationTimerState',
  ];
  const functions = names.map(name => extractFunction(APP, name)).join('\n');
  vm.runInNewContext(`${functions}\nglobalThis.api = { durationClockNow, remainingDurationMs, pauseDurationTimer, startDurationTimer, tickDurationTimer, restoreDurationTimerState };`, context);
  return { api: context.api, active, set, monotonicNow, wallNow, intervals, announcement, get persists() { return persists; }, context };
}

test('running timer ignores wall-clock jumps and follows the monotonic clock', () => {
  const h = harness({
    saved: { durationRunning: true, durationRemainingMs: 10000, durationEndsAtMonotonicMs: 11000 },
  });
  assert.equal(h.api.remainingDurationMs(h.set), 10000);
  h.wallNow.value += 6 * 60 * 60 * 1000;
  assert.equal(h.api.remainingDurationMs(h.set), 10000);
  h.monotonicNow.value += 2500;
  assert.equal(h.api.remainingDurationMs(h.set), 7500);
});

test('start stores a monotonic deadline rather than a wall-clock deadline', () => {
  const h = harness({ saved: { durationRemainingMs: 12000 } });
  h.api.startDurationTimer(0);
  assert.equal(h.set.durationRunning, true);
  assert.equal(h.set.durationEndsAtMonotonicMs, 13000);
  assert.equal(Object.hasOwn(h.set, 'durationEndsAtMs'), false);
  h.wallNow.value += 24 * 60 * 60 * 1000;
  assert.equal(h.api.remainingDurationMs(h.set), 12000);
});

test('pause captures monotonic remaining time and clears both deadline formats', () => {
  const h = harness({ saved: { durationRemainingMs: 30000 } });
  h.api.startDurationTimer(0);
  h.monotonicNow.value += 6500;
  h.api.pauseDurationTimer(0);
  assert.equal(h.set.durationRemainingMs, 23500);
  assert.equal(h.set.durationRunning, false);
  assert.equal(Object.hasOwn(h.set, 'durationEndsAtMonotonicMs'), false);
  assert.equal(Object.hasOwn(h.set, 'durationEndsAtMs'), false);
  assert.equal(h.intervals.size, 0);
  assert.equal(h.persists, 2);
});

test('timer expiry is evaluated against monotonic time', () => {
  const h = harness({ saved: { durationRemainingMs: 5000 } });
  h.api.startDurationTimer(0);
  h.wallNow.value -= 12 * 60 * 60 * 1000;
  h.monotonicNow.value += 5000;
  h.api.tickDurationTimer(0);
  assert.equal(h.set.durationRemainingMs, 0);
  assert.equal(h.set.durationElapsed, true);
  assert.equal(h.set.durationRunning, false);
  assert.equal(h.announcement.textContent, 'durationReached');
  assert.equal(h.intervals.size, 0);
});

test('process restore discards monotonic and legacy deadlines but preserves saved time', () => {
  const h = harness({
    saved: {
      durationRemainingMs: 17000,
      durationRunning: true,
      durationElapsed: false,
      durationEndsAtMonotonicMs: 999999,
      durationEndsAtMs: 888888,
    },
  });
  h.active.durationTimerSetIndex = 0;
  h.api.restoreDurationTimerState();
  assert.equal(h.set.durationRemainingMs, 17000);
  assert.equal(h.set.durationRunning, false);
  assert.equal(Object.hasOwn(h.set, 'durationEndsAtMonotonicMs'), false);
  assert.equal(Object.hasOwn(h.set, 'durationEndsAtMs'), false);
  assert.equal(h.active.durationTimerSetIndex, null);
});

test('legacy WebView fallback uses Date.now when performance.now is unavailable', () => {
  const h = harness({
    withPerformance: false,
    wall: 5000,
    saved: { durationRunning: true, durationRemainingMs: 10000, durationEndsAtMonotonicMs: 15000 },
  });
  assert.equal(h.api.durationClockNow(), 5000);
  assert.equal(h.api.remainingDurationMs(h.set), 10000);
  h.wallNow.value += 4000;
  assert.equal(h.api.remainingDurationMs(h.set), 6000);
});
