'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const sourcePath = path.resolve(__dirname, '../../android/app/src/main/assets/pulse/library-demo-motion.js');
const source = fs.readFileSync(sourcePath, 'utf8');
const indexPath = path.resolve(__dirname, '../../android/app/src/main/assets/pulse/index.html');
const indexSource = fs.readFileSync(indexPath, 'utf8');

class FakeClassList {
  constructor(initial = []) { this.values = new Set(initial); }
  contains(value) { return this.values.has(value); }
  add(value) { this.values.add(value); }
  remove(value) { this.values.delete(value); }
  toggle(value, force) {
    if (force === undefined) force = !this.values.has(value);
    if (force) this.values.add(value); else this.values.delete(value);
    return force;
  }
}

class FakeElement {
  constructor({ id = '', classes = [], dataset = {}, rect = { top: 0, left: 0, right: 120, bottom: 90, width: 120, height: 90 } } = {}) {
    this.id = id;
    this.classList = new FakeClassList(classes);
    this.dataset = { ...dataset };
    this.attributes = new Map();
    this.listeners = new Map();
    this.children = [];
    this.rect = rect;
    this.isConnected = true;
    this.textContent = '';
    this.offsetWidth = 120;
  }
  addEventListener(type, callback) {
    if (!this.listeners.has(type)) this.listeners.set(type, []);
    this.listeners.get(type).push(callback);
  }
  dispatch(type) { for (const callback of this.listeners.get(type) || []) callback({ type, target: this }); }
  setAttribute(name, value) { this.attributes.set(name, String(value)); }
  getAttribute(name) { return this.attributes.has(name) ? this.attributes.get(name) : null; }
  removeAttribute(name) { this.attributes.delete(name); }
  querySelector(selector) {
    if (selector === '.media img') return this.image || null;
    if (selector === '.detail-frame img') return this.children[0]?.image || null;
    return null;
  }
  querySelectorAll(selector) {
    if (selector === '.exercise-card') return this.children;
    if (selector === '.detail-frame') return this.children;
    return [];
  }
  getBoundingClientRect() { return this.rect; }
  getClientRects() { return this.rect.width > 0 && this.rect.height > 0 ? [{}] : []; }
}

