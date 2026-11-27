(() => {
  'use strict';

  function toDate(value) {
    if (value instanceof Date) return new Date(value.getTime());
    if (value === null || value === undefined || value === '') return null;
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? null : date;
  }

  function localDateKey(value) {
    const date = toDate(value);
    if (!date) return '';
    const year = String(date.getFullYear()).padStart(4, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  function validDateKey(value) {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return '';
    const [year, month, day] = value.split('-').map(Number);
    const date = new Date(year, month - 1, day, 12, 0, 0, 0);
    return date.getFullYear() === year && date.getMonth() === month - 1 && date.getDate() === day ? value : '';
  }

  function historyDateKey(entry) {
    const stored = validDateKey(entry?.localDate) || validDateKey(entry?.date);
    if (stored) return stored;
    const source = entry?.date ?? entry?.endedAtMs ?? entry?.startedAtMs;
    return localDateKey(source);
  }

  function sessionsForLocalDay(entries, now = new Date()) {
    const today = localDateKey(now);
    if (!today || !Array.isArray(entries)) return [];
    return entries.filter(entry => historyDateKey(entry) === today);
  }

  function currentStreak(entries, now = new Date()) {
    if (!Array.isArray(entries) || !entries.length) return 0;
    const current = toDate(now);
    if (!current) return 0;
    const days = new Set(entries.map(historyDateKey).filter(Boolean));
    const cursor = new Date(current.getFullYear(), current.getMonth(), current.getDate(), 12, 0, 0, 0);
    if (!days.has(localDateKey(cursor))) cursor.setDate(cursor.getDate() - 1);
    let streak = 0;
    for (let offset = 0; offset < 366; offset++) {
      const key = localDateKey(cursor);
      if (!key || !days.has(key)) break;
      streak++;
      cursor.setDate(cursor.getDate() - 1);
    }
    return streak;
  }

  window.THFWorkoutLocalCalendar = Object.freeze({localDateKey, historyDateKey, sessionsForLocalDay, currentStreak});
})();
