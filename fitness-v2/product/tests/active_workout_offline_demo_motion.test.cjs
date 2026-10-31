const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');

const pulse = path.resolve(__dirname, '../../android/app/src/main/assets/pulse');
const source = fs.readFileSync(path.join(pulse, 'active-workout-demo-motion.js'), 'utf8');

function classList(initial = []) {
  const values = new Set(initial);
  return {
    add(name) { values.add(name); },
    remove(name) { values.delete(name); },
    contains(name) { return values.has(name); },
    toggle(name, force) {
      const enabled = force === undefined ? !values.has(name) : Boolean(force);
      if (enabled) values.add(name); else values.delete(name);
      return enabled;
    }
  };
}

function createHarness(active = true, includeStatus = true) {
  const probes = [];
  const intervals = new Map();
  const timeouts = new Map();
  const documentListeners = new Map();
  const windowListeners = new Map();
  let nextId = 1;
  const root = {classList: classList(active ? ['active'] : [])};
  const image = {
    attrs: {}, alt: '', classList: classList(['hidden']),
    getAttribute(name) { return this.attrs[name] ?? null; },
    setAttribute(name, value) { this.attrs[name] = String(value); },
    removeAttribute(name) { delete this.attrs[name]; }
  };
  const video = {classList: classList(['hidden'])};
  const phase = {textContent: ''};
  const status = {textContent: ''};
  const reduceMotion = {
    checked: false, handlers: [],
    addEventListener(name, callback) { if (name === 'change') this.handlers.push(callback); }
  };
  const elements = {activeWorkoutScreen: root, activeDemoImage: image, activeDemoVideo: video, activeDemoPhase: phase, activeDemoStatus: status, reduceMotion};
  if (!includeStatus) delete elements.activeDemoStatus;
  const document = {
    hidden: false,
    getElementById(id) { return elements[id] || null; },
    addEventListener(name, callback) {
      const list = documentListeners.get(name) || [];
      list.push(callback); documentListeners.set(name, list);
    },
    dispatch(name) { for (const callback of documentListeners.get(name) || []) callback(); }
  };
  const window = {
    setInterval(callback, ms) { const id = nextId++; intervals.set(id, {callback, ms}); return id; },
    clearInterval(id) { intervals.delete(id); },
    setTimeout(callback, ms) { const id = nextId++; timeouts.set(id, {callback, ms}); return id; },
    clearTimeout(id) { timeouts.delete(id); },
    addEventListener(name, callback) {
      const list = windowListeners.get(name) || [];
      list.push(callback); windowListeners.set(name, list);
    },
    dispatch(name) { for (const callback of windowListeners.get(name) || []) callback(); },
    matchMedia() { return {matches: false}; }
  };
  class FakeImage {
    constructor() { this.listeners = new Map(); this._src = ''; probes.push(this); }
    addEventListener(name, callback) {
      const list = this.listeners.get(name) || [];
      list.push(callback); this.listeners.set(name, list);
    }
    removeEventListener(name, callback) {
      this.listeners.set(name, (this.listeners.get(name) || []).filter(value => value !== callback));
    }
    set src(value) { this._src = value; }
    get src() { return this._src; }
    emit(name) { for (const callback of [...(this.listeners.get(name) || [])]) callback(); }
    listenerCount() { return [...this.listeners.values()].reduce((sum, list) => sum + list.length, 0); }
  }
  new Function('window', 'document', 'Image', source)(window, document, FakeImage);
  return {
    api: window.THFActiveWorkoutDemoMotion, document, root, image, video, phase, status, probes, intervals, timeouts,
    runInterval() { for (const value of [...intervals.values()]) value.callback(); },
    runTimeouts() {
      for (const [id, value] of [...timeouts.entries()]) {
        if (!timeouts.has(id)) continue;
        timeouts.delete(id); value.callback();
      }
    }
  };
}

function sampleItem() {
  return {
    id: 'offline-demo',
    name: {en: 'Offline Demo', ar: 'عرض أوفلاين'},
    demo: {
      assets: ['media/demo/0.jpg', 'media/demo/1.jpg'],
      alt: {en: 'Start and finish positions for Offline Demo', ar: 'وضعا البداية والنهاية لعرض أوفلاين'}
    }
  };
}
async function flushPromises() {
  await Promise.resolve(); await Promise.resolve(); await Promise.resolve();
}

