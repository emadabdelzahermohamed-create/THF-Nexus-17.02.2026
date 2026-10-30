'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const MOTION_PATH = path.resolve(__dirname, '../../android/app/src/main/assets/pulse/data/motion-manifest.js');
const MOTION = fs.readFileSync(MOTION_PATH, 'utf8');

function makeHarness({exerciseId = 'one-frame', language = 'en', reduced = false, outcomes = {}} = {}) {
  const observers = [];
  const images = [];
  const intervals = new Map();
  const timeouts = new Map();
  let nextId = 1;
  let loadHandler;

  const notify = record => queueMicrotask(() => {
    observers.forEach(observer => observer.callback([record]));
  });

  class FakeElement {
    constructor(id) {
      this.id = id;
      this.nodeType = 1;
      this.parentElement = null;
      this.dataset = {};
      this.attributes = new Map();
      this._text = '';
      this._alt = '';
      this.checked = false;
      this.writes = 0;
      this.classList = {
        contains: name => id === 'activeWorkoutScreen'
          ? name === 'active'
          : id === 'activeDemoVideo' ? name === 'hidden' : false
      };
    }
    addEventListener() {}
    get textContent() { return this._text; }
    set textContent(value) {
      this._text = String(value);
      this.writes += 1;
      notify({target: this, type: 'childList'});
    }
    get alt() { return this._alt; }
    set alt(value) {
      this._alt = String(value);
      this.writes += 1;
      notify({target: this, type: 'attributes', attributeName: 'alt'});
    }
    getAttribute(name) { return this.attributes.has(name) ? this.attributes.get(name) : null; }
    setAttribute(name, value) {
      this.attributes.set(name, String(value));
      this.writes += 1;
      notify({target: this, type: 'attributes', attributeName: name});
    }
    removeAttribute(name) {
      this.attributes.delete(name);
      this.writes += 1;
      notify({target: this, type: 'attributes', attributeName: name});
    }
    closest(selector) {
      const ids = selector.split(',').map(part => part.trim().slice(1));
      for (let element = this; element; element = element.parentElement) {
        if (ids.includes(element.id)) return element;
      }
      return null;
    }
  }

  const root = new FakeElement('activeWorkoutScreen');
  root.dataset.exerciseId = exerciseId;
  const image = new FakeElement('activeDemoImage');
  const status = new FakeElement('activeDemoStatus');
  const phase = new FakeElement('activeDemoPhase');
  const video = new FakeElement('activeDemoVideo');
  const reduceMotion = new FakeElement('reduceMotion');
  const exerciseName = new FakeElement('activeExerciseName');
  for (const element of [image, status, phase, video, exerciseName]) element.parentElement = root;
  reduceMotion.checked = reduced;

  const documentElement = new FakeElement('html');
  documentElement._lang = language;
  Object.defineProperty(documentElement, 'lang', {
    get() { return this._lang; },
    set(value) {
      this._lang = value;
      notify({target: this, type: 'attributes', attributeName: 'lang'});
    }
  });

  const elements = {
    activeWorkoutScreen: root,
    activeDemoImage: image,
    activeDemoStatus: status,
    activeDemoPhase: phase,
    activeDemoVideo: video,
    reduceMotion,
    activeExerciseName: exerciseName
  };

  const exercises = [
    {
      id: 'one-frame',
      name: {en: 'One Frame', ar: 'إطار واحد'},
      demo: {
        assets: ['media/one-frame/0.jpg', 'media/one-frame/1.jpg'],
        alt: {en: 'One Frame start and finish', ar: 'بداية ونهاية الإطار الواحد'}
      }
    },
    {
      id: 'two-frame',
      name: {en: 'Two Frame', ar: 'إطاران'},
      demo: {
        assets: ['media/two-frame/0.jpg', 'media/two-frame/1.jpg'],
        alt: {en: 'Two Frame start and finish', ar: 'بداية ونهاية الإطارين'}
      }
    }
  ];

  class FakeImage {
    constructor() {
      this.listeners = new Map();
      this.decoding = '';
      this._src = '';
      images.push(this);
    }
    addEventListener(name, callback) { this.listeners.set(name, callback); }
    removeEventListener(name, callback) {
      if (this.listeners.get(name) === callback) this.listeners.delete(name);
    }
    set src(value) {
      this._src = value;
      const outcome = outcomes[value] || 'load';
      queueMicrotask(() => this.emit(outcome));
    }
    get src() { return this._src; }
    emit(name) {
      const callback = this.listeners.get(name);
      if (!callback) return false;
      this.listeners.delete(name);
      callback();
      return true;
    }
  }

  class FakeMutationObserver {
    constructor(callback) { this.callback = callback; observers.push(this); }
    observe() {}
  }

  const document = {
    documentElement,
    hidden: false,
    getElementById: id => elements[id] || null,
    addEventListener() {}
  };

  const window = {
    THF_EXERCISES: exercises,
    addEventListener(name, callback) { if (name === 'load') loadHandler = callback; },
    setTimeout(callback, delay) {
      const id = nextId++;
      timeouts.set(id, {callback, delay});
      return id;
    },
    clearTimeout(id) { timeouts.delete(id); },
    setInterval(callback, delay) {
      const id = nextId++;
      intervals.set(id, {callback, delay});
      return id;
    },
    clearInterval(id) { intervals.delete(id); },
    matchMedia() { return {matches: false, addEventListener() {}, addListener() {}}; }
  };

  vm.runInNewContext(MOTION, {window, document, Image: FakeImage, MutationObserver: FakeMutationObserver}, {
    filename: 'motion-manifest.js'
  });

  const flush = async () => {
    await new Promise(resolve => setImmediate(resolve));
    await new Promise(resolve => setImmediate(resolve));
  };
  const triggerStateMutation = () => {
    observers.forEach(observer => observer.callback([{target: root, type: 'childList'}]));
  };
  return {
    root, image, status, phase, documentElement, images, intervals, timeouts,
    flush,
    fireLoad() { assert.equal(typeof loadHandler, 'function'); loadHandler(); },
    triggerStateMutation,
    setLanguage(value) { documentElement.lang = value; },
    setExercise(value) {
      root.dataset.exerciseId = value;
      triggerStateMutation();
    }
  };
}

