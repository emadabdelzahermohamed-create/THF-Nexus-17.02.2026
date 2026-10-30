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
  },
  "romanian-deadlift": {
    "asset": "media/motion/romanian-deadlift.mp4",
    "kind": "offline_video",
    "sha256": "5f6e6258a3bbbde659ef9673620808e63b0ee6ff0f15a53d04f25ea07a229ac1",
    "licenseId": "wger-romanian-deadlift",
    "author": "Goulart",
    "source": "wger",
    "sourceUrl": "https://wger.de/media/exercise-video/507/307e7276-a14d-4ea0-b579-f5b0dbc6f5af.MOV",
    "license": "CC-BY-SA-4.0",
    "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/"
  },
  "standing-calf-raises": {
    "asset": "media/motion/standing-calf-raises.mp4",
    "kind": "offline_video",
    "sha256": "28282f7bfaf80fbc6ec7b85f465b9f7a7c3fb3a83bdd9bc01cc19fd95e5348a6",
    "licenseId": "wger-standing-calf-raises",
    "author": "Goulart",
    "source": "wger",
    "sourceUrl": "https://wger.de/media/exercise-video/622/461171e5-2b16-407d-bf27-27aeef43f105.MOV",
    "license": "CC-BY-SA-4.0",
    "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/"
  },
  "leg-press": {
    "asset": "media/motion/leg-press.mp4",
    "kind": "offline_video",
    "sha256": "1f3b4e71c153ff25c9512592bc477cc17ace0f1d7e9c55619cd2d3518e8b68ad",
    "licenseId": "wger-leg-press",
    "author": "Goulart",
    "source": "wger",
    "sourceUrl": "https://wger.de/media/exercise-video/371/6aae16b4-01b9-4eb4-935c-3250f84d2c59.MOV",
    "license": "CC-BY-SA-4.0",
    "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/"
  },
  "hammer-curls": {
    "asset": "media/motion/hammer-curls.mp4",
    "kind": "offline_video",
    "sha256": "22987fc1c5c1bbcb1174cec3319c1f63b612e79e800f3c32a2237a89811b5574",
    "licenseId": "wger-hammer-curls",
    "author": "Goulart",
    "source": "wger",
    "sourceUrl": "https://wger.de/media/exercise-video/272/df069052-2173-4f24-855f-a0eebe729f24.MOV",
    "license": "CC-BY-SA-4.0",
    "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/"
  },
  "tricep-dumbbell-kickback": {
    "asset": "media/motion/tricep-dumbbell-kickback.mp4",
    "kind": "offline_video",
    "sha256": "ab4bddda7689f1d9921e0d857e8e9667dd25e530745254f4e79b9190e796cb41",
    "licenseId": "wger-tricep-dumbbell-kickback",
    "author": "Goulart",
    "source": "wger",
    "sourceUrl": "https://wger.de/media/exercise-video/655/2d88a05b-bde3-4026-bfbf-524c11068dc5.MOV",
    "license": "CC-BY-SA-4.0",
    "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/"
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
  const PRELOAD_TIMEOUT_MS = 1200;
  let timer = null;
  let observer = null;
  let activeExerciseId = null;
  let pendingExerciseId = null;
  let staticExerciseId = null;
  let frameIndex = 0;
  const preloadPromises = new Map();
  const loadedFrames = new Map();

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
    pendingExerciseId = null;
    frameIndex = 0;
    if (resetExercise) {
      activeExerciseId = null;
      staticExerciseId = null;
    }
  }

  function renderFrame(item) {
    const image = byId('activeDemoImage');
    const loaded = loadedFrames.get(item.id);
    const assets = loaded ? loaded.map(frame => frame.asset) : item?.demo?.assets;
    if (!image || !Array.isArray(assets) || assets.length < 1) return;
    const phaseIndex = frameIndex % assets.length;
    const sourceIndex = loaded ? loaded[phaseIndex].index : phaseIndex;
    const nextSrc = './' + assets[phaseIndex];
    const isArabic = document.documentElement.lang === 'ar';
    const phaseName = isArabic
      ? (sourceIndex === 0 ? 'البداية' : 'النهاية')
      : (sourceIndex === 0 ? 'Start' : 'Finish');
    const baseAlt = item?.demo?.alt?.[isArabic ? 'ar' : 'en'] || '';
    // Avoid redundant WebView image work on the API31 Samsung lane.
    if (image.getAttribute('src') !== nextSrc) image.setAttribute('src', nextSrc);
    image.alt = `${baseAlt} — ${phaseName}`;
    const reduced = reduceMotion();
    const loadedCount = Array.isArray(loaded) ? loaded.length : null;
    const status = byId('activeDemoStatus');
    if (status) {
      const nextStatus = reduced
        ? (isArabic ? 'تقليل الحركة مفعّل؛ تظهر صورة ثابتة للتمرين.' : 'Reduced motion is on; a static exercise image is shown.')
        : loadedCount === 1
          ? (isArabic ? 'تم تحميل صورة مرجعية واحدة فقط؛ تعرض بصورة ثابتة.' : 'Only one reference frame loaded; showing a static view.')
          : '';
      if (status.textContent !== nextStatus) status.textContent = nextStatus;
    }
    const phase = byId('activeDemoPhase');
    if (phase) {
      // Keep the visible fast-changing label out of live screen-reader output;
      // the current phase remains available in the image's descriptive alt text.
      phase.setAttribute('aria-hidden', 'true');
      const phaseStatus = reduced
        ? (isArabic ? 'صورة ثابتة — تقليل الحركة' : 'Static image — reduced motion')
        : loadedCount === 1
          ? (isArabic ? 'إطار مرجعي ثابت' : 'Static reference frame')
          : (isArabic ? 'تسلسل مرجعي تلقائي' : 'Automatic reference sequence');
      phase.textContent = phaseName + ' · ' + phaseStatus;
    }
  }

  function renderStaticFallback(item) {
    const frames = loadedFrames.get(item.id) || [];
    if (frames.length === 0) {
      const image = byId('activeDemoImage');
      if (image?.getAttribute('src')) image.removeAttribute('src');
      if (image && image.alt) image.alt = '';
      const isArabic = document.documentElement.lang === 'ar';
      const status = byId('activeDemoStatus');
      const message = isArabic
        ? 'تعذر تحميل صور الحركة لهذا التمرين دون اتصال.'
        : 'Exercise reference frames could not be loaded offline.';
      if (status && status.textContent !== message) status.textContent = message;
      const phase = byId('activeDemoPhase');
      if (phase && phase.textContent !== '') phase.textContent = '';
      return;
    }
    frameIndex = 0;
    renderFrame(item);
  }

  function preloadFrames(item) {
    if (preloadPromises.has(item.id)) return preloadPromises.get(item.id);
    const framePromises = item.demo.assets.map(asset => {
      return new Promise(resolve => {
        const preload = new Image();
        preload.decoding = 'async';
        let settled = false;
        let timeoutId;
        const finish = loaded => {
          if (settled) return;
          settled = true;
          if (timeoutId !== undefined) window.clearTimeout(timeoutId);
          preload.removeEventListener('load', onLoad);
          preload.removeEventListener('error', onError);
          resolve(loaded);
        };
        const onLoad = () => finish(true);
        const onError = () => finish(false);
        preload.addEventListener('load', onLoad, {once: true});
        preload.addEventListener('error', onError, {once: true});
        // A stalled WebView decode must not block the automatic offline loop forever.
        timeoutId = window.setTimeout(() => finish(false), PRELOAD_TIMEOUT_MS);
        preload.src = './' + asset;
      });
    });
    const ready = Promise.all(framePromises);
    preloadPromises.set(item.id, ready);
    return ready;
  }

  async function start(item) {
    stop();
    activeExerciseId = item.id;
    pendingExerciseId = item.id;
    staticExerciseId = null;
    renderFrame(item);
    if (reduceMotion() || document.hidden) {
      pendingExerciseId = null;
      return;
    }
    const results = await preloadFrames(item);
    if (activeExerciseId !== item.id || pendingExerciseId !== item.id
        || reduceMotion() || document.hidden) {
      if (pendingExerciseId === item.id) pendingExerciseId = null;
      return;
    }
    const readyFrames = item.demo.assets
      .map((asset, index) => ({asset, index}))
      .filter((frame, index) => results[index]);
    loadedFrames.set(item.id, readyFrames);
    frameIndex = 0;
    if (readyFrames.length === 0) {
      staticExerciseId = item.id;
      renderStaticFallback(item);
      pendingExerciseId = null;
      return;
    }
    renderFrame(item);
    if (readyFrames.length < 2) {
      staticExerciseId = item.id;
      pendingExerciseId = null;
      return;
    }
    pendingExerciseId = null;
    timer = window.setInterval(() => {
      const latest = currentExercise();
      if (!latest || document.hidden || reduceMotion()) return;
      const frames = loadedFrames.get(latest.id) || latest.demo.assets;
      if (frames.length < 2) return;
      frameIndex = (frameIndex + 1) % frames.length;
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
      if (timer || pendingExerciseId) stop();
      renderFrame(item);
      return;
    }
    if (document.hidden) {
      if (timer || pendingExerciseId) stop();
      return;
    }
    if (item.id === staticExerciseId) {
      renderStaticFallback(item);
      return;
    }
    if (item.id !== activeExerciseId || (!timer && pendingExerciseId !== item.id)) start(item);
  }

  window.addEventListener('load', () => {
    const root = byId('activeWorkoutScreen');
    if (!root) return;
    const isMotionOutputTarget = target => {
      const element = target?.nodeType === 1 ? target : target?.parentElement;
      return Boolean(element?.closest?.('#activeDemoImage, #activeDemoStatus, #activeDemoPhase'));
    };
    observer = new MutationObserver(records => {
      const languageChanged = records?.some(record =>
        record.target === document.documentElement && record.attributeName === 'lang'
      );
      const stateChanged = !records?.length || records.some(record =>
        record.target !== document.documentElement && !isMotionOutputTarget(record.target)
      );
      if (languageChanged && activeExerciseId) {
        const item = currentExercise();
        if (item) {
          if (item.id === staticExerciseId) renderStaticFallback(item);
          else renderFrame(item);
        }
      }
      if (stateChanged) reconcile();
    });
    observer.observe(root, {
      subtree: true,
      childList: true,
      attributes: true,
      characterData: true,
      // Frame src changes are renderer output, not state inputs. Observing them wakes
      // reconcile on every animation frame and creates avoidable WebView main-thread work.
      attributeFilter: ['class', 'data-exercise-id']
    });
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['lang']
    });
    byId('reduceMotion')?.addEventListener('change', reconcile);
    const motionQuery = window.matchMedia?.('(prefers-reduced-motion: reduce)');
    if (motionQuery?.addEventListener) motionQuery.addEventListener('change', reconcile);
    else motionQuery?.addListener?.(reconcile);
    document.addEventListener('visibilitychange', reconcile);
    reconcile();
  }, {once: true});
})();
