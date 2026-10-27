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

    function coachingSegments(exercise = {}, language = 'en') {
    const arabic = language === 'ar';
    const segments = [];
    const intro = [exercise.name, exercise.setup]
      .filter(value => typeof value === 'string' && value.trim())
      .join('. ');
    if (intro) segments.push(intro);
    if (Array.isArray(exercise.steps)) {
      exercise.steps.filter(value => typeof value === 'string' && value.trim())
        .forEach((step, index) => segments.push(`${arabic ? 'الخطوة' : 'Step'} ${index + 1}. ${step}`));
    }
    if (typeof exercise.breathing === 'string' && exercise.breathing.trim()) {
      segments.push(`${arabic ? 'التنفس' : 'Breathing'}. ${exercise.breathing}`);
    }
    if (typeof exercise.safety === 'string' && exercise.safety.trim()) {
      segments.push(`${arabic ? 'السلامة' : 'Safety'}. ${exercise.safety}`);
    }
    return segments;
  }

  function speak(exercise, language, {force = false} = {}) {
    if (!force && !isEnabled()) return false;
    const segments = coachingSegments(exercise, language);
    if (!segments.length) return false;
    const locale = language === 'ar' ? 'ar-EG' : 'en-US';
    const speakSegment = typeof speakNative === 'function' ? speakNative : speakWeb;
    if (typeof speakSegment !== 'function') return false;
    segments.forEach((segment, index) => speakSegment(segment, locale, index > 0));
    return true;
  }

  return {isEnabled, setEnabled, speak};
  }

  return {createVoiceGuidance};
}));
