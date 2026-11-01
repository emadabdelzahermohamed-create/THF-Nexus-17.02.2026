const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const appRoot = path.resolve(__dirname, '../../android/app/src/main/assets/pulse');
const favoritesSource = fs.readFileSync(path.join(appRoot, 'program-favorites.js'), 'utf8');
const cardSource = fs.readFileSync(path.join(appRoot, 'program-card.js'), 'utf8');
const programsSource = fs.readFileSync(path.join(appRoot, 'data/programs.js'), 'utf8');
const appSource = fs.readFileSync(path.join(appRoot, 'app.js'), 'utf8');
const htmlSource = fs.readFileSync(path.join(appRoot, 'index.html'), 'utf8');
const cssSource = fs.readFileSync(path.join(appRoot, 'styles.css'), 'utf8');

const labels = {
  ar: {weeks:'أسابيع',daysWeekly:'أيام أسبوعيًا',min:'د',offline:'أوفلاين',addProgramFavorite:'أضف البرنامج للمفضلة',removeProgramFavorite:'إزالة البرنامج من المفضلة',savedProgram:'برنامج مفضل',openProgramDetails:'افتح تفاصيل البرنامج'},
  en: {weeks:'weeks',daysWeekly:'days weekly',min:'min',offline:'Offline',addProgramFavorite:'Add program to favorites',removeProgramFavorite:'Remove program from favorites',savedProgram:'Saved program',openProgramDetails:'Open program details'}
};
const program = {
  id:'program-1', name:{ar:'قوة <مبتدئ>',en:'Beginner <Strength>'},
  section:{ar:'الجيم',en:'Gym'}, summary:{ar:'ملخص',en:'Summary'},
  weeks:4, daysPerWeek:3, estimatedSessionMinutes:35,
  level:{ar:'مبتدئ',en:'Beginner'}, goal:{ar:'القوة',en:'Strength'}
};
function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, match => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[match]));
}
function loadModule(source, name) {
  const context = {window:{}};
  vm.runInNewContext(source, context, {filename:name});
  return context.window;
}
function createStore(initial) {
  const values = new Map(Object.entries(initial || {}));
  return {getItem:key => values.has(key) ? values.get(key) : null,setItem:(key,value) => values.set(key,String(value)),values};
}
function render(saved, lang='en', value=program, image='images/program.png') {
  const win = loadModule(cardSource, 'program-card.js');
  return win.THFProgramCard.renderProgramCard(value, {
    saved, lang, image, t:key=>labels[lang][key] || labels.en[key] || key,
    local:value=>value?.[lang] ?? value?.en ?? '', escapeHtml
  });
}

test('sanitizes persisted IDs against the canonical program catalog', () => {
  const storage = createStore({'pulse.v2.programFavorites':'["program-1","unknown",7,"program-1"]'});
  const api = loadModule(favoritesSource, 'program-favorites.js').THFProgramFavorites.createProgramFavorites(storage, [program]);
  assert.deepEqual([...api.values()], ['program-1']);
  assert.equal(api.has('unknown'), false);
});

test('adds, removes, persists, and rejects unknown program IDs', () => {
  const storage = createStore();
  const api = loadModule(favoritesSource, 'program-favorites.js').THFProgramFavorites.createProgramFavorites(storage, [program]);
  assert.equal(api.toggle('program-1'), true);
  assert.equal(storage.values.get('pulse.v2.programFavorites'), '["program-1"]');
  assert.equal(api.toggle('program-1'), false);
  assert.equal(storage.values.get('pulse.v2.programFavorites'), '[]');
  assert.equal(api.toggle('unknown'), null);
});

test('storage read and write failures do not crash or lose in-memory state', () => {
  const storage = {getItem(){throw new Error('blocked')},setItem(){throw new Error('blocked')}};
  const api = loadModule(favoritesSource, 'program-favorites.js').THFProgramFavorites.createProgramFavorites(storage, [program]);
  assert.equal(api.toggle('program-1'), true);
  assert.equal(api.has('program-1'), true);
});

test('renders separate program-open and favorite buttons with accessible state', () => {
  const html = render(false);
  assert.equal((html.match(/<button\b/g) || []).length, 2);
  assert.ok(html.indexOf('</button>') < html.indexOf('<button class="program-card-favorite"'));
  assert.match(html, /class="program-card-open"[^>]*aria-label="Open program details: Beginner &lt;Strength&gt;"/);
  assert.match(html, /class="program-card-favorite"[^>]*aria-pressed="false" aria-label="Add program to favorites: Beginner &lt;Strength&gt;"/);
  assert.match(html, /src="\.\/images\/program\.png"/);
});

test('renders saved program state and Arabic accessible labels', () => {
  const html = render(true, 'ar');
  assert.match(html, /aria-pressed="true" aria-label="إزالة البرنامج من المفضلة: قوة &lt;مبتدئ&gt;"/);
  assert.match(html, /saved-program-badge">برنامج مفضل<\/span>/);
  assert.match(html, /<span aria-hidden="true">★<\/span>/);
});

test('escapes untrusted program IDs, names, summaries, and image paths', () => {
  const unsafe = {...program, id:'p" onclick="bad', name:{en:'<script>bad</script>'}, summary:{en:'<img>'}};
  const html = render(false, 'en', unsafe, 'x"><script>');
  assert.match(html, /data-program="p&quot; onclick=&quot;bad"/);
  assert.match(html, /src="\.\/x&quot;&gt;&lt;script&gt;"/);
  assert.doesNotMatch(html, /<script>/);
});

test('app wires section-aware favorites filtering, quick-save focus recovery, and detail-sheet save state', () => {
  assert.match(appSource, /window\.THFProgramCard\.renderProgramCard/);
  assert.match(appSource, /state\.programFavoritesOnly \|\| state\.programFavorites\.has\(program\.id\)/);
  assert.match(appSource, /querySelectorAll\('\.program-card-open'\)/);
  assert.match(appSource, /querySelectorAll\('\.program-card-favorite'\)[\s\S]*?event\.stopPropagation\(\)[\s\S]*?toggleProgramFavorite\(button\.dataset\.program\)/);
  assert.match(appSource, /restoreCardFocus[\s\S]*?buttons\.find\(button => button\.dataset\.program === id\)[\s\S]*?\$\('programFavoritesOnlyFilter'\)/);
  assert.match(appSource, /renderProgramFavoriteControl\(program\)/);
  assert.match(appSource, /toggleProgramFavoriteBtn/);
});

test('page exposes bilingual program filter and detail save control, loading helpers before app', () => {
  assert.match(htmlSource, /id="programFavoritesOnlyFilter"[^>]*aria-controls="programGrid"/);
  assert.match(htmlSource, /id="toggleProgramFavoriteBtn"[^>]*aria-pressed="false"/);
  assert.match(htmlSource, /program-favorites\.js[\s\S]*?program-card\.js[\s\S]*?app\.js/);
  assert.match(cssSource, /\.program-card-favorite:focus-visible/);
  assert.match(cssSource, /\.program-favorites-filter input:focus-visible/);
});

test('the actual offline program catalog has unique IDs and bilingual names', () => {
  const win = loadModule(programsSource, 'programs.js');
  const programs = win.THF_PROGRAMS;
  assert.ok(Array.isArray(programs));
  assert.ok(programs.length > 0);
  assert.equal(new Set(programs.map(item=>item.id)).size, programs.length);
  assert.ok(programs.every(item => typeof item.id === 'string' && item.id && item.name?.ar && item.name?.en && Array.isArray(item.sessions)));
});
