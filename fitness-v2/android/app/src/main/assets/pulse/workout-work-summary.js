(function attachWorkoutWorkSummary(root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.THF_WORKOUT_WORK_SUMMARY = api;
})(typeof globalThis !== "undefined" ? globalThis : null, function createWorkoutWorkSummary() {
  "use strict";

  function completedVolume(sets) {
    return (sets || []).filter(set => set && set.complete).reduce((sum, set) => {
      return sum + Math.max(0, Number(set.load) || 0) * Math.max(0, Number(set.reps) || 0);
    }, 0);
  }

  function elapsedSeconds(set, elapsedMsForSet) {
    const durationSeconds = Number(set && set.durationSeconds);
    if (!Number.isFinite(durationSeconds) || durationSeconds <= 0) return 0;
    const durationMs = durationSeconds * 1000;
    const rawRemaining = set.durationRemainingMs;
    const remaining = Number(rawRemaining);

    if ((rawRemaining === null || rawRemaining === undefined || rawRemaining === "") && (set.complete || set.durationElapsed)) {
      return Math.floor(durationSeconds);
    }

    let elapsedMs;
    if (typeof elapsedMsForSet === "function") {
      elapsedMs = Number(elapsedMsForSet(set));
    } else if (rawRemaining !== null && rawRemaining !== undefined && rawRemaining !== "" && Number.isFinite(remaining)) {
      elapsedMs = durationMs - remaining;
    } else {
      elapsedMs = (set.complete || set.durationElapsed) ? durationMs : 0;
    }

    if (!Number.isFinite(elapsedMs)) return 0;
    return Math.floor(Math.min(durationMs, Math.max(0, elapsedMs)) / 1000);
  }

  function summarize(programEntries, activeSets, elapsedMsForSet) {
    const entries = Array.isArray(programEntries) ? programEntries : [];
    const previousSets = entries.flatMap(entry => Array.isArray(entry && entry.sets) ? entry.sets : []);
    const currentSets = Array.isArray(activeSets) ? activeSets : [];
    const allSets = previousSets.concat(currentSets);
    const timedSets = allSets.filter(set => Number(set && set.durationSeconds) > 0);

    return {
      volumeKg: completedVolume(allSets),
      timeSeconds: timedSets.reduce((sum, set) => sum + elapsedSeconds(set, elapsedMsForSet), 0),
      timedSetCount: timedSets.length
    };
  }

  function format(summary, timeLabel, formatDuration) {
    const volumeKg = Math.round(Math.max(0, Number(summary && summary.volumeKg) || 0));
    const timeSeconds = Math.max(0, Math.floor(Number(summary && summary.timeSeconds) || 0));
    const timedSetCount = Math.max(0, Math.floor(Number(summary && summary.timedSetCount) || 0));
    const volumeText = String(volumeKg) + " kg";
    const timeText = String(timeLabel || "Time") + ": " +
      (typeof formatDuration === "function" ? formatDuration(timeSeconds) : String(timeSeconds));

    if (timedSetCount > 0 && volumeKg > 0) return volumeText + " · " + timeText;
    if (timedSetCount > 0) return timeText;
    return volumeText;
  }

  return Object.freeze({ summarize, format });
});