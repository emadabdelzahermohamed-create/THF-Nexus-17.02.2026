'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const filters = require('../../android/app/src/main/assets/pulse/exercise-library-filters.js');

const PULSE = path.resolve(__dirname, '../../android/app/src/main/assets/pulse');
const app = fs.readFileSync(path.join(PULSE, 'app.js'), 'utf8');
const html = fs.readFileSync(path.join(PULSE, 'index.html'), 'utf8');
const css = fs.readFileSync(path.join(PULSE, 'styles.css'), 'utf8');

test('bodyweight exercises remain available regardless of selected equipment', () => {
  assert.equal(filters.matchesAvailableEquipment('body only', []), true);
  assert.equal(filters.matchesAvailableEquipment('body only', ['machine']), true);
});

test('profile equipment matches canonical ids after normalization', () => {
  assert.equal(filters.matchesAvailableEquipment('dumbbell', ['Dumbbell']), true);
  assert.equal(filters.matchesAvailableEquipment('machine', { equipment: ['machine'] }), true);
});

test('equipment absent from the profile is excluded', () => {
  assert.equal(filters.matchesAvailableEquipment('barbell', ['dumbbell', 'machine']), false);
  assert.equal(filters.matchesAvailableEquipment('foam roll', ['body only']), false);
});

test('empty or malformed equipment values fail closed', () => {
  assert.equal(filters.matchesAvailableEquipment('', ['dumbbell']), false);
  assert.equal(filters.matchesAvailableEquipment(null, ['dumbbell']), false);
  assert.equal(filters.matchesAvailableEquipment('cable', { equipment: 'cable' }), false);
});

test('profile equipment ids are trimmed, lowercased and deduplicated', () => {
  assert.deepEqual(filters.normalizeEquipmentIds([' Dumbbell ', 'dumbbell', '', null, 'BANDS']), ['dumbbell', 'bands']);
});

test('the library filter is localized and explicitly keyboard-operable', () => {
  assert.match(html, /<label class="equipment-match-filter"><input id="profileEquipmentFilter" type="checkbox">/);
  assert.match(html, /data-i18n="myEquipmentOnly"/);
  assert.match(app, /myEquipmentOnly:'أظهر التمارين المناسبة لمعداتي فقط (يشمل وزن الجسم)'/);
  assert.match(app, /myEquipmentOnly:'Only exercises using my available equipment (includes bodyweight)'/);
});

test('the filter reads saved profile equipment and participates in the result predicate', () => {
  assert.match(app, /helper.matchesAvailableEquipment(item?.equipment?.id, profile.equipment)/);
  assert.match(app, /state.filters.profileEquipment || matchesProfileEquipment(item)/);
  assert.match(app, /profileEquipmentFilter').addEventListener('change'/);
});

test('saving profile or onboarding refreshes an active equipment filter', () => {
  const refreshes = app.match(/if(state.filters.profileEquipment)renderExercises();/g) || [];
  assert.equal(refreshes.length, 2);
});

test('reset clears both the filter state and checkbox', () => {
  assert.match(app, /profileEquipment:false}; $('exerciseSearch').value = ''; $('profileEquipmentFilter').checked = false/);
});

test('the helper loads before the app and the control has visible focus styling', () => {
  assert.ok(html.indexOf('./exercise-library-filters.js') < html.indexOf('./app.js'));
  assert.match(css, /equipment-match-filter:focus-within/);
});
