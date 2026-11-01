(() => {
  'use strict';

  function renderExerciseCard(item, options) {
    const saved = Boolean(options.saved);
    const lang = options.lang === 'en' ? 'en' : 'ar';
    const name = options.local(item.name);
    const favoriteLabel = `${options.t(saved ? 'removeFavorite' : 'addFavorite')}: ${name}`;
    const openLabel = `${options.t('openExerciseDetails')}: ${name}`;
    const id = options.escapeHtml(item.id);
    return `<article class="exercise-card" data-id="${id}">
      <button class="exercise-card-open" type="button" data-id="${id}" aria-label="${options.escapeHtml(openLabel)}">
        <span class="media"><img src="./${options.escapeHtml(item.demo.assets[0])}" alt="${options.escapeHtml(item.demo.alt[lang])}" loading="lazy"><span class="offline-badge">✓ ${options.escapeHtml(options.t('offline'))}</span><span class="demo-unavailable-label">${options.escapeHtml(options.t('demoUnavailable'))}</span></span>
        <span class="copy"><span class="pill">${options.escapeHtml(options.local(item.section))}</span>${saved ? `<span class="pill gold saved-exercise-badge">${options.escapeHtml(options.t('savedExercise'))}</span>` : ''}<h3>${options.escapeHtml(name)}</h3><span class="meta">${options.escapeHtml(options.local(item.muscles.primary))} · ${options.escapeHtml(options.local(item.equipment))}</span><span class="tag-row"><span class="tag">${options.escapeHtml(options.local(item.level))}</span><span class="tag">${options.escapeHtml(options.local(item.movement))}</span></span></span>
      </button>
      <button class="exercise-card-favorite" type="button" data-id="${id}" aria-pressed="${saved}" aria-label="${options.escapeHtml(favoriteLabel)}" title="${options.escapeHtml(favoriteLabel)}"><span aria-hidden="true">${saved ? '★' : '☆'}</span></button>
    </article>`;
  }

  window.THFExerciseCard = Object.freeze({renderExerciseCard});
})();
