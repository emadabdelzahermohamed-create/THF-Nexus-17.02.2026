const assert = require('node:assert/strict');
const test = require('node:test');

const policy = require('../../android/app/src/main/assets/pulse/active-workout-resume-policy.js');

const catalog = [{ id: 'barbell-squat' }, { id: 'plank' }];

test('any non-null persisted value blocks destructive replacement', () => {
  assert.equal(policy.hasSession({}), true);
  assert.equal(policy.hasSession('legacy-corrupt-state'), true);
  assert.equal(policy.hasSession(null), false);
  assert.equal(policy.hasSession(undefined), false);
});

test('only an exercise still present in the catalog is resumable', () => {
  assert.equal(policy.isResumable({ exerciseId: 'barbell-squat' }, catalog), true);
  assert.equal(policy.isResumable({ exerciseId: 'removed-exercise' }, catalog), false);
  assert.equal(policy.isResumable({ exerciseId: 'barbell-squat' }, null), false);
  assert.equal(policy.isResumable(null, catalog), false);
});

test('unknown and malformed active sessions remain protected but cannot resume', () => {
  const stale = { exerciseId: 'removed-exercise', sets: [{ complete: true }] };
  assert.equal(policy.hasSession(stale), true);
  assert.equal(policy.isResumable(stale, catalog), false);
});

test('progress counts only explicitly completed sets', () => {
  const result = policy.progress({ sets: [{ complete: true }, { complete: false }, {}, { complete: true }] });
  assert.deepEqual(result, { completed: 2, total: 4 });
});

test('missing or malformed set arrays produce a safe empty progress summary', () => {
  assert.deepEqual(policy.progress(null), { completed: 0, total: 0 });
  assert.deepEqual(policy.progress({ sets: 'invalid' }), { completed: 0, total: 0 });
  assert.deepEqual(policy.progress({ sets: [null, false, { complete: 1 }] }), { completed: 0, total: 3 });
});
