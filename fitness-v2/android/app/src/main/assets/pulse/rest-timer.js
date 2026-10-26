(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.THFRestTimer = api;
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  function createRestTimer({now = () => Date.now()} = {}) {
    function deadline(seconds) {
      const duration = Number(seconds);
      return now() + (Number.isFinite(duration) && duration > 0 ? duration * 1000 : 0);
    }

    function remaining(endsAtMs) {
      const deadlineMs = Number(endsAtMs);
      if (!Number.isFinite(deadlineMs) || deadlineMs <= 0) return 0;
      return Math.max(0, Math.ceil((deadlineMs - now()) / 1000));
    }

    return {deadline, remaining};
  }

  return {createRestTimer};
}));
