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

function buildHarness({ reduced = false, visible = true } = {}) {
  const timers = new Map();
  const mutationObservers = [];
  const intersectionObservers = [];
  const mediaListeners = new Map();
  let nextTimer = 1;
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
      assets: ['media/demo-test/0.jpg', 'media/demo-test/1.jpg'],
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

  const detailImage0 = imageFor('./media/demo-test/0.jpg', exercise.demo.alt.en);
  const detailImage1 = imageFor('./media/demo-test/1.jpg', exercise.demo.alt.en);
  const frame0 = new FakeElement({ classes: ['detail-frame'] });
  const frame1 = new FakeElement({ classes: ['detail-frame'] });
  frame0.image = detailImage0;
  frame1.image = detailImage1;
  const detailDemo = new FakeElement({ id: 'detailDemo' });
  detailDemo.children = [frame0, frame1];
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
    addEventListener() {},
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
      addEventListener(type, callback) { this[type] = callback; }
      set src(value) { this._src = value; queueMicrotask(() => this.load?.()); }
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

  vm.runInNewContext(source, { window, document, Promise, Map, Set, Array, Boolean, Number, String, Math });

  const fireMutation = target => mutationObservers.filter(observer => observer.target === target).forEach(observer => observer.callback([]));
  const tick = () => {
    const active = Array.from(timers.values())[0];
    assert.ok(active, 'animation timer should be active');
    active.callback();
  };
  const setStoredPreference = value => { storedPreference = value; (mediaListeners.get('change') || []).forEach(callback => callback({ matches: value === '1' })); };

  return { timers, grid, card, cardImage, detailRoot, detailDemo, frame0, frame1, reduceControl, fireMutation, tick, setStoredPreference };
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
