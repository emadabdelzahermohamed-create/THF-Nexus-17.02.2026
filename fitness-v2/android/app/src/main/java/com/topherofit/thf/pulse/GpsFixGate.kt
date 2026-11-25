package com.topherofit.thf.pulse

import kotlin.math.max

data class GpsFix(
    val latitude: Double,
    val longitude: Double,
    val accuracyMetres: Double,
    val elapsedMs: Long,
    val mock: Boolean,
    val speedMps: Double?,
    val sourceLabel: String? = null,
    val speedAccuracyMps: Double? = null,
)

object GpsFixGate {
    const val MAX_FIX_AGE_MS = 30_000L

    /** Monotonic freshness check shared by live fixes and checkpoint-anchor restoration. */
    fun isFreshElapsedTime(fixElapsedMs: Long, nowMs: Long): Boolean =
        fixElapsedMs >= 0L && fixElapsedMs <= nowMs && nowMs - fixElapsedMs <= MAX_FIX_AGE_MS

    fun accepts(fix: GpsFix, previous: GpsFix?, mode: ActivityMode, sessionStartedMs: Long, nowMs: Long): Boolean {
        val maxAccuracyMetres = when (mode) {
            ActivityMode.WALK, ActivityMode.RUN -> 25.0
            ActivityMode.CYCLE -> 40.0
        }
        if (fix.mock || !fix.accuracyMetres.isFinite() || fix.accuracyMetres <= 0.0 || fix.accuracyMetres > maxAccuracyMetres) return false
        if (!fix.latitude.isFinite() || fix.latitude !in -90.0..90.0 ||
            !fix.longitude.isFinite() || fix.longitude !in -180.0..180.0) return false
        if (fix.elapsedMs < sessionStartedMs || !isFreshElapsedTime(fix.elapsedMs, nowMs)) return false
        val maxKph = maxSpeedKph(mode)
        fix.speedMps?.let { if (!it.isFinite() || it < 0.0 || it * 3.6 > maxKph) return false }
        // A stale previous point is not a valid speed reference after an observation gap.
        val freshPrevious = previous?.takeIf { isFreshElapsedTime(it.elapsedMs, nowMs) }
        if (freshPrevious != null) {
            if (fix.elapsedMs <= freshPrevious.elapsedMs) return false
            if (!freshPrevious.accuracyMetres.isFinite() || freshPrevious.accuracyMetres <= 0.0) return false
            val distance = ActivityMetrics.distanceMetres(freshPrevious.latitude, freshPrevious.longitude, fix.latitude, fix.longitude)
            // GPS displacement is uncertain at both endpoints. Use the worse accuracy radius so
            // a single weak fix cannot make a small stationary wander look like measured movement.
            // Rejected fixes do not advance the accepted anchor, allowing genuine movement to
            // accumulate against the last trustworthy point instead of summing jitter.
            val endpointUncertaintyMetres = max(fix.accuracyMetres, freshPrevious.accuracyMetres)
            val movementDeadbandMetres = max(1.0, endpointUncertaintyMetres * 0.5).coerceAtMost(8.0)
            if (distance < movementDeadbandMetres) return false
            if (ActivityMetrics.averageSpeedKph(distance, fix.elapsedMs - freshPrevious.elapsedMs) > maxKph) return false
        }
        return true
    }

    /**
     * Validate a provider handoff against the last accepted point without applying the normal
     * movement deadband. A stationary Fused fix may legitimately take over from Network/GPS,
     * but a spatial jump that exceeds the sport's speed envelope must not become a new route anchor.
     */
    fun acceptsSourceTransition(
        fix: GpsFix,
        previous: GpsFix?,
        mode: ActivityMode,
        sessionStartedMs: Long,
        nowMs: Long,
    ): Boolean {
        if (!accepts(fix, previous = null, mode = mode, sessionStartedMs = sessionStartedMs, nowMs = nowMs)) {
            return false
        }
        val freshPrevious = previous?.takeIf { isFreshElapsedTime(it.elapsedMs, nowMs) } ?: return true
        if (fix.elapsedMs <= freshPrevious.elapsedMs ||
            !freshPrevious.latitude.isFinite() || freshPrevious.latitude !in -90.0..90.0 ||
            !freshPrevious.longitude.isFinite() || freshPrevious.longitude !in -180.0..180.0 ||
            !freshPrevious.accuracyMetres.isFinite() || freshPrevious.accuracyMetres <= 0.0
        ) {
            return false
        }
        val elapsedMs = fix.elapsedMs - freshPrevious.elapsedMs
        if (elapsedMs <= 0L) return false
        val displacement = ActivityMetrics.distanceMetres(
            freshPrevious.latitude,
            freshPrevious.longitude,
            fix.latitude,
            fix.longitude,
        )
        if (!displacement.isFinite()) return false
        val endpointUncertaintyMetres = max(fix.accuracyMetres, freshPrevious.accuracyMetres)
        val conservativeDisplacement = (
            displacement - max(1.0, endpointUncertaintyMetres * 0.5).coerceAtMost(8.0)
        ).coerceAtLeast(0.0)
        return ActivityMetrics.averageSpeedKph(conservativeDisplacement, elapsedMs) <= maxSpeedKph(mode)
    }

    private fun maxSpeedKph(mode: ActivityMode): Double = when (mode) {
        ActivityMode.WALK -> 13.0
        ActivityMode.RUN -> 32.0
        ActivityMode.CYCLE -> 85.0
    }
}