function buildHarness({ reduced = false, visible = true, intersectionObserver = true, imageLoadMode = 'load', exerciseAssets = null } = {}) {
  const timers = new Map();
  const timeouts = new Map();
  const images = [];
  const mutationObservers = [];
  const intersectionObservers = [];
  const mediaListeners = new Map();
  const windowListeners = new Map();
  const animationFrames = new Map();
  let nextTimer = 1;
  let nextTimeout = 1;
  let nextFrame = 1;
  let storedPreference = null;

  const imageFor = (src, alt = '') => {
    const image = new FakeElement();
    image.setAttribute('src', src);
    image.setAttribute('alt', alt);
    return image;
  };
  const exercise = {
    id: 'demo-test',
    demo: {
      type: 'two_frame_image_sequence',
      offline: true,
      assets: exerciseAssets || ['media/demo-test/0.jpg', 'media/demo-test/1.jpg'],
      alt: { en: 'Start and finish positions for demo test', ar: 'وضعا البداية والنهاية لتمرين تجريبي' }
    }
  };
  const cardImage = imageFor('./media/demo-test/0.jpg', exercise.demo.alt.en);
  const card = new FakeElement({ classes: ['exercise-card'], dataset: { id: exercise.id }, rect: visible
    ? { top: 0, left: 0, right: 120, bottom: 90, width: 120, height: 90 }
    : { top: 500, left: 0, right: 0, bottom: 500, width: 0, height: 0 } });
  card.image = cardImage;
  const grid = new FakeElement({ id: 'exerciseGrid' });
  grid.children = [card];

  const detailFrames = exercise.demo.assets.map(asset => {
    const image = imageFor('./' + asset, exercise.demo.alt.en);
    const frame = new FakeElement({ classes: ['detail-frame'] });
    frame.image = image;
    return frame;
  });
  const frame0 = detailFrames[0];
  const frame1 = detailFrames[1];
  const frame2 = detailFrames[2] || null;
  const detailDemo = new FakeElement({ id: 'detailDemo' });
  detailDemo.children = detailFrames;
  const detailRoot = new FakeElement({ id: 'exerciseDetail', classes: ['hidden'] });
  const reduceControl = new FakeElement({ id: 'reduceMotion' });
  reduceControl.checked = false;

  const documentListeners = new Map();
  const document = {
    hidden: false,
    documentElement: { lang: 'en', clientWidth: 400, clientHeight: 800 },
    getElementById(id) {
      return ({ exerciseGrid: grid, exerciseDetail: detailRoot, detailDemo, reduceMotion: reduceControl })[id] || null;
    },
    addEventListener(type, callback) {
      if (!documentListeners.has(type)) documentListeners.set(type, []);
      documentListeners.get(type).push(callback);
    }
  };
  const window = {
    THF_EXERCISES: [exercise],
    innerWidth: 400,
    innerHeight: 800,
    localStorage: { getItem() { return storedPreference; } },
    setInterval(callback, delay) { const id = nextTimer++; timers.set(id, { callback, delay }); return id; },
    clearInterval(id) { timers.delete(id); },
    setTimeout(callback, delay) { const id = nextTimeout++; timeouts.set(id, { callback, delay }); return id; },
    clearTimeout(id) { timeouts.delete(id); },
    addEventListener(type, callback) {
      if (!windowListeners.has(type)) windowListeners.set(type, []);
      windowListeners.get(type).push(callback);
    },
    requestAnimationFrame(callback) {
      const id = nextFrame++;
      animationFrames.set(id, callback);
      return id;
    },
    matchMedia() {
      return {
        get matches() { return reduced; },
        addEventListener(type, callback) {
          if (!mediaListeners.has(type)) mediaListeners.set(type, []);
          mediaListeners.get(type).push(callback);
        },
        addListener(callback) {
          if (!mediaListeners.has('change')) mediaListeners.set('change', []);
          mediaListeners.get('change').push(callback);
        }
      };
    },
    Image: class {
      constructor() { this.listeners = new Map(); images.push(this); }
      addEventListener(type, callback) {
        if (!this.listeners.has(type)) this.listeners.set(type, []);
        this.listeners.get(type).push(callback);
      }
      removeEventListener(type, callback) {
        this.listeners.set(type, (this.listeners.get(type) || []).filter(listener => listener !== callback));
      }
      dispatch(type) {
        for (const callback of [...(this.listeners.get(type) || [])]) callback({ type, target: this });
      }
      set src(value) {
        this._src = value;
        const mode = typeof imageLoadMode === 'function' ? imageLoadMode(value) : imageLoadMode;
        if (mode === 'load') queueMicrotask(() => this.dispatch('load'));
        else if (mode === 'error') queueMicrotask(() => this.dispatch('error'));
      }
      get src() { return this._src; }
    },
    IntersectionObserver: class {
      constructor(callback) { this.callback = callback; this.observed = new Set(); intersectionObservers.push(this); }
      observe(element) {
        this.observed.add(element);
        this.callback([{ target: element, isIntersecting: visible, intersectionRatio: visible ? 1 : 0 }]);
      }
      unobserve(element) { this.observed.delete(element); }
    },
    MutationObserver: class {
      constructor(callback) { this.callback = callback; this.target = null; mutationObservers.push(this); }
      observe(target, options) { this.target = target; this.options = options; }
      unobserve() {}
      disconnect() {}
    }
  };

  if (!intersectionObserver) delete window.IntersectionObserver;

  vm.runInNewContext(source, { window, document, Promise, Map, Set, Array, Boolean, Number, String, Math });

  const fireMutation = target => mutationObservers.filter(observer => observer.target === target).forEach(observer => observer.callback([]));
  const tick = () => {
    const active = Array.from(timers.values())[0];
    assert.ok(active, 'animation timer should be active');
    active.callback();
  };
  const setStoredPreference = value => { storedPreference = value; (mediaListeners.get('change') || []).forEach(callback => callback({ matches: value === '1' })); };
  const fireTimeouts = () => { for (const entry of Array.from(timeouts.values())) entry.callback(); };

  const fireWindow = type => { for (const callback of windowListeners.get(type) || []) callback({ type }); };
  const flushAnimationFrames = () => {
    const callbacks = Array.from(animationFrames.values());
    animationFrames.clear();
    callbacks.forEach(callback => callback());
  };
  return { timers, timeouts, images, animationFrames, grid, card, cardImage, detailRoot, detailDemo, detailFrames, frame0, frame1, frame2, reduceControl, fireMutation, fireWindow, flushAnimationFrames, fireTimeouts, tick, setStoredPreference };
}

test('visible exercise cards cycle audited local frames automatically without a tap', async () => {
  const h = buildHarness();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.cardImage.getAttribute('src'), './media/demo-test/0.jpg');
  assert.ok(h.timers.size > 0);
  h.tick();
  assert.equal(h.cardImage.getAttribute('src'), './media/demo-test/1.jpg');
  h.tick();
  assert.equal(h.cardImage.getAttribute('src'), './media/demo-test/0.jpg');
});

