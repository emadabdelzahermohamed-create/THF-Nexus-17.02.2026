const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const appPath = path.resolve(__dirname, '../../android/app/src/main/assets/pulse/app.js');
const policyPath = path.resolve(__dirname, '../../android/app/src/main/assets/pulse/active-workout-resume-policy.js');
const app = fs.readFileSync(appPath, 'utf8');
const policy = require(policyPath);

function functionSource(name) {
  const marker = 'function ' + name + '(';
  const start = app.indexOf(marker);
  assert.notEqual(start, -1, 'missing function ' + name);
  const open = app.indexOf('{', start);
  let depth = 0;
  let quote = null;
  let escaped = false;
  let lineComment = false;
  let blockComment = false;
  for (let i = open; i < app.length; i += 1) {
    const ch = app[i];
    const next = app[i + 1];
    if (quote) {
      if (escaped) { escaped = false; continue; }
      if (ch === '\\') { escaped = true; continue; }
      if (ch === quote) quote = null;
      continue;
    }
    if (lineComment) { if (ch === '\n') lineComment = false; continue; }
    if (blockComment) {
      if (ch === '*' && next === '/') { blockComment = false; i += 1; }
      continue;
    }
    if (ch === '/' && next === '/') { lineComment = true; i += 1; continue; }
    if (ch === '/' && next === '*') { blockComment = true; i += 1; continue; }
    if (ch === "'" || ch === '"' || ch.charCodeAt(0) === 96) { quote = ch; continue; }
    if (ch === '{') depth += 1;
    else if (ch === '}') {
      depth -= 1;
      if (depth === 0) return app.slice(start, i + 1);
    }
  }
  throw new Error('unterminated function ' + name);
}

test('rendering an unknown saved exercise fails closed without deleting the session', () => {
  const renderer = functionSource('renderActiveWorkout');
  assert.match(renderer, /!resumePolicy\.isResumable\(state\.active, EXERCISES\) \|\| !item\) return;/);
  assert.doesNotMatch(renderer, /removeItem\(['"]pulse\.v2\.active/);
  assert.doesNotMatch(renderer, /state\.active\s*=\s*null/);
});

test('rendering a stale saved workout leaves the persisted session untouched', () => {
  const stale = { exerciseId: 'exercise-removed-from-catalog', sets: [{ complete: true }] };
  const storageCalls = [];
  const sandbox = {
    activeExercise: () => undefined,
    resumePolicy: policy,
    state: { active: stale },
    EXERCISES: [{ id: 'barbell-squat' }, { id: 'plank' }],
    store: {
      removeItem(key) { storageCalls.push(['remove', key]); },
      setItem(key, value) { storageCalls.push(['set', key, value]); }
    }
  };
  const renderer = vm.runInNewContext('(' + functionSource('renderActiveWorkout') + ')', sandbox);

  renderer();

  assert.equal(sandbox.state.active, stale);
  assert.deepEqual(storageCalls, []);
});

test('a non-null stale session remains protected while correctly reported as unavailable', () => {
  const stale = { exerciseId: 'exercise-removed-from-catalog', sets: [{ complete: true }] };
  const catalog = [{ id: 'barbell-squat' }, { id: 'plank' }];
  assert.equal(policy.hasSession(stale), true);
  assert.equal(policy.isResumable(stale, catalog), false);
});

test('Today keeps an unavailable session visible and disables the resume action', () => {
  const today = functionSource('renderToday');
  assert.match(today, /resumeCard\.classList\.toggle\('hidden', !hasActiveSession\)/);
  assert.match(today, /resumeButton\.disabled = !activeItem/);
  assert.match(today, /resumeUnavailableHint/);
});

test('startup language rendering still routes saved sessions through the guarded renderer', () => {
  const language = functionSource('applyLanguage');
  assert.match(language, /if \(state\.active\) renderActiveWorkout\(\)/);
  const renderer = functionSource('renderActiveWorkout');
  assert.match(renderer, /!resumePolicy\.isResumable\(state\.active, EXERCISES\) \|\| !item\) return;/);
});