test('starts cycling automatically after local frames load, without a user tap', async () => {
  const h = createHarness();
  h.api.render(sampleItem(), 'en', false);
  assert.equal(h.intervals.size, 0);
  assert.equal(h.phase.textContent, 'Preparing offline demo…');
  assert.equal(h.probes.length, 2);
  h.probes[0].emit('load'); h.probes[1].emit('load');
  await flushPromises();
  assert.equal(h.intervals.size, 1);
  assert.equal(h.phase.textContent, 'Automatic reference sequence');
  h.runInterval();
  assert.equal(h.image.getAttribute('src'), './media/demo/1.jpg');
  assert.match(h.image.alt, /Finish/);
});

test('language rerender updates alt text without restarting the active frame timer', async () => {
  const h = createHarness(); const item = sampleItem();
  h.api.render(item, 'en', false);
  h.probes[0].emit('load'); h.probes[1].emit('load'); await flushPromises();
  h.runInterval();
  const currentSrc = h.image.getAttribute('src');
  h.api.render(item, 'ar', false);
  assert.equal(h.image.getAttribute('src'), currentSrc);
  assert.match(h.image.alt, /النهاية/);
  assert.equal(h.intervals.size, 1);
});

test('reduced motion stops cycling and restores the first static frame', async () => {
  const h = createHarness(); const item = sampleItem();
  h.api.render(item, 'en', false);
  h.probes[0].emit('load'); h.probes[1].emit('load'); await flushPromises();
  h.api.render(item, 'ar', true);
  assert.equal(h.intervals.size, 0);
  assert.equal(h.image.getAttribute('src'), './media/demo/0.jpg');
  assert.match(h.phase.textContent, /تقليل الحركة/);
});

test('backgrounding pauses and resets, then resumes automatically when visible', async () => {
  const h = createHarness();
  h.api.render(sampleItem(), 'en', false);
  h.probes[0].emit('load'); h.probes[1].emit('load'); await flushPromises();
  h.runInterval();
  h.document.hidden = true; h.document.dispatch('visibilitychange');
  assert.equal(h.intervals.size, 0);
  assert.equal(h.image.getAttribute('src'), './media/demo/0.jpg');
  h.document.hidden = false; h.document.dispatch('visibilitychange');
  assert.equal(h.intervals.size, 1);
});

test('leaving and re-entering the active workout screen stops and resumes motion', async () => {
  const h = createHarness();
  h.api.render(sampleItem(), 'en', false);
  h.probes[0].emit('load'); h.probes[1].emit('load'); await flushPromises();
  h.root.classList.remove('active'); h.api.reconcile();
  assert.equal(h.intervals.size, 0);
  h.root.classList.add('active'); h.api.reconcile();
  assert.equal(h.intervals.size, 1);
});

test('a failed secondary frame leaves a stable static reference instead of a broken loop', async () => {
  const h = createHarness();
  h.api.render(sampleItem(), 'en', false);
  h.probes[0].emit('load'); h.probes[1].emit('error'); await flushPromises();
  assert.equal(h.intervals.size, 0);
  assert.equal(h.image.getAttribute('src'), './media/demo/0.jpg');
  assert.match(h.phase.textContent, /motion unavailable/);
});

test('a stalled decoder times out and releases both event listeners', async () => {
  const h = createHarness();
  h.api.render(sampleItem(), 'en', false);
  h.runTimeouts(); await flushPromises();
  assert.equal(h.intervals.size, 0);
  assert.match(h.phase.textContent, /motion unavailable/);
  assert.equal(h.probes.reduce((sum, probe) => sum + probe.listenerCount(), 0), 0);
});

test('a reviewed video demo never starts the fallback image timer', () => {
  const h = createHarness();
  h.video.classList.remove('hidden');
  h.api.render(sampleItem(), 'en', false);
  assert.equal(h.probes.length, 0);
  assert.equal(h.intervals.size, 0);
});

test('reduced motion enabled during preload remains static after frames resolve', async () => {
  const h = createHarness(); const item = sampleItem();
  h.api.render(item, 'en', false);
  h.api.render(item, 'ar', true);
  h.probes[0].emit('load'); h.probes[1].emit('load'); await flushPromises();
  assert.equal(h.intervals.size, 0);
  assert.equal(h.image.getAttribute('src'), './media/demo/0.jpg');
  assert.match(h.phase.textContent, /تقليل الحركة/);
});

