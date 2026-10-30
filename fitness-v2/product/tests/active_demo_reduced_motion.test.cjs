'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const pulse = path.resolve(__dirname, '../../android/app/src/main/assets/pulse');
const appSource = fs.readFileSync(path.join(pulse, 'app.js'), 'utf8');
const motionSource = fs.readFileSync(path.join(pulse, 'data/motion-manifest.js'), 'utf8');
const htmlSource = fs.readFileSync(path.join(pulse, 'index.html'), 'utf8');

function extractFunction(source, name, nextName) {
  const start = source.indexOf('  function ' + name + '(');
  const end = source.indexOf('  function ' + nextName + '(', start);
  assert.notEqual(start, -1, 'missing function ' + name);
  assert.notEqual(end, -1, 'missing function boundary ' + nextName);
  return source.slice(start, end).trim();
}

function loadFunction(source, name, nextName, sandbox) {
  return vm.runInNewContext('(' + extractFunction(source, name, nextName) + ')', sandbox);
}

function fakeElement(options = {}) {
  const classes = new Set();
  const attributes = new Map();
  if (options.hidden) classes.add('hidden');
  if (options.active) classes.add('active');
  return {
    classList: {
      contains(name) { return classes.has(name); },
      add(name) { classes.add(name); },
      remove(name) { classes.delete(name); },
      toggle(name, force) {
        const enabled = force === undefined ? !classes.has(name) : Boolean(force);
        if (enabled) classes.add(name); else classes.delete(name);
        return enabled;
      }
    },
    setAttribute(name, value) {
      attributes.set(name, String(value));
      if (name === 'src') this.src = String(value);
      if (name === 'aria-label') this.ariaLabel = String(value);
    },
    getAttribute(name) { return attributes.has(name) ? attributes.get(name) : null; },
    removeAttribute(name) {
      attributes.delete(name);
      if (name === 'src') this.src = '';
    },
    load() { this.loadCount = (this.loadCount || 0) + 1; },
    pause() { this.pauseCount = (this.pauseCount || 0) + 1; },
    play() { this.playCount = (this.playCount || 0) + 1; return Promise.resolve(); },
    style: { values: {}, setProperty(name, value) { this.values[name] = value; } },
    textContent: '',
    checked: false,
    src: '',
    alt: '',
    href: ''
  };
}

function activeDemoHarness(reduced, lang) {
  const elements = {
    activeDemoVideo: fakeElement(),
    activeDemoImage: fakeElement({ hidden: true }),
    activeDemoCredit: fakeElement({ hidden: true }),
    activeDemoSource: fakeElement(),
    activeDemoLicense: fakeElement(),
    activeDemoPhase: fakeElement(),
    activeDemoStatus: fakeElement()
  };
  const item = {
    id: 'pushups',
    demo: {
      assets: ['media/free-exercise-db/Pushups/0.jpg', 'media/free-exercise-db/Pushups/1.jpg'],
      alt: { en: 'Start and finish positions for pushups', ar: 'وضعا البداية والنهاية لتمرين الضغط' }
    }
  };
  const sandbox = {
    $: id => elements[id],
    motionManifest: {
      pushups: {
        asset: 'media/motion/pushups.webm',
        sourceUrl: 'https://wger.de/media/exercise-video/pushups.webm',
        licenseUrl: 'https://creativecommons.org/licenses/by-sa/4.0/',
        author: 'Goulart'
      }
    },
    state: { lang },
    document: { hidden: false },
    preferredReducedMotion: () => reduced
  };
  return { elements, item, sandbox };
}

function motionFrameHarness(reduced, lang) {
  const elements = {
    activeDemoImage: fakeElement(),
    activeDemoPhase: fakeElement(),
    activeDemoStatus: fakeElement()
  };
  const item = {
    id: 'pushups',
    demo: {
      assets: ['media/free-exercise-db/Pushups/0.jpg', 'media/free-exercise-db/Pushups/1.jpg'],
      alt: { en: 'Start and finish positions for pushups', ar: 'وضعا البداية والنهاية لتمرين الضغط' }
    }
  };
  const sandbox = {
    byId: id => elements[id],
    document: { documentElement: { lang } },
    frameIndex: 0,
    reduceMotion: () => reduced
  };
  const renderFrame = loadFunction(motionSource, 'renderFrame', 'preloadFrames', sandbox);
  renderFrame(item);
  return { elements, item };
}

test('full-motion video becomes a static local Arabic reference frame when reduced motion is enabled', () => {
  const h = activeDemoHarness(true, 'ar');
  const render = loadFunction(appSource, 'renderActiveMotion', 'renderActiveWorkout', h.sandbox);
  render(h.item);

  assert.equal(h.elements.activeDemoVideo.pauseCount, 1);
  assert.equal(h.elements.activeDemoVideo.getAttribute('src'), null);
  assert.equal(h.elements.activeDemoVideo.loadCount, 1);
  assert.equal(h.elements.activeDemoVideo.classList.contains('hidden'), true);
  assert.equal(h.elements.activeDemoImage.classList.contains('hidden'), false);
  assert.equal(h.elements.activeDemoImage.src, './media/free-exercise-db/Pushups/0.jpg');
  assert.equal(h.elements.activeDemoImage.alt, h.item.demo.alt.ar);
  assert.equal(h.elements.activeDemoCredit.classList.contains('hidden'), true);
  assert.match(h.elements.activeDemoPhase.textContent, /صورة ثابتة — تقليل الحركة/);
});

