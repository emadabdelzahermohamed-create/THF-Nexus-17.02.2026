const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const appRoot = path.resolve(__dirname, '../../android/app/src/main/assets/pulse');
const helperSource = fs.readFileSync(path.join(appRoot, 'exercise-favorites.js'), 'utf8');
const appSource = fs.readFileSync(path.join(appRoot, 'app.js'), 'utf8');
const htmlSource = fs.readFileSync(path.join(appRoot, 'index.html'), 'utf8');

function createFavorites(storage, exercises = [{id:'a'}, {id:'b'}]) {
  const context = {window:{}};
  vm.runInNewContext(helperSource, context, {filename:'exercise-favorites.js'});
  return context.window.THFExerciseFavorites.createExerciseFavorites(storage, exercises);
}

function memoryStorage(initialValue = null) {
  const values = new Map();
  const writes = [];
  if (initialValue !== null) values.set('pulse.v2.exerciseFavorites', initialValue);
  return {
    values,
    writes,
    getItem(key) { return values.has(key) ? values.get(key) : null; },
    setItem(key, value) { writes.push([key, String(value)]); values.set(key, String(value)); }
  };
}

test('loads only known unique favorite IDs and ignores malformed JSON', () => {
  const storage = memoryStorage(JSON.stringify(['a', 'a', 'stale-id', 7]));
  const favorites = createFavorites(storage);
  assert.deepEqual(Array.from(favorites.values()), ['a']);
  assert.equal(favorites.has('stale-id'), false);
  assert.equal(storage.writes.length, 0);

  const malformed = createFavorites(memoryStorage('{broken'));
  assert.deepEqual(Array.from(malformed.values()), []);
});

test('toggle adds and removes favorites and persists the exact local list', () => {
  const storage = memoryStorage();
  const favorites = createFavorites(storage);
  assert.equal(favorites.toggle('a'), true);
  assert.equal(favorites.has('a'), true);
  assert.equal(favorites.toggle('b'), true);
  assert.equal(favorites.toggle('a'), false);
  assert.deepEqual(JSON.parse(storage.getItem('pulse.v2.exerciseFavorites')), ['b']);
  assert.deepEqual(Array.from(favorites.values()), ['b']);
});

test('unknown exercise IDs cannot be saved', () => {
  const storage = memoryStorage();
  const favorites = createFavorites(storage);
  assert.equal(favorites.toggle('not-in-catalog'), null);
  assert.deepEqual(Array.from(favorites.values()), []);
  assert.equal(storage.writes.length, 0);
});

test('storage exceptions fail closed without breaking the in-memory toggle', () => {
  const storage = {
    getItem() { throw new Error('storage unavailable'); },
    setItem() { throw new Error('storage unavailable'); }
  };
  const favorites = createFavorites(storage);
  assert.equal(favorites.toggle('a'), true);
  assert.equal(favorites.has('a'), true);
});

test('favorite controls are wired into the bilingual library and detail UI', () => {
  assert.match(htmlSource, /id="favoritesOnlyFilter" type="checkbox"/);
  assert.match(htmlSource, /id="toggleFavoriteBtn"[^>]*aria-pressed="false"[^>]*data-i18n="addFavorite"/);
  assert.match(htmlSource, /<script src="\.\/exercise-favorites\.js"><\/script>\s*<script src="\.\/app\.js"><\/script>/);
  assert.match(appSource, /favoritesOnly:'المفضلة فقط'/);
  assert.match(appSource, /favoritesOnly:'Favorites only'/);
  assert.match(appSource, /state\.favorites\.has\(item\.id\)/);
  assert.match(appSource, /state\.filters\.favoritesOnly/);
  assert.match(appSource, /state\.filters = \{body:'',muscle:'',equipment:'',movement:'',level:'',goal:'',favoritesOnly:false\}/);
  assert.match(appSource, /saved-exercise-badge/);
});