test('a hidden workout screen defers preload until the screen becomes active', async () => {
  const h = createHarness(false);
  h.api.render(sampleItem(), 'en', false);
  assert.equal(h.probes.length, 0);
  h.root.classList.add('active'); h.api.reconcile();
  assert.equal(h.probes.length, 2);
  h.probes[0].emit('load'); h.probes[1].emit('load'); await flushPromises();
  assert.equal(h.intervals.size, 1);
});

test('all local frames failing hides the broken image and announces unavailable in both languages', async () => {
  const h = createHarness(); const item = sampleItem();
  h.api.render(item, 'en', false);
  h.probes[0].emit('error'); h.probes[1].emit('error'); await flushPromises();
  assert.equal(h.intervals.size, 0);
  assert.equal(h.image.classList.contains('hidden'), true);
  assert.equal(h.image.getAttribute('src'), null);
  assert.equal(h.image.alt, '');
  assert.equal(h.phase.textContent, 'Offline demo unavailable — no local image could be decoded');
  h.api.render(item, 'ar', false);
  assert.equal(h.image.classList.contains('hidden'), true);
  assert.equal(h.phase.textContent, 'تعذر عرض التمرين دون إنترنت — لم يمكن فك أي صورة');
});

test('a surviving later frame remains visible as a truthful static fallback when the first fails', async () => {
  const h = createHarness();
  h.api.render(sampleItem(), 'en', false);
  h.probes[0].emit('error'); h.probes[1].emit('load'); await flushPromises();
  assert.equal(h.intervals.size, 0);
  assert.equal(h.image.classList.contains('hidden'), false);
  assert.equal(h.image.getAttribute('src'), './media/demo/1.jpg');
  assert.match(h.image.alt, /Finish/);
  assert.match(h.phase.textContent, /motion unavailable/);
});

test('invalid non-local demo paths do not leave the previous or broken image visible', async () => {
  const h = createHarness();
  h.api.render(sampleItem(), 'en', false);
  h.probes[0].emit('load'); h.probes[1].emit('load'); await flushPromises();
  const priorProbeCount = h.probes.length;
  const invalid = {...sampleItem(), id: 'invalid-path', demo: {...sampleItem().demo, assets: ['https://example.invalid/demo.jpg']}};
  h.api.render(invalid, 'en', false);
  assert.equal(h.probes.length, priorProbeCount);
  assert.equal(h.image.classList.contains('hidden'), true);
  assert.equal(h.image.getAttribute('src'), null);
  assert.equal(h.image.alt, '');
  assert.match(h.phase.textContent, /no local image could be decoded/);
});


test('screen-reader status announces bilingual state changes without per-frame chatter', async () => {
  const h = createHarness(); const item = sampleItem();
  h.api.render(item, 'en', false);
  h.probes[0].emit('load'); h.probes[1].emit('load'); await flushPromises();
  assert.equal(h.status.textContent, 'Automatic reference sequence');
  h.runInterval();
  assert.equal(h.status.textContent, 'Automatic reference sequence');
  h.api.render(item, 'ar', false);
  assert.equal(h.status.textContent, 'تسلسل مرجعي تلقائي');
  assert.equal(h.phase.textContent, 'تسلسل مرجعي تلقائي');
  assert.equal(h.intervals.size, 1);
});

test('screen-reader status announces pause, reduced-motion, and unavailable states', async () => {
  const h = createHarness(); const item = sampleItem();
  h.api.render(item, 'en', false);
  h.probes[0].emit('load'); h.probes[1].emit('load'); await flushPromises();
  h.document.hidden = true; h.document.dispatch('visibilitychange');
  assert.equal(h.status.textContent, 'Demo paused while workout is hidden');
  h.document.hidden = false; h.document.dispatch('visibilitychange');
  assert.equal(h.status.textContent, 'Automatic reference sequence');
  h.api.render(item, 'ar', true);
  assert.equal(h.status.textContent, 'صورة ثابتة — تقليل الحركة');
  const failed = createHarness();
  failed.api.render(item, 'en', false);
  failed.probes[0].emit('error'); failed.probes[1].emit('error'); await flushPromises();
  assert.equal(failed.status.textContent, 'Offline demo unavailable — no local image could be decoded');
});

test('active demo remains usable when the optional screen-reader status node is absent', async () => {
  const h = createHarness(true, false);
  h.api.render(sampleItem(), 'en', false);
  h.probes[0].emit('load'); h.probes[1].emit('load'); await flushPromises();
  assert.equal(h.phase.textContent, 'Automatic reference sequence');
  assert.equal(h.intervals.size, 1);
});
