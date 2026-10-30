const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const PULSE = path.resolve(__dirname, '../../android/app/src/main/assets/pulse');
const APP = fs.readFileSync(path.join(PULSE, 'app.js'), 'utf8');
const HTML = fs.readFileSync(path.join(PULSE, 'index.html'), 'utf8');
const policy = require(path.join(PULSE, 'active-workout-resume-policy.js'));
const CATALOG = [{ id: 'plank' }, { id: 'barbell-squat' }];
const ACTIVE_KEY = 'pulse.v2.active';
const ARCHIVE_KEY = 'pulse.v2.stale-workout-archive';

function makeStorage(seed = {}) {
  const values = new Map(Object.entries(seed));
  return {
    getItem(key) { return values.has(key) ? values.get(key) : null; },
    setItem(key, value) { values.set(key, String(value)); },
    removeItem(key) { values.delete(key); },
    values
  };
}

function extractFunction(source, name) {
  const marker = 'function ' + name + '(';
  const start = source.indexOf(marker);
  assert.notEqual(start, -1, 'missing function ' + name);
  const open = source.indexOf('{', start);
  assert.notEqual(open, -1, 'missing function body ' + name);
  let depth = 0;
  let quote = null;
  let escaped = false;
  let lineComment = false;
  let blockComment = false;
  for (let i = open; i < source.length; i += 1) {
    const ch = source[i];
    const next = source[i + 1];
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
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  throw new Error('unterminated function ' + name);
}

test('resumability rejects missing, empty, or malformed saved set records', () => {
  assert.equal(policy.isResumable({ exerciseId: 'plank' }, CATALOG), false);
  assert.equal(policy.isResumable({ exerciseId: 'plank', sets: [] }, CATALOG), false);
  assert.equal(policy.isResumable({ exerciseId: 'plank', sets: [null] }, CATALOG), false);
  assert.equal(policy.isResumable({ exerciseId: 'plank', sets: [{}], programEntries: 'broken' }, CATALOG), false);
  assert.equal(policy.isResumable({ exerciseId: 'plank', sets: [{}], programEntries: [{ sets: [null] }] }, CATALOG), false);
  assert.equal(policy.isResumable({ exerciseId: 'plank', sets: [{}] }, CATALOG), true);
});

test('archive stores the exact saved payload and clears the active key only after read-back verification', () => {
  const raw = JSON.stringify({ exerciseId: 'removed-exercise', sets: [null], clientRecordId: 'record-1' });
  const storage = makeStorage({ [ACTIVE_KEY]: raw });
  const result = policy.archiveUnresumableSession(storage, CATALOG, { archivedAt: '2026-10-31T00:00:00.000Z' });

  assert.equal(result.ok, true);
  assert.equal(result.archiveCount, 1);
  assert.equal(storage.getItem(ACTIVE_KEY), null);
  const archive = JSON.parse(storage.getItem(ARCHIVE_KEY));
  assert.equal(archive[0].rawSession, raw);
  assert.equal(archive[0].archivedAt, '2026-10-31T00:00:00.000Z');
});

test('archive refuses a session that is still resumable', () => {
  const raw = JSON.stringify({ exerciseId: 'plank', sets: [{ complete: true }] });
  const storage = makeStorage({ [ACTIVE_KEY]: raw });
  const result = policy.archiveUnresumableSession(storage, CATALOG);

  assert.deepEqual(result, { ok: false, reason: 'session-resumable' });
  assert.equal(storage.getItem(ACTIVE_KEY), raw);
  assert.equal(storage.getItem(ARCHIVE_KEY), null);
});

test('archive write failure leaves the active session untouched', () => {
  const raw = JSON.stringify({ exerciseId: 'removed-exercise', sets: [null] });
  const storage = makeStorage({ [ACTIVE_KEY]: raw });
  const originalSet = storage.setItem;
  storage.setItem = (key, value) => {
    if (key === ARCHIVE_KEY) throw new Error('quota');
    originalSet(key, value);
  };
  const result = policy.archiveUnresumableSession(storage, CATALOG);

  assert.equal(result.ok, false);
  assert.equal(result.reason, 'archive-write-failed');
  assert.equal(storage.getItem(ACTIVE_KEY), raw);
});

test('corrupt archive is not overwritten and the active session remains preserved', () => {
  const raw = JSON.stringify({ exerciseId: 'removed-exercise', sets: [null] });
  const storage = makeStorage({ [ACTIVE_KEY]: raw, [ARCHIVE_KEY]: '{broken' });
  const result = policy.archiveUnresumableSession(storage, CATALOG);

  assert.equal(result.ok, false);
  assert.equal(result.reason, 'archive-invalid');
  assert.equal(storage.getItem(ACTIVE_KEY), raw);
  assert.equal(storage.getItem(ARCHIVE_KEY), '{broken');
});

test('archive deduplicates the same raw session and retains prior recovery copies', () => {
  const raw = JSON.stringify({ exerciseId: 'removed-exercise', sets: [null] });
  const prior = JSON.stringify([{ archivedAt: 'old', reason: 'old', rawSession: 'older-session' }, { archivedAt: 'older', reason: 'old', rawSession: raw }]);
  const storage = makeStorage({ [ACTIVE_KEY]: raw, [ARCHIVE_KEY]: prior });
  const result = policy.archiveUnresumableSession(storage, CATALOG, { archivedAt: 'new' });

  assert.equal(result.ok, true);
  const archive = JSON.parse(storage.getItem(ARCHIVE_KEY));
  assert.equal(archive.length, 2);
  assert.equal(archive[0].rawSession, 'older-session');
  assert.equal(archive[1].rawSession, raw);
  assert.equal(archive[1].archivedAt, 'new');
});

test('active-key clear failure keeps both the original and verified recovery copy', () => {
  const raw = JSON.stringify({ exerciseId: 'removed-exercise', sets: [null] });
  const storage = makeStorage({ [ACTIVE_KEY]: raw });
  storage.removeItem = () => { throw new Error('read-only'); };
  const result = policy.archiveUnresumableSession(storage, CATALOG);

  assert.equal(result.ok, false);
  assert.equal(result.reason, 'active-clear-failed');
  assert.equal(result.archived, true);
  assert.equal(storage.getItem(ACTIVE_KEY), raw);
  assert.equal(JSON.parse(storage.getItem(ARCHIVE_KEY))[0].rawSession, raw);
});

test('the real archive action stores final motion evidence, releases the active slot, and returns to Today', () => {
  const stale = { exerciseId: 'removed-exercise', sets: [null], clientRecordId: 'record-2' };
  const storage = makeStorage({ [ACTIVE_KEY]: JSON.stringify(stale) });
  const state = { active: stale };
  const events = [];
  const sandbox = {
    state,
    store: storage,
    EXERCISES: CATALOG,
    resumePolicy: policy,
    pauseActiveDurationTimer() { events.push('pause-timer'); },
    endNativeMotionSession() { events.push('end-motion'); return { available: true, sessionId: 'motion-2', stepDelta: 4 }; },
    persistActive() { storage.setItem(ACTIVE_KEY, JSON.stringify(state.active)); events.push('persist'); },
    stopMotionPolling() { events.push('stop-polling'); },
    stopRest() { events.push('stop-rest'); },
    renderToday() { events.push('render-today'); },
    showScreen(id) { events.push('show:' + id); },
    toast(message) { events.push('toast:' + message); },
    t(key) { return key === 'archiveStaleSuccess' ? 'Saved {count}' : key; }
  };
  const action = vm.runInNewContext('(' + extractFunction(APP, 'archiveUnavailableWorkout') + ')', sandbox);

  assert.equal(action(), true);
  assert.equal(state.active, null);
  assert.equal(storage.getItem(ACTIVE_KEY), null);
  const archived = JSON.parse(JSON.parse(storage.getItem(ARCHIVE_KEY))[0].rawSession);
  assert.equal(archived.motionEvidence.sessionId, 'motion-2');
  assert.equal(archived.motionEvidence.stepDelta, 4);
  assert.ok(events.includes('show:todayScreen'));
  assert.ok(events.includes('toast:Saved 1'));
});

test('the real archive action never clears the active key when archive storage fails', () => {
  const stale = { exerciseId: 'removed-exercise', sets: [null] };
  const raw = JSON.stringify(stale);
  const storage = makeStorage({ [ACTIVE_KEY]: raw });
  const originalSet = storage.setItem;
  storage.setItem = (key, value) => {
    if (key === ARCHIVE_KEY) throw new Error('quota');
    originalSet(key, value);
  };
  const state = { active: stale };
  const messages = [];
  const sandbox = {
    state,
    store: storage,
    EXERCISES: CATALOG,
    resumePolicy: policy,
    pauseActiveDurationTimer() {},
    endNativeMotionSession() { return { available: false }; },
    persistActive() { storage.setItem(ACTIVE_KEY, JSON.stringify(state.active)); },
    stopMotionPolling() {},
    stopRest() {},
    renderToday() {},
    showScreen() {},
    toast(message) { messages.push(message); },
    t(key) { return key; }
  };
  const action = vm.runInNewContext('(' + extractFunction(APP, 'archiveUnavailableWorkout') + ')', sandbox);

  assert.equal(action(), false);
  assert.equal(state.active, stale);
  assert.equal(storage.getItem(ACTIVE_KEY), raw);
  assert.deepEqual(messages, ['archiveStaleFailed']);
});

test('Today exposes the archive disclosure only for a non-resumable saved session', () => {
  assert.match(HTML, /id="resumeRecoveryActions"/);
  assert.match(HTML, /id="archiveStaleWorkoutBtn"/);
  assert.match(APP, /resumeRecoveryActions'\)\.classList\.toggle\('hidden', !hasActiveSession \|\| canResume\)/);
  assert.match(APP, /archiveStaleWorkoutBtn'\)\.addEventListener\('click', archiveUnavailableWorkout\)/);
});

test('the real archive action refuses to unlock a workout when only memory fallback storage exists', () => {
  const stale = { exerciseId: 'removed-exercise', sets: [null] };
  const raw = JSON.stringify(stale);
  const storage = makeStorage({ [ACTIVE_KEY]: raw });
  storage.persistent = false;
  const state = { active: stale };
  const events = [];
  const sandbox = {
    state,
    store: storage,
    EXERCISES: CATALOG,
    resumePolicy: policy,
    pauseActiveDurationTimer() { events.push('pause'); },
    endNativeMotionSession() { events.push('end'); return { available: false }; },
    persistActive() {},
    stopMotionPolling() { events.push('stop'); },
    stopRest() { events.push('rest'); },
    renderToday() {},
    showScreen() {},
    toast(message) { events.push('toast:' + message); },
    t(key) { return key; }
  };
  const action = vm.runInNewContext('(' + extractFunction(APP, 'archiveUnavailableWorkout') + ')', sandbox);

  assert.equal(action(), false);
  assert.equal(state.active, stale);
  assert.equal(storage.getItem(ACTIVE_KEY), raw);
  assert.deepEqual(events, ['toast:archiveStaleStorageUnavailable']);
});
