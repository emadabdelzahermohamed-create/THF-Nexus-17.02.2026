'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const APP = fs.readFileSync(path.resolve(__dirname, '../../android/app/src/main/assets/pulse/app.js'), 'utf8');

function extractFunction(source, name) {
  const marker = 'function ' + name + '(';
  const start = source.indexOf(marker);
  assert.notEqual(start, -1, 'missing ' + name);
  const open = source.indexOf('{', start);
  let depth = 0;
  for (let i = open; i < source.length; i += 1) {
    if (source[i] === '{') depth += 1;
    else if (source[i] === '}') {
      depth -= 1;
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  throw new Error('unterminated ' + name);
}

function harness() {
  const monotonic = { value: 5000 };
  const set = {
    durationSeconds: 30,
    durationRemainingMs: 12000,
    durationRunning: true,
    durationElapsed: false,
    durationEndsAtMonotonicMs: 13000,
    durationEndsAtMs: 999999
  };
  const active = { sets: [set], durationTimerSetIndex: 0 };
  const documentEvents = new Map();
  const windowEvents = new Map();
  const intervals = new Set([42]);
  const cleared = [];
  const rendered = [];
  let persists = 0;
  const context = {
    window: {
      performance: { now: () => monotonic.value },
      addEventListener(name, callback) { windowEvents.set(name, callback); }
    },
    document: { addEventListener(name, callback) { documentEvents.set(name, callback); } },
    state: { active, durationTick: 42 },
    clearInterval(id) { cleared.push(id); intervals.delete(id); },
    persistActive() { persists += 1; },
    renderDurationControls(index) { rendered.push(index); },
    Number,
    Math,
    Object,
    Date
  };
  const names = ['durationClockNow', 'remainingDurationMs', 'pauseDurationTimer', 'pauseActiveDurationTimer', 'bindDurationLifecycleEvents'];
  const functions = names.map(name => extractFunction(APP, name)).join('\n');
  vm.runInNewContext(functions + '\nglobalThis.api = { bindDurationLifecycleEvents };', context);
  context.api.bindDurationLifecycleEvents();
  return {
    set, active, documentEvents, windowEvents, intervals, cleared, rendered,
    get persists() { return persists; }, monotonic
  };
}

test('Chromium freeze pauses the active timed set and persists monotonic remaining time', () => {
  const h = harness();
  const freeze = h.documentEvents.get('freeze');
  assert.equal(typeof freeze, 'function');
  freeze();
  assert.equal(h.set.durationRemainingMs, 8000);
  assert.equal(h.set.durationRunning, false);
  assert.equal(h.set.durationElapsed, false);
  assert.equal(Object.hasOwn(h.set, 'durationEndsAtMonotonicMs'), false);
  assert.equal(Object.hasOwn(h.set, 'durationEndsAtMs'), false);
  assert.equal(h.active.durationTimerSetIndex, null);
  assert.equal(h.intervals.size, 0);
  assert.deepEqual(h.cleared, [42]);
  assert.deepEqual(h.rendered, [0]);
  assert.equal(h.persists, 1);
});

test('pagehide remains a fallback and invokes the same safe pause path', () => {
  const h = harness();
  const pagehide = h.windowEvents.get('pagehide');
  assert.equal(typeof pagehide, 'function');
  pagehide();
  assert.equal(h.set.durationRemainingMs, 8000);
  assert.equal(h.set.durationRunning, false);
  assert.equal(h.persists, 1);
});

test('freeze followed by pagehide is idempotent and does not persist twice', () => {
  const h = harness();
  h.documentEvents.get('freeze')();
  h.windowEvents.get('pagehide')();
  assert.equal(h.set.durationRemainingMs, 8000);
  assert.equal(h.persists, 1);
  assert.deepEqual(h.cleared, [42]);
});

test('a frozen timer stays paused when the document is later resumed', () => {
  const h = harness();
  h.documentEvents.get('freeze')();
  assert.equal(h.documentEvents.has('resume'), false);
  assert.equal(h.set.durationRunning, false);
  assert.equal(h.active.durationTimerSetIndex, null);
});

test('freeze and pagehide listeners are registered from the active workout binding', () => {
  assert.match(APP, /document\.addEventListener\('freeze',\s*pauseActiveDurationTimer\)/);
  assert.match(APP, /window\.addEventListener\('pagehide',\s*pauseActiveDurationTimer\)/);
  assert.match(APP, /bindDurationLifecycleEvents\(\);/);
});
