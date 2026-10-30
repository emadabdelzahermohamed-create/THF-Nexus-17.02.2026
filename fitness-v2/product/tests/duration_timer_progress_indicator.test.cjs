'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const PULSE = path.resolve(__dirname, '../../android/app/src/main/assets/pulse');
const APP = fs.readFileSync(path.join(PULSE, 'app.js'), 'utf8');
const CSS = fs.readFileSync(path.join(PULSE, 'styles.css'), 'utf8');

function extractFunction(source, name) {
  const marker = `function ${name}(`;
  const start = source.indexOf(marker);
  assert.notEqual(start, -1, `missing ${name}`);
  const open = source.indexOf('{', start);
  let depth = 0;
  for (let i = open; i < source.length; i += 1) {
    if (source[i] === '{') depth += 1;
    else if (source[i] === '}') {
      depth -= 1;
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  throw new Error(`unterminated ${name}`);
}

function formatDuration(seconds) {
  const value = Math.max(0, Math.floor(Number(seconds) || 0));
  return `${String(Math.floor(value / 60)).padStart(2, '0')}:${String(value % 60).padStart(2, '0')}`;
}

function harness({ monotonic = 1000, wall = 100000, remainingMs = 30000, running = false, deadline = null, elapsed = false } = {}) {
  const monotonicNow = { value: monotonic };
  const wallNow = { value: wall };
  const set = {
    durationSeconds: 30,
    durationRemainingMs: remainingMs,
    durationRunning: running,
    durationElapsed: elapsed,
    ...(deadline === null ? {} : { durationEndsAtMonotonicMs: deadline })
  };
  const attributes = {};
  const fill = { style: {} };
  const progress = {
    setAttribute(name, value) { attributes[name] = String(value); },
    querySelector(selector) { return selector === '.duration-progress-fill' ? fill : null; }
  };
  const display = { textContent: '' };
  const button = {
    textContent: '',
    disabled: false,
    setAttribute(name, value) { this[name] = String(value); }
  };
  const document = {
    querySelector(selector) {
      if (selector === '[data-duration-display="0"]') return display;
      if (selector === '[data-duration-toggle="0"]') return button;
      if (selector === '[data-duration-progress="0"]') return progress;
      return null;
    }
  };
  const context = {
    window: { performance: { now: () => monotonicNow.value } },
    Date: { now: () => wallNow.value },
    Number,
    Math,
    Object,
    state: { active: { sets: [set] } },
    document,
    formatDuration,
    t(key) { return key === 'timerProgress' ? 'Timer progress' : key; }
  };
  const names = ['durationClockNow', 'remainingDurationMs', 'durationProgressState', 'renderDurationControls'];
  const functions = names.map(name => extractFunction(APP, name)).join('\n');
  vm.runInNewContext(`${functions}\nglobalThis.api = { durationClockNow, remainingDurationMs, durationProgressState, renderDurationControls };`, context);
  return { api: context.api, set, attributes, fill, display, button, monotonicNow, wallNow };
}

test('fresh timed set renders zero progress with an accessible value', () => {
  const h = harness();
  h.api.renderDurationControls(0);
  assert.equal(h.attributes['aria-valuenow'], '0');
  assert.equal(h.attributes['aria-valuetext'], '00:00 / 00:30');
  assert.equal(h.fill.style.width, '0%');
  assert.equal(h.display.textContent, '00:30');
});

test('running progress follows the monotonic clock and ignores wall-clock jumps', () => {
  const h = harness({ running: true, remainingMs: 20000, deadline: 21000 });
  h.api.renderDurationControls(0);
  assert.equal(h.attributes['aria-valuenow'], '33');
  assert.equal(h.attributes['aria-valuetext'], '00:10 / 00:30');
  assert.equal(h.fill.style.width, '33%');

  h.wallNow.value += 6 * 60 * 60 * 1000;
  h.api.renderDurationControls(0);
  assert.equal(h.attributes['aria-valuenow'], '33');

  h.monotonicNow.value += 10000;
  h.api.renderDurationControls(0);
  assert.equal(h.attributes['aria-valuenow'], '67');
  assert.equal(h.attributes['aria-valuetext'], '00:20 / 00:30');
  assert.equal(h.fill.style.width, '67%');
});

test('paused timer keeps the persisted elapsed fraction', () => {
  const h = harness({ remainingMs: 12000, running: false });
  h.api.renderDurationControls(0);
  assert.equal(h.attributes['aria-valuenow'], '60');
  assert.equal(h.attributes['aria-valuetext'], '00:18 / 00:30');
  assert.equal(h.fill.style.width, '60%');
});

test('expired timer reports a complete progress value', () => {
  const h = harness({ running: true, remainingMs: 10000, deadline: 1000 });
  h.api.renderDurationControls(0);
  assert.equal(h.attributes['aria-valuenow'], '100');
  assert.equal(h.attributes['aria-valuetext'], '00:30 / 00:30');
  assert.equal(h.fill.style.width, '100%');
});

test('corrupt remaining values are clamped to a truthful zero-to-one-hundred range', () => {
  const tooMuchTime = harness({ remainingMs: 90000 });
  tooMuchTime.api.renderDurationControls(0);
  assert.equal(tooMuchTime.attributes['aria-valuenow'], '0');
  assert.equal(tooMuchTime.fill.style.width, '0%');

  const negativeTime = harness({ remainingMs: -5000 });
  negativeTime.api.renderDurationControls(0);
  assert.equal(negativeTime.attributes['aria-valuenow'], '100');
  assert.equal(negativeTime.fill.style.width, '100%');
});

test('timed-set markup uses a named determinate progressbar without a per-second live region', () => {
  const match = APP.match(/<div class="duration-progress"[\s\S]*?<\/div>/);
  assert.ok(match, 'duration progress markup is missing');
  assert.match(match[0], /data-duration-progress=/);
  assert.match(match[0], /role="progressbar"/);
  assert.match(match[0], /aria-valuemin="0"/);
  assert.match(match[0], /aria-valuemax="100"/);
  assert.match(match[0], /aria-valuenow=/);
  assert.match(match[0], /aria-valuetext=/);
  assert.doesNotMatch(match[0], /aria-live=/);
});

test('progressbar has bilingual accessible naming and a reduced-motion-aware visual track', () => {
  assert.match(APP, /timerProgress:'تقدم المؤقت'/);
  assert.match(APP, /timerProgress:'Timer progress'/);
  assert.match(CSS, /\.duration-progress\{[^}]*width:100%/);
  assert.match(CSS, /\.duration-progress-fill\{[^}]*transition:width \.25s linear/);
  assert.match(CSS, /prefers-reduced-motion:reduce/);
});
