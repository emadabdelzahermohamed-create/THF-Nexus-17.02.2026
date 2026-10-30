(function attachActiveWorkoutResumePolicy(root, factory) {
  const policy = factory();
  if (typeof module === 'object' && module.exports) module.exports = policy;
  if (root) root.THF_ACTIVE_WORKOUT_RESUME_POLICY = policy;
})(typeof globalThis !== 'undefined' ? globalThis : null, function createActiveWorkoutResumePolicy() {
  'use strict';

  function hasSession(active) {
    return active !== null && active !== undefined;
  }

  function isResumable(active, exercises) {
    if (!active || typeof active !== 'object' || Array.isArray(active)) return false;
    if (typeof active.exerciseId !== 'string' || !active.exerciseId.trim() || !Array.isArray(exercises)) return false;
    return exercises.some(item => item && item.id === active.exerciseId);
  }

  function progress(active) {
    const sets = Array.isArray(active?.sets) ? active.sets : [];
    return Object.freeze({
      completed: sets.filter(set => set?.complete === true).length,
      total: sets.length
    });
  }

  return Object.freeze({ hasSession, isResumable, progress });
});
