window.THF_MOTION_MANIFEST = {
  "bodyweight-squat": {
    "asset": "media/motion/bodyweight-squat.webm",
    "kind": "verified_frame_sequence",
    "sourceFrameCount": 16,
    "fps": 8,
    "durationSeconds": 2,
    "sha256": "39aa95865b5f45746fe17faca5693deb33b9b5bab4930b4c8dab897ef569cbe7"
  },
  "pushups": {
    "asset": "media/motion/pushups.webm",
    "kind": "verified_frame_sequence",
    "sourceFrameCount": 16,
    "fps": 8,
    "durationSeconds": 2,
    "sha256": "5b71b9a0d9f79f2fbff2f8b6b6e5bbe9610c82c0061a1636ea322f01e07eaad0"
  }
};

/*
 * Offline reference-motion fallback.
 * Reviewed full-motion media above always wins. Other exercises with >=2
 * audited local reference frames cycle automatically without inventing
 * intermediate anatomy. Reduced-motion users keep a static first frame.
 */
(() => {
  'use strict';
  const FRAME_MS = 850;
  let timer = null;
  let observer = null;
  let activeExerciseId = null;
  let frameIndex = 0;
  const preloadedExercises = new Set();

  const byId = id => document.getElementById(id);
  const exercises = () => Array.isArray(window.THF_EXERCISES) ? window.THF_EXERCISES : [];
  const currentExercise = () => exercises().find(item => item.id === activeExerciseId);
  const reduceMotion = () => {
    const control = byId('reduceMotion');
    if (control) return Boolean(control.checked);
    return Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches);
  };

  function inferActiveExercise() {
    const explicitId = byId('activeWorkoutScreen')?.dataset?.exerciseId;
    if (explicitId) {
      const exact = exercises().find(item => item.id === explicitId);
      if (exact) return exact;
    }
    const name = byId('activeExerciseName')?.textContent?.trim();
    if (!name) return null;
    return exercises().find(item => [item?.name?.ar, item?.name?.en].includes(name)) || null;
  }

  function stop({resetExercise = false} = {}) {
    if (timer) window.clearInterval(timer);
    timer = null;
    frameIndex = 0;
    if (resetExercise) activeExerciseId = null;
  }

  function renderFrame(item) {
    const image = byId('activeDemoImage');
    if (!image || !Array.isArray(item?.demo?.assets) || item.demo.assets.length < 2) return;
    const phaseIndex = frameIndex % item.demo.assets.length;
    const nextSrc = './' + item.demo.assets[phaseIndex];
    // Avoid redundant WebView image work on the API31 Samsung lane.
    if (image.getAttribute('src') !== nextSrc) image.setAttribute('src', nextSrc);
    image.alt = item?.demo?.alt?.[document.documentElement.lang === 'ar' ? 'ar' : 'en'] || '';
    const phase = byId('activeDemoPhase');
    if (phase) {
      const reduced = reduceMotion();
      phase.textContent = document.documentElement.lang === 'ar'
        ? `${phaseIndex === 0 ? 'البداية' : 'النهاية'} · ${reduced ? 'صورة ثابتة — تقليل الحركة' : 'تسلسل مرجعي تلقائي'}`
        : `${phaseIndex === 0 ? 'Start' : 'Finish'} · ${reduced ? 'Static image — reduced motion' : 'Automatic reference sequence'}`;
    }
  }

  function preloadFrames(item) {
    if (preloadedExercises.has(item.id)) return;
    preloadedExercises.add(item.id);
    item.demo.assets.forEach(asset => {
      const preload = new Image();
      preload.decoding = 'async';
      preload.src = './' + asset;
    });
  }

  function start(item) {
    stop();
    activeExerciseId = item.id;
    renderFrame(item);
    if (reduceMotion() || document.hidden) return;
    preloadFrames(item);
    timer = window.setInterval(() => {
      const latest = currentExercise();
      if (!latest || document.hidden || reduceMotion()) return;
      frameIndex = (frameIndex + 1) % latest.demo.assets.length;
      renderFrame(latest);
    }, FRAME_MS);
  }

  function reconcile() {
    const screen = byId('activeWorkoutScreen');
    const image = byId('activeDemoImage');
    const video = byId('activeDemoVideo');
    if (!screen?.classList.contains('active') || !image || !video) {
      stop({resetExercise: true});
      return;
    }
    if (!video.classList.contains('hidden')) {
      stop({resetExercise: true});
      return;
    }
    const item = inferActiveExercise();
    if (!item || !Array.isArray(item.demo?.assets) || item.demo.assets.length < 2) {
      stop({resetExercise: true});
      return;
    }
    if (reduceMotion()) {
      if (item.id !== activeExerciseId) {
        activeExerciseId = item.id;
        frameIndex = 0;
      }
      if (timer) stop();
      renderFrame(item);
      return;
    }
    if (document.hidden) {
      if (timer) stop();
      return;
    }
    if (item.id !== activeExerciseId || !timer) start(item);
  }

  window.addEventListener('load', () => {
    const root = byId('activeWorkoutScreen');
    if (!root) return;
    observer = new MutationObserver(reconcile);
    observer.observe(root, {
      subtree: true,
      childList: true,
      attributes: true,
      characterData: true,
      // Frame src changes are renderer output, not state inputs. Observing them wakes
      // reconcile on every animation frame and creates avoidable WebView main-thread work.
      attributeFilter: ['class', 'data-exercise-id']
    });
    byId('reduceMotion')?.addEventListener('change', reconcile);
    document.addEventListener('visibilitychange', reconcile);
    reconcile();
  }, {once: true});
})();
