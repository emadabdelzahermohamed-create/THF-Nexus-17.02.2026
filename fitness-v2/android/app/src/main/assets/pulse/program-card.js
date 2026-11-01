/* Accessible program cards with a separate quick-save action. */
(() => {
  'use strict';
  function renderProgramCard(program, options) {
    const saved = Boolean(options.saved);
    const name = options.local(program.name);
    const id = options.escapeHtml(program.id);
    const favoriteLabel = `${options.t(saved ? 'removeProgramFavorite' : 'addProgramFavorite')}: ${name}`;
    const image = options.image ? `<img src="./${options.escapeHtml(options.image)}" alt="" loading="lazy">` : '';
    return `<article class="program-card" data-program="${id}">
      <button class="program-card-open" type="button" data-program="${id}" aria-label="${options.escapeHtml(options.t('openProgramDetails'))}: ${options.escapeHtml(name)}">
        <span class="program-cover">${image}<span class="program-duration">${options.escapeHtml(program.weeks)} ${options.escapeHtml(options.t('weeks'))}</span></span>
        <span class="program-copy">
          <span class="pill gold">${options.escapeHtml(options.local(program.section))}</span>
          ${saved ? `<span class="pill gold saved-program-badge">${options.escapeHtml(options.t('savedProgram'))}</span>` : ''}
          <h3>${options.escapeHtml(name)}</h3>
          <p>${options.escapeHtml(options.local(program.summary))}</p>
          <span class="program-meta"><b>${options.escapeHtml(program.daysPerWeek)}</b> ${options.escapeHtml(options.t('daysWeekly'))} · <b>${options.escapeHtml(program.estimatedSessionMinutes)}</b> ${options.escapeHtml(options.t('min'))}</span>
          <span class="tag-row"><span class="tag">${options.escapeHtml(options.local(program.level))}</span><span class="tag">${options.escapeHtml(options.local(program.goal))}</span><span class="tag">✓ ${options.escapeHtml(options.t('offline'))}</span></span>
        </span>
      </button>
      <button class="program-card-favorite" type="button" data-program="${id}" aria-pressed="${saved}" aria-label="${options.escapeHtml(favoriteLabel)}" title="${options.escapeHtml(favoriteLabel)}"><span aria-hidden="true">${saved ? '★' : '☆'}</span></button>
    </article>`;
  }
  window.THFProgramCard = Object.freeze({renderProgramCard});
})();