test('one surviving frame stays terminal, does not restart, and relocalizes', async () => {
  const harness = makeHarness({
    outcomes: {
      './media/one-frame/0.jpg': 'load',
      './media/one-frame/1.jpg': 'error'
    }
  });
  harness.fireLoad();
  await harness.flush();
  assert.equal(harness.images.length, 2);
  assert.equal(harness.status.textContent, 'Only one reference frame loaded; showing a static view.');
  assert.equal(harness.intervals.size, 0);

  const outputWrites = harness.status.writes + harness.phase.writes;
  await harness.flush();
  assert.equal(harness.status.writes + harness.phase.writes, outputWrites);

  harness.triggerStateMutation();
  await harness.flush();
  assert.equal(harness.images.length, 2);
  assert.equal(harness.status.textContent, 'Only one reference frame loaded; showing a static view.');

  harness.setLanguage('ar');
  await harness.flush();
  assert.equal(harness.status.textContent, 'تم تحميل صورة مرجعية واحدة فقط؛ تعرض بصورة ثابتة.');
  assert.match(harness.image.alt, /بداية/);
  assert.equal(harness.images.length, 2);
});

test('zero loaded frames keep a stable localized error instead of retrying forever', async () => {
  const harness = makeHarness({
    outcomes: {
      './media/one-frame/0.jpg': 'error',
      './media/one-frame/1.jpg': 'error'
    }
  });
  harness.fireLoad();
  await harness.flush();
  assert.equal(harness.images.length, 2);
  assert.equal(harness.image.getAttribute('src'), null);
  assert.equal(harness.status.textContent, 'Exercise reference frames could not be loaded offline.');

  harness.triggerStateMutation();
  await harness.flush();
  harness.setLanguage('ar');
  await harness.flush();
  assert.equal(harness.images.length, 2);
  assert.equal(harness.status.textContent, 'تعذر تحميل صور الحركة لهذا التمرين دون اتصال.');
});

test('changing exercise after a static fallback starts the next exercise normally', async () => {
  const harness = makeHarness({
    outcomes: {
      './media/one-frame/0.jpg': 'load',
      './media/one-frame/1.jpg': 'error'
    }
  });
  harness.fireLoad();
  await harness.flush();
  harness.setExercise('two-frame');
  await harness.flush();
  assert.equal(harness.images.length, 4);
  assert.equal(harness.intervals.size, 1);
  assert.equal(harness.image.getAttribute('src'), './media/two-frame/0.jpg');
});

test('two loaded frames still start the automatic loop exactly once', async () => {
  const harness = makeHarness({exerciseId: 'two-frame'});
  harness.fireLoad();
  await harness.flush();
  assert.equal(harness.images.length, 2);
  assert.equal(harness.intervals.size, 1);
  harness.triggerStateMutation();
  await harness.flush();
  assert.equal(harness.images.length, 2);
  assert.equal(harness.intervals.size, 1);
});

test('reduced motion remains static and does not preload or start a timer', async () => {
  const harness = makeHarness({reduced: true});
  harness.fireLoad();
  await harness.flush();
  assert.equal(harness.images.length, 0);
  assert.equal(harness.intervals.size, 0);
  assert.match(harness.status.textContent, /Reduced motion is on/);
});