test('exercise detail shows one frame at a time and advances automatically', async () => {
  const h = buildHarness();
  await new Promise(resolve => setImmediate(resolve));
  h.detailRoot.classList.remove('hidden');
  h.fireMutation(h.detailRoot);
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.detailDemo.classList.contains('auto-sequence'), true);
  assert.equal(h.frame0.classList.contains('is-active'), true);
  assert.equal(h.frame1.getAttribute('aria-hidden'), 'true');
  h.tick();
  assert.equal(h.frame0.classList.contains('is-active'), false);
  assert.equal(h.frame1.classList.contains('is-active'), true);
  assert.equal(h.frame0.getAttribute('aria-hidden'), 'true');
});

test('reduced motion stops timers and restores the static two-frame detail', async () => {
  const h = buildHarness();
  await new Promise(resolve => setImmediate(resolve));
  h.detailRoot.classList.remove('hidden');
  h.fireMutation(h.detailRoot);
  await new Promise(resolve => setImmediate(resolve));
  assert.ok(h.timers.size > 0);
  h.setStoredPreference('1');
  assert.equal(h.timers.size, 0);
  assert.equal(h.cardImage.getAttribute('src'), './media/demo-test/0.jpg');
  assert.equal(h.detailDemo.classList.contains('auto-sequence'), false);
  assert.equal(h.frame0.getAttribute('aria-hidden'), null);
  assert.equal(h.frame1.getAttribute('aria-hidden'), null);
});

test('offscreen exercise cards do not start animation work', async () => {
  const h = buildHarness({ visible: false });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.timers.size, 0);
  assert.equal(h.cardImage.getAttribute('src'), './media/demo-test/0.jpg');
});


test('visible cards resume when reduced motion is turned off', async () => {
  const h = buildHarness();
  await new Promise(resolve => setImmediate(resolve));
  h.setStoredPreference('1');
  assert.equal(h.timers.size, 0);
  h.setStoredPreference('0');
  await new Promise(resolve => setImmediate(resolve));
  assert.ok(h.timers.size > 0);
  h.tick();
  assert.equal(h.cardImage.getAttribute('src'), './media/demo-test/1.jpg');
});


test('fallback viewport tracking resumes animation after scrolling when IntersectionObserver is unavailable', async () => {
  const h = buildHarness({ visible: false, intersectionObserver: false });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.timers.size, 0);
  h.card.rect = { top: 0, left: 0, right: 120, bottom: 90, width: 120, height: 90 };
  h.fireWindow('scroll');
  h.flushAnimationFrames();
  await new Promise(resolve => setImmediate(resolve));
  assert.ok(h.timers.size > 0);
  h.tick();
  assert.equal(h.cardImage.getAttribute('src'), './media/demo-test/1.jpg');
});

test('legacy-WebView scroll bursts are coalesced to one viewport refresh per animation frame', async () => {
  const h = buildHarness({ visible: false, intersectionObserver: false });
  await new Promise(resolve => setImmediate(resolve));
  h.card.rect = { top: 0, left: 0, right: 120, bottom: 90, width: 120, height: 90 };
  h.fireWindow('scroll');
  h.fireWindow('scroll');
  h.fireWindow('scroll');
  assert.equal(h.animationFrames.size, 1);
  h.flushAnimationFrames();
  await new Promise(resolve => setImmediate(resolve));
  assert.ok(h.timers.size > 0);
  h.tick();
  assert.equal(h.cardImage.getAttribute('src'), './media/demo-test/1.jpg');
});

test('animator loads after the motion manifest and before app bootstrap', () => {
  const manifestIndex = indexSource.indexOf('<script src="./data/motion-manifest.js"></script>');
  const animatorIndex = indexSource.indexOf('<script src="./library-demo-motion.js"></script>');
  const appIndex = indexSource.indexOf('<script src="./app.js"></script>');
  assert.ok(manifestIndex >= 0 && manifestIndex < animatorIndex && animatorIndex < appIndex);
});

test('OS reduced-motion is honored when no app override is saved', async () => {
  const h = buildHarness({ reduced: true });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.timers.size, 0);
  assert.equal(h.detailDemo.classList.contains('auto-sequence'), false);
  assert.equal(h.cardImage.getAttribute('src'), './media/demo-test/0.jpg');
});

test('checkbox change waits for the app preference write before reconciling', async () => {
  const h = buildHarness();
  await new Promise(resolve => setImmediate(resolve));
  h.reduceControl.checked = true;
  h.reduceControl.addEventListener('change', () => h.setStoredPreference('1'));
  h.reduceControl.dispatch('change');
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.timers.size, 0);
  assert.equal(h.cardImage.getAttribute('src'), './media/demo-test/0.jpg');
});


