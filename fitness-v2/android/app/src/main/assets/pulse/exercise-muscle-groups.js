(() => {
  'use strict';

  const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, match => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  }[match]));

  function muscleValues(item, group, language) {
    const source = item?.muscles?.[group];
    const localized = source?.[language];
    const values = Array.isArray(localized) && localized.length
      ? localized
      : (Array.isArray(source?.en) ? source.en : []);
    const seen = new Set();
    return values
      .filter(value => typeof value === 'string')
      .map(value => value.trim())
      .filter(value => {
        if (!value || seen.has(value)) return false;
        seen.add(value);
        return true;
      });
  }

  function groupMarkup(label, values, modifier) {
    if (!values.length) return '';
    const tags = values.map(value => `<span class="tag">${escapeHtml(value)}</span>`).join('');
    return `<section class="active-muscle-group active-muscle-group--${modifier}"><h3 class="active-muscle-label">${escapeHtml(label)}</h3><div class="tag-row">${tags}</div></section>`;
  }

  function render(item, language, labels = {}) {
    const lang = language === 'ar' ? 'ar' : 'en';
    const primaryLabel = typeof labels.primary === 'string' && labels.primary
      ? labels.primary
      : (lang === 'ar' ? 'العضلات الأساسية' : 'Primary muscles');
    const secondaryLabel = typeof labels.secondary === 'string' && labels.secondary
      ? labels.secondary
      : (lang === 'ar' ? 'العضلات المساعدة' : 'Secondary muscles');
    return [
      groupMarkup(primaryLabel, muscleValues(item, 'primary', lang), 'primary'),
      groupMarkup(secondaryLabel, muscleValues(item, 'secondary', lang), 'secondary')
    ].join('');
  }

  window.THFExerciseMuscleGroups = Object.freeze({ render });
})();
