'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const assets = path.resolve(__dirname, '../../android/app/src/main/assets/pulse');
const helperSource = fs.readFileSync(path.join(assets, 'exercise-muscle-groups.js'), 'utf8');
const sandbox = { window: {} };
vm.runInNewContext(helperSource, sandbox, { filename: 'exercise-muscle-groups.js' });
const render = sandbox.window.THFExerciseMuscleGroups.render;

test('active workout separates Arabic primary and secondary muscles', () => {
  const item = {
    muscles: {
      primary: { en: ['chest'], ar: ['الصدر'] },
      secondary: { en: ['triceps', 'shoulders'], ar: ['الترايسبس', 'الكتف'] }
    }
  };
  const html = render(item, 'ar', {
    primary: 'العضلات الأساسية',
    secondary: 'العضلات المساعدة'
  });
  assert.ok(html.indexOf('العضلات الأساسية') < html.indexOf('العضلات المساعدة'));
  assert.match(html, /الصدر/);
  assert.match(html, /الترايسبس/);
  assert.match(html, /الكتف/);
});

test('English labels and muscle values are localized independently', () => {
  const item = {
    muscles: {
      primary: { en: ['quadriceps'], ar: ['أمامية الفخذ'] },
      secondary: { en: ['glutes'], ar: ['الألوية'] }
    }
  };
  const html = render(item, 'en', { primary: 'Primary muscles', secondary: 'Secondary muscles' });
  assert.match(html, /Primary muscles/);
  assert.match(html, /Secondary muscles/);
  assert.match(html, /quadriceps/);
  assert.match(html, /glutes/);
  assert.doesNotMatch(html, /أمامية الفخذ|الألوية/);
});

test('missing Arabic muscle labels fall back to the English catalog values', () => {
  const item = { muscles: { primary: { en: ['back'] }, secondary: { en: ['biceps'] } } };
  const html = render(item, 'ar');
  assert.match(html, /العضلات الأساسية/);
  assert.match(html, /العضلات المساعدة/);
  assert.match(html, />back</);
  assert.match(html, />biceps</);
});

test('untrusted labels and muscle names are escaped and duplicate values are removed', () => {
  const item = {
    muscles: {
      primary: { en: ['<img src=x onerror=alert(1)>', 'chest', ' chest ', ''] },
      secondary: { en: [] }
    }
  };
  const html = render(item, 'en', { primary: '<script>alert(1)</script>', secondary: 'Secondary' });
  assert.match(html, /&lt;script&gt;alert\(1\)&lt;\/script&gt;/);
  assert.match(html, /&lt;img src=x onerror=alert\(1\)&gt;/);
  assert.equal((html.match(/>chest</g) || []).length, 1);
  assert.doesNotMatch(html, /<img|<script/);
});

test('missing muscle groups produce no empty headings', () => {
  assert.equal(render({ muscles: {} }, 'en'), '');
  assert.equal(render(null, 'ar'), '');
});
