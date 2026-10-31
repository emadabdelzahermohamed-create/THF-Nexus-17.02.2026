/* Offline auto-motion for exercise-library cards and detail sheets.
 * Uses only the catalog's audited local frames; never synthesizes anatomy.
 * Explicit in-app reduced-motion choice overrides the OS preference.
 */
(() => {
  'use strict';

  const FRAME_MS = 900;
  const PRELOAD_TIMEOUT_MS = 1200;
  const grid = document.getElementById('exerciseGrid');
  const detailRoot = document.getElementById('exerciseDetail');
  const detailDemo = document.getElementById('detailDemo');
  const detailStatus = document.getElementById('detailDemoStatus');
  const states = new Map();
  const preloadCache = new Map();
  const exercises = () => Array.isArray(window.THF_EXERCISES) ? window.THF_EXERCISES : [];
  let cardObserver = null;
  let gridObserver = null;
  let detailRootObserver = null;
  let detailFramesObserver = null;
  let timer = null;
  let detailIndex = 0;
  let detailLoad = null;
  let scrollRefreshPending = false;

  const itemById = id => exercises().find(item => item.id === id);
  const localAsset = asset => typeof asset === 'string' && asset.length > 0 && !asset.startsWith('/') && !asset.includes('..')
    ? './' + asset
    : null;

  function savedMotionPreference() {
    try {
      const value = window.localStorage?.getItem('pulse.v2.reduceMotion');
      if (value === '1') return true;
      if (value === '0') return false;
    } catch (_) {}
    return null;
  }

  function reduceMotion() {
    const saved = savedMotionPreference();
    if (saved !== null) return saved;
    const query = window.matchMedia?.('(prefers-reduced-motion: reduce)');
    if (query) return Boolean(query.matches);
    return Boolean(document.getElementById('reduceMotion')?.checked);
  }

  function visibleInViewport(card) {
    if (!card || card.isConnected === false || typeof card.getBoundingClientRect !== 'function') return false;
    const rect = card.getBoundingClientRect();
    const width = window.innerWidth || document.documentElement?.clientWidth || 0;
    const height = window.innerHeight || document.documentElement?.clientHeight || 0;
    return rect.width > 0 && rect.height > 0 && rect.bottom > 0 && rect.right > 0
      && rect.top < height && rect.left < width;
  }

  function preloadAsset(asset) {
    const url = localAsset(asset);
    if (!url) return Promise.resolve(false);
    if (preloadCache.has(url)) return preloadCache.get(url);
    const result = new Promise(resolve => {
      const image = new window.Image();
      let settled = false;
      let timeoutId = null;
      const finish = loaded => {
        if (settled) return;
        settled = true;
        if (timeoutId !== null) window.clearTimeout(timeoutId);
        image.removeEventListener?.('load', onLoad);
        image.removeEventListener?.('error', onError);
        resolve(loaded);
      };
      const onLoad = () => finish(true);
      const onError = () => finish(false);
      image.addEventListener('load', onLoad);
      image.addEventListener('error', onError);
      timeoutId = window.setTimeout(() => finish(false), PRELOAD_TIMEOUT_MS);
      image.src = url;
    });
    preloadCache.set(url, result);
    return result;
  }

  function setCardFrame(state, index) {
    const frames = Array.isArray(state.frames) ? state.frames : state.item.demo.assets;
    const asset = frames[index];
    const url = localAsset(asset);
    if (!url || !state.image) return;
    state.index = index;
    if (state.image.getAttribute('src') !== url) {
      state.image.classList.remove('demo-frame-swap');
      state.image.setAttribute('src', url);
      void state.image.offsetWidth;
      state.image.classList.add('demo-frame-swap');
    }
    state.image.dataset.demoFrame = String(index);
  }

  function resetCard(state) {
    if (!state || !state.item?.demo?.assets?.length) return;
    state.index = 0;
    const firstFrame = Array.isArray(state.frames) ? state.frames[0] : state.item.demo.assets[0];
    const url = localAsset(firstFrame);
    if (url && state.image && state.image.getAttribute('src') !== url) state.image.setAttribute('src', url);
    state.image?.classList.remove('demo-frame-swap');
    if (state.image) state.image.dataset.demoFrame = '0';
  }

  function loadCardFrames(state) {
    if (state.ready || state.loading || state.settled || state.item.demo.assets.length < 2) return;
    state.loading = true;
    const assets = state.item.demo.assets;
    Promise.all(assets.slice(1).map(preloadAsset)).then(results => {
      state.loading = false;
      // Keep every successfully decoded local frame. One damaged secondary
      // asset must not disable motion when two or more reviewed frames remain.
      state.frames = [assets[0], ...assets.slice(1).filter((_, index) => results[index])];
      state.ready = state.frames.length > 1;
      state.settled = true;
      if (!state.ready) resetCard(state);
      syncTimer();
    });
  }

  function scanCards() {
    if (!grid) return;
    const cards = Array.from(grid.querySelectorAll('.exercise-card'));
    const current = new Set(cards);
    for (const [card, state] of states) {
      if (current.has(card)) continue;
      cardObserver?.unobserve(card);
      states.delete(card);
    }
    for (const card of cards) {
      if (states.has(card)) continue;
      const item = itemById(card.dataset.id);
      const image = card.querySelector('.media img');
      const assets = item?.demo?.assets;
      if (!item || item.demo?.offline === false || !Array.isArray(assets) || assets.length < 2 || !image) continue;
      const state = { card, item, image, index: 0, frames: null, visible: false, ready: false, loading: false, settled: false };
      states.set(card, state);
      if (cardObserver) cardObserver.observe(card);
      else state.visible = visibleInViewport(card);
      if (state.visible && !reduceMotion() && !document.hidden) loadCardFrames(state);
    }
    for (const state of states.values()) {
      if (!cardObserver) state.visible = visibleInViewport(state.card);
      // Also preload cards that were already visible when reduced motion was enabled.
      // This lets animation resume immediately when the user turns it back off.
      if (state.visible && !reduceMotion() && !document.hidden) loadCardFrames(state);
    }
  }

  function allDetailFrames() {
    return detailDemo ? Array.from(detailDemo.querySelectorAll('.detail-frame')) : [];
  }

  function detailFrames() {
    return allDetailFrames().filter(frame => {
      const state = frame.getAttribute('data-demo-playable');
      return state !== 'pending' && state !== 'false';
    });
  }

  function detailIsOpen() {
    return Boolean(detailRoot && !detailRoot.classList.contains('hidden') && detailFrames().length > 1);
  }

  function detailExercise() {
    const first = detailDemo?.querySelector('.detail-frame img');
    const src = first?.getAttribute('src');
    if (!src) return null;
    return exercises().find(item => localAsset(item.demo?.assets?.[0]) === src) || null;
  }

  const detailStatusLabels = {
    loading: {en: 'Loading offline exercise demonstration…', ar: 'جارٍ تحميل العرض الحركي دون إنترنت…'},
    playing: {en: 'Offline demonstration is playing automatically.', ar: 'العرض دون إنترنت يعمل تلقائيًا.'},
    reduced: {en: 'Reduced motion is enabled; static reference frames are shown.', ar: 'تقليل الحركة مفعّل؛ تُعرض صور مرجعية ثابتة.'},
    paused: {en: 'Demonstration paused while the app is in the background.', ar: 'تم إيقاف العرض مؤقتًا أثناء وجود التطبيق في الخلفية.'},
    static: {en: 'Showing static offline reference frames.', ar: 'تُعرض صور مرجعية ثابتة دون حركة.'},
    single: {en: 'Motion unavailable; showing the one available reference frame.', ar: 'الحركة غير متاحة؛ تُعرض الصورة المرجعية الوحيدة المتاحة.'},
    unavailable: {en: 'Offline demonstration unavailable — no local frame could be loaded.', ar: 'العرض دون إنترنت غير متاح — تعذر تحميل أي إطار محلي.'}
  };

  function setDetailStatus(key) {
    if (!detailStatus) return;
    const lang = document.documentElement?.lang === 'ar' ? 'ar' : 'en';
    const label = key ? (detailStatusLabels[key]?.[lang] || '') : '';
    if (detailStatus.textContent !== label) detailStatus.textContent = label;
  }

  function loadDetailFrames() {
    const item = detailExercise();
    const frames = allDetailFrames();
    const assets = Array.isArray(item?.demo?.assets) ? item.demo.assets : [];
    if (!detailRoot || detailRoot.classList.contains('hidden')) {
      setDetailStatus('');
      return;
    }
    if (!item || frames.length < 1 || assets.length < 1 || frames.length !== assets.length) {
      for (const frame of frames) {
        frame.setAttribute('data-demo-playable', 'false');
        frame.setAttribute('hidden', '');
        frame.setAttribute('aria-hidden', 'true');
      }
      detailLoad = item ? {id: item.id, frames, settled: true} : null;
      setDetailStatus('unavailable');
      return;
    }

    const sameFrames = detailLoad && detailLoad.id === item.id
      && detailLoad.frames.length === frames.length
      && detailLoad.frames.every((frame, index) => frame === frames[index]);
    if (sameFrames) return;

    const token = { id: item.id, frames, settled: false };
    detailLoad = token;
    frames.forEach(frame => {
      frame.setAttribute('data-demo-playable', 'pending');
      frame.setAttribute('hidden', '');
      frame.setAttribute('aria-hidden', 'true');
    });
    setDetailStatus('loading');

    // Validate every frame, including the initial frame already present in the DOM.
    // A broken first image must not remain the assumed reference when later frames work.
    const pending = assets.map(asset => localAsset(asset) ? preloadAsset(asset) : Promise.resolve(false));
    Promise.all(pending).then(results => {
      if (detailLoad !== token) return;
      const currentFrames = allDetailFrames();
      if (currentFrames.length !== token.frames.length
        || currentFrames.some((frame, index) => frame !== token.frames[index])) return;

      for (let index = 0; index < frames.length; index++) {
        const loaded = Boolean(results[index]) && Boolean(localAsset(assets[index]));
        if (loaded) {
          frames[index].setAttribute('data-demo-playable', 'true');
          frames[index].removeAttribute('hidden');
          frames[index].removeAttribute('aria-hidden');
        } else {
          frames[index].setAttribute('data-demo-playable', 'false');
          frames[index].setAttribute('hidden', '');
          frames[index].setAttribute('aria-hidden', 'true');
        }
      }
      token.settled = true;
      detailIndex = 0;
      renderDetailSequence(!reduceMotion() && !document.hidden);
      syncTimer();
    });
  }

  function renderDetailSequence(animate) {
    const allFrames = allDetailFrames();
    const frames = detailFrames();
    if (!detailRoot || detailRoot.classList.contains('hidden')) {
      detailDemo?.classList.remove('auto-sequence');
      detailDemo?.classList.remove('single-reference');
      for (const frame of allFrames) frame.classList.remove('is-active');
      setDetailStatus('');
      return;
    }
    if (detailLoad && !detailLoad.settled && detailLoad.id === detailExercise()?.id) {
      detailDemo?.classList.remove('auto-sequence');
      detailDemo?.classList.remove('single-reference');
      setDetailStatus('loading');
      return;
    }
    if (frames.length < 2) {
      detailDemo?.classList.remove('auto-sequence');
      detailDemo?.classList.toggle('single-reference', frames.length === 1);
      const playable = new Set(frames);
      for (const frame of allFrames) {
        frame.classList.remove('is-active');
        if (playable.has(frame)) {
          frame.removeAttribute('hidden');
          frame.removeAttribute('aria-hidden');
        } else {
          frame.setAttribute('hidden', '');
          frame.setAttribute('aria-hidden', 'true');
        }
      }
      setDetailStatus(frames.length === 1 ? 'single' : 'unavailable');
      return;
    }
    const active = Boolean(animate && detailIsOpen() && !reduceMotion() && !document.hidden);
    detailDemo.classList.remove('single-reference');
    detailDemo.classList.toggle('auto-sequence', active);
    if (!active) detailIndex = 0;
    const playable = new Set(frames);
    frames.forEach((frame, index) => {
      frame.removeAttribute('hidden');
      const isActive = active && index === detailIndex;
      frame.classList.toggle('is-active', isActive);
      if (active && !isActive) frame.setAttribute('aria-hidden', 'true');
      else frame.removeAttribute('aria-hidden');
    });
    for (const frame of allFrames) {
      if (playable.has(frame)) continue;
      frame.classList.remove('is-active');
      frame.setAttribute('hidden', '');
      frame.setAttribute('aria-hidden', 'true');
    }
    setDetailStatus(active ? 'playing' : reduceMotion() ? 'reduced' : document.hidden ? 'paused' : 'static');
  }

  function stopTimer() {
    if (timer !== null) window.clearInterval(timer);
    timer = null;
  }

  function syncTimer() {
    if (reduceMotion() || document.hidden) {
      stopTimer();
      return;
    }
    if (!cardObserver) {
      for (const state of states.values()) state.visible = visibleInViewport(state.card);
    }
    const visibleReadyCard = Array.from(states.values()).some(state => state.visible && state.ready);
    const shouldRun = visibleReadyCard || detailIsOpen();
    if (shouldRun && timer === null) timer = window.setInterval(tick, FRAME_MS);
    else if (!shouldRun) stopTimer();
  }

  function tick() {
    if (reduceMotion() || document.hidden) {
      refresh();
      return;
    }
    if (!cardObserver) {
      for (const state of states.values()) state.visible = visibleInViewport(state.card);
    }
    for (const state of states.values()) {
      const frames = Array.isArray(state.frames) ? state.frames : state.item.demo.assets;
      if (!state.visible || !state.ready || frames.length < 2) continue;
      setCardFrame(state, (state.index + 1) % frames.length);
    }
    if (detailIsOpen()) {
      const item = detailExercise();
      const frames = detailFrames();
      if (item && frames.length > 1) {
        detailIndex = (detailIndex + 1) % frames.length;
        renderDetailSequence(true);
      }
    }
    syncTimer();
  }

  function refresh() {
    scanCards();
    loadDetailFrames();
    if (reduceMotion() || document.hidden) {
      stopTimer();
      for (const state of states.values()) resetCard(state);
      detailIndex = 0;
      renderDetailSequence(false);
      return;
    }
    if (!detailIsOpen()) detailIndex = 0;
    renderDetailSequence(true);
    syncTimer();
  }

  function scheduleScrollRefresh() {
    if (scrollRefreshPending) return;
    if (typeof window.requestAnimationFrame !== 'function') {
      refresh();
      return;
    }
    scrollRefreshPending = true;
    window.requestAnimationFrame(() => {
      scrollRefreshPending = false;
      refresh();
    });
  }

  function init() {
    if (typeof window.IntersectionObserver === 'function') {
      cardObserver = new window.IntersectionObserver(entries => {
        for (const entry of entries) {
          const state = states.get(entry.target);
          if (!state) continue;
          state.visible = Boolean(entry.isIntersecting && entry.intersectionRatio > 0);
          if (state.visible && !reduceMotion() && !document.hidden) loadCardFrames(state);
        }
        syncTimer();
      }, { rootMargin: '64px', threshold: 0.01 });
    }
    // Browsers without IntersectionObserver need scroll events to resume visible-card motion.
    // Coalesce a burst of legacy-WebView scroll events to one viewport scan per frame.
    if (!cardObserver) window.addEventListener('scroll', scheduleScrollRefresh, { passive: true });
    if (typeof window.MutationObserver === 'function') {
      if (grid) {
        gridObserver = new window.MutationObserver(refresh);
        gridObserver.observe(grid, { childList: true });
      }
      if (detailRoot) {
        detailRootObserver = new window.MutationObserver(refresh);
        detailRootObserver.observe(detailRoot, { attributes: true, attributeFilter: ['class'] });
      }
      if (detailDemo) {
        detailFramesObserver = new window.MutationObserver(() => {
          detailIndex = 0;
          refresh();
        });
        detailFramesObserver.observe(detailDemo, { childList: true });
      }
    }
    document.getElementById('reduceMotion')?.addEventListener('change', () => Promise.resolve().then(refresh));
    document.addEventListener('visibilitychange', refresh);
    window.addEventListener('resize', refresh, { passive: true });
    const query = window.matchMedia?.('(prefers-reduced-motion: reduce)');
    if (query?.addEventListener) query.addEventListener('change', refresh);
    else query?.addListener?.(refresh);
    refresh();
  }

  init();
})();