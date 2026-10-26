(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.THFVoiceGuidance = api;
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const STORAGE_KEY = 'pulse.v2.voiceGuidance';

  function createVoiceGuidance({storage, speakNative, speakWeb} = {}) {
    function isEnabled() {
      const saved = storage?.getItem?.(STORAGE_KEY);
      return saved === null || saved === undefined ? true : saved === '1';
    }

    function setEnabled(enabled) {
      const value = Boolean(enabled);
      storage?.setItem?.(STORAGE_KEY, value ? '1' : '0');
      return value;
    }

    function coachingText(exercise = {}) {
      return [
        exercise.name,
        exercise.setup,
        ...(Array.isArray(exercise.steps) ? exercise.steps : []),
        exercise.breathing,
        exercise.safety,
      ].filter(value => typeof value === 'string' && value.trim()).join('. ');
    }

    function speak(exercise, language, {force = false} = {}) {
      if (!force && !isEnabled()) return false;
      const text = coachingText(exercise);
      if (!text) return false;
      const locale = language === 'ar' ? 'ar-EG' : 'en-US';
      if (typeof speakNative === 'function') speakNative(text, locale);
      else if (typeof speakWeb === 'function') speakWeb(text, locale);
      else return false;
      return true;
    }

    return {isEnabled, setEnabled, speak};
  }

  return {createVoiceGuidance};
}));
