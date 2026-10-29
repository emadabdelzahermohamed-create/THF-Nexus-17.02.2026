const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const appPath = path.join(__dirname, '../../android/app/src/main/assets/pulse/app.js');
const appSource = fs.readFileSync(appPath, 'utf8');
const helperMatch = appSource.match(/(^  function bindSystemMotionPreference\(\)\{[\s\S]*?^  \})(?=\n\n  function applyMotionPreference)/m);

assert.ok(helperMatch, 'app.js must define bindSystemMotionPreference before applyMotionPreference');

function harness({ override = null, modern = true, legacy = true, hasMatchMedia = true } = {}) {
  const calls = [];
  const listeners = {};
  const query = {};
  if (modern) query.addEventListener = (type, listener) => {
    assert.equal(type, 'change');
    listeners.modern = listener;
  };
  if (legacy) query.addListener = listener => { listeners.legacy = listener; };
  const window = hasMatchMedia ? { matchMedia: () => query } : {};
  const store = { getItem: key => key === 'pulse.v2.reduceMotion' ? override : null };
  const applyMotionPreference = (...args) => calls.push(args);
  const bind = vm.runInNewContext('(' + helperMatch[1] + ')', { window, store, applyMotionPreference });
  bind();
  return { calls, listeners };
}

test('live OS reduce-on/reduce-off updates motion without persisting a preference', () => {
  const h = harness();
  assert.equal(typeof h.listeners.modern, 'function');
  h.listeners.modern({ matches: true });
  h.listeners.modern({ matches: false });
  assert.deepEqual(h.calls, [[true, false], [false, false]]);
});

test('explicit in-app reduce-motion ON overrides later OS changes', () => {
  const h = harness({ override: '1' });
  h.listeners.modern({ matches: false });
  assert.deepEqual(h.calls, []);
});

test('explicit in-app reduce-motion OFF overrides later OS changes', () => {
  const h = harness({ override: '0' });
  h.listeners.modern({ matches: true });
  assert.deepEqual(h.calls, []);
});

test('legacy WebView MediaQueryList.addListener receives live changes', () => {
  const h = harness({ modern: false, legacy: true });
  assert.equal(typeof h.listeners.legacy, 'function');
  h.listeners.legacy({ matches: true });
  assert.deepEqual(h.calls, [[true, false]]);
});

test('unsupported matchMedia is a safe no-op', () => {
  const h = harness({ hasMatchMedia: false });
  assert.deepEqual(h.calls, []);
  assert.equal(h.listeners.modern, undefined);
  assert.equal(h.listeners.legacy, undefined);
});

test('application startup installs the system listener after applying initial preference', () => {
  const applyAt = appSource.indexOf('applyMotionPreference(preferredReducedMotion(),false)');
  const bindAt = appSource.indexOf('bindSystemMotionPreference();', applyAt);
  assert.ok(applyAt >= 0);
  assert.ok(bindAt > applyAt);
  assert.ok(appSource.includes("if(store.getItem('pulse.v2.reduceMotion')!==null)return;"));
});
