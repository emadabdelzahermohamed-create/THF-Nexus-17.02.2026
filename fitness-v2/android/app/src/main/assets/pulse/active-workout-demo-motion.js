(() => {
  'use strict';
  const FRAME_MS = 850;
  const PRELOAD_TIMEOUT_MS = 1200;
  const root = document.getElementById('activeWorkoutScreen');
  const image = document.getElementById('activeDemoImage');
  const video = document.getElementById('activeDemoVideo');
  const phase = document.getElementById('activeDemoPhase');
  const preloadCache = new Map();
  let current = null;
  let timer = null;

  function localAsset(asset) {
    if (typeof asset !== 'string' || !asset.startsWith('media/') || asset.includes('..') || asset.includes('\\')) return null;
    return './' + asset;
  }
  function reducedMotion() {
    const control = document.getElementById('reduceMotion');
    if (control) return Boolean(control.checked);
    return Boolean(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  }
  function videoVisible() { return Boolean(video && !video.classList.contains('hidden')); }
  function clearReferenceFrame() {
    if (!image) return;
    image.classList.add('hidden');
    image.removeAttribute('src');
    image.alt = '';
  }
  function hasNoFrames(state) { return Array.isArray(state.frames) && state.frames.length === 0; }
  function screenActive() { return Boolean(root && root.classList.contains('active') && !document.hidden); }
  function setPhase(key, state) {
    if (!phase || !state) return;
    const labels = {
      preparing: {en: 'Preparing offline demo…', ar: 'جارٍ تجهيز العرض دون إنترنت…'},
      playing: {en: 'Automatic reference sequence', ar: 'تسلسل مرجعي تلقائي'},
      ready: {en: 'Offline demo ready', ar: 'العرض دون إنترنت جاهز'},
      paused: {en: 'Demo paused while workout is hidden', ar: 'العرض متوقف مؤقتًا عند إخفاء التمرين'},
      reduced: {en: 'Static image — reduced motion', ar: 'صورة ثابتة — تقليل الحركة'},
      unavailable: {en: 'Static reference image — motion unavailable', ar: 'صورة مرجعية ثابتة — الحركة غير متاحة'},
      missing: {en: 'Offline demo unavailable — no local image could be decoded', ar: 'تعذر عرض التمرين دون إنترنت — لم يمكن فك أي صورة'}
    };
    phase.textContent = labels[key]?.[state.lang] || labels[key]?.en || '';
  }
  function renderFrame(state, index) {
    if (!image || !state) return;
    const assets = state.item?.demo?.assets || [];
    if (hasNoFrames(state)) { clearReferenceFrame(); return; }
    const entry = Array.isArray(state.frames)
      ? state.frames[index % state.frames.length]
      : {asset: assets[0], originalIndex: 0};
    const url = localAsset(entry?.asset);
    if (!url) { clearReferenceFrame(); return; }
    if (image.getAttribute('src') !== url) image.setAttribute('src', url);
    image.classList.remove('hidden');
    const isArabic = state.lang === 'ar';
    const originalIndex = Number(entry.originalIndex) || 0;
    const phaseName = originalIndex === 0
      ? (isArabic ? 'البداية' : 'Start')
      : originalIndex === assets.length - 1
        ? (isArabic ? 'النهاية' : 'Finish')
        : (isArabic ? 'الإطار ' + (originalIndex + 1) + ' من ' + assets.length : 'Frame ' + (originalIndex + 1) + ' of ' + assets.length);
    const baseAlt = state.item?.demo?.alt?.[state.lang] || state.item?.name?.[state.lang] || '';
    image.alt = String(baseAlt) + ' — ' + phaseName;
  }
  function stopTimer() {
    if (timer !== null) window.clearInterval(timer);
    timer = null;
  }
  function pauseAndReset() {
    stopTimer();
    if (!current) return;
    current.index = 0;
    renderFrame(current, 0);
  }
  function motionAllowed(state) {
    return current === state && !state.reduced && !reducedMotion()
      && screenActive() && !videoVisible()
      && Array.isArray(state.frames) && state.frames.length > 1;
  }
  function startTimer(state) {
    if (timer !== null || !motionAllowed(state)) return;
    setPhase('playing', state);
    timer = window.setInterval(() => {
      if (current !== state) { stopTimer(); return; }
      if (!motionAllowed(state)) {
        pauseAndReset();
        setPhase(state.reduced || reducedMotion() ? 'reduced' : 'paused', state);
        return;
      }
      state.index = (state.index + 1) % state.frames.length;
      renderFrame(state, state.index);
    }, FRAME_MS);
  }
  function preloadAsset(asset) {
    if (preloadCache.has(asset)) return preloadCache.get(asset);
    const url = localAsset(asset);
    if (!url) return Promise.resolve(false);
    const result = new Promise(resolve => {
      let probe;
      try { probe = new Image(); }
      catch { resolve(false); return; }
      let settled = false;
      let timeoutId = null;
      const finish = ok => {
        if (settled) return;
        settled = true;
        if (timeoutId !== null) window.clearTimeout(timeoutId);
        probe.removeEventListener('load', onLoad);
        probe.removeEventListener('error', onError);
        resolve(Boolean(ok));
      };
      const onLoad = () => finish(true);
      const onError = () => finish(false);
      probe.addEventListener('load', onLoad);
      probe.addEventListener('error', onError);
      timeoutId = window.setTimeout(() => finish(false), PRELOAD_TIMEOUT_MS);
      probe.src = url;
    });
    preloadCache.set(asset, result);
    return result;
  }
  function loadFrames(state) {
    if (state.pending || state.frames) return;
    const entries = (state.item.demo.assets || [])
      .map((asset, originalIndex) => ({asset, originalIndex}))
      .filter(entry => localAsset(entry.asset));
    if (!entries.length) {
      state.frames = [];
      renderFrame(state, 0);
      setPhase('missing', state);
      return;
    }
    state.pending = true;
    setPhase('preparing', state);
    Promise.all(entries.map(entry => preloadAsset(entry.asset))).then(results => {
      if (current !== state) return;
      state.pending = false;
      state.frames = entries.filter((entry, index) => results[index]);
      state.index = 0;
      renderFrame(state, 0);
      if (hasNoFrames(state)) { setPhase('missing', state); return; }
      if (state.reduced || reducedMotion()) {
        pauseAndReset();
        setPhase('reduced', state);
        return;
      }
      if (state.frames.length < 2) { setPhase('unavailable', state); return; }
      if (motionAllowed(state)) startTimer(state);
      else setPhase('ready', state);
    });
  }
  function render(item, lang, reduced) {
    if (!item || !item.id || !Array.isArray(item.demo?.assets) || !item.demo.assets.length) {
      stop();
      return;
    }
    if (videoVisible()) { stop(); return; }
    const sameExercise = current && current.item.id === item.id;
    if (!sameExercise) {
      stop();
      current = {item, lang: lang === 'ar' ? 'ar' : 'en', reduced: Boolean(reduced), frames: null, index: 0, pending: false};
    } else {
      current.item = item;
      current.lang = lang === 'ar' ? 'ar' : 'en';
      current.reduced = Boolean(reduced);
    }
    const state = current;
    renderFrame(state, state.index);
    if (hasNoFrames(state)) { setPhase('missing', state); return; }
    if (state.reduced || reducedMotion()) {
      pauseAndReset();
      setPhase('reduced', state);
      return;
    }
    if (!screenActive()) {
      pauseAndReset();
      setPhase(state.frames ? 'ready' : 'preparing', state);
      return;
    }
    if (state.frames) {
      if (state.frames.length > 1) startTimer(state);
      else setPhase('unavailable', state);
      return;
    }
    loadFrames(state);
  }
  function reconcile() {
    if (!current) return;
    const state = current;
    if (videoVisible()) { stop(); return; }
    if (hasNoFrames(state)) { setPhase('missing', state); return; }
    if (state.reduced || reducedMotion()) {
      pauseAndReset();
      setPhase('reduced', state);
      return;
    }
    if (!screenActive()) {
      pauseAndReset();
      setPhase('paused', state);
      return;
    }
    if (state.frames) {
      if (state.frames.length > 1) startTimer(state);
      else setPhase('unavailable', state);
      return;
    }
    loadFrames(state);
  }
  function stop() { stopTimer(); current = null; }

  document.addEventListener('visibilitychange', reconcile);
  document.getElementById('reduceMotion')?.addEventListener('change', () => {
    if (current) { current.reduced = reducedMotion(); reconcile(); }
  });
  window.addEventListener('pagehide', () => {
    if (current) { pauseAndReset(); setPhase(hasNoFrames(current) ? 'missing' : 'paused', current); }
  });
  window.addEventListener('pageshow', reconcile);
  window.THFActiveWorkoutDemoMotion = {render, reconcile, stop};
})();