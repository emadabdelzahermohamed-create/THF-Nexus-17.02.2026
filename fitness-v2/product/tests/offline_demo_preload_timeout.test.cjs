'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const MOTION_PATH = path.resolve(__dirname, '../../android/app/src/main/assets/pulse/data/motion-manifest.js');
const MOTION = fs.readFileSync(MOTION_PATH, 'utf8');
const PRELOAD_TIMEOUT_MS = 1200;

function extractFunction(source, name) {
  const marker = 'function ' + name + '(';
  const start = source.indexOf(marker);
  assert.notEqual(start, -1, 'missing ' + name);
  const open = source.indexOf('{', start);
  let depth = 0;
  for (let i = open; i < source.length; i += 1) {
    if (source[i] === '{') depth += 1;
    else if (source[i] === '}') {
      depth -= 1;
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  throw new Error('unterminated ' + name);
}

function makeHarness() {
  const images = [];
  const timers = new Map();
  let nextTimerId = 1;

  class FakeImage {
    constructor() {
      this.listeners = new Map();
      this.decoding = '';
      this.src = '';
      images.push(this);
    }
    addEventListener(name, callback) {
      this.listeners.set(name, callback);
    }
    removeEventListener(name, callback) {
      if (this.listeners.get(name) === callback) this.listeners.delete(name);
    }
    emit(name) {
      const callback = this.listeners.get(name);
      if (!callback) return false;
      this.listeners.delete(name);
      callback();
      return true;
    }
  }

  const window = {
    setTimeout(callback, delay) {
      const id = nextTimerId++;
      timers.set(id, {callback, delay});
      return id;
    },
    clearTimeout(id) {
      timers.delete(id);
    }
  };

  const context = {Image: FakeImage, window, PRELOAD_TIMEOUT_MS};
  const preloadSource = extractFunction(MOTION, 'preloadFrames');
  vm.runInNewContext(
    'const preloadPromises = new Map();\n' +
    preloadSource +
    '\nglobalThis.api = {preloadFrames, preloadPromises};',
    context
  );

  return {
    api: context.api,
    images,
    timers,
    window
  };
}

function item(id = 'bodyweight-squat') {
  return {id, demo: {assets: ['media/' + id + '/0.jpg', 'media/' + id + '/1.jpg']}};
}

function renderFrameFor(lang, loaded) {
  const elements = {
    activeDemoImage: {
      attributes: new Map(),
      getAttribute(name) { return this.attributes.get(name) ?? null; },
      setAttribute(name, value) { this.attributes.set(name, value); },
      alt: ''
    },
    activeDemoStatus: {textContent: ''},
    activeDemoPhase: {
      attributes: new Map(),
      setAttribute(name, value) { this.attributes.set(name, value); },
      textContent: ''
    }
  };
  const context = {
    document: {documentElement: {lang}},
    byId(id) { return elements[id] || null; },
    reduceMotion() { return false; },
    loadedFrames: new Map([['test-demo', loaded]]),
    frameIndex: 0
  };
  vm.runInNewContext(extractFunction(MOTION, 'renderFrame') + '\\nglobalThis.api = {renderFrame};', context);
  context.api.renderFrame({
    id: 'test-demo',
    demo: {
      assets: ['media/start.jpg', 'media/finish.jpg'],
      alt: {en: 'Start and finish positions', ar: 'وضعا البداية والنهاية'}
    }
  });
  return elements;
}

test('successful frame loads clear their bounded preload timers', async () => {
  const h = makeHarness();
  const ready = h.api.preloadFrames(item());
  assert.equal(h.images.length, 2);
  assert.deepEqual([...h.timers.values()].map(value => value.delay), [PRELOAD_TIMEOUT_MS, PRELOAD_TIMEOUT_MS]);
  assert.equal(h.images[0].emit('load'), true);
  assert.equal(h.images[1].emit('load'), true);
  assert.deepEqual(Array.from(await ready), [true, true]);
  assert.equal(h.timers.size, 0);
});

test('missing frame errors settle without waiting for the timeout', async () => {
  const h = makeHarness();
  const ready = h.api.preloadFrames(item('pushups'));
  h.images[0].emit('error');
  h.images[1].emit('load');
  assert.deepEqual(Array.from(await ready), [false, true]);
  assert.equal(h.timers.size, 0);
});

test('a WebView image that emits neither load nor error cannot block the loop indefinitely', async () => {
  const h = makeHarness();
  const ready = h.api.preloadFrames(item('romanian-deadlift'));
  assert.equal(h.timers.size, 2);
  for (const timer of [...h.timers.values()]) timer.callback();
  assert.deepEqual(Array.from(await ready), [false, false]);
  assert.equal(h.timers.size, 0);
});

test('late load/error events after timeout are idempotent', async () => {
  const h = makeHarness();
  const ready = h.api.preloadFrames(item('hammer-curls'));
  const callbacks = [...h.timers.values()].map(value => value.callback);
  callbacks.forEach(callback => callback());
  assert.equal(h.images[0].emit('load'), false);
  assert.equal(h.images[1].emit('error'), false);
  assert.deepEqual(Array.from(await ready), [false, false]);
  assert.equal(h.timers.size, 0);
});

test('concurrent callers share one preload operation per exercise', async () => {
  const h = makeHarness();
  const exercise = item('leg-press');
  const first = h.api.preloadFrames(exercise);
  const second = h.api.preloadFrames(exercise);
  assert.equal(first, second);
  assert.equal(h.images.length, 2);
  assert.equal(h.timers.size, 2);
  h.images.forEach(image => image.emit('load'));
  assert.deepEqual(Array.from(await first), [true, true]);
});

test('one stalled frame is bounded while another frame loads normally', async () => {
  const h = makeHarness();
  const ready = h.api.preloadFrames(item('standing-calf-raises'));
  h.images[0].emit('load');
  assert.equal(h.timers.size, 1);
  [...h.timers.values()][0].callback();
  assert.deepEqual(Array.from(await ready), [true, false]);
  assert.equal(h.timers.size, 0);
});

test('the timeout remains bounded and only successfully loaded frames animate', () => {
  assert.match(MOTION, /const PRELOAD_TIMEOUT_MS = 1200;/);
  assert.match(MOTION, /const results = await preloadFrames\(item\);[\s\S]*?const readyFrames = item\.demo\.assets[\s\S]*?\.map\(\(asset, index\) => \(\{asset, index\}\)\)[\s\S]*?\.filter\(\(frame, index\) => results\[index\]\);/);
  assert.match(MOTION, /if \(readyFrames\.length < 2\)[\s\S]*?showing a static view/);
  assert.match(MOTION, /const frames = loadedFrames\.get\(latest\.id\) \|\| latest\.demo\.assets;[\s\S]*?frameIndex = \(frameIndex \+ 1\) % frames\.length/);
  assert.match(MOTION, /const sourceIndex = loaded \? loaded\[phaseIndex\]\.index : phaseIndex;/);
  assert.match(MOTION, /sourceIndex === 0 \? 'Start' : 'Finish'/);
});

test('a surviving second English frame keeps its Finish label', () => {
  const elements = renderFrameFor('en', [{asset: 'media/finish.jpg', index: 1}]);
  assert.equal(elements.activeDemoImage.getAttribute('src'), './media/finish.jpg');
  assert.match(elements.activeDemoImage.alt, /Finish/);
  assert.match(elements.activeDemoPhase.textContent, /^Finish/);
});

test('a surviving second Arabic frame keeps its النهاية label', () => {
  const elements = renderFrameFor('ar', [{asset: 'media/finish.jpg', index: 1}]);
  assert.equal(elements.activeDemoImage.getAttribute('src'), './media/finish.jpg');
  assert.match(elements.activeDemoImage.alt, /النهاية/);
  assert.match(elements.activeDemoPhase.textContent, /^النهاية/);
});

test('the complete motion manifest parses as one JavaScript asset', () => {
  assert.doesNotThrow(() => new vm.Script(MOTION, {filename: 'motion-manifest.js'}));
});
