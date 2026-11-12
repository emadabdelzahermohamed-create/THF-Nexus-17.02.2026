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

    function open(dialogId, closeButtonId, returnTarget = null) {
      const dialog = getById(dialogId);
      if (!dialog) return;
      if (!anyDialogOpen()) {
        const active = returnTarget || document.activeElement;
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
      if (restoreFocus && target && target.isConnected !== false && !(typeof target.closest === 'function' && target.closest('.hidden')) && !(typeof target.getClientRects === 'function' && target.getClientRects().length === 0)) {
        target.focus();
        return;
      }
      if (restoreFocus) {
        const fallback = getById('mainContent') || getById('trainScreen');
        if (fallback && typeof fallback.focus === 'function') fallback.focus();
      }
    }

    function handleFocusIn(event, dialogId) {
      const dialog = getById(dialogId);
      if (!dialog || dialog.classList.contains('hidden')) return false;
      const target = event && event.target;
      if (target && typeof dialog.contains === 'function' && dialog.contains(target)) return false;
      const focusables = visibleFocusable(dialog);
      if (!focusables.length) return false;
      // A script or browser action can move focus outside even when Tab is trapped.
      // Pull it back into the active modal without preventing the focusin event itself.
      focusables[0].focus();
      return true;
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
      const activeIsFocusable = focusables.includes(active);
      if (!activeIsFocusable) {
        // Dynamic content can disable or hide the focused control while the dialog stays open.
        // Keep Tab navigation inside the dialog even when the active node is still a descendant.
        event.preventDefault();
        (event.shiftKey ? last : first).focus();
      } else if (event.shiftKey && active === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && active === last) {
        event.preventDefault();
        first.focus();
      }
      return true;
    }

    return { open, close, handleKeydown, handleFocusIn };
  }

  return { createDialogFocusManager };
}));