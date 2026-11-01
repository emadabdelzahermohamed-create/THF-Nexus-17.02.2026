const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const appRoot = path.resolve(__dirname, '../../android/app/src/main/assets/pulse');
const helperSource = fs.readFileSync(path.join(appRoot, 'exercise-card.js'), 'utf8');
const appSource = fs.readFileSync(path.join(appRoot, 'app.js'), 'utf8');
const htmlSource = fs.readFileSync(path.join(appRoot, 'index.html'), 'utf8');
const cssSource = fs.readFileSync(path.join(appRoot, 'styles.css'), 'utf8');

const labels = {
  ar: {openExerciseDetails:'افتح تفاصيل التمرين',addFavorite:'أضف للمفضلة',removeFavorite:'إزالة من المفضلة',savedExercise:'مفضل',offline:'أوفلاين',demoUnavailable:'العرض غير متاح'},
  en: {openExerciseDetails:'Open exercise details',addFavorite:'Add to favorites',removeFavorite:'Remove from favorites',savedExercise:'Saved',offline:'Offline',demoUnavailable:'Demo unavailable'}
};
const item = {
  id:'ex-1',
  name:{ar:'ضغط <صدر>',en:'Bench <Press>'},
  section:{ar:'الجيم',en:'Gym'},
  demo:{assets:['images/bench.png'],alt:{ar:'صورة مرجعية',en:'Reference frame'}},
  muscles:{primary:{ar:'الصدر',en:'Chest'}},
  equipment:{ar:'دمبل',en:'Dumbbell'},
  level:{ar:'مبتدئ',en:'Beginner'},
  movement:{ar:'دفع',en:'Push'}
};
function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, match => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[match]));
}
function renderCard(saved, lang='en', exercise=item) {
  const context = {window:{}};
  vm.runInNewContext(helperSource, context, {filename:'exercise-card.js'});
  return context.window.THFExerciseCard.renderExerciseCard(exercise, {
    saved, lang, t:key=>labels[lang][key] || labels.en[key] || key,
    local:value=>value?.[lang] ?? value?.en ?? '',
    escapeHtml
  });
}

test('renders separate accessible open and favorite buttons without nesting', () => {
  const html = renderCard(false);
  assert.equal((html.match(/<button\b/g) || []).length, 2);
  assert.ok(html.indexOf('</button>') < html.indexOf('<button class="exercise-card-favorite"'));
  assert.match(html, /class="exercise-card-open"[^>]*aria-label="Open exercise details: Bench &lt;Press&gt;"/);
  assert.match(html, /class="exercise-card-favorite"[^>]*aria-pressed="false" aria-label="Add to favorites: Bench &lt;Press&gt;"/);
  assert.match(html, /<span aria-hidden="true">☆<\/span>/);
});

test('renders saved state and Arabic labels on the card control', () => {
  const html = renderCard(true, 'ar');
  assert.match(html, /aria-pressed="true" aria-label="إزالة من المفضلة: ضغط &lt;صدر&gt;"/);
  assert.match(html, /saved-exercise-badge">مفضل<\/span>/);
  assert.match(html, /<span aria-hidden="true">★<\/span>/);
});

test('escapes IDs, image paths, and visible text before placing them in card markup', () => {
  const unsafe = {...item, id:'x" onfocus="bad', demo:{assets:['x"><script>'],alt:{en:'<image>'}}};
  const html = renderCard(false, 'en', unsafe);
  assert.match(html, /data-id="x&quot; onfocus=&quot;bad"/);
  assert.match(html, /src=".\/x&quot;&gt;&lt;script&gt;"/);
  assert.doesNotMatch(html, /<script>/);
});

test('app and page wire the quick favorite action, focus recovery, and helper before app startup', () => {
  assert.match(appSource, /window\.THFExerciseCard\.renderExerciseCard/);
  assert.match(appSource, /querySelectorAll\('\.exercise-card-open'\)/);
  assert.match(appSource, /querySelectorAll\('\.exercise-card-favorite'\)[\s\S]*?event\.stopPropagation\(\)[\s\S]*?toggleFavorite\(button\.dataset\.id\)/);
  assert.match(appSource, /restoreCardFocus[\s\S]*?buttons\.find\(button => button\.dataset\.id === id\)[\s\S]*?buttons\[0\][\s\S]*?\$\('emptyReset'\)/);
  assert.match(htmlSource, /exercise-card\.js[\s\S]*?app\.js/);
  assert.match(cssSource, /\.exercise-card-favorite:focus-visible/);
});