test('successful local frame preload clears its timeout before animation starts', async () => {
  const h = buildHarness();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.timeouts.size, 0);
  assert.ok(h.timers.size > 0);
});

test('a stalled local frame preload settles at 1200 ms and keeps the first frame stable', async () => {
  const h = buildHarness({ imageLoadMode: 'stall' });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.timeouts.size, 1);
  assert.equal(Array.from(h.timeouts.values())[0].delay, 1200);
  assert.equal(h.timers.size, 0);
  h.fireTimeouts();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.timeouts.size, 0);
  assert.equal(h.timers.size, 0);
  assert.equal(h.cardImage.getAttribute('src'), './media/demo-test/0.jpg');
});

test('an image error clears the preload timeout and leaves the first frame visible', async () => {
  const h = buildHarness({ imageLoadMode: 'error' });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.timeouts.size, 0);
  assert.equal(h.timers.size, 0);
  assert.equal(h.cardImage.getAttribute('src'), './media/demo-test/0.jpg');
});

test('a late image event after timeout cannot restart a failed card preload', async () => {
  const h = buildHarness({ imageLoadMode: 'stall' });
  await new Promise(resolve => setImmediate(resolve));
  h.fireTimeouts();
  await new Promise(resolve => setImmediate(resolve));
  h.images[0].dispatch('load');
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.timeouts.size, 0);
  assert.equal(h.timers.size, 0);
  assert.equal(h.cardImage.getAttribute('src'), './media/demo-test/0.jpg');
});


test('a failed secondary frame does not disable animation when another local frame loads', async () => {
  const h = buildHarness({
    exerciseAssets: ['media/demo-test/0.jpg', 'media/demo-test/1.jpg', 'media/demo-test/2.jpg'],
    imageLoadMode: src => src.endsWith('/1.jpg') ? 'error' : 'load'
  });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.images.length, 2);
  assert.equal(h.timers.size, 1);
  h.tick();
  assert.equal(h.cardImage.getAttribute('src'), './media/demo-test/2.jpg');
  assert.equal(h.cardImage.dataset.demoFrame, '1');
  h.tick();
  assert.equal(h.cardImage.getAttribute('src'), './media/demo-test/0.jpg');
});

test('all failed secondary frames settle to a stable static card without repeated preloads', async () => {
  const h = buildHarness({
    exerciseAssets: ['media/demo-test/0.jpg', 'media/demo-test/1.jpg', 'media/demo-test/2.jpg'],
    imageLoadMode: 'error'
  });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.images.length, 2);
  assert.equal(h.timers.size, 0);
  h.fireMutation(h.grid);
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.images.length, 2);
  assert.equal(h.timers.size, 0);
  assert.equal(h.cardImage.getAttribute('src'), './media/demo-test/0.jpg');
});

test('detail animation skips a failed local frame and cycles only decoded frames', async () => {
  const h = buildHarness({
    exerciseAssets: ['media/demo-test/0.jpg', 'media/demo-test/1.jpg', 'media/demo-test/2.jpg'],
    imageLoadMode: src => src.endsWith('/1.jpg') ? 'error' : 'load'
  });
  await new Promise(resolve => setImmediate(resolve));
  h.detailRoot.classList.remove('hidden');
  h.fireMutation(h.detailRoot);
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.frame1.getAttribute('hidden'), '');
  assert.equal(h.frame1.getAttribute('aria-hidden'), 'true');
  assert.equal(h.frame2.getAttribute('hidden'), null);
  assert.equal(h.detailDemo.classList.contains('auto-sequence'), true);
  h.tick();
  assert.equal(h.frame2.classList.contains('is-active'), true);
  assert.equal(h.frame1.classList.contains('is-active'), false);
});

test('detail with no decoded secondary frames stays on the accessible reference frame', async () => {
  const h = buildHarness({
    exerciseAssets: ['media/demo-test/0.jpg', 'media/demo-test/1.jpg', 'media/demo-test/2.jpg'],
    imageLoadMode: 'error'
  });
  await new Promise(resolve => setImmediate(resolve));
  h.detailRoot.classList.remove('hidden');
  h.fireMutation(h.detailRoot);
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.detailDemo.classList.contains('auto-sequence'), false);
  assert.equal(h.frame0.getAttribute('aria-hidden'), null);
  assert.equal(h.frame1.getAttribute('hidden'), '');
  assert.equal(h.frame2.getAttribute('hidden'), '');
  assert.equal(h.timers.size, 0);
});
