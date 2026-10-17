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
 *
 * The two entries above remain the only biomechanically reviewed full-motion
 * clips. For every other exercise that ships with >=2 audited offline reference
 * frames, this adapter cycles those frames automatically while the workout is
 * active. It deliberately does not label the result as a verified animation:
 * the phase copy says "automatic reference sequence" and the full-motion
 * manifest remains the source of truth for reviewed clips.
 *
 * This removes the old tap-to-change-pose interaction without inventing
 * intermediate anatomy. Reduced-motion users keep a static first frame.
 */
(() => {
  'use strict';
  const FRAME_MS = 850;
  let timer = null;
  let activeExerciseId = null;
  let frameIndex = 0;

  const byId = id => document.getElementById(id);
  const exercises = () => Array.isArray(window.THF_EXERCISES) ? window.THF_EXERCISES : [];
  const currentExercise = () => exercises().find(item => item.id === activeExerciseId);
  const reduceMotion = () => {
    const control = byId('reduceMotion');
    return Boolean(control?.checked) || window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches;
  };

  function inferActiveExercise() {
    const name = byId('activeExerciseName')?.textContent?.trim();
    if (!name) return null;
    return exercises().find(item => [item?.name?.ar, item?.name?.en].includes(name)) || null;
  }

  function stop() {
    if (timer) window.clearInterval(timer);
    timer = null;
    frameIndex = 0;
  }

  function renderFrame(item) {
    const image = byId('activeDemoImage');
    if (!image || !Array.isArray(item?.demo?.assets) || item.demo.assets.length < 2) return;
    image.src = './' + item.demo.assets[frameIndex % item.demo.assets.length];
    image.alt = item?.demo?.alt?.[document.documentElement.lang === 'ar' ? 'ar' : 'en'] || '';
    const phase = byId('activeDemoPhase');
    if (phase) phase.textContent = document.documentElement.lang === 'ar'
      ? 'تسلسل مرجعي تلقائي — الحركة الكاملة قيد المراجعة'
      : 'Automatic reference sequence — full motion under review';
  }

  function start(item) {
    stop();
    activeExerciseId = item.id;
    renderFrame(item);
    if (reduceMotion()) return;
    timer = window.setInterval(() => {
      const latest = currentExercise();
      if (!latest || document.hidden) return;
      frameIndex = (frameIndex + 1) % latest.demo.assets.length;
      renderFrame(latest);
    }, FRAME_MS);
  }

  function reconcile() {
    const screen = byId('activeWorkoutScreen');
    const image = byId('activeDemoImage');
    const video = byId('activeDemoVideo');
    if (!screen?.classList.contains('active') || !image || !video) { stop(); activeExerciseId = null; return; }
    // A reviewed full-motion clip always wins over the reference-frame fallback.
    if (!video.classList.contains('hidden')) { stop(); return; }
    const item = inferActiveExercise();
    if (!item || !Array.isArray(item.demo?.assets) || item.demo.assets.length < 2) { stop(); return; }
    if (item.id !== activeExerciseId || !timer) start(item);
  }

  window.addEventListener('load', () => {
    const root = byId('activeWorkoutScreen');
    if (!root) return;
    const observer = new MutationObserver(reconcile);
    observer.observe(root, {subtree:true, childList:true, attributes:true, characterData:true, attributeFilter:['class','src']});
    byId('reduceMotion')?.addEventListener('change', reconcile);
    document.addEventListener('visibilitychange', reconcile);
    reconcile();
  }, {once:true});
})();
