/* Local-only saved exercises for the offline catalog. */
(() => {
  'use strict';

  const STORAGE_KEY = 'pulse.v2.exerciseFavorites';

  function createExerciseFavorites(storage, exercises) {
    const validIds = new Set((Array.isArray(exercises) ? exercises : [])
      .map(item => item && typeof item.id === 'string' ? item.id : null)
      .filter(Boolean));
    let ids = new Set();
    try {
      const parsed = JSON.parse(storage?.getItem(STORAGE_KEY) || '[]');
      if (Array.isArray(parsed)) {
        ids = new Set(parsed.filter(id => typeof id === 'string' && validIds.has(id)));
      }
    } catch (_) {}

    function persist() {
      try {
        storage?.setItem(STORAGE_KEY, JSON.stringify([...ids]));
      } catch (_) {}
    }

    return Object.freeze({
      has(id) {
        return ids.has(id);
      },
      toggle(id) {
        if (!validIds.has(id)) return null;
        if (ids.has(id)) {
          ids.delete(id);
          persist();
          return false;
        }
        ids.add(id);
        persist();
        return true;
      },
      values() {
        return [...ids];
      }
    });
  }

  window.THFExerciseFavorites = Object.freeze({createExerciseFavorites});
})();
