package com.topherofit.thf.pulse

import kotlin.math.max
import kotlin.math.min

data class GpsFix(
    val latitude: Double,
    val longitude: Double,
    val accuracyMetres: Double,
    val elapsedMs: Long,
    val mock: Boolean,
    val speedMps: Double?,
)

object GpsFixGate {
    fun accepts(fix: GpsFix, previous: GpsFix?, mode: ActivityMode, sessionStartedMs: Long, nowMs: Long): Boolean {
        val maxAccuracyMetres = when (mode) {
            ActivityMode.WALK, ActivityMode.RUN -> 25.0
            ActivityMode.CYCLE -> 40.0
        }
        if (fix.mock || !fix.accuracyMetres.isFinite() || fix.accuracyMetres <= 0.0 || fix.accuracyMetres > maxAccuracyMetres) return false
        if (!fix.latitude.isFinite() || fix.latitude !in -90.0..90.0 ||
            !fix.longitude.isFinite() || fix.longitude !in -180.0..180.0) return false
        if (fix.elapsedMs < sessionStartedMs || fix.elapsedMs > nowMs || nowMs - fix.elapsedMs > 30_000L) return false
        val maxKph = when (mode) {
            ActivityMode.WALK -> 13.0
            ActivityMode.RUN -> 32.0
            ActivityMode.CYCLE -> 85.0
        }
        fix.speedMps?.let { if (!it.isFinite() || it < 0.0 || it * 3.6 > maxKph) return false }
        if (previous != null) {
            if (fix.elapsedMs <= previous.elapsedMs) return false
            if (!previous.accuracyMetres.isFinite() || previous.accuracyMetres <= 0.0) return false
            val distance = ActivityMetrics.distanceMetres(previous.latitude, previous.longitude, fix.latitude, fix.longitude)
            // GPS displacement is uncertain at both endpoints. Use the worse accuracy radius so
            // a single weak fix cannot make a small stationary wander look like measured movement.
            // Rejected fixes do not advance the accepted anchor, allowing genuine movement to
            // accumulate against the last trustworthy point instead of summing jitter.
            val endpointUncertaintyMetres = max(fix.accuracyMetres, previous.accuracyMetres)
            val movementDeadbandMetres = max(1.0, endpointUncertaintyMetres * 0.5).coerceAtMost(8.0)
            if (distance < movementDeadbandMetres) return false
            if (ActivityMetrics.averageSpeedKph(distance, fix.elapsedMs - previous.elapsedMs) > maxKph) return false
        }
        return true
    }
}
