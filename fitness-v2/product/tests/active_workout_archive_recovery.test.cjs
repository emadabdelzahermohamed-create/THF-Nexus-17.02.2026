const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const PULSE = path.resolve(__dirname, '../../android/app/src/main/assets/pulse');
const POLICY = require(path.join(PULSE, 'active-workout-resume-policy.js'));
const APP = fs.readFileSync(path.join(PULSE, 'app.js'), 'utf8');
const HTML = fs.readFileSync(path.join(PULSE, 'index.html'), 'utf8');
const ACTIVE_KEY = 'pulse.v2.active';
const ARCHIVE_KEY = 'pulse.v2.stale-workout-archive';
const SESSION = {
  clientRecordId: 'workout-restore-1',
  exerciseId: 'plank',
  startedAt: 1793400000000,
  sets: [{ complete: true }, { complete: false }]
};
const RAW_SESSION = JSON.stringify(SESSION);
const CATALOG = [{ id: 'plank', name: { en: '<script>Plank</script>', ar: 'بلانك' } }];

function makeStorage(seed = {}) {
  const values = new Map(Object.entries(seed));
  return {
    persistent: true,
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

function makeClassList() {
  const values = new Set(['hidden']);
  return {
    add(value) { values.add(value); },
    remove(value) { values.delete(value); },
    contains(value) { return values.has(value); }
  };
}

function renderSandbox(storage, exercises = CATALOG, active = null, history = []) {
  const nodes = {
    archivedWorkoutsCard: { classList: makeClassList() },
    archivedWorkoutsList: { innerHTML: '', textContent: '' },
    archivedWorkoutsStatus: { textContent: '' }
  };
  return {
    nodes,
    sandbox: {
      $: id => nodes[id],
      store: storage,
      state: { lang: 'en', active },
      EXERCISES: exercises,
      resumePolicy: POLICY,
      history: () => history,
      local: value => value?.en || value || '',
      locale: () => 'en-US',
      escapeHtml: value => String(value ?? '').replace(/[&<>'"]/g, match => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[match])),
      t(key) {
        return ({
          archivedWorkoutsCount: '{count} saved copies',
          archiveUnknownExercise: 'Unknown exercise',
          archiveDateUnknown: 'Save date unavailable',
          archiveRecordInvalid: 'Invalid recovery copy',
          archiveNotRecoverable: 'Not currently recoverable',
          archiveReady: 'Ready to restore',
          archiveAlreadyActive: 'Already active',
          archiveAlreadyCompleted: 'Already completed',
          archiveAnotherWorkoutActive: 'Another workout is active',
          archiveRestoreAction: 'Restore workout',
          resumeWorkoutProgress: '{done} of {total} complete',
          archiveListReadFailed: 'Could not read recovery archive'
        })[key] || key;
      }
    }
  };
}

test('archive listing becomes recoverable only when the exact exercise mapping returns', () => {
  const storage = makeStorage({ [ARCHIVE_KEY]: JSON.stringify([{ archivedAt: '2026-10-31T00:00:00.000Z', reason: 'exercise_unavailable_or_invalid', rawSession: RAW_SESSION }]) });
  const missing = POLICY.readArchivedSessions(storage, []);
  const restored = POLICY.readArchivedSessions(storage, CATALOG);
  assert.equal(missing.ok, true);
  assert.equal(missing.entries[0].resumable, false);
  assert.equal(restored.entries[0].resumable, true);
  assert.equal(JSON.parse(storage.getItem(ARCHIVE_KEY))[0].rawSession, RAW_SESSION);
});

test('archive listing preserves malformed entries without mutating the archive', () => {
  const raw = JSON.stringify([{ archivedAt: 'bad-date', rawSession: '{broken' }, null, { rawSession: RAW_SESSION }]);
  const storage = makeStorage({ [ARCHIVE_KEY]: raw });
  const result = POLICY.readArchivedSessions(storage, CATALOG);
  assert.equal(result.ok, true);
  assert.equal(result.entries.length, 3);
  assert.equal(result.entries[0].valid, false);
  assert.equal(result.entries[1].valid, false);
  assert.equal(result.entries[2].resumable, true);
  assert.equal(storage.getItem(ARCHIVE_KEY), raw);
});

test('restore writes and verifies the active session before removing only the selected archive entry', () => {
  const older = { archivedAt: 'older', reason: 'legacy', rawSession: JSON.stringify({ exerciseId: 'removed', sets: [{}] }) };
  const selected = { archivedAt: 'today', reason: 'stale', rawSession: RAW_SESSION };
  const storage = makeStorage({ [ARCHIVE_KEY]: JSON.stringify([older, selected]) });
  const result = POLICY.restoreArchivedSession(storage, CATALOG, 1);
  assert.equal(result.ok, true);
  assert.equal(result.archiveRetained, false);
  assert.equal(storage.getItem(ACTIVE_KEY), RAW_SESSION);
  assert.deepEqual(JSON.parse(storage.getItem(ARCHIVE_KEY)), [older]);
  assert.deepEqual(result.session, SESSION);
});

test('restore refuses to overwrite an existing active workout', () => {
  const active = JSON.stringify({ exerciseId: 'another', sets: [{}] });
  const archive = JSON.stringify([{ rawSession: RAW_SESSION }]);
  const storage = makeStorage({ [ACTIVE_KEY]: active, [ARCHIVE_KEY]: archive });
  const result = POLICY.restoreArchivedSession(storage, CATALOG, 0);
  assert.deepEqual(result, { ok: false, reason: 'active-session-present' });
  assert.equal(storage.getItem(ACTIVE_KEY), active);
  assert.equal(storage.getItem(ARCHIVE_KEY), archive);
});

test('restore refuses a session whose exercise has not returned to the catalog', () => {
  const archive = JSON.stringify([{ rawSession: RAW_SESSION }]);
  const storage = makeStorage({ [ARCHIVE_KEY]: archive });
  const result = POLICY.restoreArchivedSession(storage, [], 0);
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'archive-session-not-resumable');
  assert.equal(storage.getItem(ACTIVE_KEY), null);
  assert.equal(storage.getItem(ARCHIVE_KEY), archive);
});

test('active write failure leaves the recovery archive unchanged', () => {
  const archive = JSON.stringify([{ rawSession: RAW_SESSION }]);
  const storage = makeStorage({ [ARCHIVE_KEY]: archive });
  storage.setItem = (key, value) => {
    if (key === ACTIVE_KEY) throw new Error('quota');
    storage.values.set(key, String(value));
  };
  const result = POLICY.restoreArchivedSession(storage, CATALOG, 0);
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'active-write-failed');
  assert.equal(storage.getItem(ACTIVE_KEY), null);
  assert.equal(storage.getItem(ARCHIVE_KEY), archive);
});

test('archive update failure restores the active session but retains the recovery copy', () => {
  const archive = JSON.stringify([{ rawSession: RAW_SESSION }]);
  const storage = makeStorage({ [ARCHIVE_KEY]: archive });
  const originalSet = storage.setItem.bind(storage);
  storage.setItem = (key, value) => {
    if (key === ARCHIVE_KEY) throw new Error('quota');
    originalSet(key, value);
  };
  const result = POLICY.restoreArchivedSession(storage, CATALOG, 0);
  assert.equal(result.ok, true);
  assert.equal(result.archiveRetained, true);
  assert.equal(storage.getItem(ACTIVE_KEY), RAW_SESSION);
  assert.equal(storage.getItem(ARCHIVE_KEY), archive);
});

test('restore reports a retained copy only when read-back still contains the selected raw session', () => {
  const archive = JSON.stringify([{ rawSession: RAW_SESSION }]);
  const storage = makeStorage({ [ARCHIVE_KEY]: archive });
  const originalGet = storage.getItem.bind(storage);
  const originalSet = storage.setItem.bind(storage);
  storage.setItem = (key, value) => {
    originalSet(key, value);
    if (key === ARCHIVE_KEY) storage.values.set(key, JSON.stringify([{ rawSession: RAW_SESSION }]));
  };
  storage.getItem = key => originalGet(key);
  const result = POLICY.restoreArchivedSession(storage, CATALOG, 0);
  assert.equal(result.ok, true);
  assert.equal(result.archiveRetained, true);
  assert.equal(storage.getItem(ACTIVE_KEY), RAW_SESSION);
  assert.equal(JSON.parse(storage.getItem(ARCHIVE_KEY))[0].rawSession, RAW_SESSION);
});

test('Today recovery list shows a safely escaped restore action only for valid available sessions', () => {
  const storage = makeStorage({ [ARCHIVE_KEY]: JSON.stringify([
    { archivedAt: '2026-10-31T00:00:00.000Z', rawSession: RAW_SESSION },
    { archivedAt: '2026-10-31T00:00:00.000Z', rawSession: JSON.stringify({ exerciseId: 'removed', sets: [{}] }) }
  ]) });
  const harness = renderSandbox(storage);
  const render = vm.runInNewContext('(' + extractFunction(APP, 'renderArchivedWorkouts') + ')', harness.sandbox);
  render();
  assert.equal(harness.nodes.archivedWorkoutsCard.classList.contains('hidden'), false);
  assert.match(harness.nodes.archivedWorkoutsList.innerHTML, /data-restore-archive="0"/);
  assert.match(harness.nodes.archivedWorkoutsList.innerHTML, /&lt;script&gt;Plank&lt;\/script&gt;/);
  assert.doesNotMatch(harness.nodes.archivedWorkoutsList.innerHTML, /<script>/);
  assert.match(harness.nodes.archivedWorkoutsList.innerHTML, /Not currently recoverable/);
  assert.doesNotMatch(harness.nodes.archivedWorkoutsList.innerHTML, /data-restore-archive="1"/);
  assert.equal(harness.nodes.archivedWorkoutsStatus.textContent, '2 saved copies');
});

test('Today recovery list hides restore when the same record is active or already completed', () => {
  const activeSession = { ...SESSION, clientRecordId: 'active-copy' };
  const completedSession = { ...SESSION, clientRecordId: 'completed-copy' };
  const storage = makeStorage({ [ARCHIVE_KEY]: JSON.stringify([
    { rawSession: JSON.stringify(activeSession) },
    { rawSession: JSON.stringify(completedSession) }
  ]) });
  const harness = renderSandbox(storage, CATALOG, activeSession, [{ clientRecordId: 'completed-copy' }]);
  const render = vm.runInNewContext('(' + extractFunction(APP, 'renderArchivedWorkouts') + ')', harness.sandbox);
  render();
  assert.doesNotMatch(harness.nodes.archivedWorkoutsList.innerHTML, /data-restore-archive=/);
  assert.match(harness.nodes.archivedWorkoutsList.innerHTML, /Already active/);
  assert.match(harness.nodes.archivedWorkoutsList.innerHTML, /Already completed/);
});

test('a different active workout blocks archive restoration controls until its slot is free', () => {
  const activeSession = { ...SESSION, clientRecordId: 'currently-active' };
  const archivedSession = { ...SESSION, clientRecordId: 'archived-copy' };
  const storage = makeStorage({ [ARCHIVE_KEY]: JSON.stringify([{ rawSession: JSON.stringify(archivedSession) }]) });
  const harness = renderSandbox(storage, CATALOG, activeSession);
  const render = vm.runInNewContext('(' + extractFunction(APP, 'renderArchivedWorkouts') + ')', harness.sandbox);
  render();
  assert.doesNotMatch(harness.nodes.archivedWorkoutsList.innerHTML, /data-restore-archive=/);
  assert.match(harness.nodes.archivedWorkoutsList.innerHTML, /Another workout is active/);
});

test('the UI restore action restores into Today without auto-starting the workout', () => {
  const storage = makeStorage({ [ARCHIVE_KEY]: JSON.stringify([{ rawSession: RAW_SESSION }]) });
  const state = { active: null };
  const events = [];
  const sandbox = {
    store: storage,
    state,
    EXERCISES: CATALOG,
    resumePolicy: POLICY,
    toast(message) { events.push('toast:' + message); },
    t(key) { return key === 'archiveRestoreSuccess' ? 'Restored' : key; },
    renderArchivedWorkouts() { events.push('render-archive'); },
    showScreen(id) { events.push('show:' + id); }
  };
  const restore = vm.runInNewContext('(' + extractFunction(APP, 'restoreArchivedWorkout') + ')', sandbox);
  assert.equal(restore(0), true);
  assert.equal(state.active.clientRecordId, SESSION.clientRecordId);
  assert.ok(events.includes('show:todayScreen'));
  assert.ok(events.includes('toast:Restored'));
  assert.equal(events.some(value => value === 'show:activeWorkoutScreen'), false);
});

test('the Today recovery panel and delegated restore control are wired', () => {
  assert.match(HTML, /id="archivedWorkoutsCard"/);
  assert.match(HTML, /id="archivedWorkoutsList"/);
  assert.match(APP, /archivedWorkoutsList'\)\.addEventListener\('click'/);
  assert.match(APP, /data-restore-archive/);
});
