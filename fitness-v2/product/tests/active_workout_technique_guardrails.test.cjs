'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const ROOT = path.resolve(__dirname, '../../..');
const PULSE = path.join(ROOT, 'fitness-v2/android/app/src/main/assets/pulse');
const APP = fs.readFileSync(path.join(PULSE, 'app.js'), 'utf8');
const HTML = fs.readFileSync(path.join(PULSE, 'index.html'), 'utf8');
const CSS = fs.readFileSync(path.join(PULSE, 'styles.css'), 'utf8');
const EXERCISES_JS = fs.readFileSync(path.join(PULSE, 'data/exercises.js'), 'utf8');
const exerciseContext = { window: {} };
vm.runInNewContext(EXERCISES_JS, exerciseContext);
const EXERCISES = exerciseContext.window.THF_EXERCISES || [];

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

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, match => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[match]));
}

const LABELS = {
  en: { mistakes: 'Common mistakes', regression: 'Regression', progression: 'Progression' },
  ar: { mistakes: 'أخطاء شائعة', regression: 'نسخة أسهل', progression: 'التدرج' }
};

function makeRenderer(language) {
  const panel = {
    hidden: false,
    classList: {
      toggle(name, hidden) {
        if (name === 'hidden') panel.hidden = Boolean(hidden);
      }
    }
  };
  const content = { innerHTML: '' };
  const dollar = id => id === 'activeCoaching' ? panel : id === 'activeCoachingContent' ? content : null;
  const context = {
    $: dollar,
    t: key => LABELS[language][key] || key,
    local: value => value?.[language] ?? value?.en ?? '',
    escapeHtml,
    state: { lang: language }
  };
  const list = vm.runInNewContext(`(${extractFunction(APP, 'list')})`, context);
  context.list = list;
  const render = vm.runInNewContext(`(${extractFunction(APP, 'renderActiveCoaching')})`, context);
  return { render, panel, content };
}

test('active workout exposes common mistakes, regression and progression in English', () => {
  const view = makeRenderer('en');
  view.render({
    commonMistakes: { en: ['Knees collapsing inward', 'Losing balance'] },
    regression: { en: 'Reduce the range and use support.' },
    progression: { en: 'Increase range only after stable control.' }
  });
  assert.equal(view.panel.hidden, false);
  assert.match(view.content.innerHTML, /Common mistakes/);
  assert.match(view.content.innerHTML, /Knees collapsing inward/);
  assert.match(view.content.innerHTML, /Regression/);
  assert.match(view.content.innerHTML, /Reduce the range and use support/);
  assert.match(view.content.innerHTML, /Progression/);
  assert.match(view.content.innerHTML, /Increase range only after stable control/);
});

test('active workout localizes all coaching sections in Arabic', () => {
  const view = makeRenderer('ar');
  view.render({
    commonMistakes: { ar: ['انهيار الركبتين للداخل'] },
    regression: { ar: 'خفّض المدى واستخدم دعمًا ثابتًا.' },
    progression: { ar: 'زد المدى بعد ثبات التحكم.' }
  });
  assert.equal(view.panel.hidden, false);
  assert.match(view.content.innerHTML, /أخطاء شائعة/);
  assert.match(view.content.innerHTML, /انهيار الركبتين للداخل/);
  assert.match(view.content.innerHTML, /نسخة أسهل/);
  assert.match(view.content.innerHTML, /خفّض المدى واستخدم دعمًا ثابتًا/);
  assert.match(view.content.innerHTML, /التدرج/);
  assert.match(view.content.innerHTML, /زد المدى بعد ثبات التحكم/);
});

test('untrusted exercise coaching text is HTML-escaped', () => {
  const view = makeRenderer('en');
  view.render({
    commonMistakes: { en: ['<script>alert(1)</script>'] },
    regression: { en: '<img src=x onerror=alert(1)>' },
    progression: { en: 'A&B < C' }
  });
  assert.match(view.content.innerHTML, /&lt;script&gt;alert\(1\)&lt;\/script&gt;/);
  assert.match(view.content.innerHTML, /&lt;img src=x onerror=alert\(1\)&gt;/);
  assert.match(view.content.innerHTML, /A&amp;B &lt; C/);
  assert.doesNotMatch(view.content.innerHTML, /<script>|<img/);
});

test('missing or malformed coaching metadata hides the optional panel', () => {
  const view = makeRenderer('en');
  view.render({ commonMistakes: { en: [null, '', 7] }, regression: { en: ' ' }, progression: null });
  assert.equal(view.panel.hidden, true);
  assert.equal(view.content.innerHTML, '');
});

test('all 112 offline exercises have bilingual coaching data and render all three sections', () => {
  assert.equal(EXERCISES.length, 112);
  for (const language of ['en', 'ar']) {
    for (const exercise of EXERCISES) {
      const view = makeRenderer(language);
      const mistakes = exercise.commonMistakes?.[language] || [];
      const regression = exercise.regression?.[language] || '';
      const progression = exercise.progression?.[language] || '';
      assert.ok(mistakes.length > 0, exercise.id + ' missing ' + language + ' mistakes');
      assert.ok(regression.trim(), exercise.id + ' missing ' + language + ' regression');
      assert.ok(progression.trim(), exercise.id + ' missing ' + language + ' progression');
      view.render(exercise);
      assert.equal(view.panel.hidden, false, exercise.id + ' hidden in ' + language);
      for (const mistake of mistakes) assert.ok(view.content.innerHTML.includes(escapeHtml(mistake)), exercise.id + ' missing mistake');
      assert.ok(view.content.innerHTML.includes(escapeHtml(regression)), exercise.id + ' missing regression');
      assert.ok(view.content.innerHTML.includes(escapeHtml(progression)), exercise.id + ' missing progression');
    }
  }
});

test('active workout rerender refreshes coaching when the exercise or language changes', () => {
  assert.match(APP, /renderActiveCoaching\(item\)/);
  assert.match(APP, /if \(state\.active\) renderActiveWorkout\(\)/);
  assert.match(APP, /state\.lang/);
  assert.match(APP, /techniqueGuardrails:'إرشادات الأداء'/);
  assert.match(APP, /techniqueGuardrails:'Technique guardrails'/);
});

test('expandable coaching panel is semantic, keyboard-focusable and motion-sensitive', () => {
  assert.match(HTML, /<details id="activeCoaching" class="surface active-coaching">/);
  assert.match(HTML, /<summary><span data-i18n="techniqueGuardrails">/);
  assert.match(HTML, /id="activeCoachingContent" class="active-coaching-content"/);
  assert.match(CSS, /\.active-coaching>summary:focus-visible/);
  assert.match(CSS, /prefers-reduced-motion:reduce/);
});
