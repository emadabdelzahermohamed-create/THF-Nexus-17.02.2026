(function attachActiveWorkoutResumePolicy(root, factory) {
  const policy = factory();
  if (typeof module === 'object' && module.exports) module.exports = policy;
  if (root) root.THF_ACTIVE_WORKOUT_RESUME_POLICY = policy;
})(typeof globalThis !== 'undefined' ? globalThis : null, function createActiveWorkoutResumePolicy() {
  'use strict';

  function hasSession(active) {
    return active !== null && active !== undefined;
  }

  function isRecord(value) {
    return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
  }

  function isResumable(active, exercises) {
    if (!isRecord(active)) return false;
    if (typeof active.exerciseId !== 'string' || !active.exerciseId.trim() || !Array.isArray(exercises)) return false;
    if (!Array.isArray(active.sets) || active.sets.length === 0 || !active.sets.every(isRecord)) return false;
    if (active.programEntries !== undefined && active.programEntries !== null) {
      if (!Array.isArray(active.programEntries)) return false;
      if (!active.programEntries.every(entry => isRecord(entry) && Array.isArray(entry.sets) && entry.sets.every(isRecord))) return false;
    }
    return exercises.some(item => item && item.id === active.exerciseId);
  }

  function progress(active) {
    const sets = Array.isArray(active?.sets) ? active.sets : [];
    return Object.freeze({
      completed: sets.filter(set => set?.complete === true).length,
      total: sets.length
    });
  }

  function archiveUnresumableSession(storage, exercises, options = {}) {
    if (!storage || typeof storage.getItem !== 'function' || typeof storage.setItem !== 'function' || typeof storage.removeItem !== 'function') {
      return { ok: false, reason: 'storage-unavailable' };
    }

    const activeKey = options.activeKey || 'pulse.v2.active';
    const archiveKey = options.archiveKey || 'pulse.v2.stale-workout-archive';
    let rawSession;
    try {
      rawSession = storage.getItem(activeKey);
    } catch {
      return { ok: false, reason: 'active-read-failed' };
    }
    if (typeof rawSession !== 'string' || rawSession.length === 0) return { ok: false, reason: 'missing-active' };

    let active = null;
    try { active = JSON.parse(rawSession); } catch {}
    if (isResumable(active, exercises)) return { ok: false, reason: 'session-resumable' };

    let existing = [];
    try {
      const rawArchive = storage.getItem(archiveKey);
      if (rawArchive) {
        existing = JSON.parse(rawArchive);
        if (!Array.isArray(existing)) return { ok: false, reason: 'archive-invalid' };
      }
    } catch {
      return { ok: false, reason: 'archive-invalid' };
    }

    const archivedAt = typeof options.archivedAt === 'string' && options.archivedAt
      ? options.archivedAt
      : new Date().toISOString();
    const next = [
      ...existing.filter(entry => entry?.rawSession !== rawSession),
      { archivedAt, reason: 'exercise_unavailable_or_invalid', rawSession }
    ];
    const serialized = JSON.stringify(next);

    try {
      storage.setItem(archiveKey, serialized);
      if (storage.getItem(archiveKey) !== serialized) return { ok: false, reason: 'archive-verification-failed' };
    } catch {
      return { ok: false, reason: 'archive-write-failed' };
    }

    try {
      storage.removeItem(activeKey);
      if (storage.getItem(activeKey) !== null) {
        return { ok: false, reason: 'active-clear-failed', archived: true, archiveCount: next.length };
      }
    } catch {
      return { ok: false, reason: 'active-clear-failed', archived: true, archiveCount: next.length };
    }

    return { ok: true, archiveCount: next.length };
  }

  return Object.freeze({ hasSession, isResumable, progress, archiveUnresumableSession });
});
