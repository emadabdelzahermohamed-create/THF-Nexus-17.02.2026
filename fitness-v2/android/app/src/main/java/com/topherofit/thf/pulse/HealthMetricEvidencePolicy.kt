package com.topherofit.thf.pulse

import java.time.Duration
import java.time.Instant

/**
 * Fail-closed sanity checks for Health Connect interval metrics.
 *
 * The ceilings are deliberately broad anomaly guards, not physiological estimates or
 * exercise targets: 6 steps/second, 50 metres/second, and 100 active kcal/minute.
 * A rejected record remains source-labelled for diagnostics but is excluded from totals.
 */
internal object HealthMetricEvidencePolicy {
    private const val MAX_STEPS_PER_SECOND = 6.0
    private const val MAX_DISTANCE_METERS_PER_SECOND = 50.0
    private const val MAX_ACTIVE_KILOCALORIES_PER_MINUTE = 100.0

    fun assessSteps(
        count: Long,
        start: Instant,
        end: Instant,
        observedAt: Instant,
    ): String? {
        intervalFailure(start, end, observedAt)?.let { return it }
        if (count < 0L) return "NEGATIVE_STEPS"
        val rate = count.toDouble() / intervalSeconds(start, end)
        return if (!rate.isFinite() || rate > MAX_STEPS_PER_SECOND) {
            "IMPLAUSIBLE_STEPS_RATE"
        } else {
            null
        }
    }

    fun assessDistance(
        meters: Double,
        start: Instant,
        end: Instant,
        observedAt: Instant,
    ): String? {
        intervalFailure(start, end, observedAt)?.let { return it }
        if (!meters.isFinite() || meters < 0.0) return "INVALID_DISTANCE_VALUE"
        val rate = meters / intervalSeconds(start, end)
        return if (!rate.isFinite() || rate > MAX_DISTANCE_METERS_PER_SECOND) {
            "IMPLAUSIBLE_DISTANCE_RATE"
        } else {
            null
        }
    }

    fun assessActiveCalories(
        kilocalories: Double,
        start: Instant,
        end: Instant,
        observedAt: Instant,
    ): String? {
        intervalFailure(start, end, observedAt)?.let { return it }
        if (!kilocalories.isFinite() || kilocalories < 0.0) {
            return "INVALID_ACTIVE_CALORIES_VALUE"
        }
        val minutes = intervalSeconds(start, end) / 60.0
        val rate = kilocalories / minutes
        return if (!rate.isFinite() || rate > MAX_ACTIVE_KILOCALORIES_PER_MINUTE) {
            "IMPLAUSIBLE_ACTIVE_CALORIES_RATE"
        } else {
            null
        }
    }

    private fun intervalFailure(
        start: Instant,
        end: Instant,
        observedAt: Instant,
    ): String? {
        if (start.isBefore(Instant.EPOCH) || !end.isAfter(start)) {
            return "INVALID_METRIC_INTERVAL"
        }
        if (end.isAfter(observedAt)) return "FUTURE_METRIC_RECORD"
        val seconds = intervalSeconds(start, end)
        return if (!seconds.isFinite() || seconds <= 0.0) {
            "INVALID_METRIC_INTERVAL"
        } else {
            null
        }
    }

    private fun intervalSeconds(start: Instant, end: Instant): Double {
        val duration = Duration.between(start, end)
        return duration.seconds.toDouble() + duration.nano.toDouble() / 1_000_000_000.0
    }
}
