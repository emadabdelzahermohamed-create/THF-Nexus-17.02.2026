const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');

const pulse = path.resolve(__dirname, '../../android/app/src/main/assets/pulse');
const catalog = JSON.parse(fs.readFileSync(path.join(pulse, 'data/exercises.json'), 'utf8'));
const appSource = fs.readFileSync(path.join(pulse, 'app.js'), 'utf8');
const htmlSource = fs.readFileSync(path.join(pulse, 'index.html'), 'utf8');

function extractFunction(name) {
  const start = appSource.indexOf(`  function ${name}(`);
  assert.notEqual(start, -1, `${name} must exist in app.js`);
  const next = appSource.indexOf('\n  function ', start + 1);
  return appSource.slice(start, next < 0 ? undefined : next).trim();
}

function classList() {
  const values = new Set();
  return {
    values,
    toggle(name, force) {
      const enabled = force === undefined ? !values.has(name) : Boolean(force);
      if (enabled) values.add(name); else values.delete(name);
      return enabled;
    },
    contains(name) { return values.has(name); }
  };
}

function makeSectionButton(id) {
  return {
    dataset: { section: id },
    handlers: {},
    addEventListener(name, callback) { this.handlers[name] = callback; },
    setAttribute() {}
  };
}

function runRenderSections() {
  const buttons = ['gym', 'home'].map(makeSectionButton);
  const elements = {
    sectionRail: { innerHTML: '', querySelectorAll: () => buttons },
    resultsTitle: { textContent: '' },
    gymCount: { textContent: '36' },
    gymIntro: { classList: classList() }
  };
  const sandbox = {
    EXERCISES: catalog,
    SECTION_ORDER: ['gym', 'home'],
    state: { section: 'gym' },
    $: id => elements[id],
    local: value => value?.en ?? value ?? '',
    escapeHtml: value => String(value ?? ''),
    resetFilters() {},
    populateFilters() {},
    renderExercises() {}
  };
  const script = `${extractFunction('sectionSummary')}\n${extractFunction('renderSections')}\n({ renderSections })`;
  const { renderSections } = vm.runInNewContext(script, sandbox);
  return { renderSections, buttons, elements, state: sandbox.state };
}

test('gym count reflects the catalog on first render and remains correct after section changes', () => {
  const expectedGymCount = catalog.filter(item => item.section.id === 'gym').length;
  const initialHtml = htmlSource.match(/id="gymCount">(\d+)<\/strong>/);
  assert.ok(initialHtml, 'HTML must provide a truthful pre-script gym count');
  assert.equal(Number(initialHtml[1]), expectedGymCount);

  const h = runRenderSections();
  h.renderSections();
  assert.equal(h.elements.gymCount.textContent, String(expectedGymCount));
  assert.equal(h.elements.gymIntro.classList.contains('hidden'), false);

  h.buttons[1].handlers.click();
  assert.equal(h.state.section, 'home');
  assert.equal(h.elements.gymIntro.classList.contains('hidden'), true);
  assert.equal(h.elements.gymCount.textContent, String(expectedGymCount));
});
