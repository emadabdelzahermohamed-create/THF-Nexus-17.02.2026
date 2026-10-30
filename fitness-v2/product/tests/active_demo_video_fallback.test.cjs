'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const PULSE = path.resolve(__dirname, '../../android/app/src/main/assets/pulse');
const APP = fs.readFileSync(path.join(PULSE, 'app.js'), 'utf8');
const MOTION = fs.readFileSync(path.join(PULSE, 'data/motion-manifest.js'), 'utf8');
const EXERCISES_JS = fs.readFileSync(path.join(PULSE, 'data/exercises.js'), 'utf8');

function extractFunction(source, name, nextName) {
  const marker = 'function ' + name + '(';
  const start = source.indexOf(marker);
  assert.notEqual(start, -1, 'missing function ' + name);
  const open = source.indexOf('{', start);
  assert.notEqual(open, -1, 'missing function body ' + name);
  let depth = 0;
  let quote = null;
  let escaped = false;
  let lineComment = false;
  let blockComment = false;
  for (let i = open; i < source.length; i += 1) {
    const ch = source[i];
    const next = source[i + 1];
    if (quote) {
      if (escaped) { escaped = false; continue; }
      if (ch === '\\') { escaped = true; continue; }
      if (ch === quote) quote = null;
      continue;
    }
    if (lineComment) { if (ch === '\n') lineComment = false; continue; }
    if (blockComment) {
      if (ch === '*' && next === '/') { blockComment = false; i += 1; }
      continue;
    }
    if (ch === '/' && next === '/') { lineComment = true; i += 1; continue; }
    if (ch === '/' && next === '*') { blockComment = true; i += 1; continue; }
    if (ch === "'" || ch === '"' || ch.charCodeAt(0) === 96) { quote = ch; continue; }
    if (ch === '{') depth += 1;
    else if (ch === '}') {
      depth -= 1;
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  throw new Error('unterminated function ' + name);
}

function makeClassList(initial = []) {
  const values = new Set(initial);
  return {
    add(value) { values.add(value); },
    remove(value) { values.delete(value); },
    contains(value) { return values.has(value); },
    toggle(value, force) {
      const next = force === undefined ? !values.has(value) : Boolean(force);
      if (next) values.add(value);
      else values.delete(value);
      return next;
    }
  };
}

function makeNode({hidden = false} = {}) {
  const attributes = new Map();
  return {
    classList: makeClassList(hidden ? ['hidden'] : []),
    dataset: {},
    listeners: new Map(),
    textContent: '',
    alt: '',
    href: '',
    setAttribute(name, value) { attributes.set(name, String(value)); },
    getAttribute(name) { return attributes.has(name) ? attributes.get(name) : null; },
    removeAttribute(name) { attributes.delete(name); },
    addEventListener(name, callback) { this.listeners.set(name, callback); },
    removeEventListener(name, callback) {
      if (this.listeners.get(name) === callback) this.listeners.delete(name);
    },
    pause() { this.pauseCount = (this.pauseCount || 0) + 1; },
    load() { this.loadCount = (this.loadCount || 0) + 1; },
    play() {
      this.playCount = (this.playCount || 0) + 1;
      if (this.playMode === 'throw') throw new Error('autoplay blocked synchronously');
      if (this.playMode === 'resolve') return Promise.resolve();
      return Promise.reject(new Error('autoplay blocked'));
    },
    playMode: 'reject'
  };
}

function exercise(id, suffix = id) {
  const catalogItem = EXERCISES.find(item => item.id === id);
  if (catalogItem) return catalogItem;
  return {
    id,
    name: {en: id, ar: id + ' بالعربية'},
    demo: {
      assets: [
        'media/free-exercise-db/' + suffix + '/0.jpg',
        'media/free-exercise-db/' + suffix + '/1.jpg'
      ],
      alt: {en: 'Start and finish positions for ' + id, ar: 'وضعا البداية والنهاية لتمرين ' + id + ' بالعربية'}
    }
  };
}

function harness({item = exercise('romanian-deadlift'), reduced = false, playMode = 'reject'} = {}) {
  let currentItem = item;
  const video = makeNode({hidden: true});
  video.playMode = playMode;
  const image = makeNode({hidden: true});
  const credit = makeNode({hidden: true});
  const source = makeNode();
  const license = makeNode();
  const phase = makeNode();
  const status = makeNode();
  const nodes = {
    activeDemoVideo: video,
    activeDemoImage: image,
    activeDemoCredit: credit,
    activeDemoSource: source,
    activeDemoLicense: license,
    activeDemoPhase: phase,
    activeDemoStatus: status
  };
  const state = {lang: 'en'};
  const motionManifest = {
    [item.id]: {
      asset: 'media/motion/' + item.id + '.mp4',
      sourceUrl: 'https://example.invalid/' + item.id + '.mp4',
      licenseUrl: 'https://creativecommons.org/licenses/by-sa/4.0/',
      author: 'Reviewed source'
    }
  };
  const context = {
    state,
    motionManifest,
    document: {hidden: false},
    preferredReducedMotion: () => reduced,
    activeExercise: () => currentItem,
    local: value => value?.[state.lang] ?? value?.en ?? '',
    t: key => ({
      videoFallback: state.lang === 'ar'
        ? 'تعذر تشغيل الفيديو؛ يعرض التطبيق تسلسل الصور المرجعية تلقائيًا.'
        : 'Video unavailable; showing the automatic reference-frame sequence.'
    }[key] || key),
    $(id) { return nodes[id] || null; }
  };
  const names = [
    'fallbackActiveMotionToFrames',
    'attemptActiveDemoVideoPlayback',
    'renderActiveMotion'
  ];
  const functions = names.map(name => extractFunction(APP, name)).join('\n');
  vm.runInNewContext(
    functions + '\nglobalThis.api = {fallbackActiveMotionToFrames, attemptActiveDemoVideoPlayback, renderActiveMotion};',
    context
  );
  return {
    api: context.api,
    nodes,
    video,
    image,
    credit,
    phase,
    status,
    state,
    motionManifest,
    setCurrentItem(value) { currentItem = value; },
    setReduced(value) { reduced = value; }
  };
}

const exerciseContext = {window: {}};
vm.runInNewContext(EXERCISES_JS, exerciseContext);
const EXERCISES = exerciseContext.window.THF_EXERCISES || [];
const manifestContext = {window: {}};
const manifestEnd = MOTION.indexOf('\n/*');
assert.notEqual(manifestEnd, -1, 'missing motion manifest boundary');
vm.runInNewContext(MOTION.slice(0, manifestEnd), manifestContext);
const MOTION_MANIFEST = manifestContext.window.THF_MOTION_MANIFEST || {};

test('autoplay rejection falls back to the first offline frame and announces the fallback', async () => {
  const h = harness();
  h.api.renderActiveMotion(exercise('romanian-deadlift'));
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.video.classList.contains('hidden'), true);
  assert.equal(h.image.classList.contains('hidden'), false);
  assert.equal(h.image.getAttribute('src'), './media/free-exercise-db/romanian-deadlift/0.jpg');
  assert.match(h.image.alt, /Start and finish positions/);
  assert.equal(h.credit.classList.contains('hidden'), true);
  assert.equal(h.phase.textContent, 'Automatic reference sequence');
  assert.match(h.status.textContent, /Video unavailable/);
  assert.equal(h.video.dataset.failedExerciseId, 'romanian-deadlift');
});

test('a media error event uses the same safe frame fallback and removes its handler', () => {
  const h = harness({playMode: 'resolve'});
  h.api.renderActiveMotion(exercise('leg-press'));
  const onError = h.video.listeners.get('error');
  assert.equal(typeof onError, 'function');
  onError();
  assert.equal(h.video.classList.contains('hidden'), true);
  assert.equal(h.image.classList.contains('hidden'), false);
  assert.equal(h.image.getAttribute('src'), './media/free-exercise-db/leg-press/0.jpg');
  assert.equal(h.video.listeners.has('error'), false);
});

test('a delayed error from a previous exercise cannot replace the current exercise demo', () => {
  const h = harness({playMode: 'resolve'});
  const first = exercise('romanian-deadlift');
  const second = exercise('standing-calf-raises');
  h.api.renderActiveMotion(first);
  const staleError = h.video.listeners.get('error');
  h.setCurrentItem(second);
  h.motionManifest[second.id] = {
    asset: 'media/motion/' + second.id + '.mp4',
    sourceUrl: 'https://example.invalid/' + second.id + '.mp4',
    licenseUrl: 'https://creativecommons.org/licenses/by-sa/4.0/'
  };
  h.api.renderActiveMotion(second);
  staleError();
  assert.equal(h.video.classList.contains('hidden'), false);
  assert.equal(h.video.getAttribute('src'), './media/motion/standing-calf-raises.mp4');
  assert.equal(h.video.dataset.failedExerciseId, undefined);
});

test('a failed video is not retried on rerender, while a different exercise can use its own video', async () => {
  const h = harness();
  const first = exercise('romanian-deadlift');
  h.api.renderActiveMotion(first);
  await new Promise(resolve => setImmediate(resolve));
  const firstPlayCount = h.video.playCount;
  h.api.renderActiveMotion(first);
  assert.equal(h.video.playCount, firstPlayCount);
  assert.equal(h.image.classList.contains('hidden'), false);

  const second = exercise('standing-calf-raises');
  h.setCurrentItem(second);
  h.motionManifest[second.id] = {asset: 'media/motion/' + second.id + '.mp4'};
  h.video.playMode = 'resolve';
  h.api.renderActiveMotion(second);
  assert.equal(h.video.classList.contains('hidden'), false);
  assert.equal(h.video.getAttribute('src'), './media/motion/standing-calf-raises.mp4');
  assert.equal(h.video.playCount, firstPlayCount + 1);
});

test('a synchronous playback exception also falls back safely', () => {
  const h = harness({playMode: 'throw'});
  h.api.renderActiveMotion(exercise('hammer-curls'));
  assert.equal(h.video.classList.contains('hidden'), true);
  assert.equal(h.image.classList.contains('hidden'), false);
  assert.equal(h.video.dataset.failedExerciseId, 'hammer-curls');
});

test('reduced motion bypasses video and keeps a static localized frame', () => {
  const h = harness({reduced: true});
  const item = exercise('romanian-deadlift');
  h.state.lang = 'ar';
  h.api.renderActiveMotion(item);
  assert.equal(h.video.playCount || 0, 0);
  assert.equal(h.video.classList.contains('hidden'), true);
  assert.equal(h.image.classList.contains('hidden'), false);
  assert.match(h.phase.textContent, /تقليل الحركة/);
  assert.match(h.status.textContent, /تقليل الحركة مفعّل/);
  assert.equal(h.image.alt, item.demo.alt.ar);
});

test('non-video exercises are truthfully labelled as an automatic reference sequence', () => {
  const h = harness();
  for (const id of Object.keys(h.motionManifest)) delete h.motionManifest[id];
  const item = exercise('bodyweight-squat');
  h.api.renderActiveMotion(item);
  assert.equal(h.video.classList.contains('hidden'), true);
  assert.equal(h.image.classList.contains('hidden'), false);
  assert.equal(h.phase.textContent, 'Automatic reference sequence');
  assert.equal(h.status.textContent, '');
});

test('all 112 catalog exercises have two localized offline frames and all seven videos map to real exercises', () => {
  assert.equal(EXERCISES.length, 112);
  for (const item of EXERCISES) {
    assert.ok(Array.isArray(item.demo?.assets) && item.demo.assets.length >= 2, item.id + ' lacks an offline frame sequence');
    for (const language of ['en', 'ar']) assert.ok(item.demo?.alt?.[language], item.id + ' lacks ' + language + ' demo alt');
  }
  assert.equal(Object.keys(MOTION_MANIFEST).length, 7);
  for (const id of Object.keys(MOTION_MANIFEST)) {
    assert.ok(EXERCISES.some(item => item.id === id), id + ' has no catalog exercise');
  }
});

test('all 112 offline exercises render their own first frame with the correct Arabic and English alt text', () => {
  const h = harness({item: EXERCISES[0], playMode: 'resolve'});
  for (const language of ['en', 'ar']) {
    h.state.lang = language;
    for (const item of EXERCISES) {
      h.setCurrentItem(item);
      for (const id of Object.keys(h.motionManifest)) delete h.motionManifest[id];
      delete h.video.dataset.failedExerciseId;
      h.api.renderActiveMotion(item);
      assert.equal(h.video.classList.contains('hidden'), true, item.id + ' video should be hidden');
      assert.equal(h.image.classList.contains('hidden'), false, item.id + ' frame should be visible');
      assert.equal(h.image.getAttribute('src'), './' + item.demo.assets[0], item.id + ' wrong first frame');
      assert.equal(h.image.alt, item.demo.alt[language], item.id + ' wrong ' + language + ' alt');
      assert.equal(h.phase.textContent, language === 'ar' ? 'تسلسل مرجعي تلقائي' : 'Automatic reference sequence');
    }
  }
});

test('all seven reviewed video mappings fall back to their own exercise frames', () => {
  const h = harness({item: EXERCISES[0], playMode: 'resolve'});
  for (const id of Object.keys(MOTION_MANIFEST)) {
    const item = EXERCISES.find(value => value.id === id);
    assert.ok(item, id + ' has no catalog exercise');
    h.setCurrentItem(item);
    for (const key of Object.keys(h.motionManifest)) delete h.motionManifest[key];
    h.motionManifest[id] = MOTION_MANIFEST[id];
    delete h.video.dataset.failedExerciseId;
    h.api.renderActiveMotion(item);
    const onError = h.video.listeners.get('error');
    assert.equal(typeof onError, 'function', id + ' has no media error handler');
    onError();
    assert.equal(h.video.classList.contains('hidden'), true, id + ' video should fall back');
    assert.equal(h.image.getAttribute('src'), './' + item.demo.assets[0], id + ' mapped to the wrong exercise frame');
    assert.equal(h.status.textContent.includes('Video unavailable'), true, id + ' fallback not announced');
  }
});

test('the active workout motion controller observes the video hidden state and starts its automatic frame loop', () => {
  assert.match(MOTION, /observer\.observe\(root,[\s\S]*attributeFilter: \['class', 'data-exercise-id'\]/);
  assert.match(MOTION, /if \(!video\.classList\.contains\('hidden'\)\) \{\s*stop\(\{resetExercise: true\}\)/);
  assert.match(MOTION, /if \(item\.id !== activeExerciseId \|\| \(!timer && pendingExerciseId !== item\.id\)\) start\(item\)/);
});

test('visibility resume uses the same fallback-aware playback handler', () => {
  assert.match(APP, /attemptActiveDemoVideoPlayback\(item,video\.getAttribute\('src'\)\)/);
  assert.doesNotMatch(APP, /video\.play\(\)\.catch\(\(\)\s*=>\s*\{\}\)/);
  assert.doesNotMatch(APP, /Reference images — motion pending|صور مرجعية — الحركة قيد الإضافة/);
});
