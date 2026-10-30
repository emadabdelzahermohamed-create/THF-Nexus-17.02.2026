const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const policy = require(path.resolve(__dirname, '../../android/app/src/main/assets/pulse/set-rir-policy.js'));

const repetitionExercise = (overrides = {}) => ({
  tracking: { rir: true },
  prescription: { durationSeconds: null },
  ...overrides,
});

test('timed catalog prescriptions never show RIR even when tracking metadata allows it', () => {
  const item = repetitionExercise({ prescription: { durationSeconds: 30 } });
  assert.equal(policy.shouldShow(item, [{ durationSeconds: 30 }]), false);
});

test('a persisted timed set suppresses RIR even if the catalog prescription is missing duration', () => {
  const item = repetitionExercise();
  assert.equal(policy.shouldShow(item, [{ durationSeconds: 45 }]), false);
});

test('repetition-based exercises retain RIR when the catalog enables it', () => {
  assert.equal(policy.shouldShow(repetitionExercise(), [{ reps: 8 }]), true);
});

test('exercises without RIR tracking do not expose the RIR field', () => {
  const item = repetitionExercise({ tracking: { rir: false } });
  assert.equal(policy.shouldShow(item, [{ reps: 8 }]), false);
});

test('timed and untracked set defaults are null while repetition targets are preserved', () => {
  const item = repetitionExercise();
  assert.equal(policy.defaultValue(item, 30, 3), null);
  assert.equal(policy.defaultValue({ tracking: { rir: false } }, null, 3), null);
  assert.equal(policy.defaultValue(item, null, 4), 4);
  assert.equal(policy.defaultValue(item, null, undefined), null);
});

test('stale RIR values are cleared from persisted timed sets', () => {
  const sets = [{ durationSeconds: 30, rir: 3 }, { durationSeconds: 30, rir: 5 }, { durationSeconds: 30, rir: null }];
  assert.equal(policy.clear(sets), true);
  assert.deepEqual(sets.map(set => set.rir), [null, null, null]);
});

test('RIR cleanup is idempotent and leaves already-null values unchanged', () => {
  const sets = [{ durationSeconds: 20, rir: null }];
  assert.equal(policy.clear(sets), false);
  assert.equal(sets[0].rir, null);
});
