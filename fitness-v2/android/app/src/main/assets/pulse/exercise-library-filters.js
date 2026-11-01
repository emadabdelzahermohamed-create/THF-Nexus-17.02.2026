(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.THFExerciseLibraryFilters = api;
})(typeof window !== 'undefined' ? window : globalThis, function () {
  'use strict';

  function normalizeEquipmentIds(value) {
    const source = Array.isArray(value)
      ? value
      : value && Array.isArray(value.equipment)
        ? value.equipment
        : [];
    const seen = new Set();
    const result = [];
    for (const candidate of source) {
      if (typeof candidate !== 'string') continue;
      const id = candidate.trim().toLowerCase();
      if (!id || seen.has(id)) continue;
      seen.add(id);
      result.push(id);
    }
    return result;
  }

  function matchesAvailableEquipment(equipmentId, profileEquipment) {
    if (typeof equipmentId !== 'string') return false;
    const id = equipmentId.trim().toLowerCase();
    if (!id) return false;
    if (id === 'body only') return true;
    return normalizeEquipmentIds(profileEquipment).includes(id);
  }

  return Object.freeze({ normalizeEquipmentIds, matchesAvailableEquipment });
});
