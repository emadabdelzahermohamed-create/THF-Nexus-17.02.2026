const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const appPath = path.resolve(__dirname, '../../android/app/src/main/assets/pulse/app.js');
const policyPath = path.resolve(__dirname, '../../android/app/src/main/assets/pulse/active-workout-resume-policy.js');
const app = fs.readFileSync(appPath, 'utf8');
const policy = require(policyPath);

function functionSource(name) {
  const start = app.indexOf(`  function ${name}(`);
  assert.notEqual(start, -1, `missing function ${name}`);
  const next = app.indexOf('\\n  function ', start + 1);
  return app.slice(start, next === -1 ? app.length : next);
}

test('rendering an unknown saved exercise fails closed without deleting the session', () => {
  const renderer = functionSource('renderActiveWorkout');
  assert.match(renderer, /!resumePolicy\\.isResumable\\(state\\.active, EXERCISES\\) \\|\\| !item\\) return;/);
  assert.doesNotMatch(renderer, /removeItem\\(['"]pulse\\.v2\\.active/);
  assert.doesNotMatch(renderer, /state\\.active\\s*=\\s*null/);
});

test('a non-null stale session remains protected while correctly reported as unavailable', () => {
  const stale = { exerciseId: 'exercise-removed-from-catalog', sets: [{ complete: true }] };
  const catalog = [{ id: 'barbell-squat' }, { id: 'plank' }];
  assert.equal(policy.hasSession(stale), true);
  assert.equal(policy.isResumable(stale, catalog), false);
});

test('Today keeps an unavailable session visible and disables the resume action', () => {
  const today = functionSource('renderToday');
  assert.match(today, /resumeCard\\.classList\\.toggle\\('hidden', !hasActiveSession\\)/);
  assert.match(today, /resumeButton\\.disabled = !activeItem/);
  assert.match(today, /resumeUnavailableHint/);
});

test('startup language rendering still routes saved sessions through the guarded renderer', () => {
  const language = functionSource('applyLanguage');
  assert.match(language, /if \\(state\\.active\\) renderActiveWorkout\\(\\)/);
  const renderer = functionSource('renderActiveWorkout');
  assert.match(renderer, /!resumePolicy\\.isResumable\\(state\\.active, EXERCISES\\) \\|\\| !item\\) return;/);
});
