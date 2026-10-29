(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.THFDialogAccessibility = api;
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const FOCUSABLE_SELECTOR = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), summary, [tabindex]:not([tabindex="-1"])';
  const DIALOG_IDS = ['exerciseDetail', 'programDetail'];

  function createDialogFocusManager({ document, getById }) {
    let returnFocus = null;
    let previousOverflow = '';

    function isOpen(id) {
      const dialog = getById(id);
      return Boolean(dialog && !dialog.classList.contains('hidden'));
    }

    function anyDialogOpen() {
      return DIALOG_IDS.some(isOpen);
    }

    function visibleFocusable(dialog) {
      return Array.from(dialog.querySelectorAll(FOCUSABLE_SELECTOR)).filter(node => {
        if (node.disabled || node.getAttribute('tabindex') === '-1') return false;
        if (typeof node.closest === 'function' && node.closest('.hidden')) return false;
        if (typeof node.getClientRects === 'function' && node.getClientRects().length === 0) return false;
        return typeof node.focus === 'function';
      });
    }

    function open(dialogId, closeButtonId) {
      const dialog = getById(dialogId);
      if (!dialog) return;
      if (!anyDialogOpen()) {
        const active = document.activeElement;
        returnFocus = active && typeof active.focus === 'function' ? active : null;
        previousOverflow = document.body.style.overflow;
      }
      dialog.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
      const closeButton = getById(closeButtonId);
      if (closeButton && typeof closeButton.focus === 'function') closeButton.focus();
    }

    function close(dialogId, restoreFocus = true) {
      const dialog = getById(dialogId);
      if (!dialog) return;
      dialog.classList.add('hidden');
      if (anyDialogOpen()) return;
      document.body.style.overflow = previousOverflow;
      const target = returnFocus;
      returnFocus = null;
      if (restoreFocus && target && target.isConnected !== false && !(typeof target.closest === 'function' && target.closest('.hidden'))) {
        target.focus();
        return;
      }
      if (restoreFocus) {
        const fallback = getById('mainContent') || getById('trainScreen');
        if (fallback && typeof fallback.focus === 'function') fallback.focus();
      }
    }

    function handleKeydown(event, dialogId) {
      if (event.key !== 'Tab') return false;
      const dialog = getById(dialogId);
      if (!dialog || dialog.classList.contains('hidden')) return false;
      const focusables = visibleFocusable(dialog);
      if (!focusables.length) {
        event.preventDefault();
        return true;
      }
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      const active = document.activeElement;
      if (event.shiftKey && (active === first || !dialog.contains(active))) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && (active === last || !dialog.contains(active))) {
        event.preventDefault();
        first.focus();
      }
      return true;
    }

    return { open, close, handleKeydown };
  }

  return { createDialogFocusManager };
}));