test('full-motion video remains automatic with source credit when reduced motion is disabled', () => {
  const h = activeDemoHarness(false, 'en');
  const render = loadFunction(appSource, 'renderActiveMotion', 'renderActiveWorkout', h.sandbox);
  render(h.item);

  assert.equal(h.elements.activeDemoVideo.getAttribute('src'), './media/motion/pushups.webm');
  assert.equal(h.elements.activeDemoVideo.classList.contains('hidden'), false);
  assert.equal(h.elements.activeDemoImage.classList.contains('hidden'), true);
  assert.equal(h.elements.activeDemoVideo.playCount, 1);
  assert.equal(h.elements.activeDemoCredit.classList.contains('hidden'), false);
  assert.match(h.elements.activeDemoPhase.textContent, /Automatic full movement/);
});

test('active-workout navigation never autoplays a full-motion video for reduced-motion users', () => {
  for (const reduced of [true, false]) {
    const video = fakeElement();
    const primaryNav = fakeElement();
    const activeScreen = fakeElement();
    const body = fakeElement();
    const sandbox = {
      document: {
        querySelectorAll(selector) {
          if (selector === '.screen') return [activeScreen];
          if (selector === '#primaryNav button') return [];
          return [];
        },
        body
      },
      window: { scrollTo() {} },
      $: id => ({ primaryNav, activeDemoVideo: video }[id]),
      preferredReducedMotion: () => reduced,
      renderProgress() {},
      renderHealthStatus() {},
      renderActivity() {},
      readActivitySnapshot() {},
      startActivityPolling() {}
    };
    const showScreen = loadFunction(appSource, 'showScreen', 'applyLanguage', sandbox);
    showScreen('activeWorkoutScreen', false);
    assert.equal(video.playCount || 0, reduced ? 0 : 1);
    assert.equal(video.pauseCount || 0, reduced ? 1 : 0);
  }
});

test('changing the saved motion preference refreshes the active workout demo immediately', () => {
  const checkbox = fakeElement();
  const activeScreen = fakeElement({ active: true });
  const css = {};
  const saved = new Map();
  const renders = [];
  const item = { id: 'pushups' };
  const sandbox = {
    $: id => ({ reduceMotion: checkbox, activeWorkoutScreen: activeScreen }[id]),
    document: { documentElement: { style: { setProperty(name, value) { css[name] = value; } } } },
    store: { setItem(key, value) { saved.set(key, value); } },
    state: { active: { exerciseId: 'pushups' } },
    activeExercise: () => item,
    renderActiveMotion: value => renders.push(value)
  };
  const apply = loadFunction(appSource, 'applyMotionPreference', 'bind', sandbox);

  apply(true);
  apply(false);

  assert.equal(checkbox.checked, false);
  assert.equal(css['--motion'], '1');
  assert.equal(saved.get('pulse.v2.reduceMotion'), '0');
  assert.equal(renders.length, 2);
  assert.equal(renders[0], item);
  assert.equal(renders[1], item);
});

test('active workout reduced-motion changes are announced in Arabic and English', () => {
  for (const [lang, expected] of [
    ['ar', 'تقليل الحركة مفعّل؛ تظهر صورة ثابتة للتمرين.'],
    ['en', 'Reduced motion is on; a static exercise image is shown.']
  ]) {
    const h = activeDemoHarness(true, lang);
    const render = loadFunction(appSource, 'renderActiveMotion', 'renderActiveWorkout', h.sandbox);
    render(h.item);
    assert.equal(h.elements.activeDemoStatus.textContent, expected);
  }
});

test('normal active-workout motion clears a stale reduced-motion announcement', () => {
  const h = activeDemoHarness(false, 'en');
  h.elements.activeDemoStatus.textContent = 'Reduced motion is on; a static exercise image is shown.';
  const render = loadFunction(appSource, 'renderActiveMotion', 'renderActiveWorkout', h.sandbox);
  render(h.item);
  assert.equal(h.elements.activeDemoStatus.textContent, '');
});

test('offline frame fallback announces reduced motion once without exposing the changing phase label', () => {
  const reduced = motionFrameHarness(true, 'ar');
  assert.equal(reduced.elements.activeDemoStatus.textContent, 'تقليل الحركة مفعّل؛ تظهر صورة ثابتة للتمرين.');
  assert.equal(reduced.elements.activeDemoPhase.getAttribute('aria-hidden'), 'true');
  const moving = motionFrameHarness(false, 'en');
  assert.equal(moving.elements.activeDemoStatus.textContent, '');
  assert.equal(moving.elements.activeDemoPhase.getAttribute('aria-hidden'), 'true');
});

test('active workout contains a persistent polite live region separate from the changing phase label', () => {
  assert.match(htmlSource, /id="activeDemoStatus" class="sr-only" role="status" aria-live="polite" aria-atomic="true"/);
  assert.ok(htmlSource.includes('id="activeDemoPhase" class="phase-label">دليل الحركة</span><span id="activeDemoStatus"'));
});

test('OS reduced-motion changes are wired to active video and reference-frame reconciliation', () => {
  assert.match(appSource, /motionPreferenceQuery=window\.matchMedia\?\.\('\(prefers-reduced-motion: reduce\)'\)/);
  assert.match(appSource, /syncSystemMotionPreference=\(\)=>applyMotionPreference\(preferredReducedMotion\(\),false\)/);
  assert.match(appSource, /!video\.classList\.contains\('hidden'\)&&!preferredReducedMotion\(\)\)video\.play\(\)\.catch/);
  assert.match(motionSource, /motionQuery = window\.matchMedia\?\.\('\(prefers-reduced-motion: reduce\)'\)/);
  assert.match(motionSource, /motionQuery\.addEventListener\('change', reconcile\)/);
  assert.match(motionSource, /motionQuery\?\.addListener\?\.\(reconcile\)/);
});
