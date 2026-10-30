(function attachRirPolicy(root, factory) {
  const policy = factory();
  if (typeof module === 'object' && module.exports) module.exports = policy;
  if (root) root.THF_SET_RIR_POLICY = policy;
})(typeof globalThis !== 'undefined' ? globalThis : null, function createRirPolicy() {
  'use strict';

  function shouldShow(item, sets) {
    if (!item || !item.tracking?.rir) return false;
    if (Number(item.prescription?.durationSeconds) > 0) return false;
    return !(Array.isArray(sets) && sets.some(set => Number(set?.durationSeconds) > 0));
  }

  function defaultValue(item, durationSeconds, value) {
    if (!item?.tracking?.rir || Number(durationSeconds) > 0) return null;
    return value === undefined ? null : value;
  }

  function clear(sets) {
    if (!Array.isArray(sets)) return false;
    let changed = false;
    for (const set of sets) {
      if (set && set.rir !== null) {
        set.rir = null;
        changed = true;
      }
    }
    return changed;
  }

  return Object.freeze({ shouldShow, defaultValue, clear });
});
