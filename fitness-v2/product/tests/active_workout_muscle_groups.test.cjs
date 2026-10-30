'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const PULSE = path.resolve(__dirname, '../../android/app/src/main/assets/pulse');
const APP = fs.readFileSync(path.join(PULSE, 'app.js'), 'utf8');
const HTML = fs.readFileSync(path.join(PULSE, 'index.html'), 'utf8');
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

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, match => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[match]));
}

const LABELS = {
  en: { primaryMuscles: 'Primary muscles', secondaryMuscles: 'Supporting muscles' },
  ar: { primaryMuscles: 'العضلات الأساسية', secondaryMuscles: 'العضلات المساعدة' }
};

function renderer(language, labels = LABELS[language]) {
  const context = {
    state: { lang: language },
    t(key) { return labels[key]; },
    escapeHtml
  };
  const source = extractFunction(APP, 'renderActiveMuscleGroups');
  return vm.runInNewContext(`(${source})`, context);
}

test('active workout separates primary and supporting muscles in English', () => {
  const render = renderer('en');
  const html = render({
    muscles: {
      primary: { en: ['Quadriceps'] },
      secondary: { en: ['Glutes', 'Calves'] }
    }
  });
  assert.ok(html.indexOf('Primary muscles') < html.indexOf('Supporting muscles'));
  assert.match(html, /role="group" aria-label="Primary muscles"/);
  assert.match(html, /role="group" aria-label="Supporting muscles"/);
  assert.match(html, />Quadriceps</);
  assert.match(html, />Glutes</);
  assert.match(html, />Calves</);
});

test('active workout uses localized Arabic labels and muscle names', () => {
  const render = renderer('ar');
  const html = render({
    muscles: {
      primary: { ar: ['أمامية الفخذ'] },
      secondary: { ar: ['الألوية', 'السمانة'] }
    }
  });
  assert.match(html, /aria-label="العضلات الأساسية"/);
  assert.match(html, /aria-label="العضلات المساعدة"/);
  assert.match(html, />أمامية الفخذ</);
  assert.match(html, />الألوية</);
  assert.match(html, />السمانة</);
});

test('empty or missing secondary muscles do not create an empty group', () => {
  const render = renderer('en');
  const html = render({ muscles: { primary: { en: ['Chest'] }, secondary: { en: [] } } });
  assert.equal((html.match(/active-muscle-group/g) || []).length, 1);
  assert.doesNotMatch(html, /Supporting muscles/);
});

test('secondary-only and malformed muscle payloads fail safely', () => {
  const render = renderer('en');
  const secondaryOnly = render({ muscles: { primary: { en: [] }, secondary: { en: ['Triceps'] } } });
  assert.match(secondaryOnly, />Triceps</);
  assert.equal(render({ muscles: null }), '');
  assert.equal(render({}), '');
});

test('muscle labels and values are escaped before entering the active workout DOM', () => {
  const render = renderer('en', {
    primaryMuscles: 'Primary <muscles>',
    secondaryMuscles: 'Supporting & stabilizing'
  });
  const html = render({
    muscles: {
      primary: { en: ['<script>alert(1)</script>'] },
      secondary: { en: ['A&B'] }
    }
  });
  assert.match(html, /Primary &lt;muscles&gt;/);
  assert.match(html, /Supporting &amp; stabilizing/);
  assert.match(html, /&lt;script&gt;alert\(1\)&lt;\/script&gt;/);
  assert.match(html, /A&amp;B/);
  assert.doesNotMatch(html, /<script>/);
});

test('active workout renderer consumes the grouped muscle helper and bilingual labels exist', () => {
  assert.match(APP, /activeMuscles'\)\.innerHTML\s*=\s*renderActiveMuscleGroups\(item\)/);
  assert.match(APP, /primaryMuscles:'العضلات الأساسية'/);
  assert.match(APP, /secondaryMuscles:'العضلات المساعدة'/);
  assert.match(APP, /primaryMuscles:'Primary muscles'/);
  assert.match(APP, /secondaryMuscles:'Supporting muscles'/);
  assert.match(HTML, /id="activeMuscles" class="active-muscle-groups"/);
  assert.match(CSS, /\.active-muscle-groups\{display:grid/);
  assert.match(CSS, /\.active-muscle-label\{[^}]*font-size:10px/);
});
