const assert = require('node:assert/strict');
const { createDialogFocusManager } = require('../../android/app/src/main/assets/pulse/dialog-accessibility.js');

function makeNode(name, { hidden = false, focusable = true, disabled = false } = {}) {
  return {
    name, disabled, isConnected: true, focused: false, attrs: {}, children: [], parent: null, focusable,
    classList: {
      values: new Set(hidden ? ['hidden'] : []),
      contains(value) { return this.values.has(value); },
      add(value) { this.values.add(value); },
      remove(value) { this.values.delete(value); }
    },
    style: {},
    focus() { this.focused = true; doc.activeElement = this; },
    getAttribute(key) { return this.attrs[key] ?? null; },
    closest(selector) { let node = this; while (node) { if (selector === '.hidden' && node.classList?.contains('hidden')) return node; node = node.parent; } return null; },
    getClientRects() { return this.classList.contains('hidden') ? [] : [{}]; },
    querySelectorAll() { return this.children.filter(node => node.focusable !== false); },
    contains(node) { while (node) { if (node === this) return true; node = node.parent; } return false; }
  };
}
const doc = { body: { style: { overflow: 'auto' } }, activeElement: null };
const trigger = makeNode('exercise-card');
const programTrigger = makeNode('program-card');
const exerciseDialog = makeNode('exercise-dialog', { hidden: true });
const programDialog = makeNode('program-dialog', { hidden: true });
const exerciseClose = makeNode('exercise-close');
const exerciseStart = makeNode('exercise-start');
const disabledControl = makeNode('temporarily-disabled-control', { disabled: true });
const programClose = makeNode('program-close');
const programSessionExercise = makeNode('program-session-exercise');
exerciseClose.parent = exerciseDialog; exerciseStart.parent = exerciseDialog; disabledControl.parent = exerciseDialog;
programClose.parent = programDialog; programSessionExercise.parent = programDialog;
exerciseDialog.children = [exerciseClose, exerciseStart, disabledControl];
programDialog.children = [programClose, programSessionExercise];
const nodes = { exerciseDetail: exerciseDialog, programDetail: programDialog, detailCloseButton: exerciseClose, programDetailCloseButton: programClose, trainScreen: makeNode('train-screen'), mainContent: makeNode('main-content') };
const getById = id => nodes[id] || null;
const manager = createDialogFocusManager({ document: doc, getById });

// Opening focuses the close button; closing restores explicit trigger and prior scroll behavior.
doc.activeElement = makeNode('body');
manager.open('exerciseDetail', 'detailCloseButton', trigger);
assert.equal(doc.activeElement, exerciseClose);
assert.equal(doc.body.style.overflow, 'hidden');
manager.close('exerciseDetail');
assert.equal(doc.activeElement, trigger);
assert.equal(doc.body.style.overflow, 'auto');

// Tab and Shift+Tab wrap inside the modal.
doc.activeElement = trigger;
manager.open('exerciseDetail', 'detailCloseButton');
doc.activeElement = exerciseStart;
let prevented = false;
manager.handleKeydown({ key: 'Tab', shiftKey: false, preventDefault() { prevented = true; } }, 'exerciseDetail');
assert.equal(prevented, true);
assert.equal(doc.activeElement, exerciseClose);
manager.handleKeydown({ key: 'Tab', shiftKey: true, preventDefault() { prevented = true; } }, 'exerciseDetail');
assert.equal(doc.activeElement, exerciseStart);
manager.close('exerciseDetail');

// Switching from program detail to exercise detail returns to the real program card.
doc.activeElement = programTrigger;
manager.open('programDetail', 'programDetailCloseButton');
manager.close('programDetail');
manager.open('exerciseDetail', 'detailCloseButton');
manager.close('exerciseDetail');
assert.equal(doc.activeElement, programTrigger);

// Programmatic close before entering a workout must not focus the now-hidden library card.
doc.activeElement = trigger;
manager.open('exerciseDetail', 'detailCloseButton');
manager.close('exerciseDetail', false);
assert.equal(doc.activeElement, exerciseClose);
assert.equal(doc.body.style.overflow, 'auto');

// If the original trigger has no rendered box, focus falls back to the main content.
doc.activeElement = trigger;
manager.open('exerciseDetail', 'detailCloseButton');
trigger.getClientRects = () => [];
manager.close('exerciseDetail');
assert.equal(doc.activeElement, nodes.mainContent);

// A dynamically disabled control can remain active even though it is no longer tabbable.
doc.activeElement = trigger;
manager.open('exerciseDetail', 'detailCloseButton');
doc.activeElement = disabledControl;
prevented = false;
manager.handleKeydown({ key: 'Tab', shiftKey: false, preventDefault() { prevented = true; } }, 'exerciseDetail');
assert.equal(prevented, true, 'Tab must be trapped when active element is no longer focusable');
assert.equal(doc.activeElement, exerciseClose, 'forward Tab must move to first visible focusable control');
doc.activeElement = disabledControl;
prevented = false;
manager.handleKeydown({ key: 'Tab', shiftKey: true, preventDefault() { prevented = true; } }, 'exerciseDetail');
assert.equal(prevented, true, 'Shift+Tab must be trapped when active element is no longer focusable');
assert.equal(doc.activeElement, exerciseStart, 'reverse Tab must move to last visible focusable control');
manager.close('exerciseDetail');

// Focus moved outside by script/browser must be redirected into the active dialog.
doc.activeElement = trigger;
manager.open('exerciseDetail', 'detailCloseButton');
doc.activeElement = trigger;
assert.equal(manager.handleFocusIn({ target: trigger }, 'exerciseDetail'), true);
assert.equal(doc.activeElement, exerciseClose, 'focusin outside the dialog must return focus to its first control');
doc.activeElement = exerciseStart;
assert.equal(manager.handleFocusIn({ target: exerciseStart }, 'exerciseDetail'), false);
assert.equal(doc.activeElement, exerciseStart, 'focus already inside the dialog must remain undisturbed');
manager.close('exerciseDetail');

console.log('PASS: 7 dialog focus/lifecycle scenarios